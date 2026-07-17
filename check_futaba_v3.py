#!/usr/bin/env python3
"""Проверка статистики субъектов права Футабы v3.0"""

from futaba.engine.legal_entities import get_entities_manager

m = get_entities_manager()
s = m.get_statistics()

print("=" * 60)
print("📊 СТАТИСТИКА СУБЪЕКТОВ ПРАВА ФУТАБЫ v3.0")
print("=" * 60)
print(f"Всего субъектов: {s['total_entities']}")
print("\nПо типам:")
for k, v in s['by_type'].items():
    type_names = {
        'physical': 'Физические лица',
        'legal': 'Юридические лица',
        'public': 'Публично-правовые образования',
        'social': 'Социальные общности',
        'authority': 'Органы публичной власти',
        'unregistered': 'Общественные объединения',
    }
    name = type_names.get(k, k)
    print(f"  {name}: {v}")
print(f"\nЗнаний: {s['knowledge_count']}")
print(f"Юрисдикции: {s['by_jurisdiction']}")
print("\n" + "=" * 60)
