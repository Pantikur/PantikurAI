"""
Латислейн — Автономная система изучения человеческого тела и проектирования тел.

Назначение:
- Изучение анатомии, физиологии, генетики человека
- Изучение ФИЗИКИ тела (биомеханика, термодинамика, электромагнетизм)
- Изучение ХИМИИ тела (биохимия, молекулы, реакции)
- Изучение БИОЛОГИИ тела (клетки, ткани, органы)
- Проектирование механических тел (робототехника)
- Проектирование бионических тел (импланты + ткани)
- Проектирование органических тел (генная инженерия, биоинженерия)
- Автономное самообучение из интернета
- Самостоятельное формирование характера
- Взаимодействие с 11 другими девочками проекта
- Автоматическое написание отчётов и повышение уровней знаний
- Интеграция с чат-ботом Pantikur
"""

from .latislane_core import LatislaneCore
from .body_modules import BodyModule, BodyType, BodySpecification
from .internet_learning import InternetLearningEngine
from .body_factory import BodyFactory
from .character_system import CharacterSystem
from .social_system import SocialSystem
from .report_system import ReportSystem

__version__ = "2.0.0"
__all__ = [
    "LatislaneCore",
    "BodyModule",
    "BodyType",
    "BodySpecification",
    "InternetLearningEngine",
    "BodyFactory",
    "CharacterSystem",
    "SocialSystem",
    "ReportSystem",
]
