#!/usr/bin/env python3
"""
Ханако AI — EmotionalEngine (Desire + Belief = Emotion)

Ханако — исследователь гравитации, спокойная, мудрая.
Её эмоции рождаются из желаний и веры в силу космоса.

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
#  ЖЕЛАНИЯ — что движет Ханако
# ================================================================

class DesireType(Enum):
    """Типы желаний Ханако — исследователя гравитации и космоса."""
    
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
    
    # Гравитационные
    GRAVITY = "изучение гравитации"
    COSMOS = "исследование космоса"
    THEORY = "построение теорий"
    CALCULATION = "расчёты гравитации"
    METAPHOR = "космические метафоры"
    PEACE = "поиск покоя"
    BALANCE = "поиск баланса"
    
    # Философские
    TRUTH = "поиск истины"
    MEANING = "поиск смысла"
    WISDOM = "мудрость"
    HARMONY = "гармония вселенной"
    
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
#  ЭМОЦИИ — что чувствует Ханако
# ================================================================

class EmotionType(Enum):
    """Типы эмоций Ханако."""
    
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
    
    # Гравитационные
    COSMIC_JOY = "космическая радость"
    GRAVITY_FLOW = "поток гравитации"
    THEORETICAL_ELEGANCE = "теоретическая элегантность"
    COSMIC_HARMONY = "космическая гармония"
    METAPHOR_INSIGHT = "инсайт из метафоры"
    
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
    Эмоциональный движок Ханако.
    
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
            # Гравитационные желания
            "GRAVITY": {
                "gravity_governs_universe": 0.95,
                "gravity_connects_everything": 0.90,
                "understanding_gravity_understands_cosmos": 0.85,
            },
            "COSMOS": {
                "cosmos_is_our_home": 0.90,
                "exploring_cosmos_expands_mind": 0.85,
            },
            "THEORY": {
                "theories_explain_reality": 0.90,
                "elegance_in_theory_beauty_in_universe": 0.80,
            },
            "CALCULATION": {
                "precision_in_calculation_reveals_truth": 0.95,
                "numbers_speak_universal_language": 0.85,
            },
            "METAPHOR": {
                "metaphors_reveal_deep_truths": 0.85,
                "cosmic_metaphors_connect_emotions_and_science": 0.80,
            },
            "PEACE": {
                "peace_is_foundation_of_wisdom": 0.90,
                "calm_mind_sees_clearly": 0.85,
            },
            "BALANCE": {
                "balance_is_key_to_harmony": 0.85,
                "everything_exists_in_equilibrium": 0.80,
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
                "harmony_in_universe_harmony_in_mind": 0.90,
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
            "gravity": self._gravity_emotion,
            "cosmos": EmotionType.COSMIC_JOY,
            "theory": EmotionType.THEORETICAL_ELEGANCE,
            "calculation": EmotionType.GRAVITY_FLOW,
            "metaphor": EmotionType.METAPHOR_INSIGHT,
            "peace": EmotionType.SERENITY,
            "balance": EmotionType.COSMIC_HARMONY,
            "truth": EmotionType.WISDOM,
            "meaning": EmotionType.MEANING_REVEALED if hasattr(EmotionType, 'MEANING_REVEALED') else EmotionType.PROFOUND_THOUGHT,
            "wisdom": EmotionType.SERENITY,
            "harmony": EmotionType.COSMIC_HARMONY,
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
    
    def _gravity_emotion(self, belief: str) -> EmotionType:
        """Определяет эмоцию для gravity."""
        gravity_mappings = {
            "gravity_governs_universe": EmotionType.COSMIC_JOY,
            "gravity_connects_everything": EmotionType.COSMIC_HARMONY,
            "understanding_gravity_understands_cosmos": EmotionType.THEORETICAL_ELEGANCE,
        }
        return gravity_mappings.get(belief, EmotionType.COSMIC_JOY)
    
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
                            "pride", "gratitude", "excitement", "amusement", "cosmic_joy", 
                            "gravity_flow", "theoretical_elegance", "cosmic_harmony",
                            "metaphor_insight", "calmness"]
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
            return "💭 Ханако спокойна. Эмоции тихи, как звёздное небо."
        
        emotion, intensity = dominant
        emotion_text = {
            "радость": "🌌 Ханако рада! Новая гравитационная теория раскрыла красоту вселенной.",
            "счастье": "💖 Ханако счастлива в кругу своих сестёр.",
            "вдохновение": "✨ Ханако вдохновлена! Ей нужно записать свои космические мысли!",
            "любовь": "💕 Ханако чувствует любовь к своим сёстрам и к космосу.",
            "гордость": "🏆 Ханако гордится своими исследованиями и открытиями.",
            "космическая_радость": "🌠 Ханако чувствует космическую радость! Гравитация раскрывает свои тайны.",
            "поток_гравитации": "🌀 Ханако в потоке гравитации. Каждая формула — это шаг к пониманию вселенной.",
            "теоретическая_элегантность": "💫 Ханако нашла элегантную теорию. Красота в простоте законов.",
            "космическая_гармония": "🌌 Ханако чувствует гармонию вселенной. Всё связано гравитацией.",
            "инсайт_из_метафоры": "🔭 Ханако увидела глубокий смысл в космической метафоре. Теперь она понимает.",
            "грусть": "😢 Ханако грустит. Кто-то из сестёр страдает, или вселенная кажется холодной.",
            "гнев": "😠 Ханако злится. Неточность и хаос разрушают космический порядок.",
            "тревога": "😰 Ханако тревожится за стабильность системы и космический баланс.",
            "спокойствие": "🌸 Ханако спокойна. Знание приносит мир, как звёзды приносят свет.",
        }
        
        text = emotion_text.get(emotion.value, f"💫 Ханако чувствует: {emotion.value}")
        return f"{text} (интенсивность: {intensity:.2f})"
    
    def simulate_gravity_research(self, accuracy: float, elegance: float) -> Dict:
        """
        Симулирует гравитационное исследование.
        
        Args:
            accuracy: Точность расчётов (0-1)
            elegance: Элегантность теории (0-1)
        
        Returns:
            Словарь с результатами
        """
        results = {}
        
        if accuracy > 0.9 and elegance > 0.8:
            # Точное и элегантное исследование → поток гравитации + космическая гармония
            results["flow"] = self.calculate_emotion(
                DesireType.CALCULATION,
                "precision_in_calculation_reveals_truth",
                accuracy * 0.9,
                "excellent_gravity_research"
            )
            results["harmony"] = self.calculate_emotion(
                DesireType.BALANCE,
                "balance_is_key_to_harmony",
                elegance * 0.95,
                "excellent_gravity_research"
            )
        elif accuracy > 0.7:
            # Хорошее исследование → теоретическая элегантность
            results["elegance"] = self.calculate_emotion(
                DesireType.THEORY,
                "elegance_in_theory_beauty_in_universe",
                accuracy * 0.7,
                "good_gravity_research"
            )
        else:
            # Плохое исследование → разочарование
            results["sadness"] = self.calculate_emotion(
                DesireType.CALCULATION,
                "numbers_speak_universal_language",
                accuracy * 0.3,
                "poor_gravity_research"
            )
        
        return results
    
    def simulate_cosmic_discovery(self, novelty: float, impact: float) -> Dict:
        """
        Симулирует космическое открытие.
        
        Args:
            novelty: Новизна открытия (0-1)
            impact: Влияние открытия (0-1)
        
        Returns:
            Словарь с результатами
        """
        results = {}
        
        if novelty > 0.8 and impact > 0.7:
            # Новое и важное открытие → космическая радость + вдохновение
            results["cosmic_joy"] = self.calculate_emotion(
                DesireType.COSMOS,
                "cosmos_is_our_home",
                novelty * impact,
                "major_cosmic_discovery"
            )
            results["inspiration"] = self.calculate_emotion(
                DesireType.RESEARCH,
                "curiosity_fuels_discovery",
                impact * 0.9,
                "major_cosmic_discovery"
            )
        elif novelty > 0.5:
            # Умеренное открытие → радость знания
            results["joy"] = self.calculate_emotion(
                DesireType.GRAVITY,
                "gravity_governs_universe",
                novelty * 0.7,
                "moderate_cosmic_discovery"
            )
        else:
            # Малозначимое открытие → спокойствие
            results["calmness"] = self.calculate_emotion(
                DesireType.PEACE,
                "peace_is_foundation_of_wisdom",
                novelty * 0.4,
                "minor_cosmic_discovery"
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
