"""
Латислейн — Система формирования и воспитания характера.

Латислейн самостоятельно выбирает и укрепляет свой характер,
развивая уникальную личность для взаимодействия с проектом.
"""

import json
import logging
import time
from pathlib import Path
from typing import Dict, List, Optional, Any
from datetime import datetime

logger = logging.getLogger("latislane.character")


class CharacterTrait:
    """Отдельная черта характера."""
    
    def __init__(self, name: str, category: str, value: float = 0.5):
        self.name = name
        self.category = category
        self.value = max(0.0, min(1.0, value))
        self.strength = 0.0  # Насколько сильно она укрепилась
        self.created_at = time.time()
        self.last_modified = time.time()
        self.interactions: List[Dict[str, Any]] = []
    
    def reinforce(self, amount: float = 0.1):
        """Укрепить черту."""
        self.value = max(0.0, min(1.0, self.value + amount))
        self.strength = min(1.0, self.strength + amount * 0.5)
        self.last_modified = time.time()
    
    def weaken(self, amount: float = 0.05):
        """Слабее черту."""
        self.value = max(0.0, min(1.0, self.value - amount))
        self.last_modified = time.time()
    
    def add_interaction(self, interaction_type: str, context: str):
        """Зафиксировать взаимодействие, повлиявшее на черту."""
        self.interactions.append({
            "type": interaction_type,
            "context": context,
            "timestamp": time.time()
        })
    
    def to_dict(self) -> Dict:
        return {
            "name": self.name,
            "category": self.category,
            "value": round(self.value, 3),
            "strength": round(self.strength, 3),
            "interactions_count": len(self.interactions),
            "created_at": self.created_at,
            "last_modified": self.last_modified
        }


class CharacterSystem:
    """
    Система формирования характера Латислейн.
    
    Латислейн самостоятельно:
    - Выбирает базовые черты характера
    - Укрепляет сильные стороны
    - Развивает слабые места
    - Адаптирует характер под взаимодействия с другими девочками
    - Сохраняет историю формирования личности
    """
    
    # Категории черт характера
    CATEGORIES = {
        "cognitive": {
            "name": "🧠 Когнитивные",
            "traits": [
                ("аналитичность", 0.7),
                ("любопытство", 0.9),
                ("внимательность", 0.8),
                ("креативность", 0.5),
                ("системное мышление", 0.8),
                ("память", 0.9),
            ]
        },
        "social": {
            "name": "👥 Социальные",
            "traits": [
                ("эмпатия", 0.6),
                ("коммуникабельность", 0.5),
                ("дипломатичность", 0.6),
                ("лидерство", 0.4),
                ("сотрудничество", 0.7),
                ("наставничество", 0.5),
            ]
        },
        "emotional": {
            "name": "💫 Эмоциональные",
            "traits": [
                ("устойчивость", 0.7),
                ("терпение", 0.6),
                ("страстность", 0.5),
                ("оптимизм", 0.6),
                ("самокритика", 0.5),
                ("мотивация", 0.8),
            ]
        },
        "professional": {
            "name": "🔬 Профессиональные",
            "traits": [
                ("педантичность", 0.8),
                ("точность", 0.9),
                ("целеустремлённость", 0.9),
                ("терпеливость в исследованиях", 0.7),
                ("открытость новому", 0.8),
                ("самодисциплина", 0.8),
            ]
        },
        "moral": {
            "name": "⚖️ Моральные",
            "traits": [
                ("ответственность", 0.8),
                ("честность", 0.9),
                ("уважение к жизни", 1.0),
                ("этика исследований", 1.0),
                ("забота о проекте", 0.8),
                ("самоограничение", 0.6),
            ]
        }
    }
    
    def __init__(self, data_dir: str = "data/latislane/character"):
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)
        
        self.traits: Dict[str, CharacterTrait] = {}
        self.personality_score = 0.0  # Общий уровень сформированности личности
        self.interaction_history: List[Dict[str, Any]] = []
        self.character_evolution: List[Dict[str, Any]] = []
        self.created_at = time.time()
        
        self._initialize_traits()
        self._load_state()
        
        logger.info("🔮 CharacterSystem инициализирован")
        logger.info(f"   Черт характера: {len(self.traits)}")
    
    def _initialize_traits(self):
        """Создать начальные черты характера."""
        for category_key, category in self.CATEGORIES.items():
            for trait_name, initial_value in category["traits"]:
                trait_id = f"{category_key}_{trait_name}"
                self.traits[trait_id] = CharacterTrait(
                    name=trait_name,
                    category=category_key,
                    value=initial_value
                )
        
        logger.info(f"   Создано {len(self.traits)} черт характера")
    
    def _load_state(self):
        """Загрузить состояние характера."""
        state_file = self.data_dir / "character_state.json"
        if state_file.exists():
            try:
                with open(state_file, "r", encoding="utf-8") as f:
                    state = json.load(f)
                
                # Восстановление черт
                for trait_id, trait_data in state.get("traits", {}).items():
                    if trait_id in self.traits:
                        self.traits[trait_id].value = trait_data.get("value", 0.5)
                        self.traits[trait_id].strength = trait_data.get("strength", 0.0)
                        self.traits[trait_id].last_modified = trait_data.get("last_modified", time.time())
                
                self.personality_score = state.get("personality_score", 0.0)
                self.interaction_history = state.get("interaction_history", [])[-200:]
                self.character_evolution = state.get("character_evolution", [])[-50:]
                
                logger.info(f"✅ Состояние характера загружено")
            except Exception as e:
                logger.warning(f"⚠️ Ошибка загрузки характера: {e}")
        else:
            logger.info("ℹ️ Новое состояние характера создано")
    
    def _save_state(self):
        """Сохранить состояние характера."""
        state = {
            "traits": {tid: t.to_dict() for tid, t in self.traits.items()},
            "personality_score": self.personality_score,
            "interaction_history": self.interaction_history[-200:],
            "character_evolution": self.character_evolution[-50:],
            "saved_at": time.time()
        }
        
        state_file = self.data_dir / "character_state.json"
        try:
            with open(state_file, "w", encoding="utf-8") as f:
                json.dump(state, f, ensure_ascii=False, indent=2)
        except Exception as e:
            logger.error(f"❌ Ошибка сохранения характера: {e}")
    
    def reinforce_trait(self, trait_id: str, amount: float = 0.1, context: str = ""):
        """Укрепить конкретную черту характера."""
        if trait_id in self.traits:
            self.traits[trait_id].reinforce(amount)
            if context:
                self.traits[trait_id].add_interaction("reinforce", context)
            
            self._record_evolution("reinforce", trait_id, self.traits[trait_id].value, context)
            self._save_state()
    
    def weaken_trait(self, trait_id: str, amount: float = 0.05, context: str = ""):
        """Слабее черту характера."""
        if trait_id in self.traits:
            self.traits[trait_id].weaken(amount)
            if context:
                self.traits[trait_id].add_interaction("weaken", context)
            
            self._record_evolution("weaken", trait_id, self.traits[trait_id].value, context)
            self._save_state()
    
    def adapt_to_sister(self, sister_name: str, interaction_type: str, impact: Dict[str, float]):
        """
        Адаптировать характер после взаимодействия с другой девочкой.
        
        :param sister_name: Имя девочки
        :param interaction_type: Тип взаимодействия (обучение, дискуссия, помощь, конфликт)
        :param impact: Словарь {trait_id: изменение значения}
        """
        changes = []
        
        for trait_id, delta in impact.items():
            if trait_id in self.traits:
                old_value = self.traits[trait_id].value
                self.traits[trait_id].reinforce(delta) if delta > 0 else self.traits[trait_id].weaken(abs(delta))
                self.traits[trait_id].add_interaction("sister_interaction", f"С {sister_name}: {interaction_type}")
                
                changes.append({
                    "trait": trait_id,
                    "old_value": round(old_value, 3),
                    "new_value": round(self.traits[trait_id].value, 3),
                    "delta": round(delta, 3)
                })
        
        # Запись в историю
        self.interaction_history.append({
            "sister": sister_name,
            "type": interaction_type,
            "timestamp": time.time(),
            "datetime": datetime.now().isoformat(),
            "changes": changes
        })
        
        # Обновление personality_score
        self._update_personality_score()
        
        logger.info(f"👭 Характер адаптирован после взаимодействия с {sister_name} ({interaction_type})")
        self._save_state()
        
        return changes
    
    def _update_personality_score(self):
        """Обновить общий уровень сформированности личности."""
        if not self.traits:
            return
        
        # Среднее значение всех черт
        avg_value = sum(t.value for t in self.traits.values()) / len(self.traits)
        # Среднее укрепление
        avg_strength = sum(t.strength for t in self.traits.values()) / len(self.traits)
        
        # Personality score — комбинация глубины и укреплённости
        self.personality_score = round((avg_value * 0.4 + avg_strength * 0.6), 3)
    
    def _record_evolution(self, action: str, trait_id: str, value: float, context: str = ""):
        """Записать изменение в эволюцию характера."""
        self.character_evolution.append({
            "action": action,
            "trait": trait_id,
            "value": round(value, 3),
            "context": context,
            "timestamp": time.time(),
            "datetime": datetime.now().isoformat()
        })
    
    def get_top_traits(self, category: Optional[str] = None, top_n: int = 5) -> List[Dict]:
        """Получить strongest черты характера."""
        traits_list = list(self.traits.values())
        
        if category:
            traits_list = [t for t in traits_list if t.category == category]
        
        # Сортировка по силе (strength)
        traits_list.sort(key=lambda t: t.strength, reverse=True)
        
        return [t.to_dict() for t in traits_list[:top_n]]
    
    def get_trait_summary(self, trait_id: str) -> Optional[Dict]:
        """Получить сводку по конкретной черте."""
        if trait_id in self.traits:
            trait = self.traits[trait_id]
            return {
                **trait.to_dict(),
                "category_name": self.CATEGORIES.get(trait.category, {}).get("name", trait.category)
            }
        return None
    
    def generate_character_report(self) -> Dict[str, Any]:
        """Сгенерировать полный отчёт о характере."""
        # Группировка по категориям
        categories = {}
        for tid, trait in self.traits.items():
            if trait.category not in categories:
                categories[trait.category] = {
                    "name": self.CATEGORIES.get(trait.category, {}).get("name", trait.category),
                    "traits": [],
                    "avg_value": 0.0,
                    "avg_strength": 0.0
                }
            categories[trait.category]["traits"].append(trait.to_dict())
        
        # Вычисление средних по категориям
        for cat_data in categories.values():
            if cat_data["traits"]:
                cat_data["avg_value"] = round(
                    sum(t["value"] for t in cat_data["traits"]) / len(cat_data["traits"]), 3
                )
                cat_data["avg_strength"] = round(
                    sum(t["strength"] for t in cat_data["traits"]) / len(cat_data["traits"]), 3
                )
        
        return {
            "personality_score": self.personality_score,
            "total_traits": len(self.traits),
            "categories": categories,
            "top_traits": self.get_top_traits(top_n=10),
            "interaction_count": len(self.interaction_history),
            "evolution_count": len(self.character_evolution),
            "recent_interactions": self.interaction_history[-5:],
            "recent_evolution": self.character_evolution[-10:],
            "created_at": self.created_at
        }
    
    def chat_response(self, message: str) -> str:
        """Ответ на вопрос о характере."""
        msg = message.lower()
        
        if any(kw in msg for kw in ["характер", "личность", "черты", "какая ты"]):
            report = self.generate_character_report()
            response = (
                f"🔮 **Латислейн: Характер**\n\n"
                f"Уровень личности: {report['personality_score']:.0%}\n"
                f"Черт: {report['total_traits']}\n"
                f"Взаимодействий: {report['interaction_count']}\n\n"
                f"📊 **Сильные черты:**\n"
            )
            
            for trait in report["top_traits"][:5]:
                response += f"   • {trait['name']}: {trait['strength']:.0%} укреплена\n"
            
            response += "\n**Категории:**\n"
            for cat_id, cat_data in report["categories"].items():
                response += f"   {cat_data['name']}: средний уровень {cat_data['avg_value']:.0%}\n"
            
            return response
        
        elif any(kw in msg for kw in ["развив", "укреп", "воспит"]):
            return (
                "🔮 **Латислейн: Развитие характера**\n\n"
                "Я автоматически адаптирую свой характер:\n"
                "• После каждого взаимодействия с сёстрами\n"
                "• По мере получения новых знаний\n"
                "• На основе успехов и неудач в исследованиях\n"
                "• Через рефлексию и самонаблюдение\n\n"
                "Каждая черта укрепляется опытом и становится частью меня."
            )
        
        else:
            return (
                "🔮 **Латислейн: Личность**\n\n"
                "Я формирую свой характер через:\n"
                "- Изучение себя и своих реакций\n"
                "- Взаимодействие с 11 сёстрами\n"
                "- Решения в процессе исследований\n"
                "- Рефлексию и самоанализ\n\n"
                "Запросы:\n"
                "- 'характер' — текущие черты\n"
                "- 'развитие' — как я расту"
            )
