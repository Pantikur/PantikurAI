#!/usr/bin/env python3
# build_training_data.py
"""
команда запуска python build_training_data.py
"""

import os
import json
import yaml
import logging
import argparse
import re
from typing import Dict, List, Any
from datetime import datetime

# === === Safe print для Windows (без UnicodeEncodeError) === ===
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

# === === НОВАЯ ФУНКЦИЯ: Сборка токенизатора из данных === ===
def build_vocab_from_data(pairs_file: str, max_vocab_size: int = 10000, min_freq: int = 1) -> Dict[str, Any]:
    """
    Создаёт токенизатор на основе всех слов из training_pairs.jsonl
    :param pairs_file: путь к data/training_pairs.jsonl
    :param max_vocab_size: макс. количество токенов
    :param min_freq: мин. частота слова для добавления
    """
    vocab = {"<PAD>": 0, "<EOS>": 1, "<UNK>": 2}
    inv_vocab = {0: "<PAD>", 1: "<EOS>", 2: "<UNK>"}
    word_counts = {}

    try:
        with open(pairs_file, "r", encoding="utf-8-sig") as f:
            for line in f:
                try:
                    pair = json.loads(line.strip())
                    for key in ["user", "bot"]:
                        if key in pair:
                            text = pair[key].strip()
                            if not text:
                                continue
                            # Декодируем, если это bytes (на всякий)
                            if isinstance(text, bytes):
                                text = text.decode('utf-8-sig')
                            text = text.lower()
                            # Разбиваем на слова, убираем цифры и пунктуацию
                            words = re.findall(r'\b[а-яёa-z0-9]{2,}\b', text)  # только рус. и англ. слова ≥2 букв
                            for word in words:
                                word_counts[word] = word_counts.get(word, 0) + 1
                except Exception as e:
                    logging.debug(f"⚠️ Ошибка при чтении строки: {e}")
                    continue
    except FileNotFoundError:
        logging.warning(f"⚠️ Файл {pairs_file} не найден — пропускаем")
        return {
            "vocab": vocab,
            "inverse_vocab": inv_vocab
        }

    # Сортируем по частоте
    sorted_words = sorted(word_counts.items(), key=lambda x: -x[1])
    idx = 3

    for word, count in sorted_words:
        if count >= min_freq and idx < max_vocab_size:
            vocab[word] = idx
            inv_vocab[idx] = word
            idx += 1

    safe_print(f"[DATA] Создан токенизатор: {len(vocab)} токенов (из {len(word_counts)} уникальных слов)")
    return {
        "vocab": vocab,
        "inverse_vocab": inv_vocab
    }


def setup_logging(verbose: bool):
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=level,
        format="%(asctime)s | %(levelname)s | %(message)s"
    )


def clean_text(text: str) -> str:
    if isinstance(text, bytes):
        text = text.decode('utf-8-sig')
    if not isinstance(text, str):
        return ""
    return text.strip()


def get_field(entry: Dict[str, Any], keys: List[str], default: str = "") -> str:
    for key in keys:
        value = entry.get(key, "").strip()
        if value:
            return value
    return default


def clean_jsonl_file(input_path: str, output_path: str, dry_run: bool) -> bool:
    if not os.path.exists(input_path):
        logging.warning(f"[WARN] Файл не найден: {input_path}")
        return False

    valid_lines = []
    invalid_count = 0

    with open(input_path, 'r', encoding='utf-8-sig') as f:
        for line_num, line in enumerate(f, 1):
            stripped = line.strip()
            if not stripped or stripped.startswith("//"):
                continue
            try:
                json.loads(stripped)
                valid_lines.append(line)
            except json.JSONDecodeError:
                invalid_count += 1
                logging.debug(f"[WARN] Пропущена строка (не JSON): {stripped}")

    if not dry_run:
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        with open(output_path, 'w', encoding='utf-8') as f:
            f.writelines(valid_lines)
        safe_print(f"[OK] {os.path.basename(input_path)} -> очищен")
        if invalid_count:
            logging.debug(f"[INFO] Пропущено {invalid_count} некорректных строк")
    else:
        safe_print(f"[OK] [dry-run] Очистка {os.path.basename(input_path)}")

    return True


def get_response_for_class(label: str, responses: Dict[str, str]) -> str:
    if not label:
        return responses.get("neutral", "Я слышу тебя. Это важно.")

    label_lower = label.lower().strip()

    # Категории с ключевыми словами
    rules = [
        (["bullying_critical", "bullying_severe"], "bullying_critical"),
        (["bullying_moderate"], "bullying_moderate"),
        (["bullying_light"], "bullying_light"),
        (["bullying_victim"], "bullying_victim"),
        (["bullying_perpetrator"], "bullying_perpetrator"),
        (["bullying_witness", "bullying_aftermath"], "bullying_aftermath"),
        (["hope", "faith", "light"], "hope"),
        (["rage", "anger", "wrath", "explosion"], "rage"),
        (["loneliness", "isolation", "alone"], "loneliness"),
        (["disturbing", "madness"], "disturbing"),
        (["cosmic", "horror"], "cosmic_horror"),
        (["existential", "void", "meaning"], "existential"),
        (["positive", "pride", "joy"], "positive"),
        (["negative", "depression", "despair", "pain"], "negative"),
    ]

    for keywords, category in rules:
        if any(kw in label_lower for kw in keywords):
            return responses.get(category, responses.get("neutral", "Я слышу тебя."))

    return responses.get("neutral", "Я слышу тебя.")


def main():
    parser = argparse.ArgumentParser(description="Сбор и генерация обучающих пар для модели")
    parser.add_argument(
        "--config",
        type=str,
        default="configs/prod.yaml",
        help="Путь к конфигурационному файлу (по умолчанию: configs/prod.yaml)"
    )
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Включить подробный вывод"
    )
    parser.add_argument(
        "--dry-run", "-n",
        action="store_true",
        help="Только показать действия, без сохранения"
    )

    args = parser.parse_args()
    setup_logging(args.verbose)
    safe_print("[RUN] Запуск build_training_data.py")

    # Загрузка конфига
    if not os.path.exists(args.config):
        logging.error(f"[ERR] Конфиг не найден: {args.config}")
        exit(1)

    with open(args.config, "r", encoding="utf-8-sig") as f:
        config = yaml.safe_load(f)

    paths = config["paths"]
    responses = config["responses"]
    fields = config["fields"]

    skip_empty = config.get("skip_empty_text", True)
    default_label = config.get("default_label", "neutral")
    data_dir = config.get("data_dir", "data")  # Теперь из конфига

    # Обязательные ответы
    if "neutral" not in responses:
        responses["neutral"] = "Я слышу тебя. Это важно."
        safe_print("[WARN] Ответ 'neutral' не задан — использован стандартный")

    # === Этап 0: Генерация данных из utils/human_params.py и utils/races.py ===
    try:
        safe_print("[DATA] Генерация данных из utils/human_params.py и utils/races.py...")
        from utils.generate_params_training_data import main as generate_params_data
        generate_params_data()
        safe_print("[OK] Данные из utils сгенерированы")
    except Exception as e:
        logging.warning(f"[WARN] Не удалось сгенерировать данные из utils: {e}")

    # === Этап 1: Очистка файлов ===
    clean_files = config["input_files"].get("clean_files", [])
    cleaned_files = []

    for item in clean_files:
        raw = item["raw"]
        clean = item["clean"]
        raw_path = os.path.join(data_dir, raw)
        clean_path = os.path.join(data_dir, clean)
        success = clean_jsonl_file(raw_path, clean_path, args.dry_run)
        if success:
            cleaned_files.append(clean)

    # === Этап 2: Сборка обучающих пар ===
    source_files = config["input_files"]["source_files"]
    all_pairs = []  # Для training_pairs.jsonl
    conversation_sessions = []  # Для conversations.json

    class_counts = {}

    # === Сначала добавляем пары из книг ===
    books_pairs_file = os.path.join(data_dir, "books_training_pairs.jsonl")
    if os.path.exists(books_pairs_file):
        safe_print("[BOOKS] Загрузка пар из книг...")
        book_count = 0
        with open(books_pairs_file, "r", encoding="utf-8") as f:
            for line in f:
                try:
                    pair = json.loads(line.strip())
                    all_pairs.append(pair)
                    book_count += 1
                except:
                    continue
        safe_print(f"[OK] Добавлено {book_count} пар из книг")

    for filename in source_files:
        filepath = os.path.join(data_dir, filename)
        if not os.path.exists(filepath):
            logging.warning(f"[ERR] Файл не найден: {filepath}")
            continue

        file_count = 0
        session = []  # Собираем диалог: user → bot

        with open(filepath, "r", encoding="utf-8-sig") as f:
            for line_num, line in enumerate(f, 1):
                line = line.strip()
                if not line or line.startswith("//"):
                    continue
                try:
                    entry = json.loads(line)
                    text = clean_text(get_field(entry, fields["text"]))
                    label = clean_text(get_field(entry, fields["label"], default_label))

                    if skip_empty and not text:
                        continue

                    response = get_response_for_class(label, responses)
                    pair = {"user": text, "bot": response}
                    all_pairs.append(pair)

                    # Добавляем в диалог: user → bot
                    session.append(text)
                    session.append(response)

                    class_counts[label] = class_counts.get(label, 0) + 1
                    file_count += 1

                except Exception as e:
                    logging.debug(f"[WARN] Пропущена строка в {filename} (line {line_num}): {e}")

        # Сохраняем сессию, если она не пустая
        if len(session) >= 2:
            conversation_sessions.append(session)

        safe_print(f"[INFO] Добавлено {file_count} фраз из {filename}")

    safe_print(f"[OK] Всего сформировано {len(all_pairs)} обучающих пар")
    safe_print(f"[OK] Сформировано {len(conversation_sessions)} диалоговых сессий")

    # === Этап 3: Сохранение данных ===
    if args.dry_run:
        safe_print("[TEST] Режим Dry Run: данные не сохранены.")
    else:
        # --- 1. Сохранение training_pairs.jsonl ---
        train_path = paths["training_pairs"]
        os.makedirs(os.path.dirname(train_path), exist_ok=True)
        with open(train_path, "w", encoding="utf-8") as f:
            for pair in all_pairs:
                f.write(json.dumps(pair, ensure_ascii=False) + "\n")
        safe_print(f"[SAVE] Сохранено в: {train_path}")

        # --- 2. Сохранение conversations.json ---
        conv_path = os.path.join(data_dir, "conversations.json")
        os.makedirs(os.path.dirname(conv_path), exist_ok=True)
        with open(conv_path, "w", encoding="utf-8") as f:
            json.dump(conversation_sessions, f, ensure_ascii=False, indent=2)
        safe_print(f"[SAVE] Сохранены диалоги: {conv_path}")

        # --- 3. Сохранение статистики ---
        stats_path = paths["knowledge_stats"]
        os.makedirs(os.path.dirname(stats_path), exist_ok=True)
        stats = {
            "total_training_pairs": len(all_pairs),
            "total_sessions": len(conversation_sessions),
            "last_update": datetime.now().isoformat(),
            "class_distribution": class_counts,
            "source_files": source_files,
            "cleaned_files": cleaned_files
        }
        with open(stats_path, "w", encoding="utf-8") as f:
            json.dump(stats, f, ensure_ascii=False, indent=2)
        safe_print(f"[INFO] Статистика обновлена: {stats_path}")

        # === Этап 4: Создание токенизатора ===
        tokenizer_path = os.path.join(data_dir, "tokenizer.json")
        vocab_data = build_vocab_from_data(train_path, max_vocab_size=10000, min_freq=1)
        # Добавляем ключи, которые проверяет retrain.py
        vocab_data.setdefault("pad_token", "<PAD>")
        vocab_data.setdefault("eos_token", "<EOS>")
        vocab_data.setdefault("unk_token", "<UNK>")
        vocab_data["vocab_size"] = len(vocab_data["vocab"])
        with open(tokenizer_path, "w", encoding="utf-8") as f:
            json.dump(vocab_data, f, ensure_ascii=False, indent=2)
        safe_print(f"[SAVE] Сохранён токенизатор: {tokenizer_path}")

    # === Итог ===
    safe_print("[INFO] Распределение по классам:")
    for cls, cnt in sorted(class_counts.items()):
        safe_print(f"   {cls}: {cnt}")

    safe_print("\n[HAPPY] Готово! Все данные собраны.")
    safe_print("Запустите ретраин модели:")
    safe_print("python retrain.py")


if __name__ == "__main__":
    main()