"""
Конфигурация системы Шиори — автономной иммунной системы защиты.
"""

from __future__ import annotations
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional


@dataclass
class ShioriConfig:
    """
    Конфигурация автономной иммунной системы Шиори.
    """

    # === Идентификация ===
    name: str = "Шиори"
    version: str = "v1.0.0"
    parent_system: str = "Вугларст"

    # === Пути к документам ===
    base_path: Path = Path("shiori")
    constitution_path: Path = field(default_factory=lambda: Path("shiori/constitution.md"))
    laws_path: Path = field(default_factory=lambda: Path("shiori/laws/01-core-laws.md"))
    ethics_path: Path = field(default_factory=lambda: Path("shiori/codes/01-ethics-code.md"))

    # === Состояние и логи ===
    state_dir: Path = field(default_factory=lambda: Path("shiori/engine/state"))
    log_path: Path = field(default_factory=lambda: Path("shiori/engine/state/shiori.log"))
    state_path: Path = field(default_factory=lambda: Path("shiori/engine/state/shiori_state.json"))
    threats_log_path: Path = field(default_factory=lambda: Path("shiori/engine/state/threats.json"))
    incidents_log_path: Path = field(default_factory=lambda: Path("shiori/engine/state/incidents.json"))
    web_cache_path: Path = field(default_factory=lambda: Path("shiori/engine/state/web_cache.json"))
    knowledge_base_path: Path = field(default_factory=lambda: Path("shiori/engine/state/knowledge_base.json"))
    reports_path: Path = field(default_factory=lambda: Path("shiori/engine/state/reports"))

    # === Циклы работы ===
    cycle_interval: float = 10.0          # секунды между циклами защиты
    scan_interval: int = 3                # каждые N циклов сканировать систему
    max_cycles: Optional[int] = None      # None = бесконечно, int = демо-режим

    # === Автономность ===
    max_autonomy_level: str = "L3"        # L0-L3 (L4 запрещён)
    require_confirmation_above: str = "L3"  # выше L3 — запрос подтверждения

    # === Интернет ===
    web_access_enabled: bool = True       # доступ к интернету для изучения угроз
    web_access_interval: int = 5          # каждые N циклов веб-поиск
    max_search_results: int = 10          # максимум результатов поиска
    research_topics: list[str] = field(default_factory=lambda: [
        "cve_vulnerabilities",     # CVE уязвимости
        "new_attack_methods",      # Новые методы атак
        "security_best_practices", # Лучшие практики защиты
        "threat_intelligence",     # Разведка угроз
        "exploit_analysis",        # Анализ эксплойтов
        "ransomware_tactics",      # Тактики ransomware
        "apt_tactics",             # Тактики APT
    ])

    # === Сканирование ===
    scan_directories: list[str] = field(default_factory=lambda: [
        ".",           # корневая папка
        "hanako",      # Ханако — гравитация
        "fuyuki",      # Фуюки — электричество
        "lucy",        # Люси — двигатели
        "futaba",      # Футаба — управление
        "shiori",      # Шиори — защита
        "nobuka",      # Нобука — улучшения
        "akva",        # Аква — математика
        "latislane",   # Latislane — проектирование
        "celesta",     # Селеста — интимная жизнь
        "naoto",       # Наото — визуальный архитектор
        "yu",          # Юи — сознание
        "scientists_network",  # Scientists Network
    ])
    exclude_patterns: list[str] = field(default_factory=lambda: [
        "__pycache__", "*.pyc", ".git", "node_modules", "venv",
        "*.egg-info", "build", "dist", "*.egg",
        "android-studio-plugin",
    ])

    # === Реагирование на угрозы ===
    auto_block_on_l3: bool = True         # авто-блокировка на L3+
    auto_block_on_l4: bool = True         # авто-блокировка на L4+
    auto_block_on_l5: bool = True         # авто-блокировка на L5+
    quarantine_enabled: bool = True       # карантин файлов
    quarantine_days: int = 30             # дни хранения карантина
    alert_on_l4: bool = True              # алерт разработчику на L4+
    alert_on_l5: bool = True              # алерт на L5+
    alert_targets: list[str] = field(default_factory=lambda: [
        "futaba", "developer"
    ])

    # === Патчи ===
    auto_patch_enabled: bool = True       # автоприменение патчей
    backup_before_patch: bool = True      # бэкап перед патчем
    rollback_on_failure: bool = True      # откат при неудаче
    backup_dir: Path = field(default_factory=lambda: Path("shiori/engine/state/backups"))

    # === Логирование ===
    log_level: str = "INFO"               # DEBUG, INFO, WARNING, ERROR
    log_format: str = "%(asctime)s | %(levelname)s | %(name)s | %(message)s"
    save_state_every_n_cycles: int = 5    # сохранять состояние каждые N циклов

    # === Симуляция ===
    random_seed: Optional[int] = None     # None = случайный, int = для воспроизводимости
    enable_deterministic_mode: bool = False

    # === LLM Модели ===
    general_model_path: str = "models/qwen2.5-3b"           # Путь/название для общих целей
    coder_model_path: str = "models/qwen2.5-coder-3b"        # Путь/название для кода
    model_device: str = "auto"                        # cpu, cuda, auto
    model_max_tokens: int = 1024                      # Максимальная длина ответа
    model_temperature: float = 0.7                    # Температура генерации
    model_use_flash_attention: bool = False           # Использовать Flash Attention
    llm_enabled: bool = True                          # Включить LLM

    # === Безопасность ===
    hard_stop_on_constitution_violation: bool = True
    protect_developer: bool = True        # никогда не блокировать разработчика
    protect_futaba: bool = True           # никогда не блокировать Футабу
    protect_sisters: bool = True          # никогда не блокировать сестёр

    # === Взаимодействие с сёстрами ===
    report_to_futaba: bool = True         # отчитываться Футабе
    report_to_developer: bool = True      # отчитываться разработчику
    interact_with_sisters: bool = True    # общаться с сёстрами

    def __post_init__(self):
        """Создать директории после инициализации."""
        self.state_dir.mkdir(parents=True, exist_ok=True)
        self.backup_dir.mkdir(parents=True, exist_ok=True)
        self.reports_path.mkdir(parents=True, exist_ok=True)

    @classmethod
    def default(cls) -> ShioriConfig:
        """Конфигурация по умолчанию."""
        return cls()

    @classmethod
    def demo(cls) -> ShioriConfig:
        """Демо-конфигурация для тестирования."""
        return cls(
            max_cycles=5,
            cycle_interval=2.0,
            log_level="DEBUG",
            scan_directories=[".", "hanako", "fuyuki", "lucy", "futaba", "shiori", "nobuka"],
        )
