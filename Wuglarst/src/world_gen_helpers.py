# Wuglarst/src/world_gen_helpers.py — Генерация миров (шаблоны/знания/fallback)
#
# Вынесено из chatbot.py для уменьшения размера модуля.
# Использует атрибуты self._generate_response_with_sampling на хосте-миксине.

import logging
import os
import random
from typing import Dict


class WorldGenMixin:
    """Миксин с хелперами генерации миров для класса ChatBot."""

    @staticmethod
    def _detect_genre_category(genre: str, tag: str) -> str:
        """Определяет категорию жанра для выбора шаблонов"""
        genre_lower = genre.lower()
        tag_lower = tag.lower()

        # Гибридные жанры
        is_cyber = "киберпанк" in genre_lower
        is_fantasy = "фэнтези" in genre_lower or "фэнтези" in tag_lower
        is_magic = "магия" in tag_lower or "мистик" in tag_lower

        if is_cyber and (is_fantasy or is_magic):
            return "cyberfantasy"
        if "пост" in genre_lower and (is_fantasy or is_magic):
            return "postfantasy"

        # Чистые жанры
        if is_cyber:
            return "cyberpunk"
        if is_fantasy:
            return "fantasy"
        if "пост" in genre_lower:
            return "postapoc"
        if "научная фантастика" in genre_lower or "sci-fi" in genre_lower:
            return "scifi"
        if "стимпанк" in genre_lower:
            return "steampunk"
        if "повседневность" in genre_lower:
            return "slice_of_life"
        if "альтернатив" in genre_lower:
            return "alt_reality"
        if "реальност" in genre_lower or "реальный мир" in genre_lower:
            return "reality"
        if "школа" in tag_lower or "учеб" in tag_lower:
            return "slice_of_life"  # Школьные темы — повседневность

        # По умолчанию — фэнтези
        return "fantasy"

    def _generate_world_from_templates(self, genre: str, tag: str, templates: Dict, category: str) -> str:
        """Генерирует структурированный мир на основе шаблонов WorldFactory"""

        # Вспомогательные функции для заполнения шаблонов
        def fill_template(template: str) -> str:
            """Заполняет шаблон случайными значениями"""
            replacements = {
                "{name}": random.choice(["Элдория", "Валерия", "Ардония", "Северия", "Тэммора", "Астра", "Небесный Предел", "Тихий Угол", "Стальной Горизонт", "Новая Земля"]),
                "{number}": str(random.randint(3, 12)),
                "{height}": str(random.randint(500, 5000)),
                "{depth}": str(random.randint(1, 50)),
                "{plant}": random.choice(["вечным туманом", "серебристым мхом", "кристальными цветами", "светящимся лишайником", "древними папоротниками"]),
                "{location}": random.choice(["Запретной Зоны", "Пустошей", "Горизонта Событий", "Мёртвого Города", "Древних Руин"]),
            }
            result = template
            for key, value in replacements.items():
                result = result.replace(key, value)
            return result

        # Генерируем географию (1-2 шаблона)
        geography = random.sample(templates.get("geography", []), min(len(templates.get("geography", [])), 2))
        geography_text = "\n".join([f"   - {fill_template(g)}" for g in geography])

        # Генерируем законы (2-3 шаблона)
        laws = random.sample(templates.get("laws", []), min(len(templates.get("laws", [])), 3))
        laws_text = "\n".join([f"   - {fill_template(l)}" for l in laws])

        # Генерируем традиции (2-3 шаблона)
        traditions = random.sample(templates.get("traditions", []), min(len(templates.get("traditions", [])), 3))
        traditions_text = "\n".join([f"   - {fill_template(t)}" for t in traditions])

        # Генерируем негласные правила (1-2 шаблона)
        unspoken = random.sample(templates.get("unspoken_rules", []), min(len(templates.get("unspoken_rules", [])), 2))
        unspoken_text = "\n".join([f"   - {fill_template(u)}" for u in unspoken])

        # Генерируем название мира
        world_name = fill_template("{name}")
        if category == "fantasy":
            world_name = random.choice(["Элдория", "Валерия", "Ардония", "Северия", "Тэммора", "Драконий Предел", "Лес Теней", "Королевство Света"])
        elif category == "cyberpunk":
            world_name = random.choice(["Нео-Токио", "Стальной Горизонт", "Хром-Сити", "Глитч-Зона", "Кибер-Предел"])
        elif category == "cyberfantasy":
            world_name = random.choice(["Арк-Сити", "Техно-Магия", "Нео-Ардония", "Кристалл-Град", "Эфир-Сити"])
        elif category == "postapoc":
            world_name = random.choice(["Пустошь-7", "Бункер-Сити", "Новый Рассвет", "Зона Выживания", "Последний Оплот"])
        elif category == "scifi":
            world_name = random.choice(["Колония Альфа", "Звёздный Предел", "Орбита-7", "Новая Земля", "Галактический Пост"])
        elif category == "reality" or category == "slice_of_life":
            world_name = random.choice(["Тихий Город", "Обычный Мир", "Наша Реальность", "Повседневность", "Знакомый Город"])
        elif category == "alt_reality":
            world_name = random.choice(["Альтернатива-42", "Параллель", "Другая Версия", "Реальность-X", "Мир Наизнанку"])

        # Формируем структурированный ответ
        response = f"""Название: {world_name}

Жанр: {genre}
Тег: {tag if tag else 'общий'}
Категория: {category}

📍 География мира:
{geography_text}

⚖️ Законы общества:
{laws_text}

🎭 Традиции и обычаи:
{traditions_text}

🤫 Негласные правила:
{unspoken_text}

👥 Типичные роли персонажей:
{chr(10).join(['   - ' + r for r in random.sample(templates.get('npc_roles', []), min(len(templates.get('npc_roles', [])), 5))])}

🏛️ Фракции:
{chr(10).join(['   - ' + f['name'].format(name=random.choice(['Стальная', 'Теней', 'Света', 'Древняя', 'Новая'])) + ' — ' + f['description'] for f in random.sample(templates.get('faction_types', []), min(len(templates.get('faction_types', [])), 3))])}

📊 Уровень технологий: {templates.get('technology_level', 0.5) * 100:.0f}%
✨ Уровень магии: {templates.get('magic_level', 0.0) * 100:.0f}%

📖 Сюжетная вводная:
Ты стоишь на пороге нового мира. {fill_template(random.choice(templates.get('geography', ['Мир открыт перед тобой.'])))} Твоё приключение начинается здесь."""

        return response

    def _generate_world_from_knowledge(self, genre: str, tag: str) -> str:
        """Генерирует мир на основе знаний из world_gen_knowledge.py (fallback)"""
        try:
            from .world_gen_knowledge import WorldGenKnowledgeEngine

            project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
            data_dir = os.path.join(project_root, "data")

            knowledge_engine = WorldGenKnowledgeEngine(data_dir=data_dir)
            knowledge = knowledge_engine.collect_all_knowledge(genre, tag)
            prompt = knowledge_engine.build_world_gen_prompt(knowledge)

            logging.info(f"📚 _generate_world_from_knowledge: собрано {len(knowledge['books_content'])} книжных концепций")

            # Генерируем через модель
            response = self._generate_response_with_sampling(prompt, max_length=512, max_words=400, temperature=1.2, top_p=0.95)
            return response
        except Exception as e:
            logging.error(f"❌ _generate_world_from_knowledge: {e}")
            return self._generate_fallback_world(genre, tag)

    def _generate_fallback_world(self, genre: str, tag: str) -> str:
        """Простой fallback для генерации мира"""
        import random

        world_name = random.choice(["Эхо", "Предел", "Горизонт", "Тени", "Свет", "Ветер", "Сталь", "Кристалл"])
        world_adj = random.choice(["Забытый", "Вечный", "Скрытый", "Новый", "Древний", "Таинственный"])

        return f"""Название: {world_adj} {world_name}

Жанр: {genre}
Тег: {tag if tag else 'общий'}

📍 География мира:
   - Мир раскинулся на бескрайних просторах, где каждый уголок хранит свои тайны.
   - Ландшафт меняется от суровых гор до тихих долин.

⚖️ Законы общества:
   - Каждый отвечает за свои поступки.
   - Сила слова важнее силы оружия.

🎭 Традиции и обычаи:
   - Праздник Первого Света — начало нового года.
   - Обмен дарами в день полнолуния.

📖 Сюжетная вводная:
Ты стоишь на пороге неизвестного. {world_adj} {world_name} ждёт своего героя. Что ты выберешь?"""