import sys
import os

# Добавляем корень проекта в путь, чтобы import src работал
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(project_root)

# Теперь можно импортировать модули
import torch
from transformers import AutoTokenizer, AutoModelForCausalLM

# Создаём необходимые директории
os.makedirs(os.path.join(project_root, 'models', 'qwen2.5-3b'), exist_ok=True)

# Загружаем диалоги из JSON
import json
with open(os.path.join(project_root, 'data', 'conversations.json'), 'r', encoding='utf-8') as f:
    conversations = json.load(f)

print(f"📝 Загружено {len(conversations)} диалогов")

# Дообучение Qwen2.5-3B
print("\n🤖 Загрузка Qwen2.5-3B...")
BASE_MODEL = "Qwen/Qwen2.5-3B-Instruct"
MODEL_PATH = os.path.join(project_root, 'models', 'qwen2.5-3b')

tokenizer = AutoTokenizer.from_pretrained(BASE_MODEL)
model = AutoModelForCausalLM.from_pretrained(BASE_MODEL)

# Формируем тексты
texts = []
for conv in conversations:
    if isinstance(conv, dict) and "messages" in conv:
        for msg in conv["messages"]:
            if isinstance(msg, dict) and "text" in msg:
                texts.append(msg["text"])
    elif isinstance(conv, str):
        texts.append(conv)

texts = [t for t in texts if t and len(t) > 5]
print(f"📊 Формируем датасет: {len(texts)} текстов")

# Токенизация
encodings = tokenizer("\n\n".join(texts[:1000]), return_tensors="pt")  # Ограничиваем для скорости

from torch.utils.data import DataLoader, TensorDataset
dataset = TensorDataset(encodings["input_ids"], encodings["attention_mask"])
dataloader = DataLoader(dataset, batch_size=2, shuffle=True)

optimizer = torch.optim.Adam(model.parameters(), lr=1e-5)

print("🚀 Начало дообучения...")
model.train()
for epoch in range(3):
    total_loss = 0
    for batch_input, batch_mask in dataloader:
        optimizer.zero_grad()
        outputs = model(input_ids=batch_input, attention_mask=batch_mask, labels=batch_input)
        loss = outputs.loss
        loss.backward()
        optimizer.step()
        total_loss += loss.item()
    
    print(f"Эпоха {epoch+1}/3, Loss: {total_loss/len(dataloader):.4f}")

# Сохранение
model.save_pretrained(MODEL_PATH)
tokenizer.save_pretrained(MODEL_PATH)
print(f"✅ Qwen2.5-3B дообучена и сохранена в {MODEL_PATH}")