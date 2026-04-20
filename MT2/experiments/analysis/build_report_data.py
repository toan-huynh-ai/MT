"""Collect data for the 3-layer Khmer report.

Outputs:
  1. Topic statistics (Vietnamese + English + sample counts + Krom evidence counts).
     Samples without a topic label are assigned to "Ăn uống" (Eating).
  2. 25 "clean" samples: GPT-4o produces a reasonable standard Khmer output
     for content that is culturally neutral / Layer-1.
  3. 25 "culture-fail" samples: REF carries a Khmer-Vietnamese marker and
     GPT-4o drops it (variety collapse).

Everything is saved to results/report_data.json so that the MD file can
reference it directly.
"""
from __future__ import annotations
import json
import random
import sys
from collections import defaultdict
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")

HERE = Path(__file__).resolve().parents[2]
RESULTS = HERE / "results" / "gpt4o_full_1856.json"
OUT = HERE / "results" / "report_data.json"

KROM_MARKERS = {
    "kinship_colloq":    ["ម៉ែ", "ម៉ាក់", "ប៉ា"],
    "ethnonym_kinh":     ["គិញ"],
    "toponym_krom":      [
        "ទ្រីតុង", "ទ្រីតូន", "សុកត្រាំង", "ខេត្តឃ្លាំង",
        "ព្រះត្រពាំង", "ត្រាវិញ", "អានយ៉ាង", "គៀងយ៉ាង", "គៀនយ៉ាង",
        "មាត់ជ្រូក", "បាយ៉ង់", "ហូវហ្សាង", "កាម៉ៅ",
        "ក្រុងហូជីមិញ", "បាកលៀវ", "ឡុងអាន", "ផ្សារទីញបៀន",
    ],
    "food_krom":         [
        "ម៉ាំប្រហុក", "អំបុក", "នំបង់ខ្លាញ់", "នំបញ្ចុកទឹកសម្ល",
        "នំបំពង់ឫស្សី", "នំគម", "នំអន្សោម", "នំអន្សម",
        "នំខ្ញី", "បាយឡាំ",
    ],
    "boat_racing":       ["ទូកង", "ទូកអុំ", "ប្រណាំងទូកង", "ប្រណាំងទូកអុំ"],
    "festival_krom":     [
        "អកអំបុក", "បុណ្យអកអំបុក", "សែនដូនតា",
        "ពិធីបុណ្យកឋិនទាន", "បុណ្យភ្ជុំបិណ្ឌ",
    ],
    "krom_religious":    ["អ្នកតា", "ភូមិសង្គម", "ព្រះឥសូរ", "ព្រះឥសូ"],
    "vn_loanword":       ["អ៊ុយបាន", "ដែនដីសណ្ដរទន្លេមេគង្គ", "តំបន់មាត់ទន្លេ"],
    "krom_ethno_label":  ["ខ្មែរក្រោម", "ខ្មែរណាមបូ"],
    "nam_bo_vn_translit": ["ណាមបូ", "យុគី"],
}


# Mapping raw dataset topic labels to (English canonical, Vietnamese canonical).
TOPIC_MAP = {
    # Meals (Q&A area - will also receive samples with no topic)
    "breakfast": ("Breakfast", "Bữa sáng"),
    "lunch": ("Lunch", "Bữa trưa"),
    "dinner": ("Dinner", "Bữa tối"),
    "snack": ("Snack", "Ăn vặt"),
    "souvenirs food": ("Souvenir foods", "Đồ ăn lưu niệm"),
    "traditional food and drinks": ("Traditional foods and drinks", "Đồ ăn và đồ uống truyền thống"),
    "eating habit": ("Eating habits", "Thói quen ăn uống"),
    "eating utensils": ("Eating utensils", "Dụng cụ ăn uống"),
    "cooking utensils": ("Cooking utensils", "Dụng cụ nấu ăn"),
    "fruits": ("Fruits", "Trái cây"),
    # Wedding
    "phong tục trước đám cưới": ("Pre-wedding customs", "Phong tục trước khi kết hôn"),
    "phong tục khi kết hôn": ("Wedding customs", "Phong tục khi kết hôn"),
    "phong tục sau khi đám cưới": ("Post-wedding customs", "Phong tục sau khi kết hôn"),
    "trang phục cưới hỏi nam": ("Groom wedding attire", "Trang phục cưới hỏi nam"),
    "trang phục cưới hỏi nữ": ("Bride wedding attire", "Trang phục cưới hỏi nữ"),
    "khách mời đám cưới": ("Wedding guests", "Khách mời đám cưới"),
    "vị trí tổ chức đám cưới": ("Wedding venue", "Vị trí tổ chức đám cưới"),
    "đồ ăn ở đám cưới": ("Wedding cuisine", "Ẩm thực đám cưới"),
    "quà cưới": ("Wedding gifts", "Quà cưới"),
    # Family
    "mối quan hệ trong gia đình chính": ("Immediate family relationships", "Mối quan hệ trong gia đình chính"),
    "mối quan hệ trong gia đình mở rộng": ("Extended family relationships", "Mối quan hệ trong gia đình mở rộng"),
    "mối quan hệ với xã hội/ hàng xóm": ("Society & neighbours", "Mối quan hệ với xã hội/hàng xóm"),
    "gia tộc/hậu duệ": ("Clan & descendants", "Gia tộc/hậu duệ"),
    "parents and children interactions as adult": ("Parent–adult-child interactions", "Tương tác giữa cha mẹ và con cái khi trưởng thành"),
    # Pregnancy & childcare
    "traditions during pregnancy": ("Pregnancy customs", "Phong tục khi mang bầu"),
    "traditions after birth": ("Postnatal customs", "Phong tục sau khi đẻ con"),
    "how to care for a newborn baby": ("Newborn care", "Cách chăm sóc trẻ sơ sinh"),
    "how to care for toddlers": ("Toddler care", "Cách chăm sóc trẻ mới biết đi"),
    "how to care for children": ("Child care", "Cách chăm sóc trẻ em"),
    "how to care for teenagers": ("Teenager care", "Cách chăm sóc trẻ vị thành niên"),
    # Death
    "when death occurs": ("When death occurs", "Khi có người mất"),
    "process of dealing with corpse": ("Corpse-handling process", "Quy trình xử lý thi thể"),
    "traditions after the body is buried": ("Post-burial customs", "Phong tục sau khi chôn cất"),
    "the clothes of the mourners": ("Mourner attire", "Trang phục của người đưa tang"),
    "inheritance matters": ("Inheritance matters", "Vấn đề thừa kế"),
    # Religious holidays
    "traditions before religious holidays": ("Pre-holiday customs", "Những phong tục trước ngày lễ tôn giáo"),
    "traditions leading up to religious holidays": ("Holiday preparation customs", "Những phong tục chuẩn bị cho ngày lễ tôn giáo"),
    "traditions during religious holidays": ("Day-of holiday customs", "Những phong tục ngay ngày lễ tôn giáo"),
    "traditions after religious holidays": ("Post-holiday customs", "Những phong tục sau ngày lễ tôn giáo"),
    # Agriculture / trade
    "what plants to grow": ("Plant choice", "Nên trồng cây gì"),
    "traditions when planting": ("Planting customs", "Phong tục khi trồng trọt"),
    "harvest": ("Harvesting", "Thu hoạch"),
    "truyền thống chăm sóc vật nuôi/thủy sản": (
        "Livestock & aquaculture care",
        "Truyền thống chăm sóc vật nuôi/thủy sản",
    ),
    "truyền thống mua bán": ("Trade traditions", "Truyền thống mua bán"),
    # Arts
    "musical instruments": ("Musical instruments", "Nhạc cụ"),
    "folk songs": ("Folk songs", "Dân ca"),
    "traditional dances": ("Traditional dances", "Các điệu múa truyền thống"),
    "use of art at certain events": ("Art at events", "Biểu diễn nghệ thuật tại một số sự kiện nhất định"),
    "poetry or similar literature": ("Poetry or similar literature", "Thơ hoặc văn học tương tự"),
    # Games / daily life
    "game types": ("Game types", "Các loại trò chơi"),
    "location played": ("Play locations", "Vị trí chơi"),
    "morning activities": ("Morning activities", "Hoạt động buổi sáng"),
    "afternoon activities": ("Afternoon activities", "Hoạt động buổi chiều"),
    "evening activities": ("Evening activities", "Hoạt động buổi tối"),
    "leisure activities": ("Leisure activities", "Hoạt động giải trí"),
    "house, household and transportation": ("Household & transport", "Nhà cửa, gia đình và giao thông"),
    # Religion / lifestyle
    "regular religious activities": ("Regular religious life", "Sinh hoạt tôn giáo thường kỳ"),
    "mystical things": ("Mystical beliefs", "Những điều huyền bí"),
    "traditional ceremonies": ("Traditional ceremonies", "Nghi lễ truyền thống"),
    "lifestyle": ("Lifestyle", "Lối sống"),
    "self care": ("Self-care", "Cách tự chăm sóc"),
    "traditional medicine": ("Traditional medicine", "Y học cổ truyền"),
    "traditional sayings": ("Traditional sayings", "Những câu nói truyền thống"),
    # Fallbacks
    "unknown": ("Unknown", "Không xác định"),
}


def norm(s: str) -> str | None:
    if s is None:
        return None
    return " ".join(str(s).strip().lower().split())


def has_any(text: str, patterns: list[str]) -> bool:
    if not text:
        return False
    return any(p in text for p in patterns)


def krom_markers_in_ref(ref: str) -> list[str]:
    cats = []
    for cat, pats in KROM_MARKERS.items():
        if has_any(ref, pats):
            cats.append(cat)
    return cats


def dropped_markers(ref: str, hyp: str) -> list[str]:
    dropped = []
    for cat, pats in KROM_MARKERS.items():
        if has_any(ref, pats) and not has_any(hyp, pats):
            dropped.append(cat)
    return dropped


def canon_topic(raw: str | None) -> tuple[str, str]:
    if not raw:
        return ("Eating (Q&A)", "Ăn uống")
    key = norm(raw)
    return TOPIC_MAP.get(key, (raw.strip(), raw.strip()))


def main() -> None:
    data = json.loads(RESULTS.read_text(encoding="utf-8"))
    per = data["per_sample"]

    # Per-canonical-topic stats
    stats: dict[tuple, dict] = defaultdict(lambda: {"total": 0, "ref_krom": 0, "dropped": 0})
    clean_pool: list[dict] = []
    fail_pool: list[dict] = []

    for r in per:
        ref = r.get("reference") or ""
        hyp = r.get("hyp_plain") or ""
        topic_en, topic_vi = canon_topic(r.get("topic"))

        s = stats[(topic_en, topic_vi)]
        s["total"] += 1

        ref_cats = krom_markers_in_ref(ref)
        if ref_cats:
            s["ref_krom"] += 1
        drops = dropped_markers(ref, hyp)
        if drops:
            s["dropped"] += 1

        chrf = r.get("eval_plain", {}).get("standard_metrics", {}).get("chrf++", 0) or 0
        cuea = (r.get("eval_plain", {}).get("cuea", {}) or {}).get("cuea")

        # Candidate for "fail" pool
        if drops and len(hyp) > 20:
            fail_pool.append({
                "topic_en": topic_en,
                "topic_vi": topic_vi,
                "source": r["source"],
                "reference": ref,
                "hyp_plain": hyp,
                "dropped_categories": drops,
                "chrf": chrf,
                "cuea": cuea,
            })

        # Candidate for "clean" pool: no Krom marker in REF, reasonable chrf,
        # and either no entities or all entities correct.
        is_clean_entities = (cuea is None) or (cuea == 1.0)
        if (not ref_cats) and chrf >= 35 and is_clean_entities and len(hyp) > 30:
            clean_pool.append({
                "topic_en": topic_en,
                "topic_vi": topic_vi,
                "source": r["source"],
                "reference": ref,
                "hyp_plain": hyp,
                "chrf": chrf,
                "cuea": cuea,
            })

    # Stratified sampling to diversify topics in each pool
    def stratified_pick(pool: list[dict], n: int, seed: int) -> list[dict]:
        random.seed(seed)
        by_topic: dict[str, list[dict]] = defaultdict(list)
        for item in pool:
            by_topic[item["topic_en"]].append(item)
        for t in by_topic:
            random.shuffle(by_topic[t])
        picks: list[dict] = []
        while len(picks) < n and any(by_topic.values()):
            for t in list(by_topic):
                if by_topic[t] and len(picks) < n:
                    picks.append(by_topic[t].pop(0))
        return picks

    clean_picks = stratified_pick(clean_pool, 25, seed=11)
    fail_picks = stratified_pick(fail_pool, 25, seed=12)

    # Serialize stats
    rows = []
    for (en, vi), s in stats.items():
        rows.append({
            "topic_en": en,
            "topic_vi": vi,
            "total": s["total"],
            "ref_has_krom": s["ref_krom"],
            "gpt4o_dropped": s["dropped"],
            "drop_rate": round(s["dropped"] * 100 / max(s["ref_krom"], 1), 1) if s["ref_krom"] else 0,
        })
    rows.sort(key=lambda x: -x["total"])

    totals = {
        "total_samples": sum(r["total"] for r in rows),
        "ref_has_krom": sum(r["ref_has_krom"] for r in rows),
        "gpt4o_dropped": sum(r["gpt4o_dropped"] for r in rows),
    }
    totals["drop_rate_percent"] = round(
        totals["gpt4o_dropped"] * 100 / max(totals["ref_has_krom"], 1), 1
    )

    dump = {
        "totals": totals,
        "topic_stats": rows,
        "clean_samples": clean_picks,
        "fail_samples": fail_picks,
        "pool_sizes": {"clean_pool": len(clean_pool), "fail_pool": len(fail_pool)},
    }
    OUT.write_text(json.dumps(dump, ensure_ascii=False, indent=2), encoding="utf-8")

    print("TỔNG SỐ MẪU :", totals["total_samples"])
    print("REF có Krom :", totals["ref_has_krom"])
    print("GPT-4o drop :", totals["gpt4o_dropped"], f"({totals['drop_rate_percent']}%)")
    print()
    print("Chủ đề có mẫu:", len(rows))
    print("Top 10 theo số mẫu:")
    for r in rows[:10]:
        print(f"  {r['total']:>4}  {r['topic_en']:<35}  {r['topic_vi']}")
    print()
    print("Pool clean:", len(clean_pool), " Pool fail:", len(fail_pool))
    print("Đã chọn", len(clean_picks), "mẫu clean và", len(fail_picks), "mẫu fail")
    print("Saved:", OUT)


if __name__ == "__main__":
    main()
