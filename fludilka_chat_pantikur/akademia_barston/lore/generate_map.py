"""
Карта мира Эрдос — детальная версия с рельефом, реками, лесами,
границами империй, внутренними морями, и специальными формами
для Квентора (полуостров + острова) и Морканта (материк + 2 острова).
"""

from PIL import Image, ImageDraw, ImageFont
import math
import random

# ============================================================
# Настройки
# ============================================================
W, H = 1800, 1200
IMG = Image.new("RGB", (W, H))
DRAW = ImageDraw.Draw(IMG)

# Цвета
C_OCEAN_TOP = (10, 20, 35)
C_OCEAN_BOT = (18, 38, 62)
C_SHALLOW = (28, 55, 80)
C_LAND = (58, 78, 56)
C_LAND_DARK = (42, 60, 42)
C_MORNER = (58, 32, 28)
C_MORNER_DARK = (38, 20, 18)
C_UR_EDEM = (68, 34, 44)
C_UR_EDEM_DARK = (48, 22, 32)
C_MTN = (105, 90, 75)
C_MTN_DARK = (82, 70, 58)
C_SNOW = (225, 228, 235)
C_FOREST = (28, 52, 32)
C_FOREST_LIGHT = (42, 72, 46)
C_RIVER = (45, 85, 125)
C_RIVER_WIDE = (55, 100, 140)
C_SWAMP = (48, 58, 42)
C_DESERT = (138, 118, 82)
C_DESERT_DARK = (118, 100, 68)
C_VOLCANIC = (75, 42, 32)
C_LAVA = (200, 70, 25)
C_TUNDRA = (125, 128, 133)
C_BORDER_DASH = (190, 165, 100)
C_TEXT = (215, 195, 165)
C_TEXT_GOLD = (220, 180, 70)
C_TEXT_RED = (190, 75, 65)
C_TEXT_BLUE = (85, 135, 195)
C_TEXT_GREEN = (95, 165, 95)
C_TEXT_WHITE = (240, 235, 225)
C_COMPASS = (175, 150, 95)
C_ACADEMY = (255, 215, 60)


def font(size, bold=False):
    paths = [
        "C:/Windows/Fonts/arialbd.ttf" if bold else "C:/Windows/Fonts/arial.ttf",
        "C:/Windows/Fonts/segoeui.ttf",
        "C:/Windows/Fonts/times.ttf",
    ]
    for p in paths:
        try:
            return ImageFont.truetype(p, size)
        except Exception:
            pass
    return ImageFont.load_default()


# ============================================================
# Сплайн для плавных береговых линий
# ============================================================

def smooth_closed(points, segments=16):
    """Catmull-Rom сплайн для замкнутой кривой."""
    result = []
    n = len(points)
    for i in range(n):
        p0 = points[(i - 1) % n]
        p1 = points[i]
        p2 = points[(i + 1) % n]
        p3 = points[(i + 2) % n]
        for j in range(segments):
            t = j / segments
            t2 = t * t
            t3 = t2 * t
            x = 0.5 * (2*p1[0] + (-p0[0]+p2[0])*t +
                       (2*p0[0]-5*p1[0]+4*p2[0]-p3[0])*t2 +
                       (-p0[0]+3*p1[0]-3*p2[0]+p3[0])*t3)
            y = 0.5 * (2*p1[1] + (-p0[1]+p2[1])*t +
                       (2*p0[1]-5*p1[1]+4*p2[1]-p3[1])*t2 +
                       (-p0[1]+3*p1[1]-3*p2[1]+p3[1])*t3)
            result.append((x, y))
    return result


def smooth_open(points, segments=12):
    """Catmull-Rom сплайн для незамкнутой кривой."""
    result = []
    pts = [points[0]] + list(points) + [points[-1]]
    for i in range(1, len(pts) - 2):
        p0 = pts[i - 1]
        p1 = pts[i]
        p2 = pts[i + 1]
        p3 = pts[i + 2]
        for j in range(segments):
            t = j / segments
            t2 = t * t
            t3 = t2 * t
            x = 0.5 * (2*p1[0] + (-p0[0]+p2[0])*t +
                       (2*p0[0]-5*p1[0]+4*p2[0]-p3[0])*t2 +
                       (-p0[0]+3*p1[0]-3*p2[0]+p3[0])*t3)
            y = 0.5 * (2*p1[1] + (-p0[1]+p2[1])*t +
                       (2*p0[1]-5*p1[1]+4*p2[1]-p3[1])*t2 +
                       (-p0[1]+3*p1[1]-3*p2[1]+p3[1])*t3)
            result.append((x, y))
    result.append(points[-1])
    return result


# ============================================================
# Океан
# ============================================================

def draw_ocean():
    for y in range(H):
        t = y / H
        r = int(C_OCEAN_TOP[0] + (C_OCEAN_BOT[0] - C_OCEAN_TOP[0]) * t)
        g = int(C_OCEAN_TOP[1] + (C_OCEAN_BOT[1] - C_OCEAN_TOP[1]) * t)
        b = int(C_OCEAN_TOP[2] + (C_OCEAN_BOT[2] - C_OCEAN_TOP[2]) * t)
        DRAW.line([(0, y), (W, y)], fill=(r, g, b))


def draw_ocean_waves():
    random.seed(77)
    for _ in range(600):
        x = random.randint(0, W)
        y = random.randint(0, H)
        length = random.randint(3, 14)
        shade = random.randint(8, 30)
        DRAW.line([(x, y), (x + length, y)],
                  fill=(15 + shade, 35 + shade, 55 + shade), width=1)


# ============================================================
# Материки
# ============================================================

def draw_landmass(points, fill, dark=None, border=None, border_w=2):
    smooth = smooth_closed(points, 16)
    DRAW.polygon(smooth, fill=fill)
    if dark:
        cx = sum(p[0] for p in points) / len(points)
        cy = sum(p[1] for p in points) / len(points)
        inner = [(cx + (p[0]-cx)*0.65, cy + (p[1]-cy)*0.65) for p in smooth]
        DRAW.polygon(inner, fill=dark)
    if border:
        DRAW.line(smooth + [smooth[0]], fill=border, width=border_w)
    return smooth


def draw_island(cx, cy, rx, ry, fill, dark=None, border=None, seed=42):
    random.seed(seed)
    points = []
    n = 24
    for i in range(n):
        angle = 2 * math.pi * i / n
        noise = random.uniform(0.75, 1.2)
        x = cx + rx * noise * math.cos(angle)
        y = cy + ry * noise * math.sin(angle)
        points.append((x, y))
    return draw_landmass(points, fill, dark, border)


# ============================================================
# Рельеф
# ============================================================

def draw_mountain(x, y, size, snow=False, volcanic=False):
    w = size * 0.75
    if volcanic:
        DRAW.polygon([(x, y - size), (x - w, y), (x + w, y)], fill=C_VOLCANIC)
        DRAW.polygon([(x, y - size), (x, y), (x + w, y)], fill=(55, 28, 22))
        DRAW.ellipse([x - 3, y - size - 3, x + 3, y - size + 2], fill=C_LAVA)
    else:
        DRAW.polygon([(x, y - size), (x - w, y), (x + w, y)], fill=C_MTN)
        DRAW.polygon([(x, y - size), (x, y), (x + w, y)], fill=C_MTN_DARK)
        if snow:
            sw = size * 0.4
            DRAW.polygon([(x, y - size),
                          (x - sw, y - size * 0.5),
                          (x + sw, y - size * 0.5)], fill=C_SNOW)


def draw_mountain_range(path_points, count=25, size_range=(10, 18),
                        snow=False, volcanic=False, seed=42):
    random.seed(seed)
    for i in range(count):
        t = i / max(count - 1, 1)
        idx = int(t * (len(path_points) - 1))
        px, py = path_points[idx]
        ox = random.randint(-18, 18)
        oy = random.randint(-10, 10)
        size = random.randint(*size_range)
        draw_mountain(px + ox, py + oy, size, snow, volcanic)


def draw_tree(x, y, size=5):
    DRAW.polygon([(x, y - size), (x - size*0.5, y), (x + size*0.5, y)],
                 fill=C_FOREST)
    DRAW.polygon([(x, y - size*1.4), (x - size*0.4, y - size*0.3),
                  (x + size*0.4, y - size*0.3)], fill=C_FOREST_LIGHT)


def draw_forest(cx, cy, count=45, radius=75, seed=42):
    random.seed(seed)
    for _ in range(count):
        angle = random.uniform(0, 2 * math.pi)
        r = random.uniform(0, radius) ** 0.7
        x = cx + r * math.cos(angle)
        y = cy + r * math.sin(angle)
        draw_tree(x, y, random.randint(4, 7))


def draw_river(points, width=2):
    smooth = smooth_open(points, 10)
    DRAW.line(smooth, fill=C_RIVER, width=width)
    DRAW.line(smooth, fill=C_RIVER_WIDE, width=max(1, width - 1))


def draw_swamp(cx, cy, count=30, radius=65, seed=42):
    random.seed(seed)
    for _ in range(count):
        angle = random.uniform(0, 2 * math.pi)
        r = random.uniform(0, radius)
        x = cx + r * math.cos(angle)
        y = cy + r * math.sin(angle)
        if random.random() < 0.45:
            wlen = random.randint(4, 12)
            DRAW.line([(x, y), (x + wlen, y)], fill=(55, 75, 95), width=1)
        else:
            DRAW.ellipse([x - 2, y - 2, x + 2, y + 2], fill=C_SWAMP)


def draw_desert(cx, cy, count=50, radius=80, seed=42):
    random.seed(seed)
    for _ in range(count):
        angle = random.uniform(0, 2 * math.pi)
        r = random.uniform(0, radius)
        x = cx + r * math.cos(angle)
        y = cy + r * math.sin(angle)
        c = C_DESERT if random.random() < 0.6 else C_DESERT_DARK
        DRAW.ellipse([x - 3, y - 2, x + 3, y + 2], fill=c)


def draw_tundra(cx, cy, count=35, radius=70, seed=42):
    random.seed(seed)
    for _ in range(count):
        angle = random.uniform(0, 2 * math.pi)
        r = random.uniform(0, radius)
        x = cx + r * math.cos(angle)
        y = cy + r * math.sin(angle)
        shade = random.randint(-15, 15)
        c = (max(0, C_TUNDRA[0] + shade),
             max(0, C_TUNDRA[1] + shade),
             max(0, C_TUNDRA[2] + shade))
        DRAW.ellipse([x - 3, y - 2, x + 3, y + 2], fill=c)


# ============================================================
# Границы империй (пунктир)
# ============================================================

def draw_dashed_line(p1, p2, dash=9, gap=6, width=2, color=C_BORDER_DASH):
    dx = p2[0] - p1[0]
    dy = p2[1] - p1[1]
    dist = math.sqrt(dx * dx + dy * dy)
    if dist == 0:
        return
    dx /= dist
    dy /= dist
    pos = 0
    while pos < dist:
        end = min(pos + dash, dist)
        DRAW.line([(p1[0] + dx * pos, p1[1] + dy * pos),
                   (p1[0] + dx * end, p1[1] + dy * end)],
                  fill=color, width=width)
        pos = end + gap


def draw_dashed_path(points, dash=9, gap=6, width=2, color=C_BORDER_DASH):
    for i in range(len(points) - 1):
        draw_dashed_line(points[i], points[i + 1], dash, gap, width, color)


# ============================================================
# Внутренние моря
# ============================================================

def draw_inland_sea(cx, cy, rx, ry, seed=42):
    random.seed(seed)
    points = []
    n = 28
    for i in range(n):
        angle = 2 * math.pi * i / n
        noise = random.uniform(0.7, 1.25)
        x = cx + rx * noise * math.cos(angle)
        y = cy + ry * noise * math.sin(angle)
        points.append((x, y))
    smooth = smooth_closed(points, 12)
    DRAW.polygon(smooth, fill=C_SHALLOW)
    DRAW.line(smooth + [smooth[0]], fill=(40, 70, 95), width=2)


# ============================================================
# Метки
# ============================================================

def draw_empire_marker(x, y, number, short, color, font_n, font_l):
    r = 20
    DRAW.ellipse([x - r, y - r, x + r, y + r], fill=color,
                 outline=C_TEXT_WHITE, width=2)
    DRAW.ellipse([x - r + 3, y - r + 3, x + r - 3, y + r - 3],
                 outline=C_TEXT_WHITE, width=1)
    bbox = DRAW.textbbox((0, 0), str(number), font=font_n)
    tw = bbox[2] - bbox[0]
    th = bbox[3] - bbox[1]
    DRAW.text((x - tw // 2, y - th // 2 - 2), str(number),
              fill=C_TEXT_WHITE, font=font_n)
    bbox = DRAW.textbbox((0, 0), short, font=font_l)
    tw = bbox[2] - bbox[0]
    DRAW.text((x - tw // 2, y + r + 5), short, fill=color, font=font_l)


def draw_academy(x, y):
    """Золотая звезда — Академия Барстон."""
    outer = 26
    inner = 11
    points = []
    for i in range(10):
        angle = math.pi / 2 + i * math.pi / 5
        r = outer if i % 2 == 0 else inner
        points.append((x + r * math.cos(angle), y - r * math.sin(angle)))
    DRAW.polygon(points, fill=C_ACADEMY, outline=(180, 130, 30), width=2)
    DRAW.ellipse([x - 7, y - 7, x + 7, y + 7], fill=(180, 130, 30))
    DRAW.ellipse([x - 4, y - 4, x + 4, y + 4], fill=C_ACADEMY)


# ============================================================
# Компас, заголовок, легенда
# ============================================================

def draw_compass():
    cx, cy = W - 110, 110
    r = 55
    DRAW.ellipse([cx - r, cy - r, cx + r, cy + r],
                 outline=C_COMPASS, width=2)
    DRAW.ellipse([cx - r + 5, cy - r + 5, cx + r - 5, cy + r - 5],
                 outline=C_COMPASS, width=1)
    DRAW.polygon([(cx, cy - r + 8), (cx - 9, cy), (cx + 9, cy)],
                 fill=C_TEXT_RED)
    DRAW.polygon([(cx, cy + r - 8), (cx - 7, cy), (cx + 7, cy)],
                 fill=C_COMPASS)
    f = font(15, bold=True)
    DRAW.text((cx - 6, cy - r - 20), "C", fill=C_TEXT_RED, font=f)
    DRAW.text((cx - 5, cy + r + 6), "Ю", fill=C_COMPASS, font=f)
    DRAW.text((cx - r - 20, cy - 8), "З", fill=C_COMPASS, font=f)
    DRAW.text((cx + r + 9, cy - 8), "В", fill=C_COMPASS, font=f)


def draw_title():
    f_title = font(44, bold=True)
    f_sub = font(18)
    title = "КАРТА МИРА ЭРДОС"
    bbox = DRAW.textbbox((0, 0), title, font=f_title)
    tw = bbox[2] - bbox[0]
    DRAW.text((W // 2 - tw // 2, 22), title, fill=C_TEXT_GOLD, font=f_title)
    sub = "Десять Империй Эрдосии  •  Территория Ур-Эдем  •  Морнар"
    bbox = DRAW.textbbox((0, 0), sub, font=f_sub)
    tw = bbox[2] - bbox[0]
    DRAW.text((W // 2 - tw // 2, 72), sub, fill=C_TEXT, font=f_sub)


def draw_legend():
    f = font(13)
    x, y = 35, H - 165
    DRAW.rectangle([x - 12, y - 12, x + 270, y + 150],
                   fill=(15, 22, 35), outline=C_COMPASS, width=1)
    DRAW.text((x, y), "ЛЕГЕНДА", fill=C_TEXT_GOLD, font=font(14, bold=True))
    y += 26
    items = [
        ("Эрдосия (восток)", C_LAND),
        ("Морнар (запад)", C_MORNER),
        ("Ур-Эдем (ничейная)", C_UR_EDEM),
        ("Мировой Океан", C_OCEAN_BOT),
        ("Горы", C_MTN),
        ("Леса", C_FOREST),
        ("Пустыни", C_DESERT),
    ]
    for label, color in items:
        DRAW.rectangle([x, y, x + 16, y + 14], fill=color, outline=C_COMPASS)
        DRAW.text((x + 23, y - 2), label, fill=C_TEXT, font=f)
        y += 19
    # Академия
    DRAW.polygon([(x + 8, y), (x + 4, y + 8), (x + 12, y + 8)],
                 fill=C_ACADEMY, outline=(180, 130, 30))
    DRAW.text((x + 23, y - 2), "Академия Барстон", fill=C_TEXT_GOLD, font=f)


# ============================================================
# КОНТРОЛЬНЫЕ ТОЧКИ МАТЕРИКОВ
# ============================================================

# Эрдосия — по часовой стрелке с севера, с полуостровом Квентора на юге
ERDOSIA_PTS = [
    (1100, 100), (1250, 80), (1400, 105), (1510, 190),
    (1575, 330), (1600, 470), (1585, 600), (1510, 740),
    (1410, 840), (1320, 905), (1260, 935),
    # Полуостров Квентора
    (1290, 1000), (1305, 1075), (1270, 1130), (1230, 1130),
    (1195, 1075), (1170, 1000), (1140, 940),
    # Возврат к берегу
    (1060, 920), (970, 880), (910, 810), (855, 710),
    (815, 600), (805, 480), (830, 360), (900, 240), (990, 150),
]

# Морнар
MORNAR_PTS = [
    (250, 100), (370, 120), (445, 230), (475, 370),
    (470, 500), (475, 620), (440, 750), (360, 850),
    (260, 880), (160, 850), (85, 760), (55, 620),
    (55, 400), (85, 250), (155, 135),
]

# Ур-Эдем — перешеек
UR_EDEM_PTS = [
    (500, 360), (570, 330), (650, 315), (730, 335),
    (770, 390), (775, 480), (770, 560), (735, 620),
    (660, 645), (570, 655), (500, 625), (475, 560),
    (475, 480), (480, 400),
]


# ============================================================
# ГЛАВНАЯ ФУНКЦИЯ
# ============================================================

def main():
    # 1. Океан
    draw_ocean()
    draw_ocean_waves()

    # 2. Морнар (запад)
    draw_landmass(MORNAR_PTS, C_MORNER, C_MORNER_DARK, (90, 45, 35), 2)
    draw_mountain_range([(150, 300), (250, 350), (350, 300)],
                        count=15, size_range=(12, 20), seed=201)
    draw_mountain_range([(180, 600), (280, 650), (380, 600)],
                        count=12, size_range=(10, 16), seed=202)
    random.seed(203)
    for _ in range(60):
        x = random.randint(80, 440)
        y = random.randint(150, 830)
        shade = random.randint(-12, 12)
        DRAW.ellipse([x - 4, y - 3, x + 4, y + 3],
                     fill=(max(0, C_MORNER_DARK[0] + shade),
                           max(0, C_MORNER_DARK[1] + shade),
                           max(0, C_MORNER_DARK[2] + shade)))

    # 3. Ур-Эдем (перешеек)
    draw_landmass(UR_EDEM_PTS, C_UR_EDEM, C_UR_EDEM_DARK, (110, 50, 65), 2)
    draw_inland_sea(620, 470, 55, 35, seed=301)
    draw_inland_sea(540, 580, 30, 20, seed=302)
    draw_swamp(680, 420, count=25, radius=45, seed=303)
    draw_swamp(530, 430, count=20, radius=35, seed=304)
    random.seed(305)
    for _ in range(20):
        x = random.randint(490, 760)
        y = random.randint(340, 640)
        r = random.randint(3, 12)
        c = random.choice([(75, 35, 50), (85, 40, 55), (60, 28, 40)])
        DRAW.ellipse([x - r, y - r, x + r, y + r], fill=c)

    # 4. Эрдосия (восток)
    draw_landmass(ERDOSIA_PTS, C_LAND, C_LAND_DARK, (100, 80, 55), 2)

    # 5. Внутренние моря Эрдосии
    draw_inland_sea(1330, 220, 45, 30, seed=401)  # Северное
    draw_inland_sea(1180, 850, 55, 35, seed=402)  # Южное
    draw_inland_sea(1200, 500, 35, 22, seed=403)  # Центральное озеро

    # 6. Острова Морканта — два больших, соединённых тонкой полосой
    draw_island(740, 950, 75, 60, C_LAND, C_LAND_DARK, (100, 80, 55), seed=501)
    draw_island(640, 1050, 65, 55, C_LAND, C_LAND_DARK, (100, 80, 55), seed=502)
    DRAW.line([(700, 990), (675, 1020)], fill=C_LAND, width=12)
    DRAW.line([(700, 990), (675, 1020)], fill=C_LAND_DARK, width=6)
    draw_swamp(740, 950, count=30, radius=55, seed=503)
    draw_swamp(640, 1050, count=25, radius=45, seed=504)

    # 7. Острова Квентора
    draw_island(1150, 1170, 35, 25, C_LAND, C_LAND_DARK, (100, 80, 55), seed=601)
    draw_island(1340, 1150, 30, 22, C_LAND, C_LAND_DARK, (100, 80, 55), seed=602)
    draw_island(1240, 1185, 22, 18, C_LAND, None, (100, 80, 55), seed=603)
    draw_forest(1250, 1080, count=35, radius=55, seed=604)

    # 8. Рельеф по империям

    # [1] Ксалорийская (СВ) — тундра, снежные горы
    draw_tundra(1430, 180, count=40, radius=80, seed=101)
    draw_mountain_range([(1380, 140), (1430, 160), (1480, 180), (1520, 220)],
                        count=18, size_range=(12, 20), snow=True, seed=102)
    draw_forest(1380, 250, count=12, radius=40, seed=103)

    # [2] Велтигерская (С) — горы
    draw_mountain_range([(1050, 160), (1150, 140), (1250, 150), (1330, 170)],
                        count=22, size_range=(12, 20), seed=104)
    draw_mountain_range([(1100, 230), (1200, 220), (1280, 240)],
                        count=15, size_range=(10, 16), seed=105)

    # [3] Глорантская Лига (СЗ) — Великий Лес
    draw_forest(930, 280, count=60, radius=85, seed=106)
    draw_forest(880, 380, count=40, radius=60, seed=107)
    draw_mountain_range([(850, 250), (900, 270), (950, 250)],
                        count=10, size_range=(8, 14), seed=108)

    # [4] Ферросская Держава (В) — вулканы
    draw_mountain_range([(1530, 350), (1560, 420), (1575, 490), (1550, 560)],
                        count=18, size_range=(12, 18), volcanic=True, seed=109)
    draw_desert(1520, 430, count=25, radius=50, seed=110)

    # [5] Тарвеш (Центр) — равнины, реки
    draw_river([(1200, 240), (1210, 320), (1195, 400),
                (1205, 480), (1190, 560), (1185, 640),
                (1170, 720), (1150, 800)], width=3)
    draw_river([(950, 350), (1000, 400), (1050, 450),
                (1100, 490), (1150, 510)], width=2)
    draw_river([(1200, 400), (1260, 430), (1320, 460),
                (1380, 490), (1440, 520)], width=2)
    draw_forest(1100, 380, count=15, radius=45, seed=111)
    draw_forest(1280, 580, count=12, radius=35, seed=112)

    # [6] Ишкарский Доминион (З) — скалы
    draw_mountain_range([(830, 450), (850, 520), (840, 590), (855, 650)],
                        count=16, size_range=(10, 16), seed=113)
    draw_desert(850, 550, count=20, radius=45, seed=114)

    # [7] Моркантское Королевство (ЮЗ) — болота
    draw_swamp(920, 780, count=35, radius=65, seed=115)
    draw_swamp(970, 850, count=30, radius=55, seed=116)
    draw_river([(900, 700), (920, 760), (940, 820), (960, 870)], width=2)
    draw_forest(880, 750, count=10, radius=35, seed=117)

    # [8] Зенгембийское Царство (ЮВ) — плато
    draw_mountain_range([(1480, 680), (1520, 720), (1540, 770), (1500, 810)],
                        count=14, size_range=(10, 16), seed=118)
    draw_desert(1490, 750, count=20, radius=45, seed=119)

    # [9] Дравольская Империя (Юг) — пустыни
    draw_desert(1280, 800, count=55, radius=90, seed=120)
    draw_desert(1350, 850, count=40, radius=70, seed=121)
    draw_mountain_range([(1250, 760), (1300, 790), (1350, 810), (1400, 830)],
                        count=12, size_range=(10, 16), seed=122)
    draw_forest(1300, 830, count=8, radius=20, seed=123)
    draw_forest(1370, 860, count=6, radius=15, seed=124)

    # [10] Квенторийский Союз (Ю) — джунгли
    draw_forest(1250, 1050, count=50, radius=70, seed=125)
    draw_forest(1200, 980, count=30, radius=50, seed=126)
    draw_river([(1230, 950), (1245, 1020), (1255, 1080), (1250, 1130)], width=2)

    # 9. Границы империй
    borders = [
        [(1350, 110), (1360, 200), (1340, 280)],          # Ксалор | Велтигер
        [(1030, 130), (1010, 220), (980, 300)],            # Велтигер | Глорант
        [(840, 380), (830, 450), (835, 520)],              # Глорант | Ишкар
        [(920, 480), (970, 510), (1020, 540)],             # Ишкар | Тарвеш
        [(1380, 400), (1390, 480), (1380, 560)],           # Тарвеш | Ферросс
        [(1530, 620), (1520, 680), (1500, 730)],           # Ферросс | Зенгемба
        [(1420, 820), (1400, 860), (1370, 890)],           # Зенгемба | Драволь
        [(1230, 900), (1220, 940), (1210, 970)],           # Драволь | Квентор
        [(1080, 880), (1120, 890), (1160, 895)],           # Моркант | Драволь
        [(870, 680), (880, 720), (890, 760)],              # Моркант | Ишкар
    ]
    for path in borders:
        draw_dashed_path(path)

    # 10. Метки империй
    font_n = font(16, bold=True)
    font_l = font(13)
    empires = [
        (1440, 180, 1, "Ксалор", "#aaccff"),
        (1190, 170, 2, "Велтигер", "#cc9966"),
        (930, 300, 3, "Глорант", "#66cc66"),
        (1540, 450, 4, "Ферросс", "#ff8844"),
        (1190, 500, 5, "Тарвеш", "#cc88ff"),
        (860, 550, 6, "Ишкар", "#cc6666"),
        (930, 820, 7, "Моркант", "#4488cc"),
        (1500, 720, 8, "Зенгемба", "#88ccff"),
        (1320, 830, 9, "Драволь", "#ccaa44"),
        (1250, 1020, 10, "Квентор", "#ffdd44"),
    ]
    for x, y, num, short, color in empires:
        draw_empire_marker(x, y, num, short, color, font_n, font_l)

    # 11. Академия Барстон
    draw_academy(1220, 470)
    f_acad = font(12, bold=True)
    DRAW.text((1245, 465), "Академия Барстон", fill=C_ACADEMY, font=f_acad)

    # 12. Подписи океана
    f_ocean = font(22)
    DRAW.text((680, 180), "Мировой Океан", fill=C_TEXT_BLUE, font=f_ocean)
    DRAW.text((680, 950), "Мировой Океан", fill=C_TEXT_BLUE, font=f_ocean)

    # 13. Подписи материков
    f_cont = font(26, bold=True)
    DRAW.text((1140, 940), "ЭРДОСИЯ", fill=C_TEXT_GREEN, font=f_cont)
    DRAW.text((200, 100), "МОРНАР", fill=C_TEXT_RED, font=f_cont)

    # 14. Подпись Ур-Эдем
    f_ur = font(15, bold=True)
    ur_text = "Ур-Эдем"
    bbox = DRAW.textbbox((0, 0), ur_text, font=f_ur)
    tw = bbox[2] - bbox[0]
    DRAW.text((620 - tw // 2, 510), ur_text, fill=(200, 110, 130), font=f_ur)
    DRAW.text((620 - 45, 530), "(ничейная)", fill=(160, 80, 100), font=font(11))

    # 15. Подписи внутренних морей
    f_sea = font(12)
    DRAW.text((1310, 215), "Северное", fill=C_TEXT_BLUE, font=f_sea)
    DRAW.text((1310, 230), "Море", fill=C_TEXT_BLUE, font=f_sea)
    DRAW.text((1160, 845), "Южное", fill=C_TEXT_BLUE, font=f_sea)
    DRAW.text((1160, 860), "Море", fill=C_TEXT_BLUE, font=f_sea)

    # 16. Подпись Морнар
    f_demon = font(14)
    DRAW.text((190, 500), "Земли", fill=C_TEXT_RED, font=f_demon)
    DRAW.text((190, 518), "Демонов", fill=C_TEXT_RED, font=f_demon)
    DRAW.text((180, 540), "Владения", fill=(160, 50, 45), font=f_demon)
    DRAW.text((190, 558), "Морны", fill=(160, 50, 45), font=f_demon)

    # 17. Подписи географических объектов
    f_geo = font(11)
    DRAW.text((1100, 120), "Ледяной Хребет", fill=C_TEXT_WHITE, font=f_geo)
    DRAW.text((1530, 370), "Огненные Горы", fill=C_TEXT_RED, font=f_geo)
    DRAW.text((1280, 770), "Каменный Пояс", fill=C_TEXT_WHITE, font=f_geo)
    DRAW.text((900, 260), "Великий Лес", fill=C_TEXT_GREEN, font=f_geo)
    DRAW.text((1180, 370), "Река Тарвеш", fill=C_TEXT_BLUE, font=f_geo)
    DRAW.text((900, 800), "Болота Морканта", fill=C_TEXT_BLUE, font=f_geo)
    DRAW.text((1280, 990), "Джунгли Квентора", fill=C_TEXT_GREEN, font=f_geo)

    # 18. Компас
    draw_compass()

    # 19. Заголовок
    draw_title()

    # 20. Легенда
    draw_legend()

    # 21. Рамка
    DRAW.rectangle([5, 5, W - 6, H - 6], outline=C_COMPASS, width=3)
    DRAW.rectangle([10, 10, W - 11, H - 11], outline=(90, 75, 50), width=1)

    # Сохранение
    out = "fludilka_chat_pantikur/akademia_barston/lore/map_erdos.png"
    IMG.save(out, "PNG")
    print(f"Map saved: {out}")
    print(f"Size: {W}x{H}")


if __name__ == "__main__":
    main()
