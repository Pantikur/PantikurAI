# test_gigachat_env.py (исправленная версия)
import os
import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
env_path = BASE_DIR / ".env"
print(f"📂 Ищем .env в: {env_path}")

if env_path.exists():
    from dotenv import load_dotenv
    load_dotenv(env_path)
    print("✅ .env загружен!")
else:
    print("❌ .env не найден!")
    sys.exit(1)

token = os.getenv("GIGACHAT_TOKEN")
if not token:
    print("❌ GIGACHAT_TOKEN не найден")
    sys.exit(1)

print(f"🔑 Используем токен: {token[:10]}...")

# === Тест GigaChat с verify=False ===
import requests

url = "https://gigachat.devices.sberbank.ru/api/v1/chat/completions"
headers = {
    "Authorization": f"Bearer {token}",
    "Content-Type": "application/json"
}
payload = {
    "model": "GigaChat-Pro",
    "messages": [{"role": "user", "content": "Привет"}],
    "stream": False,
    "temperature": 0.7
}

resp = None
try:
    resp = requests.post(
        url,
        json=payload,
        headers=headers,
        timeout=45,
        verify=False
    )
    
    # 🔍 Проверка статуса
    if resp.status_code != 200:
        print(f"❌ HTTP {resp.status_code} — ответ от сервера:")
        print(resp.text)
        sys.exit(1)
    
    data = resp.json()
    
    # 🛠️ Обработка ответа
    if "choices" in data and data["choices"]:
        print("✅ Токен валиден! (SSL отключён)")
        content = data["choices"][0]["message"]["content"]
        print("Ответ:", content)
    elif "error" in data:
        print("❌ Ошибка GigaChat API:")
        print("   Тип:", data["error"].get("type"))
        print("   Сообщение:", data["error"].get("message"))
    else:
        print("⚠️ Неожиданный ответ от GigaChat:")
        print(data)
        sys.exit(1)

except requests.exceptions.RequestException as e:
    print("❌ HTTP ошибка:", e)
    if resp is not None:
        print("   Код:", resp.status_code)
        print("   Тело:", resp.text)
except Exception as e:
    print("❌ Непредвиденная ошибка:", e)