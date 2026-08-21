# inference.py — интерактивный режим с классификацией тем

import torch
import joblib
import json
import re
import os
from collections import Counter

# === Настройки ===
MODEL_PATH = "models/qwen2.5-3b"
DATA_PATH = "data/chat_data.pkl"

MAX_LENGTH = 64
DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")

# Загружаем данные
if not os.path.exists(MODEL_PATH):
    print("❌ Модель не найдена. Сначала запустите train.py или retrain.py")
    exit()

if not os.path.exists(DATA_PATH):
    print("❌ Данные не найдены. Нет word_to_idx / idx_to_word")
    exit()

data = joblib.load(DATA_PATH)
word_to_idx = data["word_to_idx"]
idx_to_word = data["idx_to_word"]

vocab_size = data["vocab_size"]


# === Модель (должна совпадать с train.py и retrain.py) ===
class ChatModel(torch.nn.Module):
    def __init__(self, vocab_size, embedding_dim=128, hidden_dim=256, num_layers=2):
        super(ChatModel, self).__init__()
        self.embedding = torch.nn.Embedding(vocab_size, embedding_dim, padding_idx=0)
        self.lstm = torch.nn.LSTM(
            embedding_dim,
            hidden_dim,
            num_layers,
            batch_first=True,
            dropout=0.3 if num_layers > 1 else 0
        )
        self.fc = torch.nn.Linear(hidden_dim, vocab_size)

    def forward(self, input_ids, hidden=None):
        x = self.embedding(input_ids)
        out, hidden = self.lstm(x, hidden)
        logits = self.fc(out)
        return logits, hidden


# === Токенизация ===
def tokenize(text):
    text = re.sub(r'[^а-яА-Яa-zA-Z0-9\s]', '', text.lower())
    text = re.sub(r'\s+', ' ', text).strip()
    text = text.replace("яне", "я не").replace("тыже", "ты же").replace("чтобы", "чтобы ")
    return text.split()


# === Кодирование текста ===
def encode_text(text, word_to_idx):
    tokens = tokenize(text)
    seq = [word_to_idx.get(t, 1) for t in tokens]  # 1 = <UNK>
    seq = (seq + [0] * MAX_LENGTH)[:MAX_LENGTH]    # 0 = <PAD>
    return torch.tensor([seq], dtype=torch.long).to(DEVICE)


# === Декодирование ответа с использованием improved sampling ===
def decode_output(input_tensor, model, temperature=0.75, max_length=50, top_p=0.92):
    """
    Улучшенная генерация с:
    - Nucleus sampling (top_p)
    - Repetition penalty
    - Special token handling
    """
    model.eval()
    
    bos_token = word_to_idx["<BOS>"]
    eos_token = word_to_idx["<EOS>"]
    
    input_ids = torch.tensor([[bos_token]], dtype=torch.long).to(DEVICE)
    
    words = []
    generated_ids = []
    seen_words = Counter()
    
    with torch.no_grad():
        for step in range(max_length):
            logits, _ = model(input_ids)
            
            # Берём последний токен
            logits = logits[:, -1, :] / temperature
            
            # Nucleus sampling
            sorted_logits, sorted_indices = torch.sort(logits, descending=True)
            cumulative_probs = torch.softmax(sorted_logits, dim=-1).cumsum(dim=-1)
            
            sorted_indices_to_remove = cumulative_probs > top_p
            sorted_indices_to_remove[..., 1:] = sorted_indices_to_remove[..., :-1].clone()
            sorted_indices_to_remove[..., 0] = 0
            indices_to_remove = sorted_indices[sorted_indices_to_remove]
            logits[0, indices_to_remove] = float('-inf')
            
            probs = torch.softmax(logits, dim=-1)
            
            # Repetition penalty — штраф за повторяющиеся слова
            if len(generated_ids) > 3:
                for token_id in generated_ids[-10:]:
                    word = idx_to_word.get(token_id.item(), "")
                    if word and word not in [".", "!", "?", ",", ";", ":", "-", "—"]:
                        seen_words[word] += 1
                        if seen_words[word] > 1:
                            # Штраф за повторение
                            penalty = 0.5 ** seen_words[word]
                            probs[0, token_id] *= penalty
            
            # Исключаем <PAD> и <UNK>
            probs[0, 0] = 0  # <PAD>
            probs[0, 1] = 0  # <UNK>
            
            # Нормализуем
            probs = probs / probs.sum()
            
            next_token = torch.multinomial(probs, 1).item()
            
            if next_token == eos_token:
                break
                
            word = idx_to_word.get(next_token, "<UNK>")
            
            if word not in ["<PAD>", "<UNK>", "<EOS>"]:
                generated_ids.append(next_token)
                seen_words[word] += 1
                
                if len(words) == 0:
                    words.append(word.capitalize())
                else:
                    if word in [".", "!", "?"]:
                        words.append(word)
                        break
                    elif word in [",", ";", ":"]:
                        if len(words) > 0 and words[-1][-1] not in [" ", "\t"]:
                            words.append(word)
                        else:
                            words.append(word)
                    else:
                        words.append(word)
            
            input_ids = torch.tensor([[next_token]], dtype=torch.long).to(DEVICE)
    
    response = " ".join(words).strip()
    
    # Убедимся, что предложение заканчивается знаком препинания
    if response and response[-1] not in [".", "!", "?"]:
        response += "."
        
    return response


# === Классификация темы (улучшенная) ===
def classify_topic(text):
    """
    Улучшенная классификация с n-gram matching и весовыми коэффициентами.
    """
    text_lower = text.lower()

    # Генерация n-грамм
    words = text_lower.split()
    bigrams = [" ".join(words[i:i+2]) for i in range(len(words)-1)]
    trigrams = [" ".join(words[i:i+3]) for i in range(len(words)-2)]
    all_ngrams = set(words + bigrams + trigrams)

    # Категории с весами (многословные фразы имеют больший вес)
    categories = {
        "everyday": {
            "words": {"привет", "пока", "дела", "погода", "работа", "учёба", "планы",
                     "фильм", "книга", "еда", "спорт", "город", "улица", "магазин",
                     "обычный", "жизнь", "день", "вечер", "утро", "дом", "семья",
                     "друзья", "вечеринка", "отдых", "прогулка", "покупки", "готовка"},
            "phrases": {"как дела", "что делаешь", "чем занят", "иду на работу",
                       "был в магазине", "смотрю фильм", "читаю книгу", "за учебой",
                       "на перерыве", "по дороге домой", "как ты", "в порядке",
                       "ничего особенного", "обычный день", "всё как всегда",
                       "хороший день", "плохой день", "выходной", "праздник"}
        },
        "love": {
            "words": {"одиноко", "пустота", "смысл", "цель", "потерял", "страшно", "боюсь",
                     "верить", "надеюсь", "любовь", "сердце", "душ", "боль", "устал",
                     "слёзы", "поддержка", "доверяю", "рассказать", "единственный",
                     "чувствую", "близость", "воспоминание", "эхо", "тень", "забвение",
                     "скучаю", "тоскую", "грущу", "жду", "жду тебя"},
            "phrases": {"я люблю", "ты мне нужен", "мне одиноко", "нет смысла",
                       "потерял цель", "страшно жить", "боюсь будущего",
                       "надеюсь на лучшее", "поддержи меня", "доверяю только тебе",
                       "единственный на свете", "близость с тобой", "воспоминания о тебе",
                       "скучаю по тебе", "хочу тебя", "ты мой"}
        },
        "intimate": {
            "words": {"минет", "отсос", "смазка", "сперма", "сосать", "отсосать", "член",
                     "секс", "сексуально", "сексуальный", "куни", "кунилингус", "киска",
                     "моя киска", "твоя киска", "лизать", "вылизывать", "облизывать",
                     "клитор", "бугорок", "сок", "мои соки", "её соки", "в киску",
                     "внутрь", "жопка", "попка", "анус", "задняя щель"},
            "phrases": {"смазка из кончика", "взять член полностью", "возьми член",
                       "кончил внутрь", "дерёт в киску", "двигает бёдрами", "трахает",
                       "ласкает", "ускоряет темп", "меняет интенсивность",
                       "интенсивность движений", "сок из киски", "текут из киски"}
        },
        "aggressive": {
            "words": {"убью", "ненавижу", "умри", "режь", "кровь", "боль", "насилие",
                     "битва", "война", "убить", "убей", "убейте", "кишки", "злюсь",
                     "бешу", "ярость", "гнев", "раздражён", "бесит", "достало"},
            "phrases": {"убью тебя", "ненавижу тебя", "умри сейчас", "режь на куски",
                       "прольётся кровь", "будет больно", "идёт битва", "начинается война",
                       "убей его", "довольно", "достало", "злюсь"}
        },
        "fantasy": {
            "words": {"магия", "заклинание", "колдун", "ведьма", "дракон", "эльф", "гном",
                     "орк", "гоблин", "трулль", "рыцарь", "принцесса", "замок", "подземелье",
                     "сокровище", "меч", "щит", "лук", "лечение", "огонь", "лед", "молния",
                     "темнота", "свет", "зелье", "свиток", "амулет", "артефакт", "портал",
                     "телепортация", "проклятие", "чакра", "нинзя", "шиноби", "каге",
                     "хокаге", "дзюцу", "тейдзюцу", "ниндзюцу", "тайдзюцу", "гендзюцу",
                     "расенган", "чидори", "шаринган", "мудрец", "биджу", "хвостатый"},
            "phrases": {"заклинание огня", "магия льда", "молнии с небес", "темная магия",
                       "светлая магия", "древнее заклинание", "тайное заклинание",
                       "пламя дракона", "огненный дракон", "ледяной дракон",
                       "эльфийская стрела", "гномья кузня", "орочья ярость",
                       "пещера гоблинов", "рыцарский турнир", "спасение принцессы",
                       "управление чакрой", "поток чакры", "уровень чакры",
                       "режим сенна", "режим мудреца", "активация шарингана"}
        }
    }
    
    scores = {}
    for category, data in categories.items():
        # Считаем совпадения слов (вес 1)
        word_matches = sum(1 for w in data["words"] if w in words)
        # Считаем совпадения фраз (вес 3 — фразы важнее)
        phrase_matches = sum(1 for p in data["phrases"] if p in all_ngrams)
        
        scores[category] = word_matches + phrase_matches * 3
    
    # Определяем доминирующую тему
    max_score = max(scores.values())
    
    if max_score == 0:
        return "neutral"
    
    # Находим категорию с максимальным скором
    best_category = max(scores.keys(), key=lambda k: scores[k])
    
    # Если лучший скор слишком мал (< 2), считаем за neutral
    if max_score < 2:
        return "neutral"
    
    return best_category


# === Загрузка модели ===
model = ChatModel(
    vocab_size=vocab_size,
    embedding_dim=128,
    hidden_dim=256,
    num_layers=2
).to(DEVICE)

try:
    model.load_state_dict(torch.load(MODEL_PATH, map_location=DEVICE))
    print("✅ Модель загружена")
except Exception as e:
    print(f"❌ Ошибка загрузки модели: {e}")
    exit()


# === Главный цикл чата ===
print("\n💬 Привет! Я — ваш бот. Напишите что-нибудь или 'выход', чтобы закончить.\n")

hidden = None
while True:
    user_input = input("Вы: ").strip()
    if not user_input:
        continue
    if user_input.lower() in ["выход", "exit", "quit"]:
        print("Пока! 👋")
        break

    # Классификация темы
    topic = classify_topic(user_input)
    print(f"[Тема: {topic}]")

    # Кодируем ввод
    input_tensor = encode_text(user_input, word_to_idx)

    # Получаем ответ с использованием новой функции генерации
    try:
        response = decode_output(input_tensor, model)
    except Exception as e:
        print(f"❌ Ошибка генерации ответа: {e}")
        response = "Я слушаю..."

    print(f"Бот: {response}")