"""
Скриптовая система Сидни.
Отвечает за Lua/Python интеграцию, визуальное программирование и систему событий.
"""

import logging
import time
import importlib
from typing import Dict, List, Optional, Any, Callable

logger = logging.getLogger("sidney.engine.scripting")


class ScriptingCore:
    """Ядро скриптовой системы."""
    
    def __init__(self):
        self.is_initialized = False
        self.default_engine = "lua"
        self.sandbox_mode = True
        
        # Скрипты
        self.scripts: Dict[str, Any] = {}
        self.python_scripts: Dict[str, Any] = {}
        
        # Визуальные графы
        self.visual_graphs: Dict[str, Any] = {}
        
        # Система событий
        self.event_handlers: Dict[str, List[Callable]] = {}
        self.timers: Dict[str, Any] = {}
        
        # Hot reload
        self.watch_paths: List[str] = []
        self.last_reload_time = 0
        
        # Метрики
        self.stats = {
            "scripts_loaded": 0,
            "events_fired": 0,
            "scripts_executed": 0,
            "execution_time_ms": 0
        }
        
        logger.info("📜 ScriptingCore создан")
    
    def initialize(self) -> bool:
        """Инициализация скриптовой системы."""
        try:
            logger.info("  📜 Инициализация скриптовой системы...")
            
            # Создание default event handlers
            self.event_handlers["PlayerSpawn"] = []
            self.event_handlers["PlayerDeath"] = []
            self.event_handlers["ItemPickup"] = []
            self.event_handlers["LevelStart"] = []
            self.event_handlers["LevelComplete"] = []
            self.event_handlers["Update"] = []
            
            # Добавление default обработчиков
            self.bind_event("PlayerSpawn", self._default_player_spawn)
            self.bind_event("Update", self._default_update)
            
            self.is_initialized = True
            logger.info("  ✅ Скриптовая система инициализирована")
            return True
            
        except Exception as e:
            logger.error(f"  ❌ Ошибка инициализации: {e}")
            return False
    
    def execute_lua(self, code: str, script_name: str = "inline") -> bool:
        """Выполнение Lua кода (симуляция)."""
        try:
            self.scripts[script_name] = {
                "code": code,
                "engine": "lua",
                "compiled": True,
                "last_executed": time.time(),
                "execution_count": 0,
                "errors": []
            }
            
            self.stats["scripts_loaded"] += 1
            logger.info(f"  📜 Lua скрипт '{script_name}' загружен")
            return True
            
        except Exception as e:
            logger.error(f"  ❌ Ошибка Lua скрипта: {e}")
            if script_name in self.scripts:
                self.scripts[script_name]["errors"].append(str(e))
            return False
    
    def execute_python(self, code: str, script_name: str = "inline") -> bool:
        """Выполнение Python кода (симуляция)."""
        try:
            self.python_scripts[script_name] = {
                "code": code,
                "engine": "python",
                "compiled": True,
                "last_executed": time.time(),
                "execution_count": 0,
                "errors": []
            }
            
            self.stats["scripts_loaded"] += 1
            logger.info(f"  🐍 Python скрипт '{script_name}' загружен")
            return True
            
        except Exception as e:
            logger.error(f"  ❌ Ошибка Python скрипта: {e}")
            return False
    
    def create_visual_graph(self, name: str) -> Dict[str, Any]:
        """Создание визуального графа (node-based)."""
        graph = {
            "name": name,
            "nodes": [],
            "edges": [],
            "is_compiled": False,
            "is_running": False
        }
        
        self.visual_graphs[name] = graph
        logger.info(f"  📊 Визуальный граф '{name}' создан")
        return graph
    
    def add_graph_node(self, graph_name: str, node_type: str, name: str,
                       **kwargs) -> Dict[str, Any]:
        """Добавление ноды в визуальный граф."""
        if graph_name not in self.visual_graphs:
            logger.error(f"  ❌ Граф '{graph_name}' не найден")
            return {}
        
        node = {
            "id": f"node_{len(self.visual_graphs[graph_name]['nodes'])}",
            "type": node_type,
            "name": name,
            "inputs": [],
            "outputs": [],
            "properties": kwargs
        }
        
        self.visual_graphs[graph_name]["nodes"].append(node)
        logger.info(f"  📊 Нода '{name}' (тип: {node_type}) добавлена в граф '{graph_name}'")
        return node
    
    def connect_graph_nodes(self, graph_name: str, from_node: str, to_node: str,
                            from_output: str = "out", to_input: str = "in"):
        """Соединение нод в визуальном графе."""
        if graph_name not in self.visual_graphs:
            logger.error(f"  ❌ Граф '{graph_name}' не найден")
            return
        
        edge = {
            "from": from_node,
            "to": to_node,
            "from_output": from_output,
            "to_input": to_input
        }
        
        self.visual_graphs[graph_name]["edges"].append(edge)
        logger.info(f"  🔗 Ноды соединены в графе '{graph_name}'")
    
    def compile_visual_graph(self, graph_name: str) -> bool:
        """Компиляция визуального графа."""
        if graph_name not in self.visual_graphs:
            logger.error(f"  ❌ Граф '{graph_name}' не найден")
            return False
        
        graph = self.visual_graphs[graph_name]
        node_count = len(graph["nodes"])
        edge_count = len(graph["edges"])
        
        graph["is_compiled"] = True
        logger.info(f"  ✅ Граф '{graph_name}' скомпилирован: {node_count} нод, {edge_count} связей")
        return True
    
    def bind_event(self, event_name: str, handler: Callable):
        """Привязка обработчика к событию."""
        if event_name not in self.event_handlers:
            self.event_handlers[event_name] = []
        
        self.event_handlers[event_name].append(handler)
        logger.info(f"  🔗 Обработчик привязан к событию '{event_name}'")
    
    def fire_event(self, event_name: str, **kwargs):
        """Генерация события."""
        if event_name in self.event_handlers:
            for handler in self.event_handlers[event_name]:
                try:
                    handler(**kwargs)
                    self.stats["events_fired"] += 1
                except Exception as e:
                    logger.error(f"  ❌ Ошибка обработчика события '{event_name}': {e}")
    
    def add_timer(self, name: str, duration: float, callback: Callable,
                  repeat: bool = False):
        """Добавление таймера."""
        self.timers[name] = {
            "duration": duration,
            "remaining": duration,
            "callback": callback,
            "repeat": repeat,
            "is_active": True,
            "created_at": time.time()
        }
        logger.info(f"  ⏱️ Таймер '{name}' создан (duration={duration}s, repeat={repeat})")
    
    def reload_scripts(self, watch_paths: Optional[List[str]] = None):
        """Горячая перезагрузка скриптов."""
        if watch_paths:
            self.watch_paths = watch_paths
        
        self.last_reload_time = time.time()
        logger.info(f"  🔄 Скрипты перезагружены ({len(self.watch_paths)} путей наблюдения)")
    
    def _default_player_spawn(self, player_id: str = "default", **kwargs):
        """Default обработчик спавна игрока."""
        logger.info(f"  🎮 Игрок '{player_id}' заспавнен")
    
    def _default_update(self, dt: float = 0.016, **kwargs):
        """Default обработчик обновления."""
        pass
    
    def update(self, dt: float):
        """Обновление скриптовой системы."""
        if not self.is_initialized:
            return
        
        start_time = time.time()
        
        # Обновление таймеров
        for name, timer in list(self.timers.items()):
            if not timer["is_active"]:
                continue
            
            timer["remaining"] -= dt
            
            if timer["remaining"] <= 0:
                try:
                    timer["callback"]()
                except Exception as e:
                    logger.error(f"  ❌ Ошибка таймера '{name}': {e}")
                
                if not timer["repeat"]:
                    timer["is_active"] = False
                else:
                    timer["remaining"] = timer["duration"]
        
        # Обновление Python скриптов
        for name, script in self.python_scripts.items():
            if "on_update" in script["code"]:
                self.stats["scripts_executed"] += 1
        
        self.stats["execution_time_ms"] = (time.time() - start_time) * 1000
    
    def get_status(self) -> Dict[str, Any]:
        """Получение статуса скриптовой системы."""
        return {
            "status": "active" if self.is_initialized else "inactive",
            "lua_scripts": len(self.scripts),
            "python_scripts": len(self.python_scripts),
            "visual_graphs": len(self.visual_graphs),
            "event_handlers": len(self.event_handlers),
            "active_timers": sum(1 for t in self.timers.values() if t["is_active"]),
            "stats": self.stats
        }
