# scripts/inspect_data.py — анализ data/chat_data.pkl
import os
import sys

# Пути корректны при запуске из корня проекта:
#   python scripts/inspect_data.py
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
file_path = os.path.join(BASE_DIR, "data", "chat_data.pkl")

try:
    import joblib
    data = joblib.load(file_path)
except Exception:
    import pickle
    with open(file_path, "rb") as f:
        data = pickle.load(f)

print(f"Vocab size: {data.get('vocab_size')}")
print(f"Max length: {data.get('max_length')}")
print(f"Word to idx keys: {len(data.get('word_to_idx', {}))}")
print(f"Idx to word keys: {len(data.get('idx_to_word', {}))}")
print(f"Sample words: {list(data.get('word_to_idx', {}).keys())[:10]}")
print(f"\nВсе ключи: {list(data.keys())}")