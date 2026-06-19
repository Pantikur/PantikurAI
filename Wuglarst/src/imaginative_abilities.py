"""
Активное (произвольное) воображение бота.
Сознательный и целенаправленный процесс создания новых образов.
Делится на воссоздающее (репродуктивное) и творческое (продуктивное) воображение.
"""

import random
import re
import logging
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, field
from datetime import datetime


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


@dataclass
class ImaginativeAbility:
    """Результат работы активного воображения."""
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

    # Общие флаги
    should_add_response: bool = False
    selected_ability: Optional[str] = None  # "reproductive" или "productive"
    reproductive_triggered: bool = False  # флаг для добавления ответа
    productive_triggered: bool = False  # флаг для добавления ответа
    timestamp: str = ""

    def to_log(self) -> str:
        parts = []
        if self.reproductive_type:
            parts.append(f"reproductive={self.reproductive_type} ({self.reproductive_confidence:.0%})")
        if self.productive_type:
            parts.append(f"productive={self.productive_type} ({self.productive_confidence:.0%})")
        if self.reproductive_response:
            parts.append(f"repro_resp={self.reproductive_response[:30]}...")
        if self.productive_response:
            parts.append(f"prod_resp={self.productive_response[:30]}...")
        return " | ".join(parts)


class ImaginationEngine:
    """Двигатель активного воображения."""

    def __init__(self):
        self.reproductive_count: int = 0  # счётчик репродуктивных актов
        self.productive_count: int = 0  # счётчик продуктивных актов
        self.imagination_history: List[Dict[str, Any]] = []  # история воображения
        self.context_images: List[str] = []  # текущие образы в контексте

    def analyze(self, user_message: str, context: List[Dict[str, str]]) -> ImaginativeAbility:
        """Полный анализ: репродуктивное и продуктивное воображение."""
        result = ImaginativeAbility(timestamp=datetime.now().isoformat())

        # 1. Анализ воссоздающего воображения
        result.reproductive_type, result.reproductive_confidence = self._detect_reproductive_pattern(user_message)
        if self._should_show_reproductive(result.reproductive_type):
            result.reproductive_response = self._generate_reproductive_response(result.reproductive_type)
            result.reproductive_cooldown = random.randint(4, 8)
            result.reproductive_triggered = True  # ← УСТАНОВКА ФЛАГА
            self.reproductive_count += 1

        # 2. Анализ творческого воображения
        result.productive_type, result.productive_confidence = self._detect_productive_pattern(user_message)
        if self._should_show_productive(result.productive_type):
            result.productive_response = self._generate_productive_response(result.productive_type)
            result.productive_cooldown = random.randint(5, 10)
            result.productive_triggered = True  # ← УСТАНОВКА ФЛАГА
            self.productive_count += 1

        # 3. Выбор доминирующего типа воображения
        result.selected_ability = self._select_dominant_ability(result)

        # 4. Обновление истории
        self._update_history(result, user_message, context)

        # 5. Уменьшение cooldown
        result.reproductive_cooldown = max(0, result.reproductive_cooldown - 1)
        result.productive_cooldown = max(0, result.productive_cooldown - 1)

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

    def _should_show_reproductive(self, reproductive_type: Optional[str]) -> bool:
        """Определяет, нужно ли показать репродуктивный ответ."""
        if not reproductive_type:
            return False
        if self.reproductive_cooldown > 0:
            return False
        return True

    def _should_show_productive(self, productive_type: Optional[str]) -> bool:
        """Определяет, нужно ли показать продуктивный ответ."""
        if not productive_type:
            return False
        if self.productive_cooldown > 0:
            return False
        return True

    def _generate_reproductive_response(self, reproductive_type: str) -> Optional[str]:
        """Генерирует репродуктивный ответ."""
        responses = REPRODUCTIVE_RESPONSES.get(reproductive_type, [])
        return random.choice(responses) if responses else None

    def _generate_productive_response(self, productive_type: str) -> Optional[str]:
        """Генерирует продуктивный ответ."""
        responses = PRODUCTIVE_RESPONSES.get(productive_type, [])
        return random.choice(responses) if responses else None

    def _select_dominant_ability(self, result: ImaginativeAbility) -> Optional[str]:
        """Выбирает доминирующий тип воображения."""
        abilities = {
            "reproductive": result.reproductive_confidence,
            "productive": result.productive_confidence,
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
            "selected_ability": result.selected_ability,
        }
        self.imagination_history.append(entry)

        # Ограничиваем историю последними 20 записями
        if len(self.imagination_history) > 20:
            self.imagination_history = self.imagination_history[-15:]

        # Обновляем текущие образы в контексте
        if result.productive_response:
            self.context_images.append(result.productive_response)
        if len(self.context_images) > 5:
            self.context_images = self.context_images[-3:]

    def get_imagination_summary(self) -> Dict[str, Any]:
        """Возвращает сводку по активному воображению."""
        return {
            "reproductive_count": self.reproductive_count,
            "productive_count": self.productive_count,
            "imagination_history_size": len(self.imagination_history),
            "active_images_count": len(self.context_images),
            "types": {
                "reproductive": ["описание", "чертёж_схема", "история_контекст", "детализация"],
                "productive": ["генерация_нового", "гибридизация", "контрфактуал", "абстракция"],
            },
        }
