"""
API для обучения Наото из книг.

Наото:
1. Собирает книги из интернета (Author.Today, Gutenberg, Open Library)
2. Создаёт обучающие пары (user/bot) из текста книг
3. Обучает свою чат-модель на этих данных
4. Сохраняет прогресс
"""

import asyncio
import json
import logging
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

# Добавляем корень проекта в путь
sys.path.insert(0, str(Path(__file__).parent.parent))

logger = logging.getLogger("NaotoLearningAPI")


class NaotoLearningEngine:
    """
    Движок обучения Наото из книг.
    
    Запускает:
    1. Сбор книг через BookLearner
    2. Создание training_pairs
    3. Обучение модели через retrain.py
    4. Сохранение прогресса
    """
    
    def __init__(self, project_root: Path = Path(__file__).parent.parent):
        self.project_root = project_root
        self.data_dir = project_root / "naoto" / "data"
        self.books_dir = self.data_dir / "books"
        self.training_pairs_file = self.data_dir / "training_pairs.jsonl"
        self.progress_file = self.data_dir / "learning_progress.json"
        self.is_learning = False
        self.learning_status: Dict[str, Any] = {
            "status": "idle",  # idle, collecting, creating_pairs, training, completed, error
            "progress": 0.0,
            "books_collected": 0,
            "pairs_created": 0,
            "current_book": "",
            "started_at": None,
            "completed_at": None,
            "error": None,
        }
        
        # Создаём директории
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.books_dir.mkdir(parents=True, exist_ok=True)
        
        # Загружаем прогресс
        self._load_progress()
    
    def _load_progress(self):
        """Загружает прогресс обучения."""
        if self.progress_file.exists():
            try:
                with open(self.progress_file, "r", encoding="utf-8") as f:
                    self.learning_status.update(json.load(f))
            except Exception as e:
                logger.error(f"Ошибка загрузки прогресса: {e}")
    
    def _save_progress(self):
        """Сохраняет прогресс обучения."""
        self.learning_status["last_updated"] = datetime.now().isoformat()
        with open(self.progress_file, "w", encoding="utf-8") as f:
            json.dump(self.learning_status, f, ensure_ascii=False, indent=2)
    
    async def start_learning(self, topics: Optional[List[str]] = None, max_books: int = 10) -> Dict[str, Any]:
        """
        Запускает процесс обучения Наото из книг.
        
        :param topics: Темы для поиска книг (если None, используются дефолтные)
        :param max_books: Максимум книг для обработки
        :return: Статус процесса
        """
        if self.is_learning:
            return {
                "status": "error",
                "message": "Уже идёт обучение",
                "progress": self.learning_status,
            }
        
        self.is_learning = True
        self.learning_status = {
            "status": "collecting",
            "progress": 0.0,
            "books_collected": 0,
            "pairs_created": 0,
            "current_book": "",
            "started_at": datetime.now().isoformat(),
            "completed_at": None,
            "error": None,
        }
        self._save_progress()
        
        logger.info("🚀 Наото: Начинаю обучение из книг...")
        
        try:
            # Шаг 1: Сбор книг
            books = await self._collect_books(topics, max_books)
            self.learning_status["books_collected"] = len(books)
            self._save_progress()
            
            if not books:
                raise Exception("Не удалось собрать книги")
            
            # Шаг 2: Создание обучающих пар
            pairs = await self._create_training_pairs(books)
            self.learning_status["pairs_created"] = len(pairs)
            self._save_progress()
            
            if not pairs:
                raise Exception("Не удалось создать обучающие пары")
            
            # Шаг 3: Обучение модели
            await self._train_model()
            
            # Завершение
            self.learning_status["status"] = "completed"
            self.learning_status["progress"] = 1.0
            self.learning_status["completed_at"] = datetime.now().isoformat()
            self._save_progress()
            
            logger.info("✅ Наото: Обучение завершено успешно!")
            
            return {
                "status": "success",
                "message": f"Обучение завершено! Собрано {len(books)} книг, создано {len(pairs)} пар.",
                "progress": self.learning_status,
            }
            
        except Exception as e:
            logger.error(f"❌ Ошибка обучения: {e}")
            self.learning_status["status"] = "error"
            self.learning_status["error"] = str(e)
            self._save_progress()
            
            return {
                "status": "error",
                "message": f"Ошибка: {e}",
                "progress": self.learning_status,
            }
        finally:
            self.is_learning = False
    
    async def _collect_books(self, topics: Optional[List[str]], max_books: int) -> List[Dict]:
        """Собирает книги из интернета."""
        logger.info("📚 Шаг 1: Сбор книг...")
        
        try:
            from utils.book_learner import BookLearner
            
            learner = BookLearner(data_dir=str(self.books_dir))
            
            # Дефолтные темы если не указаны
            if topics is None:
                topics = [
                    "psychology communication",
                    "philosophy life",
                    "fantasy worlds",
                    "science fiction",
                ]
            
            books = []
            
            # Пробуем Author.Today (русскоязычные)
            try:
                from utils.author_today_parser import AuthorTodayParser
                logger.info("  📚 Ищу на Author.Today...")
                at_parser = AuthorTodayParser(data_dir=str(self.books_dir))
                # Используем первые 3 жанра
                for genre_name, genre_url in at_parser.genres[:3]:
                    if len(books) >= max_books:
                        break
                    at_books = at_parser.search_by_genre(genre_url, genre_name, max_results=3)
                    books.extend(at_books)
                    logger.info(f"  📚 {genre_name}: {len(at_books)} книг")
                logger.info(f"  ✅ Author.Today: {len(books)} книг всего")
            except Exception as e:
                logger.warning(f"  ⚠️ Author.Today ошибка: {e}")
                import traceback
                logger.warning(traceback.format_exc())
            
            # Пробуем Open Library (более надёжный)
            if len(books) < max_books:
                logger.info("  📚 Ищу в Open Library...")
                try:
                    openlib_books = learner.search_open_library(topics[0] if topics else "psychology", max_results=5)
                    books.extend(openlib_books)
                    logger.info(f"  ✅ Open Library: {len(openlib_books)} книг")
                except Exception as e:
                    logger.warning(f"  ⚠️ Open Library ошибка: {e}")
            
            # Уникализируем по ID
            seen_ids = set()
            unique_books = []
            for book in books:
                book_id = book.get("id", "")
                if book_id and book_id not in seen_ids:
                    seen_ids.add(book_id)
                    unique_books.append(book)
            
            books = unique_books[:max_books]
            logger.info(f"  📚 Всего собрано {len(books)} книг")
            
            return books
            
        except Exception as e:
            logger.error(f"  ❌ Ошибка сбора книг: {e}")
            import traceback
            logger.error(traceback.format_exc())
            return []
    
    def _download_author_today_text(self, reader_url: str) -> Optional[str]:
        """
        Скачивает текст книги с Author.Today.
        :param reader_url: URL читалки
        :return: Текст книги или None
        """
        try:
            import urllib.request
            from utils.book_learner import LitnetHTMLParser
            
            logger.info(f"    📥 Скачиваю с {reader_url}")
            
            req = urllib.request.Request(reader_url)
            req.add_header('User-Agent', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36')
            req.add_header('Accept', 'text/html,application/xhtml+xml')
            req.add_header('Accept-Language', 'ru-RU,ru;q=0.9')
            
            with urllib.request.urlopen(req, timeout=30) as response:
                html = response.read().decode('utf-8', errors='ignore')
            
            # Парсим текст из HTML
            parser = LitnetHTMLParser()
            parser.feed(html)
            text = parser.get_text()
            
            # Очищаем текст
            if text and len(text) > 1000:
                logger.info(f"    ✅ Скачано {len(text)} символов")
                return text
            else:
                logger.info(f"    ⚠️ Текст слишком короткий: {len(text) if text else 0} символов")
                return None
                
        except Exception as e:
            logger.warning(f"    ❌ Ошибка скачивания: {e}")
            return None
    
    async def _create_training_pairs(self, books: List[Dict]) -> List[Dict]:
        """Создаёт обучающие пары из книг."""
        logger.info("📝 Шаг 2: Создание обучающих пар...")
        
        try:
            from utils.book_learner import BookLearner
            
            learner = BookLearner(data_dir=str(self.books_dir))
            all_pairs = []
            
            for i, book in enumerate(books):
                self.learning_status["current_book"] = book.get("title", "Без названия")
                self.learning_status["progress"] = (i + 1) / len(books) * 0.5  # 0-50%
                self._save_progress()
                
                logger.info(f"  📖 Обрабатываю: {book.get('title')}")
                
                # Скачиваем текст
                text = None
                source = book.get("source", "")
                
                # Для Author.Today скачиваем текст через learner
                logger.info(f"    📥 Скачиваю текст...")
                logger.info(f"    📋 Книга: {book.get('title', 'N/A')}")
                try:
                    # Пробуем скачать текст книги
                    if "author_today" in source.lower() or "author.today" in source.lower():
                        # Для Author.Today скачиваем через reader_url
                        reader_url = book.get("reader_url", "")
                        if reader_url:
                            logger.info(f"    📥 Reader URL: {reader_url}")
                            text = self._download_author_today_text(reader_url)
                            if text:
                                logger.info(f"    ✅ Скачано {len(text)} символов")
                            else:
                                logger.info(f"    ⚠️ Не удалось скачать текст")
                                continue
                        else:
                            logger.info(f"    ⚠️ Нет reader_url")
                            continue
                    else:
                        if "gutenberg" in source.lower():
                            text = learner.download_gutenberg_text(book)
                        elif "openlibrary" in source.lower() or "open_library" in source.lower():
                            text = learner.download_open_library_text(book)
                except Exception as e:
                    logger.warning(f"    ⚠️ Ошибка скачивания: {e}")
                    import traceback
                    logger.warning(traceback.format_exc())
                
                if not text or len(text) < 500:
                    logger.info(f"    ⚠️ Текст слишком короткий или не скачан ({len(text) if text else 0} символов)")
                    continue
                
                # Создаём обучающие пары
                book_metadata = {
                    "title": book.get("title", "Без названия"),
                    "author": book.get("author", book.get("authors", "Неизвестно")),
                    "source": source,
                }
                
                logger.info(f"    📝 Создаю пары...")
                pairs = learner.extract_chunks(text, book_metadata)
                all_pairs.extend(pairs)
                
                logger.info(f"    ✅ Создано {len(pairs)} пар")
            
            # Сохраняем пары в файл
            if all_pairs:
                logger.info(f"  💾 Сохраняю {len(all_pairs)} пар...")
                with open(self.training_pairs_file, "a", encoding="utf-8") as f:
                    for pair in all_pairs:
                        f.write(json.dumps(pair, ensure_ascii=False) + "\n")
                
                logger.info(f"  💾 Сохранено {len(all_pairs)} пар в {self.training_pairs_file}")
            
            logger.info(f"  📚 Всего создано {len(all_pairs)} пар")
            return all_pairs
            
        except Exception as e:
            logger.error(f"  ❌ Ошибка создания пар: {e}")
            import traceback
            logger.error(traceback.format_exc())
            return []
    
    async def _train_model(self):
        """Запускает обучение модели через retrain.py."""
        logger.info("🧠 Шаг 3: Обучение модели...")
        
        self.learning_status["status"] = "training"
        self.learning_status["progress"] = 0.8
        self._save_progress()
        
        try:
            retrain_script = self.project_root / "retrain.py"
            
            if not retrain_script.exists():
                logger.warning(f"  ⚠️ Не найден скрипт обучения: {retrain_script}")
                logger.info("  ℹ️ Пропускаю обучение модели (нет retrain.py)")
                return
            
            logger.info(f"  🚀 Запуск обучения в фоне...")
            logger.info("  ⏳ Обучение может занять 10-30 минут")
            
            # Запускаем retrain.py в фоне (не ждём завершения)
            # Используем subprocess напрямую, так как не нужно ждать
            import subprocess
            subprocess.Popen(
                [sys.executable, str(retrain_script)],
                cwd=str(self.project_root),
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
            )
            
            logger.info("  ✅ Обучение запущено в фоне!")
            logger.info("  💡 Прогресс можно посмотреть в логах")
            
        except Exception as e:
            logger.error(f"  ❌ Ошибка запуска обучения: {e}")
    
    def get_status(self) -> Dict[str, Any]:
        """Возвращает текущий статус обучения."""
        return {
            "status": self.learning_status,
            "is_learning": self.is_learning,
            "progress_file": str(self.progress_file),
            "training_pairs_file": str(self.training_pairs_file),
        }
    
    def reset_progress(self):
        """Сбрасывает прогресс обучения."""
        self.learning_status = {
            "status": "idle",
            "progress": 0.0,
            "books_collected": 0,
            "pairs_created": 0,
            "current_book": "",
            "started_at": None,
            "completed_at": None,
            "error": None,
        }
        self._save_progress()
        logger.info("🔄 Прогресс обучения сброшен")


# Глобальный экземпляр
naoto_learning_engine: Optional[NaotoLearningEngine] = None


def get_naoto_learning_engine(project_root: Optional[Path] = None) -> NaotoLearningEngine:
    """Получение глобального движка обучения."""
    global naoto_learning_engine
    if naoto_learning_engine is None:
        if project_root is None:
            project_root = Path(__file__).parent.parent
        naoto_learning_engine = NaotoLearningEngine(project_root=project_root)
    return naoto_learning_engine
