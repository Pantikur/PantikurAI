"""
Модели данных Айко — структуры для хранения знаний и обучающих пар.
"""

from __future__ import annotations
import json
from dataclasses import dataclass, field, asdict
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any, Optional


class KnowledgeCategory(Enum):
    """Категории знаний."""
    FACT = "fact"
    CONCEPT = "concept"
    PLOT = "plot"
    CHARACTER = "character"
    STYLE = "style"
    LORE = "lore"
    THEME = "theme"


class BookType(Enum):
    """Типы книг."""
    FICTION = "fiction"
    SCIENCE = "science"
    TECHNICAL = "technical"
    PHILOSOPHY = "philosophy"
    HISTORY = "history"
    EDUCATION = "education"


@dataclass
class TrainingPair:
    """Обучающая пара вопрос-ответ."""
    question: str
    answer: str
    context: str
    source: str
    chapter: int
    category: str
    tags: list[str] = field(default_factory=list)
    confidence: float = 1.0
    metadata: dict = field(default_factory=dict)

    def to_dict(self) -> dict:
        """Конвертировать в словарь."""
        return asdict(self)

    def to_json(self) -> str:
        """Конвертировать в JSON."""
        return json.dumps(self.to_dict(), ensure_ascii=False)

    @classmethod
    def from_dict(cls, data: dict) -> "TrainingPair":
        """Создать из словаря."""
        return cls(**data)

    @classmethod
    def from_json(cls, json_str: str) -> "TrainingPair":
        """Создать из JSON."""
        return cls.from_dict(json.loads(json_str))


@dataclass
class KnowledgeEntry:
    """Запись в базе знаний."""
    content: str
    category: str
    source: str
    chapter: int
    page: Optional[int] = None
    tags: list[str] = field(default_factory=list)
    confidence: float = 1.0
    related_entries: list[str] = field(default_factory=list)
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())

    def to_dict(self) -> dict:
        """Конвертировать в словарь."""
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict) -> "KnowledgeEntry":
        """Создать из словаря."""
        return cls(**data)


@dataclass
class LoreEntry:
    """Запись в базе лора."""
    world_name: str
    entry_type: str  # geography, character, event, rule
    content: str
    book_source: str
    chapter: int
    relationships: dict[str, list[str]] = field(default_factory=dict)
    contradictions: list[str] = field(default_factory=list)
    confidence: float = 1.0

    def to_dict(self) -> dict:
        """Конвертировать в словарь."""
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict) -> "LoreEntry":
        """Создать из словаря."""
        return cls(**data)


@dataclass
class StyleEntry:
    """Запись в базе стиля."""
    author: str
    book_title: str
    chapter: int
    style_features: list[str] = field(default_factory=list)
    literary_devices: list[str] = field(default_factory=list)
    dialogue_style: str = ""
    narrative_style: str = ""
    examples: list[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        """Конвертировать в словарь."""
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict) -> "StyleEntry":
        """Создать из словаря."""
        return cls(**data)


@dataclass
class BookSummary:
    """Суть книги."""
    source: str
    summary: str
    key_points: list[str] = field(default_factory=list)
    main_characters: list[str] = field(default_factory=list)
    setting: str = ""
    genre: str = ""
    word_count: int = 0

    def to_dict(self) -> dict:
        """Конвертировать в словарь."""
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict) -> "BookSummary":
        """Создать из словаря."""
        return cls(**data)


@dataclass
class BookThought:
    """Мысль/идея книги."""
    source: str
    central_thought: str
    moral_lesson: str = ""
    philosophical_concepts: list[str] = field(default_factory=list)
    author_intention: str = ""

    def to_dict(self) -> dict:
        """Конвертировать в словарь."""
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict) -> "BookThought":
        """Создать из словаря."""
        return cls(**data)


@dataclass
class BookMetadata:
    """Метаданные книги."""
    title: str
    author: str
    book_type: str
    total_chapters: int = 0
    total_pages: int = 0
    language: str = "ru"
    tags: list[str] = field(default_factory=list)
    chapters_processed: int = 0
    training_pairs_generated: int = 0
    knowledge_entries: int = 0
    last_processed_chapter: int = 0
    processing_status: str = "pending"  # pending, in_progress, completed, error

    def to_dict(self) -> dict:
        """Конвертировать в словарь."""
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict) -> "BookMetadata":
        """Создать из словаря."""
        return cls(**data)


@dataclass
class AyikoState:
    """Состояние системы Айко."""
    version: str
    cycle_count: int = 0
    books_read: int = 0
    chapters_processed: int = 0
    training_pairs_generated: int = 0
    knowledge_entries_saved: int = 0
    lore_entries_saved: int = 0
    metrics: dict = field(default_factory=dict)
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())

    def to_dict(self) -> dict:
        """Конвертировать в словарь."""
        return asdict(self)

    def save_to_file(self, path: Path):
        """Сохранить состояние в файл."""
        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            json.dump(self.to_dict(), f, ensure_ascii=False, indent=2)

    @classmethod
    def load_from_file(cls, path: Path) -> "AyikoState":
        """Загрузить состояние из файла."""
        if not path.exists():
            return cls(version="v1.0.0")
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        return cls(**data)
