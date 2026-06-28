#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
learn_knowledge_from_web.py - Автопоиск определений для всех слов из базы знаний.

Два режима поиска:
  1. GigaChat (по умолчанию) - быстрый, без Selenium
  2. Selenium + Yandex - если GigaChat недоступен

Цикл:
  1. Загружает все слова из data/knowledge/learned_words.json
  2. Для каждого слова ищет определение через API
  3. Сохраняет найденные определения обратно в learned_words.json
  4. Генерирует обучающие пары (training_pairs.jsonl)
  5. Объединяет пары с существующими данными

Запуск:
  python learn_knowledge_from_web.py              # Все слова (GigaChat)
  python learn_knowledge_from_web.py --max 50     # Только первые 50
  python learn_knowledge_from_web.py --selenium   # Через Selenium + Yandex
  python learn_knowledge_from_web.py --retrain    # Сразу после поиска запустить переобучение
"""

import os
import sys
import json
import re
import time
import argparse
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Optional

# Пути
BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
KNOWLEDGE_DIR = DATA_DIR / "knowledge"
LEARNED_WORDS_PATH = KNOWLEDGE_DIR / "learned_words.json"
TRAINING_PAIRS_PATH = KNOWLEDGE_DIR / "training_pairs.jsonl"
KNOWLEDGE_STATS_PATH = KNOWLEDGE_DIR / "knowledge_stats.json"
MAIN_TRAINING_PAIRS_PATH = DATA_DIR / "training_pairs.jsonl"

# Добавляем путь к модулям проекта для импорта
_SRC_PATH = BASE_DIR / "Wuglarst" / "src"
if _SRC_PATH.exists():
    sys.path.insert(0, str(_SRC_PATH))

# Импорт WebSearch (опционально, может отсутствовать)
try:
    from web_search import WebSearch
    _HAS_WEB_SEARCH = True
except ImportError:
    WebSearch = None  # type: ignore
    _HAS_WEB_SEARCH = False


# ==================== ПОИСК ЧЕРЕЗ GIGACHAT ====================

def search_word_gigachat(word: str) -> Optional[str]:
    """Ищет определение слова через GigaChat API."""
    token = os.getenv("GIGACHAT_TOKEN")
    if not token:
        return None
    
    try:
        import requests
        resp = requests.post(
            "https://gigachat.devices.sberbank.ru/api/v1/chat/completions",
            headers={
                "Authorization": "Bearer " + token,
                "Content-Type": "application/json",
                "X-Request-Id": str(hash(word)),
            },
            json={
                "model": "GigaChat",
                "messages": [
                    {
                        "role": "user",
                        "content": (
                            f"Дай краткое, точное определение слова '{word}'. "
                            f"Только 1-2 предложения, без лишних слов. Формат: Слово - это ..."
                        )
                    }
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
                text = data["choices"][0]["message"]["content"].strip()
                # Очистка: убираем самоцитирование слова в начале
                text = re.sub(r'^' + re.escape(word) + r'\s*-\s*', '', text, flags=re.IGNORECASE)
                return text.strip()
        else:
            print(f"  [GigaChat] HTTP {resp.status_code}: {resp.text[:100]}")
            return None
    except Exception as e:
        print(f"  [GigaChat] Ошибка: {str(e)[:80]}")
        return None


# ==================== ПОИСК ЧЕРЕЗ SELENIUM ====================

def search_word_selenium(word: str, ws_instance) -> Optional[str]:
    """Ищет определение слова через Selenium + Yandex."""
    try:
        definition = ws_instance.lookup(word, timeout=3.0)
        return definition
    except Exception as e:
        print(f"  [Selenium] Ошибка: {str(e)[:60]}")
        return None


# ==================== ОСНОВНАЯ ЛОГИКА ====================

def load_words() -> List[Dict]:
    """Загружает все слова из базы знаний."""
    if not LEARNED_WORDS_PATH.exists():
        print(f"[ERR] Файл не найден: {LEARNED_WORDS_PATH}")
        return []
    
    with open(LEARNED_WORDS_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def save_words(words: List[Dict]):
    """Сохраняет слова обратно в базу знаний."""
    KNOWLEDGE_DIR.mkdir(parents=True, exist_ok=True)
    with open(LEARNED_WORDS_PATH, "w", encoding="utf-8") as f:
        json.dump(words, f, ensure_ascii=False, indent=2)
    print(f"[SAVE] Сохранено {len(words)} слов")


def generate_training_pairs_from_words(words: List[Dict]) -> int:
    """
    Генерирует обучающие пары из слов с определениями.
    Возвращает количество созданных пар.
    """
    pairs = []
    now = datetime.now().isoformat()
    
    for word_data in words:
        word = word_data.get("word", "")
        definition = word_data.get("definition", "")
        
        if not word or not definition:
            continue
        
        # Различные варианты вопросов
        questions = [
            f"что такое {word}?",
            f"какое значение у слова {word}?",
            f"объясни слово {word}",
            f"что означает {word}?",
            f"дай определение {word}",
            f"что такое {word} простыми словами?",
            f"в чём смысл {word}?",
            f"расскажи о значении {word}",
            f"опиши понятие {word}",
            f"что значит {word}?",
        ]
        
        # Различные варианты ответов
        answers = [
            f"{word} - это {definition}",
            f"Термин '{word}' означает: {definition}",
            f"Слово '{word}' значит: {definition}",
            f"{definition}",
            f"Вот что такое {word}: {definition}",
        ]
        
        # Генерируем пары (ограничиваем количество на слово)
        max_pairs = 3
        for i in range(min(max_pairs, len(questions))):
            pair = {
                "user": questions[i],
                "bot": answers[i % len(answers)],
                "source": "learn_knowledge_from_web",
                "word": word,
                "difficulty": word_data.get("difficulty_level", "medium"),
                "generated_at": now,
            }
            pairs.append(pair)
    
    if not pairs:
        print("[WARN] Не сгенерировано ни одной пары - нет слов с определениями")
        return 0
    
    # Сохраняем в knowledge/training_pairs.jsonl
    KNOWLEDGE_DIR.mkdir(parents=True, exist_ok=True)
    with open(TRAINING_PAIRS_PATH, "a", encoding="utf-8") as f:
        for pair in pairs:
            f.write(json.dumps(pair, ensure_ascii=False) + "\n")
    
    print(f"[OK] Сгенерировано {len(pairs)} обучающих пар -> {TRAINING_PAIRS_PATH}")
    
    # Также добавляем в основной файл training_pairs.jsonl (если есть)
    if MAIN_TRAINING_PAIRS_PATH.exists():
        try:
            existing = []
            with open(MAIN_TRAINING_PAIRS_PATH, "r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if line:
                        try:
                            existing.append(json.loads(line))
                        except json.JSONDecodeError:
                            continue
            
            # Добавляем только новые пары (по тексту вопроса)
            existing_questions = {p.get("user", "").lower() for p in existing}
            new_pairs = [p for p in pairs if p["user"].lower() not in existing_questions]
            
            if new_pairs:
                with open(MAIN_TRAINING_PAIRS_PATH, "a", encoding="utf-8") as f:
                    for pair in new_pairs:
                        f.write(json.dumps(pair, ensure_ascii=False) + "\n")
                print(f"[OK] Добавлено {len(new_pairs)} новых пар в {MAIN_TRAINING_PAIRS_PATH}")
        except Exception as e:
            print(f"[WARN] Не удалось добавить в основной файл: {e}")
    
    return len(pairs)


def update_knowledge_stats(words: List[Dict]):
    """Обновляет статистику знаний."""
    stats = {
        "total_words": len(words),
        "last_update": datetime.now().isoformat(),
        "training_pairs_generated": 0,
        "difficulty_distribution": {"simple": 0, "medium": 0, "complex": 0},
        "with_definition": 0,
        "without_definition": 0,
    }
    
    for w in words:
        diff = w.get("difficulty_level", "simple")
        if diff in stats["difficulty_distribution"]:
            stats["difficulty_distribution"][diff] += 1
        
        if w.get("definition", ""):
            stats["with_definition"] += 1
        else:
            stats["without_definition"] += 1
    
    with open(KNOWLEDGE_STATS_PATH, "w", encoding="utf-8") as f:
        json.dump(stats, f, ensure_ascii=False, indent=2)
    
    print(f"[STATS] Статистика: {stats['total_words']} слов, "
          f"{stats['with_definition']} с определениями")


def print_report(words: List[Dict]):
    """Печатает финальный отчёт."""
    print("\n" + "=" * 60)
    print("[REPORT] ОТЧЁТ")
    print("=" * 60)
    
    total = len(words)
    with_def = sum(1 for w in words if w.get("definition", ""))
    without_def = total - with_def
    
    print(f"Всего слов в базе:       {total}")
    print(f"С определениями:         {with_def}")
    print(f"Без определений:         {without_def}")
    if total > 0:
        print(f"Процент покрытых:        {with_def/total*100:.1f}%")
    
    # Распределение по сложности
    diff_counts = {"simple": 0, "medium": 0, "complex": 0}
    for w in words:
        d = w.get("difficulty_level", "simple")
        if d in diff_counts:
            diff_counts[d] += 1
    
    print(f"\nРаспределение по сложности:")
    for d, c in diff_counts.items():
        print(f"  {d:10s}: {c}")
    
    # Топ-10 самых используемых слов
    sorted_words = sorted(words, key=lambda x: x.get("usage_count", 0), reverse=True)
    if sorted_words:
        print(f"\nТоп-10 самых используемых слов:")
        for i, w in enumerate(sorted_words[:10], 1):
            has_def = "OK" if w.get("definition", "") else "NO"
            name = w['word']
            print(f"  {i:2d}. {name:30s} "
                  f"(использ: {w.get('usage_count', 0):3d}) [{has_def}]")
    
    print("=" * 60)


def main():
    parser = argparse.ArgumentParser(
        description="Автопоиск определений для слов из базы знаний"
    )
    
    # Загрузка .env ДО парсинга аргументов
    env_path = Path(__file__).resolve().parent / ".env"
    if env_path.exists():
        try:
            from dotenv import load_dotenv
            load_dotenv(env_path)
        except ImportError:
            pass  # python-dotenv не установлен, игнорируем
    
    parser.add_argument("--max", type=int, default=0,
                        help="Максимум слов для обработки (0 = все)")
    parser.add_argument("--selenium", action="store_true",
                        help="Использовать Selenium + Yandex (по умолчанию: GigaChat)")
    parser.add_argument("--retrain", action="store_true",
                        help="Запустить переобучение после поиска")
    parser.add_argument("--timeout", type=float, default=3.0,
                        help="Таймаут поиска на слово (сек)")
    parser.add_argument("--delay", type=float, default=0.5,
                        help="Задержка между запросами (сек)")
    parser.add_argument("--batch", type=int, default=5,
                        help="Размер батча: после каждого N слов сохраняется промежуточный результат")
    
    args = parser.parse_args()
    
    print("=" * 60)
    print("[INFO] АВТОПОИСК ОПРЕДЕЛЕНИЙ ДЛЯ БАЗЫ ЗНАНИЙ")
    print("=" * 60)
    search_mode = "Selenium + Yandex" if args.selenium else "GigaChat API"
    print(f"Режим поиска: {search_mode}")
    
    # 1. Загружаем слова
    print("\n[1/5] Загрузка слов из базы знаний...")
    words = load_words()
    if not words:
        print("[ERR] База знаний пуста!")
        return
    
    print(f"[OK] Загружено {len(words)} слов")
    
    # 2. Инициализируем поиск
    print("\n[2/5] Инициализация поиска...")
    search_instance = None
    
    if args.selenium:
        # Режим Selenium
        if _HAS_WEB_SEARCH and WebSearch:
            ws = WebSearch()
            ws.init_driver()
            
            if not ws.driver:
                print("[WARN] Selenium не запущен, переключаемся на GigaChat")
            else:
                search_instance = ws
                print("[OK] Selenium инициализирован")
        else:
            print("[WARN] web_search.py не найден, переключаемся на GigaChat")
    else:
        # Режим GigaChat
        token = os.getenv("GIGACHAT_TOKEN")
        if token:
            print(f"[OK] GigaChat: токен найден (длина={len(token)})")
        else:
            print("[WARN] GIGACHAT_TOKEN не найден в .env")
            print("[INFO] Установите токен в .env или используйте --selenium")
            # Пробуем Selenium как fallback
            if _HAS_WEB_SEARCH and WebSearch:
                ws = WebSearch()
                ws.init_driver()
                if ws.driver:
                    search_instance = ws
                    print("[OK] Fallback: Selenium инициализирован")
                else:
                    print("[ERR] Оба режима недоступны! Установите GIGACHAT_TOKEN или Chrome.")
                    return
            else:
                print("[ERR] Оба режима недоступны! Установите GIGACHAT_TOKEN или Chrome.")
                return
    
    # 3. Подготавливаем список слов
    print("\n[3/5] Подготовка списка слов...")
    words_to_process = [w for w in words if w.get("word", "")]
    
    if args.max > 0:
        words_to_process = words_to_process[:args.max]
    
    print(f"[OK] Слов для обработки: {len(words_to_process)}")
    
    if not words_to_process:
        print("[INFO] Нечего обрабатывать")
        return
    
    # 4. Ищем определения
    print(f"\n[4/5] Поиск определений...")
    print(f"{'N':>4} | {'Слово':<30} | {'Статус':<8} | Определение")
    print("-" * 80)
    
    found_count = 0
    error_count = 0
    batch_num = 0
    
    for i, word_data in enumerate(words_to_process, 1):
        word = word_data["word"]
        status = "?"
        
        if args.selenium and search_instance:
            definition = search_word_selenium(word, search_instance)
        else:
            definition = search_word_gigachat(word)
        
        if definition and len(definition) > 10:
            word_data["definition"] = definition
            word_data["updated_at"] = datetime.now().isoformat()
            source_name = "gigachat" if not args.selenium else "web_search"
            word_data["source"] = source_name
            status = "OK"
            found_count += 1
        else:
            status = "FAIL"
            error_count += 1
        
        # Печатаем прогресс каждые N слов
        if i % 20 == 1 or i == len(words_to_process):
            print(f"[PROGRESS] {i}/{len(words_to_process)} | "
                  f"OK: {found_count} | FAIL: {error_count}")
        
        # Промежуточное сохранение каждые N слов
        if args.batch > 0 and i % args.batch == 0:
            save_words(words)
            batch_num += 1
            print(f"[SAVE] Промежуточное сохранение (батч #{batch_num})")
        
        # Задержка между запросами
        time.sleep(args.delay)
    
    # Финальное сохранение
    print(f"\n[SAVE] Сохранение обновлённых данных...")
    save_words(words)
    
    # 5. Генерируем обучающие пары
    print("\n[5/5] Генерация обучающих пар...")
    pairs_count = generate_training_pairs_from_words(words)
    
    # Обновляем статистику
    update_knowledge_stats(words)
    
    # Финальный отчёт
    print_report(words)
    
    # Итоговая статистика этого запуска
    print("\n[SUMMARY] Статистика запуска:")
    print(f"  Обработано слов:      {len(words_to_process)}")
    print(f"  Найдено определений:  {found_count}")
    print(f"  Не найдено:           {error_count}")
    print(f"  Создано пар:          {pairs_count}")
    
    if pairs_count > 0:
        print(f"\n[INFO] Для переобучения запустите:")
        print(f"  python retrain.py")
        print(f"\n  ИЛИ")
        print(f"  python train.py")
    
    if args.retrain:
        print(f"\n[RETRAIN] Запуск переобучения...")
        try:
            import subprocess
            result = subprocess.run(
                [sys.executable, "retrain.py"],
                capture_output=False,
                text=True,
            )
            if result.returncode == 0:
                print("[OK] Переобучение завершено!")
            else:
                print(f"[WARN] Переобучение с кодом {result.returncode}")
        except Exception as e:
            print(f"[ERR] Ошибка переобучения: {e}")
    
    print("\n[OK] Готово!")


if __name__ == "__main__":
    main()
