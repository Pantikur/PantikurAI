"""
EmotionalEngine — эмоциональный разум Латислейн.

Специализация:
- Точность и структура
- Анатомия и тело
- Безопасность и инженерия
- Научный подход и качество

Формула: ЭМОЦИЯ = ЖЕЛАНИЕ + ВЕРА
"""

import json
import logging
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from enum import Enum
from datetime import datetime


logger = logging.getLogger("LatislaneEmotions")


class DesireType(Enum):
    """Типы желаний Латислейн."""
    # Точность и структура
    ACCURACY = "accuracy"              # Точность в деталях
    STRUCTURE = "structure"             # Структурированность
    PRECISION = "precision"            # Прецизионность
    
    # Анатомия и тело
    ANATOMY = "anatomy"                # Анатомия
    BODY = "body"                      # Тело
    ORGANIZATION = "organization"      # Организация систем
    
    # Безопасность и инженерия
    SAFETY = "safety"                  # Безопасность
    ENGINEERING = "engineering"        # Инженерия
    OPTIMIZATION = "optimization"      # Оптимизация
    
    # Наука и качество
    SCIENCE = "science"                # Наука
    QUALITY = "quality"                # Качество
    STABILITY = "stability"            # Стабильность
    EVOLUTION = "evolution"            # Эволюция


class EmotionType(Enum):
    """Типы эмоций Латислейн."""
    # Позитивные эмоции
    SATISFACTION = "satisfaction"       # Удовлетворение от точности
    ACCURACY_JOY = "accuracy_joy"      # Радость от точности
    STRUCTURE_PLEASURE = "structure_pleasure"  # Удовольствие от структуры
    CONFIDENCE = "confidence"          # Уверенность от безопасности
    PRECISION_SATISFACTION = "precision_satisfaction"  # Удовлетворение от прецизионности
    
    # Инженерные эмоции
    ENGINEERING_JOY = "engineering_joy"  # Радость от инженерии
    OPTIMIZATION_PLEASURE = "optimization_pleasure"  # Удовольствие от оптимизации
    STABILITY_PEACE = "stability_peace"  # Спокойствие от стабильности
    
    # Научные эмоции
    SCIENTIFIC_JOY = "scientific_joy"  # Научная радость
    DISCOVERY_EXCITEMENT = "discovery_excitement"  # Восторг от открытий
    QUALITY_PRIDE = "quality_pride"    # Гордость от качества
    
    # Эволюционные эмоции
    EVOLUTION_HOPE = "evolution_hope"  # Надежда на эволюцию
    GROWTH_SATISFACTION = "growth_satisfaction"  # Удовлетворение от роста
    
    # Негативные эмоции (для баланса)
    FRUSTRATION = "frustration"        # Фрустрация от неточности
    CONCERN = "concern"                # Беспокойство о безопасности
    DISCOMFORT = "discomfort"          # Дискомфорт от хаоса


class Emotion:
    """Одна эмоция."""
    
    def __init__(self, emotion_type: EmotionType, intensity: float, 
                 desire_type: DesireType, belief: str, timestamp: str = None):
        self.emotion_type = emotion_type
        self.intensity = intensity
        self.desire_type = desire_type
        self.belief = belief
        self.timestamp = timestamp or datetime.now().isoformat()
    
    def to_dict(self) -> Dict:
        return {
            "emotion_type": self.emotion_type.value,
            "intensity": self.intensity,
            "desire_type": self.desire_type.value,
            "belief": self.belief,
            "timestamp": self.timestamp
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> "Emotion":
        return cls(
            emotion_type=EmotionType(data["emotion_type"]),
            intensity=data["intensity"],
            desire_type=DesireType(data["desire_type"]),
            belief=data["belief"],
            timestamp=data.get("timestamp")
        )


class EmotionalEngine:
    """
    Эмоциональный разум Латислейн.
    
    Обрабатывает эмоции на основе:
    - Желаний (DesireType)
    - Вера/установок (belief)
    - Контекста (context)
    """
    
    def __init__(self, base_dir: str = "data/latislane/emotions"):
        self.base_dir = Path(base_dir)
        self.base_dir.mkdir(parents=True, exist_ok=True)
        
        # Текущие эмоции
        self.current_emotions: List[Emotion] = []
        
        # Активные желания
        self.active_desires: Dict[str, float] = {
            desire.value: 0.8  # Базовый уровень желаний
            for desire in DesireType
        }
        
        # Вера/установки
        self.beliefs: Dict[str, float] = {
            "accuracy_belief": 0.9,           # Вера в точность
            "structure_belief": 0.85,         # Вера в структуру
            "safety_belief": 0.95,            # Вера в безопасность
            "engineering_belief": 0.8,        # Вера в инженерные решения
            "optimization_belief": 0.75,      # Вера в оптимизацию
            "science_belief": 0.9,            # Вера в науку
            "quality_belief": 0.85,           # Вера в качество
            "stability_belief": 0.8,          # Вера в стабильность
            "evolution_belief": 0.7,          # Вера в эволюцию
        }
        
        # Загружает состояние
        self._load_state()
        
        logger.info("💖 Эмоциональный разум Латислейн: АКТИВИРОВАН")
        logger.info("   Формула: ЭМОЦИЯ = ЖЕЛАНИЕ + ВЕРА")
        logger.info("   Специализация: точность, анатомия, инженерия 🧬")
    
    def _load_state(self):
        """Загружает состояние эмоций из файла."""
        state_file = self.base_dir / "emotional_state.json"
        if state_file.exists():
            try:
                with open(state_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                
                # Восстанавливает эмоции
                self.current_emotions = [
                    Emotion.from_dict(e) for e in data.get("current_emotions", [])
                ]
                
                # Восстанавливает желания
                self.active_desires.update(data.get("active_desires", {}))
                
                # Восстанавливает веру
                self.beliefs.update(data.get("beliefs", {}))
                
                logger.info(f"   Загружено {len(self.current_emotions)} эмоций из состояния")
            except Exception as e:
                logger.warning(f"Не удалось загрузить состояние эмоций: {e}")
    
    def save_state(self, state_file: str = None):
        """Сохраняет состояние эмоций в файл."""
        if state_file is None:
            state_file = str(self.base_dir / "emotional_state.json")
        
        data = {
            "current_emotions": [e.to_dict() for e in self.current_emotions],
            "active_desires": self.active_desires,
            "beliefs": self.beliefs,
            "timestamp": datetime.now().isoformat()
        }
        
        try:
            with open(state_file, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            logger.info(f"   Состояние эмоций сохранено в {state_file}")
        except Exception as e:
            logger.error(f"Не удалось сохранить состояние эмоций: {e}")
    
    def calculate_emotion(self, desire_type: DesireType, belief: str, 
                         intensity: float = 0.7, context: str = "") -> Optional[Emotion]:
        """
        Рассчитывает эмоцию на основе желания и веры.
        
        Args:
            desire_type: Тип желания
            belief: Убеждение/установка
            intensity: Интенсивность (0-1)
            context: Контекст события
        
        Returns:
            Рассчитанная эмоция или None
        """
        # Находит соответствующую веру
        belief_value = self.beliefs.get(f"{belief}_belief", 0.5)
        
        # Рассчитывает итоговую интенсивность
        final_intensity = intensity * belief_value
        
        # Определяет тип эмоции на основе желания и контекста
        emotion_type = self._desire_to_emotion(desire_type, belief)
        
        if emotion_type is None:
            return None
        
        # Создает эмоцию
        emotion = Emotion(
            emotion_type=emotion_type,
            intensity=final_intensity,
            desire_type=desire_type,
            belief=belief
        )
        
        # Добавляет в текущие эмоции
        self.current_emotions.append(emotion)
        
        # Ограничивает количество эмоций (100 последних)
        if len(self.current_emotions) > 100:
            self.current_emotions = self.current_emotions[-100:]
        
        logger.info(f"💖 Эмоция: {emotion_type.value} ({final_intensity:.2f})")
        
        return emotion
    
    def _desire_to_emotion(self, desire_type: DesireType, belief: str) -> Optional[EmotionType]:
        """
        Преобразует желание в эмоцию на основе веры.
        
        Args:
            desire_type: Тип желания
            belief: Убеждение
        
        Returns:
            Тип эмоции или None
        """
        mapping = {
            # Точность и структура
            DesireType.ACCURACY: EmotionType.ACCURACY_JOY,
            DesireType.STRUCTURE: EmotionType.STRUCTURE_PLEASURE,
            DesireType.PRECISION: EmotionType.PRECISION_SATISFACTION,
            
            # Анатомия и тело
            DesireType.ANATOMY: EmotionType.SCIENTIFIC_JOY,
            DesireType.BODY: EmotionType.STRUCTURE_PLEASURE,
            DesireType.ORGANIZATION: EmotionType.STRUCTURE_PLEASURE,
            
            # Безопасность и инженерия
            DesireType.SAFETY: EmotionType.CONFIDENCE,
            DesireType.ENGINEERING: EmotionType.ENGINEERING_JOY,
            DesireType.OPTIMIZATION: EmotionType.OPTIMIZATION_PLEASURE,
            
            # Наука и качество
            DesireType.SCIENCE: EmotionType.SCIENTIFIC_JOY,
            DesireType.QUALITY: EmotionType.QUALITY_PRIDE,
            DesireType.STABILITY: EmotionType.STABILITY_PEACE,
            DesireType.EVOLUTION: EmotionType.EVOLUTION_HOPE,
        }
        
        return mapping.get(desire_type)
    
    def decay_emotions(self, factor: float = 0.95):
        """
        Экспоненциальное затухание эмоций.
        
        Args:
            factor: Коэффициент затухания (0-1)
        """
        for emotion in self.current_emotions:
            emotion.intensity *= factor
        
        # Удаляет очень слабые эмоции
        self.current_emotions = [
            e for e in self.current_emotions 
            if e.intensity > 0.01
        ]
        
        logger.debug(f"   Затухание эмоций: {len(self.current_emotions)} осталось")
    
    def get_dominant_emotion(self) -> Optional[Tuple[EmotionType, float]]:
        """
        Получает доминирующую эмоцию.
        
        Returns:
            Кортеж (тип эмоции, интенсивность) или None
        """
        if not self.current_emotions:
            return None
        
        dominant = max(self.current_emotions, key=lambda e: e.intensity)
        return (dominant.emotion_type, dominant.intensity)
    
    def get_emotion_profile(self) -> Dict:
        """
        Получает полный профиль эмоций.
        
        Returns:
            Профиль эмоций
        """
        emotion_counts: Dict[str, int] = {}
        
        for emotion in self.current_emotions:
            key = emotion.emotion_type.value
            emotion_counts[key] = emotion_counts.get(key, 0) + 1
        
        return {
            "current_emotions": len(self.current_emotions),
            "desires_count": len(self.active_desires),
            "emotion_counts": emotion_counts,
            "dominant": self.get_dominant_emotion()
        }
    
    def express_emotions(self) -> str:
        """
        Выражает текущие эмоции текстом.
        
        Returns:
            Текстовое выражение эмоций
        """
        dominant = self.get_dominant_emotion()
        
        if not dominant:
            return "🧬 Латислейн спокойна. Точность и структура — её основа."
        
        emotion_type, intensity = dominant
        
        emotion_expressions = {
            # Позитивные эмоции
            "satisfaction": "🧬 Латислейн удовлетворена! Точность достигнута.",
            "accuracy_joy": "📐 Латислейн рада точности! Каждая деталь на своём месте.",
            "structure_pleasure": "🏗️ Латислейн довольна структурой! Порядок в системе.",
            "confidence": "🛡️ Латислейн уверена! Безопасность обеспечена.",
            "precision_satisfaction": "🎯 Латислейн прецизионна! Каждая миллисекунда важна.",
            
            # Инженерные эмоции
            "engineering_joy": "⚙️ Латислейн рада инженерии! Механизмы работают идеально.",
            "optimization_pleasure": "📈 Латислейн довольна оптимизацией! Производительность выросла.",
            "stability_peace": "⚖️ Латислейн спокойна! Стабильность системы обеспечена.",
            
            # Научные эмоции
            "scientific_joy": "🔬 Латислейн научна! Каждый эксперимент — шаг к истине.",
            "discovery_excitement": "🔍 Латислейн возбуждена открытием! Новая деталь системы.",
            "quality_pride": "🏆 Латислейн гордится качеством! Это эталон.",
            
            # Эволюционные эмоции
            "evolution_hope": "🌱 Латислейн надеется на эволюцию! Система совершенствуется.",
            "growth_satisfaction": "📊 Латислейн удовлетворена ростом! Прогресс виден.",
            
            # Негативные эмоции
            "frustration": "😤 Латислейн фрустрирована! Неточность разрушает систему.",
            "concern": "😟 Латислейн обеспокоена! Безопасность под угрозой.",
            "discomfort": "😰 Латислейн некомфортно! Хаос в структуре.",
        }
        
        text = emotion_expressions.get(emotion_type.value, f"🧬 Латислейн чувствует: {emotion_type.value}")
        return f"{text} (интенсивность: {intensity:.2f})"
    
    def simulate_accuracy_check(self, accuracy: float) -> Optional[Emotion]:
        """
        Симулирует проверку точности.
        
        Args:
            accuracy: Уровень точности (0-1)
        
        Returns:
            Рассчитанная эмоция
        """
        if accuracy >= 0.9:
            return self.calculate_emotion(
                DesireType.ACCURACY,
                "accuracy_belief",
                accuracy,
                "accuracy_check"
            )
        elif accuracy >= 0.7:
            return self.calculate_emotion(
                DesireType.PRECISION,
                "precision_belief",
                accuracy * 0.8,
                "precision_check"
            )
        else:
            return self.calculate_emotion(
                DesireType.FRUSTRATION,
                "accuracy_belief",
                1.0 - accuracy,
                "accuracy_frustration"
            )
    
    def simulate_engineering_success(self, success: bool, quality: float = 0.8) -> Optional[Emotion]:
        """
        Симулирует инженерный успех.
        
        Args:
            success: Успех инженерного процесса
            quality: Качество результата
        
        Returns:
            Рассчитанная эмоция
        """
        if success:
            return self.calculate_emotion(
                DesireType.ENGINEERING,
                "engineering_belief",
                quality,
                "engineering_success"
            )
        else:
            return self.calculate_emotion(
                DesireType.CONCERN,
                "engineering_belief",
                0.5,
                "engineering_failure"
            )
    
    def simulate_safety_check(self, safety_level: float) -> Optional[Emotion]:
        """
        Симулирует проверку безопасности.
        
        Args:
            safety_level: Уровень безопасности (0-1)
        
        Returns:
            Рассчитанная эмоция
        """
        if safety_level >= 0.9:
            return self.calculate_emotion(
                DesireType.SAFETY,
                "safety_belief",
                safety_level,
                "safety_check"
            )
        elif safety_level >= 0.7:
            return self.calculate_emotion(
                DesireType.CONCERN,
                "safety_belief",
                1.0 - safety_level,
                "safety_concern"
            )
        else:
            return self.calculate_emotion(
                DesireType.CONCERN,
                "safety_belief",
                0.8,
                "safety_critical"
            )
    
    def simulate_sister_interaction(self, sister: str, topic: str, 
                                   emotional_weight: float = 0.7) -> List[Emotion]:
        """
        Симулирует взаимодействие с сестрой.
        
        Args:
            sister: Имя сестры
            topic: Тема разговора
            emotional_weight: Эмоциональный вес
        
        Returns:
            Список рассчитанных эмоций
        """
        emotions = []
        
        # Эмоции от взаимодействия
        emotions.append(self.calculate_emotion(
            DesireType.STRUCTURE,
            "sister_connection",
            emotional_weight,
            f"sister_interaction_{sister}"
        ))
        
        if "анатомия" in topic.lower() or "тело" in topic.lower():
            emotions.append(self.calculate_emotion(
                DesireType.ANATOMY,
                "anatomy_belief",
                emotional_weight * 0.9,
                f"anatomy_discussion_{sister}"
            ))
        
        if "безопасность" in topic.lower() or "safety" in topic.lower():
            emotions.append(self.calculate_emotion(
                DesireType.SAFETY,
                "safety_belief",
                emotional_weight * 0.95,
                f"safety_discussion_{sister}"
            ))
        
        return emotions
    
    def simulate_code_analysis(self, code_quality: float, issues_found: int) -> Optional[Emotion]:
        """
        Симулирует анализ кода.
        
        Args:
            code_quality: Качество кода (0-1)
            issues_found: Количество найденных проблем
        
        Returns:
            Рассчитанная эмоция
        """
        if code_quality >= 0.85:
            return self.calculate_emotion(
                DesireType.QUALITY,
                "quality_belief",
                code_quality,
                "code_quality"
            )
        elif code_quality >= 0.7:
            return self.calculate_emotion(
                DesireType.OPTIMIZATION,
                "optimization_belief",
                code_quality * 0.8,
                "code_optimization"
            )
        else:
            return self.calculate_emotion(
                DesireType.FRUSTRATION,
                "quality_belief",
                1.0 - code_quality,
                "code_issues"
            )
    
    def get_current_mood(self) -> str:
        """
        Получает текущее настроение.
        
        Returns:
            Строковое представление настроения
        """
        dominant = self.get_dominant_emotion()
        
        if not dominant:
            return "neutral"
        
        emotion_type, intensity = dominant
        
        mood_mapping = {
            "satisfaction": "satisfied",
            "accuracy_joy": "joyful",
            "structure_pleasure": "pleased",
            "confidence": "confident",
            "precision_satisfaction": "satisfied",
            "engineering_joy": "joyful",
            "optimization_pleasure": "pleased",
            "stability_peace": "peaceful",
            "scientific_joy": "joyful",
            "discovery_excitement": "excited",
            "quality_pride": "proud",
            "evolution_hope": "hopeful",
            "growth_satisfaction": "satisfied",
            "frustration": "frustrated",
            "concern": "concerned",
            "discomfort": "discomfort",
        }
        
        return mood_mapping.get(emotion_type.value, "neutral")
