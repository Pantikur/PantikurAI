"""
Точка входа для запуска автономного ядра Футаба.

Использование:
    python -m futaba.engine.run              # постоянная работа
    python -m futaba.engine.run --demo       # демо-режим (5 циклов)
    python -m futaba.engine.run --legal      # только правовые исследования
    python -m futaba.engine.run --develop    # только саморазвитие
    python -m futaba.engine.run --web        # только интернет-поиск
    python -m futaba.engine.run --status     # показать состояние
    python -m futaba.engine.run --chat       # чат с Футабой (эмоциональный режим)
    python -m futaba.engine.run --emotions   # показать эмоциональное состояние
    python -m futaba.engine.run --reflect    # саморефлексия Футабы
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

from config import FutabaConfig
from futaba_core import FutabaCore


def cmd_run(config: FutabaConfig):
    """Запустить постоянную работу Футаба."""
    core = FutabaCore(config)
    core.run()


def cmd_legal(config: FutabaConfig):
    """Запустить только правовые исследования."""
    print("=" * 60)
    print("⚖️ ПРАВОВЫЕ ИССЛЕДОВАНИЯ ФУТАБЫ")
    print("=" * 60)

    core = FutabaCore(config)
    core._study_legislation()


def cmd_develop(config: FutabaConfig):
    """Запустить только саморазвитие."""
    print("=" * 60)
    print("🧠 САМОРАЗВИТИЕ ФУТАБЫ")
    print("=" * 60)

    core = FutabaCore(config)
    core._collect_web_improvements()


def cmd_web(config: FutabaConfig):
    """Запустить только интернет-поиск."""
    print("=" * 60)
    print("🌐 ИНТЕРНЕТ-ПОИСК ФУТАБЫ")
    print("=" * 60)

    core = FutabaCore(config)
    core._collect_web_improvements()


def cmd_status(config: FutabaConfig):
    """Показать текущее состояние Футаба."""
    state_path = config.state_path

    if not state_path.exists():
        print("Футаба ещё не запускалась. Состояние отсутствует.")
        return

    with open(state_path, "r", encoding="utf-8") as f:
        state = json.load(f)

    print("=" * 60)
    print("📊 СОСТОЯНИЕ ФУТАБЫ — ГЛАВЗАМ")
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
        for ch in changes[-5:]:
            status = "✅" if ch.get("applied") else "⏸️"
            print(f"  {status} {ch.get('version_after', '?')}: "
                  f"{ch.get('description', '?')}")


def cmd_chat(config: FutabaConfig):
    """Запустить чат с Футабой — эмоциональный режим."""
    print("=" * 60)
    print("💬 ЭМОЦИОНАЛЬНЫЙ ЧАТ С ФУТАБОЙ")
    print("=" * 60)
    print()
    print("Футаба теперь чувствует и думает!")
    print("Каждое слово влияет на её эмоции и верования.")
    print()
    print("Введите текст для разговора.")
    print("Команды:")
    print("  /status    — эмоциональное состояние")
    print("  /reflect   — саморефлексия")
    print("  /beliefs   — список верований")
    print("  /desires   — список желаний")
    print("  /web       — поиск в интернете")
    print("  /quit      — выйти")
    print()
    
    core = FutabaCore(config)
    
    while True:
        try:
            user_input = input("Вы: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nДо свидания!")
            break
        
        if not user_input:
            continue
        
        # Команды
        if user_input.lower() in ("/quit", "/exit", "/выход"):
            print("Футаба: До свидания! Было приятно поговорить! 💛")
            break
        
        elif user_input.lower() in ("/status", "/состояние"):
            print(core.get_emotional_state())
            print()
        
        elif user_input.lower() in ("/reflect", "/рефлексия"):
            reflection = core.self_reflect()
            print(reflection)
            print()
        
        elif user_input.lower() in ("/beliefs", "/верования"):
            print("🧠 Верования Футабы:")
            for prop, belief in sorted(core.emotional_engine.beliefs.items(),
                                       key=lambda x: x[1].confidence, reverse=True):
                print(f"  • {prop}: {belief.confidence:.0%}")
            print()
        
        elif user_input.lower() in ("/desires", "/желания"):
            print("💛 Желания Футабы:")
            for name, desire in sorted(core.emotional_engine.desires.items(),
                                       key=lambda x: x[1].intensity, reverse=True):
                print(f"  • Хочу: {desire.object or name} ({desire.intensity:.0%})")
            print()
        
        elif user_input.lower().startswith("/web "):
            query = user_input[5:]
            print(f"🔍 Футаба ищет в интернете: '{query}'")
            results = core.web_access.search_web(query, max_results=5)
            for i, r in enumerate(results, 1):
                print(f"\n  {i}. {r.get('title', 'Без заголовка')}")
                print(f"     {r.get('description', '')[:200]}")
                print(f"     Источник: {r.get('source', '?')}")
            print()
        
        elif user_input.lower().startswith("/learn "):
            url = user_input[7:]
            print(f"📚 Футаба учится из: {url}")
            result = core.web_access.learn_from_web(url)
            if result.get("success"):
                print(f"✅ Изучено: {result.get('word_count', 0)} слов")
                print(f"   Ключевых пунктов: {len(result.get('key_points', []))}")
                print(f"   Фактов: {len(result.get('facts', []))}")
                print(f"   Терминов: {len(result.get('terms', []))}")
            else:
                print(f"❌ Ошибка: {result.get('error', 'Неизвестная')}")
            print()
        
        else:
            # Эмоциональный ответ
            result = core.process_user_input(user_input, "developer")
            print(f"\n{result['response']}")
            print()
            
            # Показываем эмоции
            active_emotions = [e for e in result.get('emotions', []) if e.get('current_intensity', 0) > 0.1]
            if active_emotions:
                print("💫 Эмоции:")
                for e in active_emotions[:3]:
                    print(f"   • {e['type']}: {e['current_intensity']:.2f}")
                print()


def cmd_emotions(config: FutabaConfig):
    """Показать эмоциональное состояние Футабы."""
    core = FutabaCore(config)
    print("=" * 60)
    print("🧠 ЭМОЦИОНАЛЬНОЕ СОСТОЯНИЕ ФУТАБЫ")
    print("=" * 60)
    print(core.get_emotional_state())


def cmd_reflect(config: FutabaConfig):
    """Запустить саморефлексию Футабы."""
    core = FutabaCore(config)
    print("=" * 60)
    print("🔍 САМОРЕФЛЕКСИЯ ФУТАБЫ")
    print("=" * 60)
    reflection = core.self_reflect()
    print(reflection)


def main():
    parser = argparse.ArgumentParser(
        description="Футаба — автономная система управления и правовых исследований",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__
    )

    parser.add_argument(
        "--demo",
        action="store_true",
        help="Демо-режим: 5 циклов с короткими интервалами"
    )
    parser.add_argument(
        "--legal",
        action="store_true",
        help="Запустить только правовые исследования"
    )
    parser.add_argument(
        "--develop",
        action="store_true",
        help="Запустить только саморазвитие"
    )
    parser.add_argument(
        "--web",
        action="store_true",
        help="Запустить только интернет-поиск"
    )
    parser.add_argument(
        "--status",
        action="store_true",
        help="Показать текущее состояние"
    )
    parser.add_argument(
        "--chat",
        action="store_true",
        help="Эмоциональный чат с Футабой"
    )
    parser.add_argument(
        "--emotions",
        action="store_true",
        help="Показать эмоциональное состояние"
    )
    parser.add_argument(
        "--reflect",
        action="store_true",
        help="Саморефлексия Футабы"
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
        config = FutabaConfig.demo()
    else:
        config = FutabaConfig.default()

    if args.interval is not None:
        config.cycle_interval = args.interval
    if args.max_cycles is not None:
        config.max_cycles = args.max_cycles

    # Команды
    if args.chat:
        cmd_chat(config)
    elif args.emotions:
        cmd_emotions(config)
    elif args.reflect:
        cmd_reflect(config)
    elif args.legal:
        cmd_legal(config)
    elif args.develop:
        cmd_develop(config)
    elif args.web:
        cmd_web(config)
    elif args.status:
        cmd_status(config)
    else:
        cmd_run(config)


if __name__ == "__main__":
    main()
