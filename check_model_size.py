#!/usr/bin/env python3
# check_model_size.py — показывает размер модели и токенизатора
# Запуск: python check_model_size.py

import os
import json

def format_size(size_bytes):
    """Форматирует байты в КБ/МБ/ГБ"""
    if size_bytes < 1024:
        return f"{size_bytes} Б"
    elif size_bytes < 1024 ** 2:
        return f"{size_bytes / 1024:.2f} КБ"
    elif size_bytes < 1024 ** 3:
        return f"{size_bytes / 1024 ** 2:.2f} МБ"
    else:
        return f"{size_bytes / 1024 ** 3:.2f} ГБ"

def check_model_size():
    """Проверяет размер модели и всех артефактов"""
    paths = {
        "Модель (chat_model.pth)": "models/chat_model.pth",
        "Модель .best": "models/chat_model.pth.best",
        "Модель .backup": "models/chat_model.pth.backup",
        "Токенизатор": "data/tokenizer.json",
        "Токенизатор backup": "data/tokenizer.json.backup",
        "Конверсация (train data)": "data/conversations.json",
        "Training pairs": "data/training_pairs.jsonl",
    }

    print("=" * 60)
    print("📊 РАЗМЕР МОДЕЛИ И АРТЕФАКТОВ")
    print("=" * 60)

    total_size = 0
    for name, path in paths.items():
        if os.path.exists(path):
            size = os.path.getsize(path)
            total_size += size
            print(f"✅ {name:30} → {format_size(size):>12}")
        else:
            print(f"❌ {name:30} → {'[Файл не найден]':>12}")

    print("=" * 60)
    print(f"📦 ИТОГО: {format_size(total_size)}")
    print("=" * 60)

    # Статистика из модели
    if os.path.exists("data/conversations.json"):
        with open("data/conversations.json", "r", encoding="utf-8") as f:
            data = json.load(f)
            if isinstance(data, list):
                print(f"\n📚 В conversations.json: {len(data)} записей")

    if os.path.exists("data/training_pairs.jsonl"):
        with open("data/training_pairs.jsonl", "r", encoding="utf-8") as f:
            lines = sum(1 for _ in f)
            print(f"📚 В training_pairs.jsonl: {lines} записей")

    # Рекомендации
    print("\n💡 РЕКОМЕНДАЦИИ:")
    model_path = "models/chat_model.pth"
    if os.path.exists(model_path):
        model_size = os.path.getsize(model_path)
        if model_size < 1024 * 1024:  # < 1 МБ
            print("   ⚠️  Модель очень маленькая — возможно, обучение не удалось")
        elif model_size < 5 * 1024 * 1024:  # < 5 МБ
            print("   ℹ️  Модель маленькая (обычно OK для простых моделей)")
        elif model_size < 50 * 1024 * 1024:  # < 50 МБ
            print("   ✅ Модель нормального размера")
        else:
            print("   ✅ Модель большая — хорошее обучение!")
    else:
        print("   ❌ Модель не найдена — нужно запустить retrain.py")

if __name__ == "__main__":
    check_model_size()
