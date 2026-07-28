#!/usr/bin/env python3
"""
Айко AI — Система Композиции и Золотого Сечения

Использует:
  📐 Правило третей
  ✨ Золотое сечение (phi = 1.618)
  🔺 Золотая спираль
  ⚖️ Баланс и симметрия
  🌀 Динамическое равновесие
  📊 Анализ композиции
"""

import math
from typing import Tuple, Dict, List
from PIL import Image, ImageDraw


GOLDEN_RATIO = 1.618033988749
GOLDEN_ANGLE = 137.508  # degrees


class AyikoComposition:
    """Профессиональная система композиции"""
    
    def __init__(self):
        print("Composition system initialized")
    
    # ================================================================
    #  ЗОЛОТОЕ СЕЧЕНИЕ
    # ================================================================
    
    def golden_divide(self, length: float) -> Tuple[float, float]:
        """Делит длину по золотому сечению"""
        short = length / GOLDEN_RATIO
        long = length - short
        return (long, short)
    
    def golden_ratio_point(self, width: int, height: int) -> Tuple[int, int]:
        """Вычисляет точку золотого сечения"""
        gw, _ = self.golden_divide(width)
        _, gh = self.golden_divide(height)
        return (int(gw), int(gh))
    
    def get_golden_rectangles(self, width: int, height: int, 
                            depth: int = 3) -> List[Tuple[int, int, int, int]]:
        """Получает вложенные золотые прямоугольники"""
        rectangles = []
        w, h = width, height
        x, y = 0, 0
        
        for i in range(depth):
            rectangles.append((x, y, w, h))
            
            if w > h:
                _, short = self.golden_divide(w)
                x += short
                w -= short
            else:
                long, _ = self.golden_divide(h)
                y += long
                h -= long
        
        return rectangles
    
    # ================================================================
    #  ЗОЛОТАЯ СПИРАЛЬ
    # ================================================================
    
    def generate_golden_spiral_points(self, width: int, height: int, 
                                     points: int = 100) -> List[Tuple[int, int]]:
        """Генерирует точки золотой спирали"""
        spiral = []
        
        # Центрируем спираль
        cx, cy = width // 2, height // 2
        max_radius = min(width, height) / 2
        
        for i in range(points):
            angle = i * math.radians(GOLDEN_ANGLE)
            radius = max_radius * (1 - i / points) * 0.5
            
            x = cx + radius * math.cos(angle)
            y = cy + radius * math.sin(angle)
            
            spiral.append((int(x), int(y)))
        
        return spiral
    
    def draw_golden_spiral(self, img: Image.Image, color: Tuple = (255, 0, 0), 
                          width: int = 2) -> Image.Image:
        """Рисует золотую спираль на изображении"""
        result = img.copy()
        draw = ImageDraw.Draw(result)
        
        points = self.generate_golden_spiral_points(img.width, img.height)
        
        if len(points) > 1:
            draw.line(points, fill=color, width=width)
        
        return result
    
    # ================================================================
    #  ПРАВИЛО ТРЕТЕЙ
    # ================================================================
    
    def get_rule_of_thirds_lines(self, width: int, height: int) -> Dict:
        """Получает линии правила третей"""
        third_w = width // 3
        third_h = height // 3
        
        return {
            "vertical_lines": [third_w, 2 * third_w],
            "horizontal_lines": [third_h, 2 * third_h],
            "intersections": [
                (third_w, third_h),
                (2 * third_w, third_h),
                (third_w, 2 * third_h),
                (2 * third_w, 2 * third_h)
            ]
        }
    
    def draw_rule_of_thirds(self, img: Image.Image, color: Tuple = (255, 255, 0),
                           width: int = 1) -> Image.Image:
        """Рисует сетку правила третей"""
        result = img.copy()
        draw = ImageDraw.Draw(result)
        
        thirds = self.get_rule_of_thirds_lines(img.width, img.height)
        
        # Вертикальные
        for x in thirds["vertical_lines"]:
            draw.line([(x, 0), (x, img.height)], fill=color, width=width)
        
        # Горизонтальные
        for y in thirds["horizontal_lines"]:
            draw.line([(0, y), (img.width, y)], fill=color, width=width)
        
        return result
    
    # ================================================================
    #  БАЛАНС И СИММЕТРИЯ
    # ================================================================
    
    def calculate_visual_balance(self, img: Image.Image, 
                                weights: Dict = None) -> float:
        """
        Рассчитывает визуальный баланс изображения
        
        Args:
            img: Входное изображение
            weights: Веса для разных цветов (r, g, b)
        """
        if weights is None:
            weights = {"r": 0.299, "g": 0.587, "b": 0.114}
        
        # Конвертируем в градации серого с весами
        gray = img.convert('L')
        pixels = list(gray.getdata())
        width, height = img.size
        
        # Рассчитываем баланс левой/правой половин
        left_sum = 0
        right_sum = 0
        left_count = 0
        right_count = 0
        
        for y in range(height):
            for x in range(width):
                idx = y * width + x
                brightness = pixels[idx] / 255.0
                
                if x < width // 2:
                    left_sum += brightness
                    left_count += 1
                else:
                    right_sum += brightness
                    right_count += 1
        
        left_avg = left_sum / left_count if left_count > 0 else 0
        right_avg = right_sum / right_count if right_count > 0 else 0
        
        # Баланс: 1.0 = идеальный, <1.0 = перекос влево, >1.0 = перекос вправо
        balance = left_avg / right_avg if right_avg > 0 else 1.0
        
        return balance
    
    def analyze_symmetry(self, img: Image.Image, axis: str = "vertical") -> float:
        """
        Анализирует симметрию изображения
        
        Args:
            img: Входное изображение
            axis: Ось симметрии ('vertical' или 'horizontal')
        """
        gray = img.convert('L')
        pixels = list(gray.getdata())
        width, height = gray.size
        
        diff_sum = 0
        count = 0
        
        if axis == "vertical":
            # Вертикальная симметрия
            for y in range(height):
                for x in range(width // 2):
                    mirror_x = width - 1 - x
                    p1 = pixels[y * width + x]
                    p2 = pixels[y * width + mirror_x]
                    diff_sum += abs(p1 - p2)
                    count += 1
        
        else:
            # Горизонтальная симметрия
            for y in range(height // 2):
                for x in range(width):
                    mirror_y = height - 1 - y
                    p1 = pixels[y * width + x]
                    p2 = pixels[mirror_y * width + x]
                    diff_sum += abs(p1 - p2)
                    count += 1
        
        avg_diff = diff_sum / count if count > 0 else 255
        symmetry = max(0, 1 - avg_diff / 255)
        
        return symmetry
    
    # ================================================================
    #  ДИНАМИЧЕСКОЕ РАВНОВЕСИЕ
    # ================================================================
    
    def calculate_composition_strength(self, img: Image.Image) -> Dict:
        """
        Рассчитывает силу композиции по нескольким факторам
        """
        gray = img.convert('L')
        pixels = list(gray.getdata())
        width, height = gray.size
        
        # Контраст
        min_p = min(pixels)
        max_p = max(pixels)
        contrast = (max_p - min_p) / 255.0
        
        # Резкость (вариантность)
        mean_p = sum(pixels) / len(pixels)
        variance = sum((p - mean_p) ** 2 for p in pixels) / len(pixels)
        sharpness = min(1.0, variance / 1000)
        
        # Золотое сечение (насколько объект в золотой точке)
        golden_x, golden_y = self.golden_ratio_point(width, height)
        
        # Проверяем яркость в золотой точке
        golden_idx = golden_y * width + golden_x
        golden_brightness = pixels[golden_idx] / 255.0
        
        # Общая оценка композиции
        composition_score = (contrast * 0.4 + sharpness * 0.3 + golden_brightness * 0.3)
        
        return {
            "contrast": round(contrast, 2),
            "sharpness": round(sharpness, 2),
            "golden_point_brightness": round(golden_brightness, 2),
            "overall_score": round(composition_score, 2),
            "golden_point": (golden_x, golden_y)
        }
    
    def suggest_composition_improvements(self, img: Image.Image) -> List[str]:
        """Даёт советы по улучшению композиции"""
        suggestions = []
        
        analysis = self.calculate_composition_strength(img)
        balance = self.calculate_visual_balance(img)
        symmetry = self.analyze_symmetry(img)
        
        if analysis["contrast"] < 0.3:
            suggestions.append("⚠️ Низкий контраст — добавьте тени и блики")
        
        if analysis["sharpness"] < 0.2:
            suggestions.append("⚠️ Низкая резкость — добавьте детали и текстуры")
        
        if balance < 0.7 or balance > 1.4:
            suggestions.append("⚠️ Дисбаланс — переместите главный объект к золотой точке")
        
        if symmetry > 0.8:
            suggestions.append("ℹ️ Высокая симметрия — можно добавить асимметрию для динамики")
        
        if not suggestions:
            suggestions.append("✅ Композиция сбалансирована!")
        
        return suggestions
    
    # ================================================================
    #  ГЕНЕРАЦИЯ КОМПОЗИЦИЙ
    # ================================================================
    
    def create_golden_composition(self, width: int, height: int, 
                                 elements: List[Dict]) -> Dict:
        """
        Создаёт композицию по золотому сечению
        
        Args:
            width, height: Размер холста
            elements: Список элементов с позициями и размерами
        """
        positions = {}
        
        # Главный элемент в золотой точке
        gx, gy = self.golden_ratio_point(width, height)
        
        for i, elem in enumerate(elements):
            if i == 0:
                # Первый элемент — в золотой точке
                elem_size = elem.get("size", 100)
                positions[i] = {
                    "x": gx - elem_size // 2,
                    "y": gy - elem_size // 2,
                    "size": elem_size
                }
            else:
                # Остальные элементы — вдоль золотой спирали
                spiral_points = self.generate_golden_spiral_points(width, height, points=10)
                idx = min(i, len(spiral_points) - 1)
                elem_size = elem.get("size", 50)
                positions[i] = {
                    "x": spiral_points[idx][0] - elem_size // 2,
                    "y": spiral_points[idx][1] - elem_size // 2,
                    "size": elem_size
                }
        
        return positions


if __name__ == "__main__":
    composition = AyikoComposition()
    
    print("\n=== ТЕСТ СИСТЕМЫ КОМПОЗИЦИИ ===\n")
    
    # Тест золотого сечения
    print("Золотое разделение 1000px:")
    long, short = composition.golden_divide(1000)
    print(f"   Длинная часть: {long:.1f}px")
    print(f"   Короткая часть: {short:.1f}px")
    
    print(f"\nТочка золотого сечения для 512x512:")
    gx, gy = composition.golden_ratio_point(512, 512)
    print(f"   ({gx}, {gy})")
    
    # Тест правила третей
    thirds = composition.get_rule_of_thirds_lines(512, 512)
    print(f"\nЛинии правила третей (512x512):")
    print(f"   Вертикальные: {thirds['vertical_lines']}")
    print(f"   Горизонтальные: {thirds['horizontal_lines']}")
    print(f"   Пересечения: {thirds['intersections']}")
    
    # Тест композиции
    test_img = Image.new('RGB', (512, 512), (100, 150, 200))
    analysis = composition.calculate_composition_strength(test_img)
    print(f"\nАнализ композиции:")
    print(f"   Контраст: {analysis['contrast']}")
    print(f"   Резкость: {analysis['sharpness']}")
    print(f"   Общая оценка: {analysis['overall_score']}")
    
    suggestions = composition.suggest_composition_improvements(test_img)
    print(f"\nСоветы:")
    for s in suggestions:
        print(f"   {s}")
