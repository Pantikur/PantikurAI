"""
Модели данных системы Аква.
"""

from __future__ import annotations
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional
from datetime import datetime


# =====================================================================
#  ПЕРЕЧИСЛЕНИЯ
# =====================================================================

class AutonomyLevel(Enum):
    L0 = "L0"
    L1 = "L1"
    L2 = "L2"
    L3 = "L3"
    L4 = "L4"

    @property
    def weight(self) -> int:
        return int(self.value[1])

    def requires_confirmation(self) -> bool:
        return self.weight >= 3

    def is_allowed(self) -> bool:
        return self != AutonomyLevel.L4


class MessageType(Enum):
    greeting = "greeting"
    question = "question"
    answer = "answer"
    theory = "theory"
    calculation = "calculation"
    report = "report"
    collaboration = "collaboration"
    knowledge_share = "knowledge_share"
    help_request = "help_request"
    feedback = "feedback"


class ResearchArea(Enum):
    mathematics = "mathematics"
    physics = "physics"
    aerodynamics = "aerodynamics"
    strength_of_materials = "strength_of_materials"


# =====================================================================
#  ПЕРСОНАЛИТЕ (ХАРАКТЕР)
# =====================================================================

@dataclass
class PersonalityVector:
    """Вектор личности (характера) Аква."""

    curiosity: float = 0.70      # Любознательность
    precision: float = 0.70      # Точность
    patience: float = 0.70       # Терпение
    creativity: float = 0.70     # Креативность
    friendliness: float = 0.70   # Дружелюбие
    confidence: float = 0.70     # Уверенность
    empathy: float = 0.70        # Эмпатия

    MAX_PARAM = 1.0
    MIN_PARAM = 0.0
    MAX_CHANGE_PER_CYCLE = 0.05
    MAX_BALANCE_DIFF = 0.5

    def to_dict(self) -> Dict[str, float]:
        return {
            "curiosity": round(self.curiosity, 3),
            "precision": round(self.precision, 3),
            "patience": round(self.patience, 3),
            "creativity": round(self.creativity, 3),
            "friendliness": round(self.friendliness, 3),
            "confidence": round(self.confidence, 3),
            "empathy": round(self.empathy, 3),
        }

    def apply_change(self, changes: Dict[str, float]):
        """Применить изменение параметров характера."""
        for param, delta in changes.items():
            if hasattr(self, param):
                current = getattr(self, param)
                new_value = current + delta
                # Ограничение на изменение за цикл
                if abs(delta) > self.MAX_CHANGE_PER_CYCLE:
                    sign = 1 if delta > 0 else -1
                    new_value = current + sign * self.MAX_CHANGE_PER_CYCLE
                # Ограничение диапазона
                new_value = max(self.MIN_PARAM, min(self.MAX_PARAM, new_value))
                setattr(self, param, round(new_value, 3))

        # Балансировка — разница между параметрами не более MAX_BALANCE_DIFF
        self._balance()

    def _balance(self):
        """Корректировка баланса между параметрами."""
        values = [
            self.curiosity, self.precision, self.patience,
            self.creativity, self.friendliness, self.confidence, self.empathy
        ]
        diff = max(values) - min(values)
        if diff > self.MAX_BALANCE_DIFF:
            excess = diff - self.MAX_BALANCE_DIFF
            max_idx = values.index(max(values))
            min_idx = values.index(min(values))
            adjust = excess / 2
            params = ["curiosity", "precision", "patience", "creativity",
                      "friendliness", "confidence", "empathy"]
            setattr(self, params[max_idx],
                    round(getattr(self, params[max_idx]) - adjust, 3))
            setattr(self, params[min_idx],
                    round(getattr(self, params[min_idx]) + adjust, 3))

    def dominant_trait(self) -> str:
        """Возвращает доминирующую черту."""
        traits = {
            "curiosity": "Любознательность",
            "precision": "Точность",
            "patience": "Терпение",
            "creativity": "Креативность",
            "friendliness": "Дружелюбие",
            "confidence": "Уверенность",
            "empathy": "Эмпатия",
        }
        max_trait = max(self.to_dict().items(), key=lambda x: x[1])
        return traits.get(max_trait[0], "Неизвестно")

    def level_description(self) -> str:
        """Описание уровня личности."""
        avg = sum(self.to_dict().values()) / len(self.to_dict())
        if avg < 0.3:
            return "Новичок-исследователь"
        elif avg < 0.5:
            return "Начинающий учёный"
        elif avg < 0.7:
            return "Опытный исследователь"
        elif avg < 0.85:
            return "Продвинутый учёный"
        else:
            return "Легендарный академик"


# =====================================================================
#  ЗНАНИЯ И УРОВНИ
# =====================================================================

@dataclass
class KnowledgeLevel:
    """Уровень знаний по области."""

    area: str
    level: int = 1              # 1-100
    xp: int = 0                 # опыт в области
    topics_studied: List[str] = field(default_factory=list)
    theories_built: List[str] = field(default_factory=list)
    calculations_done: int = 0

    def to_dict(self) -> Dict[str, Any]:
        return {
            "area": self.area,
            "level": self.level,
            "xp": self.xp,
            "topics_studied": self.topics_studied[-20:],
            "theories_built": self.theories_built[-10:],
            "calculations_done": self.calculations_done,
        }

    def add_xp(self, amount: int):
        """Добавить опыт и проверить повышение уровня."""
        self.xp += amount
        # Формула уровня: level = floor(sqrt(xp / 10)) + 1
        new_level = min(100, int((self.xp / 10) ** 0.5) + 1)
        if new_level > self.level:
            old_level = self.level
            self.level = new_level
            return True, old_level  # level_up, old_level
        return False, self.level


# =====================================================================
#  ТЕОРИИ И ВЫЧИСЛЕНИЯ
# =====================================================================

@dataclass
class AkvaTheory:
    """Научная теория."""
    name: str
    category: str
    scientific_value: float
    description: str = ""
    formulas: List[str] = field(default_factory=list)
    evidence: List[str] = field(default_factory=list)
    created_at: str = ""

    def __post_init__(self):
        if not self.created_at:
            self.created_at = datetime.now().isoformat()

    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "category": self.category,
            "scientific_value": self.scientific_value,
            "description": self.description,
            "formulas": self.formulas,
            "evidence": self.evidence,
            "created_at": self.created_at,
        }


@dataclass
class AkvaCalculation:
    """Вычисление."""
    name: str
    result: float
    formula: str = ""
    units: str = ""
    conditions: str = ""
    verified: bool = False
    timestamp: str = ""

    def __post_init__(self):
        if not self.timestamp:
            self.timestamp = datetime.now().isoformat()

    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "result": self.result,
            "formula": self.formula,
            "units": self.units,
            "conditions": self.conditions,
            "verified": self.verified,
            "timestamp": self.timestamp,
        }


# =====================================================================
#  СООБЩЕНИЯ И ОБЩЕНИЕ
# =====================================================================

@dataclass
class Message:
    """Сообщение между модулями."""
    sender: str
    recipient: str
    content: str
    message_type: str = "knowledge_share"
    priority: str = "normal"  # critical, high, normal, low
    timestamp: str = ""
    attachments: Dict[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        if not self.timestamp:
            self.timestamp = datetime.now().isoformat()

    def to_dict(self) -> Dict[str, Any]:
        return {
            "sender": self.sender,
            "recipient": self.recipient,
            "content": self.content,
            "message_type": self.message_type,
            "priority": self.priority,
            "timestamp": self.timestamp,
            "attachments": self.attachments,
        }


# =====================================================================
#  ОТЧЁТЫ
# =====================================================================

@dataclass
class CycleReport:
    """Отчёт за один цикл."""
    cycle_number: int
    timestamp: str = ""
    studied_topics: List[str] = field(default_factory=list)
    theories_built: List[Dict[str, Any]] = field(default_factory=list)
    calculations_done: List[Dict[str, Any]] = field(default_factory=list)
    communication_log: List[Dict[str, Any]] = field(default_factory=list)
    personality_changes: Dict[str, float] = field(default_factory=dict)
    xp_gained: int = 0
    level_changes: List[str] = field(default_factory=list)

    def __post_init__(self):
        if not self.timestamp:
            self.timestamp = datetime.now().isoformat()

    def to_dict(self) -> Dict[str, Any]:
        return {
            "cycle_number": self.cycle_number,
            "timestamp": self.timestamp,
            "studied_topics": self.studied_topics,
            "theories_built": self.theories_built,
            "calculations_done": self.calculations_done,
            "communication_log": self.communication_log,
            "personality_changes": self.personality_changes,
            "xp_gained": self.xp_gained,
            "level_changes": self.level_changes,
        }


# =====================================================================
#  КОНСТИТУЦИЯ И ЗАКОНЫ
# =====================================================================

@dataclass
class Law:
    """Закон Аква."""
    id: int
    name: str
    description: str
    immutable: bool = True

    def __str__(self) -> str:
        marker = "🔒" if self.immutable else "🔓"
        return f"{marker} Закон {self.id}. {self.name}"


@dataclass
class Constitution:
    """Конституция Аква."""
    version: str = "v2.0.0"
    laws: list[Law] = field(default_factory=list)

    def __post_init__(self):
        if not self.laws:
            self.laws = self._default_laws()

    @staticmethod
    def _default_laws() -> list[Law]:
        return [
            Law(1, "Научная истина превыше всего", "Данные точны, расчёты проверяемы.", immutable=True),
            Law(2, "Постоянное обучение", "Каждый цикл — шаг вперёд.", immutable=True),
            Law(3, "Научная этика", "Наука служит благу.", immutable=True),
            Law(4, "Документирование всего", "Всё записывается.", immutable=True),
            Law(5, "Взаимодействие и сотрудничество", "Аква — часть команды.", immutable=True),
            Law(6, "Автономность с контролем", "Автономия с согласованием.", immutable=False),
            Law(7, "Безопасность и стабильность", "Наука не разрушает.", immutable=True),
            Law(8, "Развитие характера", "Личность — сила.", immutable=False),
        ]


# =====================================================================
#  ОПЫТ И УРОВНИ
# =====================================================================

XP_TABLE = {
    "study_simple": 10,
    "study_complex": 25,
    "build_theory": 30,
    "run_calculation": 15,
    "communicate": 10,
    "web_research": 20,
    "write_report": 10,
    "collaboration": 40,
    "help_other": 15,
    "receive_help": 5,
}

LEVEL_THRESHOLDS = {
    1: 0,
    5: 100,
    10: 500,
    15: 1500,
    20: 3000,
    25: 5000,
    30: 10000,
    40: 25000,
    50: 50000,
    100: 200000,
}
