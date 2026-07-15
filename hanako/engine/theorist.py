"""
Построитель гравитационных теорий Ханако.
"""

from __future__ import annotations

import json
import random
import uuid
import logging
from datetime import datetime
from pathlib import Path
from typing import Optional

from hanako.engine.config import HanakoConfig
from hanako.engine.models import (
    GravityTheory, TheoryCategory, ResearchTask, ResearchStatus,
    WebResearchResult,
)


class GravityTheorist:
    """
    Построитель гравитационных теорий.

    Функции:
    - Анализ веб-результатов
    - Построение теорий из источников
    - Расчёт уверенности теории
    - Сохранение и загрузка теорий
    """

    def __init__(self, config: HanakoConfig):
        self.config = config
        self.logger = logging.getLogger("GravityTheorist")
        self.theories_path = config.state_dir / "theories.json"
        self.tasks_path = config.state_dir / "research_tasks.json"

    def build_theory_from_web(
        self, topic: str, results: list[WebResearchResult], all_topics: list[str]
    ) -> Optional[GravityTheory]:
        """Построение теории из веб-результатов."""
        if not results:
            return None

        # Выбираем категорию
        category = self._select_category(topic)

        # Собираем данные из результатов
        all_summaries = [r.summary for r in results if r.summary]
        all_equations = []
        for r in results:
            all_equations.extend(r.extracted_equations)

        # Генерируем уравнения
        equations = self._generate_equations(topic, all_equations)

        # Генерируем предсказания
        predictions = self._generate_predictions(topic, category)

        # Рассчитываем уверенность
        confidence = self._calculate_confidence(results, equations, predictions)

        # Собираем источники
        sources = [r.url for r in results[:10]]

        theory = GravityTheory(
            title=f"{self._theory_title(topic, category)}",
            category=category,
            description=self._generate_description(topic, all_summaries),
            equations=equations[:10],
            predictions=predictions[:5],
            evidence=[r.summary[:200] for r in results[:5]],
            confidence=confidence,
            sources=sources,
            tags=[topic.lower().replace(" ", "_")[:30], category.value],
        )
        theory.id = f"theory_{uuid.uuid4().hex[:8]}"
        theory.updated_at = datetime.now()

        self.logger.info(f"Теория построена: {theory.title} (уверенность: {confidence:.1%})")
        return theory

    def _select_category(self, topic: str) -> TheoryCategory:
        """Выбор категории теории по теме."""
        topic_lower = topic.lower()

        keywords_map = {
            TheoryCategory.RELATIVITY: ["относительн", "эйнштейн", "пространство-врем", "геометри", "искривлен"],
            TheoryCategory.QUANTUM: ["квант", "квантов", "планк", "дискрет"],
            TheoryCategory.STRING: ["струн", "м-теор", "брана", "суперструн"],
            TheoryCategory.LOOP: ["петлев", "loop quantum"],
            TheoryCategory.GRAVITON: ["гравитон", "гравитоны", "частиц"],
            TheoryCategory.ENTROPIC: ["энтроп", "верлинде", "информаци"],
            TheoryCategory.MODIFIED: ["mond", "монд", "модифиц", "эмд"],
            TheoryCategory.CLASSICAL: ["ньютон", "ньютонов", "классич"],
            TheoryCategory.HYPOTHETICAL: ["гипотет", "предполож", "спец"],
            TheoryCategory.UNIFIED: ["унификац", "теория всё", "то теор", "физик всё"],
        }

        for category, keywords in keywords_map.items():
            for kw in keywords:
                if kw in topic_lower:
                    return category

        return random.choice(list(TheoryCategory))

    def _theory_title(self, topic: str, category: TheoryCategory) -> str:
        """Генерация заголовка теории."""
        prefixes = {
            TheoryCategory.RELATIVITY: "Геометрическая модель",
            TheoryCategory.QUANTUM: "Квантовая теория",
            TheoryCategory.STRING: "Струнная модель",
            TheoryCategory.LOOP: "Петлевая теория",
            TheoryCategory.GRAVITON: "Гравитонная модель",
            TheoryCategory.ENTROPIC: "Энтропийная модель",
            TheoryCategory.MODIFIED: "Модифицированная теория",
            TheoryCategory.CLASSICAL: "Классическая модель",
            TheoryCategory.HYPOTHETICAL: "Гипотетическая модель",
            TheoryCategory.UNIFIED: "Объединённая теория",
        }
        prefix = prefixes.get(category, "Модель")
        return f"{prefix}: {topic}"

    def _generate_equations(self, topic: str, existing: list[str]) -> list[str]:
        """Генерация уравнений для теории."""
        templates = [
            "G_μν + Λg_μν = (8πG/c⁴)T_μν",
            "R_μν - ½Rg_μν + Λg_μν = κT_μν",
            "∇_μ T^μν = 0",
            "ds² = -c²dt² + a(t)²(dx² + dy² + dz²)",
            "R = 8πG ∂_μ φ ∂^μ φ - V(φ)",
            "G = mc²",
            "F = G(m₁m₂)/r²",
            "Γ^λ_μν = ½g^λσ(∂_μ g_νσ + ∂_ν g_μσ - ∂_σ g_μν)",
            "R^ρ_σμν = ∂_μ Γ^ρ_νσ - ∂_ν Γ^ρ_μσ + Γ^ρ_μλ Γ^λ_νσ - Γ^ρ_νλ Γ^λ_μσ",
            "∂_μ(√-g g^μν ∂_ν φ) = √-g dV/dφ",
        ]
        results = list(existing)
        random.shuffle(templates)
        results.extend(templates[:5])
        return list(dict.fromkeys(results))[:10]

    def _generate_predictions(self, topic: str, category: TheoryCategory) -> list[str]:
        """Генерация предсказаний теории."""
        predictions = {
            TheoryCategory.RELATIVITY: [
                "Гравитационное линзирование массивных объектов",
                "Замедление времени в гравитационном поле",
                "Существование чёрных дыр",
                "Гравитационные волны с предсказанной частотой",
                "Смещение перигелия Меркурия",
            ],
            TheoryCategory.QUANTUM: [
                "Дискретность пространства-времени на планковской шкале",
                "Квантовые флуктуации гравитационного поля",
                "Гравитационные экранирующие эффекты на квантовом уровне",
                "Модификация закона обратных квадратов на малых расстояниях",
            ],
            TheoryCategory.STRING: [
                "Существование дополнительных измерений",
                "Модификация гравитации на субмиллиметровых масштабах",
                "Существование суперсимметричных частиц",
                "Гравитация как проявление струнных колебаний",
            ],
            TheoryCategory.LOOP: [
                "Дискретная структура пространства-времени",
                "Исправление сингулярности в центре чёрных дыр",
                "Квантование площади и объёма",
                "Петлевая поправка к уравнениям Фридмана",
            ],
            TheoryCategory.ENTROPIC: [
                "Гравитация как энтропийная сила",
                "Связь между гравитацией и информационным содержанием",
                "Модификация закона обратных квадратов на больших масштабах",
                "Энтропийные поправки к формуле Бекенштейна-Хокинга",
            ],
        }
        return predictions.get(category, [
            f"Модификация гравитационных эффектов при {topic.lower()}",
            "Новые предсказания для гравитационных волн",
            "Коррекции к ньютоновской гравитации",
            "Влияние на космологическую эволюцию",
        ])

    def _generate_description(self, topic: str, summaries: list[str]) -> str:
        """Генерация описания теории."""
        if summaries:
            base = summaries[0][:300]
        else:
            base = f"Теория исследует {topic}."

        return (
            f"Данная теория исследует аспекты гравитации в контексте '{topic}'. "
            f"Основываясь на анализе научных источников, теория предлагает "
            f"следующий подход: {base}"
        )

    def _calculate_confidence(self, results, equations, predictions) -> float:
        """Расчёт уверенности теории."""
        confidence = 0.1  # базовая

        # Количество источников
        confidence += min(len(results) * 0.05, 0.3)

        # Наличие уравнений
        confidence += min(len(equations) * 0.05, 0.2)

        # Количество предсказаний
        confidence += min(len(predictions) * 0.03, 0.15)

        # Средний ранжирование результатов
        if results:
            avg_relevance = sum(r.relevance for r in results) / len(results)
            confidence += avg_relevance * 0.2

        return min(confidence, 0.95)

    def calculate_xp(self, theory: GravityTheory) -> float:
        """Расчёт опыта за теорию."""
        xp = 20.0
        xp += len(theory.equations) * 5
        xp += len(theory.predictions) * 3
        xp += len(theory.evidence) * 2
        xp += theory.confidence * 30
        return xp

    # ==================== Сохранение / Загрузка ====================

    def load_theories(self) -> list[GravityTheory]:
        """Загрузка теорий."""
        if not self.theories_path.exists():
            return []
        try:
            with open(self.theories_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return [GravityTheory.from_dict(d) for d in data]
        except Exception:
            return []

    def save_theories(self, theories: list[GravityTheory]):
        """Сохранение теорий."""
        with open(self.theories_path, 'w', encoding='utf-8') as f:
            json.dump([t.to_dict() for t in theories], f, ensure_ascii=False, indent=2)

    def load_research_tasks(self) -> list[ResearchTask]:
        """Загрузка задач исследований."""
        if not self.tasks_path.exists():
            return []
        try:
            with open(self.tasks_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                tasks = []
                from hanako.engine.models import ResearchStatus, TheoryCategory
                for d in data:
                    tasks.append(ResearchTask(
                        title=d["title"],
                        description=d["description"],
                        category=TheoryCategory(d["category"]),
                        status=ResearchStatus(d["status"]),
                        priority=d.get("priority", 5),
                        progress=d.get("progress", 0.0),
                        related_theories=d.get("related_theories", []),
                        sources=d.get("sources", []),
                        notes=d.get("notes", []),
                        created_at=datetime.fromisoformat(d["created_at"]),
                        id=d.get("id", ""),
                    ))
                return tasks
        except Exception:
            return []

    def save_research_tasks(self, tasks: list[ResearchTask]):
        """Сохранение задач исследований."""
        with open(self.tasks_path, 'w', encoding='utf-8') as f:
            json.dump([t.to_dict() for t in tasks], f, ensure_ascii=False, indent=2)
