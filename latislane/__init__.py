"""
Latislane — Автономная система изучения человеческого тела и проектирования тел.

Назначение:
- Изучение анатомии, физиологии, генетики человека
- Проектирование механических тел (робототехника)
- Проектирование бионических тел (импланты + ткани)
- Проектирование органических тел (генная инженерия, биоинженерия)
- Автономное самообучение из интернета
- Интеграция с чат-ботом Pantikur
"""

from .latislane_core import LatislaneCore
from .body_modules import BodyModule, BodyType, BodySpecification
from .internet_learning import InternetLearningEngine
from .body_factory import BodyFactory

__version__ = "0.1.0"
__all__ = [
    "LatislaneCore",
    "BodyModule",
    "BodyType",
    "BodySpecification",
    "InternetLearningEngine",
    "BodyFactory",
]
