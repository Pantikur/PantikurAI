#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Тест Латислейн v2.0"""
import sys
import io

# Принудительная установка UTF-8 кодировки
if sys.stdout.encoding != 'utf-8':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
if sys.stderr.encoding != 'utf-8':
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

from latislane import LatislaneCore

def main():
    print("=" * 60)
    print("ТЕСТ ЛАТИСЛЕЙН v2.0")
    print("=" * 60)
    
    # Инициализация
    c = LatislaneCore(".", demo_mode=True)
    
    # Тест 1: Статус
    print("\n=== 1. СТАТУС СИСТЕМЫ ===")
    print(c.chat_response("статус"))
    
    # Тест 2: Характер
    print("\n=== 2. ХАРАКТЕР ===")
    print(c.chat_response("характер"))
    
    # Тест 3: Сёстры
    print("\n=== 3. СОЦИАЛЬНЫЕ ВЗАИМОДЕЙСТВИЯ ===")
    print(c.chat_response("сёстры"))
    
    # Тест 4: Уровни
    print("\n=== 4. УРОВНИ ЗНАНИЙ ===")
    print(c.chat_response("уровень"))
    
    # Тест 5: Отчёты
    print("\n=== 5. ОТЧЁТЫ ===")
    print(c.chat_response("отчёт"))
    
    # Тест 6: Эволюция
    print("\n=== 6. ЭВОЛЮЦИЯ ===")
    print(c.chat_response("эволюция"))
    
    print("\n✅ ТЕСТ ЗАВЕРШЁН")

if __name__ == "__main__":
    main()
