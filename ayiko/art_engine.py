#!/usr/bin/env python3
"""
Айко AI — Художественный движок (Art Engine).

Объединяет все творческие системы Айко в один мощный инструмент:
  - 🎨 Пиксель-арт (16x16 → 32K)
  - 📐 Техническая графика / чертежи (ГОСТ, blueprint, circuit, gear)
  - 🧊 3D-моделирование и рендер (изометрия, шейдинг, объём)
  - 👤 Персонажи (пропорции, анатомия, одежда, причёски)
  - 🏞️ Пейзажи / сцены
  - 📸 Изучение референсов из папки ojidania (OjidaniaAnalyzer)
  - 🎨 Стили: realistic, anime, watercolor, oil, sketch, pixel, cyberpunk

Вся генерация выполняется локально с помощью PIL + numpy.
"""

from __future__ import annotations

import json
import math
import os
import random
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from PIL import Image, ImageDraw, ImageFilter, ImageEnhance

# Референс-анализатор (обучение на примерах из ojidania)
from ayiko.ojidania_analyzer import OjidaniaAnalyzer


class AyikoArtEngine:
    """Единый художественный движок Айко."""

    def __init__(self, output_dir: str = "ayiko/engine/state/generated",
                 references_dir: str = "ayiko/ojidania",
                 analysis_dir: str = "ayiko/engine/state/ojidania_analysis"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

        self.references_dir = Path(references_dir)
        self.analysis_dir = Path(analysis_dir)
        self.analysis_dir.mkdir(parents=True, exist_ok=True)

        # Анализатор референсов (обучение)
        self.analyzer = OjidaniaAnalyzer(
            ojidania_dir=str(self.references_dir),
            output_dir=str(self.analysis_dir),
        )

        # Палитры
        self.palettes = self._init_palettes()

        # Счётчики
        self.stats = {
            "total_images": 0,
            "pixel_art": 0,
            "technical": 0,
            "3d": 0,
            "character": 0,
            "references_analyzed": 0,
        }

        # Стили
        self.styles = ["realistic", "anime", "watercolor", "oil_painting",
                       "sketch", "pixel", "cyberpunk", "vintage"]

    # ================================================================
    #  ПАЛИТРЫ
    # ================================================================

    def _init_palettes(self) -> Dict[str, List[Tuple]]:
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
                      (176, 196, 222), (255, 255, 255), (112, 128, 144)],
            "monochrome": [(0, 0, 0), (32, 32, 32), (64, 64, 64), (96, 96, 96),
                           (128, 128, 128), (160, 160, 160), (192, 192, 192),
                           (224, 224, 224), (255, 255, 255)],
            "watercolor": [(176, 224, 230), (255, 182, 193), (255, 218, 185),
                           (221, 160, 221), (173, 216, 230), (245, 250, 240)],
            "oil_painting": [(139, 69, 19), (34, 139, 34), (65, 105, 225),
                             (255, 215, 0), (220, 20, 60), (128, 0, 128)],
            "gold": [(255, 215, 0), (218, 165, 32), (255, 255, 224),
                     (240, 230, 140), (255, 250, 205), (184, 134, 11)],
            "steampunk": [(139, 90, 43), (160, 82, 45), (210, 105, 30),
                          (244, 164, 96), (255, 228, 181), (94, 57, 25)],
        }

    # ================================================================
    #  ОБУЧЕНИЕ НА РЕФЕРЕНСАХ (ojidania)
    # ================================================================

    def analyze_references(self, limit: int = 20) -> Dict:
        """
        Изучить референсные изображения из папки ojidania.

        Возвращает сводку: сколько изображений проанализировано и что
        Айко узнала (свет, одежда, анатомия, 3D-структура и т.д.).
        """
        if not self.references_dir.exists():
            return {"error": f"Папка не найдена: {self.references_dir}"}

        image_files = []
        for ext in ("*.jpg", "*.jpeg", "*.png", "*.webp", "*.bmp"):
            image_files.extend(self.references_dir.glob(ext))

        if not image_files:
            return {"analyzed": 0, "message": "Нет изображений в ojidania"}

        # Анализируем ограниченное число (остальные — позже)
        to_analyze = image_files[:limit]
        results = []
        for img_file in to_analyze:
            try:
                res = self.analyzer.analyze_image(str(img_file))
                if "error" not in res:
                    results.append(res)
            except Exception:
                continue

        self.stats["references_analyzed"] += len(results)
        return {
            "analyzed": len(results),
            "total_available": len(image_files),
            "sections": self.analyzer.get_stats().get("knowledge_sections", {}),
        }

    def get_reference_knowledge(self) -> Dict:
        """Вернуть накопленные знания из референсов."""
        return self.analyzer.knowledge

    # ================================================================
    #  ВСПОМОГАТЕЛЬНЫЕ МЕТОДЫ
    # ================================================================

    @staticmethod
    def _blend(c1: Tuple, c2: Tuple, ratio: float) -> Tuple:
        return (int(c1[0] * (1 - ratio) + c2[0] * ratio),
                int(c1[1] * (1 - ratio) + c2[1] * ratio),
                int(c1[2] * (1 - ratio) + c2[2] * ratio))

    @staticmethod
    def _brightness(color: Tuple, factor: float) -> Tuple:
        return tuple(min(255, max(0, int(c * factor))) for c in color)

    def _pick_palette(self, palette: Optional[str]) -> List[Tuple]:
        if palette and palette in self.palettes:
            return self.palettes[palette]
        return random.choice(list(self.palettes.values()))

    def _gradient_bg(self, W: int, H: int, top: Tuple, bottom: Tuple) -> Image.Image:
        img = Image.new("RGB", (W, H))
        d = ImageDraw.Draw(img)
        for y in range(H):
            d.line([(0, y), (W, y)], fill=self._blend(top, bottom, y / max(1, H - 1)))
        return img

    def _save(self, img: Image.Image, kind: str, tag: str = "") -> str:
        ts = datetime.now().strftime("%Y%m%d_%H%M%S_%f")[:-3]
        safe_tag = "".join(c if c.isalnum() or c in "-_" else "_" for c in tag)
        filename = f"ayiko_{kind}_{safe_tag}_{ts}.png"
        path = self.output_dir / filename
        img.save(path, "PNG")
        self.stats["total_images"] += 1
        return str(path)

    # ================================================================
    #  ПИКСЕЛЬ-АРТ
    # ================================================================

    def generate_pixel_art(self, size: Tuple[int, int] = (256, 256),
                           palette: Optional[str] = None, seed: Optional[int] = None) -> str:
        """Сгенерировать пиксель-арт (сцена или персонаж)."""
        if seed is not None:
            random.seed(seed)
        target = size
        colors = self._pick_palette(palette)

        # Внутренний холст всегда крупный, чтобы фиксированные координаты работали
        W, H = 320, 320

        img = Image.new("RGB", (W, H))
        d = ImageDraw.Draw(img)

        scene = random.choice(["character", "landscape", "city", "item"])

        if scene == "character":
            cx, cy = W // 2, H // 2
            head_r = min(W, H) // 4
            d.rectangle([0, 0, W, H], fill=colors[-1])  # фон
            # тело
            d.rectangle([cx - head_r // 2, cy, cx + head_r // 2, cy + head_r * 2],
                        fill=colors[2])
            # руки
            d.rectangle([cx - head_r, cy + head_r // 3, cx - head_r // 2, cy + head_r],
                        fill=colors[2])
            d.rectangle([cx + head_r // 2, cy + head_r // 3, cx + head_r, cy + head_r],
                        fill=colors[2])
            # голова
            d.rectangle([cx - head_r // 2, cy - head_r, cx + head_r // 2, cy],
                        fill=colors[0])
            # глаза
            d.rectangle([cx - head_r // 3, cy - head_r // 2, cx - head_r // 5, cy - head_r // 3],
                        fill=colors[1])
            d.rectangle([cx + head_r // 5, cy - head_r // 2, cx + head_r // 3, cy - head_r // 3],
                        fill=colors[1])
            # ноги
            d.rectangle([cx - head_r // 2, cy + head_r * 2, cx - head_r // 5, cy + head_r * 3],
                        fill=colors[3])
            d.rectangle([cx + head_r // 5, cy + head_r * 2, cx + head_r // 2, cy + head_r * 3],
                        fill=colors[3])

        elif scene == "landscape":
            horizon = int(H * 0.6)
            for y in range(horizon):
                d.line([(0, y), (W, y)], fill=self._blend(colors[4], colors[5], y / max(1, horizon)))
            for y in range(horizon, H):
                d.line([(0, y), (W, y)], fill=self._blend(colors[3], colors[2], (y - horizon) / max(1, H - horizon)))
            # солнце
            d.rectangle([W // 4 - 12, H // 5 - 12, W // 4 + 12, H // 5 + 12], fill=colors[0])
            # горы (треугольники-ступеньки)
            for i in range(0, W, 40):
                hgt = random.randint(20, 60)
                d.polygon([(i, horizon), (i + 20, horizon - hgt), (i + 40, horizon)], fill=colors[3])

        elif scene == "city":
            d.rectangle([0, 0, W, H], fill=(15, 15, 35))
            ground_y = int(H * 0.8)
            for i in range(0, W, 30):
                bh = random.randint(30, H // 2)
                bx = i + random.randint(-8, 8)
                d.rectangle([bx, ground_y - bh, bx + 20, ground_y], fill=colors[random.randint(0, len(colors) - 1)])
                # окна
                for wy in range(ground_y - bh + 6, ground_y - 6, 14):
                    for wx in (bx + 4, bx + 12):
                        d.rectangle([wx, wy, wx + 4, wy + 6], fill=(255, 240, 150))
            # неон
            for _ in range(6):
                x0, x1 = sorted([random.randint(0, W), random.randint(0, W)])
                y0, y1 = sorted([random.randint(0, ground_y), random.randint(0, ground_y)])
                d.rectangle([x0, y0, max(x0, x1), max(y0, y1)],
                            fill=random.choice([(0, 255, 255), (255, 0, 255), (255, 255, 0)]))

        else:  # item
            d.rectangle([0, 0, W, H], fill=colors[-1])
            cx, cy = W // 2, H // 2
            kind = random.choice(["gem", "sword", "potion", "star"])
            if kind == "gem":
                d.polygon([(cx, cy - 40), (cx + 35, cy - 10), (cx + 20, cy + 45),
                           (cx - 20, cy + 45), (cx - 35, cy - 10)], fill=colors[0])
                d.polygon([(cx, cy - 40), (cx + 35, cy - 10), (cx, cy)], fill=self._brightness(colors[0], 1.3))
            elif kind == "sword":
                d.rectangle([cx - 4, cy - 60, cx + 4, cy + 10], fill=(220, 220, 230))
                d.rectangle([cx - 15, cy + 10, cx + 15, cy + 18], fill=colors[1])
            elif kind == "potion":
                d.rectangle([cx - 12, cy - 35, cx + 12, cy + 30], fill=colors[1])
                d.rectangle([cx - 6, cy - 45, cx + 6, cy - 30], fill=colors[2])
            elif kind == "star":
                pts = []
                for i in range(10):
                    ang = math.pi / 5 * i - math.pi / 2
                    r = 40 if i % 2 == 0 else 18
                    pts.append((cx + r * math.cos(ang), cy + r * math.sin(ang)))
                d.polygon(pts, fill=colors[0])

        # Финальный пиксель-арт: NEAREST-масштаб до целевого размера + чистая палитра
        result = img.resize(target, Image.NEAREST).quantize(
            colors=min(64, max(8, len(colors) * 4))
        )
        result = result.convert("RGB")

        self.stats["pixel_art"] += 1
        return self._save(result, "pixel", f"lvl{1 + self.stats['pixel_art'] // 5}")

    # ================================================================
    #  ТЕХНИЧЕСКАЯ ГРАФИКА
    # ================================================================

    def generate_technical(self, size: Tuple[int, int] = (512, 512),
                           kind: Optional[str] = None) -> str:
        """Сгенерировать техническую графику (чертёж/схема/шестерня)."""
        W, H = size
        kind = kind or random.choice(["blueprint", "circuit", "gear", "isometric_tech"])

        bg = (18, 26, 58) if random.random() < 0.5 else (240, 242, 252)
        line = (120, 190, 255) if bg[0] < 100 else (20, 60, 140)
        grid = (70, 110, 180) if bg[0] < 100 else (200, 208, 228)

        img = Image.new("RGB", (W, H), bg)
        d = ImageDraw.Draw(img)

        # Сетка
        gs = 25
        for x in range(0, W, gs):
            d.line([(x, 0), (x, H)], fill=grid, width=1)
        for y in range(0, H, gs):
            d.line([(0, y), (W, y)], fill=grid, width=1)

        if kind == "blueprint":
            d.rectangle([40, 40, W - 40, H - 40], outline=line, width=2)
            d.line([(W // 2, 40), (W // 2, H - 40)], fill=line, width=1)
            d.line([(40, H // 2), (W - 40, H // 2)], fill=line, width=1)
            # деталь
            d.ellipse([W // 2 - 70, H // 2 - 70, W // 2 + 70, H // 2 + 70], outline=line, width=2)
            d.rectangle([W // 2 - 35, H // 2 - 35, W // 2 + 35, H // 2 + 35], outline=line, width=2)
            # размерные линии
            d.line([(W // 2, H - 40), (W // 2, H - 12)], fill=(255, 120, 120), width=1)
            d.line([(W // 2 - 8, H - 22), (W // 2 + 8, H - 22)], fill=(255, 120, 120), width=1)

        elif kind == "circuit":
            d.rectangle([45, 45, W - 45, H - 45], outline=line, width=2)
            for i in range(5):
                x = 80 + i * 80
                d.rectangle([x, 100, x + 40, 140], fill=(50, 70, 130))
                d.line([(x + 20, 140), (x + 20, H - 60)], fill=line, width=2)
                d.ellipse([x + 10, H - 90, x + 30, H - 70], outline=line, width=2)
            # дорожки
            for _ in range(12):
                x1 = random.randint(60, W - 60)
                y1 = random.randint(60, H - 60)
                x2 = x1 + random.randint(-60, 60)
                y2 = y1 + random.randint(-60, 60)
                d.line([(x1, y1), (x2, y2)], fill=line, width=1)
                d.ellipse([x2 - 3, y2 - 3, x2 + 3, y2 + 3], fill=(255, 220, 120))

        elif kind == "gear":
            cx, cy = W // 2, H // 2
            teeth, outer, inner, hole = 12, 110, 88, 24
            for i in range(teeth):
                a = i * 2 * math.pi / teeth
                an = (i + 0.5) * 2 * math.pi / teeth
                d.line([(cx + outer * math.cos(a), cy + outer * math.sin(a)),
                        (cx + inner * math.cos(an), cy + inner * math.sin(an))],
                       fill=line, width=3)
            d.ellipse([cx - inner, cy - inner, cx + inner, cy + inner], outline=line, width=3)
            d.ellipse([cx - hole, cy - hole, cx + hole, cy + hole], outline=line, width=2)
            # оси
            for ang in range(0, 360, 30):
                rad = math.radians(ang)
                d.line([(cx, cy), (cx + 80 * math.cos(rad), cy + 80 * math.sin(rad))],
                       fill=line, width=1)

        elif kind == "isometric_tech":
            # Изометрическая техническая сцена
            cx, cy = W // 2, H // 2 + 40
            for dx in (-60, 60):
                d.polygon([(cx, cy - 140), (cx + dx, cy - 70), (cx + dx, cy + 60), (cx, cy - 10)],
                          outline=line, width=2)
            d.polygon([(cx, cy - 140), (cx + 60, cy - 70), (cx + 60, cy + 60), (cx, cy - 10)],
                      outline=line, width=2)
            d.polygon([(cx, cy - 10), (cx + 60, cy + 60), (cx, cy + 130), (cx - 60, cy + 60)],
                      outline=line, width=2)

        self.stats["technical"] += 1
        return self._save(img, "technical", kind)

    # ================================================================
    #  3D-МОДЕЛИРОВАНИЕ / РЕНДЕР
    # ================================================================

    def generate_3d(self, size: Tuple[int, int] = (512, 512),
                    kind: Optional[str] = None, palette: Optional[str] = None) -> str:
        """
        Сгенерировать 3D-изображение.

        Режимы:
          - isometric: изометрическая сцена с затенением граней
          - object: объёмный объект (куб/сфера/цилиндр/пирамида) с шейдингом
          - voxel: воксельная сцена (пиксельная 3D)
          - wireframe: каркасная 3D-модель
        """
        W, H = size
        kind = kind or random.choice(["isometric", "object", "voxel", "wireframe"])
        colors = self._pick_palette(palette)

        top_c = colors[0]
        side_l = self._brightness(colors[1], 1.0)
        side_r = self._brightness(colors[1], 0.6)
        dark = self._brightness(colors[2], 0.5)

        if kind == "object":
            # Сцена с одним объёмным объектом
            bg = self._gradient_bg(W, H, self._brightness(colors[-1], 1.4),
                                   self._brightness(colors[-1], 0.7))
            d = ImageDraw.Draw(bg)
            cx, cy = W // 2, H // 2
            obj = random.choice(["cube", "sphere", "cylinder", "pyramid", "diamond"])

            if obj == "cube":
                s = 110
                # верхняя грань
                d.polygon([(cx, cy - s), (cx + s, cy - s // 2), (cx, cy), (cx - s, cy - s // 2)],
                          fill=top_c)
                # левая грань
                d.polygon([(cx - s, cy - s // 2), (cx, cy), (cx, cy + s), (cx - s, cy + s // 2)],
                          fill=side_l)
                # правая грань
                d.polygon([(cx, cy), (cx + s, cy - s // 2), (cx + s, cy + s // 2), (cx, cy + s)],
                          fill=side_r)
            elif obj == "sphere":
                r = 100
                d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=side_l)
                # шейдинг — градиентные тени
                for i in range(1, 8):
                    shade = Image.new("RGBA", (W, H), (0, 0, 0, 0))
                    sd = ImageDraw.Draw(shade)
                    r2 = r * (1 - i * 0.06)
                    sd.ellipse([cx - r2, cy - r2, cx + r2, cy + r2],
                               fill=(0, 0, 0, int(8 * i)))
                    bg = Image.alpha_composite(bg.convert("RGBA"), shade)
                d = ImageDraw.Draw(bg)
                # блик
                d.ellipse([cx - r // 3, cy - r // 2, cx + r // 5, cy - r // 6],
                          fill=self._brightness(colors[0], 1.5))
                # тень на земле
                d.ellipse([cx - r // 2, cy + r + 10, cx + r // 2, cy + r + 25], fill=dark)
            elif obj == "cylinder":
                w, h = 140, 180
                d.ellipse([cx - w // 2, cy - h // 2, cx + w // 2, cy - h // 2 + 40], fill=top_c)
                d.rectangle([cx - w // 2, cy - h // 2 + 20, cx + w // 2, cy + h // 2], fill=side_r)
                d.ellipse([cx - w // 2, cy + h // 2 - 40, cx + w // 2, cy + h // 2], fill=side_r)
                # блик
                d.rectangle([cx - w // 4, cy - h // 2 + 20, cx - w // 5, cy + h // 2 - 20],
                            fill=self._brightness(side_r, 1.25))
                d.ellipse([cx - w // 4, cy - h // 2 + 20, cx - w // 5, cy - h // 2 + 40],
                          fill=self._brightness(top_c, 1.1))
            elif obj == "pyramid":
                s = 120
                d.polygon([(cx, cy - s), (cx + s, cy), (cx, cy + s)], fill=top_c)
                d.polygon([(cx, cy - s), (cx, cy + s), (cx - s, cy)], fill=side_r)
                d.polygon([(cx + s, cy), (cx, cy + s), (cx - s, cy)], fill=dark)
                # тень
                d.polygon([(cx - s, cy + 40), (cx + s, cy + 40), (cx + s + 60, cy + 70),
                           (cx - s - 60, cy + 70)], fill=dark)
            elif obj == "diamond":
                pts_top = [(cx, cy - 130), (cx + 90, cy - 30), (cx, cy + 40), (cx - 90, cy - 30)]
                pts_bottom = [(cx + 90, cy - 30), (cx, cy + 40), (cx, cy + 130), (cx - 90, cy - 30)]
                d.polygon(pts_top, fill=top_c)
                d.polygon(pts_bottom, fill=side_r)
                # грани
                d.polygon([(cx, cy - 130), (cx, cy + 40), (cx + 90, cy - 30)], fill=self._brightness(top_c, 0.85))
                d.polygon([(cx, cy - 130), (cx, cy + 40), (cx - 90, cy - 30)], fill=top_c)
                # блики
                d.line([(cx - 30, cy - 60), (cx + 30, cy - 60)], fill=(255, 255, 255), width=3)
                d.line([(cx - 20, cy - 30), (cx + 20, cy - 30)], fill=(255, 255, 255), width=2)

            img = bg.convert("RGB")

        elif kind == "isometric":
            # Изометрический город / сцена
            bg = self._gradient_bg(W, H, self._brightness(colors[4], 1.3), self._brightness(colors[5], 0.9))
            d = ImageDraw.Draw(bg)
            base_y = int(H * 0.82)
            # платформа-земля
            d.polygon([(W // 2 - 240, base_y), (W // 2, base_y - 90),
                       (W // 2 + 240, base_y), (W // 2, base_y + 90)], fill=dark)
            # несколько изометрических кубов (здания)
            for i, (off, size_s) in enumerate([(-140, 55), (0, 75), (140, 45)]):
                bx = W // 2 + off
                by = base_y - size_s // 2
                d.polygon([(bx, by - size_s), (bx + size_s, by - size_s // 2),
                           (bx, by), (bx - size_s, by - size_s // 2)], fill=self._brightness(colors[i % len(colors)], 1.2))
                d.polygon([(bx - size_s, by - size_s // 2), (bx, by), (bx, by + size_s),
                           (bx - size_s, by + size_s // 2)], fill=self._brightness(colors[i % len(colors)], 0.8))
                d.polygon([(bx, by), (bx + size_s, by - size_s // 2), (bx + size_s, by + size_s // 2),
                           (bx, by + size_s)], fill=self._brightness(colors[i % len(colors)], 0.55))
            # солнце
            d.ellipse([W - 120, 40, W - 40, 120], fill=(255, 230, 120))
            d.ellipse([W - 140, 20, W - 20, 140], outline=(255, 240, 180), width=3)

            img = bg

        elif kind == "voxel":
            # Воксельная сцена (3D в пиксельном стиле)
            img = Image.new("RGB", (W, H))
            d = ImageDraw.Draw(img)
            d.rectangle([0, 0, W, H], fill=self._brightness(colors[-1], 0.7))
            cx, cy = W // 2, int(H * 0.7)
            vox = 26
            # пирамида из вокселей
            for layer in range(6):
                width_n = 6 - layer
                y = cy - layer * vox
                for ix in range(-width_n, width_n):
                    for iz in range(-1, 2):
                        x = cx + ix * vox // 2 + iz * vox // 2
                        yy = y + iz * vox // 3
                        c = self._brightness(colors[layer % len(colors)], 1.0 - layer * 0.06)
                        d.rectangle([x - vox // 2, yy, x + vox // 2, yy + vox], fill=c,
                                    outline=self._brightness(c, 0.7))
            img = img.filter(ImageFilter.SHARPEN)

        else:  # wireframe
            bg = (10, 12, 30)
            img = Image.new("RGB", (W, H), bg)
            d = ImageDraw.Draw(img)
            cx, cy = W // 2, H // 2
            line = (0, 255, 255)
            # вращающийся куб (каркас)
            for k in range(4):
                ang = k * math.pi / 2
                dx, dy = 80 * math.cos(ang), 80 * math.sin(ang) * 0.5
                d.line([(cx - 60 + dx, cy - 60 + dy), (cx + 60 + dx, cy - 60 + dy)], fill=line, width=1)
                d.line([(cx - 60 + dx, cy + 60 + dy), (cx + 60 + dx, cy + 60 + dy)], fill=line, width=1)
                d.line([(cx - 60 + dx, cy - 60 + dy), (cx - 60 + dx, cy + 60 + dy)], fill=line, width=1)
                d.line([(cx + 60 + dx, cy - 60 + dy), (cx + 60 + dx, cy + 60 + dy)], fill=line, width=1)
            # оси
            d.line([(30, H - 30), (W - 30, H - 30)], fill=(255, 80, 80), width=2)
            d.line([(30, H - 30), (30, 30)], fill=(80, 255, 80), width=2)
            # метки
            for gx in range(50, W - 30, 50):
                d.line([(gx, H - 34), (gx, H - 26)], fill=(255, 80, 80), width=1)
            for gy in range(50, H - 30, 50):
                d.line([(26, H - 30 - gy), (34, H - 30 - gy)], fill=(80, 255, 80), width=1)

        self.stats["3d"] += 1
        return self._save(img, "3d", f"{kind}_lvl{1 + self.stats['3d'] // 5}")

    # ================================================================
    #  СЦЕНА / ПЕЙЗАЖ / ПЕРСОНАЖ
    # ================================================================

    def generate_scene(self, size: Tuple[int, int] = (512, 512),
                       palette: Optional[str] = None, seed: Optional[int] = None) -> str:
        """Сгенерировать сцену/пейзаж в случайном стиле."""
        if seed is not None:
            random.seed(seed)
        W, H = size
        colors = self._pick_palette(palette)
        style = random.choice(self.styles)

        bg = self._gradient_bg(W, H, colors[4], colors[5])
        d = ImageDraw.Draw(bg)

        # Солнце/луна
        d.ellipse([W // 2 - 45, int(H * 0.22) - 45, W // 2 + 45, int(H * 0.22) + 45],
                  fill=self._brightness(colors[0], 1.3))

        # Холмы
        horizon = int(H * 0.6)
        for i, (col, base) in enumerate([(colors[3], 0.62), (colors[2], 0.72)]):
            d.ellipse([-100, horizon * base - H * 0.35, W + 100, horizon * base + H * 0.4],
                      fill=col)

        # Деревья
        for _ in range(6):
            x = random.randint(20, W - 20)
            y = horizon + random.randint(0, 20)
            hgt = random.randint(40, 90)
            d.rectangle([x - 5, y, x + 5, y + hgt], fill=(90, 60, 30))
            d.ellipse([x - 25, y - hgt, x + 25, y], fill=colors[3])

        # Вода/река
        d.polygon([(0, H), (0, H - 30), (W, H - 40), (W, H)], fill=self._brightness(colors[4], 0.8))

        # Облака
        for _ in range(4):
            cx = random.randint(0, W)
            cy = random.randint(20, int(H * 0.25))
            d.ellipse([cx, cy, cx + 70, cy + 25], fill=(255, 255, 255, 160))

        # Применяем стиль
        img = self._apply_style(bg, style)
        self.stats["character"] += 1  # считаем как сцену
        return self._save(img, "scene", style)

    # ================================================================
    #  СТИЛИЗАЦИЯ
    # ================================================================

    def _apply_style(self, img: Image.Image, style: str) -> Image.Image:
        if style == "watercolor":
            img = img.filter(ImageFilter.GaussianBlur(radius=3))
            img = img.filter(ImageFilter.EDGE_ENHANCE)
            img = ImageEnhance.Color(img).enhance(1.2)
        elif style == "oil_painting":
            img = img.filter(ImageFilter.GaussianBlur(radius=2))
            img = img.filter(ImageFilter.SHARPEN)
            img = ImageEnhance.Color(img).enhance(1.3)
            img = ImageEnhance.Contrast(img).enhance(1.15)
        elif style == "sketch":
            gray = img.convert("L").filter(ImageFilter.CONTOUR)
            img = gray.convert("RGB")
        elif style == "pixel":
            ps = 8
            img = img.resize((img.size[0] // ps, img.size[1] // ps), Image.NEAREST)
            img = img.resize((img.size[0] * ps, img.size[1] * ps), Image.NEAREST).quantize(colors=32).convert("RGB")
        elif style == "cyberpunk":
            img = img.filter(ImageFilter.GaussianBlur(radius=1))
            img = ImageEnhance.Color(img).enhance(1.6)
            img = ImageEnhance.Contrast(img).enhance(1.3)
            glow = img.filter(ImageFilter.GaussianBlur(radius=5))
            img = Image.blend(img, glow, 0.3)
        elif style == "anime":
            img = img.filter(ImageFilter.GaussianBlur(radius=0.8))
            img = ImageEnhance.Color(img).enhance(1.4)
            img = ImageEnhance.Contrast(img).enhance(1.2)
        elif style == "vintage":
            img = ImageEnhance.Color(img).enhance(0.8)
            img = ImageEnhance.Contrast(img).enhance(1.1)
        elif style == "realistic":
            img = img.filter(ImageFilter.GaussianBlur(radius=0.8))
            img = ImageEnhance.Contrast(img).enhance(1.1)
        return img

    # ================================================================
    #  СВОДКА
    # ================================================================

    def get_stats(self) -> Dict:
        return dict(self.stats)


def create_art_engine() -> AyikoArtEngine:
    """Создать экземпляр художественного движка."""
    return AyikoArtEngine()


if __name__ == "__main__":
    engine = AyikoArtEngine()
    print("=== ТЕСТ ART ENGINE ===")
    print("1. Пиксель-арт:", engine.generate_pixel_art())
    print("2. Техграфика:", engine.generate_technical())
    print("3. 3D:", engine.generate_3d())
    print("4. Сцена:", engine.generate_scene())
    print("5. Референсы:", engine.analyze_references(limit=5))
    print("\nСтатистика:", engine.get_stats())
