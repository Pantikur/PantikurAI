#!/usr/bin/env python3
"""
Тестирование API генерации персонажей через Ayiko
"""

import requests
import json
import sys

sys.stdout.reconfigure(encoding='utf-8')

def test_ayiko_api():
    """Тестируем endpoint /ayiko/generate"""
    
    url = "http://localhost:8000/ayiko/generate"
    
    # Описание Тальсы
    payload = {
        "type": "character",
        "character": {
            "name": "Talsa_Gnorrism",
            "age": 17,
            "body_type": "athletic",
            "skin_color": [195, 155, 115],
            "hair_color": [55, 35, 25],
            "hair_style": "bun",
            "eye_color": [45, 28, 18],
            "clothing": [
                {
                    "type": "shirt",
                    "color": [155, 145, 135],
                    "sleeves": "short"
                },
                {
                    "type": "skirt",
                    "color": [115, 105, 95],
                    "length": 100
                },
                {
                    "type": "apron",
                    "color": [125, 110, 90]
                },
                {
                    "type": "boots",
                    "color": [55, 40, 25]
                }
            ],
            "accessories": [
                {
                    "type": "scar",
                    "color": [175, 135, 105]
                },
                {
                    "type": "belt",
                    "color": [75, 55, 35]
                }
            ],
            "background": "academy"
        },
        "size": [512, 512],
        "style": "realistic"
    }
    
    print("📤 Отправка запроса на /ayiko/generate...")
    print("=" * 60)
    
    try:
        response = requests.post(url, json=payload, timeout=60)
        
        print(f"📊 Status: {response.status_code}")
        print(f"📝 Response: {response.text}")
        
        if response.status_code == 200:
            data = response.json()
            print("=" * 60)
            print("✅ Успех!")
            print(f"📁 Filename: {data.get('filename')}")
            print(f"👤 Character: {data.get('character')}")
            print(f"📐 Size: {data.get('size')}")
            print(f"🎨 Style: {data.get('style')}")
        else:
            print("❌ Ошибка!")
            
    except requests.exceptions.ConnectionError:
        print("❌ Сервер не запущен! Запустите: python main.py")
    except Exception as e:
        print(f"❌ Ошибка: {e}")

if __name__ == "__main__":
    test_ayiko_api()
