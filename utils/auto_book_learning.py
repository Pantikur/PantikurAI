# utils/auto_book_learning.py — Автономное обучение из книг каждый час

import os
import sys
import time
import subprocess
import logging
import json
from pathlib import Path
from datetime import datetime, timedelta
from typing import Optional

# Принудительный UTF-8 для Windows
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

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
        '🕐': '[TIME]', '🔄': '[LOOP]', '🎯': '[TARGET]', '⏱️': '[TIMER]',
        '📊': '[STATS]', '📈': '[CHART]', '🛑': '[STOP]', '🎉': '[DONE]'
    }
    for e, t in emojis.items():
        msg = msg.replace(e, t)
    print(msg, flush=True)


class AutoBookLearning:
    """
    Автономный цикл обучения из книг.
    Работает циклами: 10 минут чтение + обучение.
    """

    def __init__(
        self,
        cycle_minutes: int = 10,  # Длительность цикла чтения
        max_books_per_cycle: int = 5,  # Максимум книг за цикл
        topics_per_cycle: int = 2,  # Тем за цикл
        data_dir: str = "data/books"
    ):
        """
        :param cycle_minutes: Длительность цикла чтения (минуты)
        :param max_books_per_cycle: Максимум книг за один цикл
        :param topics_per_cycle: Сколько тем обрабатывать за цикл
        :param data_dir: Директория для данных
        """
        self.cycle_minutes = cycle_minutes
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
        safe_print(f"   ⏱️ Цикл: {cycle_minutes} минут")
        safe_print(f"   📚 Книг за цикл: {max_books_per_cycle}")
        safe_print(f"   🎯 Тем за цикл: {topics_per_cycle}")

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
        """Получает следующие N тем (циклически) — русские названия."""
        # Русскоязычные темы для Author.Today
        ru_topics = [
            "фэнтези",
            "попаданцы",
            "фантастика",
            "мистика",
            "детектив",
            "приключения",
            "психология",
            "философия",
            "современная проза",
            "боевое фэнтези",
            "городское фэнтези",
            "научная фантастика",
            "альтернативная история",
            "литрпг",
            "ужасы",
            "романтика",
            "драма",
            "любовное фэнтези",
            "историческое фэнтези",
            "молодежная проза",
        ]
        
        topics = []
        for i in range(count):
            topic_idx = (self.current_topic_index + i) % len(ru_topics)
            topics.append(ru_topics[topic_idx])
        
        # Обновляем индекс
        self.current_topic_index = (self.current_topic_index + count) % len(ru_topics)
        return topics

    def run_learning_cycle(self) -> bool:
        """
        Запускает один цикл обучения (10 минут чтение + обработка).
        :return: True если успешно
        """
        safe_print(f"\n{'='*60}")
        safe_print(f"[🚀] Запуск цикла обучения: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
        safe_print(f"[⏱️] Длительность цикла: {self.cycle_minutes} минут")
        safe_print(f"{'='*60}")
        
        try:
            # Получаем следующие темы
            topics = self._get_next_topics(self.topics_per_cycle)
            safe_print(f"[📚] Темы цикла: {', '.join(topics)}")
            
            # Запускаем обучение из ВСЕХ русскоязычных источников
            from utils.book_learner import BookLearner
            from utils.author_today_parser import AuthorTodayParser
            from utils.selenium_parser import SeleniumBookParser
            # from utils.litnet_parser import LitnetParser  # Litnet требует авторизацию
            
            learner = BookLearner(data_dir=str(self.data_dir))
            at_parser = AuthorTodayParser(data_dir=str(self.data_dir))
            selenium_parser = SeleniumBookParser(data_dir=str(self.data_dir), headless=True)
            # litnet_parser = LitnetParser(data_dir=str(self.data_dir), headless=True)  # Отключен
            
            all_pairs = []
            
            # 1. Author.Today (описания книг) — быстро, без JS
            safe_print("\n[📚] Источник 1: Author.Today (описания)")
            try:
                at_pairs = at_parser.learn_from_author_today(
                    genres=topics,
                    max_books=self.max_books_per_cycle // 2  # Половина
                )
                all_pairs.extend(at_pairs)
                safe_print(f"   [✅] Author.Today: {len(at_pairs)} пар")
            except Exception as e:
                safe_print(f"   [⚠️] Author.Today ошибка: {e}")
            
            # 2. Selenium: Стихи.ру, Проза.ру, RuLit, LiveLib (полные тексты)
            safe_print("\n[📚] Источник 2: JavaScript сайты (Selenium)")
            try:
                selenium_pairs = selenium_parser.learn_from_all_sources(
                    max_books=self.max_books_per_cycle // 2  # Вторая половина
                )
                all_pairs.extend(selenium_pairs)
                safe_print(f"   [✅] JavaScript сайты: {len(selenium_pairs)} пар")
            except Exception as e:
                safe_print(f"   [⚠️] Selenium ошибка: {e}")
            finally:
                selenium_parser.close_driver()
            
            # 3. Litnet — отключен (требует авторизацию/защита от ботов)
            # safe_print("\n[📚] Источник 3: Litnet (полные тексты)")
            # try:
            #     litnet_pairs = litnet_parser.learn_from_litnet(max_books=5)
            #     all_pairs.extend(litnet_pairs)
            #     safe_print(f"   [✅] Litnet: {len(litnet_pairs)} пар")
            # except Exception as e:
            #     safe_print(f"   [⚠️] Litnet ошибка: {e}")
            # finally:
            #     litnet_parser.close_driver()
            
            if all_pairs:
                # Сохраняем пары
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                output_file = self.data_dir / f"books_cycle_{timestamp}.jsonl"
                learner.save_training_pairs(all_pairs, str(output_file))
                
                # Объединяем с основным файлом
                self._merge_training_pairs(output_file)
                
                # Обновляем состояние
                self.state["last_cycle"] = datetime.now().isoformat()
                self.state["total_cycles"] = self.state.get("total_cycles", 0) + 1
                self.state["total_pairs"] = self.state.get("total_pairs", 0) + len(all_pairs)
                self._save_state()
                
                safe_print(f"[✅] Цикл завершён: {len(all_pairs)} пар собрано")
                self.logger.info(f"Cycle completed: {len(all_pairs)} pairs")
                
                # Ханано: АВТОМАТИЧЕСКОЕ ПЕРЕОБУЧЕНИЕ МОДЕЛИ
                # Каждые 5 циклов запускаем переобучение
                if self.state["total_cycles"] % 5 == 0:
                    safe_print(f"\n[🧠] Ханано: Каждые 5 циклов — переобучение модели")
                    self._run_model_retrain()
                
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

    def _run_model_retrain(self):
        """
        Запускает переобучение модели после сбора данных.
        Ханako сама обучает модель без напоминаний.
        """
        try:
            project_root = Path(__file__).resolve().parent.parent
            retrain_script = project_root / "retrain.py"
            
            if not retrain_script.exists():
                safe_print(f"[⚠️] retrain.py не найден — пропуск обучения")
                return False
            
            safe_print(f"\n[🧠] Ханано: Запуск переобучения модели...")
            safe_print(f"[📚] Данных для обучения: {self.state.get('total_pairs', 0)} пар")
            
            # Запускаем retrain.py
            result = subprocess.run(
                [sys.executable, str(retrain_script), "--books"],
                cwd=str(project_root),
                capture_output=True,
                text=True,
                timeout=1800  # 30 минут на обучение
            )
            
            if result.returncode == 0:
                safe_print(f"[✅] Модель успешно переобучена!")
                self.state["last_retrain"] = datetime.now().isoformat()
                self.state["total_retrains"] = self.state.get("total_retrains", 0) + 1
                self._save_state()
                return True
            else:
                safe_print(f"[⚠️] Ошибка переобучения (продолжаем работу)")
                self.logger.warning(f"Retrain failed: {result.stderr[:200]}")
                return False
                
        except subprocess.TimeoutExpired:
            safe_print(f"[⏰] Таймаут переобучения (30 мин) — модель работает со старыми весами")
            return False
        except Exception as e:
            safe_print(f"[⚠️] Ошибка запуска обучения: {e}")
            self.logger.error(f"Retrain error: {e}", exc_info=True)
            return False

    def run_continuous(self):
        """
        Запускает непрерывный цикл обучения.
        Цикл: 10 минут чтение + обучение → пауза 10 минут → повтор.
        """
        safe_print(f"\n{'='*60}")
        safe_print(f"[🔄] ЗАПУСК НЕПРЕРЫВНОГО ОБУЧЕНИЯ ИЗ КНИГ")
        safe_print(f"[⏱️] Цикл: {self.cycle_minutes} минут чтение + обучение")
        safe_print(f"[📚] Источники: Author.Today (русскоязычные)")
        safe_print(f"[🎯] Тем всего: {len(self.all_topics)}")
        safe_print(f"{'='*60}\n")
        
        self.logger.info(f"Starting continuous learning: cycle={self.cycle_minutes}min")
        
        cycle_count = 0
        
        while True:
            try:
                # Запускаем цикл чтения + обучения
                safe_print(f"\n[📖] НАЧАЛО ЦИКЛА #{cycle_count + 1}")
                success = self.run_learning_cycle()
                
                if success:
                    cycle_count += 1
                    safe_print(f"\n[📊] Статистика:")
                    safe_print(f"   Циклов выполнено: {cycle_count}")
                    safe_print(f"   Всего пар: {self.state.get('total_pairs', 0)}")
                    safe_print(f"   Последнее обновление: {self.state.get('last_cycle', 'Никогда')}")
                
                # Пауза между циклами (10 минут)
                next_run = datetime.now() + timedelta(minutes=self.cycle_minutes)
                safe_print(f"\n[⏳] Следующий цикл: {next_run.strftime('%Y-%m-%d %H:%M')}")
                safe_print(f"[🕐] Ожидание {self.cycle_minutes} минут...\n")
                
                self.logger.info(f"Waiting {self.cycle_minutes} minutes until next cycle")
                
                # Сон в секундах
                time.sleep(self.cycle_minutes * 60)
                
            except KeyboardInterrupt:
                safe_print(f"\n[⚠️] Остановка по команде пользователя")
                self.logger.info("Stopped by user")
                break
            except Exception as e:
                safe_print(f"[❌] Критическая ошибка: {e}")
                self.logger.error(f"Critical error: {e}", exc_info=True)
                
                # Ждём 2 минуты и пробуем снова
                safe_print(f"[🕐] Перезапуск через 2 минуты...")
                time.sleep(120)

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
    
    parser = argparse.ArgumentParser(description="Автономное обучение из книг (русскоязычные)")
    parser.add_argument(
        "--cycle", "-c",
        type=int,
        default=10,
        help="Длительность цикла в минутах (по умолчанию: 10)"
    )
    parser.add_argument(
        "--books", "-b",
        type=int,
        default=5,
        help="Максимум книг за цикл (по умолчанию: 5)"
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
    safe_print(f"[📚] Источник: Author.Today (русскоязычные бесплатные книги)")
    print("=" * 60)
    
    # Создаём контроллер
    controller = AutoBookLearning(
        cycle_minutes=args.cycle,
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
