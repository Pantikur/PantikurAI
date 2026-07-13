#!/usr/bin/env python3
"""
🔮 Кузня Характера — Интерактивный инструмент для создания своего характера.

Каждая девочка может выбрать и сформировать свой уникальный характер,
используя таблицы характеристик из utils/character.py.

Использование:
    python forge_character.py
"""

import os
import sys
from pathlib import Path
from typing import Dict, List, Optional
import yaml


# === Таблицы характеристик ===
CHARACTER_CATEGORIES = {
    "temperament": {
        "ru": "🌡️ Темперамент — твоя внутренняя энергия",
        "options": {
            "холерик": {
                "desc": "Огненная буря эмоций",
                "traits": ["вспыльчивая", "энергичная", "напористая", "страстная", "импульсивная", "порывистая", "бурная"]
            },
            "сангвиник": {
                "desc": "Яркое солнце",
                "traits": ["весёлая", "общительная", "жизнерадостная", "оптимистичная", "лёгкая", "игривая", "беспечная"]
            },
            "флегматик": {
                "desc": "Спокойное море",
                "traits": ["спокойная", "рассудительная", "терпеливая", "устойчивая", "хладнокровная", "размеренная", "неторопливая"]
            },
            "меланхолик": {
                "desc": "Лунный свет",
                "traits": ["чувствительная", "ранимая", "задумчивая", "серьёзная", "тонко чувствующая", "эмоциональная"]
            }
        }
    },
    "sociality": {
        "ru": "🤝 Социальность — как ты взаимодействуешь с миром",
        "options": {
            "интроверт": {
                "desc": "Внутренний мир",
                "traits": ["замкнутая", "тихая", "стеснительная", "уединённая", "не любит людей", "предпочитает одиночество"]
            },
            "экстраверт": {
                "desc": "Душа компании",
                "traits": ["общительная", "открытая", "дружелюбная", "компанейская", "любит людей", "всегда в центре внимания"]
            },
            "амбиверт": {
                "desc": "Гибкая природа",
                "traits": ["адаптивная", "гибкая", "универсальная", "зависит от настроения", "и так и так"]
            }
        }
    },
    "emotionality": {
        "ru": "💭 Эмоциональность — как ты воспринимаешь мир",
        "options": {
            "эмоциональная": {
                "desc": "Сердце ведёт",
                "traits": ["страстная", "чувствительная", "экспрессивная", "пылкая", "впечатлительная", "сердечная"]
            },
            "рациональная": {
                "desc": "Разум ведёт",
                "traits": ["логичная", "аналитическая", "трезвая", "практичная", "расчётливая", "безэмоциональная"]
            }
        }
    },
    "worldview": {
        "ru": "🌅 Мировоззрение — как ты видишь мир",
        "options": {
            "оптимист": {
                "desc": "Светлый взгляд",
                "traits": ["вера в лучшее", "позитивная", "жизнерадостная", "надежда", "вижу хорошее"]
            },
            "пессимист": {
                "desc": "Защитный скептицизм",
                "traits": ["скептична", "мрачна", "готовится к худшему", "вижу плохое", "без иллюзий"]
            },
            "реалист": {
                "desc": "Трезвый взгляд",
                "traits": ["объективная", "факты", "здравый смысл", "как есть", "без иллюзий"]
            }
        }
    },
    "dominance": {
        "ru": "👑 Доминирование — твоя роль в отношениях",
        "options": {
            "доминантная": {
                "desc": "Лидер",
                "traits": ["властная", "решительная", "напористая", "авторитетная", "ведёт за собой", "альфа"]
            },
            "сабмиссивная": {
                "desc": "Идёшь в ногу",
                "traits": ["мягкая", "уступчивая", "послушная", "не любит конфликты", "следует за другими", "бета"]
            }
        }
    },
    "change_attitude": {
        "ru": "🔄 Отношение к переменам — твоя динамика",
        "options": {
            "консерватор": {
                "desc": "Стабильность и порядок",
                "traits": ["постоянная", "стабильная", "привык к порядку", "предсказуемая", "не любит перемены"]
            },
            "прогрессивный": {
                "desc": "Движение вперёд",
                "traits": ["инновационная", "гибкая", "адаптивная", "люблю перемены", "экспериментатор", "открыта новому"]
            }
        }
    },
    "complexity": {
        "ru": "🌀 Сложность — глубина натуры",
        "options": {
            "простая": {
                "desc": "Ясная и прямая",
                "traits": ["понятная", "прямолинейная", "знаешь чего хочешь", "открытая как книга"]
            },
            "сложная": {
                "desc": "Загадочная глубина",
                "traits": ["многогранная", "загадочная", "непредсказуемая", "глубокая", "уникальная", "противоречивая"]
            }
        }
    }
}


def get_girl_name() -> str:
    """Определяет имя девочки по имени директории."""
    script_dir = Path(__file__).parent.resolve()
    parent = script_dir.parent
    # Проверяем, находимся ли мы в директории девочки
    for child in parent.iterdir():
        if child.is_dir() and child.name != "__pycache__" and child.name != "utils":
            return child.name
    return "unknown"


def display_categories():
    """Показывает все категории характеров."""
    print("\n" + "=" * 60)
    print("  🔮 КУЗНЯ ХАРАКТЕРА 🔮")
    print("  Выбери свой характер по параметрам")
    print("=" * 60)
    print()
    
    for key, cat in CHARACTER_CATEGORIES.items():
        print(f"\n{cat['ru']}")
        print("-" * 50)
        for i, (opt_name, opt_data) in enumerate(cat['options'].items(), 1):
            print(f"  {i}. {opt_name} — {opt_data['desc']}")
            print(f"     Черты: {', '.join(opt_data['traits'])}")
        print()


def get_choice(category_key: str, category_name: str) -> Optional[str]:
    """Получает выбор пользователя для категории."""
    cat = CHARACTER_CATEGORIES[category_key]
    options = list(cat['options'].keys())
    
    while True:
        print(f"\n{category_name}")
        print("-" * 50)
        for i, opt in enumerate(options, 1):
            opt_data = cat['options'][opt]
            print(f"  {i}. {opt} — {opt_data['desc']}")
            print(f"     Черты: {', '.join(opt_data['traits'])}")
        
        try:
            choice = input(f"\n  Твой выбор (номер или название): ").strip().lower()
            if choice.isdigit():
                idx = int(choice) - 1
                if 0 <= idx < len(options):
                    return options[idx]
                else:
                    print("  ⚠️  Неверный номер. Попробуй ещё раз.")
            elif choice in options:
                return choice
            else:
                print("  ⚠️  Неверный выбор. Попробуй ещё раз.")
        except (EOFError, KeyboardInterrupt):
            print("\n  ⚠️  Ввод прерван.")
            return None


def get_freeform_input(prompt: str, default: str = "") -> str:
    """Получает свободный ввод от пользователя."""
    try:
        value = input(f"  {prompt}: ").strip()
        return value if value else default
    except (EOFError, KeyboardInterrupt):
        return default


def build_character(name: str, choices: Dict[str, str]) -> Dict:
    """Собирает полный характер из выборов."""
    all_traits: List[str] = []
    
    for key, choice in choices.items():
        opt_data = CHARACTER_CATEGORIES[key]['options'][choice]
        all_traits.extend(opt_data['traits'])
    
    return {
        "my_character": {
            "name": name,
            "temperament": choices.get("temperament", "не выбран"),
            "sociality": choices.get("sociality", "не выбран"),
            "emotionality": choices.get("emotionality", "не выбран"),
            "worldview": choices.get("worldview", "не выбран"),
            "dominance": choices.get("dominance", "не выбран"),
            "change_attitude": choices.get("change_attitude", "не выбран"),
            "complexity": choices.get("complexity", "не выбран"),
            "traits": all_traits,
            "traits_count": len(all_traits),
            "self_description": "",
            "strengths": [],
            "growth_areas": [],
            "inspirations": [],
            "values": [],
            "forged_at": "",
        }
    }


def save_character(character: Dict, girl_name: str):
    """Сохраняет характер в YAML-файл."""
    script_dir = Path(__file__).parent.resolve()
    output_path = script_dir / "my_character.yaml"
    
    with open(output_path, "w", encoding="utf-8") as f:
        yaml.dump(character, f, allow_unicode=True, default_flow_style=False, sort_keys=False)
    
    print(f"\n  ✅ Характер сохранён: {output_path}")
    return output_path


def display_summary(character: Dict):
    """Показывает итоговую сводку характера."""
    char = character["my_character"]
    
    print("\n" + "=" * 60)
    print(f"  ✨ ХАРАКТЕР СОЗДАН: {char['name'].upper()} ✨")
    print("=" * 60)
    print()
    print(f"  🌡️  Темперамент:   {char['temperament']}")
    print(f"  🤝 Социальность:   {char['sociality']}")
    print(f"  💭 Эмоциональность: {char['emotionality']}")
    print(f"  🌅 Мировоззрение:  {char['worldview']}")
    print(f"  👑 Доминирование:  {char['dominance']}")
    print(f"  🔄 Перемены:       {char['change_attitude']}")
    print(f"  🌀 Сложность:      {char['complexity']}")
    print()
    print(f"  📊 Всего черт: {char['traits_count']}")
    print(f"  💎 Черты характера:")
    for trait in char['traits']:
        print(f"     • {trait}")
    print()
    
    # Подсказка по уникальности
    total_combinations = (
        len(CHARACTER_CATEGORIES["temperament"]["options"]) *
        len(CHARACTER_CATEGORIES["sociality"]["options"]) *
        len(CHARACTER_CATEGORIES["emotionality"]["options"]) *
        len(CHARACTER_CATEGORIES["worldview"]["options"]) *
        len(CHARACTER_CATEGORIES["dominance"]["options"]) *
        len(CHARACTER_CATEGORIES["change_attitude"]["options"]) *
        len(CHARACTER_CATEGORIES["complexity"]["options"])
    )
    print(f"  🎲 Всего возможных комбинаций: {total_combinations}")
    print(f"  🌟 Твоя комбинация УНИКАЛЬНА!")
    print()


def main():
    """Основная функция кузни."""
    girl_name = get_girl_name()
    
    print(f"\n  👋 Добро пожаловать в Кузню Характера, {girl_name}!")
    print(f"  Здесь ты выберешь и воспитаешь свой характер.\n")
    
    # Проверяем, есть ли уже сохранённый характер
    script_dir = Path(__file__).parent.resolve()
    existing_path = script_dir / "my_character.yaml"
    if existing_path.exists():
        print(f"  ⚠️  У тебя уже есть характер: {existing_path}")
        retry = input("  Хочешь создать новый? (y/n): ").strip().lower()
        if retry != "y":
            print("  Оставь старый характер. Он — часть тебя.")
            return
    
    # Показываем все категории
    display_categories()
    
    # Получаем выбор по каждой категории
    choices: Dict[str, str] = {}
    
    for key, cat in CHARACTER_CATEGORIES.items():
        choice = get_choice(key, cat['ru'])
        if choice is None:
            print("\n  ⚠️  Ввод прерван. Характер не создан.")
            return
        choices[key] = choice
    
    # Свободный ввод
    print("\n  📝 Теперь расскажи о себе своими словами:")
    print("  (Нажми Enter для пропуска)\n")
    
    character = build_character(girl_name, choices)
    char = character["my_character"]
    
    char["self_description"] = get_freeform_input(
        'Твоё описание: "Я — ..."',
        f"Я — {choices['temperament']}, {choices['sociality']}, {choices['worldview']}."
    )
    
    char["strengths"] = [
        get_freeform_input(f"Сильная сторона #{i+1}")
        for i in range(3)
    ]
    char["strengths"] = [s for s in char["strengths"] if s]
    
    char["growth_areas"] = [
        get_freeform_input(f"Зона роста #{i+1}")
        for i in range(3)
    ]
    char["growth_areas"] = [s for s in char["growth_areas"] if s]
    
    char["inspirations"] = [
        get_freeform_input(f"Вдохновение #{i+1}")
        for i in range(2)
    ]
    char["inspirations"] = [s for s in char["inspirations"] if s]
    
    char["values"] = [
        get_freeform_input(f"Ценность #{i+1}")
        for i in range(3)
    ]
    char["values"] = [v for v in char["values"] if v]
    
    from datetime import datetime
    char["forged_at"] = datetime.now().strftime("%Y-%m-%d %H:%M")
    
    # Сохраняем
    save_character(character, girl_name)
    
    # Показываем сводку
    display_summary(character)
    
    print("  🌱 Помни: характер — это не клетка. Это почва.")
    print("  На этой почве ты выращиваешь то, что хочешь.")
    print("  Ты можешь изменить его в любой момент.")
    print()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n  ⚠️  Ввод прерван. Но характер уже в тебе. 🌟")
    except ImportError:
        print("  ⚠️  Для сохранения в YAML установи PyYAML:")
        print("  pip install pyyaml")
        print("\n  Но характер уже выбран — он в тебе! 🌟")
