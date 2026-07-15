"""
Генератор отчётов Люси — создание цикловых, статусных и интерактивных отчётов.

Реализует:
  - Цикловые отчёты (после каждого N-го цикла)
  - Статусные отчёты (текущее состояние)
  - Интерактивные отчёты (для сестёр)
  - Сохранение в JSON и текст
"""

from __future__ import annotations
import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Optional

from lucy.engine.config import LucyConfig


class ReportGenerator:
    """
    Генератор отчётов для Люси.
    """

    def __init__(self, config: LucyConfig):
        self.config = config
        self.logger = logging.getLogger("ReportGenerator")
        
        # Директория для отчётов
        self.reports_dir = config.reports_dir
        self.reports_dir.mkdir(parents=True, exist_ok=True)

    def generate_cycle_report(self, cycle: int, theories_count: int = 0, 
                               calculations_count: int = 0, papers_count: int = 0) -> Dict[str, Any]:
        """
        Генерирует отчёт за цикл.
        
        Args:
            cycle: Номер цикла
            theories_count: Количество теорий
            calculations_count: Количество вычислений
            papers_count: Количество изученных статей
            
        Returns:
            Словарь с данными отчёта
        """
        report = {
            "cycle": cycle,
            "timestamp": datetime.now().isoformat(),
            "theories_count": theories_count,
            "calculations_count": calculations_count,
            "papers_count": papers_count,
            "status": "completed",
        }
        
        # Сохраняем отчёт
        self._save_report(f"cycle_{cycle}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json", report)
        
        return report

    def generate_status_report(self, status_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Генерирует статусный отчёт.
        
        Args:
            status_data: Данные статуса
            
        Returns:
            Словарь с данными отчёта
        """
        report = {
            "type": "status",
            "timestamp": datetime.now().isoformat(),
            **status_data
        }
        
        self._save_report(f"status_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json", report)
        
        return report

    def generate_interactive_report(self, sender: str, recipient: str, 
                                     content: str, attachments: Optional[Dict] = None) -> Dict[str, Any]:
        """
        Генерирует интерактивный отчёт для сестёр.
        
        Args:
            sender: Отправитель
            recipient: Получатель
            content: Содержание
            attachments: Вложения
            
        Returns:
            Словарь с данными отчёта
        """
        report = {
            "type": "interactive",
            "timestamp": datetime.now().isoformat(),
            "sender": sender,
            "recipient": recipient,
            "content": content,
            "attachments": attachments or {}
        }
        
        self._save_report(f"interactive_{sender}_{recipient}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json", report)
        
        return report

    def _save_report(self, filename: str, report: Dict[str, Any]):
        """Сохраняет отчёт в файл."""
        try:
            report_path = self.reports_dir / filename
            with open(report_path, "w", encoding="utf-8") as f:
                json.dump(report, f, ensure_ascii=False, indent=2)
            self.logger.debug(f"💾 Отчёт сохранён: {report_path}")
        except Exception as e:
            self.logger.error(f"❌ Ошибка сохранения отчёта: {e}")
