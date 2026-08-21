import os
import json

# Пути к файлам с будоражащими фразами
files_to_add = [
    "data/disturbing_phrases.jsonl",
    "data/disturbing_phrases_narrative.jsonl"
]

# Целевой файл обучающих данных
training_file = "data/knowledge/training_pairs.jsonl"

# Создаем директорию, если она не существует
os.makedirs(os.path.dirname(training_file), exist_ok=True)

# Добавляем фразы в обучающие данные
added_count = 0
with open(training_file, 'a', encoding='utf-8') as outfile:
    for filename in files_to_add:
        if os.path.exists(filename):
            with open(filename, 'r', encoding='utf-8') as infile:
                for line in infile:
                    line = line.strip()
                    if line:
                        outfile.write(line + '\n')
                        added_count += 1
        else:
            print(f"Файл не найден: {filename}")

print(f"Успешно добавлено {added_count} будоражащих фраз в обучающие данные")

# Обновляем статистику в knowledge_stats.json
stats_file = "data/knowledge/knowledge_stats.json"
if os.path.exists(stats_file):
    with open(stats_file, 'r', encoding='utf-8') as f:
        stats = json.load(f)
    
    # Обновляем счетчики
    stats["total_disturbing_phrases"] = stats.get("total_disturbing_phrases", 0) + added_count
    stats["last_update"] = "2026-05-10T12:00:00"
    
    with open(stats_file, 'w', encoding='utf-8') as f:
        json.dump(stats, f, ensure_ascii=False, indent=2)
    
    print(f"Обновлена статистика знаний")
else:
    print(f"Файл статистики не найден: {stats_file}")