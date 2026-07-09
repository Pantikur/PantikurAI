"""
Движок Шиори — автономная иммунная система Вугларста.

Пакет реализует:
  - shiori_core   — бесконечный цикл защиты и саморазвития
  - threat_hunter — охотник за угрозами (сканирование, обнаружение, анализ)
  - patch_manager — менеджер патчей и восстановления
  - models        — модели данных (угрозы, инциденты, правила защиты)
  - config        — конфигурация системы
"""

from shiori.engine.config import ShioriConfig
from shiori.engine.shiori_core import ShioriCore
from shiori.engine.threat_hunter import ThreatHunter
from shiori.engine.patch_manager import PatchManager

__all__ = ["ShioriCore", "ThreatHunter", "PatchManager"]
