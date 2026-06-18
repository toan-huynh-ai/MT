"""
Download BARTBahnar model checkpoint (model.safetensors, ~1.5 GB).

Run this script once to fetch the model file from GitHub LFS or HuggingFace.

Usage:
    python download_model.py                          # auto-detect
    python download_model.py --proxy http://user:pass@host:port
    python download_model.py --source huggingface     # from HF Hub
    python download_model.py --source github          # from GitHub LFS
"""

import argparse
import hashlib
import os
import sys
import urllib.request
import json
from pathlib import Path

CHECKPOINT_DIR = Path(__file__).parent / "BARTBahnar" / "translation" / "checkpoints" / "BartBanaFinal"
MODEL_FILE = CHECKPOINT_DIR / "model.safetensors"
EXPECTED_SIZE = 1_583_480_280
EXPECTED_SHA256 = "9cf95c0de5d6207a1eb2cdb08bd3a1a0714bf7733f443734fbc63053172230fe"

HF_URL = "https://huggingface.co/IAmSkyDra/BARTBana_Translation/resolve/main/model.safetensors"
GH_LFS_BATCH_URL = "https://github.com/ura-hcmut/BARTBahnar.git/info/lfs/objects/batch"


def make_opener(proxy: str | None):
    if proxy:
        handler = urllib.request.ProxyHandler({"http": proxy, "https": proxy})
    else:
        handler = urllib.request.ProxyHandler({})
    return urllib.request.build_opener(handler)


def get_github_lfs_url(opener) -> str:
    payload = json.dumps({
        "operation": "download",
        "transfers": ["basic"],
        "objects": [{"oid": EXPECTED_SHA256, "size": EXPECTED_SIZE}],
    }).encode("utf-8")
    req = urllib.request.Request(
        GH_LFS_BATCH_URL,
        data=payload,
        headers={
            "Content-Type": "application/vnd.git-lfs+json",
            "Accept": "application/vnd.git-lfs+json",
            "User-Agent": "git-lfs/3.7.1",
        },
    )
    resp = opener.open(req, timeout=30)
    data = json.loads(resp.read())
    return data["objects"][0]["actions"]["download"]["href"]


def download_file(url: str, dest: Path, opener, chunk_size: int = 1 << 20):
    req = urllib.request.Request(url, headers={"User-Agent": "python-downloader/1.0"})
    with opener.open(req, timeout=60) as resp:
        total = int(resp.headers.get("Content-Length", 0))
        downloaded = 0
        with open(dest, "wb") as f:
            while True:
                chunk = resp.read(chunk_size)
                if not chunk:
                    break
                f.write(chunk)
                downloaded += len(chunk)
                if total:
                    pct = downloaded / total * 100
                    mb = downloaded / 1e6
                    print(f"\r  {mb:.1f} MB / {total/1e6:.1f} MB ({pct:.1f}%)", end="", flush=True)
    print()


def verify_file(path: Path) -> bool:
    if not path.exists():
        return False
    if path.stat().st_size != EXPECTED_SIZE:
        print(f"[WARN] Size mismatch: got {path.stat().st_size}, expected {EXPECTED_SIZE}")
        return False
    print("Verifying SHA-256...", flush=True)
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    if h.hexdigest() != EXPECTED_SHA256:
        print(f"[ERROR] SHA-256 mismatch. File may be corrupted.")
        return False
    return True


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--proxy", default=None, help="Proxy URL, e.g. http://user:pass@host:port")
    parser.add_argument("--source", choices=["huggingface", "github", "auto"], default="auto")
    args = parser.parse_args()

    print(f"Destination: {MODEL_FILE}", flush=True)

    if MODEL_FILE.exists() and MODEL_FILE.stat().st_size == EXPECTED_SIZE:
        print("Model file already present (correct size). Verifying hash...", flush=True)
        if verify_file(MODEL_FILE):
            print("File is valid. Nothing to do.")
            return
        else:
            print("Hash check failed, re-downloading...")

    opener = make_opener(args.proxy)

    if args.source in ("github", "auto"):
        print("Fetching GitHub LFS download URL...", flush=True)
        try:
            url = get_github_lfs_url(opener)
            print(f"Got URL. Downloading from GitHub LFS (~1.5 GB)...", flush=True)
            download_file(url, MODEL_FILE, opener)
        except Exception as e:
            if args.source == "github":
                print(f"GitHub LFS download failed: {e}")
                sys.exit(1)
            print(f"GitHub LFS failed: {e}. Falling back to HuggingFace...", flush=True)
            args.source = "huggingface"

    if args.source == "huggingface":
        print(f"Downloading from HuggingFace (~1.5 GB)...", flush=True)
        try:
            download_file(HF_URL, MODEL_FILE, opener)
        except Exception as e:
            print(f"HuggingFace download failed: {e}")
            sys.exit(1)

    if verify_file(MODEL_FILE):
        print(f"\nDownload complete and verified. File saved to:\n  {MODEL_FILE}")
    else:
        print("\n[ERROR] Downloaded file failed verification. Delete and retry.")
        sys.exit(1)


if __name__ == "__main__":
    main()
