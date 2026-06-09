# Wuglarst/src/web_search.py
# Оптимизированная версия для поиска значений слов в интернете
# Логирование: logging.info / warning / error для всех ключевых этапов

import requests
from bs4 import BeautifulSoup
import re
import time
import logging
import os
import json
from typing import Dict, List, Optional

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
    """

    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0 Safari/537.36'
        }

        # Конфигурация Yandex (единственная используемая поисковая система)
        self.yandex_config = {
            'url': 'https://yandex.ru/search/',
            'params': {'lr': 213},  # Россия
            'snippet_selector': 'div.TextSnippet',
            'link_selector': 'a[href]',
        }

        # Расширенный список словарей для проверки ссылок (не используются в основном поиске)
        self.dictionary_sources = [
            # Академические и универсальные словари
            'dic.academic.ru',
            'slovarozhegova.ru',
            'ozhegov.org',
            'slovar.cc',
            'teza.ru',
            'lifactor.ru/slovari',
            'allforchildren.ru/slovari',
            # Этимологические словари
            'etymologica.ru',
            'slovar.slovari.ru',
            # Словари иностранных слов
            'foreign_words.academic.ru',
            'slovar.silentfund.ru',
            # Специализированные словари
            'slovari.tilnp.ru',
            'slovari.gramota.ru',
            'slovari.yandex.ru',
            'dictionarium.com',
            # Энциклопедии
            'ru.wikipedia.org',
            'ru.wiktionary.org',
            'dic.academic.ru/cdit',
            # Современные словари сленга и неологизмов
            'newslang.ru',
            'slang.su',
            'russkiymir.ru/slovar',
            # Детские словари и образовательные ресурсы
            'deti-mama.ru/slovar',
            'razvitiechild.ru/slovar',
        ]

        # Стоп-слова для фильтрации (уже есть в chatbot.py, здесь дублировать не нужно)

    def search_word_meaning(self, word: str, timeout: float = 2.5) -> Dict[str, any]:
        """
        Быстрый поиск значения слова через Yandex.
        Делает максимум 2 запроса: "значение слова X" и "X — это".

        Возвращает:
        {
            'word': str,
            'status': 'success' | 'not_found',
            'definitions': List[str],  # топ-2 определения
            'dictionary_sources': List[Dict],  # топ-3 ссылки на словари
            'search_queries': List[Dict],  # истории запросов
        }

        Логирование:
        - Проверка времени
        - Обработка ошибок
        - Парсинг сниппетов и ссылок
        """
        logger.info(f"🔍 search_word_meaning('{word}') начал")
        start_time = time.time()

        all_definitions = []
        all_dict_results = []
        search_queries = []

        query_variants = [
            f'значение слова {word}',
            f'{word} — это',
        ]

        for i, query in enumerate(query_variants):
            try:
                # Прерываем, если превышен timeout
                if time.time() - start_time > timeout:
                    logger.warning(f"⏱ search_word_meaning: timeout ({time.time() - start_time:.1f} сек) для '{word}'")
                    break

                logger.info(f"⏱ search_word_meaning: запрос #{i+1} — '{query}'")

                params = {'text': query}
                params.update(self.yandex_config['params'])

                response = requests.get(
                    self.yandex_config['url'],
                    params=params,
                    headers=self.headers,
                    timeout=3.0,
                )
                response.raise_for_status()

                logger.info(f"✅ search_word_meaning: успешный ответ на '{query}' ({len(response.text)} байт)")

                soup = BeautifulSoup(response.text, 'html.parser')

                # Извлечение сниппетов (только 2, без лишних циклов)
                snippets = soup.select(self.yandex_config['snippet_selector'])
                for snippet in snippets[:2]:
                    text = snippet.get_text().strip()
                    if not (text and len(text) > 20):
                        continue

                    # Проверяем, является ли текст определением
                    if self._is_definition_text(text, word):
                        all_definitions.append({
                            'text': text,
                            'source': 'yandex',
                            'query': query,
                        })
                        logger.info(f"📚 search_word_meaning: найдено определение: {text[:60]}...")

                # Поиск ссылок на словари (только первые 3)
                links = soup.select(self.yandex_config['link_selector'])
                for link in links[:3]:
                    href = link.get('href')
                    if not href:
                        continue

                    # Проверяем, содержит ли ссылка словарь
                    if any(domain in href for domain in self.dictionary_sources):
                        link_text = link.get_text().strip()
                        if link_text and len(link_text) > 5:
                            dict_result = {
                                'title': link_text,
                                'url': href,
                                'source': 'yandex',
                                'query': query,
                            }
                            if dict_result not in all_dict_results:
                                all_dict_results.append(dict_result)
                                logger.info(f"🔗 search_word_meaning: найдена ссылка: {link_text} ({href})")

                search_queries.append({
                    'engine': 'yandex',
                    'query': query,
                    'success': True,
                })

                # Ранний выход: если нашли минимум 1 определение и 1 ссылку
                if len(all_definitions) >= 1 and len(all_dict_results) >= 1:
                    break

            except requests.exceptions.Timeout:
                logger.warning(f"⏱ search_word_meaning: timeout запроса для '{query}'")
                search_queries.append({
                    'engine': 'yandex',
                    'query': query,
                    'success': False,
                    'error': 'timeout',
                })
                continue
            except requests.exceptions.RequestException as e:
                logger.warning(f"⏱ search_word_meaning: ошибка запроса '{query}': {e}")
                search_queries.append({
                    'engine': 'yandex',
                    'query': query,
                    'success': False,
                    'error': str(e),
                })
                continue

        elapsed = time.time() - start_time
        logger.info(f"⏱ search_word_meaning('{word}'): завершено за {elapsed:.2f} сек | "
                    f"defs={len(all_definitions)}, links={len(all_dict_results)}")

        # Формируем итоговый результат
        if all_definitions:
            # Сортируем по релевантности
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

        # Если ничего не найдено
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
        """
        Проверяет, является ли текст определением слова.

        Шаблоны:
        - "слово X — это", "X — это", "означает"
        - Текст должен содержать как минимум 3 значимых слова

        Возвращает:
        - True — если текст выглядит как определение
        - False — иначе
        """
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

        # Фильтрация на значимые слова (не стоп-слова)
        words = re.findall(r'[а-яА-ЯёЁ]+', text_lower)
        common_words = {
            'и', 'в', 'на', 'не', 'а', 'но', 'или', 'да', 'нет',
            'быть', 'его', 'ее', 'их', 'мне', 'к', 'у', 'для', 'по',
            'из', 'от', 'с', 'у', 'к', 'о', 'об', 'за', 'про', 'под',
        }
        meaningful_words = [w for w in words if w not in common_words]

        # Минимум 3 слова и минимум 2 уникальных значимых слова
        return has_definition_pattern or (len(meaningful_words) >= 3 and len(set(meaningful_words)) >= 2)

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

    def lookup(self, word: str, timeout: float = 2.5, knowledge_cache: Dict = None,
               save_knowledge_cache_func=None) -> Optional[str]:
        """
        Основной метод — ищет определение слова, возвращает строку.

        Логика:
        1. Проверяет кэш неуспешных запросов (если есть → возвращает None)
        2. Делает запрос в Yandex через search_word_meaning
        3. Если найдено определение → возвращает короткую версию
        4. Если не найдено → сохраняет в кэш как "не найдено"
        5. Если timeout → сохраняет в кэш и возвращает None

        Параметры:
        - word: слово для поиска
        - timeout: максимальное время поиска (по умолчанию 2.5 сек)
        - knowledge_cache: словарь, в который сохраняются результаты
        - save_knowledge_cache_func: функция-колбек для сохранения кэша (например, json.dump)

        Возвращает:
        - str — короткое определение
        - None — если не найдено или таймаут
        """
        logger.info(f"📥 lookup('{word}') начал")

        # Проверка кэша неуспешных запросов
        if knowledge_cache and word in knowledge_cache:
            cached = knowledge_cache[word]
            if "не найдено" in cached:
                logger.info(f"📚 lookup('{word}'): из кэша → не найдено → возврат None")
                return None
            else:
                logger.info(f"📚 lookup('{word}'): из кэша → найдено: '{cached[:50]}...'")
                return cached

        # Вызов поиска
        start_time = time.time()
        result = self.search_word_meaning(word, timeout=timeout)
        elapsed = time.time() - start_time

        # Проверка timeout
        if elapsed > timeout:
            logger.warning(f"⏱ lookup('{word}'): timeout ({elapsed:.1f} сек)")
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

            logger.info(f"✅ lookup('{word}'): найдено определение за {elapsed:.1f} сек → '{short_def[:80]}...'")
            return short_def.strip()

        # Сохраняем как "не найдено"
        logger.info(f"ℹ️ lookup('{word}'): не найдено, сохранено в кэш за {elapsed:.1f} сек")
        if knowledge_cache and save_knowledge_cache_func:
            knowledge_cache[word] = "Слово не найдено в словаре."
            save_knowledge_cache_func()

        return None

    def _clean_definition(self, text: str) -> str:
        """
        Очищает текст определения от артефактов парсинга.
        """
        text = re.sub(r'\s+', ' ', text).strip()
        if text.startswith(('"', '"', ''', ''')) and text.endswith(('"', '"', ''', ''')):
            text = text[1:-1]
        text = re.sub(r'[\[\]\{\}\(\)]', '', text)
        text = re.sub(r'\.{2,}', '.', text)
        return text

    def get_word_from_context(self, text: str, common_words: set = None) -> List[str]:
        """
        Извлекает потенциально неизвестные слова из контекста.
        Возвращает топ-5 слов, исключая общие слова и стоп-слова.

        Параметры:
        - text: входной текст
        - common_words: пользовательский список стоп-слов (если не передан — используем стандартный)
        """
        if not common_words:
            common_words = {
                'и', 'в', 'на', 'не', 'я', 'что', 'он', 'с', 'как', 'а', 'то', 'мы',
                'но', 'вот', 'да', 'ты', 'вы', 'они', 'этот', 'тот', 'так', 'быть',
                'его', 'ее', 'их', 'мне', 'мной', 'к', 'у', 'для', 'по', 'из', 'о',
                'от', 'со', 'до', 'под', 'за', 'над', 'про', 'раз', 'два', 'три',
                'четыре', 'пять', 'шесть', 'семь', 'восемь', 'девять', 'десять',
                'один', 'два', 'три', 'четыре', 'пять', 'шесть', 'семь', 'восемь', 'девять', 'десять',
                'первый', 'второй', 'третий', 'четвертый', 'пятый', 'шестой', 'седьмой', 'восьмой', 'девятый', 'десятый',
                'мой', 'твой', 'наш', 'ваш', 'свой', 'ее', 'его', 'их', 'чей',
                'этот', 'тот', 'такой', 'иной', 'каждый', 'любой', 'никто', 'ничто', 'всё',
                'сам', 'другой', 'который', 'какой', 'чей', 'сколько', 'где', 'когда', 'куда',
                'откуда', 'почему', 'зачем', 'как', 'каким', 'какой', 'какая', 'какое', 'какие',
                'так', 'тогда', 'потом', 'после', 'до', 'из', 'от', 'с', 'у', 'к', 'до', 'под',
                'за', 'над', 'про', 'вокруг', 'через', 'между', 'возле', 'рядом', 'перед', 'после',
                'вместо', 'несмотря', 'вопреки', 'благодаря', 'согласно', 'вследствие',
                'ввиду', 'по', 'при', 'из-за', 'от', 'до', 'с', 'по', 'из', 'в', 'на', 'у',
                'к', 'о', 'об', 'от', 'до', 'за', 'из', 'по', 'под', 'про', 'ради', 'сквозь', 'среди'
            }

        logger.debug(f"🔍 get_word_from_context: извлечение слов из '{text[:50]}...' (common_words={len(common_words)})")

        # Извлекаем слова (только кириллица, минимум 3 символа)
        words = re.findall(r'[а-яА-ЯёЁ]{3,}', text.lower())
        logger.debug(f"🔍 get_word_from_context: найдено {len(words)} слов")

        # Фильтруем слова
        filtered_words = []
        for word in words:
            # Исключаем стоп-слова и слишком короткие слова
            if word not in common_words and len(word) >= 3:
                # Исключаем числа и слова с цифрами
                if not re.search(r'\d', word):
                    # Исключаем повторяющиеся слова
                    if word not in filtered_words:
                        filtered_words.append(word)

        logger.info(f"✅ get_word_from_context: топ-5 → {filtered_words[:5]}")
        return filtered_words[:5]
    
    
    def _load_knowledge_cache(self, cache_file: str = None):
        """Загрузка кэша из файла (опционально)."""
        if cache_file is None:
            cache_file = self._cache_file
        if os.path.exists(cache_file):
            try:
                with open(cache_file, "r", encoding="utf-8") as f:
                    self.knowledge_cache = json.load(f)
                logger.info(f"📚 knowledge_cache загружен: {len(self.knowledge_cache)} записей")
            except Exception as e:
                logger.warning(f"⚠️ Ошибка загрузки кэша: {e}")
        else:
            logger.info("ℹ️ knowledge_cache не найден, начнем с пустого кэша")

    def _save_knowledge_cache(self, word: str, response: str):
        """Сохранение записи в кэш."""
        self.knowledge_cache[word] = response
        try:
            with open(self._cache_file, "w", encoding="utf-8") as f:
                json.dump(self.knowledge_cache, f, ensure_ascii=False, indent=2)
            logger.info(f"💾 knowledge_cache сохранён (word='{word}')")
        except Exception as e:
            logger.warning(f"⚠️ Ошибка сохранения кэша: {e}")

    
    
if __name__ == "__main__":
    # Настройка логирования
    logging.basicConfig(level=logging.DEBUG)

    ws = WebSearch()
    ws._load_knowledge_cache("data/knowledge_cache.json")  # или None для пустого кэша

    # Тесты
    print("\n=== Тесты WebSearch ===")
    test_words = ["привет", "приветет", "гипотеза", "экзистенциализм"]
    for w in test_words:
        res = ws.lookup(w, timeout=2.5)
        print(f"{w}: {res}")