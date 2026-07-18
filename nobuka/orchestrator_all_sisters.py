#!/usr/bin/env python3
"""
Нобука — Оркестратор полного цикла улучшений.
Запускает тестовый режим для всех 12 девочек проекта.

Использование:
    python nobuka/orchestrator_all_sisters.py
    python nobuka/orchestrator_all_sisters.py --count 6   # Только первые 6
    python nobuka/orchestrator_all_sisters.py --sister hanako  # Только Ханако
    python nobuka/orchestrator_all_sisters.py --help
"""

import sys
import os
import json
from pathlib import Path
from datetime import datetime

# Добавляем корень проекта в path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from nobuka.engine.test_mode_creation import (
    run_test_mode_cycle,
    ImprovementCreator,
    SandboxManager
)


def print_banner():
    """Вывод приветственного баннера."""
    print()
    print("╔═══════════════════════════════════════════════════════════╗")
    print("║                                                           ║")
    print("║   ██████╗ ██╗   ██╗██████╗ ████████╗███████╗             ║")
    print("║   ██╔══██╗██║   ██║██╔══██╗╚══██╔══╝██╔════╝            ║")
    print("║   ██████╔╝██║   ██║██████╔╝   ██║   █████╗              ║")
    print("║   ██╔═══╝ ██║   ██║██╔══██╗   ██║   ██╔══╝              ║")
    print("║   ██║     ╚██████╔╝██║  ██║   ██║   ███████╗            ║")
    print("║   ╚═╝      ╚═════╝ ╚═╝  ╚═╝   ╚═╝   ╚══════╝           ║")
    print("║                                                           ║")
    print("║   Оркестратор Полного Цикла Улучшений                    ║")
    print("║   Версия: v2.0.0                                          ║")
    print("║   Статус: АКТИВЕН                                         ║")
    print("║                                                           ║")
    print("╚═══════════════════════════════════════════════════════════╝")
    print()


def print_sisters_list():
    """Вывод списка всех девочек."""
    print("📋 ВСЕ 12 ДЕВОЧЕК ПРОЕКТА:")
    print("─" * 60)
    for i, (key, zone) in enumerate(ImprovementCreator.ZONES.items(), 1):
        print(f"  {i:2d}. {zone['emoji']} {zone['name']:10s} — {zone['focus']}")
    print("─" * 60)
    print()


def run_for_all(count: int = 12):
    """Запуск для всех (или N) девочек."""
    print_banner()
    print_sisters_list()
    
    print(f"🚀 Запуск цикла для {count} девочек...")
    print()
    
    report = run_test_mode_cycle(
        target_sister=None,
        improvement_type=None,
        apply_passed=True,
        sisters_count=count
    )
    
    return report


def run_for_sister(sister_key: str):
    """Запуск для конкретной девочки."""
    print_banner()
    
    if sister_key not in ImprovementCreator.ZONES:
        print(f"❌ Неизвестная девочка: {sister_key}")
        print("\nДоступные:")
        for key in ImprovementCreator.ZONES:
            print(f"  - {key}")
        return
    
    zone = ImprovementCreator.ZONES[sister_key]
    print(f"🎯 Запуск для: {zone['emoji']} {zone['name']}")
    print(f"   Зона: {zone['focus']}")
    print()
    
    report = run_test_mode_cycle(
        target_sister=sister_key,
        improvement_type=None,
        apply_passed=True,
        sisters_count=1
    )
    
    return report


def run_with_improvement(sister_key: str, improvement_type: str):
    """Запуск для конкретной девочки с конкретным типом улучшения."""
    print_banner()
    
    if sister_key not in ImprovementCreator.ZONES:
        print(f"❌ Неизвестная девочка: {sister_key}")
        return
    
    zone = ImprovementCreator.ZONES[sister_key]
    print(f"🎯 Запуск для: {zone['emoji']} {zone['name']}")
    print(f"   Улучшение: {improvement_type}")
    print()
    
    report = run_test_mode_cycle(
        target_sister=sister_key,
        improvement_type=improvement_type,
        apply_passed=True,
        sisters_count=1
    )
    
    return report


def print_summary(report: dict):
    """Вывод итоговой сводки."""
    if not report:
        return
    
    totals = report.get("totals", {})
    
    print()
    print("╔═══════════════════════════════════════════════════════════╗")
    print("║                    ИТОГОВАЯ СВОДКА                       ║")
    print("╠═══════════════════════════════════════════════════════════╣")
    print(f"║   Создано файлов:    {totals.get('created', 0):>5d}              ║")
    print(f"║   Пройдено тестов:   {totals.get('passed', 0):>5d}              ║")
    print(f"║   Провалено тестов:  {totals.get('failed', 0):>5d}              ║")
    print(f"║   Применено:         {totals.get('applied', 0):>5d}              ║")
    print("╠═══════════════════════════════════════════════════════════╣")
    
    by_sister = report.get("by_sister", {})
    if by_sister:
        print("║   ПО ДЕВОЧКАМ:                                          ║")
        print("║   ─────────────                                         ║")
        for key, stats in by_sister.items():
            zone = ImprovementCreator.ZONES.get(key, {})
            emoji = zone.get("emoji", "❓")
            name = zone.get("name", key)
            print(f"║   {emoji} {name:10s} — Создано: {stats['total']:>2d}  "
                  f"✅: {stats['passed']:>2d}  ❌: {stats['failed']:>2d}  "
                  f"📦: {stats['applied']:>2d}")
    
    print("╚═══════════════════════════════════════════════════════════╝")
    print()


def main():
    """Основная функция."""
    args = sys.argv[1:]
    
    if "--help" in args or "-h" in args:
        print("Использование:")
        print('  python orchestrator_all_sisters.py                     # Все 12')
        print('  python orchestrator_all_sisters.py --count 6           # 6 девочек')
        print('  python orchestrator_all_sisters.py --sister hanako     # Ханако')
        print('  python orchestrator_all_sisters.py --improve hanako gravity_calculator')
        print('  python orchestrator_all_sisters.py --help              # Справка')
        return
    
    # Парсинг аргументов
    if "--sister" in args:
        idx = args.index("--sister")
        if idx + 1 < len(args):
            run_for_sister(args[idx + 1])
            return
    
    if "--improve" in args:
        idx = args.index("--improve")
        if idx + 2 < len(args):
            run_with_improvement(args[idx + 1], args[idx + 2])
            return
    
    count = 12
    if "--count" in args:
        idx = args.index("--count")
        if idx + 1 < len(args):
            try:
                count = int(args[idx + 1])
            except ValueError:
                count = 12
    
    report = run_for_all(count)
    print_summary(report)


if __name__ == "__main__":
    main()
