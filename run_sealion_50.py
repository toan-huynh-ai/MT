"""
Run local Llama-SEA-LION-v3.5-8B-R on all Vietnamese→Khmer samples.
Outputs JSON results + summary metrics.
Note: SEA-LION is a causal LM prompted for translation.
"""

import json
import re
import sys
import time
from collections import defaultdict
from datetime import datetime
from pathlib import Path

import torch
from transformers import AutoConfig, AutoModelForCausalLM, PreTrainedTokenizerFast

from cultural_kb_expanded import lookup
from evaluation_framework import classify_errors, compute_standard_metrics

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
sys.stderr.reconfigure(encoding="utf-8", errors="replace")

BASE_DIR = Path(__file__).parent
RESULTS_DIR = BASE_DIR / "experiment_results"
RESULTS_DIR.mkdir(exist_ok=True)
DATA_DIR = Path("/datastore/npl/luannt/IHSD/MT/data")
MODEL_DIR = Path("/datastore/npl/luannt/IHSD/.cache/models/Llama-SEA-LION-v3.5-8B-R")


def load_data():
    data = []
    for fname in ["all_1.jsonl", "all_2.jsonl"]:
        fpath = DATA_DIR / "khmer" / fname
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
    for d in data:
        ref = get_clean_reference(d.get("label", []))
        if not ref:
            continue
        entities = lookup(d["text"])
        selected.append(
            {
                "sample": d,
                "ref": ref,
                "entities": entities,
            }
        )
    return selected


def save_checkpoint(checkpoint_path, per_sample, hypotheses, references, selected_len):
    with open(checkpoint_path, "w", encoding="utf-8") as f:
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
    print(f"Loading SEA-LION from: {MODEL_DIR}")
    tokenizer = PreTrainedTokenizerFast.from_pretrained(MODEL_DIR)
    config = AutoConfig.from_pretrained(MODEL_DIR, trust_remote_code=True)
    config.tie_word_embeddings = True
    model = AutoModelForCausalLM.from_pretrained(
        MODEL_DIR,
        trust_remote_code=True,
        config=config,
        dtype=torch.float32,
        low_cpu_mem_usage=True,
    )
    model.eval()
    device = "cuda" if torch.cuda.is_available() else "cpu"
    model.to(device)
    print(f"Model loaded on device: {device}")
    return tokenizer, model, device


def build_prompt(text):
    return (
        "You are a translation system for Southeast Asian languages.\n"
        "Translate the following Vietnamese text into Khmer.\n"
        "Output only the Khmer translation.\n\n"
        f"Vietnamese: {text}\n"
        "Khmer:"
    )


@torch.inference_mode()
def translate(tokenizer, model, device, text):
    prompt = build_prompt(text)
    inputs = tokenizer(prompt, return_tensors="pt", truncation=True, max_length=1024)
    inputs.pop("token_type_ids", None)
    inputs = {k: v.to(device) for k, v in inputs.items()}
    input_len = inputs["input_ids"].shape[1]

    generated = model.generate(
        **inputs,
        max_new_tokens=48,
        do_sample=False,
        eos_token_id=tokenizer.eos_token_id,
        pad_token_id=tokenizer.eos_token_id,
    )
    new_tokens = generated[0][input_len:]
    text_out = tokenizer.decode(new_tokens, skip_special_tokens=True).strip()
    # Keep only first line / first answer span
    text_out = text_out.split("\n")[0].strip()
    return text_out


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
    checkpoint_path = RESULTS_DIR / "sealion_all_checkpoint_latest.json"
    for i, item in enumerate(selected[start_idx:], start=start_idx + 1):
        source = item["sample"]["text"]
        ref = item["ref"]
        ent_names = [e.get("vi", e.get("romanized", "?")) for e in item["entities"]]
        print(f"[{i}/{len(selected)}] {ent_names[:3]}", flush=True)
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

        if i % 100 == 0:
            save_checkpoint(
                checkpoint_path,
                per_sample,
                hypotheses,
                references,
                len(selected),
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
            "model": "Llama-SEA-LION-v3.5-8B-R",
            "model_dir": str(MODEL_DIR),
            "n_samples": len(selected),
            "elapsed_sec": elapsed,
            "device": device,
            "note": "Causal LM prompted for translation",
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
    outpath = RESULTS_DIR / f"sealion_all_{timestamp}.json"
    with open(outpath, "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)

    save_checkpoint(
        checkpoint_path,
        per_sample,
        hypotheses,
        references,
        len(selected),
    )

    print("\n=== SEA-LION SUMMARY ===")
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
