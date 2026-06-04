import os
import json
import joblib
import numpy as np
from collections import Counter

# Определение путей
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
data_dir = os.path.join(BASE_DIR, '..', 'data')
conversations_file = os.path.join(data_dir, 'conversations.json')
output_file = os.path.join(data_dir, 'chat_data.pkl')

# Создание директории data, если её нет
os.makedirs(data_dir, exist_ok=True)

# Проверка существования файла conversations.json
if not os.path.exists(conversations_file):
    raise FileNotFoundError(f"Файл {conversations_file} не найден. Убедитесь, что файл существует.")

# Загрузка разговоров
with open(conversations_file, 'r', encoding='utf-8') as f:
    conversations = json.load(f)

# Сбор всех слов
all_words = []
for pair in conversations:
    for sentence in pair:
        words = sentence.lower().split()
        all_words.extend(words)

# Подсчет частоты слов
word_counts = Counter(all_words)

# Создание словарей
word_to_idx = {"<PAD>": 0, "<UNK>": 1}
idx_to_word = {0: "<PAD>", 1: "<UNK>"}

# Добавление слов в словарь
for word in word_counts:
    if word not in word_to_idx:
        idx = len(word_to_idx)
        word_to_idx[word] = idx
        idx_to_word[idx] = word

# Дополнение словаря до размера 549
vocab_size = 549
while len(word_to_idx) < vocab_size:
    idx = len(word_to_idx)
    word_to_idx[f'<FAKE_{idx}>'] = idx
    idx_to_word[idx] = f'<FAKE_{idx}>'

# Определение max_length
max_length = max(len(pair[0].split()) for pair in conversations) + 1  # +1 для целевого сдвига

# Создание последовательностей
input_sequences = []
output_sequences = []

for input_text, target_text in conversations:
    # Токенизация входного текста
    input_tokens = input_text.lower().split()
    input_seq = [word_to_idx.get(word, 1) for word in input_tokens]
    
    # Паддинг входной последовательности
    if len(input_seq) < max_length:
        input_seq += [0] * (max_length - len(input_seq))
    else:
        input_seq = input_seq[:max_length]
    
    # Токенизация целевого текста
    target_tokens = target_text.lower().split()
    target_seq = [word_to_idx.get(word, 1) for word in target_tokens]
    
    # Паддинг выходной последовательности
    if len(target_seq) < max_length:
        target_seq += [0] * (max_length - len(target_seq))
    else:
        target_seq = target_seq[:max_length]
    
    input_sequences.append(input_seq)
    output_sequences.append(target_seq)

# Конвертация в numpy массивы
input_sequences = np.array(input_sequences)
output_sequences = np.array(output_sequences)

# Подготовка данных для сохранения
data = {
    'input_sequences': input_sequences,
    'target_sequences': output_sequences,
    'word_to_idx': word_to_idx,
    'idx_to_word': idx_to_word,
    'vocab_size': 549,
    'max_length': 20
}

# Сохранение данных
joblib.dump(data, output_file, compress=3)

# Вывод информации
print(f"✅ Файл {output_file} успешно создан!")
print(f"Vocab size: {len(word_to_idx)}")
print(f"Max length: {max_length}")
print(f"Input sequences shape: {input_sequences.shape}")
print(f"Output sequences shape: {output_sequences.shape}")

# Добавлен отладочный вывод
print("\nПервые 10 токенов из word_to_idx:")
for word, idx in list(word_to_idx.items())[:10]:
    print(f"  {word}: {idx}")

print("\nПоследние 10 токенов из word_to_idx:")
for word, idx in list(word_to_idx.items())[-10:]:
    print(f"  {word}: {idx}")

print(f"\nФинальный размер словаря: {len(word_to_idx)}")