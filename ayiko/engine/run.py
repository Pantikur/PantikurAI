"""
Точка входа для запуска автономного ядра Айко.

Использование:
    python -m ayiko.engine.run              # постоянная работа
    python -m ayiko.engine.run --demo       # демо-режим (5 циклов)
    python -m ayiko.engine.run --generate   # только генерация (1 цикл арта)
    python -m ayiko.engine.run --analyze    # только анализ референсов ojidania
    python -m ayiko.engine.run --status     # показать состояние
"""

from __future__ import annotations
import argparse
import json
import sys
from pathlib import Path

# Добавляем текущую директорию и корень проекта в path
_script_dir = Path(__file__).parent.resolve()
_project_root = _script_dir.parent.parent.resolve()
for _p in (_script_dir, _project_root):
    if str(_p) not in sys.path:
        sys.path.insert(0, str(_p))

# Принудительный UTF-8 для вывода (Windows-консоль использует cp1251)
for _stream in (sys.stdout, sys.stderr):
    _reconfigure = getattr(_stream, "reconfigure", None)
    if _reconfigure is not None:
        _reconfigure(encoding="utf-8")

from ayiko.engine.config import AyikoConfig
from ayiko.engine.ayiko_core import AyikoCore


def cmd_run(config: AyikoConfig):
    """Запустить постоянную работу Айко."""
    core = AyikoCore(config)
    core.run()


def cmd_generate(config: AyikoConfig):
    """Только генерация изображений (без полного цикла)."""
    print("=" * 60)
    print("🎨 ГЕНЕРАЦИЯ ИЗОБРАЖЕНИЙ АЙКО")
    print("=" * 60)

    from ayiko.art_engine import AyikoArtEngine
    engine = AyikoArtEngine(
        output_dir=str(config.art_output_dir),
        references_dir=str(config.references_dir),
        analysis_dir=str(config.references_analysis_dir),
    )

    print("\n1. Пиксель-арт...")
    p1 = engine.generate_pixel_art()
    print(f"   ✅ {p1}")

    print("\n2. Техническая графика...")
    p2 = engine.generate_technical()
    print(f"   ✅ {p2}")

    print("\n3. 3D-рендер...")
    p3 = engine.generate_3d()
    print(f"   ✅ {p3}")

    print("\n4. Сцена/пейзаж...")
    p4 = engine.generate_scene()
    print(f"   ✅ {p4}")

    print("\n📊 Статистика:", engine.get_stats())


def cmd_analyze_references(config: AyikoConfig):
    """Только анализ референсов из папки ojidania."""
    print("=" * 60)
    print("📸 АНАЛИЗ РЕФЕРЕНСОВ (ojidania)")
    print("=" * 60)

    from ayiko.art_engine import AyikoArtEngine
    engine = AyikoArtEngine(
        output_dir=str(config.art_output_dir),
        references_dir=str(config.references_dir),
        analysis_dir=str(config.references_analysis_dir),
    )

    result = engine.analyze_references(limit=50)
    print(f"\nРезультат: {json.dumps(result, ensure_ascii=False, indent=2)}")
    print(f"\n📊 Статистика: {engine.get_stats()}")


def cmd_status(config: AyikoConfig):
    """Показать текущее состояние Айко."""
    state_path = config.state_path

    if not state_path.exists():
        print("Айко ещё не запускалась. Состояние отсутствует.")
        return

    with open(state_path, "r", encoding="utf-8") as f:
        state = json.load(f)

    print("=" * 60)
    print("📊 СОСТОЯНИЕ АЙКО")
    print("=" * 60)
    print(f"Версия: {state.get('version', '?')}")
    print(f"Циклов выполнено: {state.get('cycle_count', 0)}")
    print(f"Последнее обновление: {state.get('timestamp', '?')}")
    print()
    print("Метрики:")
    for key, value in state.get("metrics", {}).items():
        print(f"  {key}: {value}")


def main():
    parser = argparse.ArgumentParser(
        description="Айко — автономный творческий ИИ (пиксель-арт, графика, 3D)",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__
    )

    parser.add_argument("--demo", action="store_true",
                        help="Демо-режим: 5 циклов с короткими интервалами")
    parser.add_argument("--generate", action="store_true",
                        help="Только генерация изображений (1 цикл арта)")
    parser.add_argument("--analyze", action="store_true",
                        help="Только анализ референсов из ojidania")
    parser.add_argument("--status", action="store_true",
                        help="Показать текущее состояние")
    parser.add_argument("--interval", type=float, default=None,
                        help="Интервал между циклами в секундах")
    parser.add_argument("--max-cycles", type=int, default=None,
                        help="Максимальное количество циклов")

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
    if args.generate:
        cmd_generate(config)
    elif args.analyze:
        cmd_analyze_references(config)
    elif args.status:
        cmd_status(config)
    else:
        cmd_run(config)


if __name__ == "__main__":
    main()
