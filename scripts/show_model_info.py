# python3 show_model_info.py

import torch
import os
import sys
import glob

# Расширения файлов моделей, которые ищем
MODEL_EXTS = (".pth", ".pt", ".bin", ".safetensors", ".ckpt")

# Директории для поиска (текущая + типичные пути на сервере Timeweb)
SEARCH_DIRS = [
    os.getcwd(),
    os.path.expanduser("~"),
    "/home",
    "/var/www",
    "/opt",
]


def find_model():
    """Находит файл чат-модели: из аргумента, переменной окружения или поиском по диску."""
    # 1. Путь передан аргументом командной строки
    if len(sys.argv) > 1:
        candidate = sys.argv[1]
        if os.path.isfile(candidate):
            return candidate
        print(f"⚠️ Файл из аргумента не найден: {candidate}")

    # 2. Путь из переменной окружения
    env_path = os.environ.get("CHAT_MODEL_PATH")
    if env_path and os.path.isfile(env_path):
        return env_path

    # 3. Автопоиск по директориям
    print("🔍 Поиск файла модели...")
    found = []
    for base in SEARCH_DIRS:
        if not os.path.isdir(base):
            continue
        for ext in MODEL_EXTS:
            # ищем рекурсивно, но ограничиваем глубину чтобы не зависнуть
            for path in glob.glob(os.path.join(base, "**", f"*{ext}"), recursive=True):
                if os.path.isfile(path):
                    found.append(path)

    # убираем дубликаты, сортируем по размеру (самая крупная — вероятно модель)
    found = sorted(set(found), key=lambda p: os.path.getsize(p), reverse=True)

    if not found:
        return None

    if len(found) > 1:
        print("\n📁 Найдено несколько файлов моделей:")
        for i, p in enumerate(found):
            mb = os.path.getsize(p) / (1024 * 1024)
            print(f"  [{i}] {p}  ({mb:.2f} МБ)")
        print("\n(Используется самый крупный. Чтобы выбрать другой, "
              "запустите: python3 show_model_info.py <путь>)\n")

    return found[0]


# Поиск модели
PATH = find_model()
if not PATH:
    print("❌ Файл чат-модели не найден.")
    print("Укажите путь явно: python3 show_model_info.py /путь/к/chatmodel.pth")
    sys.exit(1)

print(f"✅ Используется модель: {PATH}")

# 1. Размер файла
size_bytes = os.path.getsize(PATH)
size_mb = size_bytes / (1024 * 1024)
print(f"📦 Размер файла: {size_mb:.2f} МБ")

# 2. Загрузка checkpoint
print("\n📂 Загрузка модели...")
try:
    checkpoint = torch.load(PATH, map_location="cpu", weights_only=True)
except Exception as e:
    print(f"⚠️ torch не установлен или ошибка загрузки: {e}")
    sys.exit(1)

# 3. Структура / ключи
print("\n🔑 Ключи в модели:")
if isinstance(checkpoint, dict):
    for key, value in checkpoint.items():
        if isinstance(value, torch.Tensor):
            print(f"  {key}: Tensor {tuple(value.shape)}, dtype={value.dtype}")
        elif isinstance(value, dict):
            print(f"  {key}: dict ({len(value)} элементов)")
        else:
            print(f"  {key}: {type(value).__name__} = {value}")
else:
    print(f"  Не словарь, тип: {type(checkpoint).__name__}")

# 4. Общие параметры (если есть)
total_params = 0
if isinstance(checkpoint, dict):
    for key, value in checkpoint.items():
        if isinstance(value, torch.Tensor):
            total_params += value.numel()
    print(f"\n📊 Всего параметров: {total_params:,}")