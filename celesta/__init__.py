"""
Celesta — Система изучения интимной жизни и физиологии.

Изучает:
- Прикосновения и их виды
- Физиологию интимной жизни
- Последствия избыточного интима
- Последствия прерванного процесса
- Все этапы развития
- Различия по расам и типам существ
"""

from .intimacy_modules import (
    IntimacyModule,
    IntimacyStage,
    IntimacyCategory,
    create_default_modules
)
from .celesta_core import CelestaCore
from .intimacy_learning import IntimacyLearningEngine

__version__ = "0.1.0"
__all__ = [
    "CelestaCore",
    "IntimacyModule",
    "IntimacyStage",
    "IntimacyCategory",
    "IntimacyLearningEngine",
    "create_default_modules",
]
