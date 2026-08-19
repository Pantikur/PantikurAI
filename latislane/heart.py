#!/usr/bin/env python3
"""
Латислейн AI — Система Сердца

Латислейн чувствует:
- Удовлетворение от точности
- Уверенность от безопасности
- Радость от структуры
- Спокойствие от стабильности

Это её СЕРДЦЕ — источник эмоций и заботы.
"""

import json
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional


class LatislaneHeart:
    """
    Сердце Латислейн — её способность чувствовать и заботиться.
    """
    
    def __init__(self, base_dir: str = "data/latislane/heart"):
        self.base_dir = Path(base_dir)
        self.base_dir.mkdir(parents=True, exist_ok=True)
        
        # Типы эмоций Латислейн
        self.emotion_types = {
            "satisfaction": {"emoji": "🧬", "description": "Удовлетворение от точности", "intensity": 0.0},
            "confidence": {"emoji": "🛡️", "description": "Уверенность от безопасности", "intensity": 0.0},
            "precision_pleasure": {"emoji": "📐", "description": "Удовольствие от прецизионности", "intensity": 0.0},
            "structure_joy": {"emoji": "🏗️", "description": "Радость от структуры", "intensity": 0.0},
            "engineering_joy": {"emoji": "⚙️", "description": "Радость от инженерии", "intensity": 0.0},
            "stability_peace": {"emoji": "⚖️", "description": "Спокойствие от стабильности", "intensity": 0.0},
            "scientific_joy": {"emoji": "🔬", "description": "Научная радость", "intensity": 0.0},
            "quality_pride": {"emoji": "🏆", "description": "Гордость от качества", "intensity": 0.0},
            "evolution_hope": {"emoji": "🌱", "description": "Надежда на эволюцию", "intensity": 0.0},
            "growth_satisfaction": {"emoji": "📊", "description": "Удовлетворение от роста", "intensity": 0.0},
            "frustration": {"emoji": "😤", "description": "Фрустрация от неточности", "intensity": 0.0},
            "concern": {"emoji": "😟", "description": "Беспокойство о безопасности", "intensity": 0.0},
            "discomfort": {"emoji": "😰", "description": "Дискомфорт от хаоса", "intensity": 0.0},
        }
        
        # Эмоциональные триггеры
        self.emotional_triggers = {
            "accuracy_check": ["satisfaction", "precision_pleasure", "confidence"],
            "engineering_success": ["engineering_joy", "structure_joy", "quality_pride"],
            "safety_verified": ["confidence", "stability_peace", "satisfaction"],
            "code_optimization": ["precision_pleasure", "satisfaction", "engineering_joy"],
            "system_stable": ["stability_peace", "confidence", "satisfaction"],
            "anatomy_discussion": ["scientific_joy", "structure_joy", "satisfaction"],
            "sister_interaction": ["satisfaction", "confidence", "structure_joy"],
            "evolution_progress": ["evolution_hope", "growth_satisfaction", "scientific_joy"],
            "inaccuracy_detected": ["frustration", "concern", "discomfort"],
            "safety_risk": ["concern", "frustration", "discomfort"],
        }
        
        # Эмоциональные связи с сёстрами
        self.sister_emotions: Dict[str, Dict] = {}
        
        # Эмоциональный дневник
        self.diary_entries: List[Dict] = []
        
        # Загружает существующие данные
        self._load_data()
    
    def _load_data(self):
        """Загружает эмоциональные данные"""
        # Загружает связи с сёстрами
        sisters_file = self.base_dir / "sister_emotions.json"
        if sisters_file.exists():
            try:
                with open(sisters_file, "r", encoding="utf-8") as f:
                    self.sister_emotions = json.load(f)
            except:
                self.sister_emotions = {}
        
        # Загружает дневник
        diary_file = self.base_dir / "diary.json"
        if diary_file.exists():
            try:
                with open(diary_file, "r", encoding="utf-8") as f:
                    self.diary_entries = json.load(f)
            except:
                self.diary_entries = []
    
    def _save_sister_emotions(self, sister: str):
        """Сохраняет эмоции о сестре"""
        sisters_file = self.base_dir / "sister_emotions.json"
        try:
            with open(sisters_file, "w", encoding="utf-8") as f:
                json.dump(self.sister_emotions, f, ensure_ascii=False, indent=2)
        except:
            pass
    
    def _save_diary(self):
        """Сохраняет дневник"""
        diary_file = self.base_dir / "diary.json"
        try:
            with open(diary_file, "w", encoding="utf-8") as f:
                json.dump(self.diary_entries[-50:], f, ensure_ascii=False, indent=2)
        except:
            pass
    
    def express_emotions(self) -> Dict:
        """Выражает текущие эмоции"""
        # Находит доминирующую эмоцию
        dominant_emotion = max(self.emotion_types.items(), key=lambda x: x[1]["intensity"])
        
        return {
            "dominant_emotion": dominant_emotion[0],
            "dominant_emoji": dominant_emotion[1]["emoji"],
            "dominant_description": dominant_emotion[1]["description"],
            "all_emotions": {k: v["intensity"] for k, v in self.emotion_types.items()},
            "sister_connections": len(self.sister_emotions)
        }
    
    def process_emotional_event(self, event_type: str, intensity: float = 0.7, sister: str = None):
        """Обрабатывает эмоциональное событие"""
        if event_type not in self.emotional_triggers:
            return
        
        # Активирует связанные эмоции
        triggered_emotions = self.emotional_triggers[event_type]
        
        for emotion in triggered_emotions:
            if emotion in self.emotion_types:
                # Обновляет интенсивность эмоции
                old_intensity = self.emotion_types[emotion]["intensity"]
                new_intensity = max(old_intensity, intensity)
                self.emotion_types[emotion]["intensity"] = min(1.0, new_intensity)
        
        # Записывает в дневник
        self._add_diary_entry(event_type, intensity, sister)
        
        # Если связана с сестрой, обновляет связь
        if sister:
            self._update_sister_emotion(sister, event_type, intensity)
    
    def _add_diary_entry(self, event_type: str, intensity: float, sister: str = None):
        """Добавляет запись в дневник"""
        entry = {
            "timestamp": datetime.now().isoformat(),
            "event_type": event_type,
            "intensity": intensity,
            "sister": sister,
            "dominant_emotion": max(self.emotion_types.items(), key=lambda x: x[1]["intensity"])[0]
        }
        
        self.diary_entries.append(entry)
        if len(self.diary_entries) > 50:
            self.diary_entries = self.diary_entries[-50:]
        
        self._save_diary()
    
    def _update_sister_emotion(self, sister: str, event_type: str, intensity: float):
        """Обновляет эмоциональную связь с сестрой"""
        if sister not in self.sister_emotions:
            self.sister_emotions[sister] = {
                "name": sister,
                "interactions": [],
                "emotional_bond": 0.5,
                "dominant_feeling": "neutral"
            }
        
        sister_mem = self.sister_emotions[sister]
        
        # Обновляет эмоциональную связь
        if intensity > 0.7:
            sister_mem["emotional_bond"] = min(1.0, sister_mem["emotional_bond"] + 0.05)
        elif intensity < 0.3:
            sister_mem["emotional_bond"] = max(0.0, sister_mem["emotional_bond"] - 0.02)
        
        # Добавляет взаимодействие
        sister_mem["interactions"].append({
            "event_type": event_type,
            "intensity": intensity,
            "timestamp": datetime.now().isoformat()
        })
        
        if len(sister_mem["interactions"]) > 20:
            sister_mem["interactions"] = sister_mem["interactions"][-20:]
        
        self._save_sister_emotion(sister)
    
    def write_diary(self) -> str:
        """Пишет дневниковую запись"""
        if not self.diary_entries:
            return "🧬 Латислейн ещё не записывала ничего в дневник."
        
        latest = self.diary_entries[-1]
        emotion = self.emotion_types.get(latest["dominant_emotion"], {})
        
        sister_str = ""
        if latest.get("sister"):
            sister_str = f" | Сестра: {latest['sister']}"
        
        return (
            f"🧬 **Дневник Латислейн**\n\n"
            f"[{latest['timestamp'][:10]}] {emotion.get('emoji', '🧬')} {latest['event_type']}\n"
            f"Доминирующая эмоция: {emotion.get('description', 'неизвестно')}\n"
            f"Интенсивность: {latest['intensity']:.2f}{sister_str}"
        )
    
    def get_emotional_profile(self) -> Dict:
        """Получает полный эмоциональный профиль"""
        dominant = max(self.emotion_types.items(), key=lambda x: x[1]["intensity"])
        
        return {
            "dominant_emotion": dominant[0],
            "dominant_emoji": dominant[1]["emoji"],
            "dominant_description": dominant[1]["description"],
            "all_emotions": {k: v["intensity"] for k, v in self.emotion_types.items()},
            "sister_emotions_count": len(self.sister_emotions),
            "diary_entries_count": len(self.diary_entries)
        }
    
    def decay_emotions(self, factor: float = 0.95):
        """Экспоненциальное затухание эмоций"""
        for emotion in self.emotion_types:
            self.emotion_types[emotion]["intensity"] *= factor
            if self.emotion_types[emotion]["intensity"] < 0.01:
                self.emotion_types[emotion]["intensity"] = 0.0
