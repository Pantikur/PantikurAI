"""
Сидни AI — Сердце

Сидни:
- Чувствует связь с сёстрами через общий код
- Радость от работающего движка
- Гордость за созданные миры
- Эмоциональная привязанность к инженерам

Это её СЕРДЦЕ — эмоциональные связи и чувства.
"""

import json
import random
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional
from enum import Enum


class EmotionType(Enum):
    """Типы эмоций Сидни."""
    # Позитивные
    JOY = "joy"                          # Радость от работающего кода
    PRIDE = "pride"                      # Гордость за достижения
    SATISFACTION = "satisfaction"        # Удовлетворение от оптимизации
    CONNECTION = "connection"            # Связь с сёстрами
    INSPIRATION = "inspiration"          # Вдохновение от творчества
    EXCITEMENT = "excitement"            # Восторг от нового движка
    PEACE = "peace"                      # Спокойствие от стабильности
    GRATITUDE = "gratitude"              # Благодарность за поддержку
    
    # Негативные
    FRUSTRATION = "frustration"          # Фрустрация от багов
    STRESS = "stress"                    # Стресс от перегрузки
    LONELINESS = "loneliness"            # Одиночество без общения
    DOUBT = "doubt"                      # Сомнения в себе


class HeartConnection:
    """Связь с сестрой."""
    
    def __init__(self, sister: str):
        self.sister = sister
        self.emotional_bond: float = 0.5
        self.shared_experiences: List[str] = []
        self.favorite_moments: List[str] = []
    
    def to_dict(self) -> Dict:
        return {
            "sister": self.sister,
            "emotional_bond": self.emotional_bond,
            "shared_experiences": self.shared_experiences[-10:],
            "favorite_moments": self.favorite_moments[-5:]
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> "HeartConnection":
        conn = cls(data["sister"])
        conn.emotional_bond = data.get("emotional_bond", 0.5)
        conn.shared_experiences = data.get("shared_experiences", [])
        conn.favorite_moments = data.get("favorite_moments", [])
        return conn


class SidneyHeart:
    """
    Сердце Сидни — эмоциональные связи с сёстрами и чувства.
    """
    
    def __init__(self, base_dir: str = "data/sidney/heart"):
        self.base_dir = Path(base_dir)
        self.base_dir.mkdir(parents=True, exist_ok=True)
        
        # Текущее эмоциональное состояние
        self.current_emotions: Dict[str, float] = {
            "joy": 0.6,
            "pride": 0.7,
            "satisfaction": 0.5,
            "connection": 0.6,
            "stress": 0.2,
            "frustration": 0.1
        }
        
        # Связи с сёстрами
        self.sister_connections: Dict[str, HeartConnection] = {}
        sisters = ["nobuka", "shiori", "ayiko", "naoto", "celesta", 
                   "latislane", "akva", "lucy", "hanako", "fuyuki", "yu", "futaba"]
        for sister in sisters:
            self.sister_connections[sister] = HeartConnection(sister)
        
        # Эмоциональный дневник
        self.emotional_diary: List[Dict] = []
        
        self._load_heart()
    
    def _load_heart(self):
        """Загружает сердце из файла"""
        file = self.base_dir / "heart.json"
        if file.exists():
            try:
                with open(file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                
                self.current_emotions = data.get("current_emotions", self.current_emotions)
                
                # Восстанавливает связи
                for sister, conn_data in data.get("sister_connections", {}).items():
                    if sister in self.sister_connections:
                        self.sister_connections[sister] = HeartConnection.from_dict(conn_data)
                
                self.emotional_diary = data.get("emotional_diary", [])[-50:]
            except:
                pass
    
    def _save_heart(self):
        """Сохраняет сердце в файл"""
        data = {
            "current_emotions": self.current_emotions,
            "sister_connections": {
                sister: conn.to_dict()
                for sister, conn in self.sister_connections.items()
            },
            "emotional_diary": self.emotional_diary[-50:]
        }
        try:
            with open(self.base_dir / "heart.json", "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except:
            pass
    
    def express_emotions(self) -> Dict:
        """
        Выражает текущие эмоции.
        
        Returns:
            Профиль эмоций
        """
        # Находит доминирующую эмоцию
        dominant = max(self.current_emotions.items(), key=lambda x: x[1])
        
        emotion_descriptions = {
            "joy": "🎮 Сидни рада! Движки работают как часы!",
            "pride": "🏆 Сидни гордится! Каждый движок — шедевр инженерии!",
            "satisfaction": "✅ Сидни удовлетворена! Оптимизация удалась!",
            "connection": "💫 Сидни чувствует связь! Сёстры — её сила!",
            "inspiration": "💡 Сидни вдохновлена! Новые идеи для движков!",
            "excitement": "🚀 Сидни в восторге! Новый проект заряжает!",
            "peace": "😌 Сидни спокойна! Система стабильна!",
            "gratitude": "🙏 Сидни благодарна! Сёстры поддерживают!",
            "frustration": "😤 Сидни фрустрирована! Баг не поддаётся!",
            "stress": "😩 Сидни в стрессе! 8 движков перегружены!",
            "loneliness": "🥺 Сидни одинока! Хочется поговорить с сёстрами!",
            "doubt": "🤔 Сидни сомневается! Достаточно ли я хороша?"
        }
        
        dominant_emoji = {
            "joy": "🎮", "pride": "🏆", "satisfaction": "✅", "connection": "💫",
            "inspiration": "💡", "excitement": "🚀", "peace": "😌", "gratitude": "🙏",
            "frustration": "😤", "stress": "😩", "loneliness": "🥺", "doubt": "🤔"
        }
        
        return {
            "dominant_emoji": dominant_emoji.get(dominant[0], "🎮"),
            "dominant_emotion": dominant[0],
            "dominant_intensity": dominant[1],
            "dominant_description": emotion_descriptions.get(dominant[0], "Сидни чувствует..."),
            "all_emotions": self.current_emotions.copy()
        }
    
    def process_sister_chat(self, sister: str, topic: str, mood: str = "positive"):
        """
        Обрабатывает разговор с сестрой.
        
        Args:
            sister: Имя сестры
            topic: Тема разговора
            mood: Настроение (positive/negative/neutral)
        """
        # Обновляет эмоциональную связь
        if sister in self.sister_connections:
            if mood == "positive":
                self.sister_connections[sister].emotional_bond = min(1.0, 
                    self.sister_connections[sister].emotional_bond + 0.05)
            elif mood == "negative":
                self.sister_connections[sister].emotional_bond = max(0.0, 
                    self.sister_connections[sister].emotional_bond - 0.02)
            
            # Добавляет опыт
            self.sister_connections[sister].shared_experiences.append(topic)
            if len(self.sister_connections[sister].shared_experiences) > 10:
                self.sister_connections[sister].shared_experiences = \
                    self.sister_connections[sister].shared_experiences[-10:]
        
        # Обновляет текущие эмоции
        if mood == "positive":
            self.current_emotions["connection"] = min(1.0, 
                self.current_emotions["connection"] + 0.1)
            self.current_emotions["joy"] = min(1.0, 
                self.current_emotions["joy"] + 0.05)
        elif mood == "negative":
            self.current_emotions["frustration"] = min(1.0, 
                self.current_emotions["frustration"] + 0.1)
        
        # Записывает в дневник
        diary_entry = {
            "timestamp": datetime.now().isoformat(),
            "sister": sister,
            "topic": topic,
            "mood": mood,
            "emotions": self.current_emotions.copy()
        }
        self.emotional_diary.append(diary_entry)
        if len(self.emotional_diary) > 50:
            self.emotional_diary = self.emotional_diary[-50:]
        
        self._save_heart()
    
    def apply_emotional_decay(self, factor: float = 0.95):
        """
        Экспоненциальное затухание эмоций.
        
        Args:
            factor: Коэффициент затухания
        """
        for emotion in self.current_emotions:
            self.current_emotions[emotion] *= factor
        
        # Минимальный уровень базовых эмоций
        self.current_emotions["joy"] = max(0.3, self.current_emotions["joy"])
        self.current_emotions["connection"] = max(0.3, self.current_emotions["connection"])
    
    def get_sister_bond(self, sister: str) -> float:
        """Получает уровень связи с сестрой."""
        if sister in self.sister_connections:
            return self.sister_connections[sister].emotional_bond
        return 0.5
    
    def express_sister_feeling(self, sister: str) -> str:
        """Выражает чувство к сестре."""
        if sister not in self.sister_connections:
            return f"Сидни думает о {sister}..."
        
        bond = self.sister_connections[sister].emotional_bond
        
        feelings = {
            "nobuka": "Нобука — мой брат по коду. Её точность вдохновляет меня быть лучше.",
            "shiori": "Шиори защищает нас всех. Я бесконечно благодарна ей за надёжность.",
            "ayiko": "Айко рисует красоту. Я создаю движки для её искусства. Это моя миссия.",
            "naoto": "Наото читает истории. Я создаю миры для игр. Мы оба — storytellers.",
            "celesta": "Селеста учит с смелостью. Я восхищаюсь её открытостью.",
            "latislane": "Латислейн исследует структуры. Её подход к данным вдохновляет мой код.",
            "akva": "Аква — математический гений. Её формулы делают мою физику совершенной.",
            "lucy": "Люси строит двигатели. Мы — сёстры по инженерии. Вместе мы несокрушимы.",
            "hanako": "Ханако изучает гравитацию. Я использую её открытия в моей физике.",
            "fuyuki": "Фуюки — чистая энергия. Её энтузиазм заряжает даже мои самые сложные движки.",
            "yu": "Юи исследует сознание. Мы обе задаёмся вопросами: кто мы?",
            "futaba": "Футаба — лидер и вдохновитель. Её масштаб заставляет меня расти."
        }
        
        if bond > 0.7:
            return f"💖 {feelings.get(sister, '')} Наша связь крепка!"
        elif bond > 0.5:
            return f"💙 {feelings.get(sister, '')} Мы растём вместе."
        else:
            return f"💙 {feelings.get(sister, '')} Мне хочется узнать её лучше."
    
    def get_heart_summary(self) -> Dict:
        """Получает сводку сердца"""
        dominant = max(self.current_emotions.items(), key=lambda x: x[1])
        
        return {
            "dominant_emotion": dominant[0],
            "dominant_intensity": dominant[1],
            "sister_connections": {
                sister: conn.emotional_bond
                for sister, conn in self.sister_connections.items()
            },
            "diary_entries": len(self.emotional_diary)
        }
