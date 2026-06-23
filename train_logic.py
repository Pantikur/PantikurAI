# train_logic.py — логика обучения чат-бота (обновлённая)
# Поддерживает: data/conversations.json + data/training_pairs.jsonl
# Всегда создаёт data/chat_data.pkl

import torch
import torch.nn as nn
from torch.utils.data import Dataset, DataLoader
import joblib
import json
import os
import re
import random
from collections import Counter
from tqdm import tqdm

# === Настройки ===
DATA_DIR = "data"
OLD_DATA_PATH = os.path.join(DATA_DIR, "chat_data.pkl")
CONVERSATIONS_JSON = os.path.join(DATA_DIR, "conversations.json")
TRAINING_PAIRS_JSONL = os.path.join(DATA_DIR, "training_pairs.jsonl")
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
MAX_VOCAB_SIZE = 8000

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
        "word_to_idx": {"<PAD>": 0, "<UNK>": 1, "<EOS>": 2},
        "idx_to_word": {0: "<PAD>", 1: "<UNK>", 2: "<EOS>"},
        "vocab_size": 3,
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
        if len(context) > 6:  # Ограничиваем длину контекста
            context = context[-6:]
    return pairs


def collect_training_samples():
    """Собирает обучающие пары из всех доступных источников"""
    model_data = load_or_initialize_model_data()
    samples = model_data["samples"].copy()
    word_counter = Counter()

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
        if word not in ["<PAD>", "<UNK>", "<EOS>"]:
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

    # Если новых данных нет
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
    old_words = [w for w in model_data["word_to_idx"] if w not in ["<PAD>", "<UNK>", "<EOS>"]]
    new_words = [w for w, _ in word_counter.most_common() if w not in old_words]
    vocab_words = ["<PAD>", "<UNK>", "<EOS>"] + old_words
    remaining_slots = MAX_VOCAB_SIZE - len(vocab_words)
    vocab_words.extend(new_words[:remaining_slots])

    word_to_idx = {word: idx for idx, word in enumerate(vocab_words)}
    idx_to_word = {idx: word for idx, word in enumerate(vocab_words)}

    # Кодирование последовательностей
    input_sequences = []
    target_sequences = []

    def pad_seq(seq, max_len=MAX_LENGTH):
        if len(seq) >= max_len:
            return seq[:max_len-1] + [seq[-1]]  # Сохраняем последний токен (например, <EOS>)
        return (seq + [0] * max_len)[:max_len]

    for user, bot in unique_samples:
        user_seq = [word_to_idx.get(t, 1) for t in user.split()]
        bot_seq = [word_to_idx.get(t, 1) for t in bot.split()] + [word_to_idx["<EOS>"]]  # Добавляем <EOS>
        input_sequences.append(pad_seq(user_seq))
        target_sequences.append(pad_seq(bot_seq))

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
        if os.path.exists(BACKUP_CONVERSATIONS):
            os.remove(BACKUP_CONVERSATIONS)  # Удаляем старый бэкап
        os.rename(CONVERSATIONS_JSON, BACKUP_CONVERSATIONS)
        print(f"📦 Архивирован: conversations.json")

    if os.path.exists(TRAINING_PAIRS_JSONL):
        if os.path.exists(BACKUP_TRAINING):
            os.remove(BACKUP_TRAINING)  # Удаляем старый бэкап
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
        input_ids = self.input_ids[idx]
        labels = self.labels[idx]
        mask = (torch.tensor(input_ids) != 0).float()  # Маска: 1 если не <PAD>
        return {
            "input_ids": torch.tensor(input_ids, dtype=torch.long),
            "labels": torch.tensor(labels, dtype=torch.long),
            "mask": mask
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


# Импортируем модель из Wuglarst
try:
    from Wuglarst.src.chat_model import ChatNN
except ImportError:
    raise RuntimeError("❌ Не удалось импортировать ChatNN из Wuglarst/src/chat_model.py")


def train_model(model, train_loader, val_loader, epochs, device, patience=3):
    criterion = nn.CrossEntropyLoss(ignore_index=0)  # игнорируем <PAD>
    optimizer = torch.optim.Adam(model.parameters(), lr=LEARNING_RATE)

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
            mask = batch["mask"].to(device)

            optimizer.zero_grad()
            logits = model(input_ids, mask=mask)  # Теперь принимает mask
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
                mask = batch["mask"].to(device)
                logits = model(input_ids, mask=mask)
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


def generate_response(model, text, word_to_idx, idx_to_word, max_len=MAX_LENGTH, device='cpu', temperature=0.8, top_p=0.9):
    """Генерация ответа с nucleus sampling"""
    model.eval()
    tokens = clean_text(text).split()
    indices = [word_to_idx.get(t, 1) for t in tokens]
    indices = (indices + [0] * MAX_LENGTH)[:MAX_LENGTH]
    input_tensor = torch.tensor([indices], dtype=torch.long).to(device)

    eos_token_id = word_to_idx.get("<EOS>", 2)

    with torch.no_grad():
        response_ids = []
        current_input = input_tensor

        for _ in range(max_len):
            # Получаем логиты
            logits = model(current_input)[:, -1, :]  # (1, vocab_size)
            logits = logits / temperature

            # Фильтрация по top_p (nucleus sampling)
            sorted_logits, sorted_indices = torch.sort(logits, descending=True)
            cumulative_probs = torch.cumsum(torch.softmax(sorted_logits, dim=-1), dim=-1)
            sorted_indices_to_remove = cumulative_probs > top_p
            sorted_indices_to_remove[..., 1:] = sorted_indices_to_remove[..., :-1].clone()
            sorted_indices_to_remove[..., 0] = 0
            indices_to_remove = sorted_indices[sorted_indices_to_remove]
            logits[0, indices_to_remove] = float('-inf')

            # Софтмакс и выбор
            probs = torch.softmax(logits, dim=-1)
            next_token = torch.multinomial(probs, 1).item()

            if next_token == eos_token_id:
                break
            if next_token not in [0, 1]:  # не <PAD>, <UNK>
                response_ids.append(next_token)

            # Обновляем вход
            new_input = torch.cat([
                current_input,
                torch.tensor([[next_token]], device=device)
            ], dim=1)
            current_input = new_input[:, -MAX_LENGTH:]  # ограничиваем длину

    response = " ".join([idx_to_word.get(idx, "<UNK>") for idx in response_ids])
    return response.strip()


def show_sample_responses(model, word_to_idx, idx_to_word, device):
    print("\n🔍 Примеры генерации после обучения:")
    sample_inputs = ["привет", "как дела", "расскажи историю", "что такое любовь"]
    for q in sample_inputs:
        a = generate_response(
            model=model,
            text=q,
            word_to_idx=word_to_idx,
            idx_to_word=idx_to_word,
            device=device,
            temperature=0.8,
            top_p=0.9
        )
        print(f"👤 {q} → 🤖 {a}")


def run_training():
    """Основная функция: сбор данных → обучение → сохранение"""
    print("🔄 Сбор и подготовка обучающих данных...")

    temp_data_path, base_model_data = collect_training_samples()

    # === СЛУЧАЙ 1: Нет новых данных, но есть старая модель → Экспортируем tokenizer.json ===
    if temp_data_path is None:
        print("ℹ️ Новых данных нет. Проверяем существующую модель для экспорта...")

        if os.path.exists(OLD_DATA_PATH):
            try:
                data = joblib.load(OLD_DATA_PATH)
                print(f"✅ Загружены метаданные: {len(data.get('samples', []))} пар")

                # === ВОССТАНОВЛЕНИЕ СЛОВАРЯ, ЕСЛИ ПОВРЕЖДЁН ===
                if "word_to_idx" not in data or "<EOS>" not in data["word_to_idx"]:
                    print("⚠️ Обнаружен повреждённый словарь. Восстанавливаем...")
                    vocab = {"<PAD>": 0, "<UNK>": 1, "<EOS>": 2}
                    idx_to_word = {0: "<PAD>", 1: "<UNK>", 2: "<EOS>"}
                    idx = 3
                    # Восстанавливаем из пар
                    for inp, tgt in data.get("samples", []):
                        for word in clean_text(inp).split() + clean_text(tgt).split():
                            if word not in vocab:
                                vocab[word] = idx
                                idx_to_word[idx] = word
                                idx += 1
                                if idx >= MAX_VOCAB_SIZE:
                                    break
                    data["word_to_idx"] = vocab
                    data["idx_to_word"] = idx_to_word
                    data["vocab_size"] = len(vocab)
                    joblib.dump(data, OLD_DATA_PATH)
                    print(f"🔧 Словарь восстановлен и сохранён: vocab_size={len(vocab)}")
            except Exception as e:
                print(f"❌ Ошибка загрузки chat_data.pkl: {e}")
                return
        else:
            print("⚠️ Модель отсутствует. Создаём минимальную заглушку...")
            data = {
                "word_to_idx": {"<PAD>": 0, "<UNK>": 1, "<EOS>": 2, "привет": 3, "пока": 4},
                "idx_to_word": {0: "<PAD>", 1: "<UNK>", 2: "<EOS>", 3: "привет", 4: "пока"},
                "vocab_size": 5,
                "max_length": MAX_LENGTH,
                "samples": [["привет", "здравствуй"], ["пока", "до свидания"]]
            }
            os.makedirs("data", exist_ok=True)
            joblib.dump(data, OLD_DATA_PATH)
            print(f"🟢 Заглушка создана: {OLD_DATA_PATH}")

        # === ЭКСПОРТ tokenizer.json ===
        tokenizer_data = {
            "vocab": data["word_to_idx"],
            "inverse_vocab": {str(idx): word for idx, word in data["idx_to_word"].items()}
        }
        os.makedirs("data", exist_ok=True)
        with open("data/tokenizer.json", "w", encoding="utf-8") as f:
            json.dump(tokenizer_data, f, ensure_ascii=False, indent=2)
        print("✅ Экспортирован: data/tokenizer.json")

        # === Убедимся, что chat_model.pth существует ===
        model_path = MODEL_PATH
        if not os.path.exists(model_path):
            print("⚠️ Файл модели не найден. Создаём пустую модель...")
            model = ChatNN(
                vocab_size=data["vocab_size"],
                embedding_dim=EMBEDDING_DIM,
                hidden_dim=HIDDEN_DIM,
                num_layers=NUM_LAYERS,
                max_length=MAX_LENGTH,
                pad_token_id=0,
                eos_token_id=data["word_to_idx"]["<EOS>"]
            )
            os.makedirs("models", exist_ok=True)
            torch.save(model.state_dict(), model_path)
            print(f"✅ Создан: {model_path}")
        else:
            print(f"✅ Модель уже существует: {model_path}")

        return  # Завершаем — ничего не учим, но файлы созданы

    # === СЛУЧАЙ 2: Есть новые данные → обучаем модель с нуля ===
    print("🔥 Начинаем ретраин (обучение с нуля)...")

    data = joblib.load(temp_data_path)
    model = ChatNN(
        vocab_size=data["vocab_size"],
        embedding_dim=EMBEDDING_DIM,
        hidden_dim=HIDDEN_DIM,
        num_layers=NUM_LAYERS,
        max_length=MAX_LENGTH,
        pad_token_id=0,
        eos_token_id=data["word_to_idx"]["<EOS>"]
    ).to(DEVICE)

    # ПРИ РЕТРАИНЕ: не загружаем старые веса — обучаем с нуля
    print("🆕 Модель инициализирована с нуля (ретраин)")

    train_loader, val_loader = get_dataloaders(
        data["input_sequences"],
        data["target_sequences"],
        batch_size=BATCH_SIZE,
        val_split=0.1
    )

    train_model(model, train_loader, val_loader, EPOCHS, DEVICE, patience=3)

    # === Сохраняем в нужном формате ===
    torch.save(model.state_dict(), MODEL_PATH)
    print(f"✅ Модель сохранена: {MODEL_PATH}")

    # Сохраняем метаданные
    joblib.dump({
        "word_to_idx": data["word_to_idx"],
        "idx_to_word": data["idx_to_word"],
        "vocab_size": data["vocab_size"],
        "max_length": MAX_LENGTH,
        "samples": data["samples"]
    }, OLD_DATA_PATH)
    print(f"✅ Метаданные обновлены: {OLD_DATA_PATH}")

    # === Экспорт tokenizer.json ===
    tokenizer_data = {
        "vocab": data["word_to_idx"],
        "inverse_vocab": {str(idx): word for idx, word in data["idx_to_word"].items()}
    }
    with open("data/tokenizer.json", "w", encoding="utf-8") as f:
        json.dump(tokenizer_data, f, ensure_ascii=False, indent=2)
    print("✅ Экспортирован: data/tokenizer.json")

    # Удаляем временный файл
    if os.path.exists(TEMP_TRAIN_DATA):
        os.remove(TEMP_TRAIN_DATA)
        print("🧹 Временные данные удалены")

    show_sample_responses(model, data["word_to_idx"], data["idx_to_word"], DEVICE)

    print(f"🎉 Модель успешно переобучена с нуля и сохранена!")


# === ТОЧКА ВХОДА ===
if __name__ == "__main__":
    print("🚀 Запуск обучения...")
    try:
        run_training()
        print("✅ Обучение завершено!")
    except Exception as e:
        print(f"❌ Ошибка при обучении: {e}")
        raise