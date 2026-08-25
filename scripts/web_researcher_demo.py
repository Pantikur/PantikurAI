"""
WebResearcher Demo — Тест реального интернет-поиска.

Запуск:
    python web_researcher_demo.py
"""

import asyncio
import sys
import io
from pathlib import Path

# Исправление кодировки Windows
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

sys.path.insert(0, str(Path(__file__).parent.parent))

from services.web_researcher import WebResearcher


async def demo_basic():
    """Базовая демонстрация."""
    print("=" * 60)
    print("🌐 WEB RESEARCHER — ДЕМО")
    print("=" * 60)
    print()
    
    # 1. Инициализация
    print("📦 Инициализация WebResearcher...")
    researcher = WebResearcher()
    print("✅ Инициализация завершена")
    print()
    
    # 2. Тестирование источников
    topics = [
        "human anatomy physiology",
        "sexual response cycle Masters Johnson",
        "oxytocin bonding effects"
    ]
    
    print("🔍 Тестирование источников поиска:")
    print()
    
    for topic in topics:
        print(f"📚 Тема: {topic}")
        
        results = await researcher.search_all_sources(topic)
        
        sources_used = [k for k, v in results["sources"].items() if v.get("success")]
        print(f"   ✅ Использовано источников: {len(sources_used)}/4")
        print(f"   📊 Источники: {', '.join(sources_used)}")
        
        # Извлечение фактов
        facts = researcher._extract_facts(results)
        print(f"   📝 Извлечено фактов: {len(facts)}")
        
        if facts:
            print(f"   💡 Пример факта:")
            print(f"      \"{facts[0]['text'][:100]}...\"")
            print(f"      Источник: {facts[0]['source']}")
        
        print()
    
    # 3. Полный цикл обучения
    print("📖 Полный цикл обучения:")
    print()
    
    for topic in topics[:2]:
        print(f"📚 Изучение: {topic}")
        learning = await researcher.learn_from_search(topic)
        print(f"   ✅ Фактов: {learning['facts_count']}")
        print(f"   📊 Источники: {', '.join(learning['sources_used'])}")
        print()
    
    # 4. Статистика
    print("📈 Статистика:")
    stats = researcher.get_stats()
    print(f"   Всего поисков: {stats['total_searches']}")
    print(f"   Успешных: {stats['successful']}")
    print(f"   Неудачных: {stats['failed']}")
    print(f"   Успешность: {stats['success_rate']*100:.1f}%")
    print(f"   Размер кэша: {stats['cache_size']}")
    print()
    
    print("=" * 60)
    print("✅ ДЕМО ЗАВЕРШЕНО")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(demo_basic())
