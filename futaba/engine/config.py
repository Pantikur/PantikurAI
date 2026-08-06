"""
Конфигурация системы Футаба — управление, правовые исследования, саморазвитие.
"""

from __future__ import annotations
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional


@dataclass
class FutabaConfig:
    """
    Конфигурация системы управления и правовых исследований Футаба.
    """

    # === Идентификация ===
    name: str = "Футаба"
    version: str = "v2.0.0"
    role: str = "Главный заместитель Разработчика"  # Главзам

    # === Пути к документам ===
    base_path: Path = Path("futaba")
    constitution_path: Path = field(default_factory=lambda: Path("futaba/constitution.md"))
    laws_path: Path = field(default_factory=lambda: Path("futaba/laws/01-core-laws.md"))
    ethics_path: Path = field(default_factory=lambda: Path("futaba/codes/01-ethics-code.md"))

    # === Состояние и логи ===
    state_dir: Path = field(default_factory=lambda: Path("futaba/engine/state"))
    log_path: Path = field(default_factory=lambda: Path("futaba/engine/state/futaba.log"))
    state_path: Path = field(default_factory=lambda: Path("futaba/engine/state/futaba_state.json"))
    knowledge_journal_path: Path = field(default_factory=lambda: Path("futaba/engine/state/knowledge_journal.json"))
    character_path: Path = field(default_factory=lambda: Path("futaba/engine/state/my_character.yaml"))
    reports_path: Path = field(default_factory=lambda: Path("futaba/engine/state/reports.json"))
    legal_documents_path: Path = field(default_factory=lambda: Path("futaba/engine/state/legal_documents.json"))
    trials_log_path: Path = field(default_factory=lambda: Path("futaba/engine/state/trials_log.json"))

    # === Циклы работы ===
    cycle_interval: float = 10.0          # секунды между циклами управления
    development_interval: int = 3         # каждые N циклов — саморазвитие
    legal_interval: int = 5               # каждые N циклов — правовые исследования
    web_interval: int = 3                 # каждые N циклов — интернет-поиск
    report_interval: int = 10             # каждые N циклов — отчёт
    max_cycles: Optional[int] = None      # None = бесконечно, int = демо-режим

    # === Автономность ===
    max_autonomy_level: str = "L2"        # L0-L4 (см. протокол управления)
    require_confirmation_above: str = "L2"  # выше этого уровня — запрос подтверждения

    # === Интернет ===
    web_search_enabled: bool = True       # доступ к интернету для саморазвития
    web_search_interval: int = 3          # каждые N циклов веб-поиск
    max_search_results: int = 15          # максимум результатов поиска
    research_topics: list[str] = field(default_factory=lambda: [
        "legal_ai",           # Правовое регулирование ИИ
        "copyright_law",      # Авторское право
        "project_management", # Управление проектами
        "best_practices",     # Лучшие практики
        "self_development",   # Саморазвитие
        "leadership",         # Лидерство и управление
    ])

    # === Правовые исследования ===
    legal_research_enabled: bool = True   # изучение всех отраслей права
    jurisdictions: list[str] = field(default_factory=lambda: [
        "russia",       # Российская Федерация
        "eu",           # Европейский Союз
        "us",           # США
        "international", # Международное право
    ])
    law_branches_to_study: list[str] = field(default_factory=lambda: [
        "constitutional",    # Конституционное
        "civil",             # Гражданское
        "criminal",          # Уголовное
        "labor",             # Трудовое
        "administrative",    # Административное
        "family",            # Семейное
        "tax",               # Налоговое
        "corporate",         # Корпоративное
        "environmental",     # Экологическое
        "international",     # Международное
        "financial",         # Финансовое
        "information",       # Информационное
        "social",            # Социальное
        "ai_regulation",     # Регулирование ИИ
    ])

    # === Саморазвитие ===
    self_development_enabled: bool = True  # автономное развитие
    knowledge_levels: list[str] = field(default_factory=lambda: [
        "novice",      # L1 — Базовые знания
        "intermediate", # L2 — Уверенное владение
        "advanced",    # L3 — Глубокое понимание
        "expert",      # L4 — Экспертный уровень
        "master",      # L5 — Полное владение
    ])
    current_knowledge_level: str = "intermediate"
    learning_rate: float = 0.1            # скорость изучения нового
    max_topics_studied: int = 1000        # максимум тем в журнале

    # === Управление девочками ===
    girls_to_manage: list[str] = field(default_factory=lambda: [
        "nobuka",       # Нобука — улучшения
        "shiori",       # Шиори — защита
        "hanako",       # Ханако — гравитация
        "fuyuki",       # Фуюки — электричество
        "lucy",         # Люси — двигатели
        "akva",         # Аква — математика, физика
        "latislane",    # Latislane — проектирование
        "celesta",      # Селеста — интимная жизнь
        "naoto",        # Наото — визуальный архитектор
        "yu",           # Юи — сознание
    ])
    communication_interval: int = 5       # каждые N циклов — общение с девочками
    report_to_developer: bool = True      # отчёты Разработчику

    # === Логирование ===
    log_level: str = "INFO"               # DEBUG, INFO, WARNING, ERROR
    log_format: str = "%(asctime)s | %(levelname)s | %(name)s | %(message)s"
    save_state_every_n_cycles: int = 5    # сохранять состояние каждые N циклов

    # === Симуляция ===
    random_seed: Optional[int] = None     # None = случайный, int = для воспроизводимости
    enable_deterministic_mode: bool = False

    # === Полигон испытаний ===
    trial_interval: int = 10              # каждые N циклов запускать полигон
    trial_worlds_per_batch: int = 3       # миров заbatch
    trial_versions_to_test: int = 5       # версий правления на мир
    trial_epochs_per_world: int = 20      # эпох на мир

    # === Безопасность ===
    hard_stop_on_constitution_violation: bool = True
    max_change_risk_threshold: float = 0.05
    auto_rollback_on_failure: bool = True

    def __post_init__(self):
        """Создать директории после инициализации."""
        self.state_dir.mkdir(parents=True, exist_ok=True)

    @classmethod
    def default(cls) -> FutabaConfig:
        """Конфигурация по умолчанию."""
        return cls()

    @classmethod
    def demo(cls) -> FutabaConfig:
        """Демо-конфигурация для тестирования."""
        return cls(
            max_cycles=5,
            cycle_interval=2.0,
            development_interval=1,
            legal_interval=1,
            web_interval=1,
            log_level="DEBUG",
        )
