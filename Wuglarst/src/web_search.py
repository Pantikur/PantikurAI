import requests
from bs4 import BeautifulSoup
import re
from typing import Dict, List, Optional, Tuple
import time

class WebSearch:
    """
    Класс для поиска значений новых слов в интернете
    Поддерживает несколько поисковых систем и специализированные словари
    """
    
    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        
        # Конфигурация поисковых систем
        self.search_engines = {
            'yandex': {
                'url': 'https://yandex.ru/search/',
                'params': {'lr': 213},  # Россия
                'snippet_selector': 'div.TextSnippet',
                'link_selector': 'a[href]',
                'delay': 0.5  # задержка между запросами
            },
            'google': {
                'url': 'https://www.google.com/search?',
                'params': {'hl': 'ru', 'gl': 'ru'},  # русский язык, Россия
                'snippet_selector': 'div.VwiC3b',  # класс для сниппетов
                'link_selector': 'a[href]',
                'delay': 1.0  # Google более строгий к частоте запросов
            },
            'bing': {
                'url': 'https://www.bing.com/search?',
                'params': {'setlang': 'ru-ru'},  # русский язык
                'snippet_selector': 'p',  # общий селектор для сниппетов
                'link_selector': 'a[href]',
                'delay': 0.8
            }
        }
        
        # Расширенный список специализированных словарей
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
            'dic.academic.ru/cdit',  # энциклопедии на academic.ru
            
            # Современные словари сленга и неологизмов
            'newslang.ru',
            'slang.su',
            'russkiymir.ru/slovar',
            
            # Детские словари и образовательные ресурсы
            'deti-mama.ru/slovar',
            'razvitiechild.ru/slovar'
        ]
        
        # Дополнительные стоп-слова для фильтрации
        self.additional_common_words = {
            'был', 'была', 'были', 'будет', 'будут', 'мочь', 'можно', 'нужно',
            'хотеть', 'сказать', 'делать', 'еще', 'уже', 'весь', 'свой',
            'такой', 'иной', 'каждый', 'любой', 'никто', 'ничто', 'всё',
            'сам', 'другой', 'чей', 'твой', 'наш', 'ваш', 'их', 'ее',
            'его', 'её', 'ли', 'же', 'бы', 'ведь', 'вот', 'ну', 'да',
            'нет', 'ага', 'ой', 'ах', 'эй', 'эх', 'упс', 'ойойой'
        }
    
    def search_word_meaning(self, word: str) -> Dict[str, any]:
        """
        Ищет значение слова в интернете через несколько поисковых систем
        Возвращает словарь с объединенными результатами
        """
        all_definitions = []
        all_dict_results = []
        search_queries = []
        
        # Разные варианты поискового запроса
        query_variants = [
            f'значение слова {word}',
            f'что означает слово {word}',
            f'определение слова {word}',
            f'лексическое значение {word}',
            f'{word} значение',
            f'{word} это',
            f'{word} - это',
            f'объяснение слова {word}'
        ]
        
        for engine_name, engine_config in self.search_engines.items():
            for query in query_variants:
                try:
                    # Параметры запроса
                    params = {
                        'text': query if engine_name == 'yandex' else query.replace(' ', '+')
                    }
                    params.update(engine_config['params'])
                    
                    # Выполнение запроса
                    response = requests.get(
                        engine_config['url'], 
                        params=params, 
                        headers=self.headers,
                        timeout=10
                    )
                    response.raise_for_status()
                    
                    # Парсинг результатов
                    soup = BeautifulSoup(response.text, 'html.parser')
                    
                    # Извлечение сниппетов
                    snippets = soup.select(engine_config['snippet_selector'])
                    
                    for snippet in snippets[:5]:  # Берем до 5 результатов с каждой системы
                        text = snippet.get_text().strip()
                        if text and len(text) > 20:  # Фильтр очень коротких результатов
                            # Проверяем, содержит ли текст определение
                            if self._is_definition_text(text, word):
                                all_definitions.append({
                                    'text': text,
                                    'source': engine_name,
                                    'query': query
                                })
                    
                    # Поиск ссылок на словари
                    links = soup.select(engine_config['link_selector'])
                    
                    for link in links[:15]:
                        href = link['href']
                        link_text = link.get_text().strip()
                        
                        # Проверяем, содержит ли ссылка словарь
                        if any(source in href for source in self.dictionary_sources):
                            if link_text and len(link_text) > 5:
                                dict_result = {
                                    'title': link_text,
                                    'url': href,
                                    'source': engine_name,
                                    'query': query
                                }
                                if dict_result not in all_dict_results:  # Уникальность
                                    all_dict_results.append(dict_result)
                                
                                if len(all_dict_results) >= 10:
                                    break
                    
                    # Добавляем информацию о запросе
                    search_queries.append({
                        'engine': engine_name,
                        'query': query,
                        'success': True
                    })
                    
                    # Задержка между запросами для предотвращения блокировки
                    time.sleep(engine_config['delay'])
                    
                    # Ограничиваем количество запросов для производительности
                    if len(all_definitions) >= 15 and len(all_dict_results) >= 8:
                        break
                    
                except requests.RequestException as e:
                    search_queries.append({
                        'engine': engine_name,
                        'query': query,
                        'success': False,
                        'error': str(e)
                    })
                    continue
                
                # Прерываем цикл запросов, если уже получили достаточно результатов
                if len(all_definitions) >= 15 and len(all_dict_results) >= 8:
                    break
            
            # Прерываем цикл поисковых систем, если уже получили достаточно результатов
            if len(all_definitions) >= 15 and len(all_dict_results) >= 8:
                break
        
        # Формируем итоговый результат
        if all_definitions or all_dict_results:
            # Сортируем определения по релевантности (пока простая сортировка)
            sorted_definitions = sorted(
                all_definitions, 
                key=lambda x: self._calculate_relevance(x['text'], word), 
                reverse=True
            )
            
            # Возвращаем топ-5 определений
            top_definitions = [item['text'] for item in sorted_definitions[:5]]
            
            return {
                'word': word,
                'status': 'success',
                'definitions': top_definitions,
                'dictionary_sources': all_dict_results[:8],
                'search_queries': search_queries,
                'total_definitions_found': len(all_definitions),
                'total_dict_sources_found': len(all_dict_results)
            }
        
        return {
            'word': word,
            'status': 'not_found',
            'definitions': [],
            'dictionary_sources': [],
            'search_queries': search_queries,
            'total_definitions_found': 0,
            'total_dict_sources_found': 0,
            'error': 'Определения не найдены в доступных источниках'
        }
    
    def _is_definition_text(self, text: str, word: str) -> bool:
        """
        Проверяет, является ли текст определением слова
        """
        text_lower = text.lower()
        word_lower = word.lower()
        
        # Шаблоны, характерные для определений
        definition_patterns = [
            f'{word_lower} — это',
            f'{word_lower}, это',
            f'слово {word_lower}',
            f'термин {word_lower}',
            f'называется {word_lower}',
            f'именуется {word_lower}',
            'означает',
            'обозначает',
            'значит',
            'подразумевает',
            'определяется как',
            'называют',
            'это когда',
            'это значит',
            'в переводе',
            'по смыслу',
            'в значении',
            'в контексте'
        ]
        
        # Проверяем наличие шаблонов определения
        has_definition_pattern = any(pattern in text_lower for pattern in definition_patterns)
        
        # Проверяем, что текст не является просто упоминанием слова
        # (не состоит только из слова и предлогов/союзов)
        common_words_pattern = r'^(и|в|на|не|а|но|или|да|нет|ну|вот|же|бы|ли|так|тогда|потом|после|до|из|от|с|у|к|до|под|за|над|про|раз|два|три|четыре|пять|шесть|семь|восемь|девять|десять|один|два|три|четыре|пять|шесть|семь|восемь|девять|десять)$'
        words = re.findall(r'[а-яА-ЯёЁ]+', text_lower)
        meaningful_words = [w for w in words if not re.match(common_words_pattern, w)]
        
        # Текст считается определением, если содержит паттерн определения
        # или имеет достаточную длину и разнообразие слов
        return has_definition_pattern or (len(meaningful_words) > 3 and len(set(meaningful_words)) > 2)
    
    def _calculate_relevance(self, text: str, word: str) -> float:
        """
        Рассчитывает релевантность текста как определения слова
        """
        score = 0.0
        text_lower = text.lower()
        word_lower = word.lower()
        
        # Базовые критерии релевантности
        if word_lower in text_lower:
            score += 1.0
        
        # Проверка наличия паттернов определения
        definition_indicators = [
            '— это',
            ', это',
            'означает',
            'обозначает',
            'значит',
            'подразумевает',
            'определяется как',
            'называется',
            'именуется',
            'это когда',
            'в значении',
            'в контексте'
        ]
        
        for indicator in definition_indicators:
            if indicator in text_lower:
                score += 2.0  # Паттерны определения дают высокий вес

        # Штраф за очень короткие тексты
        if len(text) < 50:
            score *= 0.5
        elif len(text) < 100:
            score *= 0.8
        
        # Штраф за слишком длинные тексты (возможно, это не определение, а статья)
        if len(text) > 500:
            score *= 0.7
        
        # Поощрение за упоминание слова в начале текста
        if text_lower.strip().startswith(word_lower):
            score += 1.5
        
        # Поощрение за разнообразие слов (не повторяющиеся слова)
        words = re.findall(r'[а-яА-ЯёЁ]+', text_lower)
        if len(words) > 0:
            uniqueness = len(set(words)) / len(words)
            score *= (0.5 + uniqueness * 0.5)  # от 0.5 до 1.0

        return score
    
    def get_word_from_context(self, text: str) -> List[str]:
        """
        Извлекает потенциально неизвестные слова из контекста
        Возвращает топ-5 слов, исключая общие слова и стоп-слова
        """
        # Объединяем базовые стоп-слова с дополнительными
        all_common_words = {
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
            'вместо', 'несмотря', 'вопреки', 'благодаря', 'согласно', 'согласно', 'вследствие',
            'ввиду', 'по', 'при', 'из-за', 'от', 'до', 'с', 'по', 'из', 'в', 'на', 'с', 'у',
            'к', 'о', 'об', 'от', 'до', 'за', 'из', 'по', 'под', 'про', 'ради', 'сквозь', 'среди'
        }
        all_common_words.update(self.additional_common_words)
        
        # Извлекаем слова (только кириллица, минимум 3 символа)
        words = re.findall(r'[а-яА-ЯёЁ]{3,}', text.lower())
        
        # Фильтруем слова
        filtered_words = []
        for word in words:
            # Исключаем стоп-слова и слишком короткие слова
            if word not in all_common_words and len(word) >= 3:
                # Исключаем числа и слова с цифрами
                if not re.search(r'\d', word):
                    # Исключаем повторяющиеся слова
                    if word not in filtered_words:
                        filtered_words.append(word)
        
        # Возвращаем топ-5 слов
        return filtered_words[:5]

    def lookup(self, word: str) -> Optional[str]:
        """
        Упрощенный интерфейс для получения краткого определения слова
        """
        result = self.search_word_meaning(word)
        
        if result['status'] == 'success' and result['definitions']:
            # Берём первое определение
            definition = result['definitions'][0]
            
            # Очищаем и форматируем определение
            cleaned_definition = self._clean_definition(definition)
            
            # Обрезаем до 2-3 предложений
            sentences = re.split(r'[.!?]', cleaned_definition)
            sentences = [s.strip() for s in sentences if s.strip()]
            
            if len(sentences) > 1:
                short_def = '. '.join(sentences[:2]) + '.'
            else:
                short_def = sentences[0] if sentences else cleaned_definition
            
            return short_def.strip()
            
        return None
    
    def _clean_definition(self, text: str) -> str:
        """
        Очищает текст определения от мусора и лишних символов
        """
        # Удаляем повторяющиеся пробелы
        text = re.sub(r'\s+', ' ', text)
        
        # Удаляем лишние символы в начале и конце
        text = text.strip()
        
        # Удаляем кавычки в начале и конце, если они есть
        if text.startswith(('"', '"', ''', ''')) and text.endswith(('"', '"', ''', ''')):
            text = text[1:-1]
        
        # Удаляем символы, которые могут быть артефактами парсинга
        text = re.sub(r'[\[\]\{\}\(\)]', '', text)
        
        # Удаляем лишние точки
        text = re.sub(r'\.{2,}', '.', text)
        
        return text