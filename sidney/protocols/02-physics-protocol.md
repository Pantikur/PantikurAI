# Протокол 2: Протокол Физического Движка

## Назначение
Управляет симуляцией физики, столкновениями и разрушениями в игровом мире.

## Компоненты

### 1. Физический движок
- **Rigid Body Dynamics:** Масса, инерция, силы, моменты
- **Collision Detection:** Broad phase (SAP), Narrow phase (GJK/EPA)
- **Collision Response:** Impulse-based resolution, contact constraints
- **Sleeping:** Автоматический переход неактивных тел в sleep

### 2. Гравитация и силы
- Настраиваемая гравитация (2D/3D, векторная)
- Силы сопротивления (drag, buoyancy)
- Ветер и турбулентность
- Кастомные силовые поля

### 3. Система разрушений
- **Fragmentation:** Разбивание объектов на фрагменты при столкновении
- **Crack propagation:** Генерация трещин
- **Destructible meshes:**预设 pontos разрушения
- **Deformation:** Вершинная деформация

### 4. Физику жидкостей
- SPH (Smoothed Particle Hydrodynamics)
- Grid-based fluid simulation
- Water simulation с wave propagation

### 5. Физику тканей и веревок
- Verlet integration для тканей
- Spring-mass system для веревок
- Collision with garments
- Cloth simulation на GPU

## API
```python
# Инициализация физического движка
sidney.engine.physics.init(gravity=(0, -9.81, 0), iterations=10)

# Создание физического тела
body = sidney.engine.physics.create_rigidbody(
    mass=5.0,
    shape="box",
    dimensions=(1, 2, 1),
    position=(0, 5, 0)
)

# Применение силы
body.apply_force((0, 100, 0), position=(0, 1, 0))

# Создание разрушаемого объекта
destructible = sidney.engine.physics.create_destructible(
    mesh="models/wall.fbx",
    fragments=64,
    fragility=0.7
)

# Симуляция жидкости
fluid = sidney.engine.physics.create_fluid(
    volume=100,
    viscosity=0.001,
    density=1000
)

# Физика ткани
cloth = sidney.engine.physics.create_cloth(
    resolution=(32, 32),
    material="fabric",
    pinned_edges=True
)

# Шаг физики
sidney.engine.physics.step(dt=1/60)

# Получение коллизий
collisions = sidney.engine.physics.get_collisions()
```

## Оптимизация
- Spatial partitioning (BVH, Octree, Grid)
- Continuous collision detection (CCD) опционально
- Parallel physics update (multithreading)
- Predictive collision (swept tests)

## Статус: Инициализирован ✓
