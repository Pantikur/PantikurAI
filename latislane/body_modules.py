"""
Latislane — Модули тел и спецификации.

Описывает:
- Типы тел (механическое, бионическое, органическое)
- Модули тела (скелет, мышцы, нервная система и т.д.)
- Спецификации для каждого типа тела
"""

import json
import time
from enum import Enum
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field, asdict


class BodyType(Enum):
    """Типы проектируемых тел."""
    MECHANICAL = "mechanical"           # Полностью механическое тело
    BIONIC = "bionic"                   # Бионическое (гибрид)
    ORGANIC = "organic"                 # Органическое (биоинженерия)
    HYBRID = "hybrid"                   # Гибридный вариант


class DevelopmentStage(Enum):
    """Стадия развития проекта."""
    RESEARCH = "research"               # Исследование
    DESIGN = "design"                   # Проектирование
    PROTOTYPE = "prototype"             # Прототип
    TESTING = "testing"                 # Тестирование
    ITERATION = "iteration"             # Итерация
    COMPLETE = "complete"               # Завершено


class LatislaneEvolutionStage(Enum):
    """
    Эволюционная прогрессия Латислейн.
    
    Система проходит этапы последовательно:
    1. Механическое тело — полное изучение робототехники
    2. Бионическое тело — гибридный подход
    3. Органическое тело — биоинженерия и генетика
    4. Синтез — объединение всех технологий
    """
    MECHANICAL_RESEARCH = "mechanical_research"     # Этап 1: Изучение механических тел
    MECHANICAL_DESIGN = "mechanical_design"          # Этап 2: Проектирование
    MECHANICAL_COMPLETE = "mechanical_complete"      # Этап 3: Завершение механики
    
    BIONIC_RESEARCH = "bionic_research"              # Этап 4: Изучение бионики
    BIONIC_DESIGN = "bionic_design"                  # Этап 5: Проектирование
    BIONIC_COMPLETE = "bionic_complete"              # Этап 6: Завершение бионики
    
    ORGANIC_RESEARCH = "organic_research"            # Этап 7: Изучение биоинженерии
    ORGANIC_DESIGN = "organic_design"                # Этап 8: Проектирование
    ORGANIC_COMPLETE = "organic_complete"            # Этап 9: Завершение органики
    
    SYNTHESIS = "synthesis"                          # Этап 10: Синтез всех технологий
    FINAL = "final"                                  # Этап 11: Финальная версия


class BodyModule:
    """
    Модуль тела — отдельная система или часть.
    
    Примеры:
    - SkeletalModule — скелетная система
    - MuscularModule — мышечная система
    - NeuralModule — нервная система
    - CardiovascularModule — сердечно-сосудистая
    """
    
    def __init__(self, name: str, category: str, description: str = ""):
        self.name = name
        self.category = category  # "structural", "nervous", "circulatory", "metabolic", "reproductive"
        self.description = description
        self.components: List[Dict[str, Any]] = []
        self.knowledge_sources: List[str] = []
        self.research_progress = 0.0  # 0.0 — 1.0
        self.design_status: str = "unresearched"  # "unresearched", "researched", "designed", "optimized"
        self.body_types_supported: List[BodyType] = []
        self.variants: List[Dict[str, Any]] = []
        self.research_notes: List[Dict[str, Any]] = []
        self.created_at = time.time()
        self.updated_at = time.time()
    
    def add_component(self, name: str, function: str, specifications: Optional[Dict[str, Any]] = None):
        """Добавить компонент в модуль."""
        component = {
            "name": name,
            "function": function,
            "specifications": specifications or {},
            "added_at": time.time()
        }
        self.components.append(component)
        self.updated_at = time.time()
    
    def add_research_note(self, note: str):
        """Добавить заметку из исследования."""
        self.research_notes.append({
            "text": note,
            "timestamp": time.time()
        })
        self.updated_at = time.time()
        # Обновляем прогресс исследования
        self.research_progress = min(1.0, self.research_progress + 0.05)
    
    def mark_researched(self):
        """Отметить модуль как исследованный."""
        self.design_status = "researched"
        self.research_progress = max(self.research_progress, 0.5)
        self.updated_at = time.time()
    
    def mark_designed(self, body_type: BodyType):
        """Отметить модуль как спроектированный для типа тела."""
        self.design_status = "designed"
        if body_type not in self.body_types_supported:
            self.body_types_supported.append(body_type)
        self.updated_at = time.time()
    
    def to_dict(self) -> Dict:
        """Конвертировать в словарь."""
        return {
            "name": self.name,
            "category": self.category,
            "description": self.description,
            "components_count": len(self.components),
            "research_progress": self.research_progress,
            "design_status": self.design_status,
            "body_types_supported": [bt.value for bt in self.body_types_supported],
            "variants_count": len(self.variants),
            "research_notes_count": len(self.research_notes),
            "created_at": self.created_at,
            "updated_at": self.updated_at
        }
    
    def to_json(self) -> str:
        """Конвертировать в JSON."""
        return json.dumps(self.to_dict(), ensure_ascii=False, indent=2)


@dataclass
class BodySpecification:
    """
    Спецификация тела — полный проект тела.
    
    Включает:
    - Все модули тела
    - Параметры сборки
    - Стадию разработки
    - Метрики
    """
    name: str
    body_type: BodyType
    stage: DevelopmentStage = DevelopmentStage.RESEARCH
    modules: Dict[str, BodyModule] = field(default_factory=dict)
    parameters: Dict[str, Any] = field(default_factory=dict)
    research_data: Dict[str, Any] = field(default_factory=dict)
    test_results: List[Dict[str, Any]] = field(default_factory=list)
    created_at: float = field(default_factory=time.time)
    updated_at: float = field(default_factory=time.time)
    
    def add_module(self, module: BodyModule):
        """Добавить модуль в спецификацию."""
        self.modules[module.name] = module
        self.updated_at = time.time()
    
    def get_module(self, name: str) -> Optional[BodyModule]:
        """Получить модуль по имени."""
        return self.modules.get(name)
    
    def add_test_result(self, result: Dict[str, Any]):
        """Добавить результат тестирования."""
        self.test_results.append({
            **result,
            "timestamp": time.time()
        })
        self.updated_at = time.time()
    
    def calculate_completeness(self) -> float:
        """Рассчитать общую завершённость проекта."""
        if not self.modules:
            return 0.0
        
        total_progress = sum(m.research_progress for m in self.modules.values())
        return total_progress / len(self.modules)
    
    def get_stats(self) -> Dict[str, Any]:
        """Получить статистику проекта."""
        return {
            "name": self.name,
            "body_type": self.body_type.value,
            "stage": self.stage.value,
            "modules_count": len(self.modules),
            "completeness": self.calculate_completeness(),
            "test_results_count": len(self.test_results),
            "created_at": self.created_at,
            "updated_at": self.updated_at
        }
    
    def to_dict(self) -> Dict:
        """Конвертировать в словарь."""
        return {
            **self.get_stats(),
            "modules": {name: mod.to_dict() for name, mod in self.modules.items()},
            "parameters": self.parameters,
            "test_results": self.test_results[-10:]  # последние 10 результатов
        }
    
    def to_json(self) -> str:
        """Конвертировать в JSON."""
        return json.dumps(self.to_dict(), ensure_ascii=False, indent=2)


# === ПРЕДЕТЕРМИНИРОВАННЫЕ МОДУЛИ ТЕЛА ===

def create_default_modules() -> Dict[str, BodyModule]:
    """
    Создать стандартный набор модулей тела.
    
    Каждый модуль описывает систему человеческого тела,
    которую нужно изучить для проектирования.
    """
    modules = {}
    
    # === СТРУКТУРНЫЕ МОДУЛИ ===
    
    # Скелет
    skeletal = BodyModule(
        name="skeletal_system",
        category="structural",
        description="Опорно-двигательный аппарат: кости, суставы, хрящи, связки"
    )
    skeletal.add_component("череп", "Защита мозга, основа лица", {"bones": 22, "material": "calcium_phosphate"})
    skeletal.add_component("позвоночник", "Ось тела, защита спинного мозга", {"vertebrae": 33, "curvatures": 4})
    skeletal.add_component("грудная клетка", "Защита сердца и лёгких", {"ribs": 24, "sternum": True})
    skeletal.add_component("таз", "Опора для ног, защита органов", {"bones": 3, "type": "pelvic_girdle"})
    modules["skeletal_system"] = skeletal
    
    # Мышечная система
    muscular = BodyModule(
        name="muscular_system",
        category="structural",
        description="Мышцы: скелетные, гладкие, сердечная"
    )
    muscular.add_component("скелетные мышцы", "Добровольные движения", {"count": 650, "type": "striated"})
    muscular.add_component("гладкие мышцы", "Внутренние органы", {"type": "involuntary"})
    muscular.add_component("сердечная мышца", "Сердце, сокращения", {"type": "cardiac", "beats_per_day": 100000})
    modules["muscular_system"] = muscular
    
    # === НЕРОВНАЯ СИСТЕМА ===
    
    neural = BodyModule(
        name="nervous_system",
        category="nervous",
        description="Центральная и периферическая нервная система"
    )
    neural.add_component("головной мозг", "Центр управления", {"neurons": 86000000000, "weight_kg": 1.4})
    neural.add_component("спинной мозг", "Проводник и рефлексы", {"length_cm": 45, "segments": 31})
    neural.add_component("периферические нервы", "Связь с телом", {"pairs": 43, "types": ["sensory", "motor", "autonomic"]})
    neural.add_component("синапсы", "Связи между нейронами", {"count": "100000000000000", "transmission_ms": 0.5})
    modules["nervous_system"] = neural
    
    # === ЦИРКУЛЯТОРНАЯ СИСТЕМА ===
    
    cardiovascular = BodyModule(
        name="cardiovascular_system",
        category="circulatory",
        description="Сердце, сосуды, кровь"
    )
    cardiovascular.add_component("сердце", "Насос крови", {"chambers": 4, "output_per_min": 5000, "beats_per_day": 100000})
    cardiovascular.add_component("артерии", "Кровь от сердца", {"total_length_km": 100000, "types": ["aorta", "elastic", "muscular"]})
    cardiovascular.add_component("вены", "Кровь к сердцу", {"valves": True, "total_length_km": 100000})
    cardiovascular.add_component("капилляры", "Обмен веществ", {"total_length_km": 100000, "diameter_um": 8})
    cardiovascular.add_component("кровь", "Транспортная среда", {"volume_liters": 5, "cells": ["erythrocytes", "leukocytes", "platelets"]})
    modules["cardiovascular_system"] = cardiovascular
    
    # === МЕТАБОЛИЧЕСКАЯ СИСТЕМА ===
    
    metabolic = BodyModule(
        name="metabolic_system",
        category="metabolic",
        description="Пищеварение, дыхание, выделение"
    )
    metabolic.add_component("пищеварительный тракт", "Переваривание пищи", {"length_m": 9, "organs": ["stomach", "intestines", "liver", "pancreas"]})
    metabolic.add_component("лёгкие", "Газообмен", {"alveoli_count": 4800000000, "capacity_liters": 6})
    metabolic.add_component("почки", "Фильтрация крови", {"nephrons": 2000000, "filter_per_day_liters": 180})
    metabolic.add_component("печень", "Метаболизм и детокс", {"functions": 500, "weight_kg": 1.5})
    modules["metabolic_system"] = metabolic
    
    # === РЕПРОДУКТИВНАЯ СИСТЕМА ===
    
    reproductive = BodyModule(
        name="reproductive_system",
        category="reproductive",
        description="Репродуктивные системы мужчины и женщины"
    )
    reproductive.add_component("мужская система", "Производство сперматозоидов", {"organs": ["testes", "prostate", "penis"], "sperm_per_day": 100000000})
    reproductive.add_component("женская система", "Производство яйцеклеток, вынашивание", {"organs": ["ovaries", "uterus", "vagina"], "cycle_days": 28})
    modules["reproductive_system"] = reproductive
    
    # === ДРУГИЕ ВАЖНЫЕ СИСТЕМЫ ===
    
    integumentary = BodyModule(
        name="integumentary_system",
        category="structural",
        description="Кожа, волосы, ногти — защитный барьер"
    )
    integumentary.add_component("кожа", "Максимальный орган", {"area_m2": 2, "weight_kg": 4, "layers": ["epidermis", "dermis", "subcutaneous"]})
    integumentary.add_component("потовые железы", "Терморегуляция", {"count": 3000000, "sweat_per_day_liters": 1})
    integumentary.add_component("волосы", "Защита и терморегуляция", {"count_scalp": 100000, "growth_rate_mm_per_day": 0.3})
    modules["integumentary_system"] = integumentary
    
    endocrine = BodyModule(
        name="endocrine_system",
        category="metabolic",
        description="Гормональная регуляция"
    )
    endocrine.add_component("гипофиз", "Главная железа", {"hormones": ["growth_hormone", "tsh", "acth"]})
    endocrine.add_component("щитовидная железа", "Метаболизм", {"hormones": ["t3", "t4", "calcitonin"]})
    endocrine.add_component("надпочечники", "Стресс и метаболизм", {"hormones": ["cortisol", "adrenaline", "noradrenaline"]})
    endocrine.add_component("половые железы", "Половые гормоны", {"male": ["testosterone"], "female": ["estrogen", "progesterone"]})
    modules["endocrine_system"] = endocrine
    
    immune = BodyModule(
        name="immune_system",
        category="circulatory",
        description="Защита от патогенов"
    )
    immune.add_component("лейкоциты", "Иммунные клетки", {"types": ["neutrophils", "lymphocytes", "monocytes", "eosinophils", "basophils"]})
    immune.add_component("лимфатическая система", "Дренаж и иммунитет", {"nodes": 600, "vessels_km": 1500})
    immune.add_component("антитела", "Иммуноглобулины", {"types": ["IgG", "IgA", "IgM", "IgE", "IgD"]})
    modules["immune_system"] = immune
    
    sensory = BodyModule(
        name="sensory_system",
        category="nervous",
        description="Органы чувств"
    )
    sensory.add_component("глаза", "Зрение", {"photoreceptors": 120000000, "resolution_dpi": "approx_576", "color_range": "400-700nm"})
    sensory.add_component("уши", "Слух и равновесие", {"frequency_range": "20-20000Hz", "hair_cells": 16000})
    sensory.add_component("нос", "Обоняние", {"receptors": 4000000, "detectable_smells": 1000000000})
    sensory.add_component("язык", "Вкус", {"taste_buds": 10000, "types": ["sweet", "sour", "salty", "bitter", "umami"]})
    sensory.add_component("кожные рецепторы", "Осязание", {"types": ["mechanoreceptors", "thermoreceptors", "nociceptors"]})
    modules["sensory_system"] = sensory
    
    return modules
