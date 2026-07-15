"""
Точка входа для автономного ядра Аква.

Запуск:
    python -m akva.engine.run
    python -m akva.engine.run --demo
    python -m akva.engine.run --interval 5 --max-cycles 20
"""

import argparse
import logging
import sys
import io
from pathlib import Path

# Фикс кодировки для Windows
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")

# Добавляем корень проекта в путь
project_root = Path(__file__).parent.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from akva.engine.config import AkvaConfig
from akva.engine.akva_core import AkvaCore


def main():
    parser = argparse.ArgumentParser(description="Аква — Научный модуль Pantikur")
    parser.add_argument("--demo", action="store_true", help="Демо-режим (10 циклов, короткие интервалы)")
    parser.add_argument("--interval", type=float, default=None, help="Интервал циклов в секундах")
    parser.add_argument("--max-cycles", type=int, default=None, help="Максимум циклов")
    parser.add_argument("--no-web", action="store_true", help="Отключить интернет")
    parser.add_argument("--no-communication", action="store_true", help="Отключить общение")
    parser.add_argument("--no-reports", action="store_true", help="Отключить отчёты")
    parser.add_argument("--status", action="store_true", help="Показать текущий статус")
    args = parser.parse_args()

    # Настройка логирования
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
        handlers=[
            logging.StreamHandler(sys.stdout),
        ],
        force=True,
    )

    # Конфигурация
    if args.demo:
        config = AkvaConfig.demo()
    else:
        config = AkvaConfig.default()

    if args.interval is not None:
        config.cycle_interval = args.interval
    if args.max_cycles is not None:
        config.max_cycles = args.max_cycles
    if args.no_web:
        config.web_search_enabled = False
    if args.no_communication:
        config.communication_enabled = False
    if args.no_reports:
        config.reporting_enabled = False

    # Запуск
    core = AkvaCore(config)

    if args.status:
        status = core.get_status()
        print("\n" + "=" * 60)
        print("СТАНДАРТ АКВА")
        print("=" * 60)
        print(f"Версия: {status['version']}")
        print(f"Циклов: {status['cycle_count']}")
        print(f"Всего XP: {status['total_xp']}")
        print(f"\nХарактер: {status['personality_level']}")
        print(f"Доминирующая черта: {status['personality'].get('curiosity', 0):.2f} любознательность")
        for k, v in status['personality'].items():
            print(f"  {k}: {v:.2f}")
        print(f"\nУровни знаний:")
        for area, data in status['knowledge_levels'].items():
            print(f"  {area}: уровень {data['level']}/100, XP: {data['xp']}")
        print(f"\nМетрики:")
        for k, v in status['metrics'].items():
            print(f"  {k}: {v}")
        print("=" * 60)
        return

    print(f"\n📐 Аква запускается...")
    print(f"   Демо-режим: {args.demo}")
    print(f"   Циклов: {config.max_cycles or 'бесконечно'}")
    print(f"   Интервал: {config.cycle_interval}с")
    print(f"   Интернет: {'✅' if config.web_search_enabled else '❌'}")
    print(f"   Общение: {'✅' if config.communication_enabled else '❌'}")
    print(f"   Отчёты: {'✅' if config.reporting_enabled else '❌'}")
    print()

    core.run()

    print("\n🛑 Аква остановлена. Состояние сохранено.")


if __name__ == "__main__":
    main()
