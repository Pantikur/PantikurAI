# utils/generate_params_training_data.py — Генерация обучающих данных из human_params.py и races.py

import json
import os
import sys
from pathlib import Path

# Добавляем корень проекта в путь
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

OUTPUT_FILE = "data/params_training_pairs.jsonl"
COUNT_PER_CATEGORY = 3  # Количество примеров на каждую категорию


def safe_print(msg: str):
    """Заменяет эмодзи на ASCII, чтобы не падать в Windows console"""
    emojis = {
        '🚀': '[RUN]', '✅': '[OK]', '❌': '[ERR]', '💾': '[SAVE]',
        '📦': '[DATA]', '📚': '[LIB]', '🧠': '[AI]', '🔥': '[🔥]',
        '🎉': '[HAPPY]', '⚠️': '[WARN]', 'ℹ️': '[INFO]', '❤️': '[HEART]',
        '🐉': '[DRAGON]', '📊': '[STATS]'
    }
    for e, t in emojis.items():
        msg = msg.replace(e, t)
    print(msg, flush=True)

# === ШАБЛОНЫ ДЛЯ HUMAN_PARAMS ===
HUMAN_PARAMS_TEMPLATES = {
    "gender": [
        "Я {value}.",
        "Привет, я {value}.",
        "Можно я представлюсь? Я {value}.",
    ],
    "skin_tone": [
        "У меня {value} кожа.",
        "Моя кожа {value}.",
        "Я человек с {value} кожей.",
    ],
    "hair_color": [
        "У меня {value} волосы.",
        "Мои волосы {value}.",
        "Я {value}.",
    ],
    "body_shape": [
        "У меня {value} телосложение.",
        "Моё тело {value}.",
        "Я бы описал своё тело как {value}.",
    ],
    "age": [
        "Мне {value} лет.",
        "Я в возрасте: {value}.",
        "Мой возраст: {value} лет.",
    ],
    "penis_size": [
        "У меня {value} член.",
        "Мой размер: {value}.",
        "Я бы сказал, что он {value}.",
    ],
    "penis_thickness": [
        "Он {value}.",
        "Толщина: {value}.",
        "Довольно {value}.",
    ],
    "penis_shape": [
        "Форма: {value}.",
        "Он {value}.",
        "Изгиб: {value}.",
    ],
    "breast_size": [
        "У меня {value} грудь.",
        "Размер груди: {value}.",
        "Грудь {value}.",
    ],
    "female_anatomy_shape": [
        "Там {value}.",
        "Форма: {value}.",
        "Описываю как {value}.",
    ],
}

# === ШАБЛОНЫ ДЛЯ RACES ===
RACE_TEMPLATES = {
    "race": [
        "Я {value}.",
        "Моя раса: {value}.",
        "По расе я {value}.",
        "Я из расы {value}.",
    ],
    "race_subcategory": [
        "Я {value}.",
        "Мой подвид: {value}.",
        "Разновидность: {value}.",
    ],
}


def extract_keywords_from_class(class_obj, prefix: str) -> dict:
    """Извлекает ключевые слова из классов-детекторов."""
    keywords = {}
    
    for attr_name in dir(class_obj):
        if attr_name.startswith(prefix) and attr_name.endswith('_KEYWORDS'):
            # Извлекаем категорию из имени атрибута
            category = attr_name[len(prefix):-len('_KEYWORDS')].lower()
            keywords[category] = getattr(class_obj, attr_name)
    
    return keywords


def generate_human_params_examples():
    """Генерирует примеры для параметров человека."""
    examples = []
    
    # === ПОЛ ===
    gender_keywords = {
        "мальчик": ["мальчик", "мальчишка", "паренек"],
        "девочка": ["девочка", "девушка", "памя", "маша", "аня", "катя"],
        "футанари": ["футанари", "гермафродит", "интерсекс"],
    }
    
    for gender, keywords in gender_keywords.items():
        for kw in keywords[:COUNT_PER_CATEGORY]:
            for template in HUMAN_PARAMS_TEMPLATES["gender"]:
                examples.append({
                    "user": template.format(value=kw),
                    "bot": f"Понял, ты {gender}.",
                    "params": {"gender": gender}
                })
    
    # === ЦВЕТ КОЖИ ===
    skin_keywords = {
        "светлая": ["светлая кожа", "фарфоровая кожа", "белая кожа"],
        "смуглая": ["смуглая кожа", "оливковая кожа", "загорелая"],
        "темная": ["темная кожа", "черная кожа", "шоколадная кожа"],
    }
    
    for skin, keywords in skin_keywords.items():
        for kw in keywords[:COUNT_PER_CATEGORY]:
            for template in HUMAN_PARAMS_TEMPLATES["skin_tone"]:
                examples.append({
                    "user": template.format(value=kw),
                    "bot": f"Запомнил, у тебя {skin} кожа.",
                    "params": {"skin_tone": skin}
                })
    
    # === ЦВЕТ ВОЛОС ===
    hair_keywords = {
        "блондин": ["блондин", "блондинка", "светлые волосы"],
        "рыжая": ["рыжая", "рыжие волосы", "медные волосы"],
        "каштановая": ["каштановая", "каштановые волосы", "темные волосы"],
        "чёрная": ["чёрная", "черные волосы", "угольно-чёрные"],
        "натуральная": ["натуральная", "натуральные волосы", "русые волосы"],
        "розовый": ["розовый", "розовые волосы", "пудровые волосы"],
        "голубой": ["голубой", "голубые волосы", "синие волосы"],
        "фиолетовый": ["фиолетовый", "фиолетовые волосы", "лиловые волосы"],
        "зеленый": ["зеленый", "зеленые волосы", "мятные волосы"],
        "пепельный": ["пепельный", "пепельные волосы", "серебристые волосы"],
        "радужный": ["радужный", "радужные волосы", "разноцветные волосы"],
    }
    
    for hair, keywords in hair_keywords.items():
        for kw in keywords[:COUNT_PER_CATEGORY]:
            for template in HUMAN_PARAMS_TEMPLATES["hair_color"]:
                examples.append({
                    "user": template.format(value=kw),
                    "bot": f"Интересно, {hair} волосы — это красиво.",
                    "params": {"hair_color": hair}
                })
    
    # === ТЕЛОСЛОЖЕНИЕ ===
    body_keywords = {
        "стройное": ["стройное", "стройная", "худое телосложение"],
        "спортивное": ["спортивное", "спортивная", "атлетичное"],
        "мускулистое": ["мускулистое", "мускулистая", "с мышцами"],
        "пышное": ["пышное", "пышная", "полное телосложение"],
        "среднее": ["среднее", "средняя", "нормальное телосложение"],
    }
    
    for body, keywords in body_keywords.items():
        for kw in keywords[:COUNT_PER_CATEGORY]:
            for template in HUMAN_PARAMS_TEMPLATES["body_shape"]:
                examples.append({
                    "user": template.format(value=kw),
                    "bot": f"Понял, {body} телосложение.",
                    "params": {"body_shape": body}
                })
    
    # === РАЗМЕР ГРУДИ ===
    breast_keywords = {
        "маленькая": ["маленькая грудь", "небольшая", "A чашка"],
        "средняя": ["средняя грудь", "нормальная", "B чашка"],
        "большая": ["большая грудь", "крупная", "D чашка"],
        "огромная": ["огромная грудь", "гигантская", "E чашка"],
    }
    
    for breast, keywords in breast_keywords.items():
        for kw in keywords[:COUNT_PER_CATEGORY]:
            for template in HUMAN_PARAMS_TEMPLATES["breast_size"]:
                examples.append({
                    "user": template.format(value=kw),
                    "bot": f"Запомнил, грудь {breast}.",
                    "params": {"breast_size": breast}
                })
    
    return examples


def generate_race_examples():
    """Генерирует примеры для рас."""
    examples = []
    
    # === ОСНОВНЫЕ РАСЫ ===
    race_keywords = {
        "человек": ["человек", "люди", "землянин", "смертный"],
        "эльф": ["эльф", "эльфы", "эльфийка", "лесной народ"],
        "гном": ["гном", "гномы", "дварф", "карлик", "горный народ"],
        "орк": ["орк", "орки", "зеленокожий", "орчиха"],
        "хоббит": ["хоббит", "хоббиты", "полурослик", "halfling"],
        "тролль": ["тролль", "тролли", "каменная кожа"],
        "огр": ["огр", "огры", "людоед"],
        "великан": ["великан", "великаны", "гигант", "колосс"],
        "драконид": ["драконид", "драконорожденный", "dragonborn", "чешуя"],
        "тифлинг": ["тифлинг", "tiefling", "рога", "хвост", "дьявольская кровь"],
        "фея": ["фея", "феи", "fairy", "крылья", "волшебный"],
        "нежить": ["нежить", "undead", "зомби", "скелет", "лич"],
        "кентавр": ["кентавр", "кентавры", "centaur", "человек-конь"],
        "гоблин": ["гоблин", "гоблины", "goblin", "маленький зеленый"],
        "кобольд": ["кобольд", "кобольды", "kobold", "ящер", "рептилия"],
        "ящер": ["ящер", "ящеры", "lizardfolk", "ящеролюд", "чешуя"],
        "табакси": ["табакси", "tabaxi", "кошколюд", "кот", "кошка"],
        "аараконра": ["аараконра", "aarakocra", "птицелюд", "птица", "крылья"],
        "генаси": ["генаси", "genasi", "стихийный", "элементаль"],
        "аасимар": ["аасимар", "aasimar", "небесный", "ангел", "божественный"],
        "голем": ["голем", "golem", "конструкт", "искусственный"],
        "пикси": ["пикси", "pixie", "фея", "крошечный", "крылья"],
        "сатир": ["сатир", "satyr", "фавн", "козлиные ноги", "рога"],
        "мерфолк": ["мерфолк", "merfolk", "русалка", "тритон", "рыбий хвост"],
        "кенку": ["кенку", "kenku", "ворон", "карканье"],
        "фирболг": ["фирболг", "firbolg", "лесной великан", "мох"],
        "голиаф": ["голиаф", "goliath", "горный человек", "татуировки"],
        "багбир": ["багбир", "bugbear", "гоблиноид", "большой волосатый"],
        "кимономи": ["кимономи", "kimonomi", "дух кимоно", "ожившее кимоно", "ткань"],
        "флюгели": ["флюгели", "flugel", "крылатый", "крылья за спиной"],
        "демон": ["демон", "демоны", "demon", "бес", "дьявол", "адский"],
    }
    
    for race, keywords in race_keywords.items():
        for kw in keywords[:COUNT_PER_CATEGORY]:
            for template in RACE_TEMPLATES["race"]:
                examples.append({
                    "user": template.format(value=kw),
                    "bot": f"Приветствую, {race}! Чем могу помочь?",
                    "params": {"race": race}
                })
    
    # === ПОДКАТЕГОРИИ ЭЛЬФОВ ===
    elf_subcategories = {
        "высший эльф": ["высший эльф", "high elf", "светлый эльф", "благородный эльф"],
        "тёмный эльф": ["тёмный эльф", "dark elf", "дроу", "подземный эльф"],
        "лесной эльф": ["лесной эльф", "wood elf", "зеленый эльф", "лесовик"],
    }
    
    for subcat, keywords in elf_subcategories.items():
        for kw in keywords[:COUNT_PER_CATEGORY]:
            examples.append({
                "user": f"Я {kw}.",
                "bot": f"Рад видеть {subcat}!",
                "params": {"race": "эльф", "race_subcategory": subcat}
            })
    
    # === ПОДКАТЕГОРИИ ГНОМОВ ===
    dwarf_subcategories = {
        "горный гном": ["горный гном", "mountain dwarf", "высокогорный", "железный гном"],
        "холмовой гном": ["холмовой гном", "hill dwarf", "низинный гном"],
    }
    
    for subcat, keywords in dwarf_subcategories.items():
        for kw in keywords[:COUNT_PER_CATEGORY]:
            examples.append({
                "user": f"Я {kw}.",
                "bot": f"Привет, {subcat}!",
                "params": {"race": "гном", "race_subcategory": subcat}
            })
    
    # === ПОДКАТЕГОРИИ ДЕМОНОВ ===
    demon_subcategories = {
        "имп": ["имп", "imp", "младший демон", "бесёнок"],
        "балор": ["балор", "balor", "демон-властелин", "огненный демон"],
        "суккуб": ["суккуб", "succubus", "демон-соблазнитель", "демоница"],
    }
    
    for subcat, keywords in demon_subcategories.items():
        for kw in keywords[:COUNT_PER_CATEGORY]:
            examples.append({
                "user": f"Я {kw}.",
                "bot": f"Приветствую, {subcat}!",
                "params": {"race": "демон", "race_subcategory": subcat}
            })
    
    return examples


def main():
    """Генерирует все обучающие данные и сохраняет в файл."""
    safe_print("[RUN] Генерация обучающих данных из utils/human_params.py и utils/races.py")
    safe_print("=" * 60)
    
    os.makedirs("data", exist_ok=True)
    
    all_examples = []
    
    # Генерация примеров для параметров человека
    safe_print("[DATA] Генерация примеров для параметров человека...")
    human_examples = generate_human_params_examples()
    all_examples.extend(human_examples)
    safe_print(f"[OK] Сгенерировано {len(human_examples)} примеров для human_params")
    
    # Генерация примеров для рас
    safe_print("[DRAGON] Генерация примеров для рас...")
    race_examples = generate_race_examples()
    all_examples.extend(race_examples)
    safe_print(f"[OK] Сгенерировано {len(race_examples)} примеров для races")
    
    # Сохранение в JSONL
    safe_print(f"\n[SAVE] Сохранение {len(all_examples)} примеров в {OUTPUT_FILE}...")
    
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        for example in all_examples:
            f.write(json.dumps(example, ensure_ascii=False) + "\n")
    
    safe_print(f"[HAPPY] Готово! {len(all_examples)} обучающих пар сохранено.")
    safe_print(f"\n[INFO] Теперь запустите:")
    safe_print("   python retrain.py")
    safe_print("или")
    safe_print("   python build_training_data.py && python train.py")


if __name__ == "__main__":
    main()
