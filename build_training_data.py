#!/usr/bin/env python3
# build_training_data.py
"""
Генерация обучающих пар user → bot из JSONL-файлов.

Использование:
    python build_training_data.py [--config data/config.yaml] [--verbose] [--dry-run]
"""

import os
import json
import yaml
import logging
import argparse
from typing import Dict, List, Any

# Настройка логирования
def setup_logging(verbose: bool):
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=level,
        format="%(levelname)s | %(message)s"
    )

# Универсальный clean_text
def clean_text(text: str) -> str:
    return text.strip() if text else ""

# Функция для безопасного чтения значения из словаря по нескольким ключам
def get_field(entry: Dict[str, Any], keys: List[str], default: str = "") -> str:
    for key in keys:
        value = entry.get(key, "").strip()
        if value:
            return value
    return default

# Очистка JSONL от комментариев
def clean_jsonl_file(input_path: str, output_path: str, dry_run: bool) -> bool:
    if not os.path.exists(input_path):
        logging.error(f"❌ Файл не найден: {input_path}")
        return False

    valid_lines = []
    invalid_count = 0

    with open(input_path, 'r', encoding='utf-8') as f:
        for line_num, line in enumerate(f, 1):
            stripped = line.strip()
            if not stripped or stripped.startswith("//"):
                continue
            try:
                json.loads(stripped)
                valid_lines.append(line)
            except json.JSONDecodeError:
                invalid_count += 1
                logging.debug(f"⚠️ Пропущена строка (не JSON): {stripped}")

    if not dry_run:
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        with open(output_path, 'w', encoding='utf-8') as f:
            f.writelines(valid_lines)
        logging.info(f"✅ {input_path} → очищен в {output_path}")
        if invalid_count:
            logging.debug(f"ℹ️ Пропущено {invalid_count} некорректных строк")
    else:
        logging.info(f"✅ [dry-run] Очистка {input_path} → {output_path}")

    return True

# Генерация ответа по метке
def get_response_for_class(label: str, responses: Dict[str, str]) -> str:
    if not label:
        return "Я слышу тебя. Это важно."

    label_lower = label.lower()

    if any(kw in label_lower for kw in ["hope", "faith", "light"]):
        return responses.get("hope", responses["neutral"])
    if any(kw in label_lower for kw in ["rage", "anger", "wrath", "explosion"]):
        return responses.get("rage", responses["negative"])
    if any(kw in label_lower for kw in ["loneliness", "isolation", "alone"]):
        return responses.get("loneliness", responses["negative"])
    if "disturbing" in label_lower or "madness" in label_lower:
        return responses.get("disturbing", responses["negative"])
    if "cosmic" in label_lower or "horror" in label_lower:
        return responses.get("cosmic_horror", responses["negative"])
    if any(kw in label_lower for kw in ["existential", "void", "meaning"]):
        return responses.get("existential", responses["neutral"])
    if any(kw in label_lower for kw in ["positive", "pride", "joy"]):
        return responses.get("positive", responses["positive"])
    if any(kw in label_lower for kw in ["negative", "depression", "despair", "pain"]):
        return responses.get("negative", responses["negative"])

    return responses.get("neutral", "Я слышу тебя. Это важно.")

# Основная функция
def main():
    parser = argparse.ArgumentParser(description="Сбор и генерация обучающих пар для модели")
    parser.add_argument(
        "--config",
        type=str,
        default="data/config.yaml",
        help="Путь к конфигурационному файлу (по умолчанию: data/config.yaml)"
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
    logging.info("🚀 Запуск build_training_data.py")

    # Загрузка конфига
    if not os.path.exists(args.config):
        logging.error(f"❌ Конфиг не найден: {args.config}")
        exit(1)

    with open(args.config, "r", encoding="utf-8") as f:
        config = yaml.safe_load(f)

    paths = config["paths"]
    responses = config["responses"]
    fields = config["fields"]
    skip_empty = config.get("skip_empty_text", True)
    default_label = config.get("default_label", "neutral")
    data_dir = "data"

    # === Этап 1: Очистка файлов ===
    clean_files = config["input_files"]["clean_files"]
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
    all_pairs = []
    class_counts = {}

    for filename in source_files:
        filepath = os.path.join(data_dir, filename)
        if not os.path.exists(filepath):
            logging.warning(f"🔴 Файл не найден: {filepath}")
            continue

        file_count = 0
        with open(filepath, "r", encoding="utf-8") as f:
            for line_num, line in enumerate(f, 1):
                line = line.strip()
                if not line or line.startswith("//"):
                    continue
                try:
                    entry = json.loads(line)
                    text = clean_text(get_field(entry, fields["text"]))
                    label = get_field(entry, fields["label"], default_label)

                    if skip_empty and not text:
                        continue

                    response = get_response_for_class(label, responses)
                    pair = {"user": text, "bot": response}
                    all_pairs.append(pair)
                    class_counts[label] = class_counts.get(label, 0) + 1
                    file_count += 1

                except Exception as e:
                    logging.debug(f"⚠️ Пропущена строка в {filename} (line {line_num}): {e}")

        logging.info(f"📥 Добавлено {file_count} фраз из {filepath}")
        if file_count == 0:
            logging.warning(f"⚠️ Файл {filepath} прочитан, но ни одна строка не прошла валидацию!")


    logging.info(f"✅ Всего сформировано {len(all_pairs)} обучающих пар")

    # === Этап 3: Сохранение (если не dry-run) ===
    if args.dry_run:
        logging.info("🧪 Режим Dry Run: данные не сохранены.")
    else:
        # Сохранение training_pairs.jsonl
        train_path = paths["training_pairs"]
        os.makedirs(os.path.dirname(train_path), exist_ok=True)
        with open(train_path, "w", encoding="utf-8") as f:
            for pair in all_pairs:
                f.write(json.dumps(pair, ensure_ascii=False) + "\n")
        logging.info(f"🎯 Сохранено в: {train_path}")

        # Сохранение статистики
        stats_path = paths["knowledge_stats"]
        os.makedirs(os.path.dirname(stats_path), exist_ok=True)
        stats = {
            "total_training_pairs": len(all_pairs),
            "last_update": "2026-05-10T13:00:00",
            "class_distribution": class_counts,
            "source_files": source_files,
            "cleaned_files": cleaned_files
        }
        with open(stats_path, "w", encoding="utf-8") as f:
            json.dump(stats, f, ensure_ascii=False, indent=2)
        logging.info(f"📈 Статистика обновлена: {stats_path}")

    # === Итог ===
    logging.info("📊 Распределение по классам:")
    for cls, cnt in sorted(class_counts.items()):
        logging.info(f"   {cls}: {cnt}")

    logging.info("\n🎉 Готово! Все данные собраны.")
    logging.info("Запустите дообучение модели:")
    logging.info("python retrain.py")

if __name__ == "__main__":
    main()