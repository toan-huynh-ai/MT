"""
Quick test — load BARTBahnar and translate a few Bahnar sentences to Vietnamese.
Run this first to confirm the model works before running the full experiment.
"""

import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

CHECKPOINT = Path(__file__).parent / "BARTBahnar" / "translation" / "checkpoints" / "BartBanaFinal"

TEST_SENTENCES = [
    "Lăm hnam gŏ kon Bahnar, juăt kơ đei lu khul tơmam pai-sa ayơ kơdrô̆-pha mă ih 'bôh klep-klong loi hăm chăl arih rim năr?",
    "Lu nhôn juăt kơ yua gŏ lơ̆n, gŏ gang, đing 'lao-pơo păng adring-'buh bih kram – đĭ đăng leng kơ klep-klong hăm kơlăm-plĕnh.",
    "Kon Bahnar hăm gơh pơcheh pơjing tơmam pai-sa bih-ti ưh, dah khŏm răt đơ̆ng kơchơ dah đơ̆ng nai?",
]

EXPECTED_REFS = [
    "Trong bếp của người Bahnar, thường có những loại dụng cụ nấu ăn nào đặc trưng mà bạn thấy gắn bó nhất với đời sống hằng ngày?",
    "Bọn mình hay dùng nồi đất, chảo gang, ống tre và vỉ nướng bằng tre – tất cả đều gần gũi với thiên nhiên núi rừng.",
    "Người Bahnar có chế tác dụng cụ nấu ăn thủ công không, hay phải mua ở chợ hoặc nơi khác?",
]


def main():
    print(f"Checkpoint: {CHECKPOINT}", flush=True)

    if not CHECKPOINT.exists():
        print("ERROR: Checkpoint directory not found.")
        sys.exit(1)

    model_file = CHECKPOINT / "model.safetensors"
    if not model_file.exists() or model_file.stat().st_size < 1_000_000:
        print(f"ERROR: model.safetensors missing or too small ({model_file.stat().st_size if model_file.exists() else 0} bytes).")
        print("Run: python download_model.py")
        sys.exit(1)

    print(f"Model file: {model_file.stat().st_size / 1e6:.1f} MB", flush=True)

    import torch
    from transformers import AutoTokenizer, AutoModelForSeq2SeqLM

    device = "cuda" if torch.cuda.is_available() else "cpu"
    print(f"Loading tokenizer...", flush=True)
    tok = AutoTokenizer.from_pretrained(str(CHECKPOINT))
    print(f"Loading model on {device}...", flush=True)
    model = AutoModelForSeq2SeqLM.from_pretrained(str(CHECKPOINT))
    model.to(device)
    model.eval()
    print("Model ready.\n", flush=True)

    print("=" * 60)
    for i, (src, ref) in enumerate(zip(TEST_SENTENCES, EXPECTED_REFS)):
        inputs = tok(src, return_tensors="pt", truncation=True, max_length=512).to(device)
        with torch.no_grad():
            out = model.generate(inputs["input_ids"], max_new_tokens=256, num_beams=4, early_stopping=True)
        hyp = tok.decode(out[0], skip_special_tokens=True)
        print(f"[{i+1}] Bahnar : {src[:80]}...")
        print(f"    Ref    : {ref[:80]}")
        print(f"    Hyp    : {hyp[:80]}")
        print()

    print("Quick test done.")


if __name__ == "__main__":
    main()
