# Wuglarst/src/chatbot.py

import torch
import joblib
import numpy as np
import re
import json
import os
from .chat_model import ChatNN
from .web_search import WebSearch
from datetime import datetime

# Импортируем KnowledgeManager
try:
    from knowledge_manager import KnowledgeManager
    knowledge_manager_available = True
except ImportError:
    print("⚠️ knowledge_manager не найден. Установите сначала.")
    knowledge_manager_available = False


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

        # Кэш знаний (для быстрого доступа)
        self.knowledge_cache = {}
        self.knowledge_file = "data/knowledge_cache.json"

        # Загружаем кэш при старте
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

    def generate_response(self, messages, mode="chat"):
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

        # === Режим narrative → текст в "response" ===
        if mode == "narrative":
            response_text = self._generate_narrative(context)
            return json.dumps({"response": response_text}, ensure_ascii=False)

        # === Режим world_gen → объект "world" ===
        elif mode == "world_gen":
            genre, tags = self._extract_genre_tags(last_user_msg)
            world_data = self._generate_world_json(genre, tags)
            # Оборачиваем в "world", чтобы клиент понял тип
            return json.dumps({"world": world_data}, ensure_ascii=False)

        # === Обычный чат + поиск слов ===
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

        # === Обычный ответ модели ===
        input_text = last_user_msg
        seq = self._text_to_sequence(input_text)
        input_tensor = torch.tensor([seq], dtype=torch.long).to(self.device)

        with torch.no_grad():
            logits, _ = self.model(input_tensor)
            predicted_indices = logits.argmax(dim=-1).cpu().numpy()[0]

        response = self._sequence_to_text(predicted_indices).strip() or "Я здесь! 🤖"
        self.log_interaction(last_user_msg, response)
        return json.dumps({"response": response}, ensure_ascii=False)

    def _extract_genre_tags(self, message):
        """Извлекает жанр и теги из сообщения"""
        genre_match = re.search(r"Жанр:\s*([^\.\n]+)", message)
        tags_match = re.search(r"Темы:\s*([^\.\n]+)", message)
        genre = genre_match.group(1).strip() if genre_match else "Фэнтези"
        tags = tags_match.group(1).strip() if tags_match else "нет дополнительных тегов"
        return genre, tags

    def _generate_world_json(self, genre: str, tags: str) -> dict:
        """Генерирует мир в формате JSON"""
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
        print(f"[DEBUG] Raw model output: {raw_text}")

        # Пытаемся извлечь JSON
        world_data = self._extract_json_from_text(raw_text)
        if world_data:
            print("[INFO] JSON успешно извлечён из ответа модели")
            # Валидируем структуру
            if self._validate_world_structure(world_data):
                self.log_interaction(f"world_gen: {genre}, {tags}", json.dumps(world_data))
                return world_data
            else:
                print("[WARNING] Структура JSON некорректна. Пытаемся исправить.")
                # Пытаемся починить структуру
                world_data = self._fix_world_structure(world_data)
                if self._validate_world_structure(world_data):
                    print("[INFO] Структура JSON успешно исправлена")
                    self.log_interaction(f"world_gen: {genre}, {tags}", json.dumps(world_data))
                    return world_data

        # Если JSON не получен или неисправим — возвращаем пустую структуру
        empty_structure = {
            "name": "",
            "laws": [],
            "traditions": [],
            "unspoken_rules": [],
            "description": ""
        }
        print("[WARNING] Модель не сгенерировала корректный JSON. Возвращаем пустую структуру.")
        self.log_interaction(f"world_gen: {genre}, {tags}", json.dumps(empty_structure))
        return empty_structure

    def _extract_json_from_text(self, text: str) -> dict:
        """Извлекает JSON из текста"""
        try:
            start = text.find("{")
            end = text.rfind("}") + 1
            if start == -1 or end == 0:
                return None
            json_str = text[start:end]
            return json.loads(json_str)
        except Exception as e:
            print(f"[ERROR] Не удалось распарсить JSON: {e}")
            return None

    def _validate_world_structure(self, data: dict) -> bool:
        """Проверяет, что структура мира корректна"""
        required_keys = ['name', 'laws', 'traditions', 'unspoken_rules', 'description']
        return all(key in data for key in required_keys) and \
               isinstance(data['laws'], list) and \
               isinstance(data['traditions'], list) and \
               isinstance(data['unspoken_rules'], list) and \
               isinstance(data['name'], str) and \
               isinstance(data['description'], str)

    def _fix_world_structure(self, data: dict) -> dict:
        """Пробует починить структуру мира, добавляя недостающие поля"""
        fixed = {
            'name': data.get('name', 'Мир без имени'),
            'laws': data.get('laws', []) if isinstance(data.get('laws'), list) else [],
            'traditions': data.get('traditions', []) if isinstance(data.get('traditions'), list) else [],
            'unspoken_rules': data.get('unspoken_rules', []) if isinstance(data.get('unspoken_rules'), list) else [],
            'description': data.get('description', 'Описание отсутствует')
        }
        return fixed

    def _generate_narrative(self, context):
        """Режим narrative — остаётся текстовым"""
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
        """Сохраняет знания в кэш и менеджер"""
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
            except Exception as e:
                print(f"❌ Ошибка сохранения в менеджер знаний: {e}")

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