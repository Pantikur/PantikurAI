#!/usr/bin/env python3
# debug_at_chapter.py — Анализ HTML главы

import urllib.request
import re

url = 'https://author.today/reader/606045/5796091'
req = urllib.request.Request(url)
req.add_header('User-Agent', 'Mozilla/5.0')

print("=" * 60)
print("Анализ главы Author.Today")
print("=" * 60)

with urllib.request.urlopen(req, timeout=15) as response:
    html = response.read().decode('utf-8', errors='ignore')

print(f"\n[HTML] Размер: {len(html)}")

# 1. Ищем текст по разным классам
classes_to_try = [
    'work-text-content',
    'chapter-content', 
    'text-content',
    'reader-text',
    'book-text',
    'content-text',
    'fr-view',  # часто используется
    'paragraph',
]

for cls in classes_to_try:
    matches = re.findall(rf'class="[^"]*{cls}[^"]*"', html, re.IGNORECASE)
    if matches:
        print(f"\n[CLASS] '{cls}': {len(matches)}")

# 2. Ищем все div с class
div_classes = re.findall(r'<div[^>]*class="([^"]*)"', html, re.IGNORECASE)
print(f"\n[DIC] Уникальных class: {len(set(div_classes))}")
print("Примеры:")
for cls in list(set(div_classes))[:20]:
    print(f"   - {cls}")

# 3. Ищем параграфы <p>
paragraphs = re.findall(r'<p[^>]*>(.*?)</p>', html, re.IGNORECASE | re.DOTALL)
print(f"\n[PARAGRAPH] Найдено: {len(paragraphs)}")
total_chars = sum(len(re.sub(r'<[^>]+>', '', p)) for p in paragraphs)
print(f"[PARAGRAPH] Всего символов: {total_chars}")
for i, p in enumerate(paragraphs[:3]):
    clean = re.sub(r'<[^>]+>', '', p).strip()
    print(f"   {i+1}. {len(clean)}: {clean[:80]}...")

# 4. Выводим фрагмент середины HTML (где обычно текст)
mid = len(html) // 2
fragment_start = max(0, mid - 500)
fragment = html[fragment_start:fragment_start+1000]

print("\n" + "=" * 60)
print("Фрагмент HTML (середина):")
print("=" * 60)
safe = fragment.replace('<', '[').replace('>', ']')
try:
    print(safe.encode('utf-8').decode('cp1251', errors='replace')[:800])
except:
    print(safe[:600])
