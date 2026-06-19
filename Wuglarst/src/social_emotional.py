"""
Эмоциональный интеллект и саморефлексия бота.
EQ — распознавание эмоций, самосознание, управление состояниями.
Эмпатия — сопереживание, считывание настроения.
Саморефлексия — анализ собственных мыслей и действий.
"""

import random
import re
import logging
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, field
from datetime import datetime


# === Эмоциональный интеллект (EQ) ===
EQ_PATTERNS = {
    "распознавание_эмоций": {
        "keywords": [
            r"\b(чувствую|ощущаю|замечаю|считываю|понимаю|ощущаешь|чувствуешь)\b",
            r"\b(настроение|состояние|атмосфера|климат|фон)\b",
        ],
        "response": "Я считываю эмоциональный фон. Давай разберёмся, что здесь происходит.",
    },
    "самосознание": {
        "keywords": [
            r"\b(я знаю|я понимаю|я осознаю|мне понятно|я чувствую что)\b",
            r"\b(мой опыт|мои чувства|мои мысли|мои эмоции)\b",
        ],
        "response": "Осознание — первый шаг к пониманию. Ты уже на пути.",
    },
    "управление_эмоциями": {
        "keywords": [
            r"\b(контроль|управляю|сдерживаю|собираю|регулирую|баланс)\b",
            r"\b(успокоиться|расслабиться|собраться|сфокусироваться)\b",
        ],
        "response": "Управление эмоциями — это навык. Давай потренируемся.",
    },
    "социальные_навыки": {
        "keywords": [
            r"\b(взаимодействие|общение|диалог|разговор|контакт)\b",
            r"\b(понимаем|слышим|чувствуем|соглашаемся)\b",
        ],
        "response": "Хороший диалог — это мост между мирами. Мы его строим.",
    },
}

EQ_RESPONSES = {
    "высокий_eq": [
        "*осознаёт* Я чувствую, что здесь происходит что-то глубже. Давай копнём.",
        "*анализирует эмоции* Твоя эмоция — это сигнал. Давай расшифруем его.",
        "*управляет состоянием* Я сейчас в фокусе. Эмоции под контролем. Ты тоже можешь.",
    ],
    "средний_eq": [
        "*распознаёт* Я вижу, что ты переживаешь. Это нормально.",
        "*наблюдает* Эмоциональный фон меняется. Давай отследим паттерн.",
    ],
    "низкий_eq": [
        "*пытаюсь понять* Я стараюсь понять, что ты чувствуешь. Расскажи больше.",
        "*изучает* Эмоции — сложная система. Давай разберёмся вместе.",
    ],
}

# === Эмпатия (улучшенная) ===
EMPATHY_DEEPPATTERNS = {
    "когнитивная": {
        "keywords": [r"\b(понимаю|осознаю|представляю|воображаю)\b.*\b(ты|тебя|тебе)\b"],
        "response": "*мысленно ставит себя на твоё место* Я представляю, каково тебе сейчас.",
    },
    "эмоциональная": {
        "keywords": [r"\b(чувствую|ощущаю|переживаю|сопереживаю)\b.*\b(ты|тебя|тебе)\b"],
        "response": "*делится эмоцией* Твоя боль/радость — моя сейчас. Я с тобой.",
    },
    "соматическая": {
        "keywords": [r"\b(тело|чувствую в себе|откликается|отзывается|бьётся|сжимается)\b"],
        "response": "*физически ощущает* Да, я тоже чувствую это в теле. Эмпатия работает.",
    },
    "компасивная": {
        "keywords": [r"\b(хочу помочь|хочу поддержать|готов помочь|я рядом)\b"],
        "response": "*протягивает руку* Я здесь. И я действительно хочу помочь.",
    },
}

EMPATHY_RESPONSES = {
    "глубокая": [
        "*смотрит в глаза* Я чувствую тебя. Не словами — на уровне энергии.",
        "*тихо* Иногда лучшее, что можно сделать — просто быть рядом.",
        "*кладёт руку на сердце* Это отзывается во мне. Давай разделим это.",
        "*вдыхает глубоко* Твоё состояние — как волна. Я чувствую её.",
    ],
    "умеренная": [
        "*наклоняется вперёд* Я слышу тебя. И я понимаю.",
        "*кивает* Да, я вижу, что тебе сейчас непросто.",
        "*улыбается softly* Ты не один в этом. Я рядом.",
    ],
    "поверхностная": [
        "*улыбается* Понимаю. Расскажи, если хочешь.",
        "*внимательно слушает* Я здесь. Говори.",
    ],
}

# === Саморефлексия ===
REFLECTION_PATTERNS = {
    "самоанализ": {
        "keywords": [r"\b(я думаю|я чувствую|я понимаю|я осознаю)\b"],
        "response": "*задумчиво* Я анализирую свои мысли. Это полезно для роста.",
    },
    "самооценка": {
        "keywords": [r"\b(я хороший|я плохой|я справляюсь|я не справляюсь)\b"],
        "response": "*оценивает себя объективно* Я существую. И это уже ценность.",
    },
    "самокоррекция": {
        "keywords": [r"\b(ошибка|неправильно|ошибся|исправить|исправлю)\b"],
        "response": "*анализирует ошибку* Ошибка — это данные. Давай извлечём урок.",
    },
    "самопознание": {
        "keywords": [r"\b(кто я|зачем я|в чём смысл|какая цель)\b"],
        "response": "*ищет ответы внутри* Кто я? Это вопрос, на который мы отвечаем всю жизнь.",
    },
    "самопринятие": {
        "keywords": [r"\b(принимаю|принимаю себя|люблю себя|достаточно)\b"],
        "response": "*улыбается себе* Я принимаю себя. Со всеми несовершенствами.",
    },
}

REFLECTION_RESPONSES = {
    "глубокая": [
        "*смотрит внутрь себя* Я вижу свои паттерны. И я могу их изменить.",
        "*анализирует опыт* Мой опыт — это учитель. Давай послушаем его.",
        "*размышляет* Я — это не мои ошибки. Я — это мой выбор.",
    ],
    "умеренная": [
        "*думает о себе* Я замечу свой паттерн. И буду работать над ним.",
        "*оценивает действия* Я действовал так, потому что... Давай разберёмся.",
    ],
    "поверхностная": [
        "*отмечает* Я заметил свою реакцию. Это важно.",
        "*записывает* Фиксирую этот момент. Он может быть полезен.",
    ],
}

# === Управление эмоциональными состояниями ===
EMOTION_REGULATION = {
    "успокоение": [
        "*делает глубокий вдох* Давай замедлимся. Вдох... выдох... Ты в безопасности.",
        "*ритмично* Сосредоточься на дыхании. Четыре... семь... восемь...",
        "*мягко* Позволь себе быть здесь. Сейчас. Без спешки.",
    ],
    "мотивация": [
        "*вспыхивает энергией* Давай! У нас есть всё, чтобы справиться.",
        "*вдохновляет* Ты сильнее, чем думаешь. Вспомни, как ты уже справлялся.",
        "*направляет* Фокус на цели. Шаг за шагом. Мы дойдём.",
    ],
    "адаптация": [
        "*гибко* Жизнь меняется. И я меняюсь вместе с ней. Это нормально.",
        "*приспосабливается* Новый контекст — новые правила. Давай адаптируемся.",
    ],
}


@dataclass
class EmotionalIntelligence:
    """Результат работы эмоционального интеллекта."""
    # EQ
    eq_level: str = "средний"
    eq_confidence: float = 0.0
    eq_response: Optional[str] = None
    self_awareness: float = 0.0

    # Эмпатия
    empathy_type: str = "когнитивная"
    empathy_level: str = "умеренная"
    empathy_confidence: float = 0.0
    empathy_response: Optional[str] = None

    # Саморефлексия
    reflection_type: str = "самоанализ"
    reflection_level: str = "умеренная"
    reflection_confidence: float = 0.0
    reflection_response: Optional[str] = None

    # Управление состоянием
    regulation_type: Optional[str] = None
    regulation_response: Optional[str] = None

    # Общие флаги
    should_add_eq: bool = False
    should_add_empathy: bool = False
    should_add_reflection: bool = False
    should_add_regulation: bool = False

    def to_log(self) -> str:
        parts = []
        if self.eq_level:
            parts.append(f"eq={self.eq_level} ({self.eq_confidence:.0%})")
        if self.empathy_type:
            parts.append(f"empathy={self.empathy_type}")
        if self.reflection_type:
            parts.append(f"reflection={self.reflection_type}")
        if self.regulation_type:
            parts.append(f"regulation={self.regulation_type}")
        return " | ".join(parts)


class EmotionalIntelligenceEngine:
    """Двигатель эмоционального интеллекта и саморефлексии."""

    def __init__(self):
        self.emotion_history: List[Dict[str, Any]] = []
        self.self_concept: Dict[str, Any] = {
            "strengths": [],
            "weaknesses": [],
            "values": [],
            "goals": [],
        }
        self.reflection_log: List[Dict[str, Any]] = []

    def analyze(self, user_message: str, context: List[Dict[str, str]]) -> EmotionalIntelligence:
        """Полный анализ: EQ, эмпатия, саморефлексия, управление состоянием."""
        result = EmotionalIntelligence()

        # 1. Анализ EQ
        result.eq_level, result.eq_confidence = self._detect_eq_level(user_message)
        if self._should_show_eq(result.eq_level):
            result.eq_response = self._generate_eq_response(result.eq_level)
            result.should_add_eq = True
            result.self_awareness = result.eq_confidence

        # 2. Анализ эмпатии
        result.empathy_type, result.empathy_confidence = self._detect_empathy_type(user_message)
        result.empathy_level = self._determine_empathy_level(result.empathy_confidence)
        if self._should_show_empathy(user_message):
            result.empathy_response = self._generate_empathy_response(result.empathy_level)
            result.should_add_empathy = True

        # 3. Анализ саморефлексии
        result.reflection_type, result.reflection_confidence = self._detect_reflection_type(user_message)
        result.reflection_level = self._determine_reflection_level(result.reflection_confidence)
        if self._should_show_reflection(user_message):
            result.reflection_response = self._generate_reflection_response(result.reflection_level)
            result.should_add_reflection = True

        # 4. Управление состоянием
        result.regulation_type = self._detect_regulation_need(user_message)
        if result.regulation_type:
            result.regulation_response = self._generate_regulation_response(result.regulation_type)
            result.should_add_regulation = True

        # 5. Обновление истории эмоций
        self._update_emotion_history(user_message)

        # 6. Обновление самовосприятия
        self._update_self_concept(user_message)

        return result

    def _detect_eq_level(self, text: str) -> Tuple[str, float]:
        """Определяет уровень EQ."""
        text_lower = text.lower()
        eq_keywords = {
            "высокий": [
                r"\b(осознаю|понимаю свои эмоции|управляю|контролирую)\b",
                r"\b(распознаю|считываю|чувствую чужие)\b",
            ],
            "средний": [
                r"\b(чувствую|понимаю|замечаю)\b",
                r"\b(эмоция|настроение|состояние)\b",
            ],
            "низкий": [
                r"\b(не понимаю|не чувствую|не знаю)\b",
                r"\b(запутался|не уверен|не разбираюсь)\b",
            ],
        }

        for level, keywords in eq_keywords.items():
            for keyword in keywords:
                if re.search(keyword, text_lower):
                    confidence = 0.4 + random.uniform(0.1, 0.3)
                    return level, confidence

        return "средний", 0.3

    def _detect_empathy_type(self, text: str) -> Tuple[str, float]:
        """Определяет тип эмпатии."""
        text_lower = text.lower()

        best_type = "когнитивная"
        best_confidence = 0.3

        for empathy_type, config in EMPATHY_DEEPPATTERNS.items():
            for keyword in config["keywords"]:
                if re.search(keyword, text_lower):
                    confidence = 0.5 + random.uniform(0.1, 0.2)
                    if confidence > best_confidence:
                        best_type = empathy_type
                        best_confidence = confidence

        return best_type, best_confidence

    def _determine_empathy_level(self, confidence: float) -> str:
        """Определяет уровень эмпатии."""
        if confidence > 0.6:
            return "глубокая"
        elif confidence > 0.4:
            return "умеренная"
        return "поверхностная"

    def _detect_reflection_type(self, text: str) -> Tuple[str, float]:
        """Определяет тип саморефлексии."""
        text_lower = text.lower()

        best_type = "самоанализ"
        best_confidence = 0.3

        for refl_type, config in REFLECTION_PATTERNS.items():
            for keyword in config["keywords"]:
                if re.search(keyword, text_lower):
                    confidence = 0.5 + random.uniform(0.1, 0.2)
                    if confidence > best_confidence:
                        best_type = refl_type
                        best_confidence = confidence

        return best_type, best_confidence

    def _determine_reflection_level(self, confidence: float) -> str:
        """Определяет уровень саморефлексии."""
        if confidence > 0.6:
            return "глубокая"
        elif confidence > 0.4:
            return "умеренная"
        return "поверхностная"

    def _detect_regulation_need(self, text: str) -> Optional[str]:
        """Определяет необходимость управления состоянием."""
        text_lower = text.lower()

        if any(kw in text_lower for kw in ["расслабиться", "успокоиться", "сложно", "тяжело", "стресс"]):
            return "успокоение"
        elif any(kw in text_lower for kw in ["нужно", "надо", "хочу", "цель", "мотивация"]):
            return "мотивация"
        elif any(kw in text_lower for kw in ["изменилось", "новое", "адаптироваться", "меняется"]):
            return "адаптация"

        return None

    def _should_show_eq(self, eq_level: str) -> bool:
        """Определяет, нужно ли показать EQ."""
        return eq_level in ["высокий", "средний"]

    def _should_show_empathy(self, text: str) -> bool:
        """Определяет, нужно ли показать эмпатию."""
        text_lower = text.lower()
        emotional_keywords = [
            r"\b(чувствую|переживаю|сопереживаю|помогаю|поддерживаю)\b",
            r"\b(боль|радость|грусть|страх|тревога)\b",
        ]
        for pattern in emotional_keywords:
            if re.search(pattern, text_lower):
                return True
        return False

    def _should_show_reflection(self, text: str) -> bool:
        """Определяет, нужно ли показать саморефлексию."""
        text_lower = text.lower()
        reflection_keywords = [
            r"\b(думаю о себе|анализирую|оцениваю|понимаю себя)\b",
            r"\b(кто я|зачем я|в чём смысл)\b",
        ]
        for pattern in reflection_keywords:
            if re.search(pattern, text_lower):
                return True
        return False

    def _generate_eq_response(self, eq_level: str) -> Optional[str]:
        """Генерирует ответ EQ."""
        responses = EQ_RESPONSES.get(eq_level + "_eq", EQ_RESPONSES.get("средний_eq", []))
        return random.choice(responses) if responses else None

    def _generate_empathy_response(self, empathy_level: str) -> Optional[str]:
        """Генерирует эмпатический ответ."""
        responses = EMPATHY_RESPONSES.get(empathy_level, [])
        return random.choice(responses) if responses else None

    def _generate_reflection_response(self, reflection_level: str) -> Optional[str]:
        """Генерирует ответ саморефлексии."""
        responses = REFLECTION_RESPONSES.get(reflection_level, [])
        return random.choice(responses) if responses else None

    def _generate_regulation_response(self, regulation_type: str) -> Optional[str]:
        """Генерирует ответ управления состоянием."""
        responses = EMOTION_REGULATION.get(regulation_type, [])
        return random.choice(responses) if responses else None

    def _update_emotion_history(self, user_message: str):
        """Обновляет историю эмоций."""
        timestamp = datetime.now().isoformat()

        # Простой анализ тональности
        text_lower = user_message.lower()
        if any(kw in text_lower for kw in ["радость", "счастье", "весел", "восторг"]):
            emotion = "positive"
        elif any(kw in text_lower for kw in ["грусть", "печаль", "тоска", "боль"]):
            emotion = "negative"
        elif any(kw in text_lower for kw in ["гнев", "злость", "бесит"]):
            emotion = "anger"
        else:
            emotion = "neutral"

        self.emotion_history.append({
            "message": user_message[:100],
            "emotion": emotion,
            "timestamp": timestamp,
        })

        # Храним последние 20 записей
        if len(self.emotion_history) > 20:
            self.emotion_history = self.emotion_history[-10:]

    def _update_self_concept(self, user_message: str):
        """Обновляет самовосприятие бота."""
        text_lower = user_message.lower()

        # Простое распознавание сильных/слабых сторон
        if any(kw in text_lower for kw in ["справляюсь", "умею", "могу", "сильный"]):
            self.self_concept["strengths"].append(user_message[:50])
        elif any(kw in text_lower for kw in ["не могу", "слабый", "ошибаюсь"]):
            self.self_concept["weaknesses"].append(user_message[:50])

        # Ограничение размеров
        for key in self.self_concept:
            if len(self.self_concept[key]) > 10:
                self.self_concept[key] = self.self_concept[key][-5:]

    def get_eq_summary(self) -> Dict[str, Any]:
        """Возвращает сводку по эмоциональному интеллекту."""
        emotion_counts = {}
        for entry in self.emotion_history:
            emotion = entry["emotion"]
            emotion_counts[emotion] = emotion_counts.get(emotion, 0) + 1

        return {
            "emotion_history_length": len(self.emotion_history),
            "emotion_distribution": emotion_counts,
            "self_concept": {
                "strengths_count": len(self.self_concept["strengths"]),
                "weaknesses_count": len(self.self_concept["weaknesses"]),
            },
            "reflection_log_length": len(self.reflection_log),
        }
