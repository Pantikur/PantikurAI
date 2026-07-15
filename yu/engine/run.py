"""
Точка входа для запуска автономного ядра Юи.

Использование:
    python -m yu.engine.run              # постоянная работа
    python -m yu.engine.run --demo       # демо-режим (5 циклов)
    python -m yu.engine.run --autonomous # автономный режим
    python -m yu.engine.run --status     # показать состояние
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

from config import YuConfig
from yu_core import YuCore


def cmd_run(config: YuConfig):
    """Запустить постоянную работу Юи."""
    core = YuCore(config)
    core.run()


def cmd_analyze(config: YuConfig):
    """Запустить только анализ проекта."""
    print("=" * 60)
    print("🧠 АНАЛИЗ ПРОЕКТА ЮИ")
    print("=" * 60)
    print("Юи анализирует проект...")
    # Анализ будет реализован через YuCore


def cmd_status(config: YuConfig):
    """Показать текущее состояние Юи."""
    state_path = config.state_path

    if not state_path.exists():
        print("Юи ещё не запускалась. Состояние отсутствует.")
        return

    with open(state_path, "r", encoding="utf-8") as f:
        state = json.load(f)

    print("=" * 60)
    print("📊 СОСТОЯНИЕ ЮИ")
    print("=" * 60)
    print(f"Версия: {state.get('version', '?')}")
    print(f"Циклов выполнено: {state.get('cycle_count', 0)}")
    print(f"Последнее обновление: {state.get('timestamp', '?')}")
    print()
    print("Метрики:")
    for key, value in state.get("metrics", {}).items():
        print(f"  {key}: {value}")
    print()

    improvements = state.get("improvements_history", [])
    if improvements:
        print(f"Последние улучшения ({len(improvements)}):")
        for imp in improvements[-5:]:
            status = "✅" if imp.get("applied") else "⏸️"
            print(f"  {status} {imp.get('version_after', '?')}: "
                  f"{imp.get('description', '?')}")


def main():
    parser = argparse.ArgumentParser(
        description="Юи — автономная система изучения сознания, души и разума",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__
    )

    parser.add_argument(
        "--demo",
        action="store_true",
        help="Демо-режим: 5 циклов с короткими интервалами"
    )
    parser.add_argument(
        "--autonomous",
        action="store_true",
        help="Автономный режим: бесконечный цикл исследований"
    )
    parser.add_argument(
        "--analyze",
        action="store_true",
        help="Запустить только анализ проекта"
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
        config = YuConfig.demo()
    else:
        config = YuConfig.default()

    if args.interval is not None:
        config.cycle_interval = args.interval
    if args.max_cycles is not None:
        config.max_cycles = args.max_cycles

    # Команды
    if args.status:
        cmd_status(config)
    elif args.analyze:
        cmd_analyze(config)
    else:
        cmd_run(config)


if __name__ == "__main__":
    main()
