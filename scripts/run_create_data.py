import os
import sys

# Добавляем корень проекта в sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Запускаем create_data.py
if __name__ == "__main__":
    print("Запуск create_data.py...")
    exec(open('create_data.py').read())
    print("create_data.py выполнен.")