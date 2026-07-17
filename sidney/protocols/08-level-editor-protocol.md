# Протокол 8: Протокол Редактора Уровней

## Назначение
Инструмент для создания игрового мира, размещения объектов и настройки сцен.

## Компоненты

### 1. WYSIWYG Редактор
- **3D Viewport:** Интерактивный 3D вид с orbit/first-person камерой
- **Scene Tree:** Древовидная иерархия объектов сцены
- **Property Editor:** Настройка параметров выбранного объекта
- **Grid Snapping:** Привязка к сетке (позиция, поворот, масштаб)

### 2. Инструменты размещения
- **Object Placement:** Drag & drop объектов из библиотеки
- **Prefab System:** Шаблоны объектов и сцен
- **Batch Operations:** Массовое редактирование
- **Undo/Redo:** История изменений (неограниченная)

### 3. Ландшафт и окружение
- **Terrain Editor:** Рисование рельефа, текстур ландшафта
- **Water System:** Настройка водоёмов (реки, озёра, океаны)
- **Sky System:** День/ночь, погода, сезоны
- **Fog & Atmosphere:** Настройка видимости и атмосферы

### 4. Освещение
- **Light Placement:** Directional, point, spot, area lights
- **Light Baking:** Предварительный расчёт освещения (lightmaps)
- **Reflection Probes:** Зоны отражений
- **Exposure Control:** Настройка HDR и tone mapping

### 5. Экспорт и импорт
- **Scene Export:** .sidney, .json, .xml форматы
- **Asset Import:** FBX, glTF, OBJ, PNG, OGG
- **Packaging:** Сборка в run-time формат
- **Version Control:** Интеграция с Git, SVN

### 6. Многопользовательское редактирование
- **Collaborative Editing:** Несколько редакторов одновременно
- **Conflict Resolution:** Автоматическое разрешение конфликтов
- **Review Mode:** Проверка изменений другими

## API
```python
# Инициализация редактора
sidney.engine.editor.init(width=1920, height=1080, mode="editor")

# Создание новой сцены
scene = sidney.engine.editor.create_scene("level_01")

# Размещение объектов
tree = scene.place_prefab("prefabs/tree_oak", position=(5, 0, 3))
rock = scene.place_object("models/rock_01.fbx", position=(-2, 0, 7))
npc = scene.place_prefab("prefabs/guard", position=(0, 0, 0))

# Настройка ландшафта
terrain = scene.create_terrain(size=1000, resolution=513)
terrain.set_heightmap("heightmaps/level_01.png")
terrain.set_texture(0, "textures/grass.png", weight=0.8)
terrain.set_texture(1, "textures/rock.png", weight=0.4)

# Освещение
sun = scene.add_light("directional", position=(100, 200, 50), color=(1.0, 0.9, 0.7))
scene.set_time_of_day(hour=14, minute=30)

# Настройка физики
scene.set_physics_settings(gravity=(0, -9.81, 0), max_substeps=4)

# Настройка ИИ
spawn_point = scene.add_spawn_point("enemy", position=(20, 0, -10), count=5)
navmesh = scene.generate_navmesh(agent_radius=0.5)

# Экспорт
scene.export("levels/level_01.sidney")

# Шаг редактора
sidney.engine.editor.step(dt=1/60)
```

## Оптимизация
- Deferred loading крупных ассетов
- Streaming текстур по запросу
- Level of Detail автоматическая генерация
- Culling для редактора

## Статус: Инициализирован ✓
