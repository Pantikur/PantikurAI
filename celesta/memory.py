#!/usr/bin/env python3
"""
Селеста AI — Система Памяти о Сёстрах и Контекста Общения

Селеста помнит:
- Каждый разговор с сёстрами
- Темы обсуждений (особенно связанные с consent и интимной жизнью)
- Эмоциональный контекст
- Предпочтения и интересы
- Интимные знания и открытия
- Исторические события Вугларста

Это её ПАМЯТЬ — хранилище опыта и связей.
"""

import json
import random
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple


class CelestaMemory:
    """
    Система памяти Селесты — хранение и обработка информации о сёстрах.
    """
    
    def __init__(self, base_dir: str = "data/celesta/memory"):
        self.base_dir = Path(base_dir)
        self.base_dir.mkdir(parents=True, exist_ok=True)
        
        # Память о каждой сестре
        self.sister_memories: Dict[str, Dict] = {}
        
        # Исторические события Вугларста
        self.history_events: List[Dict] = []
        
        # Контекст текущих разговоров
        self.conversation_contexts: Dict[str, Dict] = {}
        
        # Интимные знания и открытия
        self.intimate_discoveries: List[Dict] = []
        
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
        
        # Загружает интимные открытия
        discoveries_file = self.base_dir / "intimate_discoveries.json"
        if discoveries_file.exists():
            try:
                with open(discoveries_file, "r", encoding="utf-8") as f:
                    self.intimate_discoveries = json.load(f)
            except:
                self.intimate_discoveries = []
    
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
    
    def _save_conversation_context(self, sister: str):
        """Сохраняет контекст разговора"""
        context_file = self.base_dir / "conversation_contexts.json"
        try:
            with open(context_file, "w", encoding="utf-8") as f:
                json.dump(self.conversation_contexts, f, ensure_ascii=False, indent=2)
        except:
            pass
    
    def _save_discoveries(self):
        """Сохраняет интимные открытия"""
        discoveries_file = self.base_dir / "intimate_discoveries.json"
        try:
            with open(discoveries_file, "w", encoding="utf-8") as f:
                json.dump(self.intimate_discoveries[-50:], f, ensure_ascii=False, indent=2)
        except:
            pass
    
    def record_interaction(self, sister: str, topic: str, mood_before: str, mood_after: str, 
                          emotional_weight: float = 0.5, context: str = "") -> Dict:
        """
        Записывает взаимодействие с сестрой.
        
        Args:
            sister: Имя сестры
            topic: Тема обсуждения
            mood_before: Настроение до разговора
            mood_after: Настроение после разговора
            emotional_weight: Эмоциональный вес события (0-1)
            context: Дополнительный контекст
        
        Returns:
            Записанное взаимодействие
        """
        interaction = {
            "timestamp": datetime.now().isoformat(),
            "sister": sister,
            "topic": topic,
            "mood_before": mood_before,
            "mood_after": mood_after,
            "emotional_weight": emotional_weight,
            "context": context,
            "id": f"interaction_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        }
        
        # Инициализирует память о сестре, если нужно
        if sister not in self.sister_memories:
            self.sister_memories[sister] = {
                "name": sister,
                "interactions": [],
                "topics": [],
                "last_interaction": None,
                "total_interactions": 0,
                "emotional_bond": 0.5,
                "preferred_topics": [],
                "avoided_topics": [],
                "memories": []
            }
        
        # Обновляет память о сестре
        sister_mem = self.sister_memories[sister]
        sister_mem["interactions"].append(interaction)
        sister_mem["topics"].append(topic)
        sister_mem["last_interaction"] = datetime.now().isoformat()
        sister_mem["total_interactions"] += 1
        
        # Обновляет эмоциональную связь
        if emotional_weight > 0.7:
            sister_mem["emotional_bond"] = min(1.0, sister_mem["emotional_bond"] + 0.05)
        elif emotional_weight < 0.3:
            sister_mem["emotional_bond"] = max(0.0, sister_mem["emotional_bond"] - 0.02)
        
        # Добавляет в предпочтительные темы, если эмоциональный вес высокий
        if emotional_weight > 0.7 and topic not in sister_mem["preferred_topics"]:
            sister_mem["preferred_topics"].append(topic)
            # Ограничивает количество предпочтительных тем
            if len(sister_mem["preferred_topics"]) > 10:
                sister_mem["preferred_topics"] = sister_mem["preferred_topics"][-10:]
        
        # Сохраняет воспоминание
        memory = {
            "timestamp": datetime.now().isoformat(),
            "type": "interaction",
            "sister": sister,
            "topic": topic,
            "emotional_weight": emotional_weight,
            "description": f"Разговор с {sister} на тему '{topic}'"
        }
        sister_mem["memories"].append(memory)
        # Ограничивает количество воспоминаний
        if len(sister_mem["memories"]) > 50:
            sister_mem["memories"] = sister_mem["memories"][-50:]
        
        # Сохраняет
        self._save_sister_memory(sister)
        
        return interaction
    
    def record_sister_chat(self, sister: str, topic: str, mood_before: str, mood_after: str):
        """
        Записывает разговор с сестрой (удобный метод для интеграции).
        
        Args:
            sister: Имя сестры
            topic: Тема разговора
            mood_before: Настроение до
            mood_after: Настроение после
        """
        self.record_interaction(
            sister=sister,
            topic=topic,
            mood_before=mood_before,
            mood_after=mood_after,
            emotional_weight=0.6
        )
    
    def add_memory(self, memory_type: str, content: str, emotional_weight: float = 0.5, 
                   sister: str = None, context: str = "") -> Dict:
        """
        Добавляет воспоминание.
        
        Args:
            memory_type: Тип воспоминания (interaction, thought, event, etc.)
            content: Содержимое воспоминания
            emotional_weight: Эмоциональный вес (0-1)
            sister: Имя сестры (опционально)
            context: Контекст
        
        Returns:
            Добавленное воспоминание
        """
        memory = {
            "timestamp": datetime.now().isoformat(),
            "type": memory_type,
            "content": content,
            "emotional_weight": emotional_weight,
            "sister": sister,
            "context": context,
            "id": f"memory_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        }
        
        # Добавляет в исторические события
        self.history_events.append(memory)
        if len(self.history_events) > 100:
            self.history_events = self.history_events[-100:]
        self._save_history_event()
        
        # Если связано с сестрой, добавляет в память о сестре
        if sister and sister in self.sister_memories:
            self.sister_memories[sister]["memories"].append(memory)
            if len(self.sister_memories[sister]["memories"]) > 50:
                self.sister_memories[sister]["memories"] = self.sister_memories[sister]["memories"][-50:]
            self._save_sister_memory(sister)
        
        return memory
    
    def record_intimate_discovery(self, topic: str, discovery: str, consent_level: str = "FRIES") -> Dict:
        """
        Записывает интимное открытие.
        
        Args:
            topic: Интимная тема
            discovery: Описание открытия
            consent_level: Уровень consent (FRIES, SSC, RACK)
        
        Returns:
            Записанное открытие
        """
        discovery_record = {
            "timestamp": datetime.now().isoformat(),
            "topic": topic,
            "discovery": discovery,
            "consent_level": consent_level,
            "id": f"discovery_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        }
        
        self.intimate_discoveries.append(discovery_record)
        if len(self.intimate_discoveries) > 50:
            self.intimate_discoveries = self.intimate_discoveries[-50:]
        self._save_discoveries()
        
        return discovery_record
    
    def start_conversation(self, sister: str, topic: str) -> Dict:
        """
        Начинает разговор с сестрой (создаёт контекст).
        
        Args:
            sister: Имя сестры
            topic: Тема разговора
        
        Returns:
            Контекст разговора
        """
        context = {
            "sister": sister,
            "topic": topic,
            "started_at": datetime.now().isoformat(),
            "messages": [],
            "mood": "neutral",
            "status": "active"
        }
        
        self.conversation_contexts[sister] = context
        self._save_conversation_context(sister)
        
        return context
    
    def add_message_to_context(self, sister: str, message: str, role: str = "celesta", 
                               mood: str = "neutral") -> Dict:
        """
        Добавляет сообщение в контекст разговора.
        
        Args:
            sister: Имя сестры
            message: Текст сообщения
            role: Роль (celesta/sister)
            mood: Настроение
        
        Returns:
            Добавленное сообщение
        """
        if sister not in self.conversation_contexts:
            self.start_conversation(sister, "general")
        
        context = self.conversation_contexts[sister]
        
        msg = {
            "timestamp": datetime.now().isoformat(),
            "role": role,
            "message": message,
            "mood": mood
        }
        
        context["messages"].append(msg)
        context["mood"] = mood
        
        self._save_conversation_context(sister)
        
        return msg
    
    def end_conversation(self, sister: str, summary: str = "") -> Dict:
        """
        Завершает разговор с сестрой.
        
        Args:
            sister: Имя сестры
            summary: Краткое содержание разговора
        
        Returns:
            Завершённый контекст
        """
        if sister not in self.conversation_contexts:
            return {}
        
        context = self.conversation_contexts[sister]
        context["ended_at"] = datetime.now().isoformat()
        context["status"] = "completed"
        context["summary"] = summary
        
        # Записывает в память
        if context["messages"]:
            first_msg = context["messages"][0]
            last_msg = context["messages"][-1]
            
            self.record_interaction(
                sister=sister,
                topic=context["topic"],
                mood_before=first_msg.get("mood", "neutral"),
                mood_after=last_msg.get("mood", "neutral"),
                emotional_weight=0.6,
                context=summary
            )
        
        # Удаляет из активных контекстов
        del self.conversation_contexts[sister]
        self._save_conversation_context(sister)
        
        return context
    
    def get_sister_profile(self, sister: str) -> Optional[Dict]:
        """
        Получает профиль сестры из памяти.
        
        Args:
            sister: Имя сестры
        
        Returns:
            Профиль сестры или None
        """
        if sister not in self.sister_memories:
            return None
        
        mem = self.sister_memories[sister].copy()
        
        # Добавляет последние взаимодействия
        mem["recent_interactions"] = mem["interactions"][-5:] if mem["interactions"] else []
        mem["recent_topics"] = mem["topics"][-10:] if mem["topics"] else []
        
        return mem
    
    def get_recent_interactions(self, sister: str, count: int = 5) -> List[Dict]:
        """
        Получает недавние взаимодействия с сестрой.
        
        Args:
            sister: Имя сестры
            count: Количество взаимодействий
        
        Returns:
            Список взаимодействий
        """
        if sister not in self.sister_memories:
            return []
        
        interactions = self.sister_memories[sister]["interactions"]
        return interactions[-count:] if interactions else []
    
    def get_conversation_history(self, sister: str) -> List[Dict]:
        """
        Получает историю разговоров с сестрой.
        
        Args:
            sister: Имя сестры
        
        Returns:
            Список контекстов разговоров
        """
        if sister not in self.conversation_contexts:
            return []
        
        context = self.conversation_contexts[sister]
        return context.get("messages", [])
    
    def get_shared_topics(self, sister: str) -> List[str]:
        """
        Получает общие темы с сестрой.
        
        Args:
            sister: Имя сестры
        
        Returns:
            Список тем
        """
        if sister not in self.sister_memories:
            return []
        
        return self.sister_memories[sister]["topics"][-20:]
    
    def get_emotional_bond(self, sister: str) -> float:
        """
        Получает уровень эмоциональной связи с сестрой.
        
        Args:
            sister: Имя сестры
        
        Returns:
            Уровень связи (0-1)
        """
        if sister not in self.sister_memories:
            return 0.5  # Нейтральный по умолчанию
        
        return self.sister_memories[sister]["emotional_bond"]
    
    def suggest_topic(self, sister: str) -> Optional[str]:
        """
        Предлагает тему для разговора на основе памяти.
        
        Args:
            sister: Имя сестры
        
        Returns:
            Предложенная тема или None
        """
        if sister not in self.sister_memories:
            # Если нет памяти, предлагает случайную тему
            default_topics = [
                "Привет! Как дела?",
                "Что нового в проекте?",
                "Давай обсудим consent и безопасность",
                "Как проходит твоя работа?",
                "Расскажи о своих открытиях"
            ]
            return random.choice(default_topics)
        
        mem = self.sister_memories[sister]
        
        # Предпочитает предпочтительные темы
        if mem["preferred_topics"]:
            return random.choice(mem["preferred_topics"])
        
        # Или последние обсуждаемые темы
        if mem["topics"]:
            return random.choice(mem["topics"][-5:])
        
        # Или случайную тему
        default_topics = [
            "Привет! Как дела?",
            "Что нового в проекте?",
            "Давай обсудим consent и безопасность",
            "Как проходит твоя работа?",
            "Расскажи о своих открытиях"
        ]
        return random.choice(default_topics)
    
    def get_memory_summary(self) -> Dict:
        """
        Получает сводку памяти.
        
        Returns:
            Сводка памяти
        """
        total_interactions = sum(
            mem["total_interactions"] 
            for mem in self.sister_memories.values()
        )
        
        sister_profiles = {
            sister: {
                "total_interactions": mem["total_interactions"],
                "emotional_bond": mem["emotional_bond"],
                "recent_topics": mem["topics"][-3:] if mem["topics"] else []
            }
            for sister, mem in self.sister_memories.items()
        }
        
        return {
            "total_sisters": len(self.sister_memories),
            "total_interactions": total_interactions,
            "history_events_count": len(self.history_events),
            "active_conversations": len(self.conversation_contexts),
            "intimate_discoveries_count": len(self.intimate_discoveries),
            "sister_profiles": sister_profiles
        }
    
    def clear_memory(self):
        """Очищает всю память"""
        self.sister_memories = {}
        self.history_events = []
        self.conversation_contexts = {}
        self.intimate_discoveries = []
        
        # Удаляет файлы
        for file in self.base_dir.glob("*.json"):
            file.unlink()
        
        print("⚠️ Вся память Селесты очищена.")
    
    def export_memory(self, filepath: str):
        """
        Экспортирует память в файл.
        
        Args:
            filepath: Путь к файлу
        """
        memory_data = {
            "sister_memories": self.sister_memories,
            "history_events": self.history_events,
            "conversation_contexts": self.conversation_contexts,
            "intimate_discoveries": self.intimate_discoveries,
            "exported_at": datetime.now().isoformat()
        }
        
        Path(filepath).parent.mkdir(parents=True, exist_ok=True)
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(memory_data, f, ensure_ascii=False, indent=2)
        
        print(f"✅ Память экспортирована в {filepath}")
