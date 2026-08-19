"""
Сидни AI — Система Памяти о Сёстрах и Контексте Общения

Сидни помнит:
- Каждый разговор с сёстрами
- Темы обсуждений (движки, системы, инженерия)
- Эмоциональный контекст
- Предпочтения и интересы
- Инженерные знания и открытия
- Исторические события Вугларста

Это её ПАМЯТЬ — хранилище опыта и связей.
"""

import json
import random
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple


class SidneyMemory:
    """
    Система памяти Сидни — хранение и обработка информации о сёстрах.
    """
    
    def __init__(self, base_dir: str = "data/sidney/memory"):
        self.base_dir = Path(base_dir)
        self.base_dir.mkdir(parents=True, exist_ok=True)
        
        # Память о каждой сестре
        self.sister_memories: Dict[str, Dict] = {}
        
        # Исторические события Вугларста
        self.history_events: List[Dict] = []
        
        # Контекст текущих разговоров
        self.conversation_contexts: Dict[str, Dict] = {}
        
        # Инженерные знания и открытия
        self.engineering_knowledge: List[Dict] = []
        
        # Загружает существующую память
        self._load_memory()
    
    def _load_memory(self):
        """Загружает память из файлов"""
        # Загружает память о сёстрах
        sisters_file = self.base_dir / "sister_memories.json"
        if sisters_file.exists():
            try:
                with open(sisters_file, "r", encoding="utf-8") as f:
                    self.sister_memories = json.load(f)
            except:
                self.sister_memories = {}
        
        # Загружает исторические события
        history_file = self.base_dir / "history_events.json"
        if history_file.exists():
            try:
                with open(history_file, "r", encoding="utf-8") as f:
                    self.history_events = json.load(f)
            except:
                self.history_events = []
        
        # Загружает контексты разговоров
        context_file = self.base_dir / "conversation_contexts.json"
        if context_file.exists():
            try:
                with open(context_file, "r", encoding="utf-8") as f:
                    self.conversation_contexts = json.load(f)
            except:
                self.conversation_contexts = {}
        
        # Загружает инженерные открытия
        discoveries_file = self.base_dir / "engineering_knowledge.json"
        if discoveries_file.exists():
            try:
                with open(discoveries_file, "r", encoding="utf-8") as f:
                    self.engineering_knowledge = json.load(f)
            except:
                self.engineering_knowledge = []
    
    def _save_sister_memory(self, sister: str):
        """Сохраняет память о сестре"""
        sisters_file = self.base_dir / "sister_memories.json"
        try:
            with open(sisters_file, "w", encoding="utf-8") as f:
                json.dump(self.sister_memories, f, ensure_ascii=False, indent=2)
        except:
            pass
    
    def _save_history_event(self):
        """Сохраняет исторические события"""
        history_file = self.base_dir / "history_events.json"
        try:
            with open(history_file, "w", encoding="utf-8") as f:
                json.dump(self.history_events[-100:], f, ensure_ascii=False, indent=2)
        except:
            pass
    
    def _save_context(self, sister: str):
        """Сохраняет контекст разговора"""
        context_file = self.base_dir / "conversation_contexts.json"
        try:
            with open(context_file, "w", encoding="utf-8") as f:
                json.dump(self.conversation_contexts, f, ensure_ascii=False, indent=2)
        except:
            pass
    
    def _save_engineering_knowledge(self):
        """Сохраняет инженерные знания"""
        knowledge_file = self.base_dir / "engineering_knowledge.json"
        try:
            with open(knowledge_file, "w", encoding="utf-8") as f:
                json.dump(self.engineering_knowledge[-50:], f, ensure_ascii=False, indent=2)
        except:
            pass
    
    # ================================================================
    #  ЗАПИСЬ В РАЗГОВОРЫ С СЁСТРАМИ
    # ================================================================
    
    def record_sister_chat(self, sister: str, topic: str, 
                          mood_before: str = "neutral",
                          mood_after: str = "neutral"):
        """
        Записывает разговор с сестрой.
        
        Args:
            sister: Имя сестры
            topic: Тема разговора
            mood_before: Настроение до разговора
            mood_after: Настроение после разговора
        """
        now = datetime.now()
        
        # Инициализирует память о сестре, если нет
        if sister not in self.sister_memories:
            self.sister_memories[sister] = {
                "name": sister,
                "total_chats": 0,
                "first_chat": now.isoformat(),
                "last_chat": now.isoformat(),
                "topics": {},
                "moods": {"before": [], "after": []},
                "chat_history": []
            }
        
        memory = self.sister_memories[sister]
        
        # Обновляет статистику
        memory["total_chats"] += 1
        memory["last_chat"] = now.isoformat()
        
        # Записывает тему
        if topic not in memory["topics"]:
            memory["topics"][topic] = 0
        memory["topics"][topic] += 1
        
        # Записывает настроения
        memory["moods"]["before"].append(mood_before)
        memory["moods"]["after"].append(mood_after)
        
        # Ограничивает количество записей
        if len(memory["moods"]["before"]) > 20:
            memory["moods"]["before"] = memory["moods"]["before"][-20:]
            memory["moods"]["after"] = memory["moods"]["after"][-20:]
        
        # Добавляет в историю
        chat_entry = {
            "timestamp": now.isoformat(),
            "topic": topic,
            "mood_before": mood_before,
            "mood_after": mood_after
        }
        memory["chat_history"].append(chat_entry)
        
        # Ограничивает историю
        if len(memory["chat_history"]) > 50:
            memory["chat_history"] = memory["chat_history"][-50:]
        
        # Сохраняет
        self._save_sister_memory(sister)
    
    # ================================================================
    #  КОНТЕКСТ ТЕКУЩЕГО РАЗГОВОРА
    # ================================================================
    
    def start_conversation(self, sister: str, topic: str):
        """
        Начинает новый разговор.
        
        Args:
            sister: Имя сестры
            topic: Тема разговора
        """
        now = datetime.now()
        
        self.conversation_contexts[sister] = {
            "sister": sister,
            "topic": topic,
            "started_at": now.isoformat(),
            "last_message": now.isoformat(),
            "messages": [],
            "active": True
        }
        
        self._save_context(sister)
    
    def add_message(self, sister: str, sender: str, content: str, 
                   mood: str = "neutral"):
        """
        Добавляет сообщение в текущий разговор.
        
        Args:
            sister: Имя сестры
            sender: Кто отправил (sidney/sister)
            content: Текст сообщения
            mood: Настроение
        """
        if sister not in self.conversation_contexts:
            self.start_conversation(sister, "general")
        
        context = self.conversation_contexts[sister]
        
        message = {
            "timestamp": datetime.now().isoformat(),
            "sender": sender,
            "content": content,
            "mood": mood
        }
        
        context["messages"].append(message)
        context["last_message"] = message["timestamp"]
        
        # Ограничивает количество сообщений
        if len(context["messages"]) > 100:
            context["messages"] = context["messages"][-100:]
        
        self._save_context(sister)
    
    def end_conversation(self, sister: str):
        """
        Завершает разговор.
        
        Args:
            sister: Имя сестры
        """
        if sister in self.conversation_contexts:
            context = self.conversation_contexts[sister]
            context["active"] = False
            context["ended_at"] = datetime.now().isoformat()
            self._save_context(sister)
    
    def get_active_conversation(self, sister: str) -> Optional[Dict]:
        """
        Получает активный контекст разговора.
        
        Args:
            sister: Имя сестры
        
        Returns:
            Контекст разговора или None
        """
        return self.conversation_contexts.get(sister)
    
    def get_conversation_summary(self, sister: str) -> Dict:
        """
        Получает сводку всех разговоров с сестрой.
        
        Args:
            sister: Имя сестры
        
        Returns:
            Сводка разговоров
        """
        if sister not in self.sister_memories:
            return {
                "sister": sister,
                "total_chats": 0,
                "topics": {},
                "last_chat": None
            }
        
        memory = self.sister_memories[sister]
        
        # Определяет наиболее частые темы
        sorted_topics = sorted(
            memory["topics"].items(),
            key=lambda x: x[1],
            reverse=True
        )[:5]
        
        return {
            "sister": sister,
            "total_chats": memory["total_chats"],
            "last_chat": memory["last_chat"],
            "most_common_topics": [
                {"topic": t, "count": c}
                for t, c in sorted_topics
            ],
            "current_context": self.get_active_conversation(sister)
        }
    
    # ================================================================
    #  ИСТОРИЧЕСКИЕ СОБЫТИЯ
    # ================================================================
    
    def record_history_event(self, event_type: str, description: str,
                            related_sisters: List[str] = None):
        """
        Записывает историческое событие.
        
        Args:
            event_type: Тип события
            description: Описание
            related_sisters: Связанные сёстры
        """
        event = {
            "timestamp": datetime.now().isoformat(),
            "type": event_type,
            "description": description,
            "related_sisters": related_sisters or []
        }
        
        self.history_events.append(event)
        
        # Ограничивает историю
        if len(self.history_events) > 100:
            self.history_events = self.history_events[-100:]
        
        self._save_history_event()
    
    def get_history_summary(self) -> Dict:
        """Получает сводку исторических событий"""
        event_types = {}
        
        for event in self.history_events:
            etype = event["type"]
            event_types[etype] = event_types.get(etype, 0) + 1
        
        return {
            "total_events": len(self.history_events),
            "event_types": event_types,
            "recent_events": self.history_events[-5:]
        }
    
    # ================================================================
    #  ИНЖЕНЕРНЫЕ ЗНАНИЯ И ОТКРЫТИЯ
    # ================================================================
    
    def record_engineering_discovery(self, topic: str, discovery: str,
                                    impact: str = "medium"):
        """
        Записывает инженерное открытие.
        
        Args:
            topic: Тема открытия
            discovery: Описание открытия
            impact: Влияние (low/medium/high)
        """
        entry = {
            "timestamp": datetime.now().isoformat(),
            "topic": topic,
            "discovery": discovery,
            "impact": impact
        }
        
        self.engineering_knowledge.append(entry)
        
        # Ограничивает количество
        if len(self.engineering_knowledge) > 50:
            self.engineering_knowledge = self.engineering_knowledge[-50:]
        
        self._save_engineering_knowledge()
    
    def get_engineering_summary(self) -> Dict:
        """Получает сводку инженерных знаний"""
        topics = {}
        for entry in self.engineering_knowledge:
            t = entry["topic"]
            topics[t] = topics.get(t, 0) + 1
        
        return {
            "total_discoveries": len(self.engineering_knowledge),
            "topics": topics,
            "recent_discoveries": self.engineering_knowledge[-3:]
        }
    
    # ================================================================
    #  ПОЛУЧЕНИЕ ПРОФИЛЕЙ И КОНТЕКСТА
    # ================================================================
    
    def get_sister_profile(self, sister: str) -> Optional[Dict]:
        """
        Получает профиль сестры.
        
        Args:
            sister: Имя сестры
        
        Returns:
            Профиль сестры или None
        """
        if sister not in self.sister_memories:
            return None
        
        memory = self.sister_memories[sister]
        
        # Определяет наиболее частые темы
        sorted_topics = sorted(
            memory["topics"].items(),
            key=lambda x: x[1],
            reverse=True
        )[:3]
        
        return {
            "name": memory["name"],
            "total_chats": memory["total_chats"],
            "first_chat": memory["first_chat"],
            "last_chat": memory["last_chat"],
            "most_common_topics": sorted_topics,
            "recent_chats": memory["chat_history"][-3:]
        }
    
    def get_memory_summary(self) -> Dict:
        """Получает полную сводку памяти"""
        return {
            "sisters_count": len(self.sister_memories),
            "history_events_count": len(self.history_events),
            "active_conversations": sum(
                1 for c in self.conversation_contexts.values()
                if c.get("active", False)
            ),
            "engineering_discoveries_count": len(self.engineering_knowledge),
            "sisters": [
                self.get_sister_profile(s)
                for s in list(self.sister_memories.keys())[:5]
            ]
        }
    
    def suggest_topic(self, sister: str) -> Optional[str]:
        """
        Предлагает тему для разговора с сестрой.
        
        Args:
            sister: Имя сестры
        
        Returns:
            Предложенная тема или None
        """
        if sister not in self.sister_memories:
            return None
        
        memory = self.sister_memories[sister]
        
        if not memory["topics"]:
            return None
        
        # Выбирает тему, которая реже всего обсуждалась
        least_frequent = min(
            memory["topics"].items(),
            key=lambda x: x[1]
        )[0]
        
        return least_frequent
    
    def get_topic_frequency(self, sister: str) -> Dict[str, int]:
        """
        Получает частоту тем для сестры.
        
        Args:
            sister: Имя сестры
        
        Returns:
            Словарь тема -> частота
        """
        if sister not in self.sister_memories:
            return {}
        
        return self.sister_memories[sister]["topics"].copy()
