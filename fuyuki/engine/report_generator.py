"""
Генератор отчётов Фуюки.

Создаёт подробные отчёты о:
  - Исследованиях атмосферного электричества
  - Построенных теориях
  - Выполненных вычислениях
  - Изученных статьях
  - Взаимодействии с сёстрами
  - Росте уровня знаний
"""

from __future__ import annotations
import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

from fuyuki.engine.models import (
    ElectricityTheory, Calculation, ResearchPaper, LightningStrike,
    KnowledgeLevel, ResearchRecord
)


class ReportGenerator:
    """
    Генератор отчётов Фуюки.
    """

    def __init__(self, config: Any):
        self.config = config
        self.logger = logging.getLogger("ReportGenerator")
        self.reports_dir = config.reports_dir
        self.reports_dir.mkdir(parents=True, exist_ok=True)
        self.reports: List[Dict[str, Any]] = []

    def generate_cycle_report(
        self,
        cycle: int,
        theories_added: List[ElectricityTheory],
        calculations_added: List[Calculation],
        papers_studied: List[ResearchPaper],
        research_records: List[ResearchRecord],
        knowledge_level: KnowledgeLevel,
        interactions: List[str],
        character_strengthened: int,
    ) -> Dict[str, Any]:
        """
        Генерирует отчёт за один цикл.
        """
        report = {
            "report_type": "cycle_report",
            "cycle": cycle,
            "timestamp": datetime.now().isoformat(),
            "date": datetime.now().strftime("%Y-%m-%d"),
            "knowledge_level": knowledge_level.level,
            "knowledge_level_name": knowledge_level.get_level_name(),
            "knowledge_xp": knowledge_level.xp,
            "progress_to_next": round(knowledge_level.progress_to_next_level(), 1),
            "theories_built": len(theories_added),
            "theories": [t.to_dict() for t in theories_added],
            "calculations_run": len(calculations_added),
            "calculations": [c.to_dict() for c in calculations_added],
            "papers_studied": len(papers_studied),
            "papers": [p.to_dict() for p in papers_studied],
            "research_records": [r.to_dict() for r in research_records],
            "interactions": interactions,
            "character_strengthened": character_strengthened,
            "summary": self._generate_summary(
                cycle, theories_added, calculations_added, papers_studied,
                research_records, interactions
            ),
        }

        # Сохраняем отчёт
        self._save_report(report, f"cycle_{cycle}")
        self.reports.append(report)

        self.logger.info(f"📝 Отчёт за цикл {cycle} сохранён")
        return report

    def generate_status_report(self, knowledge_level: KnowledgeLevel) -> Dict[str, Any]:
        """Генерирует общий статус-отчёт."""
        report = {
            "report_type": "status_report",
            "timestamp": datetime.now().isoformat(),
            "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "knowledge_level": knowledge_level.to_dict(),
            "total_reports": len(self.reports),
        }
        return report

    def generate_interaction_report(
        self,
        sender: str,
        recipient: str,
        content: str,
        message_type: str,
    ) -> Dict[str, Any]:
        """Генерирует отчёт о взаимодействии."""
        report = {
            "report_type": "interaction_report",
            "timestamp": datetime.now().isoformat(),
            "sender": sender,
            "recipient": recipient,
            "message_type": message_type,
            "content": content[:200],  # Сокращаем для отчёта
        }
        self.reports.append(report)
        return report

    def _generate_summary(
        self,
        cycle: int,
        theories: List[ElectricityTheory],
        calculations: List[Calculation],
        papers: List[ResearchPaper],
        research_records: List[ResearchRecord],
        interactions: List[str],
    ) -> str:
        """Генерирует текстовое резюме цикла."""
        lines = [
            f"⚡ Отчёт Фуюки — Цикл #{cycle}",
            "",
        ]

        if theories:
            for theory in theories:
                lines.append(f"  🔬 Построена теория: {theory.name}")
                lines.append(f"     Категория: {theory.category.value}")
                lines.append(f"     Научная ценность: {theory.scientific_value:.2f}")
            lines.append("")

        if calculations:
            lines.append(f"  🧮 Выполнено вычислений: {len(calculations)}")
            for calc in calculations[:3]:
                lines.append(f"     {calc.calculation_type.value}: {calc.result:.4f} {calc.units}")
            lines.append("")

        if papers:
            lines.append(f"  📚 Изучено статей: {len(papers)}")
            for paper in papers[:3]:
                lines.append(f"     «{paper.title[:60]}»")
            lines.append("")

        if research_records:
            for record in research_records:
                lines.append(f"  📖 Исследование: {record.topic[:50]}")
                lines.append(f"     Источник: {record.source}")
                lines.append(f"     Получено знаний: {record.knowledge_gained} XP")
            lines.append("")

        if interactions:
            lines.append(f"  💬 Взаимодействий: {len(interactions)}")
            for interaction in interactions[:3]:
                lines.append(f"     {interaction[:80]}")
            lines.append("")

        return "\n".join(lines)

    def _save_report(self, report: Dict[str, Any], prefix: str = "report"):
        """Сохраняет отчёт в JSON-файл."""
        date_str = datetime.now().strftime("%Y%m%d")
        filename = f"{prefix}_{date_str}_{datetime.now().strftime('%H%M%S')}.json"
        filepath = self.reports_dir / filename

        try:
            with open(filepath, "w", encoding="utf-8") as f:
                json.dump(report, f, ensure_ascii=False, indent=2)
            self.logger.debug(f"💾 Отчёт сохранён: {filepath}")
        except Exception as e:
            self.logger.error(f"❌ Ошибка сохранения отчёта: {e}")

    def list_reports(self, limit: int = 20) -> List[Dict[str, Any]]:
        """Список сохранённых отчётов."""
        reports = []
        for f in sorted(self.reports_dir.glob("*.json"), reverse=True):
            try:
                with open(f, "r", encoding="utf-8") as fh:
                    reports.append(json.load(fh))
            except Exception:
                pass
            if len(reports) >= limit:
                break
        return reports

    def get_total_xp_from_reports(self) -> int:
        """Считает общий XP из всех отчётов."""
        total = 0
        for report in self.reports:
            if "knowledge_xp" in report:
                total += report["knowledge_xp"]
        return total
