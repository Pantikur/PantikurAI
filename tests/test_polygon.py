"""
Тест SHIORI POLYGON — Боевой тренажёр Шиори.

Демонстрирует работу изолированного полигона для тренировки защиты.
"""

import sys
import logging
from pathlib import Path

# Добавляем корень проекта в путь
sys.path.insert(0, str(Path(__file__).parent))

from shiori.polygon.polygon_core import (
    ShioriPolygon,
    ThreatType,
    DefenseAction,
    create_polygon,
)


def setup_logging():
    """Настроить логирование."""
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
        handlers=[
            logging.StreamHandler(sys.stdout),
        ],
    )


def test_single_training():
    """Тест одиночной тренировки."""
    print("\n" + "=" * 70)
    print("ТЕСТ 1: Одиночная тренировка")
    print("=" * 70)
    
    # Создаём полигон
    polygon = create_polygon()
    
    # Тренировка против случайной угрозы
    session = polygon.train_single()
    
    print(f"\nРезультат тренировки:")
    print(f"   Угроза: {session.threats_faced[0].name}")
    print(f"   Защита: {session.defenses_used[0].action.value}")
    print(f"   Успех: {'ДА' if session.defenses_used[0].success else 'НЕТ'}")
    print(f"   Опыт: +{session.experience_gained} XP")
    print(f"   Рейтинг: {session.rating}")
    
    return session


def test_wave_training():
    """Тест тренировки волной."""
    print("\n" + "=" * 70)
    print("ТЕСТ 2: Тренировка волной (5 угроз)")
    print("=" * 70)
    
    polygon = create_polygon()
    
    # Волна из 5 угроз
    sessions = polygon.train_wave(count=5, min_difficulty=2, max_difficulty=5)
    
    print(f"\nРезультаты волны:")
    for i, session in enumerate(sessions, 1):
        threat = session.threats_faced[0]
        defense = session.defenses_used[0]
        status = "OK" if defense.success else "FAIL"
        print(f"   {i}. {threat.name} | {defense.action.value} | {status} | +{session.experience_gained} XP")
    
    total_exp = sum(s.experience_gained for s in sessions)
    print(f"\n   Итого опыта: +{total_exp} XP")
    
    return sessions


def test_specialized_training():
    """Тест специализированной тренировки."""
    print("\n" + "=" * 70)
    print("ТЕСТ 3: Специализация (DDoS x5)")
    print("=" * 70)
    
    polygon = create_polygon()
    
    # Специализация против DDoS
    sessions = polygon.train_specialized(
        threat_type=ThreatType.HACKER_DDOS,
        count=5,
        difficulty_range=(3, 6)
    )
    
    print(f"\nРезультаты специализации:")
    for i, session in enumerate(sessions, 1):
        threat = session.threats_faced[0]
        defense = session.defenses_used[0]
        status = "OK" if defense.success else "FAIL"
        print(f"   {i}. {threat.name} | {defense.action.value} | {status} | +{session.experience_gained} XP")
    
    return sessions


def test_status():
    """Тест просмотра статуса."""
    print("\n" + "=" * 70)
    print("ТЕСТ 4: Статус и прогресс")
    print("=" * 70)
    
    polygon = create_polygon()
    status = polygon.get_status()
    
    print(f"\nСтатус полигона:")
    stats = status["stats"]
    print(f"   Сессий проведено: {stats['total_sessions']}")
    print(f"   Угроз отражено: {stats['total_threats_faced']}")
    print(f"   Успешных защит: {stats['successful_defenses']}")
    print(f"   Неудачных защит: {stats['failed_defenses']}")
    print(f"   Успешность: {stats['success_rate']}%")
    print(f"   Всего опыта: {stats['total_experience']} XP")
    print(f"   Текущий ранг: {stats['current_rank']}")
    print(f"   Лучший рейтинг: {stats['best_rating']}")
    
    rank_info = status["rank_info"]
    print(f"\nРанг:")
    print(f"   Текущий: {rank_info['current']}")
    print(f"   Прогресс: {rank_info['progress']}%")
    print(f"   Следующий: {rank_info['next_rank']}")
    
    return status


def test_all_threat_types():
    """Тест против всех типов угроз."""
    print("\n" + "=" * 70)
    print("ТЕСТ 5: Все типы угроз (по 1 каждой)")
    print("=" * 70)
    
    polygon = create_polygon()
    
    print(f"\nТренировка против всех типов угроз:")
    for threat_type in ThreatType:
        session = polygon.train_single(threat_type=threat_type, difficulty=5)
        threat = session.threats_faced[0]
        defense = session.defenses_used[0]
        status = "OK" if defense.success else "FAIL"
        print(f"   {threat_type.value:30} | {defense.action.value:15} | {status} | +{session.experience_gained} XP")
    
    return True


if __name__ == "__main__":
    print("\n" + "=" * 70)
    print("SHIORI POLYGON — БОЕВОЙ ТРЕНАЖЁР")
    print("Изолированная среда для тренировки защиты")
    print("=" * 70)
    
    setup_logging()
    
    # Запускаем тесты
    test_single_training()
    test_wave_training()
    test_specialized_training()
    test_status()
    test_all_threat_types()
    
    # Финальный статус
    print("\n" + "=" * 70)
    print("ФИНАЛЬНЫЙ СТАТУС")
    print("=" * 70)
    
    polygon = create_polygon()
    status = polygon.get_status()
    stats = status["stats"]
    
    print(f"\nИтоговая статистика:")
    print(f"   Всего сессий: {stats['total_sessions']}")
    print(f"   Всего угроз: {stats['total_threats_faced']}")
    print(f"   Успешность: {stats['success_rate']}%")
    print(f"   Всего опыта: {stats['total_experience']} XP")
    print(f"   Текущий ранг: {stats['current_rank']}")
    print(f"   Лучший рейтинг: {stats['best_rating']}")
    
    print("\nТЕСТЫ ПОЛИГОНА ЗАВЕРШЕНЫ!")
    print("=" * 70 + "\n")
