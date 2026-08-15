# utils/selenium_parser.py — Парсеры с Selenium для JavaScript сайтов

import os
import shutil
import subprocess
import time
import re
import random
from pathlib import Path
from typing import Dict, List, Optional

# Selenium
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, WebDriverException

# webdriver-manager для автозагрузки ChromeDriver
try:
    from webdriver_manager.chrome import ChromeDriverManager
    HAS_WDM = True
except ImportError:
    HAS_WDM = False

import sys
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from utils.book_learner import safe_print, BookLearner


def _find_chrome_binary() -> Optional[str]:
    """
    Ищет исполняемый файл Chrome/Chromium.
    Приоритет: переменные окружения (CHROME_BIN / CHROME_BINARY_PATH), затем PATH.
    """
    # 1) Переменные окружения (задаются в Dockerfile/контейнере)
    for env in ('CHROME_BIN', 'CHROME_BINARY_PATH', 'CHROMIUM_BIN'):
        path = os.environ.get(env, '').strip()
        if path:
            found = shutil.which(path)
            if found:
                return found
            if Path(path).exists():
                return path

    # 2) Поиск в PATH
    candidates = ['google-chrome', 'google-chrome-stable', 'chromium', 'chromium-browser']
    for name in candidates:
        found = shutil.which(name)
        if found:
            return found

    return None


def _install_chrome_linux() -> bool:
    """
    Устанавливает Google Chrome на Linux.
    Сначала пробует .deb Google напрямую (стабильная версия).
    """
    try:
        deb_path = '/tmp/google-chrome-stable_current_amd64.deb'
        
        # Скачиваем .deb пакет Google Chrome напрямую
        dl = subprocess.run(
            ['wget', '-q', '-O', deb_path,
             'https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb'],
            capture_output=True,
        )
        if dl.returncode == 0:
            # Устанавливаем через dpkg (требует зависимости)
            install = subprocess.run(
                ['apt-get', 'install', '-y', deb_path],
                capture_output=True,
            )
            if install.returncode == 0 and _find_chrome_binary():
                return True
            
            # Если dpkg не справился с зависимостями — пробуем apt
            subprocess.run(['apt-get', 'update'], capture_output=True)
            install2 = subprocess.run(
                ['apt-get', 'install', '-y', deb_path],
                capture_output=True,
            )
            if install2.returncode == 0 and _find_chrome_binary():
                return True

        return False
    except Exception as e:
        safe_print(f"[❌] Ошибка установки Chrome: {e}")
        return False


def _ensure_chrome_installed() -> bool:
    """
    Проверяет наличие Chrome/Chromium и устанавливает его, если отсутствует.
    Работает на Linux (apt) под root.
    """
    found = _find_chrome_binary()
    if found:
        safe_print(f"✅ Chrome найден: {found}")
        return True

    # Установка возможна только на Linux под root
    if os.name != "posix" or not hasattr(os, 'geteuid') or os.geteuid() != 0:
        safe_print("[⚠️] Chrome не найден. Установите Chrome или укажите CHROME_BIN.")
        safe_print("[ℹ️] Автор.Today работает без Chrome (парсится без JavaScript).")
        return False

    safe_print("[⚙️] Chrome не найден. Попытка установки...")
    try:
        subprocess.run(['apt-get', 'update'], check=True, capture_output=True)
    except Exception as e:
        safe_print(f"[❌] Не удалось обновить репозитории: {e}")
        return False

    if _install_chrome_linux():
        safe_print("[✅] Chrome установлен успешно!")
        return True

    safe_print("[❌] Не удалось установить Chrome")
    safe_print("[ℹ️] Автор.Today работает без Chrome (парсится без JavaScript).")
    return False


class SeleniumBookParser:
    """Парсер с Selenium для сайтов с JavaScript."""
    
    def __init__(self, data_dir: str = "data/books", headless: bool = True):
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.learner = BookLearner(data_dir=str(data_dir))
        
        self.headless = headless
        self.driver = None
        
        # === СТИХИ.РУ ===
        self.stihi_base = "https://stihi.ru/"
        
        # === ПРОЗА.РУ ===
        self.proza_base = "https://proza.ru/"
        
        # === RULIT ===
        self.rulit_base = "https://rulit.me/"
        self.rulit_genres = ["fantasy", "sf", "detektiv", "priklyucheniya", "proza"]
        
        # === LIVELIB ===
        self.livelib_base = "https://www.livelib.ru/"
        self.livelib_genres = ["fantasy", "sf", "proza", "detektiv"]
    
    def start_driver(self):
        """Запускает Chrome WebDriver."""
        if self.driver:
            return True
        
        # === ПРОВЕРЯЕМ И УСТАНАВЛИВАЕМ CHROME ===
        if not _ensure_chrome_installed():
            safe_print("[❌] Chrome недоступен. Парсинг JavaScript-сайтов отключён.")
            safe_print("[ℹ️] Автор.Today будет работать без проблем.")
            return False
        
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
            
            # Отключаем лишнее для скорости
            options.add_argument('--disable-blink-features=AutomationControlled')
            options.add_experimental_option("excludeSwitches", ["enable-automation"])
            options.add_experimental_option('useAutomationExtension', False)
            
            safe_print("[🚀] Запуск Chrome WebDriver...")
            
            if HAS_WDM:
                try:
                    # Пробуем автозагрузку драйвера
                    service = Service(ChromeDriverManager().install())
                    self.driver = webdriver.Chrome(service=service, options=options)
                except Exception as wdm_err:
                    safe_print(f"⚠️ WDM ошибка: {wdm_err}")
                    safe_print("ℹ️ Пробуем системный ChromeDriver...")
                    try:
                        self.driver = webdriver.Chrome(options=options)
                    except Exception as sys_err:
                        safe_print(f"❌ Системный драйвер тоже не сработал: {sys_err}")
                        # Финальный fallback: запускаем Chrome без драйвера (иногда работает в старых версиях)
                        safe_print("⚠️ Финальный fallback — запуск без ChromeDriver...")
                        try:
                            self.driver = webdriver.Chrome(options=options)
                            self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
                        except Exception:
                            safe_print("❌ WebDriver полностью недоступен. Парсинг отключён.")
                            return False
            else:
                self.driver = webdriver.Chrome(options=options)
            
            # Скрываем признаки автоматизации
            self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")

            # Таймаут загрузки страниц — чтобы не висеть 120 сек на зависших сайтах
            self.driver.set_page_load_timeout(30)

            safe_print("[✅] WebDriver запущен")
            return True
            
        except Exception as e:
            safe_print(f"[❌] Ошибка запуска WebDriver: {e}")
            safe_print("[ℹ️] Установите: pip install selenium webdriver-manager")
            return False
    
    def close_driver(self):
        """Закрывает WebDriver."""
        if self.driver:
            try:
                self.driver.quit()
                safe_print("[🛑] WebDriver закрыт")
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
    
    # ==================== СТИХИ.РУ ====================
    
    def search_stihi(self, max_books: int = 10) -> List[Dict]:
        """Ищет произведения на Стихи.ру."""
        safe_print("[🔍] Стихи.ру: поиск произведений...")
        works = []
        
        if not self.start_driver():
            return []
        
        try:
            # Главная страница со свежими произведениями
            self.driver.get(self.stihi_base)
            time.sleep(3)  # Ждём загрузки JS
            
            # Ищем ссылки на произведения (формат /YYYY/MM/DD/ID)
            links = self.driver.find_elements(By.CSS_SELECTOR, 'a[href^="/20"]')
            
            for link in links[:max_books * 2]:  # Берём с запасом
                if len(works) >= max_books:
                    break
                
                try:
                    href = link.get_attribute('href')
                    title = link.get_attribute('title') or link.text.strip()
                    
                    if not href or '/20' not in href:
                        continue
                    
                    if len(title) < 3 or len(title) > 200:
                        continue
                    
                    # Проверяем что это произведение, не автор
                    if '/avtor/' in href:
                        continue
                    
                    work = {
                        "id": f"stihi_{len(works)}_{int(time.time())}",
                        "title": title,
                        "author": "Неизвестно",
                        "url": href,
                        "source": "stihi_ru",
                        "type": "poetry",
                    }
                    works.append(work)
                    safe_print(f"  [📚] Найдено: {title[:50]}")
                    
                except Exception:
                    continue
            
            safe_print(f"[✅] Стихи.ру: найдено {len(works)} произведений")
            return works
            
        except Exception as e:
            safe_print(f"[❌] Стихи.ру ошибка: {e}")
            return []
    
    def download_stihi_text(self, work: Dict) -> Optional[str]:
        """Скачивает текст произведения со Стихи.ру."""
        url = work.get("url")
        if not url:
            return None
        
        if not self.start_driver():
            return None
        
        try:
            safe_print(f"[⬇️] Стихи.ру: {work['title'][:40]}")
            
            self.driver.get(url)
            time.sleep(2)  # Ждём загрузки
            
            # Ищем текст произведения
            text_div = self.wait_for_element('.text', timeout=5)
            
            if not text_div:
                text_div = self.wait_for_element('#text_container', timeout=3)
            
            if text_div:
                text = text_div.text.strip()
                
                # Очищаем от лишних пробелов
                text = re.sub(r'\n{3,}', '\n\n', text)
                
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
        """Ищет произведения на Проза.ру."""
        safe_print("[🔍] Проза.ру: поиск произведений...")
        works = []
        
        if not self.start_driver():
            return []
        
        try:
            self.driver.get(self.proza_base)
            time.sleep(3)
            
            # Ищем ссылки на произведения
            links = self.driver.find_elements(By.CSS_SELECTOR, 'a[href^="/20"]')
            
            for link in links[:max_books * 2]:
                if len(works) >= max_books:
                    break
                
                try:
                    href = link.get_attribute('href')
                    title = link.get_attribute('title') or link.text.strip()
                    
                    if not href or '/20' not in href:
                        continue
                    
                    if len(title) < 3 or len(title) > 200:
                        continue
                    
                    if '/avtor/' in href:
                        continue
                    
                    work = {
                        "id": f"proza_{len(works)}_{int(time.time())}",
                        "title": title,
                        "author": "Неизвестно",
                        "url": href,
                        "source": "proza_ru",
                        "type": "prose",
                    }
                    works.append(work)
                    safe_print(f"  [📚] Найдено: {title[:50]}")
                    
                except Exception:
                    continue
            
            safe_print(f"[✅] Проза.ру: найдено {len(works)} произведений")
            return works
            
        except Exception as e:
            safe_print(f"[❌] Проза.ру ошибка: {e}")
            return []
    
    def download_proza_text(self, work: Dict) -> Optional[str]:
        """Скачивает текст произведения с Проза.ру."""
        url = work.get("url")
        if not url:
            return None
        
        if not self.start_driver():
            return None
        
        try:
            safe_print(f"[⬇️] Проза.ру: {work['title'][:40]}")
            
            self.driver.get(url)
            time.sleep(2)
            
            text_div = self.wait_for_element('.text', timeout=5)
            
            if text_div:
                text = text_div.text.strip()
                text = re.sub(r'\n{3,}', '\n\n', text)
                
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
        """Ищет книги на RuLit."""
        safe_print(f"[🔍] RuLit: жанр '{genre}'...")
        books = []
        
        if not self.start_driver():
            return []
        
        try:
            genre_url = f"{self.rulit_base}genre/{genre}/"
            self.driver.get(genre_url)
            time.sleep(3)
            
            # Ждём загрузки списка книг
            self.wait_for_element('.book', timeout=10, by='css')
            
            # Ищем ссылки на книги
            book_links = self.driver.find_elements(By.CSS_SELECTOR, 'a[href^="/books/"]')
            
            for link in book_links[:max_books]:
                try:
                    href = link.get_attribute('href')
                    title = link.text.strip()
                    
                    if not href or 'page' in href or 'tag' in href:
                        continue
                    
                    if len(title) < 3:
                        continue
                    
                    book = {
                        "id": f"rulit_{len(books)}_{int(time.time())}",
                        "title": title,
                        "author": "Неизвестно",
                        "url": href,
                        "source": "rulit",
                        "genre": genre,
                    }
                    books.append(book)
                    safe_print(f"  [📚] Найдена книга: {title[:50]}")
                    
                except Exception:
                    continue
            
            safe_print(f"[✅] RuLit: найдено {len(books)} книг")
            return books
            
        except Exception as e:
            safe_print(f"[❌] RuLit ошибка: {e}")
            return []
    
    def download_rulit_text(self, book: Dict) -> Optional[str]:
        """Скачивает текст/описание книги с RuLit."""
        url = book.get("url")
        if not url:
            return None
        
        if not self.start_driver():
            return None
        
        try:
            safe_print(f"[⬇️] RuLit: {book['title'][:40]}")
            
            self.driver.get(url)
            time.sleep(2)
            
            # Ищем описание
            description = self.wait_for_element('meta[name="description"]', timeout=5)
            
            if description:
                desc_text = description.get_attribute('content')
                if desc_text and len(desc_text) > 300:
                    desc_text = re.sub(r'\s+', ' ', desc_text).strip()
                    safe_print(f"[✅] RuLit (описание): {len(desc_text)} символов")
                    return desc_text
            
            # Ищем текст первой главы
            text_div = self.wait_for_element('.book-text', timeout=5)
            
            if text_div:
                text = text_div.text.strip()
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
        """Ищет книги на LiveLib."""
        safe_print(f"[🔍] LiveLib: жанр '{genre}'...")
        books = []
        
        if not self.start_driver():
            return []
        
        try:
            genre_url = f"{self.livelib_base}genre/{genre}"
            self.driver.get(genre_url)
            time.sleep(3)
            
            # Ждём загрузки
            self.wait_for_element('.book-card', timeout=10, by='css')
            
            # Ищем ссылки на книги
            book_links = self.driver.find_elements(By.CSS_SELECTOR('a[href^="/book/"]'))
            
            for link in book_links[:max_books]:
                try:
                    href = link.get_attribute('href')
                    title = link.get_attribute('title') or link.text.strip()
                    
                    if not href:
                        continue
                    
                    if len(title) < 3:
                        continue
                    
                    book = {
                        "id": f"livelib_{len(books)}_{int(time.time())}",
                        "title": title,
                        "author": "Неизвестно",
                        "url": href,
                        "source": "livelib",
                        "genre": genre,
                    }
                    books.append(book)
                    safe_print(f"  [📚] Найдена книга: {title[:50]}")
                    
                except Exception:
                    continue
            
            safe_print(f"[✅] LiveLib: найдено {len(books)} книг")
            return books
            
        except Exception as e:
            safe_print(f"[❌] LiveLib ошибка: {e}")
            return []
    
    def download_livelib_text(self, book: Dict) -> Optional[str]:
        """Скачивает описание/аннотацию книги с LiveLib."""
        url = book.get("url")
        if not url:
            return None
        
        if not self.start_driver():
            return None
        
        try:
            safe_print(f"[⬇️] LiveLib: {book['title'][:40]}")
            
            self.driver.get(url)
            time.sleep(2)
            
            # Ищем описание
            description = self.wait_for_element('meta[name="description"]', timeout=5)
            
            if description:
                desc_text = description.get_attribute('content')
                if desc_text and len(desc_text) > 300:
                    desc_text = re.sub(r'\s+', ' ', desc_text).strip()
                    safe_print(f"[✅] LiveLib (описание): {len(desc_text)} символов")
                    return desc_text
            
            # Ищем аннотацию
            annotation = self.wait_for_element('.annotation', timeout=5)
            
            if annotation:
                text = annotation.text.strip()
                if len(text) > 300:
                    safe_print(f"[✅] LiveLib (аннотация): {len(text)} символов")
                    return text
            
            safe_print(f"[⚠️] LiveLib: текст не найден")
            return None
                
        except Exception as e:
            safe_print(f"[❌] LiveLib ошибка: {e}")
            return None
    
    # ==================== ОБЩИЕ МЕТОДЫ ====================
    
    def process_work(self, work: Dict) -> List[Dict]:
        """Обрабатывает произведение: скачивает и создаёт пары."""
        work_id = work.get("id")
        source = work.get("source", "unknown")
        
        if not work_id:
            return []
        
        if self.learner._is_book_processed(work_id):
            safe_print(f"[ℹ️] Уже обработано: {work.get('title')}")
            return []
        
        safe_print(f"[📖] Обработка: {work.get('title')[:40]} ({source})")
        
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
        
        pairs = self.learner.extract_chunks(text, work)
        
        if pairs:
            self.learner._mark_book_processed(work_id, {
                "title": work.get("title"),
                "author": work.get("author"),
                "pairs_count": len(pairs),
                "source": source,
                "text_length": len(text),
            })
            safe_print(f"  [✅] Создано {len(pairs)} пар")
        
        return pairs
    
    def learn_from_all_sources(self, max_books: int = 20) -> List[Dict]:
        """
        Основной метод обучения из всех JavaScript источников.
        :param max_books: Максимум книг/произведений
        :return: Список обучающих пар
        """
        safe_print("[🚀] Запуск обучения из JavaScript источников...")
        safe_print(f"[ℹ️] Макс книг: {max_books}")
        
        all_pairs = []
        books_processed = 0
        books_per_source = max(5, max_books // 4)
        
        # 1. Стихи.ру
        safe_print("\n[📚] Источник 1: СТИХИ.РУ (поэзия)")
        stihi_works = self.search_stihi(max_books=books_per_source)
        for work in stihi_works:
            if books_processed >= max_books:
                break
            pairs = self.process_work(work)
            if pairs:
                all_pairs.extend(pairs)
                books_processed += 1
            time.sleep(random.uniform(2, 3))
        
        # 2. Проза.ру
        safe_print("\n[📚] Источник 2: ПРОЗА.РУ (проза)")
        proza_works = self.search_proza(max_books=books_per_source)
        for work in proza_works:
            if books_processed >= max_books:
                break
            pairs = self.process_work(work)
            if pairs:
                all_pairs.extend(pairs)
                books_processed += 1
            time.sleep(random.uniform(2, 3))
        
        # 3. RuLit
        safe_print("\n[📚] Источник 3: RULIT (книги)")
        for genre in ["fantasy", "sf", "detektiv"]:
            if books_processed >= max_books:
                break
            rulit_books = self.search_rulit(genre=genre, max_books=books_per_source // 2)
            for book in rulit_books:
                if books_processed >= max_books:
                    break
                pairs = self.process_work(book)
                if pairs:
                    all_pairs.extend(pairs)
                    books_processed += 1
                time.sleep(random.uniform(2, 3))
        
        # 4. LiveLib
        safe_print("\n[📚] Источник 4: LIVELIB (описания)")
        for genre in ["fantasy", "sf", "proza"]:
            if books_processed >= max_books:
                break
            livelib_books = self.search_livelib(genre=genre, max_books=books_per_source // 2)
            for book in livelib_books:
                if books_processed >= max_books:
                    break
                pairs = self.process_work(book)
                if pairs:
                    all_pairs.extend(pairs)
                    books_processed += 1
                time.sleep(random.uniform(2, 3))
        
        safe_print(f"\n[💾] Собрано {len(all_pairs)} пар из {books_processed} произведений")
        return all_pairs


def main():
    """Тестирование парсеров."""
    safe_print("[RUN] Selenium Parser — Тестирование")
    print("=" * 60)
    
    parser = SeleniumBookParser(headless=True)
    
    try:
        # Тест: Стихи.ру
        safe_print("\n[🧪] Тест: Стихи.ру")
        works = parser.search_stihi(max_books=3)
        
        for work in works[:1]:
            text = parser.download_stihi_text(work)
            if text:
                safe_print(f"  ✅ Текст: {len(text)} символов")
                safe_print(f"  Начало: {text[:100]}...")
        
        safe_print("\n[🎉] Готово!")
        
    finally:
        parser.close_driver()


if __name__ == "__main__":
    main()
