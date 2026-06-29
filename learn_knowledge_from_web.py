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
  3. Извлекает ВСЕ слова из определений (включая предлоги, союзы, местоимения, служебные)
  4. Повторяет для всех найденных слов (с ограничением глубины)
  5. Сохраняет найденные определения обратно в learned_words.json
  6. Генерирует обучающие пары (training_pairs.jsonl)
  7. Объединяет пары с существующими данными

Запуск:
  python learn_knowledge_from_web.py              # Все слова (GigaChat)
  python learn_knowledge_from_web.py --max 50     # Только первые 50
  python learn_knowledge_from_web.py --selenium   # Через Selenium + Yandex
  python learn_knowledge_from_web.py --retrain    # Сразу после поиска запустить переобучение
  python learn_knowledge_from_web.py --extract-depth 2  # Извлекать слова 2 уровня глубины
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


# ==================== ИЗВЛЕЧЕНИЕ СЛОВ ИЗ ТЕКСТА ====================

# Слова, которые НЕ стоит добавлять (слишком общие/бессмысленные даже для изучения)
ONLY_EXCLUDE = {
    '...', '..', '—', '–',
}


def extract_words_from_text(text: str, min_length: int = 2, max_per_text: int = 10) -> List[str]:
    """
    Извлекает ВСЕ слова из текста определения, включая:
    - Существительные, глаголы, прилагательные
    - Предлоги, союзы, местоимения
    - Служебные слова
    
    Это нужно, чтобы бот понимал НЕ ТОЛЬКО значения слов,
    но и грамматику, синтаксис, структуру предложений.
    
    Правила:
    - Минимальная длина слова: min_length (по умолчанию 2)
    - Исключаем только символы-разделители из ONLY_EXCLUDE
    - Возвращаем не более max_per_text слов
    
    Пример:
        text = "Эгоизм — это стремление к личному благополучию"
        → ["Эгоизм", "это", "стремление", "к", "личному", "благополучию"]
    """
    # Убираем кавычки, тире и другие символы-разделители
    cleaned = re.sub(r'[—–"\']', ' ', text)
    
    # Извлекаем все слова длиной >= min_length
    words = re.findall(r'\b([а-яА-ЯёЁ]{2,})\b', cleaned)
    
    if not words:
        return []
    
    # Нормализуем и фильтруем
    seen = set()
    result = []
    
    for w in words:
        w_lower = w.lower()
        
        # Пропускаем дубликаты
        if w_lower in seen:
            continue
        
        # Пропускаем только явные символы-разделители
        if w_lower in ONLY_EXCLUDE:
            continue
        
        seen.add(w_lower)
        result.append(w)
        
        if len(result) >= max_per_text:
            break
    
    return result


# ==================== ПОИСК ЧЕРЕЗ GIGACHAT ====================

def search_word_gigachat(word: str) -> Optional[str]:
    """Ищет комплексную информацию о слове через GigaChat API:
    определение, примеры использования, контекст, обстоятельства, уместность."""
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
                            f"Дай комплексную информацию о слове '{word}'. "
                            f"Ответь кратко, структурированно, в одном абзаце:\n"
                            f"1) Определение: что это такое\n"
                            f"2) Примеры использования: как и в каких фразах применяют\n"
                            f"3) Контекст и обстоятельства: когда уместно говорить/писать\n"
                            f"4) Уместность и стиль: разговорное, официальное, нейтральное и т.д.\n"
                            f"Используй разделители: 'Определение:', 'Примеры:', 'Контекст:', 'Уместность:'"
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
    
    Теперь включает:
    - Определения
    - Примеры использования
    - Контекст и обстоятельства
    - Уместность и стиль
    """
    pairs = []
    now = datetime.now().isoformat()
    
    for word_data in words:
        word = word_data.get("word", "")
        definition = word_data.get("definition", "")
        
        if not word or not definition:
            continue
        
        # Проверяем, является ли определение комплексным (с разделителями секций)
        has_context = "Контекст" in definition or "обстоятел" in definition.lower()
        has_usage = "Пример" in definition or "например" in definition.lower()
        has_register = "Уместн" in definition or "стиль" in definition.lower() or "регистр" in definition.lower()
        
        # --- Определения ---
        def_questions = [
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
        
        def_answers = [
            f"{word} — это {definition.lower()[0].upper() + definition.lower()[1:] if definition else ''}",
            f"Термин '{word}' означает: {definition}",
            f"Слово '{word}' значит: {definition}",
            f"{definition}",
            f"Вот что такое {word}: {definition}",
        ]
        
        for i in range(min(3, len(def_questions))):
            pair = {
                "user": def_questions[i],
                "bot": def_answers[i % len(def_answers)],
                "source": "learn_knowledge_from_web",
                "word": word,
                "type": "definition",
                "difficulty": word_data.get("difficulty_level", "medium"),
                "generated_at": now,
            }
            pairs.append(pair)
    
        # --- Примеры использования ---
        if has_usage:
            usage_questions = [
                f"как использовать слово {word}?",
                f"приведи примеры слова {word}",
                f"в каких фразах используют {word}?",
                f"как правильно сказать с {word}?",
                f"применение слова {word}",
            ]
            usage_answers = [
                f"Примеры использования слова '{word}': {definition}",
                f"Вот как применяют '{word}': {definition}",
            ]
            for i in range(min(2, len(usage_questions))):
                pair = {
                    "user": usage_questions[i],
                    "bot": usage_answers[i % len(usage_answers)],
                    "source": "learn_knowledge_from_web",
                    "word": word,
                    "type": "usage",
                    "difficulty": word_data.get("difficulty_level", "medium"),
                    "generated_at": now,
                }
                pairs.append(pair)
        
        # --- Контекст и обстоятельства ---
        if has_context:
            context_questions = [
                f"в каком контексте используют {word}?",
                f"когда уместно говорить {word}?",
                f"при каких обстоятельствах используют {word}?",
                f"когда можно сказать {word}?",
                f"в каких ситуациях уместен {word}?",
            ]
            context_answers = [
                f"Слово '{word}' уместно в контексте: {definition}",
                f"Контекст употребления '{word}': {definition}",
            ]
            for i in range(min(2, len(context_questions))):
                pair = {
                    "user": context_questions[i],
                    "bot": context_answers[i % len(context_answers)],
                    "source": "learn_knowledge_from_web",
                    "word": word,
                    "type": "context",
                    "difficulty": word_data.get("difficulty_level", "medium"),
                    "generated_at": now,
                }
                pairs.append(pair)
        
        # --- Уместность и стиль ---
        if has_register:
            register_questions = [
                f"какой стиль у слова {word}?",
                f"это слово формальное или разговорное?",
                f"какой регистр у слова {word}?",
                f"уместно ли использовать {word} в официальной речи?",
                f"подходит ли {word} для делового общения?",
            ]
            register_answers = [
                f"Стиль и уместность слова '{word}': {definition}",
                f"Регистр '{word}': {definition}",
            ]
            for i in range(min(2, len(register_questions))):
                pair = {
                    "user": register_questions[i],
                    "bot": register_answers[i % len(register_answers)],
                    "source": "learn_knowledge_from_web",
                    "word": word,
                    "type": "register",
                    "difficulty": word_data.get("difficulty_level", "medium"),
                    "generated_at": now,
                }
                pairs.append(pair)
        
        # --- Комплексный ответ (если определение комплексное) ---
        if has_context or has_usage or has_register:
            complex_pair = {
                "user": f"расскажи всё о слове {word} — значение, примеры, контекст, уместность",
                "bot": definition,
                "source": "learn_knowledge_from_web",
                "word": word,
                "type": "comprehensive",
                "difficulty": word_data.get("difficulty_level", "medium"),
                "generated_at": now,
            }
            pairs.append(complex_pair)
    
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
        "pair_types": {"definition": 0, "usage": 0, "context": 0, "register": 0, "comprehensive": 0},
    }
    
    for w in words:
        diff = w.get("difficulty_level", "simple")
        if diff in stats["difficulty_distribution"]:
            stats["difficulty_distribution"][diff] += 1
        
        if w.get("definition", ""):
            stats["with_definition"] += 1
            # Подсчёт типов пар по содержимому определения
            def_text = w.get("definition", "").lower()
            if "пример" in def_text or "например" in def_text:
                stats["pair_types"]["usage"] += 1
            if "контекст" in def_text or "обстоятел" in def_text:
                stats["pair_types"]["context"] += 1
            if "уместн" in def_text or "стиль" in def_text or "регистр" in def_text:
                stats["pair_types"]["register"] += 1
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
    
    # Распределение по типам пар
    if stats.get("pair_types"):
        print(f"\nРаспределение по типам знаний:")
        type_labels = {
            "definition": "определения",
            "usage": "примеры использования",
            "context": "контекст/обстоятельства",
            "register": "уместность/стиль",
            "comprehensive": "комплексные",
        }
        for t, c in stats["pair_types"].items():
            label = type_labels.get(t, t)
            if c > 0:
                print(f"  {label:30s}: {c}")
    
    # Глубина знаний
    depth_counts = {"base": 0, "depth1": 0, "depth2": 0, "depth3+": 0}
    for w in words:
        d = w.get("depth", 0)
        if d == 0 or d is None:
            depth_counts["base"] += 1
        elif d == 1:
            depth_counts["depth1"] += 1
        elif d == 2:
            depth_counts["depth2"] += 1
        else:
            depth_counts["depth3+"] += 1
    
    if any(v > 0 for k, v in depth_counts.items() if k != "base"):
        print(f"\nРаспределение по глубине знаний:")
        print(f"  {'Базовые (исходные)':30s}: {depth_counts['base']}")
        print(f"  {'Глубина 1 (из определений)':30s}: {depth_counts['depth1']}")
        print(f"  {'Глубина 2 (из найденных слов)':30s}: {depth_counts['depth2']}")
        print(f"  {'Глубина 3+':30s}: {depth_counts['depth3+']}")
    
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
    parser.add_argument("--extract-depth", type=int, default=1,
                        help="Глубина извлечения слов из определений (1 = только из первых определений, 2 = и из найденных слов тоже)")
    parser.add_argument("--max-new-words", type=int, default=10,
                        help="Максимум новых слов для извлечения из одного определения")
    parser.add_argument("--min-word-length", type=int, default=2,
                        help="Минимальная длина слова для извлечения (2 = включая короткие предлоги/союзы)")
    
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
    
    # Создаём словарь для быстрого доступа по слову (по lowercase)
    words_dict = {}
    for w in words_to_process:
        words_dict[w["word"].lower()] = w
    
    if args.max > 0:
        words_to_process = words_to_process[:args.max]
    
    print(f"[OK] Слов для обработки: {len(words_to_process)}")
    
    if not words_to_process:
        print("[INFO] Нечего обрабатывать")
        return
    
    # 4. Ищем определения (с извлечением новых слов)
    print(f"\n[4/5] Поиск определений (с извлечением новых слов)...")
    print(f"{'Глуб':>4} | {'Слово':<30} | {'Статус':<8} | Определение")
    print("-" * 80)
    
    found_count = 0
    error_count = 0
    batch_num = 0
    extracted_new_words = set()  # слова, извлечённые из определений
    newly_added_words = []  # слова, добавленные в обработку
    
    # Очередь на обработку (используем deque для эффективности)
    from collections import deque
    processing_queue = deque(words_to_process)
    
    # Отслеживаем, какие слова уже обработаны
    processed_words = set()
    
    while processing_queue:
        word_data = processing_queue.popleft()
        word = word_data["word"]
        
        # Пропускаем уже обработанные
        if word.lower() in processed_words:
            continue
        processed_words.add(word.lower())
        
        # Определяем глубину этого слова
        word_depth = word_data.get("depth", 0) or 0
        
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
            
            # === ИЗВЛЕЧЕНИЕ НОВЫХ СЛОВ ИЗ ОПРЕДЕЛЕНИЯ ===
            if word_depth < args.extract_depth:
                new_words = extract_words_from_text(
                    definition,
                    min_length=args.min_word_length,
                    max_per_text=args.max_new_words
                )
                
                added = 0
                for nw in new_words:
                    nw_lower = nw.lower()
                    # Пропускаем если:
                    # - уже в processed_words
                    # - уже в processing_queue
                    # - уже в extracted_new_words
                    if (nw_lower in processed_words or 
                        nw_lower in extracted_new_words or
                        any(w["word"].lower() == nw_lower for w in processing_queue)):
                        continue
                    
                    # Добавляем новое слово в базу
                    new_word_data = {
                        "word": nw,
                        "depth": word_depth + 1,
                        "extracted_from": word,
                        "definition": "",
                        "difficulty_level": "medium",
                        "usage_count": 0,
                    }
                    
                    # Добавляем в основной список слов
                    words.append(new_word_data)
                    # Добавляем в очередь на обработку
                    processing_queue.append(new_word_data)
                    extracted_new_words.add(nw_lower)
                    newly_added_words.append(nw)
                    added += 1
                
                if added > 0:
                    print(f"  [EXTRACT] Из '{word}' (глубина {word_depth}) извлечено {added} новых слов: {', '.join(new_words[:5])}...")
        else:
            status = "FAIL"
            error_count += 1
        
        # Печатаем прогресс
        queue_size = len(processing_queue)
        print(f"[{word_data.get('depth', 0)}] {word_data['word']:<30s} {status:<8s} | {definition[:60] if definition else 'N/A'}...")
        
        # Промежуточное сохранение каждые N слов
        if args.batch > 0 and (found_count + error_count) % args.batch == 0:
            save_words(words)
            batch_num += 1
            print(f"[SAVE] Промежуточное сохранение (батч #{batch_num}, очередь: {queue_size})")
        
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
    print(f"  Обработано слов:      {len(processed_words)}")
    print(f"  Найдено определений:  {found_count}")
    print(f"  Не найдено:           {error_count}")
    print(f"  Создано пар:          {pairs_count}")
    
    if newly_added_words:
        print(f"\n[NEW] Извлечено {len(newly_added_words)} новых слов из определений:")
        for nw in newly_added_words[:20]:
            print(f"    - {nw}")
        if len(newly_added_words) > 20:
            print(f"    ... и ещё {len(newly_added_words) - 20}")
    
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
