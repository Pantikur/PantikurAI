#!/usr/bin/env python3
"""
Загрузка модели на Hugging Face через HF_TOKEN.

Использование:
    python scripts/hf_upload.py
"""

import os
import sys
import io
from pathlib import Path

if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

from dotenv import load_dotenv
load_dotenv()

from huggingface_hub import HfApi, upload_folder

print("=" * 60)
print("[UPLOAD] Загрузка на Hugging Face")
print("=" * 60)

hf_token = os.getenv("HF_TOKEN")
if not hf_token:
    print("[ERROR] HF_TOKEN not in .env")
    sys.exit(1)

print(f"[OK] Token: {hf_token[:10]}...")

api = HfApi()

# Загружаем vuglarst модель
local_path = "models/qwen2.5-3b"
repo_id = "pantikur/qwen2.5-3b"

print(f"\n[UPLOAD] {local_path} → {repo_id}")

try:
    api.create_repo(repo_id=repo_id, repo_type="model", exist_ok=True, private=False)
    print("[OK] Repo ready")
    
    upload_folder(
        folder_path=local_path,
        repo_id=repo_id,
        repo_type="model",
        token=hf_token,
    )
    
    print(f"[SUCCESS] Model uploaded to https://huggingface.co/{repo_id}")
    
except Exception as e:
    print(f"[ERROR] {e}")
    sys.exit(1)
