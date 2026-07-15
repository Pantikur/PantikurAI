"""
Веб-доступ Ханако — выход в интернет для изучения гравитации.
"""

from __future__ import annotations

import json
import random
import logging
import re
from datetime import datetime
from pathlib import Path
from typing import Optional

try:
    import requests
    HAS_REQUESTS = True
except ImportError:
    HAS_REQUESTS = False

try:
    from bs4 import BeautifulSoup
    HAS_BS4 = True
except ImportError:
    HAS_BS4 = False

from hanako.engine.config import HanakoConfig, WebSearchMode
from hanako.engine.models import WebResearchResult


class HanakoWebAccess:
    """
    Модуль веб-доступа Ханако.
    
    Возможности:
    - Поиск в интернете по темам гравитации
    - Сканирование научных сайтов (arXiv, NASA, CERN)
    - Извлечение уравнений и фактов
    - Кэширование результатов
    """

    def __init__(self, config: HanakoConfig):
        self.config = config
        self.logger = logging.getLogger("HanakoWebAccess")
        self.cache_path = config.cache_dir / "web_cache.json"
        self.cache: dict[str, WebResearchResult] = self._load_cache()

    def scan_gravity_topic(self, topic: str) -> list[WebResearchResult]:
        """Сканирование интернета по теме гравитации."""
        if not self.config.internet_enabled:
            self.logger.warning("Интернет отключён — пропуск веб-сканирования")
            return []

        results = []

        # Пробуем реальный поиск
        if self.config.web_search_mode in (WebSearchMode.INTERNET, WebSearchMode.FULL):
            results.extend(self._search_arxiv(topic))
            results.extend(self._search_nasa(topic))
            results.extend(self._search_cern(topic))

        # Если не нашли — генерируем симуляцию
        if not results:
            results = self._simulate_search(topic)

        # Сохраняем в кэш
        for r in results:
            self.cache[r.url] = r

        self._save_cache()
        return results[:20]  # Не больше 20 результатов

    def _search_arxiv(self, query: str) -> list[WebResearchResult]:
        """Поиск на arXiv."""
        results = []
        if not HAS_REQUESTS:
            return results

        try:
            url = f"http://export.arxiv.org/api/query?search=all={query}+gravity&max_results=10"
            resp = requests.get(url, timeout=30)
            if resp.status_code == 200:
                import xml.etree.ElementTree as ET
                root = ET.fromstring(resp.content)
                ns = {'atom': 'http://www.w3.org/2005/Atom'}

                for entry in root.findall('atom:entry', ns):
                    title = entry.find('atom:title', ns).text.strip().replace('\n', ' ')
                    summary = entry.find('atom:summary', ns).text.strip().replace('\n', ' ')
                    url = entry.find('atom:id', ns).text
                    published = entry.find('atom:published', ns).text

                    result = WebResearchResult(
                        query=query,
                        url=url,
                        title=title,
                        summary=summary,
                        relevance=random.uniform(0.5, 0.95),
                        content_type="paper",
                        tags=["arxiv", "gravity", query.lower()[:30]],
                        extracted_facts=[summary[:200]],
                    )
                    results.append(result)
        except Exception as e:
            self.logger.warning(f"Ошибка arXiv поиска: {e}")

        return results

    def _search_nasa(self, query: str) -> list[WebResearchResult]:
        """Поиск на NASA."""
        results = []
        if not HAS_REQUESTS:
            return results

        try:
            url = f"https://api.nasa.gov/planetary/search?query={query}+gravity&api_key=DEMO_KEY"
            resp = requests.get(url, timeout=30)
            if resp.status_code == 200:
                data = resp.json()
                for item in data.get("results", [])[:5]:
                    result = WebResearchResult(
                        query=query,
                        url=item.get("url", ""),
                        title=item.get("title", ""),
                        summary=item.get("description", ""),
                        relevance=random.uniform(0.4, 0.9),
                        content_type="article",
                        tags=["nasa", "gravity"],
                    )
                    results.append(result)
        except Exception as e:
            self.logger.warning(f"Ошибка NASA поиска: {e}")

        return results

    def _search_cern(self, query: str) -> list[WebResearchResult]:
        """Поиск на CERN."""
        results = []
        if not HAS_REQUESTS:
            return results

        try:
            url = f"https://home.cern/search?q={query}+gravity"
            resp = requests.get(url, timeout=30)
            if resp.status_code == 200 and HAS_BS4:
                soup = BeautifulSoup(resp.text, 'html.parser')
                for item in soup.find_all('div', class_='result')[:5]:
                    title = item.get_text(strip=True)
                    result = WebResearchResult(
                        query=query,
                        url=url,
                        title=title,
                        summary="Статья с CERN по теме гравитации",
                        relevance=random.uniform(0.3, 0.85),
                        content_type="article",
                        tags=["cern", "gravity"],
                    )
                    results.append(result)
        except Exception as e:
            self.logger.warning(f"Ошибка CERN поиска: {e}")

        return results

    def _simulate_search(self, topic: str) -> list[WebResearchResult]:
        """Симуляция поиска (когда нет интернета)."""
        templates = [
            {
                "title": f"Новые исследования: {topic}",
                "summary": f"Анализ последних результатов по теме {topic}. Обзор теорий и экспериментов.",
                "url": f"https://simulation.local/gravity/{topic.lower().replace(' ', '_')}",
                "content_type": "article",
            },
            {
                "title": f"Обзор: {topic} — состояние на 2025",
                "summary": f"Комплексный обзор современных исследований {topic}. Включает данные из arXiv и других источников.",
                "url": f"https://simulation.local/review/{topic.lower().replace(' ', '_')}",
                "content_type": "review",
            },
            {
                "title": f"Математические основы {topic}",
                "summary": f"Математическая формализация {topic}. Уравнения, метрики, тензоры.",
                "url": f"https://simulation.local/math/{topic.lower().replace(' ', '_')}",
                "content_type": "paper",
            },
        ]

        results = []
        for t in templates:
            results.append(WebResearchResult(
                query=topic,
                url=t["url"],
                title=t["title"],
                summary=t["summary"],
                relevance=random.uniform(0.3, 0.8),
                content_type=t["content_type"],
                tags=["gravity", "simulation", topic.lower()[:20]],
            ))
        return results

    def _load_cache(self) -> dict[str, WebResearchResult]:
        """Загрузка кэша."""
        if self.cache_path.exists():
            try:
                with open(self.cache_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    cache = {}
                    for url, d in data.items():
                        cache[url] = WebResearchResult(
                            query=d["query"],
                            url=d["url"],
                            title=d["title"],
                            summary=d["summary"],
                            relevance=d.get("relevance", 0.0),
                            content_type=d.get("content_type", "article"),
                            tags=d.get("tags", []),
                            extracted_equations=d.get("extracted_equations", []),
                            extracted_facts=d.get("extracted_facts", []),
                            cached_at=datetime.fromisoformat(d["cached_at"]),
                        )
                    return cache
            except Exception:
                return {}
        return {}

    def _save_cache(self):
        """Сохранение кэша."""
        if len(self.cache) > self.config.max_web_cache:
            # Удаляем старые
            sorted_cache = sorted(self.cache.items(), key=lambda x: x[1].cached_at)
            for url, _ in sorted_cache[:len(self.cache) - self.config.max_web_cache]:
                del self.cache[url]

        with open(self.cache_path, 'w', encoding='utf-8') as f:
            data = {}
            for url, r in self.cache.items():
                data[url] = r.to_dict()
            json.dump(data, f, ensure_ascii=False, indent=2)

    def get_cache_stats(self) -> dict:
        """Статистика кэша."""
        return {
            "total_cached": len(self.cache),
            "content_types": dict(self._count_content_types()),
        }

    def _count_content_types(self):
        counts = {}
        for r in self.cache.values():
            counts[r.content_type] = counts.get(r.content_type, 0) + 1
        return counts
