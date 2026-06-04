# clean_pride_phrases.py

import os
import json

INPUT_FILE = "data/pride_emotional_phrases.jsonl"
OUTPUT_FILE = "data/pride_emotional_phrases_clean.jsonl"

def clean_jsonl():
    if not os.path.exists(INPUT_FILE):
        print(f"❌ Файл не найден: {INPUT_FILE}")
        return

    valid_lines = []
    removed_count = 0

    with open(INPUT_FILE, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    for line in lines:
        stripped = line.strip()
        # Пропускаем пустые строки и комментарии
        if not stripped or stripped.startswith("//"):
            removed_count += 1
            continue
        # Проверяем, что строка — валидный JSON
        try:
            json.loads(stripped)  # Только проверка
            valid_lines.append(line)  # Сохраняем исходную строку (с \n)
        except json.JSONDecodeError:
            print(f"⚠️ Некорректная строка пропущена: {stripped}")
            removed_count += 1

    # Записываем очищенный файл
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        f.writelines(valid_lines)

    print(f"✅ Очистка завершена: {len(valid_lines)} фраз сохранено.")
    print(f"🗑️ Удалено или пропущено: {removed_count} строк.")
    print(f"📄 Очищенный файл сохранён: {OUTPUT_FILE}")

if __name__ == "__main__":
    clean_jsonl()