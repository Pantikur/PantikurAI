# inference.py — интерактивный режим с классификацией тем

import torch
import joblib
import json
import re
import os

# === Настройки ===
MODEL_PATH = "models/chat_model.pth"
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


# === Декодирование ответа с использованием sampling и специальных токенов ===
def decode_output(input_tensor, model, temperature=0.7, max_length=50):
    """
    Генерация текста с использованием sampling с температурой
    и специальных токенов <BOS> и <EOS>
    """
    model.eval()
    
    # Получаем специальные токены
    bos_token = word_to_idx["<BOS>"]
    eos_token = word_to_idx["<EOS>"]
    
    # Начинаем генерацию с токена <BOS>
    input_ids = torch.tensor([[bos_token]], dtype=torch.long).to(DEVICE)
    hidden = None
    
    words = []
    
    with torch.no_grad():
        for _ in range(max_length):
            # Получаем логиты для текущего токена
            logits, hidden = model(input_ids, hidden)
            
            # Берем только последний токен
            logits = logits[:, -1, :] / temperature
            
            # Применяем softmax для получения вероятностей
            probabilities = torch.nn.functional.softmax(logits, dim=-1)
            
            # Исключаем <PAD> и <UNK> из генерации
            probabilities[0, 0] = 0  # <PAD>
            probabilities[0, 1] = 0  # <UNK>
            
            # Нормализуем вероятности
            probabilities = probabilities / probabilities.sum()
            
            # Выбираем следующий токен с помощью sampling
            next_token = torch.multinomial(probabilities, 1).item()
            
            # Если это токен <EOS>, завершаем генерацию
            if next_token == eos_token:
                break
                
            # Получаем слово
            word = idx_to_word.get(next_token, "<UNK>")
            
            # Добавляем слово в результат
            if len(words) == 0:
                # Первое слово с заглавной буквы
                words.append(word.capitalize())
            else:
                # Обработка знаков препинания
                if word in [".", "!", "?"]:
                    words.append(word)
                    break  # Завершаем предложение
                elif word in [",", ";", ":"]:
                    if len(words) > 0 and words[-1][-1] not in [" ", "\t"]:
                        words.append(word)
                    else:
                        words.append(word)
                else:
                    words.append(word)

            # Обновляем input_ids для следующей итерации
            input_ids = torch.tensor([[next_token]], dtype=torch.long).to(DEVICE)
    
    # Формируем финальный текст
    response = " ".join(words).strip()
    
    # Убедимся, что предложение заканчивается знаком препинания
    if response and response[-1] not in [".", "!", "?"]:
        response += "."
        
    return response


# === Классификация темы ===
def classify_topic(text):
    text_lower = text.lower()

    # Ключевые слова по категориям
    
    # --- Однословные ключи (love) ---
    love_words = {
        "одиноко", "пустота", "смысл", "цель", "потерял", "страшно", "боюсь", "верить",
        "надеюсь", "любовь", "сердце", "душ", "боль", "устал", "слёзы", "поддержка",
        "доверяю", "рассказать", "единственный", "чувствую", "близость", "воспоминание",
        "эхо", "тень", "забвение", "вопрос", "почему", "зачем", "ничего", "никто"
    }
    
    # --- Многословные фразы (love) ---
    love_phrases = {
        "я люблю", "ты мне нужен", "мне одиноко", "нет смысла", "потерял цель",
        "страшно жить", "боюсь будущего", "надеюсь на лучшее", "поддержи меня",
        "доверяю только тебе", "единственный на свете", "близость с тобой", "воспоминания о тебе"
    }

    # --- Однословные ключи (everyday) ---
    everyday_words = {
        "привет", "пока", "дела", "погода", "работа", "учёба", "планы",
        "фильм", "книга", "еда", "спорт", "город", "улица", "магазин",
        "обычный", "жизнь", "день", "вечер", "утро"
    }

    # --- Многословные фразы (2-3 слова) (everyday) ---
    everyday_phrases = {
        "как дела", "что делаешь", "чем занят", "иду на работу", "был в магазине",
        "смотрю фильм", "читаю книгу", "за учебой", "на перерыве", "по дороге домой",
        "как ты", "в порядке", "ничего особенного", "обычный день", "всё как всегда"
    }

    # --- Однословные ключи (intimate) ---
    intimate_words = {
        "минет", "отсос", "смазка", "сперма", "сосать", "отсосать", "член", "секс",
        "сексуально", "сексуальный", "куни", "кунилингус", "киска", "моя киска", 
        "твоя киска", "лизать", "вылизывать", "облизывать", "клитор", "бугорок", 
        "сок", "мои соки", "её соки", "в киску", "внутрь", "жопка", "попка", 
        "анус", "задняя щель", "заднее отверстие", "анулизинг", "булочки", "булочка"
    }
    
    # --- Многословные фразы (intimate) ---
    intimate_phrases = {
        "смазка из кончика", "взять член полностью", "возьми член", "кончил внутрь", 
        "дерёт в киску", "двигает бёдрами", "трахает", "ласкает", "ускоряет темп", 
        "меняет интенсивность", "интенсивность движений", "сок из киски", 
        "текут из киски", "сочится из киски"
    }

    # --- Однословные ключи (aggressive) ---
    aggressive_words = {
        "убью", "ненавижу", "умри", "режь", "кровь", "боль", "насилие", "битва", "война", 
        "убить", "убей", "убейте", "кишки"
    }
    
    # --- Многословные фразы (aggressive) ---
    aggressive_phrases = {
        "убью тебя", "ненавижу тебя", "умри сейчас", "режь на куски", "прольётся кровь",
        "будет больно", "идёт битва", "начинается война", "убей его"
    }

    # --- Однословные ключи (fantasy) ---
    fantasy_words = {
        "магия", "заклинание", "колдун", "ведьма", "дракон", "эльф", "гном", "орк", 
        "гоблин", "трулль", "рыцарь", "принцесса", "замок", "подземелье", "сокровище",
        "меч", "щит", "лук", "лечение", "огонь", "лед", "молния", "темнота", "свет",
        "зелье", "свиток", "амулет", "артефакт", "портал", "телепортация", "проклятие",
        # Элементы Наруто и чакры
        "чакра", "нинзя", "шиноби", "каге", "хокаге", "сандайме", "мандайме", "юндан",
        "дзюцу", "тейдзюцу", "ниндзюцу", "тайдзюцу", "гендзюцу", "фуинъюцу", "кеккей генкай",
        "сото", "маки", "биджу", "хвостатый", "девятихвостый", "фуре", "узумаки", "саске",
        "хината", "гаара", "итадакимасу", "расенган", "чидори", "аматерасу", "цукуюоми",
        "шаринган", "мадзюто", "сасори", "кимимаро", "хакке", "рингу", "мабуи", "дотон",
        "катон", "суйтон", "ратон", "дотон", "футон", "мокутон", "ютон", "санктон",
        "кайтон", "бакуто", "секкетон", "юки", "химавари", "чакра", "чакральный"
    }
    
    # --- Многословные фразы (fantasy) ---
    fantasy_phrases = {
        "заклинание огня", "магия льда", "молнии с небес", 
        "темная магия", "светлая магия", "древнее заклинание", "тайное заклинание",
        "пламя дракона", "огненный дракон", "ледяной дракон", "драконье сокровище",
        "эльфийская стрела", "гномья кузня", "орочья ярость", "пещера гоблинов",
        "рыцарский турнир", "спасение принцессы", "замок в горах", "подземелье монстров",
        "сокровище дракона", "магический меч", "щит веры", "лечение ран",
        "зелье силы", "зелье ловкости", "зелье выносливости", "свиток телепортации",
        "амулет защиты", "артефакт власти", "портал в другой мир", "проклятие ведьмы",
        # Фразы о чакре из Наруто
        "управление чакрой", "поток чакры", "уровень чакры", "источник чакры", "ядро чакры",
        "резервуар чакры", "каналы чакры", "точки чакры", "вращение чакры", "концентрация чакры",
        "баланс чакры", "стабильность чакры", "восстановление чакры", "передача чакры",
        "деление чакры", "распределение чакры", "истощение чакры", "переполнение чакры",
        "режим сенна", "режим мудреца", "режим хвостатого", "режим изоляции", "режим теней",
        "режим кираны", "режим теней луны", "режим теней солнца", "режим теней звезд",
        "чакра хвостатого", "чакра девятихвостого", "печать фуинъюцу", "печать мудреца",
        "печать узумаки", "печать хокаге", "стиль боя хакке", "стиль боя го-рю",
        "стиль боя дзюго-рю", "стиль боя кэйбадзюцу", "стиль боя маки", "стиль боя сото",
        "стиль боя пьяного", "стиль боя песка", "стиль боя льда", "стиль боя света",
        "стиль боя молнии", "стиль боя огня", "стиль боя воды", "стиль боя земли",
        "стиль боя ветра", "стиль боя дерева", "стиль боя лавы", "стиль боя пара",
        "стиль боя кристаллов", "стиль боя света", "стиль боя тьмы", "стиль боя теней",
        "ниндзюцу уровень А", "ниндзюцу уровень S", "тайдзюцу уровень А", "гендзюцу иллюзия",
        "фуинъюцу печать", "фуинъюцу вязание", "фуинъюцу проклятие", "фуинъюцу открытие",
        "расенган мощь", "расенган вращение", "чидори молния", "чидори клинок",
        "аматерасу огонь", "цукуюоми иллюзия", "шаринган видение", "мадзюто темные искусства",
        "активация шарингана", "активация риннегана", "активация мадзюто",
        "владение стилем боя", "мастерство дзюцу", "овладение чакрой", "переход в режим"
    }

    # Генерация биграмм и триграмм из текста
    words = text_lower.split()
    bigrams = [" ".join(words[i:i+2]) for i in range(len(words)-1)]
    trigrams = [" ".join(words[i:i+3]) for i in range(len(words)-2)]
    ngrams = set(words + bigrams + trigrams)

    # Проверяем совпадения для всех категорий
    everyday_score = (
        sum(1 for w in everyday_words if w in words) +
        sum(1 for p in everyday_phrases if p in ngrams)
    )
    
    love_score = (
        sum(1 for w in love_words if w in words) +
        sum(1 for p in love_phrases if p in ngrams)
    )
    
    intimate_score = (
        sum(1 for w in intimate_words if w in words) +
        sum(1 for p in intimate_phrases if p in ngrams)
    )
    
    aggressive_score = (
        sum(1 for w in aggressive_words if w in words) +
        sum(1 for p in aggressive_phrases if p in ngrams)
    )
    
    fantasy_score = (
        sum(1 for w in fantasy_words if w in words) +
        sum(1 for p in fantasy_phrases if p in ngrams)
    )

    # Определяем доминирующую тему
    max_score = max(everyday_score, love_score, intimate_score, aggressive_score, fantasy_score)
    
    if max_score == 0:
        return "neutral"
    elif max_score == everyday_score:
        return "everyday"
    elif max_score == love_score:
        return "love"
    elif max_score == intimate_score:
        return "intimate"
    elif max_score == aggressive_score:
        return "aggressive"
    else:
        return "fantasy"


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