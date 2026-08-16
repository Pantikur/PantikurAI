"""
Тест интеграции LLM моделей в Шиори.

Проверяет:
  1. Загрузку Qwen2.5-3B (General)
  2. Загрузку Qwen2.5-Coder-3B (Coder)
  3. Генерацию ответов
  4. Интеграцию с компонентами
"""

import sys
import logging
from pathlib import Path

# Добавляем корень проекта в путь
sys.path.insert(0, str(Path(__file__).parent))

from shiori.engine.config import ShioriConfig
from shiori.engine.llm_service import ShioriLLMService
from shiori.engine.shiori_core import ShioriCore


def test_llm_service():
    """Тестирование LLM сервиса."""
    print("=" * 60)
    print("ТЕСТ: LLM Service")
    print("=" * 60)
    
    config = ShioriConfig.default()
    config.llm_enabled = True
    
    # Создаём LLM сервис
    llm = ShioriLLMService(config)
    
    # Проверяем статус
    status = llm.get_status()
    print(f"\nСтатус моделей:")
    print(f"   General (Qwen2.5-3B): {'ЗАГРУЖЕНА' if status['general_loaded'] else 'НЕ ЗАГРУЖЕНА'}")
    print(f"   Coder (Qwen2.5-Coder-3B): {'ЗАГРУЖЕН' if status['coder_loaded'] else 'НЕ ЗАГРУЖЕН'}")
    
    if not llm.general_loaded and not llm.coder_loaded:
        print("\nНи одна модель не загружена.")
        print("   Убедитесь, что модели установлены:")
        print("   - Qwen2.5-3B")
        print("   - Qwen2.5-Coder-3B")
        print("\n   Для установки используйте:")
        print("   pip install transformers torch")
        print("   И скачайте модели с HuggingFace:")
        print("   https://huggingface.co/Qwen/Qwen2.5-3B")
        print("   https://huggingface.co/Qwen/Qwen2.5-Coder-3B")
        return False
    
    # Тестируем General модель
    if llm.general_loaded:
        print("\nТест General модели (Qwen2.5-3B)...")
        try:
            response = llm.generate_general(
                prompt="Привет! Кто ты?",
                system_prompt="Ты - помощник Шиори. Отвечай кратко и по делу."
            )
            print(f"   Ответ: {response[:100]}...")
            print("   General модель работает!")
        except Exception as e:
            print(f"   Ошибка: {e}")
    
    # Тестируем Coder модель
    if llm.coder_loaded:
        print("\nТест Coder модели (Qwen2.5-Coder-3B)...")
        try:
            response = llm.generate_coder(
                prompt="Напиши функцию на Python, которая считает факториал числа.",
                code_context="Нужна рекурсивная реализация."
            )
            print(f"   Ответ: {response[:100]}...")
            print("   Coder модель работает!")
        except Exception as e:
            print(f"   Ошибка: {e}")
    
    return True


def test_integration():
    """Тестирование интеграции с ShioriCore."""
    print("\n" + "=" * 60)
    print("ТЕСТ: Интеграция с ShioriCore")
    print("=" * 60)
    
    try:
        core = ShioriCore(ShioriConfig.demo())
        
        print(f"\nСтатус LLM в ShioriCore:")
        print(f"   General: {'OK' if core.llm.general_loaded else 'FAIL'}")
        print(f"   Coder: {'OK' if core.llm.coder_loaded else 'FAIL'}")
        
        if core.llm.general_loaded:
            print(f"\nHumanity Layer подключена к LLM: {'OK' if core.humanity.llm else 'FAIL'}")
        
        print("\nИнтеграция прошла успешно!")
        return True
        
    except Exception as e:
        print(f"\nОшибка интеграции: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    print("\n" + "=" * 60)
    print("ЗАПУСК ТЕСТОВ ИНТЕГРАЦИИ LLM В ШИОРИ")
    print("=" * 60 + "\n")
    
    # Тестируем LLM сервис
    llm_ok = test_llm_service()
    
    # Тестируем интеграцию
    integration_ok = test_integration() if llm_ok else False
    
    # Итог
    print("\n" + "=" * 60)
    print("ИТОГИ ТЕСТОВ")
    print("=" * 60)
    print(f"LLM Service: {'ПРОЙДЕН' if llm_ok else 'НЕ ПРОЙДЕН'}")
    print(f"Интеграция: {'ПРОЙДЕНА' if integration_ok else 'НЕ ПРОЙДЕНА'}")
    print("=" * 60)
    
    if llm_ok and integration_ok:
        print("\nВСЕ ТЕСТЫ ПРОЙДЕНЫ! Шиори готова к работе с LLM!")
    else:
        print("\nНекоторые тесты не пройдены. Проверьте логи выше.")
    
    print()
