#!/usr/bin/env python3
# learn_from_web.py — поиск определений слов через HTTP-запросы к онлайн-словарям
# Без Selenium — быстро и надёжно

import os
import sys
import json
import re
import time
import argparse
from pathlib import Path
from typing import List, Dict, Set

# Загрузка .env
env_path = Path(__file__).resolve().parent.parent / ".env"
if env_path.exists():
    from dotenv import load_dotenv
    load_dotenv(env_path)

# Пути
BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
TOKENIZER_PATH = DATA_DIR / "tokenizer.json"
TRAINING_PAIRS_PATH = DATA_DIR / "training_pairs.jsonl"
KNOWLEDGE_CACHE_PATH = DATA_DIR / "knowledge_cache.json"


def load_tokenizer_vocab() -> Set[str]:
    if not TOKENIZER_PATH.exists():
        print("[ERR] Токенизатор не найден: {}".format(TOKENIZER_PATH))
        return set()
    
    with open(TOKENIZER_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)
    return set(data.get("vocab", {}).keys())


def load_knowledge_cache() -> Dict[str, str]:
    if KNOWLEDGE_CACHE_PATH.exists():
        with open(KNOWLEDGE_CACHE_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}


def save_knowledge_cache(cache: Dict[str, str]):
    with open(KNOWLEDGE_CACHE_PATH, "w", encoding="utf-8") as f:
        json.dump(cache, f, ensure_ascii=False, indent=2)
    print("[SAVE] Сохранено {} знаний в {}".format(len(cache), KNOWLEDGE_CACHE_PATH))


def load_training_pairs() -> List[Dict]:
    if not TRAINING_PAIRS_PATH.exists():
        return []
    
    pairs = []
    with open(TRAINING_PAIRS_PATH, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                try:
                    pairs.append(json.loads(line))
                except json.JSONDecodeError:
                    continue
    return pairs


def save_training_pairs(pairs: List[Dict]):
    with open(TRAINING_PAIRS_PATH, "w", encoding="utf-8") as f:
        for pair in pairs:
            f.write(json.dumps(pair, ensure_ascii=False) + "\n")
    print("[SAVE] Сохранено {} пар в {}".format(len(pairs), TRAINING_PAIRS_PATH))


def find_new_words(text: str, vocab: Set[str]) -> List[str]:
    words = re.findall(r'\b[а-яёa-z]{3,}\b', text.lower())
    
    new_words = []
    seen = set()
    for word in words:
        if word not in vocab and word not in seen:
            new_words.append(word)
            seen.add(word)
    
    return new_words


def search_word_gigachat(word: str) -> str:
    """Ищет определение слова через GigaChat"""
    token = os.getenv("GIGACHAT_TOKEN")
    if not token:
        return ""
    
    try:
        import requests
        resp = requests.post(
            "https://gigachat.devices.sberbank.ru/api/v1/chat/completions",
            headers={
                "Authorization": "Bearer {}".format(token),
                "Content-Type": "application/json"
            },
            json={
                "model": "GigaChat",
                "messages": [
                    {"role": "user", "content": "Дай краткое определение слова '{}' (1-2 предложения, только суть)".format(word)}
                ],
                "temperature": 0.3,
                "stream": False
            },
            verify=False,
            timeout=15
        )
        if resp.status_code == 200:
            data = resp.json()
            if data.get("choices"):
                return data["choices"][0]["message"]["content"].strip()
    except Exception as e:
        print("[ERR] GigaChat ошибка: {}".format(str(e)[:80]))
    
    return ""


def extract_training_pairs(definitions: Dict[str, str]) -> List[Dict]:
    pairs = []
    
    for word, definition in definitions.items():
        pairs.append({
            "input": "Что такое {}?".format(word),
            "output": definition
        })
        pairs.append({
            "input": "Объясни слово {}".format(word),
            "output": definition
        })
        pairs.append({
            "input": "{} определение".format(word),
            "output": definition
        })
    
    return pairs


def main():
    parser = argparse.ArgumentParser(description="Обучение бота на определениях слов из интернета")
    parser.add_argument(
        "--texts", "-t",
        type=str,
        nargs="+",
        default=None,
        help="Тексты для анализа"
    )
    parser.add_argument(
        "--conversations", "-c",
        action="store_true",
        help="Анализировать conversations.json"
    )
    parser.add_argument(
        "--max-words", "-m",
        type=int,
        default=20,
        help="Максимум слов для обработки (по умолчанию: 20)"
    )
    parser.add_argument(
        "--timeout", "-T",
        type=float,
        default=5.0,
        help="Таймаут поиска (по умолчанию: 5.0 сек)"
    )
    parser.add_argument(
        "--no-cache",
        action="store_true",
        help="Не использовать кэш"
    )
    
    args = parser.parse_args()
    
    print("=" * 60)
    print("[AI] ОБУЧЕНИЕ НА ОПРЕДЕЛЕНИЯХ СЛОВ")
    print("=" * 60)
    
    print("\n[INFO] Загрузка словаря токенизатора...")
    vocab = load_tokenizer_vocab()
    print("[OK] Словарь: {} слов".format(len(vocab)))
    
    print("\n[INFO] Загрузка кэша знаний...")
    if args.no_cache:
        knowledge_cache = {}
    else:
        knowledge_cache = load_knowledge_cache()
    print("[OK] Известно: {} слов".format(len(knowledge_cache)))
    
    print("\n[INFO] Сбор текстов для анализа...")
    texts = []
    
    if args.conversations:
        conv_path = DATA_DIR / "conversations.json"
        if conv_path.exists():
            with open(conv_path, "r", encoding="utf-8") as f:
                dialogs = json.load(f)
            for dialog in dialogs:
                for turn in dialog:
                    if "user" in turn:
                        texts.append(turn["user"])
                    if "assistant" in turn:
                        texts.append(turn["assistant"])
            print("[OK] Conversations: {} реплик".format(len(texts)))
    
    if args.texts:
        for text in args.texts:
            texts.append(text)
        print("[OK] Добавлено {} текстов".format(len(args.texts)))
    
    if not texts:
        print("[WARN] Нет текстов для анализа")
        print("[INFO] Используйте: --conversations или --texts 'текст 1' 'текст 2'")
        return
    
    print("\n[INFO] Поиск новых слов...")
    all_new_words = []
    for text in texts:
        new_words = find_new_words(text, vocab)
        all_new_words.extend(new_words)
    
    new_words = []
    for word in all_new_words:
        if word not in knowledge_cache and word not in [w for w in new_words]:
            new_words.append(word)
    
    print("[OK] Найдено {} новых слов".format(len(new_words)))
    
    if not new_words:
        print("[INFO] Новых слов не найдено. Бот уже знает всё!")
        return
    
    if len(new_words) > args.max_words:
        print("[WARN] Обрезаем до {} слов".format(args.max_words))
        new_words = new_words[:args.max_words]
    
    print("\n[INFO] Поиск определений для {} слов...".format(len(new_words)))
    
    definitions = {}
    success_count = 0
    
    for i, word in enumerate(new_words):
        print("\n[{}/{}] {}...".format(i+1, len(new_words), word), end=" ", flush=True)
        
        try:
            definition = search_word_gigachat(word)
            
            if definition:
                print("[OK] {}".format(definition[:50]))
                definitions[word] = definition
                success_count += 1
                knowledge_cache[word] = definition
                time.sleep(0.5)
            else:
                print("[WARN] не найдено")
        except Exception as e:
            print("[ERR] {}".format(str(e)[:80]))
    
    if definitions:
        print("\n[SAVE] Сохранение знаний...")
        save_knowledge_cache(knowledge_cache)
        
        print("\n[AI] Создание обучающих пар...")
        training_pairs = extract_training_pairs(definitions)
        print("[OK] Создано {} пар".format(len(training_pairs)))
        
        print("\n[SAVE] Добавление в training data...")
        existing_pairs = load_training_pairs()
        existing_pairs.extend(training_pairs)
        save_training_pairs(existing_pairs)
        
        print("\n" + "=" * 60)
        print("[STATS] РЕЗУЛЬТАТЫ")
        print("=" * 60)
        print("Слов проанализировано: {}".format(len(new_words)))
        print("Определений найдено: {}".format(success_count))
        print("Обучающих пар создано: {}".format(len(training_pairs)))
        print("Всего пар в dataset: {}".format(len(existing_pairs)))
        print("=" * 60)
        
        print("\n[INFO] Для обучения модели запустите:")
        print("  python retrain.py")
        print("=" * 60)
    else:
        print("[WARN] Не найдено ни одного определения")


if __name__ == "__main__":
    main()
