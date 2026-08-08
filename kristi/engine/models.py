"""
Модели данных Кристи — режиссёр видеопроизводства.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional


class ProductionStage(Enum):
    """Этапы видеопроизводства."""
    CONCEPT = "concept"               # Концепция
    SCRIPT = "script"                 # Сценарий
    STORYBOARD = "storyboard"         # Раскадровка
    SHOOT = "shoot"                   # Постановка / генерация
    EDIT = "edit"                     # Монтаж
    SOUND = "sound"                   # Звуковой дизайн
    COLOR = "color"                   # Цветокоррекция
    RENDER = "render"                 # Рендер и экспорт


class SceneType(Enum):
    """Типы сцен."""
    DIALOGUE = "dialogue"             # Диалог
    ACTION = "action"                 # Действие
    EMOTION = "emotion"               # Эмоциональная
    TRANSITION = "transition"         # Переходная
    ESTABLISHING = "establishing"     # Установочная
    CLIMAX = "climax"                 # Кульминация


class CameraAngle(Enum):
    """Ракурсы камеры."""
    WIDE = "wide"                     # Общий план
    MEDIUM = "medium"                 # Средний план
    CLOSE_UP = "close_up"             # Крупный план
    MACRO = "macro"                   # Макро
    LOW_ANGLE = "low_angle"           # Нижний ракурс
    HIGH_ANGLE = "high_angle"         # Верхний ракурс
    DRONE = "drone"                   # С дрона


class TransitionType(Enum):
    """Типы переходов."""
    CUT = "cut"                       # Резкая склейка
    FADE = "fade"                     # Растворение
    DISSOLVE = "dissolve"             # Растворение
    WIPE = "wipe"                     # Протирка
    JUMP_CUT = "jump_cut"             # Прыжок
    MATCH_CUT = "match_cut"           # Плавный переход


@dataclass
class Scene:
    """Описание сцены."""
    scene_number: int
    type: SceneType
    description: str
    dialogue: str = ""
    camera_angle: CameraAngle = CameraAngle.MEDIUM
    lighting: str = "standard"
    duration_seconds: float = 5.0
    emotion: str = "neutral"
    characters: List[str] = field(default_factory=list)
    storyboard_notes: str = ""
    
    def to_dict(self) -> dict:
        return {
            "scene_number": self.scene_number,
            "type": self.type.value,
            "description": self.description,
            "dialogue": self.dialogue,
            "camera_angle": self.camera_angle.value,
            "lighting": self.lighting,
            "duration_seconds": self.duration_seconds,
            "emotion": self.emotion,
            "characters": self.characters,
            "storyboard_notes": self.storyboard_notes,
        }


@dataclass
class Script:
    """Сценарий видео."""
    title: str
    concept: str
    genre: str = ""
    target_audience: str = ""
    scenes: List[Scene] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.now)
    status: str = "draft"  # draft, in_progress, completed
    
    def to_dict(self) -> dict:
        return {
            "title": self.title,
            "concept": self.concept,
            "genre": self.genre,
            "target_audience": self.target_audience,
            "scenes": [s.to_dict() for s in self.scenes],
            "created_at": self.created_at.isoformat(),
            "status": self.status,
        }


@dataclass
class ProductionProject:
    """Проект видеопроизводства."""
    title: str
    concept: str = ""
    script: Optional[Script] = None
    stage: ProductionStage = ProductionStage.CONCEPT
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    status: str = "pending"  # pending, in_progress, completed, archived
    notes: str = ""
    technical_params: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> dict:
        return {
            "title": self.title,
            "stage": self.stage.value,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "status": self.status,
            "notes": self.notes,
            "technical_params": self.technical_params,
        }


@dataclass
class Report:
    """Отчёт Кристи."""
    title: str
    content: str
    stage: ProductionStage = ProductionStage.CONCEPT
    timestamp: datetime = field(default_factory=datetime.now)
    xp_earned: int = 0
    lessons_learned: List[str] = field(default_factory=list)
    
    def to_dict(self) -> dict:
        return {
            "title": self.title,
            "content": self.content,
            "stage": self.stage.value,
            "timestamp": self.timestamp.isoformat(),
            "xp_earned": self.xp_earned,
            "lessons_learned": self.lessons_learned,
        }


@dataclass
class KnowledgeEntry:
    """Запись о полученных знаниях."""
    category: str
    topic: str
    description: str
    source: str = ""
    timestamp: datetime = field(default_factory=datetime.now)
    
    def to_dict(self) -> dict:
        return {
            "category": self.category,
            "topic": self.topic,
            "description": self.description,
            "source": self.source,
            "timestamp": self.timestamp.isoformat(),
        }


@dataclass
class LevelProgress:
    """Прогресс по уровням."""
    current_level: int = 1
    current_xp: int = 0
    levels: Dict[int, int] = field(default_factory=lambda: {
        1: 0, 2: 100, 3: 300, 4: 600, 5: 1000,
        6: 1500, 7: 2200, 8: 3000, 9: 4000, 10: 5500,
        11: 7000, 12: 9000, 13: 11000, 14: 13500, 15: 16500,
        16: 20000, 17: 24000, 18: 28500, 19: 34000, 20: 40000,
    })
    
    @property
    def level_name(self) -> str:
        names = {
            1: "Стажёр", 2: "Ассистент режиссёра", 3: "Помощник оператора",
            4: "Монтажёр", 5: "Режиссёр короткого метра", 6: "Режиссёр клипов",
            7: "Продюсер", 8: "Режиссёр анимации", 9: "Визионер",
            10: "Мастер монтажа", 11: "Гений повествования",
            12: "Легенда видеопроизводства", 13: "Новатор",
            14: "Профессор киноискусства", 15: "Мастер режиссуры",
            16: "Визионер поколения", 17: "Повелитель кадров",
            18: "Хранитель истории", 19: "Архитектор миров",
            20: "Бог Видеопроизводства",
        }
        return names.get(self.current_level, "Неизвестно")
    
    def to_dict(self) -> dict:
        return {
            "current_level": self.current_level,
            "current_xp": self.current_xp,
            "level_name": self.level_name,
        }


@dataclass
class KristiState:
    """Состояние Кристи."""
    version: str = "v1.0.0"
    cycle_count: int = 0
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    
    # Производство
    active_projects: List[ProductionProject] = field(default_factory=list)
    completed_projects: List[ProductionProject] = field(default_factory=list)
    
    # Знания
    knowledge_entries: List[KnowledgeEntry] = field(default_factory=list)
    level_progress: LevelProgress = field(default_factory=LevelProgress)
    
    # Отчёты
    reports: List[Report] = field(default_factory=list)
    
    # Метрики
    metrics: Dict[str, Any] = field(default_factory=lambda: {
        "total_videos": 0,
        "total_scenes": 0,
        "total_scripts": 0,
        "total_lessons": 0,
        "interactions": 0,
    })
    
    def to_dict(self) -> dict:
        return {
            "version": self.version,
            "cycle_count": self.cycle_count,
            "timestamp": self.timestamp,
            "active_projects": [p.to_dict() for p in self.active_projects],
            "completed_projects": [p.to_dict() for p in self.completed_projects],
            "knowledge_entries": [k.to_dict() for k in self.knowledge_entries],
            "level_progress": self.level_progress.to_dict(),
            "reports": [r.to_dict() for r in self.reports],
            "metrics": self.metrics,
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> "KristiState":
        state = cls()
        state.version = data.get("version", state.version)
        state.cycle_count = data.get("cycle_count", 0)
        state.timestamp = data.get("timestamp", state.timestamp)
        state.metrics = data.get("metrics", state.metrics)
        return state
