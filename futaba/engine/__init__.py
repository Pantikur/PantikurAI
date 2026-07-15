"""
Futaba — система управления, правовых исследований и автономного саморазвития.

Футаба (フタバ — «расцвет») — главный заместитель Разработчика проекта Вугларст.
Управляет проектом, изучает право, развивается autonomно и воспитывает девочек-учёных.
"""

from __future__ import annotations

from futaba.engine.config import FutabaConfig
from futaba.engine.models import (
    AutonomyLevel,
    Constitution,
    GirlCharacter,
    LegalDocument,
    KnowledgeLevel,
    KnowledgeRecord,
    Law,
    ManagementDecision,
    CommunicationType,
    CommunicationLog,
    Report,
    ChangeRecord,
    ChangeType,
    SimulationResult,
    ReignVersion,
    World,
    Faction,
    EventKind,
)

__all__ = [
    "FutabaConfig",
    "AutonomyLevel",
    "Constitution",
    "GirlCharacter",
    "LegalDocument",
    "KnowledgeLevel",
    "KnowledgeRecord",
    "Law",
    "ManagementDecision",
    "CommunicationType",
    "CommunicationLog",
    "Report",
    "ChangeRecord",
    "ChangeType",
    "SimulationResult",
    "ReignVersion",
    "World",
    "Faction",
    "EventKind",
]
