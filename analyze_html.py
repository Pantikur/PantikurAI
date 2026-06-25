#!/usr/bin/env python3
# analyze_html.py — Анализ HTML Литнета

import urllib.request
import re

def analyze():
    url = 'https://litnet.com/ru/tag/psihologija-t112'
    
    req = urllib.request.Request(url)
    req.add_header('User-Agent', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36')
    
    with urllib.request.urlopen(req, timeout=15) as response:
        html = response.read().decode('utf-8', errors='ignore')
    
    print("=" * 60)
    print("Анализ структуры HTML Литнета")
    print("=" * 60)
    
    # 1. Ищем все itemprop="name"
    names = re.findall(r'itemprop="name"[^>]*>([^<]+)', html, re.IGNORECASE)
    print(f"\n1. itemprop='name' (заголовки): {len(names)}")
    for i, name in enumerate(names[:5]):
        print(f"   {i+1}. {name.strip()}")
    
    # 2. Ищем все href с /book/
    book_hrefs = re.findall(r'href="([^"]*/book/[^"]*)"', html, re.IGNORECASE)
    print(f"\n2. href с /book/: {len(book_hrefs)}")
    for i, href in enumerate(set(book_hrefs[:5])):
        print(f"   {i+1}. {href}")
    
    # 3. Ищем комбинации: href + itemprop рядом
    print("\n3. Поиск комбинаций href + itemprop:")
    
    # Ищем блоки <a> с itemprop
    a_blocks = re.findall(r'<a[^>]*href="(/ru/book/[^"]+)"[^>]*>(.*?)</a>', html, re.IGNORECASE | re.DOTALL)
    print(f"   Найдено <a> блоков с /book/: {len(a_blocks)}")
    
    for href, content in a_blocks[:3]:
        # Извлекаем itemprop="name" из содержимого
        name_match = re.search(r'itemprop="name"[^>]*>([^<]+)', content, re.IGNORECASE)
        name = name_match.group(1).strip() if name_match else "N/A"
        print(f"   - href: {href}")
        print(f"     name: {name}")
        print()
    
    # 4. Ищем data-book-id или подобные атрибуты
    data_attrs = re.findall(r'data-[\w-]+="\d+"', html[:50000])
    print(f"\n4. data-атрибуты: {len(data_attrs)}")
    for attr in set(data_attrs[:5]):
        print(f"   {attr}")
    
    # 5. Ищем JSON в HTML
    json_scripts = re.findall(r'<script[^>]*type="application/json"[^>]*>([^<]+)', html[:100000])
    print(f"\n5. JSON скрипты: {len(json_scripts)}")
    if json_scripts:
        print(f"   First: {json_scripts[0][:200]}...")

if __name__ == "__main__":
    analyze()
