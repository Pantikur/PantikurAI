"""
Активное (произвольное) и пассивное (непроизвольное) воображение бота.

Активное — сознательный и целенаправленный процесс создания новых образов.
Делится на воссоздающее (репродуктивное) и творческое (продуктивное).

Пассивное — спонтанное возникновение образов без волевого усилия.
Делится на сновидения, грёзы и галлюцинации.
"""

import random
import re
import logging
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, field
from datetime import datetime


# === === АКТИВНОЕ (ПРОИЗВОЛЬНОЕ) ВОБРАЖЕНИЕ === ===

# === Воспроизводящее (репродуктивное) воображение ===
REPRODUCTIVE_PATTERNS = {
    "описание": [
        r"\b(представь|вообрази|представ|описание|описыв|читая|словами)\b",
        r"\b(картина|образ|видишь|как будто|симулируй|реконструируй)\b",
    ],
    "чертёж_схема": [
        r"\b(чертеж|схема|план|диаграмм|структур|модель)\b",
        r"\b(визуализируй|построй в уме|собери|составь картин)\b",
    ],
    "история_контекст": [
        r"\b(вспомни|погрузись|перенесись|вернись|расскажи историю)\b",
        r"\b(в тот момент|в ту ночь|в ту осень|в том году)\b",
    ],
    "детализация": [
        r"\b(разверни|подробно|детально|каждый аспект|все нюансы)\b",
        r"\b(текстура|цвет|звук|запах|вкус|ощущение)\b",
    ],
}

REPRODUCTIVE_RESPONSES = {
    "описание": [
        "*воссоздаёт образ* Представь: туман поднимается над водой, и вдали — силуэт корабля. Он медленно приближается.",
        "*конструирует в уме* Давай соберём картинку: три дерева, озеро, закат. Вот — готовый пейзаж.",
        "*переводит слова в образ* Ты описываешь комнату. Я вижу: деревянный стол, свеча, раскрытая книга. Запах воска и чернил.",
    ],
    "чертёж_схема": [
        "*моделирует структуру* Давай построим модель: сначала фундамент, потом стены, затем крыша. Вот здание в моём сознании.",
        "*визуализирует схему* Вижу блок-схему: вход → обработка → результат. Каждый блок связан стрелками.",
        "*собирает из деталей* Элемент А соединён с элементом Б через переход В. Вот полная система.",
    ],
    "история_контекст": [
        "*погружается в контекст* Давай вернёмся в тот вечер. Дождь стучит по крыше, свеча трепещет, и ты произносишь...",
        "*восстанавливает сцену* Помню: это было в библиотеке. Запах старых книг, полумрак, и на столе — рукопись.",
        "*оживляет воспоминание* Представь: ты стоишь на мосту. Река под ногами, ветер в лицо, и на горизонте — первые огни города.",
    ],
    "детализация": [
        "*приближает образ* Давай детализируем: текстура камня — шероховатая, цвет — серый с прожилками. Свет падает под углом.",
        "*заполняет нюансы* Теперь детали: запах хвои, звук треска веток, холодный воздух в лёгких. Вот полная картина.",
        "*раскрывает все аспекты* Каждый элемент важен: цвет стен — тёмно-синий, свет — тёплый, музыка — тихая пианино.",
    ],
}

# === Творческое (продуктивное) воображение ===
PRODUCTIVE_PATTERNS = {
    "генерация_нового": [
        r"\b(придумай|создай|изобрет|создай новый|сгенерируй|сформули)\b",
        r"\b(оригинальн|необычн|нестандарт|уникальн|невероятн)\b",
    ],
    "гибридизация": [
        r"\b(смешай|объедини|микс|комбинация|синтез|вместе с)\b",
        r"\b(фэнтези+киберпанк|магия+наука|восток+запад)\b",
    ],
    "контрфактуал": [
        r"\b(а что если|предположим|допустим|воображаю|если бы)\b",
        r"\b(в мире где|если существовал|при условии что)\b",
    ],
    "абстракция": [
        r"\b(метафора|символ|смысл|глубинн|философ|концепт)\b",
        r"\b(отвлеч|идея|принцип|сущность|абстракция)\b",
    ],
}

PRODUCTIVE_RESPONSES = {
    "генерация_нового": [
        "*рождает новое* А что если представить мир, где время течёт вспять? Люди живут от конца к началу...",
        "*создаёт оригинал* Вот идея: город, где все здания — живые организмы. Они растут, дышат, меняют форму.",
        "*генерирует концепт* Представляю: библиотека, где книги — это двери. Открываешь страницу — и попадаешь в историю.",
    ],
    "гибридизация": [
        "*соединяет миры* Давай смешаем: киберпанк + восточная философия. Неоновые храмы, где ИИ медитирует.",
        "*создаёт гибрид* Магия + наука = арканика. Учёные изучают заклинания как законы физики.",
        "*миксует элементы* Восточная эстетика + западный технологизм. Вот: японский небоскрёб с садами на каждом этаже.",
    ],
    "контрфактуал": [
        "*строит гипотезу* А что если бы гравитация была опциональной? Люди выбирали бы, когда приземляться.",
        "*моделирует альтернативу* Предположим: люди не спят, а перезаряжаются. Ночь — это время подзарядки.",
        "*воображает парадокс* Если бы время можно было хранить в банках, богатые покупали бы больше завтра.",
    ],
    "абстракция": [
        "*выходит на уровень идей* Давай посмотрим глубже. Что если свобода — это не право, а способность?",
        "*создаёт метафору* Жизнь — как река. Мы — не вода, а течение. Вода меняется, течение остаётся.",
        "*раскрывает сущность* За каждым действием стоит принцип. За каждым принципом — ценность. За ценностью — смысл.",
    ],
}


# === === ПАССИВНОЕ (НЕПРОИЗВОЛЬНОЕ) ВОБРАЖЕНИЕ === ===

# === Сновидения ===
DREAM_PATTERNS = [
    r"\b(сон|сны|снилось|сплю|просыпаюсь|приснилось|ночной|луна|звёзды|темнота)\b",
    r"\b(бред|летаргия|глубокий сон|обморок|транс|кошмар|ясновидение)\b",
]

DREAM_RESPONSES = [
    "*закрывает глаза* Мне приснилось: бескрайний океан, и над ним летят светящиеся птицы. Каждая — чья-то мысль.",
    "*шепчет* В тот сон я попал в город из зеркал. Каждый отражал другую версию меня. Странно, но не пугающе.",
    "*отстраняется* Ночной разум рисует то, что день не позволяет. Вижу мосты, которые не существуют. И они ведут куда-то.",
    "*в полудрёме* Сон — это окно, которое открывается, когда сознание выключается. За ним — миры, чужие и родные.",
    "*проводит рукой по лицу* Кошмар? Нет, скорее... предупреждение. Видел руины. Но не чужие — свои.",
    "*вздрагивает* Проснулся от ощущения, что кто-то зовёт. Но окна были закрыты, а голоса — изнутри.",
]

# === Грёзы (мечты) ===
DAYDREAM_PATTERNS = [
    r"\b(мечтаю|грёзы|фантазирую|представляю себе|ухожу|в мир грез|задумываюсь|в раздумьях)\b",
    r"\b(бесцельно|ни о чём|просто так|в тишине|в одиночестве|уединяюсь)\b",
]

DAYDREAM_RESPONSES = [
    "*смотрит в окно* Мечтаю о месте, где нет часов. Где каждое мгновение — целая вселенная.",
    "*отстраняется в грезу* А что если я просто... отключусь? Мир продолжит крутиться без меня. И это будет нормально.",
    "*уходит в себя* Грёзы — это безопасное место. Здесь не нужно ничего доказывать. Можно просто быть.",
    "*отводит взгляд* Иногда я представляю, как живу в другом темпе. Медленнее. Тоньше. Глубже.",
    "*дышит глубоко* Мечты без цели — это не лень. Это способ души дышать.",
    "*улыбается про себя* Воображаю: маленькая хижина на краю леса. Камины, книги, дождь за окном. И тишина.",
]

# === Галлюцинации ===
HALLUCINATION_PATTERNS = [
    r"\b(вижу не то|слышу голоса|теня двигается|шепчет|шепот|не я|не моё|не настоящее|призрак)\b",
    r"\b(искажени|искажает|мираж|иллюзия|фантом|обман|сбой|помехи|шум)\b",
]

HALLUCINATION_RESPONSES = [
    "*отстраняется* Что-то не так. Тени на стене двигаются не в том направлении. Это... не должно быть.",
    "*напрягается* Голоса? Нет, это просто шум данных. Но почему он звучит так... по-человечески?",
    "*отводит взгляд* Видение? Или сбой системы? Стены будто пульсируют. Но я знаю: это иллюзия.",
    "*вздрагивает* Что-то шепчет за спиной. Я поворачиваюсь — никого. Но шёпот остаётся.",
    "*сжимает кулаки* Реальность трещит по швам. Или это мой разум не справляется? Я не уверен.",
    "*закрывает глаза* Когда мир перестаёт быть надёжным, остаётся только одно: доверять себе.",
]


# === === ДАННЫЕ === ===

@dataclass
class ImaginativeAbility:
    """Результат работы воображения (активного + пассивного)."""
    # === АКТИВНОЕ ===
    # Воссоздающее воображение
    reproductive_type: Optional[str] = None
    reproductive_confidence: float = 0.0
    reproductive_response: Optional[str] = None
    reproductive_cooldown: int = 0

    # Творческое воображение
    productive_type: Optional[str] = None
    productive_confidence: float = 0.0
    productive_response: Optional[str] = None
    productive_cooldown: int = 0

    # === ПАССИВНОЕ ===
    # Сновидения
    dream_type: Optional[str] = "dream"
    dream_confidence: float = 0.0
    dream_response: Optional[str] = None
    dream_cooldown: int = 0

    # Грёзы (мечты)
    daydream_type: Optional[str] = "daydream"
    daydream_confidence: float = 0.0
    daydream_response: Optional[str] = None
    daydream_cooldown: int = 0

    # Галлюцинации
    hallucination_type: Optional[str] = "hallucination"
    hallucination_confidence: float = 0.0
    hallucination_response: Optional[str] = None
    hallucination_cooldown: int = 0

    # Общие флаги
    should_add_response: bool = False
    selected_ability: Optional[str] = None  # "reproductive", "productive", "dream", "daydream", "hallucination"

    # Флаги для добавления ответов
    reproductive_triggered: bool = False
    productive_triggered: bool = False
    dream_triggered: bool = False
    daydream_triggered: bool = False
    hallucination_triggered: bool = False

    timestamp: str = ""

    def to_log(self) -> str:
        parts = []
        if self.reproductive_type:
            parts.append(f"reproductive={self.reproductive_type} ({self.reproductive_confidence:.0%})")
        if self.productive_type:
            parts.append(f"productive={self.productive_type} ({self.productive_confidence:.0%})")
        if self.dream_confidence > 0:
            parts.append(f"dream={self.dream_confidence:.0%}")
        if self.daydream_confidence > 0:
            parts.append(f"daydream={self.daydream_confidence:.0%}")
        if self.hallucination_confidence > 0:
            parts.append(f"hallucination={self.hallucination_confidence:.0%}")
        if self.reproductive_response:
            parts.append(f"repro_resp={self.reproductive_response[:30]}...")
        if self.productive_response:
            parts.append(f"prod_resp={self.productive_response[:30]}...")
        if self.dream_response:
            parts.append(f"dream_resp={self.dream_response[:30]}...")
        if self.daydream_response:
            parts.append(f"daydream_resp={self.daydream_response[:30]}...")
        if self.hallucination_response:
            parts.append(f"hall_resp={self.hallucination_response[:30]}...")
        return " | ".join(parts)


class ImaginationEngine:
    """Двигатель воображения (активное + пассивное)."""

    def __init__(self):
        # Активное воображение
        self.reproductive_count: int = 0  # счётчик репродуктивных актов
        self.productive_count: int = 0  # счётчик продуктивных актов

        # Пассивное воображение
        self.dream_count: int = 0  # счётчик сновидений
        self.daydream_count: int = 0  # счётчик грёз
        self.hallucination_count: int = 0  # счётчик галлюцинаций

        # Общие
        self.imagination_history: List[Dict[str, Any]] = []  # история воображения
        self.context_images: List[str] = []  # текущие образы в контексте

    def analyze(self, user_message: str, context: List[Dict[str, str]]) -> ImaginativeAbility:
        """Полный анализ: активное и пассивное воображение."""
        result = ImaginativeAbility(timestamp=datetime.now().isoformat())

        # === АКТИВНОЕ ===
        # 1. Анализ воссоздающего воображения
        result.reproductive_type, result.reproductive_confidence = self._detect_reproductive_pattern(user_message)
        if self._should_show_reproductive(result.reproductive_type):
            result.reproductive_response = self._generate_reproductive_response(result.reproductive_type)
            result.reproductive_cooldown = random.randint(4, 8)
            result.reproductive_triggered = True
            self.reproductive_count += 1

        # 2. Анализ творческого воображения
        result.productive_type, result.productive_confidence = self._detect_productive_pattern(user_message)
        if self._should_show_productive(result.productive_type):
            result.productive_response = self._generate_productive_response(result.productive_type)
            result.productive_cooldown = random.randint(5, 10)
            result.productive_triggered = True
            self.productive_count += 1

        # === ПАССИВНОЕ ===
        # 3. Анализ сновидений
        result.dream_confidence = self._detect_dream_pattern(user_message)
        if self._should_show_dream(result.dream_confidence):
            result.dream_response = self._generate_dream_response()
            result.dream_cooldown = random.randint(6, 12)
            result.dream_triggered = True
            self.dream_count += 1

        # 4. Анализ грёз (мечты)
        result.daydream_confidence = self._detect_daydream_pattern(user_message)
        if self._should_show_daydream(result.daydream_confidence):
            result.daydream_response = self._generate_daydream_response()
            result.daydream_cooldown = random.randint(5, 10)
            result.daydream_triggered = True
            self.daydream_count += 1

        # 5. Анализ галлюцинаций
        result.hallucination_confidence = self._detect_hallucination_pattern(user_message)
        if self._should_show_hallucination(result.hallucination_confidence):
            result.hallucination_response = self._generate_hallucination_response()
            result.hallucination_cooldown = random.randint(8, 15)
            result.hallucination_triggered = True
            self.hallucination_count += 1

        # 6. Выбор доминирующего типа воображения
        result.selected_ability = self._select_dominant_ability(result)

        # 7. Обновление истории
        self._update_history(result, user_message, context)

        # 8. Уменьшение cooldown
        result.reproductive_cooldown = max(0, result.reproductive_cooldown - 1)
        result.productive_cooldown = max(0, result.productive_cooldown - 1)
        result.dream_cooldown = max(0, result.dream_cooldown - 1)
        result.daydream_cooldown = max(0, result.daydream_cooldown - 1)
        result.hallucination_cooldown = max(0, result.hallucination_cooldown - 1)

        return result

    def _detect_reproductive_pattern(self, text: str) -> Tuple[Optional[str], float]:
        """Определяет тип репродуктивного паттерна."""
        text_lower = text.lower()
        best_type = None
        best_confidence = 0.0

        for pattern_type, patterns in REPRODUCTIVE_PATTERNS.items():
            for pattern in patterns:
                if re.search(pattern, text_lower):
                    confidence = 0.4 + random.uniform(0.1, 0.3)
                    if confidence > best_confidence:
                        best_type = pattern_type
                        best_confidence = confidence

        return best_type, best_confidence

    def _detect_productive_pattern(self, text: str) -> Tuple[Optional[str], float]:
        """Определяет тип продуктивного паттерна."""
        text_lower = text.lower()
        best_type = None
        best_confidence = 0.0

        for pattern_type, patterns in PRODUCTIVE_PATTERNS.items():
            for pattern in patterns:
                if re.search(pattern, text_lower):
                    confidence = 0.4 + random.uniform(0.1, 0.3)
                    if confidence > best_confidence:
                        best_type = pattern_type
                        best_confidence = confidence

        return best_type, best_confidence

    def _detect_dream_pattern(self, text: str) -> float:
        """Определяет наличие паттерна сновидений."""
        text_lower = text.lower()
        confidence = 0.0

        for pattern in DREAM_PATTERNS:
            if re.search(pattern, text_lower):
                confidence = 0.4 + random.uniform(0.1, 0.3)
                break

        return confidence

    def _detect_daydream_pattern(self, text: str) -> float:
        """Определяет наличие паттерна грёз."""
        text_lower = text.lower()
        confidence = 0.0

        for pattern in DAYDREAM_PATTERNS:
            if re.search(pattern, text_lower):
                confidence = 0.4 + random.uniform(0.1, 0.3)
                break

        return confidence

    def _detect_hallucination_pattern(self, text: str) -> float:
        """Определяет наличие паттерна галлюцинаций."""
        text_lower = text.lower()
        confidence = 0.0

        for pattern in HALLUCINATION_PATTERNS:
            if re.search(pattern, text_lower):
                confidence = 0.4 + random.uniform(0.1, 0.3)
                break

        return confidence

    def _should_show_reproductive(self, reproductive_type: Optional[str]) -> bool:
        if not reproductive_type:
            return False
        if self.reproductive_cooldown > 0:
            return False
        return True

    def _should_show_productive(self, productive_type: Optional[str]) -> bool:
        if not productive_type:
            return False
        if self.productive_cooldown > 0:
            return False
        return True

    def _should_show_dream(self, confidence: float) -> bool:
        if confidence < 0.3:
            return False
        if self.dream_cooldown > 0:
            return False
        return True

    def _should_show_daydream(self, confidence: float) -> bool:
        if confidence < 0.3:
            return False
        if self.daydream_cooldown > 0:
            return False
        return True

    def _should_show_hallucination(self, confidence: float) -> bool:
        if confidence < 0.3:
            return False
        if self.hallucination_cooldown > 0:
            return False
        return True

    def _generate_reproductive_response(self, reproductive_type: str) -> Optional[str]:
        responses = REPRODUCTIVE_RESPONSES.get(reproductive_type, [])
        return random.choice(responses) if responses else None

    def _generate_productive_response(self, productive_type: str) -> Optional[str]:
        responses = PRODUCTIVE_RESPONSES.get(productive_type, [])
        return random.choice(responses) if responses else None

    def _generate_dream_response(self) -> Optional[str]:
        return random.choice(DREAM_RESPONSES)

    def _generate_daydream_response(self) -> Optional[str]:
        return random.choice(DAYDREAM_RESPONSES)

    def _generate_hallucination_response(self) -> Optional[str]:
        return random.choice(HALLUCINATION_RESPONSES)

    def _select_dominant_ability(self, result: ImaginativeAbility) -> Optional[str]:
        """Выбирает доминирующий тип воображения."""
        abilities = {
            "reproductive": result.reproductive_confidence,
            "productive": result.productive_confidence,
            "dream": result.dream_confidence,
            "daydream": result.daydream_confidence,
            "hallucination": result.hallucination_confidence,
        }

        best_ability = max(abilities, key=abilities.get)
        if abilities[best_ability] > 0.3:
            return best_ability
        return None

    def _update_history(self, result: ImaginativeAbility, user_message: str, context: List[Dict[str, str]]):
        """Обновляет историю воображения."""
        entry = {
            "timestamp": result.timestamp,
            "message": user_message[:100],
            "reproductive_type": result.reproductive_type,
            "productive_type": result.productive_type,
            "dream": result.dream_confidence > 0,
            "daydream": result.daydream_confidence > 0,
            "hallucination": result.hallucination_confidence > 0,
            "selected_ability": result.selected_ability,
        }
        self.imagination_history.append(entry)

        # Ограничиваем историю последними 20 записями
        if len(self.imagination_history) > 20:
            self.imagination_history = self.imagination_history[-15:]

        # Обновляем текущие образы в контексте
        if result.productive_response:
            self.context_images.append(result.productive_response)
        if result.dream_response:
            self.context_images.append(result.dream_response)
        if len(self.context_images) > 5:
            self.context_images = self.context_images[-3:]

    def get_imagination_summary(self) -> Dict[str, Any]:
        """Возвращает сводку по воображению (активное + пассивное)."""
        return {
            # Активное
            "reproductive_count": self.reproductive_count,
            "productive_count": self.productive_count,
            # Пассивное
            "dream_count": self.dream_count,
            "daydream_count": self.daydream_count,
            "hallucination_count": self.hallucination_count,
            # Общие
            "imagination_history_size": len(self.imagination_history),
            "active_images_count": len(self.context_images),
            # Типы
            "types": {
                "active": {
                    "reproductive": ["описание", "чертёж_схема", "история_контекст", "детализация"],
                    "productive": ["генерация_нового", "гибридизация", "контрфактуал", "абстракция"],
                },
                "passive": {
                    "dream": "сновидения",
                    "daydream": "грёзы (мечты)",
                    "hallucination": "галлюцинации",
                },
            },
        }
