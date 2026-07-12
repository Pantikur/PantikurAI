"""
Конфигурация Наото — Визуального Архитектора.
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict, List, Optional


@dataclass
class NaotoConfig:
    """Конфигурация Наото."""
    
    # Основные настройки
    name: str = "Наото"
    version: str = "1.0.0"
    role: str = "visual_architect"
    
    # Настройки мониторинга
    monitoring_enabled: bool = True
    monitoring_interval_hours: int = 24
    monitored_platforms: List[str] = field(default_factory=lambda: [
        "artstation",
        "behance",
        "blenderartists",
        "deviantart",
        "github",
        "youtube"
    ])
    
    # Настройки самообучения
    self_learning_enabled: bool = True
    learning_cycle_interval: int = 12  # часов
    max_knowledge_entries: int = 10000
    
    # Настройки интернета
    web_access_enabled: bool = True
    max_references_per_search: int = 5
    web_cache_enabled: bool = True
    user_agent: str = "Naoto/1.0 (Visual Architect for Vugarst Neural Network)"
    
    # Настройки автономности
    autonomy_enabled: bool = True
    default_autonomy_level: str = "full"  # full, partial, minimal
    quality_threshold: float = 0.7  # минимальный порог качества
    
    # Настройки коммуникации
    communication_enabled: bool = True
    scientists_network_enabled: bool = True
    sister_names: List[str] = field(default_factory=lambda: [
        "Футаба",      # Система управления
        "Фуюки",       # Электричество
        "Люси",        # Инженерия, двигатели
        "Ханако",      # Гравитация
        "Шиори",       # Защита
        "Нобука",      # Код, улучшения
        "Аква",        # Математика, физика, аэродинамика
        "Селеста",     # Биология, физиология
        "Latislane",   # Проектирование тел
        "Юи"           # Сознание, перенос разума, оцифровка души
    ])
    
    # Настройки визуализации
    sketch_styles: List[str] = field(default_factory=lambda: [
        "freehand",
        "technical",
        "concept",
        "minimalist",
        "detailed"
    ])
    
    drawing_standards: List[str] = field(default_factory=lambda: [
        "iso",
        "gost",
        "ansi",
        "din"
    ])
    
    model_detail_levels: List[str] = field(default_factory=lambda: [
        "low",
        "mid",
        "high",
        "architectural"
    ])
    
    # Пути
    knowledge_dir: str = "naoto/knowledge"
    state_dir: str = "naoto/engine/state"
    logs_dir: str = "naoto/engine/logs"
    
    # Логирование
    log_level: str = "INFO"
    log_file: str = "naoto/engine/logs/naoto.log"
