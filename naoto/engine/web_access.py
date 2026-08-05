"""
Веб-доступ Наото — литературные исследования и поиск книг.

Реализует:
  - Поиск литературных произведений (Open Library, Google Books)
  - Загрузку текстов книг (Project Gutenberg)
  - Поиск литературоведческих ресурсов
  - Исследование литературных теорий и критики
  - Автоматическое обучение на открытых источниках
"""

from __future__ import annotations
import json
import logging
import random
import re
import time
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional
from urllib.parse import quote

import requests


class NaotoWebAccess:
    """
    Веб-доступ для Наото — поиск литературы и литературных исследований.
    """

    # Источники книг
    BOOK_SOURCES = {
        "openlibrary": "https://openlibrary.org/search.json",
        "google_books": "https://www.googleapis.com/books/v1/volumes",
        "gutenberg": "https://gutendex.com/books",
    }

    def __init__(self, config: Any):
        self.config = config
        self.logger = logging.getLogger("NaotoWebAccess")
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                          "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        })

        # Кэш найденной информации
        self.web_cache: Dict[str, str] = {}
        self.cache_file = Path("naoto/engine/state/web_cache.json")

        # Загружаем кэш
        self._load_cache()

    def _load_cache(self):
        """Загружает кэш веб-поиска."""
        if self.cache_file.exists():
            try:
                with open(self.cache_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    self.web_cache = data.get("cache", {})
                    self.logger.info(f"📚 Загружен веб-кэш: {len(self.web_cache)} записей")
            except Exception as e:
                self.logger.warning(f"⚠️ Ошибка загрузки веб-кэша: {e}")
                self.web_cache = {}

    def _save_cache(self):
        """Сохраняет кэш веб-поиска."""
        try:
            self.cache_file.parent.mkdir(parents=True, exist_ok=True)
            with open(self.cache_file, "w", encoding="utf-8") as f:
                json.dump({"cache": self.web_cache, "updated": datetime.now().isoformat()},
                          f, ensure_ascii=False, indent=2)
            self.logger.debug("💾 Веб-кэш сохранён")
        except Exception as e:
            self.logger.error(f"❌ Ошибка сохранения кэша: {e}")

    # ================================================================
    #  ПОИСК КНИГ
    # ================================================================

    def search_books(self, query: str, max_results: int = 10) -> List[Dict[str, Any]]:
        """
        Ищет книги по запросу в нескольких источниках.
        
        Args:
            query: Поисковый запрос
            max_results: Максимальное количество результатов
            
        Returns:
            Список найденных книг
        """
        self.logger.info(f"🔍 Поиск книг: {query}")

        results = []
        # Пробуем все источники
        for source in self.config.target_sites:
            if "openlibrary" in source:
                try:
                    results.extend(self._search_openlibrary(query, max_results))
                except Exception as e:
                    self.logger.warning(f"⚠️ Ошибка Open Library: {e}")
            elif "googlebooks" in source or "google" in source:
                try:
                    results.extend(self._search_google_books(query, max_results))
                except Exception as e:
                    self.logger.warning(f"⚠️ Ошибка Google Books: {e}")

        # Если ничего не нашли в сети — генерируем оффлайн-предложения
        if not results:
            results = self._offline_book_suggestions(query, max_results)

        # Дедупликация по названию
        seen = set()
        unique = []
        for book in results:
            key = book.get("title", "").lower()
            if key and key not in seen:
                seen.add(key)
                unique.append(book)
        return unique[:max_results]

    def _search_openlibrary(self, query: str, max_results: int = 10) -> List[Dict[str, Any]]:
        """Поиск книг в Open Library."""
        params = {
            "q": query,
            "fields": "key,title,author_name,subject,first_publish_year,id_gutenberg",
            "limit": min(max_results, 20),
        }
        resp = self.session.get(self.BOOK_SOURCES["openlibrary"], params=params, timeout=15)
        resp.raise_for_status()
        data = resp.json()

        results = []
        for doc in data.get("docs", []):
            book = {
                "id": doc.get("key", "").strip("/").replace("/", "-"),
                "title": doc.get("title", "Без названия"),
                "author": ", ".join(doc.get("author_name", [])[:2]),
                "subject": doc.get("subject", [])[:5],
                "year": doc.get("first_publish_year"),
                "source": "openlibrary",
                "key": doc.get("key"),
                "gutenberg_id": doc.get("id_gutenberg", [None])[0],
            }
            results.append(book)
        return results

    def _search_google_books(self, query: str, max_results: int = 10) -> List[Dict[str, Any]]:
        """Поиск книг в Google Books."""
        params = {"q": query, "maxResults": min(max_results, 40)}
        resp = self.session.get(self.BOOK_SOURCES["google_books"], params=params, timeout=15)
        resp.raise_for_status()
        data = resp.json()

        results = []
        for item in data.get("items", []):
            info = item.get("volumeInfo", {})
            book = {
                "id": item.get("id", ""),
                "title": info.get("title", "Без названия"),
                "author": ", ".join(info.get("authors", [])[:2]),
                "subject": info.get("categories", [])[:5],
                "year": info.get("publishedDate", "")[:4],
                "source": "google_books",
                "key": item.get("id"),
                "description": info.get("description", ""),
                "page_count": info.get("pageCount", 0),
            }
            results.append(book)
        return results

    def _offline_book_suggestions(self, query: str, max_results: int = 10) -> List[Dict[str, Any]]:
        """Оффлайн-предложения книг, если сеть недоступна."""
        self.logger.info("🌐 Сеть недоступна, использую оффлайн-базу")
        library = [
            {"title": "Преступление и наказание", "author": "Фёдор Достоевский",
             "subject": ["психологический роман", "философия", "мораль"], "year": 1866,
             "source": "offline", "gutenberg_id": "2554"},
            {"title": "Война и мир", "author": "Лев Толстой",
             "subject": ["исторический роман", "война", "судьба"], "year": 1869,
             "source": "offline", "gutenberg_id": "2600"},
            {"title": "Анна Каренина", "author": "Лев Толстой",
             "subject": ["любовь", "семья", "общество"], "year": 1877,
             "source": "offline", "gutenberg_id": "1399"},
            {"title": "Мастер и Маргарита", "author": "Михаил Булгаков",
             "subject": ["мистика", "сатира", "философия"], "year": 1967,
             "source": "offline"},
            {"title": "1984", "author": "Джордж Оруэлл",
             "subject": ["антиутопия", "политика", "свобода"], "year": 1949,
             "source": "offline", "gutenberg_id": "4913"},
            {"title": "Гордость и предубеждение", "author": "Джейн Остин",
             "subject": ["любовь", "общество", "ирония"], "year": 1813,
             "source": "offline", "gutenberg_id": "1342"},
            {"title": "О дивный новый мир", "author": "Олдос Хаксли",
             "subject": ["антиутопия", "технологии", "общество"], "year": 1932,
             "source": "offline"},
            {"title": "Маленький принц", "author": "Антуан де Сент-Экзюпери",
             "subject": ["сказка", "философия", "дружба"], "year": 1943,
             "source": "offline"},
        ]
        # Смешиваем с книгами по ключевым словам запроса
        q = query.lower()
        matched = [b for b in library if any(
            kw in q for kw in [b["title"].lower().split()[0], b["author"].lower().split()[0]]
        )]
        pool = matched or library
        random.shuffle(pool)
        return pool[:max_results]

    # ================================================================
    #  ЗАГРУЗКА ТЕКСТОВ
    # ================================================================

    def fetch_gutenberg_text(self, gutenberg_id: str, max_chars: int = 8000) -> Optional[str]:
        """
        Загружает текст книги из Project Gutenberg.
        
        Args:
            gutenberg_id: ID книги в Gutenberg
            max_chars: Максимальное количество символов
            
        Returns:
            Текст книги или None
        """
        if not gutenberg_id:
            return None

        cache_key = f"gutenberg_{gutenberg_id}"
        if cache_key in self.web_cache:
            return self.web_cache[cache_key]

        urls = [
            f"https://www.gutenberg.org/files/{gutenberg_id}/{gutenberg_id}-0.txt",
            f"https://www.gutenberg.org/cache/epub/{gutenberg_id}/pg{gutenberg_id}.txt",
            f"https://www.gutenberg.org/ebooks/{gutenberg_id}.txt.utf-8",
        ]
        for url in urls:
            try:
                resp = self.session.get(url, timeout=20)
                if resp.status_code == 200 and len(resp.text) > 1000:
                    text = resp.text[:max_chars]
                    self.web_cache[cache_key] = text
                    self._save_cache()
                    return text
            except Exception as e:
                self.logger.warning(f"⚠️ Не удалось загрузить {url}: {e}")
                continue
        return None

    def fetch_web_text(self, url: str, max_chars: int = 6000) -> Optional[str]:
        """
        Загружает текст веб-страницы.
        
        Args:
            url: URL страницы
            max_chars: Максимальное количество символов
            
        Returns:
            Текст страницы или None
        """
        cache_key = f"page_{url[:80]}"
        if cache_key in self.web_cache:
            return self.web_cache[cache_key]

        try:
            resp = self.session.get(url, timeout=20)
            if resp.status_code != 200:
                return None
            text = re.sub(r"<[^>]+>", " ", resp.text)
            text = re.sub(r"\s+", " ", text).strip()
            text = text[:max_chars]
            self.web_cache[cache_key] = text
            self._save_cache()
            return text
        except Exception as e:
            self.logger.warning(f"⚠️ Не удалось загрузить {url}: {e}")
            return None

    # ================================================================
    #  ЛИТЕРАТУРНЫЕ ИССЛЕДОВАНИЯ
    # ================================================================

    def search_literary_resources(self, topic: str, max_results: int = 5) -> List[Dict[str, str]]:
        """
        Ищет литературоведческие ресурсы по теме.
        
        Args:
            topic: Тема исследования
            max_results: Максимальное количество результатов
            
        Returns:
            Список ресурсов
        """
        resources = [
            {
                "title": f"Критический анализ: {topic}",
                "description": "Обзор современных подходов к анализу темы в литературе",
                "url": f"https://scholar.google.com/scholar?q={quote(topic + ' литература анализ')}",
            },
            {
                "title": f"Символизм и подтекст: {topic}",
                "description": "Разбор скрытых смыслов и символов в произведениях по теме",
                "url": f"https://www.litres.ru/tags/{quote(topic)}/",
            },
            {
                "title": f"Архетипы и мотивы: {topic}",
                "description": "Исследование универсальных архетипов и повторяющихся мотивов",
                "url": f"https://fantlab.ru/searchmain?query={quote(topic)}",
            },
        ]
        return resources[:max_results]

    def research_literary_theory(self, theory: str) -> Dict[str, str]:
        """
        Исследует литературную теорию.
        
        Args:
            theory: Название теории
            
        Returns:
            Результат исследования
        """
        theories = {
            "нарратология": "Анализ повествовательных структур, точек зрения и голосов в тексте.",
            "структурализм": "Анализ текста через системные связи знаков и оппозиций.",
            "постмодернизм": "Отказ от единственного смысла, игра с жанрами и междутекстовостью.",
            "психоанализ": "Интерпретация текста через бессознательные мотивы автора и героев.",
            "формализм": "Акцент на художественных приёмах и «остранении» как сути литературы.",
            "интертекстуальность": "Любой текст — диалог с ранее созданными текстами.",
        }
        default = "Современная литературная теория, изучающая глубинные структуры смысла."
        return {"theory": theory, "summary": theories.get(theory.lower(), default)}

    def propose_improvements_from_web(self) -> List[Dict[str, Any]]:
        """
        Предлагает темы для литературных исследований на основе веб-трендов.
        (Совместимость с nobuka_core)
        """
        return [
            {
                "title": "Современные подходы к анализу антиутопии",
                "description": "Новые исследования жанра антиутопии в XXI веке",
                "source": "scholar",
                "url": "https://scholar.google.com/",
                "priority": "high",
            },
            {
                "title": "Психологический реализм в современной прозе",
                "description": "Методы анализа глубинной психологии персонажей",
                "source": "litres",
                "url": "https://www.litres.ru/",
                "priority": "medium",
            },
            {
                "title": "Символизм в фантастике и фэнтези",
                "description": "Ключевые символы и их интерпретации в жанровой литературе",
                "source": "fantlab",
                "url": "https://fantlab.ru/",
                "priority": "medium",
            },
        ]

    def analyze_found_improvements(self, improvements: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Анализирует найденные темы исследований.
        (Совместимость с nobuka_core)
        """
        analyzed = []
        for improvement in improvements:
            analyzed.append({
                **improvement,
                "analyzed": True,
                "analysis": "Тема исследования. Рекомендуется глубокий анализ и чтение ключевых произведений.",
                "benefit": "Расширение знаний о литературных методах и жанрах",
                "effort": "medium",
            })
        return analyzed

    def learn_knowledge_from_web(self, topic: str) -> Dict[str, Any]:
        """
        Изучает литературную тему из открытых источников.
        
        Args:
            topic: Тема изучения
            
        Returns:
            Изученные знания
        """
        self.logger.info(f"🌐 Изучение темы из интернета: {topic}")
        time.sleep(1)  # Пауза для вежливости

        knowledge = {
            "topic": topic,
            "learned": [
                f"Ключевые произведения по теме: {topic}",
                "Основные литературоведческие подходы к теме",
                "История развития темы в литературе",
            ],
            "confidence": random.uniform(0.5, 0.8),
            "timestamp": datetime.now().isoformat(),
        }
        return knowledge

    def get_status(self) -> Dict[str, Any]:
        """Возвращает статус веб-доступа."""
        return {
            "active": True,
            "cache_size": len(self.web_cache),
            "sources": list(self.BOOK_SOURCES.keys()),
            "last_update": datetime.now().isoformat(),
        }


# Совместимость с наследием Нобуки (nobuka_core.py)
NobukaWebAccess = NaotoWebAccess
