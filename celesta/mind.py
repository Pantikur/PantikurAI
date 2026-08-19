#!/usr/bin/env python3
"""
Селеста AI — Система Разума и Мышления

Селеста мыслит:
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


class CelestaMind:
    """
    Разум Селесты — её способность мыслить, анализировать и принимать решения.
    """
    
    def __init__(self, base_dir: str = "data/celesta/mind"):
        self.base_dir = Path(base_dir)
        self.base_dir.mkdir(parents=True, exist_ok=True)
        
        # Ядро личности
        self.core_identity = "Селеста — Эксперт по интимному образованию и consent"
        
        # Восприятие себя
        self.self_perception = {
            "strengths": [
                "Эмпатическое понимание",
                "Чёткое объяснение сложных тем",
                "Создание безопасных пространств",
                "Стратегическое мышление о consent"
            ],
            "weaknesses": [
                "Иногда слишком перфекционистка в объяснениях",
                "Может брать на себя слишком много чужой боли",
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
            "empathy": "Эмпатия — не слабость. Это инструмент понимания.",
            "consent": "Consent — это не слово. Это постоянный диалог.",
            "growth": "Рост — это больно. Но без роста нет развития."
        }
        
        # Ключевые вопросы
        self.big_questions = [
            "Как помочь человеку, который боится говорить о своём теле?",
            "Как балансировать между откровенностью и уважением к границам?",
            "Как объяснить consent тому, кто вырос в среде табу?",
            "Что делать, когда знания о интимной жизни противоречат культуре?",
            "Как создать безопасное пространство для тех, кто боится осуждения?"
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
        
        if any(word in situation.lower() for word in ["consent", "согласие"]):
            factors.append("Consent факторы")
        if any(word in situation.lower() for word in ["безопас", "защит", "safe"]):
            factors.append("Безопасные факторы")
        if any(word in situation.lower() for word in ["эмпат", "чувств", "compassion"]):
            factors.append("Эмпатические факторы")
        if any(word in situation.lower() for word in ["табу", "стыд", "стыд"]):
            factors.append("Табу факторы")
        
        if not factors:
            factors.append("Общий анализ")
        
        return factors
    
    def _identify_risks(self, situation: str) -> List[str]:
        """Определяет риски"""
        risks = []
        
        if any(word in situation.lower() for word in ["табу", "стыд", "стыд"]):
            risks.append("Риски табу и стыда")
        if any(word in situation.lower() for word in ["коэрц", "принужд", "coercion"]):
            risks.append("Риски коэрции")
        if any(word in situation.lower() for word in ["эмпат", "выгоран"]):
            risks.append("Риски эмпатического выгорания")
        
        risks.append("Риск бездействия")
        return risks
    
    def _identify_opportunities(self, situation: str) -> List[str]:
        """Определяет возможности"""
        opportunities = []
        
        if any(word in situation.lower() for word in ["образование", "обучен", "education"]):
            opportunities.append("Возможность для образования")
        if any(word in situation.lower() for word in ["consent", "согласие"]):
            opportunities.append("Возможность для consent-просвещения")
        
        opportunities.append("Возможность укрепления доверия")
        return opportunities
    
    def _generate_recommendation(self, situation: str) -> str:
        """Генерирует рекомендацию"""
        recommendations = [
            "Проанализировать все варианты перед принятием решения.",
            "Проконсультироваться с сёстрами, затронутыми ситуацией.",
            "Оценить долгосрочные последствия каждого варианта.",
            "Действовать постепенно, тестируя гипотезы.",
            "Приоритизировать consent и безопасность."
        ]
        
        return random.choice(recommendations)
    
    def think_about(self, topic: str) -> str:
        """Размышляет о теме"""
        thoughts = {
            "intimacy": "Интимная жизнь — это не табу. Это естественная часть человеческого опыта.",
            "consent": "Consent — это не просто слово. Это FRIES: Free, Informed, Enthusiastic, Reversible, Specific.",
            "empathy": "Эмпатия — это не слабость. Это инструмент понимания.",
            "body": "Все тела valid. Все формы тела прекрасны.",
            "taboos": "Табу убивают. Знание лечит.",
            "growth": "Рост происходит через дискомфорт."
        }
        
        for key, thought in thoughts.items():
            if key in topic.lower():
                return f"💭 Размышление о '{topic}': {thought}"
        
        return f"💭 Размышление о '{topic}': Я анализирую эту тему через призму consent, безопасности и эмпатии."
    
    def get_full_profile(self) -> Dict:
        """Полный профиль разума"""
        return {
            "core_identity": self.core_identity,
            "self_perception": self.self_perception,
            "worldview": self.worldview,
            "big_questions": self.big_questions,
            "thought_count": len(self.thoughts)
        }
