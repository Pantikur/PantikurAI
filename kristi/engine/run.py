"""
Точка входа для запуска автономного ядра Кристи.

Использование:
    python -m kristi.engine.run              # постоянная работа
    python -m kristi.engine.run --demo       # демо-режим (5 циклов)
    python -m kristi.engine.run --produce    # только производство (1 цикл)
    python -m kristi.engine.run --script     # только сценарии и раскадровки
    python -m kristi.engine.run --analyze    # только анализ
    python -m kristi.engine.run --status     # показать состояние
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

from kristi.engine.config import KristiConfig
from kristi.engine.kristi_core import KristiCore


def cmd_run(config: KristiConfig):
    """Запустить постоянную работу Кристи."""
    core = KristiCore(config)
    core.run()


def cmd_produce(config: KristiConfig):
    """Только производство видео (без полного цикла)."""
    print("=" * 60)
    print("🎬 ПРОИЗВОДСТВО ВИДЕО КРИСТИ")
    print("=" * 60)
    
    core = KristiCore(config)
    
    # Быстрый цикл производства
    stages = [
        ("Концепция", core._develop_concept),
        ("Сценарий", core._write_script),
        ("Раскадровка", core._create_storyboard),
        ("Режиссура", core._direct_scene),
        ("Монтаж", core._edit_video),
        ("Звук", core._design_sound),
        ("Цветокоррекция", core._color_grade),
        ("Рендер", core._render_video),
    ]
    
    for stage_name, stage_func in stages:
        print(f"\n{stage_name}...")
        try:
            stage_func()
            print(f"   ✅ {stage_name} завершён")
        except Exception as e:
            print(f"   ⚠️ {stage_name}: {e}")
    
    # Сохранить состояние
    core._save_state()
    print(f"\n📊 Статистика: {json.dumps(core.state.metrics, ensure_ascii=False, indent=2)}")


def cmd_script(config: KristiConfig):
    """Только сценарии и раскадровки."""
    print("=" * 60)
    print("📋 СЦЕНАРИИ И РАСКАДРОВКИ КРИСТИ")
    print("=" * 60)
    
    core = KristiCore(config)
    
    print("\n1. Написание сценария...")
    core._write_script()
    print("   ✅ Сценарий написан")
    
    print("\n2. Создание раскадровки...")
    core._create_storyboard()
    print("   ✅ Раскадровка создана")
    
    core._save_state()
    print(f"\n📊 Статистика: {json.dumps(core.state.metrics, ensure_ascii=False, indent=2)}")


def cmd_analyze(config: KristiConfig):
    """Только анализ и изучение."""
    print("=" * 60)
    print("🌐 АНАЛИЗ И ИЗУЧЕНИЕ КРИСТИ")
    print("=" * 60)
    
    core = KristiCore(config)
    
    print("\n1. Поиск в интернете...")
    core._web_search()
    print("   ✅ Поиск завершён")
    
    print("\n2. Получение знаний...")
    core._gain_knowledge()
    core._gain_knowledge()
    print("   ✅ Знания получены")
    
    core._save_state()
    print(f"\n📊 Статистика: {json.dumps(core.state.metrics, ensure_ascii=False, indent=2)}")


def cmd_status(config: KristiConfig):
    """Показать текущее состояние Кристи."""
    state_path = config.state_path
    
    if not state_path.exists():
        print("Кристи ещё не запускалась. Состояние отсутствует.")
        return
    
    with open(state_path, "r", encoding="utf-8") as f:
        state = json.load(f)
    
    print("=" * 60)
    print("📊 СОСТОЯНИЕ КРИСТИ")
    print("=" * 60)
    print(f"Версия: {state.get('version', '?')}")
    print(f"Циклов выполнено: {state.get('cycle_count', 0)}")
    print(f"Последнее обновление: {state.get('timestamp', '?')}")
    print()
    
    level = state.get('level_progress', {})
    print(f"Уровень: {level.get('current_level', '?')} — {level.get('level_name', '?')}")
    print(f"XP: {level.get('current_xp', 0)}")
    print()
    
    print("Метрики:")
    for key, value in state.get("metrics", {}).items():
        print(f"  {key}: {value}")
    
    print()
    print("Активные проекты:")
    for project in state.get("active_projects", [])[:5]:
        print(f"  📹 {project.get('title', '?')} [{project.get('stage', '?')}]")
    
    print()
    print("Завершённые проекты:")
    for project in state.get("completed_projects", [])[:5]:
        print(f"  ✅ {project.get('title', '?')}")


def main():
    parser = argparse.ArgumentParser(
        description="Кристи — автономный режиссёр видеопроизводства",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__
    )
    
    parser.add_argument("--demo", action="store_true",
                        help="Демо-режим: 5 циклов с короткими интервалами")
    parser.add_argument("--produce", action="store_true",
                        help="Только производство видео (1 цикл)")
    parser.add_argument("--script", action="store_true",
                        help="Только сценарии и раскадровки")
    parser.add_argument("--analyze", action="store_true",
                        help="Только анализ и изучение")
    parser.add_argument("--status", action="store_true",
                        help="Показать текущее состояние")
    parser.add_argument("--interval", type=float, default=None,
                        help="Интервал между циклами в секундах")
    parser.add_argument("--max-cycles", type=int, default=None,
                        help="Максимальное количество циклов")
    
    args = parser.parse_args()
    
    # Конфигурация
    if args.demo:
        config = KristiConfig.demo()
    else:
        config = KristiConfig.default()
    
    if args.interval is not None:
        config.cycle_interval = args.interval
    if args.max_cycles is not None:
        config.max_cycles = args.max_cycles
    
    # Команды
    if args.produce:
        cmd_produce(config)
    elif args.script:
        cmd_script(config)
    elif args.analyze:
        cmd_analyze(config)
    elif args.status:
        cmd_status(config)
    else:
        cmd_run(config)


if __name__ == "__main__":
    main()
