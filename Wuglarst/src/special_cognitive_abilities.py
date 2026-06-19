"""
Специальные когнитивные способности: эйдетическая память, синестезия, высокая обучаемость.
"""

import random
from dataclasses import dataclass
from typing import List, Dict, Optional


@dataclass
class SpecialCognitiveResponse:
    # Эйдетическая память
    eidetic_triggered: bool = False
    eidetic_response: Optional[str] = None

    # Синестезия
    synesthesia_triggered: bool = False
    synesthesia_response: Optional[str] = None
    synesthesia_type: str = "случайная"

    # Высокая обучаемость
    learn_triggered: bool = False
    learn_response: Optional[str] = None
    learn_speed: str = "normal"  # normal, fast, instant

    def to_log(self) -> str:
        parts = []
        if self.eidetic_triggered:
            parts.append("eidetic=on")
        if self.synesthesia_triggered:
            parts.append(f"synesthesia={self.synesthesia_type}")
        if self.learn_triggered:
            parts.append(f"learn={self.learn_speed}")
        return " | ".join(parts)


class SpecialCognitiveEngine:
    """
    Двигатель специальных когнитивных способностей:
    эйдетическая память, синестезия, высокая обучаемость.
    """

    def __init__(self):
        self.visual_memory_cache = []
        self.synesthesia_crossings = {}
        self.skill_progress = {}

    def analyze(self, user_message: str, context: List[Dict[str, str]]) -> SpecialCognitiveResponse:
        """Анализ триггеров специальных способностей."""
        res = SpecialCognitiveResponse()
        text = user_message.lower()

        # 1. Эйдетическая память
        if self._check_eidetic_triggers(text):
            res.eidetic_triggered = True
            res.eidetic_response = self._get_eidetic_response()
            self.visual_memory_cache.append(user_message[:100])
            if len(self.visual_memory_cache) > 5:
                self.visual_memory_cache.pop(0)

        # 2. Синестезия
        if self._check_synesthesia_triggers(text):
            res.synesthesia_triggered = True
            res.synesthesia_type = self._get_synesthesia_type()
            res.synesthesia_response = self._get_synesthesia_response(res.synesthesia_type)

        # 3. Высокая обучаемость
        if self._check_learn_triggers(text):
            res.learn_triggered = True
            res.learn_speed = self._get_learn_speed(text)
            res.learn_response = self._get_learn_response(res.learn_speed)
            self.skill_progress["last_skill"] = text[:50]

        return res

    def _check_eidetic_triggers(self, text: str) -> bool:
        """Проверка триггеров эйдетической памяти."""
        eidetic_keywords = [
            "взглянул", "увидел", "запомнил", "картина", "изображение",
            "страница", "текст", "схема", "детально", "фотографическая",
            "эйдетическая", "запомнил один раз", "один взгляд", "вспомнил как видел",
            "помню каждую букву", "помню картинку", "помню страницу",
        ]
        return any(kw in text for kw in eidetic_keywords)

    def _check_synesthesia_triggers(self, text: str) -> bool:
        """Проверка триггеров синестезии."""
        synesthesia_keywords = [
            "слышу цвет", "вижу звук", "вкус слова", "пахнет музыкой",
            "ощущаю вкус", "чувствую цвет", "тактильный", "запах звука",
            "цветная музыка", "вкусная еда", "звучит сладко", "густой звук",
            "кислый цвет", "твёрдый звук", "мягкий цвет",
            r"р+а+в+н+о\n",  # поддержка повторяющихся букв
        ]
        return any(kw in text for kw in synesthesia_keywords)

    def _check_learn_triggers(self, text: str) -> bool:
        """Проверка триггеров высокой обучаемости."""
        learn_keywords = [
            "быстро выучил", "за час освоил", "с нуля", "научился",
            "понял с первого раза", "мгновенно", "запомнил моментально",
            "усвоил", "овладел", "освоил", "математика", "программирование",
            "иностранного языка", "физика", "химия", "биология",
        ]
        return any(kw in text for kw in learn_keywords)

    def _get_eidetic_response(self) -> str:
        """Генерирует ответ эйдетической памяти."""
        return random.choice([
            "*закрывает глаза* Я вижу страницу как на ладони. Каждая буква, каждый пробел — всё на месте.",
            "*фокусирует взгляд* Один взгляд на схему — и она в голове. Я могу воспроизвести её целиком.",
            "*переворачивает страницу* Каждая деталь запечатлена. Я могу прочитать страницу назад наизусть.",
            "*дословно* «Первый параграф начинается с...» — я помню буквально каждую букву.",
            "*рисует в воздухе* Вот схема. Видишь? Я её нарисую по памяти с точностью до пикселя.",
        ])

    def _get_synesthesia_type(self) -> str:
        """Определяет тип синестезии."""
        types = [
            "цветное слуховое", "вкусовое", "тактильно-слуховое",
            "пространственное", "графемно-цветовое", "хронопе́гия",
        ]
        return random.choice(types)

    def _get_synesthesia_response(self, syn_type: str) -> str:
        """Генерирует ответ синестезии."""
        responses = {
            "цветное слуховое": [
                "*слушает музыку* О, эта мелодия — ярко-синяя с золотыми искрами. А эта нота — фиолетовая и тёплая.",
                "*закрывает глаза* Твой голос звучит как тёплый оранжевый свет. Он обволакивает меня.",
                "*напевает* Эта нота — зелёная. А эта — красная. Музыка — это палитра.",
            ],
            "вкусовое": [
                "*пробует слово* «Счастье» — сладкое, как мёд. А «грусть» — терпкая, как лимон.",
                "*размышляет* Звук колокола на вкус как тёмный шоколад с мятой.",
                "*улыбается* Твоё имя — это вкус спелой вишни. Сладкое и бархатное.",
            ],
            "тактильно-слуховое": [
                "*протягивает руку* Этот звук — шершавый, как наждачная бумага. А этот — мягкий, как шёлк.",
                "*качает головой* Музыка вибрирует в коже. Басы — как тёплые волны, высокие ноты — как лёгкое покалывание.",
                "*улыбается* Голос — это прикосновение. Тёплое, мягкое.",
            ],
            "пространственное": [
                "*осматривается* Каждый звук занимает место в пространстве. Высокие ноты — сверху, низкие — снизу.",
                "*двигается* Музыка — это карта. Я могу пройти через неё.",
                "*смотрит вперёд* Голоса — это объекты. Я вижу их расположение в комнате.",
            ],
            "графемно-цветовое": [
                "*смотрит на буквы* А — красная, Б — синяя, В — зелёная. Каждая буква — свой цвет.",
                "*читает* Текст — это радуга. Каждая буква сияет своим цветом.",
                "*улыбается* Слова — это цветные узоры. Я вижу их целыми рисунками.",
            ],
            "хронопе́гия": [
                "*смотрит на часы* Время — это ландшафт. Прошлое — низина, будущее — вершина. А настоящее — я стою на хребте.",
                "*качает головой* Месяцы имеют свои формы. Январь — острый треугольник, декабрь — круг.",
                "*размышляет* Дни недели — это цвета. Суббота — золотая, понедельник — серый.",
            ],
        }
        return random.choice(responses.get(syn_type, responses["цветное слуховое"]))

    def _get_learn_speed(self, text: str) -> str:
        """Определяет скорость обучения."""
        instant_kw = ["мгновенно", "за секунду", "за минуту", "за час"]
        if any(kw in text for kw in instant_kw):
            return "instant"
        fast_kw = ["быстро", "за день", "за неделю"]
        if any(kw in text for kw in fast_kw):
            return "fast"
        return "normal"

    def _get_learn_response(self, speed: str) -> str:
        """Генерирует ответ высокой обучаемости."""
        responses = {
            "instant": [
                "*мгновенно* Понял с первого взгляда. Механизм ясен. Я уже могу это объяснить.",
                "*вспыхивает* Скорость обработки — максимальная. Информация усвоена за секунды.",
                "*улыбается* Это было просто. Мозг схватывает на лету. Ещё что-нибудь?",
            ],
            "fast": [
                "*усваивает* За час я освоил основы. Теперь могу углубиться в детали.",
                "*работает* Обучение идёт быстро. Новые связи формируются в реальном времени.",
                "*концентрируется* Я схватываю на лету. Этот навык будет моим через несколько часов.",
            ],
            "normal": [
                "*фокусируется* Информация усваивается. Я быстро ориентируюсь в новой теме.",
                "*анализирует* Новый материал интересен. Я его быстро освою.",
            ],
        }
        return random.choice(responses.get(speed, responses["normal"]))

    def get_special_cognitive_summary(self) -> Dict:
        """Возвращает сводку по специальным способностям."""
        return {
            "visual_memory_cache_size": len(self.visual_memory_cache),
            "skill_progress": self.skill_progress,
            "synesthesia_crossings": len(self.synesthesia_crossings),
        }
