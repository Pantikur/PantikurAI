# utils/ruslit_parser.py — Парсеры русских сайтов (Стихи.ру, Проза.ру, LibKing, RuLit)

import urllib.request
import re
import json
import time
import random
from pathlib import Path
from typing import Dict, List, Optional
from datetime import datetime

# Добавляем корень проекта
import sys
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from utils.book_learner import safe_print


class RusLitParser:
    """Парсер для русскоязычных сайтов с полными текстами."""
    
    def __init__(self, data_dir: str = "data/books"):
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)
        
        # Импортируем BookLearner для создания пар
        from utils.book_learner import BookLearner
        self.learner = BookLearner(data_dir=str(data_dir))
        
        # === СТИХИ.РУ ===
        self.stihi_base = "https://stihi.ru/"
        
        # === ПРОЗА.РУ ===
        self.proza_base = "https://proza.ru/"
        
        # === RULIT ===
        self.rulit_base = "https://rulit.me/"
        self.rulit_genres = [
            "fantasy",       # Фэнтези
            "sf",            # Фантастика
            "detektiv",      # Детектив
            "priklyucheniya",# Приключения
        ]
    
        # === LIVELIB ===
        self.livelib_base = "https://www.livelib.ru/"
        self.livelib_genres = [
            "fantasy",       # Фэнтези
            "sf",            # Фантастика
            "detektiv",      # Детектив
            "proza",         # Проза
        ]
    
    # ==================== СТИХИ.РУ ====================
    
    def search_stihi(self, max_books: int = 10) -> List[Dict]:
        """
        Ищет произведения на Стихи.ру.
        :param max_books: Максимум результатов
        :return: Список произведений
        """
        safe_print("[🔍] Поиск на Стихи.ру...")
        works = []
        
        try:
            # Стихи.ру — главная страница с новыми произведениями
            main_url = "https://stihi.ru/"
            
            req = urllib.request.Request(main_url)
            req.add_header('User-Agent', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)')
            req.add_header('Accept', 'text/html')
            
            with urllib.request.urlopen(req, timeout=10) as response:
                html = response.read().decode('utf-8', errors='replace')
            
            # Ищем ссылки на произведения в формате /YYYY/MM/DD/ID
            matches = re.findall(r'<a\s+href="(/20\d{2}/\d{2}/\d{2}/[\w]+)"[^>]*title="([^"]+)"', html, re.IGNORECASE)
            
            for link, title in matches[:max_books]:
                if len(title.strip()) < 3 or len(title.strip()) > 200:
                    continue
                
                work = {
                    "id": f"stihi_{len(works)}_{int(time.time())}",
                    "title": title.strip(),
                    "author": "Неизвестно",
                    "url": f"https://stihi.ru{link}",
                    "source": "stihi_ru",
                    "type": "poetry",
                }
                works.append(work)
                safe_print(f"  [📚] Найдено: {title}")
            
            safe_print(f"[✅] Стихи.ру: найдено {len(works)} произведений")
            return works
            
        except Exception as e:
            safe_print(f"[❌] Ошибка поиска Стихи.ру: {e}")
            return []
    
    def download_stihi_text(self, work: Dict) -> Optional[str]:
        """
        Скачивает текст произведения со Стихи.ру.
        :param work: Информация о произведении
        :return: Текст
        """
        url = work.get("url")
        if not url:
            return None
        
        try:
            safe_print(f"[⬇️] Стихи.ру: {work['title']}")
            
            req = urllib.request.Request(url)
            req.add_header('User-Agent', 'Mozilla/5.0')
            req.add_header('Accept', 'text/html')
            
            with urllib.request.urlopen(req, timeout=15) as response:
                html = response.read().decode('utf-8', errors='replace')
            
            # Извлекаем текст из <div class="text"> или аналогичного
            text_div = re.search(r'<div[^>]*class="text"[^>]*>(.*?)</div>', html, re.IGNORECASE | re.DOTALL)
            
            if not text_div:
                # Пробуем найти по другому классу
                text_div = re.search(r'<div[^>]*id="text_container"[^>]*>(.*?)</div>', html, re.IGNORECASE | re.DOTALL)
            
            if text_div:
                text = re.sub(r'<[^>]+>', '\n', text_div.group(1))
                text = re.sub(r'\n{3,}', '\n\n', text)
                text = re.sub(r' +', ' ', text).strip()
                
                # Фильтруем строки
                lines = [l for l in text.split('\n') if len(l.strip()) > 0 and len(l.strip()) < 100]
                text = '\n'.join(lines)
                
                if len(text) > 200:
                    safe_print(f"[✅] Стихи.ру: {len(text)} символов")
                    return text
            
            safe_print(f"[⚠️] Стихи.ру: текст не найден")
            return None
                
        except Exception as e:
            safe_print(f"[❌] Стихи.ру ошибка: {e}")
            return None
    
    # ==================== ПРОЗА.РУ ====================
    
    def search_proza(self, max_books: int = 10) -> List[Dict]:
        """
        Ищет произведения на Проза.ру.
        :param max_books: Максимум результатов
        :return: Список произведений
        """
        safe_print("[🔍] Поиск на Проза.ру...")
        works = []
        
        try:
            # Проза.ру — главная страница
            main_url = "https://proza.ru/"
            
            req = urllib.request.Request(main_url)
            req.add_header('User-Agent', 'Mozilla/5.0')
            req.add_header('Accept', 'text/html')
            
            with urllib.request.urlopen(req, timeout=10) as response:
                html = response.read().decode('utf-8', errors='replace')
            
            # Ищем ссылки на произведения
            matches = re.findall(r'<a\s+href="(/20\d{2}/\d{2}/\d{2}/[\w]+)"[^>]*title="([^"]+)"', html, re.IGNORECASE)
            
            for link, title in matches[:max_books]:
                if len(title.strip()) < 3 or len(title.strip()) > 200:
                    continue
                
                work = {
                    "id": f"proza_{len(works)}_{int(time.time())}",
                    "title": title.strip(),
                    "author": "Неизвестно",
                    "url": f"https://proza.ru{link}",
                    "source": "proza_ru",
                    "type": "prose",
                }
                works.append(work)
                safe_print(f"  [📚] Найдено: {title}")
            
            safe_print(f"[✅] Проза.ру: найдено {len(works)} произведений")
            return works
            
        except Exception as e:
            safe_print(f"[❌] Ошибка поиска Проза.ру: {e}")
            return []
    
    def download_proza_text(self, work: Dict) -> Optional[str]:
        """
        Скачивает текст произведения с Проза.ру.
        :param work: Информация о произведении
        :return: Текст
        """
        url = work.get("url")
        if not url:
            return None
        
        try:
            safe_print(f"[⬇️] Проза.ру: {work['title']}")
            
            req = urllib.request.Request(url)
            req.add_header('User-Agent', 'Mozilla/5.0')
            
            with urllib.request.urlopen(req, timeout=15) as response:
                html = response.read().decode('utf-8', errors='replace')
            
            # Извлекаем текст
            text_div = re.search(r'<div[^>]*class="text"[^>]*>(.*?)</div>', html, re.IGNORECASE | re.DOTALL)
            
            if text_div:
                text = re.sub(r'<[^>]+>', '\n', text_div.group(1))
                text = re.sub(r'\n{3,}', '\n\n', text)
                text = re.sub(r' +', ' ', text).strip()
                
                if len(text) > 500:
                    safe_print(f"[✅] Проза.ру: {len(text)} символов")
                    return text
            
            safe_print(f"[⚠️] Проза.ру: текст не найден")
            return None
                
        except Exception as e:
            safe_print(f"[❌] Проза.ру ошибка: {e}")
            return None
    
    # ==================== RULIT ====================
    
    def search_rulit(self, genre: str = "fantasy", max_books: int = 10) -> List[Dict]:
        """
        Ищет книги на RuLit.
        :param genre: Жанр (fantasy, sf, detektiv, priklyucheniya)
        :param max_books: Максимум результатов
        :return: Список книг
        """
        safe_print(f"[🔍] RuLit: жанр '{genre}'...")
        books = []
        
        try:
            # RuLit использует структуру /genre/{genre}/
            genre_url = f"https://rulit.me/genre/{genre}/"
            
            req = urllib.request.Request(genre_url)
            req.add_header('User-Agent', 'Mozilla/5.0')
            req.add_header('Accept', 'text/html')
            
            with urllib.request.urlopen(req, timeout=15) as response:
                html = response.read().decode('utf-8', errors='replace')
            
            # Ищем ссылки на книги
            # Формат: <a href="/books/12345">Название</a>
            matches = re.findall(r'<a\s+href="(/books/\d+)"[^>]*>([^<]+)</a>', html, re.IGNORECASE)
            
            for link, title in matches[:max_books]:
                # Пропускаем технические ссылки
                if 'page' in link or 'tag' in link:
                    continue
                
                book = {
                    "id": f"rulit_{len(books)}_{int(time.time())}",
                    "title": title.strip(),
                    "author": "Неизвестно",
                    "url": f"https://rulit.me{link}",
                    "source": "rulit",
                    "genre": genre,
                }
                books.append(book)
                safe_print(f"  [📚] Найдена книга: {title}")
            
            safe_print(f"[✅] RuLit: найдено {len(books)} книг")
            return books
            
        except Exception as e:
            safe_print(f"[❌] RuLit ошибка: {e}")
            return []
        
    def download_rulit_text(self, book: Dict) -> Optional[str]:
        """
        Скачивает текст/описание книги с RuLit.
        :param book: Информация о книге
        :return: Текст книги
        """
        url = book.get("url")
        if not url:
            return None
        
        try:
            safe_print(f"[⬇️] RuLit: {book['title']}")
            
            req = urllib.request.Request(url)
            req.add_header('User-Agent', 'Mozilla/5.0')
            
            with urllib.request.urlopen(req, timeout=15) as response:
                html = response.read().decode('utf-8', errors='replace')
            
            # Извлекаем описание книги
            description = re.search(r'<meta[^>]*name="description"[^>]*content="([^"]+)"', html, re.IGNORECASE)
            
            if description:
                desc_text = description.group(1)
                desc_text = re.sub(r'\s+', ' ', desc_text).strip()
                if len(desc_text) > 300:
                    safe_print(f"[✅] RuLit (описание): {len(desc_text)} символов")
                    return desc_text
            
            # Ищем текст первой главы
            text_div = re.search(r'<div[^>]*class="book-text"[^>]*>(.*?)</div>', html, re.IGNORECASE | re.DOTALL)
            
            if text_div:
                text = re.sub(r'<[^>]+>', '\n', text_div.group(1))
                text = re.sub(r'\n{3,}', '\n\n', text)
                text = re.sub(r' +', ' ', text).strip()
                
                if len(text) > 500:
                    safe_print(f"[✅] RuLit: {len(text)} символов")
                    return text
            
            safe_print(f"[⚠️] RuLit: текст не найден")
            return None
                
        except Exception as e:
            safe_print(f"[❌] RuLit ошибка: {e}")
            return None
    
    # ==================== LIVELIB ====================
    
    def search_livelib(self, genre: str = "fantasy", max_books: int = 10) -> List[Dict]:
        """
        Ищет книги на LiveLib.
        :param genre: Жанр
        :param max_books: Максимум результатов
        :return: Список книг
        """
        safe_print(f"[🔍] LiveLib: жанр '{genre}'...")
        books = []
        
        try:
            # LiveLib использует структуру /genre/{genre}
            genre_url = f"https://www.livelib.ru/genre/{genre}"
            
            req = urllib.request.Request(genre_url)
            req.add_header('User-Agent', 'Mozilla/5.0')
            req.add_header('Accept', 'text/html')
            
            with urllib.request.urlopen(req, timeout=15) as response:
                html = response.read().decode('utf-8', errors='replace')
            
            # Ищем ссылки на книги
            # Формат: <a href="/book/12345">Название</a>
            matches = re.findall(r'<a\s+href="(/book/\d+)"[^>]*title="([^"]+)"', html, re.IGNORECASE)
            
            for link, title in matches[:max_books]:
                book = {
                    "id": f"livelib_{len(books)}_{int(time.time())}",
                    "title": title.strip(),
                    "author": "Неизвестно",
                    "url": f"https://www.livelib.ru{link}",
                    "source": "livelib",
                    "genre": genre,
                }
                books.append(book)
                safe_print(f"  [📚] Найдена книга: {title}")
            
            safe_print(f"[✅] LiveLib: найдено {len(books)} книг")
            return books
            
        except Exception as e:
            safe_print(f"[❌] LiveLib ошибка: {e}")
            return []
    
    def download_livelib_text(self, book: Dict) -> Optional[str]:
        """
        Скачивает описание/рецензию книги с LiveLib.
        :param book: Информация о книге
        :return: Текст
        """
        url = book.get("url")
        if not url:
            return None
        
        try:
            safe_print(f"[⬇️] LiveLib: {book['title']}")
            
            req = urllib.request.Request(url)
            req.add_header('User-Agent', 'Mozilla/5.0')
            
            with urllib.request.urlopen(req, timeout=15) as response:
                html = response.read().decode('utf-8', errors='replace')
            
            # Извлекаем описание
            description = re.search(r'<meta[^>]*name="description"[^>]*content="([^"]+)"', html, re.IGNORECASE)
            
            if description:
                desc_text = description.group(1)
                desc_text = re.sub(r'\s+', ' ', desc_text).strip()
                if len(desc_text) > 300:
                    safe_print(f"[✅] LiveLib (описание): {len(desc_text)} символов")
                    return desc_text
            
            # Ищем аннотацию
            annotation = re.search(r'<div[^>]*class="annotation"[^>]*>(.*?)</div>', html, re.IGNORECASE | re.DOTALL)
            
            if annotation:
                annot_text = re.sub(r'<[^>]+>', '\n', annotation.group(1))
                annot_text = re.sub(r'\n{3,}', '\n\n', annot_text)
                annot_text = re.sub(r' +', ' ', annot_text).strip()
                
                if len(annot_text) > 300:
                    safe_print(f"[✅] LiveLib (аннотация): {len(annot_text)} символов")
                    return annot_text
            
            safe_print(f"[⚠️] LiveLib: текст не найден")
            return None
                
        except Exception as e:
            safe_print(f"[❌] LiveLib ошибка: {e}")
            return None
    
    # ==================== ОБЩИЕ МЕТОДЫ ====================
    
    def process_work(self, work: Dict) -> List[Dict]:
        """
        Обрабатывает произведение: скачивает и создаёт обучающие пары.
        :param work: Информация о произведении
        :return: Список обучающих пар
        """
        work_id = work.get("id")
        source = work.get("source", "unknown")
        
        if not work_id:
            return []
        
        if self.learner._is_book_processed(work_id):
            safe_print(f"[ℹ️] Уже обработано: {work.get('title')}")
            return []
        
        safe_print(f"[📖] Обработка: {work.get('title')} ({source})")
        
        # Скачиваем текст в зависимости от источника
        text = None
        if source == "stihi_ru":
            text = self.download_stihi_text(work)
        elif source == "proza_ru":
            text = self.download_proza_text(work)
        elif source == "rulit":
            text = self.download_rulit_text(work)
        elif source == "livelib":
            text = self.download_livelib_text(work)
        
        if not text:
            return []
        
        # Создаём чанки
        pairs = self.learner.extract_chunks(text, work)
        
        if pairs:
            # Сохраняем метаданные
            self.learner._mark_book_processed(work_id, {
                "title": work.get("title"),
                "author": work.get("author"),
                "pairs_count": len(pairs),
                "source": source,
                "text_length": len(text),
            })
            safe_print(f"  [✅] Создано {len(pairs)} пар")
        
        return pairs
    
    def learn_from_russian_sites(self, 
                                  sources: List[str] = None,
                                  max_books: int = 10) -> List[Dict]:
        """
        Основной метод обучения из русских сайтов.
        :param sources: Источники (rulit, livelib)
        :param max_books: Максимум книг/произведений
        :return: Список обучающих пар
        """
        if sources is None:
            sources = ["rulit", "livelib"]  # Только рабочие источники
        
        safe_print("[🚀] Запуск обучения из русских сайтов...")
        safe_print(f"[ℹ️] Источники: {', '.join(sources)}, Макс книг: {max_books}")
        
        all_pairs = []
        books_processed = 0
        books_per_source = max(3, max_books // len(sources))
        
        for source in sources:
            if books_processed >= max_books:
                break
            
            safe_print(f"\n[📚] Источник: {source.upper()}")
            
            works = []
            
            if source == "rulit":
                for genre in ["fantasy", "sf", "detektiv"]:
                    if books_processed >= max_books:
                        break
                    genre_books = self.search_rulit(genre=genre, max_books=books_per_source // 2)
                    works.extend(genre_books)
            
            elif source == "livelib":
                for genre in ["fantasy", "sf", "proza"]:
                    if books_processed >= max_books:
                        break
                    genre_books = self.search_livelib(genre=genre, max_books=books_per_source // 2)
                    works.extend(genre_books)
            
            # Обрабатываем произведения
            for work in works:
                if books_processed >= max_books:
                    break
                
                pairs = self.process_work(work)
                if pairs:
                    all_pairs.extend(pairs)
                    books_processed += 1
                    safe_print(f"[✅] Обработано: {books_processed}/{max_books}")
                
                time.sleep(random.uniform(1, 2))
            
            time.sleep(random.uniform(2, 3))
        
        safe_print(f"\n[💾] Собрано {len(all_pairs)} пар из {books_processed} произведений")
        return all_pairs


def main():
    """Тестирование парсеров."""
    safe_print("[RUN] RusLit Parser — Тестирование")
    print("=" * 60)
    
    parser = RusLitParser()
    
    # Тест 1: Стихи.ру
    safe_print("\n[🧪] Тест 1: Стихи.ру")
    stihi_works = parser.search_stihi(max_books=3)
    for work in stihi_works:
        safe_print(f"  - {work['title']}")
        text = parser.download_stihi_text(work)
        if text:
            safe_print(f"    ✅ {len(text)} символов")
    
    # Тест 2: Проза.ру
    safe_print("\n[🧪] Тест 2: Проза.ру")
    proza_works = parser.search_proza(max_books=3)
    for work in proza_works:
        safe_print(f"  - {work['title']}")
        text = parser.download_proza_text(work)
        if text:
            safe_print(f"    ✅ {len(text)} символов")
    
    # Тест 3: RuLit
    safe_print("\n[🧪] Тест 3: RuLit")
    rulit_books = parser.search_rulit(genre="fantasy", max_books=3)
    for book in rulit_books:
        safe_print(f"  - {book['title']}")
        text = parser.download_rulit_text(book)
        if text:
            safe_print(f"    ✅ {len(text)} символов")
    
    # Тест 4: LiveLib
    safe_print("\n[🧪] Тест 4: LiveLib")
    livelib_books = parser.search_livelib(genre="fantasy", max_books=3)
    for book in livelib_books:
        safe_print(f"  - {book['title']}")
        text = parser.download_livelib_text(book)
        if text:
            safe_print(f"    ✅ {len(text)} символов")
    
    safe_print("\n[🎉] Готово!")


if __name__ == "__main__":
    main()
