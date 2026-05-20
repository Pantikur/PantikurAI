# train_logic.py — логика обучения чат-бота
# Поддерживает: data/conversations.json (массив диалогов) + data/training_pairs.jsonl (FAQ)
# Всегда создаёт data/chat_data.pkl

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
OLD_DATA_PATH = os.path.join(DATA_DIR, "chat_data.pkl")          # Сохранение метаданных модели
CONVERSATIONS_JSON = os.path.join(DATA_DIR, "conversations.json") # Один JSON-файл с диалогами
TRAINING_PAIRS_JSONL = os.path.join(DATA_DIR, "training_pairs.jsonl")  # Одна пара на строку
BACKUP_CONVERSATIONS = os.path.join(DATA_DIR, "conversations.old.json")
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
MAX_VOCAB_SIZE = 8000  # ← Новая константа для максимального размера словаря

DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")

os.makedirs("models", exist_ok=True)

# === Информация о устройстве ===
if DEVICE.type == 'cuda':
    print(f"🚀 Используется GPU: {torch.cuda.get_device_name(0)}")
else:
    print("🐌 Используется CPU")


def clean_text(text):
    """Очистка и нормализация текста"""
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


def load_or_initialize_model_data():
    """Загружает старое состояние или возвращает начальное"""
    if os.path.exists(OLD_DATA_PATH):
        try:
            data = joblib.load(OLD_DATA_PATH)
            print(f"✅ Загружено состояние: {len(data.get('samples', []))} пар")
            return data
        except Exception as e:
            print(f"⚠️ Не удалось загрузить chat_data.pkl: {e}")
    print("🆕 Начинаем с чистого листа")
    return {
        "word_to_idx": {"<PAD>": 0, "<UNK>": 1},
        "idx_to_word": {0: "<PAD>", 1: "<UNK>"},
        "vocab_size": 2,
        "max_length": MAX_LENGTH,
        "samples": []
    }


def session_to_context_pairs(session, max_len=MAX_LENGTH):
    """Превращает сессию [u1, b1, u2, b2] → пары [(context+u1→b1), (context+u2→b2)]"""
    pairs = []
    context = []
    for i, msg in enumerate(session):
        if i % 2 == 1 and i > 0:  # Бот отвечает на пользователя
            user_msg = clean_text(session[i-1])
            bot_msg = clean_text(msg)
            full_context = " ".join(context + [user_msg])
            input_text = " ".join(full_context.split()[:max_len])
            pairs.append([input_text, bot_msg])
        context.append(clean_text(msg))
    return pairs


def collect_training_samples():
    """Собирает обучающие пары из всех доступных источников"""
    model_data = load_or_initialize_model_data()
    samples = model_data["samples"].copy()
    word_counter = Counter()

    print(f"До уникализации: {len(samples)} пар")
    seen = set()
    unique_samples = []
    for pair in samples:
        key = tuple(pair)
        if key not in seen:
            seen.add(key)
            unique_samples.append(pair)
    print(f"После уникализации: {len(unique_samples)} пар")

    # Базовые слова для начального словаря
    BASIC_WORDS = [
        "привет", "здравствуй", "пока", "спасибо", "пожалуйста", "извини", "прости",
        "я", "ты", "он", "она", "мы", "вы", "они", "что", "как", "почему", "где",
        "думать", "знать", "понимать", "хотеть", "можно", "нельзя", "надо", "рад",
        "грустно", "весело", "интересно"
    ]
    for word in BASIC_WORDS:
        word_counter[word] += 10

    # Слова из текущего словаря
    for word in model_data["word_to_idx"]:
        if word not in ["<PAD>", "<UNK>"]:
            word_counter[word] += 1

    new_from_conversations = 0
    new_from_knowledge = 0

    # === 1. Диалоги: data/conversations.json ===
    if os.path.exists(CONVERSATIONS_JSON):
        try:
            with open(CONVERSATIONS_JSON, "r", encoding="utf-8") as f:
                raw_data = json.load(f)
                if isinstance(raw_data, list):
                    valid_sessions = [s for s in raw_data if isinstance(s, list) and len(s) >= 2]
                    for session in valid_sessions:
                        cleaned = [clean_text(m) for m in session if m.strip()]
                        if len(cleaned) >= 2:
                            pairs = session_to_context_pairs(cleaned)
                            samples.extend(pairs)
                            new_from_conversations += len(pairs)
                            for user, bot in pairs:
                                word_counter.update(user.split())
                                word_counter.update(bot.split())
                    print(f"✅ Загружено {len(valid_sessions)} сессий из conversations.json")
        except Exception as e:
            print(f"❌ Ошибка чтения conversations.json: {e}")

    # === 2. Знания: data/training_pairs.jsonl ===
    if os.path.exists(TRAINING_PAIRS_JSONL):
        try:
            with open(TRAINING_PAIRS_JSONL, "r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if not line:
                        continue
                    try:
                        entry = json.loads(line)
                        question = entry.get("question", "").strip()
                        answer = entry.get("answer", "").strip()
                        if question and answer:
                            user_msg = clean_text(question)
                            bot_msg = clean_text(answer)
                            samples.append([user_msg, bot_msg])
                            word_counter.update(user_msg.split())
                            word_counter.update(bot_msg.split())
                            new_from_knowledge += 1
                    except json.JSONDecodeError:
                        continue
            print(f"✅ Загружено {new_from_knowledge} знаний из training_pairs.jsonl")
        except Exception as e:
            print(f"❌ Ошибка чтения training_pairs.jsonl: {e}")

    # === Если новых данных нет → всё равно нужен chat_data.pkl ===
    if new_from_conversations == 0 and new_from_knowledge == 0:
        print("ℹ️ Нет новых данных для обучения.")
        return None, model_data

    # Уникализация
    seen = set()
    unique_samples = []
    for pair in samples:
        key = tuple(pair)
        if key not in seen:
            seen.add(key)
            unique_samples.append(pair)

    print(f"📊 Всего уникальных пар: {len(unique_samples)} "
          f"(диалоги: {new_from_conversations}, знания: {new_from_knowledge})")

    # Построение словаря
    old_words = [w for w in model_data["word_to_idx"] if w not in ["<PAD>", "<UNK>"]]
    new_words = [w for w, _ in word_counter.most_common() if w not in old_words]
    vocab_words = ["<PAD>", "<UNK>"] + old_words
    remaining_slots = MAX_VOCAB_SIZE - len(vocab_words)  # ← Исправлено: теперь через константу
    vocab_words.extend(new_words[:remaining_slots])

    word_to_idx = {word: idx for idx, word in enumerate(vocab_words)}
    idx_to_word = {idx: word for idx, word in enumerate(vocab_words)}

    # Кодирование последовательностей
    input_sequences = []
    target_sequences = []
    for user, bot in unique_samples:
        user_seq = [word_to_idx.get(t, 1) for t in user.split()]
        bot_seq = [word_to_idx.get(t, 1) for t in bot.split()]
        user_seq = (user_seq + [0] * MAX_LENGTH)[:MAX_LENGTH]
        bot_seq = (bot_seq + [0] * MAX_LENGTH)[:MAX_LENGTH]
        input_sequences.append(user_seq)
        target_sequences.append(bot_seq)

    # Сохраняем временные данные
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

    # Архивируем исходные файлы
    if os.path.exists(CONVERSATIONS_JSON):
        os.rename(CONVERSATIONS_JSON, BACKUP_CONVERSATIONS)
        print(f"📦 Архивирован: conversations.json")
    if os.path.exists(TRAINING_PAIRS_JSONL):
        os.rename(TRAINING_PAIRS_JSONL, BACKUP_TRAINING)
        print(f"📦 Архивирован: training_pairs.jsonl")

    return TEMP_TRAIN_DATA, model_data


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
        self.lstm = nn.LSTM(embedding_dim, hidden_dim, num_layers, batch_first=True,
                            dropout=0.3 if num_layers > 1 else 0)
        self.fc = nn.Linear(hidden_dim, vocab_size)

    def forward(self, x, hidden=None):
        embedded = self.embedding(x)
        lstm_out, hidden = self.lstm(embedded, hidden)
        logits = self.fc(lstm_out)
        return logits, hidden


def train_model(model, train_loader, val_loader, epochs, device, patience=3):
    criterion = nn.CrossEntropyLoss(ignore_index=0)
    optimizer = optim.Adam(model.parameters(), lr=LEARNING_RATE)

    best_val_loss = float('inf')
    patience_counter = 0

    log_file = open(LOG_PATH, "a", encoding="utf-8")
    log_file.write(f"\n[Training Start] {torch.cuda.get_device_name(0) if torch.cuda.is_available() else 'CPU'} | "
                   f"Epochs={epochs}, Batch={BATCH_SIZE}, LR={LEARNING_RATE}\n")

    for epoch in range(epochs):
        # Train
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

        # Validate
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
        else:
            patience_counter += 1
            if patience_counter >= patience:
                print(f"🛑 Ранняя остановка на эпохе {epoch+1}")
                break

    log_file.close()


def generate_response(model, text, word_to_idx, idx_to_word, max_len=MAX_LENGTH, device='cpu', temperature=0.8):
    model.eval()
    tokens = clean_text(text).split()
    indices = [word_to_idx.get(t, 1) for t in tokens]
    indices = (indices + [0] * MAX_LENGTH)[:MAX_LENGTH]
    input_tensor = torch.tensor([indices], dtype=torch.long).to(device)

    with torch.no_grad():
        output, _ = model(input_tensor)
        logits = output[0]  # (seq_len, vocab_size)

        # Применяем температуру
        logits = logits / temperature

        # Top-k sampling (избегаем редких слов)
        top_k = 50
        top_k_indices = torch.topk(logits, top_k, dim=-1).indices
        filtered_logits = torch.full_like(logits, float('-inf'))
        filtered_logits.scatter_(-1, top_k_indices, logits.gather(-1, top_k_indices))

        # Софтмакс
        probs = torch.softmax(filtered_logits, dim=-1)
        
        # Генерация с запретом повторов
        response_ids = []
        seen_ngrams = set()
        for i in range(max_len):
            if i == 0:
                next_token = torch.argmax(probs[i], dim=-1).item()
            else:
                # Запрещаем повтор последнего токена
                if response_ids[-1] != 0:
                    probs[i][response_ids[-1]] *= 0.1  # штраф за повтор

                # Top-k снова для следующего шага
                top_k_next = torch.topk(probs[i], top_k).indices
                next_probs = probs[i].scatter(-1, top_k_next, probs[i][top_k_next])
                next_probs = torch.softmax(next_probs, dim=-1)
                next_token = torch.multinomial(next_probs, 1).item()

            word = idx_to_word.get(next_token, "<UNK>")
            if word in ["<PAD>", "<UNK>"]:
                continue
            if word in ".!?":
                response_ids.append(next_token)
                break

            # Проверка на триграммы (3 подряд одинаковых слова)
            if len(response_ids) >= 2:
                last_two = (response_ids[-2], response_ids[-1])
                if (last_two, next_token) in seen_ngrams:
                    continue  # пропустим повтор
                seen_ngrams.add((last_two, next_token))

            response_ids.append(next_token)

    response = [idx_to_word[idx] for idx in response_ids if idx not in [0, 1]]
    return " ".join(response).strip()


def show_sample_responses(model, word_to_idx, idx_to_word, device):
    print("\n🔍 Примеры генерации после обучения:")
    sample_inputs = ["привет", "как дела", "что ты думаешь о жизни", "расскажи что-нибудь философское"]
    for q in sample_inputs:
        a = generate_response(model, q, word_to_idx, idx_to_word, device)
        print(f"👤 {q} → 🤖 {a}")


def run_training():
    """Основная функция: сбор данных → обучение → сохранение"""
    print("🔄 Сбор и подготовка обучающих данных...")

    temp_data_path, base_model_data = collect_training_samples()

    # === СЛУЧАЙ 1: Нет новых данных → просто убедиться, что chat_data.pkl существует ===
    if temp_data_path is None:
        print("ℹ️ Новых данных нет. Проверяем наличие chat_data.pkl...")

        if os.path.exists(OLD_DATA_PATH):
            print(f"✅ Модель уже существует: {OLD_DATA_PATH} — ничего не меняем.")
            return

        print("⚠️ Модель отсутствует. Создаём минимальную заглушку...")
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

    # === СЛУЧАЙ 2: Есть данные → обучаем модель ===
    print("🧠 Начинаем дообучение...")

    data = joblib.load(temp_data_path)
    model = ChatNN(
        vocab_size=data["vocab_size"],
        embedding_dim=EMBEDDING_DIM,
        hidden_dim=HIDDEN_DIM,
        num_layers=NUM_LAYERS
    ).to(DEVICE)

    if os.path.exists(MODEL_PATH):
        try:
            model.load_state_dict(torch.load(MODEL_PATH, map_location=DEVICE))
            print("✅ Веса загружены")
        except Exception as e:
            print(f"⚠️ Не удалось загрузить веса: {e}")
    else:
        print("🆕 Модель инициализирована с нуля")

    train_loader, val_loader = get_dataloaders(
        data["input_sequences"],
        data["target_sequences"],
        batch_size=BATCH_SIZE,
        val_split=0.1
    )

    train_model(model, train_loader, val_loader, EPOCHS, DEVICE, patience=3)
    torch.save(model.state_dict(), MODEL_PATH)

    # Сохраняем метаданные модели
    joblib.dump({
        "word_to_idx": data["word_to_idx"],
        "idx_to_word": data["idx_to_word"],
        "vocab_size": data["vocab_size"],
        "max_length": MAX_LENGTH,
        "samples": data["samples"]
    }, OLD_DATA_PATH)

    # Удаляем временный файл
    if os.path.exists(TEMP_TRAIN_DATA):
        os.remove(TEMP_TRAIN_DATA)
        print("🧹 Временные данные удалены")

    show_sample_responses(model, data["word_to_idx"], data["idx_to_word"], DEVICE)

    print(f"🎉 Модель успешно переобучена и сохранена!")
    print(f"📄 Метаданные: {OLD_DATA_PATH}")
    print(f"💾 Веса: {MODEL_PATH}")