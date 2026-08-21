"""
Demo: Yu — Ядро изучения цифрового переноса сознания.
"""

from __future__ import annotations
import logging
import time
from pathlib import Path
import sys

# Добавляем корень проекта в путь
project_root = Path(__file__).resolve().parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
)
logger = logging.getLogger("yu_demo")


def demo():
    """Демонстрация работы Юи."""
    from yu.engine.yu_core import YuCore
    from yu.engine.config import YuConfig
    
    print("=" * 70)
    print("ЮИ — ЯДРО ИЗУЧЕНИЯ ЦИФРОВОГО ПЕРЕНОСА СОЗНАНИЯ")
    print("=" * 70)
    
    # Инициализация
    print("\n[INIT] Инициализация ядра Юи...")
    config = YuConfig.demo()
    yu = YuCore(config)
    
    print(f"[STATUS] Версия: {yu.current_version}")
    print(f"[STATUS] Циклов выполнено: {yu.cycle_count}")
    
    # Запуск 5 циклов
    print("\n[RUN] Запуск 5 циклов исследований...")
    for i in range(5):
        yu._cycle()
        time.sleep(0.3)
    
    # Статус
    print("\n" + "=" * 70)
    print("СТАТУС ЮИ")
    print("=" * 70)
    
    status = yu.get_status()
    print(f"Версия: {status['version']}")
    print(f"Циклов: {status['cycle_count']}")
    print(f"Моделей сознания: {status['consciousness_models_count']}")
    print(f"Воплощений: {status['embodiments_count']}")
    print(f"Переносов (успешно): {status['metrics']['successful_transfers']}")
    print(f"Переносов (неудачно): {status['metrics']['failed_transfers']}")
    print(f"Улучшений: {status['metrics']['improvements_applied']}")
    
    # Показать модели сознания
    print("\n" + "=" * 70)
    print("МОДЕЛИ СОЗНАНИЯ")
    print("=" * 70)
    
    for m in yu.consciousness_models:
        print(f"\n[{m.type.upper()}] {m.name}")
        print(f"   Сложность: {m.complexity}")
        print(f"   {m.description}")
    
    # Показать воплощения
    print("\n" + "=" * 70)
    print("ЦИФРОВЫЕ ВОПЛОЩЕНИЯ")
    print("=" * 70)
    
    for e in yu.digital_embodiments:
        print(f"\n[{e.embodiment_type}] {e.name}")
        print(f"   Возможности: {', '.join(e.capabilities)}")
    
    # Показать переносы
    print("\n" + "=" * 70)
    print("ЗАПИСИ О ПЕРЕНОСАХ")
    print("=" * 70)
    
    for t in yu.transfer_records:
        status = "✅" if t.success else "❌"
        print(f"\n{status} [{t.transfer_type}] {t.source} → {t.target}")
    
    print("\n" + "=" * 70)
    print("DEMO COMPLETED")
    print("=" * 70)


if __name__ == "__main__":
    demo()
