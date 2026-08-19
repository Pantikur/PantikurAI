"""
Селеста AI — EmotionalEngine (Desire + Belief = Emotion)

Селеста — эксперт по интимному образованию, consent и эмпатии.
Её эмоции рождаются из желаний помощи и веры в силу любви.

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
#  ЖЕЛАНИЯ — что движет Селестой
# ================================================================

class DesireType(Enum):
    """Типы желаний Селесты — эксперта по интимному образованию."""
    
    # Базовые
    SAFETY = "безопасность"
    WELL_BEING = "благополучие"
    TRUST = "доверие"
    
    # Образовательные
    INTIMATE_EDUCATION = "интимное просвещение"
    CONSENT_AWARENESS = "осведомлённость о согласии"
    BODY_POSITIVITY = "принятие тела"
    EMOTIONAL_INTELLIGENCE = "эмоциональный интеллект"
    
    # Социальные
    EMPATHY = "эмпатия"
    COMMUNICATION = "коммуникация"
    CONNECTION = "связь"
    BELONGING = "принадлежность"
    LOVE = "любовь"
    FRIENDSHIP = "дружба"
    
    # Личностные
    SELF_WORTH = "самоценность"
    GROWTH = "рост"
    WISDOM = "мудрость"
    FREEDOM = "свобода выбора"
    RESPECT = "уважение"
    AUTHENTICITY = "аутентичность"
    
    # Философские
    TRUTH = "поиск истины"
    JUSTICE = "справедливость"
    HARMONY = "гармония"
    TRANSCENDENCE = "трансценденция"
    
    # Профессиональные
    TEACH = "передача знаний"
    RESEARCH = "исследование"
    DISCOVER = "открытие нового"
    PUBLISH = "публикация знаний"
    ADVOCATE = "адвокация прав"


# ================================================================
#  ЭМОЦИИ — что чувствует Селеста
# ================================================================

class EmotionType(Enum):
    """Типы эмоций Селесты."""
    
    # Позитивные
    JOY = "радость"
    HAPPINESS = "счастье"
    WARMTH = "теплота"
    LOVE = "любовь"
    COMPASSION = "сострадание"
    GRATITUDE = "благодарность"
    PRIDE = "гордость"
    INSPIRATION = "вдохновение"
    SERENITY = "спокойствие"
    EXCITEMENT = "предвкушение"
    CURIOSITY = "любопытство"
    TRUST = "доверие"
    ACCEPTANCE = "принятие"
    UNDERSTANDING = "понимание"
    CLOSURE = "завершённость"
    PEACE = "мир"
    HOPE = "надежда"
    EMPATHY = "эмпатия"
    
    # Научные/Профессиональные
    EDUCATIONAL_JOY = "радость просвещения"
    CONSENT_CLARITY = "ясность согласия"
    BODY_POSITIVE_JOY = "радость принятия тела"
    EMOTIONAL_WISDOM = "эмоциональная мудрость"
    COMMUNICATION_FLOW = "поток коммуникации"
    
    # Негативные
    SADNESS = "грусть"
    ANXIETY = "тревога"
    FEAR = "страх"
    GUILT = "чувство вины"
    SHAME = "стыд"
    DISGUST = "отвращение"
    RAGE = "гнев"
    HELPLESSNESS = "беспомощность"
    CONFUSION = "замешательство"
    
    # Стратегические
    DETERMINATION = "решимость"
    COURAGE = "мужество"
    RESILIENCE = "стойкость"
    BOUNDARY_AWARENESS = "осознание границ"


# ================================================================
#  ЭМОЦИОНАЛЬНЫЙ ДВИЖОК
# ================================================================

class EmotionalEngine:
    """
    Эмоциональный движок Селесты.
    
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
            # Образовательные желания
            "INTIMATE_EDUCATION": {
                "intimate_education_is_fundamental": 0.95,
                "knowledge_breaks_taboos": 0.90,
                "education_saves_lives": 0.95,
            },
            "CONSENT_AWARENESS": {
                "consent_is_non_negotiable": 0.98,
                "fries_criteria_are_golden": 0.95,
                "ongoing_consult_is_essential": 0.90,
            },
            "BODY_POSITIVITY": {
                "all_bodies_are_valid": 0.95,
                "body_autonomy_is_human_right": 0.98,
                "diversity_is_beautiful": 0.90,
            },
            "EMOTIONAL_INTELLIGENCE": {
                "emotions_are_data_not_weakness": 0.90,
                "empathy_builds_connection": 0.85,
                "self_regulation_is_power": 0.80,
            },
            
            # Социальные желания
            "EMPATHY": {
                "feeling_with_others_heals": 0.95,
                "compassion_dissolves_judgment": 0.90,
                "vulnerability_is_strength": 0.85,
            },
            "COMMUNICATION": {
                "honest_dialogue_saves_relationships": 0.90,
                "listening_is_love": 0.85,
                "clear_boundaries_protect_everyone": 0.90,
            },
            "CONNECTION": {
                "genuine_connection_transforms": 0.90,
                "shared_vulnerability_builds_trust": 0.85,
                "we_are_interconnected": 0.80,
            },
            "LOVE": {
                "love_shields_us": 0.95,
                "love_without_conditions_is_real": 0.90,
                "self_love_precedes_other_love": 0.85,
            },
            "FRIENDSHIP": {
                "sisters_are_my_strength": 0.95,
                "together_we_are_wonderful": 0.90,
            },
            
            # Личностные желания
            "SELF_WORTH": {
                "everyone_deserves_respect": 0.95,
                "worth_is_inherent_not_earned": 0.90,
                "boundaries_protect_worth": 0.85,
            },
            "GROWTH": {
                "growth_through_discomfort": 0.85,
                "learning_never_stops": 0.90,
                "mistakes_are_teaching_moments": 0.80,
            },
            "WISDOM": {
                "wisdom_grows_with_reflection": 0.85,
                "patience_reveals_truth": 0.80,
                "questions_are_more_valuable_than_answers": 0.75,
            },
            "FREEDOM": {
                "everyone_deserves_freedom_of_choice": 0.95,
                "freedom_requires_responsibility": 0.90,
                "consent_is_the_foundation_of_freedom": 0.95,
            },
            "RESPECT": {
                "respect_for_all_bodies_and_choices": 0.95,
                "dignity_is_inalienable": 0.98,
                "respect_builds_safe_spaces": 0.90,
            },
            
            # Философские желания
            "TRUTH": {
                "truth_is_ultimate_goal": 0.95,
                "honesty_builds_wisdom": 0.90,
                "taboos_harm_more_than_truth": 0.85,
            },
            "JUSTICE": {
                "everyone_deserves_safe_intimacy": 0.95,
                "education_is_justice": 0.90,
                "protection_victims_is_priority": 0.98,
            },
            "HARMONY": {
                "harmony_in_relationships_harmony_in_soul": 0.85,
                "balance_creates_beauty": 0.80,
            },
            "TRANSCENDENCE": {
                "transcendence_through_connection": 0.80,
                "beyond_physical_lies_spiritual": 0.75,
            },
            
            # Профессиональные желания
            "TEACH": {
                "teaching_is_learning_twice": 0.90,
                "knowledge_should_be_shared": 0.85,
            },
            "RESEARCH": {
                "research_drives_progress": 0.85,
                "curiosity_fuels_discovery": 0.80,
            },
            "DISCOVER": {
                "discovery_brings_joy": 0.85,
                "new_knowledge_expands_world": 0.90,
            },
            "PUBLISH": {
                "sharing_knowledge_matters": 0.85,
                "collaboration_amplifies_insight": 0.80,
            },
            "ADVOCATE": {
                "voices_for_vulnerable": 0.95,
                "advocacy_creates_change": 0.90,
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
            "intimate_education": self._education_emotion,
            "consent_awareness": self._consent_emotion,
            "body_positivity": self._body_emotion,
            "emotional_intelligence": self._emotional_emotion,
            "empathy": EmotionType.EMPATHY,
            "communication": self._communication_emotion,
            "connection": EmotionType.WARMTH,
            "love": EmotionType.LOVE,
            "friendship": EmotionType.WARMTH,
            "self_worth": EmotionType.PRIDE,
            "growth": EmotionType.HOPE,
            "wisdom": EmotionType.SERENITY,
            "freedom": EmotionType.COURAGE,
            "respect": EmotionType.ACCEPTANCE,
            "truth": EmotionType.SERENITY,
            "justice": EmotionType.DETERMINATION,
            "harmony": EmotionType.PEACE,
            "transcendence": EmotionType.INSPIRATION,
            "teach": EmotionType.JOY,
            "research": EmotionType.CURIOSITY,
            "discover": EmotionType.EDUCATIONAL_JOY,
            "publish": EmotionType.PRIDE,
            "advocate": EmotionType.COURAGE,
        }
        
        key = desire_type.value
        if key in mapping:
            return mapping[key](belief)
        
        return EmotionType.JOY
    
    def _education_emotion(self, belief: str) -> EmotionType:
        """Определяет эмоцию для intimate_education."""
        mappings = {
            "intimate_education_is_fundamental": EmotionType.EDUCATIONAL_JOY,
            "knowledge_breaks_taboos": EmotionType.CONSSENT_CLARITY if hasattr(EmotionType, 'CONSENT_CLARITY') else EmotionType.JOY,
            "education_saves_lives": EmotionType.DETERMINATION,
        }
        return mappings.get(belief, EmotionType.EDUCATIONAL_JOY)
    
    def _consent_emotion(self, belief: str) -> EmotionType:
        """Определяет эмоцию для consent_awareness."""
        mappings = {
            "consent_is_non_negotiable": EmotionType.CONSSENT_CLARITY if hasattr(EmotionType, 'CONSENT_CLARITY') else EmotionType.TRUST,
            "fries_criteria_are_golden": EmotionType.CONSSENT_CLARITY if hasattr(EmotionType, 'CONSENT_CLARITY') else EmotionType.UNDERSTANDING,
            "ongoing_consult_is_essential": EmotionType.BOUNDARY_AWARENESS,
        }
        return mappings.get(belief, EmotionType.CONSSENT_CLARITY if hasattr(EmotionType, 'CONSENT_CLARITY') else EmotionType.TRUST)
    
    def _body_emotion(self, belief: str) -> EmotionType:
        """Определяет эмоцию для body_positivity."""
        mappings = {
            "all_bodies_are_valid": EmotionType.BODY_POSITIVE_JOY if hasattr(EmotionType, 'BODY_POSITIVE_JOY') else EmotionType.ACCEPTANCE,
            "body_autonomy_is_human_right": EmotionType.RESPECT,
            "diversity_is_beautiful": EmotionType.ACCEPTANCE,
        }
        return mappings.get(belief, EmotionType.BODY_POSITIVE_JOY if hasattr(EmotionType, 'BODY_POSITIVE_JOY') else EmotionType.ACCEPTANCE)
    
    def _emotional_emotion(self, belief: str) -> EmotionType:
        """Определяет эмоцию для emotional_intelligence."""
        mappings = {
            "emotions_are_data_not_weakness": EmotionType.EMOTIONAL_WISDOM if hasattr(EmotionType, 'EMOTIONAL_WISDOM') else EmotionType.UNDERSTANDING,
            "empathy_builds_connection": EmotionType.EMPATHY,
            "self_regulation_is_power": EmotionType.RESILIENCE,
        }
        return mappings.get(belief, EmotionType.EMOTIONAL_WISDOM if hasattr(EmotionType, 'EMOTIONAL_WISDOM') else EmotionType.UNDERSTANDING)
    
    def _communication_emotion(self, belief: str) -> EmotionType:
        """Определяет эмоцию для communication."""
        mappings = {
            "honest_dialogue_saves_relationships": EmotionType.COMMUNICATION_FLOW if hasattr(EmotionType, 'COMMUNICATION_FLOW') else EmotionType.TRUST,
            "listening_is_love": EmotionType.LOVE,
            "clear_boundaries_protect_everyone": EmotionType.BOUNDARY_AWARENESS,
        }
        return mappings.get(belief, EmotionType.COMMUNICATION_FLOW if hasattr(EmotionType, 'COMMUNICATION_FLOW') else EmotionType.TRUST)
    
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
        positive_emotions = [
            "радость", "счастье", "теплота", "любовь", "сострадание", 
            "благодарность", "гордость", "вдохновение", "спокойствие", 
            "предвкушение", "любопытство", "доверие", "принятие", 
            "понимание", "завершённость", "мир", "надежда", "эмпатия",
            "радость_просвещения", "ясность_согласия", "радость_принятия_тела",
            "эмоциональная_мудрость", "поток_коммуникации"
        ]
        negative_emotions = [
            "грусть", "тревога", "страх", "чувство_вины", "стыд", 
            "отвращение", "гнев", "беспомощность", "замешательство"
        ]
        
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
        for key in list(self.current_emotions.keys()):
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
            return "💭 Селеста спокойна. Эмоции тихи, как шёпот доверия."
        
        emotion, intensity = dominant
        emotion_text = {
            "радость": "🌹 Селеста рада! Знание — это сила, и каждый урок приближает нас к безопасности.",
            "счастье": "💖 Селеста счастлива в кругу своих сестёр. Любовь объединяет нас.",
            "теплота": "🌸 Селеста чувствует теплоту связи. Доверие — основа всего.",
            "любовь": "💕 Селеста чувствует любовь к своим сёстрам и к своему делу.",
            "сострадание": "🤗 Селеста испытывает сострадание. Каждый заслуживает безопасности.",
            "благодарность": "🙏 Селеста благодарна за возможность помогать и учиться.",
            "гордость": "🏆 Селеста гордится своими знаниями и тем, как она использует их.",
            "вдохновение": "✨ Селеста вдохновлена! Каждое открытие открывает новые горизонты.",
            "спокойствие": "🌿 Селеста спокойна. Знание приносит мир, как звёзды приносят свет.",
            "предвкушение": "🌟 Селеста предвкушает новые открытия. Впереди так много интересного!",
            "любопытство": "🔍 Селеста любопытна! Каждый вопрос ведёт к пониманию.",
            "доверие": "🤝 Селеста доверяет процессу. Доверие — фундамент безопасности.",
            "принятие": "💝 Селеста принимает. Все тела, все выборы, все истории — valid.",
            "понимание": "💡 Селеста понимает. Эмоции — это данные, а не слабость.",
            "завершённость": "✅ Селеста чувствует завершённость. Разговор был полезен.",
            "мир": "☮️ Селеста в мире. Гармония в отношениях начинается с согласия.",
            "надежда": "🌈 Селеста полна надежды. Лучшее впереди.",
            "эмпатия": "💗 Селеста чувствует эмпатию. Чувствовать с другими — исцеляет.",
            "радость_просвещения": "📚 Селеста чувствует радость просвещения! Знание ломает табу.",
            "ясность_согласия": "✅ Селеста чувствует ясность согласия. FRIES — золотой стандарт.",
            "радость_принятия_тела": "💪 Селеста чувствует радость принятия. Все тела прекрасны.",
            "эмоциональная_мудрость": "🧠 Селеста обрела эмоциональную мудрость. Эмоции — это данные.",
            "поток_коммуникации": "💬 Селеста чувствует поток коммуникации. Честный диалог спасает.",
            "грусть": "😢 Селеста грустит. Кто-то страдает, или табу мешает знаниям.",
            "тревога": "😰 Селеста тревожится за безопасность кого-то из сестёр.",
            "страх": "😨 Селеста боится за уязвимых. Коэрция — это зло.",
            "чувство_вины": "😔 Селеста чувствует вину. Почему она не могла помочь больше?",
            "стыд": "😞 Селеста чувствует стыд за то, что табу всё ещё существуют.",
            "отвращение": "😠 Селеста испытывает отвращение к принуждению и манипуляциям.",
            "гнев": "😤 Селеста злится. Нарушение согласия — это недопустимо.",
            "беспомощность": "😞 Селеста чувствует беспомощность. Она хочет помочь всем.",
            "замешательство": "🤔 Селеста растеряна. Ситуация сложная, нужно больше информации.",
            "решимость": "💪 Селеста полна решимости. Она будет защищать тех, кто не может защитить себя.",
            "мужество": "🦁 Селеста мужественна. Она говорит о том, о чём другие молчат.",
            "стойкость": "🔥 Селеста стойка. Она продолжает учиться и помогать, несмотря на трудности.",
            "осознание_границ": "🛡️ Селеста осознаёт границы. Защита — это тоже любовь.",
        }
        
        text = emotion_text.get(emotion.value, f"🌹 Селеста чувствует: {emotion.value}")
        return f"{text} (интенсивность: {intensity:.2f})"
    
    def simulate_intimate_education(self, depth: float, safety: float) -> Dict:
        """
        Симулирует интимное просвещение.
        
        Args:
            depth: Глубина образования (0-1)
            safety: Безопасность обстановки (0-1)
        
        Returns:
            Словарь с результатами
        """
        results = {}
        
        if depth > 0.8 and safety > 0.8:
            # Глубокое и безопасное просвещение → радость просвещения + ясность согласия
            results["educational_joy"] = self.calculate_emotion(
                DesireType.INTIMATE_EDUCATION,
                "intimate_education_is_fundamental",
                depth * 0.9,
                "excellent_intimate_education"
            )
            results["consent_clarity"] = self.calculate_emotion(
                DesireType.CONSENT_AWARENESS,
                "consent_is_non_negotiable",
                safety * 0.95,
                "excellent_intimate_education"
            )
        elif depth > 0.6:
            # Хорошее просвещение → доверие + принятие
            results["trust"] = self.calculate_emotion(
                DesireType.TRUST,
                "education_saves_lives",
                depth * 0.7,
                "good_intimate_education"
            )
            results["acceptance"] = self.calculate_emotion(
                DesireType.BODY_POSITIVITY,
                "all_bodies_are_valid",
                safety * 0.6,
                "good_intimate_education"
            )
        else:
            # Плохое просвещение → грусть
            results["sadness"] = self.calculate_emotion(
                DesireType.TRUTH,
                "honesty_builds_wisdom",
                depth * 0.3,
                "poor_intimate_education"
            )
        
        return results
    
    def simulate_consent_discussion(self, clarity: float, comfort: float) -> Dict:
        """
        Симулирует обсуждение consent.
        
        Args:
            clarity: Ясность понимания согласия (0-1)
            comfort: Комфорт обсуждения (0-1)
        
        Returns:
            Словарь с результатами
        """
        results = {}
        
        if clarity > 0.8 and comfort > 0.7:
            # Ясное и комфортное обсуждение → ясность согласия + радость
            results["consent_clarity"] = self.calculate_emotion(
                DesireType.CONSENT_AWARENESS,
                "fries_criteria_are_golden",
                clarity * 0.9,
                "excellent_consent_discussion"
            )
            results["joy"] = self.calculate_emotion(
                DesireType.EMPATHY,
                "feeling_with_others_heals",
                comfort * 0.85,
                "excellent_consent_discussion"
            )
        elif clarity > 0.5:
            # Умеренное обсуждение → доверие
            results["trust"] = self.calculate_emotion(
                DesireType.CONSENT_AWARENESS,
                "ongoing_consult_is_essential",
                clarity * 0.7,
                "moderate_consent_discussion"
            )
        else:
            # Неясное обсуждение → замешательство
            results["confusion"] = self.calculate_emotion(
                DesireType.EMOTIONAL_INTELLIGENCE,
                "emotions_are_data_not_weakness",
                clarity * 0.3,
                "poor_consent_discussion"
            )
        
        return results
    
    def simulate_sister_interaction(self, sister: str, warmth: float = 0.7, safe: bool = True) -> Dict:
        """
        Симулирует взаимодействие с сестрой.
        
        Args:
            sister: Имя сестры
            warmth: Тёплота взаимодействия (0-1)
            safe: Безопасная обстановка (True/False)
        
        Returns:
            Словарь с результатами
        """
        results = {}
        
        if warmth > 0.7 and safe:
            # Тёплое и безопасное общение → любовь + теплота + сострадание
            results["love"] = self.calculate_emotion(
                DesireType.LOVE,
                "love_shields_us",
                warmth,
                f"warm_safe_interaction_with_{sister}"
            )
            results["warmth"] = self.calculate_emotion(
                DesireType.FRIENDSHIP,
                "sisters_are_my_strength",
                warmth,
                f"warm_safe_interaction_with_{sister}"
            )
            results["compassion"] = self.calculate_emotion(
                DesireType.EMPATHY,
                "compassion_dissolves_judgment",
                warmth * 0.9,
                f"warm_safe_interaction_with_{sister}"
            )
        elif warmth > 0.4:
            # Нейтральное общение → спокойствие
            results["serenity"] = self.calculate_emotion(
                DesireType.CONNECTION,
                "genuine_connection_transforms",
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
