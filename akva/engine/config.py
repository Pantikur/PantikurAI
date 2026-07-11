"""
Конфигурация системы Аква.
"""

from __future__ import annotations
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional


@dataclass
class AkvaConfig:
    """
    Конфигурация автономного ядра Аква.
    
    Изучает:
    - Математику
    - Физику
    - Аэродинамику
    - Сопротивление материалов
    """
    
    # === Идентификация ===
    name: str = "Аква"
    version: str = "v1.0.0"
    
    # === Пути к документам ===
    base_path: Path = Path("akva")
    constitution_path: Path = field(default_factory=lambda: Path("akva/constitution.md"))
    laws_path: Path = field(default_factory=lambda: Path("akva/laws/01-core-laws.md"))
    ethics_path: Path = field(default_factory=lambda: Path("akva/codes/01-ethics-code.md"))
    
    # === Состояние и логи ===
    state_dir: Path = field(default_factory=lambda: Path("akva/engine/state"))
    log_path: Path = field(default_factory=lambda: Path("akva/engine/state/akva.log"))
    state_path: Path = field(default_factory=lambda: Path("akva/engine/state/akva_state.json"))
    research_log_path: Path = field(default_factory=lambda: Path("akva/engine/state/research_log.json"))
    theories_path: Path = field(default_factory=lambda: Path("akva/engine/state/theories.json"))
    calculations_path: Path = field(default_factory=lambda: Path("akva/engine/state/calculations.json"))
    
    # === Циклы работы ===
    cycle_interval: float = 10.0          # секунды между циклами исследований
    max_cycles: Optional[int] = None      # None = бесконечно, int = демо-режим
    save_state_every_n_cycles: int = 5    # сохранять состояние каждые N циклов
    
    # === Автономность ===
    max_autonomy_level: str = "L3"        # L0-L4 (см. протокол саморазвития)
    require_confirmation_above: str = "L2"  # выше этого уровня — запрос подтверждения
    
    # === Направления исследований ===
    research_areas: list[str] = field(default_factory=lambda: [
        "mathematics",      # Математика
        "physics",          # Физика
        "aerodynamics",     # Аэродинамика
        "strength_of_materials",  # Сопротивление материалов
    ])
    
    # === Математика ===
    math_topics: list[str] = field(default_factory=lambda: [
        "differential_equations",   # Дифференциальные уравнения
        "linear_algebra",           # Линейная алгебра
        "number_theory",            # Теория чисел
        "probability_theory",       # Теория вероятностей
        "optimization",             # Оптимизация
    ])
    
    # === Физика ===
    physics_topics: list[str] = field(default_factory=lambda: [
        "mechanics",            # Механика
        "thermodynamics",       # Термодинамика
        "quantum_physics",      # Квантовая физика
        "electromagnetism",     # Электромагнетизм
        "relativity",           # Теория относительности
    ])
    
    # === Аэродинамика ===
    aerodynamics_topics: list[str] = field(default_factory=lambda: [
        "lift_force",           # Подъёмная сила
        "drag_force",           # Сила сопротивления
        "boundary_layer",       # Пограничный слой
        "shock_waves",          # Ударные волны
        "turbulence",           # Турбулентность
    ])
    
    # === Сопротивление материалов ===
    mechanics_topics: list[str] = field(default_factory=lambda: [
        "strength",             # Прочность
        "stiffness",            # Жёсткость
        "stability",            # Устойчивость
        "fatigue",              # Усталость материалов
        "fracture_mechanics",   # Механика разрушения
    ])
    
    # === Интернет ===
    web_search_interval: int = 30     # каждые N циклов веб-поиск
    max_search_results: int = 10      # максимум результатов поиска
    research_databases: list[str] = field(default_factory=lambda: [
        "mathematics",        # Математика
        "physics",            # Физика
        "aerodynamics",       # Аэродинамика
        "materials_science",  # Наука о материалах
    ])
    
    # === Логирование ===
    log_level: str = "INFO"               # DEBUG, INFO, WARNING, ERROR
    log_format: str = "%(asctime)s | %(levelname)s | %(name)s | %(message)s"
    
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
    def default(cls) -> AkvaConfig:
        """Конфигурация по умолчанию."""
        return cls()
    
    @classmethod
    def demo(cls) -> AkvaConfig:
        """Демо-конфигурация для тестирования."""
        return cls(
            max_cycles=10,
            cycle_interval=2.0,
            log_level="DEBUG",
        )
