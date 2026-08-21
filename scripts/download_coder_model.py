"""
download_coder_model.py — Скачивает Qwen2.5-Coder-3B для Нобуки.

Запуск:
  python download_coder_model.py

Модель скачается в: models/qwen2.5-coder-3b/
Размер: ~6 ГБ

Почему Coder?
  • Специально обучена на миллионы строк кода из GitHub
  • Лучше понимает Python, синтаксис, паттерны проектирования
  • Идеальна для Нобуки — она же программист!
  • Та же архитектура, что и Qwen2.5-3B, но «заточена» под код

После скачивания бот будет работать ОФЛАЙН.
"""

import os
import sys
import io
from pathlib import Path

# Принудительный UTF-8 для Windows
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

def main():
    print("=" * 70)
    print("[DOWNLOAD] Qwen2.5-Coder-3B — Модelling для программирования")
    print("=" * 70)
    print()
    print("[INFO] Model will be saved to: models/qwen2.5-coder-3b/")
    print("[SIZE] Approximate size: ~6 GB")
    print("[TIME] 5-30 minutes (depends on internet speed)")
    print()
    print("[WHY CODER?]")
    print("  ✅ Специально обучена на коде (GitHub, StackOverflow, документация)")
    print("  ✅ Понимает Python, синтаксис, паттерны, антипаттерны")
    print("  ✅ Лучше справляется с задачами программирования")
    print("  ✅ Идеальна для Нобуки — она же инженер проекта!")
    print()
    
    # Проверяем, есть ли уже модель
    model_path = Path("models/qwen2.5-coder-3b")
    if model_path.exists() and any(model_path.iterdir()):
        print(f"[WARN] Folder {model_path} already exists and is not empty")
        response = input("Overwrite? (yes/no): ").strip().lower()
        if response != "yes":
            print("Cancelled.")
            return
        print("Removing old files...")
        import shutil
        shutil.rmtree(model_path)
    
    model_path.mkdir(parents=True, exist_ok=True)
    
    print("[START] Downloading...")
    print()
    
    try:
        from transformers import AutoTokenizer, AutoModelForCausalLM
        
        model_id = "Qwen/Qwen2.5-Coder-3B-Instruct"
        print(f"[DOWNLOAD] From: {model_id}")
        print(f"[SAVE] To: {model_path}")
        print()
        
        # Скачиваем токенер
        print("[1/2] Downloading tokenizer...")
        tokenizer = AutoTokenizer.from_pretrained(model_id, trust_remote_code=True)
        tokenizer.save_pretrained(str(model_path))
        print("[OK] Tokenizer saved")
        
        # Скачиваем модель
        print()
        print("[2/2] Downloading model (~6 GB)...")
        model = AutoModelForCausalLM.from_pretrained(
            model_id,
            torch_dtype="auto",
            device_map="cpu",  # Скачиваем на CPU
            trust_remote_code=True,
        )
        model.save_pretrained(str(model_path))
        print("[OK] Model saved")
        
        print()
        print("=" * 70)
        print("[SUCCESS] DONE!")
        print("=" * 70)
        print()
        print(f"[PATH] Model available at: {model_path.absolute()}")
        print("[INFO] Bot will now load this model on every start")
        print("[OFFLINE] No connection to HuggingFace required anymore")
        print()
        print("[NEXT] Next step: restart bot (python main.py)")
        print()
        
    except Exception as e:
        print()
        print("=" * 70)
        print("[ERROR] Download failed")
        print("=" * 70)
        print(f"[REASON] {e}")
        print()
        print("[TIPS] Possible solutions:")
        print("   1. Check your internet connection")
        print("   2. Make sure you have at least 10 GB free disk space")
        print("   3. Try installing: pip install transformers accelerate")
        print()
        sys.exit(1)


if __name__ == "__main__":
    main()
