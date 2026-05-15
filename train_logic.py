# train_logic.py — логика обучения (вынесена из retrain.py)

import torch
import torch.nn as nn
import torch.optim as optim
import joblib
import json
import os
import re
import random
from collections import Counter
from torch.utils.data import Dataset, DataLoader
from tqdm import tqdm

# === Настройки ===
DATA_DIR = "data"
OLD_DATA_PATH = os.path.join(DATA_DIR, "chat_data.pkl")
CONVERSATIONS_PATH = os.path.join(DATA_DIR, "conversations.jsonl")
TRAINING_PAIRS_PATH = os.path.join(DATA_DIR, "training_pairs.jsonl")
BACKUP_CONVERSATIONS = os.path.join(DATA_DIR, "conversations.old.jsonl")
BACKUP_TRAINING = os.path.join(DATA_DIR, "training_pairs.old.jsonl")
LOG_PATH = os.path.join(DATA_DIR, "training.log")
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


def clean_text(text):
    if not isinstance(text, str) or not text.strip():
        return ""
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


def load_or_initialize_data():
    if os.path.exists(OLD_DATA_PATH):
        data = joblib.load(OLD_DATA_PATH)
        print(f"✅ Загружено состояние: {len(data['samples'])} пар")
        return data
    else:
        print("🆕 Начинаем с чистого листа")
        return {
            "word_to_idx": {"<PAD>": 0, "<UNK>": 1},
            "idx_to_word": {0: "<PAD>", 1: "<UNK>"},
            "vocab_size": 2,
            "max_length": MAX_LENGTH,
            "samples": []
        }


def session_to_context_pairs(session, max_length=MAX_LENGTH):
    pairs = []
    context = []
    for i, msg in enumerate(session):
        if i % 2 == 1:
            user_msg = session[i-1]
            bot_msg = msg
            full_context = " ".join(context + [clean_text(user_msg)])
            input_text = " ".join(full_context.split()[:max_length])
            pairs.append([input_text, clean_text(bot_msg)])
        context.append(clean_text(msg))
    return pairs


def collect_new_conversations():
    data = load_or_initialize_data()
    samples = data["samples"].copy()
    word_counter = Counter()

    BASIC_RUSSIAN_WORDS = [
        "привет", "здравствуй", "пока", "спасибо", "пожалуйста", "извини", "прости",
        "я", "ты", "он", "она", "мы", "вы", "они",
        "мне", "тебе", "ему", "ей", "нам", "вам", "им",
        "что", "как", "почему", "где", "когда", "кто", "зачем",
        "говорить", "сказать", "думать", "знать", "понимать", "хотеть",
        "хорошо", "плохо", "нормально", "отлично",
        "можно", "нельзя", "надо", "нужно", "стоит",
        "рад", "грустно", "весело", "интересно", "скучно"
    ]
    for word in BASIC_RUSSIAN_WORDS:
        word_counter[word] += 10

    for word in data["word_to_idx"]:
        if word not in ["<PAD>", "<UNK>"]:
            word_counter[word] += 1

    new_conv_count = 0
    new_know_count = 0

    if os.path.exists(CONVERSATIONS_PATH):
        try:
            with open(CONVERSATIONS_PATH, "r", encoding="utf-8") as f:
                all_sessions = []
                for line in f:
                    line = line.strip()
                    if line:
                        try:
                            session = json.loads(line)
                            if isinstance(session, list):
                                all_sessions.append(session)
                        except json.JSONDecodeError as e:
                            print(f"⚠️ Пропущена строка в conversations.jsonl: {e}")
            for session in all_sessions:
                if len(session) >= 2:
                    cleaned = [clean_text(m) for m in session if m.strip()]
                    if len(cleaned) >= 2:
                        pairs = session_to_context_pairs(cleaned)
                        samples.extend(pairs)
                        new_conv_count += len(pairs)
                        for user, bot in pairs:
                            word_counter.update(user.split())
                            word_counter.update(bot.split())
        except Exception as e:
            print(f"❌ Ошибка чтения conversations.jsonl: {e}")

    DEFAULT_RESPONSES = [
        "Это глубоко...",
        "Я тоже об этом думал.",
        "Возможно, ты ближе к истине, чем думаешь.",
        "Когда никто не смотрит — ты свободен быть собой.",
        "Ты — больше, чем твои мысли."
    ]
    resp_idx = 0

    if os.path.exists(TRAINING_PAIRS_PATH):
        try:
            with open(TRAINING_PAIRS_PATH, "r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if not line:
                        continue
                    try:
                        entry = json.loads(line)
                        text = entry.get("text", "").strip()
                        if text:
                            bot_resp = DEFAULT_RESPONSES[resp_idx % len(DEFAULT_RESPONSES)]
                            resp_idx += 1
                            user_msg = clean_text(text)
                            bot_msg = clean_text(bot_resp)
                            samples.append([user_msg, bot_msg])
                            word_counter.update(user_msg.split())
                            word_counter.update(bot_msg.split())
                            new_know_count += 1
                    except json.JSONDecodeError:
                        continue
        except Exception as e:
            print(f"❌ Ошибка чтения training_pairs.jsonl: {e}")

    if new_conv_count == 0 and new_know_count == 0:
        print("❌ Нет новых валидных пар для обучения")
        return None

    seen = set()
    unique_samples = []
    for pair in samples:
        key = tuple(pair)
        if key not in seen:
            seen.add(key)
            unique_samples.append(pair)

    print(f"📊 Всего уникальных пар: {len(unique_samples)} "
          f"(диалоги: {new_conv_count}, знания: {new_know_count})")

    old_words = [w for w in data["word_to_idx"] if w not in ["<PAD>", "<UNK>"]]
    new_words = [w for w, _ in word_counter.most_common() if w not in old_words]

    vocab_words = ["<PAD>", "<UNK>"] + old_words
    remaining_slots = 8000 - len(vocab_words)
    vocab_words.extend(new_words[:remaining_slots])

    word_to_idx = {word: idx for idx, word in enumerate(vocab_words)}
    idx_to_word = {idx: word for idx, word in enumerate(vocab_words)}

    input_sequences = []
    target_sequences = []

    for user, bot in unique_samples:
        user_seq = [word_to_idx.get(t, 1) for t in user.split()]
        bot_seq = [word_to_idx.get(t, 1) for t in bot.split()]
        user_seq = (user_seq + [0] * MAX_LENGTH)[:MAX_LENGTH]
        bot_seq = (bot_seq + [0] * MAX_LENGTH)[:MAX_LENGTH]
        input_sequences.append(user_seq)
        target_sequences.append(bot_seq)

    temp_data = {
        "input_sequences": input_sequences,
        "target_sequences": target_sequences,
        "word_to_idx": word_to_idx,
        "idx_to_word": idx_to_word,
        "vocab_size": len(word_to_idx),
        "max_length": MAX_LENGTH,
        "samples": unique_samples
    }
    joblib.dump(temp_data, TEMP_TRAIN_DATA)
    print(f"✅ Подготовлено {len(unique_samples)} обучающих пар")

    if os.path.exists(CONVERSATIONS_PATH):
        os.rename(CONVERSATIONS_PATH, BACKUP_CONVERSATIONS)
        print(f"📦 conversations.jsonl архивирован")
    if os.path.exists(TRAINING_PAIRS_PATH):
        os.rename(TRAINING_PAIRS_PATH, BACKUP_TRAINING)
        print(f"📦 training_pairs.jsonl архивирован")

    return TEMP_TRAIN_DATA


class ChatDataset(Dataset):
    def __init__(self, input_ids, labels):
        self.input_ids = input_ids
        self.labels = labels

    def __len__(self):
        return len(self.input_ids)

    def __getitem__(self, idx):
        return {
            "input_ids": torch.tensor(self.input_ids[idx], dtype=torch.long),
            "labels": torch.tensor(self.labels[idx], dtype=torch.long)
        }


def get_dataloaders(input_sequences, target_sequences, batch_size=16, val_split=0.1):
    dataset_size = len(input_sequences)
    val_size = int(val_split * dataset_size)
    indices = list(range(dataset_size))
    random.shuffle(indices)

    val_indices = indices[:val_size]
    train_indices = indices[val_size:]

    train_inputs = [input_sequences[i] for i in train_indices]
    train_labels = [target_sequences[i] for i in train_indices]
    val_inputs = [input_sequences[i] for i in val_indices]
    val_labels = [target_sequences[i] for i in val_indices]

    train_dataset = ChatDataset(train_inputs, train_labels)
    val_dataset = ChatDataset(val_inputs, val_labels)

    train_loader = DataLoader(train_dataset, batch_size=batch_size, shuffle=True)
    val_loader = DataLoader(val_dataset, batch_size=batch_size, shuffle=False)

    return train_loader, val_loader


class ChatNN(nn.Module):
    def __init__(self, vocab_size, embedding_dim, hidden_dim, num_layers):
        super(ChatNN, self).__init__()
        self.num_layers = num_layers
        self.hidden_dim = hidden_dim
        self.embedding = nn.Embedding(vocab_size, embedding_dim, padding_idx=0)
        self.lstm = nn.LSTM(embedding_dim, hidden_dim, num_layers, batch_first=True, dropout=0.3 if num_layers > 1 else 0)
        self.fc = nn.Linear(hidden_dim, vocab_size)

    def forward(self, x, hidden=None):
        embedded = self.embedding(x)
        lstm_out, hidden = self.lstm(embedded, hidden)
        logits = self.fc(lstm_out)
        return logits, hidden


def train(model, train_loader, val_loader, epochs, device, patience=3):
    model.train()
    criterion = nn.CrossEntropyLoss(ignore_index=0)
    optimizer = optim.Adam(model.parameters(), lr=LEARNING_RATE)

    best_val_loss = float('inf')
    patience_counter = 0

    log_file = open(LOG_PATH, "a", encoding="utf-8")
    log_file.write(f"\n[Training Start] {torch.cuda.get_device_name(0) if torch.cuda.is_available() else 'CPU'} | "
                   f"Epochs={epochs}, Batch={BATCH_SIZE}, LR={LEARNING_RATE}\n")

    for epoch in range(epochs):
        model.train()
        total_train_loss = 0
        train_bar = tqdm(train_loader, desc=f"Epoch {epoch+1}/{epochs} [Train]")
        for batch in train_bar:
            input_ids = batch["input_ids"].to(device)
            labels = batch["labels"].to(device)
            optimizer.zero_grad()
            logits, _ = model(input_ids)
            loss = criterion(logits.view(-1, logits.size(-1)), labels.view(-1))
            loss.backward()
            optimizer.step()
            total_train_loss += loss.item()
            train_bar.set_postfix({"loss": f"{loss.item():.4f}"})

        avg_train_loss = total_train_loss / len(train_loader)

        model.eval()
        total_val_loss = 0
        with torch.no_grad():
            val_bar = tqdm(val_loader, desc=f"Epoch {epoch+1}/{epochs} [Valid]", leave=False)
            for batch in val_bar:
                input_ids = batch["input_ids"].to(device)
                labels = batch["labels"].to(device)
                logits, _ = model(input_ids)
                loss = criterion(logits.view(-1, logits.size(-1)), labels.view(-1))
                total_val_loss += loss.item()
                val_bar.set_postfix({"val_loss": f"{loss.item():.4f}"})

        avg_val_loss = total_val_loss / len(val_loader)

        print(f"✅ Epoch [{epoch+1}/{epochs}] Train Loss: {avg_train_loss:.4f} | Val Loss: {avg_val_loss:.4f}")

        log_entry = f"Epoch {epoch+1}: train_loss={avg_train_loss:.4f}, val_loss={avg_val_loss:.4f}"
        print(log_entry, file=log_file, flush=True)

        if avg_val_loss < best_val_loss:
            best_val_loss = avg_val_loss
            patience_counter = 0
            torch.save(model.state_dict(), MODEL_PATH.replace(".pth", "_best.pth"))
            print(f"🟢 Сохранена лучшая модель: val_loss = {best_val_loss:.4f}")
            print(f"[Best Model Saved] val_loss = {best_val_loss:.4f}", file=log_file, flush=True)
        else:
            patience_counter += 1
            if patience_counter >= patience:
                print(f"🛑 Ранняя остановка на эпохе {epoch+1}: нет улучшений в val_loss за {patience} эпох")
                print(f"[Early Stopping] Patience={patience}", file=log_file, flush=True)
                break

    log_file.close()


def generate_response(model, text, word_to_idx, idx_to_word, max_len=MAX_LENGTH, device='cpu'):
    model.eval()
    tokens = clean_text(text).split()
    indices = [word_to_idx.get(t, 1) for t in tokens]
    indices = (indices + [0] * MAX_LENGTH)[:MAX_LENGTH]
    input_tensor = torch.tensor([indices], dtype=torch.long).to(device)

    with torch.no_grad():
        output, _ = model(input_tensor)
        _, predicted = torch.max(output, dim=-1)

    response = []
    for idx in predicted[0].cpu().numpy():
        word = idx_to_word.get(idx, "<UNK>")
        if word == "<PAD>" or word == "<UNK>":
            continue
        if word in ".!?":
            response.append(word)
            break
        response.append(word)
        if len(response) >= max_len:
            break

    return " ".join(response).strip()


def show_sample_responses(model, samples, word_to_idx, idx_to_word, device):
    print("\n🔍 Примеры генерации после обучения:")
    log_file = open(LOG_PATH, "a", encoding="utf-8")
    print("\n=== Sample Responses ===", file=log_file)

    sample_inputs = [
        "привет",
        "как дела",
        "что ты думаешь о жизни",
        "расскажи что-нибудь философское"
    ]

    for question in sample_inputs:
        resp = generate_response(model, question, word_to_idx, idx_to_word, device=device)
        print(f"👤 {question} → 🤖 {resp}")
        print(f"Q: {question} → A: {resp}", file=log_file, flush=True)

    log_file.close()


def run_training():
    print("🔄 Собираем новые данные...")
    data_file = collect_new_conversations()

    if not data_file:
        print("ℹ️ Нечего учить — выхожу.")
        return

    print("🔁 Загружаем модель для дообучения...")
    data = joblib.load(data_file)
    vocab_size = data["vocab_size"]

    model = ChatNN(vocab_size=vocab_size, embedding_dim=128, hidden_dim=256, num_layers=2).to(DEVICE)

    if os.path.exists(MODEL_PATH):
        try:
            model.load_state_dict(torch.load(MODEL_PATH, map_location=DEVICE))
            print("✅ Веса загружены")
        except Exception as e:
            print(f"⚠️ Не удалось загрузить веса: {e}")
    else:
        print("🆕 Модель инициализирована с нуля")

    dataset = joblib.load(data_file)
    train_loader, val_loader = get_dataloaders(
        dataset["input_sequences"],
        dataset["target_sequences"],
        batch_size=BATCH_SIZE,
        val_split=0.1
    )

    train(model, train_loader, val_loader, EPOCHS, DEVICE, patience=3)

    torch.save(model.state_dict(), MODEL_PATH)
    joblib.dump({
        "word_to_idx": data["word_to_idx"],
        "idx_to_word": data["idx_to_word"],
        "vocab_size": vocab_size,
        "max_length": MAX_LENGTH,
        "samples": data["samples"]
    }, OLD_DATA_PATH)

    show_sample_responses(model, data["samples"], data["word_to_idx"], data["idx_to_word"], DEVICE)

    print(f"🎉 Модель дообучена и сохранена: {MODEL_PATH}")
    print(f"🥇 Лучшая модель: {MODEL_PATH.replace('.pth', '_best.pth')}")
    print(f"📄 Лог сохранён: {LOG_PATH}")