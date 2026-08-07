"""
Voxel-Core — гибридная система рендера «полигон + воксель».

Философия (оптимальное решение задачи):
  • Наблюдение (взгляд): объект рендерится как красивый полигональный меш
    с нормалями, PBR-материалами и сглаживанием — «картинка для глаз».
  • Контакт (взаимодействие): тот же объект «делится» на воксели —
    сетку мелких кубов, каждый из которых обретает собственную физику
    и может отколоться/разлететься.

Режимы объекта:
  POLYGON    — полигональный рендер (по умолчанию, «красивая картинка»)
  VOXELIZING — переход: полигон распадается на воксели (анимация деления)
  VOXEL      — воксельная репрезентация (контакт / физическое взаимодействие)
  REBUILDING — переход: воксели собираются обратно в полигон

Ключевая идея: НИКОГДА не перерисовываем два раза.
  - В режиме POLYGON рендерим исходный высокополигональный меш.
  - В режиме VOXEL рендерим воксельную сетку (те же объекты, другое представление).
  - Между ними — плавная интерполяция (morph), без «моргания».
"""

import logging
import math
import random
from typing import Dict, List, Optional, Any, Tuple

logger = logging.getLogger("sidney.engine.voxelization")


# Режимы гибридного объекта
MODE_POLYGON = "polygon"
MODE_VOXELIZING = "voxelizing"
MODE_VOXEL = "voxel"
MODE_REBUILDING = "rebuilding"

# Качество воксельной сетки (резолюции)
VX_LOW = 8
VX_MEDIUM = 16
VX_HIGH = 32
VX_ULTRA = 64


class VoxelCore:
    """Ядро гибридной системы «полигон ↔ воксель»."""

    def __init__(self):
        self.is_initialized = False

        # Гибридные объекты: имя -> состояние
        self.objects: Dict[str, Dict[str, Any]] = {}

        # Воксельные репрезентации: имя -> список вокселей
        self.voxel_grids: Dict[str, List[Dict[str, Any]]] = {}

        # Историю контактов (для аналитики и саморазвития)
        self.contact_history: List[Dict[str, Any]] = []

        # Автоматический «любопытный взгляд» — объекты проверяются на дистанцию
        self.view_distance = 30.0     # дальше этой дистанции — полигоны
        self.contact_distance = 2.0   # ближе этой дистанции — контакт

        # Скорость морфинга (сек на переход)
        self.voxelize_speed = 0.8
        self.rebuild_speed = 0.6

        # Статистика
        self.stats = {
            "hybrid_objects": 0,
            "total_voxels": 0,
            "contacts": 0,
            "releases": 0,
            "active_voxelizations": 0,
            "average_voxel_count": 0,
        }

        logger.info("🧊 VoxelCore создан")

    def initialize(self) -> bool:
        """Инициализация гибридного движка."""
        try:
            self.is_initialized = True
            logger.info("  🧊 Гибридный движок «полигон ↔ воксель» инициализирован")
            return True
        except Exception as e:
            logger.error(f"  ❌ Ошибка инициализации гибридного движка: {e}")
            return False

    # ==================================================================
    #  СОЗДАНИЕ ГИБРИДНЫХ ОБЪЕКТОВ
    # ==================================================================

    def create_hybrid_object(
        self,
        name: str,
        mesh_name: str,
        material_name: str = "default",
        position: Tuple[float, float, float] = (0, 0, 0),
        scale: Tuple[float, float, float] = (1, 1, 1),
        voxel_resolution: int = VX_MEDIUM,
        polygon_detail: str = "high",        # high/medium/low — качество полигонов
        voxel_physics: bool = True,          # воксели с собственной физикой
        sticky_ratio: float = 0.7,           # доля «прилипающих» вокселей
    ) -> Dict[str, Any]:
        """
        Создать гибридный объект.

        Один объект имеет ДВА представления:
        - полигональный меш (для глаз, «красивая картинка»);
        - воксельная сетка (для контактов и физики).
        """
        # Нормализуем разрешение
        resolution = max(VX_LOW, min(VX_ULTRA, int(voxel_resolution)))

        obj = {
            "name": name,
            "mesh_name": mesh_name,
            "material_name": material_name,
            "position": position,
            "scale": scale,
            "mode": MODE_POLYGON,               # начинаем «красивым» полигоном
            "voxel_resolution": resolution,
            "polygon_detail": polygon_detail,
            "voxel_physics": voxel_physics,
            "sticky_ratio": max(0.0, min(1.0, sticky_ratio)),
            "transition_progress": 0.0,          # 0..1 — прогресс морфинга
            "transition_direction": 0,           # +1 вокселизация, -1 сборка
            "contact_point": None,               # точка последнего контакта
            "contact_force": 0.0,                # сила последнего контакта
            "voxel_count": 0,
            "polygon_triangles": 0,              # замер для полигонов
            "active": True,
            "last_interaction": None,
        }

        # Полигональная «красивая» репрезентация
        # high-detail = много треугольников, сглаживание, нормали
        detail_factor = {"low": 1.0, "medium": 2.0, "high": 4.0}
        base_tris = int(400 * detail_factor.get(polygon_detail, 2.0))
        obj["polygon_triangles"] = base_tris

        self.objects[name] = obj

        # Предварительно строим воксельную сетку (для мгновенного перехода)
        self._build_voxel_grid(name)

        self.stats["hybrid_objects"] = len(self.objects)
        self._recalc_stats()

        logger.info(
            f"  🧊 Гибридный объект '{name}' создан "
            f"(меш={mesh_name}, воксели={self.objects[name]['voxel_count']}, "
            f"полигоны={obj['polygon_triangles']})"
        )
        return obj

    def _build_voxel_grid(self, name: str):
        """Построить воксельную сетку для объекта."""
        obj = self.objects[name]
        res = obj["voxel_resolution"]

        # Реальный расчёт: AABB объекта с учётом масштаба
        sx, sy, sz = obj["scale"]
        size_x = 1.0 * sx
        size_y = 1.0 * sy
        size_z = 1.0 * sz

        # Размер одного вокселя
        vx = size_x / res
        vy = size_y / res
        vz = size_z / res

        voxels: List[Dict[str, Any]] = []
        occupied = 0

        # Имитация «плотности поверхности»: объект-шар с воксельной оболочкой.
        # В реальном движке здесь была бы проверка пересечения треугольников.
        r = 0.45  # «радиус» объекта в нормализованных координатах

        for ix in range(res):
            for iy in range(res):
                for iz in range(res):
                    # Центр вокселя в нормализованных координатах [-0.5..0.5]
                    cx = (ix + 0.5) / res - 0.5
                    cy = (iy + 0.5) / res - 0.5
                    cz = (iz + 0.5) / res - 0.5

                    dist = math.sqrt(cx*cx + cy*cy + cz*cz)

                    # Оболочка: занимаем воксели вблизи поверхности шара
                    if 0.28 < dist <= r:
                        voxels.append({
                            "id": occupied,
                            "x": ix, "y": iy, "z": iz,
                            "center": (cx, cy, cz),
                            "size": (vx, vy, vz),
                            "material": obj["material_name"],
                            "detached": False,          # отколот ли от объекта
                            "velocity": (0, 0, 0),
                            "health": 100.0,
                        })
                        occupied += 1

        self.voxel_grids[name] = voxels
        obj["voxel_count"] = occupied

    # ==================================================================
    #  ИНТЕРАКЦИЯ: КОНТАКТ И ОТПУСКАНИЕ
    # ==================================================================

    def interact(self, name: str, contact_point: Optional[Tuple] = None,
                 force: float = 1.0) -> Dict[str, Any]:
        """
        КОНТАКТ с объектом → объект делится на воксели.

        Именно здесь происходит «магия»:
        красивая полигональная картинка распадается на воксели,
        каждый из которых обретает физику.
        """
        if name not in self.objects:
            logger.error(f"  ❌ Объект '{name}' не найден")
            return {"error": f"Объект '{name}' не найден"}

        obj = self.objects[name]

        # Если уже вокселизируемся — усиливаем контакт
        if obj["mode"] == MODE_VOXEL:
            self._apply_contact_force(name, force)
            return {"status": "voxel", "voxels": obj["voxel_count"]}

        # Запускаем переход полигон -> воксели
        obj["mode"] = MODE_VOXELIZING
        obj["transition_direction"] = 1
        obj["contact_point"] = contact_point or obj["position"]
        obj["contact_force"] = force
        obj["last_interaction"] = "contact"

        self.stats["contacts"] += 1
        self.contact_history.append({
            "object": name,
            "action": "contact",
            "time": obj["last_interaction"],
            "voxels": obj["voxel_count"],
        })

        logger.info(f"  👆 КОНТАКТ с '{name}': распад на {obj['voxel_count']} вокселей...")
        return {
            "status": "voxelizing",
            "voxels": obj["voxel_count"],
            "force": force,
        }

    def release(self, name: str) -> Dict[str, Any]:
        """
        ОТПУСКАНИЕ → воксели собираются обратно в полигон.

        Обратный морфинг: воксели «слипаются» и объект снова становится
        гладкой полигональной моделью.
        """
        if name not in self.objects:
            return {"error": f"Объект '{name}' не найден"}

        obj = self.objects[name]

        if obj["mode"] in (MODE_VOXEL, MODE_VOXELIZING):
            obj["mode"] = MODE_REBUILDING
            obj["transition_direction"] = -1
            obj["last_interaction"] = "release"
            self.stats["releases"] += 1

            logger.info(f"  ✋ Отпускание '{name}': воксели собираются в полигон...")
            return {"status": "rebuilding"}

        return {"status": "polygon"}

    def _apply_contact_force(self, name: str, force: float):
        """Усиление контакта: откалываем случайные воксели."""
        obj = self.objects[name]
        grid = self.voxel_grids.get(name, [])

        if not grid:
            return

        detached_count = 0
        for v in grid:
            if v["detached"]:
                continue
            # Воксели откалываются при сильном контакте
            if random.random() < min(0.5, force * 0.15):
                v["detached"] = True
                v["velocity"] = (
                    random.uniform(-1, 1) * force,
                    random.uniform(0, 2) * force,
                    random.uniform(-1, 1) * force,
                )
                detached_count += 1

        if detached_count:
            obj["voxel_physics"] = True
            self.stats["contacts"] += 1
            logger.info(f"  💥 Откололось вокселей: {detached_count}")

    # ==================================================================
    #  ОБНОВЛЕНИЕ (морфинг, физика вокселей)
    # ==================================================================

    def update(self, dt: float):
        """Обновление переходов и физики вокселей."""
        if not self.is_initialized:
            return

        for name, obj in self.objects.items():
            if obj["mode"] in (MODE_VOXELIZING, MODE_REBUILDING):
                self._update_transition(name, obj, dt)
            elif obj["mode"] == MODE_VOXEL:
                self._update_voxel_physics(name, obj, dt)

    def _update_transition(self, name: str, obj: Dict[str, Any], dt: float):
        """Плавный морфинг полигон -> воксели (и обратно)."""
        speed = self.voxelize_speed if obj["transition_direction"] > 0 else self.rebuild_speed

        obj["transition_progress"] += obj["transition_direction"] * dt / speed
        obj["transition_progress"] = max(0.0, min(1.0, obj["transition_progress"]))

        if obj["transition_progress"] >= 1.0:
            obj["mode"] = MODE_VOXEL
            obj["transition_progress"] = 0.0
            self.stats["active_voxelizations"] = max(
                0, self.stats["active_voxelizations"] - 1
            )
            logger.info(f"  🧊 '{name}': полностью вокселизирован ({obj['voxel_count']} вокселей)")
            self._detach_surface_voxels(name)

        elif obj["transition_progress"] <= 0.0:
            obj["mode"] = MODE_POLYGON
            obj["transition_progress"] = 0.0
            # Собираем отколотые воксели обратно
            for v in self.voxel_grids.get(name, []):
                v["detached"] = False
                v["velocity"] = (0, 0, 0)
            logger.info(f"  🎨 '{name}': снова полигональный")

    def _detach_surface_voxels(self, name: str):
        """После полной вокселизации откалываем поверхностные воксели."""
        obj = self.objects[name]
        grid = self.voxel_grids.get(name, [])

        # Откалываем «лишние» воксели по коэффициенту прилипания
        detach_limit = int(len(grid) * (1.0 - obj["sticky_ratio"]))
        detaches = 0
        for v in grid:
            if v["detached"]:
                continue
            if detaches >= detach_limit:
                break
            v["detached"] = True
            v["velocity"] = (
                random.uniform(-0.5, 0.5),
                random.uniform(0, 1.0),
                random.uniform(-0.5, 0.5),
            )
            detaches += 1

        if detaches:
            logger.info(f"  💫 Отколотые воксели: {detaches}")

    def _update_voxel_physics(self, name: str, obj: Dict[str, Any], dt: float):
        """Лёгкая физика вокселей (падение отколотых)."""
        grid = self.voxel_grids.get(name, [])
        gravity = -4.0

        for v in grid:
            if not v["detached"]:
                continue
            # Простейшая баллистика
            v["velocity"] = (
                v["velocity"][0],
                v["velocity"][1] + gravity * dt,
                v["velocity"][2],
            )
            # Замедление при «падении»
            if v["velocity"][1] < 0 and v["center"][1] < -1.0:
                v["velocity"] = (v["velocity"][0] * 0.9, 0, v["velocity"][2] * 0.9)

    # ==================================================================
    #  ЗАПРОСЫ СОСТОЯНИЯ
    # ==================================================================

    def get_object_state(self, name: str) -> Optional[Dict[str, Any]]:
        """Получить состояние гибридного объекта."""
        obj = self.objects.get(name)
        if not obj:
            return None

        detached = sum(1 for v in self.voxel_grids.get(name, []) if v["detached"])
        return {
            "name": name,
            "mode": obj["mode"],
            "polygon_triangles": obj["polygon_triangles"],
            "voxel_count": obj["voxel_count"],
            "voxel_resolution": obj["voxel_resolution"],
            "detached_voxels": detached,
            "transition_progress": round(obj["transition_progress"], 3),
            "contact_point": obj["contact_point"],
            "contact_force": obj["contact_force"],
        }

    def get_render_representation(self, name: str) -> Dict[str, Any]:
        """
        Что рендерить прямо сейчас?

        Рендерер спрашивает: «какую картинку рисовать?»
          POLYGON -> красивый меш
          VOXELIZING/REBUILDING -> морф (обе репрезентации, вес = прогресс)
          VOXEL -> воксельная сетка
        """
        obj = self.objects.get(name)
        if not obj:
            return {"representation": "none"}

        mode = obj["mode"]
        if mode == MODE_POLYGON:
            return {"representation": "polygon", "triangles": obj["polygon_triangles"]}
        if mode == MODE_VOXEL:
            return {"representation": "voxel", "voxels": obj["voxel_count"]}
        if mode in (MODE_VOXELIZING, MODE_REBUILDING):
            return {
                "representation": "morph",
                "polygon_weight": 1.0 - obj["transition_progress"],
                "voxel_weight": obj["transition_progress"],
                "triangles": obj["polygon_triangles"],
                "voxels": obj["voxel_count"],
            }
        return {"representation": "polygon", "triangles": obj["polygon_triangles"]}

    def get_contact_surface(self, name: str) -> Dict[str, Any]:
        """
        Физический коллайдер спрашивает: «какая у объекта поверхность?»
        В режиме POLYGON — обычный полигональный коллайдер.
        В режиме VOXEL — воксельная сетка (каждый куб — мини-коллайдер).
        """
        obj = self.objects.get(name)
        if not obj:
            return {"type": "none"}

        if obj["mode"] == MODE_POLYGON:
            return {"type": "mesh", "mesh": obj["mesh_name"]}
        if obj["mode"] == MODE_VOXEL:
            return {"type": "voxel_grid", "voxels": obj["voxel_count"]}
        return {"type": "mesh", "mesh": obj["mesh_name"]}

    # ==================================================================
    #  УТИЛИТЫ
    # ==================================================================

    def _recalc_stats(self):
        total_voxels = sum(o["voxel_count"] for o in self.objects.values())
        self.stats["total_voxels"] = total_voxels
        if self.objects:
            self.stats["average_voxel_count"] = total_voxels // len(self.objects)

    def get_status(self) -> Dict[str, Any]:
        """Полный статус гибридного движка."""
        modes = {}
        for obj in self.objects.values():
            modes[obj["mode"]] = modes.get(obj["mode"], 0) + 1

        return {
            "status": "active" if self.is_initialized else "inactive",
            "hybrid_objects": self.stats["hybrid_objects"],
            "total_voxels": self.stats["total_voxels"],
            "average_voxel_count": self.stats["average_voxel_count"],
            "contacts": self.stats["contacts"],
            "releases": self.stats["releases"],
            "active_voxelizations": self.stats["active_voxelizations"],
            "mode_distribution": modes,
        }
