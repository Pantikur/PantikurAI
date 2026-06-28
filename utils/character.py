# utils/character.py — Детектор характеров человека

from typing import Dict, List, Optional
from pydantic import BaseModel, Field


class CharacterDetector:
    """
    Детектор характеров человека на основе ключевых слов.
    Распознаёт тип характера по фразам пользователя.
    """

    # === ТИПЫ ХАРАКТЕРОВ ПО ТЕМПЕРАМЕНТУ ===
    CHOLERIC_KEYWORDS = [
        "вспыльчивый", "вспыльчивая",
        "горячий", "горячая",
        "импульсивный", "импульсивная",
        "энергичный", "энергичная",
        "агрессивный", "агрессивная",
        "напористый", "напористая",
        "резкий", "резкая",
        "страстный", "страстная",
        "бурный", "бурная",
        "огненный", "огненная",
        "холерик", "холеричка",
        "взрывной", "взрывная",
        "нетерпеливый", "нетерпеливая",
        "порывистый", "порывистая",
    ]

    SANGUINE_KEYWORDS = [
        "весёлый", "весёлая",
        "общительный", "общительная",
        "жизнерадостный", "жизнерадостная",
        "оптимист", "оптимистка",
        "лёгкий", "лёгкая",
        "позитивный", "позитивная",
        "дружелюбный", "дружелюбная",
        "открытый", "открытая",
        "энергичный", "энергичная",
        "сангвиник", "сангвиничка",
        "живой", "живая",
        "активный", "активная",
        "беспечный", "беспечная",
        "игривый", "игривая",
        "энтузиаст", "энтузиастка",
    ]

    PHLEGMATIC_KEYWORDS = [
        "спокойный", "спокойная",
        "медлительный", "медлительная",
        "флегматик", "флегматичка",
        "равнодушный", "равнодушная",
        "хладнокровный", "хладнокровная",
        "рассудительный", "рассудительная",
        "терпеливый", "терпеливая",
        "постоянный", "постоянная",
        "устойчивый", "устойчивая",
        "невозмутимый", "невозмутимая",
        "ленивый", "ленивая",
        "размеренный", "размеренная",
        "тихий", "тихая",
        "неторопливый", "неторопливая",
    ]

    MELANCHOLIC_KEYWORDS = [
        "грустный", "грустная",
        "меланхолик", "меланхоличка",
        "чувствительный", "чувствительная",
        "ранимый", "ранимая",
        "тревожный", "тревожная",
        "замкнутый", "замкнутая",
        "пессимист", "пессимистка",
        "тихий", "тихая",
        "скромный", "скромная",
        "неуверенный", "неуверенная",
        "робкий", "робкая",
        "задумчивый", "задумчивая",
        "серьёзный", "серьёзная",
        "эмоциональный", "эмоциональная",
        "ранимая душа",
    ]

    # === ТИПЫ ХАРАКТЕРОВ ПО СОЦИАЛЬНОСТИ ===
    INTROVERT_KEYWORDS = [
        "интроверт", "интровертка",
        "замкнутый", "замкнутая",
        "скрытный", "скрытная",
        "необщительный", "необщительная",
        "одиночка",
        "тихий", "тихая",
        "стеснительный", "стеснительная",
        "уединённый", "уединённая",
        "не люблю людей",
        "предпочитаю быть один", "предпочитаю быть одна",
        "мало друзей",
        "избегаю компаний",
    ]

    EXTROVERT_KEYWORDS = [
        "экстраверт", "экстравертка",
        "общительный", "общительная",
        "открытый", "открытая",
        "дружелюбный", "дружелюбная",
        "компания", "компанейский", "компанейская",
        "люблю людей",
        "много друзей",
        "душа компании",
        "люблю тусовки",
        "не люблю быть один", "не люблю быть одна",
        "всегда в центре внимания",
    ]

    AMBIVERT_KEYWORDS = [
        "амбиверт", "амбивертка",
        "и так и так",
        "зависит от настроения",
        "иногда общительный", "иногда общительная",
        "иногда хочу побыть один", "иногда хочу побыть одна",
        "гибкий", "гибкая",
        "адаптивный", "адаптивная",
        "универсальный", "универсальная",
    ]

    # === ТИПЫ ХАРАКТЕРОВ ПО ЭМОЦИОНАЛЬНОСТИ ===
    EMOTIONAL_KEYWORDS = [
        "эмоциональный", "эмоциональная",
        "чувствительный", "чувствительная",
        "сердечный", "сердечная",
        "страстный", "страстная",
        "впечатлительный", "впечатлительная",
        "чувственный", "чувственная",
        "экспрессивный", "экспрессивная",
        "бурный", "бурная",
        "пылкий", "пылкая",
        "горячий", "горячая",
    ]

    RATIONAL_KEYWORDS = [
        "рациональный", "рациональная",
        "логичный", "логичная",
        "хладнокровный", "хладнокровная",
        "рассудительный", "рассудительная",
        "спокойный", "спокойная",
        "аналитический", "аналитическая",
        "трезвый", "трезвая",
        "практичный", "практичная",
        "расчётливый", "расчётливая",
        "безэмоциональный", "безэмоциональная",
    ]

    # === ТИПЫ ХАРАКТЕРОВ ПО ОТНОШЕНИЮ К МИРУ ===
    OPTIMIST_KEYWORDS = [
        "оптимист", "оптимистка",
        "позитивный", "позитивная",
        "жизнерадостный", "жизнерадостная",
        "вера в лучшее",
        "всё будет хорошо",
        "светлый", "светлая",
        "надежда",
        "вижу хорошее",
        "позитивный взгляд",
    ]

    PESSIMIST_KEYWORDS = [
        "пессимист", "пессимистка",
        "негативный", "негативная",
        "мрачный", "мрачная",
        "всё плохо",
        "ничего не получится",
        "тёмный", "тёмная",
        "безнадёжность",
        "вижу плохое",
        "негативный взгляд",
        "скептик", "скептична",
    ]

    REALIST_KEYWORDS = [
        "реалист", "реалистка",
        "реальный", "реальная",
        "трезвый взгляд",
        "как есть",
        "без иллюзий",
        "практичный", "практичная",
        "здравый смысл",
        "объективный", "объективная",
        "факты",
    ]

    # === ТИПЫ ХАРАКТЕРОВ ПО ДОМИНИРОВАНИЮ ===
    DOMINANT_KEYWORDS = [
        "лидер", "лидерша",
        "доминантный", "доминантная",
        "властный", "властная",
        "сильный", "сильная",
        "решительный", "решительная",
        "напористый", "напористая",
        "авторитетный", "авторитетная",
        "контролирующий", "контролирующая",
        "командир", "командирша",
        "ведущий", "ведущая",
        "альфа",
    ]

    SUBMISSIVE_KEYWORDS = [
        "подчинённый", "подчинённая",
        "ведомый", "ведомая",
        "мягкий", "мягкая",
        "уступчивый", "уступчивая",
        "послушный", "послушная",
        "тихий", "тихая",
        "скромный", "скромная",
        "покорный", "покорная",
        "следую за другими",
        "не люблю конфликтов",
        "бета",
    ]

    # === ТИПЫ ХАРАКТЕРОВ ПО ОТНОШЕНИЮ К ПЕРЕМЕНАМ ===
    CONSERVATIVE_KEYWORDS = [
        "консерватор", "консерваторша",
        "традиционный", "традиционная",
        "постоянный", "постоянная",
        "стабильный", "стабильная",
        "не люблю перемены",
        "привык к порядку",
        "старомодный", "старомодная",
        "классический", "классическая",
        "предсказуемый", "предсказуемая",
    ]

    PROGRESSIVE_KEYWORDS = [
        "прогрессивный", "прогрессивная",
        "инновационный", "инновационная",
        "люблю перемены",
        "новатор", "новаторша",
        "современный", "современная",
        "гибкий", "гибкая",
        "адаптивный", "адаптивная",
        "открыт новому", "открыта новому",
        "экспериментатор", "экспериментаторша",
    ]

    # === СМЕШАННЫЕ ТИПЫ ===
    COMPLEX_KEYWORDS = [
        "сложный", "сложная",
        "противоречивый", "противоречивая",
        "непредсказуемый", "непредсказуемая",
        "загадочный", "загадочная",
        "многогранный", "многогранная",
        "глубокий", "глубокая",
        "интересный", "интересная",
        "уникальный", "уникальная",
        "не такой как все", "не такая как все",
    ]

    @classmethod
    def detect_character(cls, text: str) -> Dict[str, Optional[str]]:
        """
        Определяет тип характера по тексту.
        :param text: Текст пользователя
        :return: Словарь с detected character types
        """
        text_lower = text.lower()
        result: Dict[str, Optional[str]] = {
            "temperament": None,
            "sociality": None,
            "emotionality": None,
            "worldview": None,
            "dominance": None,
            "change_attitude": None,
            "complexity": None,
        }

        # === ТЕМПЕРАМЕНТ ===
        temperament_scores = {
            "холерик": sum(1 for kw in cls.CHOLERIC_KEYWORDS if kw in text_lower),
            "сангвиник": sum(1 for kw in cls.SANGUINE_KEYWORDS if kw in text_lower),
            "флегматик": sum(1 for kw in cls.PHLEGMATIC_KEYWORDS if kw in text_lower),
            "меланхолик": sum(1 for kw in cls.MELANCHOLIC_KEYWORDS if kw in text_lower),
        }
        if max(temperament_scores.values()) > 0:
            result["temperament"] = max(temperament_scores, key=temperament_scores.get)  # type: ignore[call-overload]

        # === СОЦИАЛЬНОСТЬ ===
        sociality_scores = {
            "интроверт": sum(1 for kw in cls.INTROVERT_KEYWORDS if kw in text_lower),
            "экстраверт": sum(1 for kw in cls.EXTROVERT_KEYWORDS if kw in text_lower),
            "амбиверт": sum(1 for kw in cls.AMBIVERT_KEYWORDS if kw in text_lower),
        }
        if max(sociality_scores.values()) > 0:
            result["sociality"] = max(sociality_scores, key=sociality_scores.get)  # type: ignore[call-overload]

        # === ЭМОЦИОНАЛЬНОСТЬ ===
        emotionality_scores = {
            "эмоциональный": sum(1 for kw in cls.EMOTIONAL_KEYWORDS if kw in text_lower),
            "рациональный": sum(1 for kw in cls.RATIONAL_KEYWORDS if kw in text_lower),
        }
        if max(emotionality_scores.values()) > 0:
            result["emotionality"] = max(emotionality_scores, key=emotionality_scores.get)  # type: ignore[call-overload]

        # === ОТНОШЕНИЕ К МИРУ ===
        worldview_scores = {
            "оптимист": sum(1 for kw in cls.OPTIMIST_KEYWORDS if kw in text_lower),
            "пессимист": sum(1 for kw in cls.PESSIMIST_KEYWORDS if kw in text_lower),
            "реалист": sum(1 for kw in cls.REALIST_KEYWORDS if kw in text_lower),
        }
        if max(worldview_scores.values()) > 0:
            result["worldview"] = max(worldview_scores, key=worldview_scores.get)  # type: ignore[call-overload]

        # === ДОМИНИРОВАНИЕ ===
        dominance_scores = {
            "доминантный": sum(1 for kw in cls.DOMINANT_KEYWORDS if kw in text_lower),
            "сабмиссивный": sum(1 for kw in cls.SUBMISSIVE_KEYWORDS if kw in text_lower),
        }
        if max(dominance_scores.values()) > 0:
            result["dominance"] = max(dominance_scores, key=dominance_scores.get)  # type: ignore[call-overload]

        # === ОТНОШЕНИЕ К ПЕРЕМЕНАМ ===
        change_scores = {
            "консерватор": sum(1 for kw in cls.CONSERVATIVE_KEYWORDS if kw in text_lower),
            "прогрессивный": sum(1 for kw in cls.PROGRESSIVE_KEYWORDS if kw in text_lower),
        }
        if max(change_scores.values()) > 0:
            result["change_attitude"] = max(change_scores, key=change_scores.get)  # type: ignore[call-overload]

        # === СЛОЖНОСТЬ ===
        complexity_score = sum(1 for kw in cls.COMPLEX_KEYWORDS if kw in text_lower)
        if complexity_score > 0:
            result["complexity"] = "сложный"

        return result

    @classmethod
    def get_all_character_types(cls) -> Dict[str, Dict[str, List[str]]]:
        """Возвращает все типы характеров с ключевыми словами."""
        return {
            "temperament": {
                "холерик": cls.CHOLERIC_KEYWORDS,
                "сангвиник": cls.SANGUINE_KEYWORDS,
                "флегматик": cls.PHLEGMATIC_KEYWORDS,
                "меланхолик": cls.MELANCHOLIC_KEYWORDS,
            },
            "sociality": {
                "интроверт": cls.INTROVERT_KEYWORDS,
                "экстраверт": cls.EXTROVERT_KEYWORDS,
                "амбиверт": cls.AMBIVERT_KEYWORDS,
            },
            "emotionality": {
                "эмоциональный": cls.EMOTIONAL_KEYWORDS,
                "рациональный": cls.RATIONAL_KEYWORDS,
            },
            "worldview": {
                "оптимист": cls.OPTIMIST_KEYWORDS,
                "пессимист": cls.PESSIMIST_KEYWORDS,
                "реалист": cls.REALIST_KEYWORDS,
            },
            "dominance": {
                "доминантный": cls.DOMINANT_KEYWORDS,
                "сабмиссивный": cls.SUBMISSIVE_KEYWORDS,
            },
            "change_attitude": {
                "консерватор": cls.CONSERVATIVE_KEYWORDS,
                "прогрессивный": cls.PROGRESSIVE_KEYWORDS,
            },
            "complexity": {
                "сложный": cls.COMPLEX_KEYWORDS,
            },
        }


if __name__ == "__main__":
    # Тестирование
    test_texts = [
        "Я весёлый и общительный, люблю компании!",
        "Я спокойный и медлительный, не люблю суету.",
        "Я интроверт, предпочитаю быть один.",
        "Я оптимист, верю в лучшее!",
        "Я лидер, всегда веду за собой.",
        "Я сложный человек, непредсказуемый.",
    ]

    print("🧪 Тестирование CharacterDetector")
    print("=" * 50)

    for text in test_texts:
        print(f"\n📝 Текст: {text}")
        result = CharacterDetector.detect_character(text)
        print(f"📊 Результат: {result}")
