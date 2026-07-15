"""
Юи — Система изучения сознания, души и разума.

Изучает:
- Сознание: что это, как работает, как оцифровать
- Душа: нематериальная сущность, возможность переноса
- Разум: мышление, память, эмоции, самосознание
- Оцифровка души: перенос в цифровую среду
- Переселение души: в новое физическое тело без последствий
- Нейробиологию, квантовое сознание, философию разума
- Интерфейсы мозг-компьютер, цифровое воплощение

Знаю ВСЁ: от нейрона до квантовой души.
Переселю душу. Без последствий. Без потерь.
"""

from .engine.yu_core import YuCore
from .soul_consciousness_modules import (
    ConsciousnessModule,
    ConsciousnessCategory,
    create_default_modules,
    CONSCIOUSNESS_MODULES
)
from .soul_learning import SoulLearningEngine

__version__ = "1.0.0"
__all__ = [
    "YuCore",
    "ConsciousnessModule",
    "ConsciousnessCategory",
    "create_default_modules",
    "CONSCIOUSNESS_MODULES",
    "SoulLearningEngine",
]
