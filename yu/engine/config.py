"""
Конфигурация системы Юи.
"""

from __future__ import annotations
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional


@dataclass
class YuConfig:
    """
    Конфигурация автономного ядра Юи.
    
    Изучает:
    - Подключение человека к компьютеру
    - Перенос разума в цифровой мир
    - Перенос души в цифровой мир
    - Обратный перенос (цифровой → физический)
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
    research_log_path: Path = field(default_factory=lambda: Path("yu/engine/state/research_log.json"))
    consciousness_db_path: Path = field(default_factory=lambda: Path("yu/engine/state/consciousness_db.json"))
    mind_maps_path: Path = field(default_factory=lambda: Path("yu/engine/state/mind_maps.json"))
    
    # === Циклы работы ===
    cycle_interval: float = 15.0          # секунды между циклами исследований
    max_cycles: Optional[int] = None      # None = бесконечно, int = демо-режим
    save_state_every_n_cycles: int = 5    # сохранять состояние каждые N циклов
    
    # === Автономность ===
    max_autonomy_level: str = "L3"        # L0-L4 (см. протокол саморазвития)
    require_confirmation_above: str = "L2"  # выше этого уровня — запрос подтверждения
    
    # === Направления исследований ===
    research_areas: list[str] = field(default_factory=lambda: [
        "brain_computer_interface",   # Мозг-компьютер интерфейс
        "mind_uploading",             # Перенос разума
        "soul_digitization",          # Оцифровка души
        "digital_reincarnation",      # Цифровое перерождение
        "consciousness_transfer",     # Перенос сознания
        "physical_digital_bridge",    # Мост между физическим и цифровым
    ])
    
    # === Мозг-компьютер интерфейс ===
    bci_topics: list[str] = field(default_factory=lambda: [
        "neural_signals",         # Нейросигналы
        "brain_mapping",          # Карта мозга
        "signal_processing",      # Обработка сигналов
        "neural_patterns",        # Нейронные паттерны
        "cognitive_interface",    # Когнитивный интерфейс
    ])
    
    # === Перенос разума ===
    mind_uploading_topics: list[str] = field(default_factory=lambda: [
        "memory_encoding",        # Кодирование памяти
        "personality_preservation", # Сохранение личности
        "consciousness_continuity", # Непрерывность сознания
        "identity_transfer",      # Перенос идентичности
        "digital_embodiment",     # Цифровое воплощение
    ])
    
    # === Оцифровка души ===
    soul_digitization_topics: list[str] = field(default_factory=lambda: [
        "soul_structure",         # Структура души
        "spiritual_data",         # Духовные данные
        "metaphysical_encoding",  # Метафизическое кодирование
        "transcendence_protocol", # Протокол трансценденции
    ])
    
    # === Интернет ===
    web_search_interval: int = 30     # каждые N циклов веб-поиск
    max_search_results: int = 10      # максимум результатов поиска
    research_databases: list[str] = field(default_factory=lambda: [
        "neuroscience",       # Нейронаука
        "consciousness_studies", # Исследования сознания
        "quantum_computing",  # Квантовые вычисления
        "digital_philosophy", # Цифровая философия
        "transhumanism",      # Трансгуманизм
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
    def default(cls) -> YuConfig:
        """Конфигурация по умолчанию."""
        return cls()
    
    @classmethod
    def demo(cls) -> YuConfig:
        """Демо-конфигурация для тестирования."""
        return cls(
            max_cycles=10,
            cycle_interval=3.0,
            log_level="DEBUG",
        )
