"""
Точка входа для запуска автономного ядра Айко.

Использование:
    python -m ayiko.engine.run              # постоянная работа
    python -m ayiko.engine.run --demo       # демо-режим (5 циклов)
    python -m ayiko.engine.run --status     # показать состояние
"""

from __future__ import annotations
import argparse
import json
import sys
from pathlib import Path

# Принудительный UTF-8 для вывода (Windows-консоль использует cp1251)
for _stream in (sys.stdout, sys.stderr):
    _reconfigure = getattr(_stream, "reconfigure", None)
    if _reconfigure is not None:
        _reconfigure(encoding="utf-8")

from ayiko.engine.config import AyikoConfig
from ayiko.engine import Ayiko
from ayiko.engine.models import AyikoState


def cmd_run(config: AyikoConfig):
    """Запустить постоянную работу Айко."""
    core = Ayiko(config)
    core.run()


def cmd_status(config: AyikoConfig):
    """Показать текущее состояние Айко."""
    state_path = config.state_path

    if not state_path.exists():
        print("Айко ещё не запускалась. Состояние отсутствует.")
        return

    with open(state_path, "r", encoding="utf-8") as f:
        state = json.load(f)

    print("=" * 60)
    print("📚 СОСТОЯНИЕ АЙКО")
    print("=" * 60)
    print(f"Версия: {state.get('version', '?')}")
    print(f"Циклов выполнено: {state.get('cycle_count', 0)}")
    print(f"Книг прочитано: {state.get('books_read', 0)}")
    print(f"Обучающих пар создано: {state.get('training_pairs_generated', 0)}")
    print(f"Записей в базе знаний: {state.get('knowledge_entries_saved', 0)}")
    print(f"Последнее обновление: {state.get('timestamp', '?')}")
    print()

    print("Метрики:")
    for key, value in state.get("metrics", {}).items():
        print(f"  {key}: {value}")


def main():
    parser = argparse.ArgumentParser(
        description="Айко — автономная система чтения книг и обучения модели",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__
    )

    parser.add_argument(
        "--demo",
        action="store_true",
        help="Демо-режим: 5 циклов с короткими интервалами"
    )
    parser.add_argument(
        "--status",
        action="store_true",
        help="Показать текущее состояние"
    )
    parser.add_argument(
        "--interval",
        type=float,
        default=None,
        help="Интервал между циклами в секундах"
    )
    parser.add_argument(
        "--max-cycles",
        type=int,
        default=None,
        help="Максимальное количество циклов"
    )

    args = parser.parse_args()

    # Конфигурация
    if args.demo:
        config = AyikoConfig.demo()
    else:
        config = AyikoConfig.default()

    if args.interval is not None:
        config.cycle_interval = args.interval
    if args.max_cycles is not None:
        config.max_cycles = args.max_cycles

    # Команды
    if args.status:
        cmd_status(config)
    else:
        cmd_run(config)


if __name__ == "__main__":
    main()
