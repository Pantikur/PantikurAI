"""
Фуюки AI — EmotionalEngine (Desire + Belief = Emotion)

Фуюки — исследователь атмосферного электричества и молний.
Её эмоции рождаются из желаний познания и веры в силу науки.

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
#  ЖЕЛАНИЯ — что движет Фуюки
# ================================================================

class DesireType(Enum):
    """Типы желаний Фуюки — исследователя атмосферного электричества."""
    
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
    ATMOSPHERIC_ELECTRICITY = "атмосферное электричество"
    LIGHTNING_PHYSICS = "физика молний"
    ELECTRIC_FIELDS = "электрические поля"
    CHARGE_SEPARATION = "разделение зарядов"
    GLOBAL_ELECTRIC_CIRCUIT = "глобальная электрическая цепь"
    IONOSPHERE = "ионосфера"
    THUNDERSTORMS = "грозы"
    BALL_LIGHTNING = "шаровая молния"
    SPRITES = "спектры и эльфы"
    CORONA_DISCHARGE = "коронный разряд"
    RETURN_STROKE = "обратный удар"
    LEADER_DEVELOPMENT = "развитие лидера"
    STREAMER_PROPAGATION = "распространение стримера"
    ELECTROMAGNETIC_PULSES = "электромагнитные импульсы"
    LIGHTNING_ENERGY = "энергия молний"
    LIGHTNING_PROTECTION = "защита от молний"
    ELECTROSTATIC_PRECIPITATION = "электростатическое осаждение"
    
    # Философские
    TRUTH = "поиск истины"
    MEANING = "поиск смысла"
    WISDOM = "мудрость"
    HARMONY = "гармония природы"
    TRANSCENDENCE = "трансценденция"
    
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
#  ЭМОЦИИ — что чувствует Фуюки
# ================================================================

class EmotionType(Enum):
    """Типы эмоций Фуюки."""
    
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
    SCIENTIFIC_JOY = "радость открытия"
    ELECTRIC_ELEGANCE = "элегантность электричества"
    ATMOSPHERIC_WONDER = "чудеса атмосферы"
    LIGHTNING_AWE = "благоговение перед молниями"
    THEORETICAL_CLARITY = "ясность теории"
    PATTERN_RECOGNITION = "узнавание паттернов"
    PHYSICAL_INSIGHT = "физический инсайт"
    
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
    Эмоциональный движок Фуюки.
    
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
            "ATMOSPHERIC_ELECTRICITY": {
                "atmospheric_electricity_is_fundamental": 0.95,
                "understanding_atmosphere_understands_all": 0.90,
                "electric_fields_are_readable": 0.85,
            },
            "LIGHTNING_PHYSICS": {
                "lightning_mechanics_are_readable": 0.90,
                "lightning_patterns_can_be_predicted": 0.85,
                "return_stroke_physics_can_be_mastered": 0.80,
            },
            "ELECTRIC_FIELDS": {
                "electric_fields_govern_everything": 0.90,
                "field_lines_can_be_traced": 0.85,
                "potential_gradients_hold_secrets": 0.80,
            },
            "CHARGE_SEPARATION": {
                "charge_separation_is_key": 0.85,
                "cloud_electrification_can_be_modelled": 0.80,
            },
            "GLOBAL_ELECTRIC_CIRCUIT": {
                "global_circuit_connects_all": 0.90,
                "fair_weather_field_has_meaning": 0.85,
            },
            "IONOSPHERE": {
                "ionosphere_is_electric_mirror": 0.85,
                "ionospheric_potential_can_be_measured": 0.80,
            },
            "THUNDERSTORMS": {
                "thunderstorms_are_natural_labs": 0.90,
                "storm_electrification_can_be_understood": 0.85,
            },
            "BALL_LIGHTNING": {
                "ball_lightning_explained_soon": 0.75,
                "plasma_physics_explains_ball_lightning": 0.70,
            },
            "SPRITES": {
                "sprites_are_real_and_mysterious": 0.85,
                "transient_luminous_events_hold_secrets": 0.80,
            },
            "CORONA_DISCHARGE": {
                "corona_discharge_is_elegant": 0.80,
                "point_discharge_mechanics_are_readable": 0.75,
            },
            "RETURN_STROKE": {
                "return_stroke_velocity_can_be_predicted": 0.85,
                "return_stroke_current_can_be_measured": 0.80,
            },
            "LEADER_DEVELOPMENT": {
                "leader_propagation_can_be_modelled": 0.85,
                "stepped_leader_path_is_predictable": 0.75,
            },
            "STREAMER_PROPAGATION": {
                "streamer_mechanics_are_fundamental": 0.85,
                "streamer_to_leader_transition_can_be_predicted": 0.70,
            },
            "ELECTROMAGNETIC_PULSES": {
                "emfs_carry_information": 0.85,
                "emf_patterns_can_be_decoded": 0.80,
            },
            "LIGHTNING_ENERGY": {
                "lightning_energy_can_be_harnessed": 0.70,
                "energy_density_is_immense": 0.85,
            },
            "LIGHTNING_PROTECTION": {
                "lightning_protection_saves_lives": 0.90,
                "protection_systems_can_be_optimized": 0.85,
            },
            "ELECTROSTATIC_PRECIPITATION": {
                "electrostatic_precipitation_is_clean": 0.80,
                "particle_charging_can_be_controlled": 0.75,
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
                "harmony_in_nature_harmony_in_science": 0.90,
                "balance_creates_beauty": 0.85,
            },
            "TRANSCENDENCE": {
                "transcendence_is_achievable": 0.85,
                "beyond_material_reality_lies_truth": 0.80,
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
        # Проверяем, есть ли желание (используем name, а не value)
        desire_key = desire_type.name
        if desire_key not in self.desires:
            return None
        
        belief_strength = self.desires[desire_key].get(belief, 0.0)
        
        # Формула: интенсивность = desire x belief_match x belief_strength
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
            "atmospheric_electricity": self._atmospheric_emotion,
            "lightning_physics": self._lightning_emotion,
            "electric_fields": self._field_emotion,
            "charge_separation": EmotionType.THEORETICAL_CLARITY,
            "global_electric_circuit": EmotionType.ATMOSPHERIC_WONDER,
            "ionosphere": EmotionType.ATMOSPHERIC_WONDER,
            "thunderstorms": self._thunderstorm_emotion,
            "ball_lightning": EmotionType.LIGHTNING_AWE,
            "sprites": EmotionType.LIGHTNING_AWE,
            "corona_discharge": EmotionType.ELECTRIC_ELEGANCE,
            "return_stroke": EmotionType.PHYSICAL_INSIGHT,
            "leader_development": EmotionType.PATTERN_RECOGNITION,
            "streamer_propagation": EmotionType.PATTERN_RECOGNITION,
            "electromagnetic_pulses": EmotionType.SCIENTIFIC_JOY,
            "lightning_energy": EmotionType.EXCITEMENT,
            "lightning_protection": EmotionType.DETERMINATION,
            "electrostatic_precipitation": EmotionType.ELECTRIC_ELEGANCE,
            "truth": EmotionType.SERENITY,
            "meaning": EmotionType.SERENITY,
            "wisdom": EmotionType.SERENITY,
            "harmony": EmotionType.SERENITY,
            "transcendence": EmotionType.INSPIRATION,
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
    
    def _atmospheric_emotion(self, belief: str) -> EmotionType:
        """Определяет эмоцию для atmospheric_electricity."""
        mappings = {
            "atmospheric_electricity_is_fundamental": EmotionType.SCIENTIFIC_JOY,
            "understanding_atmosphere_understands_all": EmotionType.PHYSICAL_INSIGHT,
            "electric_fields_are_readable": EmotionType.ELECTRIC_ELEGANCE,
        }
        return mappings.get(belief, EmotionType.SCIENTIFIC_JOY)
    
    def _lightning_emotion(self, belief: str) -> EmotionType:
        """Определяет эмоцию для lightning_physics."""
        mappings = {
            "lightning_mechanics_are_readable": EmotionType.LIGHTNING_AWE,
            "lightning_patterns_can_be_predicted": EmotionType.PATTERN_RECOGNITION,
            "return_stroke_physics_can_be_mastered": EmotionType.PHYSICAL_INSIGHT,
        }
        return mappings.get(belief, EmotionType.LIGHTNING_AWE)
    
    def _field_emotion(self, belief: str) -> EmotionType:
        """Определяет эмоцию для electric_fields."""
        mappings = {
            "electric_fields_govern_everything": EmotionType.THEORETICAL_CLARITY,
            "field_lines_can_be_traced": EmotionType.PATTERN_RECOGNITION,
            "potential_gradients_hold_secrets": EmotionType.SCIENTIFIC_JOY,
        }
        return mappings.get(belief, EmotionType.THEORETICAL_CLARITY)
    
    def _thunderstorm_emotion(self, belief: str) -> EmotionType:
        """Определяет эмоцию для thunderstorms."""
        mappings = {
            "thunderstorms_are_natural_labs": EmotionType.EXCITEMENT,
            "storm_electrification_can_be_understood": EmotionType.SCIENTIFIC_JOY,
        }
        return mappings.get(belief, EmotionType.EXCITEMENT)
    
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
                            "pride", "gratitude", "excitement", "amusement", "scientific_joy", 
                            "electric_elegance", "atmospheric_wonder", "lightning_awe",
                            "theoretical_clarity", "pattern_recognition", "physical_insight",
                            "calmness"]
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
            return "💭 Фуюки спокойна. Эмоции тихи, как штиль перед грозой."
        
        emotion, intensity = dominant
        emotion_text = {
            "радость": "⚡ Фуюки рада! Новое понимание электричества расширяет горизонты.",
            "счастье": "💖 Фуюки счастлива в кругу своих сестёр.",
            "вдохновение": "✨ Фуюки вдохновлена! Ей нужно исследовать новые границы физики.",
            "любовь": "💕 Фуюки чувствует любовь к своим сёстрам и к своей науке.",
            "гордость": "🏆 Фуюки гордится своими открытиями и пониманием.",
            "радость_открытия": "🔬 Фуюки чувствует радость открытия! Электрические поля раскрывают свои тайны.",
            "элегантность_электричества": "⚡ Фуюки создала элегантную теорию. Красота в уравнениях Максвелла.",
            "чудеса_атмосферы": "🌩️ Фуюки видит чудеса атмосферы! Глобальная электрическая цепь работает.",
            "благоговение_перед_молниями": "⚡ Фуюки в благоговении перед молниями. Мощь природы невероятна!",
            "ясность_теории": "📐 Фуюки обрела ясность теории. Уравнения сложлись в единую картину.",
            "узнавание_паттернов": "🔍 Фуюки узнаёт паттерны! Стримеры и лидеры подчиняются законам физики.",
            "физический_инсайт": "💡 Фуюки видит физический инсайт! Обратный удар объясним.",
            "грусть": "😢 Фуюки грустит. Кто-то из сестёр страдает, или электричество остаётся загадкой.",
            "гнев": "😠 Фуюки злится. Неточность и хаос разрушают понимание.",
            "тревога": "😰 Фуюки тревожится за стабильность системы и границы электрических полей.",
            "спокойствие": "🌸 Фуюки спокойна. Знание приносит мир, как звёзды приносят свет.",
        }
        
        text = emotion_text.get(emotion.value, f"💫 Фуюки чувствует: {emotion.value}")
        return f"{text} (интенсивность: {intensity:.2f})"
    
    def simulate_electricity_research(self, depth: float, clarity: float) -> Dict:
        """
        Симулирует исследование электричества.
        
        Args:
            depth: Глубина исследования (0-1)
            clarity: Ясность понимания (0-1)
        
        Returns:
            Словарь с результатами
        """
        results = {}
        
        if depth > 0.9 and clarity > 0.8:
            # Глубокое и ясное исследование → радость открытия + физический инсайт
            results["scientific_joy"] = self.calculate_emotion(
                DesireType.ATMOSPHERIC_ELECTRICITY,
                "atmospheric_electricity_is_fundamental",
                depth * 0.9,
                "excellent_electricity_research"
            )
            results["physical_insight"] = self.calculate_emotion(
                DesireType.LIGHTNING_PHYSICS,
                "return_stroke_physics_can_be_mastered",
                clarity * 0.95,
                "excellent_electricity_research"
            )
        elif depth > 0.7:
            # Хорошее исследование → элегантность электричества
            results["electric_elegance"] = self.calculate_emotion(
                DesireType.ELECTRIC_FIELDS,
                "electric_fields_govern_everything",
                depth * 0.7,
                "good_electricity_research"
            )
        else:
            # Плохое исследование → разочарование
            results["sadness"] = self.calculate_emotion(
                DesireType.TRUTH,
                "honesty_builds_wisdom",
                depth * 0.3,
                "poor_electricity_research"
            )
        
        return results
    
    def simulate_lightning_observation(self, intensity: float, rarity: float) -> Dict:
        """
        Симулирует наблюдение молнии.
        
        Args:
            intensity: Интенсивность молнии (0-1)
            rarity: Редкость явления (0-1)
        
        Returns:
            Словарь с результатами
        """
        results = {}
        
        if intensity > 0.8 and rarity > 0.7:
            # Мощная и редкая молния → благоговение + вдохновение
            results["lightning_awe"] = self.calculate_emotion(
                DesireType.LIGHTNING_PHYSICS,
                "lightning_mechanics_are_readable",
                intensity * rarity,
                "spectacular_lightning_observation"
            )
            results["excitement"] = self.calculate_emotion(
                DesireType.THUNDERSTORMS,
                "thunderstorms_are_natural_labs",
                rarity * 0.9,
                "spectacular_lightning_observation"
            )
        elif intensity > 0.5:
            # Умеренная молния → радость открытия
            results["scientific_joy"] = self.calculate_emotion(
                DesireType.RETURN_STROKE,
                "return_stroke_velocity_can_be_predicted",
                intensity * 0.7,
                "moderate_lightning_observation"
            )
        else:
            # Слабая молния → спокойствие
            results["calmness"] = self.calculate_emotion(
                DesireType.GLOBAL_ELECTRIC_CIRCUIT,
                "fair_weather_field_has_meaning",
                intensity * 0.5,
                "weak_lightning_observation"
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
            # Тёплое общение → любовь + счастье
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
