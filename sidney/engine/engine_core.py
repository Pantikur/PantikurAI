"""
Ядро игрового движка Сидни.
Управляет всеми 8 движками и их взаимодействием.
"""

import json
import logging
import time
import threading
from pathlib import Path
from typing import Dict, List, Optional, Any
from datetime import datetime

logger = logging.getLogger("sidney.engine")


class EngineCore:
    """
    Основное ядро игрового движка Сидни.
    
    Управляет:
    - Инициализацией и жизненным циклом всех 8 движков
    - Синхронизацией между движками
    - Производительностью и оптимизацией
    - Состоянием системы и бэкапами
    """
    
    def __init__(self, project_root: str = "."):
        self.project_root = Path(project_root) / "sidney"
        self.engine_root = self.project_root / "engine"
        
        # === Состояние движка ===
        self.is_running = False
        self.is_initialized = False
        self.start_time = 0
        self.fps = 0
        self.frame_count = 0
        self.last_fps_time = 0
        
        # === Движки ===
        self.renderers = None
        self.physics = None
        self.audio = None
        self.animation = None
        self.ai = None
        self.network = None
        self.scripting = None
        self.level_editor = None
        
        # === Состояние ===
        self.state_file = self.engine_root / "state" / "sidney_state.json"
        self.state = {
            "version": "1.0.0",
            "initialized_at": None,
            "last_update": None,
            "uptime_seconds": 0,
            "total_frames": 0,
            "total_cycles": 0,
            "engines": {},
            "performance": {
                "avg_fps": 0,
                "min_fps": 0,
                "max_fps": 0,
                "gpu_memory_mb": 0,
                "cpu_usage_percent": 0,
                "ram_usage_mb": 0
            },
            "self_development": {
                "level": 0,
                "optimization_count": 0,
                "new_algorithms": 0,
                "last_improvement": None
            },
            "character": {},
            "knowledge_levels": {
                "rendering": 0,
                "physics": 0,
                "audio": 0,
                "animation": 0,
                "ai": 0,
                "network": 0,
                "scripting": 0,
                "level_editor": 0
            }
        }
        
        # === События ===
        self._event_handlers: Dict[str, List] = {}
        
        # === Потоки ===
        self._update_thread = None
        self._lock = threading.Lock()
        
        logger.info("🔧 EngineCore инициализирован")
    
    def initialize(self) -> bool:
        """Инициализация всех 8 движков."""
        logger.info("🚀 Инициализация игрового движка Сидни...")
        
        try:
            # 1. Графический движок
            self._init_renderers()
            
            # 2. Физический движок
            self._init_physics()
            
            # 3. Аудиодвижок
            self._init_audio()
            
            # 4. Система анимации
            self._init_animation()
            
            # 5. ИИ система
            self._init_ai()
            
            # 6. Сетевой модуль
            self._init_network()
            
            # 7. Скриптовая система
            self._init_scripting()
            
            # 8. Редактор уровней
            self._init_level_editor()
            
            self.is_initialized = True
            self.start_time = time.time()
            self.state["initialized_at"] = datetime.now().isoformat()
            
            logger.info("✅ Все 8 движков инициализированы")
            self._save_state()
            self._emit_event("engine_initialized")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Ошибка инициализации: {e}")
            self.is_initialized = False
            return False
    
    def _init_renderers(self):
        """Инициализация графического движка."""
        from .renderers.renderer_core import RendererCore
        self.renderers = RendererCore()
        self.renderers.initialize()
        self.state["engines"]["renderers"] = {"status": "active", "version": "1.0.0"}
        logger.info("  🎨 Графический движок: активен")
    
    def _init_physics(self):
        """Инициализация физического движка."""
        from .physics.physics_core import PhysicsCore
        self.physics = PhysicsCore()
        self.physics.initialize()
        self.state["engines"]["physics"] = {"status": "active", "version": "1.0.0"}
        logger.info("  ⚙️ Физический движок: активен")
    
    def _init_audio(self):
        """Инициализация аудиодвижка."""
        from .audio.audio_core import AudioCore
        self.audio = AudioCore()
        self.audio.initialize()
        self.state["engines"]["audio"] = {"status": "active", "version": "1.0.0"}
        logger.info("  🔊 Аудиодвижок: активен")
    
    def _init_animation(self):
        """Инициализация системы анимации."""
        from .animation.animation_core import AnimationCore
        self.animation = AnimationCore()
        self.animation.initialize()
        self.state["engines"]["animation"] = {"status": "active", "version": "1.0.0"}
        logger.info("  🎭 Система анимации: активна")
    
    def _init_ai(self):
        """Инициализация ИИ системы."""
        from .ai.ai_core import AICore
        self.ai = AICore()
        self.ai.initialize()
        self.state["engines"]["ai"] = {"status": "active", "version": "1.0.0"}
        logger.info("  🤖 ИИ система: активна")
    
    def _init_network(self):
        """Инициализация сетевого модуля."""
        from .network.network_core import NetworkCore
        self.network = NetworkCore()
        self.network.initialize()
        self.state["engines"]["network"] = {"status": "active", "version": "1.0.0"}
        logger.info("  🌐 Сетевой модуль: активен")
    
    def _init_scripting(self):
        """Инициализация скриптовой системы."""
        from .scripting.scripting_core import ScriptingCore
        self.scripting = ScriptingCore()
        self.scripting.initialize()
        self.state["engines"]["scripting"] = {"status": "active", "version": "1.0.0"}
        logger.info("  📜 Скриптовая система: активна")
    
    def _init_level_editor(self):
        """Инициализация редактора уровней."""
        from .level_editor.editor_core import LevelEditorCore
        self.level_editor = LevelEditorCore()
        self.level_editor.initialize()
        self.state["engines"]["level_editor"] = {"status": "active", "version": "1.0.0"}
        logger.info("  🏗️ Редактор уровней: активен")
    
    def start(self):
        """Запуск основного цикла движка."""
        if not self.is_initialized:
            logger.error("Движок не инициализирован")
            return
        
        self.is_running = True
        self._update_thread = threading.Thread(target=self._update_loop, daemon=True)
        self._update_thread.start()
        logger.info("🔄 Основной цикл движка запущен")
        self._emit_event("engine_started")
    
    def stop(self):
        """Остановка основного цикла движка."""
        self.is_running = False
        if self._update_thread:
            self._update_thread.join(timeout=5.0)
        logger.info("⏹️ Основной цикл движка остановлен")
        self._emit_event("engine_stopped")
    
    def _update_loop(self):
        """Основной цикл обновления движка."""
        last_time = time.time()
        
        while self.is_running:
            current_time = time.time()
            dt = current_time - last_time
            last_time = current_time
            
            # FPS counter
            self.frame_count += 1
            if current_time - self.last_fps_time >= 1.0:
                self.fps = self.frame_count
                self.frame_count = 0
                self.last_fps_time = current_time
            
            # Обновление всех движков
            self._update_renderers(dt)
            self._update_physics(dt)
            self._update_audio(dt)
            self._update_animation(dt)
            self._update_ai(dt)
            self._update_network(dt)
            self._update_scripting(dt)
            
            # Обновление состояния
            self.state["last_update"] = datetime.now().isoformat()
            self.state["uptime_seconds"] = int(time.time() - self.start_time)
            self.state["total_frames"] += 1
            
            # Периодическое сохранение
            if self.state["total_frames"] % 3600 == 0:
                self._save_state()
    
    def _update_renderers(self, dt):
        if self.renderers:
            try:
                self.renderers.update(dt)
            except Exception as e:
                logger.error(f"Ошибка обновления рендерера: {e}")
    
    def _update_physics(self, dt):
        if self.physics:
            try:
                self.physics.step(dt)
            except Exception as e:
                logger.error(f"Ошибка обновления физики: {e}")
    
    def _update_audio(self, dt):
        if self.audio:
            try:
                self.audio.update(dt)
            except Exception as e:
                logger.error(f"Ошибка обновления аудио: {e}")
    
    def _update_animation(self, dt):
        if self.animation:
            try:
                self.animation.update(dt)
            except Exception as e:
                logger.error(f"Ошибка обновления анимации: {e}")
    
    def _update_ai(self, dt):
        if self.ai:
            try:
                self.ai.update(dt)
            except Exception as e:
                logger.error(f"Ошибка обновления ИИ: {e}")
    
    def _update_network(self, dt):
        if self.network:
            try:
                self.network.update(dt)
            except Exception as e:
                logger.error(f"Ошибка обновления сети: {e}")
    
    def _update_scripting(self, dt):
        if self.scripting:
            try:
                self.scripting.update(dt)
            except Exception as e:
                logger.error(f"Ошибка обновления скриптов: {e}")
    
    def register_event(self, event_name: str, handler):
        """Регистрация обработчика события."""
        if event_name not in self._event_handlers:
            self._event_handlers[event_name] = []
        self._event_handlers[event_name].append(handler)
    
    def _emit_event(self, event_name: str, data: Optional[Dict] = None):
        """Генерация события."""
        if event_name in self._event_handlers:
            for handler in self._event_handlers[event_name]:
                try:
                    handler(data)
                except Exception as e:
                    logger.error(f"Ошибка обработчика события {event_name}: {e}")
    
    def _save_state(self):
        """Сохранение состояния системы."""
        try:
            self.state_file.parent.mkdir(parents=True, exist_ok=True)
            with open(self.state_file, 'w', encoding='utf-8') as f:
                json.dump(self.state, f, indent=2, ensure_ascii=False)
        except Exception as e:
            logger.error(f"Ошибка сохранения состояния: {e}")
    
    def get_status(self) -> Dict[str, Any]:
        """Получение статуса всех движков."""
        return {
            "is_running": self.is_running,
            "is_initialized": self.is_initialized,
            "fps": self.fps,
            "uptime": self.state["uptime_seconds"],
            "engines": {
                "renderers": self.renderers.get_status() if self.renderers else "unknown",
                "physics": self.physics.get_status() if self.physics else "unknown",
                "audio": self.audio.get_status() if self.audio else "unknown",
                "animation": self.animation.get_status() if self.animation else "unknown",
                "ai": self.ai.get_status() if self.ai else "unknown",
                "network": self.network.get_status() if self.network else "unknown",
                "scripting": self.scripting.get_status() if self.scripting else "unknown",
                "level_editor": self.level_editor.get_status() if self.level_editor else "unknown"
            }
        }
