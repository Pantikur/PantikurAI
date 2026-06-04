# update_knowledge.py — обновление знаний и подготовка к дообучению

"""
Скрипт для:
1. Генерации обучающих пар из накопленных знаний
2. Объединения с пользовательскими диалогами
3. Подготовки данных для дообучения
"""

import os
import sys
import json
from datetime import datetime

# Добавляем путь к проекту
sys.path.append(".")

try:
    from knowledge_manager import KnowledgeManager
    from Wuglarst.src.chatbot import ChatBot
    
    print("✅ Импорты успешны")
except ImportError as e:
    print(f"❌ Ошибка импорта: {e}")
    sys.exit(1)

def update_knowledge_system():
    """Обновляет систему знаний и готовит данные для дообучения"""
    print("\n🔄 Начинаем обновление системы знаний")
    print("=" * 50)
    
    # Инициализируем менеджер знаний
    km = KnowledgeManager("data/knowledge")
    
    # Печатаем отчет до обновления
    print("📊 Текущее состояние:")
    km.print_report()
    
    # Генерируем обучающие пары
    print("\n⚙️ Генерация обучающих пар...")
    new_pairs = km.generate_training_pairs(min_difficulty="medium")
    
    if new_pairs == 0:
        print("ℹ️ Нечего обновлять - нет новых слов")
        return False
    
    # Объединяем с пользовательскими диалогами
    print("\n🔗 Объединение с пользовательскими диалогами...")
    user_conversations_path = "data/user_conversations.jsonl"
    success = km.merge_with_user_conversations(user_conversations_path)
    
    if not success:
        print("❌ Не удалось объединить с диалогами")
        return False
    
    # Печатаем отчет после обновления
    print("\n📊 Состояние после обновления:")
    km.print_report()
    
    print("\n✅ Система знаний успешно обновлена!")
    return True

if __name__ == "__main__":
    success = update_knowledge_system()
    
    if success:
        print("\n📌 Теперь можно запустить дообучение:")
        print("   python retrain.py")
    else:
        print("\n❌ Обновление не удалось")
        sys.exit(1)