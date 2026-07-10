# world_gen_knowledge.py — Генерация миров на основе ВСЕХ источников знаний бота

import os
import json
import random
import re
from typing import Any, Dict, List, Optional, Tuple
from pathlib import Path


class WorldGenKnowledgeEngine:
    """
    Двигатель генерации миров на основе реальных знаний бота:
    - Прочитанные книги (data/books/)
    - Диалоги (conversations.json, user_conversations.jsonl)
    - Культурные ссылки (cultural_references.py)
    - Модуль воображения (imaginative_abilities.py)
    - Знания о словах (knowledge_manager.py)
    - Эмоциональные фразы (data/*_emotional_phrases.jsonl)
    - RPG сцены (data/rpg_scenes.jsonl)
    """

    def __init__(self, data_dir: str = "data"):
        self.data_dir = Path(data_dir)
        self.knowledge_cache = {}
        self._load_knowledge_cache()

    def _load_knowledge_cache(self):
        """Загружает кэш знаний"""
        cache_file = self.data_dir / "knowledge_cache.json"
        if cache_file.exists():
            try:
                with open(cache_file, "r", encoding="utf-8") as f:
                    self.knowledge_cache = json.load(f)
            except Exception:
                self.knowledge_cache = {}

    def _load_json_lines(self, filename: str) -> List[str]:
        """Загружает JSONL файл как список строк"""
        filepath = self.data_dir / filename
        if not filepath.exists():
            return []
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                return [line.strip() for line in f if line.strip()]
        except Exception:
            return []

    def _load_books(self) -> List[str]:
        """Загружает тексты книг из data/books/"""
        books_dir = self.data_dir / "books"
        if not books_dir.exists():
            return []
        
        books = []
        for book_file in books_dir.iterdir():
            if book_file.suffix in ['.txt', '.md', '.json', '.jsonl']:
                try:
                    with open(book_file, "r", encoding="utf-8") as f:
                        content = f.read()
                        # Берём первые 2000 символов каждой книги
                        books.append(content[:2000])
                except Exception:
                    pass
        return books

    def _load_conversations(self) -> List[str]:
        """Загружает пользовательские диалоги"""
        convs = []
        # conversations.json
        conv_file = self.data_dir / "conversations.json"
        if conv_file.exists():
            try:
                with open(conv_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    if isinstance(data, list):
                        for conv in data[-50:]:  # Последние 50 диалогов
                            if isinstance(conv, dict) and "message" in conv:
                                convs.append(conv["message"])
                            elif isinstance(conv, str):
                                convs.append(conv)
            except Exception:
                pass
        
        # user_conversations.jsonl
        user_convs = self._load_json_lines("user_conversations.jsonl")
        convs.extend(user_convs)
        
        return convs[-100:]  # Последние 100 сообщений

    def _load_emotional_phrases(self) -> List[str]:
        """Загружает эмоциональные фразы из всех источников"""
        phrases = []
        for filename in self.data_dir.glob("*emotional_phrases*.jsonl"):
            if "clean" not in filename.name:  # Пропускаем чистые версии
                phrases.extend(self._load_json_lines(filename.name))
        return phrases

    def _load_rpg_scenes(self) -> List[str]:
        """Загружает примеры RPG сцен"""
        return self._load_json_lines("rpg_scenes.jsonl")

    def _load_world_examples(self) -> List[str]:
        """Загружает примеры миров"""
        world_dir = self.data_dir / "world_examples"
        if not world_dir.exists():
            return []
        
        examples = []
        for world_file in world_dir.iterdir():
            if world_file.suffix in ['.json', '.jsonl', '.txt']:
                try:
                    with open(world_file, "r", encoding="utf-8") as f:
                        content = f.read()
                        examples.append(content[:1500])
                except Exception:
                    pass
        return examples

    def _extract_knowledge_words(self, genre: str, tag: str) -> List[Dict]:
        """Извлекает релевантные слова из knowledge_manager"""
        # Загружаем learned_words.json
        words_file = self.data_dir / "knowledge" / "learned_words.json"
        if not words_file.exists():
            return []
        
        try:
            with open(words_file, "r", encoding="utf-8") as f:
                words_data = json.load(f)
            
            # Фильтруем по релевантности жанру/тегу
            relevant = []
            genre_lower = genre.lower()
            tag_lower = tag.lower()
            
            for word_entry in words_data:
                word = word_entry.get("word", "")
                definition = word_entry.get("definition", "")
                
                # Проверяем релевантность
                if (genre_lower in word.lower() or 
                    genre_lower in definition.lower() or
                    tag_lower in word.lower() or
                    tag_lower in definition.lower()):
                    relevant.append(word_entry)
                elif len(definition) > 50:  # Берём сложные определения как источники вдохновения
                    relevant.append(word_entry)
            
            return relevant[:20]  # Максимум 20 слов
        except Exception:
            return []

    def _extract_concepts_from_books(self, books: List[str], genre: str) -> List[str]:
        """Извлекает концепции из книг"""
        concepts = []
        genre_lower = genre.lower()
        
        # Ключевые паттерны для извлечения
        patterns = [
            r'(мир[^.]+\.)',  # Предложения про мир
            r'(горо[^.]+\.)',  # Про города
            r'(люди[^.]+\.)',  # Про людей
            r'(маги[^.]+\.)',  # Про магию
            r'(технолог[^.]+\.)',  # Про технологии
            r'(война[^.]+\.)',  # Про войны
            r'(культура[^.]+\.)',  # Про культуру
        ]
        
        for book_text in books[:5]:  # Берём первые 5 книг
            for pattern in patterns:
                matches = re.findall(pattern, book_text, re.IGNORECASE)
                for match in matches[:3]:  # По 3 на паттерн
                    if len(match) > 20 and len(match) < 200:
                        concepts.append(match.strip())
        
        return random.sample(concepts, min(len(concepts), 15))

    def _extract_emotional_atmosphere(self, emotional_phrases: List[str]) -> List[str]:
        """Извлекает эмоциональную атмосферу"""
        if not emotional_phrases:
            return []
        
        # Разбиваем на категории
        categories = {
            "мрачная": [],
            "светлая": [],
            "таинственная": [],
            "драматичная": [],
            "романтичная": [],
            "напряжённая": []
        }
        
        for phrase in emotional_phrases:
            phrase_lower = phrase.lower()
            if any(word in phrase_lower for word in ["тёмн", "мрачн", "печал", "страх"]):
                categories["мрачная"].append(phrase)
            elif any(word in phrase_lower for word in ["светл", "радост", "счаст", "тепл"]):
                categories["светлая"].append(phrase)
            elif any(word in phrase_lower for word in ["тайн", "секрет", "неизвест"]):
                categories["таинственная"].append(phrase)
            elif any(word in phrase_lower for word in ["драм", "конфликт", "борьб"]):
                categories["драматичная"].append(phrase)
            elif any(word in phrase_lower for word in ["любв", "нежн", "сердц"]):
                categories["романтичная"].append(phrase)
            elif any(word in phrase_lower for word in ["напряж", "тревог", "опасност"]):
                categories["напряжённая"].append(phrase)
        
        # Выбираем по 2-3 из каждой категории
        selected = []
        for category, phrases in categories.items():
            if phrases:
                selected.extend(random.sample(phrases, min(len(phrases), 3)))
        
        return selected

    def _extract_rpg_elements(self, rpg_scenes: List[str]) -> Dict[str, List[str]]:
        """Извлекает RPG элементы"""
        elements = {
            "locactions": [],
            "characters": [],
            "plots": [],
            "conflicts": []
        }
        
        for scene in rpg_scenes[:20]:
            scene_lower = scene.lower()
            
            if any(word in scene_lower for word in ["мест", "локац", "город", "лес", "пещер"]):
                elements["locactions"].append(scene[:100])
            elif any(word in scene_lower for word in ["геро", "персонаж", "существо", "npc"]):
                elements["characters"].append(scene[:100])
            elif any(word in scene_lower for word in ["сюжет", "истори", "начал", "начинает"]):
                elements["plots"].append(scene[:100])
            elif any(word in scene_lower for word in ["конфликт", "борьб", "враг", "битв"]):
                elements["conflicts"].append(scene[:100])
        
        # Ограничиваем количество
        for key in elements:
            elements[key] = random.sample(elements[key], min(len(elements[key]), 5))
        
        return elements

    def collect_all_knowledge(self, genre: str, tag: str) -> Dict[str, Any]:
        """
        Собирает ВСЕ знания из всех источников
        """
        knowledge = {
            "genre": genre,
            "tag": tag,
            "books_content": [],
            "conversations": [],
            "cultural_phrases": [],
            "knowledge_words": [],
            "emotional_atmosphere": [],
            "rpg_elements": {},
            "world_examples": [],
            "imaginative_concepts": []
        }
        
        # 1. Книги
        books = self._load_books()
        knowledge["books_content"] = self._extract_concepts_from_books(books, genre)
        
        # 2. Диалоги
        conversations = self._load_conversations()
        knowledge["conversations"] = random.sample(conversations, min(len(conversations), 20))
        
        # 3. Эмоциональные фразы
        emotional_phrases = self._load_emotional_phrases()
        knowledge["emotional_atmosphere"] = self._extract_emotional_atmosphere(emotional_phrases)
        
        # 4. Знания о словах
        knowledge["knowledge_words"] = self._extract_knowledge_words(genre, tag)
        
        # 5. RPG элементы
        rpg_scenes = self._load_rpg_scenes()
        knowledge["rpg_elements"] = self._extract_rpg_elements(rpg_scenes)
        
        # 6. Примеры миров
        knowledge["world_examples"] = self._load_world_examples()
        
        # 7. Фразы из кэша знаний
        if self.knowledge_cache:
            # Берём определения, релевантные жанру
            relevant_definitions = []
            genre_lower = genre.lower()
            for word, definition in self.knowledge_cache.items():
                if genre_lower in word.lower() or genre_lower in definition.lower():
                    relevant_definitions.append(f"{word}: {definition}")
            knowledge["cultural_phrases"] = relevant_definitions[:10]
        
        # 8. Создаём imaginative concepts на основе собранных данных
        knowledge["imaginative_concepts"] = self._create_imaginative_concepts(knowledge)
        
        return knowledge

    def _create_imaginative_concepts(self, knowledge: Dict) -> List[str]:
        """Создаёт творческие концепции на основе собранных знаний"""
        concepts = []
        
        # Комбинируем элементы из разных источников
        if knowledge["books_content"] and knowledge["emotional_atmosphere"]:
            book_concept = random.choice(knowledge["books_content"])
            emotion_concept = random.choice(knowledge["emotional_atmosphere"])
            concepts.append(f"Вдохновлено книгой: «{book_concept}» + атмосфера: {emotion_concept}")
        
        if knowledge["knowledge_words"]:
            word = random.choice(knowledge["knowledge_words"])
            concepts.append(f"Ключевое понятие: «{word['word']}» — {word['definition'][:100]}")
        
        if knowledge["rpg_elements"]["characters"]:
            character = random.choice(knowledge["rpg_elements"]["characters"])
            concepts.append(f"Персонаж: {character}")
        
        if knowledge["rpg_elements"]["locactions"]:
            location = random.choice(knowledge["rpg_elements"]["locactions"])
            concepts.append(f"Место: {location}")
        
        return concepts[:10]

    def build_world_gen_prompt(self, knowledge: Dict) -> str:
        """
        Строит ПРОМПТ для генерации мира на основе ВСЕХ собранных знаний
        """
        genre = knowledge["genre"]
        tag = knowledge["tag"]
        
        prompt = f"""Ты — гениальный писатель-фантаст с доступом к огромной базе знаний.

ЖАНР: {genre}
ТЕГ: {tag}

=== ТВОЯ БАЗА ЗНАНИЙ ===

📚 Книжные концепции:
{chr(10).join(['- ' + c for c in knowledge['books_content'][:5]]) or 'Нет данных'}

💬 Диалоги для стиля:
{chr(10).join(['- ' + c[:80] for c in knowledge['conversations'][:3]]) or 'Нет данных'}

🎭 Эмоциональная атмосфера:
{chr(10).join(['- ' + e for e in knowledge['emotional_atmosphere'][:5]]) or 'Нет данных'}

📖 Знания о словах:
{chr(10).join(['- ' + w['word'] + ': ' + w['definition'][:80] for w in knowledge['knowledge_words'][:3]]) or 'Нет данных'}

⚔️ RPG элементы:
Локации: {chr(10).join(['- ' + l for l in knowledge['rpg_elements']['locactions'][:2]]) or 'Нет данных'}
Персонажи: {chr(10).join(['- ' + c for c in knowledge['rpg_elements']['characters'][:2]]) or 'Нет данных'}

💡 Творческие концепции:
{chr(10).join(['- ' + c for c in knowledge['imaginative_concepts'][:5]]) or 'Нет данных'}

=== ЗАДАЧА ===

Придумай УНИКАЛЬНЫЙ мир, используя ВСЕ эти знания.

Структура ответа:

Название: [Креативное, запоминающееся]

Общее описание мира:
[3-4 абзаца. Используй книжные концепции, эмоциональную атмосферу, знания о словах.
Опиши: как устроен мир, его уникальные законы, историю, роль тега "{tag}".
Будь конкретным, избегай клише.]

Локальное описание:
[Детальное описание места, где находится пользователь.
Используй RPG локации, эмоциональные фразы.
Опиши: звуки, запахи, цвета, текстуры, необычные детали.]

Сюжетная вводная:
[Захватывающее начало истории.
Используй RPG персонажи и сюжеты.
Ответь: почему пользователь здесь? Что происходит сейчас? Что произойдёт?]

=== ТРЕБОВАНИЯ ===
1. Используй реальные знания из базы — не выдумывай на пустом месте
2. Комбинируй элементы из разных источников
3. Будь креативным, но опирайся на факты
4. Избегай шаблонных фраз типа "мир, где магия — основа"
5. Пиши развёрнуто (минимум 800 слов)

{genre}, {tag}:
"""
        return prompt


# Пример использования:
if __name__ == "__main__":
    engine = WorldGenKnowledgeEngine(data_dir="data")
    
    # Собираем знания для жанра "фэнтези" с тегом "магия"
    knowledge = engine.collect_all_knowledge("фэнтези", "магия")
    
    # Строим промпт
    prompt = engine.build_world_gen_prompt(knowledge)
    
    print("=== СОБРАННЫЕ ЗНАНИЯ ===")
    print(f"Книжные концепции: {len(knowledge['books_content'])}")
    print(f"Диалоги: {len(knowledge['conversations'])}")
    print(f"Эмоциональная атмосфера: {len(knowledge['emotional_atmosphere'])}")
    print(f"Знания о словах: {len(knowledge['knowledge_words'])}")
    print(f"RPG элементы: {knowledge['rpg_elements']}")
    print(f"Творческие концепции: {len(knowledge['imaginative_concepts'])}")
    print("\n=== ПРОМПТ ===")
    print(prompt[:500] + "...")
