import os
import requests

token = os.getenv("GIGACHAT_TOKEN")
if not token:
    print("❌ GIGACHAT_TOKEN не найден в .env")
    exit()

url = "https://gigachat.devices.sberbank.ru/api/v1/chat/completions"
headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
payload = {
    "model": "GigaChat-Pro",
    "messages": [{"role": "user", "content": "Скажи привет"}],
    "stream": False
}

try:
    resp = requests.post(url, json=payload, headers=headers, timeout=10)
    print("✅ Токен валиден!")
    print("Ответ:", resp.json()["choices"][0]["message"]["content"])
except Exception as e:
    print("❌ Ошибка:", e)