#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Research Monitor Demo — демонстрация всех 7 ядер учёных.
"""

from __future__ import annotations
import logging
import sys
import time
from pathlib import Path

# Добавляем корень проекта в путь
project_root = Path(__file__).resolve().parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
)
logger = logging.getLogger("research_monitor_demo")


def demo():
    """Демонстрация Research Monitor со всеми 7 ядрами."""
    from scientists_network.research_monitor import ResearchMonitor

    print("=" * 70)
    print("RESEARCH MONITOR — МОНИТОРИНГ ВСЕХ 7 ЯДЕР УЧЕНЫХ")
    print("=" * 70)

    # Инициализация
    print("\n[INIT] Инициализация ResearchMonitor...")
    monitor = ResearchMonitor()
    monitor.initialize()

    print("[STATUS] Инициализировано ядер: {}".format(len(monitor.cores)))
    for name in monitor.cores:
        print("   - " + name)

    # Запуск всех ядер
    print("\n" + "=" * 70)
    print("ЗАПУСК ИССЛЕДОВАНИЙ")
    print("=" * 70)

    scientists = ["hanako", "fuyuki", "lucy", "futaba", "shiori", "nobuka", "latislane", "celest", "akva"]
    for name in scientists:
        result = monitor.start_research(name)
        print("  {}:".format(name) + " " + result.get("message", "error"))

    # Ожидание
    print("\n[WAIT] Ожидание 15 секунд...")
    time.sleep(15)

    # Результаты
    print("\n" + "=" * 70)
    print("РЕЗУЛЬТАТЫ ИССЛЕДОВАНИЙ")
    print("=" * 70)

    for name in scientists:
        print("\n  " + name.upper() + ":")
        summary = monitor.get_research_summary(name)
        if summary:
            metrics = summary["status"]["metrics"]
            print("    Циклов: {}".format(metrics.get("cycles_completed", 0)))
            print("    Теорий: {}".format(metrics.get("theories_built", 0)))
            print("    Вычислений: {}".format(metrics.get("calculations_run", 0)))
            print("    Статей: {}".format(metrics.get("papers_studied", 0)))
            print("    Событий: {}".format(summary["status"].get("events_count", 0)))

            # Специфичные данные
            if summary.get("improvements"):
                print("    Улучшений: {}".format(len(summary["improvements"])))
            if summary.get("threats"):
                print("    Угроз: {}".format(len(summary["threats"])))
            if summary.get("incidents"):
                print("    Инцидентов: {}".format(len(summary["incidents"])))
            if summary.get("changes"):
                print("    Изменений: {}".format(len(summary["changes"])))

    # Остановка
    print("\n" + "=" * 70)
    print("ОСТАНОВКА ИССЛЕДОВАНИЙ")
    print("=" * 70)

    for name in scientists:
        result = monitor.stop_research(name)
        print("  {}:".format(name) + " " + result.get("message", "error"))

    print("\n" + "=" * 70)
    print("DEMO COMPLETED")
    print("=" * 70)


if __name__ == "__main__":
    demo()

