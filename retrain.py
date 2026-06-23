#!/usr/bin/env python3
# retrain.py — полный цикл: сборка данных + ретраин модели (обучение с нуля)
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


def safe_print(msg: str):
    """Заменяет эмодзи на ASCII, чтобы не падать в Windows console"""
    emojis = {
        '🚀': '[RUN]', '✅': '[OK]', '❌': '[ERR]', '💾': '[SAVE]',
        '📦': '[DATA]', '📚': '[LIB]', '🧠': '[AI]', '🔥': '[🔥]',
        '🎉': '[HAPPY]', '⚠️': '[WARN]', 'ℹ️': '[INFO]', '❤️': '[HEART]'
    }
    for e, t in emojis.items():
        msg = msg.replace(e, t)
    print(msg, flush=True)


def backup_artifacts():
    """Создаёт резервные копии токенизатора и модели"""
    if TOKENIZER_PATH.exists():
        shutil.copy(TOKENIZER_PATH, BACKUP_TOKENIZER)
        logger.info(f"[SAVE] Резервная копия токенизатора: {BACKUP_TOKENIZER}")

    if MODEL_PATH.exists():
        shutil.copy(MODEL_PATH, BACKUP_MODEL)
        logger.info(f"[SAVE] Резервная копия модели: {BACKUP_MODEL}")


def ensure_directories():
    """Создаёт нужные папки"""
    DATA_DIR.mkdir(exist_ok=True)
    MODELS_DIR.mkdir(exist_ok=True)


def enrich_with_gigachat(n: int = 10):
    """Запускает сборку данных от GigaChat, если задан токен"""
    if not GIGACHAT_TOKEN:
        logger.warning("[WARN] GIGACHAT_TOKEN не найден — ретраин без данных от GigaChat")
        return

    try:
        # Сначала генерируем новые данные
        logger.info(f"[AI] Генерация {n} новых диалогов через GigaChat...")
        import subprocess
        result = subprocess.run(
            [sys.executable, "generate_training_data.py", "--count", str(n), "--all"],
            capture_output=True,
            text=True,
            timeout=600
        )
        if result.stdout:
            for line in result.stdout.split('\n'):
                if line.strip():
                    safe_print(line)
        if result.returncode != 0 and result.stderr:
            logger.warning(f"[WARN] Генерация данных: {result.stderr[:200]}")
        logger.info("[OK] Диалоги с GigaChat добавлены в conversations.json")
    except subprocess.TimeoutExpired:
        logger.warning("[WARN] Генерация данных таймаут (600 сек)")
    except Exception as e:
        logger.warning(f"[WARN] GigaChat enrichment не удался: {e}")


def enrich_with_rpg_scenes():
    try:
        import rpg_generator
        rpg_generator.main()
        logger.info("[OK] RPG-сцены добавлены в training_pairs.jsonl")
    except Exception as e:
        logger.warning(f"[WARN] RPG enrichment не удался: {e}")


def build_training_data(args):
    """Запускает сборку данных через build_training_data.py"""
    if not os.path.exists(BUILD_SCRIPT):
        logger.error(f"[ERR] Не найден скрипт: {BUILD_SCRIPT}")
        return False

    cmd = [sys.executable, BUILD_SCRIPT]
    if args.config:
        cmd.extend(["--config", args.config])
    if args.verbose:
        cmd.append("--verbose")
    if args.dry_run:
        cmd.append("--dry-run")

    logger.info(f"[DATA] Сборка данных: {' '.join(cmd)}")
    if args.dry_run:
        logger.info("[TEST] Режим Dry Run: сборка данных пропущена")
        return True

    result = subprocess.run(cmd, capture_output=False)
    if result.returncode != 0:
        logger.error("[ERR] Сбор данных не удался.")
        return False

    line_count = 0
    if TRAINING_PAIRS_PATH.exists():
        line_count = sum(1 for _ in open(TRAINING_PAIRS_PATH, 'r', encoding='utf-8'))
        logger.info(f"[OK] Данные собраны: {TRAINING_PAIRS_PATH} ({line_count} строк)")
    else:
        logger.warning("[WARN] Файл training_pairs.jsonl не создан — возможно, нет новых знаний")

    return True


def generate_params_training_data():
    """Генерирует обучающие данные из utils/human_params.py и utils/races.py"""
    try:
        logger.info("[DATA] Генерация данных из utils (human_params, races)...")
        result = subprocess.run(
            [sys.executable, "utils/generate_params_training_data.py"],
            capture_output=True,
            text=True,
            timeout=120
        )
        if result.stdout:
            for line in result.stdout.split('\n'):
                if line.strip():
                    safe_print(line)
        if result.returncode != 0 and result.stderr:
            logger.warning(f"[WARN] Генерация данных из utils: {result.stderr[:200]}")
        logger.info("[OK] Данные из utils сгенерированы")
        return True
    except subprocess.TimeoutExpired:
        logger.warning("[WARN] Генерация данных из utils таймаут (120 сек)")
        return False
    except Exception as e:
        logger.warning(f"[WARN] Генерация данных из utils не удалась: {e}")
        return False

    result = subprocess.run(cmd, capture_output=False)
    if result.returncode != 0:
        logger.error("[ERR] Сбор данных не удался.")
        return False

    line_count = 0
    if TRAINING_PAIRS_PATH.exists():
        line_count = sum(1 for _ in open(TRAINING_PAIRS_PATH, 'r', encoding='utf-8'))
        logger.info(f"[OK] Данные собраны: {TRAINING_PAIRS_PATH} ({line_count} строк)")
    else:
        logger.warning("[WARN] Файл training_pairs.jsonl не создан — возможно, нет новых знаний")

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
    logger.warning(f"[WARN] Создан фиктивный токенизатор: {TOKENIZER_PATH}")


def validate_or_create_tokenizer():
    """Проверяет или создаёт tokenizer.json"""
    if not TOKENIZER_PATH.exists():
        logger.warning(f"[WARN] Токенизатор не найден: {TOKENIZER_PATH}. Создаём заглушку...")
        create_dummy_tokenizer()
        return TOKENIZER_PATH.exists()
    try:
        with open(TOKENIZER_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)
        required = ["vocab", "inverse_vocab", "pad_token", "eos_token"]
        if not all(k in data for k in required):
            raise ValueError("Некорректный формат tokenizer.json")
        logger.info(f"[OK] Токенизатор загружен: {len(data['vocab'])} токенов")
    except Exception as e:
        logger.error(f"[ERR] Ошибка в tokenizer.json: {e}")
        if BACKUP_TOKENIZER.exists():
            logger.info(f"[INFO] Восстанавливаем из бэкапа: {BACKUP_TOKENIZER}")
            shutil.copy(BACKUP_TOKENIZER, TOKENIZER_PATH)
            return True
        else:
            logger.warning("[INFO] Создаём новый dummy tokenizer...")
            create_dummy_tokenizer()
            return TOKENIZER_PATH.exists()
    return True


def run_training():
    """Запускает ретраин (обучение с нуля) через train.py"""
    logger.info("[FIRE] Запуск ретраина (обучение с нуля)...")

    try:
        # Импортируем train.py как модуль
        import train
        if hasattr(train, 'main'):
            train.main()
        else:
            logger.error("[ERR] В train.py нет функции main()")
            return False
        logger.info("[HAPPY] Обучение завершено успешно!")
        return True
    except ImportError as e:
        logger.error(f"[ERR] Не удалось импортировать train.py: {e}")
        logger.info("[INFO] Убедитесь, что train.py находится в корне проекта")
        return False
    except Exception as e:
        logger.error(f"[ERR] Ошибка при обучении: {e}", exc_info=True)
        return False


def restore_backup():
    """Восстанавливает артефакты из бэкапа"""
    restored = False
    if BACKUP_TOKENIZER.exists() and not TOKENIZER_PATH.exists():
        shutil.copy(BACKUP_TOKENIZER, TOKENIZER_PATH)
        logger.info(f"[INFO] Восстановлен токенизатор из бэкапа: {TOKENIZER_PATH}")
        restored = True
    if BACKUP_MODEL.exists() and not MODEL_PATH.exists():
        shutil.copy(BACKUP_MODEL, MODEL_PATH)
        logger.info(f"[INFO] Восстановлена модель из бэкапа: {MODEL_PATH}")
        restored = True
    return restored


def main():
    parser = argparse.ArgumentParser(description="Полный цикл: сбор данных + ретраин модели (обучение с нуля)")
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
    parser.add_argument(
        "--generate",
        type=int,
        default=10,
        help="Количество диалогов для генерации (по умолчанию: 10, 0 = отключить)"
    )

    args = parser.parse_args()

    ensure_directories()
    
    # === Этап 0: Генерация данных из utils ===
    generate_params_training_data()
    
    if args.generate > 0:
        enrich_with_gigachat(n=args.generate)
    enrich_with_rpg_scenes()

    # === Этап 1: Сборка данных ===
    success = build_training_data(args)
    if not success:
        logger.error("[ERR] Сбор данных не удался.")
        if not validate_or_create_tokenizer():
            restore_backup()
        if not (TOKENIZER_PATH.exists() and MODEL_PATH.exists()):
            logger.critical("[ERR] Критическая ошибка: не удалось восстановить артефакты")
            sys.exit(1)
        logger.info("[OK] Используем существующие артефакты.")
        return

    if args.dry_run:
        logger.info("[TEST] Режим Dry Run: обучение пропущено")
        logger.info("[HAPPY] Готово (симуляция): данные собраны, модель НЕ обучалась.")
        return

    # === Этап 2: Проверка данных и обучение ===
    if not has_new_data():
        logger.info("[INFO] Нет новых данных для обучения.")
        if not validate_or_create_tokenizer():
            restore_backup()
        logger.info("[OK] Используем существующие артефакты. Выход.")
        return

    backup_artifacts()

    # Проверяем/создаём токенизатор
    if not validate_or_create_tokenizer():
        logger.error("[ERR] Не удалось создать или восстановить токенизатор.")
        sys.exit(1)

    # Запускаем обучение
    success = run_training()
    if not success:
        logger.error("[ERR] Обучение не удалось. Пытаемся восстановить...")
        if restore_backup():
            logger.info("[OK] Артефакты восстановлены из бэкапа.")
        else:
            logger.critical("[ERR] Не удалось восстановить модель!")
        sys.exit(1)

    # Финальная проверка
    if TOKENIZER_PATH.exists() and MODEL_PATH.exists():
        t_size = TOKENIZER_PATH.stat().st_size // 1024
        m_size = MODEL_PATH.stat().st_size // 1024
        logger.info(f"[OK] Успешно: tokenizer.json ({t_size} КБ), chat_model.pth ({m_size} КБ)")
    else:
        logger.critical("[ERR] Фатально: один из артефактов отсутствует!")
        sys.exit(1)


if __name__ == "__main__":
    main()