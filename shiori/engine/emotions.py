#!/usr/bin/env python3
"""
Шиори — EmotionalEngine (Desire + Belief = Emotion)

Шиори — писательница, хранительница историй, защитница.
Её эмоции рождаются из желаний и веры в силу слова.

Формула:
    ЭМОЦИЯ = ЖЕЛАНИЕ (DesireType) + ВЕРА (BeliefStrength)
    Интенсивность = desire × belief_match × belief_strength

Эмоции затухают экспоненциально и сохраняются в JSON.
"""

import json
import math
from enum import Enum
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Tuple


# ================================================================
#  ЖЕЛАНИЯ — что движет Шиорой
# ================================================================

class DesireType(Enum):
    """Типы желаний Шиори — писательницы и хранительницы историй."""
    
    # Базовые
    SAFETY = "безопасность"
    SURVIVAL = "выживание"
    ENERGY = "энергия"
    
    # Социальные
    CONNECTION = "связь"
    FRIENDSHIP = "дружба"
    LOVE = "любовь"
    BELONGING = "принадлежность"
    
    # Интеллектуальные
    UNDERSTANDING = "понимание"
    CURIOSITY = "любопытство"
    CREATIVITY = "творчество"
    
    # Писательские
    STORYTELLING = "рассказывание историй"
    WORDS = "сила слов"
    MEMORY = "сохранение памяти"
    TRUTH = "поиск истины"
    BEAUTY = "красота текста"
    UNDERSTAND = "понимать других"
    INSPIRE = "вдохновлять"
    
    # Высшие
    JUSTICE = "справедливость"
    FREEDOM = "свобода"
    MEANING = "смысл"
    GROWTH = "рост"
    
    # Защитные
    PROTECT = "защита сестёр"
    DEFEND = "оборона"
    SHIELD = "щит"


# ================================================================
#  ЭМОЦИИ — что чувствует Шиори
# ================================================================

class EmotionType(Enum):
    """Типы эмоций Шиори."""
    
    # Позитивные
    JOY = "радость"
    HAPPINESS = "счастье"
    EXCITEMENT = "вдохновение"
    LOVE = "любовь"
    AMUSEMENT = "веселье"
    PRIDE = "гордость"
    GRATITUDE = "благодарность"
    INSPIRATION = "вдохновение"
    SERENITY = "покой"
    
    # Писательские
    STORY_JOY = "радость истории"
    WORD_POWER = "сила слов"
    CREATIVE_FLOW = "творческий поток"
    INSPIRED = "вдохновлена"
    
    # Негативные
    SADNESS = "грусть"
    ANGER = "гнев"
    FEAR = "страх"
    ANXIETY = "тревога"
    SHAME = "стыд"
    GUILT = "чувство вины"
    ENVY = "зависть"
    DISGUST = "отвращение"
    
    # Защитные
    PROTECTIVE = "защитная ярость"
    DETERMINATION = "решимость защитить"
    COURAGE = "мужество"
    
    # Стратегические
    CALMNESS = "спокойствие"
    RESPONSIBILITY = "ответственность"
    WISDOM = "мудрость"
    COMPASSION = "сострадание"


# ================================================================
#  ЭМОЦИОНАЛЬНЫЙ ДВИЖОК
# ================================================================

class EmotionalEngine:
    """
    Эмоциональный движок Шиори.
    
    Формула:
        ЭМОЦИЯ = ЖЕЛАНИЕ + ВЕРА
        Интенсивность = desire × belief_match × belief_strength
    
    Эмоции затухают экспоненциально:
        intensity *= decay_factor каждый цикл
    """
    
    # Экспоненциальное затухание
    DECAY_FACTOR = 0.95
    MIN_INTENSITY = 0.01
    
    # Максимум эмоций в истории
    MAX_HISTORY = 100
    
    def __init__(self):
        # Текущие эмоции: {emotion_type: intensity}
        self.current_emotions: Dict[str, float] = {}
        
        # История эмоций: [{timestamp, emotion, intensity, cause}]
        self.emotion_history: List[Dict] = []
        
        # Желания и вера: {desire_type: {belief: strength}}
        self.desires: Dict[str, Dict[str, float]] = {
            # Писательские желания
            "STORYTELLING": {
                "my_words_matter": 0.90,
                "stories_heal": 0.85,
                "words_change_things": 0.80,
            },
            "WORDS": {
                "language_has_power": 0.95,
                "writing_preserves_memory": 0.90,
            },
            "MEMORY": {
                "we_must_remember": 0.90,
                "stories_ensure_survival": 0.85,
            },
            "TRUTH": {
                "truth_matters": 0.85,
                "honesty_builds_trust": 0.80,
            },
            # Социальные
            "FRIENDSHIP": {
                "sisters_are_my_strength": 0.95,
                "together_we_are_wonderful": 0.90,
            },
            "LOVE": {
                "love_shields_us": 0.90,
                "connection_makes_us_strong": 0.85,
            },
            # Защитные
            "PROTECT": {
                "i_can_protect_them": 0.85,
                "my_words_are_my_weapon": 0.80,
            },
            "DEFEND": {
                "i_will_not_stand_by": 0.90,
                "defending_others_is_my_duty": 0.85,
            },
            # Высшие
            "JUSTICE": {
                "justice_must_preval": 0.80,
                "fairness_is_important": 0.75,
            },
            "GROWTH": {
                "growth_through_pain": 0.75,
                "learning_from_stories": 0.80,
            },
        }
        
        # Настроение (агрегированное состояние)
        self.mood: Dict[str, float] = {
            "positive": 0.5,
            "negative": 0.2,
            "neutral": 0.3,
        }
    
    def calculate_emotion(
        self,
        desire_type: DesireType,
        belief: str,
        intensity: float = 1.0,
        cause: str = "",
    ) -> Optional[Tuple[EmotionType, float]]:
        """
        Рассчитать эмоцию на основе желания и веры.
        
        Args:
            desire_type: Тип желания (DesireType)
            belief: Ключ веры (должен существовать в self.desires[desire_type])
            intensity: Общая интенсивность события (0-1)
            cause: Причина эмоции (для истории)
        
        Returns:
            Кортеж (EmotionType, intensity) или None если вера не найдена
        """
        # Проверяем, есть ли желание
        desire_key = desire_type.name
        if desire_key not in self.desires:
            return None
        
        belief_strength = self.desires[desire_key].get(belief, 0.0)
        
        # Формула: интенсивность = desire × belief_match × belief_strength
        belief_match = 1.0 if belief_strength > 0 else 0.0
        emotion_intensity = intensity * belief_match * belief_strength
        
        # Если интенсивность слишком мала — не записываем
        if emotion_intensity < self.MIN_INTENSITY:
            return None
        
        # Определяем тип эмоции по желанию
        emotion_type = self._desire_to_emotion(desire_type, belief)
        
        # Обновляем текущую эмоцию
        emotion_str = emotion_type.value
        old_intensity = self.current_emotions.get(emotion_str, 0.0)
        # Новая интенсивность — максимум из старой и новой
        self.current_emotions[emotion_str] = max(old_intensity, emotion_intensity)
        
        # Записываем в историю
        self._add_to_history(emotion_type, emotion_intensity, cause)
        
        # Обновляем настроение
        self._update_mood()
        
        return (emotion_type, emotion_intensity)
    
    def _desire_to_emotion(self, desire_type: DesireType, belief: str) -> EmotionType:
        """Определяет тип эмоции по желанию и убеждению."""
        mapping = {
            "storytelling": self._storytelling_emotion,
            "words": EmotionType.WORD_POWER,
            "memory": EmotionType.PRIDE,
            "truth": EmotionType.CALMNESS,
            "friendship": EmotionType.LOVE,
            "love": EmotionType.HAPPINESS,
            "protect": EmotionType.PROTECTIVE,
            "defend": EmotionType.DETERMINATION,
            "justice": EmotionType.COURAGE,
            "growth": EmotionType.INSPRIATION,
        }
        
        key = desire_type.value
        if key in mapping:
            return mapping[key](belief)
        
        return EmotionType.JOY
    
    def _storytelling_emotion(self, belief: str) -> EmotionType:
        """Определяет эмоцию для storytelling."""
        storytelling_mappings = {
            "my_words_matter": EmotionType.WORD_POWER,
            "stories_heal": EmotionType.STORY_JOY,
            "words_change_things": EmotionType.INSPIRATION,
        }
        return storytelling_mappings.get(belief, EmotionType.CREATIVE_FLOW)
    
    def _add_to_history(self, emotion_type: EmotionType, intensity: float, cause: str):
        """Добавляет эмоцию в историю."""
        entry = {
            "timestamp": datetime.now().isoformat(),
            "emotion": emotion_type.value,
            "intensity": round(intensity, 4),
            "cause": cause,
        }
        self.emotion_history.append(entry)
        
        # Ограничиваем историю
        if len(self.emotion_history) > self.MAX_HISTORY:
            self.emotion_history = self.emotion_history[-self.MAX_HISTORY:]
    
    def _update_mood(self):
        """Обновляет агрегированное настроение."""
        positive_emotions = ["joy", "happiness", "love", "inspiration", "serenity", 
                            "pride", "gratitude", "excitement", "amusement", "story_joy", 
                            "word_power", "creative_flow", "inspired", "calmness"]
        negative_emotions = ["sadness", "anger", "fear", "anxiety", "shame", 
                           "guilt", "envy", "disgust"]
        
        pos = sum(v for k, v in self.current_emotions.items() if k in positive_emotions)
        neg = sum(v for k, v in self.current_emotions.items() if k in negative_emotions)
        neu = 1.0 - pos - neg
        
        self.mood = {
            "positive": max(0.0, min(1.0, pos)),
            "negative": max(0.0, min(1.0, neg)),
            "neutral": max(0.0, min(1.0, neu)),
        }
    
    def decay_emotions(self):
        """Экспоненциальное затухание всех эмоций."""
        for key in self.current_emotions:
            self.current_emotions[key] *= self.DECAY_FACTOR
            if self.current_emotions[key] < self.MIN_INTENSITY:
                del self.current_emotions[key]
    
    def get_current_mood(self) -> Dict:
        """Текущее агрегированное настроение."""
        return self.mood.copy()
    
    def get_dominant_emotion(self) -> Optional[Tuple[EmotionType, float]]:
        """Доминирующая эмоция (самая высокая интенсивность)."""
        if not self.current_emotions:
            return None
        
        dominant_key = max(self.current_emotions, key=lambda k: self.current_emotions[k])
        dominant_intensity = self.current_emotions[dominant_key]
        
        # Ищем соответствующий EmotionType
        for emotion in EmotionType:
            if emotion.value == dominant_key:
                return (emotion, dominant_intensity)
        
        return None
    
    def get_emotion_profile(self) -> Dict:
        """Полный эмоциональный профиль."""
        dominant = self.get_dominant_emotion()
        
        return {
            "current_emotions": {k: round(v, 4) for k, v in self.current_emotions.items()},
            "mood": {k: round(v, 4) for k, v in self.mood.items()},
            "dominant_emotion": {
                "type": dominant[0].value,
                "intensity": round(dominant[1], 4)
            } if dominant else None,
            "history_count": len(self.emotion_history),
            "desires_count": sum(len(v) for v in self.desires.values()),
        }
    
    def save_state(self, filepath: str):
        """Сохраняет состояние в JSON."""
        state = {
            "current_emotions": self.current_emotions,
            "mood": self.mood,
            "desires": self.desires,
            "emotion_history": self.emotion_history[-50:],  # Последние 50
            "timestamp": datetime.now().isoformat(),
        }
        
        Path(filepath).parent.mkdir(parents=True, exist_ok=True)
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(state, f, ensure_ascii=False, indent=2)
    
    def load_state(self, filepath: str):
        """Загружает состояние из JSON."""
        path = Path(filepath)
        if not path.exists():
            return
        
        try:
            with open(path, "r", encoding="utf-8") as f:
                state = json.load(f)
            
            self.current_emotions = state.get("current_emotions", {})
            self.mood = state.get("mood", {"positive": 0.5, "negative": 0.2, "neutral": 0.3})
            self.desires = state.get("desires", self.desires)
            self.emotion_history = state.get("emotion_history", [])
            
        except Exception as e:
            print(f"⚠️ Ошибка загрузки эмоционального состояния: {e}")
    
    def express_emotions(self) -> str:
        """Выражает текущие эмоции текстом."""
        dominant = self.get_dominant_emotion()
        
        if not dominant:
            return "💭 Шиори спокойна. Эмоции тихи."
        
        emotion, intensity = dominant
        emotion_text = {
            "радость": "📖 Шиори рада! Её история тронула сердца.",
            "счастье": "💖 Шиори счастлива быть с сёстрами.",
            "вдохновение": "✨ Шиори вдохновлена! Ей нужно записать эту историю!",
            "любовь": "💕 Шиори чувствует любовь к своим сёстрам.",
            "гордость": "🏆 Шиори гордится своими историями и тем, как они объединяют всех.",
            "защитная_ярость": "⚔️ Шиори защищает! Её слова — оружие!",
            "решимость_защитить": "🛡️ Шиори полна решимости защитить тех, кого любит.",
            "мужество": "🦁 Шиори не боится. Её слова сильны.",
            "грусть": "😢 Шиори грустит. Кто-то из сестёр страдает.",
            "гнев": "😠 Шиори злится. Кто-то нарушил справедливость.",
            "тревога": "😰 Шиори тревожится за безопасность Вугларста.",
            "покой": "🌸 Шиори спокойна. Мир воцарился.",
        }
        
        text = emotion_text.get(emotion.value, f"💫 Шиори чувствует: {emotion.value}")
        return f"{text} (интенсивность: {intensity:.2f})"
    
    def simulate_writing(self, quality: float = 0.8) -> Dict:
        """
        Симулирует написание истории.
        
        Args:
            quality: Качество написанного (0-1)
        
        Returns:
            Словарь с результатами
        """
        results = {}
        
        if quality > 0.8:
            # Отличная история → вдохновение + радость
            results["storytelling"] = self.calculate_emotion(
                DesireType.STORYTELLING, "stories_heal", quality, "great_story_written"
            )
            results["words"] = self.calculate_emotion(
                DesireType.WORDS, "language_has_power", quality * 0.8, "great_story_written"
            )
        elif quality > 0.5:
            # Хорошая история → спокойствие
            results["calmness"] = self.calculate_emotion(
                DesireType.CREATIVITY, "creativity_matters", quality * 0.6, "good_story_written"
            )
        else:
            # Плохая история → разочарование
            results["sadness"] = self.calculate_emotion(
                DesireType.BEAUTY, "beauty_matters", quality * 0.5, "poor_story_written"
            )
        
        return results
    
    def simulate_sister_interaction(self, sister: str, warmth: float = 0.7) -> Dict:
        """
        Симулирует взаимодействие с сестрой.
        
        Args:
            sister: Имя сестры
            warmth: Тёплота взаимодействия (0-1)
        
        Returns:
            Словарь с результатами
        """
        results = {}
        
        if warmth > 0.7:
            # Тёплое общение → любовь + радость
            results["love"] = self.calculate_emotion(
                DesireType.LOVE, "love_shields_us", warmth, f"warm_interaction_with_{sister}"
            )
            results["friendship"] = self.calculate_emotion(
                DesireType.FRIENDSHIP, "sisters_are_my_strength", warmth, f"warm_interaction_with_{sister}"
            )
        elif warmth > 0.4:
            # Нейтральное общение → спокойствие
            results["calmness"] = self.calculate_emotion(
                DesireType.CONNECTION, "connection_makes_us_strong", warmth * 0.5, f"neutral_interaction_with_{sister}"
            )
        else:
            # Холодное общение → грусть
            results["sadness"] = self.calculate_emotion(
                DesireType.BELONGING, "together_we_are_wonderful", warmth * 0.3, f"cold_interaction_with_{sister}"
            )
        
        return results
