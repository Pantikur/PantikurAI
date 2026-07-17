"""
Редактор уровней Сидни.
WYSIWYG редактор для создания игровых миров.
"""

import logging
import time
import json
from typing import Dict, List, Optional, Any, Tuple

logger = logging.getLogger("sidney.engine.editor")


class LevelEditorCore:
    """Ядро редактора уровней."""
    
    def __init__(self):
        self.is_initialized = False
        self.current_scene = None
        self.scenes: Dict[str, Any] = {}
        
        # Viewport
        self.viewport_width = 1920
        self.viewport_height = 1080
        self.camera_mode = "orbit"
        
        # Объекты сцены
        self.scene_objects: List[Dict[str, Any]] = []
        
        # Ландшафт
        self.terrain: Optional[Dict[str, Any]] = None
        
        # Освещение сцены
        self.scene_lights: List[Dict[str, Any]] = []
        self.time_of_day = 14.5  # 14:30
        
        # Undo/Redo
        self.undo_stack: List[Dict[str, Any]] = []
        self.redo_stack: List[Dict[str, Any]] = []
        
        # Префабы
        self.prefabs: Dict[str, Any] = {}
        
        # Экспорт
        self.export_formats = ["sidney", "json", "xml"]
        
        # Метрики
        self.stats = {
            "object_count": 0,
            "light_count": 0,
            "triangle_count": 0,
            "texture_memory_mb": 0,
            "last_save": None
        }
        
        logger.info("🏗️ LevelEditorCore создан")
    
    def initialize(self) -> bool:
        """Инициализация редактора уровней."""
        try:
            logger.info("  🏗️ Инициализация редактора уровней...")
            
            # Создание default сцены
            self.create_scene("default_level")
            
            # Добавление default префабов
            self.register_prefab("tree_oak", {
                "model": "models/tree_oak.fbx",
                "scale": (1, 1, 1),
                "category": "nature"
            })
            self.register_prefab("rock_01", {
                "model": "models/rock_01.fbx",
                "scale": (1, 1, 1),
                "category": "nature"
            })
            self.register_prefab("guard", {
                "model": "models/guard.fbx",
                "scale": (1, 1, 1),
                "category": "npc"
            })
            self.register_prefab("building_01", {
                "model": "models/building_01.fbx",
                "scale": (1, 1, 1),
                "category": "architecture"
            })
            
            self.is_initialized = True
            logger.info("  ✅ Редактор уровней инициализирован")
            return True
            
        except Exception as e:
            logger.error(f"  ❌ Ошибка инициализации: {e}")
            return False
    
    def create_scene(self, name: str) -> Dict[str, Any]:
        """Создание новой сцены."""
        scene = {
            "name": name,
            "objects": [],
            "lights": [],
            "spawn_points": [],
            "navmesh": None,
            "created_at": time.time(),
            "modified_at": time.time()
        }
        
        self.scenes[name] = scene
        self.current_scene = name
        
        logger.info(f"  📐 Сцена '{name}' создана")
        return scene
    
    def switch_scene(self, name: str) -> bool:
        """Переключение сцены."""
        if name in self.scenes:
            self.current_scene = name
            logger.info(f"  🔄 Сцена изменена на '{name}'")
            return True
        
        logger.error(f"  ❌ Сцена '{name}' не найдена")
        return False
    
    def place_prefab(self, prefab_name: str, position: Tuple[float, float, float] = (0, 0, 0),
                     rotation: Tuple[float, float, float] = (0, 0, 0),
                     scale: Tuple[float, float, float] = (1, 1, 1)) -> Dict[str, Any]:
        """Размещение префаба в сцене."""
        if self.current_scene not in self.scenes:
            logger.error("  ❌ Нет активной сцены")
            return {}
        
        if prefab_name not in self.prefabs:
            logger.error(f"  ❌ Префаб '{prefab_name}' не найден")
            return {}
        
        prefab = self.prefabs[prefab_name]
        obj_id = f"obj_{len(self.scenes[self.current_scene]['objects'])}"
        
        obj = {
            "id": obj_id,
            "prefab": prefab_name,
            "model": prefab["model"],
            "position": position,
            "rotation": rotation,
            "scale": scale,
            "category": prefab.get("category", "unknown"),
            "visible": True,
            "enabled": True
        }
        
        self.scenes[self.current_scene]["objects"].append(obj)
        self._push_undo({"action": "place", "object": obj})
        
        self.stats["object_count"] = len(self.scenes[self.current_scene]["objects"])
        logger.info(f"  📦 Префаб '{prefab_name}' размещён: pos={position}")
        return obj
    
    def place_object(self, model_path: str, position: Tuple[float, float, float] = (0, 0, 0),
                     category: str = "custom") -> Dict[str, Any]:
        """Размещение произвольного объекта."""
        if self.current_scene not in self.scenes:
            logger.error("  ❌ Нет активной сцены")
            return {}
        
        obj_id = f"obj_{len(self.scenes[self.current_scene]['objects'])}"
        
        obj = {
            "id": obj_id,
            "model": model_path,
            "position": position,
            "rotation": (0, 0, 0),
            "scale": (1, 1, 1),
            "category": category,
            "visible": True,
            "enabled": True
        }
        
        self.scenes[self.current_scene]["objects"].append(obj)
        self._push_undo({"action": "place", "object": obj})
        
        self.stats["object_count"] = len(self.scenes[self.current_scene]["objects"])
        logger.info(f"  📦 Объект '{model_path}' размещён: pos={position}")
        return obj
    
    def create_terrain(self, size: float = 1000, resolution: int = 513) -> Dict[str, Any]:
        """Создание ландшафта."""
        self.terrain = {
            "size": size,
            "resolution": resolution,
            "heightmap": None,
            "textures": [],
            "smoothness": 0.5,
            "detail_density": 0.8
        }
        
        if self.current_scene and self.current_scene in self.scenes:
            self.scenes[self.current_scene]["terrain"] = self.terrain
        
        logger.info(f"  🏔️ Ландшафт создан (size={size}, resolution={resolution})")
        return self.terrain
    
    def add_light(self, light_type: str, position: Tuple[float, float, float],
                  color: Tuple[float, float, float] = (1, 1, 1),
                  intensity: float = 1.0) -> Dict[str, Any]:
        """Добавление света в сцену."""
        if self.current_scene not in self.scenes:
            logger.error("  ❌ Нет активной сцены")
            return {}
        
        light = {
            "type": light_type,
            "position": position,
            "color": color,
            "intensity": intensity,
            "range": 50 if light_type == "point" else 200,
            "cast_shadows": True
        }
        
        self.scenes[self.current_scene]["lights"].append(light)
        self.scene_lights.append(light)
        self.stats["light_count"] = len(self.scene_lights)
        
        logger.info(f"  💡 Свет '{light_type}' добавлен: pos={position}")
        return light
    
    def set_time_of_day(self, hour: float, minute: float = 0):
        """Настройка времени суток."""
        self.time_of_day = hour + minute / 60
        
        # Автоматическая настройка цвета солнца
        if 6 <= self.time_of_day < 8:
            sun_color = (1.0, 0.6, 0.3)  # Рассвет
        elif 8 <= self.time_of_day < 17:
            sun_color = (1.0, 0.95, 0.9)  # День
        elif 17 <= self.time_of_day < 20:
            sun_color = (1.0, 0.5, 0.2)  # Закат
        else:
            sun_color = (0.2, 0.3, 0.6)  # Ночь
        
        logger.info(f"  🌅 Время суток: {hour}:{minute:02d} (sun_color={sun_color})")
    
    def add_spawn_point(self, entity_type: str, position: Tuple[float, float, float],
                        count: int = 1) -> Dict[str, Any]:
        """Добавление точки спавна."""
        if self.current_scene not in self.scenes:
            logger.error("  ❌ Нет активной сцены")
            return {}
        
        spawn = {
            "type": entity_type,
            "position": position,
            "count": count,
            "enabled": True
        }
        
        self.scenes[self.current_scene]["spawn_points"].append(spawn)
        logger.info(f"  📍 Точка спавна '{entity_type}': pos={position}, count={count}")
        return spawn
    
    def generate_navmesh(self, agent_radius: float = 0.5) -> Dict[str, Any]:
        """Генерация NAV MESH из геометрии сцены."""
        navmesh = {
            "agent_radius": agent_radius,
            "cells": [],
            "object_count": len(self.scenes[self.current_scene]["objects"]) if self.current_scene else 0
        }
        
        # Упрощённая генерация NAV MESH
        for obj in self.scenes[self.current_scene]["objects"]:
            navmesh["cells"].append({
                "center": obj["position"],
                "radius": 2.0,
                "walkable": True
            })
        
        if self.current_scene:
            self.scenes[self.current_scene]["navmesh"] = navmesh
        
        logger.info(f"  🗺️ NAV MESH сгенерирован: {len(navmesh['cells'])} ячеек")
        return navmesh
    
    def register_prefab(self, name: str, data: Dict[str, Any]):
        """Регистрация префаба."""
        self.prefabs[name] = data
        logger.info(f"  📦 Префаб '{name}' зарегистрирован")
    
    def _push_undo(self, action: Dict[str, Any]):
        """Добавление в undo стек."""
        self.undo_stack.append(action)
        if len(self.undo_stack) > 1000:
            self.undo_stack.pop(0)
    
    def export_scene(self, path: str, format: str = "sidney") -> bool:
        """Экспорт сцены."""
        if self.current_scene not in self.scenes:
            logger.error("  ❌ Нет активной сцены")
            return False
        
        scene_data = {
            "name": self.current_scene,
            "objects": self.scenes[self.current_scene]["objects"],
            "lights": self.scenes[self.current_scene]["lights"],
            "spawn_points": self.scenes[self.current_scene]["spawn_points"],
            "navmesh": self.scenes[self.current_scene].get("navmesh"),
            "exported_at": time.time(),
            "format": format
        }
        
        try:
            with open(path, 'w', encoding='utf-8') as f:
                if format == "json":
                    json.dump(scene_data, f, indent=2)
                else:
                    json.dump(scene_data, f, indent=2)  # Default to JSON
            
            self.stats["last_save"] = time.time()
            logger.info(f"  💾 Сцена экспортирована: {path} (format={format})")
            return True
            
        except Exception as e:
            logger.error(f"  ❌ Ошибка экспорта: {e}")
            return False
    
    def update(self, dt: float):
        """Обновление редактора."""
        if not self.is_initialized:
            return
        
        # Обновление метрик
        if self.current_scene and self.current_scene in self.scenes:
            self.stats["object_count"] = len(self.scenes[self.current_scene]["objects"])
            self.stats["light_count"] = len(self.scenes[self.current_scene]["lights"])
    
    def get_status(self) -> Dict[str, Any]:
        """Получение статуса редактора."""
        return {
            "status": "active" if self.is_initialized else "inactive",
            "current_scene": self.current_scene,
            "scenes": list(self.scenes.keys()),
            "prefabs": list(self.prefabs.keys()),
            "object_count": self.stats["object_count"],
            "light_count": self.stats["light_count"],
            "time_of_day": self.time_of_day,
            "undo_steps": len(self.undo_stack),
            "stats": self.stats
        }
