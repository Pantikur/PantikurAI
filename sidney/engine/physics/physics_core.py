"""
Физический движок Сидни.
Отвечает за гравитацию, столкновения, разрушения и физику объектов.
"""

import logging
from typing import Dict, List, Optional, Any, Tuple

logger = logging.getLogger("sidney.engine.physics")


class PhysicsCore:
    """Ядро физического движка."""
    
    def __init__(self):
        self.is_initialized = False
        self.gravity = (0, -9.81, 0)
        self.max_substeps = 4
        self.iterations = 10
        
        # Тела
        self.bodies: Dict[str, Any] = {}
        
        # Разрушаемые объекты
        self.destructible: Dict[str, Any] = {}
        
        # Воксельные тела (для гибридной системы)
        self.voxel_bodies: Dict[str, Any] = {}
        
        # Жидкости
        self.fluids: Dict[str, Any] = {}
        
        # Ткани
        self.cloths: Dict[str, Any] = {}
        
        # Коллизии
        self.collisions: List[Dict[str, Any]] = []
        
        # Метрики
        self.stats = {
            "body_count": 0,
            "collision_count": 0,
            "voxel_body_count": 0,
            "framerate": 0,
            "simulation_speed": 1.0
        }
        
        logger.info("⚙️ PhysicsCore создан")
    
    def initialize(self) -> bool:
        """Инициализация физического движка."""
        try:
            logger.info("  ⚙️ Инициализация физического движка...")
            
            # Создание default ground body
            self.create_rigidbody(
                name="ground",
                shape="plane",
                mass=0,  # Статическое тело
                position=(0, 0, 0)
            )
            
            self.is_initialized = True
            logger.info("  ✅ Физический движок инициализирован")
            return True
            
        except Exception as e:
            logger.error(f"  ❌ Ошибка инициализации: {e}")
            return False
    
    def create_rigidbody(self, name: str, shape: str, mass: float,
                         position: Tuple[float, float, float] = (0, 0, 0),
                         **kwargs) -> Dict[str, Any]:
        """Создание физического тела."""
        body = {
            "name": name,
            "shape": shape,
            "mass": mass,
            "position": position,
            "velocity": (0, 0, 0),
            "angular_velocity": (0, 0, 0),
            "dimensions": kwargs.get("dimensions", (1, 1, 1)),
            "friction": kwargs.get("friction", 0.7),
            "restitution": kwargs.get("restitution", 0.3),
            "is_static": mass == 0,
            "is_sleeping": False,
            "enabled": True
        }
        
        self.bodies[name] = body
        self.stats["body_count"] = len(self.bodies)
        
        logger.info(f"  📦 Тело '{name}' создано (mass={mass}, shape={shape})")
        return body
    
    def apply_force(self, body_name: str, force: Tuple[float, float, float],
                    position: Optional[Tuple[float, float, float]] = None):
        """Применение силы к телу."""
        if body_name not in self.bodies:
            logger.error(f"  ❌ Тело '{body_name}' не найдено")
            return
        
        body = self.bodies[body_name]
        if body["is_static"]:
            logger.warning(f"  ⚠️ Тело '{body_name}' статическое, сила не применена")
            return
        
        # Обновление velocity (F = ma, a = F/m, v += a*dt)
        dt = 1.0 / 60
        if body["mass"] > 0:
            ax = force[0] / body["mass"]
            ay = force[1] / body["mass"]
            az = force[2] / body["mass"]
            
            body["velocity"] = (
                body["velocity"][0] + ax * dt,
                body["velocity"][1] + ay * dt,
                body["velocity"][2] + az * dt
            )
        
        logger.info(f"  💪 Сила применена к '{body_name}': {force}")
    
    def create_destructible(self, name: str, mesh: str, fragments: int = 64,
                            fragility: float = 0.7) -> Dict[str, Any]:
        """Создание разрушаемого объекта."""
        destructible = {
            "name": name,
            "mesh": mesh,
            "fragments": fragments,
            "fragility": fragility,
            "health": 100,
            "max_health": 100,
            "fragmented": False,
            "fragment_bodies": []
        }
        
        self.destructible[name] = destructible
        logger.info(f"  💥 Разрушаемый объект '{name}' создан (fragments={fragments})")
        return destructible
    
    def damage_destructible(self, name: str, damage: float):
        """Нанесение урона разрушаемому объекту."""
        if name not in self.destructible:
            logger.error(f"  ❌ Объект '{name}' не найден")
            return
        
        obj = self.destructible[name]
        obj["health"] -= damage
        
        if obj["health"] <= 0 and not obj["fragmented"]:
            obj["fragmented"] = True
            logger.info(f"  💥 Объект '{name}' разрушен!")
            self._fragment_object(name)
        else:
            logger.info(f"  📉 Объект '{name}' получил урон: {damage} (health: {obj['health']})")
    
    def _fragment_object(self, name: str):
        """Фрагментация объекта."""
        obj = self.destructible[name]
        fragment_count = min(obj["fragments"], 32)  # Лимит для производительности
        
        for i in range(fragment_count):
            fragment_name = f"{name}_fragment_{i}"
            self.create_rigidbody(
                name=fragment_name,
                shape="box",
                mass=0.5,
                position=(
                    obj["position"][0] + (i % 4) * 0.5,
                    obj["position"][1] + (i // 4) * 0.5,
                    obj["position"][2]
                )
            )
            # Применяем случайную силу для разлёта
            force = (
                (i - fragment_count/2) * 10,
                50 + (i % 7) * 5,
                (i - fragment_count/2) * 10
            )
            self.apply_force(fragment_name, force)
        
        self.stats["body_count"] = len(self.bodies)
    
    def create_voxel_bodies(self, name: str, voxel_count: int,
                            origin: Tuple[float, float, float] = (0, 0, 0),
                            voxel_size: float = 0.5,
                            mass_per_voxel: float = 0.1) -> Dict[str, Any]:
        """
        Создать воксельные тела из гибридного объекта.

        Каждый воксель — отдельное физическое тело (мини-куб).
        Это и есть «объект делится на воксели» на уровне физики.
        """
        voxel_body = {
            "name": name,
            "voxel_count": voxel_count,
            "origin": origin,
            "voxel_size": voxel_size,
            "mass_per_voxel": mass_per_voxel,
            "bodies_created": 0,
            "active": True,
        }
        
        self.voxel_bodies[name] = voxel_body
        
        # Создаём лёгкие тела-воксели (лимит для производительности)
        limit = min(voxel_count, 200)
        for i in range(limit):
            body_name = f"{name}_voxel_{i}"
            self.create_rigidbody(
                name=body_name,
                shape="box",
                mass=mass_per_voxel,
                position=origin,
                dimensions=(voxel_size, voxel_size, voxel_size)
            )
            voxel_body["bodies_created"] += 1
        
        self.stats["voxel_body_count"] = len(self.voxel_bodies)
        self.stats["body_count"] = len(self.bodies)
        
        logger.info(f"  🧊 Воксельные тела '{name}' созданы: {limit} мини-кубов")
        return voxel_body
    
    def apply_voxel_force(self, voxel_body_name: str, force: Tuple[float, float, float],
                          impact_point: Optional[Tuple[float, float, float]] = None,
                          radius: float = 2.0):
        """
        Применить силу к воксельным телам (удар, взрыв, контакт).

        Воксели вблизи точки контакта получают силу и разлетаются.
        """
        if voxel_body_name not in self.voxel_bodies:
            logger.error(f"  ❌ Воксельное тело '{voxel_body_name}' не найдено")
            return
        
        vb = self.voxel_bodies[voxel_body_name]
        # Локальная точка контакта (разворачиваем Optional явно)
        impact: Tuple[float, float, float]
        if impact_point is None:
            origin = vb["origin"]
            impact = (origin[0], origin[1], origin[2])
        else:
            impact = impact_point
        
        # Применяем силу к ближайшим вокселям
        applied = 0
        for i in range(vb["bodies_created"]):
            body_name = f"{voxel_body_name}_voxel_{i}"
            body = self.bodies.get(body_name)
            if not body or not body.get("position"):
                continue
            
            # Расстояние от вокселя до точки контакта
            dist = (
                (body["position"][0] - impact[0]) ** 2 +
                (body["position"][1] - impact[1]) ** 2 +
                (body["position"][2] - impact[2]) ** 2
            ) ** 0.5
            
            if dist <= radius:
                # Сила убывает с расстоянием
                falloff = 1.0 - dist / radius
                scaled_force = (
                    force[0] * falloff,
                    force[1] * falloff,
                    force[2] * falloff,
                )
                self.apply_force(body_name, scaled_force)
                applied += 1
        
        if applied:
            logger.info(f"  💥 Сила применена к {applied} вокселям '{voxel_body_name}'")
        self.stats["collision_count"] += 1
    
    def get_voxel_bodies_status(self) -> List[Dict[str, Any]]:
        """Статус всех воксельных тел."""
        return [
            {
                "name": name,
                "voxel_count": vb["voxel_count"],
                "bodies_created": vb["bodies_created"],
                "active": vb["active"],
            }
            for name, vb in self.voxel_bodies.items()
        ]
    
    def create_fluid(self, name: str, volume: float = 100,
                     viscosity: float = 0.001, density: float = 1000) -> Dict[str, Any]:
        """Создание симуляции жидкости."""
        fluid = {
            "name": name,
            "volume": volume,
            "viscosity": viscosity,
            "density": density,
            "particles": [],
            "boundaries": []
        }
        
        self.fluids[name] = fluid
        logger.info(f"  💧 Жидкость '{name}' создана (volume={volume})")
        return fluid
    
    def create_cloth(self, name: str, resolution: Tuple[int, int] = (32, 32),
                     pinned_edges: bool = True) -> Dict[str, Any]:
        """Создание физики ткани."""
        cloth = {
            "name": name,
            "resolution": resolution,
            "pinned_edges": pinned_edges,
            "stiffness": 0.7,
            "damping": 0.3,
            "vertices": [],
            "constraints": []
        }
        
        self.cloths[name] = cloth
        logger.info(f"  👗 Ткань '{name}' создана (resolution={resolution})")
        return cloth
    
    def step(self, dt: float):
        """Шаг физики."""
        if not self.is_initialized:
            return
        
        self.collisions = []
        
        # Обновление позиций тел
        for name, body in self.bodies.items():
            if body["is_static"] or not body["enabled"]:
                continue
            
            # Применение гравитации
            if not body["is_static"]:
                force = (
                    0,
                    self.gravity[1] * body["mass"],
                    0
                )
                # Добавляем к velocity напрямую
                body["velocity"] = (
                    body["velocity"][0],
                    body["velocity"][1] + self.gravity[1] * dt,
                    body["velocity"][2]
                )
            
            # Обновление позиции
            body["position"] = (
                body["position"][0] + body["velocity"][0] * dt,
                body["position"][1] + body["velocity"][1] * dt,
                body["position"][2] + body["velocity"][2] * dt
            )
            
            # Проверка столкновения с землёй
            if body["position"][1] < 0:
                body["position"] = (body["position"][0], 0, body["position"][2])
                body["velocity"] = (
                    body["velocity"][0] * 0.8,  # Damping
                    abs(body["velocity"][1]) * body["restitution"],
                    body["velocity"][2] * 0.8
                )
                
                if abs(body["velocity"][1]) < 0.5:
                    body["velocity"] = (0, 0, 0)
                    body["is_sleeping"] = True
            
            # Проверка sleep
            if body["is_sleeping"]:
                total_velocity = sum(abs(v) for v in body["velocity"])
                if total_velocity > 0.01:
                    body["is_sleeping"] = False
    
    def get_collisions(self) -> List[Dict[str, Any]]:
        """Получение списка коллизий."""
        return self.collisions
    
    def get_status(self) -> Dict[str, Any]:
        """Получение статуса физического движка."""
        return {
            "status": "active" if self.is_initialized else "inactive",
            "gravity": self.gravity,
            "body_count": self.stats["body_count"],
            "collision_count": len(self.collisions),
            "destructible_count": len(self.destructible),
            "voxel_bodies": self.get_voxel_bodies_status(),
            "voxel_body_count": self.stats["voxel_body_count"],
            "fluid_count": len(self.fluids),
            "cloth_count": len(self.cloths),
            "stats": self.stats
        }
