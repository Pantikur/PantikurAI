"""
Конфигурация Фуюки — исследователя атмосферного электричества.
"""

from __future__ import annotations
import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List


@dataclass
class FuyukiConfig:
    """Конфигурация Фуюки."""
    
    # Основные параметры
    name: str = "Fuyuki"
    version: str = "v1.0.0"
    research_focus: str = "atmospheric_electricity"
    
    # Директории
    base_dir: Path = field(default_factory=lambda: Path("fuyuki"))
    state_dir: Path = field(default_factory=lambda: Path("fuyuki/engine/state"))
    log_dir: Path = field(default_factory=lambda: Path("fuyuki/engine/logs"))
    
    # Параметры исследований
    max_cycles: int = 0  # 0 = бесконечно
    cycle_interval: float = 60.0  # секунд между циклами
    
    # Интернет
    web_search_enabled: bool = True
    web_search_interval: int = 3  # каждые 3 цикла
    
    # === Автономность ===
    max_autonomy_level: str = "L3"        # L0-L4 (см. протокол саморазвития)
    require_confirmation_above: str = "L2"  # выше этого уровня — запрос подтверждения
    
    # Теории
    max_theories: int = 100
    theory_validation_threshold: float = 0.7
    
    # Вычисления
    max_calculations: int = 1000
    calculation_precision: int = 10  # знаков после запятой
    
    # Логирование
    log_level: str = "INFO"
    save_logs: bool = True
    
    @classmethod
    def default(cls) -> "FuyukiConfig":
        """Конфигурация по умолчанию."""
        config = cls()
        config.state_dir.mkdir(parents=True, exist_ok=True)
        config.log_dir.mkdir(parents=True, exist_ok=True)
        return config
    
    @classmethod
    def demo(cls) -> "FuyukiConfig":
        """Демо-конфигурация (5 циклов, интервал 2 сек)."""
        config = cls(
            max_cycles=5,
            cycle_interval=2.0,
            web_search_interval=2,
        )
        config.state_dir.mkdir(parents=True, exist_ok=True)
        config.log_dir.mkdir(parents=True, exist_ok=True)
        return config
    
    def to_dict(self) -> Dict[str, Any]:
        """Преобразовать в словарь."""
        return {
            "name": self.name,
            "version": self.version,
            "research_focus": self.research_focus,
            "max_cycles": self.max_cycles,
            "cycle_interval": self.cycle_interval,
            "web_search_enabled": self.web_search_enabled,
            "web_search_interval": self.web_search_interval,
        }
    
    def save(self, path: Path):
        """Сохранить конфигурацию."""
        with open(path, "w", encoding="utf-8") as f:
            json.dump(self.to_dict(), f, indent=2)
    
    @classmethod
    def load(cls, path: Path) -> "FuyukiConfig":
        """Загрузить конфигурацию."""
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        return cls(**data)
