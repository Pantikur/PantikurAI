# fix_and_merge.py — исправление и объединение диалогов

import json
import os

def fix_and_merge():
    """Исправляет проблемы с кодировкой и объединяет диалоги"""
    
    training_pairs_file = "data/knowledge/training_pairs.jsonl"
    user_conversations_file = "data/user_conversations.jsonl"
    
    # Читаем сгенерированные пары
    generated_pairs = []
    if os.path.exists(training_pairs_file):
        with open(training_pairs_file, 'r', encoding='utf-8') as f:
            for line in f:
                if line.strip():
                    try:
                        generated_pairs.append(json.loads(line))
                    except json.JSONDecodeError:
                        print(f"⚠️ Пропущена строка в training_pairs: {line[:50]}...")
    
    print(f"📝 Прочитано {len(generated_pairs)} сгенерированных пар")
    
    # Читаем существующие диалоги
    existing_conversations = []
    if os.path.exists(user_conversations_file) and os.path.getsize(user_conversations_file) > 0:
        with open(user_conversations_file, 'r', encoding='utf-8') as f:
            for line in f:
                if line.strip():
                    try:
                        existing_conversations.append(json.loads(line))
                    except json.JSONDecodeError:
                        print(f"⚠️ Пропущена строка в user_conversations: {line[:50]}...")
    
    print(f"📝 Прочитано {len(existing_conversations)} пользовательских диалогов")
    
    # Объединяем
    all_conversations = existing_conversations + generated_pairs
    
    # Сохраняем
    with open(user_conversations_file, 'w', encoding='utf-8') as f:
        for conv in all_conversations:
            f.write(json.dumps(conv, ensure_ascii=False) + '\n')
    
    print(f"\n✅ Объединено {len(existing_conversations)} пользовательских и {len(generated_pairs)} сгенерированных диалогов")
    print(f"📌 Общее количество диалогов для дообучения: {len(all_conversations)}")
    
    # Статистика по расам
    race_terms = set()
    for conv in generated_pairs:
        if 'word' in conv:
            word = conv['word']
            if any(race in word for race in ['эльф', 'гном', 'орк', 'демон', 'дракон', 'флюгели', 'кимономи']):
                race_terms.add(word)
    
    print(f"\n🎭 Добавлено терминов о расах: {len(race_terms)}")
    if race_terms:
        print("Примеры:", list(race_terms)[:10])


if __name__ == "__main__":
    fix_and_merge()
