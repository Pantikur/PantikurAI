# auto_learn_cycle.py — автоматический цикл обучения

"""
Автоматический цикл обучения чат-бота:
1. Обновляет систему знаний
2. Запускает дообучение модели
3. Повторяет цикл
"""

import os
import sys
import time
import subprocess
import logging
from datetime import datetime

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('auto_learn.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Пути к скриптам
UPDATE_SCRIPT = "update_knowledge.py"
RETRAIN_SCRIPT = "retrain.py"

# Параметры цикла
CHECK_INTERVAL = 300  # Проверять каждые 5 минут (300 секунд)
MIN_WORDS_FOR_RETRAIN = 5  # Минимальное количество новых слов для дообучения

# Статус файл для отслеживания последнего дообучения
STATUS_FILE = "data/knowledge/learning_status.json"


def load_status():
    """Загружает статус из файла"""
    if os.path.exists(STATUS_FILE):
        try:
            with open(STATUS_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            logger.warning(f"Не удалось загрузить статус: {e}")
    return {
        "last_check": None,
        "last_retrain": None,
        "total_retrains": 0,
        "words_learned": 0
    }


def save_status(status):
    """Сохраняет статус в файл"""
    os.makedirs(os.path.dirname(STATUS_FILE), exist_ok=True)
    try:
        with open(STATUS_FILE, 'w', encoding='utf-8') as f:
            json.dump(status, f, ensure_ascii=False, indent=2, default=str)
    except Exception as e:
        logger.error(f"Не удалось сохранить статус: {e}")


def run_script(script_name, timeout=300):
    """Запускает скрипт и возвращает результат"""
    try:
        logger.info(f"Запуск скрипта: {script_name}")
        result = subprocess.run(
            [sys.executable, script_name],
            capture_output=True,
            text=True,
            timeout=timeout,
            encoding='utf-8'
        )
        
        if result.returncode == 0:
            logger.info(f"✅ Скрипт {script_name} успешно выполнен")
            return True, result.stdout
        else:
            logger.error(f"❌ Ошибка выполнения {script_name}")
            logger.error(f"STDOUT: {result.stdout}")
            logger.error(f"STDERR: {result.stderr}")
            return False, result.stderr
            
    except subprocess.TimeoutExpired:
        logger.error(f"⏰ Таймаут при выполнении {script_name}")
        return False, "Timeout"
    except Exception as e:
        logger.error(f"❌ Исключение при выполнении {script_name}: {e}")
        return False, str(e)


def get_word_count():
    """Получает количество выученных слов"""
    try:
        from knowledge_manager import KnowledgeManager
        km = KnowledgeManager("data/knowledge")
        stats = km.get_stats()
        return stats.get('total_words', 0)
    except Exception as e:
        logger.error(f"Не удалось получить количество слов: {e}")
        return 0


def print_cycle_report():
    """Печатает отчет о цикле обучения"""
    try:
        from knowledge_manager import KnowledgeManager
        km = KnowledgeManager("data/knowledge")
        km.print_report()
        
        status = load_status()
        print(f"\n🔄 Статус цикла обучения:")
        print(f"Последняя проверка: {status.get('last_check', 'Нет данных')}")
        print(f"Последнее дообучение: {status.get('last_retrain', 'Нет данных')}")
        print(f"Всего дообучений: {status.get('total_retrains', 0)}")
        
    except Exception as e:
        logger.error(f"Не удалось напечатать отчет: {e}")


def main():
    """Основной цикл обучения"""
    logger.info("🚀 Запуск автоматического цикла обучения")
    logger.info(f"Интервал проверки: {CHECK_INTERVAL} секунд")
    logger.info(f"Минимальное количество слов для дообучения: {MIN_WORDS_FOR_RETRAIN}")
    
    # Создаем директорию для данных знаний
    os.makedirs("data/knowledge", exist_ok=True)
    
    while True:
        try:
            # Загружаем статус
            status = load_status()
            status["last_check"] = datetime.now().isoformat()
            
            logger.info("\n" + "-" * 50)
            logger.info(f"Начало цикла проверки {status['last_check']}")
            
            # Получаем текущее количество слов
            current_words = get_word_count()
            logger.info(f"Текущее количество выученных слов: {current_words}")
            
            # Проверяем, нужно ли дообучение
            last_retrain_words = status.get('words_at_retrain', 0)
            new_words = current_words - last_retrain_words
            
            logger.info(f"Новых слов с последнего дообучения: {new_words}")
            
            if current_words >= MIN_WORDS_FOR_RETRAIN and new_words >= MIN_WORDS_FOR_RETRAIN:
                logger.info(f"🎯 Достаточно новых слов для дообучения ({new_words})")
                
                # Обновляем систему знаний
                success, output = run_script(UPDATE_SCRIPT)
                if not success:
                    logger.error("❌ Не удалось обновить систему знаний")
                    time.sleep(CHECK_INTERVAL)
                    continue
                
                # Запускаем дообучение
                success, output = run_script(RETRAIN_SCRIPT)
                if success:
                    # Обновляем статус
                    status["last_retrain"] = datetime.now().isoformat()
                    status["total_retrains"] = status.get("total_retrains", 0) + 1
                    status["words_at_retrain"] = current_words
                    status["words_learned"] = current_words
                    
                    logger.info(f"🎉 Успешное дообучение завершено!")
                    logger.info(f"Всего дообучений: {status['total_retrains']}")
                    logger.info(f"Всего выучено слов: {current_words}")
                else:
                    logger.error("❌ Дообучение не удалось")
            else:
                if current_words < MIN_WORDS_FOR_RETRAIN:
                    logger.info(f"ℹ️ Недостаточно выученных слов для дообучения ({current_words}/{MIN_WORDS_FOR_RETRAIN})")
                else:
                    logger.info(f"ℹ️ Недостаточно НОВЫХ слов для дообучения ({new_words}/{MIN_WORDS_FOR_RETRAIN})")
                
            # Сохраняем статус
            save_status(status)
            
            # Печатаем отчет
            print_cycle_report()
            
            # Ждем следующей проверки
            logger.info(f"💤 Ожидание следующей проверки через {CHECK_INTERVAL} секунд...")
            time.sleep(CHECK_INTERVAL)
            
        except KeyboardInterrupt:
            logger.info("\n🛑 Цикл обучения остановлен пользователем")
            break
        except Exception as e:
            logger.error(f"❌ Неожиданная ошибка в цикле: {e}")
            time.sleep(CHECK_INTERVAL)

if __name__ == "__main__":
    # Добавляем путь к проекту
    sys.path.append(".")
    
    try:
        import json
        main()
    except ImportError as e:
        logger.error(f"❌ Необходимые модули не найдены: {e}")
        logger.info("Пожалуйста, убедитесь, что knowledge_manager.py и другие файлы находятся в правильных местах.")
        sys.exit(1)