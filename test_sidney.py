"""
Тестовый скрипт для Сидни.
Запускает все 8 движков и демонстрирует автономную работу.
"""

import logging
import time
import json
import sys
import io

# Fix console encoding for emojis
if sys.stdout.encoding != 'utf-8':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
if sys.stderr.encoding != 'utf-8':
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(name)s] %(message)s',
    datefmt='%H:%M:%S'
)

from sidney.sidney_core import SidneyCore


def main():
    print("=" * 60)
    print("  🌟 СИДНИ — 13-я Девочка-Учёный")
    print("  Игровой Движок Полный Цикл")
    print("=" * 60)
    
    # Создание Сидни
    sidney = SidneyCore(demo_mode=True)
    
    # Инициализация
    print("\n📦 Инициализация...")
    if not sidney.initialize():
        print("❌ Ошибка инициализации!")
        return
    
    # Показать статус
    status = sidney.get_status()
    print(f"\n✅ Инициализировано!")
    print(f"   Характер: {status['character']['name']}")
    print(f"   Автономность: {status['autonomy_level']}")
    print(f"   Общий уровень знаний: {status['overall_knowledge_level']}")
    
    # Показать знания
    print("\n📚 Знания:")
    for skill, level in status['knowledge'].items():
        bar = "█" * level + "░" * (5 - level)
        print(f"   {skill:25s} [{bar}] {level}/5")
    
    # Показать сеть девочек
    print("\n👭 Сеть девочек:")
    for sister, data in status['sisters_network'].items():
        trust_bar = "❤️" * int(data['trust_level'] * 5)
        print(f"   {sister:15s} доверие: {data['trust_level']:.2f} {trust_bar}")
    
    # Показать статус движков
    print("\n🎮 Движки:")
    engines = status['engines']['engines']
    engine_names = {
        'renderers': '🎨 Графика',
        'physics': '⚙️ Физика',
        'audio': '🔊 Аудио',
        'animation': '🎭 Анимация',
        'ai': '🤖 ИИ',
        'network': '🌐 Сеть',
        'scripting': '📜 Скрипты',
        'level_editor': '🏗️ Редактор'
    }
    
    for key, name in engine_names.items():
        if key in engines:
            eng_status = engines[key].get('status', 'unknown')
            icon = '✅' if eng_status == 'active' else '❌'
            print(f"   {icon} {name:15s} {eng_status}")
    
    # Запуск
    print("\n▶️ Запуск автономной работы...")
    sidney.start()
    
    # Демонстрация работы в течение нескольких секунд
    print("\n⏳ Работа в автономном режиме (15 секунд)...")
    print("-" * 60)
    
    for i in range(15):
        time.sleep(1)
        status = sidney.get_status()
        print(f"   [{i+1:2d}s] Циклов: {status['stats']['total_cycles']:3d} | "
              f"Взаимодействий: {status['stats']['total_interactions']:3d} | "
              f"Знаний: {status['overall_knowledge_level']:.1f} | "
              f"Оптимизаций: {status['stats']['total_optimizations']}")
    
    # Остановка
    print("\n⏹️ Остановка...")
    sidney.stop()
    
    # Финальный статус
    print("\n" + "=" * 60)
    print("  🌟 ФИНАЛЬНЫЙ СТАТУС")
    print("=" * 60)
    
    final_status = sidney.get_status()
    print(f"   Характер: {final_status['character']['name']}")
    print(f"   Автономность: {final_status['autonomy_level']}")
    print(f"   Общий уровень знаний: {final_status['overall_knowledge_level']}")
    print(f"   Уровень саморазвития: {final_status['self_development_level']}")
    print(f"   Циклов выполнено: {final_status['stats']['total_cycles']}")
    print(f"   Взаимодействий: {final_status['stats']['total_interactions']}")
    print(f"   Оптимизаций: {final_status['stats']['total_optimizations']}")
    
    print("\n✅ Сидни завершила работу успешно!")
    print("=" * 60)


if __name__ == "__main__":
    main()
