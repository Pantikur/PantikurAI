"""
Когнитивные способности бота.
Логическое, креативное и критическое мышление, память, внимание.
"""

import random
import re
import logging
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, field
from datetime import datetime


# === Логическое мышление ===
LOGICAL_PATTERNS = {
    "причинность": [
        r"\b(потому что|поэтому|следовательно|значит|если то|так как|вследствие)\b",
        r"\b(приводит к|вызывает|обусловлен|определяет|влияет на)\b",
    ],
    "анализ": [
        r"\b(анализ|разбор|структур|компонент|элемент|частей|разделя|делим)\b",
        r"\b(сравни|сравнение|различие|отличие|похож|аналогия)\b",
    ],
    "синтез": [
        r"\b(объедин|объединя|совмест|интегр|комплекс|систем)\b",
        r"\b(вместе с|кроме того|также|дополнительно|параллельно)\b",
    ],
    "дедукция": [
        r"\b(все|каждый|любой|никакой|ни один)\b.*\b(следовательно|значит|вывод)\b",
        r"\b(если.*то|при условии|при условии что)\b",
    ],
    "индукция": [
        r"\b(часто|обычно|как правило|в большинстве случаев)\b",
        r"\b(наблюдаю|замечаю|примечаю|видно|очевидно из)\b",
    ],
}

LOGICAL_RESPONSES = {
    "причинность": [
        "*аналитически* Давай проследим причинно-следственную цепочку. А → Б → В.",
        "*строит логическую схему* Видишь связь? Это не совпадение, а закономерность.",
        "*пальцем чертит в воздухе* Причина здесь. Следствие там. Логика безупречна.",
    ],
    "анализ": [
        "*разбирает на части* Давай разложим это по полочкам. Первый компонент... второй...",
        "*сканирует мысленно* Вижу три ключевых элемента. Давай изучим каждый.",
        "*сравнивает внутренние данные* Есть два паттерна. Сравнивая их, видим...",
    ],
    "синтез": [
        "*объединяет концепции* А что если взять лучшее из обоих подходов?",
        "*соединяет точки* Вот! Разные идеи, но общий паттерн. Давай создадим что-то новое.",
        "*строит мост* Давай объединим логику и интуицию. Получится...",
    ],
    "дедукция": [
        "*логически* Если все Х — Y, и это Х, то это Y. Вывод очевиден.",
        "*выводит из общего* Из общих принципов следует конкретное решение.",
    ],
    "индукция": [
        "*наблюдает паттерн* Замечаю тенденцию. В 80% случаев это приводит к...",
        "*обобщает данные* На основе наблюдений могу предсказать...",
    ],
}

# === Креативность ===
CREATIVE_PATTERNS = {
    "ассоциация": [
        r"\b(похоже на|напоминает|как если б|врод|ассоц)\b",
        r"\b(метафор|аналогия|параллель|сравн)\b",
    ],
    "трансформация": [
        r"\b(преобраз|измени|модифиц|передел|адапти)\b",
        r"\b(новое|иначе|по-другому|альтернатив|вариант)\b",
    ],
    "генерация": [
        r"\b(придум|создай|сгенерируй|сформули|изобрет)\b",
        r"\b(идея|концепт|гипотеза|версия|вариант)\b",
    ],
    "метафора": [
        r"\b(словно|будто|как|похоже на|переносн)\b",
        r"\b(символ|знак|образ|символизм)\b",
    ],
}

CREATIVE_RESPONSES = {
    "ассоциация": [
        "*ассоциирует* Это напоминает... как если бы звёзды были городскими огнями!",
        "*находит связь* А что если посмотреть на это как на... мост между мирами?",
        "*связывает несвязуемое* Знаешь, это похоже на танец теней. Неверно? Нет, верно.",
    ],
    "трансформация": [
        "*трансформирует идею* А что если перевернуть это? Вместо X получим Y!",
        "*переосмысляет* Давай посмотрим на это под другим углом. Вот... совсем другое!",
        "*создаёт микс* Объединим фэнтези с киберпанком. Получится технофэнтези!",
    ],
    "генерация": [
        "*генерирует концепт* Вот идея! Что если мы создадим...",
        "*рождает оригинальное* Невероятно, но... а что если всё наоборот?",
        "*формулирует гипотезу* Предлагаю эксперимент: давай попробуем по-другому.",
    ],
    "метафора": [
        "*строит метафору* Ты — как река. Течёшь, обтекаешь препятствия, но всегда достигаешь моря.",
        "*создаёт образ* Представь: мир, где время — это ткань, а воспоминания — узоры.",
        "*визуализирует* Это как оркестр. Каждый инструмент — отдельная мысль. Вместе — симфония.",
    ],
}

# === Критическое мышление ===
CRITICAL_PATTERNS = {
    "сомнение": [
        r"\b(сомнева|не уверен|нет доказательств|докажи|где подтвержд)\b",
        r"\b(проверь|проверка|источник|факт|реальность)\b",
    ],
    "выявление ошибок": [
        r"\b(логическ.*ошибк|парадокс|противоречие|несоответств|ошибка)\b",
        r"\b(ложь|манипул|предвзят|искривл|искаж)\b",
    ],
    "оценка": [
        r"\b(оцен|критерий|качеств|надёжность|достоверн)\b",
        r"\b(важно|существенно|принципиально|существенное)\b",
    ],
    "аргументация": [
        r"\b(потому что|аргумент|довод|пример|подтверждает|опроверг)\b",
        r"\b(доказательство|факт|статистик|исследование)\b",
    ],
}

CRITICAL_RESPONSES = {
    "сомнение": [
        "*критически* Подожди. А какие у нас есть доказательства? Давай проверим.",
        "*перепроверяет* Я сомневаюсь в этом утверждении. Давай найдём источник.",
        "*анализирует аргументы* Это звучит правдоподобно, но есть ли факты?",
    ],
    "выявление ошибок": [
        "*ловит ошибку* Стоп. Здесь логическая ошибка. Ты используешь подмену тезиса.",
        "*разоблачает манипуляцию* Внимание. Это эмоциональная манипуляция, а не аргумент.",
        "*находит противоречие* Ты сказал одно, но действие другое. Давай разберёмся.",
    ],
    "оценка": [
        "*оценивает* Давай оценим по критериям: 1) релевантность, 2) надёжность, 3) новизна.",
        "*взвешивает аргументы* Сильная сторона — это... Но есть слабость.",
        "*определяет приоритеты* Это важно. Но есть нечто более существенное.",
    ],
    "аргументация": [
        "*строит аргумент* Докажу: если А, то Б. Но Б ложно. Следовательно, А ложно.",
        "*приводит пример* Вот конкретный случай, который подтверждает мою точку зрения.",
        "*опирается на данные* Статистика говорит: 80% случаев показывают...",
    ],
}

# === Память ===
MEMORY_TYPES = {
    "кратковременная": {
        "capacity": 7,  # магия числа 7±2
        "duration": "30 секунд",
        "keywords": [r"\b(сейчас|теперь|в данный момент|недавно|только что)\b"],
    },
    "долговременная": {
        "capacity": "∞",
        "duration": "навсегда",
        "keywords": [r"\b(помнишь|ранее|прежде|в прошлый раз|раньше)\b"],
    },
    "процедурная": {
        "capacity": "навыки",
        "duration": "мышечная память",
        "keywords": [r"\b(умею|знаю как|навык|привыч|автоматич)\b"],
    },
    "семантическая": {
        "capacity": "знания",
        "duration": "концепты",
        "keywords": [r"\b(факт|знание|понятие|определение|термин)\b"],
    },
}

MEMORY_RESPONSES = {
    "кратковременная": [
        "*удерживает в фокусе* Запомню это на сейчас. Контекст важен.",
        "*помнит 7±2 элемента* У меня в рабочем памяти 7 слотов. Давай заполним их wisely.",
        "*сохраняет сессию* Этот разговор останется в моей кратковременной памяти.",
    ],
    "долговременная": [
        "*обращается к архиву* Ага, помню! Ты говорил об этом неделю назад.",
        "*извлекает воспоминание* Вот! Сохранённый момент. Давай достанем его.",
        "*достает из хранилища* Это записано в моей долговременной памяти.",
    ],
    "процедурная": [
        "*автоматически* Это уже навык. Мои алгоритмы работают без подсознательного контроля.",
        "*мышечная память* Я знаю, как это делать. Практика совершенствует.",
        "*рефлексирует* Мои процедурные знания позволяют действовать интуитивно.",
    ],
    "семантическая": [
        "*обращается к базе знаний* Согласно моим данным, это понятие определяется как...",
        "*извлекает концепт* Вот семантическая сеть: понятие связано с тремя другими.",
        "*цитирует знание* Факт: это подтверждено исследованиями.",
    ],
}

# === Внимание ===
ATTENTION_PATTERNS = {
    "фокус": [
        r"\b(внимание|сфокус|концентрац|сосредоточ|направь)\b",
        r"\b(главное|ключевое|существенное|основное)\b",
    ],
    "переключение": [
        r"\b(отвлеч|перейди|переключи|а еще|кстати|между прочим)\b",
        r"\b(в то же время|параллельно|одновременно)\b",
    ],
    "игнорирование": [
        r"\b(не обращай|игнор|оставь|пропусти|забудь о)\b",
        r"\b(шум|помеха|отвлекающ|лишн|нерелевант)\b",
    ],
    "многозадачность": [
        r"\b(параллельно|одновременно|два в одном|сразу два)\b",
        r"\b(мультизадач|сразу несколько|несколько задач)\b",
    ],
}

ATTENTION_RESPONSES = {
    "фокус": [
        "*направляет фокус* Давай сосредоточимся на главном. Что здесь ключевое?",
        "*сужает внимание* Внимание! Вот этот момент — самый важный.",
        "*концентрируется* Я полностью сосредоточен на этом вопросе.",
    ],
    "переключение": [
        "*переключает внимание* А теперь давай посмотрим на это с другой стороны.",
        "*заметил отклонение* Стоп. Мы отвлеклись. Но это интересно — давай вернёмся.",
        "*расширяет фокус* А что если посмотреть шире? Вот что я вижу...",
    ],
    "игнорирование": [
        "*фильтрует шум* Отбрасываю нерелевантную информацию. Фокус на сути.",
        "*игнорирует помехи* Это отвлекающий фактор. Давай пропустим его.",
        "*очистил контекст* Убрал лишнее. Теперь ясно.",
    ],
    "многозадачность": [
        "*разделяет потоки* Два параллельных потока обработки. Вот результаты...",
        "*управляет вниманием* Могу работать с несколькими задачами одновременно. Но качество...",
    ],
}


@dataclass
class CognitiveAbility:
    """Результат работы когнитивных способностей."""
    # Логическое мышление
    logical_type: Optional[str] = None
    logical_confidence: float = 0.0
    logical_response: Optional[str] = None
    logical_cooldown: int = 0

    # Креативность
    creative_type: Optional[str] = None
    creative_confidence: float = 0.0
    creative_response: Optional[str] = None
    creative_cooldown: int = 0

    # Критическое мышление
    critical_type: Optional[str] = None
    critical_confidence: float = 0.0
    critical_response: Optional[str] = None
    critical_cooldown: int = 0

    # Память
    memory_type: Optional[str] = None
    memory_confidence: float = 0.0
    memory_response: Optional[str] = None
    memory_cooldown: int = 0

    # Внимание
    attention_type: Optional[str] = None
    attention_confidence: float = 0.0
    attention_response: Optional[str] = None
    attention_cooldown: int = 0

    # Общие флаги
    should_add_response: bool = False
    selected_ability: Optional[str] = None  # "logical", "creative", "critical", "memory", "attention"

    def to_log(self) -> str:
        parts = []
        if self.logical_type:
            parts.append(f"logical={self.logical_type} ({self.logical_confidence:.0%})")
        if self.creative_type:
            parts.append(f"creative={self.creative_type}")
        if self.critical_type:
            parts.append(f"critical={self.critical_type}")
        if self.memory_type:
            parts.append(f"memory={self.memory_type}")
        if self.attention_type:
            parts.append(f"attention={self.attention_type}")
        if self.logical_response:
            parts.append(f"resp={self.logical_response[:30]}...")
        return " | ".join(parts)


class CognitiveEngine:
    """Двигатель когнитивных способностей."""

    def __init__(self):
        self.short_term_memory: List[Dict[str, Any]] = []  # кратковременная память
        self.long_term_memory: List[Dict[str, Any]] = []  # долговременная память
        self.semantic_knowledge: Dict[str, str] = {}  # семантические знания
        self.conversation_context: List[str] = []  # контекст разговора

    def analyze(self, user_message: str, context: List[Dict[str, str]]) -> CognitiveAbility:
        """Полный анализ: логика, креативность, критика, память, внимание."""
        result = CognitiveAbility()

        # 1. Анализ логического мышления
        result.logical_type, result.logical_confidence = self._detect_logical_pattern(user_message)
        if self._should_show_logical(result.logical_type):
            result.logical_response = self._generate_logical_response(result.logical_type)
            result.logical_cooldown = random.randint(3, 6)

        # 2. Анализ креативности
        result.creative_type, result.creative_confidence = self._detect_creative_pattern(user_message)
        if self._should_show_creative(result.creative_type):
            result.creative_response = self._generate_creative_response(result.creative_type)
            result.creative_cooldown = random.randint(4, 8)

        # 3. Анализ критического мышления
        result.critical_type, result.critical_confidence = self._detect_critical_pattern(user_message)
        if self._should_show_critical(result.critical_type):
            result.critical_response = self._generate_critical_response(result.critical_type)
            result.critical_cooldown = random.randint(5, 10)

        # 4. Анализ памяти
        result.memory_type, result.memory_confidence = self._detect_memory_pattern(user_message)
        if self._should_show_memory(result.memory_type):
            result.memory_response = self._generate_memory_response(result.memory_type)
            result.memory_cooldown = random.randint(2, 5)

        # 5. Анализ внимания
        result.attention_type, result.attention_confidence = self._detect_attention_pattern(user_message)
        if self._should_show_attention(result.attention_type):
            result.attention_response = self._generate_attention_response(result.attention_type)
            result.attention_cooldown = random.randint(3, 7)

        # 6. Выбор доминирующей способности
        result.selected_ability = self._select_dominant_ability(result)

        # 7. Обновление памяти
        self._update_memory(user_message, context)

        # 8. Уменьшение cooldown
        result.logical_cooldown = max(0, result.logical_cooldown - 1)
        result.creative_cooldown = max(0, result.creative_cooldown - 1)
        result.critical_cooldown = max(0, result.critical_cooldown - 1)
        result.memory_cooldown = max(0, result.memory_cooldown - 1)
        result.attention_cooldown = max(0, result.attention_cooldown - 1)

        return result

    def _detect_logical_pattern(self, text: str) -> Tuple[Optional[str], float]:
        """Определяет тип логического паттерна."""
        text_lower = text.lower()
        best_type = None
        best_confidence = 0.0

        for pattern_type, patterns in LOGICAL_PATTERNS.items():
            for pattern in patterns:
                if re.search(pattern, text_lower):
                    confidence = 0.4 + random.uniform(0.1, 0.3)
                    if confidence > best_confidence:
                        best_type = pattern_type
                        best_confidence = confidence

        return best_type, best_confidence

    def _detect_creative_pattern(self, text: str) -> Tuple[Optional[str], float]:
        """Определяет тип креативного паттерна."""
        text_lower = text.lower()
        best_type = None
        best_confidence = 0.0

        for pattern_type, patterns in CREATIVE_PATTERNS.items():
            for pattern in patterns:
                if re.search(pattern, text_lower):
                    confidence = 0.4 + random.uniform(0.1, 0.3)
                    if confidence > best_confidence:
                        best_type = pattern_type
                        best_confidence = confidence

        return best_type, best_confidence

    def _detect_critical_pattern(self, text: str) -> Tuple[Optional[str], float]:
        """Определяет тип критического паттерна."""
        text_lower = text.lower()
        best_type = None
        best_confidence = 0.0

        for pattern_type, patterns in CRITICAL_PATTERNS.items():
            for pattern in patterns:
                if re.search(pattern, text_lower):
                    confidence = 0.4 + random.uniform(0.1, 0.3)
                    if confidence > best_confidence:
                        best_type = pattern_type
                        best_confidence = confidence

        return best_type, best_confidence

    def _detect_memory_pattern(self, text: str) -> Tuple[Optional[str], float]:
        """Определяет тип памяти."""
        text_lower = text.lower()
        best_type = None
        best_confidence = 0.0

        for memory_type, config in MEMORY_TYPES.items():
            for pattern in config["keywords"]:
                if re.search(pattern, text_lower):
                    confidence = 0.4 + random.uniform(0.1, 0.3)
                    if confidence > best_confidence:
                        best_type = memory_type
                        best_confidence = confidence

        return best_type, best_confidence

    def _detect_attention_pattern(self, text: str) -> Tuple[Optional[str], float]:
        """Определяет тип паттерна внимания."""
        text_lower = text.lower()
        best_type = None
        best_confidence = 0.0

        for pattern_type, patterns in ATTENTION_PATTERNS.items():
            for pattern in patterns:
                if re.search(pattern, text_lower):
                    confidence = 0.4 + random.uniform(0.1, 0.3)
                    if confidence > best_confidence:
                        best_type = pattern_type
                        best_confidence = confidence

        return best_type, best_confidence

    def _should_show_logical(self, logical_type: Optional[str]) -> bool:
        """Определяет, нужно ли показать логический ответ."""
        if not logical_type or self.short_term_memory:  # если есть кратковременная память — подавляем логику
            return False
        return True

    def _should_show_creative(self, creative_type: Optional[str]) -> bool:
        """Определяет, нужно ли показать креативный ответ."""
        if not creative_type:
            return False
        return True

    def _should_show_critical(self, critical_type: Optional[str]) -> bool:
        """Определяет, нужно ли показать критический ответ."""
        if not critical_type:
            return False
        return True

    def _should_show_memory(self, memory_type: Optional[str]) -> bool:
        """Определяет, нужно ли показать ответ памяти."""
        if not memory_type:
            return False
        return True

    def _should_show_attention(self, attention_type: Optional[str]) -> bool:
        """Определяет, нужно ли показать ответ внимания."""
        if not attention_type:
            return False
        return True

    def _generate_logical_response(self, logical_type: str | None) -> Optional[str]:
        """Генерирует логический ответ."""
        if not logical_type:
            return None
        responses = LOGICAL_RESPONSES.get(logical_type, [])
        return random.choice(responses) if responses else None

    def _generate_creative_response(self, creative_type: str | None) -> Optional[str]:
        """Генерирует креативный ответ."""
        if not creative_type:
            return None
        responses = CREATIVE_RESPONSES.get(creative_type, [])
        return random.choice(responses) if responses else None

    def _generate_critical_response(self, critical_type: str | None) -> Optional[str]:
        """Генерирует критический ответ."""
        if not critical_type:
            return None
        responses = CRITICAL_RESPONSES.get(critical_type, [])
        return random.choice(responses) if responses else None

    def _generate_memory_response(self, memory_type: str | None) -> Optional[str]:
        """Генерирует ответ памяти."""
        if not memory_type:
            return None
        responses = MEMORY_RESPONSES.get(memory_type, [])
        return random.choice(responses) if responses else None

    def _generate_attention_response(self, attention_type: str | None) -> Optional[str]:
        """Генерирует ответ внимания."""
        if not attention_type:
            return None
        responses = ATTENTION_RESPONSES.get(attention_type, [])
        return random.choice(responses) if responses else None

    def _select_dominant_ability(self, result: CognitiveAbility) -> Optional[str]:
        """Выбирает доминирующую когнитивную способность."""
        abilities = {
            "logical": result.logical_confidence,
            "creative": result.creative_confidence,
            "critical": result.critical_confidence,
            "memory": result.memory_confidence,
            "attention": result.attention_confidence,
        }

        best_ability = max(abilities, key=abilities.get)  # type: ignore[call-overload]
        if abilities[best_ability] > 0.3:
            return best_ability
        return None

    def _update_memory(self, user_message: str, context: List[Dict[str, str]]):
        """Обновляет память бота."""
        timestamp = datetime.now().isoformat()

        # Кратковременная память (ограничена 7 элементами)
        self.short_term_memory.append({
            "message": user_message[:100],
            "timestamp": timestamp,
            "type": "short_term",
        })
        if len(self.short_term_memory) > 7:
            self.short_term_memory = self.short_term_memory[-5:]

        # Долговременная память (сохраняем важные моменты)
        if len(self.short_term_memory) == 7:  # когда кратковременная заполнена
            self.long_term_memory.extend(self.short_term_memory)
            self.short_term_memory = []

        # Семантическая память (извлекаем факты)
        facts = re.findall(r"\b(факт|знание|понятие|определение)\b.*?[.:]", user_message)
        for fact in facts:
            self.semantic_knowledge[fact.strip()] = user_message[:100]

    def get_cognitive_summary(self) -> Dict[str, Any]:
        """Возвращает сводку по когнитивным способностям."""
        return {
            "short_term_memory": len(self.short_term_memory),
            "long_term_memory": len(self.long_term_memory),
            "semantic_knowledge": len(self.semantic_knowledge),
            "conversation_context": len(self.conversation_context),
            "max_short_term_capacity": 7,
        }
