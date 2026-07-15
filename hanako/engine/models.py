"""
Модели данных Ханако — исследователь гравитации.
"""

from __future__ import annotations

import enum
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Optional


# ==================== Гравитационные модели ====================

class TheoryCategory(enum.Enum):
    """Категории гравитационных теорий."""
    CLASSICAL = "classical"
    RELATIVITY = "relativity"
    QUANTUM = "quantum"
    STRING = "string"
    LOOP = "loop"
    ENTROPIC = "entropic"
    MODIFIED = "modified"
    GRAVITON = "graviton"
    HYPOTHETICAL = "hypothetical"
    UNIFIED = "unified"


class ResearchStatus(enum.Enum):
    """Статус исследования."""
    PLANNING = "planning"
    IN_PROGRESS = "in_progress"
    REVIEWING = "reviewing"
    PUBLISHED = "published"
    ARCHIVED = "archived"
    FAILED = "failed"


class CommunicationType(enum.Enum):
    """Типы сообщений между девочками."""
    GREETING = "greeting"
    THEORY = "theory"
    CALCULATION = "calculation"
    QUESTION = "question"
    ANSWER = "answer"
    REPORT = "report"
    LEVEL_UP = "level_up"
    SELF_DEV = "self_dev"
    CHARACTER = "character"
    REQUEST = "request"
    ACKNOWLEDGE = "acknowledge"
    EMOTION = "emotion"
    DISCUSSION = "discussion"


# ==================== Теории ====================

@dataclass
class GravityTheory:
    """Гравитационная теория."""
    title: str
    category: TheoryCategory
    description: str
    equations: list[str] = field(default_factory=list)
    predictions: list[str] = field(default_factory=list)
    evidence: list[str] = field(default_factory=list)
    confidence: float = 0.0
    sources: list[str] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    tags: list[str] = field(default_factory=list)
    id: str = ""

    def to_dict(self) -> dict[str, Any]:
        return {
            "title": self.title, "category": self.category.value,
            "description": self.description, "equations": self.equations,
            "predictions": self.predictions, "evidence": self.evidence,
            "confidence": self.confidence, "sources": self.sources,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "tags": self.tags, "id": self.id,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "GravityTheory":
        return cls(
            title=data["title"], category=TheoryCategory(data["category"]),
            description=data["description"], equations=data.get("equations", []),
            predictions=data.get("predictions", []), evidence=data.get("evidence", []),
            confidence=data.get("confidence", 0.0), sources=data.get("sources", []),
            created_at=datetime.fromisoformat(data["created_at"]),
            updated_at=datetime.fromisoformat(data["updated_at"]),
            tags=data.get("tags", []), id=data.get("id", ""),
        )


# ==================== Исследования ====================

@dataclass
class ResearchTask:
    """Задача исследования."""
    title: str
    description: str
    category: TheoryCategory
    status: ResearchStatus = ResearchStatus.PLANNING
    priority: int = 5
    progress: float = 0.0
    related_theories: list[str] = field(default_factory=list)
    sources: list[str] = field(default_factory=list)
    notes: list[str] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.now)
    id: str = ""

    def to_dict(self) -> dict[str, Any]:
        return {
            "title": self.title, "description": self.description,
            "category": self.category.value, "status": self.status.value,
            "priority": self.priority, "progress": self.progress,
            "related_theories": self.related_theories, "sources": self.sources,
            "notes": self.notes, "created_at": self.created_at.isoformat(),
            "id": self.id,
        }


# ==================== Веб-исследования ====================

@dataclass
class WebResearchResult:
    """Результат веб-исследования."""
    query: str
    url: str
    title: str
    summary: str
    relevance: float = 0.0
    content_type: str = "article"
    tags: list[str] = field(default_factory=list)
    extracted_equations: list[str] = field(default_factory=list)
    extracted_facts: list[str] = field(default_factory=list)
    cached_at: datetime = field(default_factory=datetime.now)

    def to_dict(self) -> dict[str, Any]:
        return {
            "query": self.query, "url": self.url, "title": self.title,
            "summary": self.summary, "relevance": self.relevance,
            "content_type": self.content_type, "tags": self.tags,
            "extracted_equations": self.extracted_equations,
            "extracted_facts": self.extracted_facts,
            "cached_at": self.cached_at.isoformat(),
        }


# ==================== Сообщения ====================

@dataclass
class ScientistMessage:
    """Сообщение между учёными-девочками."""
    sender: str
    recipient: str
    content: str
    message_type: CommunicationType = CommunicationType.GREETING
    priority: int = 5
    metadata: dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.now)
    message_id: str = ""
    read: bool = False

    def to_dict(self) -> dict[str, Any]:
        return {
            "sender": self.sender, "recipient": self.recipient,
            "content": self.content, "message_type": self.message_type.value,
            "priority": self.priority, "metadata": self.metadata,
            "timestamp": self.timestamp.isoformat(), "message_id": self.message_id,
            "read": self.read,
        }


# ==================== Характер ====================

@dataclass
class CharacterTraits:
    """Черты характера Ханако."""
    temperament: str = "холерик"
    sociality: str = "общительная"
    emotionality: str = "страстная"
    worldview: str = "исследователь"
    dominance: str = "уравновешенная"
    change_attitude: str = "открытая"
    complexity: str = "глубокая"
    gravity_passion: float = 0.9
    curiosity: float = 0.95
    courage: float = 0.8
    patience: float = 0.7
    creativity: float = 0.85
    collaboration: float = 0.8
    strengths: list[str] = field(default_factory=lambda: [
        "анализ пространственно-временных метрик",
        "построение гравитационных моделей",
        "математическое мышление",
        "неустрашимость перед неизвестным",
    ])
    values: list[str] = field(default_factory=lambda: [
        "истина о гравитации", "свобода исследования",
        "сотрудничество с сёстрами", "постоянное развитие",
    ])

    def to_dict(self) -> dict[str, Any]:
        return {
            "temperament": self.temperament, "sociality": self.sociality,
            "emotionality": self.emotionality, "worldview": self.worldview,
            "dominance": self.dominance, "change_attitude": self.change_attitude,
            "complexity": self.complexity, "gravity_passion": self.gravity_passion,
            "curiosity": self.curiosity, "courage": self.courage,
            "patience": self.patience, "creativity": self.creativity,
            "collaboration": self.collaboration, "strengths": self.strengths,
            "values": self.values,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "CharacterTraits":
        return cls(
            temperament=data.get("temperament", "холерик"),
            sociality=data.get("sociality", "общительная"),
            emotionality=data.get("emotionality", "страстная"),
            worldview=data.get("worldview", "исследователь"),
            dominance=data.get("dominance", "уравновешенная"),
            change_attitude=data.get("change_attitude", "открытая"),
            complexity=data.get("complexity", "глубокая"),
            gravity_passion=data.get("gravity_passion", 0.9),
            curiosity=data.get("curiosity", 0.95),
            courage=data.get("courage", 0.8),
            patience=data.get("patience", 0.7),
            creativity=data.get("creativity", 0.85),
            collaboration=data.get("collaboration", 0.8),
            strengths=data.get("strengths", []),
            values=data.get("values", []),
        )


# ==================== Уровень и опыт ====================

@dataclass
class KnowledgeLevel:
    """Уровень знаний Ханако."""
    overall_level: int = 1
    overall_xp: float = 0.0
    xp_to_next: float = 100.0

    gravity_theory_level: int = 1
    gravity_theory_xp: float = 0.0
    web_research_level: int = 1
    web_research_xp: float = 0.0
    self_development_level: int = 1
    self_development_xp: float = 0.0
    communication_level: int = 1
    communication_xp: float = 0.0
    calculation_level: int = 1
    calculation_xp: float = 0.0
    character_growth_level: int = 1
    character_growth_xp: float = 0.0

    total_theories: int = 0
    total_researches: int = 0
    total_websites_scanned: int = 0
    total_messages_sent: int = 0
    total_messages_received: int = 0
    total_reports_written: int = 0
    total_character_upgrades: int = 0
    uptime_hours: float = 0.0
    level_history: list[dict] = field(default_factory=list)

    def add_xp(self, amount: float, category: str = "overall") -> bool:
        old_level = self.overall_level
        if category == "overall" or category == "all":
            self.overall_xp += amount
        elif category == "gravity_theory":
            self.gravity_theory_xp += amount
        elif category == "web_research":
            self.web_research_xp += amount
        elif category == "self_development":
            self.self_development_xp += amount
        elif category == "communication":
            self.communication_xp += amount
        elif category == "calculation":
            self.calculation_xp += amount
        elif category == "character_growth":
            self.character_growth_xp += amount

        leveled_up = False
        if self.overall_xp >= self.xp_to_next:
            self.overall_level += 1
            self.xp_to_next = self._calc_xp_for_level(self.overall_level)
            leveled_up = True
            self.level_history.append({
                "level": self.overall_level,
                "timestamp": datetime.now().isoformat(),
                "xp": self.overall_xp,
            })
        return leveled_up or (old_level != self.overall_level)

    def add_category_xp(self, amount: float, category: str) -> bool:
        old_level = 0
        if category == "gravity_theory":
            old_level = self.gravity_theory_level
            self.gravity_theory_xp += amount
            if self.gravity_theory_xp >= self.xp_to_next:
                self.gravity_theory_level += 1
                self.gravity_theory_xp = 0
        elif category == "web_research":
            old_level = self.web_research_level
            self.web_research_xp += amount
            if self.web_research_xp >= self.xp_to_next:
                self.web_research_level += 1
                self.web_research_xp = 0
        elif category == "self_development":
            old_level = self.self_development_level
            self.self_development_xp += amount
            if self.self_development_xp >= self.xp_to_next:
                self.self_development_level += 1
                self.self_development_xp = 0
        elif category == "communication":
            old_level = self.communication_level
            self.communication_xp += amount
            if self.communication_xp >= self.xp_to_next:
                self.communication_level += 1
                self.communication_xp = 0
        elif category == "calculation":
            old_level = self.calculation_level
            self.calculation_xp += amount
            if self.calculation_xp >= self.xp_to_next:
                self.calculation_level += 1
                self.calculation_xp = 0
        elif category == "character_growth":
            old_level = self.character_growth_level
            self.character_growth_xp += amount
            if self.character_growth_xp >= self.xp_to_next:
                self.character_growth_level += 1
                self.character_growth_xp = 0

        leveled_up = self.add_xp(amount * 0.3, "overall")
        return leveled_up or (old_level != self.overall_level)

    @staticmethod
    def _calc_xp_for_level(level: int) -> float:
        return 100.0 * (level ** 1.5)

    def get_level_name(self) -> str:
        if self.overall_level < 5:
            return "Новичок гравитации"
        elif self.overall_level < 15:
            return "Ученица гравитации"
        elif self.overall_level < 30:
            return "Исследовательница"
        elif self.overall_level < 50:
            return "Мастер гравитации"
        elif self.overall_level < 70:
            return "Грандмастер гравитации"
        elif self.overall_level < 90:
            return "Легенда гравитации"
        else:
            return "Божество гравитации"

    def to_dict(self) -> dict[str, Any]:
        return {
            "overall_level": self.overall_level,
            "overall_xp": self.overall_xp,
            "xp_to_next": self.xp_to_next,
            "gravity_theory_level": self.gravity_theory_level,
            "gravity_theory_xp": self.gravity_theory_xp,
            "web_research_level": self.web_research_level,
            "web_research_xp": self.web_research_xp,
            "self_development_level": self.self_development_level,
            "self_development_xp": self.self_development_xp,
            "communication_level": self.communication_level,
            "communication_xp": self.communication_xp,
            "calculation_level": self.calculation_level,
            "calculation_xp": self.calculation_xp,
            "character_growth_level": self.character_growth_level,
            "character_growth_xp": self.character_growth_xp,
            "total_theories": self.total_theories,
            "total_researches": self.total_researches,
            "total_websites_scanned": self.total_websites_scanned,
            "total_messages_sent": self.total_messages_sent,
            "total_messages_received": self.total_messages_received,
            "total_reports_written": self.total_reports_written,
            "total_character_upgrades": self.total_character_upgrades,
            "uptime_hours": self.uptime_hours,
            "level_name": self.get_level_name(),
            "level_history": self.level_history[-50:],
        }


# ==================== Отчёты ====================

@dataclass
class ResearchReport:
    """Отчёт исследования."""
    title: str
    report_type: str
    content: str
    author: str = "hanako"
    created_at: datetime = field(default_factory=datetime.now)
    tags: list[str] = field(default_factory=list)
    related_theories: list[str] = field(default_factory=list)
    statistics: dict[str, Any] = field(default_factory=dict)
    id: str = ""

    def to_dict(self) -> dict[str, Any]:
        return {
            "title": self.title, "report_type": self.report_type,
            "content": self.content, "author": self.author,
            "created_at": self.created_at.isoformat(), "tags": self.tags,
            "related_theories": self.related_theories,
            "statistics": self.statistics, "id": self.id,
        }


# ==================== События ====================

@dataclass
class HanakoEvent:
    """Событие в жизни Ханако."""
    event_type: str
    content: str
    timestamp: datetime = field(default_factory=datetime.now)
    metadata: dict[str, Any] = field(default_factory=dict)
    event_id: str = ""

    def to_dict(self) -> dict[str, Any]:
        return {
            "event_type": self.event_type,
            "content": self.content,
            "timestamp": self.timestamp.isoformat(),
            "metadata": self.metadata,
            "event_id": self.event_id,
        }
