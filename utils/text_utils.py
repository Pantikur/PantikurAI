# utils.py
import os
import re
import joblib
import torch
from collections import Counter

# === Очистка текста ===
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


# === Токенизация ===
def tokenize(text):
    return clean_text(text).split()


# === Загрузка модели ===
def load_model_state(model, model_path, device):
    if os.path.exists(model_path):
        try:
            model.load_state_dict(torch.load(model_path, map_location=device))
            print("✅ Веса загружены")
        except Exception as e:
            print(f"❌ Ошибка загрузки весов: {e}")
    else:
        print("🆕 Модель инициализирована с нуля")
    return model


# === Загрузка старого состояния ===
def load_or_initialize_data(data_path):
    if os.path.exists(data_path):
        data = joblib.load(data_path)
        print(f"✅ Загружено состояние: {len(data['samples'])} пар")

        if "<BOS>" not in data["word_to_idx"]:
            idx = len(data["word_to_idx"])
            data["word_to_idx"]["<BOS>"] = idx
            data["idx_to_word"][idx] = "<BOS>"

        if "<EOS>" not in data["word_to_idx"]:
            idx = len(data["word_to_idx"])
            data["word_to_idx"]["<EOS>"] = idx
            data["idx_to_word"][idx] = "<EOS>"

        data["vocab_size"] = len(data["word_to_idx"])
        return data
    else:
        print("🆕 Начинаем с чистого листа")
        return {
            "word_to_idx": {"<PAD>": 0, "<UNK>": 1, "<BOS>": 2, "<EOS>": 3},
            "idx_to_word": {0: "<PAD>", 1: "<UNK>", 2: "<BOS>", 3: "<EOS>"},
            "vocab_size": 4,
            "max_length": 64,
            "samples": []
        }


# === Построение словаря ===
def build_vocab_from_samples(samples, old_word_to_idx, max_size=8000):
    counter = Counter()
    for user, bot in samples:
        counter.update(tokenize(user))
        counter.update(tokenize(bot))

    word_to_idx = old_word_to_idx.copy()
    idx_to_word = {idx: word for word, idx in word_to_idx.items()}

    for word, _ in counter.most_common():
        if word not in word_to_idx and len(word_to_idx) < max_size:
            idx = len(word_to_idx)
            word_to_idx[word] = idx
            idx_to_word[idx] = word

    print(f"✅ Словарь обновлён: {len(word_to_idx)} слов")
    return word_to_idx, idx_to_word