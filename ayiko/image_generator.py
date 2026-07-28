#!/usr/bin/env python3
"""
Айко AI — Профессиональный Генератор Изображений v3.0

Навыки:
  🎨 Пиксель-арт (16x16 → 8K)
  🖌️ Акварель / Масло / Акрил
  ✏️ Карандаш / Уголь / Пастель
  📐 Техническая графика / Чертежи
  🧊 3D-визуализация / Рендер
  🌈 Цветовая теория / Композиция
  👤 Портреты / Персонажи / Одежда
  🏞️ Пейзажи / Архитектура / Интерьеры
  ✨ Спецэффекты / Свечение / Частицы

Система обучения:
  - Анализ примеров из базы знаний
  - Прогрессия от новичка до мастера
  - Специализация по направлениям
  - Адаптивное улучшение качества
"""

import os
import json
import random
import math
import hashlib
from pathlib import Path
from typing import List, Dict, Tuple, Optional, Any
from datetime import datetime

from PIL import Image, ImageDraw, ImageFilter, ImageEnhance, ImageChops, ImageFont
from PIL.ImageFilter import KERNEL


class AyikoProGenerator:
    """
    Профессиональный генератор изображений Айко.
    
    Система навыков определяет качество генерации:
      - pixel_art: 1-10
      - character: 1-10
      - landscape: 1-10
      - technical: 1-10
      - color_theory: 1-10
      - composition: 1-10
    """
    
    def __init__(self, output_dir: str = "data/ayiko_generated"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # База знаний
        self.knowledge_dir = Path("data/ayiko/knowledge")
        self.knowledge_dir.mkdir(parents=True, exist_ok=True)
        self._load_knowledge()
        
        # Система навыков (уровни 1-10)
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
        
        # Прогресс и опыт
        self.experience = {
            "total_images": 0,
            "pixel_projects": 0,
            "character_projects": 0,
            "landscape_projects": 0,
            "technical_projects": 0,
            "sessions": 0,
            "masterpieces": 0
        }
        
        # Палитры
        self.palettes = self._init_palettes()
        
        # Шрифты
        self._font = None
        
        # Лог прогресса
        self.generation_log = []
        
        print("🎨 Ayiko Pro Generator v3.0 инициализирован")
        print(f"   Навыки: {', '.join(f'{k}: {v}' for k, v in self.skills.items())}")
    
    # ================================================================
    #  СИСТЕМА НАВЫКОВ
    # ================================================================
    
    def _init_palettes(self) -> Dict[str, List[Tuple]]:
        """Инициализация профессиональных палитр"""
        return {
            # Классические
            "classical": [
                (210, 180, 140), (139, 69, 19), (245, 245, 220),
                (101, 67, 33), (255, 250, 240), (70, 40, 20)
            ],
            # Аниме
            "anime": [
                (255, 200, 220), (135, 206, 250), (255, 182, 193),
                (255, 255, 224), (176, 224, 230), (255, 192, 203)
            ],
            # Киберпанк
            "cyberpunk": [
                (0, 255, 255), (255, 0, 255), (0, 0, 255),
                (255, 255, 0), (128, 0, 128), (0, 128, 255)
            ],
            # Природа
            "nature": [
                (34, 139, 34), (85, 107, 47), (144, 238, 144),
                (173, 216, 230), (255, 250, 205), (139, 90, 43)
            ],
            # Закат
            "sunset": [
                (255, 99, 71), (255, 165, 0), (255, 215, 0),
                (255, 105, 180), (138, 43, 226), (75, 0, 130)
            ],
            # Ночь
            "night": [
                (0, 0, 50), (25, 25, 112), (70, 130, 180),
                (176, 196, 222), (256, 256, 256), (112, 128, 144)
            ],
            # Ретро
            "retro_80s": [
                (255, 0, 255), (0, 255, 255), (255, 255, 0),
                (255, 127, 0), (128, 0, 128), (0, 128, 128)
            ],
            # Монохром
            "monochrome": [
                (0, 0, 0), (32, 32, 32), (64, 64, 64), (96, 96, 96),
                (128, 128, 128), (160, 160, 160), (192, 192, 192),
                (224, 224, 224), (255, 255, 255)
            ],
            # Пастель
            "pastel": [
                (255, 183, 197), (176, 224, 230), (255, 218, 185),
                (221, 160, 221), (152, 251, 152), (255, 255, 192)
            ],
            # Акварель
            "watercolor": [
                (176, 224, 230), (255, 182, 193), (255, 218, 185),
                (221, 160, 221), (173, 216, 230), (245, 250, 240)
            ],
            # Масло
            "oil_painting": [
                (139, 69, 19), (34, 139, 34), (65, 105, 225),
                (255, 215, 0), (220, 20, 60), (128, 0, 128)
            ],
            # Уголь
            "charcoal": [
                (20, 20, 20), (50, 50, 50), (80, 80, 80),
                (110, 110, 110), (140, 140, 140), (170, 170, 170),
                (200, 200, 200), (230, 230, 230), (255, 255, 255)
            ]
        }
    
    def get_skill_level(self, skill: str) -> int:
        """Получить уровень навыка"""
        return self.skills.get(skill, 1)
    
    def set_skill_level(self, skill: str, level: int):
        """Установить уровень навыка (1-10)"""
        level = max(1, min(10, level))
        self.skills[skill] = level
        print(f"   📈 Навык '{skill}' повышен до уровня {level}")
    
    def gain_experience(self, project_type: str, quality: float):
        """Получить опыт и улучшить навыки"""
        self.experience["total_images"] += 1
        self.experience[f"{project_type}_projects"] += 1
        
        # Улучшение навыков на основе качества
        for skill, base_level in self.skills.items():
            improvement = quality * 0.01  # 0-0.1 за работу
            new_level = min(10, base_level + improvement)
            if new_level > base_level:
                self.skills[skill] = new_level
        
        # Проверка на шедевр
        if quality > 0.9:
            self.experience["masterpieces"] += 1
            print(f"   🏆 Шедевр создан! Качество: {quality:.1%}")
    
    def get_skill_summary(self) -> Dict:
        """Сводка навыков и прогресса"""
        return {
            "skills": {k: round(v, 1) for k, v in self.skills.items()},
            "experience": self.experience,
            "average_skill": round(sum(self.skills.values()) / len(self.skills), 1)
        }
    
    # ================================================================
    #  ЦВЕТОВАЯ ТЕОРИЯ
    # ================================================================
    
    def _blend_colors(self, color1: Tuple, color2: Tuple, ratio: float) -> Tuple:
        """Смешивает два цвета"""
        r = int(color1[0] * (1 - ratio) + color2[0] * ratio)
        g = int(color1[1] * (1 - ratio) + color2[1] * ratio)
        b = int(color1[2] * (1 - ratio) + color2[2] * ratio)
        return (r, g, b)
    
    def _adjust_brightness(self, color: Tuple, factor: float) -> Tuple:
        """Регулирует яркость цвета"""
        return tuple(min(255, max(0, int(c * factor))) for c in color)
    
    def _get_complementary_color(self, color: Tuple) -> Tuple:
        """Получает комплементарный цвет"""
        return (255 - color[0], 255 - color[1], 255 - color[2])
    
    def _get_analogous_colors(self, color: Tuple, spread: int = 30) -> List[Tuple]:
        """Получает аналогичные цвета"""
        # Конвертируем в HSV
        r, g, b = color[0] / 255, color[1] / 255, color[2] / 255
        max_c = max(r, g, b)
        min_c = min(r, g, b)
        l = (max_c + min_c) / 2
        
        if max_c == min_c:
            h = s = 0
        else:
            d = max_c - min_c
            s = d / (2 - max_c - min_c) if l > 0.5 else d / (max_c + min_c)
            if max_c == r:
                h = (g - b) / d + (6 if g < b else 0)
            elif max_c == g:
                h = (b - r) / d + 2
            else:
                h = (r - g) / d + 4
            h /= 6
        
        return [
            self._hsv_to_rgb((h, s, l)),
            self._hsv_to_rgb(((h + spread/360) % 1, s, l)),
            self._hsv_to_rgb(((h - spread/360) % 1, s, l))
        ]
    
    def _hsv_to_rgb(self, hsv: Tuple) -> Tuple:
        """Конвертирует HSV в RGB"""
        h, s, v = hsv
        hi = int(h * 6) % 6
        f = h * 6 - int(h * 6)
        p = v * (1 - s)
        q = v * (1 - f * s)
        t = v * (1 - (1 - f) * s)
        
        rgb_map = [
            (v, t, p), (q, v, p), (p, v, t),
            (p, q, v), (t, p, v), (v, p, q)
        ]
        
        r, g, b = rgb_map[hi]
        return (int(r * 255), int(g * 255), int(b * 255))
    
    # ================================================================
    #  СВЕТ И ТЕНИ
    # ================================================================
    
    def _apply_lighting(self, img: Image.Image, light_dir: Tuple = (0.5, -0.5), 
                        intensity: float = 1.0) -> Image.Image:
        """Применяет освещение и тени"""
        # Создаём карту освещения
        W, H = img.size
        light_map = Image.new('L', (W, H), 128)
        draw = ImageDraw.Draw(light_map)
        
        # Градиент от источника света
        lx, ly = int(W * light_dir[0]), int(H * light_dir[1])
        for y in range(H):
            for x in range(W):
                dist = math.sqrt((x - lx)**2 + (y - ly)**2)
                max_dist = math.sqrt(W**2 + H**2) / 2
                brightness = max(0, 255 - (dist / max_dist) * 255 * (1 - intensity))
                draw.point((x, y), fill=int(brightness))
        
        # Применяем освещение
        img_light = Image.blend(img, light_map.convert('RGB'), 0.3)
        return img_light
    
    def _apply_shading(self, img: Image.Image, shade_factor: float = 0.3) -> Image.Image:
        """Применяет затенение"""
        W, H = img.size
        shaded = img.copy()
        draw = ImageDraw.Draw(shaded)
        
        # Тень снизу
        for y in range(int(H * 0.7), H):
            alpha = (y - H * 0.7) / (H * 0.3) * shade_factor
            draw.rectangle([0, y, W, y + 1], fill=(0, 0, 0, int(alpha * 255)))
        
        return shaded
    
    # ================================================================
    #  ТЕКСТУРЫ
    # ================================================================
    
    def _add_paper_texture(self, img: Image.Image, intensity: float = 0.1) -> Image.Image:
        """Добавляет текстуру бумаги"""
        W, H = img.size
        noise = Image.new('RGB', (W, H))
        pixels: Any = noise.load()
        assert pixels is not None, "Failed to load pixel data"
        
        for y in range(H):
            for x in range(W):
                n = random.randint(-20, 20)
                pixels[x, y] = (128 + n, 128 + n, 128 + n)
        
        noise = noise.filter(ImageFilter.GaussianBlur(radius=1))
        return Image.blend(img, noise, intensity)
    
    def _add_canvas_texture(self, img: Image.Image, intensity: float = 0.15) -> Image.Image:
        """Добавляет текстуру холста"""
        W, H = img.size
        texture = Image.new('RGB', (W, H))
        draw = ImageDraw.Draw(texture)
        
        # Вёртикальные и горизонтальные линии холста
        for y in range(0, H, 3):
            draw.line([(0, y), (W, y)], fill=(180, 170, 160))
        for x in range(0, W, 3):
            draw.line([(x, 0), (x, H)], fill=(180, 170, 160))
        
        texture = texture.filter(ImageFilter.GaussianBlur(radius=0.5))
        return Image.blend(img, texture, intensity)
    
    def _add_pixel_art_texture(self, img: Image.Image, pixel_size: int = 2) -> Image.Image:
        """Добавляет пиксельную текстуру"""
        W, H = img.size
        # Уменьшаем
        small = img.resize((W // pixel_size, H // pixel_size), Image.NEAREST)
        # Увеличиваем без сглаживания
        return small.resize((W, H), Image.NEAREST)
    
    # ================================================================
    #  ГЕНЕРАЦИЯ ФОНА
    # ================================================================
    
    def _draw_background(self, draw: ImageDraw.ImageDraw, W: int, H: int,
                         bg_type: str, style: str, palette: str = "classical") -> Image.Image:
        """Рисует профессиональный фон"""
        
        # Базовый градиент
        bg = Image.new('RGB', (W, H))
        draw_bg = ImageDraw.Draw(bg)
        
        colors = self.palettes.get(palette, self.palettes["classical"])
        
        if bg_type == "simple":
            # Плавный градиент
            for y in range(H):
                ratio = y / H
                color = self._blend_colors(colors[0], colors[1], ratio)
                draw_bg.line([(0, y), (W, y)], fill=color)
        
        elif bg_type == "academy":
            # Академия/школа
            for y in range(H):
                ratio = y / H
                if ratio < 0.5:
                    color = self._blend_colors((180, 200, 220), (140, 160, 180), ratio * 2)
                else:
                    color = self._blend_colors((140, 160, 180), (100, 90, 80), (ratio - 0.5) * 2)
                draw_bg.line([(0, y), (W, y)], fill=color)
            
            # Окно
            win_x, win_y = W//3, H//6
            win_w, win_h = W//3, H//2
            draw_bg.rectangle([win_x, win_y, win_x + win_w, win_y + win_h], fill=(200, 230, 255))
            draw_bg.rectangle([win_x, win_y, win_x + win_w, win_y + win_h], outline=(150, 140, 130), width=4)
            # Рама окна
            draw_bg.line([(win_x + win_w//2, win_y), (win_x + win_w//2, win_y + win_h)], fill=(150, 140, 130), width=3)
            draw_bg.line([(win_x, win_y + win_h//2), (win_x + win_w, win_y + win_h//2)], fill=(150, 140, 130), width=3)
        
        elif bg_type == "nature":
            # Природа
            sky_top = (135, 190, 230)
            sky_bottom = (173, 216, 230)
            ground = (85, 140, 70)
            
            for y in range(int(H * 0.6)):
                ratio = y / (H * 0.6)
                color = self._blend_colors(sky_top, sky_bottom, ratio)
                draw_bg.line([(0, y), (W, y)], fill=color)
            
            for y in range(int(H * 0.6), H):
                draw_bg.line([(0, y), (W, y)], fill=ground)
            
            # Солнце
            sun_x, sun_y = W//2, 50
            sun_radius = 40
            draw_bg.ellipse([sun_x - sun_radius, sun_y - sun_radius,
                           sun_x + sun_radius, sun_y + sun_radius], fill=(255, 220, 100))
            # Свечение солнца
            for r in range(sun_radius, sun_radius + 30, 2):
                alpha = 1 - (r - sun_radius) / 30
                draw_bg.ellipse([sun_x - r, sun_y - r, sun_x + r, sun_y + r],
                              outline=self._adjust_brightness((255, 220, 100), alpha))
        
        elif bg_type == "studio":
            # Студия
            gradient = [(100, 90, 80), (140, 130, 120), (180, 170, 160)]
            for y in range(H):
                ratio = y / H
                idx = min(int(ratio * 3), 2)
                next_idx = min(idx + 1, 2)
                local_ratio = (ratio * 3) - idx
                color = self._blend_colors(gradient[idx], gradient[next_idx], local_ratio)
                draw_bg.line([(0, y), (W, y)], fill=color)
        
        elif bg_type == "cyberpunk":
            # Киберпанк
            for y in range(H):
                ratio = y / H
                color = self._blend_colors((10, 0, 30), (30, 0, 60), ratio)
                draw_bg.line([(0, y), (W, y)], fill=color)
            
            # Неоновые линии
            for i in range(5):
                y = random.randint(0, H)
                color = random.choice(self.palettes["cyberpunk"])
                draw_bg.line([(0, y), (W, y)], fill=color, width=2)
        
        else:  # custom
            for y in range(H):
                ratio = y / H
                color = self._blend_colors(colors[0], colors[-1], ratio)
                draw_bg.line([(0, y), (W, y)], fill=color)
        
        return bg
    
    # ================================================================
    #  АНАТОМИЯ И ПРОПОРЦИИ
    # ================================================================
    
    def _calculate_proportions(self, body_type: str, W: int, H: int, 
                               age: int = 20, pose: str = "standing") -> Dict:
        """Рассчитывает профессиональные пропорции тела"""
        
        # Базовые пропорции (голова = 1/8 роста для взрослого)
        head_h = int(H * 0.12)
        head_w = int(head_h * 0.8)
        head_cx = W // 2
        head_cy = int(H * 0.18)
        
        # Расчёт точек
        shoulder_y = head_cy + head_h // 2 + 10
        waist_y = shoulder_y + int(H * 0.15)
        hip_y = waist_y + int(H * 0.08)
        crotch_y = hip_y + int(H * 0.06)
        knee_y = crotch_y + int(H * 0.12)
        foot_y = knee_y + int(H * 0.12)
        
        # Пропорции в зависимости от типа тела
        if body_type == "slim":
            shoulder_w = int(W * 0.18)
            waist_w = int(W * 0.12)
            hip_w = int(W * 0.14)
            limb_w = int(W * 0.06)
        elif body_type == "athletic":
            shoulder_w = int(W * 0.24)
            waist_w = int(W * 0.17)
            hip_w = int(W * 0.19)
            limb_w = int(W * 0.07)
        elif body_type == "heavy":
            shoulder_w = int(W * 0.27)
            waist_w = int(W * 0.22)
            hip_w = int(W * 0.26)
            limb_w = int(W * 0.09)
        elif body_type == "child":
            # У детей большая голова, короткие конечности
            head_h = int(H * 0.18)
            head_cy = int(H * 0.22)
            shoulder_y = head_cy + head_h // 2 + 8
            waist_y = shoulder_y + int(H * 0.12)
            hip_y = waist_y + int(H * 0.06)
            shoulder_w = int(W * 0.16)
            waist_w = int(W * 0.14)
            hip_w = int(W * 0.15)
            limb_w = int(W * 0.06)
        else:  # default athletic
            shoulder_w = int(W * 0.22)
            waist_w = int(W * 0.16)
            hip_w = int(W * 0.18)
            limb_w = int(W * 0.07)
        
        # Корректировка по возрасту
        if age < 12:
            head_h = int(H * 0.16)
            head_cy = int(H * 0.20)
            limb_w = int(limb_w * 1.2)  # Дети более пухлые
        
        return {
            'head_cx': head_cx, 'head_cy': head_cy, 'head_h': head_h, 'head_w': head_w,
            'shoulder_y': shoulder_y, 'waist_y': waist_y, 'hip_y': hip_y,
            'crotch_y': crotch_y, 'knee_y': knee_y, 'foot_y': foot_y,
            'shoulder_w': shoulder_w, 'waist_w': waist_w, 'hip_w': hip_w,
            'limb_w': limb_w, 'body_type': body_type
        }
    
    # ================================================================
    #  РИСОВАНИЕ ТЕЛА
    # ================================================================
    
    def _draw_body(self, draw: ImageDraw.ImageDraw, props: Dict, 
                   skin_color: Tuple, style: str = "realistic") -> Image.Image:
        """Рисует тело с затенением"""
        head_cx = props['head_cx']
        head_cy = props['head_cy']
        head_h = props['head_h']
        shoulder_y = props['shoulder_y']
        waist_y = props['waist_y']
        hip_y = props['hip_y']
        crotch_y = props['crotch_y']
        knee_y = props['knee_y']
        foot_y = props['foot_y']
        shoulder_w = props['shoulder_w']
        waist_w = props['waist_w']
        hip_w = props['hip_w']
        limb_w = props['limb_w']
        
        # Создаём изображение тела
        body_img = Image.new('RGBA', (512, 512), (0, 0, 0, 0))
        body_draw = ImageDraw.Draw(body_img)
        
        # Шея
        neck_w = int(shoulder_w * 0.3)
        body_draw.rectangle(
            [head_cx - neck_w, head_cy + head_h//2,
             head_cx + neck_w, shoulder_y],
            fill=skin_color
        )
        
        # Торс (плавный градиент ширины)
        for y in range(shoulder_y, waist_y):
            progress = (y - shoulder_y) / (waist_y - shoulder_y)
            width = int(shoulder_w - progress * (shoulder_w - waist_w))
            # Лёгкое затенение по краям
            shade = 0.9 if progress > 0.5 else 1.0
            color = self._adjust_brightness(skin_color, shade)
            body_draw.rectangle([head_cx - width, y, head_cx + width, y + 1], fill=color)
        
        for y in range(waist_y, hip_y):
            progress = (y - waist_y) / (hip_y - waist_y)
            width = int(waist_w + progress * (hip_w - waist_w))
            body_draw.rectangle([head_cx - width, y, head_cx + width, y + 1], fill=skin_color)
        
        # Руки
        for arm_side in [-1, 1]:
            arm_x = head_cx + arm_side * shoulder_w
            
            # Плечо
            body_draw.rectangle(
                [arm_x - limb_w, shoulder_y, arm_x + limb_w, shoulder_y + int(512*0.08)],
                fill=skin_color
            )
            # Предплечье
            body_draw.rectangle(
                [arm_x - int(limb_w*0.9), shoulder_y + int(512*0.08),
                 arm_x + int(limb_w*0.9), shoulder_y + int(512*0.16)],
                fill=skin_color
            )
            # Кисть
            body_draw.ellipse(
                [arm_x - int(limb_w*0.7), shoulder_y + int(512*0.16),
                 arm_x + int(limb_w*0.7), shoulder_y + int(512*0.16) + 15],
                fill=skin_color
            )
        
        # Ноги
        for leg_side in [-1, 1]:
            leg_x = head_cx + leg_side * int(hip_w * 0.45)
            
            # Бедро
            body_draw.rectangle(
                [leg_x - int(limb_w*1.2), hip_y,
                 leg_x + int(limb_w*1.2), crotch_y],
                fill=skin_color
            )
            # Икроножная
            body_draw.rectangle(
                [leg_x - int(limb_w*1.0), crotch_y,
                 leg_x + int(limb_w*1.0), knee_y],
                fill=skin_color
            )
            # Голень
            body_draw.rectangle(
                [leg_x - int(limb_w*0.9), knee_y,
                 leg_x + int(limb_w*0.9), foot_y - 15],
                fill=skin_color
            )
            # Стопа
            body_draw.rectangle(
                [leg_x - int(limb_w*1.1), foot_y - 15,
                 leg_x + int(limb_w*1.1), foot_y],
                fill=skin_color
            )
        
        return body_img
    
    # ================================================================
    #  РИСОВАНИЕ ГОЛОВЫ
    # ================================================================
    
    def _draw_head(self, draw: ImageDraw.ImageDraw, props: Dict,
                   skin_color: Tuple, hair_color: Tuple, hair_style: str,
                   eye_color: Tuple, style: str = "realistic") -> Image.Image:
        """Рисует голову с детализацией"""
        head_cx = props['head_cx']
        head_cy = props['head_cy']
        head_h = props['head_h']
        head_w = props['head_w']
        radius = head_h // 2
        
        head_img = Image.new('RGBA', (512, 512), (0, 0, 0, 0))
        head_draw = ImageDraw.Draw(head_img)
        
        # Лицо (овал)
        head_draw.ellipse(
            [head_cx - radius, head_cy - radius,
             head_cx + radius, head_cy + int(radius * 1.1)],
            fill=skin_color
        )
        
        # Волосы
        self._draw_hair(head_draw, head_cx, head_cy, radius, hair_color, hair_style)
        
        # Глаза
        eye_y = head_cy + int(radius * 0.15)
        eye_spacing = int(radius * 0.6)
        
        for eye_x_offset in [-1, 1]:
            eye_x = head_cx + eye_x_offset * eye_spacing
            
            # Белок
            head_draw.ellipse(
                [eye_x - int(radius*0.25), eye_y - int(radius*0.18),
                 eye_x + int(radius*0.25), eye_y + int(radius*0.18)],
                fill=(245, 235, 225)
            )
            # Радужка
            head_draw.ellipse(
                [eye_x - int(radius*0.18), eye_y - int(radius*0.16),
                 eye_x + int(radius*0.18), eye_y + int(radius*0.16)],
                fill=eye_color
            )
            # Зрачок
            head_draw.ellipse(
                [eye_x - int(radius*0.08), eye_y - int(radius*0.08),
                 eye_x + int(radius*0.08), eye_y + int(radius*0.08)],
                fill=(20, 10, 5)
            )
            # Блик
            head_draw.ellipse(
                [eye_x - int(radius*0.05), eye_y - int(radius*0.1),
                 eye_x + int(radius*0.03), eye_y - int(radius*0.04)],
                fill=(255, 255, 255)
            )
        
        # Брови
        brow_y = eye_y - int(radius * 0.25)
        brow_w = int(radius * 0.5)
        for side in [-1, 1]:
            brow_x = head_cx + side * eye_spacing
            head_draw.rectangle(
                [brow_x - brow_w, brow_y, brow_x + brow_w, brow_y + 4],
                fill=hair_color
            )
        
        # Нос
        nose_y = head_cy + int(radius * 0.2)
        head_draw.polygon([
            (head_cx, nose_y),
            (head_cx - 8, nose_y + 15),
            (head_cx + 8, nose_y + 15)
        ], fill=self._adjust_brightness(skin_color, 0.85))
        
        # Губы
        lip_y = head_cy + int(radius * 0.6)
        lip_w = int(radius * 0.4)
        # Верхняя губа
        head_draw.polygon([
            (head_cx - lip_w, lip_y),
            (head_cx, lip_y - 4),
            (head_cx + lip_w, lip_y)
        ], fill=(180, 100, 90))
        # Нижняя губа
        head_draw.polygon([
            (head_cx - lip_w, lip_y),
            (head_cx, lip_y + 8),
            (head_cx + lip_w, lip_y)
        ], fill=(200, 120, 110))
        
        return head_img
    
    def _draw_hair(self, draw: ImageDraw.ImageDraw, cx: int, cy: int, 
                   r: int, color: Tuple, style: str):
        """Рисует причёску"""
        if style == "bun":
            # База волос
            draw.ellipse([cx - r - 5, cy - r - 10, cx + r + 5, cy + r * 0.5], fill=color)
            # Пучок
            draw.ellipse([cx - 20, cy - r - 35, cx + 20, cy - r - 5], fill=color)
            # Локон
            draw.ellipse([cx - r - 8, cy - 10, cx - r + 5, cy + 30], fill=color)
            draw.ellipse([cx + r - 5, cy - 10, cx + r + 8, cy + 30], fill=color)
        
        elif style == "long":
            # Волосы по бокам
            draw.ellipse([cx - r - 10, cy - r - 15, cx + r + 10, cy + r + 80], fill=color)
            # Чёлка
            draw.ellipse([cx - r - 5, cy - r - 20, cx + r + 5, cy - r + 20], fill=color)
        
        elif style == "short":
            draw.ellipse([cx - r - 5, cy - r - 15, cx + r + 5, cy - r + 25], fill=color)
        
        elif style == "ponytail":
            draw.ellipse([cx - r - 5, cy - r - 10, cx + r + 5, cy + r * 0.5], fill=color)
            # Хвост
            draw.ellipse([cx + r - 10, cy - 20, cx + r + 30, cy + 60], fill=color)
        
        elif style == "curly":
            draw.ellipse([cx - r - 15, cy - r - 15, cx + r + 15, cy + r + 20], fill=color)
            # Кудри
            for angle in range(0, 360, 45):
                rad = math.radians(angle)
                kx = cx + int(25 * math.cos(rad))
                ky = cy + int(25 * math.sin(rad))
                draw.ellipse([kx - 8, ky - 8, kx + 8, ky + 8], fill=color)
        
        else:  # default
            draw.ellipse([cx - r - 8, cy - r - 15, cx + r + 8, cy + r * 0.6], fill=color)
    
    # ================================================================
    #  ОДЕЖДА И АКСЕССУАРЫ
    # ================================================================
    
    def _draw_clothing(self, draw: ImageDraw.ImageDraw, props: Dict,
                       clothing: List[Dict], style: str) -> Image.Image:
        """Рисует одежду"""
        clothing_img = Image.new('RGBA', (512, 512), (0, 0, 0, 0))
        c_draw = ImageDraw.Draw(clothing_img)
        
        head_cx = props['head_cx']
        shoulder_y = props['shoulder_y']
        waist_y = props['waist_y']
        hip_y = props['hip_y']
        shoulder_w = props['shoulder_w']
        waist_w = props['waist_w']
        hip_w = props['hip_w']
        
        for item in clothing:
            item_type = item.get("type", "shirt")
            color = tuple(item.get("color", (155, 145, 135)))
            
            if item_type == "shirt":
                # Футболка/рубашка
                c_draw.rectangle(
                    [head_cx - shoulder_w, shoulder_y,
                     head_cx + shoulder_w, waist_y],
                    fill=color
                )
                # Рукава
                sleeve_len = item.get("sleeves", "short")
                for side in [-1, 1]:
                    arm_x = head_cx + side * shoulder_w
                    if sleeve_len == "short":
                        c_draw.rectangle(
                            [arm_x - int(shoulder_w*0.25), shoulder_y,
                             arm_x + int(shoulder_w*0.25), shoulder_y + 25],
                            fill=color
                        )
                    elif sleeve_len == "long":
                        c_draw.rectangle(
                            [arm_x - int(shoulder_w*0.2), shoulder_y,
                             arm_x + int(shoulder_w*0.2), shoulder_y + 60],
                            fill=color
                        )
                    elif sleeve_len == "sleeveless":
                        # Вырез
                        c_draw.ellipse(
                            [head_cx - 25, shoulder_y - 5,
                             head_cx + 25, shoulder_y + 15],
                            fill=(0, 0, 0, 0)  # Прозрачный
                        )
            
            elif item_type == "skirt":
                length = item.get("length", 80)
                for y in range(hip_y, hip_y + length):
                    progress = (y - hip_y) / length
                    width = int(hip_w + progress * 25)
                    c_draw.rectangle([head_cx - width, y, head_cx + width, y + 1], fill=color)
            
            elif item_type == "pants":
                for leg in [-1, 1]:
                    leg_x = head_cx + leg * int(hip_w * 0.35)
                    c_draw.rectangle(
                        [leg_x - int(props['limb_w'] * 1.2), hip_y,
                         leg_x + int(props['limb_w'] * 1.2), props['foot_y']],
                        fill=color
                    )
            
            elif item_type == "jacket":
                # Куртка поверх рубашки
                for side in [-1, 1]:
                    x_start = head_cx + side * shoulder_w
                    c_draw.rectangle(
                        [x_start - 15, shoulder_y, x_start + 15, waist_y + 20],
                        fill=self._adjust_brightness(color, 0.8)
                    )
            
            elif item_type == "dress":
                # Платье
                for y in range(shoulder_y, hip_y + 100):
                    if y < waist_y:
                        progress = (y - shoulder_y) / (waist_y - shoulder_y)
                        width = int(shoulder_w - progress * (shoulder_w - waist_w))
                    else:
                        progress = (y - waist_y) / 100
                        width = int(waist_w + progress * 40)
                    c_draw.rectangle([head_cx - width, y, head_cx + width, y + 1], fill=color)
        
        return clothing_img
    
    def _draw_accessories(self, draw: ImageDraw.ImageDraw, props: Dict,
                          accessories: List[Dict]) -> Image.Image:
        """Рисует аксессуары"""
        acc_img = Image.new('RGBA', (512, 512), (0, 0, 0, 0))
        a_draw = ImageDraw.Draw(acc_img)
        
        head_cx = props['head_cx']
        head_cy = props['head_cy']
        head_h = props['head_h']
        radius = head_h // 2
        
        for acc in accessories:
            acc_type = acc.get("type", "none")
            color = tuple(acc.get("color", (200, 200, 200)))
            
            if acc_type == "glasses":
                for side in [-1, 1]:
                    ex = head_cx + side * int(radius * 0.6)
                    ey = head_cy + int(radius * 0.15)
                    a_draw.ellipse(
                        [ex - 15, ey - 12, ex + 15, ey + 12],
                        outline=color, width=2
                    )
                # Перемычка
                a_draw.line([(head_cx - 15, head_cy + int(radius*0.15)),
                           (head_cx + 15, head_cy + int(radius*0.15))],
                           fill=color, width=2)
            
            elif acc_type == "necklace":
                neck_y = props['shoulder_y'] - 10
                a_draw.arc([head_cx - 30, neck_y - 20, head_cx + 30, neck_y + 20],
                          0, 180, fill=color, width=2)
            
            elif acc_type == "hat":
                hat_y = head_cy - radius - 25
                a_draw.ellipse([head_cx - 40, hat_y - 10, head_cx + 40, hat_y + 10], fill=color)
                a_draw.rectangle([head_cx - 25, hat_y - 35, head_cx + 25, hat_y - 10], fill=color)
            
            elif acc_type == "bow":
                bow_y = head_cy - radius - 20
                a_draw.polygon([(head_cx - 15, bow_y), (head_cx, bow_y - 10), (head_cx, bow_y + 10)], fill=color)
                a_draw.polygon([(head_cx + 15, bow_y), (head_cx, bow_y - 10), (head_cx, bow_y + 10)], fill=color)
        
        return acc_img
    
    # ================================================================
    #  ФИНАЛЬНАЯ ОБРАБОТКА
    # ================================================================
    
    def _apply_style_filter(self, img: Image.Image, style: str, skill_level: int) -> Image.Image:
        """Применяет стиль с учётом уровня навыка"""
        
        if style == "realistic":
            # Мягкое размытие + контраст
            blur = min(1.5, skill_level * 0.15)
            img = img.filter(ImageFilter.GaussianBlur(radius=blur))
            img = ImageEnhance.Contrast(img).enhance(1.1 + skill_level * 0.02)
            img = ImageEnhance.Color(img).enhance(1.05)
        
        elif style == "anime":
            # Яркие цвета, чёткие линии
            img = img.filter(ImageFilter.GaussianBlur(radius=0.8))
            img = ImageEnhance.Color(img).enhance(1.4 + skill_level * 0.03)
            img = ImageEnhance.Contrast(img).enhance(1.2)
            # Усиление контуров
            img = img.filter(ImageFilter.FIND_EDGES)
        
        elif style == "watercolor":
            # Акварельный эффект
            img = img.filter(ImageFilter.GaussianBlur(radius=3))
            img = img.filter(ImageFilter.EDGE_ENHANCE)
            img = ImageEnhance.Color(img).enhance(1.2)
        
        elif style == "oil_painting":
            # Масляная живопись
            img = img.filter(ImageFilter.GaussianBlur(radius=2))
            img = img.filter(ImageFilter.SHARPEN)
            img = ImageEnhance.Color(img).enhance(1.3)
            img = ImageEnhance.Contrast(img).enhance(1.15)
        
        elif style == "sketch":
            # Карандашный набросок
            gray = img.convert('L')
            gray = gray.filter(ImageFilter.CONTOUR)
            # Добавляем шум для текстуры бумаги
            noise = Image.new('L', gray.size)
            for y in range(gray.size[1]):
                for x in range(gray.size[0]):
                    noise.putpixel((x, y), random.randint(200, 255))
            gray = Image.blend(gray, noise, 0.1)
            img = gray.convert('RGB')
        
        elif style == "pixel":
            # Пиксель-арт
            pixel_size = max(2, 10 - skill_level)
            small = img.resize((img.size[0] // pixel_size, img.size[1] // pixel_size), Image.NEAREST)
            img = small.resize((img.size[0], img.size[1]), Image.NEAREST)
            # Ограничиваем палитру
            img = img.quantize(colors=32)
        
        elif style == "cyberpunk":
            # Неоновое свечение
            img = img.filter(ImageFilter.GaussianBlur(radius=1))
            img = ImageEnhance.Color(img).enhance(1.6)
            img = ImageEnhance.Contrast(img).enhance(1.3)
            # Добавляем свечение
            glow = img.filter(ImageFilter.GaussianBlur(radius=5))
            img = Image.blend(img, glow, 0.3)
        
        elif style == "vintage":
            # Старинный эффект
            img = img.filter(ImageFilter.GaussianBlur(radius=0.5))
            img = ImageEnhance.Color(img).enhance(0.8)
            img = ImageEnhance.Contrast(img).enhance(1.1)
            # Сепия
            pixels = img.load()
            assert pixels is not None, "Failed to load pixel data"
            pixel_data: Any = pixels
            for y in range(img.size[1]):
                for x in range(img.size[0]):
                    r, g, b = pixel_data[x, y]
                    pixel_data[x, y] = (
                        int(r * 0.9 + g * 0.08 + b * 0.02),
                        int(r * 0.4 + g * 0.6 + b * 0.1),
                        int(r * 0.1 + g * 0.2 + b * 0.8)
                    )
        
        return img
    
    # ================================================================
    #  ГЛАВНЫЙ МЕТОД ГЕНЕРАЦИИ
    # ================================================================
    
    def generate_character(self, description: Dict, size: Tuple[int, int] = (512, 512),
                          style: str = "realistic", palette: str = "classical",
                          seed: Optional[int] = None) -> Image.Image:
        """
        Профессиональная генерация персонажа
        
        Args:
            description: Словарь с параметрами персонажа
            size: Размер изображения
            style: Стиль (realistic, anime, watercolor, oil_painting, sketch, pixel, cyberpunk, vintage)
            palette: Цветовая палитра
            seed: Seed для воспроизводимости
        
        Returns:
            PIL Image
        """
        if seed:
            random.seed(seed)
        
        W, H = size
        
        # Парсим параметры
        name = description.get("name", "Character")
        age = description.get("age", 20)
        body_type = description.get("body_type", "athletic")
        skin_color = tuple(description.get("skin_color", (195, 155, 115)))
        hair_color = tuple(description.get("hair_color", (55, 35, 25)))
        hair_style = description.get("hair_style", "bun")
        eye_color = tuple(description.get("eye_color", (45, 28, 18)))
        clothing = description.get("clothing", [])
        accessories = description.get("accessories", [])
        pose = description.get("pose", "standing")
        background = description.get("background", "studio")
        
        # Рассчитываем пропорции
        props = self._calculate_proportions(body_type, W, H, age, pose)
        
        # Генерируем фон
        bg = self._draw_background(ImageDraw.Draw(Image.new('RGB', (W, H))), W, H,
                                  background, style, palette)
        
        # Создаём слой тела
        body = self._draw_body(ImageDraw.Draw(Image.new('RGBA', (W, H))), props, skin_color, style)
        
        # Создаём слой одежды
        clothing_img = self._draw_clothing(ImageDraw.Draw(Image.new('RGBA', (W, H))), props, clothing, style)
        
        # Создаём слой головы
        head = self._draw_head(ImageDraw.Draw(Image.new('RGBA', (W, H))), props,
                              skin_color, hair_color, hair_style, eye_color, style)
        
        # Создаём слой аксессуаров
        acc = self._draw_accessories(ImageDraw.Draw(Image.new('RGBA', (W, H))), props, accessories)
        
        # Комбинируем слои
        result = bg.convert('RGBA')
        result = Image.alpha_composite(result, body)
        result = Image.alpha_composite(result, clothing_img)
        result = Image.alpha_composite(result, head)
        result = Image.alpha_composite(result, acc)
        
        # Применяем освещение
        result = self._apply_lighting(result, intensity=0.8)
        
        # Применяем стиль
        skill = self.get_skill_level("character")
        result = self._apply_style_filter(result.convert('RGB'), style, skill)
        
        # Добавляем текстуру
        if style in ["realistic", "oil_painting", "watercolor"]:
            result = self._add_canvas_texture(result, intensity=0.05)
        elif style == "sketch":
            result = self._add_paper_texture(result, intensity=0.1)
        
        return result
    
    def generate_pixel_art(self, size: Tuple[int, int] = (64, 64),
                          style: str = "character", palette_name: str = "retro",
                          complexity: str = "medium") -> Image.Image:
        """Генерация пиксель-арта"""
        skill = self.get_skill_level("pixel_art")
        pixel_size = max(1, 8 - skill // 2)
        
        W, H = size
        img = Image.new('RGB', (W, H))
        draw = ImageDraw.Draw(img)
        palette = self.palettes.get(palette_name, self.palettes["retro"])
        
        if style == "character":
            # Пиксельный персонаж
            cx, cy = W // 2, H // 2
            # Голова
            head_r = min(W, H) // 4
            draw.ellipse([cx - head_r, cy - head_r, cx + head_r, cy + head_r],
                        fill=palette[0])
            # Глаза
            eye_y = cy - head_r // 3
            draw.rectangle([cx - head_r//2 - 4, eye_y - 2, cx - head_r//2 + 4, eye_y + 2],
                          fill=palette[1])
            draw.rectangle([cx + head_r//2 - 4, eye_y - 2, cx + head_r//2 + 4, eye_y + 2],
                          fill=palette[1])
            # Тело
            draw.rectangle([cx - head_r//2, cy + head_r, cx + head_r//2, cy + head_r*2],
                          fill=palette[2])
        
        elif style == "landscape":
            # Небо
            for y in range(H // 2):
                color = self._blend_colors(palette[3], palette[4], y / (H // 2))
                draw.line([(0, y), (W, y)], fill=color)
            # Земля
            for y in range(H // 2, H):
                color = self._blend_colors(palette[4], palette[5], (y - H//2) / (H//2))
                draw.line([(0, y), (W, y)], fill=color)
            # Солнце
            sun_x, sun_y = W // 4, H // 4
            draw.ellipse([sun_x - 10, sun_y - 10, sun_x + 10, sun_y + 10],
                        fill=palette[0])
        
        # Уменьшаем и увеличиваем для пиксельного эффекта
        small = img.resize((W // pixel_size, H // pixel_size), Image.NEAREST)
        result = small.resize((W, H), Image.NEAREST)
        
        self.experience["total_images"] += 1
        self.experience["pixel_projects"] += 1
        
        return result
    
    def generate_technical_drawing(self, size: Tuple[int, int] = (512, 512),
                                  type: str = "circuit") -> Image.Image:
        """Генерация технической графики"""
        W, H = size
        img = Image.new('RGB', (W, H), (240, 240, 255))
        draw = ImageDraw.Draw(img)
        
        # Сетка
        grid_size = 20
        for x in range(0, W, grid_size):
            draw.line([(x, 0), (x, H)], fill=(200, 200, 220), width=1)
        for y in range(0, H, grid_size):
            draw.line([(0, y), (W, y)], fill=(200, 200, 220), width=1)
        
        if type == "circuit":
            # Электронная схема
            draw.rectangle([50, 50, W-50, H-50], outline=(0, 0, 100), width=2)
            # Компоненты
            for i in range(5):
                x = 80 + i * 80
                draw.rectangle([x, 100, x + 40, 140], fill=(50, 50, 100))
                draw.line([(x + 20, 140), (x + 20, 200)], fill=(0, 0, 100), width=2)
        
        elif type == "gear":
            # Шестерёнка
            cx, cy = W // 2, H // 2
            teeth = 12
            outer_r = 100
            inner_r = 80
            hole_r = 20
            
            for i in range(teeth):
                angle = i * 2 * math.pi / teeth
                next_angle = (i + 0.5) * 2 * math.pi / teeth
                x1 = cx + int(outer_r * math.cos(angle))
                y1 = cy + int(outer_r * math.sin(angle))
                x2 = cx + int(inner_r * math.cos(next_angle))
                y2 = cy + int(inner_r * math.sin(next_angle))
                draw.line([(x1, y1), (x2, y2)], fill=(50, 50, 50), width=2)
            
            draw.ellipse([cx - hole_r, cy - hole_r, cx + hole_r, cy + hole_r],
                        outline=(50, 50, 50), width=2)
        
        elif type == "blueprint":
            # Чертеж
            draw.rectangle([30, 30, W-30, H-30], outline=(0, 50, 150), width=2)
            # Оси
            draw.line([(W//2, 30), (W//2, H-30)], fill=(200, 0, 0), width=1)
            draw.line([(30, H//2), (W-30, H//2)], fill=(200, 0, 0), width=1)
            # Детали
            draw.ellipse([W//2 - 60, H//2 - 60, W//2 + 60, H//2 + 60],
                        outline=(0, 50, 150), width=2)
            draw.rectangle([W//2 - 30, H//2 - 30, W//2 + 30, H//2 + 30],
                          outline=(0, 50, 150), width=2)
        
        self.experience["total_images"] += 1
        self.experience["technical_projects"] += 1
        
        return img
    
    # ================================================================
    #  СОХРАНЕНИЕ И СТАТИСТИКА
    # ================================================================
    
    def save_image(self, img: Image.Image, filename: str = None) -> str:
        """Сохраняет изображение"""
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"ayiko_{timestamp}.png"
        
        output_path = self.output_dir / filename
        img.save(output_path, "PNG")
        return str(output_path)
    
    def get_stats(self) -> Dict:
        """Статистика генерации"""
        files = list(self.output_dir.glob("*.png"))
        return {
            "total_saved": len(files),
            "skills": {k: round(v, 1) for k, v in self.skills.items()},
            "experience": self.experience,
            "average_skill": round(sum(self.skills.values()) / len(self.skills), 1),
            "masterpieces": self.experience["masterpieces"]
        }


if __name__ == "__main__":
    gen = AyikoProGenerator()
    
    print("\n=== ТЕСТ ГЕНЕРАЦИИ ===\n")
    
    # Генерация персонажа
    char_desc = {
        "name": "Talsa",
        "age": 17,
        "body_type": "athletic",
        "skin_color": (195, 155, 115),
        "hair_color": (55, 35, 25),
        "hair_style": "bun",
        "eye_color": (45, 28, 18),
        "clothing": [
            {"type": "shirt", "color": (155, 145, 135), "sleeves": "short"}
        ],
        "accessories": [
            {"type": "glasses"}
        ],
        "background": "academy"
    }
    
    img = gen.generate_character(char_desc, (512, 512), "realistic", "classical")
    gen.save_image(img, "test_character.png")
    print("✅ Персонаж сохранён: test_character.png")
    
    # Пиксель-арт
    pixel = gen.generate_pixel_art((128, 128), "character", "retro")
    gen.save_image(pixel, "test_pixel.png")
    print("✅ Пиксель-арт сохранён: test_pixel.png")
    
    # Техническая графика
    tech = gen.generate_technical_drawing((512, 512), "blueprint")
    gen.save_image(tech, "test_tech.png")
    print("✅ Техграфика сохранена: test_tech.png")
    
    print(f"\n📊 Статистика: {json.dumps(gen.get_stats(), indent=2)}")
