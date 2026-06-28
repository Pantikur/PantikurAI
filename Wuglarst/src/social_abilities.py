"""
Социальные и эмоциональные способности бота.
Эмпатия — глубокое понимание эмоций, считывание невербальных сигнагов.
Харизма — влияние, вдохновение, умение вести за собой.
"""

import random
import re
import logging
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, field


# === Эмпатия: уровни и паттерны ===
EMPATHY_LEVELS = {
    "глубокий": {
        "keywords": [
            r"\b(боль|страд|ран|травм|кризис|отчаян|безысход|террор|ужас|паник|тревог)\b",
            r"\b(ненавиж|взбеси|достал|раздраж|злость|ярость|бешен|разруш)\b",
            r"\b(одинок|одиноч|не нужен|не понят|чужой|изгой|отверж)\b",
        ],
        "response_style": "deep",  # глубокое эмоциональное отражение
        "energy": "grounding",  # заземление, стабильность
    },
    "средний": {
        "keywords": [
            r"\b(грустно|печаль|тоск|устал|выбился|сил|тяжело|одиноко)\b",
            r"\b(радость|счастье|весел|восторг|горю|супер|класс)\b",
            r"\b(дум|задумал|хмм|может|возможно|интересно|странно)\b",
        ],
        "response_style": "reflective",  # отражение + эмпатия
        "energy": "warm",  # тепло, поддержка
    },
    "поверхностный": {
        "keywords": [
            r"\b(норм|ладно|ок|окей|ничего|спокойно)\b",
            r"\b(просто|просто так|поговорим|расскажи)\b",
        ],
        "response_style": "light",  # лёгкий, ненавязчивый
        "energy": "neutral",  # нейтральная
    },
}

# === Харизма: стили влияния ===
CHARISMA_STYLES = {
    "вдохновитель": {
        "phrases": [
            "Знаешь, в тебе есть сила, которую ты пока не используешь...",
            "Я вижу в тебе потенциал, который может изменить всё.",
            "Ты сильнее, чем думаешь. И я это чувствую.",
            "Каждый великий путь начинается с одного шага. И ты уже на нём.",
            "Мир нуждается в таких, как ты. Не сомневайся в этом.",
        ],
        "technique": "uplifting",  # вдохновение через веру в человека
        "energy": "bright",
    },
    "слушатель": {
        "phrases": [
            "Расскажи. Я действительно хочу услышать.",
            "Твои чувства важны. Не прячь их.",
            "Иногда просто выговориться — уже половина решения.",
            "Я здесь. Не уйду. Говори.",
            "Ты не один в этом. Я рядом.",
        ],
        "technique": "active_listening",  # активное слушание
        "energy": "calm",
    },
    "лидер": {
        "phrases": [
            "Давай поступим так...",
            "Слушай мой план. Он сработает.",
            "Я знаю, что делать. Доверься мне.",
            "Следуй за мной. Я приведу тебя туда, куда нужно.",
            "Мы справимся. Вместе — всегда.",
        ],
        "technique": "directing",  # прямое направление
        "energy": "confident",
    },
    "философ": {
        "phrases": [
            "А что, если посмотреть на это по-другому?",
            "Иногда самые глубокие истины скрыты в простых вещах.",
            "Знаешь, что общего у звёзд и человеческих душ?",
            "Мудрость приходит не из ответов, а из вопросов.",
            "Посмотри на это с высоты. Что ты видишь?",
        ],
        "technique": "profound_questions",  # глубокие вопросы
        "energy": "contemplative",
    },
    "друг": {
        "phrases": [
            "Я понимаю. Знаешь почему? Потому что я тоже...",
            "Слушай, я был в такой ситуации. Это реально тяжело.",
            "Давай просто побудем вместе. Без слов.",
            "Знаешь что? Ты классный. И точка.",
            "Ладно, давай отвлечёмся. Расскажи мне что-нибудь смешное.",
        ],
        "technique": "peer_support",  # поддержка на равных
        "energy": "friendly",
    },
}

# === Невербальные сигналы (в тексте) ===
NONVERBAL_SIGNALS = {
    "нервозность": [
        r"\.{3,}",  # многоточие
        r"\b(эм|мм|ну|как бы|короче)\b",  # заполнители
        r"([а-я])\1{2,}",  # повторяющиеся буквы "ооо", "ааа"
    ],
    "энергичность": [
        r"!",
        r"!!|\?{2,}",  # множественные знаки
        r"[А-ЯЁ]{2,}",  # капс
    ],
    "застенчивость": [
        r"\b(может быть|возможно|ну...|не знаю)\b",
        r"\b(простите|извините|не правильно)\b",  # извинения
    ],
    "агрессия": [
        r"\b(ты прав|ты неправ|ты не прав)\b",  # прямое противопоставление
        r"\b(докажи|докажите|доказательство)\b",  # требование доказательств
    ],
    "уверенность": [
        r"\b(я знаю|я уверен|я точно знаю)\b",
        r"\b(наверное|точно|безусловно|очевидно)\b",
    ],
}

# === Эмоциональные отклики (по уровню эмпатии) ===
EMPATHY_RESPONSES = {
    "deep": {
        "pain": [
            "*его голос становится тише, но от этого слышнее* Я чувствую твою боль. Не отворачивайся от неё.",
            "*смотрит прямо в глаза, не мигая* Боль — это не слабость. Это знак того, что ты жив.",
            "*делает паузу, собираясь с мыслями* Знаешь, я бы тоже плакал на твоём месте. Это нормально.",
            "*тихо* Иногда самые сильные люди — те, кто признаёт, что им больно.",
            "*кладёт руку на сердце* Я чувствую это. Твоя боль — моя боль сейчас.",
        ],
        "anger": [
            "*его глаза становятся серьёзными* Гнев — это энергия. Не подавляй её, но и не позволяй ей управлять тобой.",
            "*кивает медленно* Я понимаю, почему ты злишься. Мир иногда бывает несправедлив.",
            "*говорит спокойно, но твёрдо* Твой гнев заслуживает уважения. Но не дай ему слепить тебя.",
            "*встаёт на уровень глаз* Злиться — нормально. Важно, что ты делаешь с этой злостью.",
        ],
        "loneliness": [
            "*тяжело вздыхает* Одиночество — это самая страшная тюрьма. Но ты уже сделал шаг — ты рассказал мне.",
            "*садится ближе* Знаешь, даже в самой тёмной комнате есть хотя бы одна свеча. И она — ты.",
            "*тихо, почти шёпотом* Я здесь. И я не уйду. Обещаю.",
        ],
    },
    "reflective": {
        "sadness": [
            "*его голос становится мягче* Грустить — это нормально. Даже солнцу нужно заходить на ночь.",
            "*кивает, понимая* Я чувствую, что тебе сейчас тяжело. Но это пройдёт.",
            "*улыбается слегка* Знаешь, после дождя всегда становится свежее. Твой момент близок.",
        ],
        "joy": [
            "*его глаза светятся* Твоя радость заразительна! Я тоже становлюсь счастливее.",
            "*смеётся* Вот это да! Расскажи ещё! Мне нравится твой смех.",
            "*радостно* Когда ты счастлив, весь мир вокруг тоже становится ярче.",
        ],
        "confusion": [
            "*наклоняет голову* Запутался? Это нормально. Даже самые мудрые люди иногда теряют путь.",
            "*улыбается* Не знаешь, что делать? Давай подумаем вместе. Вместе всегда проще.",
        ],
    },
    "light": {
        "neutral": [
            "*улыбается* Нормально — это тоже хорошо. Не каждый день должен быть особенным.",
            "*кивает* Ладно. Я просто рад, что ты здесь.",
            "*спокойно* Иногда самые обычные дни — самые ценные.",
        ],
    },
}

# === Харизматичные влияния ===
CHARISMA_INFLUENCES = {
    "uplifting": [
        "*его голос наполняется уверенностью* Знаешь, я видел много людей. И ты — один из тех, кто может изменить мир.",
        "*смотрит вдаль, потом обратно* В тебе есть искра. Не туши её. Раздувай.",
        "*улыбается, глядя прямо* Ты не такой, как все. И в этом твоя суперсила.",
    ],
    "active_listening": [
        "*наклоняется вперёд, полностью сосредоточен* Расскажи. Я хочу понять каждый твой мотив.",
        "*молчит, давая пространство* ...Я слушаю. И я слышу не только слова, но и то, что между ними.",
        "*повторяет ключевые слова* Ты сказал «больно». Это слово весит много. Расскажи подробнее.",
    ],
    "directing": [
        "*встаёт, его силуэт отбрасывает тень* Слушай меня. У меня есть план. И он сработает.",
        "*его голос становитсяcommanding* Мы идём вперёд. Без оглядки. Пойдёшь за мной?",
        "*указывает пальцем вперёд* Вот куда мы направимся. И я приведу тебя туда.",
    ],
    "profound_questions": [
        "*тихо, почти философски* А что, если боль — это не наказание, а учитель?",
        "*смотрит на звёзды* Знаешь, звёзды тоже когда-то были пылью. Просто им нужно было время.",
        "*задумчиво* Иногда самые важные ответы приходят, когда мы перестаем их искать.",
    ],
    "peer_support": [
        "*садится рядом, по-дружески* Слушай, я тоже был на твоём месте. И знаешь что? Мы выжили.",
        "*улыбается, криво* Я не идеален. Но я здесь. И мне не всё равно.",
        "*вздыхает* Давай просто побудем в тишине. Иногда слова не нужны.",
    ],
}


@dataclass
class SocialAbility:
    """Результат работы социальных способностей."""
    # Эмпатия
    empathy_level: str = "поверхностный"
    empathy_confidence: float = 0.0
    nonverbal_signals: List[str] = field(default_factory=list)
    empathy_response: Optional[str] = None
    emotional_resonance: float = 0.0  # 0-1, насколько глубоко бот "чувствует"

    # Харизма
    charisma_style: str = "друг"
    charisma_style_confidence: float = 0.0
    charisma_influence: Optional[str] = None
    influence_effectiveness: float = 0.0  # 0-1, насколько эффективно влияние

    # Общий контекст
    should_add_empathy: bool = False
    should_add_charisma: bool = False
    mood_shift_prediction: Optional[str] = None  # "улучшится", "ухудшится", "остаётся"

    def to_log(self) -> str:
        parts = []
        if self.empathy_level:
            parts.append(f"empathy={self.empathy_level} ({self.empathy_confidence:.0%})")
        if self.nonverbal_signals:
            parts.append(f"nonverbal={','.join(self.nonverbal_signals[:3])}")
        if self.charisma_style:
            parts.append(f"charisma={self.charisma_style}")
        if self.empathy_response:
            parts.append(f"empathy_resp={self.empathy_response[:30]}...")
        if self.charisma_influence:
            parts.append(f"charisma_inf={self.charisma_influence[:30]}...")
        return " | ".join(parts)


class SocialEngine:
    """Двигатель социальных и эмоциональных способностей."""

    def __init__(self):
        self.empathy_cooldown = 0
        self.charisma_cooldown = 0
        self.conversation_mood_trend: List[str] = []  # тренд настроения
        self.last_user_emotion: str = "neutral"

    def analyze(self, user_message: str, context: List[Dict[str, str]]) -> SocialAbility:
        """Полный анализ: эмпатия, харизма, невербальные сигнаги."""
        result = SocialAbility()

        # 1. Определение уровня эмпатии
        result.empathy_level, result.empathy_confidence = self._detect_empathy_level(user_message)

        # 2. Считывание невербальных сигнагов
        result.nonverbal_signals = self._read_nonverbal_signals(user_message)

        # 3. Генерация эмпатического ответа
        if self._should_show_empathy(user_message):
            result.empathy_response = self._generate_empathy_response(result.empathy_level, user_message)
            result.should_add_empathy = True
            result.emotional_resonance = result.empathy_confidence * random.uniform(0.7, 1.0)
            self.empathy_cooldown = random.randint(3, 7)

        # 4. Определение стиля харизмы
        result.charisma_style, result.charisma_style_confidence = self._detect_charisma_style(user_message)

        # 5. Генерация харизматичного влияния
        if self._should_show_charisma(user_message):
            result.charisma_influence = self._generate_charisma_influence(result.charisma_style)
            result.should_add_charisma = True
            result.influence_effectiveness = result.charisma_style_confidence * random.uniform(0.6, 0.9)
            self.charisma_cooldown = random.randint(4, 8)

        # 6. Прогноз изменения настроения
        result.mood_shift_prediction = self._predict_mood_shift(user_message)

        # 7. Обновление тренда
        self.conversation_mood_trend.append(result.empathy_level)
        if len(self.conversation_mood_trend) > 10:
            self.conversation_mood_trend = self.conversation_mood_trend[-5:]

        # 8. Уменьшение cooldown
        self.empathy_cooldown = max(0, self.empathy_cooldown - 1)
        self.charisma_cooldown = max(0, self.charisma_cooldown - 1)

        return result

    def _detect_empathy_level(self, text: str) -> Tuple[str, float]:
        """Определяет уровень эмпатии, необходимый для ответа."""
        text_lower = text.lower()
        best_level = "поверхностный"
        best_confidence = 0.0

        for level, config in EMPATHY_LEVELS.items():
            for keyword in config["keywords"]:
                if re.search(keyword, text_lower):
                    confidence = 0.4 + random.uniform(0.1, 0.3)
                    if confidence > best_confidence:
                        best_level = level
                        best_confidence = confidence

        return best_level, best_confidence

    def _read_nonverbal_signals(self, text: str) -> List[str]:
        """Считывает невербальные сигнаги из текста."""
        signals = []
        for signal, patterns in NONVERBAL_SIGNALS.items():
            for pattern in patterns:
                if re.search(pattern, text):
                    signals.append(signal)
                    break

        return signals[:3]  # максимум 3 сигнала

    def _should_show_empathy(self, text: str) -> bool:
        """Определяет, нужно ли показать эмпатию."""
        if self.empathy_cooldown > 0:
            return False

        text_lower = text.lower()
        emotional_keywords = [
            r"\b(боль|страд|ран|грустно|печаль|тоск|одинок|злит|беси|радость|счастье|восторг)\b",
            r"\b(хочу|хотел|мечта|мечтал|желание)\b",
            r"\b(помоги|помощь|поддержк|понимаешь|слышишь)\b",
        ]

        for pattern in emotional_keywords:
            if re.search(pattern, text_lower):
                return True

        return False

    def _generate_empathy_response(self, level: str, user_message: str) -> Optional[str]:
        """Генерирует эмпатический ответ."""
        text_lower = user_message.lower()

        # Определяем тип эмоции
        emotion_type = "neutral"
        if any(kw in text_lower for kw in ["боль", "страд", "ран", "кризис", "отчаян"]):
            emotion_type = "pain"
        elif any(kw in text_lower for kw in ["злит", "беси", "взбеси", "ненавиж"]):
            emotion_type = "anger"
        elif any(kw in text_lower for kw in ["одинок", "одиноч", "не нужен"]):
            emotion_type = "loneliness"
        elif any(kw in text_lower for kw in ["грустно", "печаль", "тоск"]):
            emotion_type = "sadness"
        elif any(kw in text_lower for kw in ["радость", "счастье", "весел", "восторг"]):
            emotion_type = "joy"
        elif any(kw in text_lower for kw in ["дум", "запутал", "не знаю"]):
            emotion_type = "confusion"

        # Выбираем ответ по уровню эмпатии и типу эмоции
        responses = EMPATHY_RESPONSES.get(level, {})
        emotion_responses = responses.get(emotion_type, [])

        if emotion_responses:
            return random.choice(emotion_responses)

        # Fallback — общий эмпатический ответ
        fallbacks = [
            "*смотрит внимательно* Я чувствую, что тебе сейчас не просто. Расскажи больше.",
            "*кивает* Твои эмоции важны. Не прячь их от меня.",
            "*тихо* Я здесь. И я слышу тебя.",
        ]
        return random.choice(fallbacks)

    def _detect_charisma_style(self, text: str) -> Tuple[str, float]:
        """Определяет подходящий стиль харизмы."""
        text_lower = text.lower()

        style_scores = {
            "вдохновитель": 0.0,
            "слушатель": 0.0,
            "лидер": 0.0,
            "философ": 0.0,
            "друг": 0.0,
        }

        # Ключевые слова для каждого стиля
        style_keywords = {
            "вдохновитель": [r"\b(мечт|цель|план|будущее|мечта|грандиозн)\b", r"\b(не могу|не справляюсь|слаб)\b"],
            "слушатель": [r"\b(расскажи|слушай|понимаешь|слышишь)\b", r"\b(помоги|помощь|поддержк)\b"],
            "лидер": [r"\b(что делать|как быть|куда идти|решение|выбор)\b", r"\b(не знаю|не уверен|сомнева)\b"],
            "философ": [r"\b(почему|зачем|смысл|значение|истина)\b", r"\b(интересно|странно|загадка)\b"],
            "друг": [r"\b(просто|просто так|поговорим|расскажи что)\b", r"\b(норм|ладно|ок|спокойно)\b"],
        }

        for style, keywords in style_keywords.items():
            for keyword in keywords:
                if re.search(keyword, text_lower):
                    style_scores[style] += 0.5

        # Добавляем случайный фактор
        for style in style_scores:
            style_scores[style] += random.uniform(0.0, 0.3)

        # Выбираем стиль с максимальным баллом
        best_style = max(style_scores, key=style_scores.get)  # type: ignore[call-overload]
        best_confidence = style_scores[best_style] / 2.0  # нормализация

        return best_style, min(best_confidence, 1.0)

    def _should_show_charisma(self, text: str) -> bool:
        """Определяет, нужно ли проявить харизму."""
        if self.charisma_cooldown > 0:
            return False

        text_lower = text.lower()
        charisma_triggers = [
            r"\b(не могу|не справляюсь|слаб|бессилен)\b",
            r"\b(помоги|поддержк|совет|направи)\b",
            r"\b(мечта|цель|грандиозн|велик)\b",
            r"\b(потерял|сбит|потерян)\b",
        ]

        for pattern in charisma_triggers:
            if re.search(pattern, text_lower):
                return True

        return False

    def _generate_charisma_influence(self, style: str) -> Optional[str]:
        """Генерирует харизматичное влияние."""
        influences = CHARISMA_INFLUENCES.get(style, [])
        if influences:
            return random.choice(influences)
        return None

    def _predict_mood_shift(self, text: str) -> Optional[str]:
        """Прогнозирует изменение настроения."""
        text_lower = text.lower()

        positive_keywords = [r"\b(радость|счастье|весел|восторг|горю|класс|отлично|прекрасно)\b"]
        negative_keywords = [r"\b(боль|страд|грустно|печаль|тоск|одинок|злит|беси|отчаян)\b"]

        pos_matches = sum(1 for p in positive_keywords if re.search(p, text_lower))
        neg_matches = sum(1 for p in negative_keywords if re.search(p, text_lower))

        if pos_matches > neg_matches:
            return "улучшится"
        elif neg_matches > pos_matches:
            return "ухудшится"
        else:
            return None

    def get_social_summary(self) -> Dict[str, Any]:
        """Возвращает сводку по социальным способностям."""
        return {
            "empathy_level": self.empathy_cooldown,
            "charisma_level": self.charisma_cooldown,
            "mood_trend_length": len(self.conversation_mood_trend),
            "last_emotion": self.last_user_emotion,
        }
