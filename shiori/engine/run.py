"""
Точка входа для запуска автономного ядра Шиори.

Использование:
    python -m shiori.engine.run              # постоянная работа
    python -m shiori.engine.run --demo       # демо-режим (5 циклов)
    python -m shiori.engine.run --scan       # только сканирование уязвимостей
    python -m shiori.engine.run --threats    # только обнаружение угроз
    python -m shiori.engine.run --web        # только анализ угроз из интернета
    python -m shiori.engine.run --status     # показать состояние защиты
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

from config import ShioriConfig
from shiori_core import ShioriCore


def cmd_run(config: ShioriConfig):
    """Запустить постоянную работу Шиори."""
    core = ShioriCore(config)
    core.run()


def cmd_status(config: ShioriConfig):
    """Показать текущее состояние защиты."""
    state_path = config.state_path

    if not state_path.exists():
        print("Шиори ещё не запускалась. Состояние отсутствует.")
        return

    with open(state_path, "r", encoding="utf-8") as f:
        state = json.load(f)

    print("=" * 60)
    print("🛡️ СОСТОЯНИЕ ЗАЩИТЫ ШИОРИ")
    print("=" * 60)
    print(f"Версия: {state.get('version', '?')}")
    print(f"Циклов выполнено: {state.get('cycle_count', 0)}")
    print(f"Последнее обновление: {state.get('timestamp', '?')}")
    print()
    print("Метрики защиты:")
    for key, value in state.get("metrics", {}).items():
        print(f"  {key}: {value}")
    print()

    security = state.get("security_state", {})
    if security:
        print("Состояние безопасности:")
        print(f"  Целостность системы: {security.get('system_integrity', 0):.1%}")
        print(f"  Статус сети: {security.get('network_status', '?')}")
        print(f"  Активных угроз: {security.get('active_threats', 0)}")
        print(f"  Заблокировано: {security.get('resolved_threats', 0)}")


def main():
    parser = argparse.ArgumentParser(
        description="Шиори — автономная иммунная система абсолютной защиты",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__
    )

    parser.add_argument(
        "--demo",
        action="store_true",
        help="Демо-режим: 5 циклов с короткими интервалами"
    )
    parser.add_argument(
        "--scan",
        action="store_true",
        help="Запустить только сканирование уязвимостей"
    )
    parser.add_argument(
        "--threats",
        action="store_true",
        help="Запустить только обнаружение угроз"
    )
    parser.add_argument(
        "--web",
        action="store_true",
        help="Только анализ угроз из интернета"
    )
    parser.add_argument(
        "--status",
        action="store_true",
        help="Показать текущее состояние защиты"
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
        config = ShioriConfig.demo()
    else:
        config = ShioriConfig.default()

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
