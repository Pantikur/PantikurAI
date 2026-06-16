"""
Автоматический цикл обучения чат-бота через GigaChat:
1. Отправляет примеры диалогов в GigaChat
2. Анализирует ответы
3. Сохраняет новые знания
4. Запускает дообучение модели
5. Повторяет цикл

ВАЖНО: Скрипт автоматически обновляет токен GigaChat при 401 ошибке
"""

import os
import sys
import json
import time
import logging
import requests
from datetime import datetime
from typing import List, Dict, Optional
import subprocess
import psutil
import torch 

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('auto_gigachat_learning.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Константы
GIGACHAT_API_URL = "https://gigachat.devices.sberbank.ru/api/v1/chat/completions"
CHECK_INTERVAL = 3600  # 10 минут
RETRAIN_TIMEOUT = 1800  # 30 минут на дообучение
MIN_EXAMPLES_FOR_LEARNING = 5  # Минимум примеров для дообучения

# Пути
KNOWLEDGE_DIR = "data/knowledge"
LEARNING_DIR = os.path.join(KNOWLEDGE_DIR, "learning_examples")
STATUS_FILE = os.path.join(KNOWLEDGE_DIR, "gigachat_learning_status.json")


# Проверка загрузки системы
def is_system_idle(cpu_threshold: float = 70.0, gpu_threshold: float = 50.0) -> bool:
    """Проверяет, свободна ли система для дообучения"""
    try:
        # Проверка CPU
        cpu_percent = psutil.cpu_percent(interval=1)
        if cpu_percent > cpu_threshold:
            logger.info(f"ℹ️ Высокая загрузка CPU: {cpu_percent}% > {cpu_threshold}%")
            return False
        
        # Проверка GPU (если доступен)
        if torch.cuda.is_available():
            gpu_util = torch.cuda.utilization()
            if gpu_util > gpu_threshold:
                logger.info(f"ℹ️ Высокая загрузка GPU: {gpu_util}% > {gpu_threshold}%")
                return False
        else:
            logger.info("ℹ️ GPU недоступен, используем CPU")
        
        logger.info(f"✅ Система готова: CPU={cpu_percent}%, GPU={torch.cuda.utilization() if torch.cuda.is_available() else 'N/A'}")
        return True
    except Exception as e:
        logger.warning(f"⚠️ Ошибка проверки загрузки системы: {e}")
        return True  # пропускаем проверку в случае ошибки

class GigaChatLearningSystem:
    def __init__(self, auto_refresh_token: bool = True):
        self.auto_refresh_token = auto_refresh_token
        self.token = self._get_gigachat_token()
        self._refresh_token_if_needed()  # ← проверка валидности токена
        self.examples_collection = []
        self.learning_dir = LEARNING_DIR
        os.makedirs(self.learning_dir, exist_ok=True)
        logger.info("🚀 GigaChat Learning System initialized")

    def _get_gigachat_token(self) -> str:
        """Получение токена из переменной окружения или файла"""
        token = os.environ.get("GIGACHAT_TOKEN")
        if not token:
            # Попытка считать из файла .env
            try:
                with open(".env", "r", encoding="utf-8") as f:
                    for line in f:
                        if line.strip().startswith("GIGACHAT_TOKEN="):
                            token = line.strip().split("=", 1)[1]
                            break
            except Exception as e:
                logger.error(f"Не удалось получить GIGACHAT_TOKEN: {e}")
                raise ValueError("GIGACHAT_TOKEN не найден")
        return token

    def _refresh_token_if_needed(self):
        """Проверяет, работает ли токен, и запрашивает новый при необходимости"""
        headers = {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json"
        }
        payload = {
            "model": "GigaChat-Pro",
            "messages": [{"role": "user", "content": "Привет"}],
            "stream": False,
            "max_tokens": 5
        }
        
        try:
            response = requests.post(
                GIGACHAT_API_URL,
                headers=headers,
                json=payload,
                timeout=10,
                verify=False
            )
            
            if response.status_code == 401:
                logger.warning("⚠️ Токен устарел или недействителен. Запрашиваю новый...")
                self._refresh_token()
            else:
                logger.info("✅ Токен GigaChat валиден")
                
        except Exception as e:
            logger.error(f"❌ Ошибка проверки токена: {e}")
            # Пробуем обновить
            self._refresh_token()

    def _refresh_token(self):
        """Запрашивает новый токен и сохраняет его"""
        try:
            # Запускаем get_gigachat_token.py
            result = subprocess.run(
                [sys.executable, "get_gigachat_token.py"],
                capture_output=True,
                text=True,
                timeout=60,
                encoding='utf-8'
            )
            if result.returncode == 0:
                # Перечитываем токен
                self.token = self._get_gigachat_token()
                logger.info("✅ Токен успешно обновлен")
            else:
                logger.error(f"❌ Ошибка обновления токена: {result.stderr}")
                raise ValueError("Не удалось обновить токен GigaChat")
        except Exception as e:
            logger.error(f"❌ Не удалось обновить токен: {e}")
            raise ValueError("Не удалось получить валидный токен GigaChat")

    def _call_gigachat(self, messages: List[Dict[str, str]], 
                       temperature: float = 0.7, 
                       timeout: int = 30) -> Optional[str]:
        """Вызов GigaChat API"""
        headers = {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": "GigaChat-Pro",
            "messages": messages,
            "temperature": temperature,
            "stream": False,
            "relevance_threshold": 0.5,
            "max_tokens": 1000
        }
        
        try:
            response = requests.post(
                GIGACHAT_API_URL,
                headers=headers,
                json=payload,
                timeout=timeout,
                verify=False
            )
            response.raise_for_status()
            return response.json()["choices"][0]["message"]["content"]
        except Exception as e:
            logger.error(f"Ошибка вызова GigaChat: {e}")
            return None

    def _extract_knowledge_from_example(self, example: Dict, response: str) -> Optional[Dict]:
        """Извлечение знаний из примера диалога"""
        try:
            # Пытаемся найти ключевые фразы в ответе
            if "значение слова" in response.lower() or "это" in response.lower():
                # Извлекаем определение
                import re
                pattern = r'(?:значение слова|это|это|означает)\s*[:\-]?\s*(.+?)(?:\.|$)'
                match = re.search(pattern, response.lower())
                if match:
                    definition = match.group(1).strip()
                    # Получаем слово из первого сообщения
                    user_msg = example.get("user_message", "").lower()
                    # Ищем первое слово после "что такое"
                    word_match = re.search(r'что такое\s+([а-яёa-z]+)', user_msg)
                    if word_match:
                        return {
                            "word": word_match.group(1),
                            "definition": definition,
                            "source": "gigachat",
                            "timestamp": datetime.now().isoformat()
                        }
        except Exception as e:
            logger.warning(f"Ошибка извлечения знаний: {e}")
        return None

    def _collect_examples(self, max_examples: int = 10) -> List[Dict]:
        """Сбор новых примеров через GigaChat"""
        new_examples = []
        
        # Промпты для получения обучающих примеров
        prompts = [
            "Что такое алгоритм?",
            "Что такое нейронная сеть?",
            "Что такое машинное обучение?",
            "Что такое квантовая механика?",
            "Что такое киберпанк?",
            "Что такое фэнтези?",
            "Что такое панк?",
            "Что такое ренессанс?",
            "Что такое империализм?",
            "Что такое постмодернизм?"
        ]
        
        logger.info(f"Сбор {min(len(prompts), max_examples)} примеров через GigaChat...")
        
        for i, prompt in enumerate(prompts[:max_examples]):
            messages = [
                {"role": "user", "content": prompt}
            ]
            
            response = self._call_gigachat(messages)
            if response:
                example = {
                    "user_message": prompt,
                    "bot_response": response,
                    "timestamp": datetime.now().isoformat()
                }
                
                # Извлекаем знания
                knowledge = self._extract_knowledge_from_example(example, response)
                if knowledge:
                    knowledge["id"] = f"ex_{len(self.examples_collection) + len(new_examples)}"
                    new_examples.append(knowledge)
                    logger.info(f"✅ Получено знание: {knowledge['word']} -> {knowledge['definition'][:100]}...")
            
            # Небольшая задержка, чтобы не спамить API
            time.sleep(1)
        
        return new_examples

    def _save_examples_to_file(self, examples: List[Dict]):
        """Сохранение собранных примеров в файл"""
        if not examples:
            return
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"gigachat_examples_{timestamp}.jsonl"
        filepath = os.path.join(self.learning_dir, filename)
        
        with open(filepath, "w", encoding="utf-8") as f:
            for example in examples:
                f.write(json.dumps(example, ensure_ascii=False) + "\n")
        
        logger.info(f"💾 Сохранено {len(examples)} примеров в {filepath}")

    def _load_existing_examples(self) -> List[Dict]:
        """Загрузка ранее собранных примеров"""
        all_examples = []
        if os.path.exists(self.learning_dir):
            for filename in os.listdir(self.learning_dir):
                if filename.endswith(".jsonl"):
                    filepath = os.path.join(self.learning_dir, filename)
                    try:
                        with open(filepath, "r", encoding="utf-8") as f:
                            for line in f:
                                if line.strip():
                                    all_examples.append(json.loads(line))
                    except Exception as e:
                        logger.warning(f"Ошибка загрузки {filepath}: {e}")
        return all_examples

    def _update_knowledge_base(self):
        """Обновление базы знаний на основе собранных примеров"""
        # Здесь должна быть интеграция с вашим системой знаний
        # Например, если у вас есть KnowledgeManager
        logger.info("🔄 Обновление базы знаний...")
        #TODO: Интеграция с вашей системой знаний
        return True

    def _run_retrain(self, epochs: int = 1):
        """Запуск дообучения модели с проверкой загрузки системы"""
        try:
            logger.info("🚀 Запуск проверки загрузки системы перед дообучением...")
            if not is_system_idle():
                logger.info("⏱ Ожидание снижения загрузки системы...")
                time.sleep(300)  # ждем 5 минут
                if not is_system_idle():
                    logger.error("❌ Система перегружена, пропускаем дообучение")
                    return False

            logger.info(f"🚀 Запуск дообучения модели с {epochs} эпохой(ами)...")
            result = subprocess.run(
                [sys.executable, "retrain.py", "--epochs", str(epochs)],
                capture_output=True,
                text=True,
                timeout=RETRAIN_TIMEOUT,
                encoding='utf-8'
            )
            if result.returncode == 0:
                logger.info("✅ Дообучение завершено успешно")
                
                # Сохраняем статус
                self._save_status()
                return True
            else:
                logger.error(f"❌ Ошибка дообучения: {result.stderr}")
                return False
        except subprocess.TimeoutExpired:
            logger.error(f"⏰ Дообучение превысило таймаут ({RETRAIN_TIMEOUT} сек)")
            return False
        except Exception as e:
            logger.error(f"❌ Исключение при дообучении: {e}")
            return False
        
    def _get_optimal_epochs(self) -> int:
        """Определяет оптимальное количество эпох на основе свободной памяти"""
        try:
            if torch.cuda.is_available():
                free_mem = torch.cuda.mem_get_info()[0] / (1024**3)  # GB
                return max(1, int(free_mem // 4))  # 4GB на эпоху
            return 1
        except Exception as e:
            logger.warning(f"⚠️ Ошибка определения оптимального количества эпох: {e}")
            return 1  # fallback

    def _save_status(self):
        """Сохраняет статус обучения в файл"""
        status = {
            "last_learning_cycle": datetime.now().isoformat(),
            "last_retrain_success": True,
            "total_retrains": self._load_status().get("total_retrains", 0) + 1,
            "last_examples_count": len(self._load_existing_examples())
        }
        try:
            with open(STATUS_FILE, 'w', encoding='utf-8') as f:
                json.dump(status, f, ensure_ascii=False, indent=2)
            logger.info(f"💾 Статус сохранен: {STATUS_FILE}")
        except Exception as e:
            logger.error(f"Ошибка сохранения статуса: {e}")

    def _load_status(self):
        """Загружает статус из файла"""
        if os.path.exists(STATUS_FILE):
            try:
                with open(STATUS_FILE, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                logger.warning(f"Ошибка загрузки статуса: {e}")
        return {
            "total_retrains": 0,
            "last_learning_cycle": None,
            "last_retrain_success": False
        }
    
    def run_learning_cycle(self) -> bool:
        """Выполнение одного цикла обучения"""
        try:
            logger.info("=" * 50)
            logger.info("Начало цикла обучения через GigaChat")
            
            # Загружаем существующие примеры
            existing_examples = self._load_existing_examples()
            logger.info(f"Найдено {len(existing_examples)} существующих примеров")
            
            # Собираем новые примеры
            new_examples = self._collect_examples(max_examples=10)
            
            if not new_examples:
                logger.info("ℹ️ Новые примеры не собраны, пропускаем дообучение")
                return False
            
            # Сохраняем новые примеры
            self._save_examples_to_file(new_examples)
            
            # Проверяем, достаточно ли примеров для дообучения
            total_examples = len(existing_examples) + len(new_examples)
            
            if total_examples < MIN_EXAMPLES_FOR_LEARNING:
                logger.info(f"ℹ️ Недостаточно примеров для дообучения ({total_examples} < {MIN_EXAMPLES_FOR_LEARNING})")
                return False
            
            # Обновляем базу знаний
            if not self._update_knowledge_base():
                logger.error("❌ Ошибка обновления базы знаний")
                return False
            
            # Определяем оптимальное количество эпох
            epochs = self._get_optimal_epochs()
            logger.info(f"📊 Рассчитано {epochs} эпох(ы) для дообучения")
            
            # Запускаем дообучение
            if not self._run_retrain(epochs):
                logger.error("❌ Ошибка дообучения модели")
                return False
            
            logger.info("🎉 Цикл обучения завершен успешно")
            return True
            
        except Exception as e:
            logger.error(f"❌ Ошибка в цикле обучения: {e}")
            return False

    def start_continuous_learning(self, interval: int = 600):
        """Запуск непрерывного обучения"""
        logger.info(f"🚀 Запуск непрерывного обучения с интервалом {interval} сек")
        
        while True:
            try:
                success = self.run_learning_cycle()
                
                if success:
                    logger.info(f"⏳ Ожидание следующего цикла ({interval} сек)...")
                else:
                    logger.info(f"⏳ Ожидание следующего цикла ({interval} сек) (без дообучения)...")
                
                time.sleep(interval)
                
            except KeyboardInterrupt:
                logger.info("\n🛑 Непрерывное обучение остановлено пользователем")
                break
            except Exception as e:
                logger.error(f"❌ Неожиданная ошибка: {e}")
                time.sleep(interval)


def main():
    """Основная функция"""
    # Проверяем наличие необходимых модулей
    try:
        import requests
        import json
    except ImportError as e:
        logger.error(f"Необходимые модули не найдены: {e}")
        sys.exit(1)
    
    # Создаем систему обучения
    try:
        learning_system = GigaChatLearningSystem()
    except ValueError as e:
        logger.error(f"Ошибка инициализации: {e}")
        sys.exit(1)
    
    # Запускаем непрерывное обучение
    learning_system.start_continuous_learning(interval=CHECK_INTERVAL)


if __name__ == "__main__":
    main()