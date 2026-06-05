# get_gigachat_token.py (исправленная версия)
import requests
import uuid

AUTHORIZATION_KEY = "MDE5ZTk2NzgtZDBlNi03ZTRlLWIyOTktOWU4NGJiMzJkZGMwOmEzNmYwZmNkLWEyODMtNDUxYi1iNmYyLTYwODZmMzJlY2ZhMA=="

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

print("🔐 Запрашиваю Access token...")
try:
    response = requests.post(url, headers=headers, data=payload, verify=False, timeout=15)
    print(f"HTTP {response.status_code}")
    print(response.text)

    if response.status_code == 200:
        token = response.json().get("access_token")
        print("\n✅ SUCCESS! Получен токен:")
        print(token)
        print("🔒 Сохраняем токен как GIGACHAT_TOKEN (даже если не 'giga-...')")
        with open(".env", "r", encoding="utf-8") as f:
            lines = [l for l in f if not l.startswith("GIGACHAT_TOKEN=")]
        with open(".env", "w", encoding="utf-8") as f:
            f.writelines(lines)
            f.write(f"GIGACHAT_TOKEN={token}\n")  # ← сохраняем JWT
        print("✅ Сохранено в .env! Теперь запустите 'python test_gigachat_env.py'")
    else:
        print("\n❌ Ошибка сервера.")
except Exception as e:
    print("❌ Ошибка:", e)