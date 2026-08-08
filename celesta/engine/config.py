"""
Конфигурация системы Селеста.
"""

from __future__ import annotations
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional


@dataclass
class CelestaConfig:
    """
    Конфигурация системы изучения интимной жизни Селеста.
    """

    # === Идентификация ===
    name: str = "Селеста"
    version: str = "v2.0.0"

    # === Пути к документам ===
    base_path: Path = Path("celesta")
    constitution_path: Path = field(default_factory=lambda: Path("celesta/constitution.md"))
    laws_path: Path = field(default_factory=lambda: Path("celesta/laws/01-core-laws.md"))
    ethics_path: Path = field(default_factory=lambda: Path("celesta/codes/01-ethics-code.md"))

    # === Состояние и логи ===
    state_dir: Path = field(default_factory=lambda: Path("celesta/engine/state"))
    log_path: Path = field(default_factory=lambda: Path("celesta/engine/state/celesta.log"))
    state_path: Path = field(default_factory=lambda: Path("celesta/engine/state/celesta_state.json"))
    analysis_report_path: Path = field(default_factory=lambda: Path("celesta/engine/state/analysis_report.json"))

    # === Циклы работы ===
    cycle_interval: float = 10.0          # секунды между циклами
    analysis_interval: int = 5            # каждые N циклов запускать анализ
    max_cycles: Optional[int] = None      # None = бесконечно

    # === Автономность ===
    max_autonomy_level: str = "L3"        # L0-L4
    require_confirmation_above: str = "L2"  # выше этого уровня — запрос

    # === Интернет ===
    web_search_enabled: bool = True       # доступ к интернету
    web_search_interval: int = 3          # каждые N циклов веб-поиск
    max_search_results: int = 10

    # === Скан директорий ===
    project_root: Path = field(default_factory=lambda: Path("."))
    scan_directories: list[str] = field(default_factory=lambda: [
        ".", "hanako", "fuyuki", "lucy", "futaba",
        "shiori", "nobuka", "akva", "latislane",
        "celesta", "naoto", "yu", "scientists_network",
    ])
    exclude_patterns: list[str] = field(default_factory=lambda: [
        "__pycache__", "*.pyc", ".git", "node_modules", "venv",
    ])

    # === Логирование ===
    log_level: str = "INFO"
    log_format: str = "%(asctime)s | %(levelname)s | %(name)s | %(message)s"
    save_state_every_n_cycles: int = 5

    # === Симуляция ===
    random_seed: Optional[int] = None
    enable_deterministic_mode: bool = False

    # === Безопасность ===
    hard_stop_on_constitution_violation: bool = True

    # === Анализ файлов ===
    max_file_lines: int = 10000           # максимум строк в файле для анализа
    max_function_lines: int = 50          # максимум строк в функции
    max_complexity: int = 10              # максимум цикломатической сложности

    # === Взаимодействие с сёстрами ===
    notify_futaba_on_change: bool = True
    notify_shiori_on_security_change: bool = True

    def __post_init__(self):
        self.state_dir.mkdir(parents=True, exist_ok=True)

    @classmethod
    def default(cls) -> CelestaConfig:
        return cls()

    @classmethod
    def demo(cls) -> CelestaConfig:
        return cls(
            max_cycles=5,
            cycle_interval=2.0,
            analysis_interval=2,
            log_level="DEBUG",
        )
