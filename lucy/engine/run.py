"""
Точка входа для запуска автономного ядра Люси.

Использование:
    python -m lucy.engine.run              # постоянная работа
    python -m lucy.engine.run --demo       # демо-режим (10 циклов)
    python -m lucy.engine.run --status     # показать состояние
    python -m lucy.engine.run --report     # показать отчёты
    python -m lucy.engine.run --character  # показать характер
    python -m lucy.engine.run --knowledge  # показать знания
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

from config import LucyConfig
from lucy_core import LucyCore


def cmd_run(config: LucyConfig):
    """Запустить постоянную работу Люси."""
    core = LucyCore(config)
    core.run()


def cmd_status(config: LucyConfig):
    """Показать текущее состояние Люси."""
    from lucy.engine.config import LucyConfig
    from lucy.engine.models import KnowledgeLevel, CharacterTraits
    
    config = LucyConfig.default()
    core = LucyCore(config)
    
    status = core.get_status()
    
    print("\n" + "=" * 60)
    print("⚙️ СОСТОЯНИЕ ЛЮСИ")
    print("=" * 60)
    print(f"Версия: {status['version']}")
    print(f"Циклов выполнено: {status['cycle_count']}")
    print()
    print("📊 Метрики:")
    for key, value in status['metrics'].items():
        print(f"  {key}: {value}")
    print()
    
    # Уровень знаний
    level = status['knowledge_level']
    print(f"📚 Уровень знаний: Lvl {level['current_level']} — {level['level_name']}")
    print(f"   Опыт: {level['current_xp']} XP")
    print()
    
    # Характер
    char = status['character']
    print("⚙️ Характер Люси:")
    print()
    print(f"  🌡️  Темперамент: {char['temperament']}")
    print(f"  🤝 Социальность: {char['sociality']}")
    print(f"  💭 Эмоциональность: {char['emotionality']}")
    print(f"  🌅 Мировоззрение: {char['worldview']}")
    print(f"  👑 Доминирование: {char['dominance']}")
    print(f"  🔄 Перемены: {char['change_attitude']}")
    print(f"  🌀 Сложность: {char['complexity']}")
    print()
    print(f"  🔥 Страсть к двигателям: {int(char['specialty_passion'] * 100)}%")
    print(f"  🔍 Любознательность: {int(char['curiosity'] * 100)}%")
    print(f"  ⚔️  Смелость: {int(char['courage'] * 100)}%")
    print(f"  🧘  Терпение: {int(char['patience'] * 100)}%")
    print(f"  🎨 Креативность: {int(char['creativity'] * 100)}%")
    print(f"  🤝 Сотрудничество: {int(char['collaboration'] * 100)}%")
    print()
    
    print(f"🔬 Теорий построено: {status['theories_count']}")
    print(f"🧮 Вычислений выполнено: {status['calculations_count']}")
    print(f"📖 Статей изучено: {status['papers_count']}")


def cmd_report(config: LucyConfig):
    """Показать отчёты."""
    reports_dir = config.reports_dir
    
    if not reports_dir.exists():
        print("Отчёты отсутствуют.")
        return
    
    reports = list(reports_dir.glob("*.json"))
    if not reports:
        print("Отчёты отсутствуют.")
        return
    
    print(f"\n📝 ОТЧЁТЫ ЛЮСИ ({len(reports)}):")
    print("=" * 60)
    
    for report_path in sorted(reports)[-10:]:  # Последние 10
        try:
            with open(report_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            print(f"\n📄 {report_path.name}")
            print(f"   Цикл: {data.get('cycle', 'N/A')}")
            print(f"   Теорий: {data.get('theories_count', 0)}")
            print(f"   Вычислений: {data.get('calculations_count', 0)}")
            print(f"   Статей: {data.get('papers_count', 0)}")
        except:
            pass


def cmd_character(config: LucyConfig):
    """Показать характер."""
    character_file = config.character_file
    
    if not character_file.exists():
        print("Характер не создан.")
        return
    
    with open(character_file, "r", encoding="utf-8") as f:
        data = json.load(f)
    
    print("\n💪 ХАРАКТЕР ЛЮСИ")
    print("=" * 60)
    print(json.dumps(data, ensure_ascii=False, indent=2))


def cmd_knowledge(config: LucyConfig):
    """Показать знания."""
    from lucy.engine.knowledge_manager import KnowledgeManager
    
    knowledge_file = config.knowledge_dir / "knowledge_base.json"
    level_file = config.knowledge_dir / "knowledge_level.json"
    
    if not knowledge_file.exists():
        print("База знаний пуста.")
        return
    
    with open(knowledge_file, "r", encoding="utf-8") as f:
        data = json.load(f)
    
    print("\n📚 ЗНАНИЯ ЛЮСИ")
    print("=" * 60)
    print(f"Фактов: {len(data.get('facts', []))}")
    print(f"Формул: {len(data.get('formulas', []))}")
    print(f"Теорий: {len(data.get('theories', []))}")
    
    # Уровень
    if level_file.exists():
        with open(level_file, "r", encoding="utf-8") as f:
            level_data = json.load(f)
        print(f"\nУровень: Lvl {level_data.get('current_level', 1)} — {level_data.get('level_name', 'Механик')}")
        print(f"Опыт: {level_data.get('current_xp', 0)} XP")


def main():
    parser = argparse.ArgumentParser(
        description="Люси — автономный инженер двигателей и гравитационной пропульсии",
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
        help="Показать отчёты"
    )
    parser.add_argument(
        "--character",
        action="store_true",
        help="Показать характер"
    )
    parser.add_argument(
        "--knowledge",
        action="store_true",
        help="Показать знания"
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
    
    # Команды
    if args.knowledge:
        cmd_knowledge(config)
    elif args.character:
        cmd_character(config)
    elif args.report:
        cmd_report(config)
    elif args.status:
        cmd_status(config)
    else:
        cmd_run(config)


if __name__ == "__main__":
    main()
