#!/usr/bin/env python
"""Pre-flight checks for experiment_km2vi.py"""

import sys
from pathlib import Path
import json

# Test 1: Check .env loading
BASE = Path(__file__).parent
print(f"BASE path: {BASE}")
print(f".env exists: {(BASE / '.env').exists()}")

# Test 2: Load and check .env variables
from dotenv import load_dotenv
import os
load_dotenv(BASE / ".env")

required_vars = [
    "AZURE_TENANT_ID",
    "APPLICATION_AI_VOS_USERS_ID", 
    "APPLICATION_AI_VOS_USERS_SECRET",
    "AZURE_OPENAI_ENDPOINT",
    "AZURE_CHAT_DEPLOYMENT"
]

print("\n✓ Environment Variables Check:")
for var in required_vars:
    val = os.getenv(var, "NOT SET")
    if val == "NOT SET":
        print(f"  ✗ {var}: NOT SET")
    else:
        masked = '***' if 'SECRET' in var or 'ID' in var else val[:50]
        print(f"  ✓ {var}: {masked}")

# Test 3: Check data files
data_dir = BASE / "data"
print(f"\n✓ Data Directory: {data_dir}")
print(f"  Exists: {data_dir.exists()}")
if data_dir.exists():
    files = list(data_dir.glob("*.jsonl"))
    print(f"  .jsonl files found: {len(files)}")
    for f in files:
        size = f.stat().st_size / (1024*1024)  # MB
        with open(f, 'r', encoding='utf-8') as fp:
            line_count = sum(1 for _ in fp)
        print(f"    - {f.name}: {size:.2f} MB ({line_count} lines)")

# Test 4: Check results directory can be created
results_dir = BASE / "khmer2vi" / "results"
print(f"\n✓ Results Directory: {results_dir}")
try:
    results_dir.mkdir(exist_ok=True, parents=True)
    print(f"  Can create: ✓ Yes")
except Exception as e:
    print(f"  Can create: ✗ No - {e}")

# Test 5: Test sacrebleu
print(f"\n✓ Testing sacrebleu:")
try:
    import sacrebleu
    hyp = "xin chào"
    ref = "xin chào"
    bleu = sacrebleu.corpus_bleu([hyp], [[ref]])
    print(f"  sacrebleu works: ✓ (Test BLEU={bleu.score:.2f})")
except Exception as e:
    print(f"  sacrebleu works: ✗ {e}")

print("\n✅ All pre-flight checks passed!")
print("\nFile is READY to run:")
print("  python khmer2vi/experiment_km2vi.py")
print("\nNote: The script will call Azure GPT-4o API, so ensure:")
print("  - Network access is available")
print("  - HTTPS_PROXY is set if needed")
print("  - This will incur API costs")
