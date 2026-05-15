import os

# Пути к файлам
files_to_merge = [
    "data/sentiment_examples.jsonl",
    "data/sentiment_examples_extended.jsonl",
    "data/sentiment_examples_narrative.jsonl"
]

# Целевой файл
output_file = "data/knowledge/training_pairs.jsonl"

# Создаем директорию, если она не существует
os.makedirs(os.path.dirname(output_file), exist_ok=True)

# Объединяем файлы
with open(output_file, 'a', encoding='utf-8') as outfile:
    for filename in files_to_merge:
        with open(filename, 'r', encoding='utf-8') as infile:
            outfile.write('\n')
            for line in infile:
                outfile.write(line)
            
print(f"Успешно объединено в {output_file}")