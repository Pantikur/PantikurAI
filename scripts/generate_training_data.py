#!/usr/bin/env python3
# generate_training_data.py — генерация новых обучающих примеров
# Автоматически создаёт диалоги на разные темы, фильтрует дубликаты

import os
import sys
import json
import time
import hashlib
import argparse
from pathlib import Path
from typing import List, Dict, Optional

import requests
import yaml

# Пути
BASE_DIR = Path(__file__).resolve().parent
CONFIG_PATH = BASE_DIR / "configs" / "generation.yaml"
DATA_DIR = BASE_DIR / "data"
CONVERSATIONS_PATH = DATA_DIR / "conversations.json"

# Загрузка .env
env_path = BASE_DIR / ".env"
if env_path.exists():
    from dotenv import load_dotenv
    load_dotenv(env_path)

# Безопасный вывод
def safe_print(msg: str):
    """Заменяет эмодзи на ASCII"""
    emojis = {
        '🧠': '[AI]', '✅': '[OK]', '❌': '[ERR]', '⚠️': '[WARN]',
        '🎉': '[HAPPY]', 'ℹ️': '[INFO]', '💾': '[SAVE]', '📊': '[STATS]'
    }
    for e, t in emojis.items():
        msg = msg.replace(e, t)
    print(msg, flush=True)


def load_config() -> dict:
    """Загружает конфиг генерации"""
    if CONFIG_PATH.exists():
        with open(CONFIG_PATH, "r", encoding="utf-8") as f:
            return yaml.safe_load(f)
    # Дефолтный конфиг
    return {
        "generation": {
            "batch_size": 10,
            "max_dialogs": 500,
            "turns_per_dialog": 4,
            "delay_between_requests": 1.0,
            "scenarios": [
                {"name": "technology", "prompts": ["Объясни концепцию", "Сравни технологии"]},
                {"name": "daily_life", "prompts": ["Опиши ситуацию", "Дай совет"]}
            ]
        }
    }


def load_conversations() -> List[Dict]:
    """Загружает существующие диалоги"""
    if CONVERSATIONS_PATH.exists():
        with open(CONVERSATIONS_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    return []


def save_conversations(dialogs: List[Dict]):
    """Сохраняет диалоги"""
    DATA_DIR.mkdir(exist_ok=True)
    with open(CONVERSATIONS_PATH, "w", encoding="utf-8") as f:
        json.dump(dialogs, f, ensure_ascii=False, indent=2)
    safe_print(f"[SAVE] Сохранено {len(dialogs)} диалогов в {CONVERSATIONS_PATH}")


def get_token() -> Optional[str]:
    """Получает токен GigaChat"""
    return os.getenv("GIGACHAT_TOKEN")


def hash_dialog(dialog: List[Dict]) -> str:
    """Создаёт хеш диалога для проверки дубликатов"""
    text = json.dumps(dialog, ensure_ascii=False)
    return hashlib.md5(text.encode('utf-8')).hexdigest()


def is_duplicate(dialog: List[Dict], existing_dialogs: List[Dict], threshold: float = 0.8) -> bool:
    """Проверяет, есть ли похожий диалог (упрощённая проверка)"""
    new_hash = hash_dialog(dialog)
    for existing in existing_dialogs:
        existing_hash = hash_dialog(existing)
        if new_hash == existing_hash:
            return True
    return False


def call_gigachat(messages: List[Dict], model: str = "GigaChat", temperature: float = 0.8) -> Optional[str]:
    """Вызывает GigaChat API"""
    token = get_token()
    if not token:
        raise ValueError("[ERR] GIGACHAT_TOKEN не найден")
    
    try:
        resp = requests.post(
            "https://gigachat.devices.sberbank.ru/api/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/json"
            },
            json={
                "model": model,
                "messages": messages,
                "temperature": temperature,
                "stream": False
            },
            verify=False,
            timeout=60
        )
        resp.raise_for_status()
        data = resp.json()
        if "choices" in data and data["choices"]:
            return data["choices"][0]["message"]["content"]
        return None
    except Exception as e:
        safe_print(f"[ERR] Ошибка GigaChat: {e}")
        return None


def generate_user_prompt(scenario: dict) -> str:
    """Генерирует запрос пользователя на основе сценария"""
    prompts = scenario.get("prompts", ["Задайте вопрос"])
    base_prompt = prompts[hash(scenario["name"]) % len(prompts)]
    
    # Добавляем случайность
    variations = [
        f"{base_prompt} (развернуто)",
        f"{base_prompt} (кратко)",
        f"Расскажи подробнее о: {base_prompt.lower()}",
        f"Как ты относишься к: {base_prompt.lower()}?"
    ]
    return variations[hash(time.time()) % len(variations)]


def generate_dialog(scenario: dict, turns: int = 4) -> List[Dict]:
    """Генерирует один диалог"""
    dialog = []
    messages = []
    
    # Первый запрос пользователя
    user_prompt = generate_user_prompt(scenario)
    dialog.append({"user": user_prompt})
    messages.append({"role": "user", "content": user_prompt})
    
    safe_print(f"[AI] Генерирую {scenario['name']} диалог ({turns} раундов)...")
    
    for turn in range(turns - 1):
        # Ответ ассистента
        assistant_reply = call_gigachat(messages, temperature=0.7)
        if not assistant_reply:
            safe_print(f"[WARN] Пропускаем раунд {turn + 2}")
            break
        
        dialog.append({"assistant": assistant_reply})
        messages.append({"role": "assistant", "content": assistant_reply})
        
        # Следующий вопрос пользователя
        if turn < turns - 2:
            user_prompt = (
                f"Уточни: {assistant_reply[:50]}... "
                f"Расскажи подробнее об этом."
            )
            dialog.append({"user": user_prompt})
            messages.append({"role": "user", "content": user_prompt})
    
    return dialog


def generate_batch(n: int, scenario: dict, turns: int = 4) -> List[List[Dict]]:
    """Генерирует батч диалогов"""
    dialogs = []
    for i in range(n):
        dialog = generate_dialog(scenario, turns)
        if dialog and len(dialog) >= 2:  # Минимум 2 реплики
            dialogs.append(dialog)
            safe_print(f"[OK] Диалог #{len(dialogs)} от {scenario['name']}")
        time.sleep(1.0)
    return dialogs


def main():
    parser = argparse.ArgumentParser(description="Генерация обучающих данных")
    parser.add_argument(
        "--count", "-c",
        type=int,
        default=10,
        help="Количество диалогов для генерации (по умолчанию: 10)"
    )
    parser.add_argument(
        "--scenario", "-s",
        type=str,
        default=None,
        help="Название сценария (technology, philosophy, daily_life, creative, problem_solving)"
    )
    parser.add_argument(
        "--all",
        action="store_true",
        help="Генерировать из всех сценариев"
    )
    parser.add_argument(
        "--no-dedup",
        action="store_true",
        help="Не проверять дубликаты"
    )
    
    args = parser.parse_args()
    
    # Загрузка конфига
    config = load_config()
    gen_config = config.get("generation", {})
    
    token = get_token()
    if not token:
        safe_print("[ERR] GIGACHAT_TOKEN не найден в .env")
        sys.exit(1)
    
    safe_print(f"[INFO] Запуск генерации: {args.count} диалогов")
    safe_print(f"[INFO] Токен GigaChat: {'*' * 10}...")
    
    # Загрузка существующих диалогов
    existing_dialogs = load_conversations()
    safe_print(f"[INFO] Уже есть {len(existing_dialogs)} диалогов")
    
    max_dialogs = gen_config.get("max_dialogs", 500)
    if len(existing_dialogs) >= max_dialogs:
        safe_print(f"[WARN] Достигнут лимит {max_dialogs} диалогов")
        safe_print("[INFO] Увеличьте max_dialogs в configs/generation.yaml")
        return
    
    # Определение сценариев
    scenarios = gen_config.get("scenarios", [])
    if args.scenario:
        scenarios = [s for s in scenarios if s["name"] == args.scenario]
        if not scenarios:
            safe_print(f"[ERR] Сценарий '{args.scenario}' не найден")
            safe_print(f"[INFO] Доступные: {[s['name'] for s in gen_config['scenarios']]}")
            sys.exit(1)
    
    turns = gen_config.get("turns_per_dialog", 4)
    delay = gen_config.get("delay_between_requests", 1.0)
    
    # Генерация
    new_dialogs = []
    for scenario in scenarios:
        safe_print(f"\n[AI] Сценарий: {scenario['name']} — {scenario.get('description', '')}")
        
        count_per_scenario = args.count // len(scenarios) if len(scenarios) > 1 else args.count
        
        batch = generate_batch(count_per_scenario, scenario, turns)
        new_dialogs.extend(batch)
        
        time.sleep(delay)
    
    # Фильтрация дубликатов
    if not args.no_dedup:
        safe_print(f"\n[STATS] Фильтрация дубликатов...")
        unique_dialogs = []
        for dialog in new_dialogs:
            if not is_duplicate(dialog, existing_dialogs + unique_dialogs):
                unique_dialogs.append(dialog)
            else:
                safe_print(f"[WARN] Пропущен дубликат ({len(unique_dialogs)}/{len(new_dialogs)})")
        new_dialogs = unique_dialogs
    
    # Добавление к существующим
    if new_dialogs:
        all_dialogs = existing_dialogs + new_dialogs
        all_dialogs = all_dialogs[:max_dialogs]  # Обрезаем до лимита
        save_conversations(all_dialogs)
        safe_print(f"\n[OK] Добавлено {len(new_dialogs)} новых диалогов")
        safe_print(f"[OK] Всего: {len(all_dialogs)} диалогов")
    else:
        safe_print("[WARN] Не сгенерировано новых уникальных диалогов")
    
    safe_print("\n[HAPPY] Генерация завершена!")


if __name__ == "__main__":
    main()
