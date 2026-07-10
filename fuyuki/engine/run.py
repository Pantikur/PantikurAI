"""
Точка входа для запуска автономного ядра Фуюки.

Использование:
    python -m fuyuki.engine.run              # постоянная работа
    python -m fuyuki.engine.run --demo       # демо-режим (5 циклов)
    python -m fuyuki.engine.run --research   # только изучение в интернете
    python -m fuyuki.engine.run --theories   # только построение теорий
    python -m fuyuki.engine.run --calc       # только вычисления
    python -m fuyuki.engine.run --status     # показать состояние
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

from fuyuki.engine.config import FuyukiConfig
from fuyuki.engine.fuyuki_core import FuyukiCore


def cmd_run(config: FuyukiConfig):
    """Запустить постоянную работу Фуюки."""
    core = FuyukiCore(config)
    core.run()


def cmd_research(config: FuyukiConfig):
    """Запустить только изучение в интернете."""
    print("=" * 60)
    print("⚡ ИССЛЕДОВАНИЕ АТМОСФЕРНОГО ЭЛЕКТРИЧЕСТВА")
    print("=" * 60)
    
    core = FuyukiCore(config)
    
    print("\nПоиск статей об атмосферном электричестве...")
    papers = core.web_access.search_electricity_papers()
    
    for i, paper in enumerate(papers, 1):
        print(f"\n{i}. {paper.title}")
        print(f"   Авторы: {', '.join(paper.authors[:3])}{'...' if len(paper.authors) > 3 else ''}")
        print(f"   Журнал: {paper.journal} ({paper.year})")
        print(f"   Цитирований: {paper.citations}")
        print(f"   Релевантность: {paper.relevance_score:.2f}")
    
    print(f"\n✅ Найдено статей: {len(papers)}")


def cmd_theories(config: FuyukiConfig):
    """Запустить только построение теорий."""
    print("=" * 60)
    print("🔬 ПОСТРОЕНИЕ ТЕОРИЙ АТМОСФЕРНОГО ЭЛЕКТРИЧЕСТВА")
    print("=" * 60)
    
    core = FuyukiCore(config)
    
    papers = core.web_access.search_electricity_papers()
    
    print("\nПостроение теорий...")
    for i in range(3):
        theory = core.theorist.generate_theory(papers, core.theories)
        if theory:
            print(f"\n{i+1}. {theory.name}")
            print(f"   Категория: {theory.category.value}")
            print(f"   Описание: {theory.description}")
            print(f"   Уравнения: {', '.join(theory.equations)}")
            print(f"   Научная ценность: {theory.scientific_value:.2f}")
    
    print(f"\n✅ Построено теорий: {len(core.theories)}")


def cmd_calc(config: FuyukiConfig):
    """Запустить только вычисления."""
    print("=" * 60)
    print("🧮 ЭЛЕКТРИЧЕСКИЕ ВЫЧИСЛЕНИЯ")
    print("=" * 60)
    
    core = FuyukiCore(config)
    
    from fuyuki.engine.models import CalculationType
    
    calc_types = list(CalculationType)
    
    print("\nВыполнение вычислений...")
    for calc_type in calc_types[:5]:
        calc = core.calculator.calculate(calc_type)
        if calc:
            print(f"\n{calc_type.value}:")
            print(f"   Результат: {calc.result:.6e} {calc.units}")
            print(f"   Точность: {calc.precision} знаков")
            print(f"   Уверенность: {calc.confidence:.2f}")
    
    print(f"\n✅ Выполнено вычислений: {len(calc_types)}")


def cmd_status(config: FuyukiConfig):
    """Показать состояние."""
    core = FuyukiCore(config)
    status = core.get_status()
    
    print("=" * 60)
    print("⚡ СТАТУС ФУЮКИ")
    print("=" * 60)
    print(f"Имя: {status['name']}")
    print(f"Версия: {status['version']}")
    print(f"Циклов: {status['cycle_count']}")
    print(f"\nМетрики:")
    for key, value in status['metrics'].items():
        print(f"  - {key}: {value}")
    print(f"\nТеорий: {status['theories_count']}")
    print(f"Вычислений: {status['calculations_count']}")
    print(f"Статей: {status['papers_count']}")


def main():
    parser = argparse.ArgumentParser(
        description="Фуюки — автономный исследователь атмосферного электричества"
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
        "--theories",
        action="store_true",
        help="Запустить только построение теорий"
    )
    parser.add_argument(
        "--calc",
        action="store_true",
        help="Запустить только вычисления"
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
        config = FuyukiConfig.demo()
    else:
        config = FuyukiConfig.default()
    
    if args.interval is not None:
        config.cycle_interval = args.interval
    
    if args.max_cycles is not None:
        config.max_cycles = args.max_cycles
    
    # Выполнение команды
    if args.research:
        cmd_research(config)
    elif args.theories:
        cmd_theories(config)
    elif args.calc:
        cmd_calc(config)
    elif args.status:
        cmd_status(config)
    else:
        cmd_run(config)


if __name__ == "__main__":
    main()
