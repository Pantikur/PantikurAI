"""
Ханако — Исследователь гравитации.

Модули:
  - hanako_core: Ядро системы
  - config: Конфигурация
  - models: Модели данных
  - web_access: Веб-доступ в интернет
  - theorist: Построитель теорий гравитации
  - calculator: Калькулятор гравитационных параметров
  - self_development: Саморазвитие
  - character: Система характера
  - communication: Общение с 11 девочками
  - reports: Система отчётов
  - auto_start: Автозапуск
"""

from __future__ import annotations

from hanako.engine.config import HanakoConfig, AutonomyMode, WebSearchMode
from hanako.engine.models import (
    GravityTheory, TheoryCategory, ResearchTask, ResearchStatus,
    ScientistMessage, CommunicationType, CharacterTraits,
    KnowledgeLevel, ResearchReport, HanakoEvent, WebResearchResult,
)
from hanako.engine.hanako_core import HanakoCore
from hanako.engine.web_access import HanakoWebAccess
from hanako.engine.theorist import GravityTheorist
from hanako.engine.calculator import GravityCalculator
from hanako.engine.self_development import SelfDevelopment
from hanako.engine.character import CharacterSystem
from hanako.engine.communication import CommunicationSystem
from hanako.engine.reports import ReportSystem
from hanako.engine.auto_start import AutoStartSystem


__all__ = [
    "HanakoCore",
    "HanakoConfig",
    "AutonomyMode",
    "WebSearchMode",
    "GravityTheory",
    "TheoryCategory",
    "ResearchTask",
    "ResearchStatus",
    "ScientistMessage",
    "CommunicationType",
    "CharacterTraits",
    "KnowledgeLevel",
    "ResearchReport",
    "HanakoEvent",
    "WebResearchResult",
    "HanakoWebAccess",
    "GravityTheorist",
    "GravityCalculator",
    "SelfDevelopment",
    "CharacterSystem",
    "CommunicationSystem",
    "ReportSystem",
    "AutoStartSystem",
]
