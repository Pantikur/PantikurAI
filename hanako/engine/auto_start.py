"""
Система автозапуска Ханако.
"""

from __future__ import annotations

import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Optional

from hanako.engine.config import HanakoConfig


class AutoStartSystem:
    """
    Система автозапуска и автономной работы Ханако.
    
    Функции:
    - Регистрация автозапуска
    - Отслеживание времени работы
    - Восстановление после перезапуска
    - Управление фоновой работой
    """

    def __init__(self, config: HanakoConfig):
        self.config = config
        self.logger = logging.getLogger("AutoStartSystem")
        self.registry_path = config.state_dir / "auto_start.json"
        self._data = self._load_data()

    def register_running(self):
        """Зарегистрировать запуск."""
        self._data["last_start"] = datetime.now().isoformat()
        self._data["is_running"] = True
        self._data["start_count"] = self._data.get("start_count", 0) + 1
        self._save_data()
        self.logger.info("✅ Автозапуск зарегистрирован")

    def register_stopped(self):
        """Зарегистрировать остановку."""
        self._data["last_stop"] = datetime.now().isoformat()
        self._data["is_running"] = False
        self._data["last_uptime_hours"] = self._data.get("total_uptime_hours", 0)
        self._save_data()
        self.logger.info("⏹️ Остановка зарегистрирована")

    def is_registered(self) -> bool:
        """Проверить, зарегистрирован ли автозапуск."""
        return self._data.get("is_registered", False)

    def enable_auto_start(self):
        """Включить автозапуск."""
        self._data["is_registered"] = True
        self._data["auto_start_enabled"] = True
        self._data["registered_at"] = datetime.now().isoformat()
        self._save_data()
        self.logger.info("🚀 Автозапуск включён")

    def disable_auto_start(self):
        """Выключить автозапуск."""
        self._data["is_registered"] = False
        self._data["auto_start_enabled"] = False
        self._save_data()
        self.logger.info("⛔ Автозапуск выключен")

    def get_startup_info(self) -> dict:
        """Получить информацию о запуске."""
        return {
            "is_running": self._data.get("is_running", False),
            "last_start": self._data.get("last_start"),
            "last_stop": self._data.get("last_stop"),
            "start_count": self._data.get("start_count", 0),
            "auto_start_enabled": self._data.get("auto_start_enabled", False),
            "total_uptime_hours": self._data.get("total_uptime_hours", 0),
            "registered_at": self._data.get("registered_at"),
        }

    def _load_data(self) -> dict:
        """Загрузка данных."""
        if self.registry_path.exists():
            try:
                with open(self.registry_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception:
                return {}
        return {}

    def _save_data(self):
        """Сохранение данных."""
        with open(self.registry_path, 'w', encoding='utf-8') as f:
            json.dump(self._data, f, ensure_ascii=False, indent=2)
