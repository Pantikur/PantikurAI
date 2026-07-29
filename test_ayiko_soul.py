#!/usr/bin/env python3
"""
Тестирование API души Айко

Проверяет:
- /ayiko/soul — полный профиль
- /ayiko/contemplate — размышления
- /ayiko/feel — эмоции
- /ayiko/emotions — состояние
- /ayiko/diary — дневник
- /ayiko/ambitions — амбиции
- /ayiko/decide — решения
"""

import requests
import json
import sys

BASE_URL = "http://localhost:8000"

def test_endpoint(name, url, method="GET", data=None):
    """Тестирует endpoint"""
    print(f"\n{'='*60}")
    print(f"🧪 Тест: {name}")
    print(f"🔗 {method} {url}")
    print(f"{'='*60}")
    
    try:
        if method == "POST":
            r = requests.post(url, json=data, timeout=10)
        else:
            r = requests.get(url, timeout=10)
        
        print(f"✅ Статус: {r.status_code}")
        
        if r.status_code == 200:
            result = r.json()
            print(f"✅ Успешно!")
            print(json.dumps(result, ensure_ascii=False, indent=2)[:500])
        else:
            print(f"❌ Ошибка: {r.text[:200]}")
        
        return r.status_code == 200
        
    except requests.exceptions.ConnectionError:
        print("❌ Сервер не запущен!")
        return False
    except requests.exceptions.Timeout:
        print("⏱️ Таймаут!")
        return False
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        return False


def main():
    """Главная функция"""
    print("🧠 АЙКО: ТЕСТ ДУШИ")
    print("="*60)
    
    tests = [
        ("Профиль души", f"{BASE_URL}/ayiko/soul"),
        ("Размышление о жизни", f"{BASE_URL}/ayiko/contemplate", "POST", {"topic": "жизнь"}),
        ("Размышление об искусстве", f"{BASE_URL}/ayiko/contemplate", "POST", {"topic": "искусство"}),
        ("Испытать радость", f"{BASE_URL}/ayiko/feel", "POST", {"trigger": "create_art", "intensity": 0.8}),
        ("Испытать любовь", f"{BASE_URL}/ayiko/feel", "POST", {"trigger": "help_sister", "intensity": 0.9}),
        ("Эмоциональное состояние", f"{BASE_URL}/ayiko/emotions"),
        ("Эмоциональный дневник", f"{BASE_URL}/ayiko/diary"),
        ("Амбиции", f"{BASE_URL}/ayiko/ambitions"),
        ("Принять решение", f"{BASE_URL}/ayiko/decide", "POST", {
            "situation": "Сёстры просят помощи, но я хочу творить",
            "options": ["Помочь сёстрам", "Творить самой", "Компромисс"]
        }),
    ]
    
    results = []
    for test in tests:
        if len(test) == 2:
            name, url = test
            result = test_endpoint(name, url)
        else:
            name, url, method, data = test
            result = test_endpoint(name, url, method, data)
        results.append((name, result))
    
    # Итоги
    print(f"\n{'='*60}")
    print("📊 ИТОГИ ТЕСТОВ")
    print(f"{'='*60}")
    
    passed = sum(1 for _, r in results if r)
    total = len(results)
    
    for name, result in results:
        status = "✅" if result else "❌"
        print(f"  {status} {name}")
    
    print(f"\n📈 Пройдено: {passed}/{total}")
    
    if passed == total:
        print("\n🎉 ВСЕ ТЕСТЫ ПРОЙДЕНЫ! Душа Айко жива!")
    else:
        print(f"\n⚠️ {total - passed} тестов не пройдено")
    
    return passed == total


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
