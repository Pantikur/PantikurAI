"""
Система отчётов Ханако.
"""

from __future__ import annotations

import json
import logging
import uuid
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional

from hanako.engine.config import HanakoConfig
from hanako.engine.models import ResearchReport


class ReportSystem:
    """
    Система отчётов Ханако.
    
    Функции:
    - Генерация ежедневных отчётов
    - Генерация еженедельных отчётов
    - Отчёты по теориям
    - Отчёты по исследованиям
    - Системные отчёты
    """

    def __init__(self, config: HanakoConfig):
        self.config = config
        self.logger = logging.getLogger("ReportSystem")
        self.reports_path = config.state_dir / "reports.json"
        self._reports: list[ResearchReport] = self._load_reports()

    def generate_daily_report(self, hanako_core) -> Optional[ResearchReport]:
        """Генерация ежедневного отчёта."""
        now = datetime.now()
        day_start = now - timedelta(days=1)

        # Собираем статистику
        level = hanako_core.level
        theories_count = len([t for t in hanako_core.theories if t.created_at >= day_start])
        tasks_count = len([t for t in hanako_core.research_tasks if t.created_at >= day_start])
        messages_count = len([m for m in hanako_core.messages if m.timestamp >= day_start])

        # Уровни
        level_info = (
            f"Уровень: {level.overall_level} ({level.get_level_name()})\n"
            f"  Гравитация: {level.gravity_theory_level}\n"
            f"  Интернет: {level.web_research_level}\n"
            f"  Саморазвитие: {level.self_development_level}\n"
            f"  Общение: {level.communication_level}\n"
            f"  Вычисления: {level.calculation_level}\n"
            f"  Характер: {level.character_growth_level}"
        )

        content = (
            f"=== Ежедневный отчёт Ханако ===\n"
            f"Дата: {now.strftime('%Y-%m-%d %H:%M')}\n\n"

            f"--- Статистика за день ---\n"
            f"  Новых теорий: {theories_count}\n"
            f"  Новых задач: {tasks_count}\n"
            f"  Сообщений: {messages_count}\n"
            f"  Сайтов просканировано: {level.total_websites_scanned}\n\n"

            f"--- Уровень знаний ---\n"
            f"{level_info}\n\n"

            f"--- Характер ---\n"
            f"{hanako_core.character.get_character_summary()}\n\n"

            f"--- Последние теории ---\n"
        )

        for theory in hanako_core.theories[-5:]:
            content += f"  • {theory.title} (уверенность: {theory.confidence:.1%})\n"

        content += f"\n--- Следующие задачи ---\n"
        for task in [t for t in hanako_core.research_tasks if t.status.value == "in_progress"][:5]:
            content += f"  • {task.title} (прогресс: {task.progress:.0%})\n"

        report = ResearchReport(
            title=f"Ежедневный отчёт: {now.strftime('%Y-%m-%d')}",
            report_type="daily",
            content=content,
            statistics={
                "theories_today": theories_count,
                "tasks_today": tasks_count,
                "messages_today": messages_count,
                "total_websites": level.total_websites_scanned,
                "total_theories": level.total_theories,
            },
        )
        report.id = f"report_{uuid.uuid4().hex[:8]}"

        self._reports.append(report)
        self._save_reports()

        return report

    def generate_weekly_report(self, hanako_core) -> Optional[ResearchReport]:
        """Генерация еженедельного отчёта."""
        now = datetime.now()
        week_start = now - timedelta(weeks=1)

        level = hanako_core.level

        content = (
            f"=== Еженедельный отчёт Ханако ===\n"
            f"Период: {week_start.strftime('%Y-%m-%d')} — {now.strftime('%Y-%m-%d')}\n\n"

            f"--- Итоги недели ---\n"
            f"  Теорий создано: {level.total_theories}\n"
            f"  Исследований: {level.total_researches}\n"
            f"  Сайтов изучено: {level.total_websites_scanned}\n"
            f"  Сообщений отправлено: {level.total_messages_sent}\n"
            f"  Сообщений получено: {level.total_messages_received}\n"
            f"  Улучшений характера: {level.total_character_upgrades}\n\n"

            f"--- Прогресс уровней ---\n"
            f"  Общий: {level.overall_level} ({level.get_level_name()})\n"
            f"  Гравитация: {level.gravity_theory_level}\n"
            f"  Интернет: {level.web_research_level}\n"
            f"  Саморазвитие: {level.self_development_level}\n"
            f"  Общение: {level.communication_level}\n\n"

            f"--- Характер ---\n"
            f"{hanako_core.character.get_character_summary()}\n"
        )

        report = ResearchReport(
            title=f"Еженедельный отчёт: {now.strftime('%Y-%m-%d')}",
            report_type="weekly",
            content=content,
            statistics={
                "total_theories": level.total_theories,
                "total_researches": level.total_researches,
                "total_websites": level.total_websites_scanned,
            },
        )
        report.id = f"report_weekly_{uuid.uuid4().hex[:8]}"

        self._reports.append(report)
        self._save_reports()

        return report

    def generate_theory_report(self, theory) -> Optional[ResearchReport]:
        """Отчёт по конкретной теории."""
        content = (
            f"=== Отчёт по теории ===\n"
            f"Название: {theory.title}\n"
            f"Категория: {theory.category.value}\n"
            f"Уверенность: {theory.confidence:.1%}\n"
            f"Уравнений: {len(theory.equations)}\n"
            f"Предсказаний: {len(theory.predictions)}\n"
            f"Источников: {len(theory.sources)}\n\n"

            f"Описание:\n{theory.description}\n\n"

            f"Уравнения:\n" + "\n".join(f"  {eq}" for eq in theory.equations) + "\n\n"

            f"Предсказания:\n" + "\n".join(f"  • {p}" for p in theory.predictions) + "\n\n"

            f"Источники:\n" + "\n".join(f"  • {s}" for s in theory.sources[:10])
        )

        report = ResearchReport(
            title=f"Отчёт: {theory.title}",
            report_type="theory",
            content=content,
            related_theories=[theory.id],
            tags=theory.tags,
        )
        report.id = f"report_theory_{uuid.uuid4().hex[:8]}"

        self._reports.append(report)
        self._save_reports()

        return report

    def get_reports(self, report_type: str = "") -> list[ResearchReport]:
        """Получить отчёты."""
        if report_type:
            return [r for r in self._reports if r.report_type == report_type]
        return list(self._reports)

    def load_reports(self) -> list[ResearchReport]:
        """Публичная загрузка отчётов."""
        return self._load_reports()

    def save_reports(self, reports: list[ResearchReport] | None = None):
        """Публичное сохранение отчётов."""
        if reports is not None:
            self._reports = reports
        self._save_reports()

    def _load_reports(self) -> list[ResearchReport]:
        """Загрузка отчётов."""
        import uuid
        if not self.reports_path.exists():
            return []
        try:
            with open(self.reports_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                reports = []
                for d in data:
                    reports.append(ResearchReport(
                        title=d["title"],
                        report_type=d["report_type"],
                        content=d["content"],
                        author=d.get("author", "hanako"),
                        created_at=datetime.fromisoformat(d["created_at"]),
                        tags=d.get("tags", []),
                        related_theories=d.get("related_theories", []),
                        statistics=d.get("statistics", {}),
                        id=d.get("id", ""),
                    ))
                return reports
        except Exception:
            return []

    def _save_reports(self):
        """Сохранение отчётов."""
        with open(self.reports_path, 'w', encoding='utf-8') as f:
            json.dump([r.to_dict() for r in self._reports[-100:]], f, ensure_ascii=False, indent=2)
