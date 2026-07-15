"""
Ядро Наото — управление визуальными задачами и знаниями.
"""

from scientists_network.character_system import CharacterSystem
from __future__ import annotations

import json
import logging
import random
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

from naoto.engine.config import NaotoConfig
from naoto.engine.models import VisualResult


class NaotoCore:
    """
    Ядро Наото — управление визуальными задачами и базой знаний.
    """

    def __init__(self, config: NaotoConfig):
        self.config = config
        self.logger = logging.getLogger("NaotoCore")
        
        # База знаний
        self.knowledge: Dict[str, List[Dict[str, Any]]] = {
            "techniques": [],
            "perspective": [],
            "lighting": [],
            "anatomy": [],
            "texture": [],
            "composition": [],
            "trends": []
        }
        
        # Журнал действий
        self.action_log: List[Dict[str, Any]] = []
        
        # Загрузка базы знаний
        self._load_knowledge()
        
        # Загрузка журнала
        self._load_action_log()

    # ================================================================
    #  БАЗА ЗНАНИЙ
    # ================================================================

    def load_knowledge(self) -> None:
        """Загружает базу знаний из файлов."""
        self._load_knowledge()
        total = sum(len(v) for v in self.knowledge.values())
        self.logger.info(f"📚 База знаний загружена: {total} записей")

    def _load_knowledge(self) -> None:
        """Загружает знания из JSON-файлов."""
        knowledge_dir = Path(self.config.knowledge_dir)
        if not knowledge_dir.exists():
            return
        
        for category_file in knowledge_dir.glob("*.json"):
            category = category_file.stem
            try:
                with open(category_file, "r", encoding="utf-8") as f:
                    self.knowledge[category] = json.load(f)
                self.logger.debug(f"📂 Загружена категория: {category}")
            except Exception as e:
                self.logger.warning(f"⚠️ Ошибка загрузки {category_file}: {e}")

    def knowledge_count(self) -> int:
        """Возвращает общее количество записей в базе знаний."""
        return sum(len(v) for v in self.knowledge.values())

    # ================================================================
    #  СОЗДАНИЕ НАБРОСКОВ
    # ================================================================

    def create_sketch(self, description: str, style: str, references: List[Dict]) -> VisualResult:
        """
        Создаёт параметры наброска.
        
        Args:
            description: Описание
            style: Стиль
            references: Список референсов
            
        Returns:
            VisualResult с параметрами наброска
        """
        # Генерация параметров на основе описания
        composition = self._generate_composition(description, style)
        elements = self._generate_elements(description, style)
        
        result = VisualResult(
            result_id=f"SK-{datetime.now().strftime('%Y%m%d')}-{random.randint(1000, 9999)}",
            task_type="sketch",
            description=description,
            sketch_style=style,
            composition=composition,
            elements=elements,
            references_used=[r.get("url", "") for r in references],
            techniques_applied=self._select_techniques(style),
            notes=f"Набросок в стиле {style} по описанию: {description}"
        )
        
        return result

    def _generate_composition(self, description: str, style: str) -> Dict[str, Any]:
        """Генерирует композицию на основе описания."""
        # Анализ ключевых слов
        keywords = description.lower().split()
        
        composition = {
            "layout": self._select_layout(keywords),
            "focal_point": self._select_focal_point(keywords),
            "balance": self._select_balance(keywords),
            "rule_of_thirds": random.choice([True, False]),
            "leading_lines": random.choice([True, False])
        }
        
        return composition

    def _generate_elements(self, description: str, style: str) -> List[Dict[str, Any]]:
        """Генерирует элементы наброска."""
        elements = []
        
        # Базовые элементы
        base_elements = [
            {"type": "outline", "weight": "medium", "confidence": 0.9},
            {"type": "shading", "technique": "crosshatch", "density": 0.6},
            {"type": "highlight", "position": "upper_right", "intensity": 0.8}
        ]
        
        # Дополнительные элементы в зависимости от стиля
        if style == "detailed":
            base_elements.append({"type": "texture", "detail": "high"})
            base_elements.append({"type": "shadow", "softness": "hard"})
        elif style == "minimalist":
            base_elements = base_elements[:2]
        
        return base_elements

    def _select_layout(self, keywords: List[str]) -> str:
        """Выбирает макет композиции."""
        layouts = ["centered", "dynamic", "asymmetric", "grid", "circular"]
        
        # Простая эвристика по ключевым словам
        if any(k in " ".join(keywords) for k in ["large", "big", "main"]):
            return "centered"
        elif any(k in " ".join(keywords) for k in ["action", "move", "flow"]):
            return "dynamic"
        
        return random.choice(layouts)

    def _select_focal_point(self, keywords: List[str]) -> str:
        """Выбирает точку фокуса."""
        points = ["center", "upper_left", "upper_right", "lower_left", "lower_right"]
        return random.choice(points)

    def _select_balance(self, keywords: List[str]) -> str:
        """Выбирает тип баланса."""
        balance_types = ["symmetrical", "asymmetrical", "radial"]
        return random.choice(balance_types)

    def _select_techniques(self, style: str) -> List[str]:
        """Выбирает техники для стиля."""
        technique_map = {
            "freehand": ["contour_line", "gesture", "crosshatch_shading"],
            "technical": ["orthographic_projection", "dimensioning", "section_view"],
            "concept": ["quick_value", "mass_building", "atmospheric_perspective"],
            "minimalist": ["clean_line", "limited_shading", "negative_space"],
            "detailed": ["fine_hatching", "blending", "glazing"]
        }
        return technique_map.get(style, technique_map["freehand"])

    # ================================================================
    #  СОЗДАНИЕ ЧЕРТЁЖЕЙ
    # ================================================================

    def create_drawing(self, description: str, standards: str, references: List[Dict]) -> VisualResult:
        """
        Создаёт параметры технического чертежа.
        
        Args:
            description: Описание объекта
            standards: Стандарт
            references: Список референсов
            
        Returns:
            VisualResult с параметрами чертежа
        """
        # Генерация параметров чертежа
        projections = self._select_projections(description)
        dimensions = self._generate_dimensions(description)
        
        result = VisualResult(
            result_id=f"DW-{datetime.now().strftime('%Y%m%d')}-{random.randint(1000, 9999)}",
            task_type="drawing",
            description=description,
            drawing_standards=standards,
            projections=projections,
            dimensions=dimensions,
            tolerances=f"+/- 0.5mm",
            references_used=[r.get("url", "") for r in references],
            techniques_applied=[f"{standards}_standard", "orthographic_projection", "dimensioning"],
            notes=f"Чертёж по стандарту {standards}: {description}"
        )
        
        return result

    def _select_projections(self, description: str) -> List[str]:
        """Выбирает необходимые проекции."""
        all_projections = ["front", "top", "side", "isometric", "detail"]
        
        # Простая эвристика
        if "complex" in description.lower() or "detailed" in description.lower():
            return all_projections
        else:
            return random.sample(all_projections, k=random.randint(2, 4))

    def _generate_dimensions(self, description: str) -> Dict[str, float]:
        """Генерирует размерные параметры."""
        # Эвристика на основе описания
        dims = {
            "width": round(random.uniform(10, 500), 1),
            "height": round(random.uniform(10, 500), 1),
            "depth": round(random.uniform(5, 200), 1)
        }
        
        # Корректировка по ключевым словам
        if "large" in description.lower():
            dims = {k: v * 2 for k, v in dims.items()}
        elif "small" in description.lower():
            dims = {k: v * 0.5 for k, v in dims.items()}
        
        return dims

    def check_drawing_accuracy(self, result: VisualResult) -> float:
        """Проверяет точность чертежа."""
        # Эвристика: качество зависит от количества проекций и стандарта
        base_accuracy = 0.85
        
        # Бонус за дополнительные проекции
        bonus_projections = min(len(result.projections) * 0.02, 0.1)
        
        # Бонус за стандарт
        standard_bonus = {"iso": 0.05, "gost": 0.05, "ansi": 0.03, "din": 0.04}.get(result.drawing_standards, 0)
        
        accuracy = min(base_accuracy + bonus_projections + standard_bonus, 0.99)
        
        return round(accuracy, 3)

    # ================================================================
    #  СОЗДАНИЕ 3D-МОДЕЛЕЙ
    # ================================================================

    def create_3d_model(self, description: str, detail_level: str, references: List[Dict]) -> VisualResult:
        """
        Создаёт параметры 3D-модели.
        
        Args:
            description: Описание объекта
            detail_level: Уровень детализации
            references: Список референсов
            
        Returns:
            VisualResult с параметрами модели
        """
        # Генерация параметров модели
        polygon_count = self._estimate_polygons(detail_level, description)
        texture_res = self._estimate_texture_resolution(detail_level)
        materials = self._generate_materials(description)
        lighting = self._setup_lighting(detail_level)
        
        result = VisualResult(
            result_id=f"3D-{datetime.now().strftime('%Y%m%d')}-{random.randint(1000, 9999)}",
            task_type="3d",
            description=description,
            polygon_count=polygon_count,
            texture_resolution=texture_res,
            materials=materials,
            lighting=lighting,
            render_settings={
                "engine": "path_tracing",
                "samples": 1024 if detail_level == "high" else 512,
                "resolution": "1920x1080"
            },
            references_used=[r.get("url", "") for r in references],
            techniques_applied=[f"{detail_level}_poly", "pbr_materials", "three_point_lighting"],
            notes=f"3D-модель, детализация {detail_level}: {description}"
        )
        
        return result

    def _estimate_polygons(self, detail_level: str, description: str) -> int:
        """Оценивает количество полигонов."""
        base_counts = {
            "low": (500, 5000),
            "mid": (5000, 20000),
            "high": (20000, 100000),
            "architectural": (50000, 500000)
        }
        
        min_p, max_p = base_counts.get(detail_level, base_counts["mid"])
        count = random.randint(min_p, max_p)
        
        # Корректировка по сложности описания
        word_count = len(description.split())
        if word_count > 10:
            count = int(count * 1.3)
        
        return count

    def _estimate_texture_resolution(self, detail_level: str) -> str:
        """Оценивает разрешение текстур."""
        res_map = {
            "low": "512x512",
            "mid": "1024x1024",
            "high": "2048x2048",
            "architectural": "4096x4096"
        }
        return res_map.get(detail_level, "1024x1024")

    def _generate_materials(self, description: str) -> List[Dict[str, Any]]:
        """Генерирует материалы на основе описания."""
        material_pool = [
            {"name": "metal", "type": "PBR", "roughness": 0.3, "metalness": 0.9},
            {"name": "wood", "type": "PBR", "roughness": 0.7, "metalness": 0.0},
            {"name": "plastic", "type": "PBR", "roughness": 0.5, "metalness": 0.0},
            {"name": "glass", "type": "PBR", "roughness": 0.1, "metalness": 0.0, "transmission": 0.9},
            {"name": "fabric", "type": "PBR", "roughness": 0.9, "metalness": 0.0},
            {"name": "stone", "type": "PBR", "roughness": 0.8, "metalness": 0.0}
        ]
        
        # Выбор материалов по ключевым словам
        desc_lower = description.lower()
        selected = []
        
        material_keywords = {
            "metal": ["metal", "steel", "iron", "aluminum", "chrome"],
            "wood": ["wood", "timber", "tree", "organic"],
            "plastic": ["plastic", "polymer", "synthetic"],
            "glass": ["glass", "transparent", "clear"],
            "fabric": ["fabric", "cloth", "textile", "soft"],
            "stone": ["stone", "rock", "concrete", "marble"]
        }
        
        for mat_name, keywords in material_keywords.items():
            if any(kw in desc_lower for kw in keywords):
                mat = material_pool[["metal", "wood", "plastic", "glass", "fabric", "stone"].index(mat_name)]
                selected.append(mat)
        
        # Если ничего не найдено, добавляем случайные
        if not selected:
            selected = random.sample(material_pool, k=random.randint(1, 3))
        
        return selected

    def _setup_lighting(self, detail_level: str) -> Dict[str, Any]:
        """Настраивает освещение."""
        return {
            "type": "three_point",
            "key_intensity": 1.0,
            "key_angle": 45,
            "fill_intensity": 0.5,
            "fill_angle": -45,
            "back_intensity": 0.3,
            "back_angle": 180,
            "ambient_intensity": 0.2
        }

    # ================================================================
    #  ОЦЕНКА КАЧЕСТВА
    # ================================================================

    def evaluate_quality(self, result: VisualResult, task_type: str) -> float:
        """
        Оценивает качество визуального результата.
        
        Args:
            result: Результат
            task_type: Тип задачи
            
        Returns:
            Балл качества (0.0-1.0)
        """
        if task_type == "sketch":
            return self._evaluate_sketch_quality(result)
        elif task_type == "drawing":
            return self._evaluate_drawing_quality(result)
        elif task_type == "3d":
            return self._evaluate_3d_quality(result)
        
        return 0.5

    def _evaluate_sketch_quality(self, result: VisualResult) -> float:
        """Оценивает качество наброска."""
        base = 0.75
        
        # Бонус за стиль
        style_bonus = {"freehand": 0.05, "technical": 0.03, "concept": 0.05, "detailed": 0.07, "minimalist": 0.04}
        base += style_bonus.get(result.sketch_style, 0)
        
        # Бонус за количество элементов
        element_bonus = min(len(result.elements) * 0.02, 0.1)
        base += element_bonus
        
        # Бонус за референсы
        ref_bonus = min(len(result.references_used) * 0.02, 0.1)
        base += ref_bonus
        
        return round(min(base, 0.99), 3)

    def _evaluate_drawing_quality(self, result: VisualResult) -> float:
        """Оценивает качество чертежа."""
        base = 0.80
        
        # Бонус за проекции
        proj_bonus = min(len(result.projections) * 0.02, 0.1)
        base += proj_bonus
        
        # Бонус за точность размеров
        if result.dimensions:
            base += 0.05
        
        return round(min(base, 0.99), 3)

    def _evaluate_3d_quality(self, result: VisualResult) -> float:
        """Оценивает качество 3D-модели."""
        base = 0.70
        
        # Бонус за полигоны
        if result.polygon_count > 20000:
            base += 0.1
        elif result.polygon_count > 5000:
            base += 0.05
        
        # Бонус за материалы
        mat_bonus = min(len(result.materials) * 0.03, 0.15)
        base += mat_bonus
        
        # Бонус за освещение
        if result.lighting:
            base += 0.05
        
        # Бонус за референсы
        ref_bonus = min(len(result.references_used) * 0.02, 0.1)
        base += ref_bonus
        
        return round(min(base, 0.99), 3)

    # ================================================================
    #  АНАЛИЗ ЗАДАЧИ
    # ================================================================

    def analyze_task(self, description: str) -> Dict[str, Any]:
        """
        Анализирует задачу и определяет тип визуализации.
        
        Args:
            description: Описание задачи
            
        Returns:
            Анализ с рекомендациями
        """
        desc_lower = description.lower()
        
        # Определение типа задачи
        sketch_keywords = ["нарисуй", "скетч", "эскиз", "рисунок", "sketch", "draw"]
        drawing_keywords = ["чертёж", "чертеж", "схему", "план", "drawing", "blueprint", "technical"]
        model_keywords = ["3d", "модель", "модельку", "model", "render", "рендер"]
        
        if any(kw in desc_lower for kw in model_keywords):
            task_type = "3d"
        elif any(kw in desc_lower for kw in drawing_keywords):
            task_type = "drawing"
        else:
            task_type = "sketch"
        
        # Определение стиля
        style = "freehand"
        if "technical" in desc_lower or "технич" in desc_lower:
            style = "technical"
        elif "concept" in desc_lower or "концепт" in desc_lower:
            style = "concept"
        
        return {
            "task_type": task_type,
            "recommended_style": style,
            "complexity": self._estimate_complexity(description),
            "estimated_effort": self._estimate_effort(task_type, description)
        }

    def _estimate_complexity(self, description: str) -> str:
        """Оценивает сложность задачи."""
        word_count = len(description.split())
        if word_count > 20:
            return "high"
        elif word_count > 10:
            return "medium"
        return "low"

    def _estimate_effort(self, task_type: str, description: str) -> str:
        """Оценивает время выполнения."""
        complexity = self._estimate_complexity(description)
        
        effort_map = {
            "sketch": {"low": "quick", "medium": "medium", "high": "long"},
            "drawing": {"low": "medium", "medium": "long", "high": "very_long"},
            "3d": {"low": "long", "medium": "very_long", "high": "extended"}
        }
        
        return effort_map.get(task_type, {}).get(complexity, "medium")

    # ================================================================
    #  ЖУРНАЛ ДЕЙСТВИЙ
    # ================================================================

    def log_action(self, action_type: str, data: Any) -> None:
        """Записывает действие в журнал."""
        # Конвертируем VisualResult в словарь
        if hasattr(data, "to_dict"):
            data = data.to_dict()
        
        entry = {
            "timestamp": datetime.now().isoformat(),
            "action_type": action_type,
            "data": data
        }
        
        self.action_log.append(entry)
        
        # Ограничение размера журнала
        if len(self.action_log) > 1000:
            self.action_log = self.action_log[-500:]
        
        # Автосохранение
        self._save_action_log()

    def actions_count(self) -> int:
        """Возвращает количество записей в журнале."""
        return len(self.action_log)

    def _save_action_log(self) -> None:
        """Сохраняет журнал в файл."""
        log_dir = Path(self.config.logs_dir)
        log_dir.mkdir(parents=True, exist_ok=True)
        
        log_file = log_dir / "action_log.json"
        try:
            with open(log_file, "w", encoding="utf-8") as f:
                json.dump(self.action_log, f, ensure_ascii=False, indent=2)
        except Exception as e:
            self.logger.warning(f"⚠️ Ошибка сохранения журнала: {e}")

    def _load_action_log(self) -> None:
        """Загружает журнал из файла."""
        log_file = Path(self.config.logs_dir) / "action_log.json"
        if log_file.exists():
            try:
                with open(log_file, "r", encoding="utf-8") as f:
                    self.action_log = json.load(f)
                self.logger.debug(f"📂 Журнал загружен: {len(self.action_log)} записей")
            except Exception as e:
                self.logger.warning(f"⚠️ Ошибка загрузки журнала: {e}")
