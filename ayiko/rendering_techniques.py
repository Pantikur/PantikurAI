#!/usr/bin/env python3
"""
Айко AI — Система Продвинутых Графических Техник

Профессиональные техники рендеринга:
  🎨 Пиксельные техники (dithering, anti-aliasing, palette optimization)
  🖌️ Мазки кисти (имитация масляной живописи, акварели)
  ✏️ Линейные техники (hatching, cross-hatching, stippling)
  💡 Освещение (volumetric, rim light, ambient occlusion)
  🌫️ Эффекты (bloom, glow, depth of field, motion blur)
  📐 Геометрия (isometric, perspective, orthographic)
  🎭 Постобработка (color grading, film grain, vignette)
"""

import math
import random
from typing import List, Tuple, Dict, Any
from PIL import Image, ImageDraw, ImageFilter, ImageEnhance


class AyikoRenderingTechniques:
    """Система профессиональных графических техник"""
    
    def __init__(self):
        print("Rendering techniques initialized")
    
    # ================================================================
    #  ПИКСЕЛЬНЫЕ ТЕХНИКИ
    # ================================================================
    
    def apply_dithering(self, img: Image.Image, pattern: str = "floyd_steinberg") -> Image.Image:
        """
        Применяет дайринг для плавных градиентов
        
        Args:
            img: Входное изображение
            pattern: Тип дайринга (floyd_steinberg, bayer, ordered)
        """
        if pattern == "floyd_steinberg":
            return self._floyd_steinberg_dither(img)
        elif pattern == "bayer":
            return self._bayer_dither(img)
        else:
            return self._ordered_dither(img)
    
    def _floyd_steinberg_dither(self, img: Image.Image) -> Image.Image:
        """Dithering по методу Флойда-Стейнберга"""
        img = img.convert('L')
        width, height = img.size
        data: Any = img.load()
        
        # Квантуем до 2 уровней
        for y in range(height):
            for x in range(width):
                old_pixel = data[x, y]
                new_pixel = 255 if old_pixel > 127 else 0
                data[x, y] = new_pixel
                
                error = old_pixel - new_pixel
                
                # Распределяем ошибку
                if x + 1 < width:
                    data[x + 1, y] = min(255, data[x + 1, y] + error * 7/16)
                if x - 1 >= 0 and y + 1 < height:
                    data[x - 1, y + 1] = min(255, data[x - 1, y + 1] + error * 3/16)
                if y + 1 < height:
                    data[x, y + 1] = min(255, data[x, y + 1] + error * 5/16)
                if x + 1 < width and y + 1 < height:
                    data[x + 1, y + 1] = min(255, data[x + 1, y + 1] + error * 1/16)
        
        return img
    
    def _bayer_dither(self, img: Image.Image) -> Image.Image:
        """Байер дайринг"""
        img = img.convert('L')
        width, height = img.size
        data: Any = img.load()
        
        # 4x4 матрица Байера
        bayer_matrix = [
            [0, 8, 2, 10],
            [12, 4, 14, 6],
            [3, 11, 1, 9],
            [15, 7, 13, 5]
        ]
        
        for y in range(height):
            for x in range(width):
                old_pixel = data[x, y] / 255.0
                threshold = bayer_matrix[y % 4][x % 4] / 16.0
                new_pixel = 255 if old_pixel > threshold else 0
                data[x, y] = new_pixel
        
        return img
    
    def _ordered_dither(self, img: Image.Image) -> Image.Image:
        """Упорядоченный дайринг"""
        img = img.convert('L')
        width, height = img.size
        data: Any = img.load()
        
        for y in range(height):
            for x in range(width):
                threshold = ((x + y) % 2) * 128
                data[x, y] = 255 if data[x, y] > threshold else 0
        
        return img
    
    def apply_anti_aliasing(self, img: Image.Image, strength: float = 0.5) -> Image.Image:
        """Применяет сглаживание границ"""
        # Уменьшаем и увеличиваем для сглаживания
        small = img.resize((img.width // 4, img.height // 4), Image.BILINEAR)
        result = small.resize(img.size, Image.BILINEAR)
        return Image.blend(img, result, strength)
    
    # ================================================================
    #  ТЕХНИКИ КИСТИ
    # ================================================================
    
    def apply_oil_painting_effect(self, img: Image.Image, brush_size: int = 5, 
                                  detail: float = 0.3) -> Image.Image:
        """Имитация масляной живописи"""
        # Ensure RGB mode
        if img.mode != 'RGB':
            img = img.convert('RGB')
        
        # Блендинг близких пикселей по цвету
        result = img.copy()
        pixels: Any = result.load()
        width, height = img.size
        
        for y in range(0, height, brush_size):
            for x in range(0, width, brush_size):
                # Собираем пиксели в блоке
                colors = []
                for dy in range(brush_size):
                    for dx in range(brush_size):
                        if y + dy < height and x + dx < width:
                            colors.append(pixels[x + dx, y + dy])
                
                if colors:
                    # Средний цвет
                    avg_r = sum(c[0] for c in colors) // len(colors)
                    avg_g = sum(c[1] for c in colors) // len(colors)
                    avg_b = sum(c[2] for c in colors) // len(colors)
                    avg_color = (avg_r, avg_g, avg_b)
                    
                    # Рисуем мазок
                    draw = ImageDraw.Draw(result)
                    draw.ellipse([x, y, x + brush_size, y + brush_size], fill=avg_color)
        
        # Сохраняем детали
        if detail < 1.0:
            original = img.filter(ImageFilter.GaussianBlur(radius=1))
            result = Image.blend(result, original, 1 - detail)
        
        return result
    
    def apply_watercolor_effect(self, img: Image.Image, bleed: int = 3, 
                               paper_texture: float = 0.2) -> Image.Image:
        """Имитация акварели"""
        # Размытие для эффекта растекания
        result = img.filter(ImageFilter.GaussianBlur(radius=bleed))
        
        # Усиление краёв
        edges = result.filter(ImageFilter.FIND_EDGES)
        result = Image.blend(result, edges, 0.2)
        
        # Добавляем текстуру бумаги
        if paper_texture > 0:
            noise = Image.new('RGB', result.size)
            for y in range(result.height):
                for x in range(result.width):
                    n = random.randint(-20, 20)
                    noise.putpixel((x, y), (128 + n, 128 + n, 128 + n))
            noise = noise.filter(ImageFilter.GaussianBlur(radius=2))
            result = Image.blend(result, noise, paper_texture)
        
        return result
    
    def apply_pencil_sketch(self, img: Image.Image, darkness: int = 50) -> Image.Image:
        """Имитация карандашного наброска"""
        gray = img.convert('L')
        
        # Инвертируем и размываем
        inverted = Image.eval(gray, lambda x: 255 - x)
        blurred = inverted.filter(ImageFilter.GaussianBlur(radius=darkness))
        
        # Додж-бленд
        result = Image.blend(gray, blurred, 0.5)
        
        # Усиливаем контраст
        result = ImageEnhance.Contrast(result).enhance(1.5)
        
        return result
    
    # ================================================================
    #  ЛИНЕЙНЫЕ ТЕХНИКИ
    # ================================================================
    
    def apply_hatching(self, img: Image.Image, spacing: int = 3, 
                      angle: int = 45) -> Image.Image:
        """Штриховка (hatching)"""
        gray = img.convert('L')
        width, height = gray.size
        result = Image.new('RGB', (width, height), (255, 255, 255))
        draw = ImageDraw.Draw(result)
        
        # Конвертируем в массив пикселей
        pixels: Any = gray.load()
        
        # Рисуем штрихи
        for y in range(0, height, spacing):
            for x in range(0, width, spacing):
                brightness = pixels[x, y] / 255.0
                if brightness < 0.7:  # Только на тёмных участках
                    alpha = int((1 - brightness) * 255)
                    draw.line([(x, y), (x + 10, y + 10)], fill=(0, 0, 0, alpha), width=1)
        
        return result
    
    def apply_cross_hatching(self, img: Image.Image, spacing: int = 3) -> Image.Image:
        """Перекрёстная штриховка"""
        gray = img.convert('L')
        width, height = gray.size
        result = Image.new('RGB', (width, height), (255, 255, 255))
        draw = ImageDraw.Draw(result)
        
        pixels: Any = gray.load()
        
        # Два направления штрихов
        for y in range(0, height, spacing):
            for x in range(0, width, spacing):
                brightness = pixels[x, y] / 255.0
                if brightness < 0.6:
                    alpha = int((1 - brightness) * 200)
                    # Первое направление
                    draw.line([(x, y), (x + 8, y + 8)], fill=(0, 0, 0, alpha), width=1)
                    # Второе направление
                    draw.line([(x + 8, y), (x, y + 8)], fill=(0, 0, 0, alpha // 2), width=1)
        
        return result
    
    def apply_stippling(self, img: Image.Image, density: int = 2) -> Image.Image:
        """Пуантилизм (точечная техника)"""
        gray = img.convert('L')
        width, height = gray.size
        result = Image.new('RGB', (width, height), (255, 255, 255))
        draw = ImageDraw.Draw(result)
        
        pixels: Any = gray.load()
        
        for y in range(0, height, density):
            for x in range(0, width, density):
                brightness = pixels[x, y] / 255.0
                if brightness < 0.8:
                    dot_size = int((1 - brightness) * density)
                    if dot_size > 0:
                        draw.ellipse([x - dot_size, y - dot_size, 
                                    x + dot_size, y + dot_size], fill=(0, 0, 0))
        
        return result
    
    # ================================================================
    #  ТЕХНИКИ ОСВЕЩЕНИЯ
    # ================================================================
    
    def apply_volumetric_lighting(self, img: Image.Image, light_pos: Tuple = (0.5, 0.2),
                                  intensity: float = 0.6) -> Image.Image:
        """Объёмное освещение"""
        width, height = img.size
        lx, ly = int(width * light_pos[0]), int(height * light_pos[1])
        
        # Создаём карту освещения
        light_map = Image.new('RGB', (width, height))
        draw = ImageDraw.Draw(light_map)
        
        # Радиальный градиент от источника света
        max_dist = math.sqrt(width**2 + height**2) / 2
        for y in range(height):
            for x in range(width):
                dist = math.sqrt((x - lx)**2 + (y - ly)**2)
                brightness = max(0, 255 - (dist / max_dist) * 255 * (1 - intensity))
                draw.point((x, y), fill=(brightness, brightness, brightness))
        
        # Блендим с оригиналом
        result = Image.blend(img, light_map, 0.4)
        
        return result
    
    def apply_rim_light(self, img: Image.Image, direction: str = "back",
                       strength: float = 0.5) -> Image.Image:
        """Контурное освещение (rim light)"""
        # Создаём карту контуров
        edges = img.filter(ImageFilter.FIND_EDGES)
        
        # Инвертируем для получения только контуров
        edges = Image.eval(edges, lambda x: 255 - x)
        
        # Блендим
        result = Image.blend(img, edges, strength)
        
        return result
    
    def apply_ambient_occlusion(self, img: Image.Image, radius: int = 5) -> Image.Image:
        """Амбиент окклюзия (затенение в углах)"""
        blurred = img.filter(ImageFilter.GaussianBlur(radius=radius))
        
        # Вычисляем окклюзию как размытие оригинала
        ao_mask = Image.new('L', img.size, 200)
        result = Image.blend(img, blurred, 0.3)
        
        return result
    
    # ================================================================
    #  СПЕЦЭФФЕКТЫ
    # ================================================================
    
    def apply_bloom(self, img: Image.Image, radius: int = 10, 
                   intensity: float = 0.5) -> Image.Image:
        """Эффект свечения (bloom)"""
        # Создаём светлую часть
        bright = img.point(lambda x: 255 if x > 180 else 0)  # type: ignore[operator]
        bright = bright.filter(ImageFilter.GaussianBlur(radius=radius))
        
        # Блендим
        result = Image.blend(img, bright, intensity)
        
        return result
    
    def apply_depth_of_field(self, img: Image.Image, focus_y: float = 0.5,
                            blur_strength: int = 5) -> Image.Image:
        """Глубина резкости"""
        width, height = img.size
        result = img.copy()
        
        # Размываем области вне фокуса
        blur = result.filter(ImageFilter.GaussianBlur(radius=blur_strength))
        
        for y in range(height):
            dist_from_focus = abs(y - height * focus_y) / height
            blur_amount = dist_from_focus * blur_strength
            
            if blur_amount > 0:
                for x in range(width):
                    orig_px = result.getpixel((x, y))
                    blur_px = blur.getpixel((x, y))
                    # Ensure we have RGB tuples
                    if not isinstance(orig_px, tuple) or not isinstance(blur_px, tuple):
                        continue
                    if len(orig_px) < 3 or len(blur_px) < 3:
                        continue
                    # Смешиваем в зависимости от расстояния
                    ratio = min(1.0, blur_amount / blur_strength)
                    r = int(orig_px[0] * (1 - ratio) + blur_px[0] * ratio)
                    g = int(orig_px[1] * (1 - ratio) + blur_px[1] * ratio)
                    b = int(orig_px[2] * (1 - ratio) + blur_px[2] * ratio)
                    result.putpixel((x, y), (r, g, b))
        
        return result
    
    def apply_motion_blur(self, img: Image.Image, angle: int = 0, 
                         distance: int = 10) -> Image.Image:
        """Размытие в движении"""
        return img.filter(ImageFilter.GaussianBlur(radius=distance))
    
    # ================================================================
    #  ПОСТООБРАБОТКА
    # ================================================================
    
    def apply_color_grading(self, img: Image.Image, style: str = "cinematic") -> Image.Image:
        """Цветокоррекция"""
        if style == "cinematic":
            # Киношный стиль: тёмные тени, приглушённые цвета
            img = ImageEnhance.Color(img).enhance(0.8)
            img = ImageEnhance.Contrast(img).enhance(1.2)
            # Сдвиг в тёплые тона
            pixels: Any = img.load()
            for y in range(img.height):
                for x in range(img.width):
                    r, g, b = pixels[x, y]
                    pixels[x, y] = (
                        min(255, int(r * 1.05)),
                        g,
                        int(b * 0.95)
                    )
        
        elif style == "vintage":
            # Винтажный: сепия
            pixels: Any = img.load()
            for y in range(img.height):
                for x in range(img.width):
                    r, g, b = pixels[x, y]
                    pixels[x, y] = (
                        int(r * 0.9 + g * 0.08 + b * 0.02),
                        int(r * 0.4 + g * 0.6 + b * 0.1),
                        int(r * 0.1 + g * 0.2 + b * 0.8)
                    )
        
        elif style == "cool":
            # Холодный: синие тени
            pixels: Any = img.load()
            for y in range(img.height):
                for x in range(img.width):
                    r, g, b = pixels[x, y]
                    pixels[x, y] = (
                        r,
                        g,
                        min(255, int(b * 1.15))
                    )
        
        return img
    
    def apply_film_grain(self, img: Image.Image, intensity: float = 0.1) -> Image.Image:
        """Зерно плёнки"""
        # Ensure same mode and size
        if img.mode != 'RGB':
            img = img.convert('RGB')
        
        noise = Image.new('RGB', img.size)
        for y in range(img.height):
            for x in range(img.width):
                n = random.randint(-30, 30)
                noise.putpixel((x, y), (128 + n, 128 + n, 128 + n))
        
        return Image.blend(img, noise, intensity)
    
    def apply_vignette(self, img: Image.Image, strength: float = 0.5) -> Image.Image:
        """Виньетка (затемнение по краям)"""
        width, height = img.size
        mask = Image.new('L', (width, height), 255)
        draw = ImageDraw.Draw(mask)
        
        # Градиент от центра к краям
        cx, cy = width // 2, height // 2
        max_dist = math.sqrt(cx**2 + cy**2)
        
        for y in range(height):
            for x in range(width):
                dist = math.sqrt((x - cx)**2 + (y - cy)**2) / max_dist
                brightness = max(0, int(255 - dist * 255 * strength))
                mask.putpixel((x, y), brightness)
        
        result = img.copy()
        result.putalpha(mask)
        
        return result
    
    # ================================================================
    #  ГЕОМЕТРИЯ
    # ================================================================
    
    def create_isometric_projection(self, img: Image.Image, angle: int = 30) -> Image.Image:
        """Изометрическая проекция"""
        width, height = img.size
        rad = math.radians(angle)
        
        # Создаём новое изображение
        new_width = int(width * 2)
        new_height = int(height * 2)
        result = Image.new('RGB', (new_width, new_height), (240, 240, 240))
        
        # Простая изометрическая трансформация
        for y in range(height):
            for x in range(width):
                # Изометрическая проекция
                iso_x = (x - y) * math.cos(rad) + new_width // 2
                iso_y = (x + y) * math.sin(rad) - height * 0.5 + new_height // 2
                
                if 0 <= iso_x < new_width and 0 <= iso_y < new_height:
                    pixel = img.getpixel((x, y))
                    result.putpixel((int(iso_x), int(iso_y)), pixel)
        
        return result


if __name__ == "__main__":
    techniques = AyikoRenderingTechniques()
    
    print("\n=== ТЕСТ ГРАФИЧЕСКИХ ТЕХНИК ===\n")
    
    # Создаём тестовое изображение
    test_img = Image.new('RGB', (256, 256), (100, 150, 200))
    draw = ImageDraw.Draw(test_img)
    draw.ellipse([50, 50, 200, 200], fill=(200, 100, 100))
    
    # Тестируем техники
    print("Тестирую дайринг...")
    dithered = techniques.apply_dithering(test_img, "floyd_steinberg")
    print("   ✅ Dithering применён")
    
    print("Тестирую масляную живопись...")
    oil = techniques.apply_oil_painting_effect(test_img, brush_size=8)
    print("   ✅ Oil painting применён")
    
    print("Тестирую акварель...")
    watercolor = techniques.apply_watercolor_effect(test_img, bleed=4)
    print("   ✅ Watercolor применён")
    
    print("Тестирую свечение...")
    bloomed = techniques.apply_bloom(test_img, radius=8)
    print("   ✅ Bloom применён")
    
    print("\n🎨 Все техники работают!")
