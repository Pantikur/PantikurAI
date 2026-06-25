#!/usr/bin/env python3
# debug_litnet.py — Отладка поиска на Литнете

import urllib.request
import re

def safe_print(msg):
    """Безопасный print для Windows."""
    emojis = {
        '✅': '[OK]', '❌': '[ERR]', '📄': '[HTML]', '📚': '[BOOK]',
        '📖': '[READ]', '👤': '[USER]', '🔗': '[LINK]', '⚠️': '[WARN]'
    }
    for e, t in emojis.items():
        msg = msg.replace(e, t)
    try:
        print(msg.encode('utf-8').decode('cp1251', errors='replace'))
    except:
        print(msg)


def test_litnet_connection():
    """Тестирует подключение к Литнету."""
    url = 'https://litnet.com/ru/tag/psihologija-t112'
    
    print("=" * 60)
    safe_print("Тест подключения к Литнету")
    print("=" * 60)
    
    req = urllib.request.Request(url)
    req.add_header('User-Agent', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')
    req.add_header('Accept', 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8')
    req.add_header('Accept-Language', 'ru-RU,ru;q=0.9,en;q=0.8')
    req.add_header('Referer', 'https://litnet.com/')
    req.add_header('Connection', 'keep-alive')
    
    try:
        with urllib.request.urlopen(req, timeout=15) as response:
            html = response.read().decode('utf-8', errors='ignore')
            
            print(f"\n[OK] Status: {response.status}")
            print(f"[HTML] HTML length: {len(html)} символов")
            
            # Проверяем редирект
            print(f"[LINK] Final URL: {response.url}")
            
            # Ищем любые ссылки на книги
            book_links = re.findall(r'/ru/book/([\w-]+-b\d+)', html)
            print(f"\n[BOOK] Book links found: {len(book_links)}")
            if book_links:
                print(f"   First 5: {book_links[:5]}")
            
            # Ищем class="book-title"
            book_titles = re.findall(r'class="book-title"', html, re.IGNORECASE)
            print(f"[READ] 'book-title' class: {len(book_titles)}")
            
            # Ищем itemprop="name"
            itemprop_names = re.findall(r'itemprop="name"', html, re.IGNORECASE)
            print(f"[READ] 'itemprop=name' found: {len(itemprop_names)}")
            
            # Ищем author-wr
            author_wr = re.findall(r'class="author-wr"', html, re.IGNORECASE)
            print(f"[USER] 'author-wr' class: {len(author_wr)}")
            
            # Проверяем структуру HTML
            if 'book-title' in html.lower():
                print("\n[OK] HTML содержит 'book-title'")
            else:
                print("\n[ERR] HTML НЕ содержит 'book-title'")
                
            # Проверяем на блокировку
            if 'access denied' in html.lower() or 'blocked' in html.lower() or 'капча' in html.lower():
                print("\n[WARN] Возможна блокировка (капча/доступ запрещён)")
            
            # Выводим фрагмент HTML для анализа
            print("\n" + "=" * 60)
            print("Фрагмент HTML (первые 2000 символов):")
            print("=" * 60)
            print(html[:2000])
            
            return html
            
    except urllib.error.HTTPError as e:
        print(f"\n[ERR] HTTP Error: {e.code} - {e.reason}")
        return None
    except urllib.error.URLError as e:
        print(f"\n[ERR] URL Error: {e.reason}")
        return None
    except Exception as e:
        print(f"\n[ERR] Error: {type(e).__name__}: {e}")
        return None


def test_alternative_patterns(html):
    """Тестирует альтернативные паттерны парсинга."""
    if not html:
        return
    
    print("\n" + "=" * 60)
    print("Тест альтернативных паттернов")
    print("=" * 60)
    
    # Паттерн 1: data-widget
    pattern1 = re.findall(r'data-widget="book-card"', html, re.IGNORECASE)
    print(f"1. data-widget='book-card': {len(pattern1)}")
    
    # Паттерн 2: book-row
    pattern2 = re.findall(r'class="[^"]*book[^"]*row"', html, re.IGNORECASE)
    print(f"2. book-row class: {len(pattern2)}")
    
    # Паттерн 3: product-title
    pattern3 = re.findall(r'class="[^"]*title[^"]*"', html, re.IGNORECASE)
    print(f"3. title class: {len(pattern3)}")
    
    # Паттерн 4: Все ссылки с /book/
    pattern4 = re.findall(r'href="([^"]*/ru/book/[^"]+)"', html)
    print(f"4. Links with /book/: {len(pattern4)}")
    if pattern4:
        print(f"   Examples: {pattern4[:3]}")
    
    # Паттерн 5: JSON-LD
    jsonld = re.findall(r'type="application/ld\+json"[^>]*>([^<]+)', html, re.IGNORECASE)
    print(f"5. JSON-LD blocks: {len(jsonld)}")
    if jsonld:
        print(f"   First: {jsonld[0][:200]}...")


if __name__ == "__main__":
    html = test_litnet_connection()
    test_alternative_patterns(html)
