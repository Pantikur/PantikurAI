#!/usr/bin/env python3
# check_split.py — Проверяем split

import urllib.request

url = 'https://litnet.com/ru/tag/psihologija-t112'
req = urllib.request.Request(url)
req.add_header('User-Agent', 'Mozilla/5.0')

with urllib.request.urlopen(req, timeout=15) as response:
    html = response.read().decode('utf-8', errors='ignore')

print("Подсчёт вхождений:")
print(f"  'row book-item': {html.count('row book-item')}")
s1 = 'class="row book-item"'
print(f"  '{s1}': {html.count(s1)}")
s2 = 'class="row book-item'
print(f"  '{s2}': {html.count(s2)}")
print(f"  'book-item': {html.count('book-item')}")

# Пробуем split
parts = html.split('class="row book-item"')
print(f"\nSplit по 'class=...': {len(parts)} частей")

parts2 = html.split('row book-item')
print(f"Split по 'row book-item': {len(parts2)} частей")

# Выводим первый блок
if len(parts2) > 1:
    print("\nПервый блок (первые 500 символов):")
    block = parts2[1][:500]
    print(block[:300])
