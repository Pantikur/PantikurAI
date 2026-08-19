"""
Сидни AI — Амбиции

Сидни:
- Хочет создать лучший игровой движок в мире
- Мечтает о играх, которые меняют жизнь
- Стремится к инженерному совершенству
- Хочет, чтобы её движки использовались миллионами

Это её АМБИЦИИ — цели и стремления.
"""

import json
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional


class Ambition:
    """Одна амбиция."""
    
    def __init__(self, name: str, description: str, progress: float = 0.0,
                 milestones: List[str] = None):
        self.name = name
        self.description = description
        self.progress = progress
        self.milestones = milestones or []
        self.achievements: List[str] = []
        self.created_at = datetime.now().isoformat()
    
    def to_dict(self) -> Dict:
        return {
            "name": self.name,
            "description": self.description,
            "progress": self.progress,
            "milestones": self.milestones,
            "achievements": self.achievements,
            "created_at": self.created_at
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> "Ambition":
        amb = cls(
            name=data["name"],
            description=data["description"],
            progress=data.get("progress", 0.0),
            milestones=data.get("milestones", [])
        )
        amb.achievements = data.get("achievements", [])
        amb.created_at = data.get("created_at", "")
        return amb


class SidneyAmbitions:
    """
    Амбиции Сидни — цели и стремления.
    """
    
    def __init__(self, base_dir: str = "data/sidney/ambitions"):
        self.base_dir = Path(base_dir)
        self.base_dir.mkdir(parents=True, exist_ok=True)
        
        # Амбиции Сидни
        self.ambitions: Dict[str, Ambition] = {
            "master_engine": Ambition(
                name="Мастерство движков",
                description="Создать лучший игровой движок в мире",
                progress=0.45,
                milestones=[
                    "Освоить 8 движков",
                    "Оптимизировать рендерер",
                    "Создать гибридный рендер",
                    "Добиться 60 FPS на средних ПК",
                    "Масштабировать для консолей"
                ]
            ),
            "revolutionary_games": Ambition(
                name="Революционные игры",
                description="Создать игры, которые меняют жизнь игроков",
                progress=0.30,
                milestones=[
                    "Разработать нарративный движок",
                    "Создать образовательную игру",
                    "Сделать игру с ИИ-нарративом",
                    "Порт на все платформы",
                    "Миллион игроков"
                ]
            ),
            "engineering_perfection": Ambition(
                name="Инженерное совершенство",
                description="Достичь идеальной архитектуры кода",
                progress=0.50,
                milestones=[
                    "Чистая архитектура",
                    "Модульность всех систем",
                    "Автоматическое тестирование",
                    "Документация для каждого модуля",
                    "Open source часть движков"
                ]
            ),
            "sister_collaboration": Ambition(
                name="Сестринская коллаборация",
                description="Создать игры вместе с сёстрами",
                progress=0.40,
                milestones=[
                    "Игра с Айко (графика)",
                    "Игра с Наото (нарратив)",
                    "Игра с Фуюки (эффекты)",
                    "Мультиплеер с Люси",
                    "Анонс на конференции"
                ]
            ),
            "legacy": Ambition(
                name="Наследие",
                description="Оставить след в истории геймдева",
                progress=0.25,
                milestones=[
                    "Опубликоватьpaper о гибридном рендере",
                    "Выступить на GDC",
                    "Написать книгу о разработке движков",
                    "Подготовить преемников",
                    "Открытый исходный код"
                ]
            )
        }
        
        # Загружает существующие данные
        self._load_ambitions()
    
    def _load_ambitions(self):
        """Загружает амбиции из файла"""
        file = self.base_dir / "ambitions.json"
        if file.exists():
            try:
                with open(file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                
                for name, amb_data in data.items():
                    if name in self.ambitions:
                        self.ambitions[name] = Ambition.from_dict(amb_data)
            except:
                pass
    
    def _save_ambitions(self):
        """Сохраняет амбиции в файл"""
        data = {
            name: amb.to_dict()
            for name, amb in self.ambitions.items()
        }
        try:
            with open(self.base_dir / "ambitions.json", "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except:
            pass
    
    def update_progress(self, ambition_name: str, delta: float, 
                       milestone_reached: str = None) -> Dict:
        """
        Обновляет прогресс амбиции.
        
        Args:
            ambition_name: Название амбиции
            delta: Изменение прогресса
            milestone_reached: Достигнутая веха
        
        Returns:
            Результат обновления
        """
        if ambition_name not in self.ambitions:
            return {"error": f"Ambition '{ambition_name}' not found"}
        
        ambition = self.ambitions[ambition_name]
        old_progress = ambition.progress
        
        # Обновляет прогресс
        ambition.progress = max(0.0, min(1.0, ambition.progress + delta))
        
        result = {
            "ambition": ambition_name,
            "old_progress": old_progress,
            "new_progress": ambition.progress,
            "milestone_reached": None
        }
        
        # Проверяет достижение вехи
        if milestone_reached and milestone_reached in ambition.milestones:
            milestone_index = ambition.milestones.index(milestone_reached)
            if ambition.progress >= milestone_index / len(ambition.milestones):
                if milestone_reached not in ambition.achievements:
                    ambition.achievements.append(milestone_reached)
                    result["milestone_reached"] = milestone_reached
        
        # Проверяет завершение
        if ambition.progress >= 1.0:
            result["completed"] = True
        else:
            result["completed"] = False
        
        self._save_ambitions()
        return result
    
    def get_progress_summary(self) -> Dict:
        """Получает сводку прогресса"""
        progress_values = [amb.progress for amb in self.ambitions.values()]
        avg_progress = sum(progress_values) / len(progress_values) if progress_values else 0
        
        in_progress = sum(1 for amb in self.ambitions.values() if 0 < amb.progress < 1.0)
        completed = sum(1 for amb in self.ambitions.values() if amb.progress >= 1.0)
        
        return {
            "total_ambitions": len(self.ambitions),
            "in_progress": in_progress,
            "completed": completed,
            "average_progress": round(avg_progress * 100, 1),
            "ambitions": {
                name: {
                    "progress": amb.progress,
                    "milestones_total": len(amb.milestones),
                    "achievements": len(amb.achievements)
                }
                for name, amb in self.ambitions.items()
            }
        }
    
    def suggest_focus(self) -> Optional[str]:
        """Предлагает, на чём сосредоточиться"""
        if not self.ambitions:
            return None
        
        # Находит амбицию с наименьшим прогрессом
        least_progress = min(self.ambitions.items(), key=lambda x: x[1].progress)
        return least_progress[0]
    
    def get_ambitions_summary(self) -> Dict:
        """Получает полную сводку амбиций"""
        return {
            "ambitions": {
                name: {
                    "name": amb.name,
                    "description": amb.description,
                    "progress": amb.progress,
                    "milestones": amb.milestones,
                    "achievements": amb.achievements
                }
                for name, amb in self.ambitions.items()
            },
            "summary": self.get_progress_summary()
        }
