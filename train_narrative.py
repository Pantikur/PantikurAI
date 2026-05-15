# train_narrative.py — обучение на повествовательных примерах

import torch
import json
import os
from train import ChatDataset, ChatNN, train  # используем существующие классы

# Пути
DATA_FILE = "data/narrative_examples/examples.json"
MODEL_PATH = "models/chat_model.pth"
DATA_SAVE_PATH = "data/chat_data.pkl"

# Загружаем дополнительные данные
def load_narrative_data():
    if not os.path.exists(DATA_FILE):
        print(f"❌ Файл не найден: {DATA_FILE}. Пропуск.")
        return []
    
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)
    print(f"✅ Загружено {len(data)} повествовательных примеров")
    return data

# Расширяем основной train()
def train_with_narrative():
    # Загружаем базовые данные
    from train import load_conversations, build_vocab, ChatDataset, ChatNN
    base_data = load_conversations()
    
    # Добавляем повествовательные
    narrative_data = load_narrative_data()
    full_data = base_data + narrative_data
    
    # Продолжаем как в train.py
    word_to_idx, idx_to_word = build_vocab(full_data)
    dataset = ChatDataset(full_data, word_to_idx, 32)
    
    # Модель и обучение — как в оригинале
    model = ChatNN(len(word_to_idx), 128, 256, 2).to("cpu")
    # ... (остальное — аналогично train.py)

if __name__ == "__main__":
    train_with_narrative()