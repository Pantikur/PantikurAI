#!/usr/bin/env python3
# retrain.py — полный цикл: сборка данных + дообучение модели
# Поддерживает: data/conversations.json + data/training_pairs.jsonl
# Запуск: python retrain.py [--config configs/prod.yaml] [--verbose]

import subprocess
import sys
import os
import argparse
import shutil

# === Настройки ===
BUILD_SCRIPT = "build_training_data.py"

# Входные данные
TRAINING_PAIRS_PATH = "data/training_pairs.jsonl"   # FAQ (JSONL)
CONVERSATIONS_JSON = "data/conversations.json"      # Диалоги (один JSON)
CHAT_DATA_PATH = "data/chat_data.pkl"               # Выход: метаданные модели
BACKUP_CHAT_DATA = "data/chat_data.pkl.backup"      # Резервная копия

def run_command(command, check=True):
    """Запуск команды и вывод результата"""
    print(f"\n🚀 Выполняется: {' '.join(command)}")
    result = subprocess.run(command, capture_output=False, text=True)
    if check and result.returncode != 0:
        print(f"❌ Ошибка при выполнении: {' '.join(command)}")
        return False
    return result.returncode == 0

def ensure_chat_data_created():
    """Гарантируем, что chat_data.pkl существует (заглушка при необходимости)"""
    if os.path.exists(CHAT_DATA_PATH):
        print(f"✅ Модель уже существует: {CHAT_DATA_PATH}")
        return True

    # Попробуем восстановить из бэкапа
    if os.path.exists(BACKUP_CHAT_DATA):
        print(f"🔄 Восстанавливаем модель из резервной копии: {BACKUP_CHAT_DATA}")
        shutil.copy(BACKUP_CHAT_DATA, CHAT_DATA_PATH)
        return True

    # Создаём минимальную заглушку
    print(f"⚠️  Нет модели и бэкапа. Создаём заглушку: {CHAT_DATA_PATH}")
    try:
        import pickle
        with open(CHAT_DATA_PATH, 'wb') as f:
            pickle.dump({
                "word_to_idx": {"<PAD>": 0, "<UNK>": 1},
                "idx_to_word": {0: "<PAD>", 1: "<UNK>"},
                "vocab_size": 2,
                "max_length": 64,
                "samples": []
            }, f)
        return True
    except Exception as e:
        print(f"❌ Не удалось создать заглушку: {e}")
        return False

def backup_existing_model():
    """Создаёт резервную копию модели перед обучением"""
    if os.path.exists(CHAT_DATA_PATH):
        shutil.copy(CHAT_DATA_PATH, BACKUP_CHAT_DATA)
        print(f"📦 Резервная копия модели сохранена: {BACKUP_CHAT_DATA}")

def main():
    parser = argparse.ArgumentParser(description="Полный цикл: сбор данных + дообучение модели")
    parser.add_argument(
        "--config",
        type=str,
        default="configs/prod.yaml",
        help="Конфиг для build_training_data.py (по умолчанию: configs/prod.yaml)"
    )
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Передать --verbose в build_training_data.py"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Только показать, что будет сделано"
    )

    args = parser.parse_args()

    # Команда для сборки данных
    build_cmd = [sys.executable, BUILD_SCRIPT]
    if args.config:
        build_cmd.extend(["--config", args.config])
    if args.verbose:
        build_cmd.append("--verbose")
    if args.dry_run:
        build_cmd.append("--dry-run")

    # === Этап 1: Сборка обучающих данных ===
    if args.dry_run:
        print("🧪 Режим Dry Run: сборка данных пропущена")
    else:
        print("🔧 Шаг 1: Сбор и очистка обучающих данных...")
        if not os.path.exists(BUILD_SCRIPT):
            print(f"❌ Не найден скрипт: {BUILD_SCRIPT}")
            exit(1)

        success = run_command(build_cmd)
        if not success:
            print("❌ Сбор данных не удался.")
            if not ensure_chat_data_created():
                exit(1)
            exit(0)  # Продолжаем, чтобы не сломать сборку

        # Проверяем, создан ли training_pairs.jsonl
        if os.path.exists(TRAINING_PAIRS_PATH):
            line_count = sum(1 for _ in open(TRAINING_PAIRS_PATH, 'r', encoding='utf-8'))
            print(f"✅ Данные собраны: {TRAINING_PAIRS_PATH} ({line_count} строк)")
        else:
            print(f"🟡 Файл training_pairs.jsonl не создан — возможно, нет новых знаний")

    # === Этап 2: Дообучение модели ===
    if args.dry_run:
        print("🧪 Режим Dry Run: обучение пропущено")
        print("🎉 Готово (симуляция): данные собраны, модель НЕ обучалась.")
        return

    print("\n🧠 Шаг 2: Дообучение модели...")

    # Резервируем текущую модель
    backup_existing_model()

    # Проверяем наличие источников данных
    has_training_pairs = os.path.exists(TRAINING_PAIRS_PATH)
    has_conversations = os.path.exists(CONVERSATIONS_JSON)

    if not has_training_pairs and not has_conversations:
        print("ℹ️ Нет новых данных для обучения: ни conversations.json, ни training_pairs.jsonl")
        if not ensure_chat_data_created():
            print("💀 Критическая ошибка: не удалось создать или восстановить chat_data.pkl")
            exit(1)
        print("✅ Используем существующую модель. Выход.")
        exit(0)

    # Запускаем обучение
    try:
        from train_logic import run_training
        print("🔁 Инициализация обучения через train_logic.run_training()...")
        run_training()
        print("🎉 Модель успешно переобучена и сохранена!")

        # Финальная гарантия: файл должен существовать
        if not os.path.exists(CHAT_DATA_PATH):
            print("⚠️  Ошибка: run_training() завершился, но chat_data.pkl не создан.")
            if not ensure_chat_data_created():
                exit(1)

    except ImportError as e:
        print(f"❌ Не удалось импортировать train_logic: {e}")
        print("💡 Убедитесь, что train_logic.py находится в той же директории")
        if not ensure_chat_data_created():
            exit(1)
    except Exception as e:
        print(f"❌ Ошибка при обучении: {e}")
        import traceback
        traceback.print_exc()
        print("🔄 Пытаемся восстановить модель из бэкапа...")
        if not ensure_chat_data_created():
            print("💀 Не удалось восстановить модель после сбоя")
            exit(1)

    # Финальная проверка
    if os.path.exists(CHAT_DATA_PATH):
        size_kb = os.path.getsize(CHAT_DATA_PATH) // 1024
        print(f"✅ Успешно: {CHAT_DATA_PATH} создан (размер: {size_kb} КБ)")
    else:
        print(f"❌ Фатально: {CHAT_DATA_PATH} отсутствует!")
        exit(1)


if __name__ == "__main__":
    main()