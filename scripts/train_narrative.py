# train_narrative.py — дообучение Qwen2.5-3B на повествовательных примерах

import torch
import json
import os
from transformers import AutoTokenizer, AutoModelForCausalLM

# Пути
DATA_FILE = "data/narrative_examples/examples.json"
MODEL_PATH = "models/qwen2.5-3b"  # Qwen2.5-3B
BASE_MODEL = "Qwen/Qwen2.5-3B-Instruct"

# Загружаем дополнительные данные
def load_narrative_data():
    if not os.path.exists(DATA_FILE):
        print(f"❌ Файл не найден: {DATA_FILE}. Пропуск.")
        return []
    
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)
    print(f"✅ Загружено {len(data)} повествовательных примеров")
    return data

# Дообучение Qwen2.5-3B
def train_with_narrative():
    narrative_data = load_narrative_data()
    if not narrative_data:
        print("⚠️ Нет данных для дообучения")
        return
    
    print("🤖 Загрузка Qwen2.5-3B...")
    tokenizer = AutoTokenizer.from_pretrained(BASE_MODEL)
    model = AutoModelForCausalLM.from_pretrained(BASE_MODEL)
    
    # Формируем тексты из примеров
    texts = [ex.get("text", ex.get("prompt", "")) for ex in narrative_data if ex]
    texts = [t for t in texts if t and len(t) > 10]
    
    print(f"📝 Формируем датасет: {len(texts)} текстов")
    
    # Токенизация
    encodings = tokenizer("\n\n".join(texts), return_tensors="pt")
    
    # Простое дообучение (gradient accumulation)
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
    os.makedirs(os.path.dirname(MODEL_PATH) or ".", exist_ok=True)
    model.save_pretrained(MODEL_PATH)
    tokenizer.save_pretrained(MODEL_PATH)
    print(f"✅ Qwen2.5-3B дообучен и сохранён в {MODEL_PATH}")

if __name__ == "__main__":
    train_with_narrative()