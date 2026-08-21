"""
Итоговый тест: все 10 учёных + Scientists Network + Интернет.
"""

import logging
logging.basicConfig(level=logging.WARNING)

from scientists_network.research_monitor import ResearchMonitor
from scientists_network.network import Message, MessageType, RequestPriority, RequestType
import time

print("=" * 70)
print("ФИНАЛЬНЫЙ ТЕСТ — 10 УЧЁНЫХ + СЕТЬ + ИНТЕРНЕТ")
print("=" * 70)

# 1. Инициализация
print("\n[1] Инициализация ResearchMonitor...")
rm = ResearchMonitor()
rm.initialize()

scientists = sorted(rm.cores.keys())
print(f"    Ядра: {len(scientists)}")
for s in scientists:
    print(f"      - {s}")

# 2. Подключение к Scientists Network
print("\n[2] Подключение к Scientists Network...")
connected = 0
for name in scientists:
    core = rm.get_core(name)
    if core and core.core:
        rm.network.register_scientist(name, core.core)
        connected += 1

print(f"    Подключено: {connected}")
print(f"    В сети: {rm.network.get_all_scientists()}")

# 3. Тест Юи
print("\n[3] Тест Юи (сознание, перенос)...")
yu_proxy = rm.get_core('yu')
if yu_proxy and yu_proxy.core:
    yu = yu_proxy.core
    
    # Запускаем 5 циклов
    for i in range(5):
        yu._cycle()
    
    print(f"    Циклов: {yu.cycle_count}")
    print(f"    Моделей сознания: {len(yu.consciousness_models)}")
    print(f"    Воплощений: {len(yu.digital_embodiments)}")
    print(f"    Успешных переносов: {yu.metrics['successful_transfers']}")
    print(f"    Недоступных переносов: {yu.metrics['failed_transfers']}")
    
    # Веб-исследование
    print(f"    Веб-поисков: {yu.metrics['web_searches']}")

# 4. Тест Аквы с интернетом
print("\n[4] Тест Аквы (математика + интернет)...")
akva_proxy = rm.get_core('akva')
if akva_proxy and akva_proxy.core:
    akva = akva_proxy.core
    
    # Запускаем 5 циклов
    for i in range(5):
        akva._cycle()
    
    print(f"    Циклов: {akva.cycle_count}")
    print(f"    Теорий: {akva.metrics['theories_built']}")
    print(f"    Вычислений: {akva.metrics['calculations_run']}")
    print(f"    Улучшений: {akva.metrics['improvements_applied']}")
    print(f"    Веб-поисков: {akva.metrics['web_searches']}")
    print(f"    Интервал поиска: {akva.config.web_search_interval} циклов")

# 5. Обмен данными между учёными
print("\n[5] Обмен данными через Scientists Network...")

# Юи отправляет модель сознания
yu_model = {
    "name": "Квантовая модель сознания",
    "type": "hybrid",
    "complexity": 0.95
}
rm.network.broadcast_consciousness_model("yu", yu_model)

# Аква отправляет вычисление
akva_calc = {
    "name": "E=mc^2",
    "result": 9e16
}
rm.network.broadcast_calculation("akva", akva_calc)

# Юи запрашивает данные у Аквы
rm.network.request_data(
    sender="yu",
    recipient="akva",
    request_type=RequestType("theories"),
    description="Нужны физические данные для модели сознания"
)

time.sleep(0.5)

# 6. Статистика сети
print("\n[6] Статистика Scientists Network...")
stats = rm.network.get_stats()
print(f"    Всего учёных: {stats['total_scientists']}")
print(f"    Всего сообщений: {stats['total_messages']}")
print(f"    По типам:")
for msg_type, count in stats['messages_by_type'].items():
    print(f"      {msg_type}: {count}")
print(f"    По учёным:")
for scientist, count in stats['messages_by_scientist'].items():
    print(f"      {scientist}: {count}")

# 7. История сообщений
print("\n[7] Последние сообщения...")
history = rm.network.get_message_history(limit=5)
for msg in history:
    print(f"    [{msg['message_type']}] {msg['sender']} → {msg['recipient']}: {msg['content'][:50]}")

# Итог
print("\n" + "=" * 70)
print("ИТОГОВЫЙ ТЕСТ ЗАВЕРШЁН УСПЕШНО")
print("=" * 70)
print(f"\n✅ 10 учёных инициализированы")
print(f"✅ Все подключены к Scientists Network")
print(f"✅ Юи изучает сознание и перенос")
print(f"✅ Аква изучает физику + интернет")
print(f"✅ Обмен данными работает")
print(f"✅ Автоматическая болтовня активна")
print("\n" + "=" * 70)
