# Протокол 7: Протокол Скриптовой Системы

## Назначение
Позволяет программировать игровую логику без глубокого знания низкоуровневых языков.

## Компоненты

### 1. Скриптовый движок
- **Lua Integration:** LuaJIT для производительности
- **Python Integration:** CPython для ML и инструментов
- **Custom DSL:** Domain-specific language для игровой логики
- **Bytecode Compilation:** Компиляция в байт-код

### 2. Визуальное программирование
- **Node-based Editor:** Визуальный редактор нод
- **Node Types:** Logic, math, input, output, flow control
- **Real-time Execution:** Тестирование без компиляции
- **Graph Optimization:** Компиляция графа в оптимизированный код

### 3. Система событий
- **Event System:** Observer pattern для событий
- **Delegates:** Сигналы и слоты
- **Timers:** Задержанные и циклические события
- **Game Events:** PlayerDeath, LevelStart, ItemPickup

### 4. Hot Reloading
- **Live Code Reload:** Изменение кода без перезапуска
- **State Preservation:** Сохранение состояния при перезагрузке
- **Error Recovery:** Откат при ошибках

### 5. API для скриптов
- **Game API:** Создание, удаление, модификация объектов
- **Physics API:** Взаимодействие с физическим движком
- **AI API:** Управление NPC поведением
- **Rendering API:** Программное создание эффектов

## API
```python
# Инициализация скриптовой системы
sidney.engine.scripting.init(engine="lua", sandbox=True)

# Выполнение Lua скрипта
sidney.engine.scripting.execute("""
    function on_player_spawn(player)
        player:set_health(100)
        player:add_item("sword_01")
    end
""")

# Выполнение Python скрипта
sidney.engine.scripting.execute_python("""
def on_update(delta_time):
    for npc in get_all_npcs():
        npc.update_ai(delta_time)
    apply_post_effects()
""")

# Визуальное программирование
graph = sidney.engine.scripting.create_visual_graph()
input_node = graph.add_node("Input", type="player_spawn")
action_node = graph.add_node("SetHealth", type="action")
graph.connect(input_node, "output", action_node, "input")
graph.compile()

# Система событий
def on_player_death(player, killer):
    print(f"Player {player} was killed by {killer}")
    award_experience(killer, 100)

sidney.engine.scripting.bind_event("PlayerDeath", on_player_death)

# Hot reload
sidney.engine.scripting.reload_scripts(watch_paths=["scripts/"])

# Создание игрового объекта через скрипт
entity = sidney.engine.scripting.create_entity({
    "name": "enemy_bot",
    "model": "models/bot.fbx",
    "health": 100,
    "speed": 3.5,
    "ai": "enemy_behavior"
})
```

## Оптимизация
- JIT компиляция (LuaJIT)
- Скриптовый байткод кэш
- Пакетная обработка событий
- Lazy evaluation для сложных выражений

## Статус: Инициализирован ✓
