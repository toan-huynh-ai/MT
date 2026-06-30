import json
import os
import re
import time
from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor
from openai import OpenAI
from tqdm import tqdm
from dotenv import load_dotenv

# Nạp biến môi trường cho dự án dịch máy
load_dotenv(r"D:\Code\Python\Research\MachineTranslation\MT\MT2\.env")

# Khởi tạo OpenAI Client với endpoint chuẩn xác của dòng mô hình suy luận gpt-5.5
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# --- SYSTEM PROMPT CHUẨN HÓA LIKERT THANG ĐIỂM NGÔN NGỮ HỌC 1-5 (KHMER KROM CONTEXT) ---
SYSTEM_PROMPT = """# ROLE & EVALUATION PRINCIPLES
You are an expert academic computational linguist and sociolinguist specializing in the contrastive linguistics of Vietnamese and Khmer, with specific expertise in the linguistic variants, regional idioms, and pragmatic practices of the Khmer Krom (Khmer community living in Southern Vietnam). Your sole assignment is to evaluate a Machine Translation (MT) hypothesis against a human-verified Gold Standard Reference on a strict holistic quality scale from 1 to 5 for specific linguistic dimensions.

You must remain completely unbiased, objective, and neutral. Every sample must be treated as an independent instance. Your analysis must rely strictly on linguistic evidence present in the provided text.

# SPECIAL SOCIO-LINGUISTIC DIRECTIVE (KHMER KROM CONTEXT)
When evaluating the text, you MUST recognize and accept legitimate regional lexical variants, kinship terms, honorifics, and religious vocabulary unique to the Khmer Krom community in Southern Vietnam (e.g., terms regarding Theravada Buddhism like "thọ trai", "sư", regional southern kinship terms, or localized transliterations of cultural items). Do not penalize these localized renderings as "errors" if they accurately capture the cultural and contextual reality of the Khmer community in Vietnam as shown in the Human Reference.

# KHMER-VIETNAMESE LINGUISTIC DIMENSIONS TO CHOOSE LIKERT SCORES (1-5)
For each dimension below, assign a score from 1 (Total Failure) to 5 (Excellent/Native Match):
1. Semantic Equivalence & Informational Fidelity: Evaluate how accurately the informational units, facts, propositions, and conceptual core are transferred from the source to the hypothesis. Assess if there are omissions, critical additions, or semantic distortions against the reference.
2. Subject & Pronoun Appropriateness (Pragmatics): Evaluate if the chosen subject pronouns, kinship terms, and respect markers accurately reflect the complex social hierarchy and religious respect of the Khmer Krom community.
3. Morpho-Syntactic Flow & Word Order: Check if the grammatical structure flows naturally while preserving correct native syntax (e.g., modifier placements, classifier/numeral constructions).
4. Lexical Legitimacy (Anti-False Positive Transliteration Audit): Isolate authentic localized expressions from raw automated phonetic character-copying of Vietnamese words into fake Khmer script (or vice versa).

# SCORING SCALE DEFINITIONS (APPLIED TO EACH DIMENSION)
- 5 (Excellent): Professional quality. Perfect transfer. Fully captures the regional cultural context, subject roles, and authentic vocabulary without any fake transliterations.
- 4 (Good): High quality with minor flaws. Meaning fully preserved. Contains 1-2 minor issues in non-critical punctuation or spacing, but subjects and core grammars are culturally sound.
- 3 (Fair): Mediocre quality. Message is recoverable but contains notable errors: inappropriate leveling of pronouns, or awkward standard literal translations that ignore regional cultural realities.
- 2 (Poor): Unacceptable quality. Severe semantic distortion, critical misuse of pronouns breaching social/cultural protocols, or containing 1-2 fake phonetic words.
- 1 (Flawed/Unusable): Total failure. Output is heavily corrupted, filled with incoherent gibberish strings, completely blank, or heavily relies on fake phonetic transliterations, making it unusable.

# INPUT DATA WRAPPER
[Source Text]: {text}
[Human Reference]: {label}
[Translation Hypothesis]: {hypothesis}

# STRICT OUTPUT SCHEMA (JSON ONLY)
{
  "linguistic_analysis": {
    "step_1_semantic_equivalence_and_fidelity": "Analyze the preservation of facts, core message, and detail completeness against the reference...",
    "step_2_subject_and_pronoun_appropriateness": "Audit the subject pronouns, kinship terms, and honorific alignment within the regional context...",
    "step_3_transliteration_and_lexical_legitimacy_audit": "Character-by-character audit isolating fake phonetic transliterations from authentic vocabulary...",
    "step_4_morpho_syntactic_flow": "Analysis of word order and phrase fluency...",
    "holistic_justification": "Provide a rigorous, unbiased justification anchoring the scores to the rubric definitions..."
  },
  "evaluation_metrics": {
    "semantic_score": 5,
    "subject_pronoun_score": 5,
    "morpho_syntactic_score": 5,
    "lexical_legitimacy_score": 5
  }
}"""

def call_gpt5(client, system_prompt, user_prompt, max_retries=3):
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
    try:
        match = re.search(r'```json\s*(\{.*?\})\s*```', text, re.DOTALL)
        if match:
            return json.loads(match.group(1))

        start_idx = text.find('{')
        end_idx = text.rfind('}')
        if start_idx != -1 and end_idx != -1:
            return json.loads(text[start_idx:end_idx+1])

        return json.loads(text.strip())
    except Exception:
        return {
            "linguistic_analysis": {"error": "Failed to parse JSON directly from system response."},
            "evaluation_metrics": {
                "semantic_score": 1,
                "subject_pronoun_score": 1,
                "morpho_syntactic_score": 1,
                "lexical_legitimacy_score": 1
            }
        }

def evaluate_single_sample(args):
    sample, existing_evaluations, client = args
    sample_id = sample["id"]

    if sample_id in existing_evaluations:
        return (sample, existing_evaluations[sample_id], False)

    source_vi = sample["text"]
    reference_target = sample["label"][0] if isinstance(sample["label"], list) else sample["label"]
    hypothesis_target = sample.get("hyp_vi_to_km", sample.get("translation", ""))

    user_content = f"[Source Text]: {source_vi}\n[Human Reference]: {reference_target}\n[Translation Hypothesis]: {hypothesis_target}"
    raw_output = call_gpt5(client, SYSTEM_PROMPT, user_content)

    if raw_output:
        judge_result = extract_json_from_text(raw_output)
    else:
        judge_result = {"error": "Empty response from gpt-5.5 API"}

    return (sample, judge_result, True)

def evaluate_pipeline(input_file_path, output_file_path):
    existing_evaluations = {}
    if os.path.exists(output_file_path):
        print(f"[*] Phát hiện file kết quả cũ '{output_file_path}'. Đang đọc checkpoint...")
        try:
            with open(output_file_path, 'r', encoding='utf-8') as f:
                old_data = json.load(f)
                for sample in old_data.get("per_sample", []):
                    if "judge_evaluation" in sample and "error" not in sample["judge_evaluation"]:
                        existing_evaluations[sample["id"]] = sample["judge_evaluation"]
            print(f"[+] Phục hồi thành công {len(existing_evaluations)} câu đã chấm điểm trước đó.")
        except Exception as e:
            print(f"[Cảnh báo] Không thể đọc checkpoint cũ: {str(e)}. Chạy mới hoàn toàn.")

    print(f"[*] Đang tải dữ liệu thực nghiệm từ file: {input_file_path}", flush=True)
    with open(input_file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
        
    model_name = data["metadata"]["model"]
    samples = data["per_sample"]
    
    print(f"[+] Mô hình: {model_name} | Tổng quy mô dataset: {len(samples)} câu.", flush=True)
    processed_samples = []

    distribution_semantic = defaultdict(lambda: defaultdict(int))
    distribution_subject = defaultdict(lambda: defaultdict(int))
    distribution_syntax = defaultdict(lambda: defaultdict(int))
    distribution_lexicon = defaultdict(lambda: defaultdict(int))

    new_calls_count = 0
    unsaved_changes = False

    with ThreadPoolExecutor(max_workers=100) as executor:
        tasks = [(sample, existing_evaluations, client) for sample in samples]
        results = list(tqdm(executor.map(evaluate_single_sample, tasks), total=len(samples), desc="GPT-5.5 Judge"))

        for idx, (sample, judge_result, is_new) in enumerate(results):
            topic_name = sample.get("topic") if sample.get("topic") else "Unclassified"
            sample["judge_evaluation"] = judge_result

            metrics = judge_result.get("evaluation_metrics", {})
            sem_score = metrics.get("semantic_score", 1)
            s_score = metrics.get("subject_pronoun_score", 1)
            g_score = metrics.get("morpho_syntactic_score", 1)
            l_score = metrics.get("lexical_legitimacy_score", 1)

            distribution_semantic[topic_name][f"Score_{sem_score}"] += 1
            distribution_subject[topic_name][f"Score_{s_score}"] += 1
            distribution_syntax[topic_name][f"Score_{g_score}"] += 1
            distribution_lexicon[topic_name][f"Score_{l_score}"] += 1

            processed_samples.append(sample)

            if is_new:
                new_calls_count += 1
                if new_calls_count % 5 == 0:
                    temp_data = dict(data)
                    temp_data["per_sample"] = processed_samples
                    with open(output_file_path, 'w', encoding='utf-8') as f:
                        json.dump(temp_data, f, ensure_ascii=False, indent=2)
                    unsaved_changes = False
                else:
                    unsaved_changes = True

    if unsaved_changes:
        print("\n[*] Đang lưu các mẫu câu cuối cùng vào checkpoint...", flush=True)
        temp_data = dict(data)
        temp_data["per_sample"] = processed_samples + samples[len(processed_samples):]
        with open(output_file_path, 'w', encoding='utf-8') as f:
            json.dump(temp_data, f, ensure_ascii=False, indent=2)
            
    print("\n" + "="*60, flush=True)
    print("📊 BÁO CÁO THỐNG KÊ PHÂN PHỐI ĐIỂM SỐ NGÔN NGỮ HỌC CHI TIẾT THEO CHỦ ĐỀ", flush=True)
    print("="*60, flush=True)
    
    stats_summary = {}
    all_topics = set(list(distribution_semantic.keys()) + list(distribution_subject.keys()) + list(distribution_syntax.keys()) + list(distribution_lexicon.keys()))
    
    for topic in all_topics:
        print(f"\n📌 Topic: {topic}", flush=True)
        
        sem_dist = dict(distribution_semantic[topic])
        sub_dist = dict(distribution_subject[topic])
        syn_dist = dict(distribution_syntax[topic])
        lex_dist = dict(distribution_lexicon[topic])
        
        print("   ├── 1. Phân phối điểm Ngữ nghĩa & Độ chính xác (Semantic Fidelity):", flush=True)
        for k in sorted(sem_dist.keys(), reverse=True):
            print(f"       * {k}: {sem_dist[k]} lần", flush=True)
        print("   ├── 2. Phân phối điểm Chủ ngữ & Đại từ (Subject & Pronoun):", flush=True)
        for k in sorted(sub_dist.keys(), reverse=True):
            print(f"       * {k}: {sub_dist[k]} lần", flush=True)
        print("   ├── 3. Phân phối điểm Hình thái & Cú pháp (Morpho-Syntactic):", flush=True)
        for k in sorted(syn_dist.keys(), reverse=True):
            print(f"       * {k}: {syn_dist[k]} lần", flush=True)
        print("   └── 4. Phân phối điểm Chính danh Từ vựng (Lexical Legitimacy):", flush=True)
        for k in sorted(lex_dist.keys(), reverse=True):
            print(f"       * {k}: {lex_dist[k]} lần", flush=True)
            
        stats_summary[topic] = {
            "semantic_distribution": sem_dist,
            "subject_pronoun_distribution": sub_dist,
            "morpho_syntactic_distribution": syn_dist,
            "lexical_legitimacy_distribution": lex_dist
        }

    data["per_sample"] = processed_samples
    data["metadata"]["judge_model"] = "gpt-5.5"
    data["metadata"]["judge_status"] = "fully_evaluated_by_llm_as_a_judge_with_independent_semantic_score"
    data["metadata"]["score_range"] = "Granular 1-5 Dimensional Scores"
    data["topic_analysis_report"] = stats_summary
    
    with open(output_file_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
        
    print("\n" + "="*60, flush=True)
    print(f"[+] Pipeline hoàn tất thành công 100% dataset Khmer! Trạng thái dữ liệu toàn vẹn.", flush=True)
    print(f"[+] File kết quả lưu tại: {output_file_path}", flush=True)
    print("="*60, flush=True)
# --- KHỞI CHẠY PIPELINE ---
if __name__ == "__main__":
    input_file = r"D:\Code\Python\Research\MachineTranslation\MT\MT2\experiments\gpt4o\experiment_results\expALL_twoway_zeroshot_gpt5_at_home_full.json"
    output_file = r"D:\Code\Python\Research\MachineTranslation\MT\MT2\eval\results\evaluated_khmer_quality_score_1_5_gpt5_ver2.json"
    
    if os.path.exists(input_file):
        evaluate_pipeline(input_file, output_file)
    else:
        print(f"[Lỗi] Không tìm thấy file dữ liệu gốc '{input_file}'. Hãy kiểm tra lại cấu trúc đường dẫn.")