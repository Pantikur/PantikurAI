# test_selenium.py
from web_search import WebSearch

ws = WebSearch()
ws.init_driver()
if ws.driver:
    print("✅ driver запущен")
    ws.driver.get("https://yandex.ru/search/?text=значение слова кот")
    input("Нажмите Enter для закрытия браузера...")
    ws.driver.quit()
else:
    print("❌ driver не запущен")