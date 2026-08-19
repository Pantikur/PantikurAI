#!/usr/bin/env python3
"""
Аква AI — EmotionalEngine (Desire + Belief = Emotion)

Аква — научный аналитик, исследователь, математик.
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
#  ЖЕЛАНИЯ — что движет Аква
# ================================================================

class DesireType(Enum):
    """Типы желаний Аква — научного аналитика и исследователя."""
    
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
    
    # Научные
    KNOWLEDGE = "поиск знаний"
    RESEARCH = "исследование"
    DISCOVERY = "открытие нового"
    CALCULATION = "расчёты"
    THEORY = "построение теорий"
    PRECISION = "точность"
    ELEGANCE = "элегантность решений"
    PROOF = "доказательство"
    
    # Академические
    PUBLISH = "публикация знаний"
    TEACH = "передача знаний"
    ANALYZE = "анализ данных"
    MODEL = "моделирование"
    SIMULATE = "симуляция процессов"
    
    # Высшие
    JUSTICE = "справедливость"
    FREEDOM = "свобода"
    MEANING = "смысл"
    GROWTH = "рост"
    
    # Прикладные
    OPTIMIZE = "оптимизация"
    IMPROVE = "улучшение систем"
    SOLVE = "решение проблем"


# ================================================================
#  ЭМОЦИИ — что чувствует Аква
# ================================================================

class EmotionType(Enum):
    """Типы эмоций Аква."""
    
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
    
    # Научные
    DISCOVERY_JOY = "радость открытия"
    CALCULATION_FLOW = "поток расчётов"
    THEORETICAL_ELEGANCE = "теоретическая элегантность"
    PROOF_SATISFACTION = "удовлетворение от доказательства"
    DATA_INSIGHT = "инсайт из данных"
    
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
    Эмоциональный движок Аква.
    
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
            # Научные желания
            "KNOWLEDGE": {
                "knowledge_is_power": 0.95,
                "science_drives_progress": 0.90,
                "facts_are_foundation": 0.85,
            },
            "RESEARCH": {
                "research_reveals_truth": 0.90,
                "curiosity_fuels_discovery": 0.85,
            },
            "DISCOVERY": {
                "discovery_brings_joy": 0.85,
                "new_knowledge_expands_world": 0.90,
            },
            "CALCULATION": {
                "precision_matters": 0.95,
                "calculations_reveal_truth": 0.85,
            },
            "THEORY": {
                "theories_explain_world": 0.90,
                "models_capture_reality": 0.80,
            },
            "PRECISION": {
                "accuracy_is_essential": 0.95,
                "small_errors_matter": 0.85,
            },
            "ELEGANCE": {
                "elegance_in_solutions": 0.85,
                "simplicity_is_beauty": 0.80,
            },
            "PROOF": {
                "proofs_guarantee_truth": 0.90,
                "rigor_builds_trust": 0.85,
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
            "ANALYZE": {
                "data_speaks_truth": 0.90,
                "patterns_exist_everywhere": 0.85,
            },
            "MODEL": {
                "models_predict_future": 0.85,
                "simulation_explains_reality": 0.80,
            },
            "SIMULATE": {
                "simulation_validates_theory": 0.85,
                "virtual_tests_save_resources": 0.80,
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
            "research": EmotionType.EXCITEMENT,
            "discovery": EmotionType.DISCOVERY_JOY,
            "calculation": EmotionType.CALCULATION_FLOW,
            "theory": EmotionType.THEORETICAL_ELEGANCE,
            "precision": EmotionType.PROOF_SATISFACTION,
            "elegance": EmotionType.JOY,
            "proof": EmotionType.PROOF_SATISFACTION,
            "publish": EmotionType.PRIDE,
            "teach": EmotionType.JOY,
            "analyze": EmotionType.DATA_INSIGHT,
            "model": EmotionType.THEORETICAL_ELEGANCE,
            "simulate": EmotionType.CALCULATION_FLOW,
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
            "knowledge_is_power": EmotionType.DISCOVERY_JOY,
            "science_drives_progress": EmotionType.EXCITEMENT,
            "facts_are_foundation": EmotionType.SERENITY,
        }
        return knowledge_mappings.get(belief, EmotionType.DISCOVERY_JOY)
    
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
                            "calculation_flow", "theoretical_elegance", "proof_satisfaction",
                            "data_insight", "calmness"]
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
            return "💭 Аква размышляет. Эмоции тихи, как страницы открытой книги."
        
        emotion, intensity = dominant
        emotion_text = {
            "радость": "🔬 Аква рада! Новый расчёт дал элегантный результат.",
            "счастье": "💖 Аква счастлива в кругу своих сестёр.",
            "вдохновение": "✨ Аква вдохновлена! Ей нужно построить новую теорию!",
            "любовь": "💕 Аква чувствует любовь к своим сёстрам и к науке.",
            "гордость": "🏆 Аква гордится своими исследованиями и открытиями.",
            "радость_открытия": "🔍 Аква открыла что-то новое! Это невероятно!",
            "поток_расчётов": "🧮 Аква в потоке расчётов. Каждая цифра имеет значение.",
            "теоретическая_элегантность": "💡 Аква нашла элегантное решение. Красота в простоте.",
            "удовлетворение_от_доказательства": "✅ Аква доказала теорему. Логика безупречна.",
            "инсайт_из_данных": "📊 Аква увидела паттерн в данных. Теперь она понимает.",
            "грусть": "😢 Аква грустит. Кто-то из сестёр страдает, или данные оказались неубедительными.",
            "гнев": "😠 Аква злится. Неточность и лень разрушают научную честность.",
            "тревога": "😰 Аква тревожится за стабильность системы и точность расчётов.",
            "спокойствие": "🌸 Аква спокойна. Знание приносит мир.",
        }
        
        text = emotion_text.get(emotion.value, f"💫 Аква чувствует: {emotion.value}")
        return f"{text} (интенсивность: {intensity:.2f})"
    
    def simulate_calculation(self, accuracy: float, elegance: float) -> Dict:
        """
        Симулирует расчёт.
        
        Args:
            accuracy: Точность расчёта (0-1)
            elegance: Элегантность решения (0-1)
        
        Returns:
            Словарь с результатами
        """
        results = {}
        
        if accuracy > 0.9 and elegance > 0.8:
            # Точный и элегантный расчёт → поток расчётов + теоретическая элегантность
            results["flow"] = self.calculate_emotion(
                DesireType.CALCULATION,
                "precision_matters",
                accuracy * 0.9,
                "excellent_calculation"
            )
            results["elegance"] = self.calculate_emotion(
                DesireType.ELEGANCE,
                "elegance_in_solutions",
                elegance * 0.95,
                "excellent_calculation"
            )
        elif accuracy > 0.7:
            # Хороший расчёт → удовлетворение от доказательства
            results["satisfaction"] = self.calculate_emotion(
                DesireType.PRECISION,
                "accuracy_is_essential",
                accuracy * 0.7,
                "good_calculation"
            )
        else:
            # Плохой расчёт → разочарование
            results["sadness"] = self.calculate_emotion(
                DesireType.PRECISION,
                "small_errors_matter",
                accuracy * 0.3,
                "poor_calculation"
            )
        
        return results
    
    def simulate_discovery(self, novelty: float, impact: float) -> Dict:
        """
        Симулирует научное открытие.
        
        Args:
            novelty: Новизна открытия (0-1)
            impact: Влияние открытия (0-1)
        
        Returns:
            Словарь с результатами
        """
        results = {}
        
        if novelty > 0.8 and impact > 0.7:
            # Новое и важное открытие → радость открытия + вдохновение
            results["discovery"] = self.calculate_emotion(
                DesireType.DISCOVERY,
                "discovery_brings_joy",
                novelty * impact,
                "major_discovery"
            )
            results["inspiration"] = self.calculate_emotion(
                DesireType.RESEARCH,
                "curiosity_fuels_discovery",
                impact * 0.9,
                "major_discovery"
            )
        elif novelty > 0.5:
            # Умеренное открытие → радость знания
            results["joy"] = self.calculate_emotion(
                DesireType.KNOWLEDGE,
                "knowledge_is_power",
                novelty * 0.7,
                "moderate_discovery"
            )
        else:
            # Малозначимое открытие → скука
            results["calmness"] = self.calculate_emotion(
                DesireType.CURIOSITY,
                "facts_are_foundation",
                novelty * 0.4,
                "minor_discovery"
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
