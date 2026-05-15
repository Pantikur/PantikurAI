# knowledge_manager.py — управление знаниями и интеграция с дообучением

import json
import os
import re
from typing import Dict, List, Optional
import shutil
from datetime import datetime


class KnowledgeManager:
    """
    Менеджер знаний, который:
    - Накапливает определения слов из WebSearch
    - Периодически обновляет обучающие данные
    - Генерирует пары для дообучения модели
    """
    
    def __init__(self, knowledge_dir: str = "data/knowledge"):
        self.knowledge_dir = knowledge_dir
        self.words_file = os.path.join(knowledge_dir, "learned_words.json")
        self.training_pairs_file = os.path.join(knowledge_dir, "training_pairs.jsonl")
        self.stats_file = os.path.join(knowledge_dir, "knowledge_stats.json")
        
        # Создаем директорию
        os.makedirs(knowledge_dir, exist_ok=True)
        
        # Инициализируем файлы
        if not os.path.exists(self.words_file):
            self._save_json(self.words_file, [])
            
        if not os.path.exists(self.training_pairs_file):
            open(self.training_pairs_file, 'w').close()
            
        if not os.path.exists(self.stats_file):
            self._save_json(self.stats_file, {
                "total_words": 0,
                "last_update": None,
                "training_pairs_generated": 0
            })
            
        print(f"✅ Менеджер знаний инициализирован: {knowledge_dir}")

    def _save_json(self, filepath: str, data):
        """Сохранение данных в JSON"""
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    def _load_json(self, filepath: str):
        """Загрузка данных из JSON"""
        if os.path.exists(filepath):
            with open(filepath, 'r', encoding='utf-8') as f:
                return json.load(f)
        return None

    def add_word_knowledge(self, word: str, definition: str, source: str = "web_search") -> bool:
        """
        Добавляет новое слово и его определение в систему знаний
        """
        if not word or not definition or len(definition.strip()) < 5:
            return False
            
        # Нормализация слова
        word = word.lower().strip()
        definition = definition.strip()
        
        # Проверяем, уже ли есть такое слово
        words_data = self._load_json(self.words_file) or []
        
        # Проверяем существование слова (с учетом множественного числа, времён и т.д.)
        for item in words_data:
            if item["word"] == word:
                # Обновляем, если новое определение лучше
                if len(definition) > len(item["definition"]):
                    item["definition"] = definition
                    item["source"] = source
                    item["updated_at"] = datetime.now().isoformat()
                    self._save_json(self.words_file, words_data)
                return True

        # Добавляем новое слово
        word_entry = {
            "word": word,
            "definition": definition,
            "source": source,
            "added_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat(),
            "usage_count": 0,
            "last_used": None,
            "difficulty_level": self._assess_difficulty(definition)
        }
        
        words_data.append(word_entry)
        self._save_json(self.words_file, words_data)
        
        # Обновляем статистику
        stats = self._load_json(self.stats_file) or {}
        stats["total_words"] = len(words_data)
        stats["last_update"] = datetime.now().isoformat()
        self._save_json(self.stats_file, stats)
        
        print(f"📚 Добавлено новое слово: '{word}'")
        return True

    def _assess_difficulty(self, definition: str) -> str:
        """Оценивает сложность определения"""
        words = re.findall(r'[а-яА-ЯёЁ]+', definition.lower())
        if len(words) < 10:
            return "simple"
        elif len(words) < 30:
            return "medium"
        else:
            return "complex"

    def generate_training_pairs(self, min_difficulty: str = "medium") -> int:
        """
        Генерирует обучающие пары на основе накопленных знаний
        Возвращает количество сгенерированных пар
        """
        words_data = self._load_json(self.words_file) or []
        if not words_data:
            print("ℹ️ Нет слов для генерации обучающих пар")
            return 0

        # Фильтруем по сложности
        difficulty_map = {"simple": 0, "medium": 1, "complex": 2}
        min_level = difficulty_map.get(min_difficulty, 1)
        
        filtered_words = [
            w for w in words_data 
            if difficulty_map.get(w.get("difficulty_level", "simple"), 0) >= min_level
        ]
        
        if not filtered_words:
            print(f"ℹ️ Нет слов нужной сложности ({min_difficulty}) для генерации")
            return 0

        # Генерируем пары вопрос-ответ
        new_pairs = 0
        with open(self.training_pairs_file, 'a', encoding='utf-8') as f:
            for word_data in filtered_words:
                word = word_data["word"]
                definition = word_data["definition"]
                
                # Разные варианты вопросов
                questions = [
                    f"что такое {word}?",
                    f"какое значение у слова {word}?",
                    f"объясни слово {word}",
                    f"что означает {word}?",
                    f"расскажи про {word}",
                    f"опиши {word}",
                    f"дай определение {word}",
                    f"что такое {word} простыми словами?",
                    f"в чём смысл {word}?",
                    f"расскажи о значении {word}"
                ]
                
                # Разные варианты ответов
                answers = [
                    f"{word} — это {definition}",
                    f"Термин '{word}' означает: {definition}",
                    f"Слово '{word}' значит: {definition}",
                    f"{definition}",
                    f"{word} — это когда {definition.lower() if definition else ''}",
                    f"{word} — это такое понятие: {definition}",
                    f"Вот что такое {word}: {definition}",
                    f"{word} — это {definition.lower() if definition else ''}"
                ]
                
                # Генерируем все возможные комбинации (или ограничим количество)
                max_pairs_per_word = 3  # Ограничиваем количество пар на слово
                for i, question in enumerate(questions[:max_pairs_per_word]):
                    answer = answers[i % len(answers)]
                    
                    pair = {
                        "user": question,
                        "bot": answer,
                        "source": "knowledge_manager",
                        "word": word,
                        "difficulty": word_data.get("difficulty_level", "medium"),
                        "generated_at": datetime.now().isoformat()
                    }
                    
                    f.write(json.dumps(pair, ensure_ascii=False) + "\n")
                    new_pairs += 1
                
                # Обновляем счётчик использования
                word_data["usage_count"] += max_pairs_per_word
                word_data["last_used"] = datetime.now().isoformat()

        # Сохраняем обновленные данные слов
        self._save_json(self.words_file, words_data)
        
        # Обновляем статистику
        stats = self._load_json(self.stats_file) or {}
        stats["training_pairs_generated"] = stats.get("training_pairs_generated", 0) + new_pairs
        stats["last_update"] = datetime.now().isoformat()
        self._save_json(self.stats_file, stats)
        
        print(f"✅ Сгенерировано {new_pairs} обучающих пар из знаний")
        return new_pairs

    def merge_with_user_conversations(self, user_conversations_path: str) -> bool:
        """
        Объединяет сгенерированные обучающие пары с пользовательскими диалогами
        """
        if not os.path.exists(self.training_pairs_file):
            print("❌ Файл обучающих пар не найден")
            return False
            
        if not os.path.exists(user_conversations_path):
            print(f"ℹ️ Файл пользовательских диалогов не найден: {user_conversations_path}")
            # Создаем пустой файл
            open(user_conversations_path, 'w').close()

        try:
            # Читаем существующие диалоги
            existing_conversations = []
            if os.path.getsize(user_conversations_path) > 0:
                with open(user_conversations_path, 'r', encoding='utf-8') as f:
                    for line in f:
                        if line.strip():
                            existing_conversations.append(json.loads(line))

            # Читаем сгенерированные пары
            generated_pairs = []
            with open(self.training_pairs_file, 'r', encoding='utf-8') as f:
                for line in f:
                    if line.strip():
                        generated_pairs.append(json.loads(line))

            # Объединяем (сначала пользовательские, потом сгенерированные)
            all_conversations = existing_conversations + generated_pairs
            
            # Сохраняем объединенные данные
            with open(user_conversations_path, 'w', encoding='utf-8') as f:
                for conv in all_conversations:
                    f.write(json.dumps(conv, ensure_ascii=False) + "\n")

            print(f"✅ Объединено {len(existing_conversations)} пользовательских и {len(generated_pairs)} сгенерированных диалогов")
            print(f"📌 Общее количество диалогов для дообучения: {len(all_conversations)}")
            
            return True
            
        except Exception as e:
            print(f"❌ Ошибка при объединении диалогов: {e}")
            return False

    def get_stats(self) -> Dict:
        """Возвращает статистику знаний"""
        stats = self._load_json(self.stats_file) or {}
        words_data = self._load_json(self.words_file) or []
        
        stats["total_words"] = len(words_data)
        
        # Статистика по сложности
        difficulty_count = {"simple": 0, "medium": 0, "complex": 0}
        for word in words_data:
            diff = word.get("difficulty_level", "simple")
            if diff in difficulty_count:
                difficulty_count[diff] += 1
                
        stats["difficulty_distribution"] = difficulty_count
        
        return stats

    def print_report(self):
        """Печатает отчет о состоянии знаний"""
        stats = self.get_stats()
        
        print("\n" + "="*50)
        print("📊 ОТЧЕТ О ЗНАНИЯХ")
        print("="*50)
        print(f"Всего слов: {stats['total_words']}")
        print(f"Сгенерировано пар: {stats['training_pairs_generated']}")
        if stats['last_update']:
            print(f"Последнее обновление: {stats['last_update']}")
        
        print("\nРаспределение по сложности:")
        for diff, count in stats['difficulty_distribution'].items():
            print(f"  {diff}: {count}")
        
        # Топ-5 самых сложных слов
        words_data = self._load_json(self.words_file) or []
        if words_data:
            sorted_words = sorted(
                words_data, 
                key=lambda x: x.get('usage_count', 0), 
                reverse=True
            )
            
            print("\n🔤 Топ-5 самых используемых слов:")
            for i, word in enumerate(sorted_words[:5], 1):
                print(f"  {i}. {word['word']} ({word.get('usage_count', 0)} использований)")
        
        print("="*50 + "\n")


# Пример использования:
# if __name__ == "__main__":
#     km = KnowledgeManager()
#     km.add_word_knowledge("квантовый", "Относящийся к квантовой физике")
#     km.generate_training_pairs()
#     km.merge_with_user_conversations("data/user_conversations.jsonl")
#     km.print_report()