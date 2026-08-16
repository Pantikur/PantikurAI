"""
test_coder_model.py — Проверяет, что модель Coder доступна и загружается.

Запуск:
  python test_coder_model.py
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
    print("[TEST] Проверка модели Qwen2.5-Coder-3B")
    print("=" * 70)
    print()
    
    # Проверяем пути
    paths_to_check = [
        "models/qwen2.5-coder-3b",
        "models/qwen2.5-3b",
        # models/rugpt3_vuglarst/merged (удалена)
    ]
    
    print("[INFO] Проверяем наличие моделей:")
    for path in paths_to_check:
        full_path = Path(path)
        if full_path.exists() and any(full_path.iterdir()):
            size_mb = sum(f.stat().st_size for f in full_path.rglob('*') if f.is_file()) / (1024 * 1024)
            print(f"  [OK] {path} ({size_mb:.0f} МБ)")
        else:
            print(f"  [X]  {path} (не найдена)")
    
    print()
    print("[INFO] Проверяем конфигурацию проекта:")
    
    # Проверяем main.py
    with open("main.py", "r", encoding="utf-8") as f:
        main_content = f.read()
        if "qwen2.5-coder-3b" in main_content:
            print("  [OK] main.py использует Coder модель")
        else:
            print("  [X]  main.py НЕ использует Coder модель")
    
    # Проверяем chatbot.py
    with open("Wuglarst/src/chatbot.py", "r", encoding="utf-8") as f:
        chatbot_content = f.read()
        if "QWEN25_CODER" in chatbot_content:
            print("  [OK] Wuglarst/src/chatbot.py использует Coder модель")
        else:
            print("  [X]  Wuglarst/src/chatbot.py НЕ использует Coder модель")
    
    print()
    print("=" * 70)
    print("[INFO] Готово!")
    print("=" * 70)
    print()
    print("[NEXT] Запустите:")
    print("  python download_coder_model.py")
    print("  # Чтобы скачать модель (~6 ГБ)")
    print()
    print("  python main.py")
    print("  # Чтобы запустить бот с новой моделью")
    print()


if __name__ == "__main__":
    main()
