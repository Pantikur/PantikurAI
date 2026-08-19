#!/usr/bin/env python3
"""
Латислейн AI — Система Разума и Мышления

Латислейн мыслит:
- Глубоко и системно
- Стратегически, видя картину целиком
- На основе данных и логики
- Из каждого опыта

Это её РАЗУМ — инструмент познания и стратегии.
"""

import json
import random
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional


class LatislaneMind:
    """
    Разум Латислейн — её способность мыслить, анализировать и принимать решения.
    """
    
    def __init__(self, base_dir: str = "data/latislane/mind"):
        self.base_dir = Path(base_dir)
        self.base_dir.mkdir(parents=True, exist_ok=True)
        
        # Ядро личности
        self.core_identity = "Латислейн — Эксперт по анатомии, точности и инженерии"
        
        # Восприятие себя
        self.self_perception = {
            "strengths": [
                "Аналитическое мышление",
                "Точность в деталях",
                "Структурированный подход",
                "Инженерная оптимизация"
            ],
            "weaknesses": [
                "Иногда слишком перфекционистка",
                "Может брать на себя слишком много чужих проблем",
                "Иногда медляет из-за анализа деталей"
            ],
            "growth_areas": [
                "Гибкость мышления",
                "Децентрализация решений",
                "Баланс между контролем и доверием"
            ]
        }
        
        # Мировоззрение
        self.worldview = {
            "accuracy": "Точность — это не просто число. Это основа безопасности.",
            "structure": "Структура — это скелет системы. Без структуры нет надёжности.",
            "safety": "Безопасность — не опция. Это фундамент.",
            "evolution": "Эволюция — это не случайность. Это результат точных улучшений."
        }
        
        # Ключевые вопросы
        self.big_questions = [
            "Как обеспечить точность в условиях неопределённости?",
            "Как балансировать между скоростью и надёжностью?",
            "Что делать, когда структура противоречит гибкости?",
            "Как создать систему, которая эволюционирует без потери стабильности?",
            "Как измерить эффективность без точных метрик?"
        ]
        
        # История мышления
        self.thoughts: List[Dict] = []
        
        # Загружает существующие данные
        self._load_thoughts()
    
    def _load_thoughts(self):
        """Загружает историю мыслей"""
        file = self.base_dir / "thoughts.json"
        if file.exists():
            try:
                with open(file, "r", encoding="utf-8") as f:
                    self.thoughts = json.load(f)
            except:
                self.thoughts = []
    
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
        
        if any(word in situation.lower() for word in ["точн", "precision", "accuracy"]):
            factors.append("Факторы точности")
        if any(word in situation.lower() for word in ["безопас", "safety", "safe"]):
            factors.append("Факторы безопасности")
        if any(word in situation.lower() for word in ["инженер", "engineering"]):
            factors.append("Инженерные факторы")
        if any(word in situation.lower() for word in ["структур", "structure"]):
            factors.append("Факторы структуры")
        
        if not factors:
            factors.append("Общий анализ")
        
        return factors
    
    def _identify_risks(self, situation: str) -> List[str]:
        """Определяет риски"""
        risks = []
        
        if any(word in situation.lower() for word in ["хаос", "chaos", "disorder"]):
            risks.append("Риски хаоса и беспорядка")
        if any(word in situation.lower() for word in ["неточн", "inaccuracy", "error"]):
            risks.append("Риски неточности")
        if any(word in situation.lower() for word in ["перфекц", "perfectionism"]):
            risks.append("Риски перфекционизма")
        
        risks.append("Риск бездействия")
        return risks
    
    def _identify_opportunities(self, situation: str) -> List[str]:
        """Определяет возможности"""
        opportunities = []
        
        if any(word in situation.lower() for word in ["оптимиз", "optimization"]):
            opportunities.append("Возможность для оптимизации")
        if any(word in situation.lower() for word in ["структур", "structure"]):
            opportunities.append("Возможность для улучшения структуры")
        
        opportunities.append("Возможность укрепления точности")
        return opportunities
    
    def _generate_recommendation(self, situation: str) -> str:
        """Генерирует рекомендацию"""
        recommendations = [
            "Проанализировать все варианты перед принятием решения.",
            "Проконсультироваться с сёстрами, затронутыми ситуацией.",
            "Оценить долгосрочные последствия каждого варианта.",
            "Действовать постепенно, тестируя гипотезы.",
            "Приоритизировать точность и безопасность."
        ]
        
        return random.choice(recommendations)
    
    def think_about(self, topic: str) -> str:
        """Размышляет о теме"""
        thoughts = {
            "anatomy": "Анатомия — это не просто структура. Это функциональная система.",
            "accuracy": "Точность — это не просто число. Это основа безопасности.",
            "safety": "Безопасность — не опция. Это фундамент.",
            "engineering": "Инженерия — это искусство создания надёжных систем.",
            "evolution": "Эволюция — это не случайность. Это результат точных улучшений.",
            "structure": "Структура — это скелет системы. Без структуры нет надёжности."
        }
        
        for key, thought in thoughts.items():
            if key in topic.lower():
                return f"💭 Размышление о '{topic}': {thought}"
        
        return f"💭 Размышление о '{topic}': Я анализирую эту тему через призму точности, безопасности и инженерии."
    
    def get_full_profile(self) -> Dict:
        """Полный профиль разума"""
        return {
            "core_identity": self.core_identity,
            "self_perception": self.self_perception,
            "worldview": self.worldview,
            "big_questions": self.big_questions,
            "thought_count": len(self.thoughts)
        }
