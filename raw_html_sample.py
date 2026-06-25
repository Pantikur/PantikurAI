#!/usr/bin/env python3
# raw_html_sample.py — Получаем образец HTML

import urllib.request
import re

url = 'https://litnet.com/ru/tag/psihologija-t112'
req = urllib.request.Request(url)
req.add_header('User-Agent', 'Mozilla/5.0')

with urllib.request.urlopen(req, timeout=15) as response:
    html = response.read().decode('utf-8', errors='ignore')

# Считаем book-item
book_items = html.count('class="row book-item"')
print(f"book-item блоков: {book_items}")

# Ищем первое вхождение с data-bookItemId
match = re.search(r'data-bookItemId="(\d+)"', html)
if match:
    book_id = match.group(1)
    print(f"Первый data-bookItemId: {book_id}")
    
    # Находим позицию
    pos = html.find(f'data-bookItemId="{book_id}"')
    
    # Выводим 500 символов до и 1500 после
    start = max(0, pos - 200)
    end = min(len(html), pos + 1500)
    
    fragment = html[start:end]
    
    print("\n" + "=" * 60)
    print("HTML фрагмент:")
    print("=" * 60)
    # Заменяем < > для безопасного вывода
    safe_fragment = fragment.replace('<', '[').replace('>', ']')
    try:
        print(safe_fragment.encode('utf-8').decode('cp1251', errors='replace'))
    except:
        print(safe_fragment[:800])
    print("=" * 60)
