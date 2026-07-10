"""
Точка входа для запуска автономного ядра Люси.

Использование:
    python -m lucy.engine.run              # постоянная работа
    python -m lucy.engine.run --demo       # демо-режим (5 циклов)
    python -m lucy.engine.run --research   # только изучение в интернете
    python -m lucy.engine.run --design     # только проектирование
    python -m lucy.engine.run --calc       # только расчёты
    python -m lucy.engine.run --status     # показать состояние
"""

from __future__ import annotations
import argparse
import json
import sys
from pathlib import Path

# Принудительный UTF-8 для вывода
for _stream in (sys.stdout, sys.stderr):
    _reconfigure = getattr(_stream, "reconfigure", None)
    if _reconfigure is not None:
        _reconfigure(encoding="utf-8")

from lucy.engine.config import LucyConfig
from lucy.engine.lucy_core import LucyCore


def cmd_run(config: LucyConfig):
    """Запустить постоянную работу Люси."""
    core = LucyCore(config)
    core.run()


def cmd_research(config: LucyConfig):
    """Запустить только изучение в интернете."""
    print("=" * 60)
    print("🚀 ИССЛЕДОВАНИЕ ДВИГАТЕЛЕЙ")
    print("=" * 60)
    
    core = LucyCore(config)
    
    print("\nПоиск статей о двигателях...")
    papers = core.web_access.search_engine_papers()
    
    for i, paper in enumerate(papers, 1):
        print(f"\n{i}. {paper.title}")
        print(f"   Авторы: {', '.join(paper.authors[:3])}{'...' if len(paper.authors) > 3 else ''}")
        print(f"   Журнал: {paper.journal} ({paper.year})")
        print(f"   Цитирований: {paper.citations}")
        print(f"   Релевантность: {paper.relevance_score:.2f}")
    
    print(f"\n✅ Найдено статей: {len(papers)}")
    print(f"✅ Теорий Ханако загружено: {len(core.hanako_theories)}")
    print(f"✅ Теорий Фуюки загружено: {len(core.fuyuki_theories)}")


def cmd_design(config: LucyConfig):
    """Запустить только проектирование."""
    print("=" * 60)
    print("⚙️ ПРОЕКТИРОВАНИЕ ДВИГАТЕЛЕЙ")
    print("=" * 60)
    
    core = LucyCore(config)
    
    print("\nПроектирование двигателей...")
    for i in range(3):
        design = core.designer.generate_design(
            core.papers,
            core.hanako_theories,
            core.fuyuki_theories
        )
        if design:
            print(f"\n{i+1}. {design.name}")
            print(f"   Тип: {design.engine_type.value}")
            print(f"   Принцип: {design.principle.value}")
            print(f"   Тяга: {design.thrust:.2f} N")
            print(f"   Удельный импульс: {design.specific_impulse:.2f} s")
            print(f"   Эффективность: {design.efficiency:.2f}")
            print(f"   Реализуемость: {design.feasibility_score:.2f}")
            
            if design.gravity_theory_used:
                print(f"   Теория Ханако: {design.gravity_theory_used}")
            if design.electricity_theory_used:
                print(f"   Теория Фуюки: {design.electricity_theory_used}")
    
    print(f"\n✅ Спроектировано двигателей: {len(core.designs)}")


def cmd_calc(config: LucyConfig):
    """Запустить только расчёты."""
    print("=" * 60)
    print("🧮 РАСЧЁТЫ ДВИГАТЕЛЕЙ")
    print("=" * 60)
    
    core = LucyCore(config)
    
    print("\nВыполнение расчётов...")
    
    # Тяга
    calc = core.calculator.calculate_thrust(10.0, 30000.0)
    print(f"\nТяга: {calc.result:.2f} {calc.units}")
    
    # Удельный импульс
    calc = core.calculator.calculate_specific_impulse(30000.0)
    print(f"Удельный импульс: {calc.result:.2f} {calc.units}")
    
    # Мощность
    calc = core.calculator.calculate_power(1000.0, 3000.0)
    print(f"Мощность: {calc.result:.2e} {calc.units}")
    
    # Эффективность
    calc = core.calculator.calculate_efficiency(1000.0, 1e9, 3000.0)
    print(f"Эффективность: {calc.result:.4f}")
    
    # Гравитационный манёвр
    calc = core.calculator.calculate_gravity_assist(5.972e24, 6.771e6, 7800.0)
    print(f"Гравитационный манёвр: {calc.result:.4f} {calc.units}")
    
    # Энергия молнии
    calc = core.calculator.calculate_lightning_energy(1e8, 30000.0, 0.0003)
    print(f"Энергия молнии: {calc.result:.2f} {calc.units}")
    
    print(f"\n✅ Выполнено расчётов: 6")


def cmd_status(config: LucyConfig):
    """Показать состояние."""
    core = LucyCore(config)
    status = core.get_status()
    
    print("=" * 60)
    print("🚀 СТАТУС ЛЮСИ")
    print("=" * 60)
    print(f"Имя: {status['name']}")
    print(f"Версия: {status['version']}")
    print(f"Циклов: {status['cycle_count']}")
    print(f"\nМетрики:")
    for key, value in status['metrics'].items():
        print(f"  - {key}: {value}")
    print(f"\nПроектов: {status['designs_count']}")
    print(f"Расчётов: {status['calculations_count']}")
    print(f"Статей: {status['papers_count']}")


def main():
    parser = argparse.ArgumentParser(
        description="Люси — автономный инженер двигателей"
    )
    
    parser.add_argument(
        "--demo",
        action="store_true",
        help="Демо-режим: 5 циклов с короткими интервалами"
    )
    parser.add_argument(
        "--research",
        action="store_true",
        help="Запустить только изучение в интернете"
    )
    parser.add_argument(
        "--design",
        action="store_true",
        help="Запустить только проектирование"
    )
    parser.add_argument(
        "--calc",
        action="store_true",
        help="Запустить только расчёты"
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
        config = LucyConfig.demo()
    else:
        config = LucyConfig.default()
    
    if args.interval is not None:
        config.cycle_interval = args.interval
    
    if args.max_cycles is not None:
        config.max_cycles = args.max_cycles
    
    # Выполнение команды
    if args.research:
        cmd_research(config)
    elif args.design:
        cmd_design(config)
    elif args.calc:
        cmd_calc(config)
    elif args.status:
        cmd_status(config)
    else:
        cmd_run(config)


if __name__ == "__main__":
    main()
