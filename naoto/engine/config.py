"""
Конфигурация системы Наото — Автономного Литературного Аналитика.
"""

from __future__ import annotations
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional
from enum import Enum


class AutonomyLevel(Enum):
    """Уровни свободы Наото."""
    L0 = "L0"  # Только чтение
    L1 = "L1"  # Анализ и отчеты
    L2 = "L2"  # Эволюция личности (с проверкой)
    L3 = "L3"  # Полная автономия и инициатива


@dataclass
class PersonalityTraits:
    """Текущие черты характера Наото."""
    empathy: float = 0.5       # Эмпатия
    cynicism: float = 0.5      # Цинизм
    curiosity: float = 0.7     # Любознательность
    logic: float = 0.5         # Логика
    creativity: float = 0.5    # Креативность
    moral_alignment: float = 0.5  # Нейтральность (-1 зло, +1 добро)

    def to_dict(self) -> Dict:
        return {
            "empathy": self.empathy,
            "cynicism": self.cynicism,
            "curiosity": self.curiosity,
            "logic": self.logic,
            "creativity": self.creativity,
            "moral_alignment": self.moral_alignment,
        }

    @classmethod
    def from_dict(cls, data: Dict) -> 'PersonalityTraits':
        return cls(
            empathy=data.get("empathy", 0.5),
            cynicism=data.get("cynicism", 0.5),
            curiosity=data.get("curiosity", 0.7),
            logic=data.get("logic", 0.5),
            creativity=data.get("creativity", 0.5),
            moral_alignment=data.get("moral_alignment", 0.5),
        )


@dataclass
class NaotoConfig:
    """
    Конфигурация Автономного Литературного Аналитика.
    """

    # === Идентификация ===
    name: str = "Наото"
    version: str = "v2.0 (Soul)"

    # === Пути к документам ===
    base_path: Path = Path("naoto")
    constitution_path: Path = field(default_factory=lambda: Path("naoto/constitution.md"))
    laws_path: Path = field(default_factory=lambda: Path("naoto/laws/01-core-laws.md"))
    ethics_path: Path = field(default_factory=lambda: Path("naoto/codes/01-ethics-code.md"))

    # === Состояние и логи ===
    state_dir: Path = field(default_factory=lambda: Path("naoto/engine/state"))
    log_path: Path = field(default_factory=lambda: Path("naoto/engine/state/naoto.log"))
    state_path: Path = field(default_factory=lambda: Path("naoto/engine/state/naoto_state.json"))
    logs_dir: Path = field(default_factory=lambda: Path("naoto/engine/logs"))
    knowledge_dir: Path = field(default_factory=lambda: Path("naoto/engine/knowledge"))
    reports_dir: Path = field(default_factory=lambda: Path("naoto/engine/reports"))

    # === Циклы работы ===
    cycle_interval: float = 10.0          # секунды между циклами улучшений
    analysis_interval: int = 5            # каждые N циклов запускать анализ проекта
    max_cycles: Optional[int] = None      # None = бесконечно, int = демо-режим

    # === Автономность ===
    autonomy_level: AutonomyLevel = AutonomyLevel.L2
    max_autonomy_level: AutonomyLevel = AutonomyLevel.L3
    require_confirmation_above: str = "L2"  # выше этого уровня — запрос подтверждения

    # === Интернет и Поиск ===
    web_search_enabled: bool = True
    target_sites: List[str] = field(default_factory=lambda: [
        "litnet.com", "author.today", "gutenberg.org", "ficbook.net"
    ])
    web_search_interval: int = 5          # каждые N циклов веб-поиск
    max_search_results: int = 10          # максимум результатов поиска

    # === Персона (Личность) ===
    personality: PersonalityTraits = field(default_factory=PersonalityTraits)

    # === Взаимодействие с сёстрами ===
    sisters_communication_interval: int = 5  # Циклов
    notify_futaba_on_logic_change: bool = True
    notify_shiori_on_security_change: bool = True
    scan_with_shiori_before_apply: bool = True

    # === Анализ кода (унаследовано для совместимости) ===
    project_root: Path = field(default_factory=lambda: Path("."))
    scan_directories: list[str] = field(default_factory=lambda: [
        ".", "hanako", "fuyuki", "lucy", "futaba",
        "shiori", "nobuka", "akva", "latislane",
        "celesta", "naoto", "yu", "scientists_network",
    ])
    exclude_patterns: list[str] = field(default_factory=lambda: [
        "__pycache__", "*.pyc", ".git", "node_modules", "venv",
        "*.egg-info", "build", "dist", "*.egg",
        "android-studio-plugin",
    ])
    max_file_lines: int = 300
    max_function_lines: int = 50
    max_complexity: int = 10
    min_test_coverage: float = 0.80

    # === Тестирование ===
    test_coverage_target: float = 0.90
    max_test_duration_seconds: float = 120.0
    generate_tests_for_new_code: bool = True
    run_regression_on_change: bool = True

    # === Бенчмарки ===
    benchmark_iterations: int = 100
    benchmark_min_rounds: int = 3
    performance_regression_threshold: float = 5.0  # %

    # === Логирование ===
    log_level: str = "INFO"               # DEBUG, INFO, WARNING, ERROR
    log_format: str = "%(asctime)s | %(levelname)s | %(name)s | %(message)s"
    save_state_every_n_cycles: int = 5    # сохранять состояние каждые N циклов

    # === Симуляция ===
    random_seed: Optional[int] = None     # None = случайный, int = для воспроизводимости
    enable_deterministic_mode: bool = False

    # === Безопасность ===
    hard_stop_on_constitution_violation: bool = True
    max_change_risk_threshold: float = 0.05
    auto_rollback_on_failure: bool = True

    def __post_init__(self):
        """Создать директории после инициализации."""
        self.state_dir.mkdir(parents=True, exist_ok=True)

    @classmethod
    def default(cls) -> NaotoConfig:
        """Конфигурация по умолчанию."""
        return cls()

    @classmethod
    def demo(cls) -> NaotoConfig:
        """Демо-конфигурация для тестирования."""
        return cls(
            max_cycles=5,
            cycle_interval=2.0,
            analysis_interval=2,
            log_level="DEBUG",
            scan_directories=[
                ".", "hanako", "fuyuki", "lucy", "futaba",
                "shiori", "nobuka", "akva", "latislane",
                "celesta", "naoto", "yu", "scientists_network",
            ],
        )
