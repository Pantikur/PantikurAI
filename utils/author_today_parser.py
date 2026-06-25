# utils/author_today_parser.py — Парсер Author.Today

import urllib.request
import re
import json
import time
import random
from pathlib import Path
from typing import Dict, List, Optional

# Добавляем корень проекта
import sys
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from utils.book_learner import BookLearner

def safe_print(msg: str):
    """Безопасный print для Windows."""
    emojis = {
        '📚': '[BOOK]', '🔍': '[SEARCH]', '⬇️': '[DOWN]', '✅': '[OK]',
        '❌': '[ERR]', '💾': '[SAVE]', '📖': '[READ]', '🧠': '[LEARN]',
        '⏳': '[WAIT]', '🚀': '[RUN]', '⚠️': '[WARN]', 'ℹ️': '[INFO]'
    }
    for e, t in emojis.items():
        msg = msg.replace(e, t)
    try:
        print(msg.encode('utf-8').decode('cp1251', errors='replace'), flush=True)
    except:
        print(msg, flush=True)


class AuthorTodayParser:
    """Парсер для Author.Today — платформа с бесплатными книгами."""
    
    def __init__(self, data_dir: str = "data/books"):
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)
        
        # Жанры Author.Today (URL + название)
        # Используем фильтр ?accessType=free для бесплатных книг
        self.genres = [
            ("Фэнтези", "https://author.today/work/genre/fantasy?accessType=free"),
            ("Романтическое фэнтези", "https://author.today/work/genre/romfant?accessType=free"),
            ("Боевое фэнтези", "https://author.today/work/genre/boevoye_fentezi?accessType=free"),
            ("Городское фэнтези", "https://author.today/work/genre/urban_fantasy?accessType=free"),
            ("Мистика", "https://author.today/work/genre/mystics?accessType=free"),
            ("Современная проза", "https://author.today/work/genre/modern_prose?accessType=free"),
            ("Фантастика", "https://author.today/work/genre/science_fiction?accessType=free"),
            ("Попаданцы", "https://author.today/work/genre/popadancy?accessType=free"),
            ("Приключения", "https://author.today/work/genre/adventures?accessType=free"),
            ("Ужасы", "https://author.today/work/genre/horror?accessType=free"),
            ("Детектив", "https://author.today/work/genre/detective?accessType=free"),
            ("ЛитРПГ", "https://author.today/work/genre/litrpg?accessType=free"),
        ]
        
        self.learner = BookLearner(data_dir=str(data_dir))
    
    def search_by_genre(self, genre_url: str, genre_name: str = "", max_results: int = 10) -> List[Dict]:
        """
        Ищет книги по жанру на Author.Today.
        :param genre_url: URL жанра
        :param genre_name: Название жанра для лога
        :param max_results: Максимум результатов
        :return: Список книг
        """
        safe_print(f"[🔍] Жанр Author.Today: {genre_name or genre_url}")
        books = []
        
        try:
            req = urllib.request.Request(genre_url)
            req.add_header('User-Agent', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36')
            req.add_header('Accept', 'text/html,application/xhtml+xml')
            req.add_header('Accept-Language', 'ru-RU,ru;q=0.9')
            req.add_header('Referer', 'https://author.today/')
            
            with urllib.request.urlopen(req, timeout=15) as response:
                html = response.read().decode('utf-8', errors='ignore')
            
            # === РАЗБИВАЕМ НА БЛОКИ ПО КНИГАМ ===
            # Ищем <div class="book-row">...</div>
            book_rows = html.split('<div class="book-row"')
            
            safe_print(f"  [ℹ️] Найдено блоков: {len(book_rows) - 1}")
            
            # Пропускаем первый блок (до первой книги)
            for row_html in book_rows[1:]:
                if len(books) >= max_results:
                    break
                
                # Берём первые 1000 символов блока
                block = row_html[:1000]
                
                # 1. Извлекаем work_id из href="/work/{id}"
                work_match = re.search(r'href="/work/(\d+)"', block)
                if not work_match:
                    continue
                work_id = work_match.group(1)
                work_url = f"/work/{work_id}"
                
                # 2. Извлекаем название из <div class="book-title">
                # Формат: <div class="book-title"><a ...>Название</a></div>
                title_match = re.search(r'<div\s+class="book-title"[^>]*>.*?<a[^>]*>([^<]+)</a>', block, re.IGNORECASE | re.DOTALL)
                if not title_match:
                    continue
                
                title = title_match.group(1).strip()
                if len(title) < 3 or len(title) > 200:
                    continue
                
                # 3. Извлекаем автора (если есть)
                author = "Неизвестно"
                # Ищем после book-title
                pos = block.find('</div>', block.find('book-title'))
                if pos != -1:
                    snippet = block[pos:pos+300]
                    author_match = re.search(r'<span[^>]*>([^<]+)</span>', snippet)
                    if author_match:
                        author = author_match.group(1).strip()
                
                book_info = {
                    "id": f"at_{work_id}",
                    "title": title,
                    "work_id": work_id,
                    "author": author,
                    "url": f"https://author.today{work_url}",
                    "reader_url": f"https://author.today{work_url}",
                    "source": "author_today",
                    "genre": genre_name,
                }
                
                books.append(book_info)
                safe_print(f"  [📚] Найдена книга: {title} ({author})")
            
            safe_print(f"[✅] Найдено {len(books)} книг в жанре '{genre_name}'")
            return books
            
        except Exception as e:
            safe_print(f"[❌] Ошибка поиска: {type(e).__name__}: {e}")
            return []
    
    def download_book_text(self, book: Dict) -> Optional[str]:
        """
        Скачивает текст книги (описание/аннотацию) с Author.Today.
        Полные главы требуют JavaScript, поэтому используем описание.
        :param book: Информация о книге
        :return: Текст описания или None
        """
        work_url = book.get("url")
        if not work_url:
            return None
        
        try:
            safe_print(f"[⬇️] Скачивание: {book['title']}")
            
            req = urllib.request.Request(work_url)
            req.add_header('User-Agent', 'Mozilla/5.0')
            req.add_header('Accept', 'text/html,application/xhtml+xml')
            req.add_header('Accept-Language', 'ru-RU,ru;q=0.9')
            
            with urllib.request.urlopen(req, timeout=15) as response:
                html = response.read().decode('utf-8', errors='ignore')
            
            # Извлекаем описание из JSON-LD
            # Формат: "description": "<p>Текст</p><p>...</p>"
            json_ld_match = re.search(r'<script type="application/ld\+json"[^>]*>(.*?)</script>', html, re.DOTALL)
            
            if not json_ld_match:
                safe_print(f"[⚠️] JSON-LD не найден")
                return None
                
            json_text = json_ld_match.group(1)
            
            # Извлекаем description
            desc_match = re.search(r'"description":\s*"([^"]+)"', json_text)
            if not desc_match:
                safe_print(f"[⚠️] Description не найден")
                return None
            
            description = desc_match.group(1)
            
            # Очищаем от HTML тегов и экранирования
            description = description.replace('\\n', '\n').replace('\\"', '"')
            description = re.sub(r'<[^>]+>', ' ', description)  # Удаляем HTML теги
            description = re.sub(r'\s+', ' ', description).strip()  # Нормализуем пробелы
            
            # Автор.Today: описание может быть коротким, дополним мета-тегом
            if len(description) < 500:
                # Пробуем найти в meta description
                meta_desc = re.search(r'<meta[^>]*name="description"[^>]*content="([^"]+)"', html, re.IGNORECASE)
                if meta_desc:
                    meta_text = meta_desc.group(1)
                    meta_text = re.sub(r'<[^>]+>', ' ', meta_text)
                    meta_text = re.sub(r'\s+', ' ', meta_text).strip()
                    if len(meta_text) > len(description):
                        description = meta_text
            
            if len(description) > 300:  # Минимум 300 символов для описания
                safe_print(f"[✅] Описание: {len(description)} символов")
                return description
            else:
                safe_print(f"[⚠️] Описание слишком короткое: {len(description)}")
                return None
                
        except Exception as e:
            safe_print(f"[❌] Ошибка скачивания: {type(e).__name__}: {e}")
            return None
    
    def process_book(self, book: Dict) -> List[Dict]:
        """
        Обрабатывает книгу: скачивает и создаёт обучающие пары.
        :param book: Информация о книге
        :return: Список обучающих пар
        """
        book_id = book.get("id")
        if not book_id:
            return []
        
        if self.learner._is_book_processed(book_id):
            safe_print(f"[ℹ️] Книга уже обработана: {book.get('title')}")
            return []
        
        safe_print(f"[📖] Обработка: {book.get('title')}")
        
        text = self.download_book_text(book)
        if not text:
            return []
        
        # Создаём чанки
        pairs = self.learner.extract_chunks(text, book)
        
        if pairs:
            # Сохраняем метаданные
            self.learner._mark_book_processed(book_id, {
                "title": book.get("title"),
                "author": book.get("author"),
                "pairs_count": len(pairs),
                "source": "author_today",
                "genre": book.get("genre"),
            })
            safe_print(f"  [✅] Создано {len(pairs)} пар")
        
        return pairs
    
    def learn_from_author_today(self, genres: Optional[List[str]] = None, 
                                 max_books: int = 10) -> List[Dict]:
        """
        Основной метод обучения из книг Author.Today.
        :param genres: Список жанров (None = все из self.genres)
        :param max_books: Максимум книг
        :return: Список обучающих пар
        """
        # Маппинг русских названий в URL
        genre_url_map = {
            "фэнтези": "https://author.today/work/genre/fantasy?accessType=free",
            "попаданцы": "https://author.today/work/genre/popadancy?accessType=free",
            "фантастика": "https://author.today/work/genre/science_fiction?accessType=free",
            "мистика": "https://author.today/work/genre/mystics?accessType=free",
            "детектив": "https://author.today/work/genre/detective?accessType=free",
            "приключения": "https://author.today/work/genre/adventures?accessType=free",
            "психология": "https://author.today/work/genre/psihologija?accessType=free",
            "философия": "https://author.today/work/genre/filosofija?accessType=free",
            "современная проза": "https://author.today/work/genre/modern_prose?accessType=free",
            "боевое фэнтези": "https://author.today/work/genre/boevoye_fentezi?accessType=free",
            "городское фэнтези": "https://author.today/work/genre/urban_fantasy?accessType=free",
            "научная фантастика": "https://author.today/work/genre/nauchnaya_fantastika?accessType=free",
            "альтернативная история": "https://author.today/work/genre/alternativnaya_istoriya?accessType=free",
            "литрпг": "https://author.today/work/genre/litrpg?accessType=free",
            "ужасы": "https://author.today/work/genre/horror?accessType=free",
            "романтика": "https://author.today/work/genre/romantika?accessType=free",
            "драма": "https://author.today/work/genre/drama?accessType=free",
            "любовное фэнтези": "https://author.today/work/genre/romfant?accessType=free",
            "историческое фэнтези": "https://author.today/work/genre/istoricheskoe_fentezi?accessType=free",
            "молодежная проза": "https://author.today/work/genre/molodezhnaya_proza?accessType=free",
        }
        
        if genres is None:
            genres = [g[0] for g in self.genres]
        
        safe_print("[🚀] Запуск обучения из Author.Today...")
        safe_print(f"[ℹ️] Жанров: {len(genres)}, Макс книг: {max_books}")
        
        all_pairs = []
        books_processed = 0
        
        for genre_name in genres:
            if books_processed >= max_books:
                break
            
            # Получаем URL для жанра
            genre_url = genre_url_map.get(genre_name.lower())
            if not genre_url:
                safe_print(f"[⚠️] Не найден URL для жанра '{genre_name}'")
                continue
            
            safe_print(f"\n[🔍] Жанр: {genre_name}")
            
            # Ищем книги
            books = self.search_by_genre(genre_url, genre_name, max_results=5)
            
            for book in books:
                if books_processed >= max_books:
                    break
                
                pairs = self.process_book(book)
                if pairs:
                    all_pairs.extend(pairs)
                    books_processed += 1
                    safe_print(f"[✅] Обработано: {books_processed}/{max_books}")
                
                # Пауза между книгами
                time.sleep(random.uniform(2, 4))
            
            # Пауза между жанрами
            time.sleep(random.uniform(3, 5))
        
        safe_print(f"\n[💾] Всего собрано {len(all_pairs)} пар из {books_processed} книг")
        return all_pairs


def main():
    """Тестирование парсера Author.Today."""
    safe_print("[RUN] Author.Today Parser")
    print("=" * 60)
    
    parser = AuthorTodayParser()
    
    # Тест: поиск по жанру
    safe_print("\n[🧪] Тест: поиск по жанру 'Фэнтези'")
    books = parser.search_by_genre(
        "https://author.today/work/genre/fantasy",
        "Фэнтези",
        max_results=5
    )
    
    safe_print(f"\n[✅] Найдено книг: {len(books)}")
    for book in books:
        safe_print(f"  - {book['title']} ({book['author']})")
    
    # Тест: скачивание текста (первая книга)
    if books:
        safe_print("\n[🧪] Тест: скачивание текста")
        text = parser.download_book_text(books[0])
        if text:
            safe_print(f"[✅] Скачано {len(text)} символов")
            safe_print(f"   Начало: {text[:100]}...")
        else:
            safe_print("[❌] Не удалось скачать текст")
    
    safe_print("\n[🎉] Готово!")


if __name__ == "__main__":
    main()
