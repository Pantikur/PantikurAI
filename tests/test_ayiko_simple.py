#!/usr/bin/env python3
"""
Test all new Ayiko systems - simplified version
"""

import sys
import io

# Fix Windows console encoding
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

import json
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

def test_skill_system():
    print("\n[1/5] Testing Skill System...")
    try:
        from ayiko.skill_system import AyikoSkillSystem
        system = AyikoSkillSystem()
        system.train_skill("pixel_art", 2.0, 0.9)
        summary = system.get_skill_summary()
        print(f"      OK - Skills: {summary['total_skills']}, Avg: {summary['average_level']}")
        return True
    except Exception as e:
        print(f"      FAIL: {e}")
        return False

def test_rendering():
    print("[2/5] Testing Rendering Techniques...")
    try:
        from PIL import Image, ImageDraw
        from ayiko.rendering_techniques import AyikoRenderingTechniques
        tech = AyikoRenderingTechniques()
        
        # Dithering works on grayscale
        test_gray = Image.new('L', (256, 256), 128)
        dithered = tech.apply_dithering(test_gray, "floyd_steinberg")
        
        # Oil painting needs RGB
        test_rgb = Image.new('RGB', (256, 256), (100, 150, 200))
        draw = ImageDraw.Draw(test_rgb)
        draw.ellipse([50, 50, 200, 200], fill=(200, 100, 100))
        oil = tech.apply_oil_painting_effect(test_rgb, brush_size=8)
        
        # Bloom needs RGB
        bloom = tech.apply_bloom(test_rgb, radius=8)
        print("      OK - Dithering, Oil, Bloom applied")
        return True
    except Exception as e:
        print(f"      FAIL: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_color_theory():
    print("[3/5] Testing Color Theory...")
    try:
        from ayiko.color_theory import AyikoColorTheory
        theory = AyikoColorTheory()
        test_color = (200, 100, 50)
        comp = theory.get_complementary(test_color)
        warm_palette = theory.generate_palette_from_mood("warm", 6)
        print(f"      OK - Complementary: {comp}, Palette: {len(warm_palette)} colors")
        return True
    except Exception as e:
        print(f"      FAIL: {e}")
        return False

def test_composition():
    print("[4/5] Testing Composition...")
    try:
        from PIL import Image
        from ayiko.composition import AyikoComposition
        comp = AyikoComposition()
        gx, gy = comp.golden_ratio_point(512, 512)
        test_img = Image.new('RGB', (512, 512), (100, 150, 200))
        analysis = comp.calculate_composition_strength(test_img)
        print(f"      OK - Golden ratio: ({gx}, {gy}), Score: {analysis['overall_score']}")
        return True
    except Exception as e:
        print(f"      FAIL: {e}")
        return False

def test_professional_gen():
    print("[5/5] Testing Professional Generator...")
    try:
        from ayiko.professional_generator import AyikoProfessionalGenerator
        gen = AyikoProfessionalGenerator()
        char_desc = {
            "name": "Test",
            "skin_color": (195, 155, 115),
            "hair_color": (55, 35, 25),
            "hair_style": "bun",
            "eye_color": (45, 28, 18)
        }
        img = gen.generate_professional_character(char_desc, (512, 512), "realistic")
        gen.save_image(img, "test_prof.png")
        print("      OK - Character generated and saved")
        return True
    except Exception as e:
        print(f"      FAIL: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    print("="*60)
    print("AYIKO NEW SYSTEMS TEST")
    print("="*60)
    
    tests = [
        test_skill_system,
        test_rendering,
        test_color_theory,
        test_composition,
        test_professional_gen
    ]
    
    results = [test() for test in tests]
    
    print("\n" + "="*60)
    print("RESULTS")
    print("="*60)
    passed = sum(results)
    total = len(results)
    print(f"Passed: {passed}/{total}")
    
    if passed == total:
        print("\nALL SYSTEMS WORKING! Ayiko is now a professional!")
    else:
        print(f"\n{total - passed} tests failed")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
