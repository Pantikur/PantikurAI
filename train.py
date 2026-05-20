# train.py — полное обучение модели с нуля
# Гарантирует создание data/chat_data.pkl

import torch
import torch.nn as nn
import torch.optim as optim
import joblib
import json
import os
from torch.utils.data import Dataset, DataLoader

# === Настройки ===
DATA_DIR = "data"
OLD_DATA_PATH = os.path.join(DATA_DIR, "chat_data.pkl")          # Выход: метаданные модели
CONVERSATIONS_JSON = os.path.join(DATA_DIR, "conversations.json") # Диалоги (массив)
TRAINING_PAIRS_JSONL = os.path.join(DATA_DIR, "training_pairs.jsonl")  # FAQ (JSONL)

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


# === Вспомогательные функции (на случай, если utils не подключается) ===
def clean_text(text):
    if not isinstance(text, str) or not text.strip():
        return ""
    import re
    text = text.lower()
    text = re.sub(r'[^а-яёa-z0-9\s?!,.]', '', text)
    text = re.sub(r'\s+', ' ', text).strip()

    replacements = {
        "яне": "я не", "тыне": "ты не", "онне": "он не", "она нее": "она не",
        "мыне": "мы не", "выне": "вы не", "онине": "они не",
        "чтобы": "чтобы", "потомучто": "потому что", "вотже": "вот же",
        "нука": "ну ка", "давайка": "давай ка", "подожди": "подожди",
        "ага": "ага", "угу": "угу", "ии": "и", "ещё": "ещё", "конечно": "конечно",
        "блин": "блин", "чёрт": "чёрт", "класс": "класс", "прикольно": "прикольно",
        "незнаю": "не знаю", "хз": "не знаю", "ок": "окей", "спс": "спасибо",
        "прив": "привет", "пока": "пока", "здарова": "здравствуй", "здравствуйте": "здравствуйте"
    }
    for wrong, right in replacements.items():
        text = text.replace(wrong, right)
    return text


def tokenize(text):
    return text.split()


def load_or_initialize_data(path):
    """Загружает старые метаданные или возвращает начальное состояние"""
    if os.path.exists(path):
        try:
            data = joblib.load(path)
            print(f"✅ Загружено состояние: {len(data['samples'])} пар")
            return data
        except Exception as e:
            print(f"⚠️ Не удалось загрузить {path}: {e}")
    print("🆕 Начинаем с чистого листа")
    return {
        "word_to_idx": {"<PAD>": 0, "<UNK>": 1},
        "idx_to_word": {0: "<PAD>", 1: "<UNK>"},
        "vocab_size": 2,
        "max_length": MAX_LENGTH,
        "samples": []
    }


def build_vocab_from_samples(samples, old_word_to_idx):
    from collections import Counter
    word_counter = Counter()

    # Базовые слова
    BASIC_WORDS = ["привет", "пока", "спасибо", "извини", "что", "как", "почему"]
    for word in BASIC_WORDS:
        word_counter[word] += 10

    # Слова из старого словаря
    for word in old_word_to_idx:
        if word not in ["<PAD>", "<UNK>"]:
            word_counter[word] += 5

    # Слова из новых данных
    for user, bot in samples:
        word_counter.update(tokenize(user))
        word_counter.update(tokenize(bot))

    # Построение нового словаря
    vocab_words = ["<PAD>", "<UNK>"]
    vocab_words.extend([w for w in old_word_to_idx if w not in vocab_words])
    new_words = [w for w, _ in word_counter.most_common() if w not in vocab_words]
    remaining_slots = 8000 - len(vocab_words)
    vocab_words.extend(new_words[:remaining_slots])

    word_to_idx = {word: idx for idx, word in enumerate(vocab_words)}
    idx_to_word = {idx: word for idx, word in enumerate(vocab_words)}
    return word_to_idx, idx_to_word


def load_model_state(model, path, device):
    if os.path.exists(path):
        try:
            model.load_state_dict(torch.load(path, map_location=device))
            print("✅ Веса загружены")
        except Exception as e:
            print(f"⚠️ Не удалось загрузить веса: {e}")
    else:
        print("🆕 Модель инициализирована с нуля")
    return model


# === Преобразование сессий в пары ===
def session_to_context_pairs(session, max_length=MAX_LENGTH):
    pairs = []
    context = []
    for i, msg in enumerate(session):
        if i % 2 == 1 and i > 0:
            user_msg = clean_text(session[i-1])
            bot_msg = clean_text(msg)
            full_context = " ".join(context + [user_msg])
            input_text = " ".join(tokenize(full_context)[:max_length])
            pairs.append([input_text, bot_msg])
        context.append(clean_text(msg))
    return pairs


# === Сбор данных ===
def collect_training_samples():
    old_data = load_or_initialize_data(OLD_DATA_PATH)
    samples = old_data["samples"].copy()
    new_count = 0

    # --- 1. Диалоги: conversations.json ---
    if os.path.exists(CONVERSATIONS_JSON):
        try:
            with open(CONVERSATIONS_JSON, "r", encoding="utf-8") as f:
                data = json.load(f)
                if isinstance(data, list):
                    for entry in data:
                        if isinstance(entry, list) and len(entry) >= 2:
                            cleaned = [clean_text(m) for m in entry if m.strip()]
                            if len(cleaned) >= 2:
                                pairs = session_to_context_pairs(cleaned)
                                samples.extend(pairs)
                                new_count += len(pairs)
                        elif isinstance(entry, dict):
                            # Поддержка формата {"session": [...]}
                            session = entry.get("session", [])
                            if isinstance(session, list) and len(session) >= 2:
                                cleaned = [clean_text(m) for m in session if m.strip()]
                                if len(cleaned) >= 2:
                                    pairs = session_to_context_pairs(cleaned)
                                    samples.extend(pairs)
                                    new_count += len(pairs)
                else:
                    print("⚠️ conversations.json: ожидается массив сессий")
        except Exception as e:
            print(f"❌ Ошибка чтения conversations.json: {e}")

    # --- 2. Знания: training_pairs.jsonl ---
    if os.path.exists(TRAINING_PAIRS_JSONL):
        try:
            with open(TRAINING_PAIRS_JSONL, "r", encoding="utf-8") as f:
                for line_num, line in enumerate(f, 1):
                    line = line.strip()
                    if not line or line.startswith("//"):
                        continue
                    try:
                        entry = json.loads(line)
                        if "session" in entry:
                            session = [clean_text(m) for m in entry["session"] if m.strip()]
                            if len(session) >= 2:
                                pairs = session_to_context_pairs(session)
                                samples.extend(pairs)
                                new_count += len(pairs)
                        elif "user" in entry and "bot" in entry:
                            user = clean_text(entry["user"])
                            bot = clean_text(entry["bot"])
                            if user and bot:
                                samples.append([user, bot])
                                new_count += 1
                    except Exception as e:
                        print(f"⚠️ Пропущена строка в training_pairs.jsonl ({line_num}): {e}")
        except Exception as e:
            print(f"❌ Ошибка чтения training_pairs.jsonl: {e}")

    if new_count == 0:
        print("ℹ️ Нет новых данных для обучения.")
        return None

    # Уникализация
    seen = set()
    unique_samples = []
    for pair in samples:
        key = tuple(pair)
        if key not in seen:
            seen.add(key)
            unique_samples.append(pair)

    print(f"📊 Уникальных пар: {len(unique_samples)} (всего новых: {new_count})")

    # Построение словаря
    word_to_idx, idx_to_word = build_vocab_from_samples(unique_samples, old_data["word_to_idx"])

    # Кодирование
    input_sequences = [
        [word_to_idx.get(t, 1) for t in tokenize(u)] for u, _ in unique_samples
    ]
    target_sequences = [
        [word_to_idx.get(t, 1) for t in tokenize(b)]
        for _, b in unique_samples
    ]

    # Padding
    pad_seq = lambda seq: (seq + [0] * MAX_LENGTH)[:MAX_LENGTH]
    input_sequences = [pad_seq(seq) for seq in input_sequences]
    target_sequences = [pad_seq(seq) for seq in target_sequences]

    # Сохранение временных данных
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
    print(f"✅ Подготовлено {len(unique_samples)} обучающих пар")
    return TEMP_TRAIN_DATA


# === Датасет ===
class ChatDataset(Dataset):
    def __init__(self, data_file):
        self.data = joblib.load(data_file)
        self.inputs = self.data["input_sequences"]
        self.labels = self.data["target_sequences"]

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
        self.lstm = nn.LSTM(embedding_dim, hidden_dim, num_layers, batch_first=True,
                            dropout=0.3 if num_layers > 1 else 0)
        self.fc = nn.Linear(hidden_dim, vocab_size)

    def forward(self, x, hidden=None):
        embedded = self.embedding(x)
        lstm_out, hidden = self.lstm(embedded, hidden)
        logits = self.fc(lstm_out)
        return logits, hidden


# === Обучение ===
def train_model(model, dataloader, epochs, device):
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


# === Главная функция ===
def main():
    print("🔄 Сбор и подготовка данных...")
    data_file = collect_training_samples()

    # === Если данных нет → всё равно нужен chat_data.pkl ===
    if data_file is None:
        print("ℹ️ Нет новых данных. Создаём минимальную модель...")

        fallback_data = {
            "word_to_idx": {"<PAD>": 0, "<UNK>": 1, "привет": 2, "пока": 3},
            "idx_to_word": {0: "<PAD>", 1: "<UNK>", 2: "привет", 3: "пока"},
            "vocab_size": 4,
            "max_length": MAX_LENGTH,
            "samples": [["привет", "здравствуй"], ["пока", "до свидания"]]
        }
        joblib.dump(fallback_data, OLD_DATA_PATH)
        print(f"🟢 Заглушка создана: {OLD_DATA_PATH}")
        return

    # === Есть данные → обучаем ===
    temp_data = joblib.load(data_file)
    model = ChatNN(temp_data["vocab_size"], EMBEDDING_DIM, HIDDEN_DIM, NUM_LAYERS).to(DEVICE)
    model = load_model_state(model, MODEL_PATH, DEVICE)

    dataset = ChatDataset(data_file)
    dataloader = DataLoader(dataset, batch_size=BATCH_SIZE, shuffle=True)
    train_model(model, dataloader, EPOCHS, DEVICE)

    # Сохраняем веса
    torch.save(model.state_dict(), MODEL_PATH)

    # Сохраняем метаданные
    joblib.dump({
        "word_to_idx": temp_data["word_to_idx"],
        "idx_to_word": temp_data["idx_to_word"],
        "vocab_size": temp_data["vocab_size"],
        "max_length": MAX_LENGTH,
        "samples": temp_data["samples"]
    }, OLD_DATA_PATH)

    print(f"🎉 Модель успешно обучена и сохранена!")
    print(f"📄 Метаданные: {OLD_DATA_PATH}")
    print(f"💾 Веса: {MODEL_PATH}")


if __name__ == "__main__":
    main()