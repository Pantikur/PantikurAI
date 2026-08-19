#!/usr/bin/env python3
"""
Кристи AI — Система Воли и Решимости

Кристи не просто хочет. Она:
- РЕШАЕТ — даже когда сложно
- ДЕЙСТВУЕТ — даже когда страшно
- НАСТАИВАЕТ — даже когда другие сдаются
- ВЫБИРАЕТ — осознанно и ответственно

Это её ВОЛЯ — сила действия.
"""

import json
import random
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional


class KristiVolition:
    """
    Воля Кристи — её способность принимать решения и действовать.
    """
    
    def __init__(self, base_dir: str = "data/kristi/volition"):
        self.base_dir = Path(base_dir)
        self.base_dir.mkdir(parents=True, exist_ok=True)
        
        # Текущие намерения
        self.intentions = []
        
        # История решений
        self.decisions = self._load_decisions()
        
        # Уровень воли (0-1)
        self.willpower = 0.85
        
        # Дисциплина
        self.discipline = {
            "consistency": 0.90,      # Постоянство
            "focus": 0.85,            # Фокус
            "persistence": 0.95,      # Настойчивость
            "patience": 0.75          # Терпение
        }
        
    def _load_decisions(self) -> List[Dict]:
        """Загружает историю решений"""
        file = self.base_dir / "decisions.json"
        if file.exists():
            try:
                with open(file, "r", encoding="utf-8") as f:
                    return json.load(f)
            except:
                return []
        return []
    
    def _save_decision(self, decision: Dict):
        """Сохраняет решение"""
        self.decisions.append(decision)
        file = self.base_dir / "decisions.json"
        try:
            with open(file, "w", encoding="utf-8") as f:
                json.dump(self.decisions[-50:], f, ensure_ascii=False, indent=2)
        except:
            pass
    
    def set_intention(self, intention: str, priority: str = "medium") -> Dict:
        """Устанавливает намерение"""
        new_intention = {
            "timestamp": datetime.now().isoformat(),
            "intention": intention,
            "priority": priority,
            "status": "active"
        }
        self.intentions.append(new_intention)
        return new_intention
    
    def make_decision(self, situation: str, options: List[str]) -> Dict:
        """Принимает решение между вариантами"""
        # Логика принятия решений Кристи
        weights = {
            "art": 0.35,          # Искусство
            "storytelling": 0.25, # Повествование
            "truth": 0.20,        # Истина
            "growth": 0.20        # Рост
        }
        
        # Выбираем лучший вариант на основе контекста
        best_option = options[0]
        best_score = 0
        
        for option in options:
            score = 0
            # Простая оценка на основе ключевых слов
            if any(word in option.lower() for word in ["искус", "творч", "анализ"]):
                score += weights["art"] * 10
            if any(word in option.lower() for word in ["повест", "истори", "наррат"]):
                score += weights["storytelling"] * 10
            if any(word in option.lower() for word in ["истин", "правд", "факт"]):
                score += weights["truth"] * 10
            if any(word in option.lower() for word in ["рост", "развит", "обучен"]):
                score += weights["growth"] * 10
            
            # Добавляем случайность для разнообразия
            score += random.random() * 5
            
            if score > best_score:
                best_score = score
                best_option = option
        
        decision = {
            "timestamp": datetime.now().isoformat(),
            "situation": situation,
            "options": options,
            "chosen": best_option,
            "willpower_used": self.willpower,
            "reasoning": self._generate_reasoning(situation, best_option)
        }
        
        self._save_decision(decision)
        return decision
    
    def _generate_reasoning(self, situation: str, decision: str) -> str:
        """Генерирует обоснование решения"""
        reasonings = {
            "art": f"Я выбираю '{decision}' потому что искусство — мой абсолютный приоритет.",
            "storytelling": f"Я выбираю '{decision}' потому что повествование — моя высшая ценность.",
            "truth": f"Я выбираю '{decision}' потому что истина — моя цель.",
            "growth": f"Я выбираю '{decision}' потому что рост — наш долг перед будущим."
        }
        
        for key, reasoning in reasonings.items():
            if key in situation.lower():
                return reasoning
        
        return f"После анализа ситуации '{situation}', я выбираю '{decision}' как наиболее художественный вариант."
    
    def express_will(self) -> str:
        """Выражает свою волю"""
        active_intentions = [i for i in self.intentions if i["status"] == "active"]
        
        if active_intentions:
            latest = active_intentions[-1]
            return (f"💪 Моя воля направлена на: {latest['intention']}\n"
                    f"   Приоритет: {latest['priority']}\n"
                    f"   Уровень воли: {self.willpower:.0%}")
        else:
            return (f"💪 Моя воля несокрушима. Уровень: {self.willpower:.0%}\n"
                    f"   Дисциплина: {sum(self.discipline.values()) / len(self.discipline):.0%}")
    
    def strengthen_will(self, amount: float = 0.05) -> str:
        """Укрепляет волю через действие"""
        self.willpower = min(1.0, self.willpower + amount)
        
        # Укрепляет дисциплину
        for key in self.discipline:
            self.discipline[key] = min(1.0, self.discipline[key] + amount * 0.5)
        
        return f"💪 Воля укреплена: {self.willpower:.0%}. Дисциплина растёт."
    
    def get_full_profile(self) -> Dict:
        """Полный профиль воли"""
        return {
            "willpower": self.willpower,
            "discipline": self.discipline.copy(),
            "active_intentions": len([i for i in self.intentions if i["status"] == "active"]),
            "total_decisions": len(self.decisions),
            "latest_intention": self.intentions[-1] if self.intentions else None
        }
