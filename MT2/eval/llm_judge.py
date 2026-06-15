"""
LLM-as-a-Judge Evaluation Framework for Low-Resource Languages (Khmer Krom / Bahnar).
Endpoint: client.responses.create (GPT-5 Reasoning Specification).
Output path: experiment_results/judge_results.json
"""

import json, os, sys, time
from pathlib import Path
from openai import OpenAI

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
sys.stderr.reconfigure(encoding="utf-8", errors="replace")
os.environ["PYTHONUNBUFFERED"] = "1"

# Cấu hình đường dẫn hệ thống của bạn
BASE_DIR = Path(r"D:\Code\Python\Research\MachineTranslation\MT\MT2")
# Bạn có thể đổi tên file này thành file kết quả Bahnar hoặc Khmer Krom tùy cấu hình test
INPUT_RESULT_PATH = BASE_DIR / "experiment_results" / "expALL_twoway_zeroshot_gpt5_at_home_test.json"
OUTPUT_JUDGE_PATH = BASE_DIR / "experiment_results" / "judge_results.json"

JUDGE_SYSTEM_PROMPT = """You are an elite expert in Computational Linguistics and an Academic Reviewer for Core A* NLP conferences (ACL/EMNLP).
Your task is to act as a rigorous judge to evaluate the quality of a Machine Translation system for extreme low-resource regional languages (Khmer Krom or Bahnar).

You will be given:
1. Source Text (Original sentence)
2. Ground Truth (Human reference translation)
3. Hypothesis (Machine translation output)

You must evaluate the Hypothesis based on 4 strict criteria on a scale from 1 to 5 (1: Total failure, 5: Perfect translation):

1. Semantic Fidelity (Preservation of exact meaning without hallucinating macro-context or expanding stories).
2. Orthographic Integrity (Correct usage of specific regional diacritics and character blocks, avoiding literal character-by-character transliteration).
3. Fluency & Degeneracy Prevention (Zero tolerance for autoregressive repetition loops, stuttering, or phrase-level echoing).
4. Cultural & Local Mapping (Accurate translation of unique cultural entities, local dishes, or geographical terms).

You must output your evaluation strictly in the following JSON format, with absolutely no surrounding text or markdown blocks:
{
  "fidelity_score": 5,
  "orthography_score": 5,
  "fluency_score": 5,
  "cultural_score": 5,
  "rationale_en": "Brief academic justification of the scores."
}"""

def get_client():
    # Sử dụng chung cấu hình nhận key từ file .env hiện tại của bạn
    from dotenv import load_dotenv
    load_dotenv(BASE_DIR / ".env")
    return OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def call_judge_gpt5(client, source, reference, hypothesis, direction):
    """
    Hàm gọi GPT-5 đóng vai trò Thẩm định viên sử dụng cấu trúc endpoint mới.
    """
    user_prompt = (
        f"### EVALUATION CONTEXT:\n"
        f"Direction: {direction}\n"
        f"Source Text: \"{source}\"\n"
        f"Ground Truth Reference: \"{reference}\"\n"
        f"Machine Hypothesis to Evaluate: \"{hypothesis}\"\n\n"
        f"Provide your strict JSON evaluation object now:"
    )

    for attempt in range(3):
        try:
            resp = client.responses.create(
                model="gpt-5", # Hoặc gpt-5.5 tùy thuộc vào tên model bạn đang trỏ thực tế
                instructions=JUDGE_SYSTEM_PROMPT,
                input=user_prompt,
                max_output_tokens=300
            )
            raw_output = resp.output_text.strip()
            
            # Khử định dạng markdown block ```json nếu mô hình vô tình sinh ra
            raw_json = re.sub(r"```json\s*|\s*```", "", raw_output)
            return json.loads(raw_json)
        except Exception as e:
            print(f"    [Judge Retry {attempt+1}] Lỗi: {str(e)[:60]}... chờ {5 * (2 ** attempt)}s", flush=True)
            time.sleep(5 * (2 ** attempt))
    return None

def load_progress():
    """Cơ chế Strict Resume bảo vệ tiến độ chấm điểm của Judge"""
    if not OUTPUT_JUDGE_PATH.exists():
        return {}
    try:
        with open(OUTPUT_JUDGE_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    except:
        return {}

def main():
    if not INPUT_RESULT_PATH.exists():
        print(f"ERROR: Không tìm thấy file kết quả cần thẩm định tại: {INPUT_RESULT_PATH}")
        sys.exit(1)

    with open(INPUT_RESULT_PATH, "r", encoding="utf-8") as f:
        experiment_data = json.load(f)

    samples = experiment_data.get("per_sample", [])
    print(f"Loaded {len(samples)} samples to evaluate via LLM-as-a-Judge...", flush=True)

    client = get_client()
    judge_progress_map = load_progress()
    
    judge_results = dict(judge_progress_map)
    evaluated_count = len(judge_results)
    
    start_time = time.time()

    for idx, sample in enumerate(samples):
        sample_id = str(sample.get("id", idx))
        source_text = sample.get("text", "").strip()
        # Lấy nhãn sạch đã được tiền xử lý của bạn
        reference_text = sample.get("label", [""])[0].strip()
        
        # Ca bốc tách kết quả dịch thuận và nghịch từ file json cũ của bạn
        # (Nếu chạy cho Bahnar, bạn đổi key thành 'hyp_vi_to_ba' và 'hyp_ba_to_vi' tương ứng)
        hyp_fwd = sample.get("hyp_vi_to_km", "").strip()
        hyp_rev = sample.get("hyp_km_to_vi", "").strip()

        # Nếu mẫu này đã được Judge chấm điểm trước đó, bỏ qua (Resume Mechanism)
        if sample_id in judge_results:
            continue

        if (idx + 1) % 10 == 0 or idx == 0:
            print(f"  [Judge Process] Evaluating sample {idx+1}/{len(samples)} (ID: {sample_id})...", flush=True)

        # Chấm điểm Chiều Thuận (Forward)
        score_fwd = call_judge_gpt5(client, source_text, reference_text, hyp_fwd, direction="Vietnamese-to-Target")
        
        # Chấm điểm Chiều Nghịch (Reverse)
        score_rev = call_gpt5_fallback_check(client, reference_text, source_text, hyp_rev, source_text, direction="Target-to-Vietnamese")

        judge_results[sample_id] = {
            "id": sample.get("id"),
            "text": source_text,
            "forward_evaluation": score_fwd,
            "reverse_evaluation": score_rev
        }
        
        # Lưu tiến trình tự động sau mỗi 10 mẫu tránh mất điện hoặc rớt mạng
        if len(judge_results) % 10 == 0:
            with open(OUTPUT_JUDGE_PATH, "w", encoding="utf-8") as out_f:
                json.dump(judge_results, out_f, ensure_ascii=False, indent=2)

    # Ghi file kết quả thẩm định cuối cùng
    with open(OUTPUT_JUDGE_PATH, "w", encoding="utf-8") as out_f:
        json.dump(judge_results, out_f, ensure_ascii=False, indent=2)

    # --- TÍNH TOÁN ĐIỂM TRUNG BÌNH TOÀN DIỆN CHO BÀI BÁO KHCN ---
    print("\n" + "=" * 60)
    print("      LLM-AS-A-JUDGE ACADEMIC REPORT COMPLED")
    print("=" * 60)
    # Đoạn logic tính Mean Score để bạn vẽ biểu đồ cột (Bar Chart) trong luận văn
    compute_macro_average(judge_results)
    print(f"Total processing time: {(time.time()-start_time)/60:.1f} mins")
    print(f"Results successfully saved to: {OUTPUT_JUDGE_PATH}")

def call_gpt5_fallback_check(client, source, reference, hypothesis, origin_src, direction):
    """Bổ trợ gọi thẩm định chiều nghịch"""
    return call_judge_gpt5(client, source, reference, hypothesis, direction)

def compute_macro_average(results):
    """Tính điểm trung bình vĩ mô phục vụ viết báo cáo khoa học"""
    fwd_metrics = {"fidelity": 0, "orthography": 0, "fluency": 0, "cultural": 0, "count": 0}
    rev_metrics = {"fidelity": 0, "orthography": 0, "fluency": 0, "cultural": 0, "count": 0}
    
    for k, v in results.items():
        f = v.get("forward_evaluation")
        r = v.get("reverse_evaluation")
        if f:
            fwd_metrics["fidelity"] += f.get("fidelity_score", 0)
            fwd_metrics["orthography"] += f.get("orthography_score", 0)
            fwd_metrics["fluency"] += f.get("fluency_score", 0)
            fwd_metrics["cultural"] += f.get("cultural_score", 0)
            fwd_metrics["count"] += 1
        if r:
            rev_metrics["fidelity"] += r.get("fidelity_score", 0)
            rev_metrics["orthography"] += r.get("orthography_score", 0)
            rev_metrics["fluency"] += r.get("fluency_score", 0)
            rev_metrics["cultural"] += r.get("cultural_score", 0)
            rev_metrics["count"] += 1

    if fwd_metrics["count"] > 0:
        print(f"Forward Direction (Vi -> Target) Macro Averages:")
        print(f"  - Semantic Fidelity: {fwd_metrics['fidelity']/fwd_metrics['count']:.2f} / 5.0")
        print(f"  - Orthographic Integrity: {fwd_metrics['orthography']/fwd_metrics['count']:.2f} / 5.0")
        print(f"  - Fluency (No-Loop): {fwd_metrics['fluency']/fwd_metrics['count']:.2f} / 5.0")
        print(f"  - Cultural Entity Mapping: {fwd_metrics['cultural']/fwd_metrics['count']:.2f} / 5.0")
    if rev_metrics["count"] > 0:
        print(f"\nReverse Direction (Target -> Vi) Macro Averages:")
        print(f"  - Semantic Fidelity: {rev_metrics['fidelity']/rev_metrics['count']:.2f} / 5.0")
        print(f"  - Orthographic Integrity: {rev_metrics['orthography']/rev_metrics['count']:.2f} / 5.0")
        print(f"  - Fluency (No-Loop): {rev_metrics['fluency']/rev_metrics['count']:.2f} / 5.0")
        print(f"  - Cultural Entity Mapping: {rev_metrics['cultural']/rev_metrics['count']:.2f} / 5.0")

if __name__ == "__main__":
    import re
    main()