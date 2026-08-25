# services/service_init.py — Инициализация модулей (Latislane, Celesta, ResearchMonitor)

import sys
import logging
from pathlib import Path
from config import (
    BASE_DIR,
    LATISLANE_ENABLED,
    CELESTA_ENABLED,
    RESEARCH_MONITOR_ENABLED,
)

logger = logging.getLogger("service_init")

# === Глобальные ссылки ===
_latislane_ref: list = [None]
_celesta_ref: list = [None]
_research_monitor_ref: list = [None]

_latislane_lock = None
_celesta_lock = None
_research_monitor_lock = None


def init_latislane():
    """Инициализирует LatislaneCore."""
    global _latislane_lock
    if not LATISLANE_ENABLED:
        logger.info("🧬 Latislane: пропуск (отключён)")
        return None

    _latislane_lock = __import__("threading", fromlist=["Lock"]).Lock()

    try:
        sys.path.insert(0, str(BASE_DIR))
        from latislane import LatislaneCore
        core = LatislaneCore(project_root=str(BASE_DIR), demo_mode=True)
        _latislane_ref[0] = core  # type: ignore[index]
        logger.info("🧬 Latislane инициализирован")
        return core
    except Exception as e:
        logger.warning(f"⚠️ Latislane не загружен: {e}")
        return None


def init_celesta():
    """Инициализирует CelestaCore."""
    global _celesta_lock
    if not CELESTA_ENABLED:
        logger.info("🌹 Celesta: пропуск (отключена)")
        return None

    _celesta_lock = __import__("threading", fromlist=["Lock"]).Lock()

    try:
        sys.path.insert(0, str(BASE_DIR))
        from celesta import CelestaCore
        core = CelestaCore(project_root=str(BASE_DIR), demo_mode=True)
        _celesta_ref[0] = core  # type: ignore[index]
        logger.info("🌹 Celesta инициализирована")
        return core
    except Exception as e:
        logger.warning(f"⚠️ Celesta не загружена: {e}")
        return None


def init_research_monitor():
    """Инициализирует ResearchMonitor."""
    global _research_monitor_lock
    if not RESEARCH_MONITOR_ENABLED:
        logger.info("🔬 ResearchMonitor: пропуск (отключён)")
        return None

    _research_monitor_lock = __import__("threading", fromlist=["Lock"]).Lock()

    try:
        sys.path.insert(0, str(BASE_DIR))
        from scientists_network.research_monitor import ResearchMonitor
        monitor = ResearchMonitor()
        monitor.initialize()
        _research_monitor_ref[0] = monitor  # type: ignore[index]
        logger.info("🔬 ResearchMonitor инициализирован")
        return monitor
    except Exception as e:
        logger.warning(f"⚠️ ResearchMonitor не загружен: {e}")
        return None


def get_latislane():
    return _latislane_ref[0]


def get_celesta():
    return _celesta_ref[0]


def get_research_monitor():
    return _research_monitor_ref[0]


def get_latislane_lock():
    return _latislane_lock


def get_celesta_lock():
    return _celesta_lock


def get_research_monitor_lock():
    return _research_monitor_lock
