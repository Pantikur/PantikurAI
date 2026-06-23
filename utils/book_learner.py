# utils/book_learner.py — Автономное обучение из книг

import os
import sys
import json
import time
import random
import logging
import hashlib
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from datetime import datetime

# Добавляем корень проекта в путь
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

# === Safe print для Windows ===
def safe_print(msg: str):
    """Заменяет эмодзи на ASCII для Windows console"""
    emojis = {
        '📚': '[BOOK]', '🔍': '[SEARCH]', '⬇️': '[DOWN]', '✅': '[OK]',
        '❌': '[ERR]', '💾': '[SAVE]', '📖': '[READ]', '🧠': '[LEARN]',
        '⏳': '[WAIT]', '🚀': '[RUN]', '⚠️': '[WARN]', 'ℹ️': '[INFO]'
    }
    for e, t in emojis.items():
        msg = msg.replace(e, t)
    print(msg, flush=True)


class BookLearner:
    """
    Автономный сборщик знаний из книг.
    Ищет, скачивает и обрабатывает книги для обучения модели.
    """

    def __init__(self, data_dir: str = "data/books", cache_dir: str = "data/cache"):
        self.data_dir = Path(data_dir)
        self.cache_dir = Path(cache_dir)
        self.processed_dir = self.data_dir / "processed"
        self.metadata_file = self.data_dir / "books_metadata.json"
        
        # Создаём директории
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.processed_dir.mkdir(parents=True, exist_ok=True)
        
        # Метаданные обработанных книг
        self.processed_books = self._load_metadata()
        
        # Темы для поиска книг
        self.topics = [
            # === ПСИХОЛОГИЯ И ФИЛОСОФИЯ ===
            "психология общения",
            "философия жизни",
            "эмоциональный интеллект",
            "самопознание",
            "психология отношений",
            "экзистенциальная психология",
            "когнитивная психология",
            "позитивная психология",
            
            # === ФАНТЕЗИ И RPG ===
            "фэнтези миры",
            "магические системы",
            "эльфы и гномы",
            "драконы и демоны",
            "RPG приключения",
            "подземелья и драконы",
            "средневековое фэнтези",
            
            # === НАУЧНАЯ ФАНТАСТИКА ===
            "научная фантастика",
            "космос и цивилизации",
            "искусственный интеллект",
            "киберпанк",
            "будущее человечества",
            
            # === ЛИТЕРАТУРА ===
            "классическая литература",
            "современная проза",
            "романы о любви",
            "приключенческие романы",
            "детективы",
            
            # === САМОРАЗВИТИЕ ===
            "мотивация и успех",
            "тайм-менеджмент",
            "лидерство",
            "креативность",
            "осознанность",
        ]
        
        # Настройки
        self.max_books_per_topic = 2  # Максимум книг на тему
        self.min_text_length = 1000  # Минимальная длина текста
        self.chunk_size = 500  # Размер чанка для обработки
        self.max_chunks_per_book = 20  # Максимум чанков на книгу

    def _load_metadata(self) -> Dict:
        """Загружает метаданные обработанных книг."""
        if self.metadata_file.exists():
            try:
                with open(self.metadata_file, "r", encoding="utf-8") as f:
                    return json.load(f)
            except:
                return {}
        return {}

    def _save_metadata(self):
        """Сохраняет метаданные."""
        with open(self.metadata_file, "w", encoding="utf-8") as f:
            json.dump(self.processed_books, f, ensure_ascii=False, indent=2)

    def _is_book_processed(self, book_id: str) -> bool:
        """Проверяет, была ли книга уже обработана."""
        return book_id in self.processed_books

    def _mark_book_processed(self, book_id: str, metadata: Dict):
        """Отмечает книгу как обработанную."""
        self.processed_books[book_id] = {
            "processed_at": datetime.now().isoformat(),
            **metadata
        }
        self._save_metadata()

    def search_google_books(self, query: str, max_results: int = 5) -> List[Dict]:
        """
        Ищет книги через Google Books API.
        :param query: Поисковый запрос
        :param max_results: Максимум результатов
        :return: Список книг
        """
        import urllib.request
        import urllib.parse
        
        safe_print(f"[SEARCH] Поиск книг по запросу: {query}")
        
        try:
            # Формируем URL
            base_url = "https://www.googleapis.com/books/v1/volumes"
            params = {
                "q": query,
                "maxResults": max_results,
                "printType": "books",
                "langRestrict": "ru",
                "orderBy": "relevance"
            }
            url = f"{base_url}?{urllib.parse.urlencode(params)}"
            
            # Делаем запрос
            req = urllib.request.Request(url)
            req.add_header('User-Agent', 'Mozilla/5.0')
            
            with urllib.request.urlopen(req, timeout=10) as response:
                data = json.loads(response.read().decode('utf-8'))
            
            books = []
            for item in data.get("items", []):
                volume_info = item.get("volumeInfo", {})
                book = {
                    "id": item.get("id"),
                    "title": volume_info.get("title", "Без названия"),
                    "authors": volume_info.get("authors", ["Неизвестно"]),
                    "publisher": volume_info.get("publisher", ""),
                    "published_date": volume_info.get("publishedDate", ""),
                    "description": volume_info.get("description", ""),
                    "categories": volume_info.get("categories", []),
                    "language": volume_info.get("language", ""),
                    "info_link": volume_info.get("infoLink", ""),
                }
                books.append(book)
            
            safe_print(f"[OK] Найдено {len(books)} книг")
            return books
            
        except Exception as e:
            safe_print(f"[ERR] Ошибка поиска книг: {e}")
            return []

    def search_gutenberg(self, query: str, max_results: int = 5) -> List[Dict]:
        """
        Ищет книги в Project Gutenberg.
        :param query: Поисковый запрос
        :param max_results: Максимум результатов
        :return: Список книг
        """
        safe_print(f"[SEARCH] Поиск в Project Gutenberg: {query}")
        
        try:
            # Gutenberg API
            url = f"https://gutendex.com/books?search={urllib.parse.quote(query)}&languages=ru"
            
            req = urllib.request.Request(url)
            req.add_header('User-Agent', 'Mozilla/5.0')
            
            with urllib.request.urlopen(req, timeout=10) as response:
                data = json.loads(response.read().decode('utf-8'))
            
            books = []
            for item in data.get("results", [])[:max_results]:
                book = {
                    "id": str(item.get("id")),
                    "title": item.get("title", "Без названия"),
                    "authors": [a.get("name", "") for a in item.get("authors", [])],
                    "languages": item.get("languages", []),
                    "formats": item.get("formats", {}),
                    "gutenberg_url": f"https://www.gutenberg.org/ebooks/{item.get('id')}",
                }
                books.append(book)
            
            safe_print(f"[OK] Найдено {len(books)} книг в Gutenberg")
            return books
            
        except Exception as e:
            safe_print(f"[ERR] Ошибка поиска в Gutenberg: {e}")
            return []

    def download_gutenberg_text(self, book: Dict) -> Optional[str]:
        """
        Скачивает текст книги из Project Gutenberg.
        :param book: Информация о книге
        :return: Текст книги или None
        """
        import urllib.request
        
        formats = book.get("formats", {})
        text_url = None
        
        # Ищем текстовый формат
        for key, url in formats.items():
            if "text/plain" in key and "utf-8" in key.lower():
                text_url = url
                break
        
        if not text_url:
            # Пробуем найти любой text/plain
            for key, url in formats.items():
                if "text/plain" in key:
                    text_url = url
                    break
        
        if not text_url:
            safe_print(f"[WARN] Нет текстового формата для {book['title']}")
            return None
        
        try:
            safe_print(f"[DOWN] Скачивание: {book['title']}")
            
            req = urllib.request.Request(text_url)
            req.add_header('User-Agent', 'Mozilla/5.0')
            
            with urllib.request.urlopen(req, timeout=30) as response:
                text = response.read().decode('utf-8', errors='ignore')
            
            # Очищаем от шапки и подвала Gutenberg
            text = self._clean_gutenberg_text(text)
            
            safe_print(f"[OK] Скачано {len(text)} символов")
            return text
            
        except Exception as e:
            safe_print(f"[ERR] Ошибка скачивания: {e}")
            return None

    def _clean_gutenberg_text(self, text: str) -> str:
        """Очищает текст от служебных блоков Gutenberg."""
        # Находим начало основного текста
        start_markers = [
            "*** START OF THE PROJECT GUTENBERG EBOOK",
            "***START OF THE PROJECT GUTENBERG EBOOK",
            "Начало файла",
        ]
        
        end_markers = [
            "*** END OF THE PROJECT GUTENBERG EBOOK",
            "***END OF THE PROJECT GUTENBERG EBOOK",
            "Конец файла",
        ]
        
        start_idx = 0
        for marker in start_markers:
            if marker in text:
                start_idx = text.find(marker) + len(marker)
                # Пропускаем до конца строки
                if "\n" in text[start_idx:]:
                    start_idx = text.find("\n", start_idx) + 1
                break
        
        end_idx = len(text)
        for marker in end_markers:
            if marker in text:
                end_idx = text.find(marker)
                break
        
        return text[start_idx:end_idx].strip()

    def extract_chunks(self, text: str, book_metadata: Dict) -> List[Dict]:
        """
        Разбивает текст на чанки для обучения.
        :param text: Текст книги
        :param book_metadata: Метаданные книги
        :return: Список чанков
        """
        chunks = []
        
        # Разбиваем на абзацы
        paragraphs = [p.strip() for p in text.split('\n\n') if len(p.strip()) > 50]
        
        current_chunk = []
        current_length = 0
        
        for para in paragraphs:
            current_chunk.append(para)
            current_length += len(para)
            
            if current_length >= self.chunk_size:
                chunk_text = "\n".join(current_chunk)
                chunk = self._create_training_chunk(chunk_text, book_metadata)
                if chunk:
                    chunks.append(chunk)
                
                current_chunk = []
                current_length = 0
                
                if len(chunks) >= self.max_chunks_per_book:
                    break
        
        # Последний чанк
        if current_chunk:
            chunk_text = "\n".join(current_chunk)
            chunk = self._create_training_chunk(chunk_text, book_metadata)
            if chunk:
                chunks.append(chunk)
        
        return chunks

    def _create_training_chunk(self, text: str, book_metadata: Dict) -> Optional[Dict]:
        """
        Создаёт обучающий чанк из текста.
        :param text: Текст чанка
        :param book_metadata: Метаданные книги
        :return: Обучающая пара или None
        """
        if len(text) < self.min_text_length:
            return None
        
        # Создаём хэш для уникальности
        text_hash = hashlib.md5(text.encode('utf-8')).hexdigest()[:12]
        
        # Формируем контекст
        title = book_metadata.get("title", "Неизвестно")
        authors = ", ".join(book_metadata.get("authors", ["Неизвестно"]))
        
        # Создаём несколько вариантов обучающих пар
        pairs = []
        
        # Вариант 1: Прямое цитирование
        pairs.append({
            "user": f"Расскажи что-то из книги \"{title}\".",
            "bot": text[:500] + "..." if len(text) > 500 else text,
            "source": {
                "type": "book",
                "title": title,
                "authors": authors,
                "chunk_id": text_hash
            }
        })
        
        # Вариант 2: Вопрос-ответ
        # Берём первое предложение как контекст
        first_sentence = text.split('.')[0] + "."
        pairs.append({
            "user": f"Что говорится о \"{first_sentence[:100]}...\"?",
            "bot": text,
            "source": {
                "type": "book",
                "title": title,
                "authors": authors,
                "chunk_id": text_hash + "_qa"
            }
        })
        
        return pairs

    def process_book(self, book: Dict, source: str = "gutenberg") -> List[Dict]:
        """
        Обрабатывает книгу: скачивает и извлекает чанки.
        :param book: Информация о книге
        :param source: Источник (gutenberg, google)
        :return: Список обучающих пар
        """
        book_id = book.get("id")
        
        if not book_id:
            return []
        
        if self._is_book_processed(book_id):
            safe_print(f"[INFO] Книга уже обработана: {book.get('title')}")
            return []
        
        safe_print(f"[📖] Обработка книги: {book.get('title')}")
        
        all_pairs = []
        
        if source == "gutenberg":
            text = self.download_gutenberg_text(book)
            if text:
                chunks = self.extract_chunks(text, book)
                for chunk_pairs in chunks:
                    if isinstance(chunk_pairs, list):
                        all_pairs.extend(chunk_pairs)
                
                # Сохраняем метаданные
                self._mark_book_processed(book_id, {
                    "title": book.get("title"),
                    "authors": book.get("authors"),
                    "chunks_count": len(all_pairs),
                    "source": source
                })
        
        return all_pairs

    def learn_from_books(self, topics: Optional[List[str]] = None, 
                         max_books: int = 10) -> List[Dict]:
        """
        Основной метод обучения из книг.
        :param topics: Темы для поиска (если None, используются self.topics)
        :param max_books: Максимум книг для обработки
        :return: Список всех обучающих пар
        """
        if topics is None:
            topics = self.topics
        
        safe_print("[🚀] Запуск автономного обучения из книг...")
        safe_print(f"[ℹ️] Тем: {len(topics)}, Макс книг: {max_books}")
        
        all_pairs = []
        books_processed = 0
        
        for topic in topics:
            if books_processed >= max_books:
                break
            
            safe_print(f"\n[🔍] Тема: {topic}")
            
            # Поиск в Gutenberg
            gutenberg_books = self.search_gutenberg(topic, max_results=self.max_books_per_topic)
            
            for book in gutenberg_books:
                if books_processed >= max_books:
                    break
                
                pairs = self.process_book(book, source="gutenberg")
                if pairs:
                    all_pairs.extend(pairs)
                    books_processed += 1
                    safe_print(f"[✅] Обработано: {books_processed}/{max_books} книг")
                
                # Задержка между запросами
                time.sleep(random.uniform(1, 3))
            
            # Задержка между темами
            time.sleep(random.uniform(2, 5))
        
        safe_print(f"\n[💾] Всего собрано {len(all_pairs)} обучающих пар из {books_processed} книг")
        
        return all_pairs

    def save_training_pairs(self, pairs: List[Dict], output_file: str = "data/books_training_pairs.jsonl"):
        """Сохраняет обучающие пары в файл."""
        if not pairs:
            safe_print("[WARN] Нет пар для сохранения")
            return
        
        output_path = Path(output_file)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_path, "w", encoding="utf-8") as f:
            for pair in pairs:
                f.write(json.dumps(pair, ensure_ascii=False) + "\n")
        
        safe_print(f"[SAVE] Сохранено {len(pairs)} пар в {output_file}")

    def get_statistics(self) -> Dict:
        """Возвращает статистику обработанных книг."""
        return {
            "total_books": len(self.processed_books),
            "books": list(self.processed_books.values()),
            "last_updated": datetime.now().isoformat()
        }


def main():
    """Тестирование и запуск обучения."""
    safe_print("[RUN] BookLearner — Автономное обучение из книг")
    print("=" * 60)
    
    learner = BookLearner()
    
    # Запуск обучения
    safe_print("\n[🧠] Начало сбора знаний из книг...")
    
    # Можно настроить темы
    topics = [
        "психология общения",
        "философия жизни",
        "фэнтези миры",
        "научная фантастика",
    ]
    
    pairs = learner.learn_from_books(topics=topics, max_books=5)
    
    if pairs:
        # Сохранение
        learner.save_training_pairs(pairs)
        
        # Статистика
        stats = learner.get_statistics()
        safe_print(f"\n[STATS] Обработано книг: {stats['total_books']}")
    else:
        safe_print("[WARN] Не удалось собрать обучающие пары")
    
    safe_print("\n[HAPPY] Готово!")


if __name__ == "__main__":
    main()
