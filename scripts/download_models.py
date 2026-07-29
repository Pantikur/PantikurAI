#!/usr/bin/env python3
"""
Скрипт загрузки моделей для PantikurAI.

Использует Hugging Face Hub для загрузки моделей.
Модели хранятся в models/ и не добавляются в Git.

Использование:
    python scripts/download_models.py          # загрузить все модели
    python scripts/download_models.py chat     # загрузить чат-модель
    python scripts/download_models.py --list    # список доступных моделей
"""

import os
import sys
import json
import hashlib
import io
from pathlib import Path
from typing import Optional
from dotenv import load_dotenv

# Fix Windows console encoding
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

# Load .env
load_dotenv()

# Проверяем huggingface_hub
try:
    from huggingface_hub import hf_hub_download, list_repo_files, hf_hub_url
except ImportError:
    print("[ERROR] Install huggingface_hub: pip install huggingface_hub")
    sys.exit(1)


# Конфигурация моделей
MODELS_CONFIG = {
    "chat_model": {
        "repo_id": "Pantikur/pantikur-chat-model",  # Замени на свой!
        "filename": "chat_model.pth",
        "description": "Чат-модель для Вугларст",
        "size_estimate_mb": 52,
    },
    "rugpt3": {
        "repo_id": "sberbank-ai/rugpt3small_based_on_gpt2",
        "filenames": ["config.json", "pytorch_model.bin", "tokenizer.model", "special_tokens_map.json", "tokenizer_config.json"],
        "description": "RUGPT3 Small (Sber)",
        "size_estimate_mb": 260,
    },
}


def get_models_dir() -> Path:
    """Получает путь к директории models."""
    return Path(__file__).parent.parent / "models"


def calculate_hash(filepath: Path) -> str:
    """Вычисляет SHA256 хеш файла."""
    sha256 = hashlib.sha256()
    with open(filepath, "rb") as f:
        for block in iter(lambda: f.read(4096), b""):
            sha256.update(block)
    return sha256.hexdigest()


def download_model(model_name: str) -> bool:
    """Скачивает одну модель."""
    config = MODELS_CONFIG.get(model_name)
    if not config:
        print(f"\n[ERROR] Model '{model_name}' not found in configuration")
        print(f"   Available: {', '.join(MODELS_CONFIG.keys())}")
        return False
    
    models_dir = get_models_dir()
    models_dir.mkdir(parents=True, exist_ok=True)
    
    print(f"\n{'='*60}")
    print(f"[DOWNLOAD] Loading model: {model_name}")
    print(f"   Description: {config['description']}")
    print(f"   Repository: {config['repo_id']}")
    print(f"   Est. size: ~{config['size_estimate_mb']} MB")
    print(f"{'='*60}")
    
    filenames = config.get("filenames") or [config.get("filename", "unknown")]
    
    for filename in filenames:
        dest_path = models_dir / filename
        
        if dest_path.exists():
            print(f"  [SKIP] Already exists: {filename}")
            continue
        
        print(f"  [DOWNLOAD] Loading: {filename}...")
        try:
            local_path = hf_hub_download(
                repo_id=config["repo_id"],
                filename=filename,
                local_dir=str(models_dir),
            )
            print(f"  [OK] Saved: {local_path}")
        except Exception as e:
            print(f"  [ERROR] Failed to load {filename}: {e}")
            print(f"\n   [TIP] Solution:")
            print(f"      1. Replace repo_id in MODELS_CONFIG with your Hugging Face")
            print(f"      2. Or upload manually:")
            print(f"         huggingface-cli upload your-username/repo models/{filename} {filename}")
            return False
    
    print(f"\n  [OK] Model '{model_name}' loaded!")
    return True


def list_models():
    """Показывает список доступных моделей."""
    print("\n[MODEL] Доступные модели:")
    print("=" * 60)
    
    for name, config in MODELS_CONFIG.items():
        print(f"\n  [FOLDER] {name}")
        print(f"     Description: {config['description']}")
        print(f"     Repo: {config['repo_id']}")
        print(f"     Est. size: ~{config['size_estimate_mb']} MB")
        filenames = config.get("filenames") or [config.get("filename", "unknown")]
        print(f"     Files: {', '.join(filenames)}")
    
    print(f"\n{'='*60}")
    print("Usage:")
    print("  python scripts/download_models.py chat          - download chat model")
    print("  python scripts/download_models.py rugpt3         - download RUGPT3")
    print("  python scripts/download_models.py --all          - download all")
    print("  python scripts/download_models.py --list         - this list")


def update_versions_json():
    """Обновляет MODEL_VERSIONS.json."""
    models_dir = get_models_dir()
    versions_file = models_dir / "MODEL_VERSIONS.json"
    
    versions = {}
    
    for name, config in MODELS_CONFIG.items():
        filenames = config.get("filenames") or [config.get("filename", "unknown")]
        model_info = {
            "version": "latest",
            "repo_id": config["repo_id"],
            "size_estimate_mb": config["size_estimate_mb"],
            "files": {},
        }
        
        for filename in filenames:
            filepath = models_dir / filename
            if filepath.exists():
                file_hash = calculate_hash(filepath)
                file_size = filepath.stat().st_size / (1024 * 1024)
                model_info["files"][filename] = {
                    "exists": True,
                    "size_mb": round(file_size, 2),
                    "hash_sha256": file_hash,
                }
            else:
                model_info["files"][filename] = {
                    "exists": False,
                    "size_mb": 0,
                }
        
        versions[name] = model_info
    
    with open(versions_file, "w", encoding="utf-8") as f:
        json.dump(versions, f, ensure_ascii=False, indent=2)
    
    print(f"\n[FILE] Updated: {versions_file}")


def main():
    """Главная функция."""
    args = sys.argv[1:]
    
    if "--list" in args or "-l" in args:
        list_models()
        return
    
    if "--all" in args or "-a" in args:
        models_to_download = list(MODELS_CONFIG.keys())
    elif args:
        models_to_download = args
    else:
        print("[ERROR] Specify model or --all")
        print("   Available: " + ", ".join(MODELS_CONFIG.keys()))
        print("   Use --list for help")
        sys.exit(1)
    
    success_count = 0
    for model_name in models_to_download:
        if download_model(model_name):
            success_count += 1
    
    print(f"\n{'='*60}")
    print(f"[OK] Downloaded: {success_count}/{len(models_to_download)} models")
    print(f"{'='*60}")
    
    # Update versions
    update_versions_json()


if __name__ == "__main__":
    main()
