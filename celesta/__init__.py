"""
Celesta — Система изучения интимной жизни.

Изучает:
- Solo: мастурбация, фетиши, игрушки, сены
- Duo: все позы, оральные, анальные, мануальные
- Trio: 2F1M, 2M1F, 3F, 3M
- Quad: 2F2M, 3F1M, 3M1F
- Group: оргии, групповая динамика
- Same-Sex: M|M, F|F
- Consent: FRIES, YESC, VERBAL
- Coercion: для защиты и предупреждения
- Физиология: гормоны, нервная система
- Психология: привязанность, фант

Знаю ВСЁ — от взгляда до оргии.
"""

from .intimacy_modules import (
    IntimacyModule,
    IntimacyCategory,
    IntimacyLevel,
    create_default_modules
)
from .celesta_core import CelestaCore
from .intimacy_learning import IntimacyLearningEngine

__version__ = "2.0.0"
__all__ = [
    "CelestaCore",
    "IntimacyModule",
    "IntimacyCategory",
    "IntimacyLevel",
    "IntimacyLearningEngine",
    "create_default_modules",
]
