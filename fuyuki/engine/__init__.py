"""
Фуюки — исследователь атмосферного электричества.

Полностью автономная система, которая:
  - Изучает атмосферное электричество в интернете и проекте
  - Самостоятельно развивает свой характер и знания
  - Выходит в интернет для поиска информации
  - Работает автономно с автозапуском
  - Общается с 11 другими девочками через Scientists Network
  - Пишет отчёты и повышает уровень знаний
"""

from __future__ import annotations

from fuyuki.engine.config import FuyukiConfig
from fuyuki.engine.fuyuki_core import FuyukiCore
from fuyuki.engine.models import (
    ResearchRecord, ElectricityTheory, Calculation,
    ElectricityTheoryCategory, CalculationType, ElectricityConstants,
    ResearchPaper, LightningStrike, KnowledgeLevel,
)
from fuyuki.engine.web_access import FuyukiWebAccess
from fuyuki.engine.theorist import ElectricityTheorist
from fuyuki.engine.calculator import ElectricityCalculator
from fuyuki.engine.report_generator import ReportGenerator
from fuyuki.engine.knowledge_manager import KnowledgeManager
from fuyuki.engine.character_developer import CharacterDeveloper

__all__ = [
    "FuyukiConfig",
    "FuyukiCore",
    "FuyukiWebAccess",
    "ElectricityTheorist",
    "ElectricityCalculator",
    "ReportGenerator",
    "KnowledgeManager",
    "CharacterDeveloper",
    "ResearchRecord",
    "ElectricityTheory",
    "Calculation",
    "ElectricityTheoryCategory",
    "CalculationType",
    "ElectricityConstants",
    "ResearchPaper",
    "LightningStrike",
    "KnowledgeLevel",
]
