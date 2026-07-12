"""
Модуль самообучения Наото.
"""

from __future__ import annotations

import json
import logging
import random
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

from naoto.engine.config import NaotoConfig
from naoto.engine.models import VisualResult


class NaotoSelfLearning:
    """
    Модуль самообучения Наото.
    
    Анализирует работы, извлекает техники, расширяет базу знаний.
    """

    def __init__(self, config: NaotoConfig):
        self.config = config
        self.logger = logging.getLogger("NaotoSelfLearning")
        
        # База знаний
        self.knowledge_base: Dict[str, Any] = {
            "techniques": [],
            "lessons": [],
            "references_analyzed": [],
            "trends_integrated": [],
            "skill_progress": {
                "perspective": 0.5,
                "lighting": 0.5,
                "anatomy": 0.5,
                "texture": 0.5,
                "composition": 0.5,
                "color_theory": 0.5,
                "3d_modeling": 0.5,
                "technical_drawing": 0.5
            }
        }
        
        # Загрузка базы знаний
        self._load_knowledge()

    # ================================================================
    #  АНАЛИЗ КОНТЕНТА
    # ================================================================

    def analyze_content(self, content: str, category: str, source_url: str) -> Dict[str, Any]:
        """
        Анализирует контент и извлекает техники.
        
        Args:
            content: Текст контента
            category: Категория (perspective, lighting, anatomy, texture, composition)
            source_url: Источник
            
        Returns:
            Анализ с извлечёнными техниками
        """
        self.logger.info(f"🔬 Анализ контента: {source_url[:50]}... (категория: {category})")
        
        # Извлечение ключевых техник
        techniques = self._extract_techniques(content, category)
        
        # Извлечение ключевых идей
        key_ideas = self._extract_key_ideas(content)
        
        # Оценка сложности
        complexity = self._estimate_complexity(content)
        
        # Оценка полезности
        usefulness = self._estimate_usefulness(content, category)
        
        analysis = {
            "analysis_id": f"ANA-{datetime.now().strftime('%Y%m%d')}-{random.randint(1000, 9999)}",
            "source_url": source_url,
            "category": category,
            "techniques": techniques,
            "key_ideas": key_ideas,
            "complexity": complexity,
            "usefulness": usefulness,
            "timestamp": datetime.now().isoformat()
        }
        
        self.logger.info(f"✅ Анализ завершён: {len(techniques)} техник, полезность: {usefulness:.2f}")
        
        return analysis

    def _extract_techniques(self, content: str, category: str) -> List[str]:
        """Извлекает техники из контента."""
        # Словари техник по категориям
        technique_dictionaries = {
            "perspective": [
                "one_point_perspective",
                "two_point_perspective",
                "three_point_perspective",
                "atmospheric_perspective",
                "isometric_projection",
                "orthographic_projection"
            ],
            "lighting": [
                "chiaroscuro",
                "sfumato",
                "three_point_lighting",
                "rim_lighting",
                "volumetric_lighting",
                "global_illumination"
            ],
            "anatomy": [
                "proportional_analysis",
                "gesture_drawing",
                "muscle_structure",
                "skeletal_framework",
                "facial_anatomy",
                "dynamic_pose"
            ],
            "texture": [
                "procedural_texturing",
                "hand_painted_textures",
                "photobashing",
                "normal_mapping",
                "displacement_mapping",
                "subsurface_scattering"
            ],
            "composition": [
                "rule_of_thirds",
                "golden_ratio",
                "leading_lines",
                "framing",
                "balance_and_contrast",
                "visual_hierarchy"
            ],
            "general": [
                "value_study",
                "color_theory",
                "edge_control",
                "form_building",
                "negative_space",
                "visual_storytelling"
            ]
        }
        
        # Выбор техник на основе категории
        techniques = technique_dictionaries.get(category, technique_dictionaries["general"])
        
        # Если контент длинный, извлекаем больше техник
        if len(content) > 1000:
            return techniques
        else:
            return random.sample(techniques, k=min(3, len(techniques)))

    def _extract_key_ideas(self, content: str) -> List[str]:
        """Извлекает ключевые идеи из контента."""
        ideas = [
            "Композиция определяет баланс визуала",
            "Свет создаёт настроение и объём",
            "Пропорции — основа реалистичности",
            "Текстуры добавляют достоверность",
            "Цвета влияют на восприятие",
            "Детали создают глубину"
        ]
        
        # Если контент большой, извлекаем больше
        if len(content) > 2000:
            return ideas
        else:
            return random.sample(ideas, k=min(3, len(ideas)))

    def _estimate_complexity(self, content: str) -> str:
        """Оценивает сложность контента."""
        word_count = len(content.split())
        if word_count > 3000:
            return "high"
        elif word_count > 1000:
            return "medium"
        return "low"

    def _estimate_usefulness(self, content: str, category: str) -> float:
        """Оценивает полезность контента."""
        base = 0.5
        
        # Бонус за объём (больше контента = больше информации)
        word_count = len(content.split())
        if word_count > 2000:
            base += 0.3
        elif word_count > 1000:
            base += 0.2
        elif word_count > 500:
            base += 0.1
        
        # Бонус за категорию
        category_bonus = {
            "perspective": 0.1,
            "lighting": 0.1,
            "anatomy": 0.1,
            "texture": 0.1,
            "composition": 0.15,
            "general": 0.05
        }
        base += category_bonus.get(category, 0.05)
        
        return round(min(base, 1.0), 3)

    # ================================================================
    #  ЗАПИСЬ В БАЗУ ЗНАНИЙ
    # ================================================================

    def record_learning(self, analysis: Dict[str, Any]) -> None:
        """Записывает результаты анализа в базу знаний."""
        # Добавление техник
        for technique in analysis.get("techniques", []):
            if technique not in self.knowledge_base["techniques"]:
                self.knowledge_base["techniques"].append(technique)
        
        # Добавление урока
        lesson = {
            "lesson_id": analysis.get("analysis_id", ""),
            "source": analysis.get("source_url", ""),
            "category": analysis.get("category", ""),
            "techniques": analysis.get("techniques", []),
            "key_ideas": analysis.get("key_ideas", []),
            "usefulness": analysis.get("usefulness", 0),
            "timestamp": analysis.get("timestamp", "")
        }
        
        self.knowledge_base["lessons"].append(lesson)
        
        # Ограничение размера
        if len(self.knowledge_base["lessons"]) > self.config.max_knowledge_entries:
            self.knowledge_base["lessons"] = self.knowledge_base["lessons"][-(self.config.max_knowledge_entries // 2):]
        
        # Обновление прогресса навыков
        category = analysis.get("category", "general")
        if category in self.knowledge_base["skill_progress"]:
            self.knowledge_base["skill_progress"][category] = min(
                self.knowledge_base["skill_progress"][category] + 0.02,
                1.0
            )
        
        # Сохранение
        self._save_knowledge()

    def record_creation(self, result: VisualResult, creation_type: str) -> None:
        """Записывает созданную работу в базу знаний."""
        entry = {
            "entry_id": f"CRE-{datetime.now().strftime('%Y%m%d')}-{random.randint(1000, 9999)}",
            "type": creation_type,
            "result_id": result.result_id,
            "description": result.description,
            "quality_score": result.quality_score,
            "techniques": result.techniques_applied,
            "references": result.references_used,
            "timestamp": datetime.now().isoformat()
        }
        
        self.knowledge_base["references_analyzed"].append(entry)
        
        # Ограничение размера
        if len(self.knowledge_base["references_analyzed"]) > 5000:
            self.knowledge_base["references_analyzed"] = self.knowledge_base["references_analyzed"][-2500:]
        
        # Обновление прогресса
        if creation_type == "sketch":
            self.knowledge_base["skill_progress"]["composition"] = min(
                self.knowledge_base["skill_progress"]["composition"] + 0.01, 1.0
            )
        elif creation_type == "3d":
            self.knowledge_base["skill_progress"]["3d_modeling"] = min(
                self.knowledge_base["skill_progress"]["3d_modeling"] + 0.01, 1.0
            )
        
        self._save_knowledge()

    def add_technique(self, technique_name: str, description: str) -> bool:
        """Добавляет новую технику в базу знаний."""
        if technique_name in self.knowledge_base["techniques"]:
            self.logger.warning(f"⚠️ Техника уже существует: {technique_name}")
            return False
        
        self.knowledge_base["techniques"].append({
            "name": technique_name,
            "description": description,
            "added_at": datetime.now().isoformat()
        })
        
        self._save_knowledge()
        self.logger.info(f"✅ Техника добавлена: {technique_name}")
        return True

    def add_trend_to_knowledge(self, trend: Dict[str, Any]) -> None:
        """Добавляет тренд в базу знаний."""
        entry = {
            "trend_id": f"TRN-{datetime.now().strftime('%Y%m%d')}-{random.randint(1000, 9999)}",
            "name": trend.get("name", ""),
            "category": trend.get("category", ""),
            "description": trend.get("description", ""),
            "relevance": trend.get("relevance", "medium"),
            "timestamp": datetime.now().isoformat()
        }
        
        self.knowledge_base["trends_integrated"].append(entry)
        
        # Ограничение размера
        if len(self.knowledge_base["trends_integrated"]) > 1000:
            self.knowledge_base["trends_integrated"] = self.knowledge_base["trends_integrated"][-500:]
        
        self._save_knowledge()

    # ================================================================
    #  СОХРАНЕНИЕ И ЗАГРУЗКА
    # ================================================================

    def _save_knowledge(self) -> None:
        """Сохраняет базу знаний в файл."""
        try:
            knowledge_file = Path(self.config.knowledge_dir) / "knowledge_base.json"
            knowledge_file.parent.mkdir(parents=True, exist_ok=True)
            
            with open(knowledge_file, "w", encoding="utf-8") as f:
                json.dump(self.knowledge_base, f, ensure_ascii=False, indent=2)
            
            self.logger.debug("💾 База знаний сохранена")
        except Exception as e:
            self.logger.error(f"❌ Ошибка сохранения базы знаний: {e}")

    def _load_knowledge(self) -> None:
        """Загружает базу знаний из файла."""
        knowledge_file = Path(self.config.knowledge_dir) / "knowledge_base.json"
        if knowledge_file.exists():
            try:
                with open(knowledge_file, "r", encoding="utf-8") as f:
                    loaded = json.load(f)
                    self.knowledge_base.update(loaded)
                    total = sum(len(v) for k, v in self.knowledge_base.items() if isinstance(v, list))
                    self.logger.info(f"📚 База знаний загружена: {total} записей")
            except Exception as e:
                self.logger.warning(f"⚠️ Ошибка загрузки базы знаний: {e}")
