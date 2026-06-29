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
from typing import Dict, List, Optional, Any
import undetected_chromedriver as uc

# Настройка логирования
logger = logging.getLogger(__name__)


# 🧠 Простой тренер для сохранения метаданных в JSONL
class SimpleTrainer:
    def __init__(self, log_file: str = "data/training_data.jsonl"):
        self.log_file = log_file
        os.makedirs(os.path.dirname(log_file) or ".", exist_ok=True)
        logger.info(f"🧠 SimpleTrainer инициализирован: {log_file}")

    def log_success(self, word: str, definition: str, weights: Dict[str, Any],
                   score: float, source: str, explanation: str = ""):
        record = {
            "timestamp": time.time(),
            "word": word,
            "definition": definition,
            "weights": weights,
            "score": round(score, 2),
            "source": source,
            "explanation": explanation,
        }
        try:
            with open(self.log_file, "a", encoding="utf-8") as f:
                f.write(json.dumps(record, ensure_ascii=False) + "\n")
            logger.info(f"✅ trainer: записан успешный поиск '{word}' → {self.log_file}")
        except Exception as e:
            logger.error(f"❌ trainer: ошибка записи успешного запроса: {e}")

    def log_failure(self, word: str, error: str, reason: str = "unknown"):
        record = {
            "timestamp": time.time(),
            "word": word,
            "definition": None,
            "weights": None,
            "score": 0.0,
            "source": "none",
            "error": error,
            "reason": reason,
        }
        try:
            with open(self.log_file, "a", encoding="utf-8") as f:
                f.write(json.dumps(record, ensure_ascii=False) + "\n")
            logger.warning(f"⚠️ trainer: записан неуспешный запрос '{word}' → {self.log_file}")
        except Exception as e:
            logger.error(f"❌ trainer: ошибка записи неудачного запроса: {e}")


# 📊 Метаданные для тестов (если нужен батч-поиск + анализ)
class TestResult:
    def __init__(self, word: str, success: bool, score: float | None = None, source: str | None = None,
                 definition: str | None = None, weights: Dict[str, Any] | None = None, time_ms: int | None = None, error: str | None = None):
        self.word = word
        self.success = success
        self.score = score
        self.source = source
        self.definition = definition
        self.weights = weights
        self.time_ms = time_ms
        self.error = error

    def to_dict(self) -> Dict:
        return {
            "word": self.word,
            "success": self.success,
            "score": self.score,
            "source": self.source,
            "definition": self.definition,
            "weights": self.weights,
            "time_ms": self.time_ms,
            "error": self.error,
        }

    def __repr__(self):
        return f"TestResult('{self.word}', success={self.success}, score={self.score}, source={self.source})"


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
    - 🧠 Поддержка тренера для дообучения модели (SimpleTrainer)
    - 📊 Батч-поиск через run_test(...) для анализа
    """

    def __init__(self, cache_file: str = "data/knowledge_cache.json"):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0 Safari/537.36'
        }

        self.google_config = {
            'url': 'https://www.google.com/search',
            'params': {'hl': 'ru'},
            'snippet_selectors': ['.VwiC3b', '.DeDApp', '.BNeawe.s3v9rd.AP7Wnd'],
            'link_selectors': ['.r > a', '.yuRUbf a', 'a[href]'],
        }

        self.yandex_config = {
            'url': 'https://yandex.ru/search/',
            'params': {'lr': 213},
            'snippet_selectors': [
                '.organic__snippet', '.serp-item__snippet',
                'div[data-c] > .serp-item__snippet', 'div[data-c] span',
                'div[data-c] .text-snippet', 'div[data-c] p',
                'div[data-c] .snippet', 'div[data-c] .organs__snippet',
                'div[data-c] .text',
            ],
            'link_selectors': ['.serp-item__link', '.organic__link', 'a[href]'],
        }

        self.dictionary_sources = [
            'ozhegov', 'tolkoviy', 'dictionary', 'словарь', 'ожегов', 'толковый'
        ]

        self.driver = None
        self.temp_cache: Dict[str, str] = {}
        self.knowledge_cache: Dict[str, str] = {}
        self.trainer: Optional[Any] = None  # 🧠 SimpleTrainer

        self._load_knowledge_cache(cache_file)

    def _load_knowledge_cache(self, cache_file: str = "data/knowledge_cache.json"):
        if not cache_file:
            cache_file = "data/knowledge_cache.json"
        if os.path.exists(cache_file):
            try:
                with open(cache_file, "r", encoding="utf-8") as f:
                    self.knowledge_cache = json.load(f)
                logger.info(f"📚 knowledge_cache загружен: {len(self.knowledge_cache)} записей")
            except Exception as e:
                logger.warning(f"⚠️ Ошибка загрузки кэша: {e}")
                self.knowledge_cache = {}
        else:
            logger.info(f"ℹ️ knowledge_cache не найден ({cache_file}), начнем с пустого кэша")

    def init_driver(self):
        try:
            options = uc.ChromeOptions()
            options.add_argument("--no-sandbox")
            options.add_argument("--disable-dev-shm-usage")
            options.add_argument("--headless=new")
            options.add_argument("--disable-gpu")
            options.add_argument("--window-size=1920,1080")

            # 🔧 Автоматический поиск Chrome/Chromium по системе
            chrome_path = os.getenv("CHROME_BINARY_PATH", "")
            if not chrome_path:
                for path in [
                    r"C:\Program Files\Google\Chrome\Application\chrome.exe",
                    r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
                    "/usr/bin/google-chrome",
                    "/usr/bin/google-chrome-stable",
                    "/usr/bin/chromium",
                    "/usr/bin/chromium-browser",
                    "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
                ]:
                    if os.path.exists(path):
                        chrome_path = path
                        break
            
            if chrome_path:
                options.binary_location = chrome_path
                logger.info(f"✅ Chrome найден: {chrome_path}")
            else:
                logger.warning("⚠️ Chrome не найден. Установите CHROME_BINARY_PATH или добавьте браузер в PATH.")

            self.driver = uc.Chrome(options=options)
            logger.info("✅ WebSearch driver initialized (Docker headless)")
        except Exception as e:
            logger.error(f"❌ Ошибка инициализации драйвера: {e}")
            self.driver = None

    def _fetch_with_selenium(self, url: str, params: Dict[str, str], timeout: float = 3.0) -> Optional[str]:
        if not self.driver:
            logger.error("❌ _fetch_with_selenium: драйвер не инициализирован")
            return None
        try:
            logger.debug(f"🚀 _fetch_with_selenium: GET {url}")
            self.driver.get(f"{url}?{'&'.join(f'{k}={v}' for k, v in params.items())}")
            time.sleep(0.7)  # ← уменьшено с 1.5 → 0.7
            return self.driver.page_source
        except Exception as e:
            logger.error(f"❌ _fetch_with_selenium: ошибка при загрузке {url}: {e}")
            return None

    def search_word_meaning(self, word: str, timeout: float = 5.0) -> Dict[str, Any]:
        if not self.driver:
            logger.warning(f"⚠️ search_word_meaning: драйвер не инициализирован. Возврат not_found для '{word}'.")
            return {
                'word': word, 'status': 'not_found', 'definitions': [], 'dictionary_sources': [],
                'search_queries': [{'engine': 'yandex', 'query': '', 'success': False, 'error': 'driver_not_init'}],
                'total_definitions_found': 0,
            }

        logger.info(f"🔍 search_word_meaning('{word}') начал")
        start_time = time.time()
        all_definitions = []
        all_dict_results = []
        search_queries = []

        # 🔧 Расширенные запросы: определение + контекст + уместность
        query_variants = [
            f'{word} — это',
            f'{word} определение',
            f'{word} примеры использования',
            f'{word} контекст употребления',
            f'{word} уместно',
            f'{word} стиль речи',
            f'{word} регистр',
            f'{word} значение и употребление',
        ]

        # 🔧 Только Яндекс (быстрее и надёжнее, чем Google/Yandex вместе)
        for engine, config in [('yandex', self.yandex_config)]:
            if len(all_definitions) >= 2:
                break
            for i, query in enumerate(query_variants):
                # 🔧 Досрочный выход, если близок таймаут
                if time.time() - start_time > (timeout - 1.2):
                    logger.warning(f"⏱ search_word_meaning: близок timeout ({time.time() - start_time:.1f} сек)")
                    break

                logger.info(f"⏱ search_word_meaning: {engine} запрос #{i+1} — '{query}'")
                params = {'text': query}
                params.update(config['params'])

                html_content = self._fetch_with_selenium(config['url'], params, timeout=3.0)
                if not html_content:
                    logger.warning(f"⚠️ search_word_meaning: не удалось загрузить страницу через Selenium")
                    search_queries.append({
                        'engine': engine, 'query': query, 'success': False, 'error': 'selenium_failed',
                    })
                    continue  # ← быстро пропускаем неудачные запросы

                soup = BeautifulSoup(html_content, 'html.parser')
                all_snippets = []
                for sel in config['snippet_selectors']:
                    found = soup.select(sel)
                    if found:
                        all_snippets.extend(found)

                for snippet in all_snippets:
                    text = snippet.get_text().strip()
                    if text and len(text) > 10:
                        weights_info = self._calculate_weights(text, word)
                        score = weights_info['total_score']
                        category = self._categorize_snippet(text, word)
                        all_definitions.append({
                            'text': text, 'source': engine,
                            'weights': weights_info['weights'], 'score': score,
                            'category': category,
                        })

                # 🔍 Ищем ссылки на словари
                all_links = []
                for sel in config['link_selectors']:
                    all_links.extend(soup.select(sel))
                for link in all_links:
                    href = link.get('href')
                    if href:
                        for source in self.dictionary_sources:
                            if source in href:
                                all_dict_results.append({
                                    'title': link.get_text().strip(),
                                    'url': href, 'source': engine
                                })
                                break

        elapsed = time.time() - start_time
        logger.info(f"⏱ search_word_meaning('{word}'): завершено за {elapsed:.2f} сек | "
                    f"candidates={len(all_definitions)}, dict_links={len(all_dict_results)}")

        if all_definitions:
            sorted_defs = sorted(all_definitions, key=lambda x: x['score'], reverse=True)
            
            # Разделяем по категориям
            definitions = []
            usage_examples = []
            contexts = []
            register_info = []
            
            for d in sorted_defs:
                cat = d.get('category', 'definition')
                item = {
                    'text': d['text'], 'source': d['source'],
                    'score': round(d['score'], 2), 'weights': d['weights'],
                    'explanation': self._explain_weights(d['weights'], d['score']),
                }
                if cat == 'definition':
                    definitions.append(item)
                elif cat == 'usage':
                    usage_examples.append(item)
                elif cat == 'context':
                    contexts.append(item)
                elif cat == 'register':
                    register_info.append(item)
                elif cat == 'circumstance':
                    contexts.append(item)
            
            # Берём топ-1 определение, топ-3 примера использования, топ-2 контекста, топ-1 информации о регистре
            top_result = {
                'definitions': definitions[:1],
                'usage_examples': usage_examples[:3],
                'contexts': contexts[:2],
                'register_info': register_info[:1],
                'dictionary_sources': all_dict_results[:3],
                'search_queries': search_queries,
                'total_definitions_found': len(all_definitions),
            }

            # Если нет явных определений, берём первое подходящее
            if not top_result['definitions'] and definitions:
                top_result['definitions'] = [definitions[0]]
            
            # Если нет примеров использования, берём из определений те, что содержат примеры
            if not top_result['usage_examples']:
                for d in sorted_defs:
                    text = d['text']
                    if any(kw in text.lower() for kw in ['например', 'к примеру', 'как правило', 'включает', 'состоит из', 'применяется']):
                        top_result['usage_examples'].append({
                            'text': d['text'], 'source': d['source'],
                            'score': round(d['score'], 2), 'weights': d['weights'],
                        })
                        if len(top_result['usage_examples']) >= 3:
                            break
            
            return {
                'word': word, 'status': 'success',
                **top_result,
            }

        # 🔧 FIXED: добавлено явное 'error' при отсутствии определений
        return {
            'word': word,
            'status': 'not_found',
            'definitions': [],
            'dictionary_sources': [],
            'search_queries': search_queries,
            'total_definitions_found': 0,
            'error': 'Определения не найдены',
        }

    def _calculate_weights(self, text: str, word: str) -> Dict[str, Any]:
        """
        Рассчитывает веса текста как определения слова.
        Пример: {'word_start': True, 'pattern_is': True, 'clean_text': True, 'good_length': True, ...}
        """
        text_lower = text.lower()
        word_lower = word.lower()
        weights = {}
        
        # 1. Слово в начале
        weights['word_start'] = text_lower.strip().startswith(word_lower)

        # 2. Паттерны определения
        weights['pattern_is'] = f'{word_lower} — это' in text_lower
        weights['pattern_means'] = any(p in text_lower for p in ['означает', 'обозначает', 'значит', 'подразумевает'])
        weights['pattern_named'] = f'называется {word_lower}' in text_lower
        weights['pattern_value'] = f'значение слова {word_lower}' in text_lower

        # 3. Упоминание словаря
        weights['has_dictionary_keyword'] = any(
            phrase in text_lower for phrase in ['ожегов', 'толковый словарь', 'ozhegov', 'dictionary']
        )

        # 4. Длина
        weights['good_length'] = 30 <= len(text) <= 200
        weights['too_short_or_long'] = len(text) < 30 or len(text) > 200

        # 5. Много смысловых слов
        words = re.findall(r'[а-яА-ЯёЁ]+', text_lower)
        common_words = {'и', 'в', 'на', 'не', 'а', 'но', 'или', 'да', 'нет',
                        'быть', 'его', 'ее', 'их', 'мне', 'к', 'у', 'для', 'по',
                        'из', 'от', 'с', 'у', 'к', 'о', 'об', 'за', 'про', 'под'}
        meaningful_words = [w for w in words if w not in common_words]
        weights['meaningful_words'] = len(meaningful_words) >= 3

        # 6. Чистый текст
        weights['clean_text'] = not any(c in text for c in ['[1]', 'https://', 'смотрите также'])
        weights['no_punctuation_marks'] = '!' not in text and '?' not in text

        # Вычисляем total_score
        score = 0.0
        if weights['word_start']: score += 2.0
        if weights['pattern_is']: score += 2.0
        if weights['pattern_means']: score += 1.0
        if weights['pattern_named']: score += 1.0
        if weights['pattern_value']: score += 1.0
        if weights['has_dictionary_keyword']: score += 1.5
        if weights['good_length']: score += 1.0
        if weights['meaningful_words']: score += 0.5
        if weights['clean_text']: score += 1.0
        if weights['no_punctuation_marks']: score += 0.3
        if weights['too_short_or_long']: score *= 0.9

        return {'weights': weights, 'total_score': score}

    def _explain_weights(self, weights: Dict[str, Any], score: float) -> str:
        if not weights:
            return f"[score={score:.1f}] no weights"

        key_labels = {
            'word_start': 'слово_в_начале',
            'pattern_is': 'паттерн_это',
            'pattern_means': 'означает_или_обозначает',
            'pattern_named': 'называется',
            'pattern_value': 'значение_слова',
            'has_dictionary_keyword': 'упоминание_словаря',
            'good_length': 'длина_в_норме',
            'too_long': 'слишком_длинный',
            'too_short_or_long': 'плохая_длина',
            'meaningful_words': 'много_смысловых_слов',
            'clean_text': 'чистый_текст',
            'no_punctuation_marks': 'без_восклицаний/вопросов',
        }

        def format_value(k: str, v: Any) -> str:
            """
            Форматирует одно поле веса/фичи в читаемую строку.

            Примеры:
                format_value('word_start', True)   → '✅ слово_в_начале'
                format_value('score', 8.3)         → 'score=8.3'
                format_value('source', 'yandex')   → 'source="yandex"'
            """
            # 🔧 FIXED: используем .get(k, k), чтобы избежать KeyError
            readable_key = key_labels.get(k, k)

            if isinstance(v, bool):
                return f"{'✅' if v else '❌'} {readable_key}"
            elif isinstance(v, (int, float)):
                return f"{readable_key}={v:.1f}"
            elif isinstance(v, str):
                return f'{readable_key}="{v}"'
            elif isinstance(v, (list, tuple)):
                items = ', '.join(str(i) for i in v)
                return f"{readable_key}=[{items}]"
            elif isinstance(v, dict):
                nested_parts = []
                for nk, nv in v.items():
                    nested_parts.append(format_value(nk, nv))
                return f"{readable_key}={{{', '.join(nested_parts)}}}"
            elif v is None:
                return f"{readable_key}=null"
            else:
                return f"{readable_key}={repr(v)}"

        # ✅ Приоритетные ключи (в начале списка)
        priority_keys = [
            'word_start', 'pattern_is', 'pattern_means', 'clean_text', 'good_length',
            'meaningful_words', 'has_dictionary_keyword', 'no_punctuation_marks',
        ]
        # 🔢 Остальные ключи — сортируем по алфавиту
        other_keys = [k for k in sorted(weights.keys()) if k not in priority_keys]

        # 📌 Формируем строки для всех ключей
        parts = []
        for k in priority_keys + other_keys:
            if k in weights:
                parts.append(format_value(k, weights[k]))

        return f"[score={score:.1f}] " + ", ".join(parts)
    
    def run_test(self, words: List[str], timeout: float = 2.5) -> List[TestResult]:
        """
        📊 Батч-поиск: ищет определения для списка слов, сохраняет метаданные в TestResult.
        Полезно для анализа точности, скорости, весов.

        Возвращает:
        - List[TestResult] — для анализа (score, source, weights и т.д.)
        """
        results = []
        logger.info(f"📊 run_test: старт теста {len(words)} слов")
        start_time = time.time()

        for word in words:
            try:
                word_start = time.time()
                result = self.search_word_meaning(word, timeout=timeout)
                elapsed_ms = (time.time() - word_start) * 1000

                # Извлекаем метаданные из результата поиска
                success = result['status'] == 'success'
                score = result['definitions'][0]['score'] if result['definitions'] else 0.0
                source = result['definitions'][0]['source'] if result['definitions'] else None
                definition = result['definitions'][0]['text'] if result['definitions'] else None
                weights = result['definitions'][0]['weights'] if result['definitions'] else None

                # 🔧 FIXED: явно определяем error для логирования
                error = None
                if not success:
                    error = result.get('error', 'not_found')
                elif not result.get('definitions'):
                    error = 'empty_definitions'

                test_result = TestResult(
                    word=word,
                    success=success,
                    score=score,
                    source=source,
                    definition=definition,
                    weights=weights,
                    time_ms=int(elapsed_ms),
                    error=error
                )
                results.append(test_result)

                # 🔁 Если подключён тренер — логируем успешные и неуспешные случаи
                if self.trainer:
                    if success and definition:
                        self.trainer.log_success(
                            word=word,
                            definition=definition,
                            weights=weights,
                            score=score,
                            source=source,
                            explanation=result['definitions'][0].get('explanation', 'N/A')
                        )
                    else:
                        self.trainer.log_failure(
                            word=word,
                            error=error or 'unknown_error',
                            reason='no_definition'
                        )

                # 🔍 Логирование с деталями
                status_emoji = '✅' if success else '❌'
                logger.info(
                    f"📊 run_test: {word} → {status_emoji} (score={score:.1f}, time={elapsed_ms:.1f}мс)"
                )

            except Exception as e:
                logger.error(f"❌ run_test: ошибка поиска '{word}': {e}")

                # 🔧 FIXED: создаём TestResult даже при исключении
                test_result = TestResult(
                    word=word,
                    success=False,
                    score=0.0,
                    source=None,
                    definition=None,
                    weights=None,
                    time_ms=0
                )
                results.append(test_result)

                if self.trainer:
                    self.trainer.log_failure(
                        word=word,
                        error='exception',
                        reason=str(e)
                    )

        total_time = time.time() - start_time
        logger.info(f"📊 run_test: завершено за {total_time:.1f} сек | {len(results)} слов")
        return results

    def _categorize_snippet(self, text: str, word: str) -> str:
        """
        Определяет категорию текста:
        - 'definition' — прямое определение (слово — это ...)
        - 'usage' — примеры использования, как применять
        - 'context' — контекст/обстоятельства употребления
        - 'register' — информация о стиле, уместности, регистре
        - 'definition' (fallback)
        """
        text_lower = text.lower()
        
        # Регистрация / уместность / стиль
        register_keywords = [
            'стиль речи', 'разговорн', 'официал', 'деловой стиль', 'нейтральн',
            'литературн', 'простореч', 'жаргон', 'профессион', 'термин',
            'уместн', 'неуместн', 'подходит', 'не подходит', 'в общении',
            'в разговоре', 'в тексте', 'в письме', 'в речи',
            'в официал', 'в неформал', 'в повседнев', 'в научн',
            'степень формальности', 'уровень вежливости', 'контекст уместности',
        ]
        if any(kw in text_lower for kw in register_keywords):
            return 'register'
        
        # Контекст / обстоятельства
        context_keywords = [
            'контекст', 'обстоятел', 'в ситуации', 'при этом', 'в случае',
            'когда используют', 'когда говорят', 'когда пишут',
            'применяется в', 'употребляется в', 'используется при',
            'в зависимости от', 'в определённ', 'в определенных',
            'ситуации', 'окружени', 'поле', 'сфера', 'область',
        ]
        if any(kw in text_lower for kw in context_keywords):
            return 'context'
        
        # Примеры использования
        usage_keywords = [
            'например', 'к примеру', 'как пример', 'приведём',
            'скажем', 'возьмём', 'допустим', 'к примеру',
            'часто говорят', 'обычно говорят', 'применяется',
            'используется для', 'служит для', 'применяют для',
            'включает', 'состоит из', 'выражает', 'означает что',
        ]
        if any(kw in text_lower for kw in usage_keywords):
            return 'usage'
        
        # Определение (по умолчанию)
        def_keywords = [
            '— это', 'означает', 'обозначает', 'значит',
            'подразумевает', 'определяет', 'термин',
            'слово означает', 'понятие',
        ]
        if any(kw in text_lower for kw in def_keywords):
            return 'definition'
        
        # Fallback — определение, если содержит слово и похоже на определение
        word_lower = word.lower()
        if text_lower.strip().startswith(word_lower):
            return 'definition'
        
        return 'definition'
    
    def _build_comprehensive_answer(self, word: str, result: Dict) -> str:
        """
        Формирует комплексный ответ о слове:
        1. Определение
        2. Примеры использования
        3. Контекст и обстоятельства употребления
        4. Уместность, стиль, регистр
        """
        parts = []
        
        # 1. Определение
        definitions = result.get('definitions', [])
        if definitions:
            def_text = self._clean_definition(definitions[0]['text'])
            parts.append(f"Определение: {word} — это {def_text.lower()[0].upper() + def_text.lower()[1:]}")
        
        # 2. Примеры использования
        usage = result.get('usage_examples', [])
        if usage:
            examples = []
            for u in usage[:3]:
                cleaned = self._clean_definition(u['text'])
                # Берём первое предложение или весь короткий текст
                sentences = re.split(r'[.!?]', cleaned)
                sentences = [s.strip() for s in sentences if s.strip()]
                examples.append(sentences[0] if sentences else cleaned)
            parts.append(f"Примеры использования: {'; '.join(examples)}")
        
        # 3. Контекст и обстоятельства
        contexts = result.get('contexts', [])
        if contexts:
            ctx_texts = []
            for c in contexts[:2]:
                cleaned = self._clean_definition(c['text'])
                sentences = re.split(r'[.!?]', cleaned)
                sentences = [s.strip() for s in sentences if s.strip()]
                ctx_texts.append(sentences[0] if sentences else cleaned)
            parts.append(f"Контекст и обстоятельства: {'; '.join(ctx_texts)}")
        
        # 4. Уместность, стиль, регистр
        register = result.get('register_info', [])
        if register:
            reg_texts = []
            for r in register[:1]:
                cleaned = self._clean_definition(r['text'])
                sentences = re.split(r'[.!?]', cleaned)
                sentences = [s.strip() for s in sentences if s.strip()]
                reg_texts.append(sentences[0] if sentences else cleaned)
            parts.append(f"Уместность и стиль: {'; '.join(reg_texts)}")
        
        if not parts:
            # Fallback: просто первое определение
            if definitions:
                cleaned = self._clean_definition(definitions[0]['text'])
                return cleaned
            return f"Слово '{word}' — подробная информация не найдена."
        
        return ' '.join(parts)
    
    def _calculate_relevance(self, text: str, word: str) -> Dict[str, Any]:
        """
        Рассчитывает релевантность текста как определения слова (альтернативный/резервный метод).
        
        Возвращает dict с двумя оценками:
            - 'score' (float) — основная оценка (от 0.0 до ~10)
            - 'weights' (dict) — ключевые признаки (для логирования и дебага)
        
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
        weights = {}

        # 1. Слово в начале текста
        weights['word_start'] = text_lower.strip().startswith(word_lower)
        if weights['word_start']:
            score += 1.5

        # 2. Паттерны определения
        definition_indicators = [
            '— это',
            'означает',
            'обозначает',
            'значит',
        ]
        weights['pattern_indicators'] = []
        for indicator in definition_indicators:
            if indicator in text_lower:
                weights['pattern_indicators'].append(indicator)
                score += 2.0

        # 3. Штраф за длину
        weights['good_length'] = 50 <= len(text) <= 500
        if len(text) < 50:
            score *= 0.7
        elif len(text) > 500:
            score *= 0.8

        # 4. Уникальность слов
        words = re.findall(r'[а-яА-ЯёЁ]+', text_lower)
        weights['unique_words_ratio'] = None
        if words:
            uniqueness = len(set(words)) / len(words)
            weights['unique_words_ratio'] = uniqueness
            score *= (0.5 + uniqueness * 0.5)

        return {'score': score, 'weights': weights}
    
    def _clean_definition(self, definition: str) -> str:
        """Очистка текста определения от лишних символов и тегов"""
        cleaned = re.sub(r'\[\d+\]', '', definition)
        cleaned = ' '.join(cleaned.split())
        return cleaned.strip()

    def set_trainer(self, trainer: Any) -> None:
        """Подключает внешнюю систему дообучения (например, логгера в JSON, базу, или ML-модель)."""
        self.trainer = trainer
        logger.info(f"🧠 WebSearch подключен к тренеру: {type(trainer).__name__ if trainer else 'None'}")

    def lookup(self, word: str, timeout: float = 2.5, knowledge_cache: Dict[str, str] | None = None,
               save_knowledge_cache_func=None, return_weights: bool = False) -> str | Dict[str, Any] | None:
        """
        Основной метод — ищет определение слова, возвращает строку.

        Логика:
        1. Проверяет temp_cache (временное хранилище диалога).
        2. Проверяет knowledge_cache (постоянный кэш).
        3. Если не найдено → делает запрос в интернет.
        4. Сохраняет результат в temp_cache (и knowledge_cache, если указан).
        5. Отправляет метаданные в тренера (если подключён), чтобы можно было дообучать модель.

        Возвращает:
        - строку (если `return_weights=False`, по умолчанию) — для бота
        - или dict с метаданными (если `return_weights=True`) — для анализа
        """
        logger.info(f"📥 lookup('{word}') начал")
        
        # 🔁 1. Ищем в temp_cache
        if word in self.temp_cache:
            cached = self.temp_cache[word]
            if "не найдено" in cached:
                logger.info(f"📚 lookup('{word}'): из temp_cache → не найдено → возврат None")
                return None
            else:
                logger.info(f"📚 lookup('{word}'): из temp_cache → найдено: '{cached[:50]}...'")
                if return_weights:
                    logger.warning(f"⚠️ lookup: кэшированные веса недоступны (temp_cache хранит только текст)")
                return cached

        # 🔁 2. Ищем в knowledge_cache
        if knowledge_cache and word in knowledge_cache:
            cached = knowledge_cache[word]
            if "не найдено" in cached:
                logger.info(f"📚 lookup('{word}'): из knowledge_cache → не найдено → возврат None")
                return None
            else:
                logger.info(f"📚 lookup('{word}'): из knowledge_cache → найдено: '{cached[:50]}...'")
                self.temp_cache[word] = cached
                if return_weights:
                    logger.warning(f"⚠️ lookup: кэшированные веса недоступны (knowledge_cache хранит только текст)")
                return cached

        # 🔁 3. Если не найдено — идём в интернет
        start_time = time.time()
        result = self.search_word_meaning(word, timeout=timeout)
        elapsed = time.time() - start_time

        # Проверка timeout или неуспех
        if elapsed > timeout or result['status'] != 'success':
            logger.warning(f"⏱ lookup('{word}'): timeout или не найдено ({elapsed:.1f} сек)")
            self.temp_cache[word] = "Слово не найдено в словаре."
            if knowledge_cache and save_knowledge_cache_func:
                knowledge_cache[word] = "Слово не найдено в словаре (timeout)."
                save_knowledge_cache_func()

            # 🔄 Логируем неудачу в тренера
            if self.trainer:
                self.trainer.log_failure(
                    word=word,
                    error="timeout_or_not_found",
                    reason=f"elapsed={elapsed:.1f}s"
                )

            return None

        # Обработка результата
        if result['status'] == 'success' and result.get('definitions'):
            top_def = result['definitions'][0]

            # 🔁 Отправляем в тренера
            if self.trainer:
                try:
                    self.trainer.log_success(
                        word=word,
                        definition=top_def['text'],
                        weights=top_def['weights'],
                        score=top_def['score'],
                        source=top_def['source'],
                        explanation=top_def.get('explanation', 'N/A')
                    )
                    logger.debug(f"🧠 trainer.log_success('{word}') вызван")
                except Exception as e:
                    logger.warning(f"⚠️ trainer.log_success failed: {e}")

            # Формируем комплексный ответ
            full_answer = self._build_comprehensive_answer(word, result)

            # Сохраняем в кэши
            self.temp_cache[word] = full_answer
            if knowledge_cache and save_knowledge_cache_func:
                knowledge_cache[word] = full_answer
                save_knowledge_cache_func()

            logger.info(f"✅ lookup('{word}'): комплексный ответ за {elapsed:.1f} сек → '{full_answer[:80]}...'")

            # Возвращаем по запросу
            if return_weights:
                return {
                    'text': full_answer,
                    'weights': top_def['weights'],
                    'score': round(top_def['score'], 2),
                    'source': top_def['source'],
                    'structured': result,  # полная структура
                }
            return full_answer

        # Сохраняем как "не найдено"
        logger.info(f"ℹ️ lookup('{word}'): не найдено, сохранено в temp_cache")
        self.temp_cache[word] = "Слово не найдено в словаре."
        if knowledge_cache and save_knowledge_cache_func:
            knowledge_cache[word] = "Слово не найдено в словаре."

        # 🔄 Логируем неудачу в тренера
        if self.trainer:
            self.trainer.log_failure(word=word, error="no_definition", reason="empty_definitions")

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
            'вами', 'тобой', 'тобою',
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