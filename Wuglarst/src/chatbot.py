# Wuglarst/src/chatbot.py (обновлённая версия с Qwen2.5-3B)

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
from typing import List, Dict, Any, Optional
from transformers import AutoTokenizer, AutoModelForCausalLM
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
from .world_engine import WorldEngine
import subprocess
import threading
import logging
import asyncio

# === Настройки Qwen2.5-3B ===
QWEN25_MAX_LENGTH = 512
QWEN25_TEMPERATURE = 0.85
QWEN25_TOP_P = 0.92
QWEN25_BASE = "Qwen/Qwen2.5-3B-Instruct"
QWEN25_VUGLARST = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "models", "qwen2.5-3b")

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
    def __init__(self, tokenizer_path: str, max_length: int = QWEN25_MAX_LENGTH):
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
        """Инициализация Qwen2.5-3B вместо ChatNN."""
        self.device = device or ("cuda" if torch.cuda.is_available() else "cpu")
        self.model_path = model_path
        
        # Определяем путь к модели
        if os.path.exists(model_path):
            self.rugpt_path = model_path
        elif os.path.exists(QWEN25_VUGLARST):
            self.rugpt_path = QWEN25_VUGLARST
        else:
            self.rugpt_path = QWEN25_BASE
        
        print(f"[Qwen2.5] Загрузка модели: {self.rugpt_path}")
        
        # Загружаем Qwen2.5
        self.tokenizer = AutoTokenizer.from_pretrained(self.rugpt_path)
        self.model = AutoModelForCausalLM.from_pretrained(
            self.rugpt_path,
            torch_dtype=torch.float16 if torch.cuda.is_available() else torch.float32,
            device_map="auto" if torch.cuda.is_available() else None
        )
        
        if torch.cuda.is_available():
            print(f"[Qwen2.5] Загружено на GPU: {torch.cuda.get_device_name(0)}")
        else:
            print("[Qwen2.5] Загружено на CPU")
        
        self._user_gender = None
        self._user_skin_tone = None
        self._user_hair_color = None
        self._user_penis_size = None
        self._user_penis_thickness = None
        self._user_penis_shape = None
        
        # Инициализация движков
        self.intuition = IntuitionEngine()
        self.social = SocialEngine()
        self.cognitive = CognitiveEngine()
        self.emotional = EmotionalIntelligenceEngine()
        self.physiological = PhysiologicalEngine()
        self.special_cognitive = SpecialCognitiveEngine()
        self.imagination = ImaginationEngine()
        self.professions = ProfessionEngine()
        self.manipulation = ManipulationEngine()
        self.context = ContextAnalyzer()
        self.world = WorldEngine()

        # Поиск и знания
        self.web_search_enabled = False
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

        # === World Engine — полная система управления мирами ===
        try:
            project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
            data_dir = os.path.join(project_root, "data")
            self.world_engine = WorldEngine(data_dir=data_dir)
            self.world_engine_enabled = True
            logging.info("🌍 WorldEngine инициализирован (миры, события, NPC, лор)")
        except Exception as e:
            print(f"❌ Ошибка инициализации WorldEngine: {e}")
            self.world_engine = None
            self.world_engine_enabled = False

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

    @staticmethod
    def _detect_genre_category(genre: str, tag: str) -> str:
        """Определяет категорию жанра для выбора шаблонов"""
        genre_lower = genre.lower()
        tag_lower = tag.lower()

        # Гибридные жанры
        is_cyber = "киберпанк" in genre_lower
        is_fantasy = "фэнтези" in genre_lower or "фэнтези" in tag_lower
        is_magic = "магия" in tag_lower or "мистик" in tag_lower

        if is_cyber and (is_fantasy or is_magic):
            return "cyberfantasy"
        if "пост" in genre_lower and (is_fantasy or is_magic):
            return "postfantasy"

        # Чистые жанры
        if is_cyber:
            return "cyberpunk"
        if is_fantasy:
            return "fantasy"
        if "пост" in genre_lower:
            return "postapoc"
        if "научная фантастика" in genre_lower or "sci-fi" in genre_lower:
            return "scifi"
        if "стимпанк" in genre_lower:
            return "steampunk"
        if "повседневность" in genre_lower:
            return "slice_of_life"
        if "альтернатив" in genre_lower:
            return "alt_reality"
        if "реальност" in genre_lower or "реальный мир" in genre_lower:
            return "reality"
        if "школа" in tag_lower or "учеб" in tag_lower:
            return "slice_of_life"  # Школьные темы — повседневность

        # По умолчанию — фэнтези
        return "fantasy"

    def _generate_world_from_templates(self, genre: str, tag: str, templates: Dict, category: str) -> str:
        """Генерирует структурированный мир на основе шаблонов WorldFactory"""
        import random
        
        # Вспомогательные функции для заполнения шаблонов
        def fill_template(template: str) -> str:
            """Заполняет шаблон случайными значениями"""
            replacements = {
                "{name}": random.choice(["Элдория", "Валерия", "Ардония", "Северия", "Тэммора", "Астра", "Небесный Предел", "Тихий Угол", "Стальной Горизонт", "Новая Земля"]),
                "{number}": str(random.randint(3, 12)),
                "{height}": str(random.randint(500, 5000)),
                "{depth}": str(random.randint(1, 50)),
                "{plant}": random.choice(["вечным туманом", "серебристым мхом", "кристальными цветами", "светящимся лишайником", "древними папоротниками"]),
                "{location}": random.choice(["Запретной Зоны", "Пустошей", "Горизонта Событий", "Мёртвого Города", "Древних Руин"]),
            }
            result = template
            for key, value in replacements.items():
                result = result.replace(key, value)
            return result
        
        # Генерируем географию (1-2 шаблона)
        geography = random.sample(templates.get("geography", []), min(len(templates.get("geography", [])), 2))
        geography_text = "\n".join([f"   - {fill_template(g)}" for g in geography])
        
        # Генерируем законы (2-3 шаблона)
        laws = random.sample(templates.get("laws", []), min(len(templates.get("laws", [])), 3))
        laws_text = "\n".join([f"   - {fill_template(l)}" for l in laws])
        
        # Генерируем традиции (2-3 шаблона)
        traditions = random.sample(templates.get("traditions", []), min(len(templates.get("traditions", [])), 3))
        traditions_text = "\n".join([f"   - {fill_template(t)}" for t in traditions])
        
        # Генерируем негласные правила (1-2 шаблона)
        unspoken = random.sample(templates.get("unspoken_rules", []), min(len(templates.get("unspoken_rules", [])), 2))
        unspoken_text = "\n".join([f"   - {fill_template(u)}" for u in unspoken])
        
        # Генерируем название мира
        world_name = fill_template("{name}")
        if category == "fantasy":
            world_name = random.choice(["Элдория", "Валерия", "Ардония", "Северия", "Тэммора", "Драконий Предел", "Лес Теней", "Королевство Света"])
        elif category == "cyberpunk":
            world_name = random.choice(["Нео-Токио", "Стальной Горизонт", "Хром-Сити", "Глитч-Зона", "Кибер-Предел"])
        elif category == "cyberfantasy":
            world_name = random.choice(["Арк-Сити", "Техно-Магия", "Нео-Ардония", "Кристалл-Град", "Эфир-Сити"])
        elif category == "postapoc":
            world_name = random.choice(["Пустошь-7", "Бункер-Сити", "Новый Рассвет", "Зона Выживания", "Последний Оплот"])
        elif category == "scifi":
            world_name = random.choice(["Колония Альфа", "Звёздный Предел", "Орбита-7", "Новая Земля", "Галактический Пост"])
        elif category == "reality" or category == "slice_of_life":
            world_name = random.choice(["Тихий Город", "Обычный Мир", "Наша Реальность", "Повседневность", "Знакомый Город"])
        elif category == "alt_reality":
            world_name = random.choice(["Альтернатива-42", "Параллель", "Другая Версия", "Реальность-X", "Мир Наизнанку"])
        
        # Формируем структурированный ответ
        response = f"""Название: {world_name}

Жанр: {genre}
Тег: {tag if tag else 'общий'}
Категория: {category}

📍 География мира:
{geography_text}

⚖️ Законы общества:
{laws_text}

🎭 Традиции и обычаи:
{traditions_text}

🤫 Негласные правила:
{unspoken_text}

👥 Типичные роли персонажей:
{chr(10).join(['   - ' + r for r in random.sample(templates.get('npc_roles', []), min(len(templates.get('npc_roles', [])), 5))])}

🏛️ Фракции:
{chr(10).join(['   - ' + f['name'].format(name=random.choice(['Стальная', 'Теней', 'Света', 'Древняя', 'Новая'])) + ' — ' + f['description'] for f in random.sample(templates.get('faction_types', []), min(len(templates.get('faction_types', [])), 3))])}

📊 Уровень технологий: {templates.get('technology_level', 0.5) * 100:.0f}%
✨ Уровень магии: {templates.get('magic_level', 0.0) * 100:.0f}%

📖 Сюжетная вводная:
Ты стоишь на пороге нового мира. {fill_template(random.choice(templates.get('geography', ['Мир открыт перед тобой.'])))} Твоё приключение начинается здесь."""

        return response

    def _generate_world_from_knowledge(self, genre: str, tag: str) -> str:
        """Генерирует мир на основе знаний из world_gen_knowledge.py (fallback)"""
        try:
            from .world_gen_knowledge import WorldGenKnowledgeEngine
            
            project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
            data_dir = os.path.join(project_root, "data")
            
            knowledge_engine = WorldGenKnowledgeEngine(data_dir=data_dir)
            knowledge = knowledge_engine.collect_all_knowledge(genre, tag)
            prompt = knowledge_engine.build_world_gen_prompt(knowledge)
            
            logging.info(f"📚 _generate_world_from_knowledge: собрано {len(knowledge['books_content'])} книжных концепций")
            
            # Генерируем через модель
            response = self._generate_response_with_sampling(prompt, max_length=512, max_words=400, temperature=1.2, top_p=0.95)
            return response
        except Exception as e:
            logging.error(f"❌ _generate_world_from_knowledge: {e}")
            return self._generate_fallback_world(genre, tag)

    def _generate_fallback_world(self, genre: str, tag: str) -> str:
        """Простой fallback для генерации мира"""
        import random
        
        world_name = random.choice(["Эхо", "Предел", "Горизонт", "Тени", "Свет", "Ветер", "Сталь", "Кристалл"])
        world_adj = random.choice(["Забытый", "Вечный", "Скрытый", "Новый", "Древний", "Таинственный"])
        
        return f"""Название: {world_adj} {world_name}

Жанр: {genre}
Тег: {tag if tag else 'общий'}

📍 География мира:
   - Мир раскинулся на бескрайних просторах, где каждый уголок хранит свои тайны.
   - Ландшафт меняется от суровых гор до тихих долин.

⚖️ Законы общества:
   - Каждый отвечает за свои поступки.
   - Сила слова важнее силы оружия.

🎭 Традиции и обычаи:
   - Праздник Первого Света — начало нового года.
   - Обмен дарами в день полнолуния.

📖 Сюжетная вводная:
Ты стоишь на пороге неизвестного. {world_adj} {world_name} ждёт своего героя. Что ты выберешь?"""

    def _generate_response_with_sampling(
        self,
        input_text: str,
        max_length: int = QWEN25_MAX_LENGTH,
        temperature: float = QWEN25_TEMPERATURE,
        top_p: float = QWEN25_TOP_P,
        max_words: int = 80,
        min_words: int = 5
    ) -> str:
        """Генерация через Qwen2.5 с nucleus sampling."""
        self.model.eval()
        
        # Токенизация через Qwen2.5
        inputs = self.tokenizer.encode(input_text, return_tensors="pt")
        if torch.cuda.is_available():
            inputs = inputs.to("cuda")
        
        # Генерация
        with torch.no_grad():
            outputs = self.model.generate(
                inputs.input_ids,
                max_length=max_length,
                temperature=temperature,
                top_p=top_p,
                do_sample=True,
                pad_token_id=self.tokenizer.eos_token_id,
                eos_token_id=self.tokenizer.eos_token_id
            )
        
        # Декодируем только новое
        generated_ids = outputs[0][inputs.input_ids.shape[1]:]
        response = self.tokenizer.decode(generated_ids, skip_special_tokens=True)
        
        # Фильтр по словам
        words = response.split()
        if len(words) < min_words:
            return input_text[-50:] + " " + response
        if len(words) > max_words:
            words = words[:max_words]
            response = " ".join(words)
        
        return response.strip()


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
            genre_match = re.search(r"Жанр[:\s]+([^.;\n]+)", last_user_msg, re.IGNORECASE)
            tag_match = re.search(r"Тег[иаеs]*[:\s]+([^.;\n]+)", last_user_msg, re.IGNORECASE)
            
            genre = genre_match.group(1).strip() if genre_match else "Фэнтези"
            tag = tag_match.group(1).strip() if tag_match else ""

            # === ГЕНЕРАЦИЯ МИРА ЧЕРЕЗ ШАБЛОНЫ WorldFactory + ЗНАНИЯ ===
            try:
                # Определяем категорию жанра
                category = self._detect_genre_category(genre, tag)
                
                # Импортируем WorldFactory напрямую и получаем шаблоны
                from .world_engine import WorldFactory
                templates = WorldFactory.GENRE_TEMPLATES.get(category, {})
                
                if templates and len(templates) > 0:
                    # Генерируем мир на основе шаблонов
                    response = self._generate_world_from_templates(genre, tag, templates, category)
                    logging.info(f"📚 world_gen: сгенерирован мир из шаблонов '{category}' (жанр: {genre}, тег: {tag})")
                else:
                    # Fallback на генерацию через знания
                    response = self._generate_world_from_knowledge(genre, tag)
            
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

            return json.dumps({"response": response + response_extra}, ensure_ascii=False)

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

            # === Улучшенная генерация: модули влияют на следующий ответ, а не добавляются в текущий ===
            # Все engines работают в фоне для обучения и анализа, но НЕ добавляют мусор в ответ
            # Это критически важно для качества — ответ должен быть единым связным текстом
            try:
                # Интуиция — анализирует, но НЕ добавляет в ответ
                if self.intuition_enabled:
                    intuition_result = self.intuition.analyze(last_user_msg, context)
                    logging.info(f"🔮 [chat-analyze] {intuition_result.to_log()}")
                    if intuition_result.suggested_mode:
                        logging.info(f"➡️ Сuggested mode: {intuition_result.suggested_mode}")

                # Социальные — анализируют для будущего контекста
                if self.social_enabled:
                    social_result = self.social_engine.analyze(last_user_msg, context)
                    logging.info(f"🤝 [chat-analyze] {social_result.to_log()}")

                # Когнитивные — анализируют
                if self.cognitive_enabled:
                    cognitive_result = self.cognitive_engine.analyze(last_user_msg, context)
                    logging.info(f"🧠 [chat-analyze] {cognitive_result.to_log()}")

                # EQ — анализирует
                if self.eq_enabled:
                    eq_result = self.eq_engine.analyze(last_user_msg, context)
                    logging.info(f"💖 [chat-analyze] {eq_result.to_log()}")

                # Физиологические
                if self.phys_enabled:
                    phys_result = self.phys_engine.analyze(last_user_msg, context)
                    logging.info(f"🧬 [chat-analyze] {phys_result.to_log()}")

                # Специальные когнитивные
                if self.special_cognitive_enabled:
                    special_result = self.special_cognitive_engine.analyze(last_user_msg, context)
                    logging.info(f"🌟 [chat-analyze] {special_result.to_log()}")

                # Воображение
                if self.imagination_enabled:
                    imagination_result = self.imagination_engine.analyze(last_user_msg, context)
                    logging.info(f"🎨 [chat-analyze] {imagination_result.to_log()}")

                # Профессии
                if self.professions_enabled:
                    profession_result = self.profession_engine.analyze(last_user_msg)
                    logging.info(f"💼 [chat-analyze] {profession_result.to_log()}")

                # Манипуляция
                if self.manipulation_enabled:
                    manipulation_result = self.manipulation_engine.analyze(last_user_msg, context)
                    logging.info(f"🎭 [chat-analyze] {manipulation_result.to_log()}")

            except Exception as e:
                logging.warning(f"⚠️ Ошибка анализа модулей (chat): {e}")

            logging.info(f"⏱ generate_response (chat): {time.time() - start_mode:.2f} сек")
            return json.dumps({"response": base_response}, ensure_ascii=False)

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

    # ========================
    # WorldEngine Methods
    # ========================

    def create_world(self, genre: str, tag: str) -> str:
        """Создаёт новый мир через WorldEngine (с полным описанием)"""
        if not self.world_engine_enabled or self.world_engine is None:
            return "❌ WorldEngine не доступен"
        try:
            result = self.world_engine.create_world(genre, tag)
            return result
        except Exception as e:
            return f"❌ Ошибка создания мира: {e}"

    def create_world_from_books(self, genre: Optional[str] = None, tag: Optional[str] = None, book_titles: Optional[List[str]] = None) -> Dict:
        """Создаёт новый мир на основе прочитанных книг"""
        if not self.world_engine_enabled or self.world_engine is None:
            raise RuntimeError("WorldEngine не доступен")
        try:
            world_data = self.world_engine.create_world_from_books(genre, tag, book_titles)
            world_name = world_data["name"]

            # Сохраняем мир
            self.world_engine.save_world(world_name, world_data)

            # Обновляем индекс
            self.world_engine.world_db.index["worlds"][world_name] = {
                "genre": world_data.get("genre", genre or "unknown"),
                "tag": world_data.get("tags", ["unknown"])[0] if world_data.get("tags") else (tag or "unknown"),
                "created_at": world_data.get("created_at", ""),
                "last_updated": world_data.get("last_updated", ""),
                "state": world_data.get("state", "draft"),
                "npc_count": len(world_data.get("npcs", [])),
                "event_count": len(world_data.get("events", [])),
                "fact_count": len(world_data.get("facts", [])),
            }
            self.world_engine.world_db._save_index()

            print(f"📚 Создан мир из книг: {world_name}")
            return world_data
        except Exception as e:
            raise RuntimeError(f"Ошибка создания мира из книг: {e}")

    def get_world_info(self, world_name: str) -> str:
        """Возвращает информацию о мире"""
        if not self.world_engine_enabled or self.world_engine is None:
            return "❌ WorldEngine не доступен"
        try:
            world = self.world_engine.get_world(world_name)
            if not world:
                return f"❌ Мир '{world_name}' не найден"

            info = f"🌍 **{world['name']}**\n"
            info += f"📚 Жанр: {world['genre']}\n"
            info += f"🏷️ Тег: {world['tags']}\n"
            info += f"⚡ Состояние: {world['state']}\n"
            info += f"📅 Эпоха: {world['era']}\n"
            info += f"👥 NPC: {len(world.get('npcs', []))}\n"
            info += f"⚔️ Фракции: {len(world.get('factions', []))}\n"
            info += f"📜 События: {len(world.get('events', []))}\n"
            info += f"📝 Факты: {len(world.get('facts', []))}\n"
            info += f"🔥 Конфликт: {world.get('conflict_level', 0):.0%}\n"
            info += f"✨ Магия: {world.get('magic_level', 0):.0%}\n"
            info += f"🔧 Технологии: {world.get('technology_level', 0):.0%}\n"

            if world.get('description'):
                info += f"\n📖 {world['description'][:200]}...\n"

            return info
        except Exception as e:
            return f"❌ Ошибка: {e}"

    def get_all_worlds(self) -> str:
        """Возвращает список всех миров"""
        if not self.world_engine_enabled or self.world_engine is None:
            return "❌ WorldEngine не доступен"
        try:
            worlds = self.world_engine.get_all_worlds()
            if not worlds:
                return "📭 Нет созданных миров"

            result = "🌍 **Все миры:**\n\n"
            for name in worlds:
                summary = self.world_engine.get_world_summary(name)
                if summary:
                    result += f"• **{name}** ({summary.get('genre', '?')}) — {summary.get('npc_count', 0)} NPC, {summary.get('event_count', 0)} событий\n"

            return result
        except Exception as e:
            return f"❌ Ошибка: {e}"

    def generate_event(self, world_name: str) -> str:
        """Генерирует событие в мире"""
        if not self.world_engine_enabled or self.world_engine is None:
            return "❌ WorldEngine не доступен"
        try:
            event = self.world_engine.generate_event(world_name)
            if not event:
                return f"❌ Мир '{world_name}' не найден"

            result = f"📜 **Событие в {world_name}:** {event.title}\n"
            result += f"📝 {event.description}\n"
            result += f"⚡ Тип: {event.type}, Серьёзность: {event.severity}\n"
            result += f"📍 Место: {event.location}\n"
            result += f"🔗 Последствия: {', '.join(event.consequences)}\n"

            return result
        except Exception as e:
            return f"❌ Ошибка: {e}"

    def check_consistency(self, world_name: str) -> str:
        """Проверяет консистентность лора"""
        if not self.world_engine_enabled or self.world_engine is None:
            return "❌ WorldEngine не доступен"
        try:
            consistency = self.world_engine.check_consistency(world_name)

            result = f"🔍 **Проверка {world_name}:**\n"
            result += f"📊 Фактов: {consistency['total_facts']}\n"
            result += f"👥 NPC: {consistency['total_npcs']}\n"
            result += f"⚔️ Фракции: {consistency['total_factions']}\n"
            result += f"⚠️ Проблем: {consistency['issues_count']}\n"

            if consistency['issues']:
                result += "\n**Проблемы:**\n"
                for issue in consistency['issues'][:5]:
                    result += f"• {issue.get('type', '?')}: {issue.get('fact1', '')[:50]}...\n"

            result += f"\n{'✅ Консистентен' if consistency['is_consistent'] else '❌ Есть проблемы'}\n"
            return result
        except Exception as e:
            return f"❌ Ошибка: {e}"

    def get_world_events(self, world_name: str, limit: int = 10) -> str:
        """Возвращает последние события мира"""
        if not self.world_engine_enabled or self.world_engine is None:
            return "❌ WorldEngine не доступен"
        try:
            events = self.world_engine.get_world_events(world_name, limit)
            if not events:
                return f"📭 В '{world_name}' пока нет событий"

            result = f"📜 **Последние события {world_name}:**\n\n"
            for event in events[-limit:]:
                result += f"• **{event['title']}** ({event['date'][:10]})\n"
                result += f"  {event['description'][:100]}...\n\n"

            return result
        except Exception as e:
            return f"❌ Ошибка: {e}"

    def get_npc_info(self, world_name: str, npc_name: str) -> str:
        """Возвращает информацию о NPC"""
        if not self.world_engine_enabled or self.world_engine is None:
            return "❌ WorldEngine не доступен"
        try:
            npc = self.world_engine.get_npc_summary(world_name, npc_name)
            if not npc:
                return f"❌ NPC '{npc_name}' не найден в '{world_name}'"

            result = f"👤 **{npc['name']}**\n"
            result += f"🎭 Роль: {npc['role']}\n"
            result += f"🎂 Возраст: {npc['age']}\n"
            result += f"🧬 Раса: {npc['race']}\n"
            result += f"🎨 Характер: {npc['personality']}\n"
            result += f"📍 Место: {npc['location']}\n"
            result += f"💚 Настроение: {npc['mood']}\n"
            result += f"⭐ Влияние: {npc['influence']:.0%}\n"
            result += f"🤝 Отношения: {npc['relations_count']}\n"
            result += f"📝 Воспоминания: {npc['memories_count']}\n"
            result += f"{'💀 Мёртв' if not npc.get('alive', True) else '✅ Жив'}\n"

            return result
        except Exception as e:
            return f"❌ Ошибка: {e}"

    async def start_background_cycle(self) -> str:
        """Запускает фоновый цикл развития миров"""
        if not self.world_engine_enabled or self.world_engine is None:
            return "❌ WorldEngine не доступен"
        try:
            if self.world_engine.background_engine.running:
                return "⏳ Фоновый цикл уже запущен"

            # Запускаем в отдельном потоке
            loop = asyncio.get_event_loop()
            await loop.run_in_executor(None, self._start_bg_cycle_sync)

            return "🔄 Фоновый цикл запущен! Миры будут развиваться автоматически."
        except Exception as e:
            return f"❌ Ошибка: {e}"

    def _start_bg_cycle_sync(self):
        """Синхронная обёртка для запуска фонового цикла"""
        if self.world_engine is None:
            return
        worlds = self.world_engine.get_all_worlds()
        asyncio.run(self.world_engine.start_background_cycle(worlds))

    def stop_background_cycle(self) -> str:
        """Останавливает фоновый цикл"""
        if not self.world_engine_enabled or self.world_engine is None:
            return "❌ WorldEngine не доступен"
        try:
            self.world_engine.stop_background_cycle()
            return "🛑 Фоновый цикл остановлен"
        except Exception as e:
            return f"❌ Ошибка: {e}"

    def get_world_status(self) -> str:
        """Возвращает статус всех систем WorldEngine"""
        if not self.world_engine_enabled or self.world_engine is None:
            return "❌ WorldEngine не доступен"
        try:
            status = self.world_engine.get_status()

            result = "🌍 **Статус WorldEngine:**\n"
            result += f"📊 Всего миров: {status['total_worlds']}\n"
            result += f"🔄 Фоновый цикл: {'✅ Запущен' if status['background_running'] else '❌ Остановлен'}\n"
            result += f"⏱ Циклов: {status['cycle_count']}\n\n"

            if status['worlds']:
                result += "**Миры:**\n"
                for world in status['worlds'][:5]:
                    result += f"• {world['name']} ({world.get('genre', '?')}) — {world.get('npc_count', 0)} NPC, {world.get('event_count', 0)} событий\n"

            return result
        except Exception as e:
            return f"❌ Ошибка: {e}"