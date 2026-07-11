"""
Конфигурация системы Шиори.
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
    parent_system: str = "Вугларст"  # Нейросеть, которую защищает Шиори
    
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
    
    # === Циклы работы ===
    cycle_interval: float = 3.0          # секунды между циклами защиты
    scan_interval: int = 5               # каждые N циклов полное сканирование
    max_cycles: Optional[int] = None     # None = бесконечно, int = демо-режим
    
    # === Автономность ===
    max_autonomy_level: str = "L3"       # L0-L4 (см. протокол защиты)
    require_confirmation_above: str = "L2"  # выше этого уровня — запрос подтверждения
    
    # === Интернет ===
    web_search_enabled: bool = True      # доступ к интернету
    web_search_interval: int = 5         # каждые N циклов веб-поиск
    max_search_results: int = 10         # максимум результатов поиска
    research_databases: list[str] = field(default_factory=lambda: [
        "cybersecurity",      # Кибербезопасность
        "threat_intelligence", # Разведка угроз
        "vulnerability_db",   # База уязвимостей
        "patch_management",   # Управление патчами
    ])
    
    # === Сканирование угроз ===
    threat_scan_interval: int = 10       # секунд между сканированиями
    max_threats_per_scan: int = 100      # максимум угроз за одно сканирование
    threat_database_path: Path = field(default_factory=lambda: Path("shiori/engine/state/threat_db.json"))
    
    # === Патчи и восстановление ===
    auto_patch_enabled: bool = True      # автоматическое применение патчей
    backup_before_patch: bool = True     # создавать резервную копию перед патчем
    rollback_on_failure: bool = True     # откат при неудачном патче
    max_patch_attempts: int = 3          # максимум попыток применения патча
    
    # === Логирование ===
    log_level: str = "INFO"              # DEBUG, INFO, WARNING, ERROR
    log_format: str = "%(asctime)s | %(levelname)s | %(name)s | %(message)s"
    save_state_every_n_cycles: int = 5   # сохранять состояние каждые N циклов
    
    # === Симуляция ===
    random_seed: Optional[int] = None    # None = случайный, int = для воспроизводимости
    enable_deterministic_mode: bool = False  # если True, использовать random_seed всегда
    
    # === Безопасность ===
    hard_stop_on_critical_threat: bool = True  # остановка при критической угрозе
    quarantine_enabled: bool = True      # изоляция подозрительных файлов
    encryption_enabled: bool = True      # шифрование данных
    
    # === Реагирование ===
    auto_block_enabled: bool = True      # автоматическая блокировка угроз
    alert_threshold: str = "L2"          # порог для алертов (L0-L4)
    notification_enabled: bool = True    # уведомления о инцидентах
    
    def __post_init__(self):
        """Создать директории после инициализации."""
        self.state_dir.mkdir(parents=True, exist_ok=True)
    
    @classmethod
    def default(cls) -> ShioriConfig:
        """Конфигурация по умолчанию."""
        return cls()
    
    @classmethod
    def demo(cls) -> ShioriConfig:
        """Демо-конфигурация для тестирования (ограниченные циклы)."""
        return cls(
            max_cycles=5,
            cycle_interval=1.0,
            scan_interval=2,
            threat_scan_interval=2,
            log_level="DEBUG"
        )
