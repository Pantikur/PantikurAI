"""
Графический движок Сидни.
Отвечает за 2D/3D рендеринг, текстуры, освещение и спецэффекты.
"""

import logging
from typing import Dict, List, Optional, Any, Tuple

logger = logging.getLogger("sidney.engine.renderers")


class RendererCore:
    """Ядро графического движка."""
    
    def __init__(self):
        self.is_initialized = False
        self.width = 1920
        self.height = 1080
        self.vsync = True
        self.target_fps = 60
        
        # Сцены
        self.scenes: Dict[str, Any] = {}
        self.current_scene = None
        
        # Ресурсы
        self.textures: Dict[str, Any] = {}
        self.meshes: Dict[str, Any] = {}
        self.materials: Dict[str, Any] = {}
        self.shaders: Dict[str, Any] = {}
        
        # Освещение
        self.lights: List[Dict[str, Any]] = []
        
        # Постобработка
        self.post_effects: List[str] = []
        
        # Гибридная система «полигон ↔ воксель» (делегируется VoxelCore)
        self.voxel_engine = None
        self.render_mode = "hybrid"   # "polygon" | "voxel" | "hybrid"
        
        # Метрики
        self.stats = {
            "draw_calls": 0,
            "triangles": 0,
            "voxels": 0,
            "textures_loaded": 0,
            "fps": 0
        }
        
        logger.info("🎨 RendererCore создан")
    
    def initialize(self) -> bool:
        """Инициализация графического движка."""
        try:
            logger.info("  🎨 Инициализация графического движка...")
            
            # Создание default сцены
            self.create_scene("default")
            self.current_scene = "default"
            
            # Добавление default освещения
            self.add_light("directional", color=(1.0, 0.95, 0.9), intensity=1.0, 
                          direction=(0.5, -1.0, 0.3))
            
            # Default post-effects
            self.post_effects = ["bloom", "tonemap"]
            
            # Активируем гибридный рендер (полигон + воксель)
            self.activate_hybrid_rendering()
            
            self.is_initialized = True
            logger.info("  ✅ Графический движок инициализирован")
            return True
            
        except Exception as e:
            logger.error(f"  ❌ Ошибка инициализации: {e}")
            return False
    
    def activate_hybrid_rendering(self):
        """Активировать гибридную систему «полигон ↔ воксель»."""
        try:
            from ..voxelization.voxel_core import VoxelCore
            self.voxel_engine = VoxelCore()
            self.voxel_engine.initialize()
            self.render_mode = "hybrid"
            logger.info("  🧊 Гибридный рендер «полигон ↔ воксель» активирован")
        except Exception as e:
            logger.warning(f"  ⚠️ Гибридный рендер недоступен: {e}")
            self.render_mode = "polygon"
    
    def set_render_mode(self, mode: str):
        """Переключить режим рендера: polygon | voxel | hybrid."""
        if mode in ("polygon", "voxel", "hybrid"):
            self.render_mode = mode
            logger.info(f"  🎨 Режим рендера: {mode}")
        else:
            logger.warning(f"  ⚠️ Неизвестный режим рендера: {mode}")
    
    def add_hybrid_entity(self, scene_name: str, mesh_name: str, material_name: str,
                          position: Tuple[float, float, float] = (0, 0, 0),
                          scale: Tuple[float, float, float] = (1, 1, 1),
                          voxel_resolution: int = 16) -> Dict[str, Any]:
        """
        Добавить гибридный объект: красивые полигоны при взгляде,
        воксели при контакте.
        """
        if not self.voxel_engine:
            logger.error("  ❌ Гибридный движок не активирован")
            return {}
        
        # 1. Обычная полигональная сущность в сцене
        entity = self.add_entity(
            scene_name, mesh_name, material_name,
            position=position, scale=scale
        )
        if not entity:
            return {}
        
        # 2. Гибридная репрезентация
        hname = f"{mesh_name}_{len(self.voxel_engine.objects)}"
        hybrid = self.voxel_engine.create_hybrid_object(
            name=hname,
            mesh_name=mesh_name,
            material_name=material_name,
            position=position,
            scale=scale,
            voxel_resolution=voxel_resolution,
        )
        entity["hybrid"] = hybrid
        entity["hybrid_name"] = hname
        
        logger.info(f"  🧊 Гибридный объект '{hname}' добавлен в сцену")
        return entity
    
    def interact(self, entity_name: str, contact_point=None, force: float = 1.0) -> Dict[str, Any]:
        """
        КОНТАКТ с объектом — объект делится на воксели.
        Публичное API для игрового кода.
        """
        if not self.voxel_engine:
            return {"error": "Гибридный движок не активирован"}
        return self.voxel_engine.interact(entity_name, contact_point, force)
    
    def release(self, entity_name: str) -> Dict[str, Any]:
        """ОТПУСКАНИЕ — воксели собираются обратно в полигоны."""
        if not self.voxel_engine:
            return {"error": "Гибридный движок не активирован"}
        return self.voxel_engine.release(entity_name)
    
    def create_scene(self, name: str) -> Dict[str, Any]:
        """Создание новой сцены."""
        scene = {
            "name": name,
            "entities": [],
            "lights": [],
            "cameras": [],
            "environment": {
                "sky_color": (0.5, 0.7, 1.0),
                "fog_enabled": False,
                "fog_color": (0.5, 0.7, 1.0),
                "fog_density": 0.01
            }
        }
        self.scenes[name] = scene
        logger.info(f"  📐 Сцена '{name}' создана")
        return scene
    
    def switch_scene(self, name: str):
        """Переключение сцены."""
        if name in self.scenes:
            self.current_scene = name
            logger.info(f"  🔄 Сцена изменена на '{name}'")
        else:
            logger.warning(f"  ⚠️ Сцена '{name}' не найдена")
    
    def load_texture(self, name: str, path: str) -> bool:
        """Загрузка текстуры."""
        try:
            self.textures[name] = {
                "path": path,
                "width": 0,  # Будет заполнено при загрузке
                "height": 0,
                "format": "unknown",
                "mipmaps": True,
                "filter": "linear"
            }
            self.stats["textures_loaded"] = len(self.textures)
            logger.info(f"  🖼️ Текстура '{name}' загружена: {path}")
            return True
        except Exception as e:
            logger.error(f"  ❌ Ошибка загрузки текстуры: {e}")
            return False
    
    def load_mesh(self, name: str, path: str) -> bool:
        """Загрузка меша."""
        try:
            self.meshes[name] = {
                "path": path,
                "vertices": 0,
                "indices": 0,
                "bounding_box": {
                    "min": (0, 0, 0),
                    "max": (0, 0, 0)
                }
            }
            logger.info(f"  🔺 Меш '{name}' загружен: {path}")
            return True
        except Exception as e:
            logger.error(f"  ❌ Ошибка загрузки меша: {e}")
            return False
    
    def create_material(self, name: str, material_type: str = "PBR", **kwargs) -> bool:
        """Создание материала."""
        try:
            self.materials[name] = {
                "type": material_type,
                "properties": kwargs
            }
            logger.info(f"  🎨 Материал '{name}' создан (тип: {material_type})")
            return True
        except Exception as e:
            logger.error(f"  ❌ Ошибка создания материала: {e}")
            return False
    
    def add_light(self, light_type: str, **kwargs) -> Dict[str, Any]:
        """Добавление источника света."""
        light = {
            "type": light_type,
            "color": kwargs.get("color", (1.0, 1.0, 1.0)),
            "intensity": kwargs.get("intensity", 1.0),
            "position": kwargs.get("position", (0, 0, 0)),
            "direction": kwargs.get("direction", (0, -1, 0)),
            "range": kwargs.get("range", 50),
            "cast_shadows": kwargs.get("cast_shadows", True)
        }
        self.lights.append(light)
        
        # Добавляем в текущую сцену
        if self.current_scene:
            self.scenes[self.current_scene]["lights"].append(light)
        
        logger.info(f"  💡 Свет '{light_type}' добавлен")
        return light
    
    def add_entity(self, scene_name: str, mesh_name: str, material_name: str,
                   position: Tuple[float, float, float] = (0, 0, 0),
                   rotation: Tuple[float, float, float] = (0, 0, 0),
                   scale: Tuple[float, float, float] = (1, 1, 1)) -> Dict[str, Any]:
        """Добавление объекта в сцену."""
        if scene_name not in self.scenes:
            logger.error(f"  ❌ Сцена '{scene_name}' не найдена")
            return {}
        
        entity = {
            "mesh": mesh_name,
            "material": material_name,
            "position": position,
            "rotation": rotation,
            "scale": scale,
            "visible": True,
            "cast_shadows": True,
            "receive_shadows": True
        }
        
        self.scenes[scene_name]["entities"].append(entity)
        logger.info(f"  📦 Объект добавлен в сцену '{scene_name}'")
        return entity
    
    def set_post_effect(self, effect: str, enabled: bool = True, **params):
        """Настройка постобработки."""
        if enabled:
            if effect not in self.post_effects:
                self.post_effects.append(effect)
        else:
            if effect in self.post_effects:
                self.post_effects.remove(effect)
        
        logger.info(f"  ✨ Пост-эффект '{effect}': {'вкл' if enabled else 'выкл'}")
    
    def render_frame(self, scene_name: Optional[str] = None) -> Dict[str, Any]:
        """Рендеринг кадра (симуляция, учитывает гибридные объекты)."""
        scene = self.scenes.get(scene_name or self.current_scene)
        if not scene:
            return {}
        
        # Симуляция метрик рендеринга
        entity_count = len(scene.get("entities", []))
        triangles = 0
        voxels = 0
        draw_calls = 0
        
        for entity in scene.get("entities", []):
            hybrid_name = entity.get("hybrid_name")
            if hybrid_name and self.voxel_engine:
                rep = self.voxel_engine.get_render_representation(hybrid_name)
                if rep["representation"] == "polygon":
                    triangles += rep.get("triangles", 500)
                    draw_calls += 1
                elif rep["representation"] == "voxel":
                    voxels += rep.get("voxels", 0)
                    draw_calls += 1
                elif rep["representation"] == "morph":
                    triangles += rep.get("triangles", 500)
                    voxels += rep.get("voxels", 0)
                    draw_calls += 2  # обе репрезентации при морфинге
            else:
                triangles += 500
                draw_calls += 1
        
        self.stats["draw_calls"] = draw_calls
        self.stats["triangles"] = triangles
        self.stats["voxels"] = voxels
        
        return {
            "scene": scene_name or self.current_scene,
            "draw_calls": self.stats["draw_calls"],
            "triangles": self.stats["triangles"],
            "voxels": self.stats["voxels"],
            "render_mode": self.render_mode,
            "post_effects": self.post_effects
        }
    
    def update(self, dt: float):
        """Обновление графического движка."""
        if not self.is_initialized:
            return
        
        # Обновление гибридных объектов (морфинг, физика вокселей)
        if self.voxel_engine:
            self.voxel_engine.update(dt)
        
        # Симуляция рендеринга
        self.render_frame()
    
    def get_status(self) -> Dict[str, Any]:
        """Получение статуса графического движка."""
        return {
            "status": "active" if self.is_initialized else "inactive",
            "scenes": len(self.scenes),
            "textures": len(self.textures),
            "meshes": len(self.meshes),
            "materials": len(self.materials),
            "lights": len(self.lights),
            "render_mode": self.render_mode,
            "hybrid": self.voxel_engine.get_status() if self.voxel_engine else None,
            "stats": self.stats
        }
