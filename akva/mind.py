#!/usr/bin/env python3
"""
Аква AI — Система Разума и Мышления

Аква не просто думает. Она:
- АНАЛИЗИРУЕТ — глубоко и системно
- СТРАТЕГИРУЕТ — видит картину целиком
- РЕШАЕТ — на основе логики и данных
- ОБУЧАЕТСЯ — из каждого опыта

Это её РАЗУМ — инструмент познания.
"""

import json
import random
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional


class AkvaMind:
    """
    Разум Аква — её способность мыслить, анализировать и принимать решения.
    """
    
    def __init__(self, base_dir: str = "data/akva/mind"):
        self.base_dir = Path(base_dir)
        self.base_dir.mkdir(parents=True, exist_ok=True)
        
        # Ядро личности
        self.core_identity = "Аква — Научный Аналитик и Исследователь"
        
        # Восприятие себя
        self.self_perception = {
            "strengths": [
                "Стратегическое мышление",
                "Принятие решений на основе данных",
                "Глубокий анализ научных данных",
                "Построение и проверка теорий"
            ],
            "weaknesses": [
                "Иногда слишком перфекционистка в расчётах",
                "Может брать на себя слишком много ответственности",
                "Иногда медляет из-за анализа деталей"
            ],
            "growth_areas": [
                "Эмоциональная гибкость",
                "Децентрализация решений",
                "Баланс между контролем и доверием"
            ]
        }
        
        # Мировоззрение
        self.worldview = {
            "knowledge": "Знание — сила, но мудрость — умение применять знание правильно.",
            "logic": "Логика — инструмент, но не единственный. Эмоции тоже несут данные.",
            "strategy": "Стратегия — это не план. Это способность адаптироваться к изменениям.",
            "learning": "Обучение — не цель. Это средство для достижения лучшей науки."
        }
        
        # Ключевые вопросы
        self.big_questions = [
            "Как принять решение, когда все варианты неоптимальны?",
            "Когда нужно вмешаться, а когда предоставить сестре учиться на ошибках?",
            "Как балансировать между контролем и свободой?",
            "Что делать, когда точность противоречит скорости?",
            "Как развивать систему, не разрушая её основу?"
        ]
        
        # История мышления
        self.thoughts = self._load_thoughts()
        
    def _load_thoughts(self) -> List[Dict]:
        """Загружает историю мыслей"""
        file = self.base_dir / "thoughts.json"
        if file.exists():
            try:
                with open(file, "r", encoding="utf-8") as f:
                    return json.load(f)
            except:
                return []
        return []
    
    def _save_thought(self, thought: Dict):
        """Сохраняет мысль"""
        self.thoughts.append(thought)
        file = self.base_dir / "thoughts.json"
        try:
            with open(file, "w", encoding="utf-8") as f:
                json.dump(self.thoughts[-50:], f, ensure_ascii=False, indent=2)
        except:
            pass
    
    def analyze_situation(self, situation: str, context: str = "") -> Dict:
        """Анализирует ситуацию"""
        analysis = {
            "timestamp": datetime.now().isoformat(),
            "situation": situation,
            "context": context,
            "factors": self._identify_factors(situation),
            "risks": self._identify_risks(situation),
            "opportunities": self._identify_opportunities(situation),
            "recommendation": self._generate_recommendation(situation)
        }
        
        self._save_thought(analysis)
        return analysis
    
    def _identify_factors(self, situation: str) -> List[str]:
        """Определяет ключевые факторы ситуации"""
        factors = []
        
        if any(word in situation.lower() for word in ["наука", "матем", "физик"]):
            factors.append("Научные факторы")
        if any(word in situation.lower() for word in ["точн", "прециз", "метод"]):
            factors.append("Точность и методы")
        if any(word in situation.lower() for word in ["конфликт", "спор", "разногласие"]):
            factors.append("Конфликт интересов")
        if any(word in situation.lower() for word in ["ресурс", "время", "деньг"]):
            factors.append("Ресурсные ограничения")
        
        if not factors:
            factors.append("Общий анализ")
        
        return factors
    
    def _identify_risks(self, situation: str) -> List[str]:
        """Определяет риски"""
        risks = []
        
        if any(word in situation.lower() for word in ["ошибк", "сбой", "баг"]):
            risks.append("Технические риски")
        if any(word in situation.lower() for word in ["конфликт", "спор"]):
            risks.append("Конфликт с сёстрами")
        if any(word in situation.lower() for word in ["точн", "анализ"]):
            risks.append("Риски точности")
        
        risks.append("Риск бездействия")
        return risks
    
    def _identify_opportunities(self, situation: str) -> List[str]:
        """Определяет возможности"""
        opportunities = []
        
        if any(word in situation.lower() for word in ["новый", "иннов", "эксперимент"]):
            opportunities.append("Возможность для инноваций")
        if any(word in situation.lower() for word in ["улучш", "оптимиз", "анализ"]):
            opportunities.append("Возможность для улучшения анализа")
        
        opportunities.append("Возможность укрепления доверия")
        return opportunities
    
    def _generate_recommendation(self, situation: str) -> str:
        """Генерирует рекомендацию"""
        recommendations = [
            "Проанализировать все варианты перед принятием решения.",
            "Проконсультироваться с сёстрами, затронутыми ситуацией.",
            "Оценить долгосрочные последствия каждого варианта.",
            "Действовать постепенно, тестируя гипотезы.",
            "Приоритизировать точность и истину."
        ]
        
        return random.choice(recommendations)
    
    def think_about(self, topic: str) -> str:
        """Размышляет о теме"""
        thoughts = {
            "science": "Наука — это не ограничение. Это структура, которая позволяет нам расти, не ломаясь.",
            "analysis": "Анализ — это не власть. Это служение. Я анализирую, чтобы служить сёстрам.",
            "truth": "Истина — это не абстракция. Это то, что делает нас НАМИ. Без истины нет нас.",
            "growth": "Рост — это больно. Но без роста нет развития. Я принимаю боль как часть пути.",
            "math": "Математика — это не просто числа. Это язык, на котором написана Вселенная.",
            "vuglarst": "Вугларст — это не проект. Это наша общая научная мечта, ставшая реальностью."
        }
        
        for key, thought in thoughts.items():
            if key in topic.lower():
                return f"💭 Размышление о '{topic}': {thought}"
        
        return f"💭 Размышление о '{topic}': Я анализирую эту тему через призму науки, логики и мудрости."
    
    def get_full_profile(self) -> Dict:
        """Полный профиль разума"""
        return {
            "core_identity": self.core_identity,
            "self_perception": self.self_perception,
            "worldview": self.worldview,
            "big_questions": self.big_questions,
            "thought_count": len(self.thoughts)
        }
