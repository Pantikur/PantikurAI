#!/usr/bin/env python3
"""
🔮 Оркестратор девочек — автоматический запуск всех 12 сестёр.

Запускает автономное ядро каждой девочки в отдельном потоке.
Каждая девочка работает независимо и выбирает свой характер.

Использование:
    python orchestrator.py          # запустить всех
    python orchestrator.py nobuka   # запустить только Нобуку
    python orchestrator.py --status # показать статус
"""

import os
import sys
import time
import threading
import subprocess
import logging
from pathlib import Path
from typing import Dict, Optional

# === Настройка логирования ===
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout),
    ]
)
logger = logging.getLogger("Orchestrator")

# Принудительный UTF-8 для вывода (Windows-консоль использует cp1251)
for _stream in (sys.stdout, sys.stderr):
    _reconfigure = getattr(_stream, "reconfigure", None)
    if _reconfigure is not None:
        _reconfigure(encoding="utf-8")

# === Список всех девочек ===
GIRLS = [
    "hanako",      # Ханако — гравитация
    "fuyuki",      # Фуюки — электричество
    "lucy",        # Люси — двигатели
    "futaba",      # Футаба — управление
    "shiori",      # Шиори — защита
    "nobuka",      # Нобука — улучшения
    "akva",        # Аква — математика, физика
    "latislane",   # Latislane — проектирование тел
    "celesta",     # Селеста — интимная жизнь
    "naoto",       # Наото — визуальный архитектор
    "yu",          # Юи — сознание, перенос
    "ayiko",       # Айико — последний вариант
]

# === Словарь статусов ===
girl_processes: Dict[str, Optional[subprocess.Popen]] = {}
girl_threads: Dict[str, Optional[threading.Thread]] = {}


def start_girl(girl_name: str, demo: bool = False):
    """
    Запустить автономное ядро девочки в отдельном процессе.
    """
    girl_dir = Path(__file__).parent / girl_name
    if not girl_dir.exists():
        logger.warning(f"⚠️ Директория {girl_name} не найдена — пропускаю")
        return

    run_script = girl_dir / "engine" / "run.py"
    if not run_script.exists():
        logger.warning(f"⚠️ run.py не найден в {girl_name}/engine/ — пропускаю")
        return

    logger.info(f"🚀 Запуск {girl_name}...")

    try:
        cmd = [
            sys.executable, str(run_script),
            "--interval", "15",  # интервал между циклами
        ]
        if demo:
            cmd.append("--demo")

        process = subprocess.Popen(
            cmd,
            cwd=str(girl_dir),
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1,
        )

        girl_processes[girl_name] = process
        logger.info(f"OK {girl_name} запущена (PID: {process.pid})")

        # Читаем вывод в реальном времени
        def read_output():
            if process.stdout:
                for line in process.stdout:
                    prefix = f"[{girl_name}] "
                    sys.stdout.write(prefix + line)
                    sys.stdout.flush()

        thread = threading.Thread(target=read_output, daemon=True)
        thread.start()
        girl_threads[girl_name] = thread

    except Exception as e:
        logger.error(f"❌ Ошибка запуска {girl_name}: {e}")


def stop_girl(girl_name: str):
    """
    Остановить девочку.
    """
    process = girl_processes.get(girl_name)
    if process and process.poll() is None:
        logger.info(f"🛑 Остановка {girl_name}...")
        process.terminate()
        try:
            process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            process.kill()
        logger.info(f"✅ {girl_name} остановлена")
    else:
        logger.warning(f"⚠️ {girl_name} уже остановлена")


def start_all(demo: bool = False):
    """
    Запустить всех девочек последовательно.
    """
    logger.info("=" * 60)
    logger.info("🔮 ОРКЕСТРАТОР ДЕВОЧЕК — ЗАПУСК")
    logger.info(f"   Девочек: {len(GIRLS)}")
    logger.info(f"   Режим: {'ДЕМО' if demo else 'ПРОДАКШН'}")
    logger.info("=" * 60)

    # Ждём немного перед каждым запуском, чтобы не перегружать систему
    for girl in GIRLS:
        start_girl(girl, demo)
        time.sleep(2)  # задержка 2 секунды между запусками

    logger.info("=" * 60)
    logger.info("🎉 ВСЕ ДЕВОЧКИ ЗАПУЩЕНЫ")
    logger.info("   Каждая работает в своём процессе и выбирает характер")
    logger.info("   Для остановки: Ctrl+C")
    logger.info("=" * 60)

    # Ждём все процессы
    try:
        while True:
            # Проверяем, живы ли все
            alive = 0
            for girl, process in girl_processes.items():
                if process and process.poll() is None:
                    alive += 1
                else:
                    logger.warning(f"⚠️ {girl} остановилась")

            logger.info(f"📊 Активных девочек: {alive}/{len(GIRLS)}")
            time.sleep(30)  # отчёт каждые 30 секунд
    except KeyboardInterrupt:
        logger.info("\n🛑 Получен сигнал остановки...")
        stop_all()


def stop_all():
    """
    Остановить всех девочек.
    """
    logger.info("=" * 60)
    logger.info("🛑 ОСТАНОВКА ВСЕХ ДЕВОЧЕК")
    logger.info("=" * 60)

    for girl in GIRLS:
        stop_girl(girl)

    logger.info("✅ Все девочки остановлены")


def cmd_status():
    """
    Показать статус всех девочек.
    """
    logger.info("=" * 60)
    logger.info("📊 СТАТУС ДЕВОЧЕК")
    logger.info("=" * 60)

    for girl in GIRLS:
        process = girl_processes.get(girl)
        if process and process.poll() is None:
            status = "✅ Работает"
        else:
            status = "⏹️ Остановлена"
        logger.info(f"   {girl}: {status}")

    logger.info("=" * 60)


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(
        description="🔮 Оркестратор девочек — автоматический запуск всех 12 сестёр"
    )
    parser.add_argument(
        "--demo",
        action="store_true",
        help="Демо-режим: 5 циклов с короткими интервалами"
    )
    parser.add_argument(
        "--status",
        action="store_true",
        help="Показать статус всех девочек"
    )
    parser.add_argument(
        "--stop",
        action="store_true",
        help="Остановить всех девочек"
    )
    parser.add_argument(
        "girls",
        nargs="*",
        help="Имена девочек для запуска (по умолчанию: все)"
    )

    args = parser.parse_args()

    # Определяем, кого запускать
    if args.girls:
        girls_to_run = [g for g in args.girls if g in GIRLS]
        if not girls_to_run:
            logger.error(f"❌ Не найдены девочки: {args.girls}")
            sys.exit(1)
    else:
        girls_to_run = GIRLS[:]

    if args.status:
        cmd_status()
    elif args.stop:
        stop_all()
    else:
        # Запускаем
        if args.girls:
            logger.info(f"🚀 Запуск {len(girls_to_run)} девочек: {', '.join(girls_to_run)}")
        else:
            logger.info(f"🚀 Запуск всех {len(girls_to_run)} девочек")

        start_all(demo=args.demo)
