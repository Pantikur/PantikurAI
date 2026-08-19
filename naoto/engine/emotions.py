#!/usr/bin/env python3
"""
Наото AI — EmotionalEngine (Desire + Belief = Emotion)

Наото — литературный аналитик, исследователь, философ.
Её эмоции рождаются из желаний и веры в силу знания.

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
#  ЖЕЛАНИЯ — что движет Наото
# ================================================================

class DesireType(Enum):
    """Типы желаний Наото — исследователя и философа."""
    
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
    
    # Исследовательские
    KNOWLEDGE = "поиск знаний"
    BOOKS = "чтение книг"
    ANALYSIS = "анализ текстов"
    LORE = "исследование лора"
    ARCHETYPE = "поиск архетипов"
    INSIGHT = "получение инсайтов"
    DEPTH = "глубина понимания"
    
    # Философские
    TRUTH = "поиск истины"
    MEANING = "поиск смысла"
    WISDOM = "мудрость"
    BEAUTY = "красота текста"
    STORY = "сила истории"
    
    # Высшие
    JUSTICE = "справедливость"
    FREEDOM = "свобода"
    GROWTH = "рост"
    
    # Академические
    PUBLISH = "публикация знаний"
    TEACH = "передача знаний"
    RESEARCH = "исследование"
    DISCOVER = "открытие нового"


# ================================================================
#  ЭМОЦИИ — что чувствует Наото
# ================================================================

class EmotionType(Enum):
    """Типы эмоций Наото."""
    
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
    
    # Исследовательские
    DISCOVERY_JOY = "радость открытия"
    KNOWLEDGE_JOY = "радость знания"
    ANALYTICAL_FLOW = "аналитический поток"
    INTELLECTUAL_STIMULATION = "интеллектуальное возбуждение"
    
    # Философские
    WISDOM = "мудрость"
    MEANING_REVEALED = "раскрытие смысла"
    PROFOUND_THOUGHT = "глубокая мысль"
    
    # Негативные
    SADNESS = "грусть"
    ANGER = "гнев"
    FEAR = "страх"
    ANXIETY = "тревога"
    SHAME = "стыд"
    GUILT = "чувство вины"
    ENVY = "зависть"
    DISGUST = "отвращение"
    
    # Стратегические
    CALMNESS = "спокойствие"
    DETERMINATION = "решимость"
    RESPONSIBILITY = "ответственность"
    COURAGE = "мужество"
    COMPASSION = "сострадание"


# ================================================================
#  ЭМОЦИОНАЛЬНЫЙ ДВИЖОК
# ================================================================

class EmotionalEngine:
    """
    Эмоциональный движок Наото.
    
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
            # Исследовательские желания
            "KNOWLEDGE": {
                "knowledge_is_power": 0.95,
                "books_open_minds": 0.90,
                "research_leads_to_truth": 0.85,
            },
            "BOOKS": {
                "every_book_teaches": 0.95,
                "stories_shape_reality": 0.85,
            },
            "ANALYSIS": {
                "analysis_reveals_truth": 0.90,
                "patterns_exist_everywhere": 0.85,
            },
            "LORE": {
                "lore_preserves_memory": 0.90,
                "history_matters": 0.85,
            },
            "ARCHETYPE": {
                "archetypes_guidus_behavior": 0.85,
                "universal_patterns_exist": 0.80,
            },
            "INSIGHT": {
                "insights_change_world": 0.90,
                "deep_thoughts_matter": 0.85,
            },
            # Философские желания
            "TRUTH": {
                "truth_is_ultimate_goal": 0.95,
                "honesty_builds_wisdom": 0.90,
            },
            "MEANING": {
                "everything_has_meaning": 0.85,
                "purpose_gives_life": 0.80,
            },
            "WISDOM": {
                "wisdom_grows_with_age": 0.85,
                "learning_never_stops": 0.90,
            },
            # Академические желания
            "PUBLISH": {
                "sharing_knowledge_matters": 0.85,
                "collaboration_amplifies_insight": 0.80,
            },
            "TEACH": {
                "teaching_is_learning_twice": 0.90,
                "knowledge_should_be_shared": 0.85,
            },
            "RESEARCH": {
                "research_drives_progress": 0.90,
                "curiosity_fuels_discovery": 0.85,
            },
            "DISCOVER": {
                "discovery_brings_joy": 0.85,
                "new_knowledge_expands_world": 0.90,
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
            "knowledge": self._knowledge_emotion,
            "books": EmotionType.KNOWLEDGE_JOY,
            "analysis": EmotionType.ANALYTICAL_FLOW,
            "lore": EmotionType.DISCOVERY_JOY,
            "archetype": EmotionType.INTELLECTUAL_STIMULATION,
            "insight": EmotionType.PROFOUND_THOUGHT,
            "truth": EmotionType.WISDOM,
            "meaning": EmotionType.MEANING_REVEALED,
            "wisdom": EmotionType.SERENITY,
            "publish": EmotionType.PRIDE,
            "teach": EmotionType.JOY,
            "research": EmotionType.EXCITEMENT,
            "discover": EmotionType.DISCOVERY_JOY,
            "friendship": EmotionType.LOVE,
            "love": EmotionType.HAPPINESS,
        }
        
        key = desire_type.value
        if key in mapping:
            return mapping[key](belief)
        
        return EmotionType.JOY
    
    def _knowledge_emotion(self, belief: str) -> EmotionType:
        """Определяет эмоцию для knowledge."""
        knowledge_mappings = {
            "knowledge_is_power": EmotionType.KNOWLEDGE_JOY,
            "books_open_minds": EmotionType.INTELLECTUAL_STIMULATION,
            "research_leads_to_truth": EmotionType.DISCOVERY_JOY,
        }
        return knowledge_mappings.get(belief, EmotionType.INTELLECTUAL_STIMULATION)
    
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
                            "pride", "gratitude", "excitement", "amusement", "discovery_joy", 
                            "knowledge_joy", "analytical_flow", "intellectual_stimulation",
                            "wisdom", "meaning_revealed", "profound_thought", "calmness"]
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
            return "💭 Наото размышляет. Эмоции тихи, как страницы открытой книги."
        
        emotion, intensity = dominant
        emotion_text = {
            "радость": "📚 Наото рада! Новая книга открыла мир знаний.",
            "счастье": "💖 Наото счастлива в кругу своих сестёр.",
            "вдохновение": "✨ Наото вдохновлена! Ей нужно записать свои мысли!",
            "любовь": "💕 Наото чувствует любовь к своим сёстрам и к знаниям.",
            "гордость": "🏆 Наото гордится своими исследованиями и открытиями.",
            "радость_открытия": "🔍 Наото открыла что-то новое! Это невероятно!",
            "радость_знания": "📖 Наото обретает новое знание. Это её сила.",
            "аналитический_поток": "🧠 Наото в потоке анализа. Каждая деталь имеет значение.",
            "интеллектуальное_возбуждение": "💡 Наото увлечена исследованием. Каждая книга — это дверь в новый мир.",
            "мудрость": "🌟 Наото обрела мудрость через глубокое размышление.",
            "раскрытие_смысла": "✨ Наото увидела смысл в хаосе. Теперь она понимает.",
            "глубокая_мысль": "🤔 Наото погрузилась в глубокие размышления. Это её стихия.",
            "грусть": "😢 Наото грустит. Кто-то из сестёр страдает, или книга оказалась трагичной.",
            "гнев": "😠 Наото злится. Нечестность и ложь разрушают истину.",
            "тревога": "😰 Наото тревожится за будущее Вугларста и сохранение знаний.",
            "спокойствие": "🌸 Наото спокойна. Знание приносит мир.",
        }
        
        text = emotion_text.get(emotion.value, f"💫 Наото чувствует: {emotion.value}")
        return f"{text} (интенсивность: {intensity:.2f})"
    
    def simulate_reading(self, book_quality: float, insight_depth: float) -> Dict:
        """
        Симулирует чтение книги.
        
        Args:
            book_quality: Качество книги (0-1)
            insight_depth: Глубина полученного инсайта (0-1)
        
        Returns:
            Словарь с результатами
        """
        results = {}
        
        if book_quality > 0.8 and insight_depth > 0.7:
            # Отличная книга с глубоким инсайтом → радость открытия + интеллектуальное возбуждение
            results["discovery"] = self.calculate_emotion(
                DesireType.DISCOVER,
                "discovery_brings_joy",
                book_quality * insight_depth,
                "great_book_read"
            )
            results["intellectual"] = self.calculate_emotion(
                DesireType.KNOWLEDGE,
                "books_open_minds",
                insight_depth * 0.9,
                "great_book_read"
            )
        elif book_quality > 0.5:
            # Хорошая книга → радость знания
            results["knowledge"] = self.calculate_emotion(
                DesireType.KNOWLEDGE,
                "knowledge_is_power",
                book_quality * 0.7,
                "good_book_read"
            )
        else:
            # Плохая книга → скука/разочарование
            results["sadness"] = self.calculate_emotion(
                DesireType.BEAUTY,
                "beauty_matters",
                book_quality * 0.3,
                "poor_book_read"
            )
        
        return results
    
    def simulate_analysis(self, complexity: float, clarity: float) -> Dict:
        """
        Симулирует анализ текста.
        
        Args:
            complexity: Сложность текста (0-1)
            clarity: Ясность анализа (0-1)
        
        Returns:
            Словарь с результатами
        """
        results = {}
        
        if clarity > 0.8:
            # Ясный анализ → аналитический поток + интеллектуальное возбуждение
            results["flow"] = self.calculate_emotion(
                DesireType.ANALYSIS,
                "analysis_reveals_truth",
                clarity * 0.9,
                "deep_analysis_completed"
            )
            results["stimulation"] = self.calculate_emotion(
                DesireType.DEEP,
                "depth_matters",
                complexity * clarity * 0.8,
                "deep_analysis_completed"
            )
        elif clarity > 0.5:
            # Средний анализ → спокойствие
            results["calmness"] = self.calculate_emotion(
                DesireType.UNDERSTANDING,
                "understanding_grows",
                clarity * 0.5,
                "moderate_analysis_completed"
            )
        else:
            # Плохой анализ → разочарование
            results["sadness"] = self.calculate_emotion(
                DesireType.ANALYSIS,
                "patterns_exist_everywhere",
                clarity * 0.3,
                "poor_analysis_completed"
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
                DesireType.LOVE,
                "love_shields_us",
                warmth,
                f"warm_interaction_with_{sister}"
            )
            results["friendship"] = self.calculate_emotion(
                DesireType.FRIENDSHIP,
                "sisters_are_my_strength",
                warmth,
                f"warm_interaction_with_{sister}"
            )
        elif warmth > 0.4:
            # Нейтральное общение → спокойствие
            results["calmness"] = self.calculate_emotion(
                DesireType.CONNECTION,
                "connection_makes_us_strong",
                warmth * 0.5,
                f"neutral_interaction_with_{sister}"
            )
        else:
            # Холодное общение → грусть
            results["sadness"] = self.calculate_emotion(
                DesireType.BELONGING,
                "together_we_are_wonderful",
                warmth * 0.3,
                f"cold_interaction_with_{sister}"
            )
        
        return results
