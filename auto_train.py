# auto_train.py
import subprocess
import sys
import os
import json

# === Настройки ===
CONVERSATIONS_FILE = "data/conversations.json"
GENERATED_FILE = "generated_worlds.json"
TRAIN_SCRIPT = "train.py"  # ваш скрипт обучения

def load_json(path):
    if not os.path.exists(path):
        print(f"❌ Файл не найден: {path}")
        return []
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def save_conversations(conversations):
    os.makedirs("data", exist_ok=True)
    with open(CONVERSATIONS_FILE, "w", encoding="utf-8") as f:
        json.dump(conversations, f, ensure_ascii=False, indent=2)
    print(f"✅ Обновлён {CONVERSATIONS_FILE}")

def run_training():
    if not os.path.exists(TRAIN_SCRIPT):
        print(f"⚠️ Нет файла {TRAIN_SCRIPT}. Пропускаю обучение.")
        return

    print(f"🔥 Запускаю обучение: python {TRAIN_SCRIPT}")
    result = subprocess.run([sys.executable, TRAIN_SCRIPT], capture_output=True, text=True)

    if result.returncode == 0:
        print("✅ Обучение завершено успешно!")
        print(result.stdout)
    else:
        print("❌ Ошибка при обучении:")
        print(result.stderr)

def main():
    print("🚀 Автообучение: добавление данных и запуск train.py")

    # Загружаем все данные
    base_data = load_json(CONVERSATIONS_FILE)
    new_data_raw = load_json(GENERATED_FILE)

    # Конвертируем в пары [input, output]
    new_pairs = [[item["input"], item["output"]] for item in new_data_raw]
    initial_count = len(base_data)
    added_count = 0

    # Добавляем только уникальные
    for pair in new_pairs:
        if pair not in base_data:
            base_data.append(pair)
            added_count += 1

    # Сохраняем
    save_conversations(base_data)
    print(f"➕ Добавлено новых примеров: {added_count}")

    # Запускаем обучение
    run_training()

if __name__ == "__main__":
    main()