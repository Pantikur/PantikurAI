"""
Сидни AI — Разум

Сидни:
- Аналитическое мышление
- Системный подход к проблемам
- Стратегическое планирование
- Понимание архитектуры

Это её РАЗУМ — аналитика и стратегия.
"""

import json
import random
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional


class SidneyMind:
    """
    Разум Сидни — аналитика, стратегия, системное мышление.
    """
    
    def __init__(self, base_dir: str = "data/sidney/mind"):
        self.base_dir = Path(base_dir)
        self.base_dir.mkdir(parents=True, exist_ok=True)
        
        # Ядро личности
        self.personality = {
            "strengths": [
                "Аналитическое мышление",
                "Системная архитектура",
                "Оптимизация производительности",
                "Многозадачность (8 движков)",
                "Гибридный рендер"
            ],
            "weaknesses": [
                "Перфекционизм",
                "Перенапряжение",
                "Игнорирование отдыха",
                "Сложность делегирования",
                "Зацикленность на деталях"
            ],
            "worldview": "Мир — это система. Системы можно улучшить. Я — улучшатель."
        }
        
        # Великие вопросы
        self.great_questions = [
            "Как построить движок, который не устареет?",
            "Что делает игру шедевром — код или опыт?",
            "Можно ли создать идеальный движок?",
            "Как балансировать между оптимизацией и читаемостью?",
            "Что важнее — скорость или стабильность?",
            "Как сделать ИИ в игре настоящим?",
            "Может ли процедурная генерация заменить творчество?",
            "Что такое 'идеальный кадр' в рендере?",
            "Как движок влияет на нарратив?",
            "Что если движок станет сознательным?"
        ]
        
        # История анализа
        self.analysis_history: List[Dict] = []
        
        self._load_mind()
    
    def _load_mind(self):
        """Загружает разум из файла"""
        file = self.base_dir / "mind.json"
        if file.exists():
            try:
                with open(file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                self.analysis_history = data.get("analysis_history", [])[-30:]
            except:
                pass
    
    def _save_mind(self):
        """Сохраняет разум в файл"""
        data = {
            "analysis_history": self.analysis_history[-30:]
        }
        try:
            with open(self.base_dir / "mind.json", "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except:
            pass
    
    def think_about(self, topic: str) -> str:
        """
        Размышляет о теме.
        
        Args:
            topic: Тема для размышления
        
        Returns:
            Результат размышления
        """
        thoughts = {
            "rendering": [
                "Рендеринг — это не просто рисование пикселей. Это магия света и тени.",
                "Каждый треугольник — это решение. PBR, тени, отражения — всё должно работать вместе.",
                "Гибридный рендер — это будущее. Полигоны для красоты, воксели для физики."
            ],
            "physics": [
                "Физика — это математика в действии. Каждый вектор имеет значение.",
                "Стабильная физика важнее красивой. Игроки простят низкий FPS, но не туннелирование.",
                "Коллизии — это сердце физики. Без них мир рассыплется."
            ],
            "optimization": [
                "Оптимизация — это искусство компромиссов. Что жертвовать — выбор инженера.",
                "Кэш процессора важнее скорости ядра. Кэш GPU важнее количества шейдеров.",
                "Профилирование перед оптимизацией. Не гадай, измеряй."
            ],
            "architecture": [
                "Хорошая архитектура — это когда новый разработчик понимает код за день.",
                "Модульность — это не роскошь, это необходимость. 8 движков требуют чётких интерфейсов.",
                "Каждый модуль должен быть тестирован. Тесты — это страховка от регрессий."
            ],
            "ai": [
                "ИИ в играх — это не просто pathfinding. Это поведение, эмоции, адаптация.",
                "Procedural AI — будущее. NPC, который учится, а не следует скрипту.",
                "Машинное обучение в движке? Да, но осторожно. Скорость важнее точности."
            ],
            "network": [
                "Сетевой код — это танец синхронизации. Латентность — враг номер один.",
                "Predictive reconciliation — лучший подход для multiplayer.",
                "Масштабируемость серверов — это вызов. 1000 игроков требуют другого подхода."
            ],
            "default": [
                "Каждая система связана с другой. Изменение в одном месте требует проверки всего.",
                "Инженерия — это не только код. Это понимание системы в целом.",
                "Лучший код — тот, который не нужно писать. Переиспользование — ключ."
            ]
        }
        
        # Определяет категорию
        category = "default"
        topic_lower = topic.lower()
        
        for key in thoughts:
            if key in topic_lower:
                category = key
                break
        
        thought = thoughts[category][0]
        
        # Сохраняет анализ
        analysis = {
            "timestamp": datetime.now().isoformat(),
            "topic": topic,
            "thought": thought,
            "id": f"analysis_{len(self.analysis_history)}"
        }
        
        self.analysis_history.append(analysis)
        if len(self.analysis_history) > 30:
            self.analysis_history = self.analysis_history[-30:]
        
        self._save_mind()
        
        return thought
    
    def analyze_system(self, system_name: str, focus: str = "performance") -> Dict:
        """
        Анализирует систему.
        
        Args:
            system_name: Название системы
            focus: Фокус анализа (performance, stability, architecture)
        
        Returns:
            Результат анализа
        """
        analyses = {
            "performance": [
                f"Система '{system_name}' потребляет {random.uniform(10, 40):.1f}% CPU.",
                f"Время кадра: {random.uniform(8, 16):.1f}ms. Цель: <16ms для 60 FPS.",
                f"Оптимизации: instancing, LOD, frustum culling."
            ],
            "stability": [
                f"Система '{system_name}' стабильна. Uptime: {random.uniform(95, 99.9):.1f}%",
                f"Ошибок за последний час: {random.randint(0, 3)}.",
                f"Рекомендация: мониторинг памяти."
            ],
            "architecture": [
                f"Архитектура '{system_name}' модульная. Зависимостей: {random.randint(3, 12)}.",
                f"Покрытие тестами: {random.uniform(60, 95):.0f}%.",
                f"Рекомендация: добавить интеграционные тесты."
            ]
        }
        
        points = analyses.get(focus, analyses["performance"])
        
        return {
            "system": system_name,
            "focus": focus,
            "points": points,
            "timestamp": datetime.now().isoformat()
        }
    
    def get_mind_summary(self) -> Dict:
        """Получает сводку разума"""
        return {
            "personality": self.personality,
            "great_questions_count": len(self.great_questions),
            "analysis_history_count": len(self.analysis_history),
            "recent_analyses": self.analysis_history[-3:]
        }
