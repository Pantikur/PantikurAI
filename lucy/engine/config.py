"""
Конфигурация системы Люси — инженера двигателей.
"""

from __future__ import annotations
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional


@dataclass
class LucyConfig:
    """
    Конфигурация системы Люси — инженера двигателей.
    """

    # === Идентификация ===
    name: str = "Люси"
    version: str = "v2.0.0"

    # === Пути к документам ===
    base_path: Path = Path("lucy")
    constitution_path: Path = field(default_factory=lambda: Path("lucy/constitution.md"))
    laws_path: Path = field(default_factory=lambda: Path("lucy/laws/01-core-laws.md"))
    ethics_path: Path = field(default_factory=lambda: Path("lucy/codes/01-ethics-code.md"))

    # === Состояние и логи ===
    state_dir: Path = field(default_factory=lambda: Path("lucy/engine/state"))
    log_path: Path = field(default_factory=lambda: Path("lucy/engine/state/lucy.log"))
    state_path: Path = field(default_factory=lambda: Path("lucy/engine/state/lucy_state.json"))
    knowledge_dir: Path = field(default_factory=lambda: Path("lucy/engine/knowledge"))
    reports_dir: Path = field(default_factory=lambda: Path("lucy/engine/reports"))
    web_cache_path: Path = field(default_factory=lambda: Path("lucy/engine/state/web_cache.json"))

    # === Циклы работы ===
    cycle_interval: float = 10.0          # секунды между циклами
    web_search_interval: int = 3          # каждые N циклов веб-поиск
    report_interval: int = 5              # каждые N циклов писать отчёт
    max_cycles: Optional[int] = None      # None = бесконечно, int = демо-режим

    # === Автозапуск ===
    auto_start: bool = True               # автозапуск при старте проекта

    # === Интернет ===
    web_search_enabled: bool = True       # доступ к интернету
    max_search_results: int = 10          # максимум результатов поиска
    research_topics: list[str] = field(default_factory=lambda: [
        "internal combustion engines",
        "rocket engines",
        "ion thrusters",
        "gravitational propulsion",
        "atmospheric electricity for engines",
        "hybrid propulsion systems",
        "MHD engines",
        "plasma thrusters",
        "nuclear propulsion",
        "solar sails",
        "antimatter engines",
        "warp drive theory",
        "gravity manipulation",
        "electromagnetic propulsion",
        "pulsed plasma thrusters",
        "VASIMR engines",
        "solar thermal engines",
        "fission fragment engines",
        "beamed energy propulsion",
        "light sails",
    ])

    # === Изучение проекта ===
    project_root: Path = field(default_factory=lambda: Path("."))
    scan_directories: list[str] = field(default_factory=lambda: [
        ".", "hanako", "fuyuki", "lucy", "futaba",
        "shiori", "nobuka", "akva", "latislane",
        "celesta", "naoto", "yu", "scientists_network",
    ])
    exclude_patterns: list[str] = field(default_factory=lambda: [
        "__pycache__", "*.pyc", ".git", "node_modules", "venv",
        "*.egg-info", "build", "dist", "*.egg",
    ])

    # === Знания и уровни ===
    knowledge_levels: list[dict] = field(default_factory=lambda: [
        {"level": 1, "name": "Механик", "xp": 0},
        {"level": 2, "name": "Техник", "xp": 100},
        {"level": 3, "name": "Инженер", "xp": 300},
        {"level": 4, "name": "Мл. инженер", "xp": 600},
        {"level": 5, "name": "Инженер-проектировщик", "xp": 1000},
        {"level": 6, "name": "Ст. инженер", "xp": 1500},
        {"level": 7, "name": "Ведущий инженер", "xp": 2200},
        {"level": 8, "name": "Кандидат инженерных наук", "xp": 3000},
        {"level": 9, "name": "Доцент по двигателям", "xp": 4000},
        {"level": 10, "name": "Профессор пропульсии", "xp": 5500},
        {"level": 11, "name": "Ведущий исследователь", "xp": 7000},
        {"level": 12, "name": "Зав. лабораторией", "xp": 9000},
        {"level": 13, "name": "Доктор инженерных наук", "xp": 11000},
        {"level": 14, "name": "Проф. мирового уровня", "xp": 13500},
        {"level": 15, "name": "Легенда двигателестроения", "xp": 16500},
        {"level": 16, "name": "Гений пропульсии", "xp": 20000},
        {"level": 17, "name": "Мастер гравитации", "xp": 24000},
        {"level": 18, "name": "Повелитель двигателей", "xp": 28500},
        {"level": 19, "name": "Хранитель пропульсии", "xp": 34000},
        {"level": 20, "name": "Бог Двигателей", "xp": 40000},
    ])

    # === Характер ===
    character_development_enabled: bool = True  # Развитие характера
    character_file: Path = field(default_factory=lambda: Path("lucy/my_character.json"))
    character_traits_strengthened: int = 0  # Счётчик укрепленных черт

    # === Логирование ===
    log_level: str = "INFO"               # DEBUG, INFO, WARNING, ERROR
    log_format: str = "%(asctime)s | %(levelname)s | %(name)s | %(message)s"
    save_state_every_n_cycles: int = 5    # сохранять состояние каждые N циклов

    def __post_init__(self):
        """Создать директории после инициализации."""
        self.state_dir.mkdir(parents=True, exist_ok=True)
        self.knowledge_dir.mkdir(parents=True, exist_ok=True)
        self.reports_dir.mkdir(parents=True, exist_ok=True)

    @classmethod
    def default(cls) -> LucyConfig:
        """Конфигурация по умолчанию."""
        return cls()

    @classmethod
    def demo(cls) -> LucyConfig:
        """Демо-конфигурация для тестирования."""
        return cls(
            max_cycles=10,
            cycle_interval=2.0,
            web_search_interval=2,
            log_level="DEBUG",
            scan_directories=[
                ".", "hanako", "fuyuki", "lucy", "futaba",
                "shiori", "nobuka", "akva", "latislane",
                "celesta", "naoto", "yu", "scientists_network",
            ],
        )
