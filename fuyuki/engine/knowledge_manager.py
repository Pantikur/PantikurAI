"""
Менеджер знаний Фуюки.

Управляет:
  - Базой знаний об атмосферном электричестве
  - Получением и хранением знаний
  - Ростом уровня знаний
  - Классификацией знаний по областям
  - Сохранением и загрузкой базы знаний
"""

from __future__ import annotations
import json
import logging
import random
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Set

from fuyuki.engine.models import (
    KnowledgeDomain, KnowledgeLevel, ElectricityConstants
)


class KnowledgeManager:
    """
    Менеджер знаний Фуюки.
    """

    def __init__(self, config: Any):
        self.config = config
        self.logger = logging.getLogger("KnowledgeManager")
        self.knowledge_dir = config.knowledge_dir
        self.knowledge_dir.mkdir(parents=True, exist_ok=True)

        # База знаний
        self.knowledge_base: Dict[str, Any] = {
            "domains": {},
            "facts": [],
            "theories_learned": [],
            "papers_studied": [],
            "formulas": [],
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat(),
        }

        # Уровень знаний
        self.knowledge_level = KnowledgeLevel(
            level=config.knowledge_level,
            xp=config.knowledge_xp,
        )

        # Константы
        self.constants = ElectricityConstants()

        # Загружаем состояние
        self._load_state()

    def add_knowledge(
        self,
        fact: str,
        domain: KnowledgeDomain = KnowledgeDomain.ATMOSPHERIC_ELECTRICITY,
        source: str = "web",
        confidence: float = 0.8,
    ) -> bool:
        """
        Добавляет знание в базу.
        
        Returns:
            True если уровень повышен
        """
        knowledge_entry = {
            "fact": fact,
            "domain": domain.value,
            "source": source,
            "confidence": confidence,
            "added_at": datetime.now().isoformat(),
        }

        # Добавляем в базу знаний
        domain_key = domain.value
        if domain_key not in self.knowledge_base["domains"]:
            self.knowledge_base["domains"][domain_key] = []
        self.knowledge_base["domains"][domain_key].append(knowledge_entry)

        # Добавляем в общий список фактов
        self.knowledge_base["facts"].append(knowledge_entry)

        # Добавляем домен в изученные
        if domain_key not in self.knowledge_level.domains_studied:
            self.knowledge_level.domains_studied.append(domain_key)

        # Получаем XP
        xp_gained = self.config.xp_per_research if source == "web" else 20
        leveled_up = self.knowledge_level.add_xp(xp_gained, domain)

        # Обновляем счётчики
        self.knowledge_level.papers_studied += 1

        if leveled_up:
            self.logger.info(f"🎉 Фуюки повысила уровень! {self.knowledge_level.level} — {self.knowledge_level.get_level_name()}")

        self.logger.info(f"📚 Добавлено знание: {fact[:60]}... (+{xp_gained} XP)")
        return leveled_up

    def add_formula(
        self,
        formula: str,
        name: str,
        description: str,
        domain: KnowledgeDomain = KnowledgeDomain.ATMOSPHERIC_ELECTRICITY,
    ):
        """Добавляет формулу в базу знаний."""
        formula_entry = {
            "formula": formula,
            "name": name,
            "description": description,
            "domain": domain.value,
            "added_at": datetime.now().isoformat(),
        }
        self.knowledge_base["formulas"].append(formula_entry)
        self.logger.info(f"📐 Добавлена формула: {name} — {formula}")

    def add_theory(
        self,
        theory_name: str,
        description: str,
        category: str,
        domain: KnowledgeDomain = KnowledgeDomain.ATMOSPHERIC_ELECTRICITY,
    ):
        """Добавляет теорию в базу знаний."""
        theory_entry = {
            "name": theory_name,
            "description": description,
            "category": category,
            "domain": domain.value,
            "added_at": datetime.now().isoformat(),
        }
        self.knowledge_base["theories_learned"].append(theory_entry)

        # XP за теорию
        leveled_up = self.knowledge_level.add_xp(
            self.config.xp_per_theory, domain
        )
        self.knowledge_level.theories_count += 1

        if leveled_up:
            self.logger.info(f"🎉 Теория повысила уровень! {self.knowledge_level.level}")

    def add_calculation(
        self,
        calculation_type: str,
        result: float,
        units: str,
        domain: KnowledgeDomain = KnowledgeDomain.ATMOSPHERIC_ELECTRICITY,
    ):
        """Добавляет результат вычисления в базу знаний."""
        self.knowledge_level.calculations_count += 1
        self.knowledge_level.add_xp(self.config.xp_per_calculation, domain)

    def get_knowledge_by_domain(self, domain: KnowledgeDomain) -> List[Dict[str, Any]]:
        """Получает все знания по области."""
        domain_key = domain.value
        return self.knowledge_base["domains"].get(domain_key, [])

    def get_all_facts(self) -> List[Dict[str, Any]]:
        """Получает все факты."""
        return self.knowledge_base["facts"]

    def get_all_formulas(self) -> List[Dict[str, Any]]:
        """Получает все формулы."""
        return self.knowledge_base["formulas"]

    def get_random_fact(self, domain: Optional[KnowledgeDomain] = None) -> Optional[str]:
        """Получает случайный факт."""
        facts = self.knowledge_base["facts"]
        if not facts:
            return None
        
        if domain:
            facts = [f for f in facts if f.get("domain") == domain.value]
        
        if not facts:
            return None
        
        return random.choice(facts)["fact"]

    def get_knowledge_summary(self) -> Dict[str, Any]:
        """Получает сводку по знаниям."""
        return {
            "level": self.knowledge_level.level,
            "level_name": self.knowledge_level.get_level_name(),
            "xp": self.knowledge_level.xp,
            "progress_to_next": round(self.knowledge_level.progress_to_next_level(), 1),
            "domains_count": len(self.knowledge_base["domains"]),
            "facts_count": len(self.knowledge_base["facts"]),
            "formulas_count": len(self.knowledge_base["formulas"]),
            "theories_count": len(self.knowledge_base["theories_learned"]),
            "domains_studied": self.knowledge_level.domains_studied,
        }

    def study_from_papers(self, papers: List[Dict[str, Any]]):
        """Изучает знания из научных статей."""
        for paper in papers:
            # Добавляем ключевые находки как знания
            for finding in paper.get("key_findings", []):
                self.add_knowledge(
                    finding,
                    domain=KnowledgeDomain.ATMOSPHERIC_ELECTRICITY,
                    source=paper.get("source", "web"),
                    confidence=paper.get("relevance", 0.5),
                )
            
            # Добавляем статью в изученные
            self.knowledge_base["papers_studied"].append({
                "title": paper.get("title", "Без названия"),
                "authors": paper.get("authors", []),
                "year": paper.get("year", 2024),
                "studied_at": datetime.now().isoformat(),
            })

    def study_from_web(self, content: str, topic: str, domain: KnowledgeDomain = KnowledgeDomain.ATMOSPHERIC_ELECTRICITY):
        """Изучает знания из веб-контента."""
        # Разбиваем контент на предложения и извлекаем ключевые факты
        import re
        sentences = re.split(r'[.!?]+', content)
        
        for sentence in sentences[:10]:
            sentence = sentence.strip()
            if len(sentence) > 30:
                self.add_knowledge(
                    sentence,
                    domain=domain,
                    source="web",
                    confidence=0.6,
                )

    def save_state(self):
        """Сохраняет состояние базы знаний."""
        self.knowledge_base["updated_at"] = datetime.now().isoformat()
        
        # Сохраняем базу знаний
        kb_path = self.knowledge_dir / "knowledge_base.json"
        try:
            with open(kb_path, "w", encoding="utf-8") as f:
                json.dump(self.knowledge_base, f, ensure_ascii=False, indent=2)
            self.logger.debug(f"💾 База знаний сохранена: {kb_path}")
        except Exception as e:
            self.logger.error(f"❌ Ошибка сохранения базы знаний: {e}")

        # Сохраняем уровень знаний
        level_path = self.knowledge_dir / "knowledge_level.json"
        try:
            with open(level_path, "w", encoding="utf-8") as f:
                json.dump(self.knowledge_level.to_dict(), f, ensure_ascii=False, indent=2)
            self.logger.debug(f"💾 Уровень знаний сохранён: {level_path}")
        except Exception as e:
            self.logger.error(f"❌ Ошибка сохранения уровня знаний: {e}")

    def _load_state(self):
        """Загружает состояние базы знаний."""
        kb_path = self.knowledge_dir / "knowledge_base.json"
        if kb_path.exists():
            try:
                with open(kb_path, "r", encoding="utf-8") as f:
                    self.knowledge_base = json.load(f)
                self.logger.info(f"📚 Загружена база знаний: {len(self.knowledge_base['facts'])} фактов")
            except Exception as e:
                self.logger.warning(f"⚠️ Ошибка загрузки базы знаний: {e}")

        level_path = self.knowledge_dir / "knowledge_level.json"
        if level_path.exists():
            try:
                with open(level_path, "r", encoding="utf-8") as f:
                    level_data = json.load(f)
                self.knowledge_level = KnowledgeLevel(
                    level=level_data.get("level", 1),
                    xp=level_data.get("xp", 0),
                    domain_xp=level_data.get("domain_xp", {}),
                    domains_studied=level_data.get("domains_studied", []),
                    theories_count=level_data.get("theories_count", 0),
                    calculations_count=level_data.get("calculations_count", 0),
                    papers_studied=level_data.get("papers_studied", 0),
                    web_searches=level_data.get("web_searches", 0),
                    interactions_count=level_data.get("interactions_count", 0),
                    reports_written=level_data.get("reports_written", 0),
                )
                self.logger.info(f"📊 Загружен уровень знаний: Lvl {self.knowledge_level.level}")
            except Exception as e:
                self.logger.warning(f"⚠️ Ошибка загрузки уровня знаний: {e}")

    def get_const_value(self, name: str) -> Optional[float]:
        """Получает значение физической константы."""
        return getattr(self.constants, name, None)

    def list_constants(self) -> Dict[str, float]:
        """Список всех физических констант."""
        return {
            name: getattr(self.constants, name)
            for name in dir(self.constants)
            if not name.startswith("_") and isinstance(getattr(self.constants, name), float)
        }
