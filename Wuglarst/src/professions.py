"""
Модуль анализа профессий (классификация по предмету труда).
Поддержка категорий: Человек-Человек, Человек-Природа, Человек-Техника и т.д.
"""

import json
import os
import re
import logging
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field


@dataclass
class ProfessionAnalysis:
    """Результат анализа профессии."""
    detected_professions: List[str] = field(default_factory=list)
    detected_category: Optional[str] = None
    confidence: float = 0.0
    matched_keywords: List[str] = field(default_factory=list)
    description: Optional[str] = None

    def to_log(self) -> str:
        if self.detected_professions:
            return f"professions={','.join(self.detected_professions[:3])} (cat={self.detected_category})"
        return "professions=none"


class ProfessionEngine:
    """Двигатель анализа профессий."""

    def __init__(self, data_dir: str = "data"):
        self.data_dir = data_dir
        self.professions_data: Dict[str, Any] = {}
        self._load_professions()

    def _load_professions(self):
        """Загружает данные о профессиях из JSON файлов."""
        # Ищем все файлы профессий
        try:
            config_path = os.path.join(self.data_dir, "config.yaml")
            if not os.path.exists(config_path):
                logging.warning("⚠️ config.yaml не найден — профессии не загружены")
                return

            # Простой парсинг для получения списка файлов (без PyYAML для простоты)
            # Или используем загруженный конфиг
            import yaml
            with open(config_path, "r", encoding="utf-8") as f:
                config = yaml.safe_load(f)

            profession_files = config.get("professions", [])
            for prof_config in profession_files:
                filename = prof_config.get("filename", "")
                category = prof_config.get("category", "Unknown")
                filepath = os.path.join(self.data_dir, filename)

                if os.path.exists(filepath):
                    with open(filepath, "r", encoding="utf-8") as f:
                        data = json.load(f)
                        self.professions_data[category] = data
                        logging.info(f"📚 Загружена категория профессий: {category}")
                else:
                    logging.warning(f"⚠️ Файл профессий не найден: {filepath}")

        except ImportError:
            logging.warning("⚠️ PyYAML не установлен — профессии не будут загружены автоматически")
        except Exception as e:
            logging.error(f"❌ Ошибка загрузки профессий: {e}")

    def analyze(self, user_message: str) -> ProfessionAnalysis:
        """Анализирует сообщение на наличие профессий."""
        result = ProfessionAnalysis()
        text_lower = user_message.lower()

        all_keywords = []
        all_descriptions = []

        for category, data in self.professions_data.items():
            subcategories = data.get("subcategories", {})
            description = data.get("description", "")

            for subcat, jobs in subcategories.items():
                for job in jobs:
                    # Проверяем точное совпадение или частичное
                    if job.lower() in text_lower:
                        result.detected_professions.append(job)
                        result.matched_keywords.append(job)
                        all_keywords.append(job)

            if result.detected_professions:
                result.detected_category = category
                result.description = description
                result.confidence = min(0.5 + len(result.detected_professions) * 0.2, 1.0)

        return result

    def get_profession_summary(self) -> Dict[str, Any]:
        """Возвращает сводку по загруженным профессиям."""
        return {
            "loaded_categories": list(self.professions_data.keys()),
            "total_categories": len(self.professions_data),
            "details": {
                cat: {
                    "description": data.get("description", ""),
                    "subcategories": list(data.get("subcategories", {}).keys())
                }
                for cat, data in self.professions_data.items()
            }
        }
