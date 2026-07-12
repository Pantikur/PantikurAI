"""
Точка входа для Наото — Визуального Архитектора.
"""

from __future__ import annotations

import io
import logging
import sys
from pathlib import Path

# Fix for Windows console encoding
if sys.stdout.encoding != "utf-8":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
if sys.stderr.encoding != "utf-8":
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8")

# Добавляем корень проекта Pantikur в путь
project_root = Path(__file__).parent.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from naoto.engine import Naoto
from naoto.engine.config import NaotoConfig


def setup_logging(level: str = "INFO") -> None:
    """Настраивает логирование."""
    logging.basicConfig(
        level=getattr(logging, level.upper(), logging.INFO),
        format="%(asctime)s [%(name)s] %(levelname)s: %(message)s",
        handlers=[
            logging.StreamHandler(sys.stdout),
            logging.FileHandler("naoto/engine/logs/naoto.log", encoding="utf-8")
        ]
    )


def demo() -> None:
    """Демонстрация возможностей Наото."""
    setup_logging("INFO")
    
    print()
    print("╔═══════════════════════════════════════════════════════════╗")
    print("║                                                           ║")
    print("║    ██████╗  ██████╗ ██╗  ██╗███████╗ █████╗ ███╗   ██║   ║")
    print("║   ██╔════╝ ██╔═══██╗██║ ██╔╝██╔════╝██╔══██╗████╗  ██║   ║")
    print("║   ██║  ███╗██║   ██║█████╔╝ █████╗  ███████║██╔██╗ ██║   ║")
    print("║   ██║   ██║██║   ██║██╔═██╗ ██╔══╝  ██╔══██║██║╚██╗██║   ║")
    print("║   ╚██████╔╝╚██████╔╝██║  ██╗███████╗██║  ██║██║ ╚████║   ║")
    print("║    ╚═════╝  ╚═════╝ ╚═╝  ╚═╝╚══════╝╚═╝  ╚═╝╚═╝  ╚═══╝   ║")
    print("║                                                           ║")
    print("║        ВИЗУАЛЬНЫЙ АРХИТЕКТОР НЕЙРОСЕТИ                    ║")
    print("║              Демонстрация возможностей                    ║")
    print("║                                                           ║")
    print("╚═══════════════════════════════════════════════════════════╝")
    print()
    
    # Создание экземпляра Наото
    config = NaotoConfig()
    naoto = Naoto(config)
    
    # Запуск
    naoto.start()
    
    print()
    print("=" * 60)
    print("1. СОЗДАНИЕ НАБРОСКА")
    print("=" * 60)
    
    sketch = naoto.create_sketch(
        "old clockwork robot in a workshop",
        style="concept"
    )
    if sketch:
        print(f"   ID: {sketch.result_id}")
        print(f"   Стиль: {sketch.sketch_style}")
        print(f"   Качество: {sketch.quality_score:.2f}")
        print(f"   Техники: {', '.join(sketch.techniques_applied[:3])}")
        print()
    
    print("=" * 60)
    print("2. СОЗДАНИЕ ЧЕРТЁЖА")
    print("=" * 60)
    
    drawing = naoto.create_drawing(
        "precision gear mechanism",
        standards="iso"
    )
    if drawing:
        print(f"   ID: {drawing.result_id}")
        print(f"   Стандарт: {drawing.drawing_standards}")
        print(f"   Точность: {drawing.accuracy:.2f}")
        print(f"   Проекций: {', '.join(drawing.projections[:3])}")
        print()
    
    print("=" * 60)
    print("3. СОЗДАНИЕ 3D-МОДЕЛИ")
    print("=" * 60)
    
    model = naoto.create_3d_model(
        "fantasy castle with towers and walls",
        detail_level="mid"
    )
    if model:
        print(f"   ID: {model.result_id}")
        print(f"   Полигонов: {model.polygon_count:,}")
        print(f"   Текстур: {model.texture_resolution}")
        print(f"   Материалов: {len(model.materials)}")
        print(f"   Качество: {model.quality_score:.2f}")
        print()
    
    print("=" * 60)
    print("4. АВТОНОМНАЯ ЗАДАЧА")
    print("=" * 60)
    
    autonomous = naoto.autonomous_task(
        "create a detailed sketch of a steampunk airship",
        autonomy_level="full"
    )
    if autonomous:
        print(f"   Тип задачи: {autonomous['task_type']}")
        print(f"   Найдено референсов: {autonomous['references_found']}")
        print(f"   Уровень автономности: {autonomous['autonomy_level']}")
        print()
    
    print("=" * 60)
    print("5. МОНИТОРИНГ ТРЕНДОВ")
    print("=" * 60)
    
    trends = naoto.run_monitoring_cycle()
    print(f"   Найдено трендов: {len(trends)}")
    for trend in trends[:3]:
        print(f"   - {trend.get('name', 'N/A')} ({trend.get('relevance', 'N/A')})")
    print()
    
    print("=" * 60)
    print("6. КОММУНИКАЦИЯ")
    print("=" * 60)
    
    # Отправка запроса Фуюки
    req = naoto.communication.send_request(
        to_sister="Фуюки",
        task_type="drawing",
        description="Визуализация электрической схемы для проекта",
        priority="high"
    )
    print(f"   Запрос Фуюки (электрика): {req.get('status', 'N/A')}")
    
    # Запрос для Люси
    req_lucy = naoto.communication.send_request(
        to_sister="Люси",
        task_type="3d",
        description="3D-модель механизма двигателя",
        priority="high"
    )
    print(f"   Запрос Люси (инженерия): {req_lucy.get('status', 'N/A')}")
    
    # Запрос для Ханако
    req_hanako = naoto.communication.send_request(
        to_sister="Ханако",
        task_type="sketch",
        description="Эскиз гравитационного поля",
        priority="medium"
    )
    print(f"   Запрос Ханако (гравитация): {req_hanako.get('status', 'N/A')}")
    
    # Запрос для Аква
    req_akva = naoto.communication.send_request(
        to_sister="Аква",
        task_type="drawing",
        description="Чертёж аэродинамической трубы",
        priority="medium"
    )
    print(f"   Запрос Аква (физика): {req_akva.get('status', 'N/A')}")
    
    # Запрос для Селесты
    req_celesta = naoto.communication.send_request(
        to_sister="Селеста",
        task_type="sketch",
        description="Анатомический набросок мышечной системы",
        priority="low"
    )
    print(f"   Запрос Селеста (биология): {req_celesta.get('status', 'N/A')}")
    
    # Запрос для Latislane
    req_latislane = naoto.communication.send_request(
        to_sister="Latislane",
        task_type="3d",
        description="3D-модель бионического скелета",
        priority="medium"
    )
    print(f"   Запрос Latislane (тела): {req_latislane.get('status', 'N/A')}")
    
    # Запрос для Юи
    req_yui = naoto.communication.send_request(
        to_sister="Юи",
        task_type="3d",
        description="Визуализация модели сознания и переноса разума",
        priority="high"
    )
    print(f"   Запрос Юи (сознание): {req_yui.get('status', 'N/A')}")
    print()
    
    # Получение запроса от Люси
    lucy_request = {
        "request_id": "REQ-20260712-001",
        "from": "Люси",
        "task_type": "drawing",
        "description": "Технический чертёж механизма двигателя",
        "priority": "high",
        "context": {"project": "engine_v2"}
    }
    received = naoto.communication.receive_request(lucy_request)
    print(f"   Запрос получен от Люси: {received.get('status', 'N/A')}")
    
    # Обработка запроса
    response = naoto.handle_request(lucy_request)
    print(f"   Ответ Люси: статус = {response.get('status', 'N/A')}")
    
    # Запрос визуальной работы от Аква
    akva_visual = naoto.communication.request_visual_work(
        from_sister="Аква",
        task_type="drawing",
        description="Чертёж формулы сопротивления материалов",
        priority="high"
    )
    print(f"   Запрос от Аква: {akva_visual.get('status', 'N/A')}")
    print()
    
    print("=" * 60)
    print("7. БАЗА ЗНАНИЙ")
    print("=" * 60)
    
    print(f"   Записей в базе: {naoto.core.knowledge_count()}")
    print(f"   Действий в журнале: {naoto.core.actions_count()}")
    print(f"   Взаимодействий: {naoto.communication.count()}")
    print()
    
    # Мониторинг всех сестёр
    print("=" * 60)
    print("9. МОНИТОРИНГ ВСЕХ СЁСТЕР")
    print("=" * 60)
    
    monitoring_report = naoto.communication.monitor_all_sisters()
    print(f"   Всего сестёр: {monitoring_report['total_sisters']}")
    print(f"   Активных: {monitoring_report['active_sisters']}")
    print(f"   Неактивных: {monitoring_report['inactive_sisters']}")
    print()
    
    for sister_name, sister_data in monitoring_report['sisters'].items():
        status_icon = "🟢" if sister_data['status'] == 'online' else "⚪"
        print(f"   {status_icon} {sister_name:12s} | {sister_data['specialization']}")
        print(f"       Последний контакт: {sister_data['last_contact'] or 'Никогда'}")
    print()
    
    # Статусы сестёр
    print("=" * 60)
    print("10. ДЕТальные СТАТУСЫ СЁСТЕР")
    print("=" * 60)
    
    for sister, status in naoto.communication.get_all_sister_status().items():
        print(f"   {sister}: {status.get('status', 'N/A')} | "
              f"Запросов: {status.get('requests_sent', 0)} → {status.get('requests_received', 0)} ←")
    print()
    
    # Остановка
    naoto.stop()
    
    print()
    print("╔═══════════════════════════════════════════════════════════╗")
    print("║                                                           ║")
    print("║   ✅ НААТО — ДЕМО ЗАВЕРШЕНО                               ║")
    print("║                                                           ║")
    print("║   «Каждый пиксель — это слово. Каждый рисунок — история.» ║")
    print("║                                                           ║")
    print("╚═══════════════════════════════════════════════════════════╝")
    print()


if __name__ == "__main__":
    demo()
