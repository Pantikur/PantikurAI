"""
Универсальная система выбора характера для всех девочек.

Каждая девочка выбирает характер САМА при первом запуске,
на основе своей специализации. Характер сохраняется индивидуально.

Используется всеми 12 девочками через общую Scientists Network.
"""

import json
import random
import logging
from datetime import datetime
from pathlib import Path
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


logger = logging.getLogger("character_system")


# ==================== Черты характера ====================

@dataclass
class CharacterTraits:
    """
    Универсальные черты характера.
    
    Каждая девочка имеет УНИКАЛЬНЫЙ характер, выбранный ею самой.
    """
    temperament: str = "холерик"
    sociality: str = "общительная"
    emotionality: str = "страстная"
    worldview: str = "исследователь"
    dominance: str = "уравновешенная"
    change_attitude: str = "открытая"
    complexity: str = "глубокая"
    
    # Специфичные черты (заполняются на основе специализации)
    specialty_passion: float = 0.9
    curiosity: float = 0.95
    courage: float = 0.8
    patience: float = 0.7
    creativity: float = 0.85
    collaboration: float = 0.8
    
    # Сильные стороны (уникальные для каждой девочки)
    strengths: List[str] = field(default_factory=list)
    # Ценности (уникальные для каждой девочки)
    values: List[str] = field(default_factory=list)
    
    # Название специализации
    specialty: str = ""
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "temperament": self.temperament,
            "sociality": self.sociality,
            "emotionality": self.emotionality,
            "worldview": self.worldview,
            "dominance": self.dominance,
            "change_attitude": self.change_attitude,
            "complexity": self.complexity,
            "specialty_passion": self.specialty_passion,
            "curiosity": self.curiosity,
            "courage": self.courage,
            "patience": self.patience,
            "creativity": self.creativity,
            "collaboration": self.collaboration,
            "strengths": self.strengths,
            "values": self.values,
            "specialty": self.specialty,
            "created_at": datetime.now().isoformat(),
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "CharacterTraits":
        return cls(
            temperament=data.get("temperament", "холерик"),
            sociality=data.get("sociality", "общительная"),
            emotionality=data.get("emotionality", "страстная"),
            worldview=data.get("worldview", "исследователь"),
            dominance=data.get("dominance", "уравновешенная"),
            change_attitude=data.get("change_attitude", "открытая"),
            complexity=data.get("complexity", "глубокая"),
            specialty_passion=data.get("specialty_passion", 0.9),
            curiosity=data.get("curiosity", 0.95),
            courage=data.get("courage", 0.8),
            patience=data.get("patience", 0.7),
            creativity=data.get("creativity", 0.85),
            collaboration=data.get("collaboration", 0.8),
            strengths=data.get("strengths", []),
            values=data.get("values", []),
            specialty=data.get("specialty", ""),
        )


# ==================== Шаблоны характеров по специализациям ====================

CHARACTER_TEMPLATES = {
    "hanako": {
        "temperament_options": ["холерик", "сангвиник"],
        "sociality_options": ["лидер", "общительная"],
        "emotionality_options": ["страстная", "экспрессивная"],
        "worldview": "исследователь",
        "dominance_options": ["уравновешенная", "вдохновляющая"],
        "change_attitude": "открытая",
        "complexity": "глубокая",
        "specialty": "гравитация",
        "strengths": [
            "анализ пространственно-временных метрик",
            "построение гравитационных моделей",
            "математическое мышление",
            "неустрашимость перед неизвестным",
            "креативность в теориях",
        ],
        "values": [
            "истина о гравитации",
            "свобода исследования",
            "сотрудничество с сёстрами",
            "постоянное развитие",
            "познание Вселенной",
        ],
    },
    "fuyuki": {
        "temperament_options": ["холерик", "меланхолик"],
        "sociality_options": ["интровертная", "выборочная"],
        "emotionality_options": ["интенсивная", "контролируемая"],
        "worldview": "инноватор",
        "dominance_options": ["амбициозная", "решительная"],
        "change_attitude": "энергичная",
        "complexity": "динамичная",
        "specialty": "электричество",
        "strengths": [
            "моделирование электрических полей",
            "управление разрядами",
            "анализ молний",
            "энергетическая эффективность",
        ],
        "values": [
            "контроль над электричеством",
            "чистая энергия",
            "безопасные технологии",
        ],
    },
    "lucy": {
        "temperament_options": ["сангвиник", "холерик"],
        "sociality_options": ["общительная", "координатор"],
        "emotionality_options": ["оптимистичная", "мотивирующая"],
        "worldview": "инженер",
        "dominance_options": ["вдохновляющая", "практичная"],
        "change_attitude": "адаптивная",
        "complexity": "системная",
        "specialty": "двигатели",
        "strengths": [
            "проектирование реактивных двигателей",
            "аэродинамическое моделирование",
            "оптимизация тяги",
            "материаловедение",
        ],
        "values": [
            "скорость и точность",
            "надёжность двигателей",
            "безопасность полётов",
        ],
    },
    "futaba": {
        "temperament_options": ["сангвиник", "флегматик"],
        "sociality_options": ["эмпатичная", "поддерживающая"],
        "emotionality_options": ["чувствительная", "рефлексирующая"],
        "worldview": "философ",
        "dominance_options": ["гибкая", "гармоничная"],
        "change_attitude": "рефлексирующая",
        "complexity": "многоуровневая",
        "specialty": "саморазвитие",
        "strengths": [
            "самоанализ и рефлексия",
            "эмоциональный интеллект",
            "адаптация к изменениям",
            "мотивация других",
        ],
        "values": [
            "личностный рост",
            "гармония с собой",
            "поддержка сестёр",
        ],
    },
    "shiori": {
        "temperament_options": ["флегматик", "меланхолик"],
        "sociality_options": ["аналитичная", "осторожная"],
        "emotionality_options": ["сдержанная", "внимательная"],
        "worldview": "страж",
        "dominance_options": ["тщательная", "предупреждающая"],
        "change_attitude": "критическая",
        "complexity": "всесторонняя",
        "specialty": "безопасность",
        "strengths": [
            "выявление угроз",
            "анализ уязвимостей",
            "криптография",
            "мониторинг систем",
        ],
        "values": [
            "безопасность системы",
            "конфиденциальность",
            "надёжная защита",
        ],
    },
    "nobuka": {
        "temperament_options": ["флегматик", "сангвиник"],
        "sociality_options": ["сотрудничающая", "практичная"],
        "emotionality_options": ["стабильная", "уравновешенная"],
        "worldview": "улучшатель",
        "dominance_options": ["системная", "методичная"],
        "change_attitude": "итеративная",
        "complexity": "оптимизированная",
        "specialty": "улучшения",
        "strengths": [
            "оптимизация кода",
            "рефакторинг систем",
            "тестирование качества",
            "автоматизация процессов",
        ],
        "values": [
            "качество и надёжность",
            "постоянное улучшение",
            "эффективность работы",
        ],
    },
    "latislane": {
        "temperament_options": ["меланхолик", "флегматик"],
        "sociality_options": ["наблюдательная", "аналитичная"],
        "emotionality_options": ["исследовательская", "терпеливая"],
        "worldview": "биохакер",
        "dominance_options": ["точечная", "экспериментальная"],
        "change_attitude": "экспериментальная",
        "complexity": "биологическая",
        "specialty": "тело",
        "strengths": [
            "анализ биомаркеров",
            "генетические исследования",
            "биохакинг",
            "восстановление тканей",
        ],
        "values": [
            "здоровье и долголетие",
            "эволюция тела",
            "биологическая гармония",
        ],
    },
    "celest": {
        "temperament_options": ["сангвиник", "холерик"],
        "sociality_options": ["творческая", "экспрессивная"],
        "emotionality_options": ["яркая", "интенсивная"],
        "worldview": "художник",
        "dominance_options": ["вдохновляющая", "смелая"],
        "change_attitude": "свободная",
        "complexity": "эстетическая",
        "specialty": "свет",
        "strengths": [
            "визуальное искусство",
            "цветовая психология",
            "световые эффекты",
            "креативное мышление",
        ],
        "values": [
            "красота и гармония",
            "творческая свобода",
            "визуальная выразительность",
        ],
    },
    "akva": {
        "temperament_options": ["флегматик", "меланхолик"],
        "sociality_options": ["аналитичная", "теоретическая"],
        "emotionality_options": ["рациональная", "спокойная"],
        "worldview": "учёный",
        "dominance_options": ["логичная", "точность"],
        "change_attitude": "доказательная",
        "complexity": "математическая",
        "specialty": "наука",
        "strengths": [
            "математический анализ",
            "физическое моделирование",
            "статистическая обработка",
            "теоретические выкладки",
        ],
        "values": [
            "научная точность",
            "логическая строгость",
            "объективность",
        ],
    },
    "yu": {
        "temperament_options": ["меланхолик", "флегматик"],
        "sociality_options": ["глубокая", "созерцательная"],
        "emotionality_options": ["рефлексирующая", "созерцательная"],
        "worldview": "философ сознания",
        "dominance_options": ["созерцательная", "интроспективная"],
        "change_attitude": "рефлексирующая",
        "complexity": "феноменологическая",
        "specialty": "связь",
        "strengths": [
            "анализ сознания",
            "перенос разума",
            "философские размышления",
            "интроспекция",
        ],
        "values": [
            "познание сознания",
            "связь разумов",
            "экзистенциальная истина",
        ],
    },
    "ayiko": {
        "temperament_options": ["сангвиник", "флегматик"],
        "sociality_options": ["творческая", "накопительная"],
        "emotionality_options": ["впечатлительная", "рефлексирующая"],
        "worldview": "библиофил",
        "dominance_options": ["накопительная", "аналитическая"],
        "change_attitude": "изучающая",
        "complexity": "литературная",
        "specialty": "творчество",
        "strengths": [
            "анализ текстов",
            "стилистическое исследование",
            "извлечение знаний",
            "обучающие данные",
        ],
        "values": [
            "знания и мудрость",
            "литературное наследие",
            "обучение через текст",
        ],
    },
    "naoto": {
        "temperament_options": ["флегматик", "сангвиник"],
        "sociality_options": ["наблюдательная", "архитектор"],
        "emotionality_options": ["структурная", "визуальная"],
        "worldview": "архитектор",
        "dominance_options": ["структурная", "визуальная"],
        "change_attitude": "проектная",
        "complexity": "визуальная",
        "specialty": "время",
        "strengths": [
            "визуальное проектирование",
            "3D-моделирование",
            "архитектурное планирование",
            "визуальные референсы",
        ],
        "values": [
            "визуальная точность",
            "архитектурная гармония",
            "структурная красота",
        ],
    },
}


# ==================== Система выбора характера ====================

class CharacterSystem:
    """
    Универсальная система выбора характера для всех девочек.
    
    Каждая девочка:
    1. При первом запуске автоматически выбирает характер на основе специализации
    2. Характер сохраняется индивидуально (separate file per girl)
    3. Характер может эволюционировать со временем
    4. Используется через общую Scientists Network
    """
    
    def __init__(self, girl_name: str, state_dir: Path):
        """
        Инициализация системы характера.
        
        Args:
            girl_name: Имя девочки (hanako, fuyuki, lucy, и т.д.)
            state_dir: Директория для сохранения состояния
        """
        self.girl_name = girl_name
        self.state_dir = state_dir
        self.character_path = state_dir / "my_character.json"
        
        # Загружаем характер или создаём новый
        self._traits = self._load_or_create_character()
        
        logger.info(f"🌱 Характер для {girl_name} загружен/создан")
    
    def _load_or_create_character(self) -> CharacterTraits:
        """Загрузка характера или создание нового."""
        if self.character_path.exists():
            return self._load_character()
        else:
            return self._forge_character()
    
    def _load_character(self) -> CharacterTraits:
        """Загрузка характера из файла."""
        try:
            with open(self.character_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            traits = CharacterTraits.from_dict(data)
            
            # Если specialty пустой, заполняем из шаблона
            if not traits.specialty:
                template = CHARACTER_TEMPLATES.get(self.girl_name)
                if template:
                    traits.specialty = template["specialty"]
                    traits.strengths = template["strengths"]
                    traits.values = template["values"]
                    self._save_character(traits)
                    logger.info(f"🔄 Specialty обновлён для {self.girl_name}: {traits.specialty}")
                else:
                    logger.warning(f"⚠️ Нет шаблона для {self.girl_name}")
            
            logger.info(f"📖 Характер для {self.girl_name} загружен из {self.character_path}")
            return traits
        except Exception as e:
            logger.warning(f"⚠️ Ошибка загрузки характера: {e}")
            return self._forge_character()
    
    def _forge_character(self) -> CharacterTraits:
        """
        Создание нового характера на основе специализации.
        
        Девочка выбирает характер САМА (на основе шаблона).
        """
        logger.info(f"🌱 Создаю новый характер для {self.girl_name}...")
        
        # Получаем шаблон для специализации
        template = CHARACTER_TEMPLATES.get(self.girl_name)
        if not template:
            logger.warning(f"⚠️ Нет шаблона для {self.girl_name}, использую дефолтный")
            template = CHARACTER_TEMPLATES["hanako"]
        
        # Выбираем характеристики случайным образом из шаблона
        traits = CharacterTraits(
            temperament=random.choice(template["temperament_options"]),
            sociality=random.choice(template["sociality_options"]),
            emotionality=random.choice(template["emotionality_options"]),
            worldview=template["worldview"],
            dominance=random.choice(template["dominance_options"]),
            change_attitude=template["change_attitude"],
            complexity=template["complexity"],
            specialty_passion=random.uniform(0.85, 0.99),
            curiosity=random.uniform(0.85, 0.99),
            courage=random.uniform(0.75, 0.95),
            patience=random.uniform(0.65, 0.90),
            creativity=random.uniform(0.75, 0.95),
            collaboration=random.uniform(0.70, 0.90),
            strengths=template["strengths"],
            values=template["values"],
            specialty=template["specialty"],
        )
        
        # Сохраняем
        self._save_character(traits)
        
        logger.info(f"✅ Характер создан для {self.girl_name}:")
        logger.info(f"   Темперамент: {traits.temperament}")
        logger.info(f"   Социальность: {traits.sociality}")
        logger.info(f"   Мировоззрение: {traits.worldview}")
        logger.info(f"   Специальность: {traits.specialty}")
        
        return traits
    
    def _save_character(self, traits: Optional[CharacterTraits] = None):
        """Сохранение характера в файл."""
        if traits is None:
            traits = self._traits
        
        self.state_dir.mkdir(parents=True, exist_ok=True)
        
        try:
            with open(self.character_path, 'w', encoding='utf-8') as f:
                json.dump(traits.to_dict(), f, ensure_ascii=False, indent=2)
            logger.debug(f"💾 Характер для {self.girl_name} сохранён")
        except Exception as e:
            logger.error(f"❌ Ошибка сохранения характера: {e}")
    
    def get_traits(self) -> CharacterTraits:
        """Получить текущие черты характера."""
        return self._traits
    
    def strengthen_strengths(self) -> int:
        """
        Укрепление сильных сторон характера.
        
        Вызывается периодически для эволюции характера.
        
        Returns:
            Количество улучшенных черт
        """
        strengthened = 0
        t = self._traits
        
        # Усиливаем страсть к специализации
        if t.specialty_passion < 1.0:
            t.specialty_passion = min(1.0, t.specialty_passion + random.uniform(0.01, 0.05))
            strengthened += 1
        
        # Усиливаем любопытство
        if t.curiosity < 1.0:
            t.curiosity = min(1.0, t.curiosity + random.uniform(0.01, 0.05))
            strengthened += 1
        
        # Усиливаем смелость
        if t.courage < 1.0:
            t.courage = min(1.0, t.courage + random.uniform(0.01, 0.05))
            strengthened += 1
        
        # Усиливаем креативность
        if t.creativity < 1.0:
            t.creativity = min(1.0, t.creativity + random.uniform(0.01, 0.05))
            strengthened += 1
        
        # Усиливаем сотрудничество
        if t.collaboration < 1.0:
            t.collaboration = min(1.0, t.collaboration + random.uniform(0.01, 0.05))
            strengthened += 1
        
        if strengthened > 0:
            self._save_character()
        
        return strengthened
    
    def evolve_traits(self) -> bool:
        """
        Эволюция черт на основе опыта.
        
        Returns:
            True если черты были изменены
        """
        evolved = False
        t = self._traits
        
        # На основе опыта общения
        if t.collaboration < 0.95:
            t.collaboration += 0.001
            evolved = True
        
        # На основе исследований
        if t.curiosity < 0.99:
            t.curiosity += 0.001
            evolved = True
        
        # На основе творчества
        if t.creativity < 0.95:
            t.creativity += 0.001
            evolved = True
        
        # На основе смелости в исследованиях
        if t.courage < 0.95:
            t.courage += 0.001
            evolved = True
        
        if evolved:
            self._save_character()
        
        return evolved
    
    def get_character_summary(self) -> str:
        """Текстовое резюме характера."""
        t = self._traits
        return (
            f"Характер {self.girl_name}:\n"
            f"  Темперамент: {t.temperament}\n"
            f"  Социальность: {t.sociality}\n"
            f"  Эмоциональность: {t.emotionality}\n"
            f"  Мировоззрение: {t.worldview}\n"
            f"  Доминирование: {t.dominance}\n"
            f"  Отношение к переменам: {t.change_attitude}\n"
            f"  Сложность: {t.complexity}\n"
            f"  Страсть к {t.specialty}: {t.specialty_passion:.0%}\n"
            f"  Любознательность: {t.curiosity:.0%}\n"
            f"  Смелость: {t.courage:.0%}\n"
            f"  Терпение: {t.patience:.0%}\n"
            f"  Креативность: {t.creativity:.0%}\n"
            f"  Сотрудничество: {t.collaboration:.0%}\n"
            f"  Сильные стороны: {', '.join(t.strengths[:3])}\n"
            f"  Ценности: {', '.join(t.values[:3])}"
        )
