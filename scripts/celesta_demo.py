"""
Celesta — Демонстрация работы системы.

Запуск:
    python celesta_demo.py
"""

import asyncio
import sys
import io
from pathlib import Path

# Исправление кодировки Windows
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from celesta import CelestaCore


async def demo_basic():
    """Базовая демонстрация."""
    print("=" * 60)
    print("🌹 CELESTA — ДЕМОНСТРАЦИЯ")
    print("=" * 60)
    print()
    
    # 1. Инициализация
    print("📦 Инициализация CelestaCore...")
    core = CelestaCore(project_root=str(project_root), demo_mode=True)
    print("✅ Инициализация завершена")
    print()
    
    # 2. Статус системы
    print("📊 Статус системы:")
    status = core.get_system_status()
    print(f"   Модулей интимных знаний: {status['modules_count']}")
    print(f"   Узлов знаний: {status['learning_report']['knowledge_nodes']}")
    print(f"   Прогресс обучения: {status['learning_report']['overall_progress']*100:.1f}%")
    print()
    
    # 3. Изучение интимной жизни
    print("📖 Запуск изучения интимной жизни...")
    core.start_intimacy_study()
    print("✅ Определение пробелов завершено")
    print()
    
    # 4. Цикл обучения
    print("🔄 Запуск цикла обучения...")
    await core.run_study_cycle(batch_size=3)
    print(f"✅ Цикл завершён")
    print()
    
    # 5. Отчёт по интимным знаниям
    print("📚 Отчёт по интимной жизни:")
    report = core.get_intimacy_report()
    for name, mod in list(report["modules"].items())[:5]:
        progress = mod["research_progress"] * 100
        print(f"   - {name}: {progress:.0f}%")
    print(f"   Общий прогресс: {report['overall_progress']*100:.1f}%")
    print()
    
    # 6. Детали по этапам
    from celesta.intimacy_modules import IntimacyStage
    
    print("📋 Детали по этапам:")
    for stage in IntimacyStage:
        details = core.get_stage_details(stage)
        kp_count = len(details["knowledge_points"])
        print(f"   - {stage.value}: {kp_count} точек знаний")
    print()
    
    # 7. Последствия
    print("⚠️ Последствия избыточного интима:")
    excessive = core.get_consequences_info("excessive")
    print(f"   Модулей: {len(excessive['modules'])}")
    print(f"   Точек знаний: {len(excessive['knowledge_points'])}")
    print()
    
    print("🚫 Последствия прерванного процесса:")
    interrupted = core.get_consequences_info("interrupted")
    print(f"   Модулей: {len(interrupted['modules'])}")
    print(f"   Точек знаний: {len(interrupted['knowledge_points'])}")
    print()
    
    # 8. Особенности рас
    print("🌍 Особенности рас:")
    for race in ["human", "elf", "demon", "undead", "elemental"]:
        info = core.get_race_specific_info(race)
        if info:
            print(f"   - {race}: изучено")
        else:
            print(f"   - {race}: нет данных")
    print()
    
    # 9. Чат с Селестой
    print("💬 Чат с Селестой:")
    print()
    
    questions = [
        "какой прогресс изучения интимной жизни?",
        "расскажи о прикосновениях",
        "какие последствия избыточного интима?",
        "что бывает при прерванном процессе?",
        "статус системы",
    ]
    
    for q in questions:
        response = core.chat_response(q)
        print(f"Вопрос: {q}")
        print(f"Ответ:\n{response[:300]}...")
        print()
        print("-" * 60)
        print()
    
    # 10. Итоговая статистика
    print("📈 Итоговая статистика:")
    final_status = core.get_system_status()
    print(f"   Циклов обучения: {final_status['system_state']['total_research_cycles']}")
    print(f"   Узлов знаний: {final_status['learning_report']['knowledge_nodes']}")
    print()
    
    print("=" * 60)
    print("✅ ДЕМОНСТРАЦИЯ ЗАВЕРШЕНА")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(demo_basic())
