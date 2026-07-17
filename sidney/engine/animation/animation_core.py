"""
Система анимации Сидни.
Отвечает за скелетную анимацию, морфинг и физику объектов.
"""

import logging
from typing import Dict, List, Optional, Any, Tuple

logger = logging.getLogger("sidney.engine.animation")


class AnimationCore:
    """Ядро системы анимации."""
    
    def __init__(self):
        self.is_initialized = False
        self.max_bones = 128
        self.max_controllers = 64
        
        # Скелеты
        self.skeletons: Dict[str, Any] = {}
        
        # Анимационные контроллеры
        self.controllers: Dict[str, Any] = {}
        
        # Анимационные клипы
        self.clips: Dict[str, Any] = {}
        
        # Морфинг (blend shapes)
        self.blend_shapes: Dict[str, Any] = {}
        
        # Физика
        self.hair_physics: Dict[str, Any] = {}
        self.cloth_physics: Dict[str, Any] = {}
        
        # State Machines
        self.state_machines: Dict[str, Any] = {}
        
        # Метрики
        self.stats = {
            "active_animations": 0,
            "bones_updated": 0,
            "ik_solves": 0
        }
        
        logger.info("🎭 AnimationCore создан")
    
    def initialize(self) -> bool:
        """Инициализация системы анимации."""
        try:
            logger.info("  🎭 Инициализация системы анимации...")
            
            # Создание default skeleton
            self.create_skeleton("default", bone_count=32)
            
            self.is_initialized = True
            logger.info("  ✅ Система анимации инициализирована")
            return True
            
        except Exception as e:
            logger.error(f"  ❌ Ошибка инициализации: {e}")
            return False
    
    def create_skeleton(self, name: str, bone_count: int = 32) -> Dict[str, Any]:
        """Создание скелета."""
        skeleton = {
            "name": name,
            "bone_count": bone_count,
            "bones": [],
            "root": None,
            "is_valid": True
        }
        
        # Генерация default bone hierarchy
        default_bones = [
            "root", "spine", "chest", "neck", "head",
            "l_upper_arm", "l_forearm", "l_hand",
            "r_upper_arm", "r_forearm", "r_hand",
            "l_upper_leg", "l_shin", "l_foot",
            "r_upper_leg", "r_shin", "r_foot"
        ]
        
        for i, bone_name in enumerate(default_bones[:bone_count]):
            skeleton["bones"].append({
                "name": bone_name,
                "index": i,
                "parent": None,
                "position": (0, 0, 0),
                "rotation": (0, 0, 0, 1),  # quaternion
                "scale": (1, 1, 1)
            })
        
        self.skeletons[name] = skeleton
        logger.info(f"  🦴 Скелет '{name}' создан (bones={bone_count})")
        return skeleton
    
    def load_animation_clip(self, name: str, path: str, skeleton_name: str = "default") -> bool:
        """Загрузка анимационного клипа."""
        if skeleton_name not in self.skeletons:
            logger.error(f"  ❌ Скелет '{skeleton_name}' не найден")
            return False
        
        self.clips[name] = {
            "path": path,
            "skeleton": skeleton_name,
            "duration": 0,
            "fps": 30,
            "frames": [],
            "loop": True,
            "speed": 1.0
        }
        
        logger.info(f"  🎞️ Клип '{name}' загружен: {path}")
        return True
    
    def create_animation_controller(self, name: str, skeleton_name: str = "default") -> Dict[str, Any]:
        """Создание анимационного контроллера."""
        if skeleton_name not in self.skeletons:
            logger.error(f"  ❌ Скелет '{skeleton_name}' не найден")
            return {}
        
        controller = {
            "name": name,
            "skeleton": skeleton_name,
            "current_clip": None,
            "blend_time": 0.15,
            "ik_targets": {},
            "morph_targets": {},
            "is_playing": False,
            "playback_speed": 1.0,
            "weight": 1.0
        }
        
        self.controllers[name] = controller
        logger.info(f"  🎮 Контроллер '{name}' создан")
        return controller
    
    def set_state_machine(self, controller_name: str, states: Dict[str, Any],
                          transitions: List[Dict[str, Any]]) -> bool:
        """Настройка State Machine для контроллера."""
        if controller_name not in self.controllers:
            logger.error(f"  ❌ Контроллер '{controller_name}' не найден")
            return False
        
        sm = {
            "controller": controller_name,
            "states": states,
            "transitions": transitions,
            "current_state": "idle",
            "is_active": True
        }
        
        self.state_machines[controller_name] = sm
        logger.info(f"  🔄 State Machine для '{controller_name}': {len(states)} состояний")
        return True
    
    def set_ik_target(self, controller_name: str, bone_name: str,
                      target_position: Tuple[float, float, float]):
        """Настройка IK цели для кости."""
        if controller_name not in self.controllers:
            logger.error(f"  ❌ Контроллер '{controller_name}' не найден")
            return
        
        if "ik_targets" not in self.controllers[controller_name]:
            self.controllers[controller_name]["ik_targets"] = {}
        
        self.controllers[controller_name]["ik_targets"][bone_name] = target_position
        self.stats["ik_solves"] += 1
        logger.info(f"  🦵 IK для '{bone_name}': {target_position}")
    
    def set_morph_weight(self, controller_name: str, morph_name: str, weight: float):
        """Настройка веса морфинга."""
        if controller_name not in self.controllers:
            logger.error(f"  ❌ Контроллер '{controller_name}' не найден")
            return
        
        if "morph_targets" not in self.controllers[controller_name]:
            self.controllers[controller_name]["morph_targets"] = {}
        
        self.controllers[controller_name]["morph_targets"][morph_name] = max(0.0, min(1.0, weight))
        logger.info(f"  😊 Морф '{morph_name}': {weight}")
    
    def create_hair_physics(self, name: str, skeleton_name: str,
                            bone_prefix: str = "hair_",
                            stiffness: float = 0.7,
                            damping: float = 0.3) -> Dict[str, Any]:
        """Создание физики волос."""
        if skeleton_name not in self.skeletons:
            logger.error(f"  ❌ Скелет '{skeleton_name}' не найден")
            return {}
        
        hair = {
            "name": name,
            "skeleton": skeleton_name,
            "bone_prefix": bone_prefix,
            "stiffness": stiffness,
            "damping": damping,
            "segments": 8,
            "is_active": True
        }
        
        self.hair_physics[name] = hair
        logger.info(f"  💇 Физика волос '{name}' создана")
        return hair
    
    def update(self, dt: float, blend_time: float = 0.15):
        """Обновление системы анимации."""
        if not self.is_initialized:
            return
        
        self.stats["bones_updated"] = 0
        
        for name, controller in self.controllers.items():
            if controller.get("is_playing"):
                self.stats["active_animations"] += 1
                skeleton = self.skeletons.get(controller["skeleton"])
                if skeleton:
                    self.stats["bones_updated"] += len(skeleton["bones"])
    
    def get_status(self) -> Dict[str, Any]:
        """Получение статуса системы анимации."""
        return {
            "status": "active" if self.is_initialized else "inactive",
            "skeletons": len(self.skeletons),
            "controllers": len(self.controllers),
            "clips": len(self.clips),
            "state_machines": len(self.state_machines),
            "hair_physics": len(self.hair_physics),
            "stats": self.stats
        }
