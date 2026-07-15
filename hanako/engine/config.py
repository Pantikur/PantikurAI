"""
Конфигурация Ханако — исследователя гравитации.
"""

from __future__ import annotations

import enum
from pathlib import Path


class WebSearchMode(enum.Enum):
    """Режимы веб-поиска."""
    NONE = "none"
    LOCAL = "local"
    INTERNET = "internet"
    FULL = "full"


class AutonomyMode(enum.Enum):
    """Режимы автономности."""
    ASSISTED = "assisted"
    SEMIAUTONOMOUS = "semiautonomous"
    FULL = "full"
    GODMODE = "godmode"


class HanakoConfig:
    """Конфигурация Ханако — исследователя гравитации."""

    def __init__(
        self,
        name: str = "Hanako",
        version: str = "v2.0.0",
        max_autonomy_level: AutonomyMode = AutonomyMode.FULL,
        web_search_mode: WebSearchMode = WebSearchMode.FULL,
        auto_start: bool = True,
        research_interval_seconds: int = 300,
        report_interval_hours: float = 24.0,
        communication_interval_seconds: int = 600,
        self_development_interval_seconds: int = 1800,
        character_review_interval_hours: float = 168.0,
        max_theories: int = 100,
        max_research_tasks: int = 50,
        max_web_cache: int = 500,
        max_messages_inbox: int = 200,
        log_dir: Path = Path("."),
        state_dir: Path = Path("."),
        cache_dir: Path = Path("."),
        internet_enabled: bool = True,
        communication_enabled: bool = True,
        self_development_enabled: bool = True,
        report_generation_enabled: bool = True,
        character_growth_enabled: bool = True,
        level_up_notifications: bool = True,
        research_topics: list[str] | None = None,
        priority_sources: list[str] | None = None,
    ):
        self.name = name
        self.version = version
        self.max_autonomy_level = max_autonomy_level
        self.web_search_mode = web_search_mode
        self.auto_start = auto_start
        self.research_interval_seconds = research_interval_seconds
        self.report_interval_hours = report_interval_hours
        self.communication_interval_seconds = communication_interval_seconds
        self.self_development_interval_seconds = self_development_interval_seconds
        self.character_review_interval_hours = character_review_interval_hours
        self.max_theories = max_theories
        self.max_research_tasks = max_research_tasks
        self.max_web_cache = max_web_cache
        self.max_messages_inbox = max_messages_inbox
        self.log_dir = log_dir
        self.state_dir = state_dir
        self.cache_dir = cache_dir
        self.internet_enabled = internet_enabled
        self.communication_enabled = communication_enabled
        self.self_development_enabled = self_development_enabled
        self.report_generation_enabled = report_generation_enabled
        self.character_growth_enabled = character_growth_enabled
        self.level_up_notifications = level_up_notifications

        self.research_topics = research_topics or [
            "Общая теория относительности Эйнштейна",
            "Квантовая гравитация",
            "Петлевая квантовая гравитация",
            "Теория струн и М-теория",
            "Гравитоны и квантовые поля",
            "Тёмная материя и гравитация",
            "Гравитационные волны",
            "Чёрные дыры и информационный парадокс",
            "Энтропийная гравитация (Верлинде)",
            "Модифицированная ньютоновская динамика (MOND)",
            "Теория всего и унификация",
            "Пространство-время и квантовая запутанность",
            "Инфляция и ранняя Вселенная",
            "Иерархия проблем в физике",
            "Холодная тёмная материя vs гравитация",
        ]

        self.priority_sources = priority_sources or [
            "arXiv.org",
            "NASA.gov",
            "CERN.ch",
            "Wikipedia.org",
            "arxiv.org/abs/gr-qc",
            "arxiv.org/abs/hep-ph",
            "arxiv.org/abs/astro-ph",
            "Physical Review Letters",
            "Journal of High Energy Physics",
            "Classical and Quantum Gravity",
            "Nature Physics",
            "Science",
        ]

    @classmethod
    def default(cls) -> "HanakoConfig":
        """Конфигурация по умолчанию — полный исследователь."""
        return cls(
            max_autonomy_level=AutonomyMode.FULL,
            web_search_mode=WebSearchMode.FULL,
            auto_start=True,
            internet_enabled=True,
            communication_enabled=True,
            self_development_enabled=True,
            report_generation_enabled=True,
            character_growth_enabled=True,
        )

    @classmethod
    def demo(cls) -> "HanakoConfig":
        """Демо-конфигурация — быстрый запуск."""
        c = cls.default()
        c.research_interval_seconds = 60
        c.communication_interval_seconds = 30
        c.self_development_interval_seconds = 120
        c.report_interval_hours = 2.0
        return c

    @classmethod
    def offline(cls) -> "HanakoConfig":
        """Офлайн-конфигурация — без интернета."""
        c = cls.default()
        c.internet_enabled = False
        c.web_search_mode = WebSearchMode.LOCAL
        return c

    @classmethod
    def godmode(cls) -> "HanakoConfig":
        """Режим бога — максимальная автономия."""
        c = cls.default()
        c.max_autonomy_level = AutonomyMode.GODMODE
        c.research_interval_seconds = 10
        c.communication_interval_seconds = 5
        c.max_theories = 1000
        return c

    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "version": self.version,
            "max_autonomy_level": self.max_autonomy_level.value,
            "web_search_mode": self.web_search_mode.value,
            "auto_start": self.auto_start,
            "research_interval_seconds": self.research_interval_seconds,
            "report_interval_hours": self.report_interval_hours,
            "communication_interval_seconds": self.communication_interval_seconds,
            "self_development_interval_seconds": self.self_development_interval_seconds,
            "character_review_interval_hours": self.character_review_interval_hours,
            "max_theories": self.max_theories,
            "max_research_tasks": self.max_research_tasks,
            "max_web_cache": self.max_web_cache,
            "max_messages_inbox": self.max_messages_inbox,
            "internet_enabled": self.internet_enabled,
            "communication_enabled": self.communication_enabled,
            "self_development_enabled": self.self_development_enabled,
            "report_generation_enabled": self.report_generation_enabled,
            "character_growth_enabled": self.character_growth_enabled,
            "level_up_notifications": self.level_up_notifications,
            "research_topics_count": len(self.research_topics),
            "priority_sources_count": len(self.priority_sources),
        }

    @property
    def all_scientists(self) -> list[str]:
        """Все девочки-учёные в проекте."""
        return [
            "hanako", "fuyuki", "lucy", "futaba", "shiori",
            "nobuka", "latislane", "celest", "akva", "yu",
            "ayiko", "naoto",
        ]
