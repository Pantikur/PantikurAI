"""
Точка входа для запуска автономного ядра Нобука.

Использование:
    python -m nobuka.engine.run              # постоянная работа
    python -m nobuka.engine.run --demo       # демо-режим (5 циклов)
    python -m nobuka.engine.run --analyze    # только анализ проекта
    python -m nobuka.engine.run --tests      # только тестирование
    python -m nobuka.engine.run --status     # показать состояние
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

from nobuka.engine.config import NobukaConfig
from nobuka.engine.nobuka_core import NobukaCore
from nobuka.engine.code_analyzer import CodeAnalyzer
from nobuka.engine.test_runner import TestRunner


def cmd_run(config: NobukaConfig):
    """Запустить постоянную работу Нобука."""
    core = NobukaCore(config)
    core.run()


def cmd_analyze(config: NobukaConfig):
    """Запустить только анализ проекта."""
    print("=" * 60)
    print("📊 АНАЛИЗ КОДОВОЙ БАЗЫ НОБУКИ")
    print("=" * 60)

    analyzer = CodeAnalyzer(config)
    all_analyses = []
    total_issues = 0

    for dir_name in config.scan_directories:
        dir_path = Path(dir_name)
        if not dir_path.exists():
            continue

        files = analyzer._scan_files(dir_path)
        print(f"\n📁 {dir_name}: {len(files)} файлов")

        for file_path in files[:20]:  # Лимит для демо
            analysis = analyzer.analyze_file(file_path)
            all_analyses.append(analysis)
            total_issues += len(analysis.issues)

            if analysis.issues:
                print(f"  ⚠️  {file_path.name}: {len(analysis.issues)} проблем")
                for issue in analysis.issues[:3]:
                    print(f"     - {issue}")

    print(f"\n📊 ИТОГО: {len(all_analyses)} файлов, {total_issues} проблем")

    # Показать лучших и худших
    if all_analyses:
        sorted_by_complexity = sorted(all_analyses, key=lambda a: a.complexity, reverse=True)
        sorted_by_lines = sorted(all_analyses, key=lambda a: a.lines, reverse=True)

        print(f"\n🔝 Самая сложная: {sorted_by_complexity[0].path} (C={sorted_by_complexity[0].complexity})")
        print(f"📏 Самый длинный: {sorted_by_lines[0].path} ({sorted_by_lines[0].lines} строк)")


def cmd_tests(config: NobukaConfig):
    """Запустить только тестирование."""
    print("=" * 60)
    print("🧪 ТЕСТИРОВАНИЕ НОБУКИ")
    print("=" * 60)

    runner = TestRunner(config)
    report = runner.run_pytest()

    print(f"\n📊 Результат:")
    print(f"  Всего тестов: {report.total}")
    print(f"  Пройдено: {report.passed}")
    print(f"  Провалено: {report.failed}")
    print(f"  Покрытие: {report.coverage:.1f}%")
    print(f"  Время: {report.duration_seconds:.1f}с")


def cmd_status(config: NobukaConfig):
    """Показать текущее состояние Нобука."""
    state_path = config.state_path

    if not state_path.exists():
        print("Нобука ещё не запускалась. Состояние отсутствует.")
        return

    with open(state_path, "r", encoding="utf-8") as f:
        state = json.load(f)

    print("=" * 60)
    print("📊 СОСТОЯНИЕ НОБУКИ")
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
        description="Нобука — автономная система улучшений и модернизации",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__
    )

    parser.add_argument(
        "--demo",
        action="store_true",
        help="Демо-режим: 5 циклов с короткими интервалами"
    )
    parser.add_argument(
        "--analyze",
        action="store_true",
        help="Запустить только анализ проекта"
    )
    parser.add_argument(
        "--tests",
        action="store_true",
        help="Запустить только тестирование"
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
        config = NobukaConfig.demo()
    else:
        config = NobukaConfig.default()

    if args.interval is not None:
        config.cycle_interval = args.interval
    if args.max_cycles is not None:
        config.max_cycles = args.max_cycles

    # Команды
    if args.status:
        cmd_status(config)
    elif args.analyze:
        cmd_analyze(config)
    elif args.tests:
        cmd_tests(config)
    else:
        cmd_run(config)


if __name__ == "__main__":
    main()
