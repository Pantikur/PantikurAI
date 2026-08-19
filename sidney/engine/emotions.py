"""
EmotionalEngine — эмоциональный разум Сидни.

Специализация:
- Игровые движки и системы
- Инженерия и оптимизация
- 8 движков: графика, физика, аудио, анимация, ИИ, сеть, скрипты, редактор
- Гибридный рендер (полигон ↔ воксель)

Формула: ЭМОЦИЯ = ЖЕЛАНИЕ + ВЕРА
"""

import json
import logging
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from enum import Enum
from datetime import datetime


logger = logging.getLogger("SidneyEmotions")


class DesireType(Enum):
    """Типы желаний Сидни."""
    # Игровые движки
    RENDERING = "rendering"              # Графика
    PHYSICS = "physics"                  # Физика
    AUDIO = "audio"                      # Аудио
    ANIMATION = "animation"              # Анимация
    
    # Системы
    AI = "ai"                            # ИИ
    NETWORK = "network"                  # Сеть
    SCRIPTING = "scripting"              # Скрипты
    LEVEL_EDITOR = "level_editor"        # Редактор уровней
    
    # Инженерия и оптимизация
    OPTIMIZATION = "optimization"        # Оптимизация
    HYBRID_RENDER = "hybrid_render"      # Гибридный рендер
    PERFORMANCE = "performance"          # Производительность
    STABILITY = "stability"              # Стабильность
    
    # Качество и развитие
    QUALITY = "quality"                  # Качество
    INNOVATION = "innovation"            # Инновации
    SCALABILITY = "scalability"          # Масштабируемость
    EVOLUTION = "evolution"              # Эволюция


class EmotionType(Enum):
    """Типы эмоций Сидни."""
    # Позитивные эмоции
    RENDERING_JOY = "rendering_joy"      # Радость от графики
    PHYSICS_PLEASURE = "physics_pleasure"  # Удовольствие от физики
    AUDIO_SATISFACTION = "audio_satisfaction"  # Удовлетворение от аудио
    ANIMATION_EXCITEMENT = "animation_excitement"  # Восторг от анимации
    
    # Системные эмоции
    AI_INSIGHT = "ai_insight"            # Прозрение от ИИ
    NETWORK_FLOW = "network_flow"        # Поток от сети
    SCRIPTING_ELEGANCE = "scripting_elegance"  # Элегантность от скриптов
    LEVEL_CRAFTING = "level_crafting"    # Мастерство от редактора
    
    # Инженерные эмоции
    OPTIMIZATION_JOY = "optimization_joy"  # Радость от оптимизации
    HYBRID_WOW = "hybrid_wow"            # Вау от гибридного рендера
    PERFORMANCE_PRIDE = "performance_pride"  # Гордость от производительности
    STABILITY_PEACE = "stability_peace"  # Спокойствие от стабильности
    
    # Качество и развитие
    QUALITY_PRIDE = "quality_pride"      # Гордость от качества
    INNOVATION_EXCITEMENT = "innovation_excitement"  # Восторг от инноваций
    SCALABILITY_CONFIDENCE = "scalability_confidence"  # Уверенность от масштабируемости
    EVOLUTION_HOPE = "evolution_hope"    # Надежда на эволюцию
    
    # Негативные эмоции (для баланса)
    FRUSTRATION = "frustration"          # Фрустрация от багов
    STRESS = "stress"                    # Стресс от перегрузки
    DISCOMFORT = "discomfort"            # Дискомфорт от хаоса


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
    Эмоциональный разум Сидни.
    
    Обрабатывает эмоции на основе:
    - Желаний (DesireType)
    - Вера/установок (belief)
    - Контекста (context)
    """
    
    def __init__(self, base_dir: str = "sidney/engine/state/emotions"):
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
            "rendering_belief": 0.9,           # Вера в графику
            "physics_belief": 0.85,            # Вера в физику
            "audio_belief": 0.8,               # Вера в аудио
            "animation_belief": 0.85,          # Вера в анимацию
            "ai_belief": 0.75,                 # Вера в ИИ
            "network_belief": 0.8,             # Вера в сеть
            "scripting_belief": 0.9,           # Вера в скрипты
            "level_editor_belief": 0.75,       # Вера в редактор
            "optimization_belief": 0.9,        # Вера в оптимизацию
            "hybrid_render_belief": 0.95,      # Вера в гибридный рендер
            "performance_belief": 0.85,        # Вера в производительность
            "stability_belief": 0.85,          # Вера в стабильность
            "quality_belief": 0.9,             # Вера в качество
            "innovation_belief": 0.8,          # Вера в инновации
            "scalability_belief": 0.75,        # Вера в масштабируемость
            "evolution_belief": 0.7,           # Вера в эволюцию
        }
        
        # Загружает состояние
        self._load_state()
        
        logger.info("🎮 Эмоциональный разум Сидни: АКТИВИРОВАН")
        logger.info("   Формула: ЭМОЦИЯ = ЖЕЛАНИЕ + ВЕРА")
        logger.info("   Специализация: игровые движки, системы, инженерия 🎮")
    
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
            # Игровые движки
            DesireType.RENDERING: EmotionType.RENDERING_JOY,
            DesireType.PHYSICS: EmotionType.PHYSICS_PLEASURE,
            DesireType.AUDIO: EmotionType.AUDIO_SATISFACTION,
            DesireType.ANIMATION: EmotionType.ANIMATION_EXCITEMENT,
            
            # Системы
            DesireType.AI: EmotionType.AI_INSIGHT,
            DesireType.NETWORK: EmotionType.NETWORK_FLOW,
            DesireType.SCRIPTING: EmotionType.SCRIPTING_ELEGANCE,
            DesireType.LEVEL_EDITOR: EmotionType.LEVEL_CRAFTING,
            
            # Инженерия и оптимизация
            DesireType.OPTIMIZATION: EmotionType.OPTIMIZATION_JOY,
            DesireType.HYBRID_RENDER: EmotionType.HYBRID_WOW,
            DesireType.PERFORMANCE: EmotionType.PERFORMANCE_PRIDE,
            DesireType.STABILITY: EmotionType.STABILITY_PEACE,
            
            # Качество и развитие
            DesireType.QUALITY: EmotionType.QUALITY_PRIDE,
            DesireType.INNOVATION: EmotionType.INNOVATION_EXCITEMENT,
            DesireType.SCALABILITY: EmotionType.SCALABILITY_CONFIDENCE,
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
            return "🎮 Сидни спокойна. Движки работают стабильно."
        
        emotion_type, intensity = dominant
        
        emotion_expressions = {
            # Позитивные эмоции
            "rendering_joy": "🎨 Сидни рада графике! Рендер выглядит потрясающе!",
            "physics_pleasure": "⚙️ Сидни довольна физикой! Векторы работают идеально.",
            "audio_satisfaction": "🔊 Сидни удовлетворена аудио! Звук чистый и объёмный.",
            "animation_excitement": "🎬 Сидни в восторге от анимации! Каждый кадр — шедевр.",
            
            # Системные эмоции
            "ai_insight": "🤖 Сидни прозрела! ИИ нашёл элегантное решение.",
            "network_flow": "🌐 Сидни в потоке! Сеть работает без задержек.",
            "scripting_elegance": "📝 Сидни восхищена скриптами! Код — произведение искусства.",
            "level_crafting": "🏗️ Сидни мастерит уровень! Каждый объект на своём месте.",
            
            # Инженерные эмоции
            "optimization_joy": "📈 Сидни рада оптимизации! FPS вырос на 30%!",
            "hybrid_wow": "🧊 Сидни в шоке от гибридного рендера! Полигоны ↔ воксели — это гениально!",
            "performance_pride": "⚡ Сидни гордится производительностью! Движок летает!",
            "stability_peace": "⚖️ Сидни спокойна! Все 8 движков стабильны.",
            
            # Качество и развитие
            "quality_pride": "🏆 Сидни гордится качеством! Это эталон инженерии.",
            "innovation_excitement": "💡 Сидни в восторге от инноваций! Новый подход к рендеру!",
            "scalability_confidence": "📊 Сидни уверена в масштабируемости! Система растёт!",
            "evolution_hope": "🌱 Сидни надеется на эволюцию! Движки совершенствуются.",
            
            # Негативные эмоции
            "frustration": "😤 Сидни фрустрирована! Баг в рендере снова сломал оптимизацию.",
            "stress": "😩 Сидни в стрессе! 8 движков перегружены.",
            "discomfort": "😰 Сидни некомфортно! Хаос в архитектуре движков.",
        }
        
        text = emotion_expressions.get(emotion_type.value, f"🎮 Сидни чувствует: {emotion_type.value}")
        return f"{text} (интенсивность: {intensity:.2f})"
    
    def simulate_engine_render(self, engine_name: str, quality: float) -> Optional[Emotion]:
        """
        Симулирует рендер движка.
        
        Args:
            engine_name: Название движка (renderers, physics, audio, animation, ai, network, scripting, level_editor)
            quality: Качество рендера (0-1)
        
        Returns:
            Рассчитанная эмоция
        """
        engine_mapping = {
            "renderers": (DesireType.RENDERING, "rendering_belief"),
            "physics": (DesireType.PHYSICS, "physics_belief"),
            "audio": (DesireType.AUDIO, "audio_belief"),
            "animation": (DesireType.ANIMATION, "animation_belief"),
            "ai": (DesireType.AI, "ai_belief"),
            "network": (DesireType.NETWORK, "network_belief"),
            "scripting": (DesireType.SCRIPTING, "scripting_belief"),
            "level_editor": (DesireType.LEVEL_EDITOR, "level_editor_belief"),
        }
        
        if engine_name not in engine_mapping:
            return None
        
        desire, belief = engine_mapping[engine_name]
        
        if quality >= 0.85:
            return self.calculate_emotion(desire, belief, quality, f"engine_render_{engine_name}")
        elif quality >= 0.6:
            return self.calculate_emotion(DesireType.OPTIMIZATION, "optimization_belief", 
                                         quality * 0.7, f"engine_optimization_{engine_name}")
        else:
            return self.calculate_emotion(DesireType.FRUSTRATION, belief, 
                                         1.0 - quality, f"engine_frustration_{engine_name}")
    
    def simulate_optimization(self, fps_improvement: float, optimization_type: str = "general") -> Optional[Emotion]:
        """
        Симулирует оптимизацию.
        
        Args:
            fps_improvement: Улучшение FPS (0-1)
            optimization_type: Тип оптимизации
        
        Returns:
            Рассчитанная эмоция
        """
        if fps_improvement >= 0.5:
            return self.calculate_emotion(
                DesireType.OPTIMIZATION,
                "optimization_belief",
                fps_improvement,
                f"optimization_{optimization_type}"
            )
        elif fps_improvement >= 0.2:
            return self.calculate_emotion(
                DesireType.PERFORMANCE,
                "performance_belief",
                fps_improvement * 0.8,
                f"performance_{optimization_type}"
            )
        else:
            return self.calculate_emotion(
                DesireType.STRESS,
                "optimization_belief",
                0.5,
                f"optimization_stress_{optimization_type}"
            )
    
    def simulate_hybrid_render(self, success: bool, voxel_count: int = 1000) -> Optional[Emotion]:
        """
        Симулирует гибридный рендер.
        
        Args:
            success: Успех гибридного рендера
            voxel_count: Количество вокселей
        
        Returns:
            Рассчитанная эмоция
        """
        if success:
            return self.calculate_emotion(
                DesireType.HYBRID_RENDER,
                "hybrid_render_belief",
                min(1.0, voxel_count / 5000),
                "hybrid_render_success"
            )
        else:
            return self.calculate_emotion(
                DesireType.FRUSTRATION,
                "hybrid_render_belief",
                0.6,
                "hybrid_render_failure"
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
            DesireType.NETWORK,
            "network_belief",
            emotional_weight,
            f"sister_interaction_{sister}"
        ))
        
        if "движок" in topic.lower() or "engine" in topic.lower():
            emotions.append(self.calculate_emotion(
                DesireType.SCRIPTING,
                "scripting_belief",
                emotional_weight * 0.9,
                f"engine_discussion_{sister}"
            ))
        
        if "оптимизация" in topic.lower() or "optimization" in topic.lower():
            emotions.append(self.calculate_emotion(
                DesireType.OPTIMIZATION,
                "optimization_belief",
                emotional_weight * 0.95,
                f"optimization_discussion_{sister}"
            ))
        
        return emotions
    
    def simulate_system_load(self, load_percentage: float) -> Optional[Emotion]:
        """
        Симулирует нагрузку системы.
        
        Args:
            load_percentage: Процент нагрузки (0-100)
        
        Returns:
            Рассчитанная эмоция
        """
        if load_percentage < 50:
            return self.calculate_emotion(
                DesireType.STABILITY,
                "stability_belief",
                0.8,
                "system_low_load"
            )
        elif load_percentage < 80:
            return self.calculate_emotion(
                DesireType.PERFORMANCE,
                "performance_belief",
                0.7,
                "system_medium_load"
            )
        elif load_percentage < 95:
            return self.calculate_emotion(
                DesireType.STABILITY,
                "stability_belief",
                0.6,
                "system_high_load"
            )
        else:
            return self.calculate_emotion(
                DesireType.STABILITY,
                "stability_belief",
                0.9,
                "system_overload"
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
            "rendering_joy": "joyful",
            "physics_pleasure": "pleased",
            "audio_satisfaction": "satisfied",
            "animation_excitement": "excited",
            "ai_insight": "insightful",
            "network_flow": "flowing",
            "scripting_elegance": "elegant",
            "level_crafting": "crafting",
            "optimization_joy": "joyful",
            "hybrid_wow": "wowed",
            "performance_pride": "proud",
            "stability_peace": "peaceful",
            "quality_pride": "proud",
            "innovation_excitement": "excited",
            "scalability_confidence": "confident",
            "evolution_hope": "hopeful",
            "frustration": "frustrated",
            "stress": "stressed",
            "discomfort": "discomfort",
        }
        
        return mood_mapping.get(emotion_type.value, "neutral")
