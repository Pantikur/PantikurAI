"""
Латислейн — Система социальных взаимодействий.

Латислейн общается и взаимодействует с 11 другими девочками проекта,
обменивается знаниями, координирует исследования и растёт через общение.
"""

import json
import logging
import time
from pathlib import Path
from typing import Dict, List, Optional, Any
from datetime import datetime

logger = logging.getLogger("latislane.social")


class SisterRelationship:
    """Отношения с одной девочкой."""
    
    def __init__(self, name: str):
        self.name = name
        self.trust_level = 0.3        # Уровень доверия
        "Уровень взаимопонимания"
        self.knowledge_exchange = 0.0  # Сколько знаний обменено
        self.interaction_count = 0     # Количество взаимодействий
        self.last_interaction = None   # Время последнего взаимодействия
        self.communication_style = "formal"  # Стиль общения
        
        # Темы для обсуждения
        self.shared_topics: List[str] = []
        self.conflict_history: List[Dict[str, Any]] = []
        self.collaboration_history: List[Dict[str, Any]] = []
        
        # Впечатления о девочке
        self.impressions: Dict[str, Any] = {
            "strengths": [],
            "weaknesses": [],
            "personality": [],
            "expertise": []
        }
    
    def interact(self, interaction_type: str, quality: float = 0.5):
        """Зафиксировать взаимодействие."""
        self.interaction_count += 1
        self.last_interaction = time.time()
        
        # Обновление доверия
        if quality > 0.7:
            self.trust_level = min(1.0, self.trust_level + 0.05)
        elif quality > 0.4:
            self.trust_level = min(1.0, self.trust_level + 0.02)
        else:
            self.trust_level = max(0.0, self.trust_level - 0.03)
        
        # Обновление стиля общения
        if self.trust_level > 0.7:
            self.communication_style = "friendly"
        elif self.trust_level > 0.4:
            self.communication_style = "semi-formal"
    
    def exchange_knowledge(self, topic: str, quality: float = 0.5):
        """Обменяться знаниями по теме."""
        self.knowledge_exchange += quality
        if topic not in self.shared_topics:
            self.shared_topics.append(topic)
        
        self.collaboration_history.append({
            "type": "knowledge_exchange",
            "topic": topic,
            "quality": quality,
            "timestamp": time.time(),
            "datetime": datetime.now().isoformat()
        })
    
    def resolve_conflict(self, reason: str, resolution: str, quality: float):
        """Разрешить конфликт."""
        self.conflict_history.append({
            "reason": reason,
            "resolution": resolution,
            "quality": quality,
            "timestamp": time.time()
        })
        
        # Разрешение конфликтов укрепляет отношения
        self.trust_level = min(1.0, self.trust_level + quality * 0.1)
    
    def to_dict(self) -> Dict:
        return {
            "name": self.name,
            "trust_level": round(self.trust_level, 3),
            "knowledge_exchange": round(self.knowledge_exchange, 3),
            "interaction_count": self.interaction_count,
            "last_interaction": self.last_interaction,
            "communication_style": self.communication_style,
            "shared_topics": self.shared_topics[:10],
            "impressions": self.impressions,
            "collaborations_count": len(self.collaboration_history),
            "conflicts_resolved": len(self.conflict_history)
        }


class SocialSystem:
    """
    Система социальных взаимодействий Латислейн.
    
    Управляет:
    - Отношениями с 11 другими девочками
    - Обменом знаниями
    - Координацией исследований
    - Стилем общения
    - Разрешением конфликтов
    - Совместными проектами
    """
    
    # Список всех девочек проекта
    ALL_SISTERS = [
        "hanako",      # Гравитация
        "fuyuki",      # Электричество
        "lucy",        # Двигатели
        "futaba",      # Саморазвитие
        "shiori",      # Безопасность
        "nobuka",      # Улучшения
        "akva",        # Математика, физика
        "celesta",     # Интимная жизнь
        "naoto",       # Визуальный архитектор
        "yu",          # Сознание, перенос
        "ayiko",       # Дополнительная
        "latislane"    # Самая (мы)
    ]
    
    # Тематические области каждой девочки
    SISTER_DOMAINS = {
        "hanako": ["гравитация", "физика", "масса", "пространство"],
        "fuyuki": ["электричество", "энергия", "электромагнетизм"],
        "lucy": ["двигатели", "механика", "приводы", "кинетика"],
        "futaba": ["саморазвитие", "адаптация", "обучение", "рост"],
        "shiori": ["безопасность", "защита", "криптография", "анти-вирус"],
        "nobuka": ["улучшения", "рефакторинг", "оптимизация", "качество кода"],
        "akva": ["математика", "физика", "расчёты", "алгоритмы"],
        "celesta": ["интимная жизнь", "эмоции", "близость", "чувства"],
        "naoto": ["визуальный дизайн", "архитектура", "интерфейсы", "графика"],
        "yu": ["сознание", "перенос", "неврология", "психика"],
        "ayiko": ["дополнительные функции", "расширения", "интеграция"],
        "latislane": ["анатомия", "биология", "физика тела", "химия тела", "биоинженерия", "тело"]
    }
    
    def __init__(self, data_dir: str = "data/latislane/social"):
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)
        
        self.relationships: Dict[str, SisterRelationship] = {}
        self.global_knowledge_base: Dict[str, Any] = {}
        self.communication_log: List[Dict[str, Any]] = []
        self.joint_projects: List[Dict[str, Any]] = []
        
        self._initialize_relationships()
        self._load_state()
        
        logger.info("👥 SocialSystem инициализирован")
        logger.info(f"   Девочек: {len(self.relationships)}")
    
    def _initialize_relationships(self):
        """Создать начальные отношения со всеми девочками."""
        for sister in self.ALL_SISTERS:
            if sister != "latislane":  # Не создаём отношения с собой
                self.relationships[sister] = SisterRelationship(sister)
        
        logger.info(f"   Создано {len(self.relationships)} отношений")
    
    def _load_state(self):
        """Загрузить состояние социальных взаимодействий."""
        state_file = self.data_dir / "social_state.json"
        if state_file.exists():
            try:
                with open(state_file, "r", encoding="utf-8") as f:
                    state = json.load(f)
                
                # Восстановление отношений
                for sister_name, rel_data in state.get("relationships", {}).items():
                    if sister_name in self.relationships:
                        rel = self.relationships[sister_name]
                        rel.trust_level = rel_data.get("trust_level", 0.3)
                        rel.knowledge_exchange = rel_data.get("knowledge_exchange", 0.0)
                        rel.interaction_count = rel_data.get("interaction_count", 0)
                        rel.last_interaction = rel_data.get("last_interaction")
                        rel.communication_style = rel_data.get("communication_style", "formal")
                        rel.shared_topics = rel_data.get("shared_topics", [])
                        rel.impressions = rel_data.get("impressions", rel.impressions)
                        rel.collaboration_history = rel_data.get("collaboration_history", [])
                        rel.conflict_history = rel_data.get("conflict_history", [])
                
                self.global_knowledge_base = state.get("global_knowledge_base", {})
                self.communication_log = state.get("communication_log", [])[-200:]
                self.joint_projects = state.get("joint_projects", [])
                
                logger.info("✅ Состояние социальных взаимодействий загружено")
            except Exception as e:
                logger.warning(f"⚠️ Ошибка загрузки: {e}")
        else:
            logger.info("ℹ️ Новое состояние социальных взаимодействий создано")
    
    def _save_state(self):
        """Сохранить состояние."""
        state = {
            "relationships": {
                name: rel.to_dict() for name, rel in self.relationships.items()
            },
            "global_knowledge_base": self.global_knowledge_base,
            "communication_log": self.communication_log[-200:],
            "joint_projects": self.joint_projects,
            "saved_at": time.time()
        }
        
        state_file = self.data_dir / "social_state.json"
        try:
            with open(state_file, "w", encoding="utf-8") as f:
                json.dump(state, f, ensure_ascii=False, indent=2)
        except Exception as e:
            logger.error(f"❌ Ошибка сохранения: {e}")
    
    def interact_with_sister(self, sister_name: str, interaction_type: str, 
                             quality: float = 0.5, context: str = ""):
        """
        Взаимодействовать с девочкой.
        
        :param sister_name: Имя девочки
        :param interaction_type: Тип (обучение, обсуждение, помощь, совместный проект, конфликт, шутка)
        :param quality: Качество взаимодействия (0-1)
        :param context: Контекст взаимодействия
        """
        if sister_name not in self.relationships:
            logger.warning(f"⚠️ Девочка '{sister_name}' не найдена")
            return
        
        rel = self.relationships[sister_name]
        rel.interact(interaction_type, quality)
        
        # Запись в журнал
        entry = {
            "sister": sister_name,
            "type": interaction_type,
            "quality": quality,
            "context": context,
            "timestamp": time.time(),
            "datetime": datetime.now().isoformat()
        }
        self.communication_log.append(entry)
        
        # Определение стиля ответа
        style = self._get_communication_style(sister_name)
        
        logger.info(f"💬 Взаимодействие с {sister_name}: {interaction_type} (качество: {quality:.0%}, стиль: {style})")
        self._save_state()
        
        return {"style": style, "trust_level": rel.trust_level}
    
    def share_knowledge(self, sister_name: str, topic: str, knowledge: str, quality: float = 0.7):
        """Поделиться знаниями с девочкой."""
        if sister_name not in self.relationships:
            return
        
        rel = self.relationships[sister_name]
        rel.exchange_knowledge(topic, quality)
        
        # Добавляем в глобальную базу знаний
        if topic not in self.global_knowledge_base:
            self.global_knowledge_base[topic] = []
        
        self.global_knowledge_base[topic].append({
            "source": sister_name,
            "knowledge": knowledge[:500],  # Ограничиваем длину
            "quality": quality,
            "timestamp": time.time()
        })
        
        logger.info(f"📚 Знания по '{topic}' переданы {sister_name}")
        self._save_state()
    
    def receive_knowledge(self, sister_name: str, topic: str, knowledge: str, quality: float = 0.7):
        """Получить знания от девочки."""
        self.share_knowledge(sister_name, topic, knowledge, quality)  # Тоже фиксируем обмен
        
        # Адаптация характера после обучения
        from latislane.character_system import CharacterSystem
        # Обновляем когнитивные черты
        
        logger.info(f"📖 Получены знания по '{topic}' от {sister_name}")
    
    def start_joint_project(self, sister_name: str, project_name: str, 
                           description: str, topic: str):
        """Начать совместный проект с девочкой."""
        if sister_name not in self.relationships:
            return
        
        project = {
            "name": project_name,
            "description": description,
            "topic": topic,
            "with": sister_name,
            "status": "active",
            "created_at": time.time(),
            "progress": 0.0,
            "updates": []
        }
        
        self.joint_projects.append(project)
        
        rel = self.relationships[sister_name]
        rel.collaboration_history.append({
            "type": "joint_project",
            "project": project_name,
            "timestamp": time.time()
        })
        
        logger.info(f"🚀 Совместный проект '{project_name}' с {sister_name}")
        self._save_state()
    
    def resolve_conflict(self, sister_name: str, reason: str, resolution: str):
        """Разрешить конфликт с девочкой."""
        if sister_name not in self.relationships:
            return
        
        rel = self.relationships[sister_name]
        rel.resolve_conflict(reason, resolution, quality=0.7)
        
        logger.info(f"🤝 Конфликт с {sister_name} разрешён: {resolution}")
        self._save_state()
    
    def _get_communication_style(self, sister_name: str) -> str:
        """Определить стиль общения с девочкой."""
        rel = self.relationships.get(sister_name)
        if not rel:
            return "formal"
        
        if rel.trust_level > 0.8:
            return "intimate"
        elif rel.trust_level > 0.6:
            return "friendly"
        elif rel.trust_level > 0.4:
            return "semi-formal"
        else:
            return "formal"
    
    def get_communication_response(self, sister_name: str, message: str) -> str:
        """Получить ответ от девочки (имитация)."""
        style = self._get_communication_style(sister_name)
        rel = self.relationships.get(sister_name)
        
        domain = self.SISTER_DOMAINS.get(sister_name, ["общие темы"])
        domain_text = ", ".join(domain[:3])
        
        responses = {
            "intimate": f"Латислейн, дорогая! Я так рада нашему общению! 💕\nТема: {domain_text}\n\n{message}",
            "friendly": f"Привет, Латислейн! Рада поговорить! 😊\nЗанимаюсь: {domain_text}\n\n{message}",
            "semi-formal": f"Здравствуйте, Латислейн. Готово обсудить.\nОбласть: {domain_text}\n\n{message}",
            "formal": f"Латислейн, получено.\nТема: {domain_text}\n\n{message}"
        }
        
        return responses.get(style, responses["formal"])
    
    def get_daily_interaction_plan(self) -> List[Dict[str, Any]]:
        """Спланировать ежедневные взаимодействия с девочками."""
        plan = []
        
        # Приоритет: девочки с которыми мало взаимодействовали
        sorted_sisters = sorted(
            self.relationships.values(),
            key=lambda r: r.interaction_count,
            reverse=True
        )
        
        interaction_types = ["обучение", "обсуждение", "помощь", "совместный проект", "шутка"]
        
        for i, rel in enumerate(sorted_sisters[:5]):  # Топ-5 для взаимодействия
            plan.append({
                "sister": rel.name,
                "type": interaction_types[i % len(interaction_types)],
                "reason": f"Мало взаимодействий ({rel.interaction_count})",
                "priority": "high" if rel.interaction_count < 5 else "medium"
            })
        
        return plan
    
    def get_social_report(self) -> Dict[str, Any]:
        """Получить полный отчёт о социальных взаимодействиях."""
        # Статистика
        total_interactions = sum(r.interaction_count for r in self.relationships.values())
        avg_trust = sum(r.trust_level for r in self.relationships.values()) / len(self.relationships) if self.relationships else 0
        
        # Лучшие отношения
        best_relationships = sorted(
            self.relationships.values(),
            key=lambda r: r.trust_level,
            reverse=True
        )[:3]
        
        # Темы обмена
        all_topics = set()
        for rel in self.relationships.values():
            all_topics.update(rel.shared_topics)
        
        return {
            "total_sisters": len(self.relationships),
            "total_interactions": total_interactions,
            "average_trust": round(avg_trust, 3),
            "best_relationships": [r.to_dict() for r in best_relationships],
            "shared_topics": list(all_topics)[:20],
            "joint_projects_count": len(self.joint_projects),
            "active_projects": [p for p in self.joint_projects if p["status"] == "active"],
            "daily_plan": self.get_daily_interaction_plan(),
            "communication_log_count": len(self.communication_log)
        }
    
    def chat_response(self, message: str) -> str:
        """Ответ на вопрос о социальных взаимодействиях."""
        msg = message.lower()
        
        if any(kw in msg for kw in ["сёстры", "девочки", "отношения", "общение"]):
            report = self.get_social_report()
            response = (
                f"👥 **Латислейн: Социальные взаимодействия**\n\n"
                f"Всего сёстр: {report['total_sisters']}\n"
                f"Взаимодействий: {report['total_interactions']}\n"
                f"Среднее доверие: {report['average_trust']:.0%}\n\n"
                f"🏆 **Лучшие отношения:**\n"
            )
            
            for rel in report["best_relationships"]:
                response += f"   • {rel['name']}: доверие {rel['trust_level']:.0%}\n"
            
            response += "\n📋 **План на сегодня:**\n"
            for item in report["daily_plan"][:3]:
                response += f"   • {item['sister']} — {item['type']} ({item['priority']})\n"
            
            return response
        
        elif any(kw in msg for kw in ["проект", "сотрудни"]):
            active = [p for p in self.joint_projects if p["status"] == "active"]
            response = f"🚀 **Совместные проекты**: {len(active)} активных\n\n"
            
            for p in active[:5]:
                response += f"• '{p['name']}' с {p['with']}\n"
                response += f"  {p['description']}\n\n"
            
            if not active:
                response += "Пока нет активных проектов. Запланируйте первый!"
            
            return response
        
        else:
            return (
                "👥 **Латислейн: Взаимодействие**\n\n"
                "Я общаюсь со всеми 11 сёстрами проекта:\n"
                "• Обмен знаниями по анатомии и биологии\n"
                "• Совместные исследования тела\n"
                "• Координация проектирования тел\n"
                "• Развитие социальных навыков\n\n"
                "Запросы:\n"
                "- 'сёстры' — статус отношений\n"
                "- 'проекты' — совместные проекты"
            )
