#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
update_gigachat_token.py — Обновляет GIGACHAT_TOKEN в .env

Использует GIGACHAT_CLIENT_ID и GIGACHAT_CREDENTIALS для получения нового токена.

Запуск:
  python update_gigachat_token.py
  
Или вручную через API:
  1. Получить токен: POST https://gigachat.devices.sberbank.ru/api/v1/oauth
     Headers: Authorization: Basic <CLIENT_ID_BASE64>, Scope: GIGACHAT_API_PERS
     Body: {"scope": "GIGACHAT_API_PERS"}
  2. Заменить значение GIGACHAT_TOKEN в .env
"""

import os
import sys
import requests
from pathlib import Path

# Пути
BASE_DIR = Path(__file__).resolve().parent
ENV_PATH = BASE_DIR / ".env"


def read_env(path: Path) -> dict:
    """Читает .env файл и возвращает словарь."""
    env = {}
    if not path.exists():
        return env
    
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                key, _, value = line.partition("=")
                env[key.strip()] = value.strip()
    
    return env


def write_env(path: Path, env: dict):
    """Записывает словарь в .env файл."""
    with open(path, "w", encoding="utf-8") as f:
        for key, value in env.items():
            f.write(f"{key}={value}\n")
    print(f"[SAVE] {path} обновлён ({len(env)} переменных)")


def get_new_token(client_id_base64: str) -> str:
    """Получает новый токен GigaChat."""
    print("[INFO] Запрос нового токена через GigaChat API...")
    
    try:
        resp = requests.post(
            "https://gigachat.devices.sberbank.ru/api/v1/oauth",
            headers={
                "Authorization": "Basic " + client_id_base64,
                "Content-Type": "application/json",
                "RqUID": os.urandom(16).hex(),
            },
            json={"scope": "GIGACHAT_API_PERS"},
            verify=False,
            timeout=15
        )
        
        if resp.status_code == 200:
            data = resp.json()
            token = data.get("accessToken", "")
            if token:
                print(f"[OK] Токен получен (длина={len(token)})")
                return token
            else:
                print(f"[ERR] Ответ без accessToken: {data}")
                return ""
        else:
            print(f"[ERR] HTTP {resp.status_code}: {resp.text[:200]}")
            return ""
    
    except Exception as e:
        print(f"[ERR] Ошибка запроса: {e}")
        return ""


def main():
    print("=" * 60)
    print("[INFO] ОБНОВЛЕНИЕ GIGACHAT TOKEN")
    print("=" * 60)
    
    # Читаем текущий .env
    env = read_env(ENV_PATH)
    
    # Проверяем наличие CLIENT_ID
    client_id = env.get("GIGACHAT_CLIENT_ID", "")
    if not client_id:
        print("[ERR] GIGACHAT_CLIENT_ID не найден в .env")
        print("[INFO] Добавьте его в .env в формате:")
        print("  GIGACHAT_CLIENT_ID=MDE5ZTk2Nzgt...==")
        return
    
    # Получаем новый токен
    new_token = get_new_token(client_id)
    
    if not new_token:
        print("[ERR] Не удалось получить новый токен")
        return
    
    # Обновляем .env
    env["GIGACHAT_TOKEN"] = new_token
    write_env(ENV_PATH)
    
    print("\n[OK] Токен обновлён! Теперь можно запустить:")
    print("  python learn_knowledge_from_web.py")


if __name__ == "__main__":
    main()
