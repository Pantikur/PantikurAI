"""
Тестовый скрипт для проверки работы Qwen2.5-Coder-3B и Qwen2.5-3B.

Использование:
    python test_qwen_models.py              # тест обоих моделей
    python test_qwen_models.py --coder      # только Coder модель
    python test_qwen_models.py --general    # только General модель
    python test_qwen_models.py --auto "вопрос"  # автоматический выбор модели
"""

from __future__ import annotations
import argparse
import sys
from pathlib import Path

# Добавляем текущую директорию в path
_script_dir = Path(__file__).parent.resolve()
if str(_script_dir) not in sys.path:
    sys.path.insert(0, str(_script_dir))

from nobuka_core import NobukaCore
from config import NobukaConfig


def test_coder_model(core: NobukaCore):
    """Протестировать Coder модель."""
    print("\n" + "=" * 70)
    print("🤖 ТЕСТ QWEN2.5-CODER-3B (программирование)")
    print("=" * 70)

    test_prompts = [
        "Напиши функцию на Python для сортировки списка чисел методом пузырька",
        "Как исправить ошибку TypeError: unsupported operand type(s) for +: 'int' and 'str'",
        "Объясни что делает декоратор @property в Python",
    ]

    for i, prompt in enumerate(test_prompts, 1):
        print(f"\n--- Запрос {i} ---")
        print(f"Запрос: {prompt}")
        print("\nОтвет Coder модели:")
        print("-" * 40)
        response = core.generate_coder_response(prompt, max_length=512)
        print(response)


def test_general_model(core: NobukaCore):
    """Протестировать General модель."""
    print("\n" + "=" * 70)
    print("🤖 ТЕСТ QWEN2.5-3B (универсальная)")
    print("=" * 70)

    test_prompts = [
        "Привет! Расскажи о себе",
        "Какие у тебя хобби?",
        "Что ты думаешь о разработке игр?",
    ]

    for i, prompt in enumerate(test_prompts, 1):
        print(f"\n--- Запрос {i} ---")
        print(f"Запрос: {prompt}")
        print("\nОтвет General модели:")
        print("-" * 40)
        
        # Используем generate_response с промптом, который не содержит кодовых слов
        response = core.generate_response(prompt, max_length=512)
        print(response)


def test_auto_selection(core: NobukaCore, prompt: str):
    """Протестировать автоматический выбор модели."""
    print("\n" + "=" * 70)
    print("🤖 АВТОМАТИЧЕСКИЙ ВЫБОР МОДЕЛИ")
    print("=" * 70)
    print(f"\nЗапрос: {prompt}")
    print("\nРезультат:")
    print("-" * 40)
    response = core.generate_response(prompt, max_length=512)
    print(response)


def main():
    parser = argparse.ArgumentParser(description="Тест Qwen2.5 моделей для Нобуки")
    parser.add_argument("--coder", action="store_true", help="Тестировать только Coder модель")
    parser.add_argument("--general", action="store_true", help="Тестировать только General модель")
    parser.add_argument("--auto", type=str, help="Протестировать автоматический выбор модели с данным запросом")
    parser.add_argument("--demo", action="store_true", help="Демо-режим с короткими интервалами")
    args = parser.parse_args()

    print("=" * 70)
    print("🧪 ТЕСТ QWEN2.5 МОДЕЛЕЙ ДЛЯ НОБУКИ")
    print("=" * 70)

    # Создаём ядро
    config = NobukaConfig.demo() if args.demo else NobukaConfig.default()
    core = NobukaCore(config)

    # Проверяем доступность моделей
    coder_available = hasattr(core, 'coder_model') and core.coder_model is not None
    general_available = hasattr(core, 'general_model') and core.general_model is not None

    print(f"\n📊 Статус моделей:")
    print(f"   Qwen2.5-Coder-3B: {'✅ доступна' if coder_available else '❌ недоступна'}")
    print(f"   Qwen2.5-3B: {'✅ доступна' if general_available else '❌ недоступна'}")

    if not coder_available and not general_available:
        print("\n❌ Ни одна модель не доступна. Проверьте установку:")
        print("   - models/qwen2.5-coder-3b/")
        print("   - models/qwen2.5-3b/")
        return

    # Тестируем
    if args.coder:
        if coder_available:
            test_coder_model(core)
        else:
            print("\n❌ Coder модель недоступна")
    elif args.general:
        if general_available:
            test_general_model(core)
        else:
            print("\n❌ General модель недоступна")
    elif args.auto:
        test_auto_selection(core, args.auto)
    else:
        # Тестируем обе модели
        if coder_available:
            test_coder_model(core)
        if general_available:
            test_general_model(core)

        # Тест автоматического выбора
        print("\n" + "=" * 70)
        print("🤖 ТЕСТИРОВАНИЕ АВТОМАТИЧЕСКОГО ВЫБОРА МОДЕЛИ")
        print("=" * 70)

        auto_tests = [
            ("Напиши функцию на Python для сортировки списка", "coder"),
            ("Привет, как дела?", "general"),
            ("Что такое рефакторинг кода?", "coder"),
            ("Расскажи о своих способностях", "general"),
        ]

        for prompt, expected in auto_tests:
            print(f"\n--- Запрос: {prompt} ---")
            print(f"Ожидается: {expected}-модель")
            use_coder = core._should_use_coder_model(prompt)
            actual = "coder" if use_coder else "general"
            status = "✅" if actual == expected else "❌"
            print(f"Выбрана: {actual}-модель {status}")


if __name__ == "__main__":
    main()
