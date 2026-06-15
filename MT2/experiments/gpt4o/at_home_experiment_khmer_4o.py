"""
Two-Way Zero-Shot Evaluation Experiment with Strict Resume Mechanism.
Output path: experiment_results/expALL_twoway_zeroshot_gpt4o_at_home.json

- Retains ALL original fields from the JSONL input.
- Skips already processed samples if the output file exists.
- Computes final BLEU and chrF++ metrics for both directions.
"""

import json, os, sys, time, re
from pathlib import Path
import sacrebleu
from dotenv import load_dotenv
from openai import OpenAI

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
sys.stderr.reconfigure(encoding="utf-8", errors="replace")
os.environ["PYTHONUNBUFFERED"] = "1"
load_dotenv(r"D:\Code\Python\Research\MachineTranslation\MT\MT2\.env")

RESULTS_DIR = Path(__file__).parent / "experiment_results"
RESULTS_DIR.mkdir(exist_ok=True)

DATA_FILE_PATH = r"D:\Code\Python\Research\MachineTranslation\MT\MT2\data\all_cleaned2.jsonl"
OUTPUT_FILE_PATH = RESULTS_DIR / "expALL_twoway_zeroshot_gpt4o_at_home_test.json"

PROMPTS = {
    "vi_to_km": {
        "system": (
            "You are an expert Vietnamese-Khmer Krom translator. Translate the text into Khmer Krom dialect "
            "used in Vietnam's Mekong Delta, NOT standard Cambodian Khmer. Output ONLY the translation."
        ),
        "prefix": "Vietnamese: "
    },
    "km_to_vi": {
        "system": (
            "You are an expert Khmer Krom-Vietnamese translator. The source is in Khmer Krom dialect (Vietnam's Mekong Delta) "
            "with local cultural terms. Translate it into natural Vietnamese. Output ONLY the translation."
        ),
        "prefix": "Khmer Krom: "
    }
}


def get_client():
    return OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


def call_gpt4o(client, system_prompt, user_prompt, max_retries=3):
    for attempt in range(max_retries):
        try:
            resp = client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
                temperature=0.2,
                max_tokens=512,
            )
            return resp.choices[0].message.content.strip()
        except Exception as e:
            wait = 5 * (2 ** attempt)
            print(f"    [Retry {attempt+1}] {str(e)[:80]}... wait {wait}s", flush=True)
            time.sleep(wait)
    return ""


def load_data():
    data = []
    fpath = Path(DATA_FILE_PATH)
    if not fpath.exists():
        print(f"ERROR: File không tồn tại tại đường dẫn: {DATA_FILE_PATH}", flush=True)
        sys.exit(1)
        
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


def load_existing_results():
    """Đọc dữ liệu đã chạy trước đó từ file output cố định nếu tồn tại"""
    if not OUTPUT_FILE_PATH.exists():
        return {}, None
    
    try:
        with open(OUTPUT_FILE_PATH, "r", encoding="utf-8") as f:
            payload = json.load(f)
            samples_list = payload.get("per_sample", [])
            old_metrics = payload.get("metrics", None)
            
            existing_map = {}
            for s in samples_list:
                if "text" in s:
                    existing_map[s["text"]] = s
            return existing_map, old_metrics
    except Exception as e:
        print(f"[WARN] Không thể đọc file checkpoint cũ hoặc file bị lỗi cấu trúc: {e}. Sẽ chạy lại từ đầu.", flush=True)
        return {}, None


def compute_metrics(hypotheses, references):
    if not hypotheses or not references:
        return {"bleu": 0.0, "chrf++": 0.0}
    bleu = sacrebleu.corpus_bleu(hypotheses, [references])
    chrf = sacrebleu.corpus_chrf(hypotheses, [references])
    return {"bleu": round(bleu.score, 2), "chrf++": round(chrf.score, 2)}


def save_progress(processed_samples, metrics_fwd=None, metrics_rev=None):
    """Ghi trực tiếp vào file output đích, bảo toàn cấu trúc tổng hợp"""
    summary = {
        "metadata": {
            "model": "gpt-4o",
            "total_samples": len(processed_samples),
            "status": "running" if (metrics_fwd is None) else "completed"
        },
        "metrics": {
            "vietnamese_to_khmer": metrics_fwd or {"bleu": 0.0, "chrf++": 0.0},
            "khmer_to_vietnamese": metrics_rev or {"bleu": 0.0, "chrf++": 0.0}
        },
        "per_sample": processed_samples
    }
    
    with open(OUTPUT_FILE_PATH, "w", encoding="utf-8") as f:
        json.dump(summary, f, ensure_ascii=False, indent=2)


def main():
    print(f"Loading data from: {DATA_FILE_PATH} ...", flush=True)
    raw_data = load_data()
    print(f"Total raw samples loaded from JSONL: {len(raw_data)}", flush=True)

    # Đọc tiến trình đã chạy trước đó
    existing_results, old_metrics = load_existing_results()
    if existing_results:
        print(f"Found existing progress! {len(existing_results)} samples already processed.", flush=True)

    client = get_client()
    all_samples_progress = []
    new_runs_count = 0
    start_time = time.time()

    for i, d in enumerate(raw_data):
        raw_text = d.get("text", "").strip()
        raw_ref = get_clean_reference(d.get("label", []))
        
        if not raw_text or not raw_ref:
            continue
        
        current_sample = dict(d)
        
        # 1. KIỂM TRA XEM MẪU NÀY ĐÃ ĐƯỢC CHẠY TRƯỚC ĐÓ CHƯA
        if raw_text in existing_results:
            old_sample = existing_results[raw_text]
            current_sample["hyp_vi_to_km"] = old_sample.get("hyp_vi_to_km", "")
            current_sample["hyp_km_to_vi"] = old_sample.get("hyp_km_to_vi", "")
            all_samples_progress.append(current_sample)
            continue
            
        # 2. NẾU CHƯA CÓ, TIẾN HÀNH DỊCH 2 CHIỀU
        new_runs_count += 1
        if new_runs_count % 5 == 0 or new_runs_count == 1:
            print(f"  [API Call] Processing new sample {i+1}/{len(raw_data)}...", flush=True)
            
        # Sửa đổi quan trọng: Thay đổi dấu ngoặc kép thành ngoặc đơn trong f-string để tránh SyntaxError
        hyp_fwd = call_gpt4o(client, PROMPTS['vi_to_km']['system'], f"{PROMPTS['vi_to_km']['prefix']}{raw_text}")
        hyp_rev = call_gpt4o(client, PROMPTS['km_to_vi']['system'], f"{PROMPTS['km_to_vi']['prefix']}{raw_ref}")
        
        current_sample["hyp_vi_to_km"] = hyp_fwd
        current_sample["hyp_km_to_vi"] = hyp_rev
        all_samples_progress.append(current_sample)
        
        # Sửa đổi: Duy trì m_fwd và m_rev cũ trong suốt quá trình lưu tiến độ tự động
        if new_runs_count % 20 == 0:
            m_fwd = old_metrics["vietnamese_to_khmer"] if old_metrics else None
            m_rev = old_metrics["khmer_to_vietnamese"] if old_metrics else None
            save_progress(all_samples_progress, m_fwd, m_rev)
            print(f"    --> Automatically checkpointed at new sample {new_runs_count}", flush=True)

    # --- TÍNH TOÁN METRICS TRÊN TOÀN BỘ TẬP DỮ LIỆU ---
    print("\nCalculating final metrics...", flush=True)
    
    hyps_fwd, refs_fwd = [], []
    hyps_rev, refs_rev = [], []
    
    for s in all_samples_progress:
        ref_clean = get_clean_reference(s.get("label", []))
        
        hyps_fwd.append(s.get("hyp_vi_to_km", ""))
        refs_fwd.append(ref_clean)
        
        hyps_rev.append(s.get("hyp_km_to_vi", ""))
        refs_rev.append(s.get("text", ""))

    metrics_fwd = compute_metrics(hyps_fwd, refs_fwd)
    metrics_rev = compute_metrics(hyps_rev, refs_rev)
    
    # --- IN BẢNG KẾT QUẢ ĐẸP MẮT ---
    print("\n" + "=" * 60, flush=True)
    print(f"            FINAL TWO-WAY ZERO-SHOT RESULTS", flush=True)
    print("=" * 60, flush=True)
    print(f"{'Direction':<25} | {'BLEU Score':>12} | {'chrF++':>12}", flush=True)
    print("-" * 60, flush=True)
    print(f"{'Vietnamese -> Khmer (Fwd)':<25} | {metrics_fwd['bleu']:>12.2f} | {metrics_fwd['chrf++']:>12.2f}", flush=True)
    print(f"{'Khmer -> Vietnamese (Rev)':<25} | {metrics_rev['bleu']:>12.2f} | {metrics_rev['chrf++']:>12.2f}", flush=True)
    print("-" * 60, flush=True)
    print(f"New samples processed this run: {new_runs_count} | Total time: {(time.time()-start_time)/60:.1f} mins", flush=True)
    print("=" * 60, flush=True)
    
    # --- LƯU FILE KẾT QUẢ CUỐI CÙNG ---
    with open(OUTPUT_FILE_PATH, "w", encoding="utf-8") as f:
        json.dump({
            "metadata": {
                "model": "gpt-4o",
                "total_samples": len(all_samples_progress),
                "status": "completed"
            },
            "metrics": {
                "vietnamese_to_khmer": metrics_fwd,
                "khmer_to_vietnamese": metrics_rev
            },
            "per_sample": all_samples_progress
        }, f, ensure_ascii=False, indent=2)
    print(f"\nSaved all predictions and summaries to: {OUTPUT_FILE_PATH}", flush=True)


if __name__ == "__main__":
    main()