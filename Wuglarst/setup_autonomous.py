"""
Полная установка Wuglarst Autonomous Server.

Устанавливает:
- Все зависимости
- Автозапуск при старте Windows
- Фоновый процесс
- Интеграцию с Сидни
"""

import os
import subprocess
import sys
from pathlib import Path

print("=" * 60)
print("  🚀 Wuglarst Autonomous Server — Установка")
print("=" * 60)
print()

# Проверка Python
print("[1/5] Проверка Python...")
import sys
if sys.version_info < (3, 11):
    print("  ⚠️ Python 3.11+ рекомендуется")
else:
    print(f"  ✅ Python {sys.version_info.major}.{sys.version_info.minor} установлен")

# Установка зависимостей
print("[2/5] Установка зависимостей...")
packages = ["fastapi", "uvicorn", "pydantic"]
for pkg in packages:
    try:
        __import__(pkg.replace("-", "_"))
        print(f"  ✅ {pkg}")
    except ImportError:
        print(f"  ⏳ Установка {pkg}...")
        subprocess.check_call([
            sys.executable, "-m", "pip", "install", pkg, "-q"
        ])
        print(f"  ✅ {pkg} установлен")

# Создание директорий
print("[3/5] Создание директорий...")
data_dir = Path(__file__).parent / "data"
data_dir.mkdir(exist_ok=True)
print(f"  ✅ {data_dir}")

logs_dir = Path(__file__).parent.parent / "logs"
logs_dir.mkdir(exist_ok=True)
print(f"  ✅ {logs_dir}")

# Настройка
print("[4/5] Настройка...")
config = {
    "host": "0.0.0.0",
    "port": 8001,
    "auto_start": True,
    "sidney_integrated": True
}

config_file = Path(__file__).parent / "wuglarst_config.json"
import json
with open(config_file, 'w', encoding='utf-8') as f:
    json.dump(config, f, indent=2, ensure_ascii=False)
print(f"  ✅ Конфигурация сохранена")

# Автозапуск
print("[5/5] Установка автозапуска...")
try:
    subprocess.check_call([sys.executable, "daemon.py", "install"])
    print("  ✅ Автозапуск установлен")
except Exception as e:
    print(f"  ⚠️ Автозапуск не установлен: {e}")
    print("  💡 Запустите вручную: python daemon.py install")

print()
print("=" * 60)
print("  ✅ Установка завершена!")
print("=" * 60)
print()
print("📋 Следующие шаги:")
print("  1. Запустите сервер:")
print("     python daemon.py start")
print()
print("  2. Откройте браузер:")
print("     http://localhost:8001")
print()
print("  3. Проверьте здоровье:")
print("     http://localhost:8001/health")
print()
print("=" * 60)
