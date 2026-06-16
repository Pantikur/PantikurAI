# Wuglarst/src/web_search.py
# Оптимизированная версия для поиска значений слов в интернете
# Логирование: logging.info / warning / error для всех ключевых этапов
# Добавлено временное хранилище temp_cache для поиска определений в рамках текущей сессии

import requests
from bs4 import BeautifulSoup
import re
import time
import logging
import os
import json
from typing import Dict, List, Optional
import undetected_chromedriver as uc

# Настройка логирования (вы можете переопределить уровень через logging.basicConfig)
logger = logging.getLogger(__name__)


class WebSearch:
    """
    Класс для быстрого поиска значений новых слов в интернете.
    Использует Yandex.Search как основной источник (без delay, без fallback на Google/Bing),
    с ограничением времени (2.5 сек), кэшированием неуспешных запросов и логированием.

    Основные цели:
    - Ответ за <3 сек (включая timeout)
    - Кэширование ошибок, чтобы не повторять запросы на опечатки
    - Полное логирование времени, ошибок и релевантности
    - Поддержка temp_cache (временное хранилище в памяти) для диалогов
    """

    def __init__(self, cache_file: str = "data/knowledge_cache.json"):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0 Safari/537.36'
        }

        # ✅ Добавляем Google
        self.google_config = {
            'url': 'https://www.google.com/search',
            'params': {'hl': 'ru'},
            'snippet_selectors': ['.VwiC3b', '.DeDApp', '.BNeawe.s3v9rd.AP7Wnd'],
        }

        self.yandex_config = {
            'url': 'https://yandex.ru/search/',
            'params': {'lr': 213},
            'snippet_selectors': [
                '.organic__snippet',
                '.serp-item__snippet',
                'div[data-c] > .serp-item__snippet',
                'div[data-c] span',
                'div[data-c] .text-snippet',
                'div[data-c] p',
                'div[data-c] .snippet',
                'div[data-c] .organs__snippet',
                'div[data-c] .snippet',
                'div[data-c] .text',
            ],
            'link_selectors': [
                '.serp-item__link',
                '.organic__link',
                'a[href]',
            ],
        }

        # ✅ Список словарей для поиска ссылок
        self.dictionary_sources = [
            'ozhegov', 'tolkoviy', 'dictionary', 'словарь', 'ожегов', 'толковый'
        ]

        # Инициализация driver
        self.driver = None

        # ✅ Временное хранилище (temp_cache) для диалогов
        self.temp_cache: Dict[str, str] = {}

        # ✅ Постоянный кэш (загружается позже, но поле должно быть)
        self.knowledge_cache: Dict[str, str] = {}

        # 🔧 Загрузка постоянного кэша при инициализации
        self._load_knowledge_cache(cache_file)

    def _load_knowledge_cache(self, cache_file: str = "data/knowledge_cache.json"):
        """Загрузка кэша из файла. Создаёт пустой кэш, если файл не найден."""
        if not cache_file:
            cache_file = "data/knowledge_cache.json"
        if os.path.exists(cache_file):
            try:
                with open(cache_file, "r", encoding="utf-8") as f:
                    self.knowledge_cache = json.load(f)
                logger.info(f"📚 knowledge_cache загружен: {len(self.knowledge_cache)} записей")
            except Exception as e:
                logger.warning(f"⚠️ Ошибка загрузки кэша: {e}")
                self.knowledge_cache = {}  # Сброс при ошибке
        else:
            logger.info(f"ℹ️ knowledge_cache не найден ({cache_file}), начнем с пустого кэша")

    def init_driver(self):
        """Инициализирует undetected_chromedriver"""
        try:
            # 🔧 ДОБАВЛЕНО: настройки для Docker и headless-режима
            options = uc.ChromeOptions()
            options.add_argument("--no-sandbox")
            options.add_argument("--disable-dev-shm-usage")
            options.add_argument("--headless=new")  # ← HEADLESS
            options.add_argument("--disable-gpu")
            options.add_argument("--window-size=1920,1080")

            self.driver = uc.Chrome(options=options)
            logger.info("✅ WebSearch driver initialized (Docker headless)")
        except Exception as e:
            logger.error(f"❌ Ошибка инициализации драйвера: {e}")
            self.driver = None

    def _fetch_with_selenium(self, url: str, params: Dict[str, str], timeout: float = 3.0) -> Optional[str]:
        """Вспомогательный метод — загрузка HTML через Selenium"""
        if not self.driver:
            logger.error("❌ _fetch_with_selenium: драйвер не инициализирован")
            return None

        try:
            logger.debug(f"🚀 _fetch_with_selenium: GET {url} → params={params}")
            self.driver.get(f"{url}?{'&'.join(f'{k}={v}' for k, v in params.items())}")
            time.sleep(1.5)  # Ждём рендеринга
            return self.driver.page_source
        except Exception as e:
            logger.error(f"❌ _fetch_with_selenium: ошибка при загрузке {url}: {e}")
            return None

    def search_word_meaning(self, word: str, timeout: float = 2.5) -> Dict[str, any]:
        # Если драйвер не инициализирован, сразу возвращаем ошибку
        if not self.driver:
            logger.warning(f"⚠️ search_word_meaning: драйвер не инициализирован. Возврат not_found для '{word}'.")
            return {
                'word': word,
                'status': 'not_found',
                'definitions': [],
                'dictionary_sources': [],
                'search_queries': [{'engine': 'yandex', 'query': '', 'success': False, 'error': 'driver_not_init'}],
                'total_definitions_found': 0,
                'total_dict_sources_found': 0,
                'error': 'Сервис поиска в интернете недоступен.',
            }

        logger.info(f"🔍 search_word_meaning('{word}') начал")
        start_time = time.time()

        all_definitions = []
        all_dict_results = []
        search_queries = []

        query_variants = [
            f'значение слова {word}',
            f'{word} — это',
        ]

        for engine, config in [('google', self.google_config), ('yandex', self.yandex_config)]:
            if len(all_definitions) >= 1 and len(all_dict_results) >= 1:
                break

            for i, query in enumerate(query_variants):
                try:
                    if time.time() - start_time > timeout:
                        logger.warning(f"⏱ search_word_meaning: timeout ({time.time() - start_time:.1f} сек) для '{word}'")
                        break

                    logger.info(f"⏱ search_word_meaning: {engine} запрос #{i+1} — '{query}'")

                    params = {'q' if engine == 'google' else 'text': query}
                    params.update(config['params'])

                    html_content = self._fetch_with_selenium(
                        config['url'],
                        params,
                        timeout=3.0,
                    )
                    if not html_content:
                        logger.warning(f"⚠️ search_word_meaning: не удалось загрузить страницу через Selenium")
                        search_queries.append({
                            'engine': engine,
                            'query': query,
                            'success': False,
                            'error': 'selenium_failed',
                        })
                        continue

                    logger.info(f"✅ search_word_meaning: успешный ответ на '{query}' ({len(html_content)} байт)")

                    soup = BeautifulSoup(html_content, 'html.parser')

                    # ✅ Парсим сниппеты
                    all_snippets = []
                    for sel in config['snippet_selectors']:
                        found = soup.select(sel)
                        if found:
                            logger.debug(f"✅ search_word_meaning: найдено {len(found)} сниппетов по селектору '{sel}'")
                            all_snippets.extend(found)

                    # ✅ Обрабатываем сниппеты
                    for snippet in all_snippets:
                        text = snippet.get_text().strip()
                        if text and len(text) > 10:
                            # Проверяем, является ли это определением
                            if self._is_definition_text(text, word):
                                all_definitions.append({
                                    'text': text,
                                    'source': engine
                                })
                                logger.info(f"✅ search_word_meaning: найдено определение: '{text[:100]}...'")

                    # ✅ Ищем ссылки на словари
                    all_links = []
                    for sel in config['link_selectors']:
                        found = soup.select(sel)
                        if found:
                            logger.debug(f"✅ search_word_meaning: найдено {len(found)} ссылок по селектору '{sel}'")
                            all_links.extend(found)

                    for link in all_links:
                        href = link.get('href')
                        if href:
                            for source in self.dictionary_sources:
                                if source in href:
                                    title = link.get_text().strip()
                                    all_dict_results.append({
                                        'title': title,
                                        'url': href,
                                        'source': engine
                                    })
                                    logger.info(f"✅ search_word_meaning: найден источник: {source}")

                except Exception as e:
                    logger.warning(f"⏱ search_word_meaning: ошибка запроса '{query}': {e}")
                    search_queries.append({
                        'engine': engine,
                        'query': query,
                        'success': False,
                        'error': str(e),
                    })
                    continue

        elapsed = time.time() - start_time
        logger.info(f"⏱ search_word_meaning('{word}'): завершено за {elapsed:.2f} сек | "
                    f"defs={len(all_definitions)}, links={len(all_dict_results)}")

        if all_definitions:
            sorted_defs = sorted(
                all_definitions,
                key=lambda x: self._calculate_relevance(x['text'], word),
                reverse=True,
            )
            top_definitions = [d['text'] for d in sorted_defs[:2]]
            return {
                'word': word,
                'status': 'success',
                'definitions': top_definitions,
                'dictionary_sources': all_dict_results[:3],
                'search_queries': search_queries,
                'total_definitions_found': len(all_definitions),
                'total_dict_sources_found': len(all_dict_results),
            }

        return {
            'word': word,
            'status': 'not_found',
            'definitions': [],
            'dictionary_sources': [],
            'search_queries': search_queries,
            'total_definitions_found': 0,
            'total_dict_sources_found': 0,
            'error': 'Определения не найдены в доступных источниках',
        }
    

    def _is_definition_text(self, text: str, word: str) -> bool:
        text_lower = text.lower()
        word_lower = word.lower()

        definition_patterns = [
            f'{word_lower} — это',
            f'{word_lower}, это',
            f'слово {word_lower}',
            f'термин {word_lower}',
            f'называется {word_lower}',
            'означает',
            'обозначает',
            'значит',
            'подразумевает',
        ]

        has_definition_pattern = any(p in text_lower for p in definition_patterns)

        words = re.findall(r'[а-яА-ЯёЁ]+', text_lower)
        common_words = {
            'и', 'в', 'на', 'не', 'а', 'но', 'или', 'да', 'нет',
            'быть', 'его', 'ее', 'их', 'мне', 'к', 'у', 'для', 'по',
            'из', 'от', 'с', 'у', 'к', 'о', 'об', 'за', 'про', 'под',
        }
        meaningful_words = [w for w in words if w not in common_words]

        # Дополнительно: если текст содержит "Ожегов", "Словарь Ожегова", "Толковый словарь" — считаем определением
        has_ozhegov = any(
            phrase in text_lower
            for phrase in ['ожегов', 'толковый словарь', 'ozhegov', 'dictionary']
        )

        return has_definition_pattern or has_ozhegov or (len(meaningful_words) >= 3 and len(set(meaningful_words)) >= 2)
    
    def _calculate_relevance(self, text: str, word: str) -> float:
        """
        Рассчитывает релевантность текста как определения слова.

        Критерии:
        - Наличие слова в начале текста: +1.5
        - Паттерны определения: +2.0 за каждый
        - Короткие тексты штрафуются
        - Длинные тексты штрафуются
        - Разнообразие слов поощряется
        """
        score = 0.0
        text_lower = text.lower()
        word_lower = word.lower()

        # 1. Слово в начале текста
        if text_lower.strip().startswith(word_lower):
            score += 1.5

        # 2. Паттерны определения
        definition_indicators = [
            '— это',
            'означает',
            'обозначает',
            'значит',
        ]
        for indicator in definition_indicators:
            if indicator in text_lower:
                score += 2.0

        # 3. Штраф за длину
        if len(text) < 50:
            score *= 0.7
        elif len(text) > 500:
            score *= 0.8

        # 4. Уникальность слов
        words = re.findall(r'[а-яА-ЯёЁ]+', text_lower)
        if words:
            uniqueness = len(set(words)) / len(words)
            score *= (0.5 + uniqueness * 0.5)

        return score

    def _clean_definition(self, definition: str) -> str:
        """Очистка текста определения от лишних символов и тегов"""
        # Удаляем [1], [2], [3] и т.д.
        cleaned = re.sub(r'\[\d+\]', '', definition)
        # Удаляем лишние пробелы и переносы строк
        cleaned = ' '.join(cleaned.split())
        return cleaned.strip()

    def lookup(self, word: str, timeout: float = 2.5, knowledge_cache: Dict = None,
               save_knowledge_cache_func=None) -> Optional[str]:
        """
        Основной метод — ищет определение слова, возвращает строку.

        Логика:
        1. Проверяет temp_cache (временное хранилище диалога).
        2. Проверяет knowledge_cache (постоянный кэш).
        3. Если не найдено → делает запрос в интернет.
        4. Сохраняет результат в temp_cache (и knowledge_cache, если указан).

        Параметры:
        - word: слово для поиска
        - timeout: максимальное время поиска (по умолчанию 2.5 сек)
        - knowledge_cache: словарь, в который сохраняются результаты (постоянный кэш)
        - save_knowledge_cache_func: функция-колбек для сохранения кэша (например, json.dump)

        Возвращает:
        - str — короткое определение
        - None — если не найдено или таймаут
        """
        logger.info(f"📥 lookup('{word}') начал")

        # 🔁 1. Ищем в temp_cache (временное хранилище сессии)
        if word in self.temp_cache:
            cached = self.temp_cache[word]
            if "не найдено" in cached:
                logger.info(f"📚 lookup('{word}'): из temp_cache → не найдено → возврат None")
                return None
            else:
                logger.info(f"📚 lookup('{word}'): из temp_cache → найдено: '{cached[:50]}...'")
                return cached

        # 🔁 2. Ищем в knowledge_cache (постоянный кэш)
        if knowledge_cache and word in knowledge_cache:
            cached = knowledge_cache[word]
            if "не найдено" in cached:
                logger.info(f"📚 lookup('{word}'): из knowledge_cache → не найдено → возврат None")
                return None
            else:
                logger.info(f"📚 lookup('{word}'): из knowledge_cache → найдено: '{cached[:50]}...'")
                # Копируем в temp_cache для скорости
                self.temp_cache[word] = cached
                return cached

        # 🔁 3. Если не найдено ни в одном кэше — идём в интернет
        start_time = time.time()
        result = self.search_word_meaning(word, timeout=timeout)
        elapsed = time.time() - start_time

        # Проверка timeout
        if elapsed > timeout or result['status'] != 'success':
            logger.warning(f"⏱ lookup('{word}'): timeout или не найдено ({elapsed:.1f} сек)")
            # Сохраняем в temp_cache
            self.temp_cache[word] = "Слово не найдено в словаре."
            # Также сохраняем в knowledge_cache, если он есть
            if knowledge_cache and save_knowledge_cache_func:
                knowledge_cache[word] = "Слово не найдено в словаре (timeout)."
                save_knowledge_cache_func()
            return None

        # Обработка результата
        if result['status'] == 'success' and result['definitions']:
            definition = result['definitions'][0]
            cleaned = self._clean_definition(definition)

            # Оставляем первые 2 предложения
            sentences = re.split(r'[.!?]', cleaned)
            sentences = [s.strip() for s in sentences if s.strip()]
            short_def = '. '.join(sentences[:2]) + '.' if len(sentences) > 1 else (sentences[0] if sentences else cleaned)

            # 🔹 Сохраняем в temp_cache
            self.temp_cache[word] = short_def.strip()
            logger.info(f"✅ lookup('{word}'): найдено определение за {elapsed:.1f} сек → '{short_def[:80]}...'")
            return short_def.strip()

        # Сохраняем как "не найдено"
        logger.info(f"ℹ️ lookup('{word}'): не найдено, сохранено в temp_cache за {elapsed:.1f} сек")
        self.temp_cache[word] = "Слово не найдено в словаре."
        # Также сохраняем в knowledge_cache, если он есть
        if knowledge_cache and save_knowledge_cache_func:
            knowledge_cache[word] = "Слово не найдено в словаре."
            save_knowledge_cache_func()

        return None

    def get_word_from_context(self, text: str, min_length: int = 5) -> List[str]:
        """
        Извлекает потенциально новые слова (с заглавной буквы) из контекста.

        Правила:
        - Ищем слова, начинающиеся с заглавной буквы
        - Игнорируем: "Я", "Ты", "Мы", "Вы", "Он", "Она", "Они", "Оно"
        - Минимальная длина: min_length
        - Возвращаем 1 слово (самое длинное или первое новое)

        Возвращает:
        - List[str] — найденные слова
        """
        
        # Общие исключения (частые слова с заглавной буквы)
        exclusions = {
            'я', 'ты', 'мы', 'вы', 'он', 'она', 'они', 'оно',
            'это', 'что', 'как', 'сам', 'себя', 'себе', 'сама', 'сами',
            'вас', 'тебя', 'тебе', 'меня', 'мне', 'мной', 'мною',
            'вас', 'вами', 'тебя', 'тобой', 'тобою'
        }

        # Ищем все слова, начинающиеся с заглавной буквы
        candidates = re.findall(r'\b([А-ЯЁ][а-яё]{' + str(min_length-1) + r',})', text)
        if not candidates:
            return []

        # Фильтруем и нормализуем
        words = []
        for w in candidates:
            w_lower = w.lower()
            if w_lower not in exclusions and len(w) >= min_length:
                words.append(w)

        # Убираем дубликаты (с учётом регистра), сохраняем порядок
        seen = set()
        unique = []
        for w in words:
            w_lower = w.lower()
            if w_lower not in seen:
                seen.add(w_lower)
                unique.append(w)

        logger.debug(f"🔍 get_word_from_context: из '{text[:50]}...' → найдено {len(unique)} слов: {unique}")
        return unique[:1]  # Возвращаем первое (или пустой список)
    
    def reset_temp_cache(self):
        """Очищает временный кэш (например, при новом диалоге)."""
        self.temp_cache.clear()
        logger.info("🗑️ temp_cache сброшен")

    def save_knowledge_cache(self, cache_file: str = "data/knowledge_cache.json"):
        """Сохраняет knowledge_cache в файл (для долгосрочного хранения)."""
        if not cache_file:
            cache_file = "data/knowledge_cache.json"
        try:
            os.makedirs(os.path.dirname(cache_file) or ".", exist_ok=True)
            with open(cache_file, "w", encoding="utf-8") as f:
                json.dump(self.knowledge_cache, f, ensure_ascii=False, indent=2)
            logger.info(f"💾 knowledge_cache сохранён: {len(self.knowledge_cache)} записей → {cache_file}")
        except Exception as e:
            logger.error(f"❌ Ошибка сохранения knowledge_cache: {e}")