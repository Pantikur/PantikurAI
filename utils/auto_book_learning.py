# utils/auto_book_learning.py — Автономное обучение из книг каждый час

import os
import sys
import time
import logging
from pathlib import Path
from datetime import datetime, timedelta
from typing import Optional

# Добавляем корень проекта в путь
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from utils.book_learner import BookLearner

# === Safe print для Windows ===
def safe_print(msg: str):
    """Заменяет эмодзи на ASCII для Windows console"""
    emojis = {
        '📚': '[BOOK]', '🔍': '[SEARCH]', '⬇️': '[DOWN]', '✅': '[OK]',
        '❌': '[ERR]', '💾': '[SAVE]', '📖': '[READ]', '🧠': '[LEARN]',
        '⏳': '[WAIT]', '🚀': '[RUN]', '⚠️': '[WARN]', 'ℹ️': '[INFO]',
        '🕐': '[TIME]', '🔄': '[LOOP]', '🎯': '[TARGET]'
    }
    for e, t in emojis.items():
        msg = msg.replace(e, t)
    print(msg, flush=True)


class AutoBookLearning:
    """
    Автономный цикл обучения из книг.
    Запускается каждый час и собирает новые знания.
    """

    def __init__(
        self,
        interval_hours: int = 1,
        max_books_per_cycle: int = 3,
        topics_per_cycle: int = 2,
        data_dir: str = "data/books"
    ):
        """
        :param interval_hours: Интервал между циклами (часы)
        :param max_books_per_cycle: Максимум книг за один цикл
        :param topics_per_cycle: Сколько тем обрабатывать за цикл
        :param data_dir: Директория для данных
        """
        self.interval_hours = interval_hours
        self.max_books_per_cycle = max_books_per_cycle
        self.topics_per_cycle = topics_per_cycle
        self.data_dir = Path(data_dir)
        
        # Создаём директорию
        self.data_dir.mkdir(parents=True, exist_ok=True)
        
        # Файл состояния
        self.state_file = self.data_dir / "auto_learning_state.json"
        self.state = self._load_state()
        
        # Логгер
        self.log_file = self.data_dir / "auto_learning.log"
        self._setup_logging()
        
        # BookLearner
        self.learner = BookLearner(data_dir=str(data_dir))
        
        # Все темы
        self.all_topics = self.learner.topics
        self.current_topic_index = self.state.get("current_topic_index", 0)
        
        safe_print(f"[🎯] AutoBookLearning инициализирован")
        safe_print(f"   Интервал: {interval_hours} ч.")
        safe_print(f"   Книг за цикл: {max_books_per_cycle}")
        safe_print(f"   Тем за цикл: {topics_per_cycle}")

    def _setup_logging(self):
        """Настраивает логирование."""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s | %(levelname)s | %(message)s',
            handlers=[
                logging.FileHandler(self.log_file, encoding='utf-8'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)

    def _load_state(self) -> dict:
        """Загружает состояние из файла."""
        if self.state_file.exists():
            try:
                import json
                with open(self.state_file, "r", encoding="utf-8") as f:
                    return json.load(f)
            except:
                return {}
        return {}

    def _save_state(self):
        """Сохраняет состояние."""
        import json
        self.state["current_topic_index"] = self.current_topic_index
        self.state["last_update"] = datetime.now().isoformat()
        
        with open(self.state_file, "w", encoding="utf-8") as f:
            json.dump(self.state, f, ensure_ascii=False, indent=2)

    def _get_next_topics(self, count: int) -> list:
        """Получает следующие N тем (циклически)."""
        topics = []
        for i in range(count):
            topic_idx = (self.current_topic_index + i) % len(self.all_topics)
            topics.append(self.all_topics[topic_idx])
        
        # Обновляем индекс
        self.current_topic_index = (self.current_topic_index + count) % len(self.all_topics)
        return topics

    def run_learning_cycle(self) -> bool:
        """
        Запускает один цикл обучения.
        :return: True если успешно
        """
        safe_print(f"\n{'='*60}")
        safe_print(f"[🚀] Запуск цикла обучения: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
        safe_print(f"{'='*60}")
        
        try:
            # Получаем следующие темы
            topics = self._get_next_topics(self.topics_per_cycle)
            safe_print(f"[📚] Темы цикла: {', '.join(topics)}")
            
            # Запускаем обучение
            pairs = self.learner.learn_from_books(
                topics=topics,
                max_books=self.max_books_per_cycle
            )
            
            if pairs:
                # Сохраняем пары
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                output_file = self.data_dir / f"books_cycle_{timestamp}.jsonl"
                self.learner.save_training_pairs(pairs, str(output_file))
                
                # Объединяем с основным файлом
                self._merge_training_pairs(output_file)
                
                # Обновляем состояние
                self.state["last_cycle"] = datetime.now().isoformat()
                self.state["total_cycles"] = self.state.get("total_cycles", 0) + 1
                self.state["total_books"] = self.state.get("total_books", 0) + len(pairs) // 2  # Примерно
                self._save_state()
                
                safe_print(f"[✅] Цикл завершён: {len(pairs)} пар собрано")
                self.logger.info(f"Cycle completed: {len(pairs)} pairs from {len(topics)} topics")
                
                return True
            else:
                safe_print(f"[⚠️] Не удалось собрать пары в этом цикле")
                self.logger.warning("No pairs collected in this cycle")
                return False
                
        except Exception as e:
            safe_print(f"[❌] Ошибка цикла: {e}")
            self.logger.error(f"Cycle error: {e}", exc_info=True)
            return False

    def _merge_training_pairs(self, new_file: Path):
        """Объединяет новые пары с основным файлом."""
        main_file = Path("data/books_training_pairs.jsonl")
        
        if not new_file.exists():
            return
        
        # Читаем новые пары
        new_pairs = []
        with open(new_file, "r", encoding="utf-8") as f:
            for line in f:
                if line.strip():
                    try:
                        new_pairs.append(line.strip())
                    except:
                        continue
        
        if not new_pairs:
            return
        
        # Если главный файл существует, добавляем к нему
        if main_file.exists():
            with open(main_file, "a", encoding="utf-8") as f:
                for pair in new_pairs:
                    f.write(pair + "\n")
            safe_print(f"[💾] Добавлено {len(new_pairs)} пар в {main_file.name}")
        else:
            # Создаём новый файл
            with open(main_file, "w", encoding="utf-8") as f:
                for pair in new_pairs:
                    f.write(pair + "\n")
            safe_print(f"[💾] Создан {main_file.name} с {len(new_pairs)} пар")

    def run_continuous(self):
        """
        Запускает непрерывный цикл обучения.
        Работает 24/7 с заданным интервалом.
        """
        safe_print(f"\n{'='*60}")
        safe_print(f"[🔄] ЗАПУСК НЕПРЕРЫВНОГО ОБУЧЕНИЯ ИЗ КНИГ")
        safe_print(f"[🕐] Интервал: {self.interval_hours} час(ов)")
        safe_print(f"[🎯] Тем всего: {len(self.all_topics)}")
        safe_print(f"{'='*60}\n")
        
        self.logger.info(f"Starting continuous learning: interval={self.interval_hours}h")
        
        cycle_count = 0
        
        while True:
            try:
                # Запускаем цикл
                success = self.run_learning_cycle()
                
                if success:
                    cycle_count += 1
                    safe_print(f"\n[📊] Статистика:")
                    safe_print(f"   Циклов выполнено: {cycle_count}")
                    safe_print(f"   Всего книг: {self.state.get('total_books', 0)}")
                    safe_print(f"   Последнее обновление: {self.state.get('last_cycle', 'Никогда')}")
                
                # Ждём следующий цикл
                next_run = datetime.now() + timedelta(hours=self.interval_hours)
                safe_print(f"\n[⏳] Следующий цикл: {next_run.strftime('%Y-%m-%d %H:%M')}")
                safe_print(f"[🕐] Ожидание {self.interval_hours} час(ов)...\n")
                
                self.logger.info(f"Waiting {self.interval_hours} hours until next cycle")
                
                # Сон в секундах
                time.sleep(self.interval_hours * 3600)
                
            except KeyboardInterrupt:
                safe_print(f"\n[⚠️] Остановка по команде пользователя")
                self.logger.info("Stopped by user")
                break
            except Exception as e:
                safe_print(f"[❌] Критическая ошибка: {e}")
                self.logger.error(f"Critical error: {e}", exc_info=True)
                
                # Ждём 5 минут и пробуем снова
                safe_print(f"[🕐] Перезапуск через 5 минут...")
                time.sleep(300)

    def run_once(self):
        """Запускает один цикл обучения (для тестирования)."""
        safe_print(f"[🎯] Запуск одиночного цикла обучения")
        success = self.run_learning_cycle()
        
        if success:
            safe_print(f"[✅] Одиночный цикл завершён успешно")
            return True
        else:
            safe_print(f"[❌] Одиночный цикл завершён с ошибками")
            return False


def main():
    """Запуск автономного обучения."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Автономное обучение из книг")
    parser.add_argument(
        "--interval", "-i",
        type=int,
        default=1,
        help="Интервал между циклами в часах (по умолчанию: 1)"
    )
    parser.add_argument(
        "--books", "-b",
        type=int,
        default=3,
        help="Максимум книг за цикл (по умолчанию: 3)"
    )
    parser.add_argument(
        "--topics", "-t",
        type=int,
        default=2,
        help="Тем за цикл (по умолчанию: 2)"
    )
    parser.add_argument(
        "--once",
        action="store_true",
        help="Запустить один цикл и выйти (для тестирования)"
    )
    
    args = parser.parse_args()
    
    safe_print(f"[RUN] AutoBookLearning — Автономное обучение из книг")
    print("=" * 60)
    
    # Создаём контроллер
    controller = AutoBookLearning(
        interval_hours=args.interval,
        max_books_per_cycle=args.books,
        topics_per_cycle=args.topics
    )
    
    if args.once:
        # Одиночный запуск
        controller.run_once()
    else:
        # Непрерывный запуск
        controller.run_continuous()


if __name__ == "__main__":
    main()
