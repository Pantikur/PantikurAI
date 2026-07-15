"""
Система отчётности Аква.
"""

from __future__ import annotations
import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

from .models import CycleReport, PersonalityVector, KnowledgeLevel


class AkvaReporter:
    """Генерация и хранение отчётов Аква."""

    def __init__(self, config: Any):
        self.config = config
        self.logger = logging.getLogger("AkvaReporter")
        self.reports_dir = config.reports_dir
        self.reports_dir.mkdir(parents=True, exist_ok=True)

    def generate_cycle_report(self, cycle_number: int, personality: PersonalityVector,
                               knowledge_levels: Dict[str, KnowledgeLevel],
                               studied_topics: List[str], theories: List[Dict],
                               calculations: List[Dict], communication: List[Dict],
                               personality_changes: Dict[str, float],
                               xp_gained: int, level_changes: List[str]) -> CycleReport:
        """Создать отчёт за цикл."""
        report = CycleReport(
            cycle_number=cycle_number,
            studied_topics=studied_topics,
            theories_built=theories,
            calculations_done=calculations,
            communication_log=communication,
            personality_changes=personality_changes,
            xp_gained=xp_gained,
            level_changes=level_changes,
        )
        return report

    def save_report(self, report: CycleReport) -> str:
        """Сохранить отчёт в файл."""
        filename = f"akva_cycle_{report.cycle_number}.json"
        filepath = self.reports_dir / filename

        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(report.to_dict(), f, ensure_ascii=False, indent=2)

        self.logger.info(f"📄 Отчёт сохранён: {filename}")
        return str(filepath)

    def generate_summary(self, report: CycleReport) -> str:
        """Сгенерировать краткую сводку для других модулей."""
        lines = [
            f"📐 Аква → ВСЕ",
            f"Цикл #{report.cycle_number} | +{len(report.theories_built)} теорий | "
            f"+{len(report.calculations_done)} вычислений | +{report.xp_gained} XP",
        ]

        if report.studied_topics:
            topics_str = ", ".join(report.studied_topics[:3])
            lines.append(f"Изучено: {topics_str}")

        if report.level_changes:
            lines.append(f"Уровни: {' | '.join(report.level_changes)}")

        lines.append(f"Отчёт: data/reports/akva_cycle_{report.cycle_number}.json")
        return "\n".join(lines)

    def generate_daily_summary(self, reports: List[CycleReport]) -> str:
        """Ежедневная сводка (каждые 10 циклов)."""
        if not reports:
            return ""

        total_theories = sum(len(r.theories_built) for r in reports)
        total_calcs = sum(len(r.calculations_done) for r in reports)
        total_xp = sum(r.xp_gained for r in reports)
        all_topics = []
        for r in reports:
            all_topics.extend(r.studied_topics)

        return (
            f"=== ЕЖЕДНЕВНЫЙ ОТЧЁТ АКВА ===\n"
            f"Циклов: {len(reports)}\n"
            f"Теорий: {total_theories}\n"
            f"Вычислений: {total_calcs}\n"
            f"XP получено: {total_xp}\n"
            f"Тем изучено: {len(set(all_topics))}\n"
            f"Темы: {', '.join(list(set(all_topics))[:5])}"
        )

    def generate_final_report(self, personality: PersonalityVector,
                               knowledge_levels: Dict[str, KnowledgeLevel],
                               total_cycles: int) -> str:
        """Итоговый отчёт."""
        lines = [
            "=" * 60,
            "ИТОГОВЫЙ ОТЧЁТ АКВА",
            "=" * 60,
            f"Всего циклов: {total_cycles}",
            "",
            "--- Характер ---",
            f"  Доминирующая черта: {personality.dominant_trait()}",
            f"  Уровень личности: {personality.level_description()}",
            "",
        ]

        for key, value in personality.to_dict().items():
            bar_len = int(value * 10)
            bar = "█" * bar_len + "░" * (10 - bar_len)
            lines.append(f"  {key}: {bar} {value}")

        lines.append("")
        lines.append("--- Уровни знаний ---")

        for area, kl in knowledge_levels.items():
            lines.append(f"  {area}: уровень {kl.level}/100, XP: {kl.xp}")
            if kl.topics_studied:
                lines.append(f"    Темы: {', '.join(kl.topics_studied[-3:])}")

        lines.append("")
        lines.append("=" * 60)
        return "\n".join(lines)
