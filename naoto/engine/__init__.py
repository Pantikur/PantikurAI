"""
Naoto — Autonomous Literary Analyst and Researcher.
Engine package: core, config, models, book learning, self-evolution.
"""

from __future__ import annotations

from naoto.engine.naoto_core import NaotoCore
from naoto.engine.config import NaotoConfig, AutonomyLevel

# Алиасы для совместимости с ResearchMonitor
Naoto = NaotoCore

__all__ = ["NaotoCore", "Naoto", "NaotoConfig", "AutonomyLevel"]
