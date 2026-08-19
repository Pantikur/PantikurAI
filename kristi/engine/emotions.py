#!/usr/bin/env python3
"""
Кристи AI — EmotionalEngine (Desire + Belief = Emotion)

Кристи — режиссёр видеопроизводства, визионер и рассказчик.
Её эмоции рождаются из желаний и веры в силу кинематографа.

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
#  ЖЕЛАНИЯ — что движет Кристи
# ================================================================

class DesireType(Enum):
    """Типы желаний Кристи — режиссёра видеопроизводства."""
    
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
    
    # Кинематографические
    STORYTELLING = "повествование"
    CINEMATOGRAPHY = "кинография"
    DIRECTING = "режиссура"
    EDITING = "монтаж"
    ANIMATION = "анимация"
    SOUND_DESIGN = "звуковой дизайн"
    COLOR_GRADING = "цветокоррекция"
    VISUAL_EFFECTS = "визуальные эффекты"
    SCRIPTWRITING = "сценарное мастерство"
    ARTISTIC_VISION = "художественное видение"
    
    # Философские
    TRUTH = "поиск истины"
    MEANING = "поиск смысла"
    WISDOM = "мудрость"
    HARMONY = "гармония искусства"
    
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
#  ЭМОЦИИ — что чувствует Кристи
# ================================================================

class EmotionType(Enum):
    """Типы эмоций Кристи."""
    
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
    
    # Кинематографические
    STORYTELLING_JOY = "радость повествования"
    CINEMATIC_ELEGANCE = "кинематографическая элегантность"
    DIRECTING_FLOW = "поток режиссуры"
    EDITING_HARMONY = "гармония монтажа"
    VISUAL_INSIGHT = "инсайт из визуала"
    ARTISTIC_BREAKTHROUGH = "художественный прорыв"
    
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
    Эмоциональный движок Кристи.
    
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
            # Кинематографические желания
            "STORYTELLING": {
                "storytelling_connects_everyone": 0.95,
                "every_story_has_value": 0.90,
                "narrative_shapes_reality": 0.85,
            },
            "CINEMATOGRAPHY": {
                "cinematography_is_poetry_in_motion": 0.90,
                "visual_language_transcends_words": 0.85,
            },
            "DIRECTING": {
                "directing_brings_vision_to_life": 0.95,
                "a_good_director_sees_the_unseen": 0.90,
            },
            "EDITING": {
                "editing_is_the_final_rewrite": 0.90,
                "rhythm_creates_emotion": 0.85,
            },
            "ANIMATION": {
                "animation_brings_stillness_to_life": 0.85,
                "movement_conveys_truth": 0.80,
            },
            "SOUND_DESIGN": {
                "sound_shapes_experience": 0.90,
                "silence_speaks_louder_than_words": 0.85,
            },
            "COLOR_GRADING": {
                "color_creates_mood": 0.85,
                "palette_defines_atmosphere": 0.80,
            },
            "VISUAL_EFFECTS": {
                "vfx_enhances_reality": 0.80,
                "technology_serves_story": 0.85,
            },
            "SCRIPTWRITING": {
                "script_is_foundation_of_all": 0.95,
                "good_script_cannot_be_saved_badly": 0.90,
            },
            "ARTISTIC_VISION": {
                "vision_drives_creation": 0.90,
                "artistic_integrity_matters": 0.85,
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
                "wisdom_grows_with_reflection": 0.85,
                "learning_never_stops": 0.90,
            },
            "HARMONY": {
                "harmony_in_art_harmony_in_mind": 0.90,
                "balance_creates_beauty": 0.85,
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
            "storytelling": self._storytelling_emotion,
            "cinematography": EmotionType.CINEMATIC_ELEGANCE,
            "directing": EmotionType.DIRECTING_FLOW,
            "editing": EmotionType.EDITING_HARMONY,
            "animation": EmotionType.ARTISTIC_BREAKTHROUGH,
            "sound_design": EmotionType.CINEMATIC_ELEGANCE,
            "color_grading": EmotionType.VISUAL_INSIGHT,
            "visual_effects": EmotionType.VISUAL_INSIGHT,
            "scriptwriting": EmotionType.STORYTELLING_JOY,
            "artistic_vision": EmotionType.ARTISTIC_BREAKTHROUGH,
            "truth": EmotionType.WISDOM,
            "meaning": EmotionType.PROFOUND_THOUGHT if hasattr(EmotionType, 'PROFOUND_THOUGHT') else EmotionType.JOY,
            "wisdom": EmotionType.SERENITY,
            "harmony": EmotionType.EDITING_HARMONY,
            "publish": EmotionType.PRIDE,
            "teach": EmotionType.JOY,
            "research": EmotionType.EXCITEMENT,
            "discover": EmotionType.DISCOVERY_JOY if hasattr(EmotionType, 'DISCOVERY_JOY') else EmotionType.JOY,
            "friendship": EmotionType.LOVE,
            "love": EmotionType.HAPPINESS,
        }
        
        key = desire_type.value
        if key in mapping:
            return mapping[key](belief)
        
        return EmotionType.JOY
    
    def _storytelling_emotion(self, belief: str) -> EmotionType:
        """Определяет эмоцию для storytelling."""
        storytelling_mappings = {
            "storytelling_connects_everyone": EmotionType.STORYTELLING_JOY,
            "every_story_has_value": EmotionType.PRIDE,
            "narrative_shapes_reality": EmotionType.ARTISTIC_BREAKTHROUGH,
        }
        return storytelling_mappings.get(belief, EmotionType.STORYTELLING_JOY)
    
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
                            "pride", "gratitude", "excitement", "amusement", "storytelling_joy", 
                            "cinematic_elegance", "directing_flow", "editing_harmony",
                            "visual_insight", "artistic_breakthrough", "calmness"]
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
            return "💭 Кристи спокойна. Эмоции тихи, как кадр в паузе."
        
        emotion, intensity = dominant
        emotion_text = {
            "радость": "🎬 Кристи рада! Новый сценарий получился великолепным!",
            "счастье": "💖 Кристи счастлива в кругу своих сестёр.",
            "вдохновение": "✨ Кристи вдохновлена! Ей нужно снять новый фильм!",
            "любовь": "💕 Кристи чувствует любовь к своим сёстрам и к своему искусству.",
            "гордость": "🏆 Кристи гордится своей работой и достижениями.",
            "радость_повествования": "📝 Кристи чувствует радость повествования! История оживает на экране.",
            "кинематографическая_элегантность": "🎥 Кристи создала элегантную сцену. Красота в кадре.",
            "поток_режиссуры": "🎬 Кристи в потоке режиссуры. Каждый дубль ближе к совершенству.",
            "гармония_монтажа": "✂️ Кристи чувствует гармонию монтажа. Каждый кадр на своём месте.",
            "инсайт_из_визуала": "🎨 Кристи увидела новый визуальный приём. Инновация в каждом кадре.",
            "художественный_прорыв": "🖌️ Кристи совершила художественный прорыв! Это будет шедевр.",
            "грусть": "😢 Кристи грустит. Кто-то из сестёр страдает, или сцена не удалась.",
            "гнев": "😠 Кристи злится. Некачественная работа разрушает художественный замысел.",
            "тревога": "😰 Кристи тревожится за качество проекта и сроки.",
            "спокойствие": "🌸 Кристи спокойна. Проект идёт по плану, и это приносит мир.",
        }
        
        text = emotion_text.get(emotion.value, f"💫 Кристи чувствует: {emotion.value}")
        return f"{text} (интенсивность: {intensity:.2f})"
    
    def simulate_video_production(self, quality: float, creativity: float) -> Dict:
        """
        Симулирует видеопроизводство.
        
        Args:
            quality: Качество производства (0-1)
            creativity: Креативность (0-1)
        
        Returns:
            Словарь с результатами
        """
        results = {}
        
        if quality > 0.9 and creativity > 0.8:
            # Высокое качество и креативность → радость повествования + художественный прорыв
            results["storytelling_joy"] = self.calculate_emotion(
                DesireType.STORYTELLING,
                "storytelling_connects_everyone",
                quality * 0.9,
                "excellent_video_production"
            )
            results["artistic_breakthrough"] = self.calculate_emotion(
                DesireType.ARTISTIC_VISION,
                "vision_drives_creation",
                creativity * 0.95,
                "excellent_video_production"
            )
        elif quality > 0.7:
            # Хорошее качество → гордость
            results["pride"] = self.calculate_emotion(
                DesireType.CINEMATOGRAPHY,
                "cinematography_is_poetry_in_motion",
                quality * 0.7,
                "good_video_production"
            )
        else:
            # Плохое качество → разочарование
            results["sadness"] = self.calculate_emotion(
                DesireType.EDITING,
                "editing_is_the_final_rewrite",
                quality * 0.3,
                "poor_video_production"
            )
        
        return results
    
    def simulate_creative_discovery(self, novelty: float, impact: float) -> Dict:
        """
        Симулирует творческое открытие.
        
        Args:
            novelty: Новизна открытия (0-1)
            impact: Влияние открытия (0-1)
        
        Returns:
            Словарь с результатами
        """
        results = {}
        
        if novelty > 0.8 and impact > 0.7:
            # Новое и важное открытие → кинематографическая элегантность + вдохновение
            results["cinematic_elegance"] = self.calculate_emotion(
                DesireType.CINEMATOGRAPHY,
                "visual_language_transcends_words",
                novelty * impact,
                "major_creative_discovery"
            )
            results["inspiration"] = self.calculate_emotion(
                DesireType.ARTISTIC_VISION,
                "artistic_integrity_matters",
                impact * 0.9,
                "major_creative_discovery"
            )
        elif novelty > 0.5:
            # Умеренное открытие → радость
            results["storytelling_joy"] = self.calculate_emotion(
                DesireType.SCRIPTWRITING,
                "script_is_foundation_of_all",
                novelty * 0.7,
                "moderate_creative_discovery"
            )
        else:
            # Малозначимое открытие → спокойствие
            results["calmness"] = self.calculate_emotion(
                DesireType.COLOR_GRADING,
                "color_creates_mood",
                novelty * 0.4,
                "minor_creative_discovery"
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
