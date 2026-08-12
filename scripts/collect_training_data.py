#!/usr/bin/env python3
"""
Сборщик обучающих данных для дообучения Qwen2.5-3B.

Собирает ВСЕ данные из проекта:
  • conversations.json — диалоги
  • training_pairs.jsonl — тренировочные пары
  • character-forging.md — характеры всех девочек
  • constitution.md — конституции всех модулей
  • system-init.md — системная инициализация
  • protocols/*.md — протоколы
  • laws/*.md — законы
  • vuglarst_state/*.md — правовые документы государства
  • characters/*.md — персонажи фэнтези-мира
  • lore/*.md — лор мира
  • README.md — документация

Результат: training_dataset.jsonl (единый датасет для дообучения)
"""

import os
import sys
import json
import re
from pathlib import Path
from typing import List, Dict

print("=" * 60)
print("[DATA] Сбор обучающих данных для дообучения")
print("=" * 60)

BASE_DIR = Path(__file__).parent.parent
OUTPUT_FILE = BASE_DIR / "data" / "training_dataset.jsonl"
OUTPUT_STATS = BASE_DIR / "data" / "training_stats.json"

# Счётчики
stats = {
    "conversations": 0,
    "training_pairs": 0,
    "characters": 0,
    "constitutions": 0,
    "protocols": 0,
    "laws": 0,
    "legal_docs": 0,
    "lore": 0,
    "readmes": 0,
    "other": 0,
    "total_lines": 0,
    "total_chars": 0,
}


def clean_text(text: str) -> str:
    """Чистит текст от лишних символов."""
    # Убираем повторяющиеся пробелы
    text = re.sub(r'\s+', ' ', text)
    # Убираем слишком длинные повторы символов
    text = re.sub(r'(.)\1{10,}', r'\1', text)
    return text.strip()


def extract_conversations(filepath: Path) -> List[Dict]:
    """Извлекает диалоги из conversations.json."""
    items = []
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            data = json.load(f)
        
        # conversations.json может быть списком или словарём
        if isinstance(data, list):
            for conv in data:
                if isinstance(conv, dict):
                    user = conv.get("user", conv.get("input", ""))
                    assistant = conv.get("assistant", conv.get("output", conv.get("response", "")))
                    if user and assistant:
                        items.append({
                            "prompt": f"User: {user}\nAssistant:",
                            "completion": assistant,
                            "source": "conversations",
                            "length": len(assistant),
                        })
                        stats["conversations"] += 1
                elif isinstance(conv, str):
                    items.append({
                        "prompt": "User:",
                        "completion": conv,
                        "source": "conversations",
                        "length": len(conv),
                    })
                    stats["conversations"] += 1
        elif isinstance(data, dict):
            # Словарь: ключи = user, значения = assistant
            for user_msg, assistant_msg in data.items():
                if user_msg and assistant_msg:
                    items.append({
                        "prompt": f"User: {user_msg}\nAssistant:",
                        "completion": assistant_msg,
                        "source": "conversations",
                        "length": len(assistant_msg),
                    })
                    stats["conversations"] += 1
    except Exception as e:
        print(f"  [WARN] Ошибка чтения {filepath}: {e}")
    
    return items


def extract_training_pairs(filepath: Path) -> List[Dict]:
    """Извлекает пары из JSONL."""
    items = []
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    data = json.loads(line)
                    # Поддержка разных форматов
                    if "prompt" in data and "completion" in data:
                        items.append(data)
                    elif "input" in data and "output" in data:
                        items.append({
                            "prompt": data["input"],
                            "completion": data["output"],
                            "source": "training_pairs",
                        })
                    elif "question" in data and "answer" in data:
                        items.append({
                            "prompt": f"Question: {data['question']}\nAnswer:",
                            "completion": data["answer"],
                            "source": "training_pairs",
                        })
                    elif "text" in data:
                        # Просто текст для продолжения
                        text = data["text"]
                        if len(text) > 20:
                            items.append({
                                "prompt": "Continue:",
                                "completion": text,
                                "source": "training_pairs",
                            })
                    stats["training_pairs"] += 1
                except json.JSONDecodeError:
                    continue
    except Exception as e:
        print(f"  [WARN] Ошибка чтения {filepath}: {e}")
    
    return items


def extract_md_documents(directory: Path, category: str, extensions: List[str] = None) -> List[Dict]:
    """Извлекает тексты из Markdown файлов."""
    items = []
    if not directory.exists():
        return items
    
    for md_file in directory.rglob("*.md"):
        if not md_file.name.endswith(".md"):
            continue
        
        try:
            with open(md_file, "r", encoding="utf-8") as f:
                content = f.read()
            
            content = clean_text(content)
            
            if len(content) < 50:
                continue
            
            # Определяем тип документа
            rel_path = md_file.relative_to(BASE_DIR)
            
            # Конституции
            if "constitution" in md_file.name.lower():
                stats["constitutions"] += 1
                items.append({
                    "prompt": f"[CONSTITUTION] {rel_path}:\n",
                    "completion": content,
                    "source": category,
                    "length": len(content),
                })
            
            # Character-forging (характеры)
            elif "character-forging" in md_file.name.lower():
                stats["characters"] += 1
                items.append({
                    "prompt": f"[CHARACTER] {rel_path}:\n",
                    "completion": content,
                    "source": category,
                    "length": len(content),
                })
            
            # System-init
            elif "system-init" in md_file.name.lower():
                stats["other"] += 1
                items.append({
                    "prompt": f"[SYSTEM-INIT] {rel_path}:\n",
                    "completion": content,
                    "source": category,
                    "length": len(content),
                })
            
            # Протоколы
            elif "protocol" in md_file.name.lower():
                stats["protocols"] += 1
                items.append({
                    "prompt": f"[PROTOCOL] {rel_path}:\n",
                    "completion": content,
                    "source": category,
                    "length": len(content),
                })
            
            # Законы
            elif "law" in md_file.name.lower():
                stats["laws"] += 1
                items.append({
                    "prompt": f"[LAW] {rel_path}:\n",
                    "completion": content,
                    "source": category,
                    "length": len(content),
                })
            
            # Фэнтезийные персонажи
            elif "characters" in str(md_file.parent).lower():
                stats["characters"] += 1
                items.append({
                    "prompt": f"[FANTASY-CHARACTER] {rel_path}:\n",
                    "completion": content,
                    "source": category,
                    "length": len(content),
                })
            
            # Лор
            elif "lore" in str(md_file.parent).lower():
                stats["lore"] += 1
                items.append({
                    "prompt": f"[LORE] {rel_path}:\n",
                    "completion": content,
                    "source": category,
                    "length": len(content),
                })
            
            # Правовые документы государства
            elif "vuglarst_state" in str(rel_path):
                stats["legal_docs"] += 1
                items.append({
                    "prompt": f"[LEGAL-DOC] {rel_path}:\n",
                    "completion": content,
                    "source": category,
                    "length": len(content),
                })
            
            # README
            elif "readme" in md_file.name.lower():
                stats["readmes"] += 1
                items.append({
                    "prompt": f"[README] {rel_path}:\n",
                    "completion": content,
                    "source": category,
                    "length": len(content),
                })
            
            else:
                stats["other"] += 1
                items.append({
                    "prompt": f"[DOCUMENT] {rel_path}:\n",
                    "completion": content,
                    "source": category,
                    "length": len(content),
                })
        
        except Exception as e:
            print(f"  [WARN] Ошибка чтения {md_file}: {e}")
    
    return items


def main():
    """Собирает все данные."""
    print("\n[1/4] Сбор данных из conversations.json...")
    conv_file = BASE_DIR / "data" / "conversations.json"
    if conv_file.exists():
        conv_items = extract_conversations(conv_file)
        print(f"  [OK] Собрано {len(conv_items)} диалогов")
    else:
        print(f"  [SKIP] {conv_file} не найден")
        conv_items = []
    
    print("\n[2/4] Сбор данных из training_pairs.jsonl...")
    pairs_file = BASE_DIR / "data" / "training_pairs.jsonl"
    if pairs_file.exists():
        pairs_items = extract_training_pairs(pairs_file)
        print(f"  [OK] Собрано {len(pairs_items)} пар")
    else:
        print(f"  [SKIP] {pairs_file} не найден")
        pairs_items = []
    
    print("\n[3/4] Сбор данных из Markdown документов...")
    
    all_md_items = []
    
    # Все директории с .md файлами
    md_dirs = [
        (BASE_DIR / "futaba", "futaba"),
        (BASE_DIR / "futaba" / "vuglarst_state", "vuglarst_state"),
        (BASE_DIR / "futaba" / "laws", "futaba_laws"),
        (BASE_DIR / "futaba" / "protocols", "futaba_protocols"),
        (BASE_DIR / "nobuka", "nobuka"),
        (BASE_DIR / "shiori", "shiori"),
        (BASE_DIR / "hanako", "hanako"),
        (BASE_DIR / "fuyuki", "fuyuki"),
        (BASE_DIR / "lucy", "lucy"),
        (BASE_DIR / "akva", "akva"),
        (BASE_DIR / "latislane", "latislane"),
        (BASE_DIR / "celesta", "celesta"),
        (BASE_DIR / "naoto", "naoto"),
        (BASE_DIR / "sidney", "sidney"),
        (BASE_DIR / "yu", "yu"),
        (BASE_DIR / "fludilka_chat_pantikur" / "akademia_barston", "akademia_barston"),
        (BASE_DIR / "fludilka_chat_pantikur" / "akademia_barston" / "characters", "akademia_characters"),
        (BASE_DIR / "fludilka_chat_pantikur" / "akademia_barston" / "lore", "akademia_lore"),
        (BASE_DIR / "Wuglarst", "wuglarst"),
        (BASE_DIR / "scientists_network", "scientists_network"),
    ]
    
    for dir_path, category in md_dirs:
        if dir_path.exists():
            items = extract_md_documents(dir_path, category)
            all_md_items.extend(items)
            print(f"  [OK] {dir_path.name}: {len(items)} документов")
    
    print(f"\n  [OK] Всего Markdown документов: {len(all_md_items)}")
    
    print("\n[4/4] Объединение и сохранение...")
    
    # Объединяем все данные
    all_items = conv_items + pairs_items + all_md_items
    
    # Фильтруем слишком короткие/длинные
    filtered = []
    for item in all_items:
        completion = item.get("completion", "")
        if len(completion) < 10:
            continue
        if len(completion) > 2000:
            completion = completion[:2000]
            item["completion"] = completion
        
        filtered.append(item)
    
    # Сортируем по длине (короткие первыми для лучшего обучения)
    filtered.sort(key=lambda x: len(x.get("completion", "")))
    
    # Сохраняем в JSONL
    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        for item in filtered:
            f.write(json.dumps(item, ensure_ascii=False) + "\n")
    
    # Считаем статистику
    total_chars = sum(len(item.get("completion", "")) for item in filtered)
    stats["total_lines"] = len(filtered)
    stats["total_chars"] = total_chars
    stats["total_mb"] = round(total_chars / (1024 * 1024), 2)
    
    # Сохраняем статистику
    with open(OUTPUT_STATS, "w", encoding="utf-8") as f:
        json.dump(stats, f, ensure_ascii=False, indent=2)
    
    print(f"\n{'='*60}")
    print("[SUCCESS] Данные собраны!")
    print(f"{'='*60}")
    print(f"\nРезультаты:")
    print(f"  Диалоги:        {stats['conversations']}")
    print(f"  Тренировочные пары: {stats['training_pairs']}")
    print(f"  Характеры:      {stats['characters']}")
    print(f"  Конституции:    {stats['constitutions']}")
    print(f"  Протоколы:      {stats['protocols']}")
    print(f"  Законы:         {stats['laws']}")
    print(f"  Прав. документы: {stats['legal_docs']}")
    print(f"  Лор:            {stats['lore']}")
    print(f"  README:         {stats['readmes']}")
    print(f"  Прочее:         {stats['other']}")
    print(f"\nВсего примеров:   {stats['total_lines']}")
    print(f"Общий размер:     {stats['total_mb']} МБ ({total_chars:,} символов)")
    print(f"\nФайл: {OUTPUT_FILE}")
    print(f"Статистика: {OUTPUT_STATS}")
    print(f"{'='*60}")


if __name__ == "__main__":
    main()
