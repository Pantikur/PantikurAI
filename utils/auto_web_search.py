# utils/auto_web_search.py
# Автоматический поиск определений слов в интернете
# Запускается раз в час, перебирает все доступные поисковики
# Собирает слова из диалогов, JSON и JSONL файлов

import asyncio
import time
import logging
import os
import re
import json
from typing import Dict, List, Optional, Set
from pathlib import Path

logger = logging.getLogger(__name__)


class AutoWebSearch:
    """
    Автоматический поиск определений слов в интернете.
    
    Работает по следующему алгоритму:
    1. Собирает неизвестные слова из диалогов, JSON и JSONL файлов
    2. Перебирает все доступные поисковики (Yandex, Google, Bing)
    3. Сохраняет найденные определения в knowledge_cache
    4. Запускается циклически с заданным интервалом (по умолчанию 1 час)
    """
    
    def __init__(
        self,
        interval_seconds: int = 3600,  # 1 час
        batch_size: int = 10,  # слов за цикл
        min_word_length: int = 5,  # минимальная длина слова
        cache_file: str = "data/knowledge_cache.json",
        conversations_file: str = "data/conversations.json",
        project_root: str = "."  # Корневая папка проекта
    ):
        self.interval = interval_seconds
        self.batch_size = batch_size
        self.min_word_length = min_word_length
        self.cache_file = cache_file
        self.conversations_file = conversations_file
        self.project_root = project_root
        
        # Экземпляр WebSearch для поиска
        self.web_search = None
        self.knowledge_cache: Dict[str, str] = {}
        
        # История поиска (чтобы не повторяться)
        self.searched_words: Set[str] = set()
        
        # Флаги остановки
        self._running = False
        self._stop_event = asyncio.Event()
        
        logger.info(f"🔍 AutoWebSearch инициализирован:")
        logger.info(f"   ⏱️ Интервал: {interval_seconds // 60} минут")
        logger.info(f"   📝 Пакет: {batch_size} слов")
        logger.info(f"   📄 Кэш: {cache_file}")
    
    def load_knowledge_cache(self):
        """Загружает существующий кэш знаний."""
        if os.path.exists(self.cache_file):
            try:
                with open(self.cache_file, "r", encoding="utf-8") as f:
                    self.knowledge_cache = json.load(f)
                logger.info(f"📚 Загружен knowledge_cache: {len(self.knowledge_cache)} записей")
            except Exception as e:
                logger.warning(f"⚠️ Ошибка загрузки кэша: {e}")
                self.knowledge_cache = {}
        else:
            logger.info(f"ℹ️ knowledge_cache не найден ({self.cache_file}), начнем с пустого кэша")
    
    def save_knowledge_cache(self):
        """Сохраняет кэш знаний в файл."""
        try:
            os.makedirs(os.path.dirname(self.cache_file) or ".", exist_ok=True)
            with open(self.cache_file, "w", encoding="utf-8") as f:
                json.dump(self.knowledge_cache, f, ensure_ascii=False, indent=2)
            logger.info(f"💾 knowledge_cache сохранён: {len(self.knowledge_cache)} записей")
        except Exception as e:
            logger.error(f"❌ Ошибка сохранения кэша: {e}")
    
    def load_conversations(self) -> List[Dict]:
        """Загружает историю диалогов."""
        if os.path.exists(self.conversations_file):
            try:
                with open(self.conversations_file, "r", encoding="utf-8") as f:
                    conversations = json.load(f)
                logger.info(f"📜 Загружено {len(conversations)} диалогов")
                return conversations
            except Exception as e:
                logger.warning(f"⚠️ Ошибка загрузки диалогов: {e}")
        return []
    
    def find_all_json_files(self) -> List[str]:
        """
        Находит все JSON и JSONL файлы в проекте.
        
        Возвращает список путей к файлам.
        """
        json_files = []
        project_path = Path(self.project_root).resolve()
        
        # Проверяем, что путь существует
        if not project_path.exists():
            logger.warning(f"⚠️ Путь проекта не найден: {project_path}")
            return []
        
        # Исключаем папки, которые не содержат полезных данных
        exclude_dirs = {
            'node_modules', '.git', 'venv', '.venv', '__pycache__',
            '.kubernetes', '.docker', '.helm', 'tests', '.vscode',
            '.idea', 'build', 'dist', 'node_modules'
        }
        
        for file_path in project_path.rglob('*'):
            if file_path.is_file() and file_path.suffix.lower() in {'.json', '.jsonl'}:
                # Проверяем, что файл не в исключённых папках
                try:
                    rel_path = file_path.relative_to(project_path)
                    parts = [p for p in rel_path.parts if p not in exclude_dirs]
                    if parts:
                        json_files.append(str(file_path))
                except ValueError:
                    # Файл за пределами проекта (например, системный)
                    pass
        
        logger.info(f"🔍 Найдено {len(json_files)} JSON/JSONL файлов в проекте")
        return json_files
    
    def extract_words_from_text(self, text: str) -> List[str]:
        """
        Извлекает потенциально новые слова из текста.
        
        Правила:
        - Слова с заглавной буквы (кроме местоимений)
        - Минимальная длина: min_word_length
        - Только русские слова
        """
        # Исключения (частые слова с заглавной буквы)
        exclusions = {
            'я', 'ты', 'мы', 'вы', 'он', 'она', 'они', 'оно',
            'это', 'что', 'как', 'сам', 'себя', 'себе', 'сама', 'сами',
            'вас', 'тебя', 'тебе', 'меня', 'мне', 'мной', 'мною',
            'вами', 'тобой', 'тобою', 'да', 'нет',
        }
        
        # Ищем слова с заглавной буквы
        candidates = re.findall(r'\b([А-ЯЁ][а-яё]{' + str(self.min_word_length-1) + r',})', text)
        
        # Фильтруем
        words = []
        for word in candidates:
            word_lower = word.lower()
            if word_lower not in exclusions and len(word) >= self.min_word_length:
                words.append(word)
        
        return words
    
    def extract_words_from_json_file(self, file_path: str) -> List[str]:
        """
        Извлекает слова из JSON или JSONL файла.
        
        Возвращает список слов.
        """
        words = []
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                if file_path.endswith('.jsonl'):
                    # JSONL: каждая строка — отдельный JSON объект
                    for line_num, line in enumerate(f, 1):
                        line = line.strip()
                        if not line:
                            continue
                        try:
                            data = json.loads(line)
                            # Рекурсивно извлекаем текст из объекта
                            texts = self._extract_texts_from_object(data)
                            for text in texts:
                                words.extend(self.extract_words_from_text(text))
                        except json.JSONDecodeError:
                            # Если не JSON, просто извлекаем слова из строки
                            words.extend(self.extract_words_from_text(line))
                else:
                    # JSON: обычный файл
                    data = json.load(f)
                    texts = self._extract_texts_from_object(data)
                    for text in texts:
                        words.extend(self.extract_words_from_text(text))
        except Exception as e:
            logger.warning(f"⚠️ Ошибка чтения файла {file_path}: {e}")
        
        return words
    
    def _extract_texts_from_object(self, obj, depth: int = 0) -> List[str]:
        """
        Рекурсивно извлекает текстовые значения из JSON объекта.
        
        Возвращает список текстовых строк.
        """
        texts = []
        
        if isinstance(obj, str):
            # Проверяем длину текста
            if len(obj) > 2:  # Не извлекаем слишком короткие строки
                texts.append(obj)
        elif isinstance(obj, dict):
            for key, value in obj.items():
                if isinstance(value, (str, dict, list)):
                    texts.extend(self._extract_texts_from_object(value, depth + 1))
        elif isinstance(obj, list):
            for item in obj:
                if isinstance(item, (str, dict, list)):
                    texts.extend(self._extract_texts_from_object(item, depth + 1))
        
        return texts
    
    def extract_new_words(self, conversations, limit: int = 50) -> List[str]:
        """
        Извлекает новые слова из истории диалогов.
        
        Правила:
        - Слова с заглавной буквы (кроме местоимений)
        - Минимальная длина: min_word_length
        - Не повторяются
        - Только русские слова
        
        conversations может быть:
        - List[Dict] — список диалогов
        - Dict — один диалог
        - List[List] — список списков сообщений
        """
        # Исключения (частые слова с заглавной буквы)
        exclusions = {
            'я', 'ты', 'мы', 'вы', 'он', 'она', 'они', 'оно',
            'это', 'что', 'как', 'сам', 'себя', 'себе', 'сама', 'сами',
            'вас', 'тебя', 'тебе', 'меня', 'мне', 'мной', 'мною',
            'вами', 'тобой', 'тобою', 'да', 'нет',
        }
        
        # Собираем все слова из диалогов
        all_words: List[str] = []
        
        # Обработка разных форматов conversations
        if isinstance(conversations, dict):
            # Один диалог
            messages = conversations.get('messages', [])
            if isinstance(messages, list):
                for msg in messages[-10:]:  # Последние 10 сообщений
                    if isinstance(msg, dict):
                        text = msg.get('message', '')
                        if isinstance(text, str):
                            candidates = re.findall(r'\b([А-ЯЁ][а-яё]{' + str(self.min_word_length-1) + r',})', text)
                            all_words.extend(candidates)
        elif isinstance(conversations, list):
            # Список диалогов или список списков
            for conv in conversations[:20]:  # Берем последние 20 диалогов
                if isinstance(conv, dict):
                    # Формат: [{"messages": [...], ...}, ...]
                    messages = conv.get('messages', [])
                    if isinstance(messages, list):
                        for msg in messages[-10:]:  # Последние 10 сообщений
                            if isinstance(msg, dict):
                                text = msg.get('message', '')
                                if isinstance(text, str):
                                    candidates = re.findall(r'\b([А-ЯЁ][а-яё]{' + str(self.min_word_length-1) + r',})', text)
                                    all_words.extend(candidates)
                elif isinstance(conv, list):
                    # Формат: [[{"message": ...}, ...], ...]
                    for msg in conv[-10:]:
                        if isinstance(msg, dict):
                            text = msg.get('message', '')
                            if isinstance(text, str):
                                candidates = re.findall(r'\b([А-ЯЁ][а-яё]{' + str(self.min_word_length-1) + r',})', text)
                                all_words.extend(candidates)
        
        # Фильтруем и убираем дубликаты
        unique_words = []
        seen = set()
        for word in all_words:
            word_lower = word.lower()
            if word_lower not in exclusions and word_lower not in seen:
                # Проверяем, что слово еще не в кэше
                if word_lower not in self.knowledge_cache:
                    seen.add(word_lower)
                    unique_words.append(word)
        
        logger.debug(f"🔍 Извлечено {len(unique_words)} новых слов из диалогов")
        return unique_words[:limit]
    
    def collect_words_to_search(self) -> List[str]:
        """
        Собирает слова для поиска из всех источников.
        
        Алгоритм:
        1. Загружаем диалоги
        2. Извлекаем новые слова из диалогов
        3. Загружаем все JSON/JSONL файлы
        4. Извлекаем новые слова из файлов
        5. Объединяем результаты
        6. Фильтруем уже искавшиеся
        7. Возвращаем пакет для поиска
        """
        all_new_words: List[str] = []
        seen_words: Set[str] = set()
        
        # 1. Извлекаем слова из диалогов
        conversations = self.load_conversations()
        dialog_words = self.extract_new_words(conversations, limit=self.batch_size * 2)
        
        for word in dialog_words:
            word_lower = word.lower()
            if word_lower not in self.searched_words and word_lower not in seen_words:
                seen_words.add(word_lower)
                all_new_words.append(word)
        
        # 2. Извлекаем слова из всех JSON/JSONL файлов
        json_files = self.find_all_json_files()
        
        for file_path in json_files:
            try:
                file_words = self.extract_words_from_json_file(file_path)
                
                for word in file_words:
                    word_lower = word.lower()
                    # Фильтруем: не в кэше, не в searched, не дубликаты
                    if (word_lower not in self.knowledge_cache and
                        word_lower not in self.searched_words and
                        word_lower not in seen_words):
                        seen_words.add(word_lower)
                        all_new_words.append(word)
                
                # Ограничиваем общее количество слов
                if len(all_new_words) >= self.batch_size * 2:
                    break
                    
            except Exception as e:
                logger.warning(f"⚠️ Ошибка обработки файла {file_path}: {e}")
        
        # 3. Фильтруем уже искавшиеся
        words_to_search = [
            word for word in all_new_words
            if word.lower() not in self.searched_words
        ]
        
        # 4. Ограничиваем размер пакета
        words_to_search = words_to_search[:self.batch_size]
        
        if words_to_search:
            logger.info(f"📝 Подготовлено {len(words_to_search)} слов для поиска: {words_to_search[:5]}...")
        else:
            logger.info("ℹ️ Нет новых слов для поиска")
        
        return words_to_search
    
    def search_word(self, word: str) -> Optional[str]:
        """
        Ищет определение слова через все доступные поисковики.
        
        Возвращает:
        - Строку с определением, если найдено
        - None, если не найдено
        """
        if not self.web_search:
            logger.warning("⚠️ WebSearch не инициализирован")
            return None
        
        word_lower = word.lower()  # ✅ Определяем сразу
        
        try:
            # Ищем в кэше
            if word_lower in self.knowledge_cache:
                return self.knowledge_cache[word_lower]
            
            # Ищем через web_search
            result = self.web_search.lookup(
                word,
                timeout=5.0,  # Увеличенный таймаут для thorough поиска
                knowledge_cache=self.knowledge_cache,
                save_knowledge_cache_func=self.save_knowledge_cache
            )
            
            if result and result != "Слово не найдено в словаре.":
                self.searched_words.add(word_lower)
                logger.info(f"✅ Найдено определение для '{word}': {result[:50]}...")
                return result
            else:
                logger.debug(f"❌ Не найдено определение для '{word}'")
                self.searched_words.add(word_lower)
                return None
                
        except Exception as e:
            logger.error(f"❌ Ошибка поиска '{word}': {e}")
            self.searched_words.add(word_lower)
            return None
    
    def search_batch(self, words: List[str]) -> Dict[str, Optional[str]]:
        """
        Ищет определения для пакета слов.
        
        Возвращает словарь: слово -> определение
        """
        results = {}
        logger.info(f"🔍 Начало поиска {len(words)} слов...")
        
        for i, word in enumerate(words, 1):
            logger.info(f"   [{i}/{len(words)}] Ищу '{word}'...")
            result = self.search_word(word)
            results[word] = result
            
            # Пауза между поисками (чтобы не перегружать сервер)
            if i < len(words):
                time.sleep(1)
        
        # Подсчет результатов
        found_count = sum(1 for r in results.values() if r)
        logger.info(f"✅ Поиск завершен: найдено {found_count}/{len(words)} определений")
        
        return results
    
    def run_once(self):
        """Выполняет один цикл поиска."""
        logger.info("🔄 Запуск цикла автопоиска слов...")
        
        try:
            # Собираем слова для поиска
            words = self.collect_words_to_search()
            
            if not words:
                logger.info("ℹ️ Нет слов для поиска, пропускаем цикл")
                return
            
            # Ищем определения
            results = self.search_batch(words)
            
            # Сохраняем результаты
            self.save_knowledge_cache()
            
            # Логирование итогов
            found = [w for w, r in results.items() if r]
            not_found = [w for w, r in results.items() if not r]
            
            logger.info(f"📊 Итоги цикла:")
            logger.info(f"   ✅ Найдено: {len(found)} слов")
            if found:
                for word in found[:3]:
                    result_text = results.get(word, "")
                    if result_text:
                        logger.info(f"      - {word}: {result_text[:50]}...")
            
            if not_found:
                logger.info(f"   ❌ Не найдено: {len(not_found)} слов")
                if len(not_found) <= 5:
                    logger.info(f"      - {', '.join(not_found)}")
        
        except Exception as e:
            logger.error(f"❌ Ошибка цикла автопоиска: {e}", exc_info=True)
    
    def run_continuous(self):
        """
        Запускает непрерывный цикл поиска.
        
        Работает до получения сигнала остановки.
        """
        self._running = True
        logger.info("🚀 Запуск непрерывного автопоиска слов...")
        
        # Загружаем кэш
        self.load_knowledge_cache()
        
        cycle_count = 0
        while self._running:
            cycle_count += 1
            logger.info(f"🔄 Цикл #{cycle_count}")
            
            try:
                self.run_once()
            except Exception as e:
                logger.error(f"❌ Ошибка в цикле #{cycle_count}: {e}", exc_info=True)
            
            # Ждем до следующего цикла
            logger.info(f"⏱️ Следующий цикл через {self.interval // 60} минут...")
            time.sleep(self.interval)
        
        logger.info("🛑 Автопоиск остановлен")
    
    def stop(self):
        """Останавливает автопоиск."""
        self._running = False
        self._stop_event.set()
        logger.info("🛑 Запрошена остановка автопоиска")
    
    async def run_async(self):
        """Асинхронная обертка для запуска."""
        await asyncio.to_thread(self.run_continuous)


# === Пример использования ===
if __name__ == "__main__":
    # Настройка логирования
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s | %(levelname)s | %(name)s | %(message)s"
    )
    
    # Создаем контроллер
    controller = AutoWebSearch(
        interval_seconds=60,  # 1 минута для теста
        batch_size=5,
        min_word_length=5
    )
    
    # Запускаем один цикл
    controller.run_once()
    
    # Или непрерывный режим
    # controller.run_continuous()
