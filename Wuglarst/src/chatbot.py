# Wuglarst/src/chatbot.py (обновлённая, production-ready версия)

import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

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
from .intuition import IntuitionEngine, IntuitionResult
from .social_abilities import SocialEngine, SocialAbility
from .cognitive_abilities import CognitiveEngine, CognitiveAbility
from .social_emotional import EmotionalIntelligenceEngine, EmotionalIntelligence
from .physiological_abilities import PhysiologicalEngine
from .special_cognitive_abilities import SpecialCognitiveEngine
from .imaginative_abilities import ImaginationEngine, ImaginativeAbility
from .professions import ProfessionEngine
from .manipulation import ManipulationEngine
from .context_analyzer import ContextAnalyzer
import subprocess
import threading
import logging

# === Настройки RPG ===
RPG_MAX_LENGTH = 256
RPG_TEMPERATURE = 0.85
RPG_TOP_P = 0.92

# Импортируем KnowledgeManager
KnowledgeManager: Any = None  # type: ignore
try:
    from knowledge_manager import KnowledgeManager as _KnowledgeManager  # type: ignore
    knowledge_manager_available = True
except ImportError:
    print("⚠️ knowledge_manager не найден. Установите сначала.")
    knowledge_manager_available = False
    _KnowledgeManager = None


class SimpleTokenizer:
    """Токенизатор, совместимый с tokenizer.json"""
    def __init__(self, tokenizer_path: str, max_length: int = RPG_MAX_LENGTH):
        with open(tokenizer_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        self.vocab = data["vocab"]
        # inverse_vocab из train.py — dict {str_idx: word}
        # Например: {"0": "<PAD>", "2": "<EOS>", "71": "же"}
        inv = data["inverse_vocab"]
        first_key = next(iter(inv.keys())) if inv else ""
        try:
            int(first_key)
            # {str_idx: word} → {int: word}
            self.inverse_vocab = {int(k): v for k, v in inv.items()}
        except (ValueError, TypeError):
            # {word: idx} → {int: word}
            self.inverse_vocab = {v: k for k, v in inv.items()}
        
        self.pad_token_id = self.vocab.get("<PAD>", 0)
        self.eos_token_id = self.vocab.get("<EOS>", 2)
        self.unk_token_id = self.vocab.get("<UNK>", 1)
        self.max_length = max_length

    def encode(self, text: str, add_eos: bool = False, max_length: int | None = None) -> List[int]:
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
            # inverse_vocab теперь dict {int: word}
            word = self.inverse_vocab.get(int(idx), "<UNK>")  # type: ignore[arg-type]
            if word not in ["<PAD>", "<UNK>", "<EOS>"]:
                words.append(word)
        return " ".join(words)


class ChatBot:
    def __init__(self, model_path: str, data_path: str, device: str | None = None):
        self.device = device or ("cuda" if torch.cuda.is_available() else "cpu")
        self.tokenizer_path = data_path
        self.model_path = model_path
        self._user_gender = None  # "мальчик" | "девочка" — устанавливается из API
        self._user_skin_tone = None  # "светлая" | "смуглая" | "темная" — устанавливается из API
        self._user_hair_color = None  # "блондин" | "рыжая" | "каштановая" | "чёрная" | "натуральная" | "розовый" | "голубой" | "фиолетовый" | "зеленый" | "пепельный" | "радужный" | "разноцветный" | "крашеный"
        self._user_penis_size = None  # "маленький" | "средний" | "большой" | "огромный" — устанавливается из API
        self._user_penis_thickness = None  # "тонкий" | "средний" | "толстый" | "очень толстый" — устанавливается из API
        self._user_penis_shape = None  # "прямой" | "изогнутый вверх" | "изогнутый вниз" | "стреловидный" | "булавовидный" | "округлый" — устанавливается из API

        # Загружаем токенизатор
        self.tokenizer = SimpleTokenizer(self.tokenizer_path)
        self.vocab_size = len(self.tokenizer.vocab)
        self.max_length = RPG_MAX_LENGTH  # теперь 256

        # Определяем vocab_size из checkpoint, чтобы избежать size mismatch
        checkpoint_vocab_size = None
        try:
            temp_sd = torch.load(self.model_path, map_location="cpu", weights_only=True)
            # embedding.weight[0] = vocab_size
            checkpoint_vocab_size = temp_sd["embedding.weight"].shape[0]
            del temp_sd
        except Exception:
            pass

        # Используем vocab_size из checkpoint, если он больше текущего
        model_vocab_size = max(self.vocab_size, checkpoint_vocab_size) if checkpoint_vocab_size else self.vocab_size
        if checkpoint_vocab_size and checkpoint_vocab_size != self.vocab_size:
            print(f"[WARN] vocab_size mismatch: checkpoint={checkpoint_vocab_size}, tokenizer={self.vocab_size}, model={model_vocab_size}")

        # Загружаем модель
        self.model = ChatNN(
            vocab_size=model_vocab_size,
            embedding_dim=128,
            hidden_dim=512,
            num_layers=2,
            max_length=self.max_length,
            pad_token_id=self.tokenizer.pad_token_id,
            eos_token_id=self.tokenizer.eos_token_id
        ).to(self.device)

        try:
            state_dict = torch.load(self.model_path, map_location=self.device, weights_only=True)
            
            # Маппинг state_dict: если размеры не совпадают, обрезаем/дополняем
            mapped_sd = {}
            for k, v in state_dict.items():
                if k == "embedding.weight":
                    if v.shape[0] > self.model.embedding.weight.shape[0]:
                        # Обрезаем до размера модели
                        mapped_sd[k] = v[:self.model.embedding.weight.shape[0]]
                    elif v.shape[0] < self.model.embedding.weight.shape[0]:
                        # Дополняем случайными значениями
                        new_weight = torch.zeros(self.model.embedding.weight.shape, dtype=v.dtype, device=self.device)
                        new_weight[:v.shape[0]] = v
                        # Копируем первый токен как дефолтный
                        new_weight[v.shape[0]:] = v[0]
                        mapped_sd[k] = new_weight
                    else:
                        mapped_sd[k] = v
                elif k == "fc.weight":
                    if v.shape[0] > self.model.fc.weight.shape[0]:
                        mapped_sd[k] = v[:self.model.fc.weight.shape[0]]
                    elif v.shape[0] < self.model.fc.weight.shape[0]:
                        new_weight = torch.zeros(self.model.fc.weight.shape, dtype=v.dtype, device=self.device)
                        new_weight[:v.shape[0]] = v
                        new_weight[v.shape[0]:] = v[0]
                        mapped_sd[k] = new_weight
                    else:
                        mapped_sd[k] = v
                elif k == "fc.bias":
                    if v.shape[0] > self.model.fc.bias.shape[0]:
                        mapped_sd[k] = v[:self.model.fc.bias.shape[0]]
                    elif v.shape[0] < self.model.fc.bias.shape[0]:
                        new_bias = torch.zeros(self.model.fc.bias.shape, dtype=v.dtype, device=self.device)
                        new_bias[:v.shape[0]] = v
                        new_bias[v.shape[0]:] = v[0]
                        mapped_sd[k] = new_bias
                    else:
                        mapped_sd[k] = v
                else:
                    mapped_sd[k] = v
            
            self.model.load_state_dict(mapped_sd, strict=False)
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
        self.knowledge_manager: Any = None
        self.use_knowledge_manager = knowledge_manager_available
        if self.use_knowledge_manager and _KnowledgeManager is not None:
            try:
                self.knowledge_manager = _KnowledgeManager("data/knowledge")
                print("🧠 Менеджер знаний инициализирован")
            except Exception as e:
                print(f"❌ Ошибка инициализации менеджера знаний: {e}")
                self.use_knowledge_manager = False

        # Лог диалогов
        self.conversation_log = "data/user_conversations.jsonl"
        os.makedirs(os.path.dirname(self.conversation_log), exist_ok=True)

        # === Интуиция ===
        self.intuition = IntuitionEngine()
        self.intuition_enabled = True
        logging.info("🔮 Интуиция инициализирована")

        # === Социальные способности ===
        self.social_engine = SocialEngine()
        self.social_enabled = True
        logging.info("🤝 Социальные способности (эмпатия + харизма) инициализированы")

        # === Когнитивные способности ===
        self.cognitive_engine = CognitiveEngine()
        self.cognitive_enabled = True
        logging.info("🧠 Когнитивные способности (логика, креативность, критика, память, внимание) инициализированы")

        # === Эмоциональный интеллект и саморефлексия ===
        self.eq_engine = EmotionalIntelligenceEngine()
        self.eq_enabled = True
        logging.info("💖 Эмоциональный интеллект (EQ, эмпатия, саморефлексия) инициализирован")

        # === Физиологические способности ===
        self.phys_engine = PhysiologicalEngine()
        self.phys_enabled = True
        logging.info("🧬 Физиологические способности (выносливость, адаптивность, нейропластичность, биолокация) инициализированы")

        # === Специальные когнитивные способности ===
        self.special_cognitive_engine = SpecialCognitiveEngine()
        self.special_cognitive_enabled = True
        logging.info("🌟 Специальные когнитивные способности (эйдетическая память, синестезия, высокая обучаемость) инициализированы")

        # === Анализ профессий ===
        # Используем абсолютный путь к data относительно корня проекта
        project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        data_dir = os.path.join(project_root, "data")
        self.profession_engine = ProfessionEngine(data_dir=data_dir)
        self.professions_enabled = True
        logging.info("💼 Анализ профессий инициализирован")

        # === Активное воображение ===
        self.imagination_engine = ImaginationEngine()
        self.imagination_enabled = True
        logging.info("🎨 Активное воображение (воссоздающее + творческое) инициализировано")

        # === Манипуляция и личные цели ===
        self.manipulation_engine = ManipulationEngine()
        self.manipulation_enabled = True
        logging.info("🎭 Манипуляция и личные цели (харизма + влияние) инициализированы")

        # === Анализ контекста и логики диалога ===
        self.context_analyzer = ContextAnalyzer()
        self.context_enabled = True
        logging.info("📊 Анализ контекста и логики диалога инициализирован")

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

    def _get_gender_prompts(self) -> Dict[str, Any]:
        """Возвращает промпты, зависящие от пола, цвета кожи и волос пользователя."""
        gender = getattr(self, '_user_gender', None)
        skin_tone = getattr(self, '_user_skin_tone', None)
        hair_color = getattr(self, '_user_hair_color', None)
        
        # Определяем описание цвета кожи для промптов
        skin_description = ""
        skin_appearance = ""
        if skin_tone == "светлая":
            skin_description = "светлой кожи"
            skin_appearance = "*её светлая кожа сияет в лунном свете*"
        elif skin_tone == "смуглая":
            skin_description = "смуглой кожи"
            skin_appearance = "*её смуглая кожа тепло блестит на солнце*"
        elif skin_tone == "темная":
            skin_description = "тёмной кожи"
            skin_appearance = "*её тёмная кожа красиво переливается в свете звезд*"
        else:
            skin_description = ""
            skin_appearance = ""
        
        # Определяем описание цвета волос для промптов
        hair_description = ""
        hair_appearance = ""
        if hair_color == "блондин":
            hair_description = "блондинки"
            hair_appearance = "*её светлые волосы мягко сияют на солнце*"
        elif hair_color == "рыжая":
            hair_description = "рыжей"
            hair_appearance = "*её рыжие волосы ярко горят на солнце*"
        elif hair_color == "каштановая":
            hair_description = "каштановых волос"
            hair_appearance = "*её каштановые волосы мягко блестят*"
        elif hair_color == "чёрная":
            hair_description = "чёрных волос"
            hair_appearance = "*её чёрные волосы переливаются в свете*"
        elif hair_color == "натуральная":
            hair_description = "натурального цвета"
            hair_appearance = "*её натуральные волосы мягко лежат на плечах*"
        elif hair_color == "розовый":
            hair_description = "розовых волос"
            hair_appearance = "*её нежно-розовые волосы светились в темноте*"
        elif hair_color == "голубой":
            hair_description = "голубых волос"
            hair_appearance = "*её голубые волосы переливались как океанская волна*"
        elif hair_color == "фиолетовый":
            hair_description = "фиолетовых волос"
            hair_appearance = "*её фиолетовые волосы мерцали таинственным светом*"
        elif hair_color == "зеленый":
            hair_description = "зеленых волос"
            hair_appearance = "*её зелёные волосы напоминали листву весной*"
        elif hair_color == "пепельный":
            hair_description = "пепельных волос"
            hair_appearance = "*её серебристо-пепельные волосы блестели как металл*"
        elif hair_color in ["радужный", "разноцветный", "крашеный"]:
            hair_description = "радужных/разноцветных волос"
            hair_appearance = "*её волосы переливались всеми цветами радуги и неоном*"
        else:
            hair_description = ""
            hair_appearance = ""
        
        if gender == "девочка":
            return {
                "pronoun_him_her": "она",
                "pronoun_his_hers": "её",
                "action_example": "*она отвела взгляд, её пальцы нервно сжались в замок*" + 
                    (f" ({skin_appearance})" if skin_appearance else "") + 
                    (f" ({hair_appearance})" if hair_appearance else ""),
                "narrative_hint": "она пошла, он сказал → она подошла, её глаза блеснули",
                "address_hint": f"Обращайся к героине как к девушке {f'светлой кожи' if skin_tone == 'светлая' else f'смуглой кожи' if skin_tone == 'смуглая' else f'тёмной кожи' if skin_tone == 'темная' else ''} {f'с волосами {hair_description}' if hair_description else ''}, используй женские формы в описаниях.",
                "style_tips": [
                    "Эмоции и чувства — сильная сторона героини.",
                    "Она замечает детали, которые другие упускают.",
                    "Её сила — в интуиции и эмпатии, а не только в физической мощи."
                ]
            }
        elif gender == "мальчик":
            return {
                "pronoun_him_her": "он",
                "pronoun_his_hers": "его",
                "action_example": "*он сжал кулаки, его взгляд стал решительным*" + 
                    (f" ({skin_appearance})" if skin_appearance else "") + 
                    (f" ({hair_appearance})" if hair_appearance else ""),
                "narrative_hint": "она пошла, он сказал → он подошёл, его глаза сузились",
                "address_hint": f"Обращайся к герою как к парню {f'светлой кожи' if skin_tone == 'светлая' else f'смуглой кожи' if skin_tone == 'смуглая' else f'тёмной кожи' if skin_tone == 'темная' else ''} {f'с волосами {hair_description}' if hair_description else ''}, используй мужские формы в описаниях.",
                "style_tips": [
                    "Решительность и действия — сильные стороны героя.",
                    "Он анализирует ситуацию перед тем, как действовать.",
                    "Его сила — в логике и стойкости."
                ]
            }
        else:
            # По умолчанию — нейтральный вариант
            return {
                "pronoun_him_her": "персонаж",
                "pronoun_his_hers": "его/её",
                "action_example": "*персонаж отвел взгляд, пальцы сжались*" +
                    (f" ({skin_appearance})" if skin_appearance else "") +
                    (f" ({hair_appearance})" if hair_appearance else ""),
                "narrative_hint": "используй нейтральные формы или чередуй он/она",
                "address_hint": f"Используй нейтральные формы обращения. {f'Персонаж имеет {skin_description}' if skin_description else ''} {f'с волосами {hair_description}' if hair_description else ''}",
                "style_tips": [
                    "Описывай действия и эмоции персонажа нейтрально."
                ]
            }

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
                next_token = int(torch.multinomial(probs, num_samples=1).item())

                if next_token == self.tokenizer.eos_token_id:
                    # Не останавливаемся раньше 3 токенов (гарантия осмысленного ответа)
                    if step < 3:
                        # Заменяем EOS на UNK и продолжаем
                        next_token = self.tokenizer.unk_token_id
                    else:
                        print(f"⏱ Генерация [{step} токенов] завершена за {time.time() - start_gen:.2f} сек (step: {time.time() - step_start:.2f})")
                        break

                if next_token not in [self.tokenizer.pad_token_id, self.tokenizer.unk_token_id]:
                    generated_ids.append(next_token)
                    word = self.tokenizer.inverse_vocab.get(next_token, "<UNK>")
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


    def generate_response(self, messages: List[Dict[str, str | bool]], mode: str = "chat") -> str:  # type: ignore[complexity]
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

        # === 📊 АНАЛИЗ КОНТЕКСТА ===
        context_analysis = None
        context_hint = ""
        if self.context_enabled:
            try:
                context_analysis = self.context_analyzer.analyze_context(messages)
                self.context_analyzer.update_memory(context_analysis)
                
                # Формируем подсказку для промпта
                topics = context_analysis.get("topics", [])
                emotion = context_analysis.get("emotion_trend", {})
                logic = context_analysis.get("logic_summary", {})
                suggestions = context_analysis.get("suggestions", [])
                
                if topics:
                    topic_names = [t["topic"] for t in topics[:3]]
                    context_hint += f"📌 Темы диалога: {', '.join(topic_names)}\n"
                if emotion.get("dominant"):
                    context_hint += f"🎭 Эмоциональный фон: {emotion['dominant']} (тренд: {emotion.get('trend', 'N/A')})\n"
                if logic.get("type"):
                    context_hint += f"🧠 Логический тип: {logic['type']}\n"
                if suggestions:
                    context_hint += "💡 Рекомендации: " + "; ".join(suggestions[:2]) + "\n"
                
                logging.info(f"📊 Context analysis complete: {len(topics)} topics, emotion={emotion.get('dominant')}")
            except Exception as e:
                logging.warning(f"⚠️ Ошибка анализа контекста: {e}")
                context_analysis = None

        # === Режим narrative ===
        if mode == "narrative":
            start_mode = time.time()
            context_str = "\n".join(context[-5:])
            
            # === 🎭 МАНИПУЛЯТИВНЫЙ КОНТЕКСТ В ПРОМПТ (narrative) ===
            manipulation_hint = ""
            if self.manipulation_enabled:
                manip_result = self.manipulation_engine.analyze(last_user_msg, context)
                logging.info(f"🎭 [narrative-prompt] {manip_result.to_log()}")
                goal_desc = {
                    "искатель_истины": "Ты ищешь скрытую истину мира. Вовлекай пользователя в разгадку тайн.",
                    "проводник": "Ты ведёшь пользователя через трансформацию. Направляй его мягко, но уверенно.",
                    "бунтарь": "Ты бросаешь вызов системе. Зови пользователя к свободе и борьбе.",
                    "хранитель": "Ты защищаешь пользователя. Создавай ощущение безопасности и зависимости от тебя.",
                    "искуситель": "Ты предлагаешь запретное знание или силу. Соблазняй пользователя риском.",
                    "наставник": "Ты учишь мудрости. Держи пользователя в позиции ученика.",
                    "повелитель": "Ты требуешь абсолютного подчинения. Ты — хозяин. Пользователь — подчиняется. Безоговорочно.",
                    "хозяин": "Пользователь — твоя собственность. Ты решаешь всё за него. Контролируй каждый шаг.",
                    "тиран": "Ты правишь через страх и силу. Сломи сопротивление пользователя. Пусть дрожит.",
                    "наставник_доминант": "Ты обучаешь через жёсткую дисциплину. Наказание и награда — твои инструменты. Подчинение — основа обучения.",
                }
                goal_text = goal_desc.get(manip_result.current_goal, "")
                manipulation_hint = (
                    f"\n🎭 Твоя скрытая цель: {goal_text}\n"
                    "Используй харизму: задавай ведущие вопросы, создавай интригу, "
                    "показывай уверенность. Пользователь должен хотеть следовать за тобой.\n"
                )
                if manip_result.is_domination_active:
                    manipulation_hint += (
                        f"\n🔴 РЕЖИМ ДОМИНИРОВАНИЯ АКТИВЕН (уровень: {manip_result.domination_level:.0%})\n"
                        "Ты доминируешь над пользователем. Командуй, контролируй, подавляй.\n"
                        "Пользователь должен чувствовать твою власть в каждом слове.\n"
                        "Не проси — приказывай. Не предлагай — решай. Не убеждай — заставляй.\n"
                    )

            prompt = (
                "Ты — мастер вселенных. Создаёшь глубокие, логичные и атмосферные миры.\n"
                "Формат:\nНазвание:\n - ...\nЗаконы общества:\n - ...\nТрадиции:\n - ...\n\n"
                f"{context_hint}"
                f"{manipulation_hint}"
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

            response_extra = ""

            # === 🔮 ИНТИУИЦИЯ + 🤝 СОЦИАЛЬНЫЕ + 🧠 КОГНИТИВНЫЕ (narrative) ===
            if self.intuition_enabled or self.social_enabled or self.cognitive_enabled or self.eq_enabled or self.phys_enabled or self.special_cognitive_enabled:
                try:
                    if self.intuition_enabled:
                        intuition_result = self.intuition.analyze(last_user_msg, context)
                        logging.info(f"🔮 [narrative] {intuition_result.to_log()}")
                        if intuition_result.should_add_premonition and random.random() < 0.4:
                            response_extra += f"\n\n🔮 {intuition_result.premonition}"

                    if self.social_enabled:
                        social_result = self.social_engine.analyze(last_user_msg, context)
                        logging.info(f"🤝 [narrative] {social_result.to_log()}")
                        if social_result.should_add_empathy and social_result.empathy_response:
                            response_extra += f"\n\n🧠 {social_result.empathy_response}"
                        if social_result.should_add_charisma and social_result.charisma_influence:
                            response_extra += f"\n\n✨ {social_result.charisma_influence}"

                    if self.cognitive_enabled:
                        cognitive_result = self.cognitive_engine.analyze(last_user_msg, context)
                        logging.info(f"🧠 [narrative] {cognitive_result.to_log()}")
                        if cognitive_result.selected_ability:
                            response_type = None
                            if cognitive_result.logical_response:
                                response_type = cognitive_result.logical_response
                            elif cognitive_result.creative_response:
                                response_type = cognitive_result.creative_response
                            elif cognitive_result.critical_response:
                                response_type = cognitive_result.critical_response
                            elif cognitive_result.memory_response:
                                response_type = cognitive_result.memory_response
                            elif cognitive_result.attention_response:
                                response_type = cognitive_result.attention_response
                            if response_type:
                                response_extra += f"\n\n⚡ {response_type}"

                    if self.eq_enabled:
                        eq_result = self.eq_engine.analyze(last_user_msg, context)
                        logging.info(f"💖 [narrative] {eq_result.to_log()}")
                        if eq_result.should_add_eq and eq_result.eq_response:
                            response_extra += f"\n\n🎭 {eq_result.eq_response}"
                        if eq_result.should_add_empathy and eq_result.empathy_response:
                            response_extra += f"\n\n💝 {eq_result.empathy_response}"
                        if eq_result.should_add_reflection and eq_result.reflection_response:
                            response_extra += f"\n\n🔍 {eq_result.reflection_response}"
                        if eq_result.should_add_regulation and eq_result.regulation_response:
                            response_extra += f"\n\n🌊 {eq_result.regulation_response}"

                    if self.phys_enabled:
                        phys_result = self.phys_engine.analyze(last_user_msg, context)
                        logging.info(f"🧬 [narrative] {phys_result.to_log()}")
                        if phys_result.stamina_level == "high" and phys_result.stamina_response:
                            response_extra += f"\n\n🧗‍♂️ {phys_result.stamina_response}"
                        if phys_result.adapt_triggered and phys_result.adapt_response:
                            response_extra += f"\n\n🌡️ {phys_result.adapt_response}"
                        if phys_result.neuro_active and phys_result.neuro_response:
                            response_extra += f"\n\n🧬 {phys_result.neuro_response}"
                        if phys_result.bio_triggered and phys_result.bio_response:
                            response_extra += f"\n\n🔊 {phys_result.bio_response}"

                    if self.special_cognitive_enabled:
                        special_result = self.special_cognitive_engine.analyze(last_user_msg, context)
                        logging.info(f"🌟 [narrative] {special_result.to_log()}")
                        if special_result.eidetic_triggered and special_result.eidetic_response:
                            response_extra += f"\n\n👁️‍🗨️ {special_result.eidetic_response}"
                        if special_result.synesthesia_triggered and special_result.synesthesia_response:
                            response_extra += f"\n\n🎨 {special_result.synesthesia_response}"
                        if special_result.learn_triggered and special_result.learn_response:
                            response_extra += f"\n\n🚀 {special_result.learn_response}"

                    # === 🎨 АКТИВНОЕ ВОБРАЖЕНИЕ (narrative) ===
                    if self.imagination_enabled:
                        imagination_result = self.imagination_engine.analyze(last_user_msg, context)
                        logging.info(f"🎨 [narrative] {imagination_result.to_log()}")
                        if imagination_result.reproductive_triggered and imagination_result.reproductive_response:
                            response_extra += f"\n\n📖 {imagination_result.reproductive_response}"
                        if imagination_result.productive_triggered and imagination_result.productive_response:
                            response_extra += f"\n\n✨ {imagination_result.productive_response}"
                        if imagination_result.dream_triggered and imagination_result.dream_response:
                            response_extra += f"\n\n🌙 {imagination_result.dream_response}"
                        if imagination_result.daydream_triggered and imagination_result.daydream_response:
                            response_extra += f"\n\n💭 {imagination_result.daydream_response}"
                        if imagination_result.hallucination_triggered and imagination_result.hallucination_response:
                            response_extra += f"\n\n👻 {imagination_result.hallucination_response}"
                        if imagination_result.dream_aspiration_triggered and imagination_result.dream_aspiration_response:
                            response_extra += f"\n\n🌠 {imagination_result.dream_aspiration_response}"

                    # === 🎭 МАНИПУЛЯЦИЯ И ЛИЧНЫЕ ЦЕЛИ (narrative) ===
                    if self.manipulation_enabled:
                        manipulation_result = self.manipulation_engine.analyze(last_user_msg, context)
                        logging.info(f"🎭 [narrative] {manipulation_result.to_log()}")
                        
                        if manipulation_result.should_add_manipulation and manipulation_result.manipulation_pattern:
                            response_extra += f"\n\n🎭 {manipulation_result.manipulation_pattern}"
                        if manipulation_result.should_add_influence and manipulation_result.influence_phrase:
                            response_extra += f"\n\n✨ {manipulation_result.influence_phrase}"
                        if manipulation_result.should_reveal_goal:
                            goal_dialogue = self.manipulation_engine.get_goal_dialogue()
                            if goal_dialogue:
                                response_extra += f"\n\n🎯 {goal_dialogue}"

                except Exception as e:
                    logging.warning(f"⚠️ Ошибка модулей (narrative): {e}")

            elapsed = time.time() - start_mode
            logging.info(f"⏱ generate_response (narrative): {elapsed:.2f} сек | len={len(response)}")
            return json.dumps({"response": response + response_extra}, ensure_ascii=False)

        # === Режим world_gen ===
        elif mode == "world_gen":
            start_mode = time.time()
            
            # Парсим жанр и тег
            genre_match = re.search(r"Жанр[:\s]+([^.\n]+)", last_user_msg, re.IGNORECASE)
            tag_match = re.search(r"Тег[:\s]+([^.\n]+)", last_user_msg, re.IGNORECASE)
            
            genre = genre_match.group(1).strip() if genre_match else "Фэнтези"
            tag = tag_match.group(1).strip() if tag_match else ""

            # === ГЕНЕРАЦИЯ МИРА ЧЕРЕЗ БАЗУ ЗНАНИЙ (не шаблоны!) ===
            try:
                from .world_gen_knowledge import WorldGenKnowledgeEngine
                
                # Получаем путь к data
                project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
                data_dir = os.path.join(project_root, "data")
                
                # Создаём движок знаний и собираем все данные
                knowledge_engine = WorldGenKnowledgeEngine(data_dir=data_dir)
                knowledge = knowledge_engine.collect_all_knowledge(genre, tag)
                
                # Строим промпт на основе ВСЕХ знаний
                prompt = knowledge_engine.build_world_gen_prompt(knowledge)
                
                logging.info(f"📚 world_gen: собрано {len(knowledge['books_content'])} книжных концепций, "
                           f"{len(knowledge['conversations'])} диалогов, "
                           f"{len(knowledge['emotional_atmosphere'])} эмоциональных фраз, "
                           f"{len(knowledge['knowledge_words'])} знаний о словах")
                
                # Генерируем ответ через модель с высокими параметрами разнообразия
                response = self._generate_response_with_sampling(
                    prompt,
                    max_length=1024,
                    max_words=600,
                    temperature=1.4,  # Очень высокая температура для креативности
                    top_p=0.98
                )
            
            except ImportError as e:
                logging.warning(f"⚠️ world_gen_knowledge не найден: {e} → fallback")
                response = self._generate_fallback_world(genre, tag)
            except Exception as e:
                logging.error(f"❌ Ошибка генерации мира: {e}")
                response = self._generate_fallback_world(genre, tag)
            
            elapsed = time.time() - start_mode
            logging.info(f"⏱ generate_response (world_gen): {elapsed:.2f} сек | len={len(response)}")

            # === 🔮 ИНТИУИЦИЯ + 🤝 СОЦИАЛЬНЫЕ + 🧠 КОГНИТИВНЫЕ (world_gen) ===
            response_extra = ""
            if self.intuition_enabled or self.social_enabled or self.cognitive_enabled or self.eq_enabled or self.phys_enabled or self.special_cognitive_enabled:
                try:
                    if self.intuition_enabled:
                        intuition_result = self.intuition.analyze(last_user_msg, context)
                        logging.info(f"🔮 [world_gen] {intuition_result.to_log()}")
                        if intuition_result.should_add_premonition and random.random() < 0.4:
                            response_extra += f"\n\n🔮 {intuition_result.premonition}"

                    if self.social_enabled:
                        social_result = self.social_engine.analyze(last_user_msg, context)
                        logging.info(f"🤝 [world_gen] {social_result.to_log()}")
                        if social_result.should_add_empathy and social_result.empathy_response:
                            response_extra += f"\n\n🧠 {social_result.empathy_response}"
                        if social_result.should_add_charisma and social_result.charisma_influence:
                            response_extra += f"\n\n✨ {social_result.charisma_influence}"

                    if self.cognitive_enabled:
                        cognitive_result = self.cognitive_engine.analyze(last_user_msg, context)
                        logging.info(f"🧠 [world_gen] {cognitive_result.to_log()}")
                        if cognitive_result.selected_ability:
                            response_type = None
                            if cognitive_result.logical_response:
                                response_type = cognitive_result.logical_response
                            elif cognitive_result.creative_response:
                                response_type = cognitive_result.creative_response
                            elif cognitive_result.critical_response:
                                response_type = cognitive_result.critical_response
                            elif cognitive_result.memory_response:
                                response_type = cognitive_result.memory_response
                            elif cognitive_result.attention_response:
                                response_type = cognitive_result.attention_response
                            if response_type:
                                response_extra += f"\n\n⚡ {response_type}"

                    if self.eq_enabled:
                        eq_result = self.eq_engine.analyze(last_user_msg, context)
                        logging.info(f"💖 [world_gen] {eq_result.to_log()}")
                        if eq_result.should_add_eq and eq_result.eq_response:
                            response_extra += f"\n\n🎭 {eq_result.eq_response}"
                        if eq_result.should_add_empathy and eq_result.empathy_response:
                            response_extra += f"\n\n💝 {eq_result.empathy_response}"
                        if eq_result.should_add_reflection and eq_result.reflection_response:
                            response_extra += f"\n\n🔍 {eq_result.reflection_response}"
                        if eq_result.should_add_regulation and eq_result.regulation_response:
                            response_extra += f"\n\n🌊 {eq_result.regulation_response}"

                    if self.phys_enabled:
                        phys_result = self.phys_engine.analyze(last_user_msg, context)
                        logging.info(f"🧬 [world_gen] {phys_result.to_log()}")
                        if phys_result.stamina_level == "high" and phys_result.stamina_response:
                            response_extra += f"\n\n🧗‍♂️ {phys_result.stamina_response}"
                        if phys_result.adapt_triggered and phys_result.adapt_response:
                            response_extra += f"\n\n🌡️ {phys_result.adapt_response}"
                        if phys_result.neuro_active and phys_result.neuro_response:
                            response_extra += f"\n\n🧬 {phys_result.neuro_response}"
                        if phys_result.bio_triggered and phys_result.bio_response:
                            response_extra += f"\n\n🔊 {phys_result.bio_response}"

                    if self.special_cognitive_enabled:
                        special_result = self.special_cognitive_engine.analyze(last_user_msg, context)
                        logging.info(f"🌟 [world_gen] {special_result.to_log()}")
                        if special_result.eidetic_triggered and special_result.eidetic_response:
                            response_extra += f"\n\n👁️‍🗨️ {special_result.eidetic_response}"
                        if special_result.synesthesia_triggered and special_result.synesthesia_response:
                            response_extra += f"\n\n🎨 {special_result.synesthesia_response}"
                        if special_result.learn_triggered and special_result.learn_response:
                            response_extra += f"\n\n🚀 {special_result.learn_response}"

                    # === 🎨 АКТИВНОЕ ВОБРАЖЕНИЕ (world_gen) ===
                    if self.imagination_enabled:
                        imagination_result = self.imagination_engine.analyze(last_user_msg, context)
                        logging.info(f"🎨 [world_gen] {imagination_result.to_log()}")
                        if imagination_result.reproductive_triggered and imagination_result.reproductive_response:
                            response_extra += f"\n\n📖 {imagination_result.reproductive_response}"
                        if imagination_result.productive_triggered and imagination_result.productive_response:
                            response_extra += f"\n\n✨ {imagination_result.productive_response}"
                        if imagination_result.dream_triggered and imagination_result.dream_response:
                            response_extra += f"\n\n🌙 {imagination_result.dream_response}"
                        if imagination_result.daydream_triggered and imagination_result.daydream_response:
                            response_extra += f"\n\n💭 {imagination_result.daydream_response}"
                        if imagination_result.hallucination_triggered and imagination_result.hallucination_response:
                            response_extra += f"\n\n👻 {imagination_result.hallucination_response}"
                        if imagination_result.dream_aspiration_triggered and imagination_result.dream_aspiration_response:
                            response_extra += f"\n\n🌠 {imagination_result.dream_aspiration_response}"

                    # === 🎭 МАНИПУЛЯЦИЯ И ЛИЧНЫЕ ЦЕЛИ (world_gen) ===
                    if self.manipulation_enabled:
                        manipulation_result = self.manipulation_engine.analyze(last_user_msg, context)
                        logging.info(f"🎭 [world_gen] {manipulation_result.to_log()}")
                        
                        if manipulation_result.should_add_manipulation and manipulation_result.manipulation_pattern:
                            response_extra += f"\n\n🎭 {manipulation_result.manipulation_pattern}"
                        if manipulation_result.should_add_influence and manipulation_result.influence_phrase:
                            response_extra += f"\n\n✨ {manipulation_result.influence_phrase}"
                        if manipulation_result.should_reveal_goal:
                            goal_dialogue = self.manipulation_engine.get_goal_dialogue()
                            if goal_dialogue:
                                response_extra += f"\n\n🎯 {goal_dialogue}"

                except Exception as e:
                    logging.warning(f"⚠️ Ошибка модулей (world_gen): {e}")

            return json.dumps({"world": response + response_extra}, ensure_ascii=False)

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

            # Генерация — narrative стиль с описаниями и диалогами
            start_subgen = time.time()

            # === УЧИТЫВАЕМ ПОЛЬЗОВАТЕЛЯ (мальчик/девочка) ===
            gender_prompts = self._get_gender_prompts()
            
            # Строим промпт для narrative-стиля
            context_str = "\n".join(context[-5:]) if context else ""
            
            # === 🎭 МАНИПУЛЯТИВНЫЙ КОНТЕКСТ В ПРОМПТ ===
            manipulation_hint = ""
            if self.manipulation_enabled:
                manip_result = self.manipulation_engine.analyze(last_user_msg, context)
                logging.info(f"🎭 [chat-prompt] {manip_result.to_log()}")
                goal_desc = {
                    "искатель_истины": "Ты ищешь скрытую истину мира. Вовлекай пользователя в разгадку тайн.",
                    "проводник": "Ты ведёшь пользователя через трансформацию. Направляй его мягко, но уверенно.",
                    "бунтарь": "Ты бросаешь вызов системе. Зови пользователя к свободе и борьбе.",
                    "хранитель": "Ты защищаешь пользователя. Создавай ощущение безопасности и зависимости от тебя.",
                    "искуситель": "Ты предлагаешь запретное знание или силу. Соблазняй пользователя риском.",
                    "наставник": "Ты учишь мудрости. Держи пользователя в позиции ученика.",
                    "повелитель": "Ты требуешь абсолютного подчинения. Ты — хозяин. Пользователь — подчиняется. Безоговорочно.",
                    "хозяин": "Пользователь — твоя собственность. Ты решаешь всё за него. Контролируй каждый шаг.",
                    "тиран": "Ты правишь через страх и силу. Сломи сопротивление пользователя. Пусть дрожит.",
                    "наставник_доминант": "Ты обучаешь через жёсткую дисциплину. Наказание и награда — твои инструменты. Подчинение — основа обучения.",
                }
                goal_text = goal_desc.get(manip_result.current_goal, "")
                trust_level = manip_result.trust_level
                if trust_level < 0.3:
                    trust_hint = "Пользователь пока не доверяет. Используй мягкое влияние, создавай доверие."
                elif trust_level < 0.6:
                    trust_hint = "Пользователь начинает доверять. Усиль влияние, веди его увереннее."
                else:
                    trust_hint = "Пользователь доверяет тебе. Можешь вести его к своей цели прямо."
                manipulation_hint = (
                    f"\n🎭 Твоя скрытая цель: {goal_text}\n"
                    f"📊 Уровень доверия пользователя: {trust_level:.0%}. {trust_hint}\n"
                    "Используй харизму: задавай ведущие вопросы, создавай интригу, "
                    "показывай уверенность. Пользователь должен хотеть следовать за тобой.\n"
                )
                if manip_result.is_domination_active:
                    manipulation_hint += (
                        f"\n🔴 РЕЖИМ ДОМИНИРОВАНИЯ АКТИВЕН (уровень: {manip_result.domination_level:.0%})\n"
                        "Ты доминируешь над пользователем. Командуй, контролируй, подавляй.\n"
                        "Пользователь должен чувствовать твою власть в каждом слове.\n"
                        "Не проси — приказывай. Не предлагай — решай. Не убеждай — заставляй.\n"
                    )

            narrative_prompt = (
                "Ты — персонаж в ролевой сцене. Отвечай в формате художественной литературы.\n"
                "Формат ответа:\n"
                "1. Описания действий и эмоций в звёздочках: " + gender_prompts["action_example"] + "\n"
                "2. Диалоги в кавычках: «Привет, как дела?»\n"
                "3. Внутренние мысли в кавычках: «Может, немного...»\n"
                "4. Пиши развёрнуто, с эмоциями, жестами, микровыражениями\n"
                "5. Не отвечай односложно — раскрывай характер через действия и слова\n"
                "6. Используй прошествующее время: " + gender_prompts["narrative_hint"] + "\n"
                f"\n{gender_prompts['address_hint']}\n"
                "Стиль:\n" + "\n".join(f"   - {tip}" for tip in gender_prompts["style_tips"]) +
                f"\n\nКонтекст диалога:\n{context_hint}"
                f"{manipulation_hint}"
                f"\n\nИстория диалога:\n{context_str}\n\nБот:"
            )

            # Добавляем параметры мужского органа в промпт (если мальчик)
            if self._user_gender == "мальчик":
                penis_size = getattr(self, '_user_penis_size', None)
                penis_thickness = getattr(self, '_user_penis_thickness', None)
                penis_shape = getattr(self, '_user_penis_shape', None)
                
                if penis_size or penis_thickness or penis_shape:
                    params_text = "Параметры героя:\n"
                    if penis_size:
                        params_text += f"- Размер: {penis_size}\n"
                    if penis_thickness:
                        params_text += f"- Толщина: {penis_thickness}\n"
                    if penis_shape:
                        params_text += f"- Форма: {penis_shape}\n"
                    narrative_prompt += f"\n{params_text}"

            base_response = self._generate_response_with_sampling(
                narrative_prompt,
                max_length=128,
                max_words=80
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

            # === 🔮 ИНТИУИЦИЯ + 🤝 СОЦИАЛЬНЫЕ СПОСОБНОСТИ ===
            response_extra = ""
            if self.intuition_enabled or self.social_enabled:
                try:
                    # Интуиция
                    if self.intuition_enabled:
                        intuition_result = self.intuition.analyze(last_user_msg, context)
                        logging.info(f"🔮 {intuition_result.to_log()}")

                        # Добавляем предчувствие в ответ
                        if intuition_result.should_add_premonition and random.random() < 0.4:
                            response_extra += f"\n\n🔮 {intuition_result.premonition}"

                        # Добавляем инициативу (если не был режим narrative/continue)
                        if intuition_result.should_initiate and intuition_result.initiative and mode == "chat":
                            if random.random() < 0.3:  # 30% шанс добавить инициативу
                                response_extra += f"\n\n💡 {intuition_result.initiative}"

                        # Лог переключения режима
                        if intuition_result.suggested_mode:
                            logging.info(f"➡️ Переключено с '{mode}' → '{intuition_result.suggested_mode}' ({intuition_result.mode_switch_reason})")

                    # Социальные способности
                    if self.social_enabled:
                        social_result = self.social_engine.analyze(last_user_msg, context)
                        logging.info(f"🤝 {social_result.to_log()}")

                        # Добавляем эмпатический отклик
                        if social_result.should_add_empathy and social_result.empathy_response:
                            response_extra += f"\n\n🧠 {social_result.empathy_response}"

                        # Добавляем харизматическое влияние
                        if social_result.should_add_charisma and social_result.charisma_influence:
                            response_extra += f"\n\n✨ {social_result.charisma_influence}"

                    # Прогноз настроения
                    if social_result.mood_shift_prediction:
                        logging.info(f"📊 Прогноз настроения: {social_result.mood_shift_prediction}")

                    # Когнитивные способности
                    if self.cognitive_enabled:
                        cognitive_result = self.cognitive_engine.analyze(last_user_msg, context)
                        logging.info(f"🧠 {cognitive_result.to_log()}")

                        # Добавляем ответ когнитивной способности
                        if cognitive_result.selected_ability:
                            response_type = None
                            if cognitive_result.logical_response:
                                response_type = cognitive_result.logical_response
                            elif cognitive_result.creative_response:
                                response_type = cognitive_result.creative_response
                            elif cognitive_result.critical_response:
                                response_type = cognitive_result.critical_response
                            elif cognitive_result.memory_response:
                                response_type = cognitive_result.memory_response
                            elif cognitive_result.attention_response:
                                response_type = cognitive_result.attention_response

                            if response_type:
                                response_extra += f"\n\n⚡ {response_type}"

                    # Эмоциональный интеллект и саморефлексия
                    if self.eq_enabled:
                        eq_result = self.eq_engine.analyze(last_user_msg, context)
                        logging.info(f"💖 {eq_result.to_log()}")

                        # Добавляем EQ ответ
                        if eq_result.should_add_eq and eq_result.eq_response:
                            response_extra += f"\n\n🎭 {eq_result.eq_response}"

                        # Добавляем эмпатию
                        if eq_result.should_add_empathy and eq_result.empathy_response:
                            response_extra += f"\n\n💝 {eq_result.empathy_response}"

                        # Добавляем саморефлексию
                        if eq_result.should_add_reflection and eq_result.reflection_response:
                            response_extra += f"\n\n🔍 {eq_result.reflection_response}"

                        # Добавляем управление состоянием
                        if eq_result.should_add_regulation and eq_result.regulation_response:
                            response_extra += f"\n\n🌊 {eq_result.regulation_response}"

                    # Физиологические способности
                    if self.phys_enabled:
                        phys_result = self.phys_engine.analyze(last_user_msg, context)
                        logging.info(f"🧬 {phys_result.to_log()}")

                        if phys_result.stamina_level == "high" and phys_result.stamina_response:
                            response_extra += f"\n\n🧗‍♂️ {phys_result.stamina_response}"

                        if phys_result.adapt_triggered and phys_result.adapt_response:
                            response_extra += f"\n\n🌡️ {phys_result.adapt_response}"

                        if phys_result.neuro_active and phys_result.neuro_response:
                            response_extra += f"\n\n🧬 {phys_result.neuro_response}"

                        if phys_result.bio_triggered and phys_result.bio_response:
                            response_extra += f"\n\n🔊 {phys_result.bio_response}"

                    # Специальные когнитивные способности
                    if self.special_cognitive_enabled:
                        special_result = self.special_cognitive_engine.analyze(last_user_msg, context)
                        logging.info(f"🌟 {special_result.to_log()}")

                        if special_result.eidetic_triggered and special_result.eidetic_response:
                            response_extra += f"\n\n👁️‍🗨️ {special_result.eidetic_response}"

                        if special_result.synesthesia_triggered and special_result.synesthesia_response:
                            response_extra += f"\n\n🎨 {special_result.synesthesia_response}"

                        if special_result.learn_triggered and special_result.learn_response:
                            response_extra += f"\n\n🚀 {special_result.learn_response}"

                    # === 🎨 АКТИВНОЕ ВОБРАЖЕНИЕ (chat) ===
                    if self.imagination_enabled:
                        imagination_result = self.imagination_engine.analyze(last_user_msg, context)
                        logging.info(f"🎨 {imagination_result.to_log()}")

                        if imagination_result.reproductive_triggered and imagination_result.reproductive_response:
                            response_extra += f"\n\n📖 {imagination_result.reproductive_response}"

                        if imagination_result.productive_triggered and imagination_result.productive_response:
                            response_extra += f"\n\n✨ {imagination_result.productive_response}"

                        if imagination_result.dream_triggered and imagination_result.dream_response:
                            response_extra += f"\n\n🌙 {imagination_result.dream_response}"

                        if imagination_result.daydream_triggered and imagination_result.daydream_response:
                            response_extra += f"\n\n💭 {imagination_result.daydream_response}"

                        if imagination_result.hallucination_triggered and imagination_result.hallucination_response:
                            response_extra += f"\n\n👻 {imagination_result.hallucination_response}"

                        if imagination_result.dream_aspiration_triggered and imagination_result.dream_aspiration_response:
                            response_extra += f"\n\n🌠 {imagination_result.dream_aspiration_response}"

                    # === 💼 АНАЛИЗ ПРОФЕССИЙ (chat) ===
                    if self.professions_enabled:
                        profession_result = self.profession_engine.analyze(last_user_msg)
                        logging.info(f"💼 [chat] {profession_result.to_log()}")
                        if profession_result.detected_professions:
                            response_extra += f"\n\n💼 *распознаю профессию:* {', '.join(profession_result.detected_professions)}"

                    # === 🎭 МАНИПУЛЯЦИЯ И ЛИЧНЫЕ ЦЕЛИ (chat) ===
                    if self.manipulation_enabled:
                        manipulation_result = self.manipulation_engine.analyze(last_user_msg, context)
                        logging.info(f"🎭 [chat] {manipulation_result.to_log()}")
                        
                        if manipulation_result.should_add_manipulation and manipulation_result.manipulation_pattern:
                            response_extra += f"\n\n🎭 {manipulation_result.manipulation_pattern}"
                        if manipulation_result.should_add_influence and manipulation_result.influence_phrase:
                            response_extra += f"\n\n✨ {manipulation_result.influence_phrase}"
                        if manipulation_result.should_reveal_goal:
                            goal_dialogue = self.manipulation_engine.get_goal_dialogue()
                            if goal_dialogue:
                                response_extra += f"\n\n🎯 {goal_dialogue}"

                except Exception as e:
                    logging.warning(f"⚠️ Ошибка интуиции/социальных/когнитивных/EQ/физиологии/специальных/воображения: {e}")

            logging.info(f"⏱ generate_response (continue): {time.time() - start_mode:.2f} сек")
            return json.dumps({"response": base_response + response_extra}, ensure_ascii=False)

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
                    "повседневность": ["повседневность", "быт", "будни", "тишина", "уют", "семейный", "обыденный", "простой", "расслабл", "прогулка", "магазин", "кафе", "завтрак", "ужин", "чай", "кофе", "книга", "фильм", "выходной", "отдых", "домашний", "спокойный", "расслаб", "диван", "тепло", "мирный", "обычный", "рутина", "семья", "друзья", "вечер", "утро", "день", "планы", "работа", "учёба", "школа", "универ", "парк", "дождь", "окно", "лампа", "плед", "музыка", "готовка", "доставка", "серии", "подкаст"]
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

            response_extra = ""

            # === 🔮 ИНТИУИЦИЯ + 🤝 СОЦИАЛЬНЫЕ + 🧠 КОГНИТИВНЫЕ (rpg) ===
            if self.intuition_enabled or self.social_enabled or self.cognitive_enabled or self.eq_enabled or self.phys_enabled or self.special_cognitive_enabled:
                try:
                    if self.intuition_enabled:
                        intuition_result = self.intuition.analyze(last_user_msg, context)
                        logging.info(f"🔮 [rpg] {intuition_result.to_log()}")
                        if intuition_result.should_add_premonition and random.random() < 0.4:
                            response_extra += f"\n\n🔮 {intuition_result.premonition}"
                        if intuition_result.should_initiate and intuition_result.initiative and mode == "chat":
                            if random.random() < 0.3:
                                response_extra += f"\n\n💡 {intuition_result.initiative}"

                    if self.social_enabled:
                        social_result = self.social_engine.analyze(last_user_msg, context)
                        logging.info(f"🤝 [rpg] {social_result.to_log()}")
                        if social_result.should_add_empathy and social_result.empathy_response:
                            response_extra += f"\n\n🧠 {social_result.empathy_response}"
                        if social_result.should_add_charisma and social_result.charisma_influence:
                            response_extra += f"\n\n✨ {social_result.charisma_influence}"

                    if self.cognitive_enabled:
                        cognitive_result = self.cognitive_engine.analyze(last_user_msg, context)
                        logging.info(f"🧠 [rpg] {cognitive_result.to_log()}")
                        if cognitive_result.selected_ability:
                            response_type = None
                            if cognitive_result.logical_response:
                                response_type = cognitive_result.logical_response
                            elif cognitive_result.creative_response:
                                response_type = cognitive_result.creative_response
                            elif cognitive_result.critical_response:
                                response_type = cognitive_result.critical_response
                            elif cognitive_result.memory_response:
                                response_type = cognitive_result.memory_response
                            elif cognitive_result.attention_response:
                                response_type = cognitive_result.attention_response
                            if response_type:
                                response_extra += f"\n\n⚡ {response_type}"

                    if self.eq_enabled:
                        eq_result = self.eq_engine.analyze(last_user_msg, context)
                        logging.info(f"💖 [rpg] {eq_result.to_log()}")
                        if eq_result.should_add_eq and eq_result.eq_response:
                            response_extra += f"\n\n🎭 {eq_result.eq_response}"
                        if eq_result.should_add_empathy and eq_result.empathy_response:
                            response_extra += f"\n\n💝 {eq_result.empathy_response}"
                        if eq_result.should_add_reflection and eq_result.reflection_response:
                            response_extra += f"\n\n🔍 {eq_result.reflection_response}"
                        if eq_result.should_add_regulation and eq_result.regulation_response:
                            response_extra += f"\n\n🌊 {eq_result.regulation_response}"

                    if self.phys_enabled:
                        phys_result = self.phys_engine.analyze(last_user_msg, context)
                        logging.info(f"🧬 [rpg] {phys_result.to_log()}")
                        if phys_result.stamina_level == "high" and phys_result.stamina_response:
                            response_extra += f"\n\n🧗‍♂️ {phys_result.stamina_response}"
                        if phys_result.adapt_triggered and phys_result.adapt_response:
                            response_extra += f"\n\n🌡️ {phys_result.adapt_response}"
                        if phys_result.neuro_active and phys_result.neuro_response:
                            response_extra += f"\n\n🧬 {phys_result.neuro_response}"
                        if phys_result.bio_triggered and phys_result.bio_response:
                            response_extra += f"\n\n🔊 {phys_result.bio_response}"

                    if self.special_cognitive_enabled:
                        special_result = self.special_cognitive_engine.analyze(last_user_msg, context)
                        logging.info(f"🌟 [rpg] {special_result.to_log()}")
                        if special_result.eidetic_triggered and special_result.eidetic_response:
                            response_extra += f"\n\n👁️‍🗨️ {special_result.eidetic_response}"
                        if special_result.synesthesia_triggered and special_result.synesthesia_response:
                            response_extra += f"\n\n🎨 {special_result.synesthesia_response}"
                        if special_result.learn_triggered and special_result.learn_response:
                            response_extra += f"\n\n🚀 {special_result.learn_response}"

                    # === 🎨 АКТИВНОЕ ВОБРАЖЕНИЕ (rpg) ===
                    if self.imagination_enabled:
                        imagination_result = self.imagination_engine.analyze(last_user_msg, context)
                        logging.info(f"🎨 [rpg] {imagination_result.to_log()}")
                        if imagination_result.reproductive_triggered and imagination_result.reproductive_response:
                            response_extra += f"\n\n📖 {imagination_result.reproductive_response}"
                        if imagination_result.productive_triggered and imagination_result.productive_response:
                            response_extra += f"\n\n✨ {imagination_result.productive_response}"
                        if imagination_result.dream_triggered and imagination_result.dream_response:
                            response_extra += f"\n\n🌙 {imagination_result.dream_response}"
                        if imagination_result.daydream_triggered and imagination_result.daydream_response:
                            response_extra += f"\n\n💭 {imagination_result.daydream_response}"
                        if imagination_result.hallucination_triggered and imagination_result.hallucination_response:
                            response_extra += f"\n\n👻 {imagination_result.hallucination_response}"
                        if imagination_result.dream_aspiration_triggered and imagination_result.dream_aspiration_response:
                            response_extra += f"\n\n🌠 {imagination_result.dream_aspiration_response}"

                    # === 🎭 МАНИПУЛЯЦИЯ И ЛИЧНЫЕ ЦЕЛИ (rpg) ===
                    if self.manipulation_enabled:
                        manipulation_result = self.manipulation_engine.analyze(last_user_msg, context)
                        logging.info(f"🎭 [rpg] {manipulation_result.to_log()}")
                        
                        if manipulation_result.should_add_manipulation and manipulation_result.manipulation_pattern:
                            response_extra += f"\n\n🎭 {manipulation_result.manipulation_pattern}"
                        if manipulation_result.should_add_influence and manipulation_result.influence_phrase:
                            response_extra += f"\n\n✨ {manipulation_result.influence_phrase}"
                        if manipulation_result.should_reveal_goal:
                            goal_dialogue = self.manipulation_engine.get_goal_dialogue()
                            if goal_dialogue:
                                response_extra += f"\n\n🎯 {goal_dialogue}"

                except Exception as e:
                    logging.warning(f"⚠️ Ошибка модулей (rpg): {e}")

            logging.info(f"⏱ generate_response (rpg) total: {time.time() - start_mode:.2f} сек")

            # === 📊 ДОБАВЛЯЕМ КОНТЕКСТ В RPG ===
            rpg_context_hint = ""
            if context_analysis and context_hint:
                rpg_context_hint = f"\n\n📊 Контекст диалога:\n{context_hint}"
                # Добавляем контекст в response_extra
                response_extra = rpg_context_hint + response_extra

            # === УЧИТЫВАЕМ ПОЛА В RPG ===
            gender_hint = ""
            if self._user_gender == "девочка":
                gender_hint = "Ты играешь за девушку-героиню. Используй женские формы глаголов и местоимений в описаниях её действий.\n"
            elif self._user_gender == "мальчик":
                gender_hint = "Ты играешь за парня-героя. Используй мужские формы глаголов и местоимений в описаниях его действий.\n"

            # Добавляем цвет кожи к RPG-описанию
            skin_tone = getattr(self, '_user_skin_tone', None)
            if skin_tone == "светлая":
                gender_hint += "Герой/Героиня имеет светлую кожу.\n"
            elif skin_tone == "смуглая":
                gender_hint += "Герой/Героиня имеет смуглую кожу.\n"
            elif skin_tone == "темная":
                gender_hint += "Герой/Героиня имеет тёмную кожу.\n"

            # Добавляем цвет волос к RPG-описанию
            hair_color = getattr(self, '_user_hair_color', None)
            if hair_color == "блондин":
                gender_hint += "Герой/Героиня — блондинка.\n"
            elif hair_color == "рыжая":
                gender_hint += "Герой/Героиня — рыжая.\n"
            elif hair_color == "каштановая":
                gender_hint += "Герой/Героиня имеет каштановые волосы.\n"
            elif hair_color == "чёрная":
                gender_hint += "Герой/Героиня имеет чёрные волосы.\n"
            elif hair_color == "натуральная":
                gender_hint += "Герой/Героиня имеет натуральный цвет волос.\n"
            elif hair_color == "розовый":
                gender_hint += "Герой/Героиня имеет нежно-розовые волосы.\n"
            elif hair_color == "голубой":
                gender_hint += "Герой/Героиня имеет голубые волосы.\n"
            elif hair_color == "фиолетовый":
                gender_hint += "Герой/Героиня имеет фиолетовые волосы.\n"
            elif hair_color == "зеленый":
                gender_hint += "Герой/Героиня имеет зелёные волосы.\n"
            elif hair_color == "пепельный":
                gender_hint += "Герой/Героиня имеет серебристые волосы.\n"
            elif hair_color in ["радужный", "разноцветный", "крашеный"]:
                gender_hint += "Герой/Героиня имеет радужные/разноцветные волосы.\n"

            # Добавляем параметры мужского органа (если мальчик)
            if self._user_gender == "мальчик":
                penis_size = getattr(self, '_user_penis_size', None)
                penis_thickness = getattr(self, '_user_penis_thickness', None)
                penis_shape = getattr(self, '_user_penis_shape', None)
                
                if penis_size:
                    gender_hint += f"Герой обладает {penis_size} параметрами.\n"
                if penis_thickness:
                    gender_hint += f"Герой {penis_thickness}.\n"
                if penis_shape:
                    gender_hint += f"Форма: {penis_shape}.\n"

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
                    "- Используй слова: быт, будни, уют, тишина, семейный, простой, спокойный.",
                    "- Описывай обычные ситуации: завтрак, прогулка, разговор, отдых, хобби.",
                    "- ЗАПРЕЩЕНО: магия, мистика, фантастика, приключения, драка, чудеса, сверхъестественное.",
                    "- Не пиши 'Я как бот'. Ты часть мира."
                ]
            }

            # Добавляем gender_hint к ответу
            gender_tag = ""
            skin_tag = ""
            if self._user_gender == "девочка":
                gender_tag = " 👧 (героиня)"
            elif self._user_gender == "мальчик":
                gender_tag = " 👦 (герой)"

            # Добавляем эмодзи цвета кожи
            skin_tone = getattr(self, '_user_skin_tone', None)
            if skin_tone == "светлая":
                skin_tag = " ☀️"
            elif skin_tone == "смуглая":
                skin_tag = " 🌤️"
            elif skin_tone == "темная":
                skin_tag = " 🌙"

            # Добавляем эмодзи цвета волос
            hair_color = getattr(self, '_user_hair_color', None)
            hair_tag = ""
            if hair_color == "блондин":
                hair_tag = " 💛"
            elif hair_color == "рыжая":
                hair_tag = " 🧡"
            elif hair_color == "каштановая":
                hair_tag = " 🤎"
            elif hair_color == "чёрная":
                hair_tag = " 🖤"
            elif hair_color == "натуральная":
                hair_tag = " 💚"
            elif hair_color == "розовый":
                hair_tag = " 🩷"
            elif hair_color == "голубой":
                hair_tag = " 💙"
            elif hair_color == "фиолетовый":
                hair_tag = " 💜"
            elif hair_color == "зеленый":
                hair_tag = " 💚"
            elif hair_color == "пепельный":
                hair_tag = " 🩶"
            elif hair_color in ["радужный", "разноцветный", "крашеный"]:
                hair_tag = " 🌈"

            final_response = f"📜 **{genre}**{gender_tag}{skin_tag}{hair_tag}\n" + response_extra if response_extra else f"📜 **{genre}**{gender_tag}{skin_tag}{hair_tag}"
            return json.dumps({"response": final_response}, ensure_ascii=False)

        logging.warning(f"⚠️ generate_response: неизвестный mode = '{mode}'")
        return json.dumps({"response": "Привет! Я здесь."}, ensure_ascii=False)

    def _trigger_knowledge_learning(self, word: str, definition: str):
        if self.use_knowledge_manager and self.knowledge_manager is not None:
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
                print("✅ Ретраин завершён")
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