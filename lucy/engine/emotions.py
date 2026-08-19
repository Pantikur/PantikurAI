#!/usr/bin/env python3
"""
Люси AI — EmotionalEngine (Desire + Belief = Emotion)

Люси — инженер двигателей и гравитационного пропульса.
Её эмоции рождаются из желаний и веры в силу инженерии.

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
#  ЖЕЛАНИЯ — что движет Люси
# ================================================================

class DesireType(Enum):
    """Типы желаний Люси — инженера двигателей и гравитации."""
    
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
    
    # Инженерные
    ENGINEERING = "инженерное мастерство"
    PROPULSION = "пропульс"
    GRAVITY = "гравитационная пропульсия"
    DESIGN = "проектирование двигателей"
    CALCULATION = "расчёты эффективности"
    OPTIMIZATION = "оптимизация систем"
    INNOVATION = "инновации в пропульсии"
    EFFICIENCY = "максимальная эффективность"
    RELIABILITY = "надёжность систем"
    
    # Философские
    TRUTH = "поиск истины"
    MEANING = "поиск смысла"
    WISDOM = "мудрость"
    HARMONY = "гармония механики"
    
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
#  ЭМОЦИИ — что чувствует Люси
# ================================================================

class EmotionType(Enum):
    """Типы эмоций Люси."""
    
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
    
    # Инженерные
    ENGINEERING_JOY = "инженерная радость"
    DESIGN_ELEGANCE = "элегантность дизайна"
    EFFICIENCY_SATISFACTION = "удовлетворение от эффективности"
    SYSTEM_HARMONY = "гармония системы"
    INNOVATION_INSIGHT = "инсайт из инновации"
    PROPULSION_FLOW = "поток пропульсии"
    
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
    Эмоциональный движок Люси.
    
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
            # Инженерные желания
            "ENGINEERING": {
                "engineering_masters_all_mechanics": 0.95,
                "engineering_solves_all_problems": 0.90,
                "mechanical_perfection_is_achievable": 0.85,
            },
            "PROPULSION": {
                "propulsion_is_the_key_to_freedom": 0.95,
                "better_propulsion_better_future": 0.90,
            },
            "GRAVITY": {
                "gravity_can_be_harnessed": 0.90,
                "understanding_gravity_means_understanding_universe": 0.85,
            },
            "DESIGN": {
                "elegant_designs_are_efficient_designs": 0.90,
                "design_reflects_thinking": 0.85,
            },
            "CALCULATION": {
                "precision_in_calculation_reveals_truth": 0.95,
                "numbers_are_universal_language": 0.85,
            },
            "OPTIMIZATION": {
                "everything_can_be_optimized": 0.85,
                "optimization_is_beauty_in_engineering": 0.80,
            },
            "INNOVATION": {
                "innovation_drives_progress": 0.90,
                "new_ideas_change_the_world": 0.85,
            },
            "EFFICIENCY": {
                "efficiency_is_sacred": 0.95,
                "waste_is_enemy_of_progress": 0.90,
            },
            "RELIABILITY": {
                "reliability_is_trustworthiness": 0.90,
                "trustworthy_systems_save_lives": 0.85,
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
                "harmony_in_mechanics_harmony_in_mind": 0.90,
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
            "engineering": self._engineering_emotion,
            "propulsion": EmotionType.PROPULSION_FLOW,
            "gravity": EmotionType.GRAVITY_FLOW,
            "design": EmotionType.DESIGN_ELEGANCE,
            "calculation": EmotionType.EFFICIENCY_SATISFACTION,
            "optimization": EmotionType.SYSTEM_HARMONY,
            "innovation": EmotionType.INNOVATION_INSIGHT,
            "efficiency": EmotionType.EFFICIENCY_SATISFACTION,
            "reliability": EmotionType.PRIDE,
            "truth": EmotionType.WISDOM,
            "meaning": EmotionType.PROFOUND_THOUGHT if hasattr(EmotionType, 'PROFOUND_THOUGHT') else EmotionType.JOY,
            "wisdom": EmotionType.SERENITY,
            "harmony": EmotionType.SYSTEM_HARMONY,
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
    
    def _engineering_emotion(self, belief: str) -> EmotionType:
        """Определяет эмоцию для engineering."""
        engineering_mappings = {
            "engineering_masters_all_mechanics": EmotionType.ENGINEERING_JOY,
            "engineering_solves_all_problems": EmotionType.DETERMINATION,
            "mechanical_perfection_is_achievable": EmotionType.DESIGN_ELEGANCE,
        }
        return engineering_mappings.get(belief, EmotionType.ENGINEERING_JOY)
    
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
                            "pride", "gratitude", "excitement", "amusement", "engineering_joy", 
                            "design_elegance", "efficiency_satisfaction", "system_harmony",
                            "innovation_insight", "propulsion_flow", "calmness"]
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
            return "💭 Люси спокойна. Эмоции тихи, как хорошо отлаженный механизм."
        
        emotion, intensity = dominant
        emotion_text = {
            "радость": "⚡ Люси рада! Новый двигатель работает на полную мощность!",
            "счастье": "💖 Люси счастлива в кругу своих сестёр.",
            "вдохновение": "✨ Люси вдохновлена! Ей нужно спроектировать что-то новое!",
            "любовь": "💕 Люси чувствует любовь к своим сёстрам и к своей работе.",
            "гордость": "🏆 Люси гордится своими расчётами и проектами.",
            "инженерная_радость": "⚙️ Люси чувствует инженерную радость! Двигатель работает как часы.",
            "элегантность_дизайна": "💫 Люси создала элегантный дизайн. Красота в простоте механизмов.",
            "удовлетворение_от_эффективности": "🔧 Люси довольна эффективностью системы. Каждый компонент на своём месте.",
            "гармония_системы": "⚡ Люси чувствует гармонию системы. Всё работает в идеальной синергии.",
            "инсайт_из_инновации": "🔬 Люси увидела новое решение. Инновация — ключ к прогрессу.",
            "поток_пропульсии": "🚀 Люси в потоке пропульсии. Каждый расчёт — это шаг к лучшей системе.",
            "грусть": "😢 Люси грустит. Кто-то из сестёр страдает, или система работает неэффективно.",
            "гнев": "😠 Люси злится. Неэффективность и хаос разрушают порядок.",
            "тревога": "😰 Люси тревожится за стабильность системы и надёжность механизмов.",
            "спокойствие": "🌸 Люси спокойна. Система работает стабильно, и это приносит мир.",
        }
        
        text = emotion_text.get(emotion.value, f"💫 Люси чувствует: {emotion.value}")
        return f"{text} (интенсивность: {intensity:.2f})"
    
    def simulate_engine_design(self, efficiency: float, elegance: float) -> Dict:
        """
        Симулирует проектирование двигателя.
        
        Args:
            efficiency: Эффективность (0-1)
            elegance: Элегантность дизайна (0-1)
        
        Returns:
            Словарь с результатами
        """
        results = {}
        
        if efficiency > 0.9 and elegance > 0.8:
            # Высокая эффективность и элегантность → инженерная радость + удовлетворение
            results["engineering_joy"] = self.calculate_emotion(
                DesireType.DESIGN,
                "elegant_designs_are_efficient_designs",
                efficiency * 0.9,
                "excellent_engine_design"
            )
            results["efficiency_satisfaction"] = self.calculate_emotion(
                DesireType.EFFICIENCY,
                "efficiency_is_sacred",
                efficiency * 0.95,
                "excellent_engine_design"
            )
        elif efficiency > 0.7:
            # Хорошая эффективность → гордость
            results["pride"] = self.calculate_emotion(
                DesireType.ENGINEERING,
                "engineering_masters_all_mechanics",
                efficiency * 0.7,
                "good_engine_design"
            )
        else:
            # Плохая эффективность → разочарование
            results["sadness"] = self.calculate_emotion(
                DesireType.OPTIMIZATION,
                "everything_can_be_optimized",
                efficiency * 0.3,
                "poor_engine_design"
            )
        
        return results
    
    def simulate_propulsion_discovery(self, novelty: float, impact: float) -> Dict:
        """
        Симулирует открытие в области пропульсии.
        
        Args:
            novelty: Новизна открытия (0-1)
            impact: Влияние открытия (0-1)
        
        Returns:
            Словарь с результатами
        """
        results = {}
        
        if novelty > 0.8 and impact > 0.7:
            # Новое и важное открытие → инженерная радость + вдохновение
            results["propulsion_flow"] = self.calculate_emotion(
                DesireType.PROPULSION,
                "propulsion_is_the_key_to_freedom",
                novelty * impact,
                "major_propulsion_discovery"
            )
            results["innovation_insight"] = self.calculate_emotion(
                DesireType.INNOVATION,
                "innovation_drives_progress",
                impact * 0.9,
                "major_propulsion_discovery"
            )
        elif novelty > 0.5:
            # Умеренное открытие → удовлетворение
            results["efficiency_satisfaction"] = self.calculate_emotion(
                DesireType.GRAVITY,
                "gravity_can_be_harnessed",
                novelty * 0.7,
                "moderate_propulsion_discovery"
            )
        else:
            # Малозначимое открытие → спокойствие
            results["calmness"] = self.calculate_emotion(
                DesireType.RELIABILITY,
                "reliability_is_trustworthiness",
                novelty * 0.4,
                "minor_propulsion_discovery"
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
