# get_gigachat_token.py
import requests
import uuid
import os
import base64
import pathlib

# Загружаем .env вручную
env_path = pathlib.Path(".env")
env_vars = {}
if env_path.exists():
    with open(env_path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                key, value = line.split("=", 1)
                env_vars[key.strip()] = value.strip()

# Пытаемся получить credentials из .env
GIGACHAT_CLIENT_ID = env_vars.get("GIGACHAT_CLIENT_ID", "")
GIGACHAT_CLIENT_SECRET = env_vars.get("GIGACHAT_CLIENT_SECRET", "")

AUTHORIZATION_KEY = ""
if GIGACHAT_CLIENT_ID and GIGACHAT_CLIENT_SECRET:
    AUTHORIZATION_KEY = base64.b64encode(f"{GIGACHAT_CLIENT_ID}:{GIGACHAT_CLIENT_SECRET}".encode()).decode()
    print(f"[OK] Используем credentials из .env")
elif GIGACHAT_CLIENT_ID:
    AUTHORIZATION_KEY = GIGACHAT_CLIENT_ID  # Если уже base64
    print(f"[OK] Используем Authorization Key из .env")
else:
    print("[WARN] GIGACHAT_CLIENT_ID или GIGACHAT_CLIENT_SECRET не найдены в .env")
    print("[INFO] Получите их на https://ai.sber.ru -> API Studio -> Ключи API")
    print("[INFO] Добавьте в .env: GIGACHAT_CLIENT_ID=... и GIGACHAT_CLIENT_SECRET=...")
    exit(1)

url = "https://ngw.devices.sberbank.ru:9443/api/v2/oauth"

payload = {
    'scope': 'GIGACHAT_API_PERS'
}
headers = {
    'Content-Type': 'application/x-www-form-urlencoded',
    'Accept': 'application/json',
    'Authorization': f'Basic {AUTHORIZATION_KEY}',
    'RqUID': str(uuid.uuid4())
}

print("[INFO] Запрашиваю Access token...")
try:
    response = requests.post(url, headers=headers, data=payload, verify=False, timeout=15)
    print(f"[INFO] HTTP {response.status_code}")
    print(response.text)

    if response.status_code == 200:
        token = response.json().get("access_token")
        print("\n[OK] Получен токен:")
        print(token)
        print("[INFO] Сохраняем токен в .env")
        
        # Читаем .env
        env_path = ".env"
        if os.path.exists(env_path):
            with open(env_path, "r", encoding="utf-8") as f:
                lines = [l for l in f if not l.startswith("GIGACHAT_TOKEN=")]
        else:
            lines = []
        
        with open(env_path, "w", encoding="utf-8") as f:
            f.writelines(lines)
            f.write(f"GIGACHAT_TOKEN={token}\n")
        print("[OK] Сохранено в .env!")
    else:
        print("\n[ERR] Ошибка сервера.")
except Exception as e:
    print(f"[ERR] Ошибка: {e}")