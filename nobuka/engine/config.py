"""
Конфигурация системы Нобука.
"""

from __future__ import annotations
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional


@dataclass
class NobukaConfig:
    """
    Конфигурация системы улучшений Нобука.
    """

    # === Идентификация ===
    name: str = "Нобука"
    version: str = "v1.0.0"

    # === Пути к документам ===
    base_path: Path = Path("nobuka")
    constitution_path: Path = field(default_factory=lambda: Path("nobuka/constitution.md"))
    laws_path: Path = field(default_factory=lambda: Path("nobuka/laws/01-core-laws.md"))
    ethics_path: Path = field(default_factory=lambda: Path("nobuka/codes/01-ethics-code.md"))

    # === Состояние и логи ===
    state_dir: Path = field(default_factory=lambda: Path("nobuka/engine/state"))
    log_path: Path = field(default_factory=lambda: Path("nobuka/engine/state/nobuka.log"))
    state_path: Path = field(default_factory=lambda: Path("nobuka/engine/state/nobuka_state.json"))
    improvements_log_path: Path = field(default_factory=lambda: Path("nobuka/engine/state/improvements.json"))
    test_report_path: Path = field(default_factory=lambda: Path("nobuka/engine/state/test_report.json"))
    analysis_report_path: Path = field(default_factory=lambda: Path("nobuka/engine/state/analysis_report.json"))

    # === Циклы работы ===
    cycle_interval: float = 10.0          # секунды между циклами улучшений
    analysis_interval: int = 5            # каждые N циклов запускать анализ проекта
    max_cycles: Optional[int] = None      # None = бесконечно, int = демо-режим

    # === Автономность ===
    max_autonomy_level: str = "L3"        # L0-L4 (см. протокол саморазвития)
    require_confirmation_above: str = "L2"  # выше этого уровня — запрос подтверждения

    # === Интернет ===
    web_search_enabled: bool = True       # доступ к интернету
    web_search_interval: int = 5          # каждые N циклов веб-поиск
    max_search_results: int = 10          # максимум результатов поиска
    research_databases: list[str] = field(default_factory=lambda: [
        "code_quality",       # Качество кода
        "best_practices",     # Лучшие практики
        "refactoring",        # Рефакторинг
        "testing_strategies", # Стратегии тестирования
    ])

    # === Анализ кода ===
    project_root: Path = field(default_factory=lambda: Path("."))
    scan_directories: list[str] = field(default_factory=lambda: [
        ".",           # корневая папка (все .py файлы)
        "hanako",      # Ханако — гравитация
        "fuyuki",      # Фуюки — электричество
        "lucy",        # Люси — двигатели
        "futaba",      # Футаба — управление
        "shiori",      # Шиори — защита
        "nobuka",      # Нобука — улучшения
        "akva",        # Аква — математика, физика
        "latislane",   # Latislane — проектирование тел
        "celesta",     # Селеста — интимная жизнь
        "naoto",       # Наото — визуальный архитектор
        "yu",          # Юи — сознание, перенос
        "scientists_network",  # Scientists Network
    ])
    exclude_patterns: list[str] = field(default_factory=lambda: [
        "__pycache__", "*.pyc", ".git", "node_modules", "venv",
        "*.egg-info", "build", "dist", "*.egg",
        "android-studio-plugin",  # Android-проект, не Python
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

    # === Итеративная доработка (Закон 1: рабочий код) ===
    # Сколько попыток доработать код, если тесты не прошли.
    # Нобука не выбрасывает код при первой неудаче — она чинит его.
    max_fix_attempts: int = 3

    # === Взаимодействие с сёстрами ===
    notify_futaba_on_logic_change: bool = True
    notify_shiori_on_security_change: bool = True
    scan_with_shiori_before_apply: bool = True

    # === Мониторинг логов приложения (main.py / TimeWeb) ===
    app_log_monitoring_enabled: bool = True       # читать логи приложения в цикле
    app_log_path: Optional[Path] = None           # явный путь к app.log (если None — автопоиск)
    # Типичные места расположения логов приложения (в т.ч. на TimeWeb)
    app_log_candidates: list[Path] = field(default_factory=lambda: [
        Path("logs/app.log"),                                  # локальная разработка / контейнер
        Path("~/.local/logs/app.log"),                         # Linux home
        Path("~/logs/app.log"),                                # TimeWeb: домашняя директория
        Path("/var/log/app.log"),                              # системные логи
        Path("/var/www/logs/app.log"),                         # TimeWeb: веб-папки
        Path("/opt/pantikur/logs/app.log"),                    # серверные установки
    ])
    app_log_tail_lines: int = 200                  # сколько строк читать при первом запуске
    app_log_offset_state: Path = field(default_factory=lambda: Path("nobuka/engine/state/app_log_offset.json"))

    # === Поиск и исправление реальных ошибок ===
    error_fixer_enabled: bool = True               # включить ErrorFixer
    error_scan_limit: int = 200                    # макс. файлов за одно сканирование
    error_fix_auto_apply: bool = True              # автоматически применять правки
    error_fix_max_per_cycle: int = 5               # макс. исправлений за цикл
    error_fix_backup_dir: Path = field(default_factory=lambda: Path("nobuka/engine/state/error_fix_backups"))

    def __post_init__(self):
        """Создать директории после инициализации."""
        self.state_dir.mkdir(parents=True, exist_ok=True)
        self.error_fix_backup_dir.mkdir(parents=True, exist_ok=True)

    @classmethod
    def default(cls) -> NobukaConfig:
        """Конфигурация по умолчанию."""
        return cls()

    @classmethod
    def demo(cls) -> NobukaConfig:
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
