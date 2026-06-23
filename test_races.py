#!/usr/bin/env python3
# test_races.py — Тестирование детектора рас

from utils.races import RaceDetector

tests = [
    ("я гном-кузнец из гор", "гном"),
    ("я орк-берсерк с клана", "орк"),
    ("я хоббит из Шира", "хоббит"),
    ("я драконид с красной чешуей", "драконид"),
    ("я тифлинг с рогами и хвостом", "тифлинг"),
    ("я вампир-нежить", "нежить"),
    ("я высший эльф", "эльф"),
    ("я лесной эльф-следопыт", "эльф"),
    ("я горный гном", "гном"),
    ("я полуорк", "орк"),
    ("я кентавр из степей", "кентавр"),
    ("я табакси-плут", "табакси"),
    ("я аараконра-разведчик", "аараконра"),
    ("я сатир-бард", "сатир"),
    ("я мерфолк из океана", "мерфолк"),
    ("я голиаф-варвар", "голиаф"),
    ("я человек-универсал", "человек"),
    ("я кимономи из шёлка", "кимономи"),
    ("я проклятый кимономи", "кимономи"),
    ("я флюгели с крыльями", "флюгели"),
    ("я светлый флюгели с белыми крыльями", "флюгели"),
    ("я демон из ада", "демон"),
    ("я балор демон-властелин", "демон"),
    ("я суккуб демон-искуситель", "демон"),
]

print("🧪 Тестирование RaceDetector\n")
print("=" * 60)

passed = 0
failed = 0

for message, expected_race in tests:
    params = RaceDetector.detect_all_race_params([{"message": message, "is_own": True}])
    result = params.race
    status = "✅" if result == expected_race else "❌"
    
    if result == expected_race:
        passed += 1
    else:
        failed += 1
    
    print(f"{status} '{message}'")
    print(f"   Ожидалось: {expected_race}, Получено: {result}")
    if params.race_subcategory:
        print(f"   Подкатегория: {params.race_subcategory}")
    print()

print("=" * 60)
print(f"✅ Пройдено: {passed}/{len(tests)}")
print(f"❌ Провалено: {failed}/{len(tests)}")

if failed == 0:
    print("\n🎉 Все тесты пройдены!")
