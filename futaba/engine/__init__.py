"""
Движок Футаба — автономное ядро постоянной работы.

Пакет реализует:
  - futaba_core   — бесконечный цикл саморазвития и самопроверки
  - trial_grounds — полигон испытаний: генерация миров для тестов правления
  - models        — модели данных (конституция, мир, версия правления)
  - config        — конфигурация системы
"""

from futaba.engine.config import FutabaConfig
from futaba.engine.futaba_core import FutabaCore
from futaba.engine.trial_grounds import TrialGrounds

__all__ = ["FutabaConfig", "FutabaCore", "TrialGrounds"]
