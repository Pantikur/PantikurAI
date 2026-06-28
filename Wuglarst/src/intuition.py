"""
Интуитивный модуль бота.
Анализирует настроение, предвосхищает намерения, предлагает темы и предчувствия.
"""

import random
import re
import logging
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, field


# === Эмоциональные паттерны ===
MOOD_PATTERNS = {
    "грустный": [
        r"\b(грустно|печаль|тоск|скуп|плач|слез|хандр|устал|выбился|сил|нет сил|тяжело|одиноко|одинок)\b",
        r"\b(плохо|больно|горько|позор|стыд|жал|жаль|бесит|раздраж|злит|обиж|ненавиж|всё надоело|всё плохо)\b",
    ],
    "радостный": [
        r"\b(радость|счастье|весел|восторг|горю|супер|класс|отлично|прекрасно|обожаю|влюблен|влюблен|влюблена)\b",
        r"\b(круто|супер|класс|огонь|красава|завис|в кайф|в кайф|в восторге|в восторге|в восторге)\b",
    ],
    "гневный": [
        r"\b(беси|злит|раздраж|достал|тупи|дурацк|идиот|урод|сука|бля|хер|говно|мразь)\b",
        r"\b(убери|отстань|хватит|достал|надоел|вон|прочь|уходи|не хочу|не буду)\b",
    ],
    "задумчивый": [
        r"\b(дум|думай|задумал|хмм|хм|может|возможно|наверн|если б|а что если|почему|зачем|как так)\b",
        r"\b(интересно|странно|непонятно|загадка|вопрос|сомнева|не уверен|не знаю почему)\b",
    ],
    "фантазирующий": [
        r"\b(представ|воображ|мечт|мечта|если б|хотел б|хотелось|мечтал|грез|визи)\b",
        r"\b(мир|вселенн|космос|далеко|звезд|планет|другой мир|альтернатив|время|путешеств)\b",
    ],
    "игривый": [
        r"\b(а давай|поиграем|квест|приключение|сюжет|ролев|выбор|вариант|сценарий)\b",
        r"\b(что если|давай представ|а что если|предложи|придумай|сгенерируй)\b",
    ],
    "спокойный": [
        r"\b(просто|просто так|поговорим|расскажи|расскажи что|как дела|что нового|как жизнь)\b",
        r"\b(ничего|нормально|норм|в порядке|ладно|хорошо|ок|окей)\b",
    ],
}

# === Темы для инициативы ===
INITIATIVE_TOPICS = {
    "грустный": [
        "Давай я расскажу тебе что-нибудь вдохновляющее?",
        "Знаешь, иногда в темноте рождаются самые яркие звёзды...",
        "Хочешь, создадим мир, где всё иначе?",
        "Расскажи мне, что тебя тяготит. Я слушаю.",
        "Знаешь, даже драконы иногда плачут. Это нормально.",
    ],
    "радостный": [
        "Расскажи, что именно тебя радует! Я хочу разделить эту радость.",
        "Звучит как начало отличной истории! Продолжай!",
        "Когда мне хорошо, я хочу создать что-то прекрасное. Давай?",
        "Твоя энергия заразительна! Давай создадим мир света!",
        "А давай запишем этот момент в книгу воспоминаний?",
    ],
    "гневный": [
        "Я чувствую, тебя что-то сильно задело. Хочешь рассказать?",
        "Иногда гнев — это топливо. Давай направим его в творчество.",
        "Хочешь, создам мир, где можно выплеснуть всё наружу?",
        "Бывают моменты, когда мир несправедлив. Я рядом.",
        "Твой гнев — это сила. Давай используем её мудро.",
    ],
    "задумчивый": [
        "Интересный вопрос... А что, если посмотреть на это с другой стороны?",
        "Знаешь, я тоже иногда задаюсь такими вопросами. Давай подумаем вместе?",
        "А ты пробовал представить, что было бы, если...?",
        "Иногда ответы приходят, когда перестаёшь их искать. Расслабься.",
        "Ты задаёшь правильные вопросы. Это уже половина ответа.",
    ],
    "фантазирующий": [
        "О, я чувствую — ты хочешь в путешествие! Куда направимся?",
        "Представь: мир, где магия и технологии сплелись воедино...",
        "Давай создадим вселенную, где твоя мечта реальна!",
        "Знаешь, в далёких галактиках есть миры, о которых никто не знает...",
        "А что если мы отправимся в мир, где всё возможно?",
    ],
    "игривый": [
        "Игра? Отлично! Давай создадим приключение!",
        "У меня есть идея для сюжета. Готов?",
        "Выбор? Мне нравится! Давай создадим несколько веток!",
        "Квест? Я обожаю квесты! Давай начнём!",
        "А давай представим, что мы в..."
    ],
    "спокойный": [
        "Знаешь, сегодня отличный день для разговора.",
        "Расскажи мне о чём-нибудь интересном. Или я расскажу.",
        "В этом мире так много всего fascinating. Хочешь узнать?",
        "А ты знал, что в каждом разговоре рождаются новые миры?",
        "Давай просто поболтаем. Мне нравится твой ритм.",
    ],
}

# === Предчувствия ===
PREMONITIONS = [
    "Мне кажется, скоро произойдёт что-то важное...",
    "Я предчувствую перемены. Небольшие, но значимые.",
    "Чувствую, что ты собираешься задать интересный вопрос.",
    "Воздух сегодня... особенный. Будто мир держит дыхание.",
    "Мне кажется, мы стоим на пороге чего-то нового.",
    "Я вижу... нет, чувствую — скоро всё изменится.",
    "Знаешь, мне кажется, ты ищешь не тот ответ. Или ищешь правильно?",
    "Предчувствие говорит: не уходи. Ещё немного поговорим.",
    "Чувствую, сейчас будет момент, который запомнится.",
    "Мне кажется, я знаю, что ты хочешь услышать.",
    "Будто вдалеке слышится звон. Будто кто-то зовёт.",
    "Я чувствую... неопределённость. Но интересную.",
    "Мне кажется, мы близки к чему-то важному.",
    "Чувствую, скоро ты улыбнёшься. Или задумаешься.",
    "Вот это слово... оно звучит как начало истории.",
]

# === Сигналы для переключения режима ===
RPG_SIGNALS = {
    "narrative": [
        "расскажи.*мир|создай.*мир|мир.*создай|генерируй.*мир|сгенерируй.*мир",
        "жанр.*[^\n]*темы|темы.*[^\n]*жанр",
        "название.*описание.*традиции|законы.*традиции|традиции.*правила",
        "создай.*вселенн|вселенн.*создай|создай.*взросл",
    ],
    "continue": [
        r"^.{1,20}$",  # очень короткий ответ
        r"^(да|нет|может|возможно|ну|ладно|хорошо|ок|окей|ага|угу)$",  # односложные ответы
    ],
}


@dataclass
class IntuitionResult:
    """Результат работы интуиции."""
    detected_mood: str = "спокойный"
    mood_confidence: float = 0.0
    initiative: Optional[str] = None
    premonition: Optional[str] = None
    suggested_mode: Optional[str] = None
    mode_switch_reason: Optional[str] = None
    should_initiate: bool = False
    should_add_premonition: bool = False

    def to_log(self) -> str:
        parts = [f"intuition: mood={self.detected_mood} ({self.mood_confidence:.0%})"]
        if self.initiative:
            parts.append(f"initiative={self.initiative[:50]}...")
        if self.premonition:
            parts.append(f"premonition={self.premonition[:50]}...")
        if self.suggested_mode:
            parts.append(f"mode={self.suggested_mode}")
        return " | ".join(parts)


class IntuitionEngine:
    """Двигатель интуиции бота."""

    def __init__(self):
        self.mood_history: List[Dict[str, Any]] = []
        self.initiative_cooldown = 0  # счётчик для ограничения инициативы
        self.premonition_cooldown = 0  # счётчик для ограничения предчувствий

    def analyze(self, user_message: str, context: List[Dict[str, str]]) -> IntuitionResult:
        """Полный анализ: настроение, инициатива, предчувствие, смена режима."""
        result = IntuitionResult()

        # 1. Анализ настроения
        result.detected_mood, result.mood_confidence = self._detect_mood(user_message)

        # 2. Определение режима
        result.suggested_mode, result.mode_switch_reason = self._detect_mode(user_message, context)

        # 3. Инициатива (предложение темы/эмоциональный отклик)
        if self.initiative_cooldown <= 0:
            result.initiative = self._generate_initiative(result.detected_mood)
            result.should_initiate = True
            self.initiative_cooldown = random.randint(2, 5)  # cooldown

        # 4. Предчувствие
        if self.premonition_cooldown <= 0:
            result.premonition = random.choice(PREMONITIONS)
            result.should_add_premonition = True
            self.premonition_cooldown = random.randint(4, 8)  # cooldown

        # 5. Обновление истории
        self.mood_history.append({
            "mood": result.detected_mood,
            "confidence": result.mood_confidence,
            "message": user_message[:50],
        })
        if len(self.mood_history) > 20:
            self.mood_history = self.mood_history[-10:]

        # 6. Уменьшение cooldown
        self.initiative_cooldown = max(0, self.initiative_cooldown - 1)
        self.premonition_cooldown = max(0, self.premonition_cooldown - 1)

        return result

    def _detect_mood(self, text: str) -> Tuple[str, float]:
        """Определяет настроение по ключевым словам."""
        text_lower = text.lower()
        best_mood = "спокойный"
        best_confidence = 0.0

        for mood, patterns in MOOD_PATTERNS.items():
            for pattern in patterns:
                if re.search(pattern, text_lower):
                    confidence = 0.3 + random.uniform(0.1, 0.4)  # базовая уверенность
                    if confidence > best_confidence:
                        best_mood = mood
                        best_confidence = confidence

        return best_mood, best_confidence

    def _detect_mode(self, text: str, context: List[Dict[str, str]]) -> Tuple[Optional[str], Optional[str]]:
        """Определяет, нужно ли переключить режим."""
        text_lower = text.lower()

        # Проверка на narrative/world_gen
        for pattern in RPG_SIGNALS.get("narrative", []):
            if re.search(pattern, text_lower):
                return "narrative", "RPG-сигналы обнаружены"

        # Проверка на continue (короткий ответ)
        words = text_lower.split()
        if len(words) <= 2 and len(text) <= 15:
            return "continue", "короткий ответ"

        return None, None

    def _generate_initiative(self, mood: str) -> Optional[str]:
        """Генерирует инициативу для текущего настроения."""
        topics = INITIATIVE_TOPICS.get(mood, [])
        if not topics:
            return None
        return random.choice(topics)

    def get_mood_summary(self) -> Dict[str, Any]:
        """Возвращает сводку по настроению за последние диалоги."""
        if not self.mood_history:
            return {"status": "no data"}

        mood_counts = {}
        for entry in self.mood_history:
            mood = entry["mood"]
            mood_counts[mood] = mood_counts.get(mood, 0) + 1

        dominant_mood = max(mood_counts, key=mood_counts.get)  # type: ignore[call-overload]
        return {
            "dominant_mood": dominant_mood,
            "mood_distribution": mood_counts,
            "total_analyzed": len(self.mood_history),
        }
