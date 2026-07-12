"""
Модели данных Наото.
"""

from __future__ import annotations
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, List, Optional


@dataclass
class VisualTask:
    """Визуальная задача."""
    
    task_id: str
    description: str
    task_type: str  # sketch, drawing, 3d, reference
    priority: str = "medium"  # high, medium, low
    style: str = "freehand"
    standards: str = "iso"
    detail_level: str = "mid"
    references: List[str] = field(default_factory=list)
    context: Dict[str, Any] = field(default_factory=dict)
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    completed_at: Optional[str] = None


@dataclass
class VisualResult:
    """Результат визуальной работы."""
    
    result_id: str
    task_type: str  # sketch, drawing, 3d
    description: str
    quality_score: float = 0.0
    accuracy: float = 0.0
    
    # Для набросков
    sketch_style: str = ""
    composition: Dict[str, Any] = field(default_factory=dict)
    elements: List[Dict[str, Any]] = field(default_factory=list)
    
    # Для чертежей
    drawing_standards: str = ""
    projections: List[str] = field(default_factory=list)
    dimensions: Dict[str, float] = field(default_factory=dict)
    tolerances: str = ""
    
    # Для 3D-моделей
    polygon_count: int = 0
    texture_resolution: str = ""
    materials: List[Dict[str, Any]] = field(default_factory=list)
    lighting: Dict[str, Any] = field(default_factory=dict)
    render_settings: Dict[str, Any] = field(default_factory=dict)
    
    # Общие
    references_used: List[str] = field(default_factory=list)
    techniques_applied: List[str] = field(default_factory=list)
    notes: str = ""
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    
    def to_dict(self) -> Dict[str, Any]:
        """Конвертирует в словарь."""
        return {
            "result_id": self.result_id,
            "task_type": self.task_type,
            "description": self.description,
            "quality_score": self.quality_score,
            "accuracy": self.accuracy,
            "sketch_style": self.sketch_style,
            "composition": self.composition,
            "elements": self.elements,
            "drawing_standards": self.drawing_standards,
            "projections": self.projections,
            "dimensions": self.dimensions,
            "tolerances": self.tolerances,
            "polygon_count": self.polygon_count,
            "texture_resolution": self.texture_resolution,
            "materials": self.materials,
            "lighting": self.lighting,
            "render_settings": self.render_settings,
            "references_used": self.references_used,
            "techniques_applied": self.techniques_applied,
            "notes": self.notes,
            "created_at": self.created_at
        }
