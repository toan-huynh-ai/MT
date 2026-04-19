"""
Run local aya-101 on all Vietnamese->Khmer samples.
Outputs JSON results + summary metrics.
"""

import json
import re
import sys
import time
from collections import defaultdict
from datetime import datetime
from pathlib import Path

import torch
from transformers import AutoModelForSeq2SeqLM, AutoTokenizer

from cultural_kb_expanded import lookup
from evaluation_framework import classify_errors, compute_standard_metrics

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
sys.stderr.reconfigure(encoding="utf-8", errors="replace")

BASE_DIR = Path(__file__).parent
RESULTS_DIR = BASE_DIR / "experiment_results"
RESULTS_DIR.mkdir(exist_ok=True)
DATA_DIR = Path("/datastore/npl/luannt/IHSD/MT/data/khmer")
MODEL_DIR = Path("/datastore/npl/luannt/IHSD/.cache/models/aya-101")
CHECKPOINT_PATH = RESULTS_DIR / "aya101_all_checkpoint_latest.json"


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


def prepare_samples(data):
    selected = []
    for sample in data:
        ref = get_clean_reference(sample.get("label", []))
        if not ref:
            continue
        entities = lookup(sample["text"])
        selected.append(
            {
                "sample": sample,
                "ref": ref,
                "entities": entities,
            }
        )
    return selected


def save_checkpoint(per_sample, hypotheses, references, selected_len):
    with open(CHECKPOINT_PATH, "w", encoding="utf-8") as f:
        json.dump(
            {
                "per_sample": per_sample,
                "hypotheses": hypotheses,
                "references": references,
                "progress": f"{len(per_sample)}/{selected_len}",
            },
            f,
            ensure_ascii=False,
            indent=2,
        )


def load_model():
    print(f"Loading aya-101 from: {MODEL_DIR}")
    tokenizer = AutoTokenizer.from_pretrained(MODEL_DIR, trust_remote_code=True)
    model_dtype = torch.bfloat16 if torch.cuda.is_available() else torch.float32
    model = AutoModelForSeq2SeqLM.from_pretrained(
        MODEL_DIR,
        trust_remote_code=True,
        dtype=model_dtype,
        low_cpu_mem_usage=True,
    )
    model.eval()
    device = "cuda" if torch.cuda.is_available() else "cpu"
    model.to(device)
    print(f"Model loaded on device: {device}")
    return tokenizer, model, device


def build_prompt(text):
    return (
        "Translate the following Vietnamese text into Khmer. "
        "Output only the Khmer translation.\n\n"
        f"Vietnamese: {text}\n"
        "Khmer:"
    )


@torch.inference_mode()
def translate(tokenizer, model, device, text):
    prompt = build_prompt(text)
    inputs = tokenizer(prompt, return_tensors="pt", truncation=True, max_length=1024)
    inputs = {key: value.to(device) for key, value in inputs.items()}
    generated = model.generate(
        **inputs,
        max_new_tokens=160,
        do_sample=False,
        num_beams=4,
        repetition_penalty=1.05,
    )
    return tokenizer.batch_decode(generated, skip_special_tokens=True)[0].strip()


def main(resume_from=None):
    print("Loading data...")
    data = load_data()
    print(f"Loaded {len(data)} raw samples from all_1.jsonl and all_2.jsonl")
    selected = prepare_samples(data)
    print(f"Selected {len(selected)} samples with valid references")

    tokenizer, model, device = load_model()

    hypotheses, references = [], []
    per_sample = []
    start_idx = 0

    if resume_from and Path(resume_from).exists():
        print(f"Resuming from checkpoint: {resume_from}")
        with open(resume_from, "r", encoding="utf-8") as f:
            checkpoint_data = json.load(f)
        per_sample = checkpoint_data.get("per_sample", [])
        hypotheses = checkpoint_data.get("hypotheses", [])
        references = checkpoint_data.get("references", [])
        start_idx = len(per_sample)
        print(f"Resuming from sample {start_idx + 1}/{len(selected)}")

    start = time.time()
    for index, item in enumerate(selected[start_idx:], start=start_idx + 1):
        source = item["sample"]["text"]
        ref = item["ref"]
        ent_names = [entity.get("vi", entity.get("romanized", "?")) for entity in item["entities"]]
        print(f"[{index}/{len(selected)}] {ent_names[:3]}", flush=True)
        hyp = translate(tokenizer, model, device, source)

        hypotheses.append(hyp)
        references.append(ref)
        per_sample.append(
            {
                "source": source,
                "reference": ref,
                "hypothesis": hyp,
                "entities": ent_names,
                "eval": classify_errors(source, hyp, ref),
            }
        )

        if index % 100 == 0:
            save_checkpoint(per_sample, hypotheses, references, len(selected))

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
            "model": "aya-101",
            "model_dir": str(MODEL_DIR),
            "n_samples": len(selected),
            "elapsed_sec": elapsed,
            "device": device,
            "note": "Encoder-decoder multilingual model prompted for translation",
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
    outpath = RESULTS_DIR / f"aya101_all_{timestamp}.json"
    with open(outpath, "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)

    save_checkpoint(per_sample, hypotheses, references, len(selected))

    print("\n=== AYA-101 SUMMARY ===")
    print(f"chrF++: {corpus['chrf++']}")
    print(f"BLEU: {corpus['bleu']}")
    print(f"Avg CuEA: {results['corpus_results']['avg_cuea']}")
    print(f"Avg Script Purity: {results['corpus_results']['avg_script_purity']}")
    print(f"Elapsed: {elapsed}s")
    print(f"Saved to: {outpath}")


if __name__ == "__main__":
    resume_from = None

    for arg in sys.argv[1:]:
        if arg == "--all":
            continue
        if arg.startswith("--resume="):
            resume_from = arg.split("=", 1)[1]

    main(resume_from=resume_from)