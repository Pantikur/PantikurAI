# upload_to_huggingface.py — загрузка Qwen2.5-3B на HuggingFace Hub
# Использование: python upload_to_huggingface.py

import os
from huggingface_hub import HfApi, login

# === НАСТРОЙКИ ===
HF_TOKEN = os.getenv("HF_TOKEN", "your_token_here")  # Или введи вручную
MODEL_PATH = "models/qwen2.5-3b"  # Qwen2.5-3B
REPO_ID = "Pantikur/Wuglarst"  # Твой репозиторий на HF

def upload_model():
    print("Вход в HuggingFace...")
    login(token=HF_TOKEN)
    
    api = HfApi()
    
    # Создаём репозиторий если не существует
    try:
        api.create_repo(repo_id=REPO_ID, repo_type="model", exist_ok=True)
        print(f"Репозиторий {REPO_ID} готов")
    except Exception as e:
        print(f"Репозиторий уже существует: {e}")
    
    print(f"Загрузка модели из {MODEL_PATH}...")
    api.upload_folder(
        folder_path=MODEL_PATH,
        repo_id=REPO_ID,
        repo_type="model"
    )
    
    print(f"✅ Модель загружена на https://huggingface.co/{REPO_ID}")

if __name__ == "__main__":
    upload_model()