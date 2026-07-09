"""
Точка входа для запуска автономного ядра Футаба.

Использование:
    python -m futaba.engine.run              # постоянная работа
    python -m futaba.engine.run --demo       # демо-режим (5 циклов)
    python -m futaba.engine.run --trials     # только полигон испытаний
    python -m futaba.engine.run --status     # показать состояние
"""

from __future__ import annotations
import argparse
import json
import sys
from pathlib import Path

# Принудительный UTF-8 для вывода (Windows-консоль использует cp1251)
# reconfigure доступен у io.TextIOWrapper, но Pylance видит TextIO — используем getattr
for _stream in (sys.stdout, sys.stderr):
    _reconfigure = getattr(_stream, "reconfigure", None)
    if _reconfigure is not None:
        _reconfigure(encoding="utf-8")

from futaba.engine.config import FutabaConfig
from futaba.engine.futaba_core import FutabaCore
from futaba.engine.trial_grounds import TrialGrounds


def cmd_run(config: FutabaConfig):
    """Запустить постоянную работу Футаба."""
    core = FutabaCore(config)
    core.run()


def cmd_trials(config: FutabaConfig):
    """Запустить только полигон испытаний."""
    print("=" * 60)
    print("🧪 ПОЛИГОН ИСПЫТАНИЙ ФУТАБА")
    print("=" * 60)
    
    grounds = TrialGrounds(config)
    
    print(f"\nГенерация {config.trial_worlds_per_batch} миров...")
    worlds = [grounds.generate_world() for _ in range(config.trial_worlds_per_batch)]
    
    for w in worlds:
        print(f"  • {w.name}: популяция {w.population:,}, "
              f"угрозы: {len(w.threats)}, фракций: {len(w.factions)}")
    
    print(f"\nТестирование {config.trial_versions_to_test} версий правления...")
    results = grounds.run_batch()
    
    print(f"\nПроведено {len(results)} симуляций")
    print("-" * 60)
    
    # Сравнение версий
    comparison = grounds.compare_versions(results)
    
    print("\n🏆 РЕЙТИНГ ВЕРСИЙ ПРАВЛЕНИЯ:")
    print("-" * 60)
    for i, rank in enumerate(comparison["rankings"], 1):
        medal = ["🥇", "🥈", "🥉"][i-1] if i <= 3 else f"{i}."
        print(f"  {medal} {rank['name']}")
        print(f"     Score: {rank['avg_score']:.1f} | "
              f"Эпох: {rank['avg_epochs']:.1f} | "
              f"Выживаемость: {rank['survival_rate']:.0%}")
    
    print("-" * 60)
    print(f"\n✅ Лучшая версия: {comparison['best_version']}")
    
    # Сохранить результаты
    output = {
        "comparison": comparison,
        "results": [r.to_dict() for r in results],
    }
    out_path = Path("futaba/engine/state/trials_report.json")
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False, indent=2)
    
    print(f"\n💾 Отчёт сохранён: {out_path}")


def cmd_status(config: FutabaConfig):
    """Показать текущее состояние Футаба."""
    state_path = config.state_path
    
    if not state_path.exists():
        print("Футаба ещё не запускалась. Состояние отсутствует.")
        return
    
    with open(state_path, "r", encoding="utf-8") as f:
        state = json.load(f)
    
    print("=" * 60)
    print("📊 СОСТОЯНИЕ ФУТАБА")
    print("=" * 60)
    print(f"Версия: {state.get('version', '?')}")
    print(f"Циклов выполнено: {state.get('cycle_count', 0)}")
    print(f"Последнее обновление: {state.get('timestamp', '?')}")
    print()
    print("Метрики:")
    for key, value in state.get("metrics", {}).items():
        print(f"  {key}: {value}")
    print()
    
    changes = state.get("changes_history", [])
    if changes:
        print(f"Последние изменения ({len(changes)}):")
        for change in changes[-5:]:
            status = "✅" if change.get("applied") else "⏸️"
            print(f"  {status} {change.get('version_after', '?')}: "
                  f"{change.get('description', '?')}")


def main():
    parser = argparse.ArgumentParser(
        description="Футаба — автономное ядро саморазвития",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__
    )
    
    parser.add_argument(
        "--demo",
        action="store_true",
        help="Демо-режим: 5 циклов с короткими интервалами"
    )
    parser.add_argument(
        "--trials",
        action="store_true",
        help="Запустить только полигон испытаний"
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
        help="Максимальное количество циклов (по умолчанию бесконечно)"
    )
    
    args = parser.parse_args()
    
    # Конфигурация
    if args.demo:
        config = FutabaConfig.demo()
    else:
        config = FutabaConfig.default()
    
    if args.interval is not None:
        config.cycle_interval = args.interval
    if args.max_cycles is not None:
        config.max_cycles = args.max_cycles
    
    # Команды
    if args.status:
        cmd_status(config)
    elif args.trials:
        cmd_trials(config)
    else:
        cmd_run(config)


if __name__ == "__main__":
    main()
