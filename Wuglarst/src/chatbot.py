# Wuglarst/src/chatbot.py

import torch
import json
import os
import re
import random
from datetime import datetime
from typing import List, Dict, Any
from . import chat_model
from .chat_model import ChatNN
from .web_search import WebSearch
from .cultural_references import get_cultural_phrase
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


class SimpleTokenizer:
    """Токенизатор, совместимый с tokenizer.json"""
    def __init__(self, tokenizer_path: str):
        with open(tokenizer_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        self.vocab = data["vocab"]
        self.inverse_vocab = data["inverse_vocab"]
        self.pad_token_id = self.vocab["<PAD>"]
        self.eos_token_id = self.vocab["<EOS>"]
        self.unk_token_id = self.vocab["<UNK>"]

    def encode(self, text: str, add_eos: bool = False, max_length: int = 64) -> List[int]:
        words = text.lower().split()
        ids = [self.vocab.get(word, self.unk_token_id) for word in words]
        if add_eos:
            ids.append(self.eos_token_id)
        if len(ids) >= max_length:
            ids = ids[:max_length-1] + [ids[-1]]  # сохраняем последний токен
        else:
            ids += [self.pad_token_id] * (max_length - len(ids))
        return ids

    def decode(self, token_ids: List[int]) -> str:
        words = []
        for idx in token_ids:
            if idx in [self.pad_token_id, self.eos_token_id]:
                break
            word = self.inverse_vocab.get(idx, "<UNK>")
            if word not in ["<PAD>", "<UNK>", "<EOS>"]:
                words.append(word)
        return " ".join(words)


class ChatBot:
    def __init__(self, model_path: str, data_path: str, device=None):
        """
        :param model_path: путь к модели (model.pth)
        :param data_path: путь к tokenizer.json
        :param device: 'cuda' или 'cpu'
        """
        self.device = device or ("cuda" if torch.cuda.is_available() else "cpu")
        self.tokenizer_path = data_path
        self.model_path = model_path

        # Загружаем токенизатор
        self.tokenizer = SimpleTokenizer(self.tokenizer_path)
        self.vocab_size = len(self.tokenizer.vocab)
        self.max_length = 64  # Должно совпадать с обучением

        # Загружаем модель
        self.model = ChatNN(
            vocab_size=self.vocab_size,
            embedding_dim=128,
            hidden_dim=256,
            num_layers=2,
            max_length=self.max_length,
            pad_token_id=self.tokenizer.pad_token_id,
            eos_token_id=self.tokenizer.eos_token_id
        ).to(self.device)

        try:
            state_dict = torch.load(self.model_path, map_location=self.device)
            self.model.load_state_dict(state_dict, strict=False)
            self.model.eval()
            print(f"✅ Модель загружена: {self.model_path} на {self.device}")
        except Exception as e:
            raise RuntimeError(f"❌ Не удалось загрузить модель: {e}")

        # Поиск и знания
        self.web_search = WebSearch()
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
        """Загружает кэш знаний"""
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
        """Сохраняет знание в кэш"""
        self.knowledge_cache[word] = response
        with open(self.knowledge_file, "w", encoding="utf-8") as f:
            json.dump(self.knowledge_cache, f, ensure_ascii=False, indent=2)

    def _clean_text(self, text: str) -> str:
        """Очистка текста"""
        if not isinstance(text, str) or not text.strip():
            return ""
        text = text.lower()
        text = re.sub(r'[^а-яёa-z0-9\s?!,.]', '', text)
        text = re.sub(r'\s+', ' ', text).strip()
        replacements = {
            "яне": "я не", "тыне": "ты не", "онне": "он не", "она нее": "она не",
            "незнаю": "не знаю", "хз": "не знаю", "ок": "окей", "спс": "спасибо",
            "прив": "привет", "пока": "пока", "здарова": "здравствуй"
        }
        for k, v in replacements.items():
            text = text.replace(k, v)
        return text

    def _generate_response_with_sampling(
        self,
        input_text: str,
        max_length: int = 32,
        temperature: float = 0.8,
        top_p: float = 0.9
    ) -> str:
        """Генерация ответа с nucleus sampling"""
        self.model.eval()
        tokens = self._clean_text(input_text).split()
        input_ids = self.tokenizer.encode(" ".join(tokens), add_eos=False)
        input_tensor = torch.tensor([input_ids], dtype=torch.long).to(self.device)

        # Создаём маску
        mask = (input_tensor != self.tokenizer.pad_token_id).float().to(self.device)

        generated_ids = []
        current_input = input_tensor
        current_mask = mask

        with torch.no_grad():
            for _ in range(max_length):
                logits = self.model(current_input, mask=current_mask)[:, -1, :]
                logits = logits / temperature

                # Top-p (nucleus sampling)
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
                    break
                if next_token != self.tokenizer.pad_token_id and next_token != self.tokenizer.unk_token_id:
                    generated_ids.append(next_token)

                # Обновляем вход
                new_token = torch.tensor([[next_token]], device=self.device)
                current_input = torch.cat([current_input, new_token], dim=1)
                current_input = current_input[:, -self.max_length:]

                new_mask = torch.ones((1, 1), device=self.device)
                current_mask = torch.cat([current_mask, new_mask], dim=1)
                current_mask = current_mask[:, -self.max_length:]

        return self.tokenizer.decode(generated_ids).strip()

    def generate_response(self, messages: List[Dict[str, str]], mode: str = "chat") -> str:
        """
        Генерация ответа.
        :param messages: [{"message": "...", "is_own": True/False}]
        :param mode: "chat", "world_gen", "narrative"
        """
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
            return json.dumps({"response": "Я здесь! 🤖"}, ensure_ascii=False)

        # === Режим narrative ===
        if mode == "narrative":
            context_str = "\n".join(context)
            prompt = (
                "Ты — мастер вселенных. Создаёшь глубокие, логичные и атмосферные миры.\n"
                "Формат:\nНазвание:\n - ...\nЗаконы общества:\n - ...\n...\n\n"
                f"История диалога:\n{context_str}\nБот:"
            )
            response = self._generate_response_with_sampling(prompt, max_length=64)
            required = ["Название:", "Законы общества:", "Традиции:"]
            if not all(kw in response for kw in required):
                response = (
                    "Название:\n - Мир без имени\n"
                    "Законы общества:\n - Никто не вспоминает прошлое.\n"
                    "Традиции:\n - Каждую полночь зажигают свечи за умершие идеи.\n"
                    "Внегласные правила:\n - Не задавай, кто ты на самом деле."
                )
            return json.dumps({"response": response}, ensure_ascii=False)

        # === Режим world_gen ===
        elif mode == "world_gen":
            genre_match = re.search(r"Жанр:\s*([^\.\n]+)", last_user_msg)
            tags_match = re.search(r"Темы:\s*([^\.\n]+)", last_user_msg)
            genre = genre_match.group(1).strip() if genre_match else "Фэнтези"
            tags = tags_match.group(1).strip() if tags_match else ""

            prompt = f"Создай мир: {genre}"
            if tags:
                prompt += f", {tags}"

            response = self._generate_response_with_sampling(prompt, max_length=64)
            return json.dumps({"world": response}, ensure_ascii=False)

        # === Режим chat ===
        elif mode == "chat":
            # Проверка неизвестных слов
            tokens = self._clean_text(last_user_msg).split()
            unknown_words = [t for t in tokens if t not in self.tokenizer.vocab]
            if unknown_words:
                word = unknown_words[0]
                if word in self.knowledge_cache:
                    return json.dumps({"response": self.knowledge_cache[word]}, ensure_ascii=False)

                try:
                    definition = self.web_search.lookup(word)
                    if definition and len(definition) > 5:
                        response = f"🔍 Я не знал слово «{word}», но нашёл:\n\n{definition.strip()}"
                        self._save_knowledge_cache(word, response)
                        self._trigger_knowledge_learning(word, definition)
                        return json.dumps({"response": response}, ensure_ascii=False)
                except Exception as e:
                    print(f"❌ Ошибка поиска: {e}")

            # Генерация основного ответа
            base_response = self._generate_response_with_sampling(last_user_msg)

            # Fallback
            if not base_response or len(base_response.split()) < 2:
                base_response = random.choice([
                    "Привет! Я здесь.",
                    "Расскажи больше?",
                    "Интересно...",
                    "А ты как думаешь?"
                ])

            # Культурная отсылка
            final_response = base_response
            if random.random() < 0.25:
                phrase = get_cultural_phrase()
                style = random.choice(['prefix', 'suffix'])
                if style == 'prefix':
                    final_response = f"{phrase} {base_response}"
                else:
                    final_response = f"{base_response} ({phrase})"

            self.log_interaction(last_user_msg, final_response)
            return json.dumps({"response": final_response}, ensure_ascii=False)

    def _trigger_knowledge_learning(self, word: str, definition: str):
        """Запускает обучение при накоплении знаний"""
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
        """Фоновое дообучение"""
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
            response = self.generate_response(history)
            print(f"ChatBot: {json.loads(response)['response']}")
            history.append({"message": json.loads(response)['response'], "is_own": False})