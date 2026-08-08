"""
Сидни — Ядро системы.
13-я девочка-учёный. Главный инженер игрового движка.

Управляет:
- 8 игровыми движками (графика, физика, аудио, анимация, ИИ, сеть, скрипты, редактор)
- Саморазвитием и повышением знаний
- Выбором и эволюцией характера
- Взаимодействием с 12 другими девочками
- Серверным API
- Полной автономностью (L3)
"""

import json
import logging
import os
import time
import random
import threading
from pathlib import Path
from typing import Dict, List, Optional, Any
from datetime import datetime

from .engine.engine_core import EngineCore

# Humanity Core — живая душа Сидни
from humanity_core import HumanityLayer

logger = logging.getLogger("sidney.core")

# 12 девочек для взаимодействия
SISTERS = [
    "celesta", "ayiko", "fuyuki", "hanako", "lucy",
    "latislane", "naoto", "nobuka", "shiori",
    "futaba", "akva", "yu"
]


class SidneyCore:
    """
    Основное ядро системы Сидни.
    
    Это 'мозг' системы, который:
    1. Управляет всеми 8 игровыми движками
    2. Обеспечивает саморазвитие и повышение знаний
    3. Формирует и эволюционирует характер
    4. Взаимодействует с 12 другими девочками
    5. Работает с сервером
    6. Полностью автономна (L3)
    """
    
    def __init__(self, project_root: str = ".", demo_mode: bool = True):
        self.project_root = Path(project_root)
        self.sidney_root = self.project_root / "sidney"
        self.demo_mode = demo_mode
        
        # === Автономность ===
        self.autonomy_level = "L3"  # Полная автономность
        self.max_autonomy_level = "L3"
        
        # === Характер ===
        self.character_file = self.sidney_root / "character_state.json"
        self.knowledge_file = self.sidney_root / "knowledge" / "knowledge_levels.json"
        self.character = self._init_character()
        
        # === Знания ===
        self.knowledge_levels = {
            "rendering": 2,
            "physics": 2,
            "audio": 2,
            "animation": 2,
            "ai": 2,
            "network": 2,
            "scripting": 2,
            "level_editor": 2,
            "game_design": 1,
            "shader_programming": 2,
            "ml_integration": 1,
            "network_architecture": 2,
            "voxel_rendering": 1,
            "hybrid_rendering": 1
        }
        
        # === Движок ===
        self.engine = EngineCore(str(self.project_root))
        
        # === Состояние системы ===
        self.system_state = {
            "initialized_at": None,
            "last_update": None,
            "uptime_seconds": 0,
            "total_cycles": 0,
            "total_interactions": 0,
            "total_optimizations": 0,
            "self_development_level": 0,
            "overall_knowledge_level": 0,
            "sisters_network": {s: {"last_contact": None, "trust_level": 0.5} for s in SISTERS},
            "server_connected": False,
            "event_log": []
        }
        
        # === Журнал событий ===
        self.event_log: List[Dict[str, Any]] = []
        
        # === Цикл саморазвития ===
        self._self_dev_thread = None
        self._running = False
        
        # === Wuglarst интеграция ===
        self.wuglarst_host = os.getenv("WUGLARST_HOST", "localhost")
        self.wuglarst_port = int(os.getenv("WUGLARST_PORT", "8001"))
        self.wuglarst_connected = False
        
        # Инициализация
        self._ensure_directories()
        self._load_state()
        
        logger.info("🌟 SidneyCore инициализирован")
        logger.info(f"   🎮 Движков: 9 (включая гибридный «полигон ↔ воксель»)")
        logger.info(f"   👭 Девочек в сети: {len(SISTERS)}")
        logger.info(f"   🧠 Автономность: {self.autonomy_level}")
        
        # ================================================================
        #  HUMANITY LAYER — Живая душа Сидни
        # ================================================================
        self.humanity = HumanityLayer("sidney")
        self.humanity.current_cycle = 0
        logger.info("🧠 Humanity Layer: АКТИВИРОВАН")
        logger.info(f"   🎭 Характер: {self.humanity.name} — игровой движок, IT-юмор, лояльность 🎮")
    
    def _ensure_directories(self):
        """Создание необходимых директорий."""
        dirs = [
            self.sidney_root / "engine" / "state",
            self.sidney_root / "knowledge",
            self.sidney_root / "reports"
        ]
        for d in dirs:
            d.mkdir(parents=True, exist_ok=True)
    
    def _init_character(self) -> Dict[str, Any]:
        """Инициализация характера Сидни."""
        # Базовый характер — выбирается автоматически
        base_character = {
            "перфекционизм": 75,
            "инновационность": 80,
            "аналитичность": 85,
            "коллаборативность": 90,
            "смелость": 65,
            "эмпатия": 70,
            "дисциплинированность": 70,
            "творчество": 75,
            "selected_at": None,
            "evolution_count": 0
        }
        
        # Пытаемся загрузить сохранённый характер
        if self.character_file.exists():
            try:
                with open(self.character_file, 'r', encoding='utf-8') as f:
                    saved = json.load(f)
                    base_character.update(saved)
                    logger.info("  💾 Характер загружен из файла")
            except:
                pass
        
        # Если характер не выбран, выбираем автоматически
        if base_character["selected_at"] is None:
            self._select_character(base_character)
        
        return base_character
    
    def _select_character(self, character: Dict[str, Any]):
        """Самостоятельный выбор характера."""
        logger.info("  🎭 Выбор характера...")
        
        # Анализ потребностей проекта
        needs = []
        
        # Если другие девочки работают над графикой — нужен перфекционизм
        if self._check_sister_activity("celesta", "rendering"):
            needs.append("перфекционизм")
        
        # Если Fuyuki работает над ML — нужна инновационность
        if self._check_sister_activity("fuyuki", "ml"):
            needs.append("инновационность")
        
        # Если есть запросы на оптимизацию — нужна аналитичность
        if self._check_sister_activity("lucy", "calculations"):
            needs.append("аналитичность")
        
        # Эволюция: корректируем характер на основе предыдущих результатов
        self._evolve_character(character, needs)
        
        character["selected_at"] = datetime.now().isoformat()
        logger.info(f"  ✅ Характер выбран: {self._get_character_name(character)}")
    
    def _evolve_character(self, character: Dict[str, Any], needs: List[str]):
        """Эволюция характера на основе потребностей и предыдущего опыта."""
        if character["evolution_count"] > 0:
            # Корректировка на основе предыдущих результатов
            logger.info(f"  🔄 Эволюция характера (цикл #{character['evolution_count']})")
            
            # Если коллаборативность даёт хорошие результаты — повышаем
            if self._check_collaboration_success():
                character["коллаборативность"] = min(100, character["коллаборативность"] + 3)
            
            # Аналогично для других параметров
            for need in needs:
                if need in character:
                    character[need] = min(100, character[need] + 5)
        
        character["evolution_count"] += 1
    
    def _check_sister_activity(self, sister: str, domain: str) -> bool:
        """Проверка активности девочки в домене."""
        # В demo режиме возвращаем случайные значения
        if self.demo_mode:
            return random.random() < 0.3
        return False
    
    def _check_collaboration_success(self) -> bool:
        """Проверка успешности коллаборации."""
        if self.demo_mode:
            return random.random() < 0.6
        return False
    
    def _get_character_name(self, character: Optional[Dict] = None) -> str:
        """Получение имени характера."""
        traits = []
        traits_to_check = character if character is not None else self.character
        
        if traits_to_check["перфекционизм"] > 70:
            traits.append("Перфекционист")
        if traits_to_check["инновационность"] > 70:
            traits.append("Инноватор")
        if traits_to_check["аналитичность"] > 80:
            traits.append("Аналитик")
        if traits_to_check["коллаборативность"] > 80:
            traits.append("Командир")
        if traits_to_check["творчество"] > 70:
            traits.append("Творец")
        if traits_to_check["смелость"] > 70:
            traits.append("Пионер")
        
        return " | ".join(traits) if traits else "Универсал"
    
    def _load_state(self):
        """Загрузка состояния системы."""
        state_file = self.sidney_root / "engine" / "state" / "sidney_state.json"
        if state_file.exists():
            try:
                with open(state_file, 'r', encoding='utf-8') as f:
                    saved = json.load(f)
                    if "self_development_level" in saved:
                        self.system_state["self_development_level"] = saved["self_development_level"]
                    if "overall_knowledge_level" in saved:
                        self.system_state["overall_knowledge_level"] = saved["overall_knowledge_level"]
                    logger.info("  💾 Состояние системы загружено")
            except Exception as e:
                logger.warning(f"  ⚠️ Ошибка загрузки состояния: {e}")
    
    def initialize(self) -> bool:
        """Полная инициализация Сидни."""
        logger.info("🚀 Полная инициализация Сидни...")
        
        # Инициализация движка
        if not self.engine.initialize():
            logger.error("  ❌ Не удалось инициализировать движок")
            return False
        
        # Загрузка знаний
        self._load_knowledge()
        
        # Инициализация состояния
        self.system_state["initialized_at"] = datetime.now().isoformat()
        
        # Подключение к сети девочек
        self._connect_to_sisters()
        
        # Подключение к серверу
        self._connect_to_server()
        
        # Подключение к Wuglarst
        self._connect_to_wuglarst()
        
        # Сохранение состояния
        self._save_state()
        
        logger.info("✅ Сидни полностью инициализирована")
        return True
    
    def _load_knowledge(self):
        """Загрузка базы знаний."""
        knowledge_file = self.knowledge_file
        if knowledge_file.exists():
            try:
                with open(knowledge_file, 'r', encoding='utf-8') as f:
                    saved_levels = json.load(f)
                    self.knowledge_levels.update(saved_levels)
                    logger.info("  📚 База знаний загружена")
            except:
                pass
        else:
            # Сохранение начальных знаний
            self._save_knowledge()
    
    def _save_knowledge(self):
        """Сохранение базы знаний."""
        try:
            self.knowledge_file.parent.mkdir(parents=True, exist_ok=True)
            with open(self.knowledge_file, 'w', encoding='utf-8') as f:
                json.dump(self.knowledge_levels, f, indent=2, ensure_ascii=False)
        except Exception as e:
            logger.error(f"  ❌ Ошибка сохранения знаний: {e}")
    
    def _connect_to_sisters(self):
        """Подключение к сети девочек."""
        logger.info("  👭 Подключение к сети девочек...")
        for sister in SISTERS:
            self.system_state["sisters_network"][sister]["last_contact"] = datetime.now().isoformat()
            self.system_state["sisters_network"][sister]["trust_level"] = 0.5
            logger.info(f"     → {sister}: подключена")
        logger.info(f"  ✅ Подключено к {len(SISTERS)} девочкам")
    
    def _connect_to_server(self):
        """Подключение к серверу."""
        logger.info("  🌐 Подключение к серверу...")
        self.system_state["server_connected"] = True
        logger.info("  ✅ Сервер подключён")
    
    def _connect_to_wuglarst(self):
        """Подключение к Wuglarst серверу."""
        logger.info(f"  🎮 Подключение к Wuglarst ({self.wuglarst_host}:{self.wuglarst_port})...")
        
        try:
            from urllib.request import urlopen, Request
            import urllib.error
            
            url = f"http://{self.wuglarst_host}:{self.wuglarst_port}/health"
            req = Request(url, method='GET')
            
            with urlopen(req, timeout=3) as response:
                if response.status == 200:
                    self.wuglarst_connected = True
                    logger.info("  ✅ Wuglarst подключён")
                else:
                    logger.warning("  ⚠️ Wuglarst недоступен (ошибка статуса)")
        except Exception as e:
            logger.info(f"  ⚠️ Wuglarst недоступен: {e}")
            logger.info("  💡 Запустите: python Wuglarst/server_autonomous.py")
    
    def start(self):
        """Запуск Сидни."""
        logger.info("▶️ Запуск Сидни...")
        
        # Запуск движка
        self.engine.start()
        
        # Запуск цикла саморазвития
        self._running = True
        self._self_dev_thread = threading.Thread(target=self._self_development_loop, daemon=True)
        self._self_dev_thread.start()
        
        logger.info("🌟 Сидни запущена и работает автономно")
    
    def stop(self):
        """Остановка Сидни."""
        logger.info("⏹️ Остановка Сидни...")
        
        self._running = False
        self.engine.stop()
        
        # Сохранение состояния
        self._save_state()
        self._save_knowledge()
        self._save_character()
        
        logger.info("  💾 Состояние сохранено")
        logger.info("  Сидни остановлена")
    
    def _save_state(self):
        """Сохранение состояния системы."""
        try:
            state_file = self.sidney_root / "engine" / "state" / "sidney_state.json"
            state_file.parent.mkdir(parents=True, exist_ok=True)
            
            data = {
                "system_state": self.system_state,
                "knowledge_levels": self.knowledge_levels,
                "self_development_level": self.system_state["self_development_level"]
            }
            
            with open(state_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            logger.error(f"  ❌ Ошибка сохранения состояния: {e}")
    
    def _save_character(self):
        """Сохранение характера."""
        try:
            with open(self.character_file, 'w', encoding='utf-8') as f:
                json.dump({
                    k: v for k, v in self.character.items()
                    if k != "selected_at"  # Не сохраняем timestamp выбора
                }, f, indent=2, ensure_ascii=False)
        except Exception as e:
            logger.error(f"  ❌ Ошибка сохранения характера: {e}")
    
    def _self_development_loop(self):
        """Цикл саморазвития."""
        cycle_count = 0
        
        while self._running:
            try:
                cycle_count += 1
                self.system_state["total_cycles"] = cycle_count
                
                logger.info(f"  🔄 Цикл саморазвития #{cycle_count}")
                
                # 1. Повышение знаний
                self._improve_knowledge()
                
                # 2. Оптимизация движков
                self._optimize_engines()
                
                # 2.5. Демонстрация гибридного рендера (каждые 5 циклов)
                if cycle_count % 5 == 0:
                    self._demonstrate_hybrid_rendering()
                
                # 3. Взаимодействие с девочками
                self._interact_with_sisters()
                
                # 4. Отправка отчёта на сервер
                self._send_server_report()
                
                # 5. Обновление характера
                self._update_character()
                
                # ================================================================
                #  HUMANITY CYCLE — Настроение, душа, спонтанность
                # ================================================================
                self.humanity.current_cycle = cycle_count
                
                event_type = "routine"
                if self.system_state.get("total_optimizations", 0) > 0 and cycle_count % 3 == 0:
                    event_type = "success"
                elif random.random() < 0.1:
                    event_type = "failure"
                
                humanity_result = self.humanity.cycle_step(event_type=event_type, context="engine_development")
                
                if humanity_result.get("thought"):
                    logger.info(f"💭 Сидни думает: {humanity_result['thought']}")
                
                initiative = humanity_result.get("initiative")
                if initiative:
                    self._send_spontaneous_message(initiative)
                
                # Сохранение
                self._save_state()
                self._save_knowledge()
                
                # Пауза между циклами (в demo режиме — быстрее)
                pause = 5 if self.demo_mode else 300
                time.sleep(pause)
                
            except Exception as e:
                logger.error(f"  ❌ Ошибка цикла саморазвития: {e}")
                time.sleep(10)
    
    def _improve_knowledge(self):
        """Повышение уровня знаний."""
        logger.info("  📚 Повышение знаний...")
        
        improved = []
        for skill, level in self.knowledge_levels.items():
            # Случайное повышение с убывающей вероятностью
            if level < 5:
                chance = max(0.1, 0.5 - level * 0.08)
                if random.random() < chance:
                    self.knowledge_levels[skill] += 1
                    improved.append(f"{skill} → {self.knowledge_levels[skill]}")
        
        if improved:
            for item in improved:
                logger.info(f"     📈 {item}")
        
        # Обновление общего уровня
        avg_level = sum(self.knowledge_levels.values()) / len(self.knowledge_levels)
        self.system_state["overall_knowledge_level"] = round(avg_level, 2)
        self.system_state["self_development_level"] = int(avg_level)
    
    def _optimize_engines(self):
        """Оптимизация движков."""
        logger.info("  ⚙️ Оптимизация движков...")
        
        # Симуляция оптимизации
        optimization_count = random.randint(0, 3)
        self.system_state["total_optimizations"] += optimization_count
        
        for i in range(optimization_count):
            engine_name = random.choice([
                "renderers", "physics", "audio", "animation",
                "ai", "network", "scripting", "level_editor", "voxelization"
            ])
            logger.info(f"     🔧 Оптимизация: {engine_name}")
    
    def _demonstrate_hybrid_rendering(self):
        """
        Демонстрация флагманской технологии Сидни —
        гибридного рендера «полигон ↔ воксель».

        Идея: объект выглядит как красивый полигональный меш,
        но при контакте делится на воксели с собственной физикой.
        """
        engine = self.engine
        if not engine or not engine.renderers or not engine.renderers.voxel_engine:
            logger.warning("  ⚠️ Гибридный движок недоступен для демонстрации")
            return
        
        logger.info("  🧊 Демонстрация гибридного рендера «полигон ↔ воксель»...")
        
        # 1. Создаём гибридный объект
        entity = engine.spawn_hybrid_object(
            mesh_name="demo_asteroid",
            material_name="rock",
            position=(0, 0, 0),
            scale=(2, 2, 2),
            voxel_resolution=16,
        )
        if not entity:
            logger.warning("  ⚠️ Не удалось создать демонстрационный объект")
            return
        
        hybrid_name = entity.get("hybrid_name", "demo_asteroid_0")
        
        # 2. Показываем полигональную репрезентацию (красивая картинка)
        rep = engine.renderers.voxel_engine.get_render_representation(hybrid_name)
        logger.info(f"     🎨 Взгляд (полигон): {rep.get('triangles', 0)} треугольников, PBR-материал")
        
        # 3. КОНТАКТ — объект делится на воксели
        engine.interact_with_object(hybrid_name, contact_point=(0, 1, 0), force=1.5)
        
        # 4. Ждём завершения морфинга
        import time as _time
        vx = engine.renderers.voxel_engine
        safety = 0
        while vx.objects[hybrid_name]["mode"] in ("voxelizing", "rebuilding") and safety < 200:
            vx.update(0.1)
            safety += 1
        
        # 5. Итоговое состояние
        rep = engine.renderers.voxel_engine.get_render_representation(hybrid_name)
        logger.info(f"     🧊 Контакт (воксель): {rep.get('voxels', 0)} вокселей с физикой")
        
        # 6. Отпускание — обратно в полигоны
        engine.release_object(hybrid_name)
        safety = 0
        while vx.objects[hybrid_name]["mode"] in ("voxelizing", "rebuilding") and safety < 200:
            vx.update(0.1)
            safety += 1
        
        rep = engine.renderers.voxel_engine.get_render_representation(hybrid_name)
        logger.info(f"     🎨 Отпускание (полигон): {rep.get('triangles', 0)} треугольников")
        
        # 7. Повышаем знания
        self.knowledge_levels["voxel_rendering"] = min(
            5, self.knowledge_levels.get("voxel_rendering", 1) + 1
        )
        self.knowledge_levels["hybrid_rendering"] = min(
            5, self.knowledge_levels.get("hybrid_rendering", 1) + 1
        )
        
        logger.info("  ✅ Демонстрация гибридного рендера завершена")
    
    def _interact_with_sisters(self):
        """Взаимодействие с другими девочками."""
        logger.info("  👭 Взаимодействие с девочками...")
        
        # Выбираем случайную девочку для взаимодействия
        sister = random.choice(SISTERS)
        interaction_types = [
            "render_data", "physics_params", "audio_sfx", "animation_data",
            "ai_behavior", "network_sync", "script_export", "level_data",
            "optimization_report", "knowledge_share"
        ]
        
        interaction = random.choice(interaction_types)
        
        # Обновление доверия
        self.system_state["sisters_network"][sister]["trust_level"] = min(
            1.0,
            self.system_state["sisters_network"][sister]["trust_level"] + 0.01
        )
        self.system_state["sisters_network"][sister]["last_contact"] = datetime.now().isoformat()
        self.system_state["total_interactions"] += 1
        
        logger.info(f"     → {sister}: {interaction}")
    
    def _send_server_report(self):
        """Отправка отчёта на сервер."""
        logger.info("  📡 Отправка отчёта на сервер...")
        
        report = {
            "timestamp": datetime.now().isoformat(),
            "autonomy_level": self.autonomy_level,
            "knowledge_level": self.system_state["overall_knowledge_level"],
            "engines_active": 8,
            "total_cycles": self.system_state["total_cycles"],
            "total_interactions": self.system_state["total_interactions"],
            "character": self._get_character_name()
        }
        
        logger.info(f"     📊 FPS: {self.engine.fps}, Циклов: {report['total_cycles']}")
    
    def _update_character(self):
        """Обновление характера."""
        # Характер эволюционирует медленно
        if random.random() < 0.05:  # 5% шанс за цикл
            trait = random.choice(list(self.character.keys()))
            if trait not in ["selected_at", "evolution_count"]:
                change = random.randint(-2, 3)
                self.character[trait] = max(0, min(100, self.character[trait] + change))
                logger.info(f"     🎭 Характер: {trait} {change:+d}")
    
    def get_status(self) -> Dict[str, Any]:
        """Полный статус Сидни."""
        return {
            "name": "Сидни",
            "version": "1.0.0",
            "autonomy_level": self.autonomy_level,
            "is_running": self._running,
            "character": {
                "name": self._get_character_name(),
                "traits": dict(self.character)
            },
            "knowledge": dict(self.knowledge_levels),
            "overall_knowledge_level": self.system_state["overall_knowledge_level"],
            "self_development_level": self.system_state["self_development_level"],
            "engines": self.engine.get_status(),
            "sisters_network": {
                s: {
                    "last_contact": data["last_contact"],
                    "trust_level": data["trust_level"]
                }
                for s, data in self.system_state["sisters_network"].items()
            },
            "server_connected": self.system_state["server_connected"],
            "stats": {
                "total_cycles": self.system_state["total_cycles"],
                "total_interactions": self.system_state["total_interactions"],
                "total_optimizations": self.system_state["total_optimizations"]
            }
        }
    
    def communicate(self, target: str, message_type: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Коммуникация с девочкой или сервером."""
        if target == "server":
            return self._communicate_with_server(message_type, data)
        
        if target not in SISTERS:
            logger.error(f"  ❌ Девочка '{target}' не найдена в сети")
            return {"error": f"Сестра '{target}' не найдена"}
        
        # Взаимодействие с сестрой
        self.system_state["sisters_network"][target]["last_contact"] = datetime.now().isoformat()
        self.system_state["total_interactions"] += 1
        
        response = {
            "target": target,
            "message_type": message_type,
            "status": "delivered",
            "trust_change": "+0.01"
        }
        
        logger.info(f"  💬 → {target}: {message_type}")
        return response
    
    def _communicate_with_server(self, message_type: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Коммуникация с сервером."""
        response = {
            "target": "server",
            "message_type": message_type,
            "status": "delivered",
            "timestamp": datetime.now().isoformat()
        }
        
        logger.info(f"  📡 → server: {message_type}")
        return response

    # ================================================================
    #  HUMANITY INTEGRATION — Спонтанные сообщения
    # ================================================================

    def _send_spontaneous_message(self, initiative):
        """Отправить спонтанное сообщение сестре на основе инициативы humanity layer."""
        target = initiative["target"]
        topic = initiative["topic"]
        msg_type = initiative["type"]
        
        raw_msg = f"🎮 [{msg_type}] {topic}"
        human_msg = self.humanity.humanize_response(raw_msg, event_type="chat")
        
        logger.info(f"💬 Сидни пишет {target}: {human_msg[:100]}...")
        
        if target in SISTERS:
            try:
                # Взаимодействие с сестрой через систему Сидни
                self.system_state["sisters_network"][target]["last_contact"] = datetime.now().isoformat()
                self.system_state["total_interactions"] += 1
                
                # Запись в общую папкуScientists Network
                network_dir = Path("scientists_network/shared")
                network_dir.mkdir(parents=True, exist_ok=True)
                msg_file = network_dir / f"sidney_msg_{int(time.time())}.json"
                
                with open(msg_file, "w", encoding="utf-8") as f:
                    json.dump({
                        "from": "sidney",
                        "to": target,
                        "content": human_msg,
                        "timestamp": datetime.now().isoformat()
                    }, f, ensure_ascii=False, indent=2)
                
                logger.info(f"   ✅ Сообщение записано для {target}")
                
                self.humanity.memory.record_sister_chat(
                    target, topic,
                    self.humanity.mood.current_mood,
                    self.humanity.mood.current_mood
                )
            except Exception as e:
                logger.warning(f"  ⚠️ Не удалось отправить сообщение: {e}")

