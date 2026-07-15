"""
Конфигурация системы Аква — научный модуль Pantikur.
"""

from __future__ import annotations
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional


@dataclass
class AkvaConfig:
    """Конфигурация научного модуля Аква."""

    # === Идентификация ===
    name: str = "Аква"
    version: str = "v2.0.0"

    # === Пути к документам ===
    base_path: Path = field(default_factory=lambda: Path("akva"))
    constitution_path: Path = field(default_factory=lambda: Path("akva/constitution.md"))
    laws_path: Path = field(default_factory=lambda: Path("akva/laws/01-core-laws.md"))
    ethics_path: Path = field(default_factory=lambda: Path("akva/codes/01-ethics-code.md"))

    # === Состояние и логи ===
    state_dir: Path = field(default_factory=lambda: Path("akva/engine/state"))
    log_path: Path = field(default_factory=lambda: Path("akva/engine/state/akva.log"))
    state_path: Path = field(default_factory=lambda: Path("akva/engine/state/akva_state.json"))
    reports_dir: Path = field(default_factory=lambda: Path("data/reports"))
    knowledge_dir: Path = field(default_factory=lambda: Path("data/knowledge"))
    communication_dir: Path = field(default_factory=lambda: Path("data/communication"))
    personality_path: Path = field(default_factory=lambda: Path("akva/engine/state/personality.json"))
    knowledge_levels_path: Path = field(default_factory=lambda: Path("akva/engine/state/knowledge_levels.json"))

    # === Циклы работы ===
    cycle_interval: float = 5.0           # секунды между циклами
    max_cycles: Optional[int] = None       # None = бесконечно
    save_state_every_n_cycles: int = 5    # сохранять состояние каждые N циклов

    # === Научные области ===
    research_areas: list[str] = field(default_factory=lambda: [
        "mathematics",
        "physics",
        "aerodynamics",
        "strength_of_materials",
    ])

    # === Интернет ===
    web_search_enabled: bool = True
    web_search_interval: int = 3          # каждые N циклов
    max_search_results: int = 10

    # === Автономность ===
    max_autonomy_level: str = "L2"        # L0-L4
    require_confirmation_above: str = "L2"

    # === Саморазвитие ===
    self_development_enabled: bool = True
    self_assessment_interval: int = 10    # каждые N циклов — самоанализ
    xp_per_cycle_base: int = 10           # базовый XP за цикл

    # === Общение ===
    communication_enabled: bool = True
    communication_interval: int = 3       # каждые N циклов — общение
    other_girls: list[str] = field(default_factory=lambda: [
        "hanako", "fuyuki", "lucy", "futaba", "shiori",
        "nobuka", "latislane", "celest", "yu", "naoto",
    ])

    # === Отчётность ===
    reporting_enabled: bool = True
    report_every_cycle: bool = True       # отчёт каждый цикл
    summary_to_others: bool = True        # сводка другим модулям

    # === Логирование ===
    log_level: str = "INFO"
    log_format: str = "%(asctime)s | %(levelname)s | %(name)s | %(message)s"

    # === Безопасность ===
    hard_stop_on_constitution_violation: bool = True

    def __post_init__(self):
        """Создать директории после инициализации."""
        self.state_dir.mkdir(parents=True, exist_ok=True)
        self.reports_dir.mkdir(parents=True, exist_ok=True)
        self.knowledge_dir.mkdir(parents=True, exist_ok=True)
        self.communication_dir.mkdir(parents=True, exist_ok=True)

    @classmethod
    def default(cls) -> AkvaConfig:
        return cls()

    @classmethod
    def demo(cls) -> AkvaConfig:
        """Демо-конфигурация для тестирования."""
        return cls(
            max_cycles=10,
            cycle_interval=2.0,
            web_search_interval=2,
            communication_interval=2,
            log_level="DEBUG",
        )
