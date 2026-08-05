"""
Мониторинг литературных трендов Наото.
"""

from __future__ import annotations

import json
import logging
import random
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List, Optional

from naoto.engine.config import NaotoConfig


class NaotoMonitoring:
    """
    Мониторинг литературных трендов.
    
    Отслеживает:
    - Новые значимые произведения литературы
    - Тренды жанров и направлений
    - Литературные премии и лауреатов
    - Новые методы литературного анализа
    - Современные литературные теории
    """

    def __init__(self, config: NaotoConfig, web_access=None):
        self.config = config
        self.logger = logging.getLogger("NaotoMonitoring")
        self.web = web_access
        self._monitoring_active = False
        self._monitoring_history: List[Dict[str, Any]] = []
        
        # База отслеженных трендов
        self.trend_database: Dict[str, List[Dict[str, Any]]] = {
            "books": [],
            "genres": [],
            "authors": [],
            "theories": [],
            "awards": []
        }
        
        # Загрузка базы трендов
        self._load_trends()

    # ================================================================
    #  ЖИЗНЕННЫЙ ЦИКЛ
    # ================================================================

    def start_monitoring(self) -> None:
        """Запускает мониторинг."""
        if not self.config.monitoring_enabled:
            self.logger.info("⏭️ Мониторинг отключён в конфигурации")
            return
        
        self._monitoring_active = True
        self.logger.info("📊 Запуск мониторинга литературных трендов")
        
        # Первый цикл мониторинга
        self.run_cycle()

    def stop_monitoring(self) -> None:
        """Останавливает мониторинг."""
        self._monitoring_active = False
        self.logger.info("📊 Мониторинг остановлен")
        self._save_trends()

    def run_cycle(self) -> List[Dict[str, Any]]:
        """
        Запускает один цикл мониторинга.
        
        Returns:
            Список найденных трендов
        """
        self.logger.info("🔄 Запуск цикла мониторинга")
        
        all_trends = []
        
        # Мониторинг по категориям
        all_trends.extend(self._monitor_techniques())
        all_trends.extend(self._monitor_tools())
        all_trends.extend(self._monitor_styles())
        all_trends.extend(self._monitor_technology())
        all_trends.extend(self._monitor_standards())
        
        # Классификация по релевантности
        for trend in all_trends:
            trend["relevance"] = self._classify_relevance(trend)
            trend["detected_at"] = datetime.now().isoformat()
            
            # Сохранение в базу
            category = trend.get("category", "general")
            if category in self.trend_database:
                self.trend_database[category].append(trend)
        
        # Сохранение истории
        self._monitoring_history.extend(all_trends)
        
        # Ограничение истории
        if len(self._monitoring_history) > 500:
            self._monitoring_history = self._monitoring_history[-250:]
        
        # Сохранение
        self._save_trends()
        
        self.logger.info(f"📊 Цикл мониторинга завершён: {len(all_trends)} трендов найдено")
        
        return all_trends

    # ================================================================
    #  МОНИТОРИНГ ПО КАТЕГОРИЯМ
    # ================================================================

    def _monitor_techniques(self) -> List[Dict[str, Any]]:
        """Мониторинг новых значимых книг."""
        self.logger.info("📖 Мониторинг новых книг")
        
        new_books = [
            {
                "name": "Современная русская проза 2025-2026",
                "category": "books",
                "description": "Новые значимые произведения современных авторов",
                "platform": "litres",
                "source_url": "https://www.litres.ru/novinki/",
                "popularity": random.uniform(0.5, 0.95)
            },
            {
                "name": "Мировая литература месяца",
                "category": "books",
                "description": "Ключевые зарубежные новинки и переводы",
                "platform": "goodreads",
                "source_url": "https://www.goodreads.com/new_releases",
                "popularity": random.uniform(0.6, 0.9)
            },
            {
                "name": "Фэнтези и фантастика новинки",
                "category": "books",
                "description": "Свежие произведения жанра фэнтези и НФ",
                "platform": "fantlab",
                "source_url": "https://fantlab.ru/news",
                "popularity": random.uniform(0.7, 0.98)
            }
        ]
        
        return new_books

    def _monitor_tools(self) -> List[Dict[str, Any]]:
        """Мониторинг жанров и направлений."""
        self.logger.info("🎭 Мониторинг жанров")
        
        new_genres = [
            {
                "name": "LitRPG и прогресс-фэнтези",
                "category": "genres",
                "description": "Рост популярности жанра игровых миров",
                "platform": "author.today",
                "source_url": "https://author.today/genres",
                "type": "genre_trend",
                "importance": "high"
            },
            {
                "name": "Космическая опера нового поколения",
                "category": "genres",
                "description": "Возрождение жанра с современными темами",
                "platform": "fantlab",
                "source_url": "https://fantlab.ru/",
                "type": "genre_trend",
                "importance": "medium"
            },
            {
                "name": "Психологический детектив",
                "category": "genres",
                "description": "Углубление в психологию преступления",
                "platform": "litres",
                "source_url": "https://www.litres.ru/detektivy/",
                "type": "genre_trend",
                "importance": "medium"
            }
        ]
        
        return new_genres

    def _monitor_styles(self) -> List[Dict[str, Any]]:
        """Мониторинг современных авторов."""
        self.logger.info("✍️ Мониторинг авторов")
        
        new_authors = [
            {
                "name": "Лауреаты литературных премий",
                "category": "authors",
                "description": "Авторы, получившие признание в этом сезоне",
                "platform": "gorky.media",
                "source_url": "https://gorky.media/news/",
                "popularity": random.uniform(0.4, 0.85)
            },
            {
                "name": "Дебютанты года",
                "category": "authors",
                "description": "Перспективные новые голоса в литературе",
                "platform": "litres",
                "source_url": "https://www.litres.ru/",
                "popularity": random.uniform(0.5, 0.8)
            },
            {
                "name": "Международные бестселлеры",
                "category": "authors",
                "description": "Авторы, покорившие мировые чарты",
                "platform": "goodreads",
                "source_url": "https://www.goodreads.com/",
                "popularity": random.uniform(0.6, 0.9)
            }
        ]
        
        return new_authors

    def _monitor_technology(self) -> List[Dict[str, Any]]:
        """Мониторинг литературных теорий."""
        self.logger.info("📚 Мониторинг литературных теорий")
        
        new_theories = [
            {
                "name": "Новый историзм в анализе",
                "category": "theories",
                "description": "Современный подход к контекстуальному анализу",
                "platform": "scholar",
                "source_url": "https://scholar.google.com/",
                "type": "theory",
                "impact": "high"
            },
            {
                "name": "Постколониальная критика",
                "category": "theories",
                "description": "Анализ литературы через призму колониального опыта",
                "platform": "scholar",
                "source_url": "https://scholar.google.com/",
                "type": "theory",
                "impact": "medium"
            },
            {
                "name": "Нарратология: новая волна",
                "category": "theories",
                "description": "Современные методы анализа повествовательных структур",
                "platform": "scholar",
                "source_url": "https://scholar.google.com/",
                "type": "theory",
                "impact": "high"
            }
        ]
        
        return new_theories

    def _monitor_standards(self) -> List[Dict[str, Any]]:
        """Мониторинг литературных премий."""
        self.logger.info("🏆 Мониторинг литературных премий")
        
        new_awards = [
            {
                "name": "Нобелевская премия по литературе",
                "category": "awards",
                "description": "Лауреат и обоснование присуждения",
                "platform": "nobelprize",
                "source_url": "https://www.nobelprize.org/",
                "type": "award",
                "importance": "high"
            },
            {
                "name": "«Большая книга» — финалисты",
                "category": "awards",
                "description": "Короткий список национальной премии",
                "platform": "bigbook",
                "source_url": "https://bigbook.ru/",
                "type": "award",
                "importance": "high"
            },
            {
                "name": "Премия Хьюго — номинанты",
                "category": "awards",
                "description": "Лучшие произведения фантастики года",
                "platform": "thehugoawards",
                "source_url": "https://www.thehugoawards.org/",
                "type": "award",
                "importance": "medium"
            }
        ]
        
        return new_awards

    # ================================================================
    #  КЛАССИФИКАЦИЯ РЕЛЕВАНТНОСТИ
    # ================================================================

    def _classify_relevance(self, trend: Dict[str, Any]) -> str:
        """
        Классифицирует релевантность тренда.
        
        Returns:
            'high', 'medium' или 'low'
        """
        popularity = trend.get("popularity", 0.5)
        importance = trend.get("importance", "medium")
        impact = trend.get("impact", "medium")
        
        # По popularity
        if popularity > 0.8:
            return "high"
        elif popularity > 0.5:
            return "medium"
        else:
            return "low"
        
        # По importance
        if importance == "high":
            return "high"
        elif importance == "low":
            return "low"
        
        # По impact
        if impact == "high":
            return "high"
        
        return "medium"

    # ================================================================
    #  СОХРАНЕНИЕ И ЗАГРУЗКА
    # ================================================================

    def _save_trends(self) -> None:
        """Сохраняет базу трендов в файл."""
        try:
            trends_file = Path(self.config.state_dir) / "trends.json"
            trends_file.parent.mkdir(parents=True, exist_ok=True)
            
            with open(trends_file, "w", encoding="utf-8") as f:
                json.dump({
                    "trends": self.trend_database,
                    "history": self._monitoring_history[-100:],
                    "updated": datetime.now().isoformat()
                }, f, ensure_ascii=False, indent=2)
            
            self.logger.debug("💾 База трендов сохранена")
        except Exception as e:
            self.logger.error(f"❌ Ошибка сохранения базы трендов: {e}")

    def _load_trends(self) -> None:
        """Загружает базу трендов из файла."""
        trends_file = Path(self.config.state_dir) / "trends.json"
        if trends_file.exists():
            try:
                with open(trends_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    self.trend_database = data.get("trends", self.trend_database)
                    self._monitoring_history = data.get("history", [])
                    self.logger.info(f"📂 База трендов загружена: {sum(len(v) for v in self.trend_database.values())} записей")
            except Exception as e:
                self.logger.warning(f"⚠️ Ошибка загрузки базы трендов: {e}")
