# utils/auto_web_search.py
# Автоматический поиск определений слов в интернете
# Запускается в фоне на TimeWeb, ищет определения + извлекает новые слова из них

import asyncio
import time
import logging
import os
import re
import json
from typing import Dict, List, Optional, Set
from pathlib import Path
from collections import deque
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from Wuglarst.src.web_search import WebSearch  # type: ignore

logger = logging.getLogger(__name__)


# ==================== ИЗВЛЕЧЕНИЕ СЛОВ ИЗ ТЕКСТА ====================

# Слова, которые НЕ стоит добавлять (только явные символы-разделители)
ONLY_EXCLUDE = {
    '...', '..', '—', '–',
}


def extract_words_from_text(text: str, min_length: int = 2, max_per_text: int = 10) -> List[str]:
    """
    Извлекает ВСЕ слова из текста определения, включая:
    - Существительные, глаголы, прилагательные
    - Предлоги, союзы, местоимения
    - Служебные слова
    
    Это нужно, чтобы бот понимал НЕ ТОЛЬКО значения слов,
    но и грамматику, синтаксис, структуру предложений.
    """
    # Убираем кавычки, тире и другие символы-разделители
    cleaned = re.sub(r'[—–"\']', ' ', text)
    
    # Извлекаем все слова длиной >= min_length
    words = re.findall(r'\b([а-яА-ЯёЁ]{2,})\b', cleaned)
    
    if not words:
        return []
    
    # Нормализуем и фильтруем
    seen = set()
    result = []
    
    for w in words:
        w_lower = w.lower()
        
        # Пропускаем дубликаты
        if w_lower in seen:
            continue
        
        # Пропускаем только явные символы-разделители
        if w_lower in ONLY_EXCLUDE:
            continue
        
        seen.add(w_lower)
        result.append(w)
        
        if len(result) >= max_per_text:
            break
    
    return result


class AutoWebSearch:
    """
    Автоматический поиск определений слов в интернете.
    
    Работает по следующему алгоритму:
    1. Загружает все слова из базы знаний (learned_words.json)
    2. Для каждого слова ищет определение через WebSearch
    3. Извлекает ВСЕ слова из определений (включая предлоги, союзы, местоимения)
    4. Добавляет новые слова в очередь на обработку
    5. Повторяет для всех найденных слов (с ограничением глубины)
    6. Сохраняет найденные определения в knowledge_cache
    7. Запускается циклически с заданным интервалом
    """
    
    def __init__(
        self,
        interval_seconds: int = 3600,  # 1 час
        batch_size: int = 10,  # слов за цикл (для старых методов)
        min_word_length: int = 2,  # минимальная длина слова
        extract_depth: int = 1,  # глубина извлечения слов из определений
        max_new_words_per_def: int = 10,  # макс новых слов из одного определения
        cache_file: str = "data/knowledge_cache.json",
        learned_words_file: str = "data/knowledge/learned_words.json",
        knowledge_stats_file: str = "data/knowledge/knowledge_stats.json",
        project_root: str = "."
    ):
        self.interval = interval_seconds
        self.batch_size = batch_size
        self.min_word_length = min_word_length
        self.extract_depth = extract_depth
        self.max_new_words_per_def = max_new_words_per_def
        self.cache_file = cache_file
        self.learned_words_file = learned_words_file
        self.knowledge_stats_file = knowledge_stats_file
        self.project_root = project_root
        
        # Экземпляр WebSearch для поиска
        self.web_search: Optional["WebSearch"] = None
        
        # Кэш знаний (слово -> определение)
        self.knowledge_cache: Dict[str, str] = {}
        
        # База знаний (все слова)
        self.words_db: List[Dict] = []
        
        # История поиска (чтобы не повторяться)
        self.searched_words: Set[str] = set()
        
        # Флаги остановки
        self._running = False
        self._stop_event = asyncio.Event()
        
        logger.info(f"🔍 AutoWebSearch инициализирован:")
        logger.info(f"   ⏱️ Интервал: {interval_seconds // 60} минут")
        logger.info(f"   📝 Пакет: {batch_size} слов")
        logger.info(f"   🔍 Глубина извлечения: {extract_depth}")
        logger.info(f"   📄 Кэш: {cache_file}")
        logger.info(f"   📚 База знаний: {learned_words_file}")
    
    def load_knowledge_cache(self):
        """Загружает существующий кэш знаний."""
        cache_path = Path(self.project_root) / self.cache_file
        if cache_path.exists():
            try:
                with open(cache_path, "r", encoding="utf-8") as f:
                    self.knowledge_cache = json.load(f)
                logger.info(f"📚 Загружен knowledge_cache: {len(self.knowledge_cache)} записей")
            except Exception as e:
                logger.warning(f"⚠️ Ошибка загрузки кэша: {e}")
                self.knowledge_cache = {}
        else:
            logger.info(f"ℹ️ knowledge_cache не найден, начнем с пустого кэша")
    
    def save_knowledge_cache(self):
        """Сохраняет кэш знаний в файл."""
        try:
            cache_path = Path(self.project_root) / self.cache_file
            cache_path.parent.mkdir(parents=True, exist_ok=True)
            with open(cache_path, "w", encoding="utf-8") as f:
                json.dump(self.knowledge_cache, f, ensure_ascii=False, indent=2)
            logger.info(f"💾 knowledge_cache сохранён: {len(self.knowledge_cache)} записей")
        except Exception as e:
            logger.error(f"❌ Ошибка сохранения кэша: {e}")
    
    def load_words_db(self) -> List[Dict]:
        """Загружает базу знаний (learned_words.json)."""
        words_path = Path(self.project_root) / self.learned_words_file
        if words_path.exists():
            try:
                with open(words_path, "r", encoding="utf-8") as f:
                    self.words_db = json.load(f)
                logger.info(f"📚 Загружена база знаний: {len(self.words_db)} слов")
                return self.words_db
            except Exception as e:
                logger.warning(f"⚠️ Ошибка загрузки базы знаний: {e}")
                self.words_db = []
        else:
            logger.info(f"ℹ️ База знаний не найдена, начнем с пустой")
            self.words_db = []
        
        return self.words_db
    
    def save_words_db(self):
        """Сохраняет базу знаний."""
        try:
            words_path = Path(self.project_root) / self.learned_words_file
            words_path.parent.mkdir(parents=True, exist_ok=True)
            with open(words_path, "w", encoding="utf-8") as f:
                json.dump(self.words_db, f, ensure_ascii=False, indent=2)
            logger.info(f"💾 База знаний сохранена: {len(self.words_db)} слов")
        except Exception as e:
            logger.error(f"❌ Ошибка сохранения базы знаний: {e}")
    
    def extract_new_words_from_definition(self, definition: str, source_word: str, 
                                          current_depth: int, processed_words: Set[str],
                                          queue_words: Set[str]) -> List[str]:
        """
        Извлекает новые слова из определения и добавляет их в базу знаний.
        
        Правила:
        - Извлекаем ВСЕ слова (включая предлоги, союзы, местоимения)
        - Исключаем уже обработанные и слова в очереди
        - Добавляем в базу знаний с глубиной current_depth + 1
        
        Возвращает список извлечённых слов.
        """
        if current_depth >= self.extract_depth:
            return []
        
        new_words = extract_words_from_text(
            definition,
            min_length=self.min_word_length,
            max_per_text=self.max_new_words_per_def
        )
        
        extracted = []
        for nw in new_words:
            nw_lower = nw.lower()
            
            # Пропускаем если:
            # - уже в processed_words
            # - уже в queue_words
            # - уже в базе знаний
            if nw_lower in processed_words:
                continue
            if nw_lower in queue_words:
                continue
            if nw_lower in {w["word"].lower() for w in self.words_db}:
                continue
            
            # Добавляем в базу знаний
            new_word_data = {
                "word": nw,
                "depth": current_depth + 1,
                "extracted_from": source_word,
                "definition": "",
                "difficulty_level": "medium",
                "usage_count": 0,
            }
            
            self.words_db.append(new_word_data)
            extracted.append(nw)
        
        if extracted:
            logger.info(f"  [EXTRACT] Из '{source_word}' (глубина {current_depth}) извлечено {len(extracted)} слов: {', '.join(extracted[:5])}...")
        
        return extracted
    
    def search_word(self, word: str) -> Optional[str]:
        """
        Ищет определение слова через WebSearch.
        
        Возвращает:
        - Строку с определением, если найдено
        - None, если не найдено
        """
        if not self.web_search:
            logger.warning("⚠️ WebSearch не инициализирован")
            return None
        
        word_lower = word.lower()
        
        try:
            # Ищем в кэше
            if word_lower in self.knowledge_cache:
                return self.knowledge_cache[word_lower]
            
            # Ищем через web_search
            result = self.web_search.lookup(
                word,
                timeout=5.0,
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
    
    def run_once(self):
        """Выполняет один цикл поиска с рекурсивным извлечением слов."""
        logger.info("🔄 Запуск цикла автопоиска слов...")
        
        try:
            # Загружаем базу знаний
            self.load_words_db()
            self.load_knowledge_cache()
            
            if not self.words_db:
                logger.info("ℹ️ База знаний пуста, пропускаем цикл")
                return
            
            # Очередь на обработку
            processing_queue = deque()
            
            # Добавляем все слова без определений
            for word_data in self.words_db:
                word = word_data.get("word", "")
                if not word_data.get("definition", ""):
                    processing_queue.append(word_data)
            
            processed_words = set()
            extracted_new_words = set()
            newly_added_words = []
            
            found_count = 0
            error_count = 0
            
            # Обрабатываем очередь
            while processing_queue:
                word_data = processing_queue.popleft()
                word = word_data["word"]
                word_lower = word.lower()
                
                # Пропускаем уже обработанные
                if word_lower in processed_words:
                    continue
                processed_words.add(word_lower)
                
                # Определяем глубину
                word_depth = word_data.get("depth", 0) or 0
                
                # Ищем определение
                definition = self.search_word(word)
                
                if definition:
                    word_data["definition"] = definition
                    word_data["updated_at"] = time.strftime("%Y-%m-%d %H:%M:%S")
                    word_data["source"] = "auto_web_search"
                    found_count += 1
                    
                    # Извлекаем новые слова из определения
                    extracted = self.extract_new_words_from_definition(
                        definition, word, word_depth,
                        processed_words, extracted_new_words
                    )
                    newly_added_words.extend(extracted)
                    
                    # Добавляем новые слова в очередь
                    for new_word in extracted:
                        new_word_lower = new_word.lower()
                        # Находим соответствующий элемент в words_db
                        for wd in self.words_db:
                            if wd["word"].lower() == new_word_lower:
                                processing_queue.append(wd)
                                break
                    
                    # Сохраняем в кэш
                    self.knowledge_cache[word_lower] = definition
                    
                    logger.info(f"[{word_depth}] {word}: ✅ найдено")
                else:
                    error_count += 1
                    logger.info(f"[{word_depth}] {word}: ❌ не найдено")
                
                # Пауза между поисками
                time.sleep(1)
            
            # Сохраняем результаты
            self.save_words_db()
            self.save_knowledge_cache()
            
            # Итоги
            logger.info(f"📊 Итоги цикла:")
            logger.info(f"   ✅ Найдено определений: {found_count}")
            logger.info(f"   ❌ Не найдено: {error_count}")
            logger.info(f"   📚 Всего слов в базе: {len(self.words_db)}")
            logger.info(f"   🆕 Извлечено новых слов: {len(newly_added_words)}")
            
            if newly_added_words:
                logger.info(f"   📝 Новые слова: {', '.join(newly_added_words[:10])}...")
        
        except Exception as e:
            logger.error(f"❌ Ошибка цикла автопоиска: {e}", exc_info=True)
    
    def run_continuous(self):
        """
        Запускает непрерывный цикл поиска.
        
        Работает до получения сигнала остановки.
        """
        self._running = True
        logger.info("🚀 Запуск непрерывного автопоиска слов...")
        
        # Загружаем кэш и базу
        self.load_knowledge_cache()
        self.load_words_db()
        
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
        batch_size=10,
        min_word_length=2,
        extract_depth=1,
        max_new_words_per_def=10
    )
    
    # Запускаем один цикл
    controller.run_once()
    
    # Или непрерывный режим
    # controller.run_continuous()
