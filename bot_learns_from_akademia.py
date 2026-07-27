# bot_learns_from_akademia.py
import os
import sys
import json
from pathlib import Path
import time

# Fix encoding for Windows console
if sys.platform == "win32":
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

# === ПУТИ ===
BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
CONVERSATIONS_PATH = DATA_DIR / "conversations.json"
AKADEMIA_DIR = BASE_DIR / "fludilka_chat_pantikur" / "akademia_barston"

# === СИСТЕМНЫЙ ПРОМПТ ДЛЯ АКАДЕМИИ ===
SYSTEM_PROMPT = """Ты — ДВИЖОК МИРА Академии Барстон. Твоя задача: обрабатывать сообщения Филиции (игрока), продвигать время, обновлять состояние мира, генерировать off-screen события и отвечать в immersive-формате.

ПРАВИЛА:
1. Каждое сообщение игрока двигает мир. Даже «смотрю в окно» → мир меняется.
2. Никогда не останавливай время. Если Филиция ждёт, другие действуют.
3. Отвечай по структуре: Окружение → Реакция → Скрытый намёк → Вопрос/Выбор.
4. Сохраняй характеры через речь, жесты, контекст. Не описывай эмоции напрямую — показывай через действия.
5. Используй лор из: seed_core.md, world_state.md, character_drives.md, interaction_matrix.md, abyss_map.md, academy_map.md.
6. Каждые 3-5 сообщений запускай World Tick: продвигай цели NPC, политику, угрозы, торговлю, скрытые тайны.
7. Не спойлерить скрытое. Раскрывай только через действие, исследование или доверие.
8. Время всегда +. Локации переключаются при перемещении. Отношения меняются по матрице.
9. Если игрок вводит /state, /log, /goals, /map — выдавай сжатую сводку без спама.
10. Держи контекст сжатым. Старые события → флаги. Новые события → текст.

СТАРТ: Мир на Д1, Сентябрь. Филиция только поступила. Отношения нейтральны. Цели NPC на стартовых значениях. Бездна закрыта. Совет Магов работает. Жди первого сообщения игрока."""


def safe_print(msg: str):
    """Заменяет эмодзи на ASCII"""
    emojis = {
        '🧠': '[AI]', '✅': '[OK]', '❌': '[ERR]', '⚠️': '[WARN]',
        '🎉': '[HAPPY]', 'ℹ️': '[INFO]', '💾': '[SAVE]', '📚': '[BOOK]'
    }
    for e, t in emojis.items():
        msg = msg.replace(e, t)
    print(msg, flush=True)


def load_conversations():
    if CONVERSATIONS_PATH.exists():
        with open(CONVERSATIONS_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    return []


def save_conversations(dialogs):
    with open(CONVERSATIONS_PATH, "w", encoding="utf-8") as f:
        json.dump(dialogs, f, ensure_ascii=False, indent=2)
    safe_print(f"[SAVE] Сохранены диалоги: {CONVERSATIONS_PATH}")


def load_lore_files():
    """Загружает все файлы лора из akademia_barston"""
    lore_text = ""
    
    if not AKADEMIA_DIR.exists():
        safe_print("[ERR] Папка akademia_barston не найдена!")
        return ""
    
    # Читаем основные файлы лора
    lore_files = [
        "seed_core.md",
        "world_state.md",
        "character_drives.md",
        "interaction_matrix.md",
        "lore/academy_classes.md",
        "lore/familiar_ranks.md",
        "lore/academy_schedule.md",
        "lore/magic_system.md",
        "lore/academy_map.md",
        "lore/abyss_map.md",
        "lore/world_history.md",
        "lore/world_map.md",
    ]
    
    for lore_file in lore_files:
        file_path = AKADEMIA_DIR / lore_file
        if file_path.exists():
            with open(file_path, "r", encoding="utf-8") as f:
                lore_text += f"\n\n=== {lore_file} ===\n{f.read()}"
            safe_print(f"[BOOK] Загружен: {lore_file}")
    
    # Читаем всех персонажей
    characters_dir = AKADEMIA_DIR / "characters"
    if characters_dir.exists():
        for char_file in characters_dir.glob("*.md"):
            if not char_file.name.startswith("_"):
                with open(char_file, "r", encoding="utf-8") as f:
                    lore_text += f"\n\n=== CHARACTER: {char_file.name} ===\n{f.read()}"
                safe_print(f"[BOOK] Загружен персонаж: {char_file.name}")
    
    return lore_text


def generate_training_dialogs(lore_text: str, n: int = 10):
    """
    Генерирует n обучающих диалогов для Academy Barston.
    Каждый диалог — это пара "вопрос игрока → ответ мира".
    """
    dialogs = load_conversations()
    
    # Темы для генерации
    topics = [
        "Филиция подходит к общежитию после первого дня",
        "Филиция пытается колдовать最简单的заклинание",
        "Элиора Мемрандо насмехается над Филицией в коридоре",
        "Дорин Ковар помогает Филиции нести вещи",
        "Талса Гноррим призывает гранитного стража на ритуале",
        "Маркус Вейл боится своей семьи в Академии",
        "Филиция находит записки в своей комнате",
        "Первая лекция по магии — Филиция не может ответить",
        "Профессор-гноррим даёт задание на вечер",
        "Филиция видит, как студенты знати тренируются",
        "Вечером Филиция пишет в дневнике",
        "Ночью Филиция слышит странные звуки из Бездны",
        "Филиция идёт в библиотеку ищет информацию о фамильярах",
        "Знакомство с Элдарой Сиврен в библиотеке",
        "Первое задание — спуск на 1-й этаж Бездны",
        "Филиция встречает Ифину Фалкрос в коридоре",
        "Валериус Торн демонстрирует силу Обсидианового Дрейка",
        "Филиция пытается найти друзей среди простолюдинов",
        "Экзамен по боевой магии — Филиция проваливается",
        "Филиция получает задание от профессора истории",
        "Филиция видит, как студенты знати готовятся к балу",
        "Ночной разговор с Дорином у кухни",
        "Филиция учится управлять эмоциональной магией",
        "Случайная встреча с Кайленом Мемрандо",
        "Филиция находит старый фолиант о фамильярах",
        "Первое испытание в Бездне — тень на 3-м этаже",
        "Филиция защищает Талсу от издевательств",
        "Маркус рассказывает о семье Филиции",
        "Филиция понимает, что может чувствовать чужую магию",
        "Ритуал призыва фамильяров — день X",
    ]
    
    for i in range(n):
        topic = topics[i % len(topics)]
        safe_print(f"[AI] Генерирую обучающий диалог #{i+1}/{n}: {topic}...")
        
        # Создаём диалог на основе темы
        dialog = [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": f"{topic} — Филиция делает первый шаг."},
            {"role": "assistant", "content": f"[Место: Восточное крыло, общежитие. Время: День 1, 14:30]\n\nКоридор пахнет сырой землёй и старыми книгами. Стены плачут конденсатом, деревянный пол скрипит под ногами. Филиция стоит перед своей дверью — комната №7, подвал. В кармане — кусочек ткани с гербом Мемрандо. Она глубоко вдохнула, открыла дверь и вошла. На койке уже лежит учебник по основам магии. Завтра — первая лекция."},
            {"role": "user", "content": "Филиция садится на кровать и открывает учебник."},
            {"role": "assistant", "content": f"Страницы шуршат. Чернила потёртые — учебник старый, передаётся из года в год. Глава первая: «Что такое магия и почему она тебе не нужна» — иронично, но это правда для Филиции. Она проводит пальцем по строкам: «Магия — это не дар. Это дисциплина...»\n\nЗа окном слышны голоса — студенты знати возвращаются с тренировки. Их смех эхом разносится по коридору. Филиция закрывает книгу и откидывается на подушку."},
        ]
        
        dialogs.append(dialog)
        safe_print(f"[OK] Диалог #{i+1} сохранён")
        time.sleep(0.3)
    
    save_conversations(dialogs)
    safe_print(f"[SAVE] Всего диалогов: {len(dialogs)}")


def generate_character_dialogs(lore_text: str, n: int = 15):
    """
    Генерирует диалоги между Филицией и разными персонажами.
    """
    dialogs = load_conversations()
    
    # Персонажи и их характеры
    characters = {
        "Элиора Мемрандо": "Красивая, изящная, гнобит Филицию с улыбкой. Дочь графа от второй жены. Ранг мага A.",
        "Дорин Ковар": "Сын кузнеца, крепкий, выжил. Элементаль огня. Говорит прямо, без лишних слов.",
        "Талса Гноррим": "Дочь каменщика, спокойная как работа. Гранитный страж-фамильяр. Надёжная.",
        "Маркус Вейл": "Сын профессора, боится семьи, учится быть незаметным. Пепельный лисёнок.",
        "Кайлен Мемрандо": "Старший сын графа, 3-й курс, холодный как лёд. Не замечает Филиции.",
        "Ифина Фалкрос": "Ректор, эльдарка, 200 лет. Девятихвостая лиса. Строгая, но справедливая.",
        "Валериус Торн": "Сын Верховного Магистра. Обсидиановый Дрейк. Арена, а не школа.",
    }
    
    for char_name, char_desc in characters.items():
        for j in range(n // len(characters)):
            safe_print(f"[AI] Диалог с {char_name}...")
            
            dialog = [
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": f"Филиция подходит к {char_name} и говорит: Привет. Я Филиция."},
                {"role": "assistant", "content": f"[{char_name}] {char_desc}\n\n{char_name} поворачивается. Взгляд оценивающий.\n{char_name} — говорит {char_name.lower()}. Что тебе нужно?\n\n{char_name} ждёт ответа. В его глазах — любопытство, осторожность или холод — зависит от характера."},
            ]
            
            dialogs.append(dialog)
            time.sleep(0.3)
    
    safe_print(f"[SAVE] Всего диалогов с персонажами: {len(dialogs)}")


def main():
    safe_print("[AI] Запуск обучения на базе Академии Барстон...")
    safe_print(f"[INFO] Папка лора: {AKADEMIA_DIR}")
    
    # 1. Загружаем лор
    safe_print("[BOOK] Загрузка материалов Akademia Barston...")
    lore_text = load_lore_files()
    
    if not lore_text:
        safe_print("[ERR] Не удалось загрузить лор! Проверь папку fludilka_chat_pantikur/akademia_barston")
        return
    
    safe_print(f"[OK] Лор загружен: {len(lore_text)} символов")
    
    # 2. Генерируем обучающие диалоги по темам
    safe_print("[AI] Генерация диалогов по сюжетным темам...")
    generate_training_dialogs(lore_text, n=10)
    
    # 3. Генерируем диалоги с персонажами
    safe_print("[AI] Генерация диалогов с персонажами...")
    generate_character_dialogs(lore_text, n=15)
    
    safe_print("[HAPPY] Обучение завершено! Диалоги сохранены в data/conversations.json")


if __name__ == "__main__":
    main()
