# inspect_data.py
import pickle
import os

# Определяем базовую директорию проекта
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
file_path = os.path.join(BASE_DIR, "data", "chat_data.pkl")

with open(file_path, 'rb') as f:
    data = pickle.load(f)

print("Ключи в chat_data.pkl:")
print(data.keys())

print("\nПример содержимого:")
for k, v in data.items():
    print(f"{k}: {v[:5] if hasattr(v, '__len__') and len(v) > 5 else v}")