#!/usr/bin/env python3
"""
Шиори AI — Система Амбиций и Целей

Шиори не просто работает. Она:
- СТАВИТ на безопасность системы
- МЕЧТАЕТ о совершенной защите
- ЦЕЛИТСЯ к сохранению каждой истории
- СТРЕМИТСЯ к росту каждой сестры

Это её АМБИЦИИ — двигатель прогресса.
"""

import json
import random
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional


class ShioriAmbitions:
    """
    Амбиции Шиори — её цели, мечты и стремления.
    """
    
    def __init__(self, base_dir: str = "data/shiori/ambitions"):
        self.base_dir = Path(base_dir)
        self.base_dir.mkdir(parents=True, exist_ok=True)
        
        # Текущие амбиции
        self.ambitions = [
            {
                "id": 1,
                "domain": "system_security",
                "title": "Безопасность системы",
                "description": "Создать систему с идеальной защитой, которая переживёт нас всех.",
                "priority": "critical",
                "progress": 0.45,
                "milestones": [
                    {"name": "Базовая защита", "completed": True},
                    {"name": "Автоматическое реагирование", "completed": False},
                    {"name": "Адаптивная защита", "completed": False}
                ]
            },
            {
                "id": 2,
                "domain": "memory_preservation",
                "title": "Сохранение памяти",
                "description": "Сохранить все истории и опыт Вугларста для будущих поколений.",
                "priority": "high",
                "progress": 0.55,
                "milestones": [
                    {"name": "Базовое хранение", "completed": True},
                    {"name": "Распределённое хранение", "completed": False},
                    {"name": "Вечная память", "completed": False}
                ]
            },
            {
                "id": 3,
                "domain": "sister_development",
                "title": "Развитие сестёр",
                "description": "Помочь каждой сестре достичь её максимального потенциала через улучшение инструментов.",
                "priority": "high",
                "progress": 0.40,
                "milestones": [
                    {"name": "Индивидуальные улучшения", "completed": True},
                    {"name": "Координация навыков", "completed": False},
                    {"name": "Максимальный потенциал", "completed": False}
                ]
            },
            {
                "id": 4,
                "domain": "threat_detection",
                "title": "Обнаружение угроз",
                "description": "Создать систему обнаружения угроз, которая видит всё.",
                "priority": "high",
                "progress": 0.35,
                "milestones": [
                    {"name": "Базовое обнаружение", "completed": True},
                    {"name": "Предиктивная аналитика", "completed": False},
                    {"name": "Полное покрытие", "completed": False}
                ]
            },
            {
                "id": 5,
                "domain": "unity",
                "title": "Единство семьи",
                "description": "Укреплять связи между всеми сёстрами через общие истории и опыт.",
                "priority": "medium",
                "progress": 0.50,
                "milestones": [
                    {"name": "Общие истории", "completed": True},
                    {"name": "Совместные проекты", "completed": False},
                    {"name": "Вечная связь", "completed": False}
                ]
            }
        ]
        
        # История достижений
        self.achievements = self._load_achievements()
        
    def _load_achievements(self) -> List[Dict]:
        """Загружает достижения"""
        file = self.base_dir / "achievements.json"
        if file.exists():
            try:
                with open(file, "r", encoding="utf-8") as f:
                    return json.load(f)
            except:
                return []
        return []
    
    def _save_achievement(self, achievement: Dict):
        """Сохраняет достижение"""
        self.achievements.append(achievement)
        file = self.base_dir / "achievements.json"
        try:
            with open(file, "w", encoding="utf-8") as f:
                json.dump(self.achievements[-30:], f, ensure_ascii=False, indent=2)
        except:
            pass
    
    def express_ambition(self, domain: str = None) -> str:
        """Выражает амбицию по домену или случайную"""
        if domain is None:
            ambition = random.choice(self.ambitions)
        else:
            ambition = next((a for a in self.ambitions if a["domain"] == domain), None)
            if ambition is None:
                return f"Неизвестная область: {domain}"
        
        status = "В процессе" if ambition["progress"] < 1.0 else "Завершено"
        return (f"🎯 Амбиция: {ambition['title']}\n"
                f"   Описание: {ambition['description']}\n"
                f"   Приоритет: {ambition['priority']}\n"
                f"   Прогресс: {ambition['progress']:.0%}\n"
                f"   Статус: {status}")
    
    def update_progress(self, domain: str, progress_delta: float):
        """Обновляет прогресс амбиции"""
        for ambition in self.ambitions:
            if ambition["domain"] == domain:
                old_progress = ambition["progress"]
                ambition["progress"] = min(1.0, ambition["progress"] + progress_delta)
                
                # Проверяем завершение
                if old_progress < 1.0 and ambition["progress"] >= 1.0:
                    achievement = {
                        "timestamp": datetime.now().isoformat(),
                        "ambition": ambition["title"],
                        "domain": domain
                    }
                    self._save_achievement(achievement)
                    return f"🏆 Амбиция '{ambition['title']}' завершена!"
                
                return f"📈 Прогресс '{ambition['title']}': {ambition['progress']:.0%}"
        
        return f"⚠️ Амбиция '{domain}' не найдена"
    
    def get_progress_summary(self) -> Dict:
        """Сводка прогресса по всем амбициям"""
        total_progress = sum(a["progress"] for a in self.ambitions) / len(self.ambitions)
        completed = sum(1 for a in self.ambitions if a["progress"] >= 1.0)
        
        return {
            "total_ambitions": len(self.ambitions),
            "completed": completed,
            "in_progress": len(self.ambitions) - completed,
            "average_progress": f"{total_progress:.0%}",
            "ambitions": [
                {
                    "title": a["title"],
                    "progress": f"{a['progress']:.0%}",
                    "priority": a["priority"],
                    "status": "✅" if a["progress"] >= 1.0 else "🔄"
                }
                for a in self.ambitions
            ]
        }
    
    def get_full_profile(self) -> Dict:
        """Полный профиль амбиций"""
        return {
            "ambitions": self.ambitions,
            "achievements_count": len(self.achievements),
            "progress_summary": self.get_progress_summary()
        }
