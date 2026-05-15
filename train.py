# train.py — полное обучение модели с нуля

import torch
import torch.nn as nn
import torch.optim as optim
import joblib
import json
import os
from torch.utils.data import Dataset, DataLoader

from utils import *

# === Настройки ===
DATA_DIR = "data"
OLD_DATA_PATH = os.path.join(DATA_DIR, "chat_data.pkl")
CONVERSATIONS_JSON = os.path.join(DATA_DIR, "conversations.json")
TRAINING_PAIRS_PATH = os.path.join(DATA_DIR, "training_pairs.jsonl")

TEMP_TRAIN_DATA = os.path.join(DATA_DIR, "temp_train.pkl")
MODEL_PATH = "models/chat_model.pth"

MAX_LENGTH = 64
BATCH_SIZE = 16
EPOCHS = 20
EMBEDDING_DIM = 128
HIDDEN_DIM = 256
NUM_LAYERS = 2
LEARNING_RATE = 0.001
DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")

os.makedirs("models", exist_ok=True)



# === Преобразование сессий в пары ===
def session_to_context_pairs(session, max_length=MAX_LENGTH):
    pairs = []
    context = []
    for i, msg in enumerate(session):
        if i % 2 == 1:
            user_msg = clean_text(session[i-1])
            bot_msg = clean_text(msg)
            full_context = " ".join(context + [user_msg])
            input_text = " ".join(tokenize(full_context)[:max_length])
            pairs.append([input_text, bot_msg])
        context.append(clean_text(msg))
    return pairs


# === Сбор данных ===
def collect_new_conversations():
    old_data = load_or_initialize_data(OLD_DATA_PATH)
    samples = old_data["samples"].copy()

    new_count = 0

    # --- 1. Основной файл: conversations.json ---
    if os.path.exists(CONVERSATIONS_JSON):
        with open(CONVERSATIONS_JSON, "r", encoding="utf-8") as f:
            try:
                data = json.load(f)
                if not isinstance(data, list):
                    print("❌ Формат conversations.json: ожидается массив")
                    return None
            except Exception as e:
                print(f"❌ Ошибка чтения conversations.json: {e}")
                return None

            for entry in data:
                if not isinstance(entry, dict):
                    continue
                try:
                    pairs = []
                    if "session" in entry:
                        session = [clean_text(m) for m in entry["session"] if m.strip()]
                        if len(session) >= 2:
                            pairs = session_to_context_pairs(session)
                    elif "user" in entry and "bot" in entry:
                        user = clean_text(entry["user"])
                        bot = clean_text(entry["bot"])
                        if user and bot:
                            pairs = [(user, bot)]
                    samples.extend(pairs)
                    new_count += len(pairs)
                except Exception as e:
                    print(f"⚠️ Пропущена запись в conversations.json: {e}")

    # --- 2. Дополнительно: training_pairs.jsonl ---
    TRAINING_PAIRS_PATH = os.path.join(DATA_DIR, "training_pairs.jsonl")
    if os.path.exists(TRAINING_PAIRS_PATH):
        with open(TRAINING_PAIRS_PATH, "r", encoding="utf-8") as f:
            for line_num, line in enumerate(f, 1):
                line = line.strip()
                if not line or line.startswith("//"):
                    continue
                try:
                    entry = json.loads(line)
                    pairs = []
                    if "session" in entry:
                        session = [clean_text(m) for m in entry["session"] if m.strip()]
                        if len(session) >= 2:
                            pairs = session_to_context_pairs(session)
                    elif "user" in entry and "bot" in entry:
                        user = clean_text(entry["user"])
                        bot = clean_text(entry["bot"])
                        if user and bot:
                            pairs = [(user, bot)]
                    samples.extend(pairs)
                    new_count += len(pairs)
                except Exception as e:
                    print(f"⚠️ Пропущена строка в training_pairs.jsonl (line {line_num}): {e}")

    if new_count == 0:
        print("❌ Нет новых данных для обучения.")
        return None

    # --- Удаление дубликатов ---
    seen = set()
    unique_samples = []
    for pair in samples:
        key = tuple(pair)
        if key not in seen:
            seen.add(key)
            unique_samples.append(pair)

    print(f"📊 Уникальных пар: {len(unique_samples)} (всего новых: {new_count})")

    # --- Построение словаря ---
    word_to_idx, idx_to_word = build_vocab_from_samples(unique_samples, old_data["word_to_idx"])

    # --- Кодирование ---
    bos_token = word_to_idx["<BOS>"]
    eos_token = word_to_idx["<EOS>"]

    input_sequences = [
        [word_to_idx.get(t, 1) for t in tokenize(u)] for u, _ in unique_samples
    ]
    target_sequences = [
        [bos_token] + [word_to_idx.get(t, 1) for t in tokenize(b)] + [eos_token]
        for _, b in unique_samples
    ]

    # --- Padding ---
    pad_seq = lambda seq: (seq + [0] * MAX_LENGTH)[:MAX_LENGTH]
    input_sequences = [pad_seq(seq) for seq in input_sequences]
    target_sequences = [pad_seq(seq) for seq in target_sequences]

    # --- Сохранение ---
    temp_data = {
        "input_sequences": input_sequences,
        "target_sequences": target_sequences,
        "word_to_idx": word_to_idx,
        "idx_to_word": idx_to_word,
        "vocab_size": len(word_to_idx),
        "max_length": MAX_LENGTH,
        "samples": unique_samples,
    }
    joblib.dump(temp_data, TEMP_TRAIN_DATA)
    print(f"✅ Подготовлено {len(unique_samples)} пар")
    return TEMP_TRAIN_DATA


# === Датасет ===
class ChatDataset(Dataset):
    def __init__(self, data_file):
        data = joblib.load(data_file)
        self.inputs = data["input_sequences"]
        self.labels = data["target_sequences"]

    def __len__(self):
        return len(self.inputs)

    def __getitem__(self, idx):
        return {
            "input_ids": torch.tensor(self.inputs[idx], dtype=torch.long),
            "labels": torch.tensor(self.labels[idx], dtype=torch.long)
        }


# === Модель ===
class ChatNN(nn.Module):
    def __init__(self, vocab_size, embedding_dim, hidden_dim, num_layers):
        super(ChatNN, self).__init__()
        self.embedding = nn.Embedding(vocab_size, embedding_dim, padding_idx=0)
        self.lstm = nn.LSTM(embedding_dim, hidden_dim, num_layers, batch_first=True, dropout=0.3 if num_layers > 1 else 0)
        self.fc = nn.Linear(hidden_dim, vocab_size)

    def forward(self, x, hidden=None):
        embedded = self.embedding(x)
        lstm_out, hidden = self.lstm(embedded, hidden)
        logits = self.fc(lstm_out)
        return logits, hidden


# === Обучение ===
def train(model, dataloader, epochs, device):
    model.train()
    criterion = nn.CrossEntropyLoss(ignore_index=0)
    optimizer = optim.Adam(model.parameters(), lr=LEARNING_RATE)

    for epoch in range(epochs):
        total_loss = 0
        for batch in dataloader:
            input_ids = batch["input_ids"].to(device)
            labels = batch["labels"].to(device)

            optimizer.zero_grad()
            logits, _ = model(input_ids)
            loss = criterion(logits.view(-1, logits.size(-1)), labels.view(-1))
            loss.backward()
            optimizer.step()

            total_loss += loss.item()

        avg_loss = total_loss / len(dataloader)
        print(f"Epoch [{epoch+1}/{epochs}], Loss: {avg_loss:.4f}")


# === Главный блок ===
if __name__ == "__main__":
    print("🔄 Собираем данные...")
    data_file = collect_new_conversations()

    if not data_file:
        print("ℹ️ Нечего учить — выхожу.")
        exit()

    temp_data = joblib.load(data_file)
    vocab_size = temp_data["vocab_size"]

    model = ChatNN(vocab_size, EMBEDDING_DIM, HIDDEN_DIM, NUM_LAYERS).to(DEVICE)
    model = load_model_state(model, MODEL_PATH, DEVICE)

    dataset = ChatDataset(data_file)
    dataloader = DataLoader(dataset, batch_size=BATCH_SIZE, shuffle=True)
    train(model, dataloader, EPOCHS, DEVICE)

    torch.save(model.state_dict(), MODEL_PATH)
    joblib.dump({
        "word_to_idx": temp_data["word_to_idx"],
        "idx_to_word": temp_data["idx_to_word"],
        "vocab_size": vocab_size,
        "max_length": MAX_LENGTH,
        "samples": temp_data["samples"]
    }, OLD_DATA_PATH)

    print(f"🎉 Модель обучена: {MODEL_PATH}")