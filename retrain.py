#!/usr/bin/env python3
# retrain.py — полный цикл: сборка данных + дообучение модели
# Запуск: python retrain.py [--config configs/prod.yaml] [--verbose]

import subprocess
import sys
import os
import argparse

# Настройки
BUILD_SCRIPT = "build_training_data.py"
TRAINING_PAIRS_PATH = "data/training_pairs.jsonl"
CONVERSATIONS_PATH = "data/conversations.jsonl"

def run_command(command, check=True):
    """Запуск команды и вывод результата"""
    print(f"\n🚀 Выполняется: {' '.join(command)}")
    result = subprocess.run(command, capture_output=False, text=True)
    if check and result.returncode != 0:
        print(f"❌ Ошибка при выполнении: {' '.join(command)}")
        return False
    return result.returncode == 0

def main():
    parser = argparse.ArgumentParser(description="Полный цикл: сбор данных + дообучение")
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

    # Собираем аргументы для build_training_data.py
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
            exit(1)

        if not os.path.exists(TRAINING_PAIRS_PATH):
            print(f"❌ Ожидался файл: {TRAINING_PAIRS_PATH}, но его нет!")
            exit(1)

        print(f"✅ Данные собраны: {TRAINING_PAIRS_PATH}")

    # === Этап 2: Дообучение модели ===
    if args.dry_run:
        print("🧪 Режим Dry Run: обучение пропущено")
        print("🎉 Готово (симуляция): данные собраны, модель НЕ обучалась.")
        return

    print("\n🧠 Шаг 2: Дообучение модели...")

    # Проверим, есть ли вообще данные для обучения
    if not os.path.exists(TRAINING_PAIRS_PATH) and not os.path.exists(CONVERSATIONS_PATH):
        print("❌ Нет данных для обучения: ни training_pairs.jsonl, ни conversations.jsonl")
        exit(1)

    try:
        from train_logic import run_training
        print("🔁 Инициализация обучения...")
        run_training()
        print("🎉 Модель успешно переобучена и сохранена!")
    except ImportError as e:
        print(f"❌ Не удалось импортировать train_logic: {e}")
        print("💡 Убедитесь, что у вас есть файл train_logic.py с функцией run_training()")
        exit(1)
    except Exception as e:
        print(f"❌ Ошибка при обучении: {e}")
        exit(1)


if __name__ == "__main__":
    main()