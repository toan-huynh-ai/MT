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

from cultural_kb_expanded import lookup
from evaluation_framework import classify_errors, compute_standard_metrics

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
sys.stderr.reconfigure(encoding="utf-8", errors="replace")

BASE_DIR = Path(__file__).parent
RESULTS_DIR = BASE_DIR / "experiment_results"
RESULTS_DIR.mkdir(exist_ok=True)
MODEL_DIR = Path(r"c:\Users\HOY9HC\Desktop\Code\Learning\models\nllb-200-3.3B")


def load_data():
    data = []
    for fname in ["all_1.jsonl", "all_2.jsonl"]:
        fpath = BASE_DIR / fname
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


def select_samples(data, n=50):
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
        max_new_tokens=96,
        do_sample=False,
        num_beams=1,
    )
    return tokenizer.batch_decode(generated, skip_special_tokens=True)[0].strip()


def main():
    print("Loading data...")
    data = load_data()
    selected = select_samples(data, n=50)
    print(f"Selected {len(selected)} samples")

    tokenizer, model, device = load_model()

    hypotheses, references, sources = [], [], []
    per_sample = []

    start = time.time()
    for i, item in enumerate(selected, 1):
        source = item["sample"]["text"]
        ref = item["ref"]
        ent_names = [e.get("vi", e.get("romanized", "?")) for e in item["entities"]]
        print(f"[{i}/{len(selected)}] {ent_names[:3]}", flush=True)
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
    outpath = RESULTS_DIR / f"nllb_50_{timestamp}.json"
    with open(outpath, "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)

    print("\n=== NLLB SUMMARY ===")
    print(f"chrF++: {corpus['chrf++']}")
    print(f"BLEU: {corpus['bleu']}")
    print(f"Avg CuEA: {results['corpus_results']['avg_cuea']}")
    print(f"Avg Script Purity: {results['corpus_results']['avg_script_purity']}")
    print(f"Elapsed: {elapsed}s")
    print(f"Saved to: {outpath}")


if __name__ == "__main__":
    main()
