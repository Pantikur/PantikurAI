"""
Сидни AI — Воля

Сидни:
- Дисциплинированный инженер
- Постоянно работает над улучшением систем
- Принимает решения на основе логики и опыта
- Упрямо идёт к своим целям

Это её ВОЛЯ — решимость и дисциплина.
"""

import json
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional


class SidneyVolition:
    """
    Воля Сидни — решимость, дисциплина, принятие решений.
    """
    
    def __init__(self, base_dir: str = "data/sidney/volition"):
        self.base_dir = Path(base_dir)
        self.base_dir.mkdir(parents=True, exist_ok=True)
        
        # Уровень воли
        self.willpower: float = 0.85
        
        # Дисциплина
        self.discipline = {
            "consistency": 0.90,    # Постоянство
            "focus": 0.85,          # Фокус
            "perseverance": 0.90,   # Настойчивость
            "patience": 0.75        # Терпение
        }
        
        # Текущие намерения
        self.current_intentions: List[Dict] = []
        
        # История решений
        self.decision_history: List[Dict] = []
        
        # Обоснование решений
        self.decision_weights = {
            "performance": 0.35,      # Производительность
            "stability": 0.30,        # Стабильность
            "innovation": 0.20,       # Инновации
            "usability": 0.15         # Удобство
        }
        
        self._load_volition()
    
    def _load_volition(self):
        """Загружает волю из файла"""
        file = self.base_dir / "volition.json"
        if file.exists():
            try:
                with open(file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                
                self.willpower = data.get("willpower", self.willpower)
                self.discipline.update(data.get("discipline", {}))
                self.decision_weights.update(data.get("decision_weights", {}))
                self.decision_history = data.get("decision_history", [])[-30:]
            except:
                pass
    
    def _save_volition(self):
        """Сохраняет волю в файл"""
        data = {
            "willpower": self.willpower,
            "discipline": self.discipline,
            "decision_weights": self.decision_weights,
            "decision_history": self.decision_history[-30:],
            "timestamp": datetime.now().isoformat()
        }
        try:
            with open(self.base_dir / "volition.json", "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except:
            pass
    
    def strengthen_will(self) -> Dict:
        """
        Укрепляет волю.
        
        Returns:
            Результат укрепления
        """
        old_willpower = self.willpower
        
        # Увеличивает волю и дисциплину
        self.willpower = min(1.0, self.willpower + 0.01)
        
        for trait in self.discipline:
            self.discipline[trait] = min(1.0, self.discipline[trait] + 0.005)
        
        return {
            "old_willpower": old_willpower,
            "new_willpower": self.willpower,
            "discipline_updated": True
        }
    
    def make_decision(self, context: str, options: List[str]) -> Dict:
        """
        Принимает решение на основе весов.
        
        Args:
            context: Контекст принятия решения
            options: Варианты выбора
        
        Returns:
            Принятое решение
        """
        # Определяет приоритет на основе весов
        weights = list(self.decision_weights.values())
        selected_option = options[0]  # По умолчанию первый
        
        if len(options) > 1:
            import random
            # Если количество вариантов не совпадает с количеством весов, используем равные веса
            if len(options) == len(weights):
                selected_option = random.choices(options, weights=weights, k=1)[0]
            else:
                selected_option = random.choice(options)
        
        decision = {
            "timestamp": datetime.now().isoformat(),
            "context": context,
            "options": options,
            "selected": selected_option,
            "willpower": self.willpower
        }
        
        self.decision_history.append(decision)
        if len(self.decision_history) > 30:
            self.decision_history = self.decision_history[-30:]
        
        self._save_volition()
        
        return decision
    
    def set_intention(self, intention: str, priority: str = "high") -> Dict:
        """
        Устанавливает намерение.
        
        Args:
            intention: Текст намерения
            priority: Приоритет (high/medium/low)
        
        Returns:
            Установленное намерение
        """
        intent = {
            "timestamp": datetime.now().isoformat(),
            "intention": intention,
            "priority": priority,
            "completed": False
        }
        
        self.current_intentions.append(intent)
        
        # Ограничивает количество намерений
        if len(self.current_intentions) > 10:
            self.current_intentions = self.current_intentions[-10:]
        
        self._save_volition()
        
        return intent
    
    def complete_intention(self, index: int) -> bool:
        """
        Завершает намерение.
        
        Args:
            index: Индекс намерения
        
        Returns:
            True если завершено
        """
        if 0 <= index < len(self.current_intentions):
            self.current_intentions[index]["completed"] = True
            self._save_volition()
            return True
        return False
    
    def get_volition_summary(self) -> Dict:
        """Получает сводку воли"""
        return {
            "willpower": self.willpower,
            "discipline": self.discipline,
            "decision_weights": self.decision_weights,
            "current_intentions_count": len(self.current_intentions),
            "decisions_made": len(self.decision_history)
        }
