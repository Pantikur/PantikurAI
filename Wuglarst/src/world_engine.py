# world_engine.py — Полная система управления мирами бота
# Включает: базу данных миров, события, NPC с памятью, проверку консистентности, фоновый цикл

import os
import json
import random
import re
import asyncio
import hashlib
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Any, Set, Tuple
from dataclasses import dataclass, field, asdict
from enum import Enum


# ========================
# ENUMS & DATA CLASSES
# ========================

class WorldState(Enum):
    """Состояние мира"""
    DRAFT = "draft"           # Черновик — только создан
    BIRTH = "birth"           # Рождение — первые события
    GROWING = "growing"       # Рост — активное развитие
    PEACE = "peace"           # Мирная эпоха
    WAR = "war"               # Война/конфликт
    CRISIS = "crisis"         # Кризис
    RENAISSANCE = "renaissance" # Возрождение
    DECLINE = "decline"       # Упадок
    REBIRTH = "rebirth"       # Перерождение


class EventSeverity(Enum):
    """Серьёзность события"""
    MINOR = "minor"           # Незначительное
    MODERATE = "moderate"     # Умеренное
    MAJOR = "major"           # Важное
    CATASTROPHIC = "catastrophic"  # Катастрофическое
    LEGENDARY = "legendary"   # Легендарное


class NPCRelation(Enum):
    """Отношения между NPC"""
    ALLY = "ally"
    ENEMY = "enemy"
    NEUTRAL = "neutral"
    LOVER = "lover"
    MASTER = "master"
    SERVANT = "servant"
    FRIEND = "friend"
    RIVAL = "rival"


@dataclass
class NPC:
    """Персонаж мира с памятью"""
    name: str
    age: int
    race: str
    role: str              # Профессия/роль в мире
    personality: str       # Характер
    skills: List[str] = field(default_factory=list)
    secrets: List[str] = field(default_factory=list)
    goals: List[str] = field(default_factory=list)
    relations: Dict[str, Dict[str, Any]] = field(default_factory=dict)
    memories: List[Dict] = field(default_factory=list)
    location: str = "unknown"
    alive: bool = True
    created_at: str = ""
    last_seen: str = ""
    influence: float = 0.5  # Влияние в мире (0-1)
    mood: str = "neutral"   # Текущее настроение

    def to_dict(self) -> Dict:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict) -> 'NPC':
        return cls(**{k: v for k, v in data.items() if k in cls.__dataclass_fields__})


@dataclass
class WorldEvent:
    """Событие в мире"""
    id: str
    world_name: str
    title: str
    description: str
    type: str                # political, military, economic, cultural, natural, magical, personal
    severity: str
    date: str
    participants: List[str]  # NPC или группы
    consequences: List[str]  # Последствия
    location: str = "unknown"
    resolved: bool = False
    resolution: str = ""
    lore_impact: float = 0.3  # Влияние на лор (0-1)

    def to_dict(self) -> Dict:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict) -> 'WorldEvent':
        return cls(**{k: v for k, v in data.items() if k in cls.__dataclass_fields__})


@dataclass
class WorldFact:
    """Факт о мире (атомарное знание)"""
    id: str
    world_name: str
    statement: str
    category: str            # geography, history, culture, politics, magic, technology, economy, race
    confidence: float = 1.0  # Уверенность в факте
    sources: List[str] = field(default_factory=list)  # Откуда известен
    created_at: str = ""
    last_verified: str = ""
    contradicts: List[str] = field(default_factory=list)  # ID противоречащих фактов
    verified: bool = True

    def to_dict(self) -> Dict:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict) -> 'WorldFact':
        return cls(**{k: v for k, v in data.items() if k in cls.__dataclass_fields__})


# ========================
# WORLD FACTORY
# ========================

class WorldFactory:
    """Создаёт миры из шаблонов и знаний"""

    WORLD_TEMPLATES = {
        "geography": [
            "Континент {name} разделён {number} великими хребтами, между которыми лежат бескрайние равнины, покрытые {plant}.",
            "Мир состоит из {number} архипелагов, парящих в облаках на высоте {height} метров.",
            "Под поверхностью планеты простирается сеть пещер глубиной до {depth} км, где течёт светящаяся река.",
            "Мир плоский как диск, и его края обрушиваются в Бездну, откуда нет возврата.",
            "Континент {name} окружён Океаном Времени, где вода течёт вспять и старики молодятся.",
        ],
        "society": [
            "Общество разделено на {number} каст, каждая из которых управляет своим элементом.",
            "Власть принадлежит Совету {number} мудрецов, которые выбирают лидера жребием.",
            "Королевство правит через систему заложников: каждый дворянин отправляет ребёнка в столицу.",
            "Демократия здесь буквальна: каждый вопрос решается голосованием на площади.",
            "Фактическая власть у гильдий, а короли — лишь марионетки для народа.",
        ],
        "magic_tech": [
            "Магия основана на звуке: заклинания — это песни, а молчание — самое сильное оружие.",
            "Технологии работают на биологической энергии: машины питаются кровью добровольцев.",
            "ИИ стал религией, а люди строят ему храмы из серверов и кабелей.",
            "Магия — это договор с духами природы, а маги — посредники между мирами.",
            "Технологии забыты, но их руины до сих пор порождают аномалии и мутантов.",
        ],
        "conflict": [
            "Две великие державы ведут холодную войну за контроль над {resource}.",
            "Древнее зло пробуждается каждую {number} лет, и только {hero_title} может его остановить.",
            "Между расами идёт тихая война за ресурсы, замаскированная под торговлю.",
            "Культы противостоят официальным институтам, пытаясь изменить порядок вещей.",
            "Внутри общества растёт разрыв между элитой и простыми людьми.",
        ]
    }

    NPC_TEMPLATES = {
        "roles": [
            "странствующий маг", "капитан торгового корабля", "главный инженер",
            "предводитель гильдии", "придворный советник", "охотник на чудовищ",
            "алхимик", "пророк", "наёмник", "учёный-антрополог",
            "кузнец-чародей", "капитан гвардии", "торговец артефактами",
            "хранитель библиотеки", "шпион", "беглый принц/принцесса",
            "лечебник", "картограф", "пилот воздушного корабля", "жрец"
        ],
        "personalities": [
            "амбициозный и хитрый", "добрый, но наивный", "мрачный циник",
            "весёлый безбашенный", "строгий и справедливый", "загадочный и отстранённый",
            "горячий и импульсивный", "расчётливый и холодный", "щедрый и добрый",
            "ревнивый и собственнический", "любопытный и неугомонный", "патриотичный и решительный"
        ],
        "races": [
            "человек", "эльф", "орк", "дварф", "полуэльф",
            "полукровка", "нежить", "киборг", "андроид", "драконид",
            "демон", "ангел", "голем", "феникс-человек", "тенец"
        ]
    }

    @classmethod
    def create_world(cls, genre: str, tag: str, existing_facts: Optional[List[WorldFact]] = None) -> Dict:
        """Создаёт новый мир на основе шаблонов и знаний"""

        world = {
            "name": cls._generate_world_name(genre, tag),
            "genre": genre,
            "tags": [tag],
            "state": WorldState.DRAFT.value,
            "created_at": datetime.now().isoformat(),
            "last_updated": datetime.now().isoformat(),
            "era": 1,  # Номер эпохи
            "description": "",
            "laws": [],
            "traditions": [],
            "unspoken_rules": [],
            "geography": [],
            "history": [],
            "factions": [],
            "npcs": [],
            "events": [],
            "facts": [],
            "mood": "neutral",  # Общее настроение мира
            "conflict_level": 0.0,  # 0-1
            "technology_level": 0.0,  # 0-1
            "magic_level": 0.0,  # 0-1
            "population": 0,
            "resources": {},
        }

        # Генерируем базовые элементы из шаблонов
        world["geography"] = cls._generate_geography(genre, tag)
        world["laws"] = cls._generate_laws(genre, tag)
        world["traditions"] = cls._generate_traditions(genre, tag)
        world["unspoken_rules"] = cls._generate_unspoken_rules(genre, tag)

        # Создаём начальных NPC
        world["npcs"] = cls._generate_initial_npcs(genre, tag, count=random.randint(5, 12))

        # Создаём фракции
        world["factions"] = cls._generate_factions(genre, tag)

        # Генерируем описание
        world["description"] = cls._generate_description(world, genre, tag)

        # Создаём начальные факты
        world["facts"] = cls._extract_facts(world, genre, tag)

        return world

    @classmethod
    def _generate_world_name(cls, genre: str, tag: str) -> str:
        prefixes = {
            "Фэнтези": ["Тёмный", "Сияющий", "Забытый", "Вечный", "Падший", "Кристальный", "Звёздный"],
            "Киберпанк": ["Нео-", "Квантовый", "Нейро-", "Синтетический", "Цифровой", "Голографический"],
            "Постапокалипсис": ["Пепельный", "Пустошь", "Ржавый", "Выжженный", "Последний", "Послеледниковый"],
            "Научная фантастика": ["Орбитальный", "Галактический", "Космический", "Звёздный", "Межзвёздный"],
            "Стимпанк": ["Паровой", "Медный", "Шестерёнчатый", "Паровой", "Бронзовый"],
            "Повседневность": ["Обычный", "Тихий", "Уютный", "Простой", "Знакомый"],
        }
        suffixes = ["Хранитель", "Звёзд", "Теней", "Мечты", "Хаоса", "Света", "Бездны", "Вечности",
                    "Рассвета", "Заката", "Пустоты", "Искры", "Кристалла", "Дракона", "Волка"]

        genre_prefixes = prefixes.get(genre, prefixes["Фэнтези"])
        prefix = random.choice(genre_prefixes)
        suffix = random.choice(suffixes)

        return f"{prefix} {suffix}"

    @classmethod
    def _generate_geography(cls, genre: str, tag: str) -> List[str]:
        templates = cls.WORLD_TEMPLATES["geography"]
        count = random.randint(2, 4)
        results = []

        for _ in range(count):
            template = random.choice(templates)
            text = template.format(
                name=cls._generate_region_name(),
                number=random.choice([3, 5, 7, 12]),
                height=random.choice([1000, 5000, 10000, 50000]),
                depth=random.choice([10, 50, 100, 500]),
                plant=random.choice(["светящихся деревьев", "кристаллов", "тумана", "папоротников"]),
            )
            results.append(text)

        return results

    @classmethod
    def _generate_laws(cls, genre: str, tag: str) -> List[str]:
        count = random.randint(3, 6)
        laws = []
        templates = [
            "Все мысли, записанные в импланты, доступны корпорации по запросу",
            "Владение нелегальным артефактом карается изгнанием",
            "Деньги привязаны к био-рейтингу: чем полезнее, тем богаче",
            "Искусственный интеллект приравнён к человеку",
            "Любой может купить чужое воспоминание на чёрном рынке",
            "Запрещено модифицировать геном без лицензии Совета",
            "Каждый гражданин обязан служить обществу {number} лет",
            "Магия доступна только тем, кто прошёл Обряд",
            "Война запрещена, но наёмники существуют в серой зоне",
            "Никто не знает, что находится за {location}",
        ]

        for _ in range(count):
            template = random.choice(templates)
            law = template.format(
                number=random.randint(5, 20),
                location=random.choice(["Горящих Гор", "Тихого Океана", "Шепчущего Леса", "Края Мироздания"])
            )
            laws.append(law)

        return laws

    @classmethod
    def _generate_traditions(cls, genre: str, tag: str) -> List[str]:
        count = random.randint(2, 5)
        traditions = []
        templates = [
            "Каждый новый год все отключают импланты на 24 часа — «День тишины»",
            "Перед свадьбой пары обмениваются фрагментами памяти",
            "Молодёжь устраивает «гонки глитчей» — взламывают рекламу на лету",
            "Старейшины хранят «живые архивы» — импланты с воспоминаниями предков",
            "При посадке на новую землю сажают дерево из семян Земли",
            "Перед полётом астронавты пишут письмо будущему поколению",
            "День Земли — все колонии гасят свет в честь родной планеты",
            "Новорождённым дают имя по созвездию, в котором их нашли",
            "Каждую полночь зажигают свечи за умершие идеи",
            "Молодые проходят испытание одиночеством в Пустоши",
        ]

        for _ in range(count):
            traditions.append(random.choice(templates))

        return traditions

    @classmethod
    def _generate_unspoken_rules(cls, genre: str, tag: str) -> List[str]:
        count = random.randint(2, 4)
        templates = [
            "Не смотри в глаза с красными имплантами — это наёмники без чипа",
            "В зоне «мёртвого сигнала» нельзя говорить о работе",
            "Если кто-то предлагает «чистый чип» — убегай, это ловушка",
            "Никогда не храни чужие воспоминания — они могут содержать вирусы",
            "Если сигнал из глубокого космоса — не отвечай, жди Совета",
            "Не пей воду с чужих планет — микробы могут мутировать",
            "Если корабль меняет курс без разрешения — он уже потерян",
            "Никогда не открывай люк на орбите — там нет воздуха",
            "Не верь тому, кто говорит с твоим голосом",
            "Если тень двигается не так, как должна — убегай",
        ]

        selected = random.sample(templates, min(count, len(templates)))
        return selected

    @classmethod
    def _generate_region_name(cls) -> str:
        prefixes = ["Север", "Юг", "Восток", "Запад", "Центр", "Пустошь", "Тень", "Свет"]
        suffixes = ["ия", "ия", "ланд", "ия", "ия", "ия", "ия", "ия"]
        return random.choice(prefixes) + random.choice(suffixes)

    @classmethod
    def _generate_initial_npcs(cls, genre: str, tag: str, count: int = 8) -> List[Dict]:
        npcs = []
        templates = cls.NPC_TEMPLATES

        for i in range(count):
            npc = {
                "name": cls._generate_npc_name(),
                "age": random.randint(18, 120),
                "race": random.choice(templates["races"]),
                "role": random.choice(templates["roles"]),
                "personality": random.choice(templates["personalities"]),
                "skills": random.sample(["combat", "magic", "diplomacy", "stealth", "alchemy",
                                         "engineering", "meditation", "navigation", "cooking",
                                         "forging", "healing", "spying"], k=random.randint(1, 3)),
                "secrets": [f"Скрывает {random.choice(['прошлое', 'происхождение', 'любовь', 'преступление', 'дар'])}"],
                "goals": [f"Хочет {random.choice(['найти себя', 'стать сильным', 'спасти мир', 'отомстить', 'создать что-то великое'])}"],
                "relations": {},
                "memories": [],
                "location": random.choice(["Столица", "Пограничье", "Подземелье", "Корабль", "Лес", "Горы"]),
                "alive": True,
                "created_at": datetime.now().isoformat(),
                "last_seen": datetime.now().isoformat(),
                "influence": round(random.uniform(0.1, 0.9), 2),
                "mood": random.choice(["neutral", "happy", "anxious", "angry", "curious", "melancholic"]),
            }
            npcs.append(npc)

        # Создаём связи между NPC
        for i, npc in enumerate(npcs):
            num_relations = random.randint(1, 3)
            other_indices = [j for j in range(len(npcs)) if j != i]
            for _ in range(min(num_relations, len(other_indices))):
                target_idx = random.choice(other_indices)
                target_name = npcs[target_idx]["name"]
                relation = random.choice([r.value for r in NPCRelation])
                npc["relations"][target_name] = {"relation": relation, "strength": round(random.uniform(0.2, 1.0), 2)}
                other_indices.remove(target_idx)

        return npcs

    @classmethod
    def _generate_npc_name(cls) -> str:
        first_names = [
            "Александр", "Мария", "Дмитрий", "Елена", "Артём", "Анна",
            "Максим", "Софья", "Иван", "Виктория", "Никита", "Полина",
            "Кирилл", "Дарья", "Тимур", "Ольга", "Роман", "Ксения",
            "Sebastian", "Luna", "Orion", "Nova", "Zephyr", "Aria"
        ]
        last_names = [
            "Ветров", "Звёздный", "Теневой", "Огненный", "Ледяной",
            "Каменный", "Серебряный", "Золотой", "Морозов", "Светлов",
            "Storm", "Shadow", "Fire", "Ice", "Star", "Moon"
        ]
        return f"{random.choice(first_names)} {random.choice(last_names)}"

    @classmethod
    def _generate_factions(cls, genre: str, tag: str) -> List[Dict]:
        count = random.randint(2, 5)
        factions = []
        faction_templates = [
            {
                "name": "Гильдия {name}",
                "type": "economic",
                "description": "Контролирует торговлю и ремёсла",
                "power": random.uniform(0.3, 0.9),
            },
            {
                "name": "Орден {name}",
                "type": "military",
                "description": "Военная организация, защищающая границы",
                "power": random.uniform(0.4, 1.0),
            },
            {
                "name": "Культ {name}",
                "type": "religious",
                "description": "Поклоняется древним силам",
                "power": random.uniform(0.2, 0.7),
            },
            {
                "name": "Корпорация {name}",
                "type": "corporate",
                "description": "Контролирует технологии и ресурсы",
                "power": random.uniform(0.5, 1.0),
            },
            {
                "name": "Сопротивление {name}",
                "type": "rebel",
                "description": "Борется против системы",
                "power": random.uniform(0.1, 0.5),
            },
        ]

        faction_names = ["Аврора", "Веспер", "Кронос", "Элизиум", "Тенарис", "Зенит", "Нова", "Аэрон"]

        for _ in range(count):
            template = random.choice(faction_templates)
            faction = template.copy()
            faction["name"] = template["name"].format(name=random.choice(faction_names))
            faction["created_at"] = datetime.now().isoformat()
            faction["allies"] = []
            faction["enemies"] = []
            factions.append(faction)

        # Создаём связи между фракциями
        for i, faction in enumerate(factions):
            num_relations = random.randint(0, 2)
            other_indices = [j for j in range(len(factions)) if j != i]
            for _ in range(min(num_relations, len(other_indices))):
                target_idx = random.choice(other_indices)
                if random.random() < 0.5:
                    faction["allies"].append(factions[target_idx]["name"])
                else:
                    faction["enemies"].append(factions[target_idx]["name"])
                other_indices.remove(target_idx)

        return factions

    @classmethod
    def _generate_description(cls, world: Dict, genre: str, tag: str) -> str:
        """Генерирует связное описание мира"""
        parts = []

        if world.get("geography"):
            parts.append(world["geography"][0])

        if world.get("laws"):
            parts.append(f"В этом мире действуют строгие законы: {world['laws'][0]}.")

        if world.get("factions"):
            factions = [f["name"] for f in world["factions"][:2]]
            parts.append(f"На сцене доминируют {', '.join(factions)}.")

        if world.get("npcs"):
            key_npc = world["npcs"][0]
            parts.append(f"Ключевая фигура — {key_npc['name']}, {key_npc['role']}, {key_npc['personality']}.")

        return " ".join(parts)

    @classmethod
    def _extract_facts(cls, world: Dict, genre: str, tag: str) -> List[Dict]:
        """Извлекает атомарные факты из мира"""
        facts = []
        world_name = world["name"]

        # Географические факты
        for geo in world.get("geography", []):
            fact_id = hashlib.md5(f"{world_name}:geo:{geo[:50]}".encode()).hexdigest()[:12]
            facts.append({
                "id": fact_id,
                "world_name": world_name,
                "statement": geo,
                "category": "geography",
                "confidence": 0.9,
                "sources": ["template_generation"],
                "created_at": datetime.now().isoformat(),
                "last_verified": datetime.now().isoformat(),
                "contradicts": [],
                "verified": True
            })

        # Факты о законах
        for law in world.get("laws", []):
            fact_id = hashlib.md5(f"{world_name}:law:{law[:50]}".encode()).hexdigest()[:12]
            facts.append({
                "id": fact_id,
                "world_name": world_name,
                "statement": f"В мире действует закон: {law}",
                "category": "politics",
                "confidence": 0.95,
                "sources": ["template_generation"],
                "created_at": datetime.now().isoformat(),
                "last_verified": datetime.now().isoformat(),
                "contradicts": [],
                "verified": True
            })

        # Факты о традициях
        for trad in world.get("traditions", []):
            fact_id = hashlib.md5(f"{world_name}:trad:{trad[:50]}".encode()).hexdigest()[:12]
            facts.append({
                "id": fact_id,
                "world_name": world_name,
                "statement": f"Традиция: {trad}",
                "category": "culture",
                "confidence": 0.9,
                "sources": ["template_generation"],
                "created_at": datetime.now().isoformat(),
                "last_verified": datetime.now().isoformat(),
                "contradicts": [],
                "verified": True
            })

        return facts


# ========================
# WORLD DATABASE
# ========================

class WorldDatabase:
    """Хранит и управляет всеми мирами"""

    def __init__(self, db_path: str = "data/worlds"):
        self.db_path = Path(db_path)
        self.db_path.mkdir(parents=True, exist_ok=True)
        self.index_file = self.db_path / "index.json"
        self.index = self._load_index()
        print(f"✅ WorldDatabase инициализирован: {db_path}")

    def _load_index(self) -> Dict:
        if self.index_file.exists():
            try:
                with open(self.index_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception:
                return {"worlds": {}, "last_scan": None}
        return {"worlds": {}, "last_scan": None}

    def _save_index(self):
        self.index["last_scan"] = datetime.now().isoformat()
        with open(self.index_file, 'w', encoding='utf-8') as f:
            json.dump(self.index, f, ensure_ascii=False, indent=2)

    def create_world(self, genre: str, tag: str) -> str:
        """Создаёт новый мир и возвращает его имя"""
        world_data = WorldFactory.create_world(genre, tag)
        world_name = world_data["name"]

        # Сохраняем мир
        self.save_world(world_name, world_data)

        # Обновляем индекс
        self.index["worlds"][world_name] = {
            "genre": genre,
            "tag": tag,
            "created_at": world_data["created_at"],
            "last_updated": world_data["last_updated"],
            "state": world_data["state"],
            "npc_count": len(world_data.get("npcs", [])),
            "event_count": len(world_data.get("events", [])),
            "fact_count": len(world_data.get("facts", [])),
        }
        self._save_index()

        print(f"🌍 Создан мир: {world_name} (genre={genre}, tag={tag})")
        return world_name

    def save_world(self, world_name: str, world_data: Dict):
        """Сохраняет мир в JSON-файл"""
        filepath = self.db_path / f"{world_name}.json"
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(world_data, f, ensure_ascii=False, indent=2)

    def load_world(self, world_name: str) -> Optional[Dict]:
        """Загружает мир из файла"""
        filepath = self.db_path / f"{world_name}.json"
        if not filepath.exists():
            return None
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"❌ Ошибка загрузки мира {world_name}: {e}")
            return None

    def get_all_worlds(self) -> List[str]:
        """Возвращает список всех имён миров"""
        return list(self.index["worlds"].keys())

    def get_world_summary(self, world_name: str) -> Optional[Dict]:
        """Возвращает сводку о мире"""
        return self.index["worlds"].get(world_name)

    def delete_world(self, world_name: str) -> bool:
        """Удаляет мир"""
        filepath = self.db_path / f"{world_name}.json"
        if filepath.exists():
            filepath.unlink()
        if world_name in self.index["worlds"]:
            del self.index["worlds"][world_name]
            self._save_index()
            return True
        return False

    def update_world_state(self, world_name: str, state: str):
        """Обновляет состояние мира"""
        world = self.load_world(world_name)
        if world:
            world["state"] = state
            world["last_updated"] = datetime.now().isoformat()
            self.save_world(world_name, world)

            if world_name in self.index["worlds"]:
                self.index["worlds"][world_name]["state"] = state
                self.index["worlds"][world_name]["last_updated"] = world["last_updated"]
                self._save_index()


# ========================
# EVENT ENGINE
# ========================

class EventEngine:
    """Генерирует и управляет событиями в мире"""

    EVENT_TEMPLATES = {
        "political": [
            {
                "title": "Политический переворот",
                "description": "{npc1} организует заговор против {npc2}. Гвардия переходит на сторону заговорщиков.",
                "type": "political",
                "severity": "major",
                "consequences": ["Смена власти", "Новые законы", "Нестабильность"],
            },
            {
                "title": "Дипломатический саммит",
                "description": "Лидеры {faction1} и {faction2} встречаются для переговоров. Атмосфера напряжённая.",
                "type": "political",
                "severity": "moderate",
                "consequences": ["Союзы", "Договоры", "Новые границы"],
            },
            {
                "title": "Выборы лидера",
                "description": "В {location} проходят выборы. Кандидаты обещают перемены.",
                "type": "political",
                "severity": "moderate",
                "consequences": ["Новый лидер", "Изменение политики"],
            },
        ],
        "military": [
            {
                "title": "Пограничный конфликт",
                "description": "Военные отряды {faction1} сталкиваются с {faction2} на границе.",
                "type": "military",
                "severity": "major",
                "consequences": ["Жертвы", "Новые укрепления", "Эскалация"],
            },
            {
                "title": "Наёмники в городе",
                "description": "Отряд наёмников во главе с {npc1} прибывает в {location}.",
                "type": "military",
                "severity": "moderate",
                "consequences": ["Нанятые защитники", "Проблемы с местными"],
            },
            {
                "title": "Осада крепости",
                "description": "{faction1} осаждают крепость {location}. Защитники держатся.",
                "type": "military",
                "severity": "catastrophic",
                "consequences": ["Разрушения", "Гуманитарный кризис", "Падение крепости"],
            },
        ],
        "cultural": [
            {
                "title": "Фестиваль",
                "description": "В {location} проходит великий фестиваль. Люди празднуют {tradition}.",
                "type": "cultural",
                "severity": "minor",
                "consequences": ["Единство", "Новые традиции", "Рост экономики"],
            },
            {
                "title": "Открытие искусства",
                "description": "{npc1} представляет новое произведение искусства в {location}.",
                "type": "cultural",
                "severity": "minor",
                "consequences": ["Вдохновение", "Споры", "Культурный подъём"],
            },
            {
                "title": "Религиозное пробуждение",
                "description": "В {location} появляется новый пророк, несущий слово {deity}.",
                "type": "cultural",
                "severity": "major",
                "consequences": ["Новый культ", "Раскол общества", "Чудеса"],
            },
        ],
        "natural": [
            {
                "title": "Природная катастрофа",
                "description": "В {location} происходит землетрясение/ураган/наводнение.",
                "type": "natural",
                "severity": "catastrophic",
                "consequences": ["Разрушения", "Жертвы", "Переселение"],
            },
            {
                "title": "Аномальное явление",
                "description": "Небо над {location} окрашивается в необычные цвета. Люди в восторге и ужасе.",
                "type": "natural",
                "severity": "moderate",
                "consequences": ["Суеверия", "Научные исследования", "Паника"],
            },
            {
                "title": "Миграция существ",
                "description": "Тысячи {creature} мигрируют через {location}.",
                "type": "natural",
                "severity": "moderate",
                "consequences": ["Охота", "Опасность", "Новые ресурсы"],
            },
        ],
        "magical": [
            {
                "title": "Магическая аномалия",
                "description": "В {location} обнаружена нестабильная магическая зона. Магия работает непредсказуемо.",
                "type": "magical",
                "severity": "major",
                "consequences": ["Исследования", "Опасность", "Новые артефакты"],
            },
            {
                "title": "Пробуждение силы",
                "description": "{npc1} неожиданно пробуждает древнюю магическую способность.",
                "type": "magical",
                "severity": "legendary",
                "consequences": ["Изменение баланса сил", "Охота на героя", "Новая эра"],
            },
            {
                "title": "Древний артефакт",
                "description": "В {location} найден древний артефакт неведомого происхождения.",
                "type": "magical",
                "severity": "legendary",
                "consequences": ["Борьба за артефакт", "Новые знания", "Опасность"],
            },
        ],
        "economic": [
            {
                "title": "Экономический бум",
                "description": "В {location} обнаружены новые ресурсы. Торговля процветает.",
                "type": "economic",
                "severity": "moderate",
                "consequences": ["Рост богатства", "Иммиграция", "Новые рабочие места"],
            },
            {
                "title": "Экономический кризис",
                "description": "Цена на {resource} резко упала. Люди теряют заработок.",
                "type": "economic",
                "severity": "major",
                "consequences": ["Бедность", "Беспорядки", "Эмиграция"],
            },
            {
                "title": "Новый торговый путь",
                "description": "Открыт новый торговый маршрут через {location}.",
                "type": "economic",
                "severity": "moderate",
                "consequences": ["Рост торговли", "Богатение", "Конкуренция"],
            },
        ],
    }

    CREATURES = ["волков", "драконов", "птиц", "рыб", "насекомых", "призраков", "теней"]
    RESOURCES = ["золота", "магической энергии", "воды", "еды", "топлива", "кристаллов"]
    DEITIES = ["Древних", "Звёзд", "Бездны", "Света", "Теней", "Природы"]

    def __init__(self, world_db: WorldDatabase):
        self.world_db = world_db

    def generate_event(self, world_name: str) -> Optional[WorldEvent]:
        """Генерирует случайное событие для мира"""
        world = self.world_db.load_world(world_name)
        if not world:
            return None

        # Выбираем категорию события на основе состояния мира
        category = self._select_event_category(world)

        # Выбираем шаблон
        templates = self.EVENT_TEMPLATES.get(category, self.EVENT_TEMPLATES["political"])
        template = random.choice(templates)

        # Заполняем шаблон данными мира
        description = template["description"]
        description = description.replace("{npc1}", self._pick_npc(world))
        description = description.replace("{npc2}", self._pick_npc(world, exclude=self._pick_npc(world)))
        description = description.replace("{faction1}", self._pick_faction(world))
        description = description.replace("{faction2}", self._pick_faction(world, exclude=self._pick_faction(world)))
        description = description.replace("{location}", self._pick_location(world))
        description = description.replace("{tradition}", random.choice(world.get("traditions", ["народные праздники"])))
        description = description.replace("{deity}", random.choice(self.DEITIES))
        description = description.replace("{creature}", random.choice(self.CREATURES))
        description = description.replace("{resource}", random.choice(self.RESOURCES))

        # Создаём событие
        event_id = hashlib.md5(f"{world_name}:{datetime.now().isoformat()}:{random.random()}".encode()).hexdigest()[:12]

        event = WorldEvent(
            id=event_id,
            world_name=world_name,
            title=template["title"],
            description=description,
            type=template["type"],
            severity=template["severity"],
            date=datetime.now().isoformat(),
            participants=[self._pick_npc(world)],
            consequences=template["consequences"],
            location=self._pick_location(world),
            lore_impact=random.uniform(0.1, 0.8)
        )

        # Сохраняем событие
        self._save_event(world_name, event)

        # Обновляем NPC память
        self._update_npc_memories(world_name, event)

        # Обновляем состояние мира
        self._update_world_state_from_event(world_name, event)

        print(f"📜 Событие в {world_name}: {event.title} ({event.severity})")
        return event

    def _select_event_category(self, world: Dict) -> str:
        """Выбирает категорию события на основе состояния мира"""
        state = world.get("state", "peace")
        conflict_level = world.get("conflict_level", 0)

        # Воевающее состояние → военные события
        if state in [WorldState.WAR.value, WorldState.CRISIS.value]:
            return random.choice(["military", "political", "natural"])

        # Высокий конфликт → военные/политические
        if conflict_level > 0.7:
            return random.choice(["military", "political", "economic"])

        # Мирное состояние → культурные/экономические
        if state in [WorldState.PEACE.value, WorldState.RENAISSANCE.value]:
            return random.choice(["cultural", "economic", "magical", "natural"])

        # По умолчанию — случайная
        return random.choice(list(self.EVENT_TEMPLATES.keys()))

    def _pick_npc(self, world: Dict, exclude: str = "") -> str:
        npcs = world.get("npcs", [])
        alive_npcs = [n for n in npcs if n.get("alive", True)]
        if not alive_npcs:
            return "Неизвестный персонаж"
        npc = random.choice(alive_npcs)
        if npc["name"] == exclude:
            alive_npcs.remove(npc)
            if not alive_npcs:
                return "Неизвестный персонаж"
            npc = random.choice(alive_npcs)
        return npc["name"]

    def _pick_faction(self, world: Dict, exclude: str = "") -> str:
        factions = world.get("factions", [])
        if not factions:
            return "Неизвестная фракция"
        faction = random.choice(factions)
        if faction["name"] == exclude:
            factions.remove(faction)
            if not factions:
                return "Неизвестная фракция"
            faction = random.choice(factions)
        return faction["name"]

    def _pick_location(self, world: Dict) -> str:
        npcs = world.get("npcs", [])
        locations = list(set([n.get("location", "unknown") for n in npcs]))
        if not locations:
            return "Неизвестное место"
        return random.choice(locations)

    def _save_event(self, world_name: str, event: WorldEvent):
        """Сохраняет событие в мир"""
        world = self.world_db.load_world(world_name)
        if not world:
            return

        if "events" not in world:
            world["events"] = []

        world["events"].append(event.to_dict())
        world["last_updated"] = datetime.now().isoformat()
        self.world_db.save_world(world_name, world)

    def _update_npc_memories(self, world_name: str, event: WorldEvent):
        """Добавляет событие в память NPC"""
        world = self.world_db.load_world(world_name)
        if not world:
            return

        for npc_name in event.participants:
            for npc in world.get("npcs", []):
                if npc["name"] == npc_name:
                    npc["memories"].append({
                        "event_id": event.id,
                        "event_title": event.title,
                        "date": event.date,
                        "description": event.description[:200],
                    })
                    npc["last_seen"] = datetime.now().isoformat()

        self.world_db.save_world(world_name, world)

    def _update_world_state_from_event(self, world_name: str, event: WorldEvent):
        """Обновляет состояние мира на основе события"""
        world = self.world_db.load_world(world_name)
        if not world:
            return

        severity = event.severity
        event_type = event.type

        # Катастрофические события повышают конфликт
        if severity in ["catastrophic", "legendary"]:
            world["conflict_level"] = min(1.0, world.get("conflict_level", 0) + 0.2)
            world["state"] = WorldState.CRISIS.value

        # Военные события
        if event_type == "military":
            world["conflict_level"] = min(1.0, world.get("conflict_level", 0) + 0.15)
            if world["conflict_level"] > 0.7:
                world["state"] = WorldState.WAR.value

        # Культурные события снижают конфликт
        if event_type == "cultural":
            world["conflict_level"] = max(0.0, world.get("conflict_level", 0) - 0.1)
            if world["conflict_level"] < 0.3 and world["state"] != WorldState.PEACE.value:
                world["state"] = WorldState.PEACE.value

        # Магические события могут дать ренессанс
        if event_type == "magical" and event.severity == "legendary":
            world["state"] = WorldState.RENAISSANCE.value
            world["conflict_level"] = max(0.0, world.get("conflict_level", 0) - 0.2)

        world["last_updated"] = datetime.now().isoformat()
        self.world_db.save_world(world_name, world)

    def get_world_events(self, world_name: str, limit: int = 20) -> List[Dict]:
        """Возвращает последние события мира"""
        world = self.world_db.load_world(world_name)
        if not world:
            return []
        events = world.get("events", [])
        return events[-limit:]


# ========================
# CONSISTENCY ENGINE
# ========================

class ConsistencyEngine:
    """Проверяет и поддерживает консистентность лора"""

    def __init__(self, world_db: WorldDatabase):
        self.world_db = world_db

    def check_consistency(self, world_name: str) -> Dict:
        """Проверяет мир на противоречия"""
        world = self.world_db.load_world(world_name)
        if not world:
            return {"error": "Мир не найден"}

        facts = world.get("facts", [])
        issues = []

        # Проверяем противоречия между фактами
        for i, fact1 in enumerate(facts):
            for j, fact2 in enumerate(facts):
                if i >= j:
                    continue

                if self._are_contradictory(fact1, fact2):
                    issues.append({
                        "type": "contradiction",
                        "fact1_id": fact1["id"],
                        "fact2_id": fact2["id"],
                        "fact1": fact1["statement"][:100],
                        "fact2": fact2["statement"][:100],
                    })

        # Проверяем согласованность NPC
        npcs = world.get("npcs", [])
        for npc in npcs:
            if npc.get("alive") and npc.get("memories"):
                for memory in npc["memories"]:
                    if "date" in memory:
                        # Проверяем, что память не из будущего
                        pass  # Упрощённая проверка

        # Проверяем связи фракций
        factions = world.get("factions", [])
        faction_names = [f["name"] for f in factions]
        for faction in factions:
            for ally in faction.get("allies", []):
                if ally not in faction_names:
                    issues.append({
                        "type": "orphan_relation",
                        "faction": faction["name"],
                        "relation": "ally",
                        "target": ally,
                    })

        return {
            "world": world_name,
            "total_facts": len(facts),
            "total_npcs": len(npcs),
            "total_factions": len(factions),
            "issues_count": len(issues),
            "issues": issues,
            "is_consistent": len(issues) == 0,
        }

    def _are_contradictory(self, fact1: Dict, fact2: Dict) -> bool:
        """Проверяют ли два факта противоречие"""
        # Факты должны быть из одной категории
        if fact1.get("category") != fact2.get("category"):
            return False

        stmt1 = fact1["statement"].lower()
        stmt2 = fact2["statement"].lower()

        # Простые проверки на противоречие
        contradiction_pairs = [
            ("запрещено", "разрешено"),
            ("мёртв", "жив"),
            ("уничтожен", "сохранён"),
            ("враг", "союзник"),
            ("нет", "есть"),
        ]

        for neg, pos in contradiction_pairs:
            if neg in stmt1 and pos in stmt2:
                return True
            if pos in stmt1 and neg in stmt2:
                return True

        return False

    def add_fact(self, world_name: str, statement: str, category: str, confidence: float = 0.9) -> Optional[WorldFact]:
        """Добавляет новый факт с проверкой на противоречия"""
        world = self.world_db.load_world(world_name)
        if not world:
            return None

        new_fact = WorldFact(
            id=hashlib.md5(f"{world_name}:{statement[:50]}:{datetime.now().isoformat()}".encode()).hexdigest()[:12],
            world_name=world_name,
            statement=statement,
            category=category,
            confidence=confidence,
            sources=["manual_addition"],
            created_at=datetime.now().isoformat(),
            last_verified=datetime.now().isoformat(),
            contradicts=[],
            verified=True
        )

        # Проверяем на противоречия
        existing_facts: List[Dict] = world.get("facts", [])
        for existing in existing_facts:
            if self._are_contradictory(new_fact.to_dict(), existing):
                new_fact.contradicts.append(existing.get("id", ""))
                if "contradicts" not in existing:
                    existing["contradicts"] = []
                existing["contradicts"].append(new_fact.id)
                new_fact.confidence *= 0.5  # Снижаем уверенность

        world["facts"].append(new_fact.to_dict())
        world["last_updated"] = datetime.now().isoformat()
        self.world_db.save_world(world_name, world)

        print(f"📝 Факт добавлен в {world_name}: {statement[:50]}...")
        return new_fact

    def resolve_contradiction(self, world_name: str, fact1_id: str, fact2_id: str, keep_fact1: bool = True):
        """Разрешает противоречие, удаляя один из фактов"""
        world = self.world_db.load_world(world_name)
        if not world:
            return

        facts = world.get("facts", [])
        to_remove = fact2_id if keep_fact1 else fact1_id
        to_keep = fact1_id if keep_fact1 else fact2_id

        # Удаляем факт
        facts = [f for f in facts if f["id"] != to_remove]

        # Обновляем ссылки
        for fact in facts:
            if to_remove in fact.get("contradicts", []):
                fact["contradicts"].remove(to_remove)

        world["facts"] = facts
        world["last_updated"] = datetime.now().isoformat()
        self.world_db.save_world(world_name, world)

        print(f"✅ Противоречие разрешено в {world_name}: удалён факт {to_remove}")


# ========================
# NPC MEMORY ENGINE
# ========================

class NPCMemoryEngine:
    """Управляет памятью и отношениями NPC"""

    def __init__(self, world_db: WorldDatabase):
        self.world_db = world_db

    def update_relations(self, world_name: str, npc1_name: str, npc2_name: str,
                         relation: str, strength: float):
        """Обновляет отношения между NPC"""
        world = self.world_db.load_world(world_name)
        if not world:
            return

        for npc in world.get("npcs", []):
            if npc["name"] == npc1_name:
                npc["relations"][npc2_name] = {
                    "relation": relation,
                    "strength": strength,
                    "updated_at": datetime.now().isoformat()
                }

        self.world_db.save_world(world_name, world)

    def add_memory(self, world_name: str, npc_name: str, memory: Dict):
        """Добавляет воспоминание NPC"""
        world = self.world_db.load_world(world_name)
        if not world:
            return

        for npc in world.get("npcs", []):
            if npc["name"] == npc_name:
                npc["memories"].append(memory)
                # Ограничиваем память последними 50 записями
                if len(npc["memories"]) > 50:
                    npc["memories"] = npc["memories"][-50:]

        self.world_db.save_world(world_name, world)

    def get_npc_summary(self, world_name: str, npc_name: str) -> Optional[Dict]:
        """Возвращает сводку по NPC"""
        world = self.world_db.load_world(world_name)
        if not world:
            return None

        for npc in world.get("npcs", []):
            if npc["name"] == npc_name:
                return {
                    "name": npc["name"],
                    "age": npc["age"],
                    "race": npc["race"],
                    "role": npc["role"],
                    "personality": npc["personality"],
                    "location": npc["location"],
                    "alive": npc["alive"],
                    "mood": npc["mood"],
                    "influence": npc["influence"],
                    "relations_count": len(npc.get("relations", {})),
                    "memories_count": len(npc.get("memories", [])),
                    "last_seen": npc.get("last_seen"),
                }
        return None

    def simulate_npc_behavior(self, world_name: str) -> List[str]:
        """Симулирует поведение NPC и генерирует микро-события"""
        world = self.world_db.load_world(world_name)
        if not world:
            return []

        actions = []
        npcs = world.get("npcs", [])

        for npc in npcs:
            if not npc.get("alive", True):
                continue

            # NPC может переместиться
            if random.random() < 0.3:
                old_location = npc["location"]
                possible_locations = list(set([n.get("location", "unknown") for n in npcs]))
                if possible_locations:
                    npc["location"] = random.choice(possible_locations)
                    if npc["location"] != old_location:
                        actions.append(f"🚶 {npc['name']} переместился из {old_location} в {npc['location']}")

            # NPC может сменить настроение
            if random.random() < 0.2:
                old_mood = npc["mood"]
                npc["mood"] = random.choice(["happy", "anxious", "angry", "curious", "melancholic", "neutral"])
                if npc["mood"] != old_mood:
                    actions.append(f"🎭 {npc['name']} изменил настроение: {old_mood} → {npc['mood']}")

            # NPC может изменить отношение к другому NPC
            if random.random() < 0.1 and npc.get("relations"):
                other_name = random.choice(list(npc["relations"].keys()))
                other_npc = next((n for n in npcs if n["name"] == other_name), None)
                if other_npc and other_npc.get("alive", True):
                    new_strength = round(random.uniform(0.2, 1.0), 2)
                    npc["relations"][other_name]["strength"] = new_strength
                    actions.append(f"🤝 {npc['name']} и {other_npc['name']} изменили отношения (сила: {new_strength})")

        if actions:
            self.world_db.save_world(world_name, world)

        return actions

    def kill_npc(self, world_name: str, npc_name: str, cause: str = ""):
        """Убивает NPC"""
        world = self.world_db.load_world(world_name)
        if not world:
            return

        for npc in world.get("npcs", []):
            if npc["name"] == npc_name:
                npc["alive"] = False
                npc["death_cause"] = cause or "Неизвестно"
                npc["death_date"] = datetime.now().isoformat()

                # Уведомляем связанных NPC
                for related_name, relation_data in npc["relations"].items():
                    for other_npc in world.get("npcs", []):
                        if other_npc["name"] == related_name and other_npc["alive"]:
                            other_npc["mood"] = "grieving" if relation_data["relation"] in ["lover", "friend", "ally"] else "angry"
                            other_npc["memories"].append({
                                "event": f"Смерть {npc_name}",
                                "cause": cause,
                                "date": datetime.now().isoformat(),
                            })

                break

        self.world_db.save_world(world_name, world)
        print(f"💀 {npc_name} погиб: {cause or 'Неизвестно'}")

    def age_npcs(self, world_name: str, years: int = 1):
        """Старит всех NPC на N лет"""
        world = self.world_db.load_world(world_name)
        if not world:
            return

        for npc in world.get("npcs", []):
            if npc.get("alive", True):
                npc["age"] += years
                # Шанс естественной смерти
                death_chance = 0.001 * (npc["age"] - 50) if npc["age"] > 50 else 0
                if random.random() < death_chance:
                    self.kill_npc(world_name, npc["name"], "Естественная смерть")

        self.world_db.save_world(world_name, world)
        print(f"⏳ Все NPC в {world_name} постарели на {years} лет")


# ========================
# BACKGROUND CYCLE ENGINE
# ========================

class BackgroundCycleEngine:
    """Фоновый цикл развития мира"""

    def __init__(self, world_db: WorldDatabase, event_engine: EventEngine,
                 consistency_engine: ConsistencyEngine, npc_memory_engine: NPCMemoryEngine):
        self.world_db = world_db
        self.event_engine = event_engine
        self.consistency_engine = consistency_engine
        self.npc_memory_engine = npc_memory_engine
        self.running = False
        self.cycle_interval = 60  # секунд между циклами
        self.current_cycle = 0

    async def run_continuous(self, world_names: Optional[List[str]] = None):
        """Запускает непрерывный цикл развития"""
        self.running = True

        if world_names is None:
            world_names = self.world_db.get_all_worlds()

        print(f"🔄 Фоновый цикл запущен для {len(world_names)} миров")

        while self.running:
            try:
                self.current_cycle += 1

                for world_name in world_names:
                    await self.process_world(world_name)

                print(f"✅ Цикл {self.current_cycle} завершён")

            except Exception as e:
                print(f"❌ Ошибка в фоновом цикле: {e}")

            # Ждём до следующего цикла
            await asyncio.sleep(self.cycle_interval)

    async def process_world(self, world_name: str):
        """Обрабатывает один мир за цикл"""
        world = self.world_db.load_world(world_name)
        if not world:
            return

        # 1. Генерируем события (30% шанс)
        if random.random() < 0.3:
            event = self.event_engine.generate_event(world_name)

        # 2. Симулируем поведение NPC (50% шанс)
        if random.random() < 0.5:
            actions = self.npc_memory_engine.simulate_npc_behavior(world_name)
            if actions:
                print(f"  🎭 {world_name}: {'; '.join(actions[:3])}")

        # 3. Проверяем консистентность (10% шанс, чтобы не грузить)
        if random.random() < 0.1:
            consistency = self.consistency_engine.check_consistency(world_name)
            if consistency.get("issues_count", 0) > 0:
                print(f"  ⚠️ {world_name}: обнаружено {consistency['issues_count']} проблем с консистентностью")

        # 4. Старение NPC (каждые 10 циклов)
        if self.current_cycle % 10 == 0:
            self.npc_memory_engine.age_npcs(world_name, years=1)

        # 5. Эволюция эпохи
        await self._evolve_era(world_name, world)

    async def _evolve_era(self, world_name: str, world: Dict):
        """Эволюция эпохи мира"""
        conflict = world.get("conflict_level", 0)
        state = world.get("state", "peace")

        # Переходы состояний
        if conflict > 0.8 and state != WorldState.WAR.value:
            self.world_db.update_world_state(world_name, WorldState.WAR.value)
            print(f"  ⚔️ {world_name} перешёл в состояние ВОЙНЫ")
        elif conflict < 0.2 and state in [WorldState.WAR.value, WorldState.CRISIS.value]:
            self.world_db.update_world_state(world_name, WorldState.PEACE.value)
            print(f"  🕊️ {world_name} перешёл в состояние МИРА")
        elif state == WorldState.PEACE.value and self.current_cycle % 5 == 0:
            self.world_db.update_world_state(world_name, WorldState.RENAISSANCE.value)
            print(f"  ✨ {world_name} перешёл в состояние ВОЗРОЖДЕНИЯ")

    def stop(self):
        """Останавливает фоновый цикл"""
        self.running = False
        print("🛑 Фоновый цикл остановлен")


# ========================
# MASTER WORLD ENGINE
# ========================

class WorldEngine:
    """
    Мастер-движок, объединяющий все системы:
    - WorldDatabase: хранение миров
    - EventEngine: генерация событий
    - ConsistencyEngine: проверка лора
    - NPCMemoryEngine: память NPC
    - BackgroundCycleEngine: фоновый цикл
    """

    def __init__(self, data_dir: str = "data"):
        self.data_dir = Path(data_dir)
        self.worlds_dir = self.data_dir / "worlds"

        # Инициализируем подсистемы
        self.world_db = WorldDatabase(db_path=str(self.worlds_dir))
        self.event_engine = EventEngine(self.world_db)
        self.consistency_engine = ConsistencyEngine(self.world_db)
        self.npc_memory_engine = NPCMemoryEngine(self.world_db)
        self.background_engine = BackgroundCycleEngine(
            self.world_db,
            self.event_engine,
            self.consistency_engine,
            self.npc_memory_engine
        )

        print("🌍 WorldEngine инициализирован полностью")

    def create_world(self, genre: str, tag: str) -> str:
        """Создаёт новый мир"""
        return self.world_db.create_world(genre, tag)

    def get_world(self, world_name: str) -> Optional[Dict]:
        """Загружает мир"""
        return self.world_db.load_world(world_name)

    def get_all_worlds(self) -> List[str]:
        """Возвращает список всех миров"""
        return self.world_db.get_all_worlds()

    def get_world_summary(self, world_name: str) -> Optional[Dict]:
        """Возвращает сводку о мире"""
        return self.world_db.get_world_summary(world_name)

    def generate_event(self, world_name: str) -> Optional[WorldEvent]:
        """Генерирует событие в мире"""
        return self.event_engine.generate_event(world_name)

    def check_consistency(self, world_name: str) -> Dict:
        """Проверяет консистентность лора"""
        return self.consistency_engine.check_consistency(world_name)

    def add_fact(self, world_name: str, statement: str, category: str, confidence: float = 0.9):
        """Добавляет факт в мир"""
        return self.consistency_engine.add_fact(world_name, statement, category, confidence)

    def get_world_events(self, world_name: str, limit: int = 20) -> List[Dict]:
        """Возвращает события мира"""
        return self.event_engine.get_world_events(world_name, limit)

    def get_npc_summary(self, world_name: str, npc_name: str) -> Optional[Dict]:
        """Возвращает сводку по NPC"""
        return self.npc_memory_engine.get_npc_summary(world_name, npc_name)

    async def start_background_cycle(self, world_names: Optional[List[str]] = None):
        """Запускает фоновый цикл развития"""
        if world_names is None:
            world_names = self.get_all_worlds()
        await self.background_engine.run_continuous(world_names)

    def stop_background_cycle(self):
        """Останавливает фоновый цикл"""
        self.background_engine.stop()

    def get_status(self) -> Dict:
        """Возвращает статус всех систем"""
        worlds = self.get_all_worlds()
        world_summaries = []

        for name in worlds:
            summary = self.world_db.get_world_summary(name)
            if summary:
                world_summaries.append({
                    "name": name,
                    **summary
                })

        return {
            "total_worlds": len(worlds),
            "worlds": world_summaries,
            "background_running": self.background_engine.running,
            "cycle_count": self.background_engine.current_cycle,
        }


# ========================
# TEST
# ========================

if __name__ == "__main__":
    print("=" * 60)
    print("🧪 ТЕСТ WorldEngine")
    print("=" * 60)

    engine = WorldEngine()

    # Создаём мир
    print("\n📝 Создание мира...")
    world_name = engine.create_world("Киберпанк", "нейроимпланты")
    print(f"✅ Мир создан: {world_name}")

    # Загружаем мир
    world = engine.get_world(world_name)
    if world:
        print(f"\n📖 Мир '{world_name}':")
        print(f"   Жанр: {world['genre']}")
        print(f"   NPC: {len(world['npcs'])}")
        print(f"   Фракции: {len(world['factions'])}")
        print(f"   Законы: {len(world['laws'])}")
        print(f"   Традиции: {len(world['traditions'])}")
        print(f"   Факты: {len(world['facts'])}")

        print(f"\n👤 Первые NPC:")
        for npc in world["npcs"][:3]:
            print(f"   - {npc['name']} ({npc['role']}), {npc['personality']}")

        print(f"\n⚔️ Фракции:")
        for faction in world["factions"][:3]:
            print(f"   - {faction['name']} ({faction['type']}), сила: {faction['power']:.2f}")

    # Генерируем событие
    print("\n📜 Генерация события...")
    event = engine.generate_event(world_name)
    if event:
        print(f"   Название: {event.title}")
        print(f"   Описание: {event.description[:100]}...")
        print(f"   Тип: {event.type}, серьёзность: {event.severity}")

    # Проверяем консистентность
    print("\n🔍 Проверка консистентности...")
    consistency = engine.check_consistency(world_name)
    print(f"   Фактов: {consistency['total_facts']}")
    print(f"   Проблем: {consistency['issues_count']}")

    # Симулируем поведение NPC
    print("\n🎭 Симуляция NPC...")
    actions = engine.npc_memory_engine.simulate_npc_behavior(world_name)
    if actions:
        for action in actions[:3]:
            print(f"   {action}")

    print("\n✅ Тест завершён!")
