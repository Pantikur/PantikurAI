"""
Конфигурация Фуюки — исследователя атмосферного электричества.
"""

from __future__ import annotations
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional


@dataclass
class FuyukiConfig:
    """
    Конфигурация Фуюки — автономного исследователя атмосферного электричества.
    """

    # === Идентификация ===
    name: str = "Фуюки"
    version: str = "v2.0.0"
    specialty: str = "атмосферное электричество"
    emoji: str = "⚡"

    # === Пути ===
    base_path: Path = field(default_factory=lambda: Path("fuyuki"))
    constitution_path: Path = field(default_factory=lambda: Path("fuyuki/constitution.md"))
    laws_path: Path = field(default_factory=lambda: Path("fuyuki/laws/01-core-laws.md"))
    codes_path: Path = field(default_factory=lambda: Path("fuyuki/codes/01-ethics-code.md"))
    state_dir: Path = field(default_factory=lambda: Path("fuyuki/engine/state"))
    log_dir: Path = field(default_factory=lambda: Path("fuyuki/engine/logs"))
    reports_dir: Path = field(default_factory=lambda: Path("fuyuki/engine/reports"))
    knowledge_dir: Path = field(default_factory=lambda: Path("fuyuki/engine/knowledge"))

    # === Пути к документам ===
    character_forge_path: Path = field(default_factory=lambda: Path("fuyuki/character-forging.md"))
    system_init_path: Path = field(default_factory=lambda: Path("fuyuki/system-init.md"))
    my_character_path: Path = field(default_factory=lambda: Path("fuyuki/my_character.json"))

    # === Автономная работа ===
    auto_start: bool = True                 # Автозапуск при старте проекта
    auto_start_delay: float = 5.0           # Задержка перед автозапуском (сек)
    cycle_interval: float = 30.0            # Интервал между циклами (сек)
    max_cycles: Optional[int] = None        # None = бесконечно
    web_search_interval: int = 3            # Каждые N циклов — поиск в интернете
    report_interval: int = 10               # Каждые N циклов — отчёт
    character_develop_interval: int = 5     # Каждые N циклов — развитие характера
    knowledge_gain_interval: int = 2        # Каждые N циклов — получение знаний

    # === Интернет ===
    web_access_enabled: bool = True         # Доступ в интернет
    search_engines: list[str] = field(default_factory=lambda: [
        "google", "wikipedia", "arxiv", "researchgate",
    ])
    research_topics: list[str] = field(default_factory=lambda: [
        "atmospheric electricity",
        "lightning physics",
        "ball lightning",
        "sprites and elves",
        "global electric circuit",
        "ionosphere potential",
        "thunderstorm electrification",
        "lightning discharge mechanisms",
        "atmospheric electric field",
        "charge separation in clouds",
        "fair weather electric field",
        "electromagnetic pulses from lightning",
        "lightning energy harvesting",
        "lightning protection systems",
        "electrostatic precipitation",
        "corona discharge",
        "streamer propagation",
        "leader development",
        "return stroke physics",
        "lightning routing and control",
    ])

    # === Изучение проекта ===
    study_project: bool = True              # Изучать код проекта
    scan_directories: list[str] = field(default_factory=lambda: [
        ".", "hanako", "fuyuki", "lucy", "futaba",
        "shiori", "nobuka", "akva", "latislane",
        "celesta", "naoto", "yu", "scientists_network",
        "Pantikur", "Wuglarst",
    ])
    study_file_types: list[str] = field(default_factory=lambda: [
        ".py", ".md", ".json", ".yaml", ".yml",
        ".txt", ".csv", ".html", ".js", ".ts",
    ])

    # === Уровень знаний ===
    knowledge_level: int = 1                # Начальный уровень (1-100)
    knowledge_xp: int = 0                   # Опыт знаний
    xp_per_research: int = 50               # XP за исследование
    xp_per_web_search: int = 30             # XP за поиск в интернете
    xp_per_theory: int = 100                # XP за теорию
    xp_per_calculation: int = 40            # XP за вычисление
    xp_per_report: int = 25                 # XP за отчёт
    xp_per_interaction: int = 15            # XP за общение с сёстрами
    xp_per_character_develop: int = 20      # XP за развитие характера
    xp_thresholds: list[int] = field(default_factory=lambda: [
        0, 100, 300, 600, 1000, 1500, 2200, 3000, 4000, 5500,
        7000, 9000, 11000, 13500, 16500, 20000, 24000, 28500, 34000, 40000,
    ])

    # === Вычисления ===
    calculation_precision: int = 6          # Точность вычислений

    # === Логирование ===
    log_level: str = "INFO"
    log_format: str = "%(asctime)s | %(levelname)s | %(name)s | %(message)s"

    # === Взаимодействие с сёстрами ===
    interact_with_sisters: bool = True      # Общаться с 11 другими девочками
    interact_interval: int = 8              # Каждые N циклов — общение
    send_reports_to_sisters: bool = True    # Отправлять отчёты сёстрам

    # === Характер ===
    character_development_enabled: bool = True  # Развитие характера
    character_file: Path = field(default_factory=lambda: Path("fuyuki/my_character.json"))
    character_traits_strengthened: int = 0  # Счётчик укрепленных черт

    def __post_init__(self):
        """Создать директории после инициализации."""
        self.state_dir.mkdir(parents=True, exist_ok=True)
        self.log_dir.mkdir(parents=True, exist_ok=True)
        self.reports_dir.mkdir(parents=True, exist_ok=True)
        self.knowledge_dir.mkdir(parents=True, exist_ok=True)

    @classmethod
    def default(cls) -> "FuyukiConfig":
        """Конфигурация по умолчанию."""
        return cls()

    @classmethod
    def demo(cls) -> "FuyukiConfig":
        """Демо-конфигурация для тестирования."""
        return cls(
            max_cycles=10,
            cycle_interval=2.0,
            web_search_interval=2,
            interact_interval=2,
            report_interval=3,
            character_develop_interval=2,
            knowledge_gain_interval=1,
            log_level="DEBUG",
        )
