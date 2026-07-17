# Протокол 3: Протокол Аудиодвижка

## Назначение
Управляет звуковыми эффектами, музыкой, пространственным звуком и DSP-обработкой.

## Компоненты

### 1. Аудиоплеер
- Поддержка форматов: WAV, OGG, FLAC, MP3
- Streaming для больших файлов
- Буферизация и prefetch
- Мультитрек микширование

### 2. Пространственный звук
- HRTF (Head-Related Transfer Function)
- 3D позиционирование (position, velocity, orientation)
- Doppler effect
- Obstruction и occlusion

### 3. Система микширования
- Динамическое микширование (priority-based)
- Audio buses и groups
- Ducking (музыка приглушается при диалогах)
- Adaptive music (слоистая музыка)

### 4. DSP Эффекты
- Reverb (convolution, algorithmic)
- Echo/Delay
- Equalizer (parametric, graphical)
- Distortion, chorus, flanger, phaser
- Low-pass, high-pass, band-pass фильтры
- Compression, limiting

### 5. Процедурный звук
- Генерация звуков в реальном времени
- Synthesis (FM, wavetable, subtractive)
- Физически-обоснованные звуки (удары, трение)

## API
```python
# Инициализация аудио движка
sidney.engine.audio.init(samplerate=48000, channels=2, buffer_size=512)

# Загрузка звука
sfx = sidney.engine.audio.load_sound("sounds/explosion.ogg")
music = sidney.engine.audio.load_music("music/battle_theme.ogg")

# 3D звук
spatial_sound = sidney.engine.audio.create_spatial_sound(
    source=sfx,
    position=(5, 1, -3),
    attenuation=0.5,
    cone_angle=360
)

# Воспроизведение
sidney.engine.audio.play(spatial_sound)
sidney.engine.audio.set_volume(music, 0.7)
sidney.engine.audio.play_music(music, loop=True)

# DSP эффекты
reverb = sidney.engine.audio.create_reverb(
    room_size=0.8,
    damping=0.5,
    wet_level=0.3
)
sidney.engine.audio.apply_effect(spatial_sound, reverb)

# Адаптивная музыка
sidney.engine.audio.set_music_layer("battle_theme", "drums", 1.0)
sidney.engine.audio.set_music_layer("battle_theme", "bass", 0.8)
sidney.engine.audio.set_music_layer("battle_theme", "melody", 0.0)

# Шаг аудио
sidney.engine.audio.step(dt=1/60)
```

## Оптимизация
- Voice pooling и recyling
- Distance-based fade out
- LOD для звука (упрощение DSP на расстоянии)
- Async loading

## Статус: Инициализирован ✓
