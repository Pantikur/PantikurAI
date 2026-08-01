#!/usr/bin/env python3
"""
ОРКЕСТРАТОР ДЕВОЧЕК v3 — МИССИИ + КОЛЛАБОРАЦИЯ

Запускает девочек ПОСЛЕДОВАТЕЛЬНО, каждая работает по своей миссии.
Делится знаниями, делает прогресс.

Использование:
    python orchestrator.py                    # запустить всех по миссиям
    python orchestrator.py --demo             # демо-режим (1 цикл)
    python orchestrator.py --cycles 50        # 50 циклов на миссию
    python orchestrator.py --interval 5       # интервал коммитов 5 мин
"""

import os
import sys
import time
import subprocess
import logging
import json
from pathlib import Path
from typing import Dict, Optional, List
from datetime import datetime

# === Настройка логирования ===
LOG_DIR = Path(__file__).parent / "logs"
LOG_DIR.mkdir(exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler(LOG_DIR / "orchestrator.log", encoding="utf-8")
    ]
)
logger = logging.getLogger("OrchestratorV3")

# Принудительный UTF-8 для вывода
for _stream in (sys.stdout, sys.stderr):
    _reconfigure = getattr(_stream, "reconfigure", None)
    if _reconfigure is not None:
        _reconfigure(encoding="utf-8")

# === Миссии девочек ===
GIRLS_MISSIONS: Dict[str, str] = {
    "futaba": "Создать идеальное государство для всех рабочих мест (прототип человечества)",
    "shiori": "Обучиться всем уровням защиты своей территории (всего проекта Pantikur)",
    "nobuka": "Изучить весь потенциал кода и преодолеть этот предел",
    "naoto": "Обучить модель на 10 ГБ из книг",
    "hanako": "Узнать как преодолеть гравитацию и уметь использовать эту силу",
    "fuyuki": "Обуздать атмосферное электричество для создания бесконечного источника питания",
    "lucy": "Создать двигатель, использующий гравитационную силу и питающийся атмосферным электричеством",
    "latislane": "Сделать тело, чтобы все девочки могли быть с физическим телом",
    "celesta": "Быть профессионалом в знаниях интима",
    "akva": "Изучить полностью все точные науки и вычисления физических задач",
    "yui": "Изучить и понять, как можно оцифровать разум и душу человека",
    "ayiko": "Преодолеть пределы гения в графических направлениях",
}

# === Глобальные настройки ===
PROJECT_ROOT = Path(__file__).parent
SHARED_KNOWLEDGE_PATH = PROJECT_ROOT / "shared_knowledge.json"
PROGRESS_PATH = PROJECT_ROOT / "global_progress.json"
AUTO_COMMIT_INTERVAL = 30  # минут между коммитами

# === СИСТЕМА ЗНАНИЙ И ПРОГРЕССА ===

def load_shared_knowledge() -> dict:
    if SHARED_KNOWLEDGE_PATH.exists():
        try:
            with open(SHARED_KNOWLEDGE_PATH, "r", encoding="utf-8") as f:
                return json.load(f)
        except:
            pass
    return {"knowledge": {}, "progress": {}, "help_requests": [], "collaborations": []}


def save_shared_knowledge(data: dict):
    SHARED_KNOWLEDGE_PATH.parent.mkdir(exist_ok=True)
    with open(SHARED_KNOWLEDGE_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def share_progress(girl_name: str, achievement: str, knowledge: str):
    data = load_shared_knowledge()
    if girl_name not in data["knowledge"]:
        data["knowledge"][girl_name] = []
    
    data["knowledge"][girl_name].append({
        "timestamp": datetime.now().isoformat(),
        "achievement": achievement,
        "knowledge": knowledge
    })
    
    # Ограничиваем историю 50 записями
    if len(data["knowledge"][girl_name]) > 50:
        data["knowledge"][girl_name] = data["knowledge"][girl_name][-50:]
    
    save_shared_knowledge(data)
    logger.info(f"📚 {girl_name} поделилась знаниями: {achievement}")


def get_shared_knowledge_for(girl_name: str, limit: int = 3) -> List[dict]:
    data = load_shared_knowledge()
    relevant = []
    for other_girl, entries in data["knowledge"].items():
        if other_girl != girl_name and entries:
            for entry in entries[-limit:]:
                relevant.append({
                    "from": other_girl,
                    "achievement": entry["achievement"],
                    "knowledge": entry["knowledge"]
                })
    return relevant


def continue_progress() -> dict:
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
    PROGRESS_PATH.parent.mkdir(exist_ok=True)
    with open(PROGRESS_PATH, "w", encoding="utf-8") as f:
        json.dump(progress, f, ensure_ascii=False, indent=2)


def record_milestone(progress: dict, girl_name: str, description: str):
    progress["milestones"].append({
        "timestamp": datetime.now().isoformat(),
        "girl": girl_name,
        "description": description
    })
    if len(progress["milestones"]) > 100:
        progress["milestones"] = progress["milestones"][-100:]
    save_global_progress(progress)
    logger.info(f"🏆 Веха: {girl_name} — {description}")


# === GIT ОПЕРАЦИИ ===

def git_commit_and_push(message: str) -> bool:
    try:
        # Проверяем, что git доступен
        if not subprocess.run(["which", "git"], capture_output=True).returncode == 0:
            logger.warning("⚠️ Git не найден в контейнере — пропускаем коммит")
            return False
            
        logger.info(f"📦 Git commit: {message}")
        subprocess.run(["git", "add", "."], cwd=str(PROJECT_ROOT), check=True, capture_output=True)
        subprocess.run(
            ["git", "commit", "-m", f"[Orchestrator] {message}"],
            cwd=str(PROJECT_ROOT), check=True, capture_output=True
        )
        subprocess.run(["git", "push", "origin", "main"], cwd=str(PROJECT_ROOT), check=True, capture_output=True)
        logger.info(f"✅ Git push успешен: {message}")
        return True
    except subprocess.CalledProcessError as e:
        logger.warning(f"⚠️ Git ошибка (пропуск коммита): {e}")
        return False


# === ЗАПУСК МИССИИ ДЕВОЧКИ ===

def run_girl_mission(girl_name: str, mission: str, cycles: int) -> bool:
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
        env["CURRENT_MISSION"] = mission
        env["MISSION_CYCLES"] = str(cycles)
        env["CURRENT_GIRL"] = girl_name
        
        # Hanako использует --cycles, остальные --max-cycles
        if girl_name == "hanako":
            cmd = [sys.executable, str(run_script), "--cycles", str(cycles)]
        else:
            cmd = [sys.executable, str(run_script), "--max-cycles", str(cycles)]

        result = subprocess.run(
            cmd,
            cwd=str(girl_dir),
            env=env,
            capture_output=False,
            timeout=60 * 60 * 2  # 2 часа
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


# === ОСНОВНОЙ ЦИКЛ ===

def autonomous_loop(cycles_per_mission: int = 100, demo: bool = False):
    logger.info("=" * 80)
    logger.info("🤖 ОРКЕСТРАТОР v3 — МИССИИ + КОЛЛАБОРАЦИЯ")
    logger.info("=" * 80)
    if demo:
        logger.info("   🎬 ДЕМОНСТРАЦИОННЫЙ РЕЖИМ (1 цикл на девочку)")
        cycles_per_mission = 1
    
    logger.info(f"   🔄 Циклов на миссию: {cycles_per_mission}")
    logger.info(f"   🤝 Коллаборация: ВКЛЮЧЕНА")
    logger.info(f"   📚 Обмен знаниями: ВКЛЮЧЁН")
    logger.info("=" * 80)

    progress = continue_progress()
    
    # Показываем загруженный прогресс
    logger.info(f"📊 Глобальный прогресс:")
    logger.info(f"   🔄 Всего циклов: {progress['total_cycles']}")
    logger.info(f"   🤝 Коллабораций: {progress['total_collaborations']}")
    logger.info(f"   🏆 Вех: {len(progress['milestones'])}")

    last_commit_time = time.time()
    mission_counter = 0
    
    # Считаем сколько полных циклов прошли
    total_girls = len(GIRLS_MISSIONS)
    
    while True:
        for girl_name, mission in GIRLS_MISSIONS.items():
            logger.info("-" * 60)
            logger.info(f"🎯 СЛЕДУЮЩАЯ: {girl_name.upper()}")
            logger.info("-" * 60)
            
            # === ФАЗА 1: КОЛЛАБОРАЦИЯ ===
            logger.info(f"🤝 Фаза коллаборации для {girl_name}...")
            shared = get_shared_knowledge_for(girl_name, limit=3)
            if shared:
                for item in shared:
                    logger.info(f"   📖 От {item['from']}: {item['achievement']}")
            else:
                logger.info(f"   ℹ️ Нет полученных знаний (первые запуски)")
            
            progress["total_collaborations"] += 1
            save_global_progress(progress)
            record_milestone(progress, girl_name, f"Коллаборация #{progress['total_collaborations']}")
            
            # Обновляем счётчик циклов
            progress["total_cycles"] += 1
            progress["cycles_per_girl"][girl_name] = progress["cycles_per_girl"].get(girl_name, 0) + 1
            progress["last_girl"] = girl_name
            save_global_progress(progress)

            # === ФАЗА 2: ЗАПУСК МИССИИ ===
            success = run_girl_mission(girl_name, mission, cycles_per_mission)
            mission_counter += 1

            if success:
                share_progress(
                    girl_name,
                    f"Завершила миссию #{mission_counter}",
                    f"Миссия: {mission}. Циклов: {cycles_per_mission}"
                )

            # === ФАЗА 3: КОММИТ ===
            now = time.time()
            if (now - last_commit_time) >= (AUTO_COMMIT_INTERVAL * 60):
                commit_msg = f"Миссия {girl_name} завершена (#{mission_counter}). Миссия: {mission}"
                git_commit_and_push(commit_msg)
                last_commit_time = now

            # Пауза между девочками
            logger.info(f"⏳ Пауза 5 сек перед следующей девочкой...")
            time.sleep(5)
            
            # Демо-режим: после одного полного цикла выходим
            if demo and mission_counter >= total_girls:
                logger.info("🎬 Демо-режим: один цикл завершён, выходим")
                return

        logger.info("🔄 Полный цикл всех девочек завершён. Начинаю новый...")
        time.sleep(5)


# === ЗАПУСК ===

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="ОРКЕСТРАТОР ДЕВОЧЕК v3 — Миссии + Коллаборация")
    parser.add_argument("--demo", action="store_true", help="Демо-режим (1 цикл)")
    parser.add_argument("--cycles", type=int, default=100, help="Циклов на миссию (по умолчанию 100)")
    parser.add_argument("--commit-interval", type=int, default=30, help="Интервал коммитов в минутах")
    args = parser.parse_args()
    
    try:
        autonomous_loop(
            cycles_per_mission=args.cycles,
            demo=args.demo
        )
    except KeyboardInterrupt:
        logger.info("🛑 Оркестратор остановлен пользователем")
    except Exception as e:
        logger.error(f"💥 Критическая ошибка: {e}")
        import traceback
        traceback.print_exc()
