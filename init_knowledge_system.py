# init_knowledge_system.py — инициализация системы знаний

"""
Скрипт для инициализации системы знаний:
1. Создает необходимые директории
2. Создает пустые файлы
3. Проверяет структуру проекта
"""

import os
import json
import sys
from datetime import datetime

# Добавляем путь к проекту
sys.path.append(".")

def create_directory(path: str) -> bool:
    """Создает директорию, если она не существует"""
    try:
        os.makedirs(path, exist_ok=True)
        print(f"✅ Создана директория: {path}")
        return True
    except Exception as e:
        print(f"❌ Ошибка создания директории {path}: {e}")
        return False

def create_file(path: str, content=None) -> bool:
    """Создает файл с определенным содержимым"""
    try:
        # Создаем директорию, если она не существует
        directory = os.path.dirname(path)
        if directory and not os.path.exists(directory):
            os.makedirs(directory, exist_ok=True)
            
        if content is None:
            # Пустой файл
            if not os.path.exists(path):
                with open(path, 'w', encoding='utf-8') as f:
                    pass
                print(f"✅ Создан пустой файл: {path}")
            else:
                print(f"ℹ️ Файл уже существует: {path}")
        else:
            with open(path, 'w', encoding='utf-8') as f:
                if isinstance(content, dict):
                    json.dump(content, f, ensure_ascii=False, indent=2)
                else:
                    f.write(str(content))
            print(f"✅ Создан файл: {path}")
        
        return True
    except Exception as e:
        print(f"❌ Ошибка создания файла {path}: {e}")
        return False

def check_file_exists(path: str) -> bool:
    """Проверяет существование файла"""
    exists = os.path.exists(path)
    status = "✅" if exists else "❌"
    print(f"{status} {path}")
    return exists

def main():
    """Основная функция инициализации"""
    print("\n🚀 ИНИЦИАЛИЗАЦИЯ СИСТЕМЫ ЗНАНИЙ")
    print("=" * 50)
    
    # Структура директорий
    directories = [
        "data/knowledge",
        "data/knowledge/__pycache__"
    ]
    
    # Создаем директории
    for directory in directories:
        create_directory(directory)
    
    # Создаем файлы системы знаний
    files_to_create = [
        {
            "path": "data/knowledge/learned_words.json",
            "content": [],
            "description": "Выученные слова и определения"
        },
        {
            "path": "data/knowledge/training_pairs.jsonl",
            "content": None,  # Пустой файл
            "description": "Обучающие пары для дообучения"
        },
        {
            "path": "data/knowledge/knowledge_stats.json",
            "content": {
                "total_words": 0,
                "last_update": None,
                "training_pairs_generated": 0,
                "difficulty_distribution": {
                    "simple": 0,
                    "medium": 0,
                    "complex": 0
                }
            },
            "description": "Статистика знаний"
        },
        {
            "path": "data/knowledge/learning_status.json",
            "content": {
                "last_check": None,
                "last_retrain": None,
                "total_retrains": 0,
                "words_at_retrain": 0,
                "words_learned": 0,
                "initial_setup": datetime.now().isoformat()
            },
            "description": "Статус цикла обучения"
        }
    ]
    
    print("\n📝 Создание файлов системы знаний:")
    for file_info in files_to_create:
        create_file(file_info["path"], file_info["content"])
    
    # Проверяем основные файлы проекта
    print("\n🔍 Проверка основных файлов проекта:")
    essential_files = [
        "knowledge_manager.py",
        "update_knowledge.py",
        "auto_learn_cycle.py",
        "Wuglarst/src/chatbot.py",
        "retrain.py",
        "train.py"
    ]
    
    all_files_exist = True
    for filepath in essential_files:
        if not check_file_exists(filepath):
            all_files_exist = False
    
    # Проверяем директории
    print("\n📁 Проверка директорий:")
    essential_dirs = [
        "data",
        "models",
        "Wuglarst/src"
    ]
    
    for directory in essential_dirs:
        dir_exists = os.path.exists(directory)
        status = "✅" if dir_exists else "❌"
        print(f"{status} {directory}")
        if not dir_exists:
            all_files_exist = False
    
    # Результат инициализации
    print("\n" + "=" * 50)
    if all_files_exist:
        print("🎉 Система знаний успешно инициализирована!")
        print("\n📌 Доступные команды:")
        print("   python update_knowledge.py         - Обновить знания")
        print("   python retrain.py                  - Дообучить модель")
        print("   python auto_learn_cycle.py         - Автоматический цикл обучения")
        print("   python -m Wuglarst.src.chatbot     - Запустить чат-бота")
    else:
        print("⚠️  Инициализация завершена с ошибками!")
        print("   Пожалуйста, убедитесь, что все файлы находятся в правильных местах.")

if __name__ == "__main__":
    main()