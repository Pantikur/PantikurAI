# utils/litnet_parser.py — Парсер для Litnet (через Selenium)

import time
import re
import random
from pathlib import Path
from typing import Dict, List, Optional

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException

try:
    from webdriver_manager.chrome import ChromeDriverManager
    HAS_WDM = True
except ImportError:
    HAS_WDM = False

import sys
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from utils.book_learner import safe_print, BookLearner


class LitnetParser:
    """Парсер для Litnet.com — русскоязычные книги с полными текстами."""
    
    def __init__(self, data_dir: str = "data/books", headless: bool = True):
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.learner = BookLearner(data_dir=str(data_dir))
        
        self.headless = headless
        self.driver = None
        
        self.litnet_base = "https://litnet.com/"
        
        # Популярные жанры на Litnet
        self.genres = [
            "fantastika",      # Фантастика
            "fentezi",         # Фэнтези
            "detektiv",        # Детектив
            "priklyucheniya",  # Приключения
            "ljubovnye-romany",# Любовные романы
            "proza",           # Проза
        ]
    
    def start_driver(self):
        """Запускает Chrome WebDriver."""
        if self.driver:
            return True
        
        try:
            options = Options()
            
            if self.headless:
                options.add_argument('--headless=new')
            
            options.add_argument('--no-sandbox')
            options.add_argument('--disable-dev-shm-usage')
            options.add_argument('--disable-gpu')
            options.add_argument('--window-size=1920,1080')
            options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')
            options.add_argument('--lang=ru-RU,ru;q=0.9,en;q=0.8')
            
            options.add_argument('--disable-blink-features=AutomationControlled')
            options.add_experimental_option("excludeSwitches", ["enable-automation"])
            options.add_experimental_option('useAutomationExtension', False)
            
            safe_print("[🚀] Litnet: Запуск Chrome WebDriver...")
            
            if HAS_WDM:
                service = Service(ChromeDriverManager().install())
                self.driver = webdriver.Chrome(service=service, options=options)
            else:
                self.driver = webdriver.Chrome(options=options)
            
            self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
            
            safe_print("[✅] Litnet: WebDriver запущен")
            return True
            
        except Exception as e:
            safe_print(f"[❌] Litnet: Ошибка запуска WebDriver: {e}")
            return False
    
    def close_driver(self):
        """Закрывает WebDriver."""
        if self.driver:
            try:
                self.driver.quit()
                safe_print("[🛑] Litnet: WebDriver закрыт")
            except:
                pass
            self.driver = None
    
    def wait_for_element(self, selector: str, timeout: int = 10, by: str = "css"):
        """Ждёт появления элемента."""
        try:
            by_type = By.CSS_SELECTOR if by == "css" else By.XPATH
            element = WebDriverWait(self.driver, timeout).until(
                EC.presence_of_element_located((by_type, selector))
            )
            return element
        except TimeoutException:
            return None
    
    def search_litnet(self, genre: str = "fentezi", max_books: int = 10) -> List[Dict]:
        """
        Ищет книги на Litnet по жанру.
        :param genre: Жанр (fentezi, fantastika, detektiv...)
        :param max_books: Максимум результатов
        :return: Список книг
        """
        safe_print(f"[🔍] Litnet: жанр '{genre}'...")
        books = []
        
        if not self.start_driver():
            return []
        
        try:
            # Litnet использует русскую версию
            genre_url = f"{self.litnet_base}ru/book/{genre}/"
            
            self.driver.get(genre_url)
            time.sleep(5)  # Ждём загрузки JS
            
            # Пробуем разные селекторы для книг
            selectors = [
                'a[href*="/book/"]',
                '.book-item a',
                '.book a.title',
                '[data-book-id] a',
            ]
            
            book_links = []
            for selector in selectors:
                try:
                    links = self.driver.find_elements(By.CSS_SELECTOR, selector)
                    if links:
                        book_links.extend(links)
                        safe_print(f"[OK] Selecktor '{selector}': {len(links)}")
                except:
                    pass
            
            # Уникальные ссылки
            seen_urls = set()
            for link in book_links:
                if len(books) >= max_books:
                    break
                
                try:
                    href = link.get_attribute('href')
                    
                    if not href or '/book/' not in href or href in seen_urls:
                        continue
                    
                    seen_urls.add(href)
                    
                    title = link.text.strip()
                    if len(title) < 3 or len(title) > 200:
                        continue
                    
                    # Очищаем название
                    title = re.sub(r'\s+', ' ', title).strip()
                    
                    book = {
                        "id": f"litnet_{len(books)}_{int(time.time())}",
                        "title": title,
                        "author": "Неизвестно",
                        "url": href,
                        "source": "litnet",
                        "genre": genre,
                    }
                    books.append(book)
                    safe_print(f"  [📚] Kniga: {title[:50]}")
                    
                except Exception:
                    continue
            
            safe_print(f"[✅] Litnet: naideno {len(books)} knig")
            return books
            
        except Exception as e:
            safe_print(f"[❌] Litnet oshibka poiska: {e}")
            return []
    
    def download_litnet_text(self, book: Dict) -> Optional[str]:
        """
        Скачивает текст книги с Litnet (первую главу или описание).
        :param book: Информация о книге
        :return: Текст книги
        """
        url = book.get("url")
        if not url:
            return None
        
        if not self.start_driver():
            return None
        
        try:
            safe_print(f"[⬇️] Litnet: {book['title'][:40]}")
            
            self.driver.get(url)
            time.sleep(3)  # Ждём загрузки
            
            # Пробуем найти текст книги
            # Litnet часто скрывает текст за кнопкой "Читать"
            
            # 1. Ищем аннотацию/описание
            description = self.wait_for_element('.annot', timeout=5)
            
            if description:
                text = description.text.strip()
                if len(text) > 300:
                    safe_print(f"[✅] Litnet (описание): {len(text)} символов")
                    return text
            
            # 2. Ищем кнопку "Читать" и открываем книгу
            read_button = self.driver.find_element(By.CSS_SELECTOR, 'a.btn_read') if self.driver.find_elements(By.CSS_SELECTOR, 'a.btn_read') else None
            
            if read_button:
                try:
                    read_url = read_button.get_attribute('href')
                    self.driver.get(read_url)
                    time.sleep(3)
                    
                    # Ищем текст главы
                    text_div = self.wait_for_element('.text-content', timeout=5)
                    
                    if text_div:
                        text = text_div.text.strip()
                        text = re.sub(r'\n{3,}', '\n\n', text)
                        
                        if len(text) > 500:
                            safe_print(f"[✅] Litnet (глава): {len(text)} символов")
                            return text
                except Exception as e:
                    safe_print(f"[⚠️] Litnet: не удалось открыть главу: {e}")
            
            # 3. Если не нашли текст, пробуем description из meta
            meta_desc = self.wait_for_element('meta[name="description"]', timeout=3)
            
            if meta_desc:
                desc_text = meta_desc.get_attribute('content')
                if desc_text and len(desc_text) > 300:
                    desc_text = re.sub(r'\s+', ' ', desc_text).strip()
                    safe_print(f"[✅] Litnet (meta): {len(desc_text)} символов")
                    return desc_text
            
            safe_print(f"[⚠️] Litnet: текст не найден")
            return None
                
        except Exception as e:
            safe_print(f"[❌] Litnet ошибка скачивания: {e}")
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
            safe_print(f"[ℹ️] Litnet: Уже обработано: {book.get('title')}")
            return []
        
        safe_print(f"[📖] Litnet: Обработка: {book.get('title')[:40]}")
        
        text = self.download_litnet_text(book)
        
        if not text:
            return []
        
        pairs = self.learner.extract_chunks(text, book)
        
        if pairs:
            self.learner._mark_book_processed(book_id, {
                "title": book.get("title"),
                "author": book.get("author"),
                "pairs_count": len(pairs),
                "source": "litnet",
                "text_length": len(text),
            })
            safe_print(f"  [✅] Litnet: Создано {len(pairs)} пар")
        
        return pairs
    
    def learn_from_litnet(self, max_books: int = 10) -> List[Dict]:
        """
        Основной метод обучения из Litnet.
        :param max_books: Максимум книг
        :return: Список обучающих пар
        """
        safe_print("[🚀] Litnet: Запуск обучения...")
        safe_print(f"[ℹ️] Макс книг: {max_books}")
        
        all_pairs = []
        books_processed = 0
        books_per_genre = max(3, max_books // len(self.genres))
        
        for genre in self.genres:
            if books_processed >= max_books:
                break
            
            safe_print(f"\n[📚] Litnet: Жанр '{genre}'")
            
            books = self.search_litnet(genre=genre, max_books=books_per_genre)
            
            for book in books:
                if books_processed >= max_books:
                    break
                
                pairs = self.process_book(book)
                if pairs:
                    all_pairs.extend(pairs)
                    books_processed += 1
                
                time.sleep(random.uniform(2, 3))
            
            time.sleep(random.uniform(3, 5))
        
        safe_print(f"\n[💾] Litnet: Собрано {len(all_pairs)} пар из {books_processed} книг")
        return all_pairs


def main():
    """Тестирование парсера Litnet."""
    safe_print("[RUN] Litnet Parser — Тестирование")
    print("=" * 60)
    
    parser = LitnetParser(headless=True)
    
    try:
        # Тест: поиск книг
        safe_print("\n[🧪] Тест: Поиск книг")
        books = parser.search_litnet(genre="fentezi", max_books=3)
        
        for book in books[:1]:
            text = parser.download_litnet_text(book)
            if text:
                safe_print(f"  ✅ Текст: {len(text)} символов")
                safe_print(f"  Начало: {text[:100]}...")
        
        safe_print("\n[🎉] Готово!")
        
    finally:
        parser.close_driver()


if __name__ == "__main__":
    main()
