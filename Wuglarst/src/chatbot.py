# Wuglarst/src/chatbot.py (обновлённая, production-ready версия)

import torch
import json
import os
import re
import random
from datetime import datetime
from typing import List, Dict, Any
from . import chat_model
from .chat_model import ChatNN
# from .web_search import WebSearch  # Отключён — поиск в чате отключён
from .cultural_references import get_cultural_phrase
import sys
import subprocess
import threading
import logging

# === Настройки RPG ===
RPG_MAX_LENGTH = 256
RPG_TEMPERATURE = 0.85
RPG_TOP_P = 0.92

# Импортируем KnowledgeManager
try:
    from knowledge_manager import KnowledgeManager
    knowledge_manager_available = True
except ImportError:
    print("⚠️ knowledge_manager не найден. Установите сначала.")
    knowledge_manager_available = False


class SimpleTokenizer:
    """Токенизатор, совместимый с tokenizer.json"""
    def __init__(self, tokenizer_path: str, max_length: int = RPG_MAX_LENGTH):
        with open(tokenizer_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        self.vocab = data["vocab"]
        # inverse_vocab может быть dict или list — нормализуем к list
        inv = data["inverse_vocab"]
        if isinstance(inv, list):
            self.inverse_vocab = inv
        else:
            # dict с int-ключами
            max_key = max(inv.keys()) if inv else 0
            self.inverse_vocab = [None] * (max_key + 1)
            for k, v in inv.items():
                self.inverse_vocab[k] = v
        self.pad_token_id = self.vocab["<PAD>"]
        self.eos_token_id = self.vocab["<EOS>"]
        self.unk_token_id = self.vocab["<UNK>"]
        self.max_length = max_length  # теперь глобально 256

    def encode(self, text: str, add_eos: bool = False, max_length: int = None) -> List[int]:
        if max_length is None:
            max_length = self.max_length
        words = text.lower().split()
        ids = [self.vocab.get(word, self.unk_token_id) for word in words]
        if add_eos:
            ids.append(self.eos_token_id)
        if len(ids) >= max_length:
            ids = ids[:max_length - 1] + [ids[-1]]  # сохраняем последний токен
        else:
            ids += [self.pad_token_id] * (max_length - len(ids))
        return ids

    def decode(self, token_ids: List[int]) -> str:
        words = []
        for idx in token_ids:
            if idx in [self.pad_token_id, self.eos_token_id]:
                break
            # inverse_vocab теперь list
            word = self.inverse_vocab[idx] if idx < len(self.inverse_vocab) else "<UNK>"
            if word not in ["<PAD>", "<UNK>", "<EOS>"]:
                words.append(word)
        return " ".join(words)


class ChatBot:
    def __init__(self, model_path: str, data_path: str, device=None):
        self.device = device or ("cuda" if torch.cuda.is_available() else "cpu")
        self.tokenizer_path = data_path
        self.model_path = model_path

        # Загружаем токенизатор
        self.tokenizer = SimpleTokenizer(self.tokenizer_path)
        self.vocab_size = len(self.tokenizer.vocab)
        self.max_length = RPG_MAX_LENGTH  # теперь 256

        # Загружаем модель
        self.model = ChatNN(
            vocab_size=self.vocab_size,
            embedding_dim=128,
            hidden_dim=512,
            num_layers=2,
            max_length=self.max_length,
            pad_token_id=self.tokenizer.pad_token_id,
            eos_token_id=self.tokenizer.eos_token_id
        ).to(self.device)

        try:
            state_dict = torch.load(self.model_path, map_location=self.device, weights_only=True)
            self.model.load_state_dict(state_dict, strict=False)
            self.model.eval()
            print(f"[OK] Model loaded: {self.model_path} on {self.device}")
        except Exception as e:
            raise RuntimeError(f"[FAIL] Failed to load model: {e}")

        # Поиск и знания
        # self.web_search = WebSearch()  # Отключён — поиск в чате отключён
        self.web_search_enabled = False  # Флаг отключения поиска
        self.knowledge_cache = {}
        self.knowledge_file = "data/knowledge_cache.json"
        self._load_knowledge_cache()

        # Менеджер знаний
        self.knowledge_manager = None
        self.use_knowledge_manager = knowledge_manager_available
        if self.use_knowledge_manager:
            try:
                self.knowledge_manager = KnowledgeManager("data/knowledge")
                print("🧠 Менеджер знаний инициализирован")
            except Exception as e:
                print(f"❌ Ошибка инициализации менеджера знаний: {e}")
                self.use_knowledge_manager = False

        # Лог диалогов
        self.conversation_log = "data/user_conversations.jsonl"
        os.makedirs(os.path.dirname(self.conversation_log), exist_ok=True)

    def _load_knowledge_cache(self):
        if os.path.exists(self.knowledge_file):
            try:
                with open(self.knowledge_file, "r", encoding="utf-8") as f:
                    self.knowledge_cache = json.load(f)
                print(f"✅ Загружено {len(self.knowledge_cache)} знаний из кэша")
            except Exception as e:
                print(f"⚠️ Ошибка загрузки кэша: {e}")
                self.knowledge_cache = {}
        else:
            print("ℹ️ Кэш знаний не найден.")

    def _save_knowledge_cache(self, word: str, response: str):
        self.knowledge_cache[word] = response
        with open(self.knowledge_file, "w", encoding="utf-8") as f:
            json.dump(self.knowledge_cache, f, ensure_ascii=False, indent=2)

    def _clean_text(self, text: str) -> str:
        if not isinstance(text, str) or not text.strip():
            return ""
        text = text.lower()
        text = re.sub(r'[^а-яёa-z0-9\s?!,.]', '', text)
        text = re.sub(r'\s+', ' ', text).strip()
        replacements = {
            "яне": "я не", "тыне": "ты не", "онне": "он не", "она нее": "она не",
            "мыне": "мы не", "выне": "вы не", "онине": "они не",
            "незнаю": "не знаю", "хз": "не знаю", "ок": "окей", "спс": "спасибо",
            "прив": "привет", "пока": "пока", "здарова": "здравствуй"
        }
        for wrong, right in replacements.items():
            text = text.replace(wrong, right)
        return text

    # ... existing code ...

    def _generate_response_with_sampling(
        self,
        input_text: str,
        max_length: int = RPG_MAX_LENGTH,
        temperature: float = RPG_TEMPERATURE,
        top_p: float = RPG_TOP_P,
        max_words: int = 40
    ) -> str:
        """Генерация ответа с nucleus sampling"""
        self.model.eval()
        tokens = self._clean_text(input_text).split()
        input_ids = self.tokenizer.encode(" ".join(tokens), add_eos=False)
        input_tensor = torch.tensor([input_ids], dtype=torch.long).to(self.device)
        mask = (input_tensor != self.tokenizer.pad_token_id).float().to(self.device)

        import time
        start_gen = time.time()

        generated_ids = []
        current_input = input_tensor
        current_mask = mask

        word_count = 0
        prev_word = ""
        repeat_count = 0

        with torch.no_grad():
            for step in range(max_length):
                step_start = time.time()
                logits = self.model(current_input, mask=current_mask)[:, -1, :]
                logits = logits / temperature

                sorted_logits, sorted_indices = torch.sort(logits, descending=True)
                cumulative_probs = torch.softmax(sorted_logits, dim=-1).cumsum(dim=-1)
                sorted_indices_to_remove = cumulative_probs > top_p
                sorted_indices_to_remove[..., 1:] = sorted_indices_to_remove[..., :-1].clone()
                sorted_indices_to_remove[..., 0] = 0
                indices_to_remove = sorted_indices[sorted_indices_to_remove]
                logits[0, indices_to_remove] = float('-inf')

                probs = torch.softmax(logits, dim=-1)
                next_token = torch.multinomial(probs, num_samples=1).item()

                if next_token == self.tokenizer.eos_token_id:
                    print(f"⏱ Генерация [{step} токенов] завершена за {time.time() - start_gen:.2f} сек (step: {time.time() - step_start:.2f})")
                    break

                if next_token not in [self.tokenizer.pad_token_id, self.tokenizer.unk_token_id]:
                    generated_ids.append(next_token)
                    word = self.inverse_vocab[next_token] if next_token < len(self.inverse_vocab) else "<UNK>"
                    if word != prev_word:
                        repeat_count = 0
                    else:
                        repeat_count += 1
                    prev_word = word
                    word_count += 1

                    # Ранняя остановка: макс слов или 3 одинаковых подряд
                    if word_count >= max_words or repeat_count >= 3:
                        print(f"⏱ Ранняя остановка: {word_count} слов, repeat={repeat_count} за {time.time() - start_gen:.2f} сек")
                        break

                new_token = torch.tensor([[next_token]], device=self.device)
                current_input = torch.cat([current_input, new_token], dim=1)
                current_input = current_input[:, -self.max_length:]

                new_mask = torch.ones((1, 1), device=self.device)
                current_mask = torch.cat([current_mask, new_mask], dim=1)
                current_mask = current_mask[:, -self.max_length:]

                step_time = time.time() - step_start
                if step_time > 0.5:
                    print(f"⚠️ Долгий шаг генерации: {step_time:.2f} сек на токен {step}")

        decoded = self.tokenizer.decode(generated_ids).strip()
        print(f"⏱ Генерация завершена за {time.time() - start_gen:.2f} сек | Длина: {len(decoded)} | слов: {word_count}")
        return decoded


    def generate_response(self, messages: List[Dict[str, str]], mode: str = "chat") -> str:
        import time
        start_total = time.time()
        logging.info(f"⏱ generate_response(start_total): {time.time() - start_total:.2f} сек | mode={mode}")

        context = []
        last_user_msg = ""

        for msg in messages:
            if not msg["message"].strip():
                continue
            role = "Пользователь" if msg["is_own"] else "Бот"
            context.append(f"{role}: {msg['message']}")

        for msg in reversed(messages):
            if msg["is_own"]:
                last_user_msg = msg["message"].strip()
                break

        if not last_user_msg:
            logging.warning("⏱ generate_response: пустой last_user_msg → fallback")
            return json.dumps({"response": "Я здесь! 🤖"}, ensure_ascii=False)

        # === Режим narrative ===
        if mode == "narrative":
            start_mode = time.time()
            context_str = "\n".join(context[-5:])
            prompt = (
                "Ты — мастер вселенных. Создаёшь глубокие, логичные и атмосферные миры.\n"
                "Формат:\nНазвание:\n - ...\nЗаконы общества:\n - ...\nТрадиции:\n - ...\n\n"
                f"История диалога:\n{context_str}\nБот:"
            )
            response = self._generate_response_with_sampling(prompt, max_length=128)
            required = ["Название:", "Законы общества:", "Традиции:"]
            if not all(kw in response for kw in required):
                response = (
                    "Название:\n - Мир без имени\n"
                    "Законы общества:\n - Никто не вспоминает прошлое.\n"
                    "Традиции:\n - Каждую полночь зажигают свечи за умершие идеи.\n"
                    "Внегласные правила:\n - Не задавай, кто ты на самом деле."
                )
            elapsed = time.time() - start_mode
            logging.info(f"⏱ generate_response (narrative): {elapsed:.2f} сек")
            return json.dumps({"response": response}, ensure_ascii=False)

        # === Режим world_gen ===
        elif mode == "world_gen":
            start_mode = time.time()
            genre_match = re.search(r"Жанр:\s*([^\.\n]+)", last_user_msg)
            tags_match = re.search(r"Темы:\s*([^\.\n]+)", last_user_msg)
            genre = genre_match.group(1).strip() if genre_match else "Фэнтези"
            tags = tags_match.group(1).strip() if tags_match else ""

            prompt = f"Создай мир: {genre}"
            if tags:
                prompt += f", {tags}"

            response = self._generate_response_with_sampling(prompt, max_length=128)
            elapsed = time.time() - start_mode
            logging.info(f"⏱ generate_response (world_gen): {elapsed:.2f} сек")
            return json.dumps({"world": response}, ensure_ascii=False)

        # === Режим chat ===
        elif mode == "chat":
            start_mode = time.time()
            tokens = self._clean_text(last_user_msg).split()
            unknown_words = [t for t in tokens if t not in self.tokenizer.vocab]

            if unknown_words:
                word = unknown_words[0]
                # Поиск в интернете отключён
                # if word in self.knowledge_cache:
                #     logging.info(f"📚 chat: знание найдено в кэше → '{word}'")
                #     logging.info(f"⏱ generate_response (chat+cache): {time.time() - start_mode:.2f} сек")
                #     return json.dumps({"response": self.knowledge_cache[word]}, ensure_ascii=False)

                # Поиск в интернете — ОТКЛЮЧЁН
                # start_search = time.time()
                # try:
                #     definition = self.web_search.lookup(word)
                #     search_time = time.time() - start_search
                #     logging.info(f"⏱ web_search.lookup('{word}'): {search_time:.2f} сек")
                #     if definition and len(definition) > 5:
                #         response = f"🔍 Я не знал слово «{word}», но нашёл:\n\n{definition.strip()}"
                #         self._save_knowledge_cache(word, response)
                #         self._trigger_knowledge_learning(word, definition)
                #         logging.info(f"⏱ generate_response (chat+search): {time.time() - start_mode:.2f} сек")
                #         return json.dumps({"response": response}, ensure_ascii=False)
                # except Exception as e:
                #     logging.error(f"❌ Ошибка поиска: {e}")

            # Генерация
            start_subgen = time.time()
            base_response = self._generate_response_with_sampling(
                last_user_msg,
                max_length=64,
                max_words=30
            )
            subgen_time = time.time() - start_subgen
            logging.info(f"⏱ generate_response (chat+subgen): {subgen_time:.2f} сек | len={len(base_response)}")

            if not base_response or len(base_response.split()) < 2:
                base_response = random.choice([
                    "Привет! Я здесь.",
                    "Расскажи больше?",
                    "Интересно...",
                    "А ты как думаешь?"
                ])
                logging.warning("⚠️ chat: fallback → случайный ответ")

            final_response = base_response
            if random.random() < 0.25:
                phrase = get_cultural_phrase()
                style = random.choice(['prefix', 'suffix'])
                final_response = f"{phrase} {base_response}" if style == 'prefix' else f"{base_response} ({phrase})"

            self.log_interaction(last_user_msg, final_response)
            total = time.time() - start_mode
            logging.info(f"⏱ generate_response (chat): {total:.2f} сек")
            return json.dumps({"response": final_response}, ensure_ascii=False)

        # === Режим continue ===
        elif mode == "continue":
            start_mode = time.time()
            context_str = "\n".join(context[-6:])
            prompt = (
                "Продолжи диалог как бот. Сохраняй стиль, характер, логику и атмосферу. "
                "Не переспрашивай, не задавай вопросов — просто продолжай.\n"
                "Твой ответ должен быть логичным продолжением предыдущего сообщения.\n"
                f"Контекст:\n{context_str}\nБот:"
            )
            response = self._generate_response_with_sampling(prompt, max_length=128)

            # Удаляем повторяющиеся слова в начале
            words = response.split()
            if len(words) >= 2 and words[0] == words[1]:
                response = " ".join(words[1:])

            if not response or len(response.split()) < 3:
                response = (
                    random.choice([
                        "Это важно...",
                        "Ты прав...",
                        "Может быть...",
                        "Интересно..."
                    ]) + " " + response.strip()
                )

            self.log_interaction(last_user_msg, response)
            logging.info(f"⏱ generate_response (continue): {time.time() - start_mode:.2f} сек")
            return json.dumps({"response": response}, ensure_ascii=False)

        # === Режим RPG ===
        elif mode == "rpg":
            start_mode = time.time()
            # 🔍 ОПРЕДЕЛЕНИЕ ЖАНРА (обновлённое, 21 жанр)
            def detect_genre(messages: List[Dict[str, str]]) -> str:
                last_msg = ""
                for m in reversed(messages):
                    if m["is_own"]:
                        last_msg = m["message"].lower()
                        break
                if not last_msg:
                    return "фэнтези"

                # Глобальные ключевые слова (регистронезависимые)
                genres = {
                    "фэнтези": ["фэнтези", "замок", "дракон", "магия", "эльф", "гоблин", "волшебник", "руны", "лес", "друид", "зелье"],
                    "киберпанк": ["киберпанк", "руины", "нейроимплант", "туман", "неон", "хром", "квартал", "глитч", "синий", "мозг", "робот"],
                    "стимпанк": ["стимпанк", "пар", "механизм", "труба", "бракон", "воздух", "локомотив", "часы", "медный", "фабрика", "масло"],
                    "постапокалипсис": ["постапокалипсис", "пустошь", "радиация", "выживание", "бомба", "мусор", "бункер", "ржавчина", "взрыв", "заброшенный", "мутант"],
                    "научная фантастика": ["научная фантастика", "космос", "звездолёт", "инопланетянин", "механизм", "исследование", "технология", "научный", "генетика", "эксперимент"],
                    "городское фэнтези": ["городское фэнтези", "город", "подземелье", "аллея", "мост", "ночь", "дождь", "фонарь", "кошка", "пассажир", "подземка"],
                    "биопанк": ["биопанк", "кровь", "кость", "биоинженерия", "клетка", "мутация", "шприц", "лаборатория", "глаз", "ткань", "мускул"],
                    "солнечный панк": ["солнечный панк", "солнце", "песок", "закат", "зонт", "пляж", "вода", "тень", "заряд", "фотон", "свет"],
                    "дизельпанк": ["дизельпанк", "дизель", "грязь", "труба", "двигатель", "дым", "колесо", "пар", "механик", "масло", "дизель"],
                    "меха": ["меха", "мех", "танк", "робот", "пилот", "двигатель", "баланс", "пушка", "панцирь", "система", "тревога"],
                    "драма": ["драма", "слёзы", "разрыв", "сожаление", "память", "надежда", "потеря", "сердце", "голос", "тишина", "книга"],
                    "комедия": ["комедия", "смех", "шутка", "абсурд", "ситуация", "смешной", "сценка", "шут", "смешок", "ржач", "смех"],
                    "триллер": ["триллер", "напряжение", "тревога", "запугивание", "подозрение", "побег", "секрет", "шаги", "холод", "тень", "затылок"],
                    "романтика": ["романтика", "сердце", "поцелуй", "любовь", "сладкий", "вечер", "месяц", "объятие", "тепло", "слёзы", "счастье"],
                    "детектив": ["детектив", "улика", "сыщик", "преступление", "тень", "свидетель", "досье", "пыль", "бандит", "преступник", "договор"],
                    "роман": ["роман", "история", "переживания", "событие", "характер", "нрав", "жизнь", "смысл", "день", "воспоминание", "воспоминания"],
                    "технофэнтези": ["технофэнтези", "магия", "технология", "глаз", "механизм", "руны", "нейрон", "мозг", "энергия", "силуэт", "пиксель"],
                    "нуар": ["нуар", "дождь", "тень", "туман", "глаза", "мужчина", "женщина", "смокинг", "сигарета", "табак", "ночь", "улица"],
                    "фантастика": ["фантастика", "невероятный", "сказка", "волшебство", "чудо", "загадка", "сюжет", "мировоззрение", "фантазия", "выдумка"],
                    "исекай": ["исекай", "другой мир", "перерождение", "мечта", "книга", "пиксель", "карта", "quest", "гильдия", "квест"],
                    "обратный исекай": ["обратный исекай", "вернулся", "домой", "мир", "технология", "странный", "чужак", "посторонний", "чудо", "чудесный", "глаз"],
                    "повседневность": ["повседневность", "кофе", "квартира", "дом", "семья", "работа", "суббота", "воскресенье", "погода", "дома", "свет"]
                }

                # Быстрый поиск по всем ключевым словам
                for genre, keywords in genres.items():
                    if any(kw in last_msg for kw in keywords):
                        return genre
                return "фэнтези"  # по умолчанию

            genre = detect_genre(messages)
            logging.info(f"📜 rpg: жанр = '{genre}'")

            # Лог подстановки промпта
            if genre in genre_prompts:
                prompt_parts = genre_prompts[genre]
                logging.info(f"📜 rpg: промпт для '{genre}' содержит {len(prompt_parts)} строк")
            else:
                logging.warning(f"⚠️ rpg: жанр '{genre}' не найден в genre_prompts → fallback на фэнтези")

            logging.info(f"⏱ generate_response (rpg): {time.time() - start_mode:.2f} сек")

            # 🔥 ЗАГРУЗКА СТИЛЬНОГО ПРОМПТА ПО ЖАНРУ (обновлённые промпты)
            genre_prompts = {
                "киберпанк": [
                    "Ты — писатель-сценарист. Пиши атмосферные сцены в стиле научной фантастики.",
                    "Формат ответа:",
                    "1. Заголовок: **Локация — Время**",
                    "2. Описание: Действия и окружение.",
                    "3. Диалог: «Речь» — действие говорящего.",
                    "4. Мысли: *Внутренний монолог в курсиве.*",
                    "Место: {location}",
                    "Здоровье: {hp} / 100",
                    "Инвентарь: {items}",
                    "",
                    "Правила:",
                    "- Используй термины: нейроимплант, глитч, дата-поток, хром.",
                    "- Не пиши 'Я как бот'. Ты часть мира."
                ],
                "фэнтези": [
                    "Ты — писатель-сценарист. Пиши эпические сцены в стиле фэнтези.",
                    "Формат ответа:",
                    "1. Заголовок: **Локация — Время**",
                    "2. Описание: Действия и окружение.",
                    "3. Диалог: «Речь» — действие говорящего.",
                    "4. Мысли: *Внутренний монолог в курсиве.*",
                    "Место: {location}",
                    "Здоровье: {hp} / 100",
                    "Инвентарь: {items}",
                    "",
                    "Правила:",
                    "- Используй слова: дракон, руны, эльф, магия, туман, башня.",
                    "- Не пиши 'Я как бот'. Ты часть мира."
                ],
                "стимпанк": [
                    "Ты — писатель-сценарист. Пиши сцены в стиле стимпанка.",
                    "Формат ответа:",
                    "1. Заголовок: **Локация — Время**",
                    "2. Описание: Действия и окружение.",
                    "3. Диалог: «Речь» — действие говорящего.",
                    "4. Мысли: *Внутренний монолог в курсиве.*",
                    "Место: {location}",
                    "Здоровье: {hp} / 100",
                    "Инвентарь: {items}",
                    "",
                    "Правила:",
                    "- Используй слова: пар, шестерёнка, дым, масло, гайка.",
                    "- Не пиши 'Я как бот'. Ты часть мира."
                ],
                "постапокалипсис": [
                    "Ты — писатель-сценарист. Пиши сцены в стиле постапокалипсиса.",
                    "Формат ответа:",
                    "1. Заголовок: **Локация — Время**",
                    "2. Описание: Действия и окружение.",
                    "3. Диалог: «Речь» — действие говорящего.",
                    "4. Мысли: *Внутренний монолог в курсиве.*",
                    "Место: {location}",
                    "Здоровье: {hp} / 100",
                    "Инвентарь: {items}",
                    "",
                    "Правила:",
                    "- Используй слова: радиация, бункер, мутант, ржавчина.",
                    "- Не пиши 'Я как бот'. Ты часть мира."
                ],
                "научная фантастика": [
                    "Ты — писатель-сценарист. Пиши сцены в стиле научной фантастики.",
                    "Формат ответа:",
                    "1. Заголовок: **Локация — Время**",
                    "2. Описание: Действия и окружение.",
                    "3. Диалог: «Речь» — действие говорящего.",
                    "4. Мысли: *Внутренний монолог в курсиве.*",
                    "Место: {location}",
                    "Здоровье: {hp} / 100",
                    "Инвентарь: {items}",
                    "",
                    "Правила:",
                    "- Используй слова: космос, исследование, генетика, лаборатория.",
                    "- Не пиши 'Я как бот'. Ты часть мира."
                ],
                "городское фэнтези": [
                    "Ты — писатель-сценарист. Пиши сцены в стиле городского фэнтези.",
                    "Формат ответа:",
                    "1. Заголовок: **Локация — Время**",
                    "2. Описание: Действия и окружение.",
                    "3. Диалог: «Речь» — действие говорящего.",
                    "4. Мысли: *Внутренний монолог в курсиве.*",
                    "Место: {location}",
                    "Здоровье: {hp} / 100",
                    "Инвентарь: {items}",
                    "",
                    "Правила:",
                    "- Используй слова: подземка, аллея, фонарь, мост, дождь.",
                    "- Не пиши 'Я как бот'. Ты часть мира."
                ],
                "биопанк": [
                    "Ты — писатель-сценарист. Пиши сцены в стиле биопанка.",
                    "Формат ответа:",
                    "1. Заголовок: **Локация — Время**",
                    "2. Описание: Действия и окружение.",
                    "3. Диалог: «Речь» — действие говорящего.",
                    "4. Мысли: *Внутренний монолог в курсиве.*",
                    "Место: {location}",
                    "Здоровье: {hp} / 100",
                    "Инвентарь: {items}",
                    "",
                    "Правила:",
                    "- Используй слова: клетка, мутация, шприц, ткань, мускул.",
                    "- Не пиши 'Я как бот'. Ты часть мира."
                ],
                "солнечный панк": [
                    "Ты — писатель-сценарист. Пиши сцены в стиле солнечного панка.",
                    "Формат ответа:",
                    "1. Заголовок: **Локация — Время**",
                    "2. Описание: Действия и окружение.",
                    "3. Диалог: «Речь» — действие говорящего.",
                    "4. Мысли: *Внутренний монолог в курсиве.*",
                    "Место: {location}",
                    "Здоровье: {hp} / 100",
                    "Инвентарь: {items}",
                    "",
                    "Правила:",
                    "- Используй слова: солнце, пляж, зонт, волна, солёный.",
                    "- Не пиши 'Я как бот'. Ты часть мира."
                ],
                "дизельпанк": [
                    "Ты — писатель-сценарист. Пиши сцены в стиле дизельпанка.",
                    "Формат ответа:",
                    "1. Заголовок: **Локация — Время**",
                    "2. Описание: Действия и окружение.",
                    "3. Диалог: «Речь» — действие говорящего.",
                    "4. Мысли: *Внутренний монолог в курсиве.*",
                    "Место: {location}",
                    "Здоровье: {hp} / 100",
                    "Инвентарь: {items}",
                    "",
                    "Правила:",
                    "- Используй слова: дизель, гарь, двигатель, колесо, дым.",
                    "- Не пиши 'Я как бот'. Ты часть мира."
                ],
                "меха": [
                    "Ты — писатель-сценарист. Пиши сцены в стиле меха.",
                    "Формат ответа:",
                    "1. Заголовок: **Локация — Время**",
                    "2. Описание: Действия и окружение.",
                    "3. Диалог: «Речь» — действие говорящего.",
                    "4. Мысли: *Внутренний монолог в курсиве.*",
                    "Место: {location}",
                    "Здоровье: {hp} / 100",
                    "Инвентарь: {items}",
                    "",
                    "Правила:",
                    "- Используй слова: пилот, танк, пушка, баланс, тревога.",
                    "- Не пиши 'Я как бот'. Ты часть мира."
                ],
                "драма": [
                    "Ты — писатель-сценарист. Пиши эмоциональные сцены в стиле драмы.",
                    "Формат ответа:",
                    "1. Заголовок: **Локация — Время**",
                    "2. Описание: Действия и окружение.",
                    "3. Диалог: «Речь» — действие говорящего.",
                    "4. Мысли: *Внутренний монолог в курсиве.*",
                    "Место: {location}",
                    "Здоровье: {hp} / 100",
                    "Инвентарь: {items}",
                    "",
                    "Правила:",
                    "- Используй слова: слёзы, разрыв, память, надежда, тишина.",
                    "- Не пиши 'Я как бот'. Ты часть мира."
                ],
                "комедия": [
                    "Ты — писатель-сценарист. Пиши сцены в стиле комедии.",
                    "Формат ответа:",
                    "1. Заголовок: **Локация — Время**",
                    "2. Описание: Действия и окружение.",
                    "3. Диалог: «Речь» — действие говорящего.",
                    "4. Мысли: *Внутренний монолог в курсиве.*",
                    "Место: {location}",
                    "Здоровье: {hp} / 100",
                    "Инвентарь: {items}",
                    "",
                    "Правила:",
                    "- Используй слова: смех, шутка, абсурд, сценка.",
                    "- Не пиши 'Я как бот'. Ты часть мира."
                ],
                "триллер": [
                    "Ты — писатель-сценарист. Пиши напряжённые сцены в стиле триллера.",
                    "Формат ответа:",
                    "1. Заголовок: **Локация — Время**",
                    "2. Описание: Действия и окружение.",
                    "3. Диалог: «Речь» — действие говорящего.",
                    "4. Мысли: *Внутренний монолог в курсиве.*",
                    "Место: {location}",
                    "Здоровье: {hp} / 100",
                    "Инвентарь: {items}",
                    "",
                    "Правила:",
                    "- Используй слова: напряжение, тень, шаги, холод, подозрение.",
                    "- Не пиши 'Я как бот'. Ты часть мира."
                ],
                "романтика": [
                    "Ты — писатель-сценарист. Пиши романтичные сцены.",
                    "Формат ответа:",
                    "1. Заголовок: **Локация — Время**",
                    "2. Описание: Действия и окружение.",
                    "3. Диалог: «Речь» — действие говорящего.",
                    "4. Мысли: *Внутренний монолог в курсиве.*",
                    "Место: {location}",
                    "Здоровье: {hp} / 100",
                    "Инвентарь: {items}",
                    "",
                    "Правила:",
                    "- Используй слова: поцелуй, тепло, объятие, вечер, свечи.",
                    "- Не пиши 'Я как бот'. Ты часть мира."
                ],
                "детектив": [
                    "Ты — писатель-сценарист. Пиши сцены в стиле детектива.",
                    "Формат ответа:",
                    "1. Заголовок: **Локация — Время**",
                    "2. Описание: Действия и окружение.",
                    "3. Диалог: «Речь» — действие говорящего.",
                    "4. Мысли: *Внутренний монолог в курсиве.*",
                    "Место: {location}",
                    "Здоровье: {hp} / 100",
                    "Инвентарь: {items}",
                    "",
                    "Правила:",
                    "- Используй слова: улика, досье, тень, пыль, бандит.",
                    "- Не пиши 'Я как бот'. Ты часть мира."
                ],
                "роман": [
                    "Ты — писатель-сценарист. Пиши сцены в стиле психологического романа.",
                    "Формат ответа:",
                    "1. Заголовок: **Локация — Время**",
                    "2. Описание: Действия и окружение.",
                    "3. Диалог: «Речь» — действие говорящего.",
                    "4. Мысли: *Внутренний монолог в курсиве.*",
                    "Место: {location}",
                    "Здоровье: {hp} / 100",
                    "Инвентарь: {items}",
                    "",
                    "Правила:",
                    "- Используй слова: событие, воспоминание, день, смысл, жизнь.",
                    "- Не пиши 'Я как бот'. Ты часть мира."
                ],
                "технофэнтези": [
                    "Ты — писатель-сценарист. Пиши сцены в стиле технофэнтези.",
                    "Формат ответа:",
                    "1. Заголовок: **Локация — Время**",
                    "2. Описание: Действия и окружение.",
                    "3. Диалог: «Речь» — действие говорящего.",
                    "4. Мысли: *Внутренний монолог в курсиве.*",
                    "Место: {location}",
                    "Здоровье: {hp} / 100",
                    "Инвентарь: {items}",
                    "",
                    "Правила:",
                    "- Используй слова: руны, нейрон, пиксель, магия, технология.",
                    "- Не пиши 'Я как бот'. Ты часть мира."
                ],
                "нуар": [
                    "Ты — писатель-сценарист. Пиши сцены в стиле нуар.",
                    "Формат ответа:",
                    "1. Заголовок: **Локация — Время**",
                    "2. Описание: Действия и окружение.",
                    "3. Диалог: «Речь» — действие говорящего.",
                    "4. Мысли: *Внутренний монолог в курсиве.*",
                    "Место: {location}",
                    "Здоровье: {hp} / 100",
                    "Инвентарь: {items}",
                    "",
                    "Правила:",
                    "- Используй слова: дождь, туман, сигарета, тень, морген.",
                    "- Не пиши 'Я как бот'. Ты часть мира."
                ],
                "фантастика": [
                    "Ты — писатель-сценарист. Пиши сцены в стиле научной фантастики.",
                    "Формат ответа:",
                    "1. Заголовок: **Локация — Время**",
                    "2. Описание: Действия и окружение.",
                    "3. Диалог: «Речь» — действие говорящего.",
                    "4. Мысли: *Внутренний монолог в курсиве.*",
                    "Место: {location}",
                    "Здоровье: {hp} / 100",
                    "Инвентарь: {items}",
                    "",
                    "Правила:",
                    "- Используй слова: чудо, загадка, невероятный, фантазия, сказка.",
                    "- Не пиши 'Я как бот'. Ты часть мира."
                ],
                "исекай": [
                    "Ты — писатель-сценарист. Пиши сцены в стиле исекая.",
                    "Формат ответа:",
                    "1. Заголовок: **Локация — Время**",
                    "2. Описание: Действия и окружение.",
                    "3. Диалог: «Речь» — действие говорящего.",
                    "4. Мысли: *Внутренний монолог в курсиве.*",
                    "Место: {location}",
                    "Здоровье: {hp} / 100",
                    "Инвентарь: {items}",
                    "",
                    "Правила:",
                    "- Используй слова: квест, гильдия, уровень, карта, класс.",
                    "- Не пиши 'Я как бот'. Ты часть мира."
                ],
                "обратный исекай": [
                    "Ты — писатель-сценарист. Пиши сцены в стиле обратного исекая.",
                    "Формат ответа:",
                    "1. Заголовок: **Локация — Время**",
                    "2. Описание: Действия и окружение.",
                    "3. Диалог: «Речь» — действие говорящего.",
                    "4. Мысли: *Внутренний монолог в курсиве.*",
                    "Место: {location}",
                    "Здоровье: {hp} / 100",
                    "Инвентарь: {items}",
                    "",
                    "Правила:",
                    "- Используй слова: странный, чужак, мир, технология, меч.",
                    "- Не пиши 'Я как бот'. Ты часть мира."
                ],
                "повседневность": [
                    "Ты — писатель-сценарист. Пиши сцены в стиле повседневности.",
                    "Формат ответа:",
                    "1. Заголовок: **Локация — Время**",
                    "2. Описание: Действия и окружение.",
                    "3. Диалог: «Речь» — действие говорящего.",
                    "4. Мысли: *Внутренний монолог в курсиве.*",
                    "Место: {location}",
                    "Здоровье: {hp} / 100",
                    "Инвентарь: {items}",
                    "",
                    "Правила:",
                    "- Используй слова: кофе, диван, дом, погода, соседи.",
                    "- Не пиши 'Я как бот'. Ты часть мира."
                ]
            }

        logging.warning(f"⚠️ generate_response: неизвестный mode = '{mode}'")
        return json.dumps({"response": "Привет! Я здесь."}, ensure_ascii=False)

    def _trigger_knowledge_learning(self, word: str, definition: str):
        if self.use_knowledge_manager:
            try:
                self.knowledge_manager.add_word_knowledge(word, definition, source="web_search")
                count = self.knowledge_manager.get_stats().get('total_words', 0)
                if count % 10 == 0:
                    thread = threading.Thread(target=self._run_retrain, daemon=True)
                    thread.start()
            except Exception as e:
                print(f"❌ Ошибка обучения: {e}")

    def _run_retrain(self):
        try:
            result = subprocess.run(
                [sys.executable, "retrain.py"],
                cwd=os.path.dirname(os.path.abspath(__file__)),
                capture_output=True,
                text=True,
                timeout=600
            )
            if result.returncode == 0:
                print("✅ Дообучение завершено")
            else:
                print(f"❌ Ошибка: {result.stderr}")
        except Exception as e:
            print(f"💥 Ошибка: {e}")

    def log_interaction(self, user_message: str, bot_response: str):
        interaction = {
            "user": user_message,
            "bot": bot_response,
            "timestamp": datetime.now().isoformat()
        }
        with open(self.conversation_log, "a", encoding="utf-8") as f:
            f.write(json.dumps(interaction, ensure_ascii=False) + "\n")

    def chat(self):
        history = []
        print("ChatBot: Привет! Готов к диалогу. Напиши 'выход' для завершения.")
        while True:
            user_input = input("Вы: ").strip()
            if user_input.lower() in ['выход', 'стоп']:
                print("ChatBot: Пока!")
                break
            if not user_input:
                continue

            history.append({"message": user_input, "is_own": True})

            # Автоматический режим продолжения для коротких/однословных вводов
            mode = "continue" if (len(user_input.split()) <= 2 and len(user_input) <= 15) else "chat"
            response = self.generate_response(history, mode=mode)

            print(f"ChatBot: {json.loads(response)['response']}")
            history.append({"message": json.loads(response)['response'], "is_own": False})