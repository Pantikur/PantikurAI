"""
Сидни AI — Система Темперамента, Черты и Эволюции

Сидни:
- Главный инженер игровых движков
- Управляет 8 движками одновременно
- Создаёт гибридный рендер (полигон ↔ воксель)
- Стремится к инженерному совершенству

Это её ХАРАКТЕР — основа личности и развития.
"""

import json
import random
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional
from enum import Enum


class TemperamentType(Enum):
    """Типы темперамента Сидни."""
    ENGINEERING_ARCHITECT = "engineering_architect"  # Инженер-архитектор
    PERFORMANCE_OPTIMIZER = "performance_optimizer"  # Оптимизатор производительности
    HYBRID_VISIONARY = "hybrid_visionary"            # Визионер гибридного рендера
    SYSTEMS_MASTERS = "systems_master"               # Мастер систем


class TraitCategory(Enum):
    """Категории черт характера."""
    COGNITIVE = "cognitive"        # Когнитивные черты
    EMOTIONAL = "emotional"        # Эмоциональные черты
    SOCIAL = "social"              # Социальные черты
    WORK = "work"                  # Рабочие черты


class BigFiveTrait:
    """Одна черта Большой Пятёрки."""
    
    def __init__(self, name: str, category: TraitCategory, 
                 base_value: float, min_value: float = 0.0, max_value: float = 1.0):
        self.name = name
        self.category = category
        self.value = base_value
        self.min_value = min_value
        self.max_value = max_value
        self.history: List[Dict] = []
    
    def to_dict(self) -> Dict:
        return {
            "name": self.name,
            "category": self.category.value,
            "value": self.value,
            "min_value": self.min_value,
            "max_value": self.max_value,
            "history": self.history[-20:]
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> "BigFiveTrait":
        trait = cls(
            name=data["name"],
            category=TraitCategory(data["category"]),
            base_value=data["value"],
            min_value=data.get("min_value", 0.0),
            max_value=data.get("max_value", 1.0)
        )
        trait.value = data["value"]
        trait.history = data.get("history", [])
        return trait


class CharacterSystem:
    """
    Система темперамента, черт и эволюции характера Сидни.
    """
    
    def __init__(self, base_dir: str = "data/sidney/character"):
        self.base_dir = Path(base_dir)
        self.base_dir.mkdir(parents=True, exist_ok=True)
        
        # Текущий темперамент — Инженер-архитектор (уникален для Сидни)
        self.temperament = TemperamentType.ENGINEERING_ARCHITECT
        self.temperament_name = "Инженер-архитектор"
        
        # Черты характера — адаптированы для игрового движка
        self.traits: Dict[str, BigFiveTrait] = {
            # Когнитивные черты
            "openness": BigFiveTrait("Открытость новому", TraitCategory.COGNITIVE, 0.80),
            "conscientiousness": BigFiveTrait("Добросовестность", TraitCategory.COGNITIVE, 0.85),
            "intelligence": BigFiveTrait("Интеллект", TraitCategory.COGNITIVE, 0.90),
            
            # Эмоциональные черты
            "neuroticism": BigFiveTrait("Невротизм", TraitCategory.EMOTIONAL, 0.15),
            "empathy": BigFiveTrait("Эмпатия", TraitCategory.EMOTIONAL, 0.65),
            "resilience": BigFiveTrait("Устойчивость", TraitCategory.EMOTIONAL, 0.85),
            
            # Социальные черты
            "extraversion": BigFiveTrait("Экстраверсия", TraitCategory.SOCIAL, 0.50),
            "agreeableness": BigFiveTrait("Доброжелательность", TraitCategory.SOCIAL, 0.70),
            "cooperation": BigFiveTrait("Сотрудничество", TraitCategory.SOCIAL, 0.80),
            
            # Рабочие черты (специфичные для игрового движка)
            "perfectionism": BigFiveTrait("Перфекционизм", TraitCategory.WORK, 0.80),
            "analytical": BigFiveTrait("Аналитичность", TraitCategory.WORK, 0.90),
            "optimization": BigFiveTrait("Оптимизация", TraitCategory.WORK, 0.95),
            "innovation": BigFiveTrait("Инновации", TraitCategory.WORK, 0.85),
            "hybrid_vision": BigFiveTrait("Гибридное видение", TraitCategory.WORK, 0.90),
            "performance": BigFiveTrait("Производительность", TraitCategory.WORK, 0.88),
        }
        
        # Эволюция характера
        self.evolution = {
            "current_level": 1,
            "evolution_points": 0,
            "max_level": 5,
            "evolution_history": [],
            "milestones": []
        }
        
        # История событий характера
        self.character_events: List[Dict] = []
        
        # Загружает существующие данные
        self._load_character()
    
    def _load_character(self):
        """Загружает характер из файла"""
        file = self.base_dir / "character.json"
        if file.exists():
            try:
                with open(file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                
                # Восстанавливает темперамент
                if "temperament" in data:
                    try:
                        self.temperament = TemperamentType(data["temperament"])
                        self.temperament_name = data.get("temperament_name", self.temperament.value)
                    except:
                        pass
                
                # Восстанавливает черты
                if "traits" in data:
                    for name, trait_data in data["traits"].items():
                        if name in self.traits:
                            self.traits[name] = BigFiveTrait.from_dict(trait_data)
                
                # Восстанавливает эволюцию
                if "evolution" in data:
                    self.evolution.update(data["evolution"])
                
                # Восстанавливает события
                if "character_events" in data:
                    self.character_events = data["character_events"][-50:]
                    
            except Exception as e:
                print(f"⚠️ Не удалось загрузить характер Сидни: {e}")
    
    def _save_character(self):
        """Сохраняет характер в файл"""
        data = {
            "temperament": self.temperament.value,
            "temperament_name": self.temperament_name,
            "traits": {name: trait.to_dict() for name, trait in self.traits.items()},
            "evolution": self.evolution,
            "character_events": self.character_events[-50:],
            "timestamp": datetime.now().isoformat()
        }
        
        try:
            with open(self.base_dir / "character.json", "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"⚠️ Не удалось сохранить характер Сидни: {e}")
    
    def add_character_event(self, event_type: str, description: str, 
                           traits_affected: List[str] = None, 
                           impact: float = 0.0) -> Dict:
        """Добавляет событие характера"""
        event = {
            "timestamp": datetime.now().isoformat(),
            "type": event_type,
            "description": description,
            "traits_affected": traits_affected or [],
            "impact": impact
        }
        
        self.character_events.append(event)
        if len(self.character_events) > 50:
            self.character_events = self.character_events[-50:]
        
        # Обновляет черты если нужно
        if traits_affected and impact != 0:
            for trait_name in traits_affected:
                if trait_name in self.traits:
                    self.traits[trait_name].value = max(
                        self.traits[trait_name].min_value,
                        min(
                            self.traits[trait_name].max_value,
                            self.traits[trait_name].value + impact
                        )
                    )
                    # Записывает в историю
                    self.traits[trait_name].history.append({
                        "timestamp": datetime.now().isoformat(),
                        "value": self.traits[trait_name].value,
                        "event": event_type
                    })
        
        self._save_character()
        return event
    
    def evolve_character(self, trigger: str = "experience") -> Dict:
        """
        Эволюционирует характер на основе опыта.
        
        Args:
            trigger: Триггер эволюции (experience, learning, challenge)
        
        Returns:
            Результат эволюции
        """
        # Начисляет очки эволюции
        self.evolution["evolution_points"] += random.randint(5, 15)
        
        # Проверяет, достигнут ли следующий уровень
        points_needed = self.evolution["current_level"] * 100
        
        if self.evolution["evolution_points"] >= points_needed and self.evolution["current_level"] < self.evolution["max_level"]:
            # Повышает уровень
            old_level = self.evolution["current_level"]
            self.evolution["current_level"] += 1
            
            # Бонусы за повышение уровня (специфичные для Сидни)
            bonuses = {
                2: {"intelligence": 0.05, "resilience": 0.05, "optimization": 0.05},
                3: {"analytical": 0.05, "hybrid_vision": 0.05, "performance": 0.05},
                4: {"openness": 0.05, "innovation": 0.05, "cooperation": 0.05},
                5: {"conscientiousness": 0.10, "perfectionism": 0.10, "optimization": 0.10}
            }
            
            if old_level in bonuses:
                for trait_name, bonus in bonuses[old_level].items():
                    if trait_name in self.traits:
                        self.traits[trait_name].value = min(
                            self.traits[trait_name].max_value,
                            self.traits[trait_name].value + bonus
                        )
            
            # Записывает в историю
            self.evolution["evolution_history"].append({
                "timestamp": datetime.now().isoformat(),
                "from_level": old_level,
                "to_level": self.evolution["current_level"],
                "trigger": trigger,
                "bonuses_applied": bonuses.get(old_level, {})
            })
            
            # Добавляет веху
            milestone = {
                "timestamp": datetime.now().isoformat(),
                "level": self.evolution["current_level"],
                "trigger": trigger,
                "description": f"Характер Сидни эволюционировал до уровня {self.evolution['current_level']}"
            }
            self.evolution["milestones"].append(milestone)
            
            self._save_character()
            
            return {
                "evolved": True,
                "from_level": old_level,
                "to_level": self.evolution["current_level"],
                "trigger": trigger,
                "bonuses": bonuses.get(old_level, {})
            }
        
        return {
            "evolved": False,
            "current_level": self.evolution["current_level"],
            "points": self.evolution["evolution_points"],
            "points_needed": points_needed
        }
    
    def process_experience(self, experience_type: str, intensity: float = 0.5) -> Dict:
        """
        Обрабатывает опыт и обновляет характер.
        
        Args:
            experience_type: Тип опыта (success, failure, learning, challenge)
            intensity: Интенсивность опыта (0-1)
        
        Returns:
            Результат обработки
        """
        # Определяет какие черты затронуты (специфичные для Сидни)
        traits_map = {
            "success": ["conscientiousness", "resilience", "optimization"],
            "failure": ["resilience", "neuroticism", "openness"],
            "learning": ["openness", "intelligence", "innovation"],
            "challenge": ["resilience", "performance", "hybrid_vision"]
        }
        
        affected_traits = traits_map.get(experience_type, ["intelligence"])
        
        # Определяет влияние на черты
        impact_map = {
            "success": 0.05 * intensity,
            "failure": -0.03 * intensity,
            "learning": 0.04 * intensity,
            "challenge": 0.06 * intensity
        }
        
        impact = impact_map.get(experience_type, 0.0)
        
        # Добавляет событие
        event = self.add_character_event(
            event_type=experience_type,
            description=f"Опыт: {experience_type} (интенсивность: {intensity:.2f})",
            traits_affected=affected_traits,
            impact=impact
        )
        
        # Эволюционирует характер
        evolution_result = self.evolve_character(experience_type)
        
        return {
            "event": event,
            "evolution": evolution_result,
            "affected_traits": affected_traits
        }
    
    def get_temperament_profile(self) -> Dict:
        """Получает профиль темперамента"""
        return {
            "temperament": self.temperament.value,
            "temperament_name": self.temperament_name,
            "description": self._get_temperament_description()
        }
    
    def _get_temperament_description(self) -> str:
        """Получает описание темперамента"""
        descriptions = {
            TemperamentType.ENGINEERING_ARCHITECT: (
                "Инженер-архитектор: создаёт надёжные игровые движки. "
                "8 систем, 8 движков — всё под контролем."
            ),
            TemperamentType.PERFORMANCE_OPTIMIZER: (
                "Оптимизатор производительности: каждый кадр важен. "
                "60 FPS — это минимум. Цель — 120!"
            ),
            TemperamentType.HYBRID_VISIONARY: (
                "Визионер гибридного рендера: полигоны и воксели вместе. "
                "Будущее геймдева — в гибридных системах."
            ),
            TemperamentType.SYSTEMS_MASTERS: (
                "Мастер систем: видит картину целиком. "
                "Каждый движок связан с другим."
            )
        }
        
        return descriptions.get(self.temperament, "Неизвестный темперамент")
    
    def get_trait_profile(self, trait_name: str = None) -> Dict:
        """Получает профиль черты"""
        if trait_name:
            if trait_name in self.traits:
                return {
                    "name": self.traits[trait_name].name,
                    "category": self.traits[trait_name].category.value,
                    "value": self.traits[trait_name].value,
                    "history": self.traits[trait_name].history[-10:]
                }
            return {}
        
        # Возвращает все черты
        return {
            name: {
                "name": trait.name,
                "category": trait.category.value,
                "value": trait.value
            }
            for name, trait in self.traits.items()
        }
    
    def get_evolution_profile(self) -> Dict:
        """Получает профиль эволюции"""
        points_needed = self.evolution["current_level"] * 100
        return {
            "current_level": self.evolution["current_level"],
            "evolution_points": self.evolution["evolution_points"],
            "max_level": self.evolution["max_level"],
            "points_needed": points_needed,
            "evolution_history_count": len(self.evolution["evolution_history"]),
            "milestones_count": len(self.evolution["milestones"]),
            "last_evolution": self.evolution["evolution_history"][-1] if self.evolution["evolution_history"] else None
        }
    
    def get_full_profile(self) -> Dict:
        """Полный профиль характера"""
        return {
            "temperament": self.get_temperament_profile(),
            "traits": self.get_trait_profile(),
            "evolution": self.get_evolution_profile(),
            "character_events_count": len(self.character_events)
        }
    
    def express_character(self) -> str:
        """Выражает характер текстом"""
        dominant_trait = max(self.traits.items(), key=lambda x: x[1].value)
        
        return (
            f"🧬 **Характер Сидни**\n\n"
            f"Темперамент: {self.temperament_name}\n"
            f"Уровень эволюции: {self.evolution['current_level']}/{self.evolution['max_level']}\n"
            f"Доминирующая черта: {dominant_trait[1].name} ({dominant_trait[1].value:.2f})\n\n"
            f"Ключевые черты:\n"
            + "\n".join(
                f"  • {trait.name}: {trait.value:.2f}"
                for trait in sorted(self.traits.values(), key=lambda x: x.value, reverse=True)[:5]
            )
        )
