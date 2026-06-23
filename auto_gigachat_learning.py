"""
auto_gigachat_learning.py — автоматическое обучение через GigaChat:
1. Запускает вопросы через GigaChat API
2. Анализирует ответы
3. Сохраняет новые знания
4. Запускает ретраин модели
5. Повторяет цикл
6. команда запуска python auto_gigachat_learning.py
7. для токена python get_gigachat_token.py

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

# === Безопасная проверка GPU при запуске ===
try:
    cuda_available = torch.cuda.is_available()
    print(f"✅ CUDA доступна: {cuda_available}")
    if cuda_available:
        print(f"🖥️ GPU: {torch.cuda.get_device_name(0)}")
        print(f"🔢 Свободная память: {torch.cuda.mem_get_info()[0] / 1024**3:.1f} GB")
    else:
        print("ℹ️ GPU недоступен — обучение будет на CPU")
except Exception as e:
    print(f"⚠️ Ошибка проверки GPU: {e}")


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
CHECK_INTERVAL = 3600  # 1 час
RETRAIN_TIMEOUT = 3600  # 1 час на ретраин
MIN_EXAMPLES_FOR_LEARNING = 5  # Минимум примеров для ретраина

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
            gpu_name = torch.cuda.get_device_name(0)
            gpu_total_mem = torch.cuda.get_device_properties(0).total_memory / 1024**3
            gpu_util = torch.cuda.utilization()
            gpu_free_mem = torch.cuda.mem_get_info()[0] / 1024**3
            
            logger.info(f"📊 GPU: {gpu_name} ({gpu_total_mem:.1f} ГБ)")
            if gpu_util > gpu_threshold:
                logger.info(f"ℹ️ Высокая загрузка GPU ({gpu_util}% > {gpu_threshold}%) — ожидаем снижения...")
                return False
            logger.info(f"✅ GPU готова: {gpu_name} (свободно {gpu_free_mem:.1f} ГБ из {gpu_total_mem:.1f} ГБ, загрузка {gpu_util}%)")
        else:
            logger.info("ℹ️ GPU недоступен — обучение будет на CPU")
        
        logger.info(f"✅ Система готова: CPU={cpu_percent}%")
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
            self._refresh_token()

    def _refresh_token(self):
        """Запрашивает новый токен и сохраняет его"""
        try:
            result = subprocess.run(
                [sys.executable, "get_gigachat_token.py"],
                capture_output=True,
                text=True,
                timeout=60,
                encoding='cp1251',
                errors='ignore'
            )
            if result.returncode == 0:
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
        
    def _generate_prompts(self, topic: str = "наука", count: int = 10) -> List[str]:
        """Генерирует новые вопросы через GigaChat по заданной теме"""
        try:
            logger.info(f"🔄 Генерация {count} вопросов по теме '{topic}'...")
            messages = [
                {"role": "user", "content": f"Сгенерируй {count} вопросов формата 'Что такое ...?' по теме '{topic}'. "
                                            "Каждый вопрос на новой строке, без нумерации."}
            ]
            
            response = self._call_gigachat(messages)
            if not response:
                logger.warning("⚠️ GigaChat не сгенерировал вопросы")
                return []
            
            questions = []
            for line in response.split("\n"):
                line = line.strip()
                if not line:
                    continue
                if line[0].isdigit():
                    line = line.split(".", 1)[-1].strip() if "." in line else line
                if line.endswith("?") and "что такое" in line.lower():
                    questions.append(line)
            
            logger.info(f"✅ Сгенерировано {len(questions)} вопросов по теме '{topic}'")
            return questions[:count]
        except Exception as e:
            logger.warning(f"⚠️ Ошибка генерации вопросов: {e}")
            return []
        
    def _save_prompts_to_file(self, prompts: List[str], append: bool = True):
        """Сохраняет промпты в файл prompts.txt"""
        prompts_file = os.path.join(KNOWLEDGE_DIR, "prompts.txt")
        try:
            mode = "a" if append else "w"
            with open(prompts_file, mode, encoding="utf-8") as f:
                for prompt in prompts:
                    f.write(prompt + "\n")
            logger.info(f"💾 Сохранено {len(prompts)} промптов в {prompts_file}")
        except Exception as e:
            logger.warning(f"⚠️ Ошибка сохранения промптов: {e}")

    def _extract_knowledge_from_example(self, example: Dict, response: str) -> Optional[Dict]:
        """Извлечение знаний из примера диалога"""
        try:
            if "значение слова" in response.lower() or "это" in response.lower():
                import re
                pattern = r'(?:значение слова|это|означает)\s*[:\-]?\s*(.+?)(?:\.|$)'
                match = re.search(pattern, response.lower())
                if match:
                    definition = match.group(1).strip()
                    user_msg = example.get("user_message", "").lower()
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
        
        prompts = []
        prompts_file = os.path.join(KNOWLEDGE_DIR, "prompts.txt")
        if os.path.exists(prompts_file):
            try:
                with open(prompts_file, "r", encoding="utf-8") as f:
                    prompts = [line.strip() for line in f if line.strip()]
                logger.info(f"📚 Загружено {len(prompts)} промптов из {prompts_file}")
            except Exception as e:
                logger.warning(f"⚠️ Ошибка загрузки промптов: {e}")
        
        if not prompts:
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
            logger.info("ℹ️ Используем дефолтные промпты")
            
            topics = ["технологии", "история", "искусство", "философия"]
            for topic in topics:
                new_prompts = self._generate_prompts(topic, count=3)
                if new_prompts:
                    prompts.extend(new_prompts)
            
            self._save_prompts_to_file(prompts, append=False)
        
        max_examples = min(max_examples, len(prompts))
        logger.info(f"Сбор {max_examples} примеров через GigaChat...")
        
        for i, prompt in enumerate(prompts[:max_examples]):
            messages = [{"role": "user", "content": prompt}]
            
            response = self._call_gigachat(messages)
            if response:
                example = {
                    "user_message": prompt,
                    "bot_response": response,
                    "timestamp": datetime.now().isoformat()
                }
                
                knowledge = self._extract_knowledge_from_example(example, response)
                if knowledge:
                    knowledge["id"] = f"ex_{len(self.examples_collection) + len(new_examples)}"
                    new_examples.append(knowledge)
                    logger.info(f"✅ Получено знание: {knowledge['word']} -> {knowledge['definition'][:100]}...")
            
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
        logger.info("🔄 Обновление базы знаний...")
        return True

    def _run_retrain(self, epochs: int = 1):
        """Запуск ретраина модели с проверкой загрузки системы"""
        try:
            logger.info("🚀 Запуск проверки загрузки системы перед ретраином...")
            if not is_system_idle():
                logger.info("⏱ Ожидание снижения загрузки системы...")
                time.sleep(300)
                if not is_system_idle():
                    logger.error("❌ Система перегружена, пропускаем ретраин")
                    return False

            logger.info(f"🚀 Запуск ретраина модели (количество эпох управляется через retrain.py -> train.py)...")

            result = subprocess.run(
                [sys.executable, "retrain.py", "--verbose"],
                capture_output=True,
                text=True,
                timeout=RETRAIN_TIMEOUT,
                encoding='cp1251',
                errors='ignore'
            )
            if result.returncode == 0:
                logger.info("✅ Ретраин завершён успешно")
                self._save_status()
                return True
            else:
                logger.error(f"❌ Ошибка ретраина: {result.stderr}")
                return False
        except subprocess.TimeoutExpired:
            logger.error(f"⏰ Ретраин превысил таймаут ({RETRAIN_TIMEOUT} сек)")
            return False
        except Exception as e:
            logger.error(f"❌ Исключение при ретраине: {e}")
            return False
        
    def _get_optimal_epochs(self) -> int:
        """Определяет оптимальное количество эпох на основе свободной памяти"""
        try:
            if torch.cuda.is_available():
                gpu_name = torch.cuda.get_device_name(0)
                free_mem = torch.cuda.mem_get_info()[0] / (1024**3)
                optimal = max(1, int(free_mem // 3.5))
                logger.info(f"📊 {gpu_name} (8GB): рассчитано {optimal} эпох(ы) для ретраина")
                return optimal
            return 1
        except Exception as e:
            logger.warning(f"⚠️ Ошибка определения оптимального количества эпох: {e}")
            return 1

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
                logger.info("ℹ️ Новые примеры не собраны, пропускаем ретраин")
                return False
            
            # Сохраняем примеры
            self._save_examples_to_file(new_examples)
            
            # Проверяем, достаточно ли примеров для ретраина
            total_examples = len(existing_examples) + len(new_examples)
            
            if total_examples < MIN_EXAMPLES_FOR_LEARNING:
                logger.info(f"ℹ️ Недостаточно примеров для ретраина ({total_examples} < {MIN_EXAMPLES_FOR_LEARNING})")
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
            logger.info(f"📊 Рассчитано {epochs} эпох(ы) для ретраина")
            
            # Запускаем ретраин
            if not self._run_retrain(epochs):
                logger.error("❌ Ошибка ретраина модели")
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
                    logger.info(f"⏳ Ожидание следующего цикла ({interval} сек) (без ретраина)...")
                
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