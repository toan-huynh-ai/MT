import json
import os
import re
import time
from collections import defaultdict
from openai import OpenAI
from tqdm import tqdm
from dotenv import load_dotenv

# Nạp biến môi trường cho dự án dịch máy
load_dotenv(r"D:\Code\Python\Research\MachineTranslation\MT\MT2\.env")

# Khởi tạo OpenAI Client
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# --- SYSTEM PROMPT CHUẨN HÓA THANG ĐIỂM QUALITY SCORE 1-5 (ANTI-BIAS) ---
SYSTEM_PROMPT = """You are an expert Computational Linguist and professional Bilingual Evaluator specializing in the contrastive linguistics of Vietnamese and native Southeast Asian languages (such as Khmer and Bahnar). Your sole task is to strictly evaluate the translation quality of a Machine Translation (MT) hypothesis against a human-verified Gold Standard Reference, using a customized Multidimensional Quality Metrics (MQM) framework.

To ensure top-tier academic rigor and eliminate any evaluation bias, you MUST strictly adhere to the following execution laws:
1. NO PRE-CONCEIVED ASSUMPTIONS: Do not assume the translation will suffer from specific errors like repetitive token degeneration, text collapse, or domain shifts unless explicitly evidenced in the exact text segment provided. Evaluate each sample as a completely independent instance.
2. REFERENCE-ANCHORED VALIDATION: The Human Reference is your absolute semantic ground truth. If the translation introduces fluent but hallucinated phrases (such as general platitudes about preserving culture or protecting forests) that are NOT supported by the human reference, you MUST punish the accuracy score. Do not reward fluency over accuracy.
3. SCORING RUBRIC (Strict 1-5 Scale):
   - 5 (Excellent): Perfect translation. Fully preserves semantic meaning, cultural items, and correct structural/grammatical morphology.
   - 4 (Good): Clear meaning with minor flaws. 1-2 minor morphology, character-spacing, or word-order issues that do not alter the core message.
   - 3 (Fair): Notable errors. Features mis-translated terminology, wrong classifiers, or register/honorifics mismatch.
   - 2 (Poor): Severe degradation. Domain mismatch, severe hallucinations, forcing the text into a religious/Biblical context, or minor text repetitions.
   - 1 (Flawed/Unusable): Completely unusable. Extreme automatic token collapse, infinite repetition loops, gibberish strings, or text that is completely broken/irrelevant.

OUTPUT FORMAT RULE:
You must output your final evaluation strictly as a valid JSON object matching the schema below. Do not include any conversational prose outside the JSON markdown block.

{
  "evaluation_analysis": {
    "step_1_semantic_deconstruction": "Notes on meaning units of source and reference...",
    "step_2_target_structural_check": "Technical notes auditing the target translation...",
    "step_3_cross_lingual_alignment": "Notes mapping meaning and catching hallucinations/shifts...",
    "step_4_scoring_justification": "Logical justification for the assigned score based on the 1-5 rubric..."
  },
  "mqm_report": {
    "primary_error_category": "Accuracy > Cultural Rendition > Mistranslated CSI | Accuracy > Mistranslation > Domain Mismatch | Fluency > Grammar > Morphology > Affix-Omission | Fluency > Content-Generation > Degenerate Repetition | Style > Register > Honorifics-Mismatch | None",
    "detected_severity": "Minor | Major | Critical | None",
    "final_quality_score": 5
  }
}"""

def call_gpt5(client, system_prompt, user_prompt, max_retries=3):
    """
    Hàm gọi API sử dụng endpoint responses.create chuẩn xác của dòng mô hình suy luận gpt-5.5.
    """
    for attempt in range(max_retries):
        try:
            resp = client.responses.create(
                model="gpt-5.5",
                instructions=system_prompt,
                input=user_prompt,
            )
            return resp.output_text or ""
        except Exception as e:
            wait = 5 * (2 ** attempt)
            print(f"    [Retry {attempt+1}] {str(e)[:80]}... wait {wait}s", flush=True)
            time.sleep(wait)
    return ""

def extract_json_from_text(text):
    """
    Bóc tách khối JSON từ chuỗi phản hồi thô của mô hình suy luận gpt-5.5.
    """
    try:
        match = re.search(r'```json\s*(\{.*?\})\s*```', text, re.DOTALL)
        if match:
            return json.loads(match.group(1))
        return json.loads(text.strip())
    except Exception:
        return {
            "evaluation_analysis": {"error": "Failed to parse JSON from output text"},
            "mqm_report": {"primary_error_category": "None", "detected_severity": "None", "final_quality_score": 1}
        }

def evaluate_pipeline(input_file_path, output_file_path):
    # --- BƯỚC KHỞI TẠO CƠ CHẾ CHECKPOINT (RESUME) ---
    existing_evaluations = {}
    if os.path.exists(output_file_path):
        print(f"[*] Phát hiện file kết quả cũ '{output_file_path}'. Đang tiến hành đọc checkpoint để phục hồi trạng thái...")
        try:
            with open(output_file_path, 'r', encoding='utf-8') as f:
                old_data = json.load(f)
                for sample in old_data.get("per_sample", []):
                    if "judge_evaluation" in sample and "error" not in sample["judge_evaluation"]:
                        existing_evaluations[sample["id"]] = sample["judge_evaluation"]
            print(f"[+] Phục hồi thành công! Đã tìm thấy {len(existing_evaluations)} câu đã được chấm điểm trước đó.")
        except Exception as e:
            print(f"[Cảnh báo] Không thể đọc checkpoint cũ do lỗi: {str(e)}. Tiến hành chạy mới hoàn toàn.")

    # Đọc file dữ liệu gốc đầu vào
    print(f"[*] Đang tải dữ liệu thực nghiệm gốc từ file: {input_file_path}", flush=True)
    with open(input_file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
        
    model_name = data["metadata"]["model"]
    samples = data["per_sample"]
    
    print(f"[+] Mô hình thực nghiệm: {model_name} | Tổng quy mô dataset: {len(samples)} câu.", flush=True)
    processed_samples = []
    
    # Cấu trúc lưu trữ phục vụ báo cáo thống kê cuối cùng
    topic_scores = defaultdict(list)
    topic_errors = defaultdict(lambda: defaultdict(int))
    
    # Biến cờ kiểm soát lưu lũy tiến cụm 5 mẫu câu
    new_calls_count = 0
    unsaved_changes = False

    # Duyệt qua toàn bộ mẫu câu trong bộ dữ liệu sử dụng enumerate để lấy chỉ số vòng lặp
    for idx, sample in enumerate(tqdm(samples, desc="GPT-5.5 Resume-supported Judge"), start=1):
        sample_id = sample["id"]
        topic_name = sample.get("topic") if sample.get("topic") else "Unclassified"
        
        # KIỂM TRA CHECKPOINT: Nếu ID đã chạy thành công ở lần trước, lấy kết quả luôn và BỎ QUA call API
        if sample_id in existing_evaluations:
            judge_result = existing_evaluations[sample_id]
            sample["judge_evaluation"] = judge_result
            
            # Đưa vào bộ đếm thống kê bình thường để đảm bảo báo cáo cuối cùng đủ mẫu
            score = judge_result.get("mqm_report", {}).get("final_quality_score", 1)
            error_cat = judge_result.get("mqm_report", {}).get("primary_error_category", "None")
            topic_scores[topic_name].append(score)
            if error_cat != "None" and error_cat != "":
                topic_errors[topic_name][error_cat] += 1
                
            processed_samples.append(sample)
            continue # Nhảy sang câu kế tiếp lập tức
            
        # NẾU CHƯA CHẠY: Tiến hành thiết lập ngữ cảnh để gọi API gpt-5.5
        source_vi = sample["text"]
        reference_target = sample["label"][0] if isinstance(sample["label"], list) else sample["label"]
        
        # Thích ứng linh hoạt cấu trúc file Bahnar hoặc Khmer của anh
        hypothesis_target = ""
        if "hyp_vi_to_ba" in sample:
            hypothesis_target = sample["hyp_vi_to_ba"]
        elif "hyp_vi_to_km" in sample:
            hypothesis_target = sample["hyp_vi_to_km"]
        else:
            hypothesis_target = sample.get("translation", "")
            
        user_content = f"[Source Vietnamese]: {source_vi}\n[Human Reference]: {reference_target}\n[Translation Hypothesis]: {hypothesis_target}"
        
        # Gọi mô hình suy luận gpt-5.5
        raw_output = call_gpt5(client, SYSTEM_PROMPT, user_content)
        
        if raw_output:
            judge_result = extract_json_from_text(raw_output)
            sample["judge_evaluation"] = judge_result
            
            score = judge_result.get("mqm_report", {}).get("final_quality_score", 1)
            error_cat = judge_result.get("mqm_report", {}).get("primary_error_category", "None")
            
            topic_scores[topic_name].append(score)
            if error_cat != "None" and error_cat != "":
                topic_errors[topic_name][error_cat] += 1
        else:
            print(f"\n[Lỗi Kết Nối] Không nhận được phản hồi từ gpt-5.5 cho câu ID {sample_id}", flush=True)
            sample["judge_evaluation"] = {"error": "Empty response from gpt-5.5 API"}
            topic_scores[topic_name].append(1.0)
            
        processed_samples.append(sample)
        new_calls_count += 1
        unsaved_changes = True
        
        # --- CƠ CHẾ LƯU LŨY TIẾN MỖI 5 SAMPLES ---
        if new_calls_count % 5 == 0:
            temp_data = dict(data)
            temp_data["per_sample"] = processed_samples + samples[len(processed_samples):]
            with open(output_file_path, 'w', encoding='utf-8') as f:
                json.dump(temp_data, f, ensure_ascii=False, indent=2)
            unsaved_changes = False

    # LƯU ĐỢT CUỐI: Đảm bảo nếu tổng số câu gọi mới không chia hết cho 5 thì vẫn được lưu trọn vẹn
    if unsaved_changes:
        print("\n[*] Đang lưu các mẫu câu cuối cùng vào checkpoint...", flush=True)
        temp_data = dict(data)
        temp_data["per_sample"] = processed_samples + samples[len(processed_samples):]
        with open(output_file_path, 'w', encoding='utf-8') as f:
            json.dump(temp_data, f, ensure_ascii=False, indent=2)
            
    # --- TÍNH TOÁN VÀ ĐÓNG GÓI BÁO CÁO TỔNG KẾT CUỐI CÙNG (SAU KHI TOÀN BỘ DATASET HOÀN THÀNH) ---
    print("\n" + "="*60, flush=True)
    print("📊 BÁO CÁO THỐNG KÊ CHẤT LƯỢNG DỊCH GPT-5.5 JUDGE THEO CHỦ ĐỀ (TOPIC)", flush=True)
    print("="*60, flush=True)
    
    stats_summary = {}
    for topic, scores in topic_scores.items():
        avg_score = sum(scores) / len(scores) if scores else 0
        total_samples_in_topic = len(scores)
        
        print(f"\n📌 Topic: {topic} (Tổng số mẫu: {total_samples_in_topic})", flush=True)
        print(f"   └── Điểm Chất lượng Trung bình (1-5): {avg_score:.2f} / 5.0", flush=True)
        print(f"   └── Phân phối lỗi MQM phát hiện bởi GPT-5.5:", flush=True)
        
        errors_dict = dict(topic_errors[topic])
        if errors_dict:
            for err, count in errors_dict.items():
                print(f"       * {err}: {count} lần", flush=True)
        else:
            print("       * Không phát hiện lỗi hệ thống nghiêm trọng.", flush=True)
            
        stats_summary[topic] = {
            "average_quality_score": round(avg_score, 2),
            "total_samples": total_samples_in_topic,
            "detected_error_distribution": errors_dict
        }

    # Đóng gói và lưu trữ báo cáo hoàn chỉnh cuối cùng vào file đầu ra
    data["per_sample"] = processed_samples
    data["metadata"]["judge_model"] = "gpt-5.5"
    data["metadata"]["judge_status"] = "fully_evaluated_by_llm_as_a_judge"
    data["metadata"]["score_range"] = "1-5 (Likert Quality Scale)"
    data["topic_analysis_report"] = stats_summary
    
    with open(output_file_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
        
    print("\n" + "="*60, flush=True)
    print(f"[+] Pipeline hoàn tất thành công 100% dataset! Không có mẫu nào bị bỏ sót.", flush=True)
    print(f"[+] File kết quả làm giàu cuối cùng lưu tại: {output_file_path}", flush=True)
    print("="*60, flush=True)

# --- KHỞI CHẠY PIPELINE ---
if __name__ == "__main__":
    input_file = r"D:\Code\Python\Research\MachineTranslation\MT\MT2\bahnar\results\expALL_twoway_zeroshot_bahnar_gpt5_at_home.json"
    output_file = r"D:\Code\Python\Research\MachineTranslation\MT\MT2\eval\results\evaluated_bahnar_quality_score_1_5_gpt5.json"
    
    if os.path.exists(input_file):
        evaluate_pipeline(input_file, output_file)
    else:
        print(f"[Lỗi] Không tìm thấy file dữ liệu gốc '{input_file}'. Hãy kiểm tra lại cấu trúc đường dẫn.")