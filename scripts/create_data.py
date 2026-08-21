# create_data.py

import os
import joblib
import numpy as np

# Определяем BASE_DIR
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Пример данных (замените на реальные из вашего обучения)
data = {
    'word_to_idx': {
        '<PAD>': 0,
        '<UNK>': 1,
        'привет': 2,
        'пока': 3,
        'как': 4,
        'дела': 5,
        'хорошо': 6,
        'спасибо': 7
    },
    'idx_to_word': {
        0: '<PAD>',
        1: '<UNK>',
        2: 'привет',
        3: 'пока',
        4: 'как',
        5: 'дела',
        6: 'хорошо',
        7: 'спасибо'
    },
    'vocab_size': 549,
    'max_length': 20
}

# Сохраняем с помощью joblib
joblib.dump(data, os.path.join(BASE_DIR, 'data', 'chat_data.pkl'), compress=3)

print("✅ Файл data/chat_data.pkl успешно создан!")