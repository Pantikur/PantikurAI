"""
download_image_models.py — Скачивает модели для генерации изображений для Айко.

Модели:
1. PixArt-α Sigma (основная, 4 ГБ) — models/image_models/pixart-sigma
2. Anything V5 (аниме/пиксель-арт, 2 ГБ) — models/image_models/anything-v5
3. PixelArt-Diffusion (специально для пиксель-арта, 2 ГБ) — models/image_models/pixelart-diffusion

Запуск:
    python download_image_models.py [--all] [--pixart] [--anything] [--pixelart]

Все модели скачиваются в папку models/image_models/ и не попадают в git.
"""
from __future__ import annotations

import os
import sys
import io
from pathlib import Path

# Принудительный UTF-8 для Windows
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

MODELS_DIR = Path("models/image_models")

MODELS = {
    "pixart": {
        "repo_id": "PixArt-alpha/PixArt-Sigma-XL-2-1024-MS",
        "local_dir": MODELS_DIR / "pixart-sigma",
        "description": "PixArt-α Sigma (основная, 4 ГБ)",
    },
    "anything": {
        "repo_id": "stablediffusionapi/anything-v5",
        "local_dir": MODELS_DIR / "anything-v5",
        "description": "Anything V5 (аниме стиль, 2 ГБ)",
    },
    "pixelart": {
        "repo_id": "cahyavirayla/PixelArt-Diffusion",
        "local_dir": MODELS_DIR / "pixelart-diffusion",
        "description": "PixelArt-Diffusion (пиксель-арт, 2 ГБ)",
    },
}


def download_model(model_key: str = "all"):
    """Скачивает одну или все модели."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Скачивание моделей для генерации изображений")
    parser.add_argument("model", nargs="?", default="all", choices=list(MODELS.keys()) + ["all"],
                        help="Модель для скачивания (по умолчанию: all)")
    args = parser.parse_args()
    
    if args.model == "all":
        keys = list(MODELS.keys())
    else:
        keys = [args.model]
    
    for key in keys:
        if key not in MODELS:
            print(f"[ERR] Неизвестная модель: {key}")
            continue
        
        config = MODELS[key]
        print(f"\n{'=' * 60}")
        print(f"[DOWNLOAD] {config['description']}")
        print(f"{'=' * 60}")
        print(f"[REPO] {config['repo_id']}")
        print(f"[SAVE] {config['local_dir']}")
        print()
        
        # Проверяем, есть ли уже модель
        if config['local_dir'].exists() and any(config['local_dir'].iterdir()):
            print(f"[WARN] Папка {config['local_dir']} уже существует")
            response = input("Перезаписать? (yes/no): ").strip().lower()
            if response != "yes":
                print("Пропуск...")
                continue
            import shutil
            shutil.rmtree(config['local_dir'])
        
        config['local_dir'].mkdir(parents=True, exist_ok=True)
        
        try:
            from diffusers.pipelines.auto_pipeline import AutoPipelineForText2Image
            import torch
            
            print("[START] Скачивание...")
            
            # Скачиваем модель
            pipeline = AutoPipelineForText2Image.from_pretrained(
                config['repo_id'],
                torch_dtype=torch.float16,
                use_safetensors=True,
            )
            
            # Сохраняем локально
            pipeline.save_pretrained(str(config['local_dir']))
            print(f"[OK] {config['description']} скачана!")
            print(f"[PATH] {config['local_dir'].absolute()}")
            
        except ImportError:
            print("[ERR] diffusers не установлен!")
            print("[FIX] pip install diffusers torch transformers accelerate safetensors")
        except Exception as e:
            print(f"[ERR] Ошибка: {e}")
            print(f"[TIP] Проверь интернет и место на диске (минимум 10 ГБ)")


if __name__ == "__main__":
    download_model()
