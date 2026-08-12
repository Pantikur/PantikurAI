#!/usr/bin/env python3
"""
Загрузка Qwen2.5-3B через transformers.

Этот скрипт скачивает Qwen2.5-3B от Qwen и сохраняет в models/.

Пример:
    python scripts/download_qwen.py
"""

import os
import sys
import io
from pathlib import Path

# Fix Windows console encoding
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

print("=" * 60)
print("[Qwen2.5] Загрузка Qwen2.5-3B от Qwen")
print("=" * 60)

# Проверяем что установлены нужные библиотеки
try:
    import torch
    print(f"[OK] PyTorch: {torch.__version__}")
except ImportError:
    print("[ERROR] Install torch: pip install torch")
    sys.exit(1)

try:
    from transformers import AutoTokenizer, AutoModelForCausalLM
    print("[OK] transformers installed")
except ImportError:
    print("[ERROR] Install transformers: pip install transformers")
    sys.exit(1)

MODEL_NAME = "Qwen/Qwen2.5-3B-Instruct"
SAVE_DIR = Path(__file__).parent.parent / "models" / "qwen2.5-3b"

print(f"\n[INFO] Model: {MODEL_NAME}")
print(f"[INFO] Save to: {SAVE_DIR}")
print(f"[INFO] Size: ~260 MB")
print("-" * 60)

# 1. Загружаем модель и токенizer
print("\n[1/3] Loading model from Hugging Face...")
try:
    tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
    model = AutoModelForCausalLM.from_pretrained(MODEL_NAME)
    print("[OK] Model loaded!")
except Exception as e:
    print(f"[ERROR] Failed to load model: {e}")
    sys.exit(1)

# 2. Сохраняем локально
print(f"\n[2/3] Saving to {SAVE_DIR}...")
SAVE_DIR.mkdir(parents=True, exist_ok=True)

try:
    tokenizer.save_pretrained(str(SAVE_DIR))
    model.save_pretrained(str(SAVE_DIR))
    print("[OK] Model saved!")
except Exception as e:
    print(f"[ERROR] Failed to save: {e}")
    sys.exit(1)

# 3. Проверяем
print(f"\n[3/3] Verifying...")
files = list(SAVE_DIR.glob("*"))
total_size = sum(f.stat().st_size for f in files)
total_size_mb = total_size / (1024 * 1024)

print(f"[OK] Saved {len(files)} files")
print(f"[OK] Total size: {total_size_mb:.0f} MB")

print("\n" + "=" * 60)
print("[SUCCESS] Qwen2.5-3B Small loaded successfully!")
print("=" * 60)
print()
print("Usage in code:")
print(f"    from transformers import AutoTokenizer, AutoModelForCausalLM")
print(f"    tokenizer = AutoTokenizer.from_pretrained('{SAVE_DIR}')")
print(f"    model = AutoModelForCausalLM.from_pretrained('{SAVE_DIR}')")
print()
