# add_world_examples.py
import os
import json
from datetime import datetime

# === Настройки ===
DATA_DIR = "data"
CONVERSATIONS_FILE = os.path.join(DATA_DIR, "conversations.json")

# Примеры миров — добавьте столько, сколько хотите
WORLD_EXAMPLES = [
    {
        "input": "Создай мир: Фэнтези",
        "output": "Название: Авалора\nОписание: Остров, парящий в небе, питаемый пением древних храмов.\nЗаконы общества: Никто не может молчать во время храмового пения.\nТрадиции: Каждое утро проходит Хор Небес.\nВнегласные правила: Не останавливай пение — иначе остров начнёт падать."
    },
    {
        "input": "Создай мир: Киберпанк",
        "output": "Название: Неоновый Лабиринт\nОписание: Город, где память можно купить на чёрном рынке.\nЗаконы общества: Все нейроимпланты должны быть зарегистрированы.\nТрадиции: Ежегодный фестиваль забвения.\nВнегласные правила: Не спрашивай, чья это память."
    },
    {
        "input": "Создай мир: Стимпанк, приключения",
        "output": "Название: Этерия\nОписание: Мир, где воздух — валюта, а дирижабли — дома.\nЗаконы общества: Запрещено вскрывать чужие баллоны с воздухом.\nТрадиции: Парад воздушных капитанов каждые 13 дней.\nВнегласные правила: Не доверяй тем, кто дышит слишком тихо."
    },
    {
        "input": "Создай мир: Фэнтези, магия",
        "output": "Название: Арканум\nОписание: Континент, где заклинания пишутся на коже.\nЗаконы общества: Запрещено стирать чужие руны.\nТрадиции: Ежегодное сожжение старых магов.\nВнегласные правила: Не трогай тех, у кого глаза — чернильные пятна."
    },
    {
        "input": "Создай мир: Постапокалипсис, выживание",
        "output": "Название: Пепелище\nОписание: Развалины города, где дождь плавит металл.\nЗаконы общества: Нельзя выходить без маски.\nТрадиции: Жертвоприношение дождю раз в год.\nВнегласные правила: Не рассказывай, что видел под землёй."
    }
]

def load_conversations():
    """Загружает существующие диалоги"""
    if not os.path.exists(CONVERSATIONS_FILE):
        print(f"📁 Файл {CONVERSATIONS_FILE} не найден. Создаю новый.")
        return []
    
    try:
        with open(CONVERSATIONS_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
            if isinstance(data, list):
                return data
            else:
                print("⚠️ Формат файла не список. Создаю новый список.")
                return []
    except json.JSONDecodeError as e:
        print(f"❌ Ошибка чтения JSON: {e}")
        backup_name = f"{CONVERSATIONS_FILE}.backup.{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        os.rename(CONVERSATIONS_FILE, backup_name)
        print(f"💾 Создана резервная копия: {backup_name}")
        return []

def save_conversations(conversations):
    """Сохраняет диалоги обратно в файл"""
    os.makedirs(DATA_DIR, exist_ok=True)
    with open(CONVERSATIONS_FILE, "w", encoding="utf-8") as f:
        json.dump(conversations, f, ensure_ascii=False, indent=2)
    print(f"✅ Сохранено {len(conversations)} пар в {CONVERSATIONS_FILE}")

def main():
    print("🚀 Добавление примеров миров в conversations.json")
    
    # Загружаем текущие данные
    convs = load_conversations()
    initial_count = len(convs)
    added_count = 0

    # Преобразуем новые примеры
    new_pairs = [[ex["input"], ex["output"]] for ex in WORLD_EXAMPLES]

    # Добавляем только уникальные
    for pair in new_pairs:
        if pair not in convs:
            convs.append(pair)
            print(f"➕ Добавлено: {pair[0]}")
            added_count += 1
        else:
            print(f"🟨 Уже есть: {pair[0]}")

    # Сохраняем
    if added_count > 0:
        save_conversations(convs)
        print(f"\n🎉 Готово! Добавлено: {added_count}, Всего примеров: {len(convs)}")
    else:
        print("\n✅ Все примеры уже есть. Ничего не добавлено.")

if __name__ == "__main__":
    main()