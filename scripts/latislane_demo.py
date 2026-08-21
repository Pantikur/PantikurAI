"""
Latislane — Демонстрация работы системы.

Запуск:
    python latislane_demo.py
"""

import asyncio
import sys
import io
from pathlib import Path

# Исправление кодировки Windows
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

# Добавляем корень проекта в путь
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from latislane import LatislaneCore, BodyType


async def demo_basic():
    """Базовая демонстрация."""
    print("=" * 60)
    print("🧬 LATISLANE — ДЕМОНСТРАЦИЯ")
    print("=" * 60)
    print()
    
    # 1. Инициализация
    print("📦 Инициализация LatislaneCore...")
    core = LatislaneCore(project_root=str(project_root), demo_mode=True)
    print("✅ Инициализация завершена")
    print()
    
    # 2. Статус системы
    print("📊 Статус системы:")
    status = core.get_system_status()
    print(f"   Модулей тела: {status['modules_count']}")
    print(f"   Узлов знаний: {status['learning_report']['knowledge_nodes']}")
    print(f"   Прогресс обучения: {status['learning_report']['overall_progress']*100:.1f}%")
    print()
    
    # 3. Изучение анатомии
    print("📖 Запуск изучения анатомии...")
    core.start_anatomy_study()
    print("✅ Определение пробелов завершено")
    print()
    
    # 4. Цикл обучения
    print("🔄 Запуск цикла обучения...")
    results = await core.run_study_cycle(batch_size=3)
    print(f"✅ Цикл завершён")
    print()
    
    # 4.5. Статус эволюции
    print("🧬 Статус эволюции:")
    evolution = core.evolution.get_evolution_report()
    print(f"   Этап: {evolution['stage_details'][0]['stage']}")
    print(f"   Прогресс: {evolution['overall_progress']*100:.1f}%")
    print()
    
    # 5. Отчёт по анатомии
    print("📚 Отчёт по анатомии:")
    anatomy = core.get_anatomy_report()
    for name, mod in list(anatomy["modules"].items())[:5]:
        progress = mod["research_progress"] * 100
        print(f"   - {name}: {progress:.0f}%")
    print(f"   Общий прогресс: {anatomy['overall_progress']*100:.1f}%")
    print()
    
    # 6. Проектирование тел
    print("🤖 Проектирование механического тела...")
    mech = core.design_mechanical_body("Mechanical-Alpha")
    print(f"   ✅ Создано: {mech.name}")
    print(f"   Модулей: {len(mech.modules)}")
    print(f"   Завершённость: {mech.calculate_completeness()*100:.1f}%")
    print()
    
    print("🦾 Проектирование бионического тела...")
    bionic = core.design_bionic_body("Bionic-Beta")
    print(f"   ✅ Создано: {bionic.name}")
    print()
    
    print("🧬 Проектирование органического тела...")
    organic = core.design_organic_body("Organic-Gamma")
    print(f"   ✅ Создано: {organic.name}")
    print()
    
    # 7. Чат с Латислейн
    print("💬 Чат с Латислейн:")
    print()
    
    questions = [
        "какой прогресс изучения анатомии?",
        "расскажи о механических телах",
        "статус системы",
    ]
    
    for q in questions:
        response = core.chat_response(q)
        print(f"Вопрос: {q}")
        print(f"Ответ:\n{response}\n")
        print("-" * 60)
        print()
    
    # 8. Итоговая статистика
    print("📈 Итоговая статистика:")
    final_status = core.get_system_status()
    print(f"   Тел спроектировано: {final_status['system_state']['total_bodies_designed']}")
    print(f"   Циклов обучения: {final_status['system_state']['total_research_cycles']}")
    print(f"   Узлов знаний: {final_status['learning_report']['knowledge_nodes']}")
    print()
    
    print("=" * 60)
    print("✅ ДЕМОНСТРАЦИЯ ЗАВЕРШЕНА")
    print("=" * 60)


async def demo_evolution():
    """Демонстрация эволюции."""
    print("=" * 60)
    print("🧬 LATISLANE — ЭВОЛЮЦИЯ")
    print("=" * 60)
    print()
    
    core = LatislaneCore(project_root=str(project_root), demo_mode=True)
    
    print("📊 Начальный статус эволюции:")
    evolution = core.evolution.get_evolution_report()
    print(f"   Этап: {evolution['stage_details'][0]['stage']}")
    print(f"   Номер: {evolution['stage_number']}/{evolution['total_stages']}")
    print()
    
    # Имитация изучения тем для перехода к следующему этапу
    print("📚 Изучение тем для механического этапа...")
    topics_mech = [
        "prosthetics design principles",
        "robotic exoskeleton human",
        "biomechanics human movement",
        "titanium alloy materials",
        "servo motor systems",
    ]
    await core.run_study_cycle(topics=topics_mech, batch_size=5)
    print()
    
    print("📊 После изучения механических тем:")
    evolution = core.evolution.get_evolution_report()
    for stage in evolution["stage_details"][:3]:
        icon = "✅" if stage["completed"] else "🔵" if stage["is_current"] else "⚪"
        print(f"   {icon} {stage['stage']}: {stage['progress']*100:.0f}%")
    print()
    
    # Принудительный переход
    print("🚀 Принудительный переход к следующему этапу...")
    learned = len(core.learning_engine.topic_progress)
    if core.evolution.can_advance(learned):
        core.evolution.advance(reason="demo_manual")
        print(f"   ✅ Переход: {core.evolution.current_stage.value}")
    print()
    
    print("=" * 60)
    print("✅ ЭВОЛЮЦИЯ ЗАВЕРШЕНА")
    print("=" * 60)


async def demo_advanced():
    """Расширенная демонстрация."""
    print("=" * 60)
    print("🧬 LATISLANE — РАСШИРЕННАЯ ДЕМОНСТРАЦИЯ")
    print("=" * 60)
    print()
    
    core = LatislaneCore(project_root=str(project_root), demo_mode=True)
    
    # Пакетное обучение
    print("🔄 Пакетное обучение по конкретным темам...")
    topics = [
        "human skeletal system anatomy",
        "human nervous system neuroanatomy",
        "3d bioprinting organs",
    ]
    await core.run_study_cycle(topics=topics, batch_size=3)
    print("✅ Пакетное обучение завершено")
    print()
    
    # Изучение отчёт
    print("📊 Отчёт об обучении:")
    report = core.learning_engine.get_learning_report()
    for topic, progress in list(report["topic_details"].items())[:5]:
        print(f"   - {topic}: {progress*100:.1f}%")
    print()
    
    # Экспорт данных
    print("📤 Экспорт данных...")
    export_dir = core.export_all()
    print(f"   ✅ Экспортировано в: {export_dir}")
    print()
    
    print("=" * 60)
    print("✅ РАСШИРЕННАЯ ДЕМОНСТРАЦИЯ ЗАВЕРШЕНА")
    print("=" * 60)


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Latislane Demo")
    parser.add_argument("--advanced", action="store_true", help="Расширенная демонстрация")
    parser.add_argument("--evolution", action="store_true", help="Демонстрация эволюции")
    args = parser.parse_args()
    
    if args.evolution:
        asyncio.run(demo_evolution())
    elif args.advanced:
        asyncio.run(demo_advanced())
    else:
        asyncio.run(demo_basic())
