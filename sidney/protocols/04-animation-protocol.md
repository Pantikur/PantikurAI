# Протокол 4: Протокол Системы Анимации

## Назначение
Обеспечивает движение персонажей и объектов, включая скелетную анимацию, морфинг и физику.

## Компоненты

### 1. Скелетная анимация
- **Skeleton:** Иерархия костей с forward kinematics
- **Animation Clips:** Последовательности поз (keyframe animation)
- **Animation Blending:** Плавное переключение между анимациями
- **Animation Layers:** Многослойная анимация (body, head, hands)
- **Inverse Kinematics (IK):** Two-bone IK, CCD IK, FABRIK

### 2. Морфинг (Blend Shapes)
- **Morph Targets:** Деформация меша по контрольным точкам
- **Facial Animation:** 50+ blend shapes для мимики
- **Lip Sync:** Автоматическая синхронизация с аудио
- **Weight Mixing:** Комбинирование нескольких морфов

### 3. Физика анимации
- **Hair Physics:** Симуляция волос (spring-based)
- **Cloth Physics:** Ткани, плащи,_flags
- **Accessory Physics:** Бижутерия, оружие, рюкзаки
- **Root Motion:** Позиция персонажа от анимации

### 4. Система ретаргетинга
- Перенос анимаций между разными скелетами
- Mapping костей (bone mapping)
- Adaptive retargeting (учёт пропорций)

### 5. State Machine
- Animation State Machine для управления состояниями
- Blend Trees для плавных переходов
- Event-based анимация (footstep, impact)

## API
```python
# Инициализация анимационной системы
sidney.engine.animation.init(skeleton_bones=128)

# Загрузка скелета и анимаций
skeleton = sidney.engine.animation.load_skeleton("models/character.skel")
anim_controller = sidney.engine.animation.create_controller(skeleton)

# Загрузка анимаций
run_anim = sidney.engine.animation.load_clip("animations/run.fbx")
idle_anim = sidney.engine.animation.load_clip("animations/idle.fbx")
attack_anim = sidney.engine.animation.load_clip("animations/attack.fbx")

# Настройка State Machine
state_machine = sidney.engine.animation.create_state_machine()
state_machine.add_state("idle", idle_anim)
state_machine.add_state("run", run_anim)
state_machine.add_state("attack", attack_anim)
state_machine.add_transition("idle", "run", condition="speed > 0.1")
state_machine.add_transition("run", "idle", condition="speed == 0")
state_machine.add_transition("idle", "attack", condition="attack_pressed")

# IK настройки
left_foot_ik = anim_controller.set_ik("left_foot", target=(0, 0.5, 0))
right_foot_ik = anim_controller.set_ik("right_foot", target=(0, 0.5, 0))

# Морфинг (лицо)
anim_controller.set_morph("smile", 0.8)
anim_controller.set_morph("surprise", 0.3)

# Физика волос
hair = sidney.engine.animation.create_hair_physics(
    skeleton=skeleton,
    bone_prefix="hair_",
    stiffness=0.7,
    damping=0.3
)

# Шаг анимации
sidney.engine.animation.step(dt=1/60, blend_time=0.15)

# События анимации
events = sidney.engine.animation.get_events()  # footstep, impact, etc.
```

## Оптимизация
- Animation compression
- LOD для анимации (упрощение IK на расстоянии)
- Animation culling (не рендерить анимацию для невидимых объектов)
- GPU skinning

## Статус: Инициализирован ✓
