"""
ИИ модуль Сидни.
Отвечает за поведение NPC, навигацию, поиск пути и принятие решений.
"""

import logging
import random
from typing import Dict, List, Optional, Any, Tuple

logger = logging.getLogger("sidney.engine.ai")


class AICore:
    """Ядро ИИ системы."""
    
    def __init__(self):
        self.is_initialized = False
        self.max_agents = 256
        self.navmesh_resolution = 50
        
        # Агенты (NPC)
        self.agents: Dict[str, Any] = {}
        
        # NAV MESH
        self.navmesh: Optional[Dict[str, Any]] = None
        
        # Поведенческие деревья
        self.behavior_trees: Dict[str, Any] = {}
        
        # Группы
        self.squads: Dict[str, Any] = {}
        
        # Восприятие
        self.perception_area: Dict[str, Any] = {}
        
        # Метрики
        self.stats = {
            "agent_count": 0,
            "active_paths": 0,
            "decisions_made": 0,
            "nav_query_time_ms": 0
        }
        
        logger.info("🤖 AICore создан")
    
    def initialize(self) -> bool:
        """Инициализация ИИ системы."""
        try:
            logger.info("  🤖 Инициализация ИИ системы...")
            
            # Создание default NAV MESH
            self.create_navmesh()
            
            # Создание test agent
            self.create_agent("test_guard", position=(0, 0, 0))
            
            self.is_initialized = True
            logger.info("  ✅ ИИ система инициализирована")
            return True
            
        except Exception as e:
            logger.error(f"  ❌ Ошибка инициализации: {e}")
            return False
    
    def create_navmesh(self) -> Dict[str, Any]:
        """Создание навигационной сетки."""
        self.navmesh = {
            "cells": [],
            "agent_radius": 0.5,
            "agent_height": 2.0,
            "max_slope": 45,
            "is_baked": True,
            "cell_count": 0
        }
        
        # Генерация простой NAV сетки
        for x in range(-10, 10):
            for y in range(-10, 10):
                self.navmesh["cells"].append({
                    "x": x,
                    "y": y,
                    "walkable": True,
                    "connections": []
                })
                self.navmesh["cell_count"] += 1
        
        # Установка соединений
        for cell in self.navmesh["cells"]:
            for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                nx, ny = cell["x"] + dx, cell["y"] + dy
                neighbor = next((c for c in self.navmesh["cells"] if c["x"] == nx and c["y"] == ny), None)
                if neighbor:
                    cell["connections"].append(neighbor)
        
        logger.info(f"  🗺️ NAV MESH создан: {self.navmesh['cell_count']} ячеек")
        return self.navmesh
    
    def create_agent(self, name: str, position: Tuple[float, float, float] = (0, 0, 0),
                     **kwargs) -> Dict[str, Any]:
        """Создание NPC агента."""
        agent = {
            "name": name,
            "position": position,
            "velocity": (0, 0, 0),
            "rotation": 0,
            "health": 100,
            "state": "idle",
            "speed": kwargs.get("speed", 3.0),
            "sight_range": kwargs.get("sight_range", 15),
            "hearing_range": kwargs.get("hearing_range", 20),
            "aggression": kwargs.get("aggression", 0.5),
            "fear": kwargs.get("fear", 0.3),
            "path": [],
            "current_target": None,
            "behavior_tree": None,
            "memory": [],
            "in_squad": None,
            "is_alive": True
        }
        
        self.agents[name] = agent
        self.stats["agent_count"] = len(self.agents)
        
        logger.info(f"  🤖 Агент '{name}' создан (pos={position})")
        return agent
    
    def set_behavior_tree(self, agent_name: str, tree_name: str) -> bool:
        """Назначение поведенческого дерева агенту."""
        if agent_name not in self.agents:
            logger.error(f"  ❌ Агент '{agent_name}' не найден")
            return False
        
        if tree_name not in self.behavior_trees:
            logger.error(f"  ❌ Дерево '{tree_name}' не найдено")
            return False
        
        self.agents[agent_name]["behavior_tree"] = tree_name
        logger.info(f"  🌳 BT назначен агенту '{agent_name}': {tree_name}")
        return True
    
    def create_behavior_tree(self, name: str, structure: Dict[str, Any]) -> bool:
        """Создание поведенческого дерева."""
        self.behavior_trees[name] = {
            "structure": structure,
            "root": structure.get("root"),
            "is_compiled": True
        }
        
        logger.info(f"  🌳 Поведенческое дерево '{name}' создано")
        return True
    
    def find_path(self, agent_name: str, target_position: Tuple[float, float, float]) -> List[Tuple[float, float, float]]:
        """Поиск пути (A* simulation)."""
        if agent_name not in self.agents:
            logger.error(f"  ❌ Агент '{agent_name}' не найден")
            return []
        
        agent = self.agents[agent_name]
        
        # Симуляция A* pathfinding
        path = []
        current = list(agent["position"])
        target = list(target_position)
        
        steps = 0
        max_steps = 50
        
        while current != target and steps < max_steps:
            steps += 1
            # Движение к цели
            dx = target[0] - current[0]
            dy = target[1] - current[1]
            dz = target[2] - current[2]
            
            distance = (dx**2 + dy**2 + dz**2) ** 0.5
            if distance < 0.1:
                break
            
            step_size = 1.0
            current[0] += (dx / distance) * step_size
            current[1] = max(0, current[1])  # Не ниже земли
            current[2] += (dz / distance) * step_size
            
            path.append(tuple(current))
        
        agent["path"] = path
        agent["current_target"] = target_position
        self.stats["active_paths"] = sum(1 for a in self.agents.values() if a["path"])
        
        logger.info(f"  🛤️ Путь для '{agent_name}': {len(path)} точек")
        return path
    
    def create_squad(self, name: str, agent_names: List[str],
                     formation: str = "V") -> Dict[str, Any]:
        """Создание squad'а."""
        squad = {
            "name": name,
            "agents": agent_names,
            "formation": formation,
            "leader": agent_names[0] if agent_names else None,
            "is_active": True
        }
        
        self.squads[name] = squad
        
        # Назначение агентов в squad
        for agent_name in agent_names:
            if agent_name in self.agents:
                self.agents[agent_name]["in_squad"] = name
        
        logger.info(f"  👥 Squad '{name}' создан: {len(agent_names)} агентов")
        return squad
    
    def update(self, dt: float):
        """Обновление ИИ системы."""
        if not self.is_initialized:
            return
        
        self.stats["decisions_made"] = 0
        
        for name, agent in self.agents.items():
            if not agent["is_alive"]:
                continue
            
            # Обновление состояния
            self._update_agent_state(agent, dt)
            
            # Движение по пути
            if agent["path"]:
                self._move_along_path(agent, dt)
            
            self.stats["decisions_made"] += 1
    
    def _update_agent_state(self, agent: Dict[str, Any], dt: float):
        """Обновление состояния агента."""
        current_state = agent["state"]
        
        # Простая логика состояний
        if current_state == "idle":
            if random.random() < 0.01:  # 1% шанс перейти к патрулированию
                agent["state"] = "patrol"
                self._patrol_agent(agent)
        
        elif current_state == "patrol":
            if not agent["path"]:
                agent["state"] = "idle"
        
        elif current_state == "chase":
            agent["speed"] = agent["speed"] * 1.5  # Ускорение при погоне
        
        elif current_state == "attack":
            agent["speed"] = agent["speed"] * 0.5  # Замедление при атаке
    
    def _patrol_agent(self, agent: Dict[str, Any]):
        """Патрулирование агента."""
        patrol_points = [
            (10, 0, 10),
            (-10, 0, 10),
            (-10, 0, -10),
            (10, 0, -10)
        ]
        import random
        target = random.choice(patrol_points)
        self.find_path(agent["name"], target)
    
    def _move_along_path(self, agent: Dict[str, Any], dt: float):
        """Движение агента по пути."""
        if not agent["path"]:
            return
        
        target = agent["path"][0]
        dx = target[0] - agent["position"][0]
        dz = target[2] - agent["position"][2]
        distance = (dx**2 + dz**2) ** 0.5
        
        if distance < 0.5:
            agent["path"].pop(0)
        else:
            speed = agent["speed"] * dt
            agent["position"] = (
                agent["position"][0] + (dx / distance) * speed,
                agent["position"][1],
                agent["position"][2] + (dz / distance) * speed
            )
    
    def get_status(self) -> Dict[str, Any]:
        """Получение статуса ИИ системы."""
        return {
            "status": "active" if self.is_initialized else "inactive",
            "agent_count": self.stats["agent_count"],
            "active_paths": self.stats["active_paths"],
            "behavior_trees": len(self.behavior_trees),
            "squads": len(self.squads),
            "navmesh_cells": self.navmesh["cell_count"] if self.navmesh else 0,
            "stats": self.stats
        }
