#!/usr/bin/env python3
# debug_at_book.py — Анализ страницы книги

import urllib.request
import re

url = 'https://author.today/work/606045'  # Мастер Трав IX
req = urllib.request.Request(url)
req.add_header('User-Agent', 'Mozilla/5.0')

print("=" * 60)
print("Анализ страницы книги")
print("=" * 60)

with urllib.request.urlopen(req, timeout=15) as response:
    html = response.read().decode('utf-8', errors='ignore')

print(f"\n[HTML] Размер: {len(html)}")

# 1. Ищем текст
text_divs = re.findall(r'class="[^"]*text[^"]*"', html, re.IGNORECASE)
print(f"\n1. 'text' class: {len(text_divs)}")

# 2. Ищем content
content_divs = re.findall(r'class="[^"]*content[^"]*"', html, re.IGNORECASE)
print(f"\n2. 'content' class: {len(content_divs)}")

# 3. Ищем chapter / глава
chapter_divs = re.findall(r'class="[^"]*chapter[^"]*"', html, re.IGNORECASE)
print(f"\n3. 'chapter' class: {len(chapter_divs)}")

# 4. Ищем параграфы
paragraphs = re.findall(r'<p[^>]*>(.*?)</p>', html, re.IGNORECASE | re.DOTALL)
print(f"\n4. Параграфы <p>: {len(paragraphs)}")
for i, p in enumerate(paragraphs[:3]):
    clean = re.sub(r'<[^>]+>', '', p).strip()
    print(f"   {i+1}. {clean[:80]}...")

# 5. Ищем конкретные классы
for class_name in ['work-text', 'book-text', 'reader-text', 'chapter-content', 'text-content']:
    matches = re.findall(rf'class="[^"]*{class_name}[^"]*"', html, re.IGNORECASE)
    if matches:
        print(f"\n5. '{class_name}': {len(matches)}")

# 6. Ищем JSON-LD с текстом
print("\n6. Поиск JSON-LD...")
json_ld = re.search(r'<script type="application/ld\+json"[^>]*>(.*?)</script>', html, re.DOTALL)
if json_ld:
    json_text = json_ld.group(1)
    print(f"[JSON] Размер: {len(json_text)}")
    # Ищем description
    desc_match = re.search(r'"description":\s*"([^"]+)"', json_text)
    if desc_match:
        desc = desc_match.group(1)
        # Очищаем от экранирования
        desc = desc.replace('\\n', '\n').replace('\\"', '"')
        print(f"[DESC] {desc[:200]}...")

# 7. Ищем весь текст в data-attributes
print("\n7. Поиск в data-attributes...")
data_attrs = re.findall(r'data-([^=]+)="([^"]{50,})"', html)
for attr, val in data_attrs[:3]:
    print(f"   data-{attr}: {val[:100]}...")

# 8. Ищем список глав разными способами
print("\n8. Поиск глав...")

# Способ 1: href="/reader/{work_id}/{chapter_id}"
chapters1 = re.findall(r'href="(/reader/\d+/\d+)"', html)
print(f"[METHOD 1] Найдено глав: {len(chapters1)}")
for ch in chapters1[:5]:
    print(f"   - {ch}")

# Способ 2: ищем "Читать" кнопки
read_links = re.findall(r'href="(/reader/\d+)"', html, re.IGNORECASE)
print(f"\n[METHOD 2] Read links: {len(read_links)}")

# 9. Скачиваем первую главу
if chapters1:
    first_chapter = chapters1[0]
    chapter_url = f"https://author.today{first_chapter}"
    print(f"\n9. Скачивание первой главы: {chapter_url}")
    
    req_ch = urllib.request.Request(chapter_url)
    req_ch.add_header('User-Agent', 'Mozilla/5.0')
    
    try:
        with urllib.request.urlopen(req_ch, timeout=15) as resp:
            chapter_html = resp.read().decode('utf-8', errors='ignore')
        
        print(f"[OK] Размер главы: {len(chapter_html)}")
        
        # Ищем текст главы - Author.Today хранит в <div class="work-text-content">
        # или в <div class="chapter-content">
        text_divs = re.findall(r'<div[^>]*class="[^"]*(?:work-text|chapter-content|text-content)[^"]*"[^>]*>(.*?)</div>', chapter_html, re.IGNORECASE | re.DOTALL)
        print(f"[TEXT] Блоков текста: {len(text_divs)}")
        
        all_text = []
        for block in text_divs:
            clean = re.sub(r'<[^>]+>', '', block)
            clean = re.sub(r'\s+', ' ', clean).strip()
            if len(clean) > 50:
                all_text.append(clean)
        
        full_text = '\n'.join(all_text)
        print(f"[TEXT] Всего символов: {len(full_text)}")
        if full_text:
            print(f"[TEXT] Начало: {full_text[:300]}...")
            
    except Exception as e:
        print(f"[ERR] {type(e).__name__}: {e}")
