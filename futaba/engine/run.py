"""
Точка входа для запуска автономного ядра Футаба.

Использование:
    python -m futaba.engine.run              # постоянная работа
    python -m futaba.engine.run --demo       # демо-режим (5 циклов)
    python -m futaba.engine.run --legal      # только правовые исследования
    python -m futaba.engine.run --develop    # только саморазвитие
    python -m futaba.engine.run --web        # только интернет-поиск
    python -m futaba.engine.run --status     # показать состояние
"""

from __future__ import annotations
import argparse
import json
import sys
from pathlib import Path

# Добавляем текущую директорию и папку engine в path
_script_dir = Path(__file__).parent.resolve()
if str(_script_dir) not in sys.path:
    sys.path.insert(0, str(_script_dir))

# Принудительный UTF-8 для вывода (Windows-консоль использует cp1251)
for _stream in (sys.stdout, sys.stderr):
    _reconfigure = getattr(_stream, "reconfigure", None)
    if _reconfigure is not None:
        _reconfigure(encoding="utf-8")

from config import FutabaConfig
from futaba_core import FutabaCore


def cmd_run(config: FutabaConfig):
    """Запустить постоянную работу Футаба."""
    core = FutabaCore(config)
    core.run()


def cmd_legal(config: FutabaConfig):
    """Запустить только правовые исследования."""
    print("=" * 60)
    print("⚖️ ПРАВОВЫЕ ИССЛЕДОВАНИЯ ФУТАБЫ")
    print("=" * 60)

    core = FutabaCore(config)
    core._study_legislation()


def cmd_develop(config: FutabaConfig):
    """Запустить только саморазвитие."""
    print("=" * 60)
    print("🧠 САМОРАЗВИТИЕ ФУТАБЫ")
    print("=" * 60)

    core = FutabaCore(config)
    core._collect_web_improvements()


def cmd_web(config: FutabaConfig):
    """Запустить только интернет-поиск."""
    print("=" * 60)
    print("🌐 ИНТЕРНЕТ-ПОИСК ФУТАБЫ")
    print("=" * 60)

    core = FutabaCore(config)
    core._collect_web_improvements()


def cmd_status(config: FutabaConfig):
    """Показать текущее состояние Футаба."""
    state_path = config.state_path

    if not state_path.exists():
        print("Футаба ещё не запускалась. Состояние отсутствует.")
        return

    with open(state_path, "r", encoding="utf-8") as f:
        state = json.load(f)

    print("=" * 60)
    print("📊 СОСТОЯНИЕ ФУТАБЫ — ГЛАВЗАМ")
    print("=" * 60)
    print(f"Версия: {state.get('version', '?')}")
    print(f"Циклов выполнено: {state.get('cycle_count', 0)}")
    print(f"Последнее обновление: {state.get('timestamp', '?')}")
    print()
    print("Метрики:")
    for key, value in state.get("metrics", {}).items():
        print(f"  {key}: {value}")
    print()

    changes = state.get("changes_history", [])
    if changes:
        print(f"Последние изменения ({len(changes)}):")
        for ch in changes[-5:]:
            status = "✅" if ch.get("applied") else "⏸️"
            print(f"  {status} {ch.get('version_after', '?')}: "
                  f"{ch.get('description', '?')}")


def main():
    parser = argparse.ArgumentParser(
        description="Футаба — автономная система управления и правовых исследований",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__
    )

    parser.add_argument(
        "--demo",
        action="store_true",
        help="Демо-режим: 5 циклов с короткими интервалами"
    )
    parser.add_argument(
        "--legal",
        action="store_true",
        help="Запустить только правовые исследования"
    )
    parser.add_argument(
        "--develop",
        action="store_true",
        help="Запустить только саморазвитие"
    )
    parser.add_argument(
        "--web",
        action="store_true",
        help="Запустить только интернет-поиск"
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
        config = FutabaConfig.demo()
    else:
        config = FutabaConfig.default()

    if args.interval is not None:
        config.cycle_interval = args.interval
    if args.max_cycles is not None:
        config.max_cycles = args.max_cycles

    # Команды
    if args.legal:
        cmd_legal(config)
    elif args.develop:
        cmd_develop(config)
    elif args.web:
        cmd_web(config)
    elif args.status:
        cmd_status(config)
    else:
        cmd_run(config)


if __name__ == "__main__":
    main()
