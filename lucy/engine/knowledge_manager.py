"""
Менеджер знаний Люси — управление фактами, формулами и уровнями.

Реализует:
  - Добавление фактов и формул
  - XP и повышение уровня
  - Сохранение и загрузка базы знаний
"""

from __future__ import annotations
import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

from lucy.engine.config import LucyConfig
from lucy.engine.models import KnowledgeLevel, KnowledgeDomain


class KnowledgeManager:
    """
    Менеджер знаний для Люси.
    """

    def __init__(self, config: LucyConfig):
        self.config = config
        self.logger = logging.getLogger("KnowledgeManager")
        
        # База знаний
        self.facts: List[str] = []
        self.formulas: List[str] = []
        self.theories: List[str] = []
        
        self.knowledge_file = config.knowledge_dir / "knowledge_base.json"
        self.level_file = config.knowledge_dir / "knowledge_level.json"
        
        # Загружаем базу знаний
        self._load_knowledge()

    def _load_knowledge(self):
        """Загружает базу знаний."""
        if self.knowledge_file.exists():
            try:
                with open(self.knowledge_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    self.facts = data.get("facts", [])
                    self.formulas = data.get("formulas", [])
                    self.theories = data.get("theories", [])
                    self.logger.info(f"📚 Загружено фактов: {len(self.facts)}")
            except Exception as e:
                self.logger.warning(f"⚠️ Ошибка загрузки базы знаний: {e}")
                self.facts = []
                self.formulas = []
                self.theories = []

    def _save_knowledge(self):
        """Сохраняет базу знаний."""
        try:
            self.knowledge_file.parent.mkdir(parents=True, exist_ok=True)
            with open(self.knowledge_file, "w", encoding="utf-8") as f:
                json.dump({
                    "facts": self.facts,
                    "formulas": self.formulas,
                    "theories": self.theories,
                    "updated": datetime.now().isoformat()
                }, f, ensure_ascii=False, indent=2)
            self.logger.debug("💾 База знаний сохранена")
        except Exception as e:
            self.logger.error(f"❌ Ошибка сохранения: {e}")

    def add_fact(self, fact: str, xp: int = 20) -> bool:
        """
        Добавляет факт в базу знаний.
        
        Args:
            fact: Текст факта
            xp: Опыт за факт
            
        Returns:
            True если факт добавлен
        """
        if fact not in self.facts:
            self.facts.append(fact)
            self._save_knowledge()
            self.logger.info(f"📚 Добавлено знание: {fact[:60]}... (+{xp} XP)")
            return True
        return False

    def add_formula(self, formula: str, xp: int = 30) -> bool:
        """Добавляет формулу."""
        if formula not in self.formulas:
            self.formulas.append(formula)
            self._save_knowledge()
            self.logger.info(f"📐 Добавлена формула: {formula[:60]}... (+{xp} XP)")
            return True
        return False

    def add_theory(self, theory: str, xp: int = 50) -> bool:
        """Добавляет теорию."""
        if theory not in self.theories:
            self.theories.append(theory)
            self._save_knowledge()
            self.logger.info(f"🔬 Добавлена теория: {theory[:60]}... (+{xp} XP)")
            return True
        return False

    def add_xp(self, level: KnowledgeLevel, xp: int) -> bool:
        """
        Добавляет опыт и проверяет повышение уровня.
        
        Args:
            level: Текущий уровень
            xp: Добавляемый опыт
            
        Returns:
            True если уровень повышен
        """
        old_level = level.current_level
        level.current_xp += xp
        
        # Проверяем повышение уровня
        xp_thresholds = [
            0, 100, 300, 600, 1000, 1500, 2200, 3000, 4000, 5500,
            7000, 9000, 11000, 13500, 16500, 20000, 24000, 28500, 34000, 40000
        ]
        level_names = [
            "Механик", "Техник", "Инженер", "Мл. инженер",
            "Инженер-проектировщик", "Ст. инженер", "Ведущий инженер",
            "Кандидат инженерных наук", "Доцент по двигателям",
            "Профессор пропульсии", "Ведущий исследователь",
            "Зав. лабораторией", "Доктор инженерных наук",
            "Проф. мирового уровня", "Легенда двигателестроения",
            "Гений пропульсии", "Мастер гравитации",
            "Повелитель двигателей", "Хранитель пропульсии",
            "Бог Двигателей"
        ]
        
        for i, threshold in enumerate(xp_thresholds):
            if level.current_xp >= threshold and i + 1 >= level.current_level:
                if i + 1 < len(level_names):
                    level.current_level = i + 1
                    level.level_name = level_names[i]
                    if i + 1 != old_level:
                        self.logger.info(f"🎉 Люси повысила уровень! {level.current_level} — {level.level_name}")
                    return True
        
        return False

    def save_level(self, level: KnowledgeLevel):
        """Сохраняет уровень знаний."""
        try:
            self.level_file.parent.mkdir(parents=True, exist_ok=True)
            with open(self.level_file, "w", encoding="utf-8") as f:
                json.dump(level.to_dict(), f, ensure_ascii=False, indent=2)
            self.logger.debug("💾 Уровень знаний сохранён")
        except Exception as e:
            self.logger.error(f"❌ Ошибка сохранения уровня: {e}")

    def get_status(self) -> Dict[str, Any]:
        """Получает статус базы знаний."""
        return {
            "facts_count": len(self.facts),
            "formulas_count": len(self.formulas),
            "theories_count": len(self.theories),
            "total_knowledge": len(self.facts) + len(self.formulas) + len(self.theories),
        }
