# train.py — обучение Transformer модели (ChatNN из chat_model.py)

import torch
import torch.nn as nn
from torch.utils.data import Dataset, DataLoader
import joblib
import json
import os
from collections import Counter

# === Настройки ===
DATA_DIR = "data"
OLD_DATA_PATH = os.path.join(DATA_DIR, "chat_data.pkl")
CONVERSATIONS_JSON = os.path.join(DATA_DIR, "conversations.json")
TRAINING_PAIRS_JSONL = os.path.join(DATA_DIR, "training_pairs.jsonl")
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

# Добавляем путь для импорта ChatNN
import sys
sys.path.append(".")  # Чтобы можно было импортировать из Wuglarst

from Wuglarst.src.chat_model import ChatNN


# === Вспомогательные функции ===
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
    if os.path.exists(path):
        try:
            data = joblib.load(path)
            print(f"✅ Загружено состояние: {len(data['samples'])} пар")
            return data
        except Exception as e:
            print(f"⚠️ Не удалось загрузить {path}: {e}")
    print("🆕 Начинаем с чистого листа")
    return {
        "word_to_idx": {"<PAD>": 0, "<UNK>": 1, "<EOS>": 2},
        "idx_to_word": {0: "<PAD>", 1: "<UNK>", 2: "<EOS>"},
        "vocab_size": 3,
        "max_length": MAX_LENGTH,
        "samples": []
    }


def build_vocab_from_samples(samples, old_word_to_idx):
    word_counter = Counter()

    # Базовые слова
    BASIC_WORDS = ["привет", "пока", "спасибо", "извини", "что", "как", "почему"]
    for word in BASIC_WORDS:
        word_counter[word] += 10

    # Слова из старого словаря
    for word in old_word_to_idx:
        if word not in ["<PAD>", "<UNK>", "<EOS>"]:
            word_counter[word] += 5

    # Слова из новых данных
    for user, bot in samples:
        word_counter.update(tokenize(user))
        word_counter.update(tokenize(bot))

    # Построение словаря
    vocab_words = ["<PAD>", "<UNK>", "<EOS>"]
    vocab_words.extend([w for w in old_word_to_idx if w not in vocab_words])
    new_words = [w for w, _ in word_counter.most_common() if w not in vocab_words]
    remaining_slots = 8000 - len(vocab_words)
    vocab_words.extend(new_words[:remaining_slots])

    word_to_idx = {word: idx for idx, word in enumerate(vocab_words)}
    idx_to_word = {idx: word for idx, word in enumerate(vocab_words)}
    return word_to_idx, idx_to_word


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
        if len(context) > 6:  # Ограничиваем длину контекста
            context = context[-6:]
    return pairs


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
                            session = entry.get("session", [])
                            if isinstance(session, list) and len(session) >= 2:
                                cleaned = [clean_text(m) for m in session if m.strip()]
                                if len(cleaned) >= 2:
                                    pairs = session_to_context_pairs(cleaned)
                                    samples.extend(pairs)
                                    new_count += len(pairs)
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
        [word_to_idx.get(t, 1) for t in tokenize(b)] + [word_to_idx["<EOS>"]]  # Добавляем <EOS>
        for _, b in unique_samples
    ]

    # Паддинг с сохранением <EOS>
    def pad_seq(seq):
        if len(seq) >= MAX_LENGTH:
            return seq[:MAX_LENGTH-1] + [seq[-1]]  # Сохраняем последний токен
        return (seq + [0] * MAX_LENGTH)[:MAX_LENGTH]

    input_sequences = [pad_seq(seq) for seq in input_sequences]
    target_sequences = [pad_seq(seq) for seq in target_sequences]

    # Сохраняем временные данные
    temp_data = {
        "input_sequences": input_sequences,
        "target_sequences": target_sequences,
        "word_to_idx": word_to_idx,
        "idx_to_word": idx_to_word,
        "vocab_size": len(word_to_idx),
        "max_length": MAX_LENGTH,
        "samples": unique_samples,
    }
    temp_path = os.path.join(DATA_DIR, "temp_train.pkl")
    joblib.dump(temp_data, temp_path)
    print(f"✅ Подготовлено {len(unique_samples)} обучающих пар")
    return temp_path


# === Dataset ===
class ChatDataset(Dataset):
    def __init__(self, data_file):
        self.data = joblib.load(data_file)
        self.inputs = self.data["input_sequences"]
        self.labels = self.data["target_sequences"]

    def __len__(self):
        return len(self.inputs)

    def __getitem__(self, idx):
        input_ids = self.inputs[idx]
        labels = self.labels[idx]
        mask = (torch.tensor(input_ids) != 0).float()  # Маска: 1 если не <PAD>
        return {
            "input_ids": torch.tensor(input_ids, dtype=torch.long),
            "labels": torch.tensor(labels, dtype=torch.long),
            "mask": mask
        }


# === Загрузка весов с адаптацией под новый словарь ===
def load_model_weights(model, path, device):
    if not os.path.exists(path):
        print("🆕 Модель инициализирована с нуля")
        return model

    try:
        state_dict = torch.load(path, map_location=device)
        current_vocab_size = model.vocab_size
        ckpt_vocab_size = state_dict["embedding.weight"].size(0)

        if current_vocab_size != ckpt_vocab_size:
            print(f"⚠️ Размер словаря изменился: {ckpt_vocab_size} → {current_vocab_size}. Адаптируем...")
            old_w_emb = state_dict['embedding.weight']
            old_w_fc = state_dict['fc.weight']
            old_b_fc = state_dict['fc.bias']

            new_w_emb = torch.zeros(current_vocab_size, model.embedding_dim, device=device)
            new_w_fc = torch.zeros(current_vocab_size, model.hidden_dim, device=device)
            new_b_fc = torch.zeros(current_vocab_size, device=device)

            min_size = min(old_w_emb.size(0), current_vocab_size)
            new_w_emb[:min_size] = old_w_emb[:min_size]
            new_w_fc[:min_size] = old_w_fc[:min_size]
            new_b_fc[:min_size] = old_b_fc[:min_size]

            state_dict['embedding.weight'] = new_w_emb
            state_dict['fc.weight'] = new_w_fc
            state_dict['fc.bias'] = new_b_fc

        model.load_state_dict(state_dict, strict=False)
        print("✅ Веса загружены (с адаптацией)")
    except Exception as e:
        print(f"⚠️ Ошибка загрузки весов: {e}")
    return model


# === Обучение ===
def train_model(model, dataloader, epochs, device, lr=LEARNING_RATE):
    model.train()
    criterion = nn.CrossEntropyLoss(ignore_index=0)  # игнорируем <PAD>
    optimizer = torch.optim.Adam(model.parameters(), lr=lr)

    for epoch in range(epochs):
        total_loss = 0
        for batch in dataloader:
            input_ids = batch["input_ids"].to(device)
            labels = batch["labels"].to(device)
            mask = batch["mask"].to(device)

            optimizer.zero_grad()
            logits = model(input_ids, mask=mask)
            loss = criterion(logits.view(-1, model.vocab_size), labels.view(-1))
            loss.backward()
            optimizer.step()

            total_loss += loss.item()

        avg_loss = total_loss / len(dataloader)
        print(f"Epoch [{epoch+1}/{epochs}], Loss: {avg_loss:.4f}")


# === Главная функция ===
def main():
    print("🔄 Сбор и подготовка данных...")
    data_file = collect_training_samples()

    if data_file is None:
        print("ℹ️ Нет новых данных. Создаём минимальную модель...")

        fallback_data = {
            "word_to_idx": {"<PAD>": 0, "<UNK>": 1, "<EOS>": 2, "привет": 3, "пока": 4},
            "idx_to_word": {0: "<PAD>", 1: "<UNK>", 2: "<EOS>", 3: "привет", 4: "пока"},
            "vocab_size": 5,
            "max_length": MAX_LENGTH,
            "samples": [["привет", "здравствуй"], ["пока", "до свидания"]]
        }
        joblib.dump(fallback_data, OLD_DATA_PATH)
        print(f"🟢 Заглушка создана: {OLD_DATA_PATH}")
        return

    # Загружаем данные
    temp_data = joblib.load(data_file)

    # Создаём модель
    model = ChatNN(
        vocab_size=temp_data["vocab_size"],
        embedding_dim=EMBEDDING_DIM,
        hidden_dim=HIDDEN_DIM,
        num_layers=NUM_LAYERS,
        max_length=MAX_LENGTH,
        pad_token_id=0,
        eos_token_id=temp_data["word_to_idx"]["<EOS>"]
    ).to(DEVICE)

    # Загружаем предыдущие веса
    model = load_model_weights(model, MODEL_PATH, DEVICE)

    # Датасет и даталоадер
    dataset = ChatDataset(data_file)
    dataloader = DataLoader(dataset, batch_size=BATCH_SIZE, shuffle=True)

    # Обучение
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