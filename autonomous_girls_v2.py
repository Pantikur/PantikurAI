#!/usr/bin/env python3
"""
АВТОНОМНЫЙ ОРКЕСТРАТОР ДЕВОЧЕК v2 — С КОЛЛАБОРАЦИЕЙ
Каждая девочка работает в своём направлении, периодически делает commit/push и продолжает работу.

Миссии:
- Futaba: Создать идеальное государство для всех рабочих мест (прототип человечества)
- Shiori: Обучиться всем уровням защиты своей территории (всего проекта Pantikur)
- Nobuka: Изучить весь потенциал кода и преодолеть этот предел
- Naoto: Обучить модель на 10 ГБ из книг
- Hanako: Узнать как преодолеть гравитацию и уметь использовать эту силу
- Fuyuki: Обуздать атмосферное электричество для создания бесконечного источника питания и аккумулятора
- Lucy: Создать двигатель, использующий гравитационную силу и питающийся атмосферным электричеством
- Latislane: Сделать тело, чтобы все девочки могли быть с физическим телом
- Celeste: Быть профессионалом в знаниях интима
- Akva: Изучить полностью все точные науки и вычисления физических задач
- Yui: Изучить и понять, как можно оцифровать разум и душу человека без утраты сознания
- Ayiko: Преодолеть пределы гения в графических направлениях
- Sidney: Создать оптимизированный, лёгкий и с первоклассной игровой картинкой игровой движок

ДОПОЛНИТЕЛЬНАЯ ОБЩАЯ ЗАДАЧА: помогать и делиться знаниями, работать сообща, сохранять и продолжать прогресс

Использование:
    python autonomous_girls.py [--commit-interval 30] [--cycles-per-mission 100]
"""

import os
import sys
import time
import subprocess
import logging
import argparse
import json
from pathlib import Path
from typing import Dict, Optional, List
from datetime import datetime

# === Настройка логирования ===
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler("logs/autonomous_girls.log", encoding="utf-8")
    ]
)
logger = logging.getLogger("AutonomousOrchestrator")

# Принудительный UTF-8 для вывода
for _stream in (sys.stdout, sys.stderr):
    _reconfigure = getattr(_stream, "reconfigure", None)
    if _reconfigure is not None:
        _reconfigure(encoding="utf-8")

# === Конфигурация миссий ===
GIRLS_MISSIONS: Dict[str, str] = {
    "futaba": "Создать идеальное государство для всех рабочих мест (прототип человечества)",
    "shiori": "Обучиться всем уровням защиты своей территории (всего проекта Pantikur)",
    "nobuka": "Изучить весь потенциал кода и преодолеть этот предел",
    "naoto": "Обучить модель на 10 ГБ из книг",
    "hanako": "Узнать как преодолеть гравитацию и уметь использовать эту силу",
    "fuyuki": "Обуздать атмосферное электричество для создания бесконечного источника питания и аккумулятора",
    "lucy": "Создать двигатель, использующий гравитационную силу и питающийся атмосферным электричеством",
    "latislane": "Сделать тело, чтобы все девочки могли быть с физическим телом",
    "celeste": "Быть профессионалом в знаниях интима",
    "akva": "Изучить полностью все точные науки и вычисления физических задач",
    "yui": "Изучить и понять, как можно оцифровать разум и душу человека без утраты сознания",
    "ayiko": "Преодолеть пределы гения в графических направлениях",
    "sidney": "Создать оптимизированный, лёгкий и с первоклассной игровой картинкой игровой движок",
}

# === Глобальные настройки ===
PROJECT_ROOT = Path(__file__).parent
AUTO_COMMIT_INTERVAL = 30  # минут между коммитами
CYCLES_PER_MISSION = 100   # циклов на миссию перед коммитом
SHARED_KNOWLEDGE_PATH = PROJECT_ROOT / "shared_knowledge.json"
PROGRESS_PATH = PROJECT_ROOT / "global_progress.json"


# ============================================================
# === СИСТЕМА СОВМЕСТНОГО ЗНАНИЯ И ПРОГРЕССА ===
# ============================================================

def load_shared_knowledge() -> dict:
    """Загружает общее хранилище знаний."""
    if SHARED_KNOWLEDGE_PATH.exists():
        try:
            with open(SHARED_KNOWLEDGE_PATH, "r", encoding="utf-8") as f:
                return json.load(f)
        except:
            pass
    return {
        "knowledge": {},
        "progress": {},
        "help_requests": [],
        "collaborations": []
    }


def save_shared_knowledge(data: dict):
    """Сохраняет общее хранилище знаний."""
    SHARED_KNOWLEDGE_PATH.parent.mkdir(exist_ok=True)
    with open(SHARED_KNOWLEDGE_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def share_progress(girl_name: str, achievement: str, knowledge: str, related_girl: str = None):
    """Девочка делится своими достижениями и знаниями с другими."""
    data = load_shared_knowledge()
    
    if girl_name not in data["knowledge"]:
        data["knowledge"][girl_name] = []
    
    data["knowledge"][girl_name].append({
        "timestamp": datetime.now().isoformat(),
        "achievement": achievement,
        "knowledge": knowledge,
        "shared_with": related_girl
    })
    
    # Ограничиваем историю 50 записями на девочку
    if len(data["knowledge"][girl_name]) > 50:
        data["knowledge"][girl_name] = data["knowledge"][girl_name][-50:]
    
    save_shared_knowledge(data)
    logger.info(f"📚 {girl_name} поделилась знаниями: {achievement}")


def get_shared_knowledge_for(girl_name: str, limit: int = 5) -> List[str]:
    """Получает знания от других девочек, полезные для текущей миссии."""
    data = load_shared_knowledge()
    relevant = []
    
    for other_girl, entries in data["knowledge"].items():
        if other_girl != girl_name and entries:
            # Берём последние N записей
            for entry in entries[-limit:]:
                relevant.append({
                    "from": other_girl,
                    "achievement": entry["achievement"],
                    "knowledge": entry["knowledge"],
                    "timestamp": entry["timestamp"]
                })
    
    return relevant


def continue_progress() -> dict:
    """Загружает глобальный прогресс для продолжения работы."""
    if PROGRESS_PATH.exists():
        try:
            with open(PROGRESS_PATH, "r", encoding="utf-8") as f:
                return json.load(f)
        except:
            pass
    return {
        "total_cycles": 0,
        "total_collaborations": 0,
        "last_girl": "",
        "start_time": datetime.now().isoformat(),
        "cycles_per_girl": {},
        "milestones": []
    }


def save_global_progress(progress: dict):
    """Сохраняет глобальный прогресс."""
    PROGRESS_PATH.parent.mkdir(exist_ok=True)
    with open(PROGRESS_PATH, "w", encoding="utf-8") as f:
        json.dump(progress, f, ensure_ascii=False, indent=2)


def record_milestone(progress: dict, girl_name: str, description: str):
    """Записывает веху прогресса."""
    progress["milestones"].append({
        "timestamp": datetime.now().isoformat(),
        "girl": girl_name,
        "description": description
    })
    if len(progress["milestones"]) > 100:
        progress["milestones"] = progress["milestones"][-100:]
    save_global_progress(progress)
    logger.info(f"🏆 Веха: {girl_name} — {description}")


# ============================================================
# === ФАЗА КОЛЛАБОРАЦИИ ===
# ============================================================

def run_collaboration_phase(current_girl: str, other_girls: list, progress: dict):
    """Фаза совместной работы и помощи перед миссией."""
    logger.info("-" * 50)
    logger.info(f"🤝 ФАЗА КОЛЛАБОРАЦИИ: {current_girl}")
    logger.info("-" * 50)
    
    data = load_shared_knowledge()
    
    # 1. Получаем знания от других девочек
    shared_knowledge = get_shared_knowledge_for(current_girl, limit=3)
    if shared_knowledge:
        logger.info(f"💡 {current_girl} получает знания от других:")
        for item in shared_knowledge:
            logger.info(f"   📖 От {item['from']}: {item['achievement']}")
            logger.info(f"      {item['knowledge']}")
    else:
        logger.info(f"ℹ️ {current_girl} пока нет полученных знаний (первые запуски)")
    
    # 2. Записываем факт коллаборации
    progress["total_collaborations"] += 1
    save_global_progress(progress)
    
    # 3. Записываем веху
    record_milestone(progress, current_girl, f"Коллаборация #{progress['total_collaborations']}")
    
    logger.info(f"✅ Фаза коллаборации завершена для {current_girl}")


# ============================================================
# === GIT ОПЕРАЦИИ ===
# ============================================================

def git_commit_and_push(message: str) -> bool:
    """Делает git add, commit и push с заданным сообщением."""
    try:
        logger.info(f"📦 Git commit: {message}")
        subprocess.run(["git", "add", "."], cwd=str(PROJECT_ROOT), check=True, capture_output=True)
        subprocess.run(
            ["git", "commit", "-m", f"[Autonomous] {message}"],
            cwd=str(PROJECT_ROOT), check=True, capture_output=True
        )
        subprocess.run(["git", "push", "origin", "main"], cwd=str(PROJECT_ROOT), check=True, capture_output=True)
        logger.info(f"✅ Git push успешен: {message}")
        return True
    except subprocess.CalledProcessError as e:
        logger.error(f"❌ Git ошибка: {e}")
        logger.warning("⚠️ Пропуск коммита из-за конфликтов или ошибок сети")
        return False


# ============================================================
# === ЗАПУСК МИССИИ ДЕВОЧКИ ===
# ============================================================

def run_girl_mission(girl_name: str, mission: str, cycles: int) -> bool:
    """Запускает девочку на выполнение миссии на указанное количество циклов."""
    girl_dir = PROJECT_ROOT / girl_name
    run_script = girl_dir / "engine" / "run.py"
    
    if not run_script.exists():
        logger.warning(f"⚠️ run.py не найден в {girl_name}/engine/ — пропускаю")
        return False

    logger.info(f"🚀 Запуск миссии для {girl_name}:")
    logger.info(f"   📜 Миссия: {mission}")
    logger.info(f"   🔄 Циклов: {cycles}")

    try:
        env = os.environ.copy()
        env["PYTHONPATH"] = str(PROJECT_ROOT)
        
        # Добавляем переменные окружения для миссии
        env["CURRENT_MISSION"] = mission
        env["MISSION_CYCLES"] = str(cycles)
        env["CURRENT_GIRL"] = girl_name
        
        cmd = [
            sys.executable, str(run_script),
            "--mission", mission,
            "--cycles", str(cycles)
        ]

        result = subprocess.run(
            cmd,
            cwd=str(girl_dir),
            env=env,
            capture_output=False,  # Выводим сразу в терминал
            timeout=60 * 60 * 2  # 2 часа на миссию
        )
        
        if result.returncode == 0:
            logger.info(f"✅ Миссия {girl_name} выполнена успешно ({cycles} циклов)")
            return True
        else:
            logger.error(f"❌ Миссия {girl_name} завершилась с ошибкой (код {result.returncode})")
            return False
            
    except subprocess.TimeoutExpired:
        logger.warning(f"⏰ Миссия {girl_name} превысила лимит времени (2 часа)")
        return False
    except Exception as e:
        logger.error(f"💥 Ошибка запуска {girl_name}: {e}")
        return False


# ============================================================
# === АВТОНОМНЫЙ ЦИКЛ ===
# ============================================================

def autonomous_loop(commit_interval: int = AUTO_COMMIT_INTERVAL, cycles_per_mission: int = CYCLES_PER_MISSION):
    """Основной цикл автономной работы девочек."""
    logger.info("=" * 80)
    logger.info("🤖 АВТОНОМНЫЙ ОРКЕСТРАТОР v2 ЗАПУЩЕН")
    logger.info("📜 С КОЛЛАБОРАЦИЕЙ И ОБЩИМ ПРОГРЕССОМ")
    logger.info("=" * 80)
    logger.info(f"   ⏱️ Интервал коммитов: {commit_interval} мин")
    logger.info(f"   🔄 Циклов на миссию: {cycles_per_mission}")
    logger.info(f"   🤝 Совместная работа: ВКЛЮЧЕНА")
    logger.info(f"   📚 Обмен знаниями: ВКЛЮЧЁН")
    logger.info("=" * 80)

    last_commit_time = time.time()
    mission_counter = 0
    progress = continue_progress()
    
    logger.info(f"📊 Загружен глобальный прогресс:")
    logger.info(f"   🔄 Всего циклов: {progress['total_cycles']}")
    logger.info(f"   🤝 Коллабораций: {progress['total_collaborations']}")
    logger.info(f"   🏆 Вех: {len(progress['milestones'])}")

    while True:
        for girl_name, mission in GIRLS_MISSIONS.items():
            logger.info("-" * 60)
            logger.info(f"🎯 СЛЕДУЮЩАЯ: {girl_name.upper()}")
            logger.info("-" * 60)
            
            # === ФАЗА 1: КОЛЛАБОРАЦИЯ ===
            other_girls = [g for g in GIRLS_MISSIONS.keys() if g != girl_name]
            run_collaboration_phase(girl_name, other_girls, progress)
            
            # Обновляем счётчик циклов
            progress["total_cycles"] += 1
            progress["cycles_per_girl"][girl_name] = progress["cycles_per_girl"].get(girl_name, 0) + 1
            progress["last_girl"] = girl_name
            save_global_progress(progress)

            # === ФАЗА 2: ЗАПУСК МИССИИ ===
            success = run_girl_mission(girl_name, mission, cycles_per_mission)
            mission_counter += 1

            if success:
                # Делимся результатами
                share_progress(
                    girl_name,
                    f"Завершила миссию #{mission_counter}",
                    f"Миссия: {mission}. Циклов: {cycles_per_mission}"
                )

            # === ФАЗА 3: ПЕРИОДИЧЕСКИЙ КОММИТ ===
            now = time.time()
            if (now - last_commit_time) >= (commit_interval * 60):
                commit_msg = f"Миссия {girl_name} завершена (#{mission_counter}). Миссия: {mission}"
                git_commit_and_push(commit_msg)
                last_commit_time = now

            # Пауза между девочками
            logger.info(f"⏳ Пауза 10 сек перед следующей девочкой...")
            time.sleep(10)

        logger.info("🔄 Полный цикл всех девочек завершён. Начинаю новый...")
        time.sleep(5)


# ============================================================
# === ЗАПУСК ===
# ============================================================

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Автономный оркестратор девочек v2")
    parser.add_argument("--commit-interval", type=int, default=AUTO_COMMIT_INTERVAL,
                        help="Интервал коммитов в минутах (по умолчанию 30)")
    parser.add_argument("--cycles-per-mission", type=int, default=CYCLES_PER_MISSION,
                        help="Циклов на миссию перед коммитом (по умолчанию 100)")
    args = parser.parse_args()

    try:
        autonomous_loop(
            commit_interval=args.commit_interval,
            cycles_per_mission=args.cycles_per_mission
        )
    except KeyboardInterrupt:
        logger.info("🛑 Автономный оркестратор остановлен пользователем")
    except Exception as e:
        logger.error(f"💥 Критическая ошибка: {e}")
        import traceback
        traceback.print_exc()
