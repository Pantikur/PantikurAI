#!/usr/bin/env python3
# retrain.py — полный цикл: сборка данных + дообучение модели
# Поддерживает: data/conversations.json + data/training_pairs.jsonl
# Запуск: python retrain.py [--config configs/prod.yaml] [--verbose]

import subprocess
import sys
import os
import argparse
import shutil
import json
import logging
from pathlib import Path
from bot_learns_from_gigachat import generate_self_teaching_dialogs
GIGACHAT_TOKEN = os.getenv("GIGACHAT_TOKEN")

# === Настройки ===
BUILD_SCRIPT = "build_training_data.py"
TRAIN_SCRIPT = "train.py"

# Пути
BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
MODELS_DIR = BASE_DIR / "models"

TRAINING_PAIRS_PATH = DATA_DIR / "training_pairs.jsonl"
CONVERSATIONS_JSON = DATA_DIR / "conversations.json"
TOKENIZER_PATH = DATA_DIR / "tokenizer.json"
MODEL_PATH = MODELS_DIR / "chat_model.pth"

BACKUP_TOKENIZER = DATA_DIR / "tokenizer.json.backup"
BACKUP_MODEL = MODELS_DIR / "chat_model.pth.backup"

# Гиперпараметры (можно вынести в конфиг)
VOCAB_SIZE = 1000
MAX_LENGTH = 32
BATCH_SIZE = 8
EPOCHS = 100
LR = 0.001

# === Логирование ===
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler("logs/retrain.log", encoding="utf-8")
    ]
)
logger = logging.getLogger("retrain")

os.makedirs("logs", exist_ok=True)


def backup_artifacts():
    """Создаёт резервные копии токенизатора и модели"""
    if TOKENIZER_PATH.exists():
        shutil.copy(TOKENIZER_PATH, BACKUP_TOKENIZER)
        logger.info(f"📦 Резервная копия токенизатора: {BACKUP_TOKENIZER}")

    if MODEL_PATH.exists():
        shutil.copy(MODEL_PATH, BACKUP_MODEL)
        logger.info(f"📦 Резервная копия модели: {BACKUP_MODEL}")


def ensure_directories():
    """Создаёт нужные папки"""
    DATA_DIR.mkdir(exist_ok=True)
    MODELS_DIR.mkdir(exist_ok=True)

def enrich_with_gigachat():
    """Запускает сборку данных от GigaChat, если задан токен"""
    if not GIGACHAT_TOKEN:
        logger.warning("⚠️ GIGACHAT_TOKEN не найден — дообучение без данных от GigaChat")
        return

    try:
        generate_self_teaching_dialogs(n=5)  # ← можно настроить n
        logger.info("✅ Диалоги с GigaChat добавлены в conversations.json")
    except Exception as e:
        logger.warning(f"⚠️ GigaChat enrichment не удался: {e}")

def enrich_with_rpg_scenes():
    try:
        import rpg_generator
        rpg_generator.main()
        logger.info("✅ RPG-сцены добавлены в training_pairs.jsonl")
    except Exception as e:
        logger.warning(f"⚠️ RPG enrichment не удался: {e}")


def build_training_data(args):
    """Запускает сборку данных через build_training_data.py"""
    if not os.path.exists(BUILD_SCRIPT):
        logger.error(f"❌ Не найден скрипт: {BUILD_SCRIPT}")
        return False

    cmd = [sys.executable, BUILD_SCRIPT]
    if args.config:
        cmd.extend(["--config", args.config])
    if args.verbose:
        cmd.append("--verbose")
    if args.dry_run:
        cmd.append("--dry-run")

    logger.info(f"🔧 Сборка данных: {' '.format(cmd)}")
    if args.dry_run:
        logger.info("🧪 Режим Dry Run: сборка данных пропущена")
        return True

    result = subprocess.run(cmd, capture_output=False)
    if result.returncode != 0:
        logger.error("❌ Сбор данных не удался.")
        return False

    line_count = 0
    if TRAINING_PAIRS_PATH.exists():
        line_count = sum(1 for _ in open(TRAINING_PAIRS_PATH, 'r', encoding='utf-8'))
        logger.info(f"✅ Данные собраны: {TRAINING_PAIRS_PATH} ({line_count} строк)")
    else:
        logger.warning("🟡 Файл training_pairs.jsonl не создан — возможно, нет новых знаний")

    return True


def has_new_data():
    """Проверяет, есть ли новые данные для обучения"""
    has_training = TRAINING_PAIRS_PATH.exists() and TRAINING_PAIRS_PATH.stat().st_size > 0
    has_conversations = CONVERSATIONS_JSON.exists() and CONVERSATIONS_JSON.stat().st_size > 0
    return has_training or has_conversations


def create_dummy_tokenizer():
    """Создаёт заглушку tokenizer.json"""
    dummy = {
        "vocab": {"<PAD>": 0, "<EOS>": 1, "<UNK>": 2},
        "inverse_vocab": {0: "<PAD>", 1: "<EOS>", 2: "<UNK>"},
        "vocab_size": 3,
        "pad_token": "<PAD>",
        "eos_token": "<EOS>",
        "unk_token": "<UNK>"
    }
    with open(TOKENIZER_PATH, "w", encoding="utf-8") as f:
        json.dump(dummy, f, ensure_ascii=False, indent=2)
    logger.warning(f"⚠️ Создан фиктивный токенизатор: {TOKENIZER_PATH}")


def validate_or_create_tokenizer():
    """Проверяет или создаёт tokenizer.json"""
    if not TOKENIZER_PATH.exists():
        logger.warning(f"⚠️ Токенизатор не найден: {TOKENIZER_PATH}. Создаём заглушку...")
        create_dummy_tokenizer()
        return TOKENIZER_PATH.exists()
    try:
        with open(TOKENIZER_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)
        required = ["vocab", "inverse_vocab", "pad_token", "eos_token"]
        if not all(k in data for k in required):
            raise ValueError("Некорректный формат tokenizer.json")
        logger.info(f"✅ Токенизатор загружен: {len(data['vocab'])} токенов")
    except Exception as e:
        logger.error(f"❌ Ошибка в tokenizer.json: {e}")
        if BACKUP_TOKENIZER.exists():
            logger.info(f"🔄 Восстанавливаем из бэкапа: {BACKUP_TOKENIZER}")
            shutil.copy(BACKUP_TOKENIZER, TOKENIZER_PATH)
            return True
        else:
            logger.warning("🔄 Создаём новый dummy tokenizer...")
            create_dummy_tokenizer()
            return TOKENIZER_PATH.exists()
    return True


def run_training():
    """Запускает обучение через train.py"""
    logger.info("🧠 Запуск обучения...")

    try:
        # Импортируем train.py как модуль
        import train
        if hasattr(train, 'main'):
            train.main()
        else:
            logger.error("❌ В train.py нет функции main()")
            return False
        logger.info("🎉 Обучение завершено успешно!")
        return True
    except ImportError as e:
        logger.error(f"❌ Не удалось импортировать train.py: {e}")
        logger.info("💡 Убедитесь, что train.py находится в корне проекта")
        return False
    except Exception as e:
        logger.error(f"❌ Ошибка при обучении: {e}", exc_info=True)
        return False


def restore_backup():
    """Восстанавливает артефакты из бэкапа"""
    restored = False
    if BACKUP_TOKENIZER.exists() and not TOKENIZER_PATH.exists():
        shutil.copy(BACKUP_TOKENIZER, TOKENIZER_PATH)
        logger.info(f"🔄 Восстановлен токенизатор из бэкапа: {TOKENIZER_PATH}")
        restored = True
    if BACKUP_MODEL.exists() and not MODEL_PATH.exists():
        shutil.copy(BACKUP_MODEL, MODEL_PATH)
        logger.info(f"🔄 Восстановлена модель из бэкапа: {MODEL_PATH}")
        restored = True
    return restored


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
        help="Подробный вывод"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Только показать, что будет сделано"
    )

    args = parser.parse_args()

    ensure_directories()
    enrich_with_gigachat()
    enrich_with_rpg_scenes()

    # === Этап 1: Сборка данных ===
    success = build_training_data(args)
    if not success:
        logger.error("❌ Сбор данных не удался.")
        if not validate_or_create_tokenizer():
            restore_backup()
        if not (TOKENIZER_PATH.exists() and MODEL_PATH.exists()):
            logger.critical("💀 Критическая ошибка: не удалось восстановить артефакты")
            sys.exit(1)
        logger.info("✅ Используем существующие артефакты.")
        return

    if args.dry_run:
        logger.info("🧪 Режим Dry Run: обучение пропущено")
        logger.info("🎉 Готово (симуляция): данные собраны, модель НЕ обучалась.")
        return

    # === Этап 2: Проверка данных и обучение ===
    if not has_new_data():
        logger.info("ℹ️ Нет новых данных для обучения.")
        if not validate_or_create_tokenizer():
            restore_backup()
        logger.info("✅ Используем существующие артефакты. Выход.")
        return

    backup_artifacts()

    # Проверяем/создаём токенизатор
    if not validate_or_create_tokenizer():
        logger.error("❌ Не удалось создать или восстановить токенизатор.")
        sys.exit(1)

    # Запускаем обучение
    success = run_training()
    if not success:
        logger.error("❌ Обучение не удалось. Пытаемся восстановить...")
        if restore_backup():
            logger.info("✅ Артефакты восстановлены из бэкапа.")
        else:
            logger.critical("💀 Не удалось восстановить модель!")
        sys.exit(1)

    # Финальная проверка
    if TOKENIZER_PATH.exists() and MODEL_PATH.exists():
        t_size = TOKENIZER_PATH.stat().st_size // 1024
        m_size = MODEL_PATH.stat().st_size // 1024
        logger.info(f"✅ Успешно: tokenizer.json ({t_size} КБ), chat_model.pth ({m_size} КБ)")
    else:
        logger.critical("❌ Фатально: один из артефактов отсутствует!")
        sys.exit(1)


if __name__ == "__main__":
    main()