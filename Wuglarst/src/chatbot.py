# Wuglarst/src/chatbot.py

import torch
import joblib
import numpy as np
import re
import json
import os
from .chat_model import ChatNN, generate_response as beam_generate
from .web_search import WebSearch
from datetime import datetime
from .cultural_references import get_cultural_phrase
import random
import sys
import subprocess
import threading

# Импортируем KnowledgeManager
try:
    from knowledge_manager import KnowledgeManager
    knowledge_manager_available = True
except ImportError:
    print("⚠️ knowledge_manager не найден. Установите сначала.")
    knowledge_manager_available = False

# Pydantic для строгой валидации (опционально)
try:
    from pydantic import BaseModel, validator
    from typing import List
    PYDANTIC_AVAILABLE = True
except ImportError:
    print("ℹ️ pydantic не установлен. Используется базовая валидация.")
    PYDANTIC_AVAILABLE = False


class WorldModel(BaseModel):
    """Pydantic-схема для структуры мира."""
    name: str
    laws: List[str]
    traditions: List[str]
    unspoken_rules: List[str]
    description: str

    @validator('laws', 'traditions', 'unspoken_rules', pre=True)
    def ensure_list(cls, v):
        if isinstance(v, list):
            return [str(item) for item in v if item is not None]
        return []


class ChatBot:
    def __init__(self, model_path, data_path, device=None, conversation_log="data/user_conversations.jsonl"):
        # Загружаем данные
        data = joblib.load(data_path)
        self.word_to_idx = data['word_to_idx']
        self.idx_to_word = data['idx_to_word']
        self.vocab_size = data['vocab_size']
        self.max_length = data['max_length']

        # Устройство
        self.device = device if device else torch.device('cpu')

        # Создаём модель
        self.model = ChatNN(
            vocab_size=self.vocab_size,
            embedding_dim=128,
            hidden_dim=256,
            num_layers=2
        )
        self.model.load_state_dict(torch.load(model_path, map_location=self.device))
        self.model.to(self.device)
        self.model.eval()

        # Поиск слов
        self.web_search = WebSearch()

        # Кэш знаний
        self.knowledge_cache = {}
        self.knowledge_file = "data/knowledge_cache.json"

        # Загружаем кэш
        if os.path.exists(self.knowledge_file):
            try:
                with open(self.knowledge_file, 'r', encoding='utf-8') as f:
                    self.knowledge_cache = json.load(f)
                print(f"✅ Загружено {len(self.knowledge_cache)} знаний из кэша")
            except Exception as e:
                print(f"⚠️ Ошибка загрузки кэша: {e}")
                self.knowledge_cache = {}
        else:
            print("ℹ️ Кэш знаний не найден. Будет создан новый.")

        # Менеджер знаний
        self.knowledge_manager = None
        self.use_knowledge_manager = knowledge_manager_available
        if self.use_knowledge_manager:
            try:
                self.knowledge_manager = KnowledgeManager("data/knowledge")
                print("🧠 Менеджер знаний инициализирован")
                stats = self.knowledge_manager.get_stats()
                if stats.get('total_words', 0) > 0:
                    print(f"📊 Всего выучено слов: {stats['total_words']}")
            except Exception as e:
                print(f"❌ Ошибка инициализации менеджера знаний: {e}")
                self.use_knowledge_manager = False

        # Путь для лога диалогов
        self.conversation_log = conversation_log
        os.makedirs(os.path.dirname(self.conversation_log), exist_ok=True)
        print(f'ChatBot (Custom LSTM) loaded on {self.device}')

    def _tokenize(self, text):
        """Улучшенная токенизация"""
        text = text.lower().strip()
        replacements = {
            "яне": "я не", "тыже": "ты же", "чтобы": "чтобы ", "всёравно": "всё равно",
            "незнаю": "не знаю", "нетебя": "не тебя", "нетак": "не так",
            "идуя": "иду я", "тыто": "ты то", "этоже": "это же"
        }
        for k, v in replacements.items():
            text = text.replace(k, v)
        text = re.sub(r'[^а-яa-z0-9\s\.\!\?]', '', text)
        text = re.sub(r'\s+', ' ', text).strip()
        return text.split()

    def _text_to_sequence(self, text):
        tokens = self._tokenize(text)
        seq = [self.word_to_idx.get(t, self.word_to_idx['<UNK>']) for t in tokens]
        if len(seq) < self.max_length:
            seq += [self.word_to_idx['<PAD>']] * (self.max_length - len(seq))
        else:
            seq = seq[:self.max_length]
        return np.array(seq)

    def _sequence_to_text(self, seq):
        words = []
        for idx in seq:
            if idx == self.word_to_idx['<PAD>']:
                break
            word = self.idx_to_word.get(idx, '<UNK>')
            if word not in ['<PAD>', '<UNK>']:
                words.append(word)
        return ' '.join(words)

    def _generate_with_beam(self, input_text, max_length=32):
        """Генерация через beam search (из chat_model.py)"""
        tokenizer = {
            'word_to_idx': self.word_to_idx,
            'idx_to_word': self.idx_to_word,
            'vocab_size': self.vocab_size
        }
        return beam_generate(
            self.model,
            tokenizer,
            input_text,
            device=self.device,
            max_length=max_length
        )

    def _generate_with_sampling(self, input_tensor, max_length=32, temperature=0.8, top_k=40, top_p=0.9):
        """Генерация с top-k и top-p фильтрацией."""
        self.model.eval()
        generated_ids = []
        current_input = input_tensor
        seen_ngrams = set()

        with torch.no_grad():
            for _ in range(max_length):
                outputs, _ = self.model(current_input)
                next_token_logits = outputs[:, -1, :]

                # Температура
                next_token_logits = next_token_logits / temperature

                # Top-K
                if top_k > 0:
                    indices_to_remove = next_token_logits < torch.topk(next_token_logits, top_k)[0][..., -1, None]
                    next_token_logits[indices_to_remove] = float('-inf')

                # Top-P
                if top_p < 1.0:
                    sorted_logits, sorted_indices = torch.sort(next_token_logits, descending=True)
                    cumulative_probs = torch.softmax(sorted_logits, dim=-1).cumsum(dim=-1)

                    sorted_indices_to_remove = cumulative_probs > top_p
                    sorted_indices_to_remove[..., 1:] = sorted_indices_to_remove[..., :-1].clone()
                    sorted_indices_to_remove[..., 0] = 0

                    indices_to_remove = sorted_indices[sorted_indices_to_remove]
                    next_token_logits.scatter_(1, indices_to_remove.unsqueeze(0), float('-inf'))

                probs = torch.softmax(next_token_logits, dim=-1)

                # Штраф за повторы
                if len(generated_ids) >= 2:
                    last_two = tuple(generated_ids[-2:])
                    for token_id in range(len(probs[0])):
                        if (last_two, token_id) in seen_ngrams:
                            probs[0][token_id] *= 0.1

                # Исключаем <PAD> и <UNK>
                probs[0][self.word_to_idx['<PAD>']] = 0
                probs[0][self.word_to_idx['<UNK>']] = 0

                # Случайный выбор
                next_token = torch.multinomial(probs, num_samples=1).item()

                if next_token in [self.word_to_idx['<PAD>'], self.word_to_idx['<UNK>']]:
                    break

                word = self.idx_to_word.get(next_token, "")
                if word in ['.', '!', '?']:
                    generated_ids.append(next_token)
                    break

                generated_ids.append(next_token)
                if len(generated_ids) >= 2:
                    seen_ngrams.add((generated_ids[-2], generated_ids[-1], next_token))

                current_input = torch.cat([
                    current_input,
                    torch.tensor([[next_token]], device=self.device)
                ], dim=1)

        return self._sequence_to_text(generated_ids).strip()

    def generate_response(self, messages, mode="chat"):
        """
        Основной метод генерации.
        Поддерживает WebSocket и JSON API.
        """
        last_user_msg = ""
        context = []

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
            return json.dumps({"response": "Я здесь! 🤖"}, ensure_ascii=False)

        tokens = self._tokenize(last_user_msg)
        unknown_words = [t for t in tokens if t not in self.word_to_idx]

        # === Режим narrative ===
        if mode == "narrative":
            response_text = self._generate_narrative(context)
            return json.dumps({"response": response_text}, ensure_ascii=False)

        # === Режим world_gen ===
        elif mode == "world_gen":
            genre, tags = self._extract_genre_tags(last_user_msg)
            world_data = self._generate_world_json(genre, tags)
            return json.dumps({"world": world_data}, ensure_ascii=False)

        # === Поиск неизвестных слов ===
        elif mode == "chat" and len(unknown_words) > 0:
            word = unknown_words[0]
            if word in self.knowledge_cache:
                return json.dumps({"response": self.knowledge_cache[word]}, ensure_ascii=False)

            try:
                definition = self.web_search.lookup(word)
                if definition and len(definition) > 5:
                    response = f"🔍 Я не знал слово «{word}», но нашёл:\n\n{definition.strip()}"
                    self._save_knowledge(word, response, definition.strip())
                    return json.dumps({"response": response}, ensure_ascii=False)
            except Exception as e:
                print(f"Ошибка поиска: {e}")

        # === Генерация основного ответа модели ===
        input_text = last_user_msg
        seq = self._text_to_sequence(input_text)
        input_tensor = torch.tensor([seq], dtype=torch.long).to(self.device)

        # Попробуем beam search → fallback на sampling
        try:
            base_response = self._generate_with_beam(input_text, max_length=32).strip()
            if not base_response or len(base_response.split()) < 2:
                raise Exception("Beam search failed")
        except:
            base_response = self._generate_with_sampling(
                input_tensor,
                max_length=32,
                temperature=0.8,
                top_k=40,
                top_p=0.9
            ).strip()

        # --- Fallback на шаблоны ---
        if (not base_response or len(base_response.split()) < 2 or
                base_response.count("свет") > 2 or base_response.count("один") > 2):
            fallbacks = [
                "Привет! Я здесь.",
                "Я слушаю.",
                "Расскажи больше?",
                "Интересно...",
                "А ты как думаешь?"
            ]
            base_response = random.choice(fallbacks)

        # --- Вставка культурной отсылки ---
        final_response = base_response
        if mode == "chat" and random.random() < 0.25:
            cultural_phrase = get_cultural_phrase()
            style_choice = random.choice(['prefix', 'suffix', 'separate'])
            if style_choice == 'prefix':
                final_response = f"{cultural_phrase} {base_response}"
            elif style_choice == 'suffix':
                final_response = f"{base_response} ({cultural_phrase})"
            else:
                final_response = f"{base_response}\n\n{cultural_phrase}"

        # --- Логируем подозрительные ответы ---
        if "свет" in final_response.lower() and final_response.count("свет") > 2:
            print(f"[WARNING] Подозрительный ответ: {repr(final_response)}")
            with open("data/suspicious_responses.log", "a", encoding="utf-8") as f:
                f.write(f"{datetime.now().isoformat()} | {last_user_msg} → {final_response}\n")

        self.log_interaction(last_user_msg, final_response)
        return json.dumps({"response": final_response}, ensure_ascii=False)

    def _extract_genre_tags(self, message):
        genre_match = re.search(r"Жанр:\s*([^\.\n]+)", message)
        tags_match = re.search(r"Темы:\s*([^\.\n]+)", message)
        genre = genre_match.group(1).strip() if genre_match else "Фэнтези"
        tags = tags_match.group(1).strip() if tags_match else "нет дополнительных тегов"
        return genre, tags

    def _generate_world_json(self, genre: str, tags: str) -> dict:
        prompt = (
            "Ты — мастер миров. Верни ТОЛЬКО валидный JSON и ничего больше.\n"
            "Структура ОБЯЗАТЕЛЬНО должна быть: {\n"
            '  "name": "",\n'
            '  "laws": [],\n'
            '  "traditions": [],\n'
            '  "unspoken_rules": [],\n'
            '  "description": ""\n'
            "}.\n"
            "Замени поля пустыми строками или списками, но не удаляй их.\n"
            "Никаких комментариев, пояснений или текста вне JSON.\n\n"
            f"Создай уникальный мир в жанре: {genre}. Темы: {tags}. Атмосфера — глубокая, оригинальная и атмосферная."
        )
        seq = self._text_to_sequence(prompt)
        input_tensor = torch.tensor([seq], dtype=torch.long).to(self.device)

        with torch.no_grad():
            logits, _ = self.model(input_tensor)
            indices = logits.argmax(dim=-1).cpu().numpy()[0]
        raw_text = self._sequence_to_text(indices)
        world_data = self._extract_json_from_text(raw_text)

        if world_data:
            validated_data = self._validate_and_fix_world(world_data)
            if validated_data:
                self.log_interaction(f"world_gen: {genre}, {tags}", json.dumps(validated_data))
                return validated_data

        print("[WARNING] Не удалось извлечь или валидировать JSON. Возвращаем пустую структуру.")
        empty = {
            "name": "",
            "laws": [],
            "traditions": [],
            "unspoken_rules": [],
            "description": ""
        }
        self.log_interaction(f"world_gen: {genre}, {tags}", json.dumps(empty))
        return empty

    def _extract_json_from_text(self, text: str) -> dict:
        """
        Ищет самый большой сбалансированный JSON-объект в тексте.
        Поддерживает вложенность.
        """
        best_match = None
        best_len = 0
        depth = 0
        start = -1

        for i, char in enumerate(text):
            if char == '{':
                if depth == 0:
                    start = i
                depth += 1
            elif char == '}':
                depth -= 1
                if depth == 0 and start != -1:
                    try:
                        candidate = text[start:i+1]
                        parsed = json.loads(candidate)
                        if len(candidate) > best_len:
                            best_match = parsed
                            best_len = len(candidate)
                    except json.JSONDecodeError:
                        continue  # Пропускаем невалидные
        return best_match

    def _validate_and_fix_world(self, data: dict) -> dict:
        """
        Валидирует и исправляет структуру мира.
        Использует pydantic, если доступен.
        """
        if PYDANTIC_AVAILABLE:
            try:
                validated = WorldModel(**data)
                return validated.dict()
            except Exception as e:
                print(f"❌ Pydantic validation failed: {e}")

        # Фолбэк: ручная валидация
        required_keys = ['name', 'laws', 'traditions', 'unspoken_rules', 'description']
        if not all(k in data for k in required_keys):
            return None

        # Проверяем типы
        if not isinstance(data['name'], str) or not isinstance(data['description'], str):
            return None

        def ensure_list(x):
            return x if isinstance(x, list) else []

        return {
            'name': str(data['name']),
            'laws': ensure_list(data['laws']),
            'traditions': ensure_list(data['traditions']),
            'unspoken_rules': ensure_list(data['unspoken_rules']),
            'description': str(data['description'])
        }

    def _generate_narrative(self, context):
        context_str = '\\n'.join(context)
        prompt = (
            "Ты — мастер вселенных. Создаёшь глубокие, логичные и атмосферные миры.\n"
            "Отвечай только на русском языке.\n"
            "Формат:\nНазвание:\n - ...\nЗаконы общества:\n - ...\n...\n\n"
            f"История диалога:\n{context_str}\nБот:"
        )
        seq = self._text_to_sequence(prompt)
        input_tensor = torch.tensor([seq], dtype=torch.long).to(self.device)

        with torch.no_grad():
            logits, _ = self.model(input_tensor)
            indices = logits.argmax(dim=-1).cpu().numpy()[0]
        response = self._sequence_to_text(indices).strip()

        required_parts = ["Название:", "Законы общества:", "Традиции:"]
        if not all(kw in response for kw in required_parts):
            response = (
                "Название:\n - Мир без имени\n"
                "Законы общества:\n - Никто не вспоминает прошлое.\n"
                "Традиции:\n - Каждую полночь зажигают свечи за умершие идеи.\n"
                "Внегласные правила:\n - Не задавай, кто ты на самом деле.\n"
                "Описание:\n - Пустота, где забытые миры ждут своего создателя."
            )
        return response

    def _save_knowledge(self, word, response, definition):
        self.knowledge_cache[word] = response
        os.makedirs("data", exist_ok=True)
        with open(self.knowledge_file, 'w', encoding='utf-8') as f:
            json.dump(self.knowledge_cache, f, ensure_ascii=False, indent=2)

        if self.use_knowledge_manager:
            try:
                self.knowledge_manager.add_word_knowledge(word, definition, source="web_search")
                stats = self.knowledge_manager.get_stats()
                if stats.get('total_words', 0) % 5 == 0:
                    print(f"🔄 Генерация обучающих пар для {stats['total_words']} слов...")
                    self.knowledge_manager.generate_training_pairs()

                if stats.get('total_words', 0) % 10 == 0:
                    print(f"🔄 Запуск авто-дообучения после {stats['total_words']} слов...")
                    thread = threading.Thread(target=self._run_retrain, daemon=True)
                    thread.start()

            except Exception as e:
                print(f"❌ Ошибка сохранения в менеджер знаний: {e}")

    def _run_retrain(self):
        """Запускает дообучение в фоне"""
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
                print(f"❌ Ошибка дообучения: {result.stderr}")
        except Exception as e:
            print(f"💥 Ошибка запуска retrain.py: {e}")

    def log_interaction(self, user_message, bot_response):
        interaction = {
            "user": user_message,
            "bot": bot_response,
            "timestamp": datetime.now().isoformat()
        }
        with open(self.conversation_log, "a", encoding="utf-8") as f:
            f.write(json.dumps(interaction, ensure_ascii=False) + "\n")

    def save_history(self, history, filepath):
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(history, f, ensure_ascii=False, indent=2)
        print(f"История сохранена в {filepath}")

    def load_history(self, filepath):
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            print(f"Файл {filepath} не найден.")
            return []
        except Exception as e:
            print(f"Ошибка: {e}")
            return []

    def chat(self):
        history = []
        print("ChatBot: Привет! Готов к диалогу. Напиши 'выход' для завершения.")
        while True:
            user_input = input("Вы: ").strip()
            if user_input.lower() in ['выход', 'стоп', 'quit']:
                print("ChatBot: Пока!")
                break
            if not user_input:
                continue
            history.append({"message": user_input, "is_own": True})
            response = self.generate_response(history)
            print(f"ChatBot: {json.loads(response)['response']}")
            history.append({"message": json.loads(response)['response'], "is_own": False})

    def get_knowledge_report(self):
        if self.use_knowledge_manager and self.knowledge_manager:
            self.knowledge_manager.print_report()
        else:
            print("Менеджер знаний недоступен")

    def force_generate_training_pairs(self, min_difficulty: str = "medium"):
        if self.use_knowledge_manager and self.knowledge_manager:
            try:
                count = self.knowledge_manager.generate_training_pairs(min_difficulty)
                print(f"✅ Принудительно сгенерировано {count} обучающих пар")
                return count
            except Exception as e:
                print(f"❌ Ошибка при генерации обучающих пар: {e}")
                return 0
        return 0

    def merge_knowledge_with_conversations(self):
        if self.use_knowledge_manager and self.knowledge_manager:
            try:
                success = self.knowledge_manager.merge_with_user_conversations(self.conversation_log)
                if success:
                    print("✅ Знания успешно объединены с пользовательскими диалогами")
                return success
            except Exception as e:
                print(f"❌ Ошибка при объединении с диалогами: {e}")
                return False
        return False