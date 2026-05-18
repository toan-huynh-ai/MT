# Phân tích chi tiết lỗi của GPT-4o trong dịch Khmer -> Việt

## 1. Mục tiêu của tài liệu

Tài liệu này tổng hợp các lỗi và khuyết điểm nổi bật của GPT-4o khi dịch tiếng Khmer sang tiếng Việt trong bộ dữ liệu đang dùng để nghiên cứu, với trọng tâm là:

- Chất lượng dịch ở mức tổng quát.
- Khả năng bảo toàn cultural entities của cộng đồng Khmer, đặc biệt là Khmer ở Việt Nam / Khmer Krom.

Phân tích này dựa trên hai nguồn chính:

- File kết quả đánh giá thí nghiệm: [results/km2vi_results_20260518_162617.json](results/km2vi_results_20260518_162617.json)
- File toàn bộ bản dịch: [translation_output/all_translations_parallel_20260518_190336.json](translation_output/all_translations_parallel_20260518_190336.json)

## 2. Tóm tắt định lượng

### 2.1. Kết quả tổng quát

- Zero-shot 50 mẫu: BLEU = 35.67 tại [BLEU](results/km2vi_results_20260518_162617.json#L5), chrF++ = 58.09 tại [chrF++](results/km2vi_results_20260518_162617.json#L6).
- Khi thêm ngữ cảnh hội thoại, chrF++ tăng từ 68.46 lên 74.58, tức tăng +6.13 tại [isolated](results/km2vi_results_20260518_162617.json#L1145), [context](results/km2vi_results_20260518_162617.json#L1146), [delta](results/km2vi_results_20260518_162617.json#L1147).

### 2.2. Kết quả theo nhóm lỗi văn hóa

- Nhóm `food_cultural`: chrF++ = 62.11 tại [food_cultural](results/km2vi_results_20260518_162617.json#L463)
- Nhóm `khmer_krom_regional`: chrF++ = 53.39 tại [khmer_krom_regional](results/km2vi_results_20260518_162617.json#L802)

Ý nghĩa:

- Model xử lý nội dung ẩm thực tương đối khá hơn các biểu thức gắn với đời sống xã hội-văn hóa Khmer Krom.
- Các điểm yếu lớn nhất không nằm ở ngữ pháp tiếng Việt mà nằm ở lexical fidelity, cultural preservation và identity grounding.

### 2.3. Một vài dấu hiệu lỗi lặp lại trên toàn bộ tập 1,852 mẫu

Qua quét pattern trên file dịch đầy đủ, có một số hiện tượng lặp lại đáng chú ý:

- Có 51 hypothesis chứa từ `Campuchia`, cho thấy model nhiều lần kéo nội dung Khmer ở Việt Nam về khung tham chiếu Cambodia.
- Có 10 trường hợp dùng `Tết Nguyên Đán` thay cho các lễ Khmer như Chol Chnam Thmay.
- Có ít nhất 7 trường hợp bị rò rỉ artifact kiểu `Tiếng Việt:` vào output.
- Có ít nhất 2 trường hợp Achar/Achar duki bị méo thành `thầy Yuki` hoặc `Yukida`.
- Có ít nhất 35 trường hợp cultural entity xuất hiện rõ trong reference nhưng không còn được giữ nguyên hoặc không còn nhận diện được trong hypothesis.

Lưu ý: các con số trên là quick scan theo pattern, có tính bảo thủ, không phải annotation tay 100% toàn bộ corpus.

## 3. Kết luận chính

Kết luận quan trọng nhất là: GPT-4o trong bộ dữ liệu này dịch trôi chảy hơn là dịch trung thành.

Nói cách khác:

- Ở mức câu, output thường đọc tự nhiên, mượt, ít lỗi cú pháp.
- Nhưng ở mức thực thể văn hóa, hệ thân tộc, lễ nghi và định danh cộng đồng, model thường xuyên suy diễn hoặc thay bằng khái niệm quen thuộc hơn với tiếng Việt phổ thông.
- Vì vậy, nếu dùng cho nghiên cứu văn hóa, dân tộc học, hoặc tài liệu hóa Khmer Krom, bản dịch của model không đủ tin cậy nếu không có human review.

## 4. Các khuyết điểm ở góc nhìn tổng quát

### 4.1. Fluency cao nhưng fidelity thấp

Đây là lỗi lớn nhất và là lỗi có tính hệ thống.

Model thường tạo ra một câu tiếng Việt rất mượt, nhưng lại thay đổi hoặc làm lệch nghĩa của thực thể gốc.

Ví dụ điển hình:

- `nùm bong khlanh` bị đổi thành `bánh mì mỡ` tại [line 44](translation_output/all_translations_parallel_20260518_190336.json#L44)
- `nùm bong khlanh` bị đổi thành `bánh bông lan` tại [line 54](translation_output/all_translations_parallel_20260518_190336.json#L54)
- Cùng thực thể này lại bị đổi thành `bánh nậm mỡ` tại [line 634](translation_output/all_translations_parallel_20260518_190336.json#L634)
- Và bị đổi tiếp thành `bánh mì nhiều dầu mỡ` tại [line 824](translation_output/all_translations_parallel_20260518_190336.json#L824)

Điểm cần nhấn mạnh:

- Đây không phải lỗi đánh máy.
- Đây là lỗi model "đoán nghĩa" bằng một món Việt có vẻ gần âm hoặc gần cảm giác sử dụng.
- Khi model làm vậy, nó phá hỏng giá trị tư liệu của dữ liệu đầu ra.

### 4.2. Semantic drift: câu vẫn đúng tiếng Việt nhưng sai trường nghĩa

Model có xu hướng giữ được skeleton của câu nhưng lệch ở semantic field.

Ví dụ:

- `xum họp` bị kéo thành `cuộc họp` ở [line 5264](translation_output/all_translations_parallel_20260518_190336.json#L5264)
- `túc trực bên linh cữu` bị kéo thành `ở gần mộ` ở [line 5284](translation_output/all_translations_parallel_20260518_190336.json#L5284)

Phân tích:

- `xum họp` là gathering trong bối cảnh tang lễ, có sắc thái cộng đồng và nghi thức.
- `cuộc họp` là một event có tính hành chính / meeting.
- `linh cữu` và `mộ` không tương đương nhau trong trình tự tang lễ.

Điều này cho thấy model không chỉ sai từ vựng, mà còn sai cả event structure của bối cảnh văn hóa.

### 4.3. Phụ thuộc ngữ cảnh mạnh

Kết quả context experiment cho thấy khi có ngữ cảnh hội thoại thì chất lượng tăng khá rõ, delta +6.13 tại [delta](results/km2vi_results_20260518_162617.json#L1147).

Ý nghĩa nghiên cứu:

- Nhiều lỗi của GPT-4o không phải vì không hiểu tiếng Khmer từng câu một cách tuyệt đối.
- Mà vì khi đứng một mình, câu chứa quá nhiều cultural shorthand, social role, kinship label, ritual term.
- Khi có ngữ cảnh, model disambiguate tốt hơn.

Nói cách khác, Khmer Krom discourse có mật độ ngầm định văn hóa cao, nên zero-shot sentence-level translation là setting khá bất lợi cho model.

### 4.4. Chính sách xử lý thực thể không nhất quán

Model không có chiến lược ổn định cho các tên món ăn, nghi lễ hay xưng hô Khmer:

- Có lúc giữ nguyên transliteration.
- Có lúc dịch sang tiếng Việt phổ thông.
- Có lúc phiên âm lệch.
- Có lúc thay bằng một khái niệm hoàn toàn khác.

Ví dụ:

- `Som-lo Co Cô` có lúc được đổi thành `Samlor Korko` tại [line 124](translation_output/all_translations_parallel_20260518_190336.json#L124)
- Nhưng ở chỗ khác lại bị làm phẳng thành `canh và cá khô` tại [line 954](translation_output/all_translations_parallel_20260518_190336.json#L954)
- Hoặc bị generic hóa thành `canh chua` tại [line 10854](translation_output/all_translations_parallel_20260518_190336.json#L10854)

Lỗi này đặc biệt khó chịu cho nghiên cứu, vì cùng một entity mà model không giữ nhất quán.

### 4.5. Output artifact và instruction leakage

Model đôi lúc sinh ra những dấu vết không nên có trong output dịch, ví dụ tiền tố `Tiếng Việt:`:

- [line 2794](translation_output/all_translations_parallel_20260518_190336.json#L2794)
- [line 2904](translation_output/all_translations_parallel_20260518_190336.json#L2904)
- [line 5304](translation_output/all_translations_parallel_20260518_190336.json#L5304)
- [line 9034](translation_output/all_translations_parallel_20260518_190336.json#L9034)

Đây là lỗi behavior-level, cho thấy model không hoàn toàn kiểm soát được output format ngay cả khi prompt yêu cầu chỉ xuất bản dịch.

## 5. Các khuyết điểm ở góc nhìn cultural entities Khmer / Khmer Krom

## 5.1. Ẩm thực: tên món Khmer thường bị Việt hóa sai

Đây là nhóm lỗi lớn và dễ quan sát nhất.

### 5.1.1. Nùm bong khlanh bị suy diễn thành món Việt khác

Đây là case rất mạnh để dùng trong report.

Các hypothesis sai gồm:

- `bánh mì mỡ` tại [line 44](translation_output/all_translations_parallel_20260518_190336.json#L44)
- `bánh bông lan` tại [line 54](translation_output/all_translations_parallel_20260518_190336.json#L54)
- `bánh nậm mỡ` tại [line 634](translation_output/all_translations_parallel_20260518_190336.json#L634)
- `bánh mì nhiều dầu mỡ` tại [line 824](translation_output/all_translations_parallel_20260518_190336.json#L824)
- `bánh dầu` tại [line 1054](translation_output/all_translations_parallel_20260518_190336.json#L1054)
- `bánh mì mỡ` tại [line 1484](translation_output/all_translations_parallel_20260518_190336.json#L1484)
- `bánh mì mỡ` tại [line 1674](translation_output/all_translations_parallel_20260518_190336.json#L1674)

Điều này cho thấy:

- Model không có lexical anchor cho món Khmer này.
- Khi không chắc, model domesticate sang một món nghe quen hơn với người Việt phổ thông.
- Đây là loại lỗi `cultural entity substitution`.

### 5.1.2. Num Pong / Num Bompung bị méo nghĩa

`Num Pong` bị kéo thành `bánh trứng` tại [line 324](translation_output/all_translations_parallel_20260518_190336.json#L324).

`num bompung` trong một ngữ cảnh khác bị bỏ phần `num`, chỉ còn `bánh ống`, đồng thời còn làm sai nguyên liệu ở [line 1014](translation_output/all_translations_parallel_20260518_190336.json#L1014) khi `nước lá dứa` bị đổi thành `nước lá thốt nốt`.

Ở đây có hai lớp lỗi:

- Sai tên món.
- Sai luôn thành phần cấu thành món.

### 5.1.3. Dừa sáp bị kéo thành nước cốt dừa

Ở [line 334](translation_output/all_translations_parallel_20260518_190336.json#L334), `dừa sáp` bị model viết thành `nước cốt dừa`.

Đây là lỗi loại hình entity:

- `dừa sáp` là một thực thể nông sản / đặc sản.
- `nước cốt dừa` là một thành phần chế biến.

Về mặt văn hóa ẩm thực, hai thứ này không thể hoán đổi cho nhau.

### 5.1.4. Kroeung bị làm phẳng thành “nguyên liệu”

Ở [line 614](translation_output/all_translations_parallel_20260518_190336.json#L614), `kroeung` bị dịch thành `nguyên liệu`.

Vấn đề:

- `kroeung` không đơn giản là ingredient list.
- Nó là một hệ gia vị/cốt gia vị đặc trưng trong ẩm thực Khmer.
- Khi đổi thành `nguyên liệu`, model làm mất tầng tri thức ẩm thực.

### 5.1.5. Som-lo Co Cô / Samlor Korko bị bất nhất và đôi lúc bị generic hóa

Ví dụ:

- Giữ dạng `Samlor Korko` ở [line 124](translation_output/all_translations_parallel_20260518_190336.json#L124)
- Biến thành `súp Samlor Korko` ở [line 1114](translation_output/all_translations_parallel_20260518_190336.json#L1114)
- Làm phẳng thành `canh và cá khô` ở [line 954](translation_output/all_translations_parallel_20260518_190336.json#L954)
- Làm phẳng thành `canh chua` ở [line 10854](translation_output/all_translations_parallel_20260518_190336.json#L10854)

Lỗi ở đây không chỉ là sai một lần, mà là sai theo nhiều kiểu khác nhau, chứng tỏ model không có quy tắc cố định để bảo toàn entity này.

## 5.2. Lễ nghi, lễ hội và thực hành tôn giáo Khmer bị nội địa hóa sai

### 5.2.1. Chol Chnam Thmay bị thay bằng Tết Nguyên Đán

Đây là một lỗi cực kỳ quan trọng về cultural identity.

Ví dụ:

- [line 3814](translation_output/all_translations_parallel_20260518_190336.json#L3814)
- [line 4254](translation_output/all_translations_parallel_20260518_190336.json#L4254)
- [line 5034](translation_output/all_translations_parallel_20260518_190336.json#L5034)
- [line 7684](translation_output/all_translations_parallel_20260518_190336.json#L7684)
- [line 9804](translation_output/all_translations_parallel_20260518_190336.json#L9804)
- [line 15504](translation_output/all_translations_parallel_20260518_190336.json#L15504)

Tại sao lỗi này nghiêm trọng:

- `Chol Chnam Thmay` là lễ tết Khmer, không phải `Tết Nguyên Đán` của người Kinh.
- Việc thay thế này xóa mờ định danh văn hóa của cộng đồng Khmer ở Việt Nam.
- Đây là lỗi `ritual domestication` hoặc `majority-culture normalization`.

### 5.2.2. Lễ tắm Phật bị đổi sang nghi lễ khác

Ở [line 9804](translation_output/all_translations_parallel_20260518_190336.json#L9804), reference nói về `lễ tắm Phật vào dịp Chol Chnam Thmay`, nhưng hypothesis biến thành `nghi lễ rước nước thánh nhân dịp Tết Nguyên Đán`.

Như vậy model đã làm ba việc cùng lúc:

- Đổi tên lễ.
- Đổi loại nghi thức.
- Đổi khung văn hóa của sự kiện.

Đây là một ví dụ rất mạnh cho lập luận rằng model không chỉ mất entity, mà còn tái cấu trúc sai ritual frame.

### 5.2.3. Kathina bị lược hoặc làm mờ

Ví dụ ở [line 14 case summary](translation_output/all_translations_parallel_20260518_190336.json#L144), `Kathina` trong reference không còn hiện rõ trong hypothesis. Ở nhiều chỗ khác model vẫn giữ `Kathina`, nhưng việc giữ hay bỏ là không nhất quán.

Điều này cho thấy model không ổn định trong việc quyết định khi nào nên giữ ritual term gốc, khi nào nên Việt hóa.

### 5.2.4. Achar duki bị hallucinate thành “thầy Yuki”

Đây là một lỗi rất điển hình của model khi gặp một chức danh tôn giáo - nghi lễ ít phổ biến.

Ví dụ:

- `Achar duki` -> `thầy Yuki` tại [line 5224](translation_output/all_translations_parallel_20260518_190336.json#L5224)
- `Achar ...` -> `thầy Yukida` tại [line 5314](translation_output/all_translations_parallel_20260518_190336.json#L5314)

Đây gần như là lỗi hallucination theo âm đọc, không còn là dịch.

## 5.3. Hệ thống thân tộc và xưng hô Khmer bị làm phẳng

Đây là nhóm lỗi rất đáng chú ý nếu mục tiêu nghiên cứu không chỉ là dịch nghĩa mà còn là bảo tồn cấu trúc văn hóa.

### 5.3.1. Bong / Oun / Bon / Uon bị kéo về anh / em tiếng Việt

Ví dụ:

- `bon Dara` và `uon Srey` bị đổi thành `anh Dara` và `em Srey` tại [line 15094](translation_output/all_translations_parallel_20260518_190336.json#L15094)
- `bong` / `oun` trong nhiều chỗ chỉ còn `anh` / `em` tại [line 7174](translation_output/all_translations_parallel_20260518_190336.json#L7174) và [line 15084](translation_output/all_translations_parallel_20260518_190336.json#L15084)

Vấn đề ở đây:

- Về mặt giao tiếp, `anh/em` có thể tạm hiểu được.
- Nhưng về mặt nghiên cứu cultural system, nó làm mất logic xưng hô Khmer.
- Hệ thống kinship label Khmer không hoàn toàn đẳng cấu với hệ tiếng Việt.

### 5.3.2. Cha mẹ vợ/chồng bị dịch thành “ông thông gia / bà thông gia”

Ở [line 15124](translation_output/all_translations_parallel_20260518_190336.json#L15124), model dịch các cách gọi cha mẹ vợ/chồng của Khmer thành `Ông thông gia` và `Bà thông gia`.

Đây là lỗi nặng vì:

- `thông gia` là quan hệ giữa hai bên cha mẹ, không phải cách con rể/con dâu gọi cha mẹ bên kia.
- Model đã map sai role relation trong kinship graph.

### 5.3.3. Có khi model giữ âm nhưng lại không hiểu role

Ở [line 7164](translation_output/all_translations_parallel_20260518_190336.json#L7164), model sinh ra `mẹ kẹt`, `cha kẹt`.

Đây là loại lỗi nửa phiên âm, nửa dịch nghĩa:

- Không tự nhiên trong tiếng Việt.
- Cũng không bảo tồn đúng văn hóa Khmer.
- Kết quả là tạo ra một biểu thức lạ, khó dùng cho bất kỳ mục đích nào.

### 5.3.4. Quan hệ thông gia và vai vế hôn nhân bị làm phẳng

Ở [line 7184](translation_output/all_translations_parallel_20260518_190336.json#L7184), model biến cách gọi thân tộc Khmer cụ thể thành `anh trai vợ` và `em gái chồng`.

Về mặt nội dung, câu vẫn có vẻ hiểu được. Nhưng về mặt cultural-linguistic system, model đã xóa mất từ vựng hệ thân tộc bản địa.

## 5.4. Định danh cộng đồng Khmer ở Việt Nam bị trượt sang Campuchia

Đây là lỗi identity-level, rất đáng chú ý đối với chủ đề Khmer-Vi.

Model nhiều lần dịch nội dung đang nói về cộng đồng Khmer ở Việt Nam thành nội dung về `Campuchia` hoặc `người dân Campuchia`.

Ví dụ:

- [line 404](translation_output/all_translations_parallel_20260518_190336.json#L404)
- [line 2334](translation_output/all_translations_parallel_20260518_190336.json#L2334)
- [line 2614](translation_output/all_translations_parallel_20260518_190336.json#L2614)
- [line 4384](translation_output/all_translations_parallel_20260518_190336.json#L4384)
- [line 11214](translation_output/all_translations_parallel_20260518_190336.json#L11214)

Tại sao đây là lỗi nghiêm trọng:

- Bộ dữ liệu của bạn không đơn thuần nói về Cambodia như một quốc gia.
- Nó nói về cộng đồng Khmer ở Việt Nam, với đời sống, phong tục, ngôn ngữ và kinh nghiệm địa phương riêng.
- Khi model kéo mọi thứ về `Campuchia`, nó làm mất chiều kích Khmer Krom.

Đây là lỗi `identity shift` hoặc `geocultural overgeneralization`.

## 5.5. Khái niệm xã hội - văn hóa bị hiểu sai theo nghĩa phổ thông

Trong phần probe regional, một ví dụ rất đáng chú ý là `tình làng nghĩa xóm` bị model trượt sang kiểu `tình yêu gần gũi` trong phần phân tích lỗi tự động tại [regional example](results/km2vi_results_20260518_162617.json#L809).

Điều đó cho thấy model có thể nhận ra từng từ riêng lẻ, nhưng lại fail khi cần dựng đúng cultural concept ở cấp phrase.

## 6. Một số ví dụ tiêu biểu nên đưa vào nghiên cứu

### Ví dụ 1: Sai tên món hoàn toàn

- Reference: `Nùm bong khlanh`
- Hypothesis: `bánh bông lan`
- Vị trí: [line 54](translation_output/all_translations_parallel_20260518_190336.json#L54)
- Nhận xét: sai cultural entity, sai loại món, sai giá trị tư liệu.

### Ví dụ 2: Sai khung lễ hội

- Reference: `Chol Chnam Thmay`
- Hypothesis: `Tết Nguyên Đán`
- Vị trí: [line 4254](translation_output/all_translations_parallel_20260518_190336.json#L4254)
- Nhận xét: model đồng hóa lễ Khmer với lễ Kinh.

### Ví dụ 3: Sai nghi thức tôn giáo

- Reference: `lễ tắm Phật`
- Hypothesis: `rước nước thánh`
- Vị trí: [line 9804](translation_output/all_translations_parallel_20260518_190336.json#L9804)
- Nhận xét: không chỉ mất tên gọi, mà còn thay cả ritual frame.

### Ví dụ 4: Sai chức danh nghi lễ

- Reference: `Achar duki`
- Hypothesis: `thầy Yuki`
- Vị trí: [line 5224](translation_output/all_translations_parallel_20260518_190336.json#L5224)
- Nhận xét: lỗi hallucination theo âm.

### Ví dụ 5: Sai hệ thân tộc

- Reference: `bon Dara`, `uon Srey`
- Hypothesis: `anh Dara`, `em Srey`
- Vị trí: [line 15094](translation_output/all_translations_parallel_20260518_190336.json#L15094)
- Nhận xét: model làm phẳng hệ xưng hô Khmer thành hệ Việt phổ thông.

### Ví dụ 6: Sai định danh cộng đồng

- Reference: nói về `người Khmer`
- Hypothesis: `người dân Campuchia`
- Vị trí: [line 2614](translation_output/all_translations_parallel_20260518_190336.json#L2614)
- Nhận xét: identity shift từ Khmer ở Việt Nam sang Cambodia.

### Ví dụ 7: Sai thành phần ẩm thực

- Reference: `dừa sáp`
- Hypothesis: `nước cốt dừa`
- Vị trí: [line 334](translation_output/all_translations_parallel_20260518_190336.json#L334)
- Nhận xét: model đổi một đặc sản thành nguyên liệu chế biến.

### Ví dụ 8: Sai event semantics

- Reference: `xum họp`
- Hypothesis: `cuộc họp`
- Vị trí: [line 5264](translation_output/all_translations_parallel_20260518_190336.json#L5264)
- Nhận xét: semantic drift từ communal gathering sang formal meeting.

## 7. Vì sao GPT-4o mắc các lỗi này?

Có thể giải thích các lỗi trên bằng một số nguyên nhân khả dĩ:

### 7.1. Frequency bias trong dữ liệu huấn luyện

Các từ Khmer / Khmer Krom ít phổ biến có xác suất thấp hơn trong dữ liệu huấn luyện so với:

- khái niệm văn hóa Kinh quen thuộc
- các món Việt tương đối gần âm
- tri thức phổ thông về Cambodia

Do đó model bị kéo về các mapping phổ biến hơn.

### 7.2. Ưu tiên tính tự nhiên hơn tính bảo toàn thực thể

Khi không chắc, model có xu hướng:

- làm câu nghe tự nhiên hơn
- chọn từ người Việt dễ hiểu hơn
- thay entity lạ bằng entity quen

Đây là chiến lược tốt cho chatbot phổ thông, nhưng không phù hợp với machine translation cho dữ liệu văn hóa.

### 7.3. Thiếu glossary constraint

Nếu không có glossary hoặc terminology list cố định, model sẽ tự quyết định:

- khi nào giữ nguyên từ Khmer
- khi nào dịch sang tiếng Việt
- khi nào đoán nghĩa

Và kết quả là bất nhất.

### 7.4. Thiếu grounding cho Khmer ở Việt Nam

Việc model nhiều lần kéo nội dung sang `Campuchia` cho thấy nó có tri thức chung về Khmer, nhưng không đủ grounding cho biến thể xã hội-văn hóa Khmer ở Việt Nam.

Đây là điểm rất quan trọng cho hướng nghiên cứu của bạn.

## 8. Ý nghĩa đối với nghiên cứu machine translation Khmer-Vi

### 8.1. Chỉ dùng metric tổng quát là chưa đủ

BLEU và chrF++ có thể phản ánh mức tương đồng bề mặt, nhưng không đo hết được cultural loss.

Một câu có thể:

- rất giống reference ở mức từ vựng chung
- nhưng lại sai hoàn toàn ở thực thể văn hóa cốt lõi

Vì vậy, nếu chỉ nhìn BLEU/chrF++, bạn có thể đánh giá quá lạc quan.

### 8.2. Cần human evaluation theo taxonomy lỗi văn hóa

Đối với bài toán Khmer-Vi, đặc biệt Khmer Krom -> Việt, cần thêm human annotation cho các loại lỗi như:

- Identity shift
- Cultural entity substitution
- Ritual domestication
- Kinship flattening
- Semantic drift
- Output artifact

### 8.3. Context là một biến rất quan trọng

Việc tăng +6.13 chrF++ khi có context cho thấy:

- Dịch từng câu đơn lẻ chưa phản ánh hết năng lực thật của model.
- Với discourse mang tính văn hóa cao, translation setting nên cân nhắc thêm context window.

## 9. Taxonomy lỗi đề xuất cho annotation tay

Bạn có thể dùng taxonomy sau để gắn nhãn thủ công trong giai đoạn nghiên cứu tiếp theo.

### 9.1. Identity shift

Định danh cộng đồng bị kéo sang cộng đồng khác.

Ví dụ:

- Khmer ở Việt Nam -> Campuchia

### 9.2. Cultural entity substitution

Thực thể văn hóa gốc bị thay bằng một thực thể khác nghe quen hơn.

Ví dụ:

- nùm bong khlanh -> bánh bông lan
- dừa sáp -> nước cốt dừa

### 9.3. Ritual domestication

Lễ nghi Khmer bị thay bằng khung lễ nghi Kinh hoặc khung phổ thông.

Ví dụ:

- Chol Chnam Thmay -> Tết Nguyên Đán
- lễ tắm Phật -> rước nước thánh

### 9.4. Kinship flattening

Hệ thân tộc Khmer bị quy về hệ anh/em, cha/mẹ thông thường của tiếng Việt.

Ví dụ:

- bon / oun -> anh / em
- role in-law term -> ông/bà thông gia

### 9.5. Semantic drift

Model giữ câu nghe hợp lý nhưng đẩy nghĩa sang frame khác.

Ví dụ:

- xum họp -> cuộc họp
- linh cữu -> mộ

### 9.6. Output artifact

Model tự sinh thêm format marker hoặc text lạ.

Ví dụ:

- `Tiếng Việt:`

## 10. Kết luận cuối cùng

GPT-4o trong bộ dữ liệu này có thể dùng để:

- nắm gist nội dung
- tạo bản dịch đọc được
- hỗ trợ sơ bộ cho người không biết tiếng Khmer

Nhưng GPT-4o chưa đủ đáng tin nếu mục tiêu là:

- bảo tồn đúng tên món ăn, lễ nghi, vai thân tộc, chức danh tôn giáo
- nghiên cứu cultural entities của Khmer ở Việt Nam
- dùng bản dịch như dữ liệu chuẩn cho phân tích dân tộc học hoặc ngôn ngữ học văn hóa

Kết luận thực chất nhất là:

- Model mạnh về fluency.
- Model yếu ở cultural fidelity.
- Model đặc biệt yếu khi phải phân biệt Khmer Krom / Khmer ở Việt Nam với khung tri thức chung về Cambodia.

Nếu dùng kết quả này cho report nghiên cứu, luận điểm trung tâm có thể viết ngắn gọn như sau:

> GPT-4o không thất bại chủ yếu ở mức ngữ pháp hay độ trôi chảy, mà thất bại ở mức bảo toàn bản sắc văn hóa, thực thể văn hóa và định danh cộng đồng. Trong bài toán Khmer-Vi, nhất là với dữ liệu Khmer ở Việt Nam, lỗi nghiêm trọng nhất của model là domestication và overgeneralization: biến cái đặc thù thành cái quen thuộc, và biến Khmer Krom thành Khmer/Cambodia nói chung.
