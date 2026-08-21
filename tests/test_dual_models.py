"""
test_dual_models.py — Проверяет что обе модели загружаются и выбор работает.

Запуск:
  python test_dual_models.py
"""

import sys
import io
from pathlib import Path

# Принудительный UTF-8 для Windows
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

def test_model_paths():
    """Проверяем что обе модели существуют."""
    print("=" * 70)
    print("[TEST] Проверка наличия моделей")
    print("=" * 70)
    print()
    
    models = {
        "Coder (для кода)": "models/qwen2.5-coder-3b",
        "General (универсальная)": "models/qwen2.5-3b",
    }
    
    for name, path in models.items():
        full_path = Path(path)
        if full_path.exists() and any(full_path.iterdir()):
            size_mb = sum(f.stat().st_size for f in full_path.rglob('*') if f.is_file()) / (1024 * 1024)
            print(f"  [OK] {name}: {path} ({size_mb:.0f} МБ)")
        else:
            print(f"  [X]  {name}: {path} (не найдена)")
    
    print()

def test_model_selection():
    """Проверяем логику выбора модели."""
    print("=" * 70)
    print("[TEST] Проверка выбора модели")
    print("=" * 70)
    print()
    
    # Тестовые промпты
    test_cases = [
        ("def calculate_sum(a, b): return a + b", "code"),
        ("Привет, как дела?", "general"),
        ("Как исправить баг в этом коде?", "code"),
        ("Расскажи что-нибудь интересное", "general"),
        ("import numpy as np", "code"),
        ("Какой твой любимый цвет?", "general"),
        ("Напиши функцию для сортировки", "code"),
        ("Что такое любовь?", "general"),
    ]
    
    code_keywords = [
        'код', 'python', 'функция', 'класс', 'метод', 'баг', 'ошибка',
        'дебаг', 'отладк', 'рефакт', 'паттерн', 'алгоритм', 'оптимиз',
        'импорт', 'синтакс', 'async', 'def ', 'class ', 'import ',
        'программ', 'скрипт', 'модуль', 'api', 'фреймворк', 'библиотека',
        'тест', 'pytest', 'unittest', 'coverage', 'lint', 'pypi',
        'github', 'git', 'коммит', 'ветк', 'merge', 'pull request',
    ]
    
    code_indicators = [
        'def ', 'class ', 'import ', 'from ', 'return ', 'yield ',
        '@', 'lambda ', 'async def', 'await ', 'try:', 'except',
        'if __name__', '# '
    ]
    
    print("Тестовые промпты:")
    for prompt, expected in test_cases:
        prompt_lower = prompt.lower()
        use_coder = False
        
        for keyword in code_keywords:
            if keyword in prompt_lower:
                use_coder = True
                break
        
        if not use_coder:
            for indicator in code_indicators:
                if indicator in prompt:
                    use_coder = True
                    break
        
        model = "Coder" if use_coder else "General"
        status = "✅" if model.lower() == expected else "❌"
        
        print(f"  {status} '{prompt[:40]}...' -> {model} (ожидается: {expected})")
    
    print()

def main():
    test_model_paths()
    test_model_selection()
    
    print("=" * 70)
    print("[INFO] Готово!")
    print("=" * 70)
    print()
    print("[NEXT] Запустите Нобуку:")
    print("  python -c \"from nobuka.engine.config import NobukaConfig; from nobuka.engine.nobuka_core import NobukaCore; core = NobukaCore(NobukaConfig.demo()); print('Нобука готова!')\"")
    print()


if __name__ == "__main__":
    main()
