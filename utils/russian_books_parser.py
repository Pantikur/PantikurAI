# utils/russian_books_parser.py — Парсеры русскоязычных книг (Samlib, Lib.ru, Flibusta)

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


class RussianBooksParser:
    """Парсер для русскоязычных книг с полным текстом."""
    
    def __init__(self, data_dir: str = "data/books"):
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)
        
        # Импортируем BookLearner для создания пар
        from utils.book_learner import BookLearner
        self.learner = BookLearner(data_dir=str(data_dir))
        
        # === SAMLIB.RU ===
        # Самиздат, бесплатные книги, простой HTML
        self.samlib_base = "http://samlib.ru/"
        self.samlib_authors = [
            # Популярные авторы на Samlib
            ("https://samlib.ru/s/sokolow_w_a/", "Соколов В.А."),
            ("https://samlib.ru/k/kowalew_a_w/", "Ковалёв А.В."),
            ("https://samlib.ru/m/mihajlow_a_a/", "Михайлов А.А."),
        ]
        
        # === LIB.RU ===
        # Классика, общественное достояние
        self.libru_base = "http://lib.ru/"
        self.libru_sections = [
            ("Фантастика", "http://lib.ru/HTML_DEFAULT/fantasy.txt"),
            ("Приключения", "http://lib.ru/HTML_DEFAULT/prikl.txt"),
            ("Детектив", "http://lib.ru/DETEKTIWY/"),
            ("Проза", "http://lib.ru/PROZA/"),
        ]
        
        # === FLIBUSTA ===
        # Зеркала (могут меняться)
        self.flibusta_mirrors = [
            "https://flibusta.is",
            "https://flibusta.site",
            "https://flibusta.foo",
        ]
    
    # ==================== SAMLIB.RU ====================
    
    def search_samlib(self, max_books: int = 10) -> List[Dict]:
        """
        Ищет книги на Samlib.ru (Самиздат).
        :param max_books: Максимум результатов
        :return: Список книг
        """
        safe_print("[🔍] Поиск на Samlib.ru...")
        books = []
        
        try:
            # Используем прямой доступ к популярным разделам
            # Samlib структурирован по буквам фамилий авторов
            sections = [
                "http://samlib.ru/a/",  # Авторы на 'А'
                "http://samlib.ru/b/",  # Авторы на 'Б'
                "http://samlib.ru/v/",  # Авторы на 'В'
            ]
            
            for section_url in sections:
                if len(books) >= max_books:
                    break
                
                req = urllib.request.Request(section_url)
                req.add_header('User-Agent', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)')
                req.add_header('Accept', 'text/html')
                
                try:
                    with urllib.request.urlopen(req, timeout=10) as response:
                        html = response.read().decode('cp1251', errors='replace')
                    
                    # Ищем ссылки на авторов
                    author_matches = re.findall(r'<a\s+href="(http://samlib\.ru/[\w/]+/)"[^>]*>([^<]+)</a>', html, re.IGNORECASE)
                    
                    for author_url, author_name in author_matches[:5]:  # До 5 авторов
                        if len(books) >= max_books:
                            break
                        
                        # Заходим на страницу автора
                        try:
                            req_author = urllib.request.Request(author_url)
                            req_author.add_header('User-Agent', 'Mozilla/5.0')
                            
                            with urllib.request.urlopen(req_author, timeout=10) as resp:
                                author_html = resp.read().decode('cp1251', errors='replace')
                            
                            # Ищем произведения .txt
                            work_matches = re.findall(r'<a\s+href="([^"]+\.txt)"[^>]*>([^<]+)</a>', author_html, re.IGNORECASE)
                            
                            for work_link, work_title in work_matches[:1]:  # 1 книга с автора
                                if len(books) >= max_books:
                                    break
                                
                                title = re.sub(r'\s+', ' ', work_title).strip()
                                if len(title) < 5 or len(title) > 200:
                                    continue
                                
                                # Полная ссылка
                                if not work_link.startswith('http'):
                                    base = author_url.rstrip('/') + '/'
                                    work_link = base + work_link
                                
                                book = {
                                    "id": f"samlib_{len(books)}_{int(time.time())}",
                                    "title": title,
                                    "author": author_name.strip(),
                                    "url": work_link,
                                    "source": "samlib",
                                }
                                books.append(book)
                                safe_print(f"  [📚] Найдена книга: {title} ({author_name})")
                            
                            time.sleep(0.3)
                            
                        except:
                            continue
                    
                except:
                    continue
            
            safe_print(f"[✅] Samlib: найдено {len(books)} книг")
            return books
            
        except Exception as e:
            safe_print(f"[❌] Ошибка поиска Samlib: {e}")
            return []
        
    def download_samlib_text(self, book: Dict) -> Optional[str]:
        """
        Скачивает полный текст книги с Samlib.
        :param book: Информация о книге
        :return: Текст книги
        """
        url = book.get("url")
        if not url:
            return None
        
        try:
            safe_print(f"[⬇️] Samlib: {book['title']}")
            
            req = urllib.request.Request(url)
            req.add_header('User-Agent', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)')
            req.add_header('Accept', 'text/plain,text/html')
            
            with urllib.request.urlopen(req, timeout=15) as response:
                # Samlib использует CP1251 (Windows Cyrillic)
                html = response.read().decode('cp1251', errors='replace')
            
            # Очищаем от HTML тегов
            text = re.sub(r'<[^>]+>', '\n', html)
            text = re.sub(r'\n{3,}', '\n\n', text)  # Нормализуем пустые строки
            text = re.sub(r' +', ' ', text).strip()
            
            # Разбиваем на строки и фильтруем
            lines = text.split('\n')
            clean_lines = []
            
            skip_patterns = [
                r'samlib\.ru',
                r'Самиздат',
                r'Библиотека',
                r'Реклама',
                r'О авторе',
                r'Комментарии',
                r'www\.samlib',
            ]
            
            for line in lines:
                line = line.strip()
                
                # Пропускаем короткие строки (< 20 символов) кроме пустых
                if len(line) < 20 and len(line) > 0:
                    continue
                
                # Пропускаем служебные строки
                skip = False
                for pattern in skip_patterns:
                    if re.search(pattern, line, re.IGNORECASE):
                        skip = True
                        break
                
                if not skip and len(line) > 0:
                    clean_lines.append(line)
            
            text = '\n'.join(clean_lines)
            
            if len(text) > 1000:
                safe_print(f"[✅] Samlib: {len(text)} символов")
                return text
            else:
                safe_print(f"[⚠️] Samlib: текст слишком короткий ({len(text)})")
                return None
                
        except Exception as e:
            safe_print(f"[❌] Samlib ошибка: {e}")
            return None
        
    # ==================== LIB.RU ====================
    
    def search_libru(self, section: str = "Фантастика", max_books: int = 10) -> List[Dict]:
        """
        Ищет книги в библиотеке Lib.ru (Мошков).
        :param section: Раздел (Фантастика, Приключения, Детектив, Проза)
        :param max_books: Максимум результатов
        :return: Список книг
        """
        safe_print(f"[🔍] Lib.ru: раздел '{section}'...")
        books = []
        
        # URL для разделов — используем основные каталоги
        section_urls = {
            "Фантастика": "http://lib.ru/HTML_DEFAULT/fantlst.txt",
            "Приключения": "http://lib.ru/HTML_DEFAULT/prikl.txt",
            "Детектив": "http://lib.ru/DETEKTIWY/",
            "Проза": "http://lib.ru/PROZA/",
            "Классика": "http://lib.ru/KLASSIK/",
            "Поэзия": "http://lib.ru/POEZIA/",
        }
        
        url = section_urls.get(section, "http://lib.ru/HTML_DEFAULT/fantlst.txt")
        
        try:
            req = urllib.request.Request(url)
            req.add_header('User-Agent', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)')
            req.add_header('Accept', 'text/html,text/plain')
            
            with urllib.request.urlopen(req, timeout=15) as response:
                # Lib.ru использует KOI8-R (старая Unix-кодировка)
                html = response.read().decode('koi8-r', errors='replace')
            
            # Ищем ссылки на книги
            # Формат: <A HREF="FILE/author_book.txt">Название</A>
            # Или: <A HREF="author.htm">Автор</A>
            matches = re.findall(r'<A\s+HREF="([^"]+)"[^>]*>([^<]+)</A>', html, re.IGNORECASE)
            
            for link, title in matches:
                if len(books) >= max_books:
                    break
                
                # Пропускаем навигацию и технические ссылки
                if '#' in link:
                    continue
                if 'HTML_DEFAULT' in link and not link.endswith('.txt'):
                    continue
                if link.endswith('/') or link.endswith('htm'):
                    continue
                
                # Базовый URL для относительных ссылок
                if link.startswith('http'):
                    full_url = link
                else:
                    base = url.rsplit('/', 1)[0] + '/'
                    full_url = base + link
                
                # Очищаем название
                clean_title = re.sub(r'\s+', ' ', title).strip()
                if len(clean_title) < 3 or len(clean_title) > 200:
                    continue
                
                book = {
                    "id": f"libru_{len(books)}_{int(time.time())}",
                    "title": clean_title,
                    "author": "Неизвестно",
                    "url": full_url,
                    "source": "libru",
                    "section": section,
                }
                books.append(book)
                safe_print(f"  [📚] Найдена книга: {clean_title}")
            
            safe_print(f"[✅] Lib.ru: найдено {len(books)} книг")
            return books
            
        except Exception as e:
            safe_print(f"[❌] Lib.ru ошибка: {e}")
            return []
        
    def download_libru_text(self, book: Dict) -> Optional[str]:
        """
        Скачивает текст книги с Lib.ru.
        :param book: Информация о книге
        :return: Текст книги
        """
        url = book.get("url")
        if not url:
            return None
        
        try:
            safe_print(f"[⬇️] Lib.ru: {book['title']}")
            
            req = urllib.request.Request(url)
            req.add_header('User-Agent', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)')
            req.add_header('Accept', 'text/plain,text/html')
            
            with urllib.request.urlopen(req, timeout=15) as response:
                # Lib.ru использует KOI8-R
                html = response.read().decode('koi8-r', errors='replace')
            
            # Очищаем от HTML тегов
            text = re.sub(r'<[^>]+>', '\n', html)
            text = re.sub(r'\n{3,}', '\n\n', text)  # Нормализуем пустые строки
            text = re.sub(r' +', ' ', text).strip()
            
            # Разбиваем на строки и фильтруем
            lines = text.split('\n')
            clean_lines = []
            
            skip_patterns = [
                r'lib\.ru',
                r'Библиотека Максима Мошкова',
                r'Оригинал здесь',
                r'Last Modified',
                r'HTTP://LIB\.RU',
                r'© Lib\.Ru',
            ]
            
            for line in lines:
                line = line.strip()
                
                # Пропускаем очень короткие строки
                if len(line) < 15 and len(line) > 0:
                    continue
                
                # Пропускаем служебные строки
                skip = False
                for pattern in skip_patterns:
                    if re.search(pattern, line, re.IGNORECASE):
                        skip = True
                        break
                
                if not skip and len(line) > 0:
                    clean_lines.append(line)
            
            text = '\n'.join(clean_lines)
            
            if len(text) > 1000:
                safe_print(f"[✅] Lib.ru: {len(text)} символов")
                return text
            else:
                safe_print(f"[⚠️] Lib.ru: текст слишком короткий ({len(text)})")
                return None
                
        except Exception as e:
            safe_print(f"[❌] Lib.ru ошибка скачивания: {e}")
            return None
        
        try:
            safe_print(f"[⬇️] Lib.ru: {book['title']}")
            
            req = urllib.request.Request(url)
            req.add_header('User-Agent', 'Mozilla/5.0')
            
            with urllib.request.urlopen(req, timeout=15) as response:
                # Lib.ru использует KOI8-R
                html = response.read().decode('koi8-r', errors='ignore')
            
            # Очищаем от HTML
            text = re.sub(r'<[^>]+>', '\n', html)
            text = re.sub(r'\n{3,}', '\n\n', text)  # Нормализуем пустые строки
            text = re.sub(r' +', ' ', text).strip()
            
            # Удаляем служебные элементы
            skip_patterns = [
                r'lib\.ru',
                r'Библиотека Максима Мошкова',
                r'Оригинал здесь',
                r'Last Modified',
            ]
            for pattern in skip_patterns:
                text = re.sub(pattern, '', text, flags=re.IGNORECASE)
            
            if len(text) > 1000:
                safe_print(f"[✅] Lib.ru: {len(text)} символов")
                return text
            else:
                safe_print(f"[⚠️] Lib.ru: текст слишком короткий ({len(text)})")
                return None
                
        except Exception as e:
            safe_print(f"[❌] Lib.ru ошибка скачивания: {e}")
            return None
    
    # ==================== FLIBUSTA ====================
    
    def search_flibusta(self, query: str = "фэнтези", max_books: int = 10) -> List[Dict]:
        """
        Ищет книги на Flibusta.
        :param query: Поисковый запрос
        :param max_books: Максимум результатов
        :return: Список книг
        """
        safe_print(f"[🔍] Flibusta: поиск '{query}'...")
        books = []
        
        # Пробуем зеркала
        for mirror in self.flibusta_mirrors[:2]:  # Первые 2 зеркала
            try:
                # Поиск книг
                search_url = f"{mirror}/book/search?query={urllib.parse.quote(query)}"
                
                req = urllib.request.Request(search_url)
                req.add_header('User-Agent', 'Mozilla/5.0')
                
                with urllib.request.urlopen(req, timeout=10) as response:
                    html = response.read().decode('utf-8', errors='ignore')
                
                # Ищем книги в результатах
                # Формат: <a href="/book/12345">Название</a>
                matches = re.findall(r'<a\s+href="(/book/\d+)"[^>]*>([^<]+)</a>', html, re.IGNORECASE)
                
                for link, title in matches[:max_books]:
                    if len(title.strip()) < 3:
                        continue
                    
                    book = {
                        "id": f"flibusta_{len(books)}",
                        "title": title.strip(),
                        "author": "Неизвестно",
                        "url": f"{mirror}{link}",
                        "source": "flibusta",
                    }
                    books.append(book)
                
                if books:
                    safe_print(f"[✅] Flibusta ({mirror}): найдено {len(books)} книг")
                    break
                
            except Exception as e:
                safe_print(f"[⚠️] Flibusta зеркало {mirror} недоступно: {e}")
                continue
        
        if not books:
            safe_print("[⚠️] Flibusta: ни одно зеркало не доступно")
        
        return books
    
    def download_flibusta_text(self, book: Dict) -> Optional[str]:
        """
        Скачивает текст книги с Flibusta (FB2 конвертируем в текст).
        :param book: Информация о книге
        :return: Текст книги
        """
        url = book.get("url")
        if not url:
            return None
        
        try:
            safe_print(f"[⬇️] Flibusta: {book['title']}")
            
            # Заменяем /book/ на /book/fb2/ для получения FB2
            fb2_url = url.replace("/book/", "/book/fb2/")
            
            req = urllib.request.Request(fb2_url)
            req.add_header('User-Agent', 'Mozilla/5.0')
            
            with urllib.request.urlopen(req, timeout=15) as response:
                fb2_content = response.read().decode('utf-8', errors='ignore')
            
            # Извлекаем текст из FB2
            # FB2 — это XML, извлекаем содержимое <p> тегов
            paragraphs = re.findall(r'<p[^>]*>([^<]+(?:</[^>]+>[^<]+)*)</p>', fb2_content, re.IGNORECASE)
            
            text_parts = []
            for p in paragraphs:
                clean = re.sub(r'<[^>]+>', ' ', p).strip()
                if len(clean) > 50:
                    text_parts.append(clean)
            
            text = '\n\n'.join(text_parts)
            
            if len(text) > 1000:
                safe_print(f"[✅] Flibusta: {len(text)} символов")
                return text
            else:
                safe_print(f"[⚠️] Flibusta: текст слишком короткий ({len(text)})")
                return None
                
        except Exception as e:
            safe_print(f"[❌] Flibusta ошибка: {e}")
            return None
    
    # ==================== ОБЩИЕ МЕТОДЫ ====================
    
    def process_book(self, book: Dict) -> List[Dict]:
        """
        Обрабатывает книгу: скачивает и создаёт обучающие пары.
        :param book: Информация о книге
        :return: Список обучающих пар
        """
        book_id = book.get("id")
        source = book.get("source", "unknown")
        
        if not book_id:
            return []
        
        if self.learner._is_book_processed(book_id):
            safe_print(f"[ℹ️] Книга уже обработана: {book.get('title')}")
            return []
        
        safe_print(f"[📖] Обработка: {book.get('title')} ({source})")
        
        # Скачиваем текст в зависимости от источника
        text = None
        if source == "samlib":
            text = self.download_samlib_text(book)
        elif source == "libru":
            text = self.download_libru_text(book)
        elif source == "flibusta":
            text = self.download_flibusta_text(book)
        
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
                "source": source,
                "text_length": len(text),
            })
            safe_print(f"  [✅] Создано {len(pairs)} пар")
        
        return pairs
    
    def learn_from_russian_books(self, 
                                  sources: List[str] = None,
                                  max_books: int = 10,
                                  topics: List[str] = None) -> List[Dict]:
        """
        Основной метод обучения из русскоязычных книг (Samlib, Lib.ru, Flibusta).
        :param sources: Источники (samlib, libru, flibusta)
        :param max_books: Максимум книг
        :param topics: Темы для поиска
        :return: Список обучающих пар
        """
        if sources is None:
            sources = ["samlib", "libru"]  # Flibusta может быть нестабильна
        
        if topics is None:
            topics = ["фэнтези", "фантастика", "приключения", "детектив"]
        
        safe_print("[🚀] Запуск обучения из русскоязычных книг...")
        safe_print(f"[ℹ️] Источники: {', '.join(sources)}, Макс книг: {max_books}")
        
        all_pairs = []
        books_processed = 0
        books_per_source = max(2, max_books // len(sources))
        
        for source in sources:
            if books_processed >= max_books:
                break
            
            safe_print(f"\n[📚] Источник: {source.upper()}")
            
            books = []
            
            if source == "samlib":
                books = self.search_samlib(max_books=books_per_source)
            
            elif source == "libru":
                # Проходим по разделам
                for section in ["Фантастика", "Приключения", "Проза"]:
                    if books_processed >= max_books:
                        break
                    section_books = self.search_libru(section=section, max_books=books_per_source // 2)
                    books.extend(section_books)
            
            elif source == "flibusta":
                for topic in topics[:2]:
                    if books_processed >= max_books:
                        break
                    topic_books = self.search_flibusta(query=topic, max_books=books_per_source // 2)
                    books.extend(topic_books)
            
            # Обрабатываем книги
            for book in books:
                if books_processed >= max_books:
                    break
                
                pairs = self.process_book(book)
                if pairs:
                    all_pairs.extend(pairs)
                    books_processed += 1
                    safe_print(f"[✅] Обработано: {books_processed}/{max_books}")
                
                time.sleep(random.uniform(1, 3))
            
            time.sleep(random.uniform(2, 5))
        
        safe_print(f"\n[💾] Собрано {len(all_pairs)} пар из {books_processed} книг")
        return all_pairs


def main():
    """Тестирование парсеров."""
    safe_print("[RUN] Russian Books Parser — Тестирование")
    print("=" * 60)
    
    parser = RussianBooksParser()
    
    # Тест 1: Samlib
    safe_print("\n[🧪] Тест 1: Samlib.ru")
    samlib_books = parser.search_samlib(max_books=3)
    for book in samlib_books:
        safe_print(f"  - {book['title']}")
        text = parser.download_samlib_text(book)
        if text:
            safe_print(f"    ✅ {len(text)} символов")
    
    # Тест 2: Lib.ru
    safe_print("\n[🧪] Тест 2: Lib.ru")
    libru_books = parser.search_libru(section="Фантастика", max_books=3)
    for book in libru_books:
        safe_print(f"  - {book['title']}")
        text = parser.download_libru_text(book)
        if text:
            safe_print(f"    ✅ {len(text)} символов")
    
    # Тест 3: Flibusta
    safe_print("\n[🧪] Тест 3: Flibusta")
    flibusta_books = parser.search_flibusta(query="фэнтези", max_books=3)
    for book in flibusta_books:
        safe_print(f"  - {book['title']}")
        text = parser.download_flibusta_text(book)
        if text:
            safe_print(f"    ✅ {len(text)} символов")
    
    safe_print("\n[🎉] Готово!")


if __name__ == "__main__":
    main()
