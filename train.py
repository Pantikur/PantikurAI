# train.py — обучение Qwen2.5-3B модели

import torch
import torch.nn as nn
from torch.utils.data import Dataset, DataLoader
import joblib
import json
import os
import sys
from collections import Counter
import re
from transformers import AutoTokenizer, AutoModelForCausalLM

# Принудительный UTF-8 для Windows
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

# === Настройки ===
DATA_DIR = "data"
OLD_DATA_PATH = os.path.join(DATA_DIR, "chat_data.pkl")
CONVERSATIONS_JSON = os.path.join(DATA_DIR, "conversations.json")
TRAINING_PAIRS_JSONL = os.path.join(DATA_DIR, "training_pairs.jsonl")
MODEL_PATH = "models/qwen2.5-3b"

MAX_LENGTH = 256
BATCH_SIZE = 16
EPOCHS = 30
EMBEDDING_DIM = 128
HIDDEN_DIM = 512
NUM_LAYERS = 2
LEARNING_RATE = 0.0005
MAX_GRAD_NORM = 1.0  # Gradient clipping для стабильности

os.makedirs("models", exist_ok=True)

# Добавляем путь для импорта
sys.path.append(".")


# === Вспомогательные функции ===
def safe_print(msg: str):
    """Заменяет эмодзи на ASCII, чтобы не падать в Windows console"""
    emojis = {
        '🚀': '[RUN]', '✅': '[OK]', '❌': '[ERR]', '💾': '[SAVE]',
        '📦': '[DATA]', '📚': '[LIB]', '🧠': '[AI]', '🔥': '[FIRE]',
        '🎉': '[HAPPY]', '⚠️': '[WARN]', 'ℹ️': '[INFO]', '❤️': '[HEART]'
    }
    for e, t in emojis.items():
        msg = msg.replace(e, t)
    print(msg, flush=True)


# === ПРОВЕРКА ПАМЯТИ ===
try:
    import psutil
    def check_memory():
        """Проверяет доступную память и возвращает безопасный batch_size."""
        total_gb = psutil.virtual_memory().total / (1024**3)
        available_gb = psutil.virtual_memory().available / (1024**3)
        safe_print(f"[MEM] Система: {total_gb:.1f} ГБ всего, {available_gb:.1f} ГБ свободно")
        
        # Определяем безопасный batch_size
        if available_gb < 4:
            safe_print("[WARN] Мало памяти! Используем минимальный batch_size=1")
            return 1
        elif available_gb < 8:
            safe_print("[INFO] Умеренная память. batch_size=2")
            return 2
        else:
            safe_print("[INFO] Достаточная память. batch_size=4")
            return 4
    BATCH_SIZE = check_memory()
except ImportError:
    safe_print("[WARN] psutil не установлен, используем batch_size=2")
    BATCH_SIZE = 2


# === Настройка устройства (GPU/CPU) ===
if torch.cuda.is_available():
    DEVICE = torch.device("cuda")
    safe_print(f"[🔥] GPU обнаружен: {torch.cuda.get_device_name(0)}")
    safe_print(f"[INFO] Память GPU: {torch.cuda.get_device_properties(0).total_memory / 1024**3:.2f} GB")
else:
    DEVICE = torch.device("cpu")
    safe_print("[INFO] GPU не обнаружен, обучение на CPU")


def clean_text(text):
    if not isinstance(text, str) or not text.strip():
        return ""
    text = text.lower()
    text = re.sub(r'[^а-яёa-z0-9\s?!,.\-:;]', '', text)
    text = re.sub(r'\s+', ' ', text).strip()

    replacements = {
        # Разделённые слова
        "яне": "я не", "тыне": "ты не", "онне": "он не", "она нее": "она не",
        "мыне": "мы не", "выне": "вы не", "онине": "они не",
        "чтобы": "чтобы", "потомучто": "потому что", "вотже": "вот же",
        "нука": "ну ка", "давайка": "давай ка", "подожди": "подожди",
        "ага": "ага", "угу": "угу", "ии": "и", "ещё": "ещё", "конечно": "конечно",
        "блин": "блин", "чёрт": "чёрт", "класс": "класс", "прикольно": "прикольно",
        # Сленг и сокращения
        "незнаю": "не знаю", "не могу": "не могу", "хз": "не знаю",
        "ок": "окей", "спс": "спасибо", "прив": "привет", "пока": "пока",
        "здарова": "здравствуй", "здравствуйте": "здравствуйте",
        "как дела": "как дела", "что делаешь": "что делаешь", "чем занят": "чем занят",
        "извини": "извини", "извиняй": "извини", "сорри": "извини",
        "спасиб": "спасибо", "благодар": "спасибо",
        "да": "да", "нет": "нет", "может": "может быть", "можно": "можно",
        "хорошо": "хорошо", "отлично": "отлично", "замечательно": "замечательно",
        "плохо": "плохо", "грустно": "грустно", "весело": "весело",
        "люблю": "люблю", "нрав": "нравится", "хочу": "хочу", "надо": "надо",
        "нужно": "нужно", "должен": "должен", "могу": "могу", "умею": "умею",
        "думаю": "думаю", "считаю": "считаю", "верю": "верю",
        "знаю": "знаю", "помню": "помню", "забыл": "забыл",
        "понял": "понял", "понимаю": "понимаю", "не понимаю": "не понимаю",
        "скучно": "скучно", "интересно": "интересно", "странно": "странно",
        "важно": "важно", "важное": "важное", "главное": "главное",
        "потом": "потом", "сейчас": "сейчас", "вчера": "вчера", "завтра": "завтра",
        "сегодня": "сегодня", "утро": "утром", "вечер": "вечером", "ночь": "ночью",
        "день": "днём", "всегда": "всегда", "никогда": "никогда", "часто": "часто",
        "редко": "редко", "иногда": "иногда", "вдруг": "вдруг", "вдруг": "вдруг",
        "может быть": "может быть", "возможно": "возможно", "наверное": "наверное",
        "конечно": "конечно", "точно": "точно", "правда": "правда",
        "серьёзно": "серьёзно", "честно": "честно", "искренне": "искренне",
        "рад": "рад", "счастлив": "счастлив", "доволен": "доволен",
        "злюсь": "злюсь", "раздражён": "раздражён", "бесит": "бесит",
        "боюсь": "боюсь", "пугаюсь": "пугаюсь", "тревожусь": "тревожусь",
        "надеюсь": "надеюсь", "жду": "жду", "скучаю": "скучаю",
        "тоскую": "тоскую", "грущу": "грущу", "плачу": "плачу",
        "смеюсь": "смеюсь", "радуюсь": "радуюсь", "люблю": "люблю",
        "уважаю": "уважаю", "доверяю": "доверяю", "ненавижу": "ненавижу",
        "разочарован": "разочарован", "восторжен": "восторжен",
        # Повторяющиеся слова (устранение)
        "очень очень": "очень", "самый самый": "самый",
        "очень очень очень": "очень",
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
            safe_print(f"[OK] Загружено состояние: {len(data['samples'])} пар")
            return data
        except Exception as e:
            safe_print(f"[WARN] Не удалось загрузить {path}: {e}")
    safe_print("[INFO] Начинаем с чистого листа")
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
            safe_print(f"[ERR] Ошибка чтения conversations.json: {e}")

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
                        safe_print(f"[WARN] Пропущена строка в training_pairs.jsonl ({line_num}): {e}")
        except Exception as e:
            safe_print(f"[ERR] Ошибка чтения training_pairs.jsonl: {e}")

    if new_count == 0:
        safe_print("[INFO] Нет новых данных для обучения.")
        return None

    # Уникализация
    seen = set()
    unique_samples = []
    for pair in samples:
        key = tuple(pair)
        if key not in seen:
            seen.add(key)
            unique_samples.append(pair)

    safe_print(f"[DATA] Уникальных пар: {len(unique_samples)} (всего новых: {new_count})")

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
    safe_print(f"[OK] Подготовлено {len(unique_samples)} обучающих пар")
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
    """
    ПРИ РЕТРАИНЕ: не загружаем старые веса — обучаем с нуля.
    Эта функция оставлена для совместимости, но всегда возвращает модель без загрузки.
    """
    safe_print("[INFO] РЕТРАИН: модель инициализирована с нуля (старые веса не загружаются)")
    return model


# === Обучение ===
def train_model(model, dataloader, epochs, device, lr=LEARNING_RATE):
    model.train()
    criterion = nn.CrossEntropyLoss(ignore_index=0)  # игнорируем <PAD>
    optimizer = torch.optim.Adam(model.parameters(), lr=lr, weight_decay=1e-4)  # weight decay для регуляризации
    
    # Cosine annealing scheduler — плавно снижает lr
    scheduler = torch.optim.lr_scheduler.CosineAnnealingLR(optimizer, T_max=epochs, eta_min=1e-6)
    
    # Mixed Precision Training для GPU (ускоряет обучение в 1.5-2x)
    use_amp = device.type == "cuda"
    scaler = torch.cuda.amp.GradScaler() if use_amp else None
    
    best_loss = float('inf')
    
    for epoch in range(epochs):
        total_loss = 0
        for batch in dataloader:
            input_ids = batch["input_ids"].to(device)
            labels = batch["labels"].to(device)
            mask = batch["mask"].to(device)

            optimizer.zero_grad()
            
            if use_amp and scaler is not None:
                # Mixed precision forward pass
                with torch.cuda.amp.autocast():
                    logits = model(input_ids, mask=mask)
                    loss = criterion(logits.view(-1, model.vocab_size), labels.view(-1))
                
                # Mixed precision backward pass
                scaler.scale(loss).backward()
                
                # Gradient clipping — предотвращает взрыв градиентов
                scaler.unscale_(optimizer)
                torch.nn.utils.clip_grad_norm_(model.parameters(), MAX_GRAD_NORM)
                
                scaler.step(optimizer)
                scaler.update()
            else:
                logits = model(input_ids, mask=mask)
                loss = criterion(logits.view(-1, model.vocab_size), labels.view(-1))
                loss.backward()
                
                # Gradient clipping
                torch.nn.utils.clip_grad_norm_(model.parameters(), MAX_GRAD_NORM)
                
                optimizer.step()

            total_loss += loss.item()

        avg_loss = total_loss / len(dataloader)
        scheduler.step()  # Снижаем lr
        
        # Получаем текущий lr
        current_lr = optimizer.param_groups[0]['lr']
        
        gpu_info = f" | GPU: {torch.cuda.memory_allocated() / 1024**2:.0f} MB" if device.type == "cuda" else ""
        
        # Сохраняем лучшую модель
        if avg_loss < best_loss:
            best_loss = avg_loss
            torch.save(model.state_dict(), MODEL_PATH + ".best")
        
        safe_print(f"[INFO] Epoch [{epoch+1}/{epochs}], Loss: {avg_loss:.4f}, LR: {current_lr:.6f}, Best: {best_loss:.4f}{gpu_info}")


# === Главная функция ===
def main():
    safe_print("[DATA] Сбор и подготовка данных...")
    data_file = collect_training_samples()

    if data_file is None:
        safe_print("[INFO] Нет новых данных. Создаём минимальную модель...")

        fallback_data = {
            "word_to_idx": {"<PAD>": 0, "<UNK>": 1, "<EOS>": 2, "привет": 3, "пока": 4},
            "idx_to_word": {0: "<PAD>", 1: "<UNK>", 2: "<EOS>", 3: "привет", 4: "пока"},
            "vocab_size": 5,
            "max_length": MAX_LENGTH,
            "samples": [["привет", "здравствуй"], ["пока", "до свидания"]]
        }
        joblib.dump(fallback_data, OLD_DATA_PATH)
        safe_print(f"[OK] Заглушка создана: {OLD_DATA_PATH}")
        return

    # Загружаем данные
    temp_data = joblib.load(data_file)

    # Загружаем Qwen2.5-3B — сначала локальную, потом fallback на HuggingFace
    safe_print("[AI] Загрузка Qwen2.5-3B для дообучения...")
    safe_print(f"[AI] Путь к модели: {MODEL_PATH}")
    
    import torch
    
    # Сначала пробуем локальную модель
    if os.path.isdir(MODEL_PATH) and os.listdir(MODEL_PATH):
        safe_print(f"[LOCAL] Загружаем из {MODEL_PATH}")
        try:
            tokenizer = AutoTokenizer.from_pretrained(MODEL_PATH)
            model = AutoModelForCausalLM.from_pretrained(MODEL_PATH, torch_dtype=torch.float16)
            safe_print("[OK] Загружена локальная модель")
        except Exception as e:
            safe_print(f"[WARN] Локальная модель не загрузилась: {e}")
            safe_print("[HF] Fallback на HuggingFace...")
            tokenizer = AutoTokenizer.from_pretrained("Qwen/Qwen2.5-3B-Instruct")
            model = AutoModelForCausalLM.from_pretrained("Qwen/Qwen2.5-3B-Instruct", torch_dtype=torch.float16)
    else:
        safe_print("[HF] Локальная модель не найдена, загружаем с HuggingFace...")
        tokenizer = AutoTokenizer.from_pretrained("Qwen/Qwen2.5-3B-Instruct")
        model = AutoModelForCausalLM.from_pretrained("Qwen/Qwen2.5-3B-Instruct", torch_dtype=torch.float16)

    # Pad token
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token

    safe_print("[FIRE] РЕТРАИН: дообучение Qwen2.5-3B на всех данных")

    # Формируем тексты из данных — ИСПРАВЛЕНО: поддерживаем list, dict, str
    texts = []
    if "samples" in temp_data:
        for sample in temp_data["samples"]:
            if isinstance(sample, list) and len(sample) >= 2:
                # Формат [user, bot] — основной формат из collect_training_samples
                user_text = str(sample[0]).strip()
                bot_text = str(sample[1]).strip()
                if user_text and bot_text:
                    texts.append(f"Пользователь: {user_text}\nАссистент: {bot_text}{tokenizer.eos_token}")
            elif isinstance(sample, dict):
                t = sample.get("text", sample.get("prompt", ""))
                if t:
                    texts.append(str(t).strip())
            elif isinstance(sample, str):
                if sample.strip():
                    texts.append(sample.strip())

    texts = [t for t in texts if t and len(t) > 5]

    if not texts:
        safe_print("[WARN] Нет текстов для дообучения — сохраняем базовую модель")
        texts = ["Пользователь: Привет!\nАссистент: Здравствуй!" + tokenizer.eos_token]

    safe_print(f"[DATA] Формируем датасет: {len(texts)} текстов")

    # Правильная токенизация: каждый текст отдельно, с truncation
    from torch.utils.data import DataLoader, TensorDataset
    import torch

    block_size = 256  # Максимальная длина последовательности
    all_input_ids = []

    for text in texts:
        enc = tokenizer(text, truncation=True, max_length=block_size, return_tensors="pt")
        all_input_ids.append(enc["input_ids"].squeeze(0))

    # Склеиваем все токены в один длинный массив и нарезаем на блоки
    cat_ids = torch.cat(all_input_ids, dim=0)
    safe_print(f"[DATA] Всего токенов: {len(cat_ids)}")

    # Нарезаем на блоки фиксированной длины
    blocks = []
    for i in range(0, len(cat_ids) - block_size, block_size):
        blocks.append(cat_ids[i:i + block_size])

    if not blocks:
        # Если данных очень мало — дублируем
        chunk = cat_ids[:block_size]
        if len(chunk) < block_size:
            pad_len = block_size - len(chunk)
            chunk = torch.cat([chunk, torch.full((pad_len,), tokenizer.pad_token_id, dtype=chunk.dtype)])
        blocks = [chunk]

    input_ids = torch.stack(blocks)
    safe_print(f"[DATA] Блоков для обучения: {len(blocks)} (размер: {block_size} токенов)")

    dataset = TensorDataset(input_ids)
    dataloader = DataLoader(dataset, batch_size=BATCH_SIZE, shuffle=True)

    # Оптимизатор с scheduler
    optimizer = torch.optim.AdamW(model.parameters(), lr=5e-5, weight_decay=0.01)
    scheduler = torch.optim.lr_scheduler.CosineAnnealingLR(optimizer, T_max=3 * len(dataloader))

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    safe_print(f"[INFO] Устройство: {device}")
    model = model.to(device)
    model.train()

    num_epochs = 3
    safe_print(f"[RUN] Начало дообучения ({num_epochs} эпох)...")

    for epoch in range(num_epochs):
        total_loss = 0
        num_batches = 0
        for (batch_input,) in dataloader:
            batch_input = batch_input.to(device)
            attention_mask = torch.ones_like(batch_input)
            labels = batch_input.clone()

            optimizer.zero_grad()
            outputs = model(input_ids=batch_input, attention_mask=attention_mask, labels=labels)
            loss = outputs.loss
            loss.backward()
            torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0)
            optimizer.step()
            scheduler.step()

            total_loss += loss.item()
            num_batches += 1

        avg_loss = total_loss / max(num_batches, 1)
        gpu_info = f" | GPU: {torch.cuda.memory_allocated() / 1024**2:.0f} MB" if device.type == "cuda" else ""
        safe_print(f"[INFO] Эпоха {epoch+1}/{num_epochs}, Loss: {avg_loss:.4f}{gpu_info}")

    # Сохраняем Qwen2.5-3B
    os.makedirs(MODEL_PATH, exist_ok=True)
    model.save_pretrained(MODEL_PATH)
    tokenizer.save_pretrained(MODEL_PATH)

    safe_print("[HAPPY] Qwen2.5-3B успешно дообучена и сохранена!")
    safe_print(f"[SAVE] Модель: {MODEL_PATH}")
    safe_print(f"[DATA] Обучено на {len(texts)} текстах, {len(cat_ids)} токенов")


if __name__ == "__main__":
    main()