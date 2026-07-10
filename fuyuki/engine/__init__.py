"""
Фуюки — исследователь атмосферного электричества.
"""

from fuyuki.engine.config import FuyukiConfig
from fuyuki.engine.fuyuki_core import FuyukiCore
from fuyuki.engine.models import (
    ElectricityTheory, Calculation, ResearchPaper, ElectricityTheoryCategory,
    CalculationType, ElectricityConstants
)

__all__ = [
    "FuyukiConfig",
    "FuyukiCore",
    "ElectricityTheory",
    "Calculation",
    "ResearchPaper",
    "ElectricityTheoryCategory",
    "CalculationType",
    "ElectricityConstants",
]
