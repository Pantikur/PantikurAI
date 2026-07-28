#!/usr/bin/env python3
"""
Айко AI — Система Продвинутых Навыков и Техник

Профессиональная система навыков с:
  🎨 15+ художественными техниками
  📊 Система прогрессии от новичка до мастера
  🧠 Адаптивное обучение на примерах
  🌈 Профессиональная цветовая теория
  📐 Композиция и золотое сечение
  💡 Светотень и объём
  ✨ Спецэффекты и постобработка
"""

import json
import random
import math
from pathlib import Path
from typing import Dict, List, Tuple, Optional
from datetime import datetime


class AyikoSkillSystem:
    """
    Система профессиональных навыков Айко.
    
    Навыки делятся на категории:
      - Художественные техники (1-10)
      - Теоретические знания (1-10)
      - Специализации (1-10)
      - Эффекты и постобработка (1-10)
    """
    
    def __init__(self, base_dir: str = "data/ayiko/skills"):
        self.base_dir = Path(base_dir)
        self.base_dir.mkdir(parents=True, exist_ok=True)
        
        # Загружаем навыки или создаём новые
        self.skills = self._load_skills()
        
        # История обучения
        self.training_log = self._load_training_log()
        
        # Специализации
        self.specializations = {
            "pixel_art": {
                "name": "Пиксель-арт Мастер",
                "level": 0,
                "techniques": ["dithering", "anti_aliasing", "palette_optimization", "animation"]
            },
            "character_design": {
                "name": "Дизайн Персонажей",
                "level": 0,
                "techniques": ["anatomy", "proportions", "expression", "costume_design"]
            },
            "landscape": {
                "name": "Мастер Пейзажей",
                "level": 0,
                "techniques": ["atmospheric_perspective", "lighting", "weather_effects", "composition"]
            },
            "technical": {
                "name": "Техническая Графика",
                "level": 0,
                "techniques": ["blueprint", "isometric", "orthographic", "rendering"]
            },
            "portrait": {
                "name": "Портретист",
                "level": 0,
                "techniques": ["facial_features", "skin_texture", "eye_detail", "hair_rendering"]
            }
        }
        
        print("Skill System initialized")
    
    def _load_skills(self) -> Dict:
        """Загружает навыки из файла"""
        file = self.base_dir / "skills.json"
        if file.exists():
            try:
                with open(file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    print(f"   📚 Загружено {len(data)} навыков")
                    return data
            except:
                pass
        
        # Создаём базовые навыки
        return self._create_default_skills()
    
    def _create_default_skills(self) -> Dict:
        """Создаёт начальные навыки"""
        skills = {
            # Художественные техники
            "pixel_art": {
                "name": "Пиксель-арт",
                "category": "technique",
                "level": 8,
                "experience": 800,
                "techniques_mastered": ["basic_pixels", "color_palette", "shading"],
                "techniques_learning": ["dithering", "anti_aliasing"]
            },
            "watercolor": {
                "name": "Акварель",
                "category": "technique",
                "level": 6,
                "experience": 600,
                "techniques_mastered": ["wet_on_wet", "color_mixing"],
                "techniques_learning": ["glazing", "lifting"]
            },
            "oil_painting": {
                "name": "Масляная живопись",
                "category": "technique",
                "level": 7,
                "experience": 700,
                "techniques_mastered": ["layering", "impasto"],
                "techniques_learning": ["glazing", "scumbling"]
            },
            "charcoal": {
                "name": "Угольный рисунок",
                "category": "technique",
                "level": 5,
                "experience": 500,
                "techniques_mastered": ["blending"],
                "techniques_learning": ["hatching", "stumping"]
            },
            "pencil": {
                "name": "Карандаш",
                "category": "technique",
                "level": 9,
                "experience": 900,
                "techniques_mastered": ["shading", "line_work", "texture"],
                "techniques_learning": ["cross_hatching"]
            },
            
            # Теоретические знания
            "color_theory": {
                "name": "Теория Цвета",
                "category": "theory",
                "level": 9,
                "experience": 900,
                "knowledge_areas": ["complementary", "analogous", "triadic", "split_complementary"]
            },
            "composition": {
                "name": "Композиция",
                "category": "theory",
                "level": 8,
                "experience": 800,
                "knowledge_areas": ["rule_of_thirds", "golden_ratio", "symmetry", "balance"]
            },
            "anatomy": {
                "name": "Анатомия",
                "category": "theory",
                "level": 8,
                "experience": 800,
                "knowledge_areas": ["skeletal", "muscular", "proportions", "movement"]
            },
            "lighting": {
                "name": "Свет и Тень",
                "category": "theory",
                "level": 7,
                "experience": 700,
                "knowledge_areas": ["chiaroscuro", "rim_light", "volumetric", "ambient"]
            },
            
            # Специализации
            "character_design": {
                "name": "Дизайн Персонажей",
                "category": "specialization",
                "level": 9,
                "experience": 900,
                "sub_skills": ["expression", "pose", "costume", "silhouette"]
            },
            "landscape": {
                "name": "Пейзаж",
                "category": "specialization",
                "level": 7,
                "experience": 700,
                "sub_skills": ["nature", "architecture", "weather", "time_of_day"]
            },
            "technical_drawing": {
                "name": "Техническая Графика",
                "category": "specialization",
                "level": 6,
                "experience": 600,
                "sub_skills": ["blueprint", "isometric", "orthographic", "assembly"]
            }
        }
        
        self._save_skills(skills)
        return skills
    
    def _save_skills(self, skills: Dict):
        """Сохраняет навыки"""
        file = self.base_dir / "skills.json"
        with open(file, "w", encoding="utf-8") as f:
            json.dump(skills, f, ensure_ascii=False, indent=2)
    
    def _load_training_log(self) -> List[Dict]:
        """Загружает историю обучения"""
        file = self.base_dir / "training_log.json"
        if file.exists():
            try:
                with open(file, "r", encoding="utf-8") as f:
                    return json.load(f)
            except:
                return []
        return []
    
    def _save_training_log(self, log: List[Dict]):
        """Сохраняет историю обучения"""
        file = self.base_dir / "training_log.json"
        with open(file, "w", encoding="utf-8") as f:
            json.dump(log, f, ensure_ascii=False, indent=2)
    
    def train_skill(self, skill_name: str, practice_hours: float, quality: float = 1.0):
        """
        Тренирует навык
        
        Args:
            skill_name: Название навыка
            practice_hours: Часы практики
            quality: Качество практики (0-1)
        """
        if skill_name not in self.skills:
            print(f"   ⚠️ Навык '{skill_name}' не найден")
            return
        
        skill = self.skills[skill_name]
        
        # Рассчитываем опыт
        base_xp = practice_hours * 50
        quality_bonus = 1 + quality * 0.5
        
        # Бонус за разнообразие практики
        diversity_bonus = 1.0
        if skill.get("techniques_learning"):
            diversity_bonus += 0.2
        
        gained_xp = base_xp * quality_bonus * diversity_bonus
        skill["experience"] = skill.get("experience", 0) + gained_xp
        
        # Проверка повышения уровня
        xp_for_level = skill["level"] * 100
        if skill["experience"] >= xp_for_level and skill["level"] < 10:
            old_level = skill["level"]
            skill["level"] += 1
            print(f"   🎉 Навык '{skill_name}' повышен с {old_level} до {skill['level']}!")
            
            # Разблокируем техники
            if skill["level"] % 2 == 0 and "techniques_learning" in skill:
                new_tech = skill["techniques_learning"].pop(0)
                skill["techniques_mastered"].append(new_tech)
                print(f"   🔓 Освоена техника: {new_tech}")
        
        # Логирование
        entry = {
            "skill": skill_name,
            "hours": practice_hours,
            "quality": quality,
            "xp_gained": gained_xp,
            "new_level": skill["level"],
            "timestamp": datetime.now().isoformat()
        }
        
        self.training_log.append(entry)
        self._save_training_log(self.training_log)
        self._save_skills(self.skills)
    
    def get_skill_level(self, skill_name: str) -> int:
        """Получает уровень навыка"""
        if skill_name in self.skills:
            return self.skills[skill_name].get("level", 1)
        return 1
    
    def get_skill_info(self, skill_name: str) -> Dict:
        """Получает информацию о навыке"""
        if skill_name in self.skills:
            return self.skills[skill_name]
        return {}
    
    def get_mastered_techniques(self, skill_name: str) -> List[str]:
        """Получает освоенные техники навыка"""
        if skill_name in self.skills:
            return self.skills[skill_name].get("techniques_mastered", [])
        return []
    
    def get_average_skill(self) -> float:
        """Средний уровень всех навыков"""
        if not self.skills:
            return 0
        total = sum(s.get("level", 1) for s in self.skills.values())
        return total / len(self.skills)
    
    def get_skill_summary(self) -> Dict:
        """Сводка всех навыков"""
        return {
            "total_skills": len(self.skills),
            "average_level": round(self.get_average_skill(), 1),
            "skills": {name: {
                "name": info.get("name", name),
                "level": info.get("level", 1),
                "experience": info.get("experience", 0),
                "category": info.get("category", "unknown")
            } for name, info in self.skills.items()},
            "mastered_techniques": {name: self.get_mastered_techniques(name) 
                                   for name in self.skills}
        }
    
    def analyze_training_efficiency(self) -> Dict:
        """Анализирует эффективность обучения"""
        if not self.training_log:
            return {"message": "Нет данных для анализа"}
        
        total_hours = sum(entry["hours"] for entry in self.training_log)
        total_xp = sum(entry["xp_gained"] for entry in self.training_log)
        avg_quality = sum(entry["quality"] for entry in self.training_log) / len(self.training_log)
        
        # Эффективность по навыкам
        skill_efficiency = {}
        for entry in self.training_log:
            skill = entry["skill"]
            if skill not in skill_efficiency:
                skill_efficiency[skill] = {"hours": 0, "xp": 0, "count": 0}
            skill_efficiency[skill]["hours"] += entry["hours"]
            skill_efficiency[skill]["xp"] += entry["xp_gained"]
            skill_efficiency[skill]["count"] += 1
        
        for skill in skill_efficiency:
            skill_efficiency[skill]["avg_xp_per_hour"] = (
                skill_efficiency[skill]["xp"] / skill_efficiency[skill]["hours"]
                if skill_efficiency[skill]["hours"] > 0 else 0
            )
        
        return {
            "total_hours": round(total_hours, 1),
            "total_xp": round(total_xp, 1),
            "avg_quality": round(avg_quality, 2),
            "sessions": len(self.training_log),
            "skill_efficiency": skill_efficiency
        }


if __name__ == "__main__":
    system = AyikoSkillSystem()
    
    print("\n=== ТЕСТ СИСТЕМЫ НАВЫКОВ ===\n")
    
    # Тренируем навык
    print("Тренируем пиксель-арт (2 часа, качество 0.9):")
    system.train_skill("pixel_art", 2.0, 0.9)
    
    print("\nТренируем акварель (1.5 часа, качество 0.8):")
    system.train_skill("watercolor", 1.5, 0.8)
    
    print(f"\n📊 Сводка навыков: {json.dumps(system.get_skill_summary(), indent=2, ensure_ascii=False)}")
    
    print(f"\n📈 Анализ эффективности: {json.dumps(system.analyze_training_efficiency(), indent=2, ensure_ascii=False)}")
