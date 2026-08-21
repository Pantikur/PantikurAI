"""
Demo: Scientists Network — коммуникация между учёными.
"""

from __future__ import annotations
import logging
import time
from pathlib import Path
import sys

# Добавляем корень проекта в путь
project_root = Path(__file__).resolve().parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
)
logger = logging.getLogger("network_demo")


def demo():
    """Демонстрация коммуникации между учёными."""
    from scientists_network.research_monitor import ResearchMonitor
    from scientists_network.network import Message, MessageType, RequestPriority
    
    print("=" * 70)
    print("SCIENTISTS NETWORK — КОММУНИКАЦИЯ МЕЖДУ УЧЁНЫМИ")
    print("=" * 70)
    
    # Инициализация
    print("\n[INIT] Инициализация ResearchMonitor...")
    rm = ResearchMonitor()
    rm.initialize()
    
    print(f"[STATUS] Инициализировано ядер: {len(rm.cores)}")
    
    # Подключаем учёных к сети
    print("\n[NETWORK] Подключение учёных к Scientists Network...")
    scientists = ['hanako', 'fuyuki', 'lucy', 'akva', 'nobuka', 'shiori', 'yu', 'naoto', 'ayiko']
    
    for name in scientists:
        core = rm.get_core(name)
        if core and core.core:
            rm.network.register_scientist(name, core.core)
            print(f"  ✅ {name} подключена")
    
    print(f"\n[NETWORK] Всего подключено: {len(rm.network.get_all_scientists())}")
    
    # Отправляем приветствия
    print("\n[CHAT] Отправляем приветствия...")
    
    greetings = [
        Message(MessageType.GREETING, "hanako", "all", "👋 Всем привет! Я Ханако, изучаю гравитацию!"),
        Message(MessageType.GREETING, "fuyuki", "all", "⚡ Привет! Я Фуюки, атмосферное электричество!"),
        Message(MessageType.GREETING, "lucy", "all", "🚀 Привет! Я Люси, проектирую двигатели!"),
        Message(MessageType.GREETING, "akva", "all", "📐 Привет! Я Аква, математика и физика!"),
        Message(MessageType.GREETING, "yu", "all", "🧠 Привет! Я Юи, изучаю перенос сознания и души!"),
        Message(MessageType.GREETING, "naoto", "all", "🎨 Привет! Я Наото, визуальный архитектор — наброски, чертежи, 3D!"),
        Message(MessageType.GREETING, "ayiko", "all", "📚 Привет! Я Айко, читаю книги, извлекаю знания, обучаю модель!"),
    ]
    
    for msg in greetings:
        rm.network.send_message(msg)
        time.sleep(0.2)
    
    # Обмен данными
    print("\n[DATA] Обмен данными...")
    
    data_messages = [
        Message(
            MessageType.THEORY,
            "hanako",
            "all",
            "🔬 Новая теория: Петлевая квантовая гравитация",
            data={"theory": {"name": "Петлевая квантовая гравитация", "value": 0.85}},
            priority=RequestPriority.HIGH,
        ),
        Message(
            MessageType.CALCULATION,
            "akva",
            "all",
            "🧮 Вычисление: E=mc^2 = 9×10^16 J",
            data={"calculation": {"name": "Энергия частицы", "result": 9e16}},
            priority=RequestPriority.NORMAL,
        ),
        Message(
            MessageType.COORDINATION,
            "lucy",
            "hanako",
            "🤝 Ханако, нужны твои теории гравитации для двигателя!",
            priority=RequestPriority.HIGH,
        ),
        Message(
            MessageType.CONSCIOUSNESS,
            "yu",
            "hanako",
            "🧠 Ханако, у меня есть модель сознания для твоей теории гравитации!",
            data={"model": {"name": "Квантовое сознание", "type": "hybrid"}},
            priority=RequestPriority.HIGH,
        ),
    ]
    
    for msg in data_messages:
        rm.network.send_message(msg)
        time.sleep(0.2)
    
    # Болтовня
    print("\n[BOREDOM] Автоматическая болтовня...")
    
    for i in range(3):
        rm.network.auto_chat_cycle()
        time.sleep(0.2)
    
    # Статистика
    print("\n" + "=" * 70)
    print("СТАТИСТИКА COMMUNICATION")
    print("=" * 70)
    
    stats = rm.network.get_stats()
    print(f"Всего сообщений: {stats['total_messages']}")
    print(f"Подключено учёных: {stats['total_scientists']}")
    print(f"\nПо типам:")
    for msg_type, count in stats['messages_by_type'].items():
        print(f"  {msg_type}: {count}")
    print(f"\nПо учёным:")
    for scientist, count in stats['messages_by_scientist'].items():
        print(f"  {scientist}: {count}")
    
    # История сообщений
    print("\n" + "=" * 70)
    print("ИСТОРИЯ СООБЩЕНИЙ (последние 10)")
    print("=" * 70)
    
    history = rm.network.get_message_history(limit=10)
    for msg in history:
        print(f"\n[{msg['message_type']}] {msg['sender']} → {msg['recipient']}")
        print(f"  {msg['content']}")
    
    print("\n" + "=" * 70)
    print("DEMO COMPLETED")
    print("=" * 70)


if __name__ == "__main__":
    demo()
