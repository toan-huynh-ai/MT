"""
Run local NLLB-200-3.3B on 50 Vietnamese→Khmer samples.
Outputs JSON results + summary metrics.
"""

import json
import random
import re
import sys
import time
from collections import defaultdict
from datetime import datetime
from pathlib import Path

import torch
from transformers import AutoModelForSeq2SeqLM, AutoTokenizer
from tqdm import tqdm

from cultural_kb_expanded import lookup
from evaluation_framework import classify_errors, compute_standard_metrics

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
sys.stderr.reconfigure(encoding="utf-8", errors="replace")

BASE_DIR = Path(__file__).parent
RESULTS_DIR = BASE_DIR / "experiment_results"
RESULTS_DIR.mkdir(exist_ok=True)
MODEL_DIR = Path("/datastore/npl/luannt/IHSD/.cache/models/nllb-200-3.3B")
DATA_DIR = Path("/datastore/npl/luannt/IHSD/MT/data/khmer")


def load_data():
    data = []
    for fname in ["all_1.jsonl", "all_2.jsonl"]:
        fpath = DATA_DIR / fname
        if not fpath.exists():
            continue
        with open(fpath, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line:
                    data.append(json.loads(line))
    return data


def get_clean_reference(labels):
    best = ""
    for lbl in labels:
        clean = lbl.split("###")[0].strip()
        parts = clean.split("***")
        if len(parts) == 1 and len(clean) > len(best):
            best = clean
    if not best and labels:
        raw = labels[0].split("###")[0].strip()
        best = re.sub(r"\S+\s*\*\*\*\s*", "", raw).strip()
        if not best:
            best = labels[0].split("###")[-1].strip()
    return best


def select_samples(data, n=50, use_all=False):
    """
    Select samples for translation.
    
    Args:
        data: list of samples
        n: number of samples (ignored if use_all=True)
        use_all: if True, use all samples; if False, filter by entities
    """
    if use_all:
        # Use all samples, prioritize those with valid references
        selected = []
        for d in data:
            ref = get_clean_reference(d.get("label", []))
            if ref:
                try:
                    entities = lookup(d["text"]) if "lookup" in dir() else []
                except:
                    entities = []
                selected.append(
                    {
                        "sample": d,
                        "ref": ref,
                        "entities": entities,
                        "n_entities": len(
                            set(e.get("vi", e.get("romanized", "")) for e in entities)
                        ),
                    }
                )
        print(f"Using all {len(selected)} samples with valid references")
        return selected
    
    # Original logic: filter by entities
    samples_with_entities = []
    for d in data:
        ref = get_clean_reference(d.get("label", []))
        if not ref:
            continue
        entities = lookup(d["text"])
        if entities:
            samples_with_entities.append(
                {
                    "sample": d,
                    "ref": ref,
                    "entities": entities,
                    "n_entities": len(
                        set(e.get("vi", e.get("romanized", "")) for e in entities)
                    ),
                }
            )

    random.seed(42)
    if len(samples_with_entities) > n:
        samples_with_entities.sort(key=lambda x: -x["n_entities"])
        top = samples_with_entities[: n // 2]
        rest = samples_with_entities[n // 2 :]
        random_rest = random.sample(rest, min(n - len(top), len(rest)))
        selected = top + random_rest
    else:
        selected = samples_with_entities
    return selected[:n]


def load_model():
    print(f"Loading NLLB from: {MODEL_DIR}")
    tokenizer = AutoTokenizer.from_pretrained(
        MODEL_DIR,
        src_lang="vie_Latn",
        use_fast=False,
    )
    model = AutoModelForSeq2SeqLM.from_pretrained(
        MODEL_DIR,
        torch_dtype=torch.float32,
        low_cpu_mem_usage=True,
    )
    model.eval()
    device = "cuda" if torch.cuda.is_available() else "cpu"
    model.to(device)
    print(f"Model loaded on device: {device}")
    return tokenizer, model, device


@torch.inference_mode()
def translate(tokenizer, model, device, text):
    inputs = tokenizer(text, return_tensors="pt", truncation=True, max_length=512)
    inputs = {k: v.to(device) for k, v in inputs.items()}
    generated = model.generate(
        **inputs,
        forced_bos_token_id=tokenizer.convert_tokens_to_ids("khm_Khmr"),
        max_new_tokens=120,
        do_sample=False,
        num_beams=4,
    )
    return tokenizer.batch_decode(generated, skip_special_tokens=True)[0].strip()


def main(n_samples=50, use_all=False, resume_from=None):
    print("Loading data...")
    data = load_data()
    print(f"Total data available: {len(data)} samples")
    
    if use_all:
        selected = select_samples(data, use_all=True)
    else:
        selected = select_samples(data, n=n_samples)
    
    print(f"Selected {len(selected)} samples for translation")

    tokenizer, model, device = load_model()

    hypotheses, references, sources = [], [], []
    per_sample = []

    # Resume from checkpoint if exists
    checkpoint_file = None
    start_idx = 0
    if resume_from and Path(resume_from).exists():
        print(f"\nResuming from checkpoint: {resume_from}")
        with open(resume_from, "r", encoding="utf-8") as f:
            checkpoint_data = json.load(f)
        per_sample = checkpoint_data.get("per_sample", [])
        hypotheses = checkpoint_data.get("hypotheses", [])
        references = checkpoint_data.get("references", [])
        sources = checkpoint_data.get("sources", [])
        start_idx = len(per_sample)
        print(f"Resuming from sample {start_idx + 1}/{len(selected)}")

    start = time.time()
    for idx, item in enumerate(selected[start_idx:], start=start_idx):
        source = item["sample"]["text"]
        ref = item["ref"]
        ent_names = [e.get("vi", e.get("romanized", "?")) for e in item["entities"]]
        hyp = translate(tokenizer, model, device, source)

        hypotheses.append(hyp)
        references.append(ref)
        sources.append(source)
        per_sample.append(
            {
                "source": source,
                "reference": ref,
                "hypothesis": hyp,
                "entities": ent_names,
                "eval": classify_errors(source, hyp, ref),
            }
        )
        
        # Save checkpoint every 100 samples
        if (idx + 1) % 100 == 0:
            checkpoint_file = RESULTS_DIR / f"checkpoint_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            with open(checkpoint_file, "w", encoding="utf-8") as f:
                json.dump({
                    "per_sample": per_sample,
                    "hypotheses": hypotheses,
                    "references": references,
                    "sources": sources,
                    "progress": f"{idx + 1}/{len(selected)}"
                }, f, ensure_ascii=False)

    elapsed = round(time.time() - start, 2)
    corpus = compute_standard_metrics(hypotheses, references)
    cueas = [
        row["eval"]["cuea"]["cuea"]
        for row in per_sample
        if row["eval"]["cuea"]["cuea"] is not None
    ]
    purities = [row["eval"]["script_purity"]["purity"] for row in per_sample]
    errors = defaultdict(int)
    for row in per_sample:
        for err in row["eval"]["errors"]:
            errors[err["type"]] += 1

    results = {
        "metadata": {
            "model": "nllb-200-3.3B",
            "model_dir": str(MODEL_DIR),
            "n_samples": len(selected),
            "elapsed_sec": elapsed,
            "device": device,
        },
        "corpus_results": {
            **corpus,
            "avg_cuea": round(sum(cueas) / len(cueas), 3) if cueas else None,
            "avg_script_purity": round(sum(purities) / len(purities), 3),
            "error_distribution": dict(errors),
        },
        "per_sample": per_sample,
    }

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    outpath = RESULTS_DIR / f"nllb_all_{timestamp}.json"
    with open(outpath, "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)

    print("\n" + "="*50)
    print(f"NLLB Translation Summary ({len(selected)} samples)")
    print("="*50)
    print(f"chrF++: {corpus['chrf++']:.4f}")
    print(f"BLEU: {corpus['bleu']:.4f}")
    print(f"Avg CuEA: {results['corpus_results']['avg_cuea']:.4f}" if results['corpus_results']['avg_cuea'] else "Avg CuEA: N/A")
    print(f"Avg Script Purity: {results['corpus_results']['avg_script_purity']:.4f}")
    print(f"Time elapsed: {elapsed}s ({elapsed/len(selected):.2f}s per sample)")
    print(f"Saved to: {outpath}")
    print("="*50)


if __name__ == "__main__":
    n_samples = 50
    use_all = False
    resume_from = None
    
    # Parse command line args
    for arg in sys.argv[1:]:
        if arg == "--all":
            use_all = True
        elif arg.startswith("--resume="):
            resume_from = arg.split("=", 1)[1]
        else:
            try:
                n_samples = int(arg)
            except ValueError:
                pass
    
    main(n_samples=n_samples, use_all=use_all, resume_from=resume_from)
