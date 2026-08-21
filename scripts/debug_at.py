#!/usr/bin/env python3
# debug_at.py — Отладка Author.Today

import urllib.request
import re

url = 'https://author.today/work/genre/fantasy'
req = urllib.request.Request(url)
req.add_header('User-Agent', 'Mozilla/5.0')

with urllib.request.urlopen(req, timeout=15) as response:
    html = response.read().decode('utf-8', errors='ignore')

print("=" * 60)
print("Отладка Author.Today")
print("=" * 60)

# 1. Считаем работы
work_matches = re.findall(r'href="(/work/(\d+))"', html)
print(f"\n1. Работы: {len(work_matches)}")
if work_matches:
    print(f"   Примеры: {work_matches[:5]}")

# 2. Ищем первую работу и контекст
if work_matches:
    first_url, first_id = work_matches[0]
    pos = html.find(f'href="{first_url}"')
    
    print(f"\n2. Первая работа: {first_url} (позиция {pos})")
    
    # Выводим 800 символов вокруг
    start = max(0, pos - 200)
    end = min(len(html), pos + 800)
    fragment = html[start:end]
    
    print("\nКонтекст:")
    print("-" * 60)
    # Заменяем < > для вывода
    safe = fragment.replace('<', '[').replace('>', ']')
    try:
        print(safe.encode('utf-8').decode('cp1251', errors='replace'))
    except:
        print(safe[:400])
    print("-" * 60)
    
    # 3. Ищем h3 рядом
    snippet = html[pos:pos+500]
    h3_matches = re.findall(r'<h3[^>]*>([^<]+)</h3>', snippet)
    print(f"\n3. H3 рядом: {len(h3_matches)}")
    for h in h3_matches:
        print(f"   - {h.strip()[:50]}")
    
    # 4. Ищем title в любом месте
    title_matches = re.findall(r'title="([^"]+)"', snippet)
    print(f"\n4. title атрибуты: {len(title_matches)}")
    for t in title_matches[:3]:
        print(f"   - {t[:50]}")
