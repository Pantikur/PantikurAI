# bot_learns_from_gigachat.py
import os
import json
from pathlib import Path
import requests
import time
import sys

DATA_DIR = Path(__file__).resolve().parent / "data"
CONVERSATIONS_PATH = DATA_DIR / "conversations.json"

BASE_DIR = Path(__file__).resolve().parent
env_path = BASE_DIR / ".env"
if env_path.exists():
    from dotenv import load_dotenv
    load_dotenv(env_path)
else:
    print(f"❌ .env не найден в {env_path}")
    sys.exit(1)

# === ОСНОВНОЙ КОД ===
DATA_DIR = Path(__file__).resolve().parent / "data"
CONVERSATIONS_PATH = DATA_DIR / "conversations.json"

def load_conversations():
    if CONVERSATIONS_PATH.exists():
        with open(CONVERSATIONS_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    return []

def save_conversations(dialogs):
    with open(CONVERSATIONS_PATH, "w", encoding="utf-8") as f:
        json.dump(dialogs, f, ensure_ascii=False, indent=2)

def generate_self_teaching_dialogs(n: int = 5):
    """
    Генерирует n саморазвивающихся диалогов с GigaChat.
    Каждый диалог сохраняется как список {"user": "...", "assistant": "..."}
    """
    token = os.getenv("GIGACHAT_TOKEN")
    if not token:
        raise ValueError("❌ GIGACHAT_TOKEN не найден в .env")

    dialogs = load_conversations()

    for i in range(n):
        print(f"🧠 Генерирую диалог #{i+1}/{n}...")
        messages = []
        dialog = []

        for turn in range(4):  # 4-х輪对话 (4round)
            # 1. Генерируем пользовательский запрос
            user_prompt = (
                "Сгенерируй короткий, но содержательный вопрос по теме "
                "технологий, культуры или науки — длина 5-15 слов."
            )
            if turn > 0:
                user_prompt = (
                    f"На основе предыдущего ответа («{messages[-1]['content']}»), "
                    "сформулируй уточняющий или развёрнутый вопрос."
                )

            # Отправляем GigaChat
            try:
                resp = requests.post(
                    "https://gigachat.devices.sberbank.ru/api/v1/chat/completions",
                    headers={
                        "Authorization": f"Bearer {token}",
                        "Content-Type": "application/json"
                    },
                    json={
                        "model": "GigaChat-Pro",
                        "messages": [{"role": "user", "content": user_prompt}],
                        "temperature": 0.9,
                        "stream": False
                    },
                    verify=False,
                    timeout=45
                )
                resp.raise_for_status()
                data = resp.json()
                if "choices" in data and data["choices"]:
                    user_message = data["choices"][0]["message"]["content"]
                    messages.append({"role": "user", "content": user_message})
                    dialog.append({"user": user_message})
                else:
                    print("⚠️ GigaChat не вернул ответ (пропускаем)")
                    break
            except Exception as e:
                print(f"❌ Ошибка при генерации запроса: {e}")
                break

            # 2. Генерируем ответ ассистента
            try:
                resp = requests.post(
                    "https://gigachat.devices.sberbank.ru/api/v1/chat/completions",
                    headers={
                        "Authorization": f"Bearer {token}",
                        "Content-Type": "application/json"
                    },
                    json={
                        "model": "GigaChat-Pro",
                        "messages": [
                            {"role": "user", "content": user_message}
                        ],
                        "temperature": 0.7,
                        "stream": False
                    },
                    verify=False,
                    timeout=15
                )
                resp.raise_for_status()
                data = resp.json()
                if "choices" in data and data["choices"]:
                    assistant_message = data["choices"][0]["message"]["content"]
                    messages.append({"role": "assistant", "content": assistant_message})
                    dialog.append({"assistant": assistant_message})
                else:
                    print("⚠️ GigaChat не вернул ответ (пропускаем)")
                    break
            except Exception as e:
                print(f"❌ Ошибка при генерации ответа: {e}")
                break

        if dialog:
            dialogs.append(dialog)
            print(f"✅ Диалог #{i+1} сохранён")
        time.sleep(0.5)  # Чтобы не спамить API

    save_conversations(dialogs)
    print(f"✅ Всего сохранено {len(dialogs)} диалогов")