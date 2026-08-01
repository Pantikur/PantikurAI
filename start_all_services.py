#!/usr/bin/env python3
"""
СТАРТЕР ВСЕХ СЕРВИСОВ PANTIKUR
Запускает:
1. ChatBot API (порт 8000)
2. Автообучение из книг (Ханако)
3. Автономных девочек
"""

import os
import sys
import time
import subprocess
import logging
from pathlib import Path
from datetime import datetime

# Настройка логирования
LOG_DIR = Path("logs")
LOG_DIR.mkdir(exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s | %(levelname)s | %(message)s',
    handlers=[
        logging.FileHandler(LOG_DIR / "starter.log", encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("PantikurStarter")

PROJECT_ROOT = Path(__file__).resolve().parent

# Загрузка .env
def load_env():
    env_file = PROJECT_ROOT / ".env"
    if env_file.exists():
        with open(env_file, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    key, value = line.split("=", 1)
                    os.environ[key.strip()] = value.strip()
        logger.info("✅ .env загружен")

# Запуск сервиса
def start_service(name, command, cwd=None, env=None):
    """Запускает сервис в отдельном процессе"""
    full_env = os.environ.copy()
    if env:
        full_env.update(env)
    
    logger.info(f"🚀 Запуск сервиса: {name}")
    logger.info(f"   Команда: {' '.join(command)}")
    
    try:
        process = subprocess.Popen(
            command,
            cwd=cwd or str(PROJECT_ROOT),
            env=full_env,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1
        )
        
        logger.info(f"✅ {name} запущен (PID: {process.pid})")
        return process
    except Exception as e:
        logger.error(f"❌ Ошибка запуска {name}: {e}")
        return None

# Мониторинг процессов
def monitor_processes(processes):
    """Мониторит процессы и перезапускает упавшие"""
    logger.info("\n" + "="*60)
    logger.info("👁️  Мониторинг запущен")
    logger.info("="*60 + "\n")
    
    while True:
        time.sleep(30)  # Проверка каждые 30 секунд
        
        for name, proc in processes.items():
            if proc is None:
                continue
            
            if proc.poll() is not None:
                logger.warning(f"⚠️ {name} остановился (код: {proc.returncode})")
                logger.info(f"🔄 Перезапуск {name}...")
                
                # Перезапуск
                if name == "chatbot-api":
                    new_proc = start_service(
                        name,
                        [sys.executable, "main.py"],
                        env={"PORT": "8000"}
                    )
                elif name == "auto-learn":
                    new_proc = start_service(
                        name,
                        [sys.executable, "utils/auto_book_learning.py", "--cycle", "10"]
                    )
                elif name == "autonomous-girls":
                    new_proc = start_service(
                        name,
                        [sys.executable, "autonomous_girls_v2.py"]
                    )
                else:
                    continue
                
                if new_proc:
                    processes[name] = new_proc
                    logger.info(f"✅ {name} перезапущен (PID: {new_proc.pid})")
                else:
                    logger.error(f"❌ Не удалось перезапустить {name}")

def main():
    logger.info("="*60)
    logger.info("🤖 PANTIKUR STARTER — Запуск всех сервисов")
    logger.info("="*60)
    
    # Загрузка .env
    load_env()
    
    processes = {}
    
    # 1. ChatBot API
    logger.info("\n" + "-"*60)
    logger.info("📡 СЕРВИС 1: ChatBot API")
    logger.info("-"*60)
    chatbot = start_service(
        "chatbot-api",
        [sys.executable, "main.py"],
        env={"PORT": "8000"}
    )
    if chatbot:
        processes["chatbot-api"] = chatbot
    
    time.sleep(2)
    
    # 2. Автообучение из книг (Ханако)
    logger.info("\n" + "-"*60)
    logger.info("📚 СЕРВИС 2: Автообучение из книг (Ханако)")
    logger.info("-"*60)
    auto_learn = start_service(
        "auto-learn",
        [sys.executable, "utils/auto_book_learning.py", "--cycle", "10"]
    )
    if auto_learn:
        processes["auto-learn"] = auto_learn
    
    time.sleep(2)
    
    # 3. Автономные девочки
    logger.info("\n" + "-"*60)
    logger.info("👧 СЕРВИС 3: Автономные девочки")
    logger.info("-"*60)
    girls = start_service(
        "autonomous-girls",
        [sys.executable, "autonomous_girls_v2.py"]
    )
    if girls:
        processes["autonomous-girls"] = girls
    
    # Запуск мониторинга
    logger.info("\n" + "="*60)
    logger.info("🎉 ВСЕ СЕРВИСЫ ЗАПУЩЕНЫ!")
    logger.info("="*60)
    logger.info("📡 ChatBot API: http://localhost:8000")
    logger.info("📚 Автообучение: Ханако собирает данные и учит модель")
    logger.info("👧 Девочки: futaba, shiori, nobuka, naoto, hanako, ...")
    logger.info("="*60 + "\n")
    
    monitor_processes(processes)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        logger.info("\n🛑 Остановка всех сервисов...")
        sys.exit(0)
