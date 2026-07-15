"""
Точка входа для запуска автономного ядра Фуюки.

Использование:
    python -m fuyuki.engine.run              # постоянная работа
    python -m fuyuki.engine.run --demo       # демо-режим (10 циклов)
    python -m fuyuki.engine.run --status     # показать состояние
    python -m fuyuki.engine.run --report     # показать отчёты
    python -m fuyuki.engine.run --character  # показать характер
    python -m fuyuki.engine.run --knowledge  # показать знания
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

from config import FuyukiConfig
from fuyuki_core import FuyukiCore


def cmd_run(config: FuyukiConfig):
    """Запустить постоянную работу Фуюки."""
    core = FuyukiCore(config)
    core.run()


def cmd_status(config: FuyukiConfig):
    """Показать текущее состояние Фуюки."""
    from fuyuki.engine.knowledge_manager import KnowledgeManager
    from fuyuki.engine.character_developer import CharacterDeveloper
    
    core = FuyukiCore(config)
    status = core.get_status()
    
    print("\n" + "=" * 60)
    print("⚡ СОСТОЯНИЕ ФУКИ")
    print("=" * 60)
    print(f"Версия: {status['version']}")
    print(f"Циклов выполнено: {status['cycle_count']}")
    print()
    print("📊 Метрики:")
    for key, value in status["metrics"].items():
        print(f"  {key}: {value}")
    print()
    
    # Уровень знаний
    kl = status.get("knowledge_level", {})
    print(f"📚 Уровень знаний: Lvl {kl.get('level', '?')} — {kl.get('level_name', '?')}")
    print(f"   Опыт: {kl.get('xp', 0)} XP")
    print(f"   Прогресс: {kl.get('progress_to_next', 0):.1f}% до следующего уровня")
    print()
    
    # Характер
    char = status.get("character_summary", "")
    if char:
        print(char)
    
    print()
    print(f"🔬 Теорий построено: {status.get('theories_count', 0)}")
    print(f"🧮 Вычислений выполнено: {status.get('calculations_count', 0)}")
    print(f"📖 Статей изучено: {status.get('papers_count', 0)}")


def cmd_report(config: FuyukiConfig):
    """Показать последние отчёты."""
    from fuyuki.engine.report_generator import ReportGenerator
    
    rg = ReportGenerator(config)
    reports = rg.list_reports(limit=5)
    
    if not reports:
        print("Отчётов пока нет.")
        return
    
    print("\n" + "=" * 60)
    print("📝 ПОСЛЕДНИЕ ОТЧЁТЫ ФУКИ")
    print("=" * 60)
    
    for report in reports:
        print(f"\n📅 {report.get('date', 'N/A')} — Цикл #{report.get('cycle', '?')}")
        print(f"   Уровень: Lvl {report.get('knowledge_level', '?')}")
        print(f"   Теорий: {report.get('theories_built', 0)}")
        print(f"   Вычислений: {report.get('calculations_run', 0)}")
        print(f"   Статей: {report.get('papers_studied', 0)}")


def cmd_character(config: FuyukiConfig):
    """Показать текущий характер Фуюки."""
    from fuyuki.engine.character_developer import CharacterDeveloper
    
    dev = CharacterDeveloper(config)
    print("\n" + "=" * 60)
    print("💪 ХАРАКТЕР ФУКИ")
    print("=" * 60)
    print(dev.get_character_summary())


def cmd_knowledge(config: FuyukiConfig):
    """Показать текущие знания Фуюки."""
    from fuyuki.engine.knowledge_manager import KnowledgeManager
    
    km = KnowledgeManager(config)
    summary = km.get_knowledge_summary()
    
    print("\n" + "=" * 60)
    print("📚 ЗНАНИЯ ФУКИ")
    print("=" * 60)
    print(f"Уровень: Lvl {summary['level']} — {summary['level_name']}")
    print(f"Опыт: {summary['xp']} XP")
    print(f"Прогресс: {summary['progress_to_next']}% до следующего уровня")
    print(f"Фактов: {summary['facts_count']}")
    print(f"Формул: {summary['formulas_count']}")
    print(f"Теорий: {summary['theories_count']}")
    print(f"Изучено областей: {summary['domains_count']}")
    
    if summary['domains_studied']:
        print("\nИзученные области:")
        for domain in summary['domains_studied']:
            print(f"  • {domain}")


def main():
    parser = argparse.ArgumentParser(
        description="Фуюки — автономный исследователь атмосферного электричества",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__
    )
    
    parser.add_argument(
        "--demo",
        action="store_true",
        help="Демо-режим: 10 циклов с короткими интервалами"
    )
    parser.add_argument(
        "--status",
        action="store_true",
        help="Показать текущее состояние"
    )
    parser.add_argument(
        "--report",
        action="store_true",
        help="Показать последние отчёты"
    )
    parser.add_argument(
        "--character",
        action="store_true",
        help="Показать текущий характер"
    )
    parser.add_argument(
        "--knowledge",
        action="store_true",
        help="Показать текущие знания"
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
        config = FuyukiConfig.demo()
    else:
        config = FuyukiConfig.default()
    
    if args.interval is not None:
        config.cycle_interval = args.interval
    if args.max_cycles is not None:
        config.max_cycles = args.max_cycles
    
    # Команды
    if args.status:
        cmd_status(config)
    elif args.report:
        cmd_report(config)
    elif args.character:
        cmd_character(config)
    elif args.knowledge:
        cmd_knowledge(config)
    else:
        cmd_run(config)


if __name__ == "__main__":
    main()
