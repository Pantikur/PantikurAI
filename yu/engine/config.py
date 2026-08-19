"""
Конфигурация системы Юи — изучения сознания, души и разума.
"""

from __future__ import annotations
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional


@dataclass
class YuConfig:
    """
    Конфигурация системы изучения сознания Юи.
    """

    # === Идентификация ===
    name: str = "Юи"
    version: str = "v1.0.0"

    # === Пути к документам ===
    base_path: Path = Path("yu")
    constitution_path: Path = field(default_factory=lambda: Path("yu/constitution.md"))
    laws_path: Path = field(default_factory=lambda: Path("yu/laws/01-core-laws.md"))
    ethics_path: Path = field(default_factory=lambda: Path("yu/codes/01-ethics-code.md"))

    # === Состояние и логи ===
    state_dir: Path = field(default_factory=lambda: Path("yu/engine/state"))
    log_path: Path = field(default_factory=lambda: Path("yu/engine/state/yu.log"))
    state_path: Path = field(default_factory=lambda: Path("yu/engine/state/yu_state.json"))
    analysis_report_path: Path = field(default_factory=lambda: Path("yu/engine/state/analysis_report.json"))

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
    
    # === LLM ===
    llm_enabled: bool = True              # вкл/выкл LLM
    general_model_path: str = "models/Qwen2.5-3B-Instruct"
    coder_model_path: str = "models/Qwen2.5-Coder-3B-Instruct"

    # === Симуляция ===
    random_seed: Optional[int] = None
    enable_deterministic_mode: bool = False

    # === Безопасность ===
    hard_stop_on_constitution_violation: bool = True

    # === Взаимодействие с сёстрами ===
    notify_futaba_on_change: bool = True
    notify_shiori_on_security_change: bool = True

    def __post_init__(self):
        self.state_dir.mkdir(parents=True, exist_ok=True)

    @classmethod
    def default(cls) -> YuConfig:
        return cls()

    @classmethod
    def demo(cls) -> YuConfig:
        return cls(
            max_cycles=5,
            cycle_interval=2.0,
            analysis_interval=2,
            log_level="DEBUG",
        )
