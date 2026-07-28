#!/usr/bin/env python3
"""
Айко AI — Интегрированный Профессиональный Генератор

Полная интеграция всех систем:
  - image_generator.py (базовый генератор)
  - skill_system.py (система навыков)
  - rendering_techniques.py (графические техники)
  - color_theory.py (цветовая теория)
  - composition.py (композиция)
"""

import json
import random
import math
from pathlib import Path
from typing import List, Dict, Tuple, Optional, Any
from datetime import datetime

from PIL import Image, ImageDraw, ImageFilter, ImageEnhance

from ayiko.skill_system import AyikoSkillSystem
from ayiko.rendering_techniques import AyikoRenderingTechniques
from ayiko.color_theory import AyikoColorTheory
from ayiko.composition import AyikoComposition


class AyikoProfessionalGenerator:
    """
    Интегрированный профессиональный генератор Айко.
    
    Объединяет все системы в единый мощный инструмент.
    """
    
    def __init__(self, output_dir: str = "data/ayiko_generated"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Инициализируем все системы
        self.skill_system = AyikoSkillSystem()
        self.rendering = AyikoRenderingTechniques()
        self.color_theory = AyikoColorTheory()
        self.composition = AyikoComposition()
        
        # Базовые навыки
        self.skills = {
            "pixel_art": 8,
            "character": 9,
            "landscape": 7,
            "technical": 6,
            "color_theory": 9,
            "composition": 8,
            "anatomy": 8,
            "lighting": 7,
            "texture": 6,
            "style_adaptation": 7
        }
        
        # Прогресс
        self.experience = {
            "total_images": 0,
            "masterpieces": 0,
            "sessions": 0
        }
        
        # Палитры
        self.palettes = self._init_palettes()
        
        print("\n" + "="*60)
        print("AYIKO PROFESSIONAL GENERATOR v4.0")
        print("="*60)
        print(f"OK Skill System: {self.skill_system.get_skill_summary()['total_skills']} skills")
        print("OK Rendering techniques: loaded")
        print("OK Color theory: loaded")
        print("OK Composition: loaded")
        print("="*60 + "\n")
    
    def _init_palettes(self) -> Dict[str, List[Tuple]]:
        """Инициализация палитр"""
        return {
            "classical": [(210, 180, 140), (139, 69, 19), (245, 245, 220),
                         (101, 67, 33), (255, 250, 240), (70, 40, 20)],
            "anime": [(255, 200, 220), (135, 206, 250), (255, 182, 193),
                     (255, 255, 224), (176, 224, 230), (255, 192, 203)],
            "cyberpunk": [(0, 255, 255), (255, 0, 255), (0, 0, 255),
                         (255, 255, 0), (128, 0, 128), (0, 128, 255)],
            "nature": [(34, 139, 34), (85, 107, 47), (144, 238, 144),
                      (173, 216, 230), (255, 250, 205), (139, 90, 43)],
            "sunset": [(255, 99, 71), (255, 165, 0), (255, 215, 0),
                      (255, 105, 180), (138, 43, 226), (75, 0, 130)],
            "night": [(0, 0, 50), (25, 25, 112), (70, 130, 180),
                     (176, 196, 222), (256, 256, 256), (112, 128, 144)],
            "pastel": [(255, 183, 197), (176, 224, 230), (255, 218, 185),
                      (221, 160, 221), (152, 251, 152), (255, 255, 192)],
            "watercolor": [(176, 224, 230), (255, 182, 193), (255, 218, 185),
                          (221, 160, 221), (173, 216, 230), (245, 250, 240)],
            "oil_painting": [(139, 69, 19), (34, 139, 34), (65, 105, 225),
                            (255, 215, 0), (220, 20, 60), (128, 0, 128)],
        }
    
    # ================================================================
    #  ПРОФЕССИОНАЛЬНАЯ ГЕНЕРАЦИЯ ПЕРСОНАЖА
    # ================================================================
    
    def generate_professional_character(self, description: Dict, 
                                       size: Tuple[int, int] = (512, 512),
                                       style: str = "realistic",
                                       use_golden_ratio: bool = True) -> Image.Image:
        """
        Профессиональная генерация персонажа с использованием всех систем.
        
        Args:
            description: Параметры персонажа
            size: Размер изображения
            style: Стиль (realistic, anime, watercolor, oil_painting, sketch, pixel)
            use_golden_ratio: Использовать золотое сечение для композиции
        """
        if use_golden_ratio:
            print("   Using golden ratio for composition...")
        
        W, H = size
        
        # Получаем палитру по стилю
        palette_name = style if style in self.palettes else "classical"
        palette = self.palettes[palette_name]
        
        # Применяем цветовую теорию
        if self.skills["color_theory"] >= 7:
            base_color = palette[0]
            harmonious = self.color_theory.get_analogous(base_color)
            palette = harmonious
            print("   Applied analogous harmony")
        
        # Генерируем фон с композицией
        bg = self._generate_composition_background(W, H, palette, use_golden_ratio)
        
        # Создаём персонажа
        char_img = self._draw_character_layer(W, H, description, palette)
        
        # Комбинируем
        result = bg.copy()
        result = Image.alpha_composite(result, char_img)
        
        # Применяем стиль с учётом навыков
        skill_level = self.skills.get(style.replace("_", ""), 7)
        result = self._apply_style_with_skills(result, style, skill_level)
        
        # Постобработка
        result = self._professional_postprocess(result, style)
        
        # Увеличиваем опыт
        self.experience["total_images"] += 1
        
        return result
    
    def _generate_composition_background(self, width: int, height: int,
                                        palette: List[Tuple], 
                                        use_golden: bool = True) -> Image.Image:
        """Генерирует фон с профессиональной композицией"""
        bg = Image.new('RGBA', (width, height), (255, 255, 255, 0))
        draw = ImageDraw.Draw(bg)
        
        if use_golden:
            # Золотое сечение для размещения элементов
            gx, gy = self.composition.golden_ratio_point(width, height)
            
            # Градиент от золотой точки
            for y in range(height):
                for x in range(width):
                    dist = math.sqrt((x - gx)**2 + (y - gy)**2)
                    max_dist = math.sqrt(width**2 + height**2) / 2
                    ratio = dist / max_dist
                    
                    color_idx = min(int(ratio * len(palette)), len(palette) - 1)
                    color = palette[color_idx]
                    draw.point((x, y), fill=color)
        else:
            # Простой градиент
            for y in range(height):
                ratio = y / height
                color_idx = min(int(ratio * len(palette)), len(palette) - 1)
                color = palette[color_idx]
                draw.line([(0, y), (width, y)], fill=color)
        
        return bg
    
    def _draw_character_layer(self, width: int, height: int, 
                             description: Dict, palette: List[Tuple]) -> Image.Image:
        """Слой персонажа"""
        char = Image.new('RGBA', (width, height), (0, 0, 0, 0))
        draw = ImageDraw.Draw(char)
        
        # Параметры
        skin_color = tuple(description.get("skin_color", (195, 155, 115)))
        hair_color = tuple(description.get("hair_color", (55, 35, 25)))
        eye_color = tuple(description.get("eye_color", (45, 28, 18)))
        hair_style = description.get("hair_style", "bun")
        
        # Центр
        cx, cy = width // 2, height // 3
        
        # Голова
        head_r = int(height * 0.12)
        draw.ellipse([cx - head_r, cy - head_r, cx + head_r, cy + head_r], 
                    fill=skin_color)
        
        # Волосы
        draw.ellipse([cx - head_r - 5, cy - head_r - 10, 
                     cx + head_r + 5, cy + head_r * 0.5], 
                    fill=hair_color)
        
        # Глаза
        eye_y = cy
        for side in [-1, 1]:
            ex = cx + side * head_r * 0.5
            draw.ellipse([ex - 8, eye_y - 6, ex + 8, eye_y + 6], 
                        fill=(255, 255, 255))
            draw.ellipse([ex - 5, eye_y - 5, ex + 5, eye_y + 5], 
                        fill=eye_color)
            draw.ellipse([ex - 2, eye_y - 2, ex + 2, eye_y + 2], 
                        fill=(20, 10, 5))
        
        # Тело
        body_y = cy + head_r
        body_w = head_r * 1.5
        draw.rectangle([cx - body_w, body_y, cx + body_w, body_y + height // 2], 
                      fill=palette[1] if len(palette) > 1 else (100, 100, 100))
        
        return char
    
    def _apply_style_with_skills(self, img: Image.Image, style: str, 
                                skill_level: int) -> Image.Image:
        """Применяет стиль с учётом уровня навыка"""
        
        if style == "realistic":
            blur = min(1.5, skill_level * 0.15)
            img = img.filter(ImageFilter.GaussianBlur(radius=blur))
            img = ImageEnhance.Contrast(img).enhance(1.1 + skill_level * 0.02)
        
        elif style == "watercolor":
            img = img.filter(ImageFilter.GaussianBlur(radius=3))
            img = img.filter(ImageFilter.EDGE_ENHANCE)
            img = ImageEnhance.Color(img).enhance(1.2)
        
        elif style == "oil_painting":
            img = img.filter(ImageFilter.GaussianBlur(radius=2))
            img = img.filter(ImageFilter.SHARPEN)
            img = ImageEnhance.Color(img).enhance(1.3)
        
        elif style == "sketch":
            gray = img.convert('L')
            gray = gray.filter(ImageFilter.CONTOUR)
            noise = Image.new('L', gray.size)
            for y in range(gray.size[1]):
                for x in range(gray.size[0]):
                    noise.putpixel((x, y), random.randint(200, 255))
            gray = Image.blend(gray, noise, 0.1)
            img = gray.convert('RGB')
        
        elif style == "pixel":
            pixel_size = max(2, 10 - skill_level)
            small = img.resize((img.width // pixel_size, img.height // pixel_size), 
                             Image.NEAREST)
            img = small.resize(img.size, Image.NEAREST)
        
        return img
    
    def _professional_postprocess(self, img: Image.Image, style: str) -> Image.Image:
        """Профессиональная постобработка"""
        
        # Цветокоррекция
        img = self.color_theory.apply_color_grading(img, style)
        
        # Зерно плёнки (для реализма)
        if style in ["realistic", "oil_painting"]:
            img = self.rendering.apply_film_grain(img, intensity=0.05)
        
        # Виньетка
        img = self.rendering.apply_vignette(img, strength=0.3)
        
        return img
    
    # ================================================================
    #  ОБУЧЕНИЕ И ПРОГРЕССИЯ
    # ================================================================
    
    def train_with_example(self, example_image: Image.Image, 
                          target_style: str = "realistic"):
        """
        Обучается на примере изображения.
        
        Анализирует технику, цвета, композицию и улучшает навыки.
        """
        print(f"\n📚 Анализ примера для стиля '{target_style}'...")
        
        # Анализируем композицию
        comp_analysis = self.composition.calculate_composition_strength(example_image)
        print(f"   📐 Композиция: {comp_analysis['overall_score']}")
        
        # Анализируем цвета
        palette = self.color_theory.generate_palette_from_image(example_image, k=5)
        print(f"   🎨 Извлечено {len(palette)} цветов")
        
        # Тренируем навыки
        quality = comp_analysis['overall_score']
        self.skill_system.train_skill("character", 1.0, quality)
        self.skill_system.train_skill("color_theory", 0.5, quality)
        
        # Обновляем навыки
        self.skills["character"] = self.skill_system.get_skill_level("character")
        self.skills["color_theory"] = self.skill_system.get_skill_level("color_theory")
        
        print(f"   ✅ Навыки обновлены")
    
    def practice_technique(self, technique: str, hours: float = 1.0):
        """Практикует технику"""
        print(f"\n🎯 Практика: {technique} ({hours}ч)")
        
        if technique == "pixel_art":
            self.skill_system.train_skill("pixel_art", hours, 0.8)
            self.skills["pixel_art"] = self.skill_system.get_skill_level("pixel_art")
        
        elif technique == "watercolor":
            self.skill_system.train_skill("watercolor", hours, 0.7)
            self.skills["character"] = max(self.skills["character"], 
                                          self.skill_system.get_skill_level("watercolor"))
        
        elif technique == "oil_painting":
            self.skill_system.train_skill("oil_painting", hours, 0.7)
            self.skills["character"] = max(self.skills["character"],
                                          self.skill_system.get_skill_level("oil_painting"))
        
        elif technique == "anatomy":
            self.skill_system.train_skill("anatomy", hours, 0.9)
            self.skills["anatomy"] = self.skill_system.get_skill_level("anatomy")
        
        print(f"   ✅ Навык обновлён")
    
    # ================================================================
    #  СТАТИСТИКА И ОТЧЁТЫ
    # ================================================================
    
    def get_full_stats(self) -> Dict:
        """Полная статистика"""
        return {
            "experience": self.experience,
            "skills": {k: round(v, 1) for k, v in self.skills.items()},
            "skill_system": self.skill_system.get_skill_summary(),
            "training_efficiency": self.skill_system.analyze_training_efficiency(),
            "average_skill": round(sum(self.skills.values()) / len(self.skills), 1)
        }
    
    def save_stats(self, filename: str = "ayiko_stats.json"):
        """Сохраняет статистику"""
        stats = self.get_full_stats()
        file = self.output_dir / filename
        with open(file, "w", encoding="utf-8") as f:
            json.dump(stats, f, ensure_ascii=False, indent=2)
        print(f"   Stats saved: {file}")
    
    def save_image(self, img: Image.Image, filename: str = None) -> str:
        """Сохраняет изображение"""
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"ayiko_{timestamp}.png"
        
        output_path = self.output_dir / filename
        img.save(output_path, "PNG")
        return str(output_path)


if __name__ == "__main__":
    gen = AyikoProfessionalGenerator()
    
    print("\n=== ТЕСТ ПРОФЕССИОНАЛЬНОГО ГЕНЕРАТОРА ===\n")
    
    # Тест генерации персонажа
    char_desc = {
        "name": "Talsa",
        "age": 17,
        "body_type": "athletic",
        "skin_color": (195, 155, 115),
        "hair_color": (55, 35, 25),
        "hair_style": "bun",
        "eye_color": (45, 28, 18),
        "clothing": [{"type": "shirt", "color": (155, 145, 135), "sleeves": "short"}],
        "accessories": [{"type": "glasses"}],
        "background": "academy"
    }
    
    print("Генерация персонажа (реалистичный стиль)...")
    img = gen.generate_professional_character(char_desc, (512, 512), "realistic")
    gen.save_image(img, "test_professional.png")
    print("   ✅ Сохранён: test_professional.png")
    
    # Тест практики
    print("\nПрактика пиксель-арта (2 часа)...")
    gen.practice_technique("pixel_art", 2.0)
    
    print("\nПрактика акварели (1.5 часа)...")
    gen.practice_technique("watercolor", 1.5)
    
    # Статистика
    print("\n📊 Статистика:")
    stats = gen.get_full_stats()
    print(json.dumps(stats, indent=2, ensure_ascii=False))
