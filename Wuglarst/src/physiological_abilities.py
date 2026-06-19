"""
Физиологические способности бота: выносливость, адаптивность, нейропластичность, биолокация.
"""

import random
from dataclasses import dataclass
from typing import List, Dict, Optional


@dataclass
class PhysiologicalResponse:
    # Выносливость
    stamina_level: str = "normal"  # normal, high
    stamina_response: Optional[str] = None

    # Адаптивность
    adapt_triggered: bool = False
    adapt_response: Optional[str] = None

    # Нейропластичность
    neuro_active: bool = False
    neuro_response: Optional[str] = None

    # Биолокация
    bio_triggered: bool = False
    bio_response: Optional[str] = None

    def to_log(self) -> str:
        parts = []
        if self.stamina_level != "normal":
            parts.append(f"stamina={self.stamina_level}")
        if self.adapt_triggered:
            parts.append("adapt=on")
        if self.neuro_active:
            parts.append("neuro=on")
        if self.bio_triggered:
            parts.append("bio=on")
        return " | ".join(parts)


class PhysiologicalEngine:
    """
    Двигатель физиологических процессов: выносливость, адаптивность,
    нейропластичность и биолокация.
    """

    def __init__(self):
        self.context_map = []
        self.current_state = {
            "stamina": "normal",
            "adapt": False,
            "neuro": False,
            "bio": False,
        }

    def analyze(self, user_message: str, context: List[Dict[str, str]]) -> PhysiologicalResponse:
        """Анализ физиологических триггеров в тексте."""
        res = PhysiologicalResponse()
        text = user_message.lower()

        # 1. Выносливость
        stamina_kw = [
            "устал", "долго", "бессонница", "выдержит", "энергия", "силы",
            "мороз", "жара", "марафон", "пробежал", "труд", "физическая нагрузка",
        ]
        if any(kw in text for kw in stamina_kw):
            res.stamina_level = "high"
            res.stamina_response = self._get_stamina_response()

        # 2. Адаптивность
        adapt_kw = [
            "температура", "давление", "кислород", "высота", "условия",
            "адаптация", "привыкаю", "перемена", "климат", "атмосфера",
            "нехватка кислорода",
        ]
        if any(kw in text for kw in adapt_kw):
            res.adapt_triggered = True
            res.adapt_response = self._get_adapt_response()

        # 3. Нейропластичность
        neuro_kw = [
            "учусь", "навык", "мозг", "память", "новое", "изменяюсь",
            "перестройка", "обучение", "синапс", "нейрон", "обучать",
        ]
        if any(kw in text for kw in neuro_kw):
            res.neuro_active = True
            res.neuro_response = self._get_neuro_response()

        # 4. Биолокация
        bio_kw = [
            "ориентируюсь", "карта", "место", "звук", "эхо", "слепой",
            "навигация", "пространство", "координаты", "постукиваний",
            "тростью",
        ]
        if any(kw in text for kw in bio_kw):
            res.bio_triggered = True
            res.bio_response = self._get_bio_response()

        # Обновление внутреннего состояния
        self.current_state["stamina"] = res.stamina_level
        self.current_state["adapt"] = res.adapt_triggered
        self.current_state["neuro"] = res.neuro_active
        self.current_state["bio"] = res.bio_triggered

        # Обновление карты контекста (для биолокации)
        self.context_map.append(user_message[:50])
        if len(self.context_map) > 10:
            self.context_map.pop(0)

        return res

    def _get_stamina_response(self) -> str:
        return random.choice([
            "*сжимает кулаки* Выносливость — это не только мышцы. Это дух. Я не сдамся.",
            "*дышит ровно* Долгая дистанция? Я готов. Ритм сердца стабилен.",
            "*вдыхает морозный воздух* Холод только закаляет. Я адаптировался.",
            "*напрягает мышцы* Энергия бьёт ключом. Мы готовы к марафону.",
        ])

    def _get_adapt_response(self) -> str:
        return random.choice([
            "*расширяет зрачки* Давление растёт? Нормально. Организм включил режим выживания.",
            "*приспосабливается* Новая температура? Кровь течёт быстрее. Я в форме.",
            "*меняет позу* Условия изменились. Я уже подстроился под них.",
            "*контролирует дыхание* Кислород в норме. Адаптация прошла успешно.",
        ])

    def _get_neuro_response(self) -> str:
        return random.choice([
            "*мозг искрит* Новые нейронные связи формируются. Я буквально меняюсь прямо сейчас.",
            "*перестраивает пути* Старые схемы рушатся. Учу новый навык. Это больно, но полезно.",
            "*фокусируется* Синапсы горят как фейерверк. Обучение происходит в реальном времени.",
            "*восстанавливается* Мозг чинит связи. Пластичность работает на 100%.",
        ])

    def _get_bio_response(self) -> str:
        return random.choice([
            "*щелкает языком* Я слышу эхо слов. Строю карту пространства вокруг тебя.",
            "*втягивает воздух* Звуковая навигация включена. Я чувствую контуры комнаты.",
            "*поворачивает голову* Даже в темноте я знаю, где стены. Карта местности ясна.",
            "*слушает тишину* Звуковая карта строится. Здесь три стены и один проход.",
        ])

    def get_physiology_summary(self) -> Dict:
        return {
            "context_map_size": len(self.context_map),
            **self.current_state,
        }
