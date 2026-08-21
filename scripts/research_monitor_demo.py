"""
Демонстрация Research Monitor - мониторинг исследований учёных.

Показывает:
  - Запуск исследований ядра
  - Просмотр событий в реальном времени
  - Получение результатов (теории, вычисления)
  - Просмотр логов
"""

import sys
import os
import time
from pathlib import Path

# Fix Windows console encoding
if sys.platform == "win32":
    import codecs
    sys.stdout = codecs.getwriter("utf-8")(sys.stdout.buffer, "strict")
    sys.stderr = codecs.getwriter("utf-8")(sys.stderr.buffer, "strict")

# Добавляем проект в путь
sys.path.insert(0, str(Path(__file__).parent.parent))

from scientists_network.research_monitor import ResearchMonitor


def demo():
    """Демонстрация работы Research Monitor."""
    print("=" * 70)
    print("RESEARCH MONITOR - МОНИТОРИНГ ИССЛЕДОВАНИЙ УЧЕНЫХ")
    print("=" * 70)
    
    # Инициализация
    print("\n[INIT] Инициализация ResearchMonitor...")
    monitor = ResearchMonitor()
    monitor.initialize()
    
    print(f"\n[STATUS] Инициализировано ядер: {len(monitor.cores)}")
    for name in monitor.cores:
        print(f"   - {name}")
    
    # Статус всех ядер
    print("\n" + "=" * 70)
    print("СТАТУС ВСЕХ ЯДЕР")
    print("=" * 70)
    status = monitor.get_all_status()
    print(f"Всего ядер: {status['total_cores']}")
    print(f"Запущено: {status['running_count']}")
    
    for name, core_status in status['cores'].items():
        print(f"\n  {name.upper()}:")
        print(f"    Запущено: {core_status['is_running']}")
        metrics = core_status.get('metrics', {})
        print(f"    Циклов: {metrics.get('cycles_completed', 0)}")
    
    # Запуск исследований
    print("\n" + "=" * 70)
    print("ЗАПУСК ИССЛЕДОВАНИЙ")
    print("=" * 70)
    
    for name in monitor.cores:
        result = monitor.start_research(name)
        print(f"  {name}: {result['message']}")
        time.sleep(1)  # Небольшая задержка между запусками
    
    # Мониторинг событий
    print("\n" + "=" * 70)
    print("МОНИТОРИНГ СОБЫТИЙ (10 секунд)")
    print("=" * 70)
    
    for i in range(10):
        print(f"\n[Second {i+1}]")
        for name in monitor.cores:
            core = monitor.get_core(name)
            if core:
                events = core.get_events(limit=5)
                if events:
                    print(f"\n  {name.upper()}:")
                    for event in events[-3:]:  # Последние 3 события
                        print(f"    [{event['event_type']}] {event['message']}")
        
        status = monitor.get_all_status()
        for name, core_status in status['cores'].items():
            metrics = core_status.get('metrics', {})
            cycles = metrics.get('cycles_completed', 0)
            print(f"  {name}: {cycles} cycles")
        
        time.sleep(1)
    
    # Получение результатов
    print("\n" + "=" * 70)
    print("РЕЗУЛЬТАТЫ ИССЛЕДОВАНИЙ")
    print("=" * 70)
    
    for name in monitor.cores:
        print(f"\n  {name.upper()}:")
        summary = monitor.get_research_summary(name)
        if summary:
            metrics = summary['status']['metrics']
            
            if name == 'lucy':
                # У Люси свои метрики
                print(f"    Designs created: {metrics.get('designs_created', 0)}")
                print(f"    Calculations run: {metrics.get('calculations_run', 0)}")
                print(f"    Papers studied: {metrics.get('papers_studied', 0)}")
                print(f"    Hybrid engines: {metrics.get('hybrid_engines_designed', 0)}")
            else:
                print(f"    Theories built: {metrics.get('theories_built', 0)}")
                print(f"    Calculations run: {metrics.get('calculations_run', 0)}")
                print(f"    Papers studied: {metrics.get('papers_studied', 0)}")
            
            print(f"    Events: {summary['status'].get('events_count', 0)}")
            print(f"    Log lines: {summary['status'].get('logs_count', 0)}")
            
            # Последние теории/дизайны
            if summary['theories']:
                print(f"\n    LAST THEORIES:")
                for t in summary['theories'][-3:]:
                    theory_name = t.get('name', 'N/A')
                    category = t.get('category', {})
                    cat_value = category.get('value', category) if isinstance(category, dict) else category
                    value = t.get('scientific_value', 0)
                    print(f"      - {theory_name} ({cat_value}, value: {value:.2f})")
    
    # Остановка
    print("\n" + "=" * 70)
    print("ОСТАНОВКА ИССЛЕДОВАНИЙ")
    print("=" * 70)
    
    for name in monitor.cores:
        result = monitor.stop_research(name)
        print(f"  {name}: {result['message']}")
        time.sleep(0.5)
    
    # Финальный статус
    print("\n" + "=" * 70)
    print("ФИНАЛЬНЫЙ СТАТУС")
    print("=" * 70)
    status = monitor.get_all_status()
    for name, core_status in status['cores'].items():
        metrics = core_status.get('metrics', {})
        print(f"\n  {name.upper()}:")
        print(f"    Запущено: {core_status['is_running']}")
        print(f"    Циклов: {metrics.get('cycles_completed', 0)}")
        print(f"    Теорий: {metrics.get('theories_built', 0)}")
        print(f"    Вычислений: {metrics.get('calculations_run', 0)}")
        print(f"    Статей: {metrics.get('papers_studied', 0)}")
    
    print("\n" + "=" * 70)
    print("DEMO COMPLETED")
    print("=" * 70)


if __name__ == "__main__":
    demo()
