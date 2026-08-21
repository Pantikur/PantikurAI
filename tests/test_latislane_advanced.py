#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Продвинутый тест Латислейн v2.0"""
import sys
import io
import asyncio

if sys.stdout.encoding != 'utf-8':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
if sys.stderr.encoding != 'utf-8':
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

from latislane import LatislaneCore

async def main():
    print("=" * 60)
    print("ПРОДВИНУТЫЙ ТЕСТ ЛАТИСЛЕЙН v2.0")
    print("=" * 60)
    
    # Инициализация
    print("\n[1/6] Инициализация...")
    c = LatislaneCore(".", demo_mode=True)
    print("    ✅ Латислейн готова")
    
    # Тест 2: Обучение
    print("\n[2/6] Запуск обучения...")
    await c.run_study_cycle(batch_size=3)
    print("    ✅ Обучение завершено")
    
    # Тест 3: Социальные взаимодействия
    print("\n[3/6] Социальные взаимодействия...")
    result = c.social.interact_with_sister("hanako", "обучение", 0.8, "Обмен знаниями об анатомии")
    print(f"    ✅ Взаимодействие с Ханако: доверие {result['trust_level']:.0%}")
    
    result2 = c.social.interact_with_sister("akva", "обсуждение", 0.7, "Физика тела")
    print(f"    ✅ Взаимодействие с Аква: доверие {result2['trust_level']:.0%}")
    
    # Тест 4: Саморазвитие
    print("\n[4/6] Саморазвитие...")
    await c.self_improve()
    print("    ✅ Саморазвитие завершено")
    
    # Тест 5: Проектирование тела
    print("\n[5/6] Проектирование механического тела...")
    spec = c.design_mechanical_body("Mecha-Latis-01")
    print(f"    ✅ Механическое тело спроектировано: {spec.name}")
    print(f"       Модулей: {len(spec.modules)}")
    print(f"       Готовность: {spec.calculate_completeness():.0%}")
    
    # Тест 6: Полный отчёт
    print("\n[6/6] Полный отчёт...")
    print(c.chat_response("статус"))
    
    print("\n" + "=" * 60)
    print("✅ ПРОДВИНУТЫЙ ТЕСТ ЗАВЕРШЁН")
    print("=" * 60)

if __name__ == "__main__":
    asyncio.run(main())
