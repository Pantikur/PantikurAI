#!/usr/bin/env python3
"""
Загрузка дообученной модели на Hugging Face.

Использование:
    python scripts/upload_to_hf.py              # загрузить все модели
    python scripts/upload_to_hf.py vuglarst     # только vuglarst
    python scripts/upload_to_hf.py --push       # загрузить и запушить

Требования:
    1. HF_TOKEN в .env файле
    2. Авторизация: hf auth login
"""

import os
import sys
import io
from pathlib import Path

# Fix Windows console
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

from dotenv import load_dotenv
load_dotenv()

from huggingface_hub import HfApi, upload_folder

print("=" * 60)
print("[UPLOAD] Загрузка моделей на Hugging Face")
print("=" * 60)

# Проверяем токен
hf_token = os.getenv("HF_TOKEN")
if not hf_token:
    print("[ERROR] HF_TOKEN not found in .env")
    print("   Add HF_TOKEN=hf_... to your .env file")
    sys.exit(1)

print(f"[OK] Token found: {hf_token[:10]}...{hf_token[-5:]}")

# Создаём API
api = HfApi()

# Конфигурация моделей
MODELS = {
    "vuglarst": {
        "local_path": "models/qwen2.5-3b",
        "repo_id": "Pantikur/qwen2.5-3b",
        "description": "Qwen2.5-3B base model",
    },
    "qwen2.5-3b": {
        "local_path": "models/qwen2.5-3b",
        "repo_id": "Pantikur/qwen2.5-3b",
        "description": "Qwen2.5-3B base model",
    },
}


def upload_model(model_name: str) -> bool:
    """Загружает одну модель на Hugging Face."""
    config = MODELS.get(model_name)
    if not config:
        print(f"[ERROR] Model '{model_name}' not found")
        return False
    
    local_path = Path(config["local_path"])
    if not local_path.exists():
        print(f"[ERROR] Local path not found: {local_path}")
        return False
    
    print(f"\n{'='*60}")
    print(f"[UPLOAD] Загрузка: {model_name}")
    print(f"   Local: {local_path}")
    print(f"   Repo: {config['repo_id']}")
    print(f"   Desc: {config['description']}")
    print(f"{'='*60}")
    
    try:
        # Создаём репозиторий если не существует
        try:
            api.create_repo(
                repo_id=config["repo_id"],
                repo_type="model",
                exist_ok=True,
                private=False,  # Публичный для бесплатного хранилища
            )
            print(f"[OK] Repo created/exists: {config['repo_id']}")
        except Exception as e:
            print(f"[WARN] Repo creation: {e}")
        
        # Загружаем папку
        upload_folder(
            folder_path=str(local_path),
            repo_id=config["repo_id"],
            repo_type="model",
            token=hf_token,
        )
        
        print(f"[SUCCESS] Model '{model_name}' uploaded!")
        return True
    
    except Exception as e:
        print(f"[ERROR] Upload failed: {e}")
        return False


def main():
    """Главная функция."""
    args = sys.argv[1:]
    
    if "--list" in args:
        print("[MODELS] Available models:")
        for name, config in MODELS.items():
            print(f"  - {name}: {config['repo_id']}")
        return
    
    if "--push" in args or "-p" in args:
        models_to_upload = list(MODELS.keys())
    elif args:
        models_to_upload = args
    else:
        print("[PROMPT] Which models to upload?")
        print("  Options: qwen2.5-3b, --all")
        print("  Use --list to see available")
        return
    
    success_count = 0
    for model_name in models_to_upload:
        if upload_model(model_name):
            success_count += 1
    
    print(f"\n{'='*60}")
    print(f"[RESULT] Uploaded: {success_count}/{len(models_to_upload)}")
    print(f"{'='*60}")
    
    if success_count > 0:
        print("\n[TIP] To use uploaded model:")
        print("  from transformers import AutoModelForCausalLM")
        print("  model = AutoModelForCausalLM.from_pretrained('Pantikur/qwen2.5-3b')")


if __name__ == "__main__":
    main()
