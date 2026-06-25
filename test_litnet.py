#!/usr/bin/env python3
# test_litnet.py — Анализ Litnet

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
import time

print("=" * 70)
print("Analiz Litnet")
print("=" * 70)

options = Options()
options.add_argument('--headless=new')
options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64)')

print("\n[START] Zapusk WebDriver...")
driver = webdriver.Chrome(options=options)

try:
    url = "https://litnet.com/book/fentezi/"
    print(f"[URL] {url}")
    
    driver.get(url)
    time.sleep(5)
    
    print(f"\n[TITLE] {driver.title}")
    
    # Ищем ВСЕ ссылки
    all_links = driver.find_elements(By.TAG_NAME, 'a')
    print(f"\n[STATS] Vsego ssylok: {len(all_links)}")
    
    # Ищем книги по разным селекторам
    selectors = [
        'a.book-title',
        'a.title',
        '.book-row a',
        '[class*="book"] a',
        'a[href*="/book/"]',
    ]
    
    for selector in selectors:
        try:
            elems = driver.find_elements(By.CSS_SELECTOR, selector)
            if elems:
                print(f"\n[OK] Selecktor '{selector}': naideno {len(elems)}")
                for elem in elems[:3]:
                    href = elem.get_attribute('href')
                    text = elem.text.strip()
                    if text and len(text) > 3:
                        print(f"  - {text[:50]}")
        except Exception as e:
            print(f"[ERR] Selecktor '{selector}': {e}")
    
    # Sohranjaem HTML
    html = driver.page_source
    print(f"\n[SIZE] HTML: {len(html)} simvolov")
    
    with open('data/cache/litnet_test.html', 'w', encoding='utf-8') as f:
        f.write(html)
    print(f"[OK] HTML sohranon")
    
finally:
    driver.quit()
    print("\n[STOP] WebDriver zakryt")
