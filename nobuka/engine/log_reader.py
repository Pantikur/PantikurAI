"""
Чтение логов приложения (main.py) для Нобуки.

Нобука получает доступ к логам приложения, работающего на TimeWeb (или локально):

  - ищет лог-файл в типичных местах (env APP_LOG_FILE, logs/app.log, пути TimeWeb);
  - читает НОВЫЕ записи с места последнего чтения (tail по байтовому смещению),
    чтобы не обрабатывать один и тот же лог дважды;
  - извлекает из записей сигналы (ERROR / WARNING / CRITICAL + traceback)
    в формате, совместимом с pipeline улучшений Нобуки.
"""

from __future__ import annotations

import json
import logging
import os
import re
from pathlib import Path
from typing import Any, Optional

from nobuka.engine.config import NobukaConfig


class AppLogReader:
    """
    Читатель логов приложения.

    Позиция чтения сохраняется в файле состояния (app_log_offset_state),
    поэтому каждая запись попадает в обработку ровно один раз.
    """

    # Строка формата логов main.py: "%(asctime)s | %(levelname)s | %(name)s | %(message)s"
    _ENTRY_RE = re.compile(
        r"^\d{4}-\d{2}-\d{2}[ T]\d{2}:\d{2}:\d{2}[^|]*\|\s*(?P<level>[A-Z]+)\s*\|"
    )

    # Уровни, которые превращаются в сигналы (INFO/DEBUG игнорируются)
    _SIGNAL_LEVELS = {"ERROR", "WARNING", "CRITICAL", "FATAL"}

    def __init__(self, config: NobukaConfig):
        self.config = config
        self.logger = logging.getLogger("NobukaAppLogReader")
        self.log_path: Optional[Path] = None
        self._offset_state: dict[str, Any] = {}

        self._load_offset_state()

    # ================================================================
    #  ПОИСК ФАЙЛА ЛОГА
    # ================================================================

    def find_log_file(self) -> Optional[Path]:
        """
        Найти файл лога приложения.

        Приоритет:
          1. Явный путь из конфига (app_log_path)
          2. Переменная окружения APP_LOG_FILE
          3. Кандидаты из конфига (включая типичные пути TimeWeb)
        """
        # 1. Конфиг
        if self.config.app_log_path is not None:
            path = Path(os.path.expanduser(str(self.config.app_log_path)))
            if path.exists():
                return path

        # 2. Окружение (то же значение, что использует main.py)
        env_path = os.environ.get("APP_LOG_FILE", "").strip()
        if env_path:
            path = Path(env_path)
            if path.exists():
                return path

        # 3. Кандидаты из конфига (с glob-поддержкой для TimeWeb /var/www/*/...)
        for candidate in self.config.app_log_candidates:
            candidate_str = os.path.expanduser(str(candidate))
            if any(ch in candidate_str for ch in "*?["):
                # Путь с wildcard — перебираем совпадения (может быть абсолютным)
                import glob as _glob
                matched = sorted(_glob.glob(candidate_str))
                for path in matched:
                    if Path(path).is_file():
                        return Path(path)
            else:
                path = Path(candidate_str)
                if path.is_file():
                    return path

        return None

    def _load_offset_state(self):
        """Загрузить сохранённое смещение чтения."""
        offset_path = self.config.app_log_offset_state
        try:
            if offset_path.exists():
                with open(offset_path, "r", encoding="utf-8") as f:
                    self._offset_state = json.load(f)
        except Exception as e:
            self.logger.debug(f"Не удалось загрузить состояние оффсета логов: {e}")
            self._offset_state = {}

    def _save_offset_state(self, offset: int):
        """Сохранить смещение чтения."""
        offset_path = self.config.app_log_offset_state
        try:
            offset_path.parent.mkdir(parents=True, exist_ok=True)
            self._offset_state = {
                "file": str(self.log_path) if self.log_path else "",
                "offset": offset,
                "updated_at": __import__("datetime").datetime.now().isoformat(),
            }
            with open(offset_path, "w", encoding="utf-8") as f:
                json.dump(self._offset_state, f, ensure_ascii=False, indent=2)
        except Exception as e:
            self.logger.debug(f"Не удалось сохранить оффсет логов: {e}")

    # ================================================================
    #  ЧТЕНИЕ НОВЫХ ЗАПИСЕЙ
    # ================================================================

    def read_new_entries(self) -> list[dict]:
        """
        Прочитать новые записи из лога приложения.

        Returns:
            Список записей: {"level", "message", "lines"} (новые с последнего чтения).
            Пустой список, если лог не найден или новых записей нет.
        """
        if not self.config.app_log_monitoring_enabled:
            return []

        log_path = self.find_log_file()
        if log_path is None:
            # Лог пока не найден — не ошибка (файл может появиться позже)
            return []

        self.log_path = log_path

        try:
            size = log_path.stat().st_size
        except OSError:
            return []

        # Файл сменился или уменьшился (ротация) либо это первый запуск — читаем хвост
        prev_file = self._offset_state.get("file", "")
        prev_offset = self._offset_state.get("offset", 0)

        if prev_file != str(log_path) or size < prev_offset:
            new_text = self._read_tail(log_path)
            offset = size
        else:
            try:
                with open(log_path, "r", encoding="utf-8", errors="ignore") as f:
                    f.seek(prev_offset)
                    new_text = f.read()
                offset = size
            except (OSError, ValueError):
                new_text = self._read_tail(log_path)
                offset = size

        self._save_offset_state(offset)

        entries = self._parse_entries(new_text)
        if entries:
            self.logger.debug(
                f"📋 Лог {log_path}: {len(entries)} новых записей"
            )
        return entries

    def _read_tail(self, log_path: Path) -> str:
        """Прочитать хвост лог-файла (последние N строк)."""
        tail_lines = self.config.app_log_tail_lines
        try:
            with open(log_path, "r", encoding="utf-8", errors="ignore") as f:
                lines = f.readlines()
            return "".join(lines[-tail_lines:])
        except OSError:
            return ""

    # ================================================================
    #  ПАРСИНГ И СИГНАЛЫ
    # ================================================================

    def _parse_entries(self, text: str) -> list[dict]:
        """
        Разобрать текст лога на записи.

        Строка вида "2026-08-11 12:00:00 | ERROR | main | сообщение" начинает новую
        запись; последующие строки (например, traceback) присоединяются к ней.
        Строка с любым другим уровнем (INFO/DEBUG) прерывает присоединение.
        """
        entries: list[dict] = []
        current: Optional[dict] = None

        for raw_line in text.splitlines():
            line = raw_line.rstrip()
            if not line:
                continue

            m = self._ENTRY_RE.match(line)
            if m:
                level = m.group("level")
                if level in self._SIGNAL_LEVELS:
                    message = self._ENTRY_RE.sub("", line, count=1).strip()
                    current = {
                        "level": level,
                        "message": message or line,
                        "lines": [line],
                    }
                    entries.append(current)
                else:
                    # INFO/DEBUG и прочие несignальные уровни — прерывают traceback
                    current = None
            elif current is not None:
                # Продолжение предыдущей записи (traceback и т.п.)
                if len(current["lines"]) < 30:
                    current["lines"].append(line)
                current["message"] += "\n" + line

        return entries

    def extract_signals(self, entries: list[dict]) -> list[dict]:
        """
        Превратить записи лога в сигналы для pipeline улучшений Нобуки.

        Формат сигнала совместим с _collect_project_signals():
          {"type": "bug_detected", "severity": ..., "file": ..., "context": ...}

        Повторяющиеся сообщения агрегируются (дедупликация по тексту).
        """
        severity_map = {
            "CRITICAL": "high",
            "FATAL": "high",
            "ERROR": "high",
            "WARNING": "medium",
        }

        grouped: dict[str, dict] = {}
        for entry in entries:
            severity = severity_map.get(entry["level"], "low")
            message = entry["message"][:300]
            key = message
            if key not in grouped:
                grouped[key] = {
                    "level": entry["level"],
                    "severity": severity,
                    "message": message,
                    "count": 0,
                }
            grouped[key]["count"] += 1

        signals = []
        for item in grouped.values():
            context = f"{item['level']} (x{item['count']}): {item['message']}"
            signals.append({
                "type": "bug_detected",
                "severity": item["severity"],
                "file": f"{self.log_path} (приложение main.py)",
                "context": context,
            })
        return signals

    def get_log_summary(self) -> dict:
        """
        Краткая сводка по логу приложения для отчёта.
        """
        log_path = self.find_log_file()
        if log_path is None:
            return {"found": False}

        try:
            size = log_path.stat().st_size
        except OSError:
            return {"found": False}

        return {
            "found": True,
            "path": str(log_path),
            "size_bytes": size,
            "last_offset": self._offset_state.get("offset", 0),
        }
