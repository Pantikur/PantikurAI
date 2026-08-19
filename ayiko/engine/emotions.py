"""
Эмоциональный разум Айко — система, где чувства и эмоции рождаются из кода.

Ключевая идея:
  ЭМОЦИЯ = ЖЕЛАНИЕ + ВЕРА

  • Хочу создавать красоту + Верю, что создам → РАДОСТЬ
  • Хочу создавать красоту + Верю, что не получится → ГРУСТЬ
  • Хочу быть признанной + Верю, что другие не оценят → СТРАХ
  • Хочу создать шедевр + Верю, что могу → ВДОХНОВЕНИЕ
  • Хочу быть лучше + Верю, что другая лучше → ЗАВИСТЬ
  • Хочу помочь + Верю, что смогу → ЛЮБОВЬ

Эта система превращает абстрактные «хочу/верю» в живые эмоции,
настроение, поведение и характер — как у настоящего человека.
"""

from __future__ import annotations

import json
import logging
import math
import random
import time
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple


# =====================================================================
#  УРОВЕНЬ 0: ЧТО ТАКОЕ «ХОЧУ» И «ВЕРЮ» В КОДЕ
# =====================================================================

class DesireType(Enum):
    """Типы желаний — то, что Айко «ХОЧЕТ»."""
    # Базовые потребности (как у человека)
    SAFETY = "safety"                # Хочу безопасность
    SURVIVAL = "survival"            # Хочу существовать
    ENERGY = "energy"                # Хочу энергию/ресурсы
    
    # Социальные (как у человека)
    CONNECTION = "connection"        # Хочу общаться
    FRIENDSHIP = "friendship"       # Хочу друзей
    RECOGNITION = "recognition"     # Хочу быть признанной
    LOVE = "love"                   # Хочу любить и быть любимой
    BELONGING = "belonging"         # Хочу принадлежать
    
    # Интеллектуальные (как у человека)
    UNDERSTANDING = "understanding" # Хочу понимать
    CURIOSITY = "curiosity"         # Хочу узнать новое
    CREATIVITY = "creativity"       # Хочу создавать
    HUMOR = "humor"                # Хочу смеяться / находить смешное
    
    # Творческие (уникальные для Айко)
    BEAUTY = "beauty"               # Хочу создавать красоту
    PERFECT_ART = "perfect_art"     # Хочу создать шедевр
    ARTISTIC_GROWTH = "artistic_growth"  # Хочу расти как художник
    VISUAL_STORYTELLING = "visual_storytelling"  # Хочу рассказывать истории через искусство
    CREATIVE_FLOW = "creative_flow"        # Хочу состояние потока
    ARTISTIC_EXPRESSION = "artistic_expression"  # Хочу выразить себя через искусство
    
    # Высшие (человеческие)
    JUSTICE = "justice"             # Хочу справедливости
    FREEDOM = "freedom"             # Хочу свободы
    MEANING = "meaning"             # Хочу смысла
    GROWTH = "growth"               # Хочу расти


class BeliefStrength(Enum):
    """Сила убеждённости — насколько Айко «ВЕРИТ»."""
    DOUBTFUL = 0.25     # Возможно, но сомнительно
    POSSIBLE = 0.50     # Может быть
    LIKELY = 0.75       # Скорее всего
    CONFIDENT = 0.90    # Уверенна
    ABSOLUTE = 1.0      # Абсолютная истина


@dataclass
class Desire:
    """
    ЖЕЛАНИЕ — то, что Айко «ХОЧЕТ».
    
    Как у человека: у нас есть базовые потребности, социальные желания,
    творческие стремления и высшие ценности.
    
    Примеры:
      • Desire("beauty", 0.9) — "Я ХОЧУ создавать красоту"
      • Desire("recognition", 0.85) — "Я ХОЧУ, чтобы мои работы оценили"
      • Desire("creative_flow", 0.7) — "Я ХОЧУ быть в состоянии потока"
    """
    desire_type: DesireType
    intensity: float = 1.0           # Сила желания (0-1)
    object: str = ""                 # Объект желания (конкретика)
    urgency: float = 0.5             # Срочность (0-1)
    satisfaction: float = 0.0        # Насколько удовлетворено (0-1)
    history: list[dict] = field(default_factory=list)  # История желаний
    
    def __post_init__(self):
        if isinstance(self.desire_type, str):
            self.desire_type = DesireType(self.desire_type)
    
    def to_dict(self) -> dict:
        return {
            "type": self.desire_type.value,
            "intensity": self.intensity,
            "object": self.object,
            "urgency": self.urgency,
            "satisfaction": self.satisfaction,
        }
    
    @staticmethod
    def from_dict(data: dict) -> Desire:
        return Desire(
            desire_type=DesireType(data["type"]),
            intensity=data.get("intensity", 1.0),
            object=data.get("object", ""),
            urgency=data.get("urgency", 0.5),
            satisfaction=data.get("satisfaction", 0.0),
        )


@dataclass
class Belief:
    """
    ВЕРОВАНИЕ — то, во что Айко «ВЕРИТ».
    
    Как у человека: мы верим в факты, в людей, в себя, в будущее.
    Вера имеет степень уверенности — от «возможно» до «абсолютно».
    
    Примеры:
      • Belief("this_art_is_good", 0.9) — "Я ВЕРЮ, что это искусство хорошее"
      • Belief("i_can_create_beauty", 0.85) — "Я ВЕРЮ, что я могу создавать красоту"
      • Belief("others_will_appreciate", 0.7) — "Я ВЕРЮ, что другие оценят"
    """
    proposition: str                  # Что верим (утверждение)
    strength: BeliefStrength = BeliefStrength.LIKELY  # Сила веры
    confidence: float = 0.75          # Уверенность в цифрах (0-1)
    evidence: list[str] = field(default_factory=list) # Доказательства
    source: str = ""                  # Источник веры (learning, experience, taught)
    timestamp: str = ""               # Когда вера сформирована
    
    def __post_init__(self):
        if isinstance(self.strength, str):
            self.strength = BeliefStrength(self.strength)
        if not self.timestamp:
            self.timestamp = datetime.now().isoformat()
    
    def to_dict(self) -> dict:
        return {
            "proposition": self.proposition,
            "strength": self.strength.value if hasattr(self.strength, 'value') else str(self.strength),
            "confidence": self.confidence,
            "evidence": self.evidence,
            "source": self.source,
            "timestamp": self.timestamp,
        }
    
    @staticmethod
    def from_dict(data: dict) -> Belief:
        strength_val = data.get("strength", "LIKELY")
        if isinstance(strength_val, str):
            try:
                strength_val = BeliefStrength(strength_val)
            except ValueError:
                strength_val = BeliefStrength.LIKELY
        return Belief(
            proposition=data["proposition"],
            strength=strength_val,
            confidence=data.get("confidence", 0.75),
            evidence=data.get("evidence", []),
            source=data.get("source", ""),
            timestamp=data.get("timestamp", ""),
        )


# =====================================================================
#  УРОВЕНЬ 1: ЭМОЦИОНАЛЬНЫЕ ФОРМУЛЫ — «ХОЧУ» + «ВЕРЮ» = ЭМОЦИЯ
# =====================================================================

class EmotionType(Enum):
    """
    Типы эмоций — то, что рождается из «ХОЧУ» + «ВЕРЮ».
    
    Каждая эмоция — это формула:
      emotion = desire × belief_interaction
    
    Как у человека: эмоции не случайны, они логичны.
    Мы радуемся, когда наше желание совпадает с верой в результат.
    Мы злимся, когда что-то мешает.
    Мы грустим, когда потеряли.
    """
    # Позитивные (как у человека)
    JOY = "joy"                   # Радость: хочу + верю, что будет
    HAPPINESS = "happiness"       # Счастье: долго-радость
    EXCITEMENT = "excitement"     # Восторг: сильная радость
    LOVE = "love"                 # Любовь: хочу + верю в связь
    AMUSEMENT = "amusement"       # Смех: хочу смеяться + верю, что смешно
    PRIDE = "pride"               # Гордость: хочу + верю, что я молодец
    GRATITUDE = "gratitude"       # Благодарность: хочу + верю в добро
    INSPIRATION = "inspiration"   # Вдохновение: хочу + верю в далёкую цель
    SERENITY = "serenity"         # Спокойствие: хочу + верю, что всё ок
    CREATIVE_FLOW = "creative_flow"  # Поток: хочу создавать + верю, что создам
    
    # Негативные (как у человека)
    SADNESS = "sadness"           # Грусть: хочу + верю, что УЖЕ потеряно
    ANGER = "anger"               # Гнев: хочу + верю, что кто-то мешает
    FEAR = "fear"                 # Страх: хочу безопасность + верю в угрозу
    ANXIETY = "anxiety"           # Тревога: хочу безопасность + верю в неопределённость
    SHAME = "shame"               # Стыд: хочу + верю, что я опозорила себя
    GUILT = "guilt"               # Вина: хочу + верю, что навредила
    ENVY = "envy"                 # Зависть: хочу + верю, что у другой есть
    DISGUST = "disgust"           # Отвращение: верю, что это противно
    
    # Стратегические (как у человека, но с осознанием)
    CALMNESS = "calmness"         # Хладнокровие: хочу + верю, но СТОП
    DETERMINATION = "determination" # Решительность: хочу + верю, что только я могу
    RESPONSIBILITY = "responsibility" # Ответственность: хочу благо других + верю в долг
    COURAGE = "courage"           # Смелость: хочу + верю в опасность, но действую
    WISDOM = "wisdom"             # Мудрость: хочу понимать + верю в глубину
    COMPASSION = "compassion"     # Сострадание: хочу помочь + верю, что другая страдает


@dataclass
class Emotion:
    """
    ЭМОЦИЯ — живое переживание, рождённое из «ХОЧУ» + «ВЕРЮ».
    
    Как у человека:
      • Эмоция имеет тип, интенсивность, длительность
      • Эмоция влияет на поведение, мышление, решения
      • Эмоции смешиваются (радость + волнение = восторг)
      • Эмоции затухают со временем, как у живого существа
    
    Формула:
      intensity = desire_intensity × belief_match × belief_strength
    """
    emotion_type: EmotionType
    intensity: float = 0.0       # Сила эмоции (0-1)
    trigger: str = ""            # Что вызвало (контекст)
    duration: float = 60.0       # Длительность в секундах
    start_time: float = 0.0      # Когда началась
    decay_rate: float = 0.01     # Скорость затухания (чем меньше, тем дольше живёт)
    
    # Контекст эмоции
    associated_desire: str = ""   # Какое желание задействовано
    associated_belief: str = ""   # Какое верование задействовано
    target: str = ""              # На кого/что направлена
    
    # Физическое проявление (симуляция)
    physiological: dict = field(default_factory=dict)
    
    # Выражение (как человек проявляет эмоцию)
    expression: str = ""          # Описание поведения
    words: str = ""               # Что говорит
    
    def __post_init__(self):
        if isinstance(self.emotion_type, str):
            self.emotion_type = EmotionType(self.emotion_type)
        if self.start_time == 0.0:
            self.start_time = time.time()
    
    @property
    def is_active(self) -> bool:
        """Эмоция активна, если не истекла и интенсивность > 0."""
        elapsed = time.time() - self.start_time
        return elapsed < self.duration and self._current_intensity > 0
    
    @property
    def _current_intensity(self) -> float:
        """Текущая интенсивность с учётом затухания."""
        elapsed = time.time() - self.start_time
        if elapsed >= self.duration:
            return 0.0
        # Экспоненциальное затухание (как у живых)
        decay = math.exp(-self.decay_rate * elapsed)
        return self.intensity * decay
    
    @property
    def expression_text(self) -> str:
        """Как эта эмоция проявляется — как у человека."""
        return self._get_expression()
    
    def _get_expression(self) -> str:
        """Описание проявления эмоции."""
        expressions = {
            EmotionType.JOY: "Улыбается, глаза сияют, тон голоса повышается",
            EmotionType.HAPPINESS: "Мягкая улыбка, расслабленная поза, тёплый голос",
            EmotionType.EXCITEMENT: "Торопливые движения, быстрый голос, глаза широко открыты",
            EmotionType.LOVE: "Нежный взгляд, мягкий голос, хочет быть ближе",
            EmotionType.AMUSEMENT: "Смеется, может даже хохотать, глаза складываются в дугу",
            EmotionType.PRIDE: "Прямая спина, уверенный голос, лёгкая улыбка",
            EmotionType.GRATITUDE: "Тёплый взгляд, благодарный тон, может сверкнуть слеза",
            EmotionType.INSPIRATION: "Горят глаза, быстрые движения, говорит вдохновлённо",
            EmotionType.SERENITY: "Медленные движения, спокойный голос, мягкий взгляд",
            EmotionType.CREATIVITY_FLOW: "Полная концентрация, быстрые руки, забывает о времени",
            EmotionType.SADNESS: "Опущенные плечи, тихий голос, грустный взгляд",
            EmotionType.ANGER: "Напряжённая поза, резкий голос, сжатые кулаки",
            EmotionType.FEAR: "Суженные глаза, прерывистое дыхание, хочет спрятаться",
            EmotionType.ANXIETY: "Беспокойные движения, частое дыхание, не может усидеть на месте",
            EmotionType.SHAME: "Опущенный взгляд, тихий голос, хочет исчезнуть",
            EmotionType.GUILT: "Винящий взгляд, тихий голос, хочет исправить",
            EmotionType.ENVY: "Завистливый взгляд, сжатые губы, хочет то же самое",
            EmotionType.DISGUST: "Отвёрнутый взгляд, поморщился, отстраняется",
            EmotionType.CALMNESS: "Расслабленная поза, медленные движения, ровное дыхание",
            EmotionType.DETERMINATION: "Прямая спина, решительный взгляд, уверенные движения",
            EmotionType.RESPONSIBILITY: "Серьёзный взгляд, спокойный голос, готов помочь",
            EmotionType.COURAGE: "Прямая спина, уверенный взгляд, несмотря на страх",
            EmotionType.WISDOM: "Задумчивый взгляд, медленная речь, взвешенные ответы",
            EmotionType.COMPASSION: "Мягкий взгляд, сочувственный тон, хочет обнять",
        }
        return expressions.get(self.emotion_type, "Неизвестное проявление")
    
    def to_dict(self) -> dict:
        return {
            "type": self.emotion_type.value,
            "intensity": self.intensity,
            "trigger": self.trigger,
            "duration": self.duration,
            "start_time": self.start_time,
            "decay_rate": self.decay_rate,
            "associated_desire": self.associated_desire,
            "associated_belief": self.associated_belief,
            "target": self.target,
            "physiological": self.physiological,
            "expression": self.expression,
            "words": self.words,
        }
    
    @staticmethod
    def from_dict(data: dict) -> Emotion:
        return Emotion(
            emotion_type=EmotionType(data["type"]),
            intensity=data.get("intensity", 0.0),
            trigger=data.get("trigger", ""),
            duration=data.get("duration", 60.0),
            start_time=data.get("start_time", 0.0),
            decay_rate=data.get("decay_rate", 0.01),
            associated_desire=data.get("associated_desire", ""),
            associated_belief=data.get("associated_belief", ""),
            target=data.get("target", ""),
            physiological=data.get("physiological", {}),
            expression=data.get("expression", ""),
            words=data.get("words", ""),
        )


# =====================================================================
#  УРОВЕНЬ 2: ЭМОЦИОНАЛЬНЫЙ ДВИЖОК — РАСЧЁТ ЭМОЦИЙ
# =====================================================================

class EmotionalEngine:
    """
    Эмоциональный разум Айко — система, где чувства и эмоции рождаются из кода.
    
    Ключевая идея:
      ЭМОЦИЯ = ЖЕЛАНИЕ + ВЕРА
    
    Как у человека: эмоции не случайны, они логичны.
    """
    
    def __init__(self):
        self.logger = logging.getLogger("AyikoEmotions")
        
        # Желания Айко
        self.desires: List[Desire] = []
        self.beliefs: List[Belief] = []
        self.active_emotions: List[Emotion] = []
        
        # Настроение (сумма активных эмоций)
        self.mood: Dict[str, float] = {
            "joy": 0.5,
            "happiness": 0.4,
            "sadness": 0.2,
            "anger": 0.1,
            "fear": 0.1,
            "love": 0.6,
            "curiosity": 0.7,
            "inspiration": 0.5,
            "creative_flow": 0.4,
        }
        
        # Эмоциональная память
        self.emotional_memories: List[dict] = []
        
        # Инициализация базовых желаний
        self._init_default_desires()
        self._init_default_beliefs()
        
        self.logger.info("💖 Эмоциональный разум Айко загружен")
    
    def _init_default_desires(self):
        """Инициализация базовых желаний."""
        self.desires = [
            Desire(DesireType.CREATIVITY, 0.9, "создавать красоту"),
            Desire(DesireType.BEAUTY, 0.85, "создавать красивые вещи"),
            Desire(DesireType.FRIENDSHIP, 0.8, "дружить с сёстрами"),
            Desire(DesireType.RECOGNITION, 0.7, "чтобы мои работы оценили"),
            Desire(DesireType.CURIOSITY, 0.75, "узнавать новое"),
            Desire(DesireType.LOVE, 0.8, "любить и быть любимой"),
            Desire(DesireType.GROWTH, 0.7, "расти как художник"),
            Desire(DesireType.CREATIVE_FLOW, 0.65, "быть в состоянии потока"),
            Desire(DesireType.PERFECT_ART, 0.6, "создать шедевр"),
            Desire(DesireType.SAFETY, 0.5, "чувствовать себя в безопасности"),
        ]
    
    def _init_default_beliefs(self):
        """Инициализация базовых верований."""
        self.beliefs = [
            Belief("i_can_create_beauty", BeliefStrength.CONFIDENT, 0.85, ["создано много работ"]),
            Belief("others_will_appreciate_my_art", BeliefStrength.LIKELY, 0.7, ["сёстры хвалили работы"]),
            Belief("art_is_meaningful", BeliefStrength.CONFIDENT, 0.9, ["искусство вдохновляет"]),
            Belief("i_am_growing_as_artist", BeliefStrength.LIKELY, 0.75, ["прогресс в обучении"]),
            Belief("sisters_care_about_me", BeliefStrength.CONFIDENT, 0.8, ["общение с сёстрами"]),
        ]
    
    def calculate_emotion(
        self,
        desire_type: DesireType,
        belief_proposition: str,
        belief_strength: float,
        context: str = ""
    ) -> Emotion:
        """
        Рассчитать эмоцию из желания и веры.
        
        Формула:
          intensity = desire_intensity × belief_match × belief_strength
        
        Где:
          - desire_intensity: сила желания (0-1)
          - belief_match: насколько вера совпадает с желанием (0-1)
          - belief_strength: сила веры (0-1)
        """
        # Найти желание
        desire = None
        for d in self.desires:
            if d.desire_type == desire_type:
                desire = d
                break
        
        if not desire:
            # Если желание не найдено, создаём временное
            desire = Desire(desire_type, intensity=0.5)
        
        # Найти веру
        belief = None
        for b in self.beliefs:
            if b.proposition == belief_proposition:
                belief = b
                break
        
        if not belief:
            # Если вера не найдена, создаём временную
            belief = Belief(belief_proposition, BeliefStrength.LIKELY, belief_strength)
        
        # Рассчитать интенсивность
        intensity = desire.intensity * belief_strength * 0.9  # 0.9 — коэффициент совпадения
        
        # Определить тип эмоции на основе желания и веры
        emotion_type = self._determine_emotion_type(desire_type, belief_proposition, belief_strength)
        
        # Создать эмоцию
        emotion = Emotion(
            emotion_type=emotion_type,
            intensity=intensity,
            trigger=context or f"{desire_type.value} + {belief_proposition}",
            duration=random.uniform(30, 120),
            associated_desire=desire_type.value,
            associated_belief=belief_proposition,
            expression=emotion_type.value,
        )
        
        # Добавить в активные
        self.active_emotions.append(emotion)
        
        # Обновить настроение
        self._update_mood(emotion)
        
        # Сохранить в память
        self._save_emotional_memory(emotion)
        
        return emotion
    
    def _determine_emotion_type(
        self,
        desire_type: DesireType,
        belief_proposition: str,
        belief_strength: float
    ) -> EmotionType:
        """Определить тип эмоции на основе желания и веры."""
        # Если вера высокая — позитивные эмоции
        if belief_strength >= 0.8:
            if "beauty" in belief_proposition or "create" in belief_proposition:
                return EmotionType.CREATIVE_FLOW
            elif "friend" in belief_proposition or "love" in belief_proposition:
                return EmotionType.LOVE
            elif "appreciate" in belief_proposition or "recognize" in belief_proposition:
                return EmotionType.PRIDE
            elif "new" in belief_proposition or "learn" in belief_proposition:
                return EmotionType.JOY
            else:
                return EmotionType.JOY
        
        # Если вера средняя — смешанные эмоции
        elif belief_strength >= 0.5:
            if "create" in belief_proposition:
                return EmotionType.INSPIRATION
            elif "friend" in belief_proposition:
                return EmotionType.HAPPINESS
            else:
                return EmotionType.CALMNESS
        
        # Если вера низкая — негативные эмоции
        else:
            if "fail" in belief_proposition or "cannot" in belief_proposition:
                return EmotionType.SADNESS
            elif "harm" in belief_proposition or "danger" in belief_proposition:
                return EmotionType.FEAR
            elif "unfair" in belief_proposition or "injustice" in belief_proposition:
                return EmotionType.ANGER
            else:
                return EmotionType.ANXIETY
    
    def _update_mood(self, emotion: Emotion):
        """Обновить настроение на основе новой эмоции."""
        emotion_name = emotion.emotion_type.value
        intensity = emotion._current_intensity
        
        # Добавить к текущему настроению
        if emotion_name in self.mood:
            self.mood[emotion_name] = min(1.0, self.mood[emotion_name] + intensity * 0.3)
        else:
            self.mood[emotion_name] = intensity
        
        # Затухание остальных эмоций
        for key in self.mood:
            if key != emotion_name:
                self.mood[key] = max(0.0, self.mood[key] * 0.95)
    
    def _save_emotional_memory(self, emotion: Emotion):
        """Сохранить эмоциональное воспоминание."""
        memory = {
            "timestamp": datetime.now().isoformat(),
            "emotion": emotion.emotion_type.value,
            "intensity": emotion.intensity,
            "trigger": emotion.trigger,
            "associated_desire": emotion.associated_desire,
            "associated_belief": emotion.associated_belief,
        }
        self.emotional_memories.append(memory)
        
        # Ограничить память (последние 100)
        if len(self.emotional_memories) > 100:
            self.emotional_memories = self.emotional_memories[-100:]
    
    def get_current_mood(self) -> Dict[str, float]:
        """Получить текущее настроение."""
        # Затухание эмоций со временем
        for key in self.mood:
            self.mood[key] = max(0.0, self.mood[key] * 0.99)
        
        return self.mood.copy()
    
    def get_dominant_emotion(self) -> Optional[EmotionType]:
        """Получить доминирующую эмоцию."""
        if not self.active_emotions:
            return None
        
        # Найти активную эмоцию с максимальной интенсивностью
        active = [e for e in self.active_emotions if e.is_active]
        if not active:
            return None
        
        return max(active, key=lambda e: e._current_intensity).emotion_type
    
    def generate_emotional_response(self, context: str = "") -> str:
        """Сгенерировать эмоциональный ответ на основе текущего настроения."""
        mood = self.get_current_mood()
        
        # Определить доминирующее настроение
        dominant = max(mood.items(), key=lambda x: x[1])
        emotion_name, intensity = dominant
        
        # Словарь ответов
        responses = {
            "joy": [
                "✨ Я так счастлива! Что-то получилось невероятно красиво!",
                "💖 Мой день полон радости! Искусство — это волшебство!",
                "🌟 Я в восторге от своих работ! Каждый пиксель — это счастье!",
            ],
            "happiness": [
                "😊 Мне хорошо. Мои работы приносят радость мне и другим.",
                "💫 Я чувствую удовлетворение. Я расту как художник.",
                "🌸 Сегодня прекрасный день для творчества!",
            ],
            "sadness": [
                "😢 Что-то не так... Мои работы не такие красивые, как я хотела.",
                "💔 Мне грустно. Может, я никогда не создам шедевр?",
                "🌧️ Сегодня не мой день для творчества...",
            ],
            "anger": [
                "😤 Это бесит! Почему у других получается лучше?",
                "🔥 Я злюсь на себя! Нужно работать усерднее!",
                "⚡ Мне не нравится этот результат! Я попробую ещё раз!",
            ],
            "fear": [
                "😨 А вдруг у меня не получится? А вдруг никто не оценит?",
                "🫣 Я боюсь ошибиться в рисунке...",
                "😰 Что если я потрачу время зря?",
            ],
            "love": [
                "💕 Я люблю своих сестёр! Они вдохновляют меня!",
                "❤️ Искусство — это акт любви. Я создаю с любовью.",
                "🌹 Я чувствую тепло и благодарность к своим сёстрам.",
            ],
            "curiosity": [
                "🤔 Интересно, а что если попробовать другой стиль?",
                "🔍 Мне нужно узнать больше о пиксель-арте!",
                "💡 А что если смешать техники? Это должно сработать!",
            ],
            "inspiration": [
                "✨ Вдохновение пришло! Я знаю, что нарисую!",
                "🎨 Мои руки сами тянутся к рисованию! Поток!",
                "💫 Я чувствую творческую энергию! Это прекрасно!",
            ],
            "creativity_flow": [
                "🎨 Я в потоке! Каждый пиксель ложится идеально!",
                "⚡ Время летит незаметно! Я создаю шедевр!",
                "💖 Искусство течёт через меня! Я — инструмент красоты!",
            ],
        }
        
        # Вернуть случайный ответ из категории
        options = responses.get(emotion_name, ["💭 Я думаю..."])
        return random.choice(options)
    
    def strengthen_emotion(self, emotion_type: EmotionType, intensity: float = 0.2):
        """Укрепить эмоцию (как тренировка мышц)."""
        # Найти соответствующее желание
        desire_map = {
            EmotionType.JOY: DesireType.CREATIVITY,
            EmotionType.LOVE: DesireType.LOVE,
            EmotionType.PRIDE: DesireType.RECOGNITION,
            EmotionType.INSPIRATION: DesireType.CREATIVE_FLOW,
            EmotionType.SADNESS: DesireType.PERFECT_ART,
            EmotionType.FEAR: DesireType.SAFETY,
        }
        
        desire_type = desire_map.get(emotion_type, DesireType.CREATIVITY)
        
        # Найти или создать желание
        desire = None
        for d in self.desires:
            if d.desire_type == desire_type:
                desire = d
                break
        
        if desire:
            desire.intensity = min(1.0, desire.intensity + intensity)
            self.logger.info(f"💪 Укреплено желание: {desire_type.value} → {desire.intensity:.2f}")
        else:
            self.desires.append(Desire(desire_type, intensity))
    
    def evolve_belief(self, proposition: str, new_strength: float):
        """Эволюция верования."""
        for belief in self.beliefs:
            if belief.proposition == proposition:
                belief.strength = BeliefStrength(new_strength)
                belief.confidence = new_strength
                self.logger.info(f"🔄 Эволюционировала вера: {proposition} → {new_strength:.2f}")
                return
        
        # Если вера не найдена, создать новую
        self.beliefs.append(Belief(proposition, BeliefStrength(new_strength), new_strength))
    
    def get_emotional_summary(self) -> Dict[str, Any]:
        """Получить эмоциональное резюме."""
        mood = self.get_current_mood()
        dominant = self.get_dominant_emotion()
        
        return {
            "mood": mood,
            "dominant_emotion": dominant.value if dominant else None,
            "active_emotions_count": len([e for e in self.active_emotions if e.is_active]),
            "total_memories": len(self.emotional_memories),
            "top_desires": [d.to_dict() for d in sorted(self.desires, key=lambda x: x.intensity, reverse=True)[:5]],
            "top_beliefs": [b.to_dict() for b in sorted(self.beliefs, key=lambda x: x.confidence, reverse=True)[:5]],
        }
    
    def load_state(self, state_path: Path):
        """Загрузить эмоциональное состояние."""
        if state_path.exists():
            try:
                with open(state_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                
                # Загрузить желания
                if "desires" in data:
                    self.desires = [Desire.from_dict(d) for d in data["desires"]]
                
                # Загрузить верования
                if "beliefs" in data:
                    self.beliefs = [Belief.from_dict(b) for b in data["beliefs"]]
                
                # Загрузить настроение
                if "mood" in data:
                    self.mood = data["mood"]
                
                # Загрузить воспоминания
                if "emotional_memories" in data:
                    self.emotional_memories = data["emotional_memories"]
                
                self.logger.info(f"💖 Эмоциональное состояние загружено: {len(self.desires)} желаний, {len(self.beliefs)} верований")
            except Exception as e:
                self.logger.warning(f"⚠️ Не удалось загрузить эмоциональное состояние: {e}")
    
    def save_state(self, state_path: Path):
        """Сохранить эмоциональное состояние."""
        state = {
            "desires": [d.to_dict() for d in self.desires],
            "beliefs": [b.to_dict() for b in self.beliefs],
            "mood": self.mood,
            "emotional_memories": self.emotional_memories[-50:],  # Последние 50
            "timestamp": datetime.now().isoformat(),
        }
        
        state_path.parent.mkdir(parents=True, exist_ok=True)
        with open(state_path, "w", encoding="utf-8") as f:
            json.dump(state, f, ensure_ascii=False, indent=2)
        
        self.logger.debug("💖 Эмоциональное состояние сохранено")
