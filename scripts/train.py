import sys
import os

# Добавляем корень проекта в путь, чтобы import src работал
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(project_root)

# Теперь можно импортировать модули
import torch
from src.preprocess import prepare_chat_dataset
from src.chat_model import train_model

# Создаём необходимые директории
os.makedirs('Wuglarst/data', exist_ok=True)
os.makedirs('Wuglarst/models', exist_ok=True)

# Загружаем диалоги из JSON
import json
with open(os.path.join(project_root, 'data', 'conversations.json'), 'r', encoding='utf-8') as f:
    conversations = json.load(f)

# Подготавливаем датасет
print("Preparing dataset...")
data = prepare_chat_dataset(conversations, vocab_size=5000, max_length=20)

# Обучаем модель
print("\nTraining model...")
model = train_model(
    data_file='Wuglarst/data/chat_data.pkl',
    vocab_size=data['vocab_size'],
    embedding_dim=128,
    hidden_dim=256,
    num_layers=2,
    epochs=200,
    batch_size=16,
    lr=0.001
)

print("\nTraining completed!")
print("You can now run python -m src.chatbot to start chatting")