"""
Конфигурация системы Футаба.
"""

from __future__ import annotations
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional


@dataclass
class FutabaConfig:
    """
    Конфигурация автономного ядра Футаба.
    """
    
    # === Идентификация ===
    name: str = "Футаба"
    version: str = "v1.0.0"
    
    # === Пути к документам ===
    base_path: Path = Path("futaba")
    constitution_path: Path = field(default_factory=lambda: Path("futaba/constitution.md"))
    laws_path: Path = field(default_factory=lambda: Path("futaba/laws/01-core-laws.md"))
    ethics_path: Path = field(default_factory=lambda: Path("futaba/codes/01-ethics-code.md"))
    
    # === Состояние и логи ===
    state_dir: Path = field(default_factory=lambda: Path("futaba/engine/state"))
    log_path: Path = field(default_factory=lambda: Path("futaba/engine/state/futaba.log"))
    state_path: Path = field(default_factory=lambda: Path("futaba/engine/state/futaba_state.json"))
    trials_log_path: Path = field(default_factory=lambda: Path("futaba/engine/state/trials.json"))
    
    # === Циклы работы ===
    cycle_interval: float = 5.0          # секунды между циклами саморазвития
    trial_interval: int = 10             # каждые N циклов запускать полигон испытаний
    max_cycles: Optional[int] = None     # None = бесконечно, int = демо-режим
    
    # === Автономность ===
    max_autonomy_level: str = "L3"       # L0-L4 (см. протокол саморазвития)
    require_confirmation_above: str = "L2"  # выше этого уровня — запрос подтверждения
    
    # === Интернет ===
    web_search_enabled: bool = True      # доступ к интернету
    web_search_interval: int = 5         # каждые N циклов веб-поиск
    max_search_results: int = 10         # максимум результатов поиска
    research_databases: list[str] = field(default_factory=lambda: [
        "self_development",   # Саморазвитие
        "political_theory",   # Политическая теория
        "governance",         # Управление
        "evolution",          # Эволюция
    ])
    
    # === Полигон испытаний ===
    trial_worlds_per_batch: int = 3      # сколько миров генерировать за один запуск полигона
    trial_epochs_per_world: int = 20     # сколько эпох симулировать на мир
    trial_versions_to_test: int = 5      # сколько версий правления тестировать
    
    # === Логирование ===
    log_level: str = "INFO"              # DEBUG, INFO, WARNING, ERROR
    log_format: str = "%(asctime)s | %(levelname)s | %(name)s | %(message)s"
    save_state_every_n_cycles: int = 5   # сохранять состояние каждые N циклов
    
    # === Симуляция ===
    random_seed: Optional[int] = None    # None = случайный, int = для воспроизводимости
    enable_deterministic_mode: bool = False  # если True, использовать random_seed всегда
    
    # === Безопасность ===
    hard_stop_on_constitution_violation: bool = True  # остановка при нарушении конституции
    max_change_risk_threshold: float = 0.05  # максимальный допустимый риск изменения (5%)
    
    def __post_init__(self):
        """Создать директории после инициализации."""
        self.state_dir.mkdir(parents=True, exist_ok=True)
    
    @classmethod
    def default(cls) -> FutabaConfig:
        """Конфигурация по умолчанию."""
        return cls()
    
    @classmethod
    def demo(cls) -> FutabaConfig:
        """Демо-конфигурация для тестирования (ограниченные циклы)."""
        return cls(
            max_cycles=5,
            cycle_interval=1.0,
            trial_interval=2,
            trial_worlds_per_batch=2,
            trial_epochs_per_world=10,
            log_level="DEBUG"
        )
