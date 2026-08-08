"""
Конфигурация системы Кристи — режиссёр видеопроизводства.
"""

from __future__ import annotations
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional


@dataclass
class KristiConfig:
    """
    Конфигурация режиссёра видеопроизводства Кристи.

    Кристи специализируется на:
      - 🎬 Управление созданием видео (полный цикл)
      - 📋 Сценарии и раскадровки
      - 🎭 Режиссура и постановка
      - ✂️ Монтаж и постпродакшн
      - 🎵 Звуковой дизайн
      - 🎞️ Анимация для видео
    """

    # === Идентификация ===
    name: str = "Кристи"
    version: str = "v1.0.0"

    # === Пути к документам ===
    base_path: Path = Path("kristi")
    constitution_path: Path = field(default_factory=lambda: Path("kristi/constitution.md"))
    laws_path: Path = field(default_factory=lambda: Path("kristi/laws/01-core-laws.md"))
    ethics_path: Path = field(default_factory=lambda: Path("kristi/codes/01-ethics-code.md"))

    # === Состояние и логи ===
    state_dir: Path = field(default_factory=lambda: Path("kristi/engine/state"))
    log_path: Path = field(default_factory=lambda: Path("kristi/engine/state/kristi.log"))
    state_path: Path = field(default_factory=lambda: Path("kristi/engine/state/kristi_state.json"))

    # === Циклы работы ===
    cycle_interval: float = 10.0          # секунды между циклами
    analysis_interval: int = 5            # каждые N циклов — анализ прогресса
    max_cycles: Optional[int] = None      # None = бесконечно, int = демо-режим

    # === Производство видео ===
    production_enabled: bool = True       # производство видео
    production_output_dir: Path = field(default_factory=lambda: Path("kristi/engine/state/productions"))
    production_interval: int = 1          # каждый цикл — этап производства
    script_interval: int = 2            # каждые N циклов — новый сценарий
    storyboard_interval: int = 3        # каждые N циклов — раскадровка
    edit_interval: int = 2              # каждые N циклов — монтаж
    animation_interval: int = 4         # каждые N циклов — анимация

    # === Координация с Айка ===
    aika_integration: bool = True        # интеграция с Айка
    aika_references_interval: int = 5    # каждые N циклов — запрос референсов
    aika_assets_dir: Path = field(default_factory=lambda: Path("ayiko/ojidania"))

    # === Интернет ===
    web_search_enabled: bool = True       # доступ к интернету
    web_search_interval: int = 7          # каждые N циклов веб-поиск

    # === Взаимодействие с сёстрами ===
    interact_with_sisters_interval: int = 10
    self_improve_interval: int = 20

    # === Логирование ===
    log_level: str = "INFO"               # DEBUG, INFO, WARNING, ERROR
    log_format: str = "%(asctime)s | %(levelname)s | %(name)s | %(message)s"
    save_state_every_n_cycles: int = 5    # сохранять состояние каждые N циклов

    # === Симуляция ===
    random_seed: Optional[int] = None     # None = случайный, int = для воспроизводимости

    def __post_init__(self):
        """Создать директории после инициализации."""
        self.state_dir.mkdir(parents=True, exist_ok=True)
        self.production_output_dir.mkdir(parents=True, exist_ok=True)

    @classmethod
    def default(cls) -> "KristiConfig":
        """Конфигурация по умолчанию."""
        return cls()

    @classmethod
    def demo(cls) -> "KristiConfig":
        """Демо-конфигурация для тестирования (5 циклов, быстро)."""
        return cls(
            max_cycles=5,
            cycle_interval=2.0,
            log_level="DEBUG",
        )
