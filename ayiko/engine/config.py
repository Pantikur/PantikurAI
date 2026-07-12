"""
Конфигурация системы Айко — чтение книг и обучение модели.
"""

from __future__ import annotations
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional


@dataclass
class AyikoConfig:
    """
    Конфигурация системы чтения и обучения Айко.
    """

    # === Идентификация ===
    name: str = "Айко"
    version: str = "v1.0.0"

    # === Пути к документам ===
    base_path: Path = field(default_factory=lambda: Path("ayiko"))
    constitution_path: Path = field(default_factory=lambda: Path("ayiko/constitution.md"))
    laws_path: Path = field(default_factory=lambda: Path("ayiko/laws/01-core-laws.md"))
    ethics_path: Path = field(default_factory=lambda: Path("ayiko/codes/01-ethics-code.md"))

    # === Состояние и логи ===
    state_dir: Path = field(default_factory=lambda: Path("ayiko/engine/state"))
    log_path: Path = field(default_factory=lambda: Path("ayiko/engine/state/ayiko.log"))
    state_path: Path = field(default_factory=lambda: Path("ayiko/engine/state/ayiko_state.json"))
    knowledge_base_path: Path = field(default_factory=lambda: Path("ayiko/engine/state/knowledge_base.json"))
    training_pairs_path: Path = field(default_factory=lambda: Path("ayiko/engine/state/training_pairs.jsonl"))
    lore_db_path: Path = field(default_factory=lambda: Path("ayiko/engine/state/lore_db.json"))
    style_db_path: Path = field(default_factory=lambda: Path("ayiko/engine/state/style_db.json"))

    # === Книги ===
    books_directory: Path = field(default_factory=lambda: Path("data/books"))
    supported_formats: list[str] = field(default_factory=lambda: [
        ".txt", ".epub", ".pdf", ".md", ".json",
    ])

    # === Обучение ===
    max_training_pairs_per_book: int = 1000
    min_confidence_threshold: float = 0.7
    enable_style_learning: bool = True
    enable_lore_extraction: bool = True
    enable_plot_analysis: bool = True

    # === Интернет ===
    web_search_enabled: bool = True
    web_search_interval: int = 10
    max_search_results: int = 10

    # === Автономность ===
    max_autonomy_level: str = "L3"
    require_confirmation_above: str = "L2"

    # === Циклы работы ===
    cycle_interval: float = 10.0
    analysis_interval: int = 5
    max_cycles: Optional[int] = None

    # === Логирование ===
    log_level: str = "INFO"
    log_format: str = "%(asctime)s | %(levelname)s | %(name)s | %(message)s"
    save_state_every_n_cycles: int = 5

    # === Безопасность ===
    hard_stop_on_constitution_violation: bool = True
    auto_rollback_on_failure: bool = True

    # === Взаимодействие с сёстрами ===
    notify_sisters_on_new_knowledge: bool = True
    share_knowledge_with_sisters: bool = True

    def __post_init__(self):
        """Создать директории после инициализации."""
        self.state_dir.mkdir(parents=True, exist_ok=True)

    @classmethod
    def default(cls) -> AyikoConfig:
        """Конфигурация по умолчанию."""
        return cls()

    @classmethod
    def demo(cls) -> AyikoConfig:
        """Демо-конфигурация для тестирования."""
        return cls(
            max_cycles=5,
            cycle_interval=2.0,
            analysis_interval=2,
            log_level="DEBUG",
        )
