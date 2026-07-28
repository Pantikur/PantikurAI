#!/usr/bin/env python3
"""
Айко AI — Профессиональная Цветовая Теория

Использует:
  🌈 Цветовые модели (RGB, HSV, HSL, CMYK)
  🎨 Цветовые гармонии (комплементарная, аналоговая, триадная)
  💡 Настроения через цвет (тёплые/холодные, светлые/тёмные)
  📊 Автоматический подбор палитр
  🔄 Конвертация между моделями
"""

import colorsys
import random
import math
from typing import List, Tuple, Dict
from PIL import Image


class AyikoColorTheory:
    """Профессиональная система цветовой теории"""
    
    def __init__(self):
        self.color_moods = {
            "warm": {"description": "Тёплые, энергичные", "range": (0, 60)},
            "cool": {"description": "Холодные, спокойные", "range": (180, 270)},
            "neutral": {"description": "Нейтральные, сдержанные", "range": (0, 360), "saturation_range": (0, 0.2)},
            "vibrant": {"description": "Яркие, насыщенные", "saturation_range": (0.7, 1.0)},
            "pastel": {"description": "Мягкие, нежные", "value_range": (0.7, 1.0), "saturation_range": (0.2, 0.5)},
            "dark": {"description": "Тёмные, драматичные", "value_range": (0, 0.4)},
            "earth": {"description": "Земляные, натуральные", "range": (20, 50), "saturation_range": (0.2, 0.6)},
            "jewel": {"description": "Драгоценные, глубокие", "saturation_range": (0.6, 1.0), "value_range": (0.3, 0.7)}
        }
        print("Color theory initialized")
    
    # ================================================================
    #  ЦВЕТОВЫЕ МОДЕЛИ
    # ================================================================
    
    def rgb_to_hsv(self, r: int, g: int, b: int) -> Tuple[float, float, float]:
        """RGB → HSV"""
        return colorsys.rgb_to_hsv(r/255, g/255, b/255)
    
    def hsv_to_rgb(self, h: float, s: float, v: float) -> Tuple[int, int, int]:
        """HSV → RGB"""
        r, g, b = colorsys.hsv_to_rgb(h, s, v)
        return (int(r*255), int(g*255), int(b*255))
    
    def rgb_to_hsl(self, r: int, g: int, b: int) -> Tuple[float, float, float]:
        """RGB → HSL"""
        h, l, s = colorsys.rgb_to_hsv(r/255, g/255, b/255)
        # Преобразуем к HSL
        l_new = l - s * min(l, 1-l)
        s_new = s * min(l, 1-l) if l != 0 else 0
        return (h, s_new, l_new)
    
    def hsl_to_rgb(self, h: float, s: float, l: float) -> Tuple[int, int, int]:
        """HSL → RGB"""
        v = l + s * min(l, 1-l)
        s_new = 2 * (v - l) / v if v != 0 else 0
        return self.hsv_to_rgb(h, s_new, v)
    
    # ================================================================
    #  ЦВЕТОВЫЕ ГАРМОНИИ
    # ================================================================
    
    def get_complementary(self, color: Tuple[int, int, int]) -> Tuple[int, int, int]:
        """Комплементарный цвет (противоположный на круге)"""
        h, s, v = self.rgb_to_hsv(*color)
        h = (h + 0.5) % 1.0
        return self.hsv_to_rgb(h, s, v)
    
    def get_analogous(self, color: Tuple[int, int, int], spread: float = 0.08) -> List[Tuple[int, int, int]]:
        """Аналоговые цвета (соседние на круге)"""
        h, s, v = self.rgb_to_hsv(*color)
        return [
            self.hsv_to_rgb((h - spread) % 1.0, s, v),
            color,
            self.hsv_to_rgb((h + spread) % 1.0, s, v)
        ]
    
    def get_triadic(self, color: Tuple[int, int, int]) -> List[Tuple[int, int, int]]:
        """Триадные цвета (через 120°)"""
        h, s, v = self.rgb_to_hsv(*color)
        return [
            color,
            self.hsv_to_rgb((h + 1/3) % 1.0, s, v),
            self.hsv_to_rgb((h + 2/3) % 1.0, s, v)
        ]
    
    def get_split_complementary(self, color: Tuple[int, int, int]) -> List[Tuple[int, int, int]]:
        """Раздельно-комплементарная"""
        h, s, v = self.rgb_to_hsv(*color)
        return [
            color,
            self.hsv_to_rgb((h + 0.5 - 0.15) % 1.0, s, v),
            self.hsv_to_rgb((h + 0.5 + 0.15) % 1.0, s, v)
        ]
    
    def get_tetradic(self, color: Tuple[int, int, int]) -> List[Tuple[int, int, int]]:
        """Тетрадная (прямоугольная)"""
        h, s, v = self.rgb_to_hsv(*color)
        return [
            color,
            self.hsv_to_rgb((h + 0.25) % 1.0, s, v),
            self.get_complementary(color),
            self.hsv_to_rgb((h + 0.75) % 1.0, s, v)
        ]
    
    def get_monochromatic(self, color: Tuple[int, int, int], steps: int = 5) -> List[Tuple[int, int, int]]:
        """Монохроматическая (разная яркость)"""
        h, s, v = self.rgb_to_hsv(*color)
        palette = []
        for i in range(steps):
            new_v = 0.2 + (v * (i / (steps - 1)))
            palette.append(self.hsv_to_rgb(h, s, new_v))
        return palette
    
    # ================================================================
    #  АВТОМАТИЧЕСКИЙ ПОДБОР ПАЛИТР
    # ================================================================
    
    def generate_palette_from_mood(self, mood: str, size: int = 6) -> List[Tuple[int, int, int]]:
        """Генерирует палитру по настроению"""
        if mood not in self.color_moods:
            raise ValueError(f"Неизвестное настроение: {mood}")
        
        config = self.color_moods[mood]
        palette = []
        
        for i in range(size):
            # Генерируем цвет в диапазоне
            if "range" in config:
                h = (config["range"][0] + (config["range"][1] - config["range"][0]) * (i / size)) / 360.0
            else:
                h = i / size
            
            s = 0.6 + 0.3 * (i / size)
            if "saturation_range" in config:
                s = config["saturation_range"][0] + (config["saturation_range"][1] - config["saturation_range"][0]) * (i / size)
            
            v = 0.7 + 0.2 * ((size - i) / size)
            if "value_range" in config:
                v = config["value_range"][0] + (config["value_range"][1] - config["value_range"][0]) * (i / size)
            
            palette.append(self.hsv_to_rgb(h, s, v))
        
        return palette
    
    def generate_palette_from_image(self, img: Image.Image, k: int = 6) -> List[Tuple[int, int, int]]:
        """Извлекает доминирующие цвета из изображения (k-means упрощённый)"""
        # Уменьшаем для скорости
        small = img.resize((50, 50))
        pixels = list(small.getdata())
        
        # Простой подбор: берём случайные точки с разной яркостью
        palette = []
        for target_v in [0.2, 0.4, 0.6, 0.8]:
            best_color = None
            best_diff = float('inf')
            
            for _ in range(100):  # 100 попыток
                idx = random.randint(0, len(pixels) - 1)
                r, g, b = pixels[idx]
                h, s, v = self.rgb_to_hsv(r, g, b)
                
                if abs(v - target_v) < best_diff:
                    best_diff = abs(v - target_v)
                    best_color = (r, g, b)
            
            if best_color:
                palette.append(best_color)
        
        return palette[:k]
    
    def calculate_color_distance(self, color1: Tuple[int, int, int], 
                                color2: Tuple[int, int, int]) -> float:
        """Рассчитывает расстояние между цветами (в HSV пространстве)"""
        h1, s1, v1 = self.rgb_to_hsv(*color1)
        h2, s2, v2 = self.rgb_to_hsv(*color2)
        
        # Учитываем круговую природу оттенка
        dh = min(abs(h1 - h2), 1 - abs(h1 - h2))
        ds = abs(s1 - s2)
        dv = abs(v1 - v2)
        
        return math.sqrt(dh**2 + ds**2 + dv**2)
    
    def is_color_harmonious(self, colors: List[Tuple[int, int, int]], 
                           threshold: float = 0.5) -> bool:
        """Проверяет гармоничность палитры"""
        if len(colors) < 2:
            return True
        
        total_distance = 0
        count = 0
        
        for i in range(len(colors)):
            for j in range(i + 1, len(colors)):
                dist = self.calculate_color_distance(colors[i], colors[j])
                total_distance += dist
                count += 1
        
        avg_distance = total_distance / count if count > 0 else 0
        return avg_distance < threshold
    
    def adjust_color_for_mood(self, color: Tuple[int, int, int], 
                             mood: str) -> Tuple[int, int, int]:
        """Корректирует цвет под настроение"""
        h, s, v = self.rgb_to_hsv(*color)
        
        if mood == "warm":
            h = (h + 0.05) % 1.0  # Сдвиг в тёплую сторону
            s = min(1.0, s * 1.1)  # Насыщеннее
        elif mood == "cool":
            h = (h + 0.2) % 1.0   # Сдвиг в холодную
            v = min(1.0, v * 1.05)
        elif mood == "melancholy":
            s = max(0.1, s * 0.7)  # Приглушаем
            v = max(0.2, v * 0.8)
        elif mood == "joyful":
            s = min(1.0, s * 1.2)
            v = min(1.0, v * 1.1)
        elif mood == "mysterious":
            v = max(0.2, v * 0.6)  # Темнее
            s = min(1.0, s * 1.1)
        
        return self.hsv_to_rgb(h, s, v)
    
    def get_color_temperature(self, color: Tuple[int, int, int]) -> str:
        """Определяет температуру цвета"""
        r, g, b = color
        if r > b:
            return "warm"
        elif b > r:
            return "cool"
        else:
            return "neutral"
    
    def get_color_emotion(self, color: Tuple[int, int, int]) -> str:
        """Определяет эмоцию цвета"""
        h, s, v = self.rgb_to_hsv(*color)
        
        if s < 0.2:
            return "neutral"
        elif v < 0.3:
            return "dark"
        elif h < 0.08:
            return "passion"  # Красный
        elif h < 0.15:
            return "energy"   # Оранжевый
        elif h < 0.3:
            return "joy"      # Жёлтый
        elif h < 0.5:
            return "calm"     # Зелёный
        elif h < 0.65:
            return "trust"    # Синий
        elif h < 0.8:
            return "creativity"  # Фиолетовый
        else:
            return "romance"  # Розовый
    
    def apply_color_grading(self, img, style="cinematic"):
        """Цветокоррекция - wrapper для rendering techniques"""
        from ayiko.rendering_techniques import AyikoRenderingTechniques
        tech = AyikoRenderingTechniques()
        return tech.apply_color_grading(img, style)


if __name__ == "__main__":
    import random
    color_theory = AyikoColorTheory()
    
    print("\n=== ТЕСТ ЦВЕТОВОЙ ТЕОРИИ ===\n")
    
    test_color = (200, 100, 50)
    print(f"Базовый цвет: {test_color}")
    
    print("\nКомплементарный:")
    comp = color_theory.get_complementary(test_color)
    print(f"   {comp}")
    
    print("\nАналоговые:")
    analog = color_theory.get_analogous(test_color)
    for c in analog:
        print(f"   {c}")
    
    print("\nТриадные:")
    triadic = color_theory.get_triadic(test_color)
    for c in triadic:
        print(f"   {c}")
    
    print("\nПалитра по настроению 'warm':")
    warm_palette = color_theory.generate_palette_from_mood("warm", 6)
    for c in warm_palette:
        print(f"   {c}")
    
    print(f"\nТемпература цвета {test_color}: {color_theory.get_color_temperature(test_color)}")
    print(f"Эмоция цвета {test_color}: {color_theory.get_color_emotion(test_color)}")
