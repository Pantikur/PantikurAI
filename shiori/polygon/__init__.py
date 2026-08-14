"""
SHIORI POLYGON — Боевой тренажёр Шиори.

Изолированная среда для обучения и тренировки защиты.
"""

from shiori.polygon.polygon_core import (
    ShioriPolygon,
    create_polygon,
    ThreatType,
    AttackMethod,
    DefenseAction,
    TrainingResult,
)

__all__ = [
    "ShioriPolygon",
    "create_polygon",
    "ThreatType",
    "AttackMethod",
    "DefenseAction",
    "TrainingResult",
]
