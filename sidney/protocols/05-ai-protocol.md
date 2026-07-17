# Протокол 5: Протокол ИИ (Искусственного Интеллекта)

## Назначение
Контролирует поведение NPC, навигацию, поиск пути и принятие решений.

## Компоненты

### 1. Поведенческие системы
- **Behavior Trees:** Древовидная структура поведения с leaf nodes
- **State Machines:** Конечные автоматы для дискретных состояний
- **Utility AI:** Оценка действий по приоритету
- **GOAP (Goal Oriented Action Planning):** Планирование достижений целей

### 2. Навигация
- **NAV MESH:** Поверхность навигации для статических препятствий
- **A* Pathfinding:** Алгоритм поиска кратчайшего пути
- **RVO (Reciprocal Velocity Obstacles):** Избегание столкновений с другими NPC
- **Waypoint Systems:** Система контрольных точек
- **Dynamic Obstacle Avoidance:** Реакция на движущиеся препятствия

### 3. Принятие решений
- **Perception System:** Зрение, слух, датчики
- **Memory System:** Запоминание событий, мест, игроков
- **Decision Making:** Взвешенный выбор действий
- **Emotion System:** Влияние «эмоций» на поведение

### 4. Групповое поведение
- **Flocking:** Стая (separation, alignment, cohesion)
- **Formation:** Строенные формации
- **Roles:** Роли в группе (атакующий, защитник, поддержка)
- **Swarm Intelligence:** Коллективный интеллект

### 5. Обучаемый ИИ
- **Reinforcement Learning:** Обучение через вознаграждение
- **Neural Network Integration:** Подключение к ML моделям Fuyuki
- **Experience Replay:** Запоминание и анализ прошлого опыта
- **Adaptive Difficulty:** Подстройка сложности под игрока

## API
```python
# Инициализация ИИ системы
sidney.engine.ai.init(max_agents=256, navmesh_resolution=50)

# Создание NAV MESH
navmesh = sidney.engine.ai.create_navmesh(
    world_geometry=scene,
    agent_radius=0.5,
    agent_height=2.0
)

# Создание NPC
npc = sidney.engine.ai.create_agent(
    id="guard_01",
    position=(10, 0, 5),
    navmesh=navmesh
)

# Поведенческое дерево
bt = sidney.engine.ai.create_behavior_tree()
bt.root = sidney.engine.ai.composite("Selector")
bt.add_child("Patrol", sidney.engine.ai.action("move_to_waypoints", waypoints=patrol_points))
bt.add_child("Chase", sidney.engine.ai.sequence(
    sidney.engine.ai.condition("see_player"),
    sidney.engine.ai.action("move_to", target="player")
))
bt.add_child("Attack", sidney.engine.ai.action("attack", target="player"))
npc.set_behavior_tree(bt)

# Восприятие
npc.perception.set_sight(range=15, angle=90)
npc.perception.set_hearing(range=20, volume_threshold=50)

# Группа
squad = sidney.engine.ai.create_squad(leaders=[npc], formation="V")

# Шаг ИИ
sidney.engine.ai.step(dt=1/60)

# Получение решений
decisions = sidney.engine.ai.get_agent_decisions(npc)
```

## Оптимизация
- Spatial hashing для perception
- LOD ИИ (упрощение AI для далёких агентов)
- Async AI updates
- Shared navmesh queries

## Статус: Инициализирован ✓
