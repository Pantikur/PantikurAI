#!/usr/bin/env python3
# analyze_at.py — Анализ HTML Author.Today

import urllib.request
import re

url = 'https://author.today/'
req = urllib.request.Request(url)
req.add_header('User-Agent', 'Mozilla/5.0')

with urllib.request.urlopen(req, timeout=15) as response:
    html = response.read().decode('utf-8', errors='ignore')

print("=" * 60)
print("Анализ Author.Today HTML")
print("=" * 60)

# 1. Считаем работы
work_links = re.findall(r'href="(/work/\d+)"', html)
print(f"\n1. Работы (/work/N): {len(work_links)}")
if work_links:
    print(f"   Примеры: {work_links[:5]}")

# 2. Ищем карточки книг
card_divs = re.findall(r'class="[^"]*card[^"]*"', html, re.IGNORECASE)
print(f"\n2. 'card' class: {len(card_divs)}")

# 3. Ищем work-item
work_items = re.findall(r'class="[^"]*work[^"]*item[^"]*"', html, re.IGNORECASE)
print(f"\n3. 'work*item' class: {len(work_items)}")

# 4. Находим первую работу и выводим контекст
first_work = re.search(r'href="(/work/\d+)"', html)
if first_work:
    work_id = first_work.group(1)
    pos = html.find(work_id)
    start = max(0, pos - 300)
    end = min(len(html), pos + 500)
    
    print(f"\n4. Первая работа: {work_id} (позиция {pos})")
    print("\nКонтекст (800 символов):")
    print("-" * 60)
    fragment = html[start:end]
    # Заменяем для безопасного вывода
    safe_fragment = fragment.replace('<', '[').replace('>', ']')
    try:
        print(safe_fragment.encode('utf-8').decode('cp1251', errors='replace'))
    except:
        print(safe_fragment[:400])
    print("-" * 60)

# 5. Ищем заголовки
titles = re.findall(r'<h3[^>]*>[^<]+</h3>', html)
print(f"\n5. Заголовки h3: {len(titles)}")
for t in titles[:3]:
    clean = re.sub(r'<[^>]+>', '', t)
    print(f"   - {clean.strip()[:60]}")

# 6. Ищем авторов
authors = re.findall(r'class="[^"]*author[^"]*"[^>]*>([^<]+)', html, re.IGNORECASE)
print(f"\n6. Авторы: {len(authors)}")
for a in authors[:3]:
    print(f"   - {a.strip()[:40]}")
