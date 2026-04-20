"""Render docs/15_bao_cao_3_lop_khmer.md from results/report_data.json.

The report has four sections:
  1. Three-layer model of the Khmer language.
  2. Cambodian Khmer vs Khmer-Vietnamese (Krom) differences.
  3. Topic distribution table with English + Vietnamese columns.
  4. 25 "clean" samples and 25 "culture-fail" samples.
     Each fail sample carries a Vietnamese explanation of why it is wrong.
"""
from __future__ import annotations
import json
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")

HERE = Path(__file__).resolve().parents[2]
DATA = HERE / "results" / "report_data.json"
OUT = HERE / "docs" / "15_bao_cao_3_lop_khmer.md"

# User's canonical 63-topic list used to order the statistics table.
CANONICAL_ORDER_VI = [
    "Ăn uống",
    "Thói quen ăn uống",
    "Đồ ăn và đồ uống truyền thống",
    "Đồ ăn lưu niệm",
    "Dụng cụ ăn uống",
    "Dụng cụ nấu ăn",
    "Trái cây",
    "Phong tục trước khi kết hôn",
    "Phong tục khi kết hôn",
    "Phong tục sau khi kết hôn",
    "Trang phục cưới hỏi nam",
    "Trang phục cưới hỏi nữ",
    "Khách mời đám cưới",
    "Vị trí tổ chức đám cưới",
    "Ẩm thực đám cưới",
    "Quà cưới",
    "Mối quan hệ trong gia đình chính",
    "Mối quan hệ trong gia đình mở rộng",
    "Mối quan hệ với xã hội/hàng xóm",
    "Gia tộc/hậu duệ",
    "Tương tác giữa cha mẹ và con cái khi trưởng thành",
    "Phong tục khi mang bầu",
    "Phong tục sau khi đẻ con",
    "Cách chăm sóc trẻ sơ sinh",
    "Cách chăm sóc trẻ mới biết đi",
    "Cách chăm sóc trẻ em",
    "Cách chăm sóc trẻ vị thành niên",
    "Khi có người mất",
    "Quy trình xử lý thi thể",
    "Phong tục sau khi chôn cất",
    "Trang phục của người đưa tang",
    "Vấn đề thừa kế",
    "Những phong tục trước ngày lễ tôn giáo",
    "Những phong tục chuẩn bị cho ngày lễ tôn giáo",
    "Những phong tục ngay ngày lễ tôn giáo",
    "Những phong tục sau ngày lễ tôn giáo",
    "Nên trồng cây gì",
    "Phong tục khi trồng trọt",
    "Thu hoạch",
    "Truyền thống chăm sóc vật nuôi/thủy sản",
    "Truyền thống mua bán",
    "Nhạc cụ",
    "Dân ca",
    "Các điệu múa truyền thống",
    "Biểu diễn nghệ thuật tại một số sự kiện nhất định",
    "Thơ hoặc văn học tương tự",
    "Các loại trò chơi",
    "Vị trí chơi",
    "Hoạt động buổi sáng",
    "Hoạt động buổi chiều",
    "Hoạt động buổi tối",
    "Hoạt động giải trí",
    "Nhà cửa, gia đình và giao thông",
    "Sinh hoạt tôn giáo thường kỳ",
    "Những điều huyền bí",
    "Nghi lễ truyền thống",
    "Lối sống",
    "Cách tự chăm sóc",
    "Y học cổ truyền",
    "Những câu nói truyền thống",
]


# Explanations for the 25 fail samples. Matched by a stable prefix of the
# Vietnamese source so the mapping survives reshuffling.
FAIL_EXPLANATIONS: list[tuple[str, str]] = [
    (
        "Tôi còn nhớ năm 2020, Tôi tham gia đoàn đi dự lễ Khánh thành",
        "REF giữ cách phiên âm địa danh Nam Bộ mà cộng đồng Khmer ĐBSCL đã "
        "dùng quen: `ទ្រីតុង` (Tri Tôn), `អានយ៉ាង` (An Giang), `ទីញបៀន` "
        "(Tịnh Biên). GPT-4o không biết dạng chuẩn này nên tự đặt phiên âm "
        "khác: `ទ្រីតន`, `អនជាង`, `តិញបៀន`. Với người Khmer Nam Bộ, các "
        "dạng của GPT-4o nghe như tên lạ.",
    ),
    (
        "- Khi về nhà chồng, ngoài việc đôi tân hôn được rải nước thơm",
        "Trong văn hoá Khmer Nam Bộ, \"lễ cúng tổ tiên\" có tên chuyên "
        "biệt là `ពិធីសែនដូនតា` (Sen Dolta, được REF dùng). GPT-4o dịch "
        "word-for-word thành `បូជាឪពុកម្តាយ` (cúng cha mẹ) — tuy đúng "
        "nghĩa đen nhưng mất tên riêng của nghi lễ truyền thống của cộng "
        "đồng. Ngoài ra, GPT cũng dịch \"nghi thức truyền thống\" thành "
        "`ពិធីសាសនាបុរាណ` (nghi lễ tôn giáo cổ) — chuyển khung khái niệm "
        "từ văn hoá sang tôn giáo, lệch so với bản gốc.",
    ),
    (
        "Nó vừa là phương tiện buôn bán, vận chuyển nông sản, vừa là hình ảnh",
        "\"Ghe ngo\" là loại thuyền đặc trưng của Phật giáo Nam tông "
        "Khmer ĐBSCL, có tên chuẩn là `ទូកង` (REF dùng đúng). GPT-4o "
        "viết `ទូកងូរ` (thêm âm `ូរ`), làm sai tên riêng của một hiện "
        "vật văn hoá. Lỗi này nhỏ về ký tự nhưng nặng về ngữ cảnh: nó "
        "biến một từ chuyên biệt thành một từ không có trong từ vựng "
        "Khmer chuẩn.",
    ),
    (
        "Chúng tôi thường thờ cúng Neak Ta, tin rằng vị thần bảo hộ làng",
        "`អ្នកតា` (Neak Ta) là tên thần bảo hộ làng trong tín ngưỡng "
        "Khmer Nam Bộ, REF dùng đúng chữ Khmer. GPT-4o lại **giữ nguyên "
        "phiên âm Latin** `Neak Ta` trong một câu tiếng Khmer — nghĩa "
        "là nó không nhận ra đây vốn là thuật ngữ Khmer, chỉ coi đó là "
        "tên riêng nước ngoài. Đây là lỗi nặng vì độ tinh khiết chữ "
        "viết (Khmer thuần) bị phá.",
    ),
    (
        "Có chứ chị. Dịp lễ Sen Dolta hay Ok Om Bok",
        "Hai lễ hội Khmer Nam Bộ có tên chuẩn trong cộng đồng: "
        "`សែនដូនតា` (Sen Dolta) và `អកអំបុក` (Ok Om Bok). GPT-4o viết "
        "sai thành `សែនដុលតា` và `អុកអុំបុក` — chuyển phiên âm gần "
        "với cách đọc tiếng Việt hơn là cách viết đã định hình trong "
        "cộng đồng Khmer. `អកអំបុក` có gốc từ `អក` (vỗ) + `អំបុក` "
        "(cốm dẹp) và mô tả chính nghi lễ, còn `អុកអុំបុក` của GPT "
        "không có nghĩa rõ.",
    ),
    (
        "Người phỏng vấn: Vậy hình thức sân khấu có được tổ chức trong dịp lễ Sen Dolta",
        "Lặp lại lỗi Sen Dolta: REF `សែនដូនតា`, HYP `សែនដុលតា`. Lỗi "
        "xuất hiện lặp lại nhiều lần cho thấy GPT-4o không thuộc cách "
        "viết chuẩn của tên lễ hội này, thay vào đó phiên âm lại từ "
        "tiếng Việt một cách sai lệch.",
    ),
    (
        "Chủ yếu vào các lễ hội lớn như Chol Chnam Thmay hay Ok Om Bok",
        "REF dùng `ពិធីបុណ្យអកអំបុក` (Ok Om Bok). GPT-4o bỏ chữ "
        "`ពិធីបុណ្យ` (lễ hội) và viết `អុកអុំបុក` — vừa rút ngắn vừa "
        "phiên âm sai. Với các cộng đồng Khmer ở Sóc Trăng, Trà Vinh, "
        "Bạc Liêu, Ok Om Bok là lễ hội trung tâm năm; dạng của GPT-4o "
        "làm nó trông như một tên nước ngoài lạ.",
    ),
    (
        "Anh có thể chia sẻ vai trò của dân ca trong đời sống tinh thần và văn hóa cộng đồng Khmer Nam Bộ",
        "REF dùng `សហគមន៍ខ្មែរណាមបូ` — phiên âm trực tiếp \"Khmer Nam "
        "Bộ\" vào chữ Khmer, là cách cộng đồng dùng để gọi chính mình. "
        "GPT-4o thay bằng `សហគមន៍ខ្មែរនៅតំបន់ខាងត្បូង` (Khmer ở miền "
        "Nam) — đúng địa lý nhưng không còn là tên gọi cộng đồng. Đây "
        "là hiện tượng sụp đổ điển hình: **tên cộng đồng bị kéo xuống "
        "thành mô tả địa danh trừu tượng**.",
    ),
    (
        "- Ngoài ra, một số nghi thức quan trọng như cúng tổ tiên",
        "REF dùng `ការសែនដូនតា` (Sen Dolta, nghi lễ cúng tổ tiên Khmer "
        "Nam Bộ). GPT-4o dịch thành `ការបូជា祖先` — **ghép tiếng Khmer "
        "`បូជា` với chữ Hán `祖先`**. Đây là lỗi ô nhiễm chữ viết rất "
        "nặng: bản dịch Khmer chứa chữ Hán, chứng tỏ model lấy khái "
        "niệm từ vùng tri thức tiếng Trung chứ không từ văn hoá Khmer.",
    ),
    (
        "- Một trong những món không thể thiếu là bún nước lèo",
        "REF giữ tên cộng đồng cho các món ăn đặc trưng: `នំបញ្ចុកទឹកសម្ល` "
        "(bún nước lèo Khmer) và `ម៉ាំប្រហុក` (mắm bò hóc — `ម៉ាំ` là "
        "phiên âm Việt, nối với `ប្រហុក` prahok). GPT-4o dịch thành "
        "`គុយទាវ` (hủ tiếu — **sai món hoàn toàn**) + `ទឹកល្អក់` (nước "
        "đục — không phải tên món), và giản lược `ម៉ាំប្រហុក` thành "
        "`ប្រហុក` generic. Mất cả tên món đặc thù Nam Bộ lẫn dạng "
        "phiên âm Việt hoá.",
    ),
    (
        "Người Khmer: Neak Tà là vị thần cai quản đất đai",
        "REF: `អ្នកតា` (Neak Ta, thần bảo hộ làng Khmer Nam Bộ). GPT-4o "
        "viết `នាគតា` — tức `នាគ` (rồng/nāga) + `តា` (ông). Đây là "
        "**ảo giác nghĩa** (semantic hallucination): GPT tạo ra một từ "
        "nghe có cấu trúc hợp lý nhưng không tồn tại trong tín ngưỡng "
        "Khmer. Từ này không nói gì về thần bảo hộ làng.",
    ),
    (
        "Thay vào đó, người thân tập trung đọc kinh, làm lễ bái Tam bảo",
        "`អាចារ្យយុគី` (Achar duki) là chức sắc trợ lễ cho nhà sư trong "
        "Phật giáo Nam tông Khmer ĐBSCL. GPT-4o viết `អាចារ្យដូគី` — "
        "phiên âm gần với cách đọc tiếng Việt \"duki\" hơn là cách "
        "viết đã định hình trong cộng đồng Khmer. Cũng có thể GPT "
        "không phân biệt được vai trò Achar lễ (`អាចារ្យ`) và Achar "
        "duki (`អាចារ្យយុគី`) là hai chức vụ khác nhau.",
    ),
    (
        "Dạ, dù con cái đã lớn và lập gia đình, người Khmer vẫn giữ truyền thống",
        "**Đây có thể là false positive của heuristic**: pattern `អានយ៉ាង` "
        "(tên Khmer của An Giang) vô tình trùng với chuỗi con trong "
        "`រាប់អានយ៉ាងជិត` (tôn trọng rất gần gũi). REF không thực sự nói "
        "về địa danh An Giang, mà dùng cụm ngữ pháp `រាប់អាន`. Cần "
        "native reviewer loại bỏ trường hợp này khỏi bảng chính thức.",
    ),
    (
        "Anh có thể chia sẻ một vài nét khái quát về lối sống của cộng đồng Khmer ở Nam Bộ",
        "REF dùng `ខ្មែរណាមបូ` (Khmer Nam Bộ, phiên âm Việt vào chữ "
        "Khmer). GPT-4o tạo ra `ខ្មែរនៅតំបន់នាគប្បូរ` — từ `នាគប្បូរ` "
        "không tồn tại trong tiếng Khmer, nó là **ảo giác** mà model "
        "tự đặt khi không biết \"Nam Bộ\". So với việc thay bằng "
        "`តំបន់ខាងត្បូង` (miền Nam) đã thấy ở mẫu khác, lần này nặng "
        "hơn vì bịa ra từ vô nghĩa.",
    ),
    (
        "Người Khmer: Chính xác, cốm dẹp tượng trưng cho thành quả lao động",
        "REF: `អំបុក` — tên Khmer chuẩn cho \"cốm dẹp\", món ăn lễ hội "
        "Ok Om Bok của Khmer Nam Bộ. GPT-4o viết `កុមដេប` — phiên âm "
        "trực tiếp từ tiếng Việt \"cốm dẹp\" mà không biết đã có tên "
        "Khmer tồn tại. Kết quả là một từ không có trong từ vựng "
        "Khmer.",
    ),
    (
        "Người phỏng vấn: Còn lễ hội Ok Om Bok dâng cúng trăng",
        "Hai lỗi cùng câu: (1) tên lễ hội Ok Om Bok — REF `អកអំបុក`, "
        "HYP giữ `Ok Om Bok` bằng chữ Latin trong bản Khmer; (2) \"ghe "
        "ngo\" — REF `ទូកង`, HYP `ទូកងូ` (thiếu ký tự). Một câu ngắn "
        "mất cả tên lễ hội lẫn tên hiện vật văn hoá trung tâm.",
    ),
    (
        "Lễ vật thường có gạo, trái cây, bánh truyền thống như bánh tét, bánh ít",
        "REF dùng `នំអន្សម` (Num Ansom, tức bánh tét Khmer) và `នំគម` "
        "(Num Kom, tức bánh ít). GPT-4o viết `នំតេត` và `នំអិត` — tức "
        "là **phiên âm trực tiếp từ tiếng Việt \"tét\" và \"ít\"** mà "
        "không biết mỗi món bánh này đã có tên Khmer riêng. Về mặt "
        "nghĩa đen thì người đọc Khmer Nam Bộ có thể đoán được, nhưng "
        "về mặt tên chuẩn thì sai hoàn toàn.",
    ),
    (
        "Đua ghe Ngo diễn ra vào dịp Ok Om Bok",
        "Ba lỗi trong một câu: (1) `ទូកង` → `ទូកងូរ` (sai tên ghe "
        "ngo); (2) `អកអំបុក` → `អុកអុំបុក` (sai tên Ok Om Bok); (3) "
        "GPT-4o còn dịch chi tiết số đo: REF `រាប់សិបម៉ែត្រ` (hàng "
        "chục mét) → HYP `ជាងដប់ម៉ែត្រ` (hơn mười mét) — đổi nghĩa "
        "số lượng. Câu này là ví dụ gọn của việc mất sạch lớp 2 khi "
        "dịch cảnh văn hoá lễ hội.",
    ),
    (
        "Anh có thể chia sẻ về những truyền thống chăm sóc vật nuôi",
        "REF dùng `បងប្អូនខ្មែរណាមបូ` (bà con Khmer Nam Bộ). GPT-4o "
        "tạo `បងប្អូនខ្មែរនៅតំបន់នាគរបត់` — `នាគរបត់` là từ bịa, "
        "không có trong tiếng Khmer. Đây lại là **ảo giác nghĩa** "
        "theo đúng pattern: khi gặp \"Nam Bộ\" GPT-4o không biết "
        "phiên âm đúng nên tạo ra các biến thể ngẫu nhiên nghe có "
        "cấu trúc Khmer nhưng vô nghĩa.",
    ),
    (
        "- Chúng tôi thường mặc sampot chang kben",
        "**Đây có thể là false positive của heuristic**: pattern "
        "`ម៉ែ` (mẹ, xưng hô Krom) trùng với substring trong các từ "
        "như `ព្យាយាម` hoặc các tiếng có chứa chuỗi này. Nội dung "
        "mẫu nói về trang phục cưới (sampot chang kben), không có "
        "xưng hô gia đình. Cần native reviewer xác nhận lại.",
    ),
    (
        "Anh có thể chia sẻ về vai trò của nhạc cụ trong đời sống văn hóa và tinh thần của người Khmer Nam Bộ",
        "REF dùng `ខ្មែរណាមបូ` (Khmer Nam Bộ). GPT-4o thay bằng "
        "`ខ្មែរនៅតំបន់ខាងត្បូង` (Khmer ở miền Nam địa lý). Pattern "
        "giống mẫu dân ca: tên cộng đồng bị kéo xuống thành mô tả "
        "địa danh trừu tượng, đánh mất bản sắc định danh cộng đồng.",
    ),
    (
        "- Mỗi bộ trang phục đều có màu sắc và phụ kiện riêng",
        "REF dùng `ការថ្វាយសែនដូនតា` (lễ cúng tổ tiên Sen Dolta). "
        "GPT-4o dịch thành `បូជាបុព្វបុរស` (cúng tổ tiên — phiên "
        "bản Pali-Sanskrit trừu tượng). Tuy đúng nghĩa nhưng mất tên "
        "riêng lễ `សែនដូនតា` mà cộng đồng Khmer Nam Bộ dùng làm danh "
        "pháp nghi lễ chính thức.",
    ),
    (
        "Đúng vậy, lễ cúng trăng trong dịp Ok Om Bok diễn ra ban đêm",
        "Lặp cả hai pattern: (1) `អកអំបុក` → `អុកអុំបុក` (sai Ok Om "
        "Bok); (2) `អំបុក` → `អំពៅស្ងោរ` — GPT-4o dịch \"cốm dẹp\" "
        "thành \"mía luộc\" (!) Đây là **ảo giác nghĩa nghiêm trọng**: "
        "cốm dẹp (làm từ lúa) bị thay bằng mía — hai loại nguyên "
        "liệu hoàn toàn khác nhau.",
    ),
    (
        "Chúng tôi thường cùng nhau gói bánh truyền thống như bánh tét, bánh ít",
        "REF `នំអន្សមជ្រូក នំគម` (bánh tét nhân thịt lợn, bánh ít). "
        "GPT-4o `នំតេត និងនំអិត` — phiên âm trực tiếp từ \"tét\" và "
        "\"ít\" tiếng Việt, không biết rằng hai loại bánh này đã có "
        "tên Khmer riêng đã lưu truyền trong cộng đồng Khmer Nam Bộ "
        "hàng trăm năm.",
    ),
    (
        "Người Khmer: Nếu đối với người Khmer Nam bộ thì có sự khác biệt",
        "Nhiều lỗi nặng trong một câu: (1) REF dùng `ខ្មែណាមបូ` và "
        "`ជនជាតិគិញ` (Khmer Nam Bộ và người Kinh); HYP thay bằng "
        "`ខ្មែរនៅតំបន់ខាងត្បូង` và `ជនជាតិវៀតណាម` — kéo cả hai "
        "ethnonym cộng đồng về dạng địa lý/quốc gia trừu tượng. (2) "
        "Về xưng hô ông bà, REF giữ lai ghép `តា Nội`, `យាយ Ngoại` "
        "(mang nguyên các từ Việt \"Nội\", \"Ngoại\" trong bản Khmer "
        "— đặc trưng code-switching Krom). GPT-4o phiên âm sai thành "
        "`តាណៃ` và `យាយណៃ`, tức là nó bịa ra một phiên âm không tồn "
        "tại, cũng xoá cả sự phân biệt nội/ngoại.",
    ),
]


def md_escape(text: str) -> str:
    return text.replace("|", "\\|").replace("\n", " ").strip()


def truncate(text: str, n: int = 220) -> str:
    text = text.strip().replace("\n", " ")
    if len(text) <= n:
        return text
    return text[:n - 1] + "…"


def find_explanation(sample: dict) -> str:
    src = sample["source"].strip()
    for prefix, expl in FAIL_EXPLANATIONS:
        if src.startswith(prefix):
            return expl
    # Fallback template based on dropped categories
    cats = sample.get("dropped_categories", [])
    if not cats:
        return "(chưa có giải thích chi tiết cho mẫu này)"
    return (
        "GPT-4o đánh rơi marker thuộc nhóm "
        + ", ".join(f"`{c}`" for c in cats)
        + ". Bản dịch chuyển về dạng Khmer Cambodia chuẩn, mất nét Khmer Nam Bộ "
        "mà REF giữ lại."
    )


def stat_table(rows: list[dict]) -> str:
    lines = [
        "| # | English topic | Chủ đề tiếng Việt | Tổng mẫu | REF có marker Khmer-Việt | GPT-4o đánh rơi | Tỉ lệ |",
        "|---:|---|---|---:|---:|---:|---:|",
    ]
    vi_index = {v: i for i, v in enumerate(CANONICAL_ORDER_VI)}
    rows_sorted = sorted(rows, key=lambda r: (vi_index.get(r["topic_vi"], 999), -r["total"]))
    for i, r in enumerate(rows_sorted, 1):
        rate = f"{r['drop_rate']:.0f}%" if r["ref_has_krom"] else "–"
        lines.append(
            f"| {i} | {md_escape(r['topic_en'])} | {md_escape(r['topic_vi'])} "
            f"| {r['total']} | {r['ref_has_krom']} | {r['gpt4o_dropped']} | {rate} |"
        )
    return "\n".join(lines)


def clean_table(samples: list[dict]) -> str:
    lines = [
        "| # | Chủ đề | Tiếng Việt | REF (Khmer) | GPT-4o (Khmer) | chrF++ |",
        "|---:|---|---|---|---|---:|",
    ]
    for i, s in enumerate(samples, 1):
        vi = truncate(s["source"], 200)
        ref = truncate(s["reference"], 200)
        hyp = truncate(s["hyp_plain"], 200)
        lines.append(
            f"| {i} | {md_escape(s['topic_en'])} | {md_escape(s['topic_vi'])} | "
            f"{md_escape(ref)} | {md_escape(hyp)} | {s.get('chrf', 0):.1f} |"
        )
        lines.append(
            f"|   | _VI_ | _nguồn_ | _{md_escape(vi)}_ |  |  |"
        )
    return "\n".join(lines)


def fail_blocks(samples: list[dict]) -> str:
    out = []
    for i, s in enumerate(samples, 1):
        vi = s["source"].strip().replace("\n", " ")
        ref = s["reference"].strip().replace("\n", " ")
        hyp = s["hyp_plain"].strip().replace("\n", " ")
        markers = ", ".join(f"`{c}`" for c in s.get("dropped_categories", [])) or "–"
        chrf = s.get("chrf", 0)
        expl = find_explanation(s)

        out.append(
            f"#### Mẫu {i} — {s['topic_en']} / {s['topic_vi']}\n\n"
            f"- **Câu tiếng Việt**: {vi}\n"
            f"- **REF (Khmer)**: {ref}\n"
            f"- **GPT-4o (Khmer)**: {hyp}\n"
            f"- **Marker bị đánh rơi**: {markers} | **chrF++**: {chrf:.1f}\n"
            f"- **Giải thích**: {expl}\n"
        )
    return "\n".join(out)


def main() -> None:
    data = json.loads(DATA.read_text(encoding="utf-8"))
    totals = data["totals"]
    rows = data["topic_stats"]
    clean = data["clean_samples"][:25]
    fail = data["fail_samples"][:25]

    header = f"""# Báo cáo sơ bộ: Ba lớp tiếng Khmer và khoảng cách dịch Việt–Khmer

> Tài liệu này được tạo tự động từ `results/report_data.json`.
> Dữ liệu đầu vào: kết quả GPT-4o trên 1,856 mẫu song ngữ Việt–Khmer
> (`results/gpt4o_full_1856.json`).

**Tổng quan nhanh**

- Tổng số mẫu: **{totals['total_samples']}**.
- Số mẫu mà bản dịch tham chiếu (REF) chứa marker Khmer-Việt / Khmer Nam Bộ: **{totals['ref_has_krom']}** (≈ {totals['ref_has_krom']*100/totals['total_samples']:.1f}% dataset).
- Số mẫu mà GPT-4o đánh rơi marker đó (dịch thẳng sang Khmer Cambodia chuẩn): **{totals['gpt4o_dropped']} / {totals['ref_has_krom']} ({totals['drop_rate_percent']}%)**.

---
"""

    section1 = """## 1. Ba lớp của tiếng Khmer (khung phân tích)

Tiếng Khmer tại Việt Nam (Khmer Nam Bộ, Khmer Krom) không phải một ngôn ngữ
độc lập. Nó là một phương ngữ của tiếng Khmer. Để phân tích cho đúng, ta chia
nó thành ba lớp:

### 1.1 Lớp 1 — Cốt lõi (Core)

Lớp ngôn ngữ chung giữa Khmer Campuchia và Khmer Nam Bộ. Bao gồm:

- Ngữ pháp, cấu trúc câu SVO, bảng chữ cái.
- Từ vựng cơ bản: ăn, ngủ, nước, lửa, trời, đất, cha, mẹ (dạng trang trọng), người, nhà.
- Vốn học thuật – tôn giáo có gốc Pali/Sanskrit: `ព្រះសង្ឃ` (nhà sư),
  `វត្ត` (chùa), `មរណភាព` (qua đời), `សាកសព` (thi thể).

Người Khmer Nam Bộ và người Campuchia nói chuyện ở lớp này vẫn hiểu nhau.
**Ở lớp này, một bản dịch chuẩn Campuchia cũng xem là đúng.**

### 1.2 Lớp 2 — Khmer Krom thuần (văn nói / giao tiếp thực tế)

Đây là lớp làm nên bản sắc. Đặc trưng:

- **Mượn âm Việt Nam** cho đồ vật / khái niệm mới: xe máy → `សេម៉ាយ`,
  tivi → `ទីវី`, bệnh viện → `បេញវៀង`, Ủy ban → `អ៊ុយបាន`.
- **Phiên âm Việt Nam vào tiếng Khmer** cho tên món, địa danh, ethnonym:
  mắm bò hóc → `ម៉ាំប្រហុក`, người Kinh → `គិញ`, Tri Tôn → `ទ្រីតុង`,
  Nam Bộ → `ណាមបូ`.
- **Xưng hô khẩu ngữ**: mẹ → `ម៉ែ` / `ម៉ាក់`, ba → `ប៉ា`.
- **Code-switching**: chèn hư từ tiếng Việt vào câu tiếng Khmer.
- **Phát âm chệch** so với Khmer Campuchia chuẩn.

Lớp này sống chủ yếu ở dạng văn nói, tin nhắn cộng đồng, bài đăng mạng xã
hội. Rất hiếm khi lên báo chí.

### 1.3 Lớp 3 — Khmer hành chính / báo chí (văn viết đã chuẩn hoá)

Khi người Khmer Nam Bộ phải viết văn bản chính thức (cán bộ, phóng viên),
họ gạt Lớp 2 sang bên và dùng ngữ pháp + từ vựng học thuật Campuchia
(gốc Pali/Sanskrit) để dịch các khái niệm Việt Nam:

- Công an → `នគរបាល` (Nokorbal).
- Ủy ban nhân dân → `គណៈកម្មាធិការប្រជាជន`.
- Bộ Giáo dục → `ក្រសួងអប់រំ`.

Đặc trưng Lớp 3: **vỏ Campuchia, ruột Việt Nam** — dùng từ chuẩn Campuchia
để nói về thiết chế / khái niệm chỉ có trong bối cảnh Việt Nam.

---
"""

    section2 = """## 2. So sánh Khmer Campuchia và Khmer-Việt Nam (Khmer Krom)

| Khía cạnh | Khmer Campuchia (chuẩn) | Khmer Nam Bộ (Krom) |
|---|---|---|
| Khu vực chính | Vương quốc Campuchia | Đồng bằng sông Cửu Long, Việt Nam |
| Số người dùng | ~16 triệu | ~1.3 triệu |
| Nguồn vay mượn hiện đại | Pháp, Anh | Tiếng Việt |
| Cách gọi "mẹ" (khẩu ngữ) | `ម៉ាក់` hoặc `ម្តាយ` | `ម៉ែ`, `ម៉ាក់`, `ប៉ា` |
| Cách gọi "người Kinh" | Thường dùng `វៀតណាម` hoặc `យួន` | `គិញ` |
| Tên "Nam Bộ" | `តំបន់ខាងត្បូង` (miền Nam địa lý) | `ណាមបូ` (phiên âm Việt) |
| Tên Trà Vinh | `ព្រះត្រពាំង` (tên Khmer cổ) | `ត្រាវិញ` (phiên âm Việt) |
| Tên Tri Tôn | `ស្រុកបាយ៉ង់` (Srok Bayon) | `ទ្រីតុង` (phiên âm Việt) |
| Mắm bò hóc | `ប្រហុក` (prahok) | `ម៉ាំប្រហុក` (mắm prahok) |
| Cốm dẹp | `អង្ករកន្ទក់` | `អំបុក` |
| Ủy ban | `គណៈកម្មាធិការ` (từ Pali) | `អ៊ុយបាន` (phiên âm Việt) |
| Ghe ngo | `ទូកង` / `ទូកអុំ` | cùng dạng, nhưng thường đi kèm `ប្រណាំងទូកអុំ` |
| Thần bảo hộ làng | `អ្នកតា` được dùng nhưng hạn hẹp hơn | `អ្នកតា`, `ភូមិសង្គម` dùng rộng hơn |
| Tôn giáo nền | Theravāda | Theravāda (Phật giáo Nam tông Khmer) |
| Độ phủ của NLP / MT | Trung bình (FLORES, NLLB, Google) | Rất thấp |

Phần lớn **từ vựng học thuật và tôn giáo giống nhau** (Lớp 1). Điểm khác
biệt tập trung ở **tên riêng, ẩm thực, xưng hô khẩu ngữ, thiết chế hành
chính mượn âm Việt** (Lớp 2 và Lớp 3).

---
"""

    section3_title = f"""## 3. Thống kê chủ đề trong bộ dữ liệu

Mỗi mẫu trong dataset được gắn một nhãn chủ đề. **Các mẫu không có nhãn
(chủ yếu là phần hỏi-đáp về ăn uống) được gán vào "Ăn uống" / "Eating (Q&A)"**
theo yêu cầu của báo cáo.

- Tổng số mẫu: **{totals['total_samples']}**.
- Số chủ đề độc nhất sau khi chuẩn hoá: **{len(rows)}**.
- Cột "REF có marker Khmer-Việt" đếm số mẫu mà bản dịch tham chiếu chứa ít
  nhất một dấu ngôn ngữ Khmer Nam Bộ (xưng hô khẩu ngữ, ethnonym `គិញ`,
  địa danh Nam Bộ dạng Krom, tên món Khmer-Việt, lễ hội Nam Bộ, thuật ngữ
  tôn giáo Krom, từ mượn âm Việt).
- Cột "GPT-4o đánh rơi" đếm số mẫu mà GPT-4o **không** tái hiện marker đó
  trong bản dịch, tức đã chuẩn hoá về Khmer Campuchia.

"""

    section3_table = stat_table(rows) + "\n"

    section4_intro = """\n---\n\n## 4. Minh hoạ định tính: 50 mẫu

Chia làm hai nhóm:
- **25 mẫu dịch được** — nội dung thuộc Lớp 1 hoặc chỉ chứa khái niệm
  phổ thông. GPT-4o đưa ra bản Khmer chuẩn, không mất nét văn hoá nào có
  thể xác định được bằng heuristic.
- **25 mẫu dịch fail vì yếu tố văn hoá Việt Nam** — REF có marker
  Khmer-Việt, GPT-4o **đánh rơi** marker đó, dịch thẳng sang dạng Khmer
  Campuchia. Từng mẫu đi kèm một đoạn giải thích chỉ ra **đánh rơi chỗ
  nào** và **tại sao đó là lỗi văn hoá**.

### 4.1 — 25 mẫu GPT-4o dịch được Khmer Campuchia chuẩn

Dòng in nghiêng `_VI_` bên dưới mỗi mẫu là **câu nguồn tiếng Việt**.

"""

    section4_2_intro = """

### 4.2 — 25 mẫu GPT-4o dịch fail do yếu tố văn hoá Việt Nam

Mỗi mẫu trình bày dưới dạng khối (block) để có chỗ cho phần giải thích
chi tiết. Các mẫu được đánh dấu **false positive** là trường hợp heuristic
marker khớp nhầm; chúng được giữ lại để minh hoạ giới hạn của phương pháp
rà soát tự động, chứ không tính là bằng chứng lỗi dịch.

"""

    md = [
        header,
        section1,
        section2,
        section3_title,
        section3_table,
        section4_intro,
        clean_table(clean),
        section4_2_intro,
        fail_blocks(fail),
        "\n\n---\n\n## 5. Ghi chú phương pháp\n",
        """- Heuristic marker Khmer-Việt / Khmer Krom được liệt kê trong
  `experiments/analysis/build_report_data.py`. Danh sách này là **sàn**,
  chưa phủ hết mọi biến thể địa phương. Native reviewer có thể tìm ra
  thêm các trường hợp khác.
- Nhóm "25 mẫu dịch được" chọn ngẫu nhiên phân tầng theo chủ đề, ưu tiên
  mẫu có `chrF++ ≥ 35` và `CuEA = 1.0` hoặc không có thực thể văn hoá nào.
- Nhóm "25 mẫu dịch fail" chọn từ 139 mẫu đã được flag variety collapse,
  phân tầng theo chủ đề để tránh lặp lại.
- Giải thích trong mục 4.2 là phân tích ngôn ngữ học dựa trên so sánh
  REF và HYP. Đây **không phải** đánh giá của người Khmer bản ngữ, mà là
  suy luận từ pattern được nhìn thấy trong dữ liệu. Một số case được
  đánh dấu false positive khi marker khớp nhầm ngữ pháp.
- Con số `CuEA` được giữ để tham chiếu nhưng **không dùng làm chuẩn mực
  đánh giá trong báo cáo này** — độ đo đó sẽ được đề xuất ở phần sau của
  dự án, sau khi cơ sở tri thức văn hoá được xây dựng.
""",
    ]

    OUT.write_text("\n".join(md), encoding="utf-8")
    print("Đã ghi:", OUT)
    print("Số dòng:", len("\n".join(md).splitlines()))


if __name__ == "__main__":
    main()
