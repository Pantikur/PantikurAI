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
MODEL_PATH = MODELS_DIR / "qwen2.5-3b"

BACKUP_TOKENIZER = DATA_DIR / "tokenizer.json.backup"
BACKUP_MODEL = MODELS_DIR / "qwen2.5-3b.backup"

# Гиперпараметры (можно вынести в конфиг)
VOCAB_SIZE = 1000
MAX_LENGTH = 32
BATCH_SIZE = 8
EPOCHS = 100
LR = 0.001

# === Логирование ===
# Принудительный UTF-8 для Windows
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

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
    """Генерирует обучающие данные из utils (human_params, races, character)"""
    try:
        logger.info("[DATA] Генерация данных из utils (human_params, races, character)...")
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


def learn_from_books(args):
    """Собирает знания из книг через book_learner.py"""
    if not args.books:
        logger.info("[BOOKS] Обучение из книг отключено (используйте --books)")
        return True
    
    try:
        logger.info("[BOOKS] Запуск автономного обучения из книг...")
        result = subprocess.run(
            [sys.executable, "utils/book_learner.py"],
            capture_output=True,
            text=True,
            timeout=600  # 10 минут на сбор книг
        )
        if result.stdout:
            for line in result.stdout.split('\n'):
                if line.strip():
                    safe_print(line)
        if result.returncode != 0 and result.stderr:
            logger.warning(f"[WARN] Обучение из книг: {result.stderr[:200]}")
        logger.info("[OK] Обучение из книг завершено")
        return True
    except subprocess.TimeoutExpired:
        logger.warning("[WARN] Обучение из книг таймаут (10 мин)")
        return False
    except Exception as e:
        logger.warning(f"[WARN] Обучение из книг не удалась: {e}")
        return False


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


def merge_generated_worlds():
    """Добавляет сгенерированные миры (generated_worlds.json) в conversations.json.
    Раньше это делал отдельный скрипт auto_train.py."""
    generated_file = BASE_DIR / "generated_worlds.json"

    if not generated_file.exists():
        logger.info("[WORLD] generated_worlds.json не найден — пропускаем")
        return 0

    if not CONVERSATIONS_JSON.exists():
        logger.warning("[WARN] conversations.json не найден — пропускаем мердж")
        return 0

    try:
        with open(generated_file, "r", encoding="utf-8") as f:
            new_data_raw = json.load(f)
    except Exception as e:
        logger.warning(f"[WARN] Не удалось прочитать generated_worlds.json: {e}")
        return 0

    if not isinstance(new_data_raw, list):
        logger.warning("[WARN] generated_worlds.json — не список, пропускаем")
        return 0

    with open(CONVERSATIONS_JSON, "r", encoding="utf-8") as f:
        base_data = json.load(f)

    if not isinstance(base_data, list):
        logger.warning("[WARN] conversations.json — не список, пропускаем мердж")
        return 0

    new_pairs = []
    for item in new_data_raw:
        if isinstance(item, dict) and item.get("input") and item.get("output"):
            new_pairs.append([str(item["input"]), str(item["output"])])

    added = 0
    for pair in new_pairs:
        if pair not in base_data:
            base_data.append(pair)
            added += 1

    if added > 0:
        with open(CONVERSATIONS_JSON, "w", encoding="utf-8") as f:
            json.dump(base_data, f, ensure_ascii=False, indent=2)
        logger.info(f"[DATA] Добавлено новых примеров из миров: {added}")
    else:
        logger.info("[DATA] Новых примеров из generated_worlds.json нет")

    return added


def watch_data_changes():
    """Режим слежения за изменениями данных (раньше auto_retrain.py).
    Запускает полный ретраин при изменении conversations.json / training_pairs.jsonl."""
    from watchdog.observers import Observer
    from watchdog.events import FileSystemEventHandler

    watched_files = ["conversations.json", "training_pairs.jsonl"]

    class RetrainHandler(FileSystemEventHandler):
        def on_modified(self, event):
            if event.is_directory:
                return
            filename = os.path.basename(event.src_path)
            if filename not in watched_files:
                return

            logger.info(f"[WATCH] Изменён файл: {filename}")
            logger.info("[WATCH] Запускаем полный ретраин...")
            cmd = [sys.executable, os.path.basename(__file__)]

            try:
                result = subprocess.run(
                    cmd + ["--generate", "0"],
                    check=False,
                    capture_output=True,
                    text=True,
                    timeout=7200,
                )
                if result.returncode == 0:
                    logger.info("[WATCH] Ретраин успешно завершён")
                else:
                    logger.error(f"[WATCH] Ошибка ретраина: {result.stderr[:500]}")
            except subprocess.TimeoutExpired:
                logger.error("[WATCH] Ретраин превысил лимит (2 часа)")
            except Exception as e:
                logger.error(f"[WATCH] Ошибка: {e}")

    print(f"👀 Слежение за папкой: {DATA_DIR}")
    print("💡 Измените conversations.json или training_pairs.jsonl — начнётся обучение")

    event_handler = RetrainHandler()
    observer = Observer()
    observer.schedule(event_handler, path=str(DATA_DIR), recursive=False)
    observer.start()

    try:
        while True:
            import time as _time
            _time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
        print("\n🛑 Слежение остановлено")

    observer.join()


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

    parser.add_argument(
        "--books",
        action="store_true",
        help="Включить обучение из книг (автономный сбор знаний)"
    )

    parser.add_argument(
        "--merge-generated",
        action="store_true",
        help="Добавить сгенерированные миры (generated_worlds.json) в conversations.json перед обучением"
    )

    parser.add_argument(
        "--watch",
        action="store_true",
        help="Режим слежения: запускает ретраин при изменении файлов данных (раньше auto_retrain.py)"
    )

    args = parser.parse_args()

    # === Режим слежения (раньше auto_retrain.py) ===
    if args.watch:
        watch_data_changes()
        return

    ensure_directories()

    # === Мердж сгенерированных миров (раньше auto_train.py) ===
    if args.merge_generated:
        merge_generated_worlds()

    # === Этап 0: Генерация данных из utils ===
    generate_params_training_data()
    
    # === Этап 0.5: Обучение из книг (если включено) ===
    learn_from_books(args)
    
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
        logger.info(f"[OK] Успешно: tokenizer.json ({t_size} КБ), qwen2.5-3b ({m_size} КБ)")
    else:
        logger.critical("[ERR] Фатально: один из артефактов отсутствует!")
        sys.exit(1)


if __name__ == "__main__":
    main()