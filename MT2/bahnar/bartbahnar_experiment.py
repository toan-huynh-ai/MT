"""
BARTBahnar Experiment — Bahnar → Vietnamese translation on vi_bahnar.jsonl
Using BARTBahnar checkpoint directly (without full pipeline requiring spacy/Solr).

Output: results/expALL_twoway_zeroshot_bartbahnar_at_home.json
- Matches the structure of GPT-4o/GPT-5 experiment files for easy metric comparison.
- Direction supported: Bahnar → Vietnamese (ba_to_vi) — the model's primary task.
- Vi → Bahnar direction is not supported by BARTBahnar; stored as empty string.
- Resume-safe: skips already-processed samples if output file exists.
"""

import json
import re
import sys
import time
from pathlib import Path

import sacrebleu
import torch
from transformers import AutoModelForSeq2SeqLM, AutoTokenizer

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
sys.stderr.reconfigure(encoding="utf-8", errors="replace")

CHECKPOINT_PATH = Path(__file__).parent / "BARTBahnar" / "translation" / "checkpoints" / "BartBanaFinal"
DATA_FILE_PATH = Path(__file__).parent / "data" / "vi_bahnar.jsonl"
RESULTS_DIR = Path(__file__).parent / "results"
RESULTS_DIR.mkdir(exist_ok=True)
OUTPUT_FILE_PATH = RESULTS_DIR / "expALL_twoway_zeroshot_bartbahnar_at_home.json"

BATCH_SIZE = 8
MAX_NEW_TOKENS = 256


class BARTBahnarTranslator:
    def __init__(self, checkpoint_path: str):
        print(f"Loading BARTBahnar from: {checkpoint_path}", flush=True)
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        print(f"Using device: {self.device}", flush=True)
        self.tokenizer = AutoTokenizer.from_pretrained(checkpoint_path)
        self.model = AutoModelForSeq2SeqLM.from_pretrained(checkpoint_path)
        self.model.to(self.device)
        self.model.eval()
        print("Model loaded successfully.", flush=True)

    def translate_batch(self, sentences: list[str]) -> list[str]:
        inputs = self.tokenizer(
            sentences,
            return_tensors="pt",
            padding=True,
            truncation=True,
            max_length=512,
        ).to(self.device)
        with torch.no_grad():
            outputs = self.model.generate(
                inputs["input_ids"],
                attention_mask=inputs["attention_mask"],
                max_new_tokens=MAX_NEW_TOKENS,
                num_beams=4,
                early_stopping=True,
            )
        return [self.tokenizer.decode(o, skip_special_tokens=True) for o in outputs]

    def translate(self, sentence: str) -> str:
        return self.translate_batch([sentence])[0]


def load_data() -> list[dict]:
    if not DATA_FILE_PATH.exists():
        print(f"ERROR: File not found: {DATA_FILE_PATH}", flush=True)
        sys.exit(1)
    data = []
    with open(DATA_FILE_PATH, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                data.append(json.loads(line))
    return data


def get_clean_reference(labels: list[str]) -> str:
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


def load_existing_results() -> tuple[dict, dict | None]:
    if not OUTPUT_FILE_PATH.exists():
        return {}, None
    try:
        with open(OUTPUT_FILE_PATH, "r", encoding="utf-8") as f:
            payload = json.load(f)
        existing_map = {s["text"]: s for s in payload.get("per_sample", []) if "text" in s}
        return existing_map, payload.get("metrics")
    except Exception as e:
        print(f"[WARN] Cannot read checkpoint: {e}. Starting fresh.", flush=True)
        return {}, None


def compute_metrics(hypotheses: list[str], references: list[str]) -> dict:
    if not hypotheses or not references:
        return {"bleu": 0.0, "chrf++": 0.0}
    bleu = sacrebleu.corpus_bleu(hypotheses, [references])
    chrf = sacrebleu.corpus_chrf(hypotheses, [references])
    return {"bleu": round(bleu.score, 2), "chrf++": round(chrf.score, 2)}


def save_progress(samples: list[dict], metrics_rev: dict | None = None):
    summary = {
        "metadata": {
            "model": "BARTBahnar (BartBanaFinal checkpoint)",
            "total_samples": len(samples),
            "status": "running" if metrics_rev is None else "completed",
        },
        "metrics": {
            "vietnamese_to_bahnar": {"bleu": 0.0, "chrf++": 0.0},
            "bahnar_to_vietnamese": metrics_rev or {"bleu": 0.0, "chrf++": 0.0},
        },
        "per_sample": samples,
    }
    with open(OUTPUT_FILE_PATH, "w", encoding="utf-8") as f:
        json.dump(summary, f, ensure_ascii=False, indent=2)


def main():
    print(f"Loading data from: {DATA_FILE_PATH} ...", flush=True)
    raw_data = load_data()
    print(f"Total samples: {len(raw_data)}", flush=True)

    existing_results, old_metrics = load_existing_results()
    if existing_results:
        print(f"Resuming: {len(existing_results)} samples already done.", flush=True)

    translator = BARTBahnarTranslator(str(CHECKPOINT_PATH))

    all_samples: list[dict] = []
    pending_indices: list[int] = []
    start_time = time.time()

    # Separate already-done from pending
    for i, d in enumerate(raw_data):
        raw_text = d.get("text", "").strip()
        raw_ref = get_clean_reference(d.get("label", []))
        if not raw_text or not raw_ref:
            continue
        sample = dict(d)
        if raw_text in existing_results:
            old = existing_results[raw_text]
            sample["hyp_vi_to_ba"] = old.get("hyp_vi_to_ba", "")
            sample["hyp_ba_to_vi"] = old.get("hyp_ba_to_vi", "")
            all_samples.append(sample)
        else:
            sample["_ref_bahnar"] = raw_ref
            all_samples.append(sample)
            pending_indices.append(len(all_samples) - 1)

    print(f"Samples to process: {len(pending_indices)}", flush=True)

    # Batch translate pending samples (Bahnar → Vietnamese)
    for batch_start in range(0, len(pending_indices), BATCH_SIZE):
        batch_idx = pending_indices[batch_start : batch_start + BATCH_SIZE]
        bahnar_inputs = [all_samples[i]["_ref_bahnar"] for i in batch_idx]

        print(
            f"  Translating batch {batch_start // BATCH_SIZE + 1}/"
            f"{(len(pending_indices) + BATCH_SIZE - 1) // BATCH_SIZE} "
            f"(samples {batch_start + 1}–{min(batch_start + BATCH_SIZE, len(pending_indices))})...",
            flush=True,
        )

        translations = translator.translate_batch(bahnar_inputs)

        for idx, hyp in zip(batch_idx, translations):
            all_samples[idx]["hyp_vi_to_ba"] = ""  # BARTBahnar doesn't do Vi→Bahnar
            all_samples[idx]["hyp_ba_to_vi"] = hyp

        # Checkpoint every 5 batches
        if (batch_start // BATCH_SIZE + 1) % 5 == 0:
            save_progress(
                [{k: v for k, v in s.items() if k != "_ref_bahnar"} for s in all_samples]
            )
            print(f"    --> Checkpointed at batch {batch_start // BATCH_SIZE + 1}", flush=True)

    # Strip temporary field
    for s in all_samples:
        s.pop("_ref_bahnar", None)

    print("\nCalculating final metrics...", flush=True)

    hyps_rev, refs_rev = [], []
    for s in all_samples:
        hyps_rev.append(s.get("hyp_ba_to_vi", ""))
        refs_rev.append(s.get("text", ""))

    metrics_rev = compute_metrics(hyps_rev, refs_rev)

    print("\n" + "=" * 60, flush=True)
    print("     FINAL RESULTS — BARTBahnar (BartBanaFinal)", flush=True)
    print("=" * 60, flush=True)
    print(f"{'Direction':<28} | {'BLEU':>8} | {'chrF++':>8}", flush=True)
    print("-" * 60, flush=True)
    print(f"{'Bahnar -> Vietnamese':<28} | {metrics_rev['bleu']:>8.2f} | {metrics_rev['chrf++']:>8.2f}", flush=True)
    print(f"{'Vietnamese -> Bahnar':<28} | {'N/A':>8} | {'N/A':>8}", flush=True)
    print("-" * 60, flush=True)
    elapsed = (time.time() - start_time) / 60
    print(f"Total samples: {len(all_samples)} | Time: {elapsed:.1f} min", flush=True)
    print("=" * 60, flush=True)

    save_progress(all_samples, metrics_rev)
    print(f"\nSaved to: {OUTPUT_FILE_PATH}", flush=True)


if __name__ == "__main__":
    main()
