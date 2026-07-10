"""
Latislane — Фабрика тел.

Создаёт спецификации тел для разных типов:
- Механическое
- Бионическое
- Органическое
"""

import json
import logging
import os
import time
from pathlib import Path
from typing import Dict, List, Optional, Any

from .body_modules import (
    BodyModule,
    BodyType,
    BodySpecification,
    DevelopmentStage
)
from .internet_learning import InternetLearningEngine

logger = logging.getLogger("latislane.factory")


class BodyFactory:
    """
    Фабрика для проектирования тел.
    
    Использует изученные знания анатомии
    для создания спецификаций тел.
    """
    
    def __init__(
        self,
        body_modules: Dict[str, BodyModule],
        learning_engine: InternetLearningEngine,
        data_dir: str = "data/latislane/bodies"
    ):
        self.body_modules = body_modules
        self.learning_engine = learning_engine
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)
        
        # Спроектированные тела
        self.designed_bodies: Dict[str, BodySpecification] = {}
        
        # Шаблоны проектирования
        self.design_templates = self._load_design_templates()
        
        logger.info(f"🏭 BodyFactory инициализирован")
        logger.info(f"   📦 Модулей: {len(body_modules)}")
        logger.info(f"   📋 Шаблонов: {len(self.design_templates)}")
    
    def _load_design_templates(self) -> Dict[str, Any]:
        """Загрузить шаблоны проектирования."""
        templates_file = self.data_dir / "design_templates.json"
        
        if templates_file.exists():
            try:
                with open(templates_file, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception as e:
                logger.warning(f"⚠️ Ошибка загрузки шаблонов: {e}")
        
        # Создание шаблонов по умолчанию
        templates = self._create_default_templates()
        self._save_templates(templates)
        return templates
    
    def _create_default_templates(self) -> Dict[str, Any]:
        """Создать шаблоны проектирования по умолчанию."""
        templates = {
            "mechanical": {
                "skeletal_system": {
                    "material": "titanium_alloy_ti64",
                    "weight_kg": 60,
                    "strength_n": 50000,
                    "joints": "hydraulic_servo",
                    "modular": True
                },
                "muscular_system": {
                    "actuator_type": "electromechanical",
                    "force_n": 500,
                    "speed_ms": 2.0,
                    "efficiency_percent": 85
                },
                "nervous_system": {
                    "processor": "neural_chip_fpga",
                    "latency_ms": 1,
                    "bandwidth_tbps": 10,
                    "ai_model": "custom_rnn_lstm"
                },
                "cardiovascular_system": {
                    "pump_type": "electromagnetic",
                    "flow_l_min": 5,
                    "power_w": 50
                },
                "metabolic_system": {
                    "power_source": "lipo_battery_5kwh",
                    "efficiency_percent": 90,
                    "charging_hours": 2
                }
            },
            "bionic": {
                "skeletal_system": {
                    "material": "carbon_fiber_titanium",
                    "weight_kg": 50,
                    "osseo_integration": True,
                    "bio_compatible": True
                },
                "muscular_system": {
                    "organic_muscle_percent": 60,
                    "artificial_muscle_percent": 40,
                    "artificial_type": "electroactive_polymer"
                },
                "nervous_system": {
                    "neural_interface": "implantable_electrodes",
                    "bio_signal_processing": True,
                    "feedback_sensors": True
                },
                "cardiovascular_system": {
                    "organic_heart": True,
                    "assist_device": "vadc",
                    "bio_artificial_kidney": False
                },
                "metabolic_system": {
                    "organic_digestion": True,
                    "artificial_support": ["artificial_pancreas", "dialysis"]
                }
            },
            "organic": {
                "skeletal_system": {
                    "genetic_modifications": ["enhanced_density", "rapid_healing"],
                    "growth_method": "tissue_engineering",
                    "donor_cells": "iPSC_reprogrammed"
                },
                "muscular_system": {
                    "gene_therapy": ["myostatin_inhibition", "hypertrophy_boost"],
                    "cell_source": "autologous_stem_cells",
                    "vascularization": "3d_bioprinted"
                },
                "nervous_system": {
                    "brain_source": "stem_cell_differentiated",
                    "neural_connections": "synthetic_guidance",
                    "cognitive_enhancement": True
                },
                "cardiovascular_system": {
                    "heart_method": "bioartificial_or_cloned",
                    "vessel_engineering": "decellularization_recellularization"
                },
                "metabolic_system": {
                    "organ_source": ["3d_bioprinted", "xenotransplant"],
                    "immune_suppression": "gene_edited"
                }
            }
        }
        
        return templates
    
    def _save_templates(self, templates: Dict[str, Any]):
        """Сохранить шаблоны."""
        templates_file = self.data_dir / "design_templates.json"
        try:
            with open(templates_file, "w", encoding="utf-8") as f:
                json.dump(templates, f, ensure_ascii=False, indent=2)
        except Exception as e:
            logger.error(f"❌ Ошибка сохранения шаблонов: {e}")
    
    def create_body_specification(self, name: str, body_type: BodyType) -> BodySpecification:
        """
        Создать спецификацию тела.
        
        :param name: Имя проекта
        :param body_type: Тип тела
        :return: Спецификация тела
        """
        spec = BodySpecification(
            name=name,
            body_type=body_type,
            stage=DevelopmentStage.RESEARCH
        )
        
        # Добавление модулей
        for module_name, module in self.body_modules.items():
            spec.add_module(module)
        
        # Установка параметров по шаблону
        template_key = body_type.value
        if template_key in self.design_templates:
            spec.parameters = self.design_templates[template_key].copy()
        
        # Сохранение
        self.designed_bodies[name] = spec
        self._save_body_spec(spec)
        
        logger.info(f"📋 Спецификация создана: {name} ({body_type.value})")
        
        return spec
    
    def design_modules_for_body_type(self, spec: BodySpecification, body_type: BodyType) -> BodySpecification:
        """
        Спроектировать модули для типа тела.
        
        :param spec: Спецификация тела
        :param body_type: Тип тела
        :return: Обновлённая спецификация
        """
        template_key = body_type.value
        template = self.design_templates.get(template_key, {})
        
        for module_name, module_spec in template.items():
            if module_name in spec.modules:
                module = spec.modules[module_name]
                
                # Применение параметров шаблона
                module.design_status = "designed"
                module.body_types_supported.append(body_type)
                
                # Добавление вариантов
                variant = {
                    "body_type": body_type.value,
                    "parameters": module_spec,
                    "designed_at": time.time()
                }
                module.variants.append(variant)
                
                # Обновление прогресса на основе изученности
                learning_progress = self.learning_engine.topic_progress.get(module_name, 0.0)
                module.research_progress = min(1.0, learning_progress + 0.3)
        
        # Обновление стадии
        if spec.calculate_completeness() > 0.5:
            spec.stage = DevelopmentStage.DESIGN
        else:
            spec.stage = DevelopmentStage.RESEARCH
        
        spec.updated_at = time.time()
        self._save_body_spec(spec)
        
        logger.info(f"🎨 Модули спроектированы для {body_type.value}: {spec.name}")
        
        return spec
    
    def _save_body_spec(self, spec: BodySpecification):
        """Сохранить спецификацию тела."""
        spec_file = self.data_dir / f"{spec.name.replace(' ', '_')}.json"
        try:
            with open(spec_file, "w", encoding="utf-8") as f:
                json.dump(spec.to_dict(), f, ensure_ascii=False, indent=2)
        except Exception as e:
            logger.error(f"❌ Ошибка сохранения спецификации: {e}")
    
    def get_body_spec(self, name: str) -> Optional[BodySpecification]:
        """Получить спецификацию тела по имени."""
        return self.designed_bodies.get(name)
    
    def list_bodies(self) -> List[Dict[str, Any]]:
        """Список всех спроектированных тел."""
        return [spec.get_stats() for spec in self.designed_bodies.values()]
    
    def get_status(self) -> Dict[str, Any]:
        """Получить статус фабрики."""
        return {
            "bodies_count": len(self.designed_bodies),
            "bodies": self.list_bodies(),
            "templates_count": len(self.design_templates),
            "data_dir": str(self.data_dir)
        }
    
    def export_all_specs(self, output_dir: str) -> str:
        """Экспорт всех спецификаций."""
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        for name, spec in self.designed_bodies.items():
            spec_file = output_path / f"{name.replace(' ', '_')}.json"
            with open(spec_file, "w", encoding="utf-8") as f:
                json.dump(spec.to_dict(), f, ensure_ascii=False, indent=2)
        
        logger.info(f"📤 Экспортировано {len(self.designed_bodies)} спецификаций")
        return str(output_path)
