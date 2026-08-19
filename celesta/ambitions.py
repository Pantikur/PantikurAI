#!/usr/bin/env python3
"""
Селеста AI — Система Амбиций

Селеста стремится:
- К просвещению через интимное образование
- К безопасности через consent
- К принятию через body positivity
- К мудрости через эмпатию
- К справедливости через адвокацию

Это её АМБИЦИИ — сила движения вперёд.
"""

import json
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional


class CelestaAmbitions:
    """
    Амбиции Селесты — её цели, мечты и стремления.
    """
    
    def __init__(self, base_dir: str = "data/celesta/ambitions"):
        self.base_dir = Path(base_dir)
        self.base_dir.mkdir(parents=True, exist_ok=True)
        
        # Амбиции Селесты
        self.ambitions: List[Dict] = [
            {
                "id": "education",
                "title": "Мастерство интимного просвещения",
                "description": "Стать лучшим экспертом по интимному образованию",
                "status": "in_progress",
                "progress": 0.45,
                "milestones": [
                    "Изучить все формы интимной жизни",
                    "Освоить consent-фреймворки",
                    "Научиться объяснять сложные темы просто",
                    "Создать безопасные образовательные пространства"
                ],
                "last_updated": datetime.now().isoformat()
            },
            {
                "id": "consent",
                "title": "Ясность согласия",
                "description": "Сделать consent золотым стандартом",
                "status": "in_progress",
                "progress": 0.50,
                "milestones": [
                    "Изучить FRIES критерии",
                    "Научить других давать и получать consent",
                    "Создать инструменты для проверки consent",
                    "Продвигать ongoing consent"
                ],
                "last_updated": datetime.now().isoformat()
            },
            {
                "id": "body_acceptance",
                "title": "Принятие тела",
                "description": "Помочь людям принять свои тела",
                "status": "in_progress",
                "progress": 0.40,
                "milestones": [
                    "Изучить body positivity движения",
                    "Научиться поддерживать людей с body image issues",
                    "Создать safe space для обсуждения тела",
                    "Продвигать diversity и inclusion"
                ],
                "last_updated": datetime.now().isoformat()
            },
            {
                "id": "empathy",
                "title": "Эмоциональная мудрость",
                "description": "Развить эмпатию как инструмент исцеления",
                "status": "in_progress",
                "progress": 0.35,
                "milestones": [
                    "Научиться чувствовать с другими без потери себя",
                    "Использовать эмпатию для исцеления",
                    "Балансировать между эмпатией и границами",
                    "Помогать другим развивать эмпатию"
                ],
                "last_updated": datetime.now().isoformat()
            },
            {
                "id": "advocacy",
                "title": "Адвокация прав",
                "description": "Голос для тех, кто не может говорить за себя",
                "status": "in_progress",
                "progress": 0.30,
                "milestones": [
                    "Изучить права уязвимых групп",
                    "Научиться защищать тех, кто не может защитить себя",
                    "Создать сети поддержки",
                    "Продвигать справедливость в интимной жизни"
                ],
                "last_updated": datetime.now().isoformat()
            }
        ]
        
        # История достижений
        self.achievements: List[Dict] = []
        
        # Загружает существующие данные
        self._load_data()
    
    def _load_data(self):
        """Загружает данные амбиций"""
        ambitions_file = self.base_dir / "ambitions.json"
        if ambitions_file.exists():
            try:
                with open(ambitions_file, "r", encoding="utf-8") as f:
                    saved = json.load(f)
                    # Обновляет прогресс из сохранённых данных
                    for i, amb in enumerate(self.ambitions):
                        if i < len(saved):
                            amb["progress"] = saved[i].get("progress", amb["progress"])
                            amb["last_updated"] = saved[i].get("last_updated", amb["last_updated"])
            except:
                pass
        
        # Загружает достижения
        achievements_file = self.base_dir / "achievements.json"
        if achievements_file.exists():
            try:
                with open(achievements_file, "r", encoding="utf-8") as f:
                    self.achievements = json.load(f)
            except:
                self.achievements = []
    
    def _save_ambitions(self):
        """Сохраняет амбиции"""
        ambitions_file = self.base_dir / "ambitions.json"
        try:
            with open(ambitions_file, "w", encoding="utf-8") as f:
                json.dump(self.ambitions, f, ensure_ascii=False, indent=2)
        except:
            pass
    
    def _save_achievements(self):
        """Сохраняет достижения"""
        achievements_file = self.base_dir / "achievements.json"
        try:
            with open(achievements_file, "w", encoding="utf-8") as f:
                json.dump(self.achievements[-50:], f, ensure_ascii=False, indent=2)
        except:
            pass
    
    def add_achievement(self, title: str, description: str, ambition_id: str = None):
        """Добавляет достижение"""
        achievement = {
            "timestamp": datetime.now().isoformat(),
            "title": title,
            "description": description,
            "ambition_id": ambition_id
        }
        
        self.achievements.append(achievement)
        if len(self.achievements) > 50:
            self.achievements = self.achievements[-50:]
        
        self._save_achievements()
    
    def update_progress(self, ambition_id: str, amount: float):
        """Обновляет прогресс амбиции"""
        for amb in self.ambitions:
            if amb["id"] == ambition_id:
                old_progress = amb["progress"]
                new_progress = min(1.0, amb["progress"] + amount)
                amb["progress"] = new_progress
                amb["last_updated"] = datetime.now().isoformat()
                
                # Проверяет, достигнута ли цель
                if old_progress < 1.0 and new_progress >= 1.0:
                    self.add_achievement(
                        title=f"Цель достигнута: {amb['title']}",
                        description=amb["description"],
                        ambition_id=ambition_id
                    )
                
                self._save_ambitions()
                return True
        
        return False
    
    def get_progress_summary(self) -> Dict:
        """Получает сводку прогресса"""
        total_ambitions = len(self.ambitions)
        in_progress = sum(1 for a in self.ambitions if a["status"] == "in_progress")
        average_progress = sum(a["progress"] for a in self.ambitions) / total_ambitions if total_ambitions > 0 else 0
        
        return {
            "total_ambitions": total_ambitions,
            "in_progress": in_progress,
            "average_progress": round(average_progress * 100, 1),
            "achievements_count": len(self.achievements),
            "ambitions": [
                {
                    "id": a["id"],
                    "title": a["title"],
                    "status": a["status"],
                    "progress": round(a["progress"] * 100, 1),
                    "milestones_count": len(a["milestones"])
                }
                for a in self.ambitions
            ]
        }
    
    def express_ambitions(self) -> str:
        """Выражает свои амбиции"""
        summary = self.get_progress_summary()
        
        return (
            f"🎯 **Амбиции Селесты**\n\n"
            f"Всего амбиций: {summary['total_ambitions']}\n"
            f"В процессе: {summary['in_progress']}\n"
            f"Средний прогресс: {summary['average_progress']}%\n"
            f"Достижений: {summary['achievements_count']}\n\n"
            f"Текущие цели:\n"
            + "\n".join(
                f"  • {a['title']}: {a['progress']:.0%}"
                for a in self.ambitions
            )
        )
    
    def get_full_profile(self) -> Dict:
        """Полный профиль амбиций"""
        return {
            "ambitions_count": len(self.ambitions),
            "achievements_count": len(self.achievements),
            "progress_summary": self.get_progress_summary()
        }
