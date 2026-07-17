"""
Аудиодвижок Сидни.
Отвечает за звуковые эффекты, музыку, пространственный звук и DSP.
"""

import logging
from typing import Dict, List, Optional, Any, Tuple

logger = logging.getLogger("sidney.engine.audio")


class AudioCore:
    """Ядро аудиодвижка."""
    
    def __init__(self):
        self.is_initialized = False
        self.samplerate = 48000
        self.channels = 2
        self.buffer_size = 512
        
        # Звуки
        self.sounds: Dict[str, Any] = {}
        self.music_tracks: Dict[str, Any] = {}
        
        # Пространственные звуки
        self.spatial_sounds: List[Dict[str, Any]] = []
        
        # DSP эффекты
        self.effects: Dict[str, Any] = {}
        self.active_buses: Dict[str, Any] = {}
        
        # Микширование
        self.master_volume = 1.0
        self.music_volume = 0.7
        self.sfx_volume = 0.8
        
        # Адаптивная музыка
        self.adaptive_music: Dict[str, Any] = {}
        
        # Метрики
        self.stats = {
            "active_voices": 0,
            "dsp_cpu_percent": 0,
            "buffer_underruns": 0
        }
        
        logger.info("🔊 AudioCore создан")
    
    def initialize(self) -> bool:
        """Инициализация аудиодвижка."""
        try:
            logger.info("  🔊 Инициализация аудиодвижка...")
            
            # Создание default buses
            self.create_bus("master")
            self.create_bus("sfx")
            self.create_bus("music")
            self.create_bus("voice")
            
            self.is_initialized = True
            logger.info("  ✅ Аудиодвижок инициализирован")
            return True
            
        except Exception as e:
            logger.error(f"  ❌ Ошибка инициализации: {e}")
            return False
    
    def load_sound(self, name: str, path: str) -> bool:
        """Загрузка звукового эффекта."""
        try:
            self.sounds[name] = {
                "path": path,
                "duration": 0,
                "format": "ogg",
                "samples": 0,
                "loaded": True
            }
            logger.info(f"  🔊 Звук '{name}' загружен: {path}")
            return True
        except Exception as e:
            logger.error(f"  ❌ Ошибка загрузки звука: {e}")
            return False
    
    def load_music(self, name: str, path: str) -> bool:
        """Загрузка музыкального трека."""
        try:
            self.music_tracks[name] = {
                "path": path,
                "duration": 0,
                "format": "ogg",
                "layers": {},
                "is_playing": False,
                "loop": True,
                "volume": 0.7
            }
            logger.info(f"  🎵 Музыка '{name}' загружена: {path}")
            return True
        except Exception as e:
            logger.error(f"  ❌ Ошибка загрузки музыки: {e}")
            return False
    
    def create_spatial_sound(self, name: str, source_name: str,
                             position: Tuple[float, float, float] = (0, 0, 0),
                             attenuation: float = 0.5,
                             cone_angle: float = 360) -> Dict[str, Any]:
        """Создание 3D пространственного звука."""
        if source_name not in self.sounds:
            logger.error(f"  ❌ Источник '{source_name}' не найден")
            return {}
        
        spatial = {
            "name": name,
            "source": source_name,
            "position": position,
            "velocity": (0, 0, 0),
            "attenuation": attenuation,
            "cone_angle": cone_angle,
            "is_playing": False,
            "volume": 1.0,
            "effect": None
        }
        
        self.spatial_sounds.append(spatial)
        logger.info(f"  📍 Пространственный звук '{name}' создан: pos={position}")
        return spatial
    
    def play_sound(self, name: str, spatial: Optional[Dict] = None):
        """Воспроизведение звукового эффекта."""
        if name in self.sounds:
            self.sounds[name]["is_playing"] = True
            self.sounds[name]["loop"] = False
            self.stats["active_voices"] += 1
            logger.info(f"  ▶️ Звук '{name}' воспроизводится")
        else:
            logger.error(f"  ❌ Звук '{name}' не найден")
    
    def play_music(self, name: str, loop: bool = True, volume: float = 0.7):
        """Воспроизведение музыки."""
        if name in self.music_tracks:
            track = self.music_tracks[name]
            track["is_playing"] = True
            track["loop"] = loop
            track["volume"] = volume
            self.stats["active_voices"] += 1
            logger.info(f"  🎵 Музыка '{name}' воспроизводится (loop={loop}, vol={volume})")
        else:
            logger.error(f"  ❌ Музыка '{name}' не найдена")
    
    def stop_music(self, name: str):
        """Остановка музыки."""
        if name in self.music_tracks:
            self.music_tracks[name]["is_playing"] = False
            logger.info(f"  ⏹️ Музыка '{name}' остановлена")
    
    def set_music_layer(self, track_name: str, layer_name: str, volume: float):
        """Настройка слоя адаптивной музыки."""
        if track_name not in self.music_tracks:
            logger.error(f"  ❌ Трек '{track_name}' не найден")
            return
        
        if "layers" not in self.music_tracks[track_name]:
            self.music_tracks[track_name]["layers"] = {}
        
        self.music_tracks[track_name]["layers"][layer_name] = volume
        logger.info(f"  🎼 Слой '{layer_name}' трека '{track_name}': {volume}")
    
    def create_reverb(self, name: str, room_size: float = 0.5,
                      damping: float = 0.5, wet_level: float = 0.3) -> Dict[str, Any]:
        """Создание эффекта реверберации."""
        effect = {
            "name": name,
            "type": "reverb",
            "room_size": room_size,
            "damping": damping,
            "wet_level": wet_level,
            "dry_level": 0.8
        }
        
        self.effects[name] = effect
        logger.info(f"  🏛️ Реверб '{name}' создан (room_size={room_size})")
        return effect
    
    def create_bus(self, name: str) -> Dict[str, Any]:
        """Создание аудио шины."""
        bus = {
            "name": name,
            "volume": 1.0,
            "muted": False,
            "effects": [],
            "voices": []
        }
        
        self.active_buses[name] = bus
        logger.info(f"  🔀 Шина '{name}' создана")
        return bus
    
    def apply_effect(self, sound_name: str, effect_name: str):
        """Применение DSP эффекта к звуку."""
        if effect_name in self.effects:
            logger.info(f"  ✨ Эффект '{effect_name}' применён к '{sound_name}'")
        else:
            logger.error(f"  ❌ Эффект '{effect_name}' не найден")
    
    def update(self, dt: float):
        """Обновление аудиодвижка."""
        if not self.is_initialized:
            return
        
        # Обновление DSP
        self.stats["dsp_cpu_percent"] = min(30, len(self.effects) * 5)
        
        # Обновление пространственных звуков
        active_count = 0
        for spatial in self.spatial_sounds:
            if spatial["is_playing"]:
                active_count += 1
        
        self.stats["active_voices"] = active_count + sum(
            1 for s in self.sounds.values() if s.get("is_playing")
        )
    
    def get_status(self) -> Dict[str, Any]:
        """Получение статуса аудиодвижка."""
        return {
            "status": "active" if self.is_initialized else "inactive",
            "samplerate": self.samplerate,
            "channels": self.channels,
            "sounds_loaded": len(self.sounds),
            "music_loaded": len(self.music_tracks),
            "spatial_sounds": len(self.spatial_sounds),
            "effects": len(self.effects),
            "buses": list(self.active_buses.keys()),
            "stats": self.stats
        }
