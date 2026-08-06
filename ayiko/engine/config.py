"""
Конфигурация системы Айко — творческий ИИ (пиксель-арт, графика, 3D).
"""

from __future__ import annotations
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional


@dataclass
class AyikoConfig:
    """
    Конфигурация творческого ИИ Айко.

    Айко специализируется на:
      - 🎨 Пиксель-арт (16x16 → 32K)
      - 📐 Техническая графика / чертежи
      - 🧊 3D-моделирование и рендер
      - 📸 Изучение референсов из папки ojidania
      - 🖼️ Генерация изображений (персонажи, пейзажи, сцены)
    """

    # === Идентификация ===
    name: str = "Айко"
    version: str = "v2.0.0"

    # === Пути к документам ===
    base_path: Path = Path("ayiko")
    constitution_path: Path = field(default_factory=lambda: Path("ayiko/constitution.md"))
    laws_path: Path = field(default_factory=lambda: Path("ayiko/laws/01-core-laws.md"))
    ethics_path: Path = field(default_factory=lambda: Path("ayiko/codes/01-ethics-code.md"))

    # === Состояние и логи ===
    state_dir: Path = field(default_factory=lambda: Path("ayiko/engine/state"))
    log_path: Path = field(default_factory=lambda: Path("ayiko/engine/state/ayiko.log"))
    state_path: Path = field(default_factory=lambda: Path("ayiko/engine/state/ayiko_state.json"))

    # === Циклы работы ===
    cycle_interval: float = 10.0          # секунды между циклами
    analysis_interval: int = 5            # каждые N циклов — анализ прогресса
    max_cycles: Optional[int] = None      # None = бесконечно, int = демо-режим

    # === Творчество: генерация изображений ===
    art_enabled: bool = True              # генерировать реальные изображения
    art_output_dir: Path = field(default_factory=lambda: Path("ayiko/engine/state/generated"))
    art_interval: int = 1                 # каждый цикл генерировать арт
    art_3d_interval: int = 5              # каждые N циклов — 3D-проект
    art_pixel_interval: int = 1           # каждый цикл — пиксель-арт
    art_technical_interval: int = 3       # каждые N циклов — техграфика
    default_image_size: tuple = (512, 512)

    # === Референсы (ojidania) ===
    references_dir: Path = field(default_factory=lambda: Path("ayiko/ojidania"))
    references_analysis_dir: Path = field(default_factory=lambda: Path("ayiko/engine/state/ojidania_analysis"))
    learn_references_interval: int = 10   # каждые N циклов изучать референсы

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
        self.art_output_dir.mkdir(parents=True, exist_ok=True)
        self.references_analysis_dir.mkdir(parents=True, exist_ok=True)

    @classmethod
    def default(cls) -> "AyikoConfig":
        """Конфигурация по умолчанию."""
        return cls()

    @classmethod
    def demo(cls) -> "AyikoConfig":
        """Демо-конфигурация для тестирования (5 циклов, быстро)."""
        return cls(
            max_cycles=5,
            cycle_interval=2.0,
            log_level="DEBUG",
        )
