import os
import json

# Файлы с негативными эмоциональными фразами
negative_files = [
    "data/negative_emotional_phrases_part1.jsonl",
    "data/negative_emotional_phrases_part2.jsonl",
    "data/negative_narrative_phrases.jsonl"
]

# Целевой файл обучающих данных
training_file = "data/knowledge/training_pairs.jsonl"

# Создаем директорию, если она не существует
os.makedirs(os.path.dirname(training_file), exist_ok=True)

# Подсчет общего количества добавленных фраз
total_added = 0

class_counts = {}

# Добавляем негативные фразы
with open(training_file, 'a', encoding='utf-8') as outfile:
    for file_path in negative_files:
        if os.path.exists(file_path):
            file_count = 0
            with open(file_path, 'r', encoding='utf-8') as infile:
                for line in infile:
                    line = line.strip()
                    if line:
                        outfile.write(line + '\n')
                        total_added += 1
                        file_count += 1
                        
                        # Подсчет по классам
                        try:
                            data = json.loads(line)
                            sentiment = data.get('sentiment', 'unknown')
                            class_counts[sentiment] = class_counts.get(sentiment, 0) + 1
                        except:
                            class_counts['parse_error'] = class_counts.get('parse_error', 0) + 1
            
            print(f"Добавлено {file_count} негативных фраз из {file_path}")
        else:
            print(f"Файл не найден: {file_path}")

print(f"\nВсего добавлено {total_added} негативных эмоциональных фраз")
print("Распределение по типам:")
for sentiment, count in class_counts.items():
    print(f"  {sentiment}: {count}")

# Обновляем статистику
stats_file = "data/knowledge/knowledge_stats.json"
if os.path.exists(stats_file):
    with open(stats_file, 'r', encoding='utf-8') as f:
        stats = json.load(f)
    
    # Обновляем статистику
    stats["total_negative_phrases"] = stats.get("total_negative_phrases", 0) + total_added
    stats["last_negative_update"] = "2026-05-10T14:00:00"
    stats["negative_classes"] = class_counts
    
    with open(stats_file, 'w', encoding='utf-8') as f:
        json.dump(stats, f, ensure_ascii=False, indent=2)
    
    print(f"\nСтатистика негативных эмоций обновлена в {stats_file}")
else:
    print(f"Файл статистики не найден: {stats_file}")

print("\nГотово! Теперь запустите процесс переобучения:")
print("python retrain.py")
print("или")
print("python auto_learn_cycle.py")