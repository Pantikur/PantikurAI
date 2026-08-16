"""
Пример использования Qwen2.5 API в проекте Pantikur.

Покажите, как использовать модели Qwen2.5-Coder-3B и Qwen2.5-3B
из других частей проекта.
"""

from __future__ import annotations

# Импортируем API
import sys
from pathlib import Path

_script_dir = Path(__file__).parent.resolve()
if str(_script_dir) not in sys.path:
    sys.path.insert(0, str(_script_dir))

from qwen_api import qwen

# Убедимся, что qwen инициализирован (для Pylance)
assert qwen is not None


def example_1_auto_selection():
    """Пример 1: Автоматический выбор модели."""
    print("=" * 60)
    print("📝 ПРИМЕР 1: Автоматический выбор модели")
    print("=" * 60)

    # Этот запрос содержит кодовые слова → Coder модель
    response = qwen.generate("Напиши функцию на Python для сортировки списка")
    print(f"\nЗапрос: 'Напиши функцию на Python для сортировки списка'")
    print(f"Ответ: {response[:200]}...")

    # Этот запрос не содержит кодовых слов → General модель
    response = qwen.generate("Привет! Расскажи о себе")
    print(f"\nЗапрос: 'Привет! Расскажи о себе'")
    print(f"Ответ: {response[:200]}...")


def example_2_forced_coder():
    """Пример 2: Принудительное использование Coder модели."""
    print("\n" + "=" * 60)
    print("📝 ПРИМЕР 2: Принудительное использование Coder")
    print("=" * 60)

    code = """
def bubble_sort(arr):
    n = len(arr)
    for i in range(n):
        for j in range(0, n-i-1):
            if arr[j] > arr[j+1]:
                arr[j], arr[j+1] = arr[j+1], arr[j]
    return arr
"""
    
    response = qwen.generate_coder(f"Проанализируй этот код и найди баги:\n{code}")
    print(f"\nКод:\n{code}")
    print(f"\nОтвет Coder модели: {response[:300]}...")


def example_3_forced_general():
    """Пример 3: Принудительное использование General модели."""
    print("\n" + "=" * 60)
    print("📝 ПРИМЕР 3: Принудительное использование General")
    print("=" * 60)

    response = qwen.generate_general("Какие у тебя хобби? Чем ты увлекаешься?")
    print(f"\nЗапрос: 'Какие у тебя хобби? Чем ты увлекаешься?'")
    print(f"\nОтвет General модели: {response[:300]}...")


def example_4_status():
    """Пример 4: Проверка статуса моделей."""
    print("\n" + "=" * 60)
    print("📝 ПРИМЕР 4: Проверка статуса моделей")
    print("=" * 60)

    status = qwen.status()
    print(f"\nСтатус моделей:")
    print(f"  Coder доступна: {status['coder_available']}")
    print(f"  General доступна: {status['general_available']}")
    print(f"  Путь Coder: {status['coder_model_path']}")
    print(f"  Путь General: {status['general_model_path']}")


def example_5_task_type():
    """Пример 5: Определение типа задачи."""
    print("\n" + "=" * 60)
    print("📝 ПРИМЕР 5: Определение типа задачи")
    print("=" * 60)

    queries = [
        "Напиши функцию для сортировки",
        "Привет, как дела?",
        "Как исправить ошибку в коде?",
        "Расскажи о своих способностях",
    ]

    for query in queries:
        is_coder = qwen.is_coder_task(query)
        model_type = "Coder" if is_coder else "General"
        print(f"\n  '{query}' → {model_type} модель")


def main():
    print("=" * 60)
    print("🤖 ПРИМЕРЫ ИСПОЛЬЗОВАНИЯ QWEN2.5 API")
    print("=" * 60)

    # Проверка статуса
    example_4_status()

    # Определение типа задачи
    example_5_task_type()

    # Примеры генерации (раскомментируйте для запуска)
    # example_1_auto_selection()
    # example_2_forced_coder()
    # example_3_forced_general()


if __name__ == "__main__":
    main()
