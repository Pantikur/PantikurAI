#!/usr/bin/env python3
"""
Тестирование всех новых систем Айко

Проверяет:
- Система навыков
- Графические техники
- Цветовая теория
- Композиция
- Профессиональный генератор
"""

import sys
import json
from pathlib import Path
from PIL import Image, ImageDraw

# Добавляем проект в путь
sys.path.insert(0, str(Path(__file__).parent))

def test_skill_system():
    """Тестирует систему навыков"""
    print("\n" + "="*60)
    print("🎯 ТЕСТ: Система навыков")
    print("="*60)
    
    try:
        from ayiko.skill_system import AyikoSkillSystem
        system = AyikoSkillSystem()
        
        # Тренируем навыки
        system.train_skill("pixel_art", 2.0, 0.9)
        system.train_skill("watercolor", 1.5, 0.8)
        
        # Проверяем
        summary = system.get_skill_summary()
        print(f"\n✅ Всего навыков: {summary['total_skills']}")
        print(f"✅ Средний уровень: {summary['average_level']}")
        
        efficiency = system.analyze_training_efficiency()
        print(f"✅ Часов практики: {efficiency['total_hours']}")
        print(f"✅ Эффективность: {efficiency['avg_quality']}")
        
        return True
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_rendering_techniques():
    """Тестирует графические техники"""
    print("\n" + "="*60)
    print("🛠️ ТЕСТ: Графические техники")
    print("="*60)
    
    try:
        from PIL import Image
        from ayiko.rendering_techniques import AyikoRenderingTechniques
        
        techniques = AyikoRenderingTechniques()
        
        # Создаём тестовое изображение
        test_img = Image.new('RGB', (256, 256), (100, 150, 200))
        draw = ImageDraw.Draw(test_img)
        draw.ellipse([50, 50, 200, 200], fill=(200, 100, 100))
        
        # Тестируем техники
        dithered = techniques.apply_dithering(test_img, "floyd_steinberg")
        print("✅ Dithering применён")
        
        oil = techniques.apply_oil_painting_effect(test_img, brush_size=8)
        print("✅ Oil painting применён")
        
        watercolor = techniques.apply_watercolor_effect(test_img, bleed=4)
        print("✅ Watercolor применён")
        
        bloom = techniques.apply_bloom(test_img, radius=8)
        print("✅ Bloom применён")
        
        grain = techniques.apply_film_grain(test_img, intensity=0.1)
        print("✅ Film grain применён")
        
        vignette = techniques.apply_vignette(test_img, strength=0.5)
        print("✅ Vignette применён")
        
        return True
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_color_theory():
    """Тестирует цветовую теорию"""
    print("\n" + "="*60)
    print("🎨 ТЕСТ: Цветовая теория")
    print("="*60)
    
    try:
        from ayiko.color_theory import AyikoColorTheory
        
        theory = AyikoColorTheory()
        
        test_color = (200, 100, 50)
        print(f"\nБазовый цвет: {test_color}")
        
        # Тестируем гармонии
        comp = theory.get_complementary(test_color)
        print(f"✅ Комплементарный: {comp}")
        
        analog = theory.get_analogous(test_color)
        print(f"✅ Аналоговые: {len(analog)} цветов")
        
        triadic = theory.get_triadic(test_color)
        print(f"✅ Триадные: {len(triadic)} цветов")
        
        # Тестируем палитры
        warm_palette = theory.generate_palette_from_mood("warm", 6)
        print(f"✅ Палитра 'warm': {len(warm_palette)} цветов")
        
        cool_palette = theory.generate_palette_from_mood("cool", 6)
        print(f"✅ Палитра 'cool': {len(cool_palette)} цветов")
        
        # Тестируем температуру
        temp = theory.get_color_temperature(test_color)
        print(f"✅ Температура: {temp}")
        
        emotion = theory.get_color_emotion(test_color)
        print(f"✅ Эмоция: {emotion}")
        
        return True
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_composition():
    """Тестирует систему композиции"""
    print("\n" + "="*60)
    print("📐 ТЕСТ: Композиция")
    print("="*60)
    
    try:
        from PIL import Image
        from ayiko.composition import AyikoComposition
        
        comp = AyikoComposition()
        
        # Тест золотого сечения
        long, short = comp.golden_divide(1000)
        print(f"\n✅ Золотое разделение 1000px: {long:.1f} / {short:.1f}")
        
        gx, gy = comp.golden_ratio_point(512, 512)
        print(f"✅ Точка золотого сечения: ({gx}, {gy})")
        
        # Правило третей
        thirds = comp.get_rule_of_thirds_lines(512, 512)
        print(f"✅ Линии третей: {len(thirds['vertical_lines'])} вертикальных, {len(thirds['horizontal_lines'])} горизонтальных")
        
        # Анализ композиции
        test_img = Image.new('RGB', (512, 512), (100, 150, 200))
        analysis = comp.calculate_composition_strength(test_img)
        print(f"✅ Оценка композиции: {analysis['overall_score']}")
        
        # Советы
        suggestions = comp.suggest_composition_improvements(test_img)
        print(f"✅ Советы: {len(suggestions)}")
        for s in suggestions[:2]:
            print(f"   - {s}")
        
        return True
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_professional_generator():
    """Тестирует профессиональный генератор"""
    print("\n" + "="*60)
    print("🎨 ТЕСТ: Профессиональный генератор")
    print("="*60)
    
    try:
        from ayiko.professional_generator import AyikoProfessionalGenerator
        
        gen = AyikoProfessionalGenerator()
        
        # Тест генерации персонажа
        char_desc = {
            "name": "Talsa",
            "skin_color": (195, 155, 115),
            "hair_color": (55, 35, 25),
            "hair_style": "bun",
            "eye_color": (45, 28, 18),
            "clothing": [{"type": "shirt", "color": (155, 145, 135)}],
            "accessories": [{"type": "glasses"}]
        }
        
        img = gen.generate_professional_character(char_desc, (512, 512), "realistic")
        gen.save_image(img, "test_professional.png")
        print("✅ Персонаж сохранён: test_professional.png")
        
        # Тест практики
        gen.practice_technique("pixel_art", 2.0)
        print("✅ Практика пиксель-арта выполнена")
        
        gen.practice_technique("watercolor", 1.5)
        print("✅ Практика акварели выполнена")
        
        # Статистика
        stats = gen.get_full_stats()
        print(f"\n📊 Статистика:")
        print(f"   - Всего изображений: {stats['experience']['total_images']}")
        print(f"   - Средний навык: {stats['average_skill']}")
        print(f"   - Навыков в системе: {stats['skill_system']['total_skills']}")
        
        return True
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Главная функция"""
    print("\n" + "="*60)
    print("🧪 ТЕСТИРОВАНИЕ НОВЫХ СИСТЕМ АЙКО")
    print("="*60)
    
    tests = [
        ("Система навыков", test_skill_system),
        ("Графические техники", test_rendering_techniques),
        ("Цветовая теория", test_color_theory),
        ("Композиция", test_composition),
        ("Профессиональный генератор", test_professional_generator),
    ]
    
    results = []
    for name, test_func in tests:
        try:
            result = test_func()
            results.append((name, result))
        except Exception as e:
            print(f"\n❌ Критическая ошибка в {name}: {e}")
            results.append((name, False))
    
    # Итоги
    print("\n" + "="*60)
    print("RESULTS SUMMARY")
    print("="*60)
    
    passed = sum(1 for _, r in results if r)
    total = len(results)
    
    for name, result in results:
        status = "✅" if result else "❌"
        print(f"  {status} {name}")
    
    print(f"\n📈 Пройдено: {passed}/{total}")
    
    if passed == total:
        print("\n🎉 ВСЕ СИСТЕМЫ РАБОТАЮТ! Айко теперь профессионал!")
    else:
        print(f"\n⚠️ {total - passed} тестов не пройдено")
    
    return passed == total


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
