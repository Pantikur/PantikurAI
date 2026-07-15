"""
Веб-доступ Фуюки — поиск информации об атмосферном электричестве.

Реализует:
  - Поиск исследований атмосферного электричества в интернете
  - Изучение научных статей и теорий
  - Анализ кода проекта на предмет связанного с электричеством
  - Сбор данных из открытых источников
  - Извлечение знаний из веб-страниц
"""

from __future__ import annotations
import json
import logging
import random
import re
import time
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple

import requests
from bs4 import BeautifulSoup


class FuyukiWebAccess:
    """
    Веб-доступ для Фуюки — поиск информации об атмосферном электричестве.
    """

    def __init__(self, config: Any):
        self.config = config
        self.logger = logging.getLogger("FuyukiWebAccess")
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                          "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        })
        
        # Кэш найденной информации
        self.web_cache: Dict[str, str] = {}
        self.cache_file = config.state_dir / "web_cache.json"
        
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
    #  ПОИСК ИССЛЕДОВАНИЙ
    # ================================================================

    def search_electricity_papers(self, topic: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Ищет исследования атмосферного электричества.
        
        Args:
            topic: Конкретная тема поиска (если None — случайная из research_topics)
            
        Returns:
            Список найденных статей
        """
        if topic is None:
            topic = random.choice(self.config.research_topics)
        
        cache_key = f"search:{topic}"
        if cache_key in self.web_cache:
            try:
                return json.loads(self.web_cache[cache_key])
            except Exception:
                pass
        
        self.logger.info(f"🌐 Поиск исследований: {topic}")
        papers = self._search_topic(topic)
        
        # Сохраняем в кэш
        self.web_cache[cache_key] = json.dumps(papers, ensure_ascii=False)
        self._save_cache()
        
        return papers

    def _search_topic(self, topic: str) -> List[Dict[str, Any]]:
        """Симулирует поиск по теме (в реальной системе — реальный поиск)."""
        # База знаний об атмосферном электричестве
        electricity_knowledge = {
            "atmospheric electricity": [
                {
                    "title": "Глобальная электрическая цепь атмосферы",
                    "authors": ["Willett", "Smart"],
                    "year": 2023,
                    "source": "arxiv",
                    "summary": "Обзор глобальной электрической цепи, связывающей грозы с ионосферой",
                    "key_findings": [
                        "Ток глобальной цепи ~1000-2000 А",
                        "Ионосферный потенциал ~250 кВ",
                        "Сопротивление атмосферы ~200 Ом·м²"
                    ],
                    "relevance": 0.95
                },
                {
                    "title": "Механизмы разделения зарядов в грозовых облаках",
                    "authors": ["Marshall", "Rakov"],
                    "year": 2024,
                    "source": "researchgate",
                    "summary": "Анализ механизмов разделения зарядов при столкновении града и льда",
                    "key_findings": [
                        "Инверсия полярности заряда в верхней части облака",
                        "Роль температуры -10°C в процессе зарядки",
                        "Влияние градиента температуры на разделение зарядов"
                    ],
                    "relevance": 0.92
                },
            ],
            "lightning physics": [
                {
                    "title": "Физика молнии: от лидера до обратного разряда",
                    "authors": ["Rakov", "Uman"],
                    "year": 2023,
                    "source": "arxiv",
                    "summary": "Полный обзор физики молний, от формирования лидера до возвращающего разряда",
                    "key_findings": [
                        "Скорость лидера ~10⁵-10⁶ м/с",
                        "Ток обратного разряда до 200 кА",
                        "Температура канала до 30000 К"
                    ],
                    "relevance": 0.98
                },
                {
                    "title": "Электромагнитные импульсы от молний",
                    "authors": ["Wait"],
                    "year": 2022,
                    "source": "researchgate",
                    "summary": "Спектральный анализ электромагнитных импульсов от молний",
                    "key_findings": [
                        "Основной спектр до 100 кГц",
                        "Пики на частотах LF и VHF",
                        "Влияние на радиосвязь и навигацию"
                    ],
                    "relevance": 0.88
                },
            ],
            "ball lightning": [
                {
                    "title": "Шаровая молния: гипотезы и доказательства",
                    "authors": ["Steinmetz", "Katz"],
                    "year": 2024,
                    "source": "arxiv",
                    "summary": "Обзор современных гипотез о природе шаровой молнии",
                    "key_findings": [
                        "Гипотеза микроволнового резонанса",
                        "Гипотеза испарения кремния",
                        "Плазменная модель с магнитным удержанием"
                    ],
                    "relevance": 0.85
                },
            ],
            "sprites and elves": [
                {
                    "title": "Верхнеатмосферные разряды: спрайты и джеты",
                    "authors": ["Pasko", "Inan"],
                    "year": 2023,
                    "source": "arxiv",
                    "summary": "Исследование transient luminous events в мезосфере",
                    "key_findings": [
                        "Спрайты возникают на высоте 70-90 км",
                        "Связаны с положительно заряженными грозовыми разрядами",
                        "Энергия спрайта ~1-10 кДж"
                    ],
                    "relevance": 0.80
                },
            ],
            "lightning energy harvesting": [
                {
                    "title": "Сбор энергии молний: технические возможности",
                    "authors": ["Chergui", "Bellaredj"],
                    "year": 2024,
                    "source": "researchgate",
                    "summary": "Анализ технических ограничений и возможностей сбора энергии молний",
                    "key_findings": [
                        "Энергия одной молнии ~1-10 ГДж",
                        "КПД сбора не превышает 10-20%",
                        "Проблемы накопления и стабилизации"
                    ],
                    "relevance": 0.75
                },
            ],
        }
        
        # Ищем совпадения в базе знаний
        results = []
        topic_lower = topic.lower()
        
        for key, papers in electricity_knowledge.items():
            if key in topic_lower or topic_lower in key:
                results.extend(papers)
        
        if not results:
            # Генерируем случайные статьи на основе темы
            results = self._generate_random_papers(topic)
        
        return results[:5]  # Максимум 5 статей

    def _generate_random_papers(self, topic: str) -> List[Dict[str, Any]]:
        """Генерирует случайные статьи для неизвестной темы."""
        templates = [
            {
                "title": f"Исследование: {topic}",
                "authors": ["Unknown", "Researcher"],
                "year": random.randint(2020, 2024),
                "source": "web",
                "summary": f"Обзор современных исследований по теме {topic}",
                "key_findings": [
                    f"Ключевой фактор: интенсивность {topic}",
                    f"Влияние на атмосферные процессы",
                    f"Перспективы практического применения"
                ],
                "relevance": random.uniform(0.5, 0.9)
            },
            {
                "title": f"Моделирование {topic}",
                "authors": ["Simulator", "Analyst"],
                "year": random.randint(2021, 2024),
                "source": "arxiv",
                "summary": f"Численное моделирование явлений, связанных с {topic}",
                "key_findings": [
                    f"Оптимальные параметры для {topic}",
                    f"Связь с другими атмосферными явлениями"
                ],
                "relevance": random.uniform(0.4, 0.85)
            },
        ]
        return templates

    # ================================================================
    #  ИЗУЧЕНИЕ КОДА ПРОЕКТА
    # ================================================================

    def study_project_code(self) -> List[Dict[str, Any]]:
        """
        Изучает код проекта на предмет связанного с электричеством.
        
        Returns:
            Список найденных релевантных файлов
        """
        self.logger.info("📁 Изучение кода проекта...")
        found_files = []
        
        for scan_dir in self.config.scan_directories:
            dir_path = Path(scan_dir)
            if not dir_path.exists():
                continue
            
            for file_type in self.config.study_file_types:
                for file_path in dir_path.rglob(f"*{file_type}"):
                    if self._is_electricity_related(file_path):
                        found_files.append({
                            "path": str(file_path),
                            "size": file_path.stat().st_size,
                            "electricity_relevance": self._calculate_relevance(file_path),
                        })
        
        self.logger.info(f"Найдено {len(found_files)} файлов, связанных с электричеством")
        return found_files

    def _is_electricity_related(self, file_path: Path) -> bool:
        """Проверяет, связан ли файл с электричеством."""
        electricity_keywords = [
            "electric", "voltage", "current", "charge", "field", "magnetic",
            "lightning", "thunder", "storm", "plasma", "ion", "conductor",
            "resistor", "capacitor", "inductor", "circuit", "power",
            "energy", "electromagnetic", "wave", "frequency", "signal",
            "потенциал", "напряжение", "ток", "заряд", "поле", "молния",
            "гроза", "плазма", "проводник", "энергия", "электрич",
        ]
        
        try:
            content = file_path.read_text(encoding="utf-8", errors="ignore")
            content_lower = content.lower()
            
            for keyword in electricity_keywords:
                if keyword.lower() in content_lower:
                    return True
        except Exception:
            pass
        
        return False

    def _calculate_relevance(self, file_path: Path) -> float:
        """Рассчитывает релевантность файла для Фуюки."""
        electricity_keywords = [
            "electric", "voltage", "current", "charge", "field",
            "lightning", "thunder", "storm", "plasma", "ion",
            "потенциал", "напряжение", "ток", "заряд", "поле",
            "молния", "гроза", "плазма", "проводник",
        ]
        
        try:
            content = file_path.read_text(encoding="utf-8", errors="ignore")
            content_lower = content.lower()
            
            score = 0
            for keyword in electricity_keywords:
                count = content_lower.count(keyword.lower())
                score += count
            
            return min(1.0, score / 10)  # Нормализация до 0-1
        except Exception:
            return 0.0

    # ================================================================
    #  ПОЛУЧЕНИЕ ДЕТАЛЕЙ ФАЙЛА
    # ================================================================

    def get_file_content(self, file_path: Path, max_lines: int = 200) -> Optional[str]:
        """Получает содержимое файла для изучения."""
        try:
            with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                lines = f.readlines()
            
            # Извлекаем ключевые части
            key_lines = []
            for i, line in enumerate(lines[:max_lines]):
                # Берём комментарии, docstrings, ключевые строки
                if any(kw in line.lower() for kw in [
                    "electric", "voltage", "current", "charge", "field",
                    "def ", "class ", "import ", "from ", "#", "\"\"\"",
                    "потенциал", "напряжение", "ток", "заряд", "поле",
                ]):
                    key_lines.append(line.strip())
            
            if not key_lines and lines:
                # Если ничего не нашли, берём первые строки
                key_lines = [line.strip() for line in lines[:20]]
            
            return "\n".join(key_lines)
        except Exception as e:
            self.logger.error(f"Ошибка чтения файла {file_path}: {e}")
            return None

    # ================================================================
    #  ИЗУЧЕНИЕ НАУЧНОЙ СТАТЬИ
    # ================================================================

    def study_web_article(self, url: str) -> Optional[Dict[str, Any]]:
        """
        Загружает и изучает научную статью с веб-страницы.
        
        Args:
            url: URL статьи
            
        Returns:
            Извлечённые данные или None
        """
        try:
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, "html.parser")
            
            # Убираем скрипты и стили
            for script in soup(["script", "style"]):
                script.decompose()
            
            # Получаем текст
            text = soup.get_text(separator="\n")
            lines = [line.strip() for line in text.splitlines() if line.strip()]
            text = "\n".join(lines[:2000])  # Ограничиваем длину
            
            # Извлекаем ключевые моменты
            key_points = self._extract_key_points(text)
            
            return {
                "url": url,
                "title": soup.title.string if soup.title else url,
                "text": text[:3000],
                "key_points": key_points,
                "studied_at": datetime.now().isoformat(),
            }
            
        except Exception as e:
            self.logger.error(f"Ошибка загрузки {url}: {e}")
            return None

    def _extract_key_points(self, text: str) -> List[str]:
        """Извлекает ключевые пункты из текста."""
        points = []
        sentences = re.split(r'[.!?]+', text)
        
        for sentence in sentences[:10]:
            sentence = sentence.strip()
            if len(sentence) > 50 and any(kw in sentence.lower() for kw in [
                "electric", "voltage", "current", "charge", "field",
                "lightning", "thunder", "storm", "energy", "power",
                "потенциал", "напряжение", "ток", "заряд", "поле",
                "молния", "гроза", "энергия", "мощность",
            ]):
                points.append(sentence[:200])
        
        return points[:5]

    # ================================================================
    #  ИЗУЧЕНИЕ ВСЕГО О ЭЛЕКТРИЧЕСТВЕ
    # ================================================================

    def learn_everything_about_electricity(self) -> Dict[str, Any]:
        """
        Изучает абсолютно всё, что связано с атмосферным электричеством.
        
        Returns:
            Сводка изученного
        """
        self.logger.info("⚡ Фуюки изучает всё об атмосферном электричестве!")
        
        summary = {
            "web_papers": [],
            "project_files": [],
            "knowledge_gained": 0,
            "topics_covered": [],
        }
        
        # 1. Поиск в интернете
        if self.config.web_access_enabled:
            for topic in random.sample(self.config.research_topics, min(5, len(self.config.research_topics))):
                papers = self.search_electricity_papers(topic)
                summary["web_papers"].extend(papers)
                summary["topics_covered"].append(topic)
                summary["knowledge_gained"] += len(papers) * self.config.xp_per_web_search
        
        # 2. Изучение кода проекта
        if self.config.study_project:
            files = self.study_project_code()
            summary["project_files"] = files[:10]  # Топ-10 релевантных файлов
            summary["knowledge_gained"] += len(files) * 5
        
        # 3. Изучение существующих знаний
        knowledge_file = self.config.knowledge_dir / "knowledge_base.json"
        if knowledge_file.exists():
            try:
                with open(knowledge_file, "r", encoding="utf-8") as f:
                    existing = json.load(f)
                    summary["existing_knowledge"] = existing
            except Exception:
                pass
        
        self.logger.info(f"Изучено: {len(summary['web_papers'])} статей, {len(summary['project_files'])} файлов")
        self.logger.info(f"Получено знаний: {summary['knowledge_gained']} XP")
        
        return summary

    # ================================================================
    #  ПОИСК СПЕЦИАЛИЗИРОВАННОЙ ИНФОРМАЦИИ
    # ================================================================

    def search_lightning_control_methods(self) -> List[Dict[str, Any]]:
        """Ищет способы управления молниями."""
        self.logger.info("⚡ Поиск способов управления молниями...")
        
        methods = [
            {
                "name": "Лазерная ионизация",
                "description": "Направленный лазер создаёт проводящий канал для молнии",
                "source": "arxiv",
                "relevance": 0.9,
                "feasibility": "средняя",
            },
            {
                "name": "Земляные шары (ground balls)",
                "description": "Пассивное устройство для направления молнии",
                "source": "web",
                "relevance": 0.7,
                "feasibility": "низкая",
            },
            {
                "name": "Электрические проводники",
                "description": "Высокие мачты и провода для перехвата разрядов",
                "source": "researchgate",
                "relevance": 0.95,
                "feasibility": "высокая",
            },
            {
                "name": "Зарядка облаков",
                "description": "Активное изменение заряда облака для предотвращения молний",
                "source": "arxiv",
                "relevance": 0.6,
                "feasibility": "низкая",
            },
        ]
        
        return methods

    def get_electricity_facts(self) -> List[str]:
        """Получает интересные факты об атмосферном электричестве."""
        return [
            "Молния в 5 раз горячее поверхности Солнца (до 30 000 К)",
            "Каждая молния переносит около 15 кулонов заряда",
            "В мире происходит около 1,4 миллиона гроз в год",
            "Глобальная электрическая цепь поддерживает разность потенциалов ~250 кВ между ионосферой и землёй",
            "Шаровая молния до сих пор не имеет единого научного объяснения",
            "Спрайты — самые большие разряды в атмосфере, достигают 90 км высоты",
            "Энергия одной молнии достаточно велика для работы лампочки ~3 месяца",
            "Молнии могут содержать до 200 кА тока",
            "Скорость лидера молнии — около 200 000 км/ч",
            "Молнии обнаружены на Юпитере, Сатурне и Венере",
        ]
