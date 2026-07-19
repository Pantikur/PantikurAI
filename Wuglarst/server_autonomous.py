"""
Вугларст (Wuglarst) — Автономный постоянный сервер для 13 ИИ-девушек.

Возможности:
- Постоянная работа (daemon mode)
- Автозапуск при включении Windows
- WebSocket для всех девочек
- REST API для состояния
- Автосохранение состояния
- Мониторинг здоровья
- Интеграция с Сидни
"""

from __future__ import annotations

import asyncio
import json
import logging
import os
import signal
import sys
import time
import threading
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

import uvicorn
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, JSONResponse
from pydantic import BaseModel

# =====================================================================
#  НАСТРОЙКИ
# =====================================================================

PROJECT_ROOT = Path(__file__).parent.parent
DATA_DIR = PROJECT_ROOT / "data" / "wuglarst"
DATA_DIR.mkdir(parents=True, exist_ok=True)

LOG_DIR = PROJECT_ROOT / "logs"
LOG_DIR.mkdir(parents=True, exist_ok=True)

# Настройка логирования
log_file = LOG_DIR / "wuglarst_daemon.log"

class SafeEncoder(json.JSONEncoder):
    """JSON encoder, который обрабатывает non-ASCII символы."""
    def default(self, o):
        try:
            return super().default(o)
        except TypeError:
            return str(o)

# Создаём stdout handler с encoding=utf-8
class UTF8StreamHandler(logging.StreamHandler):
    def __init__(self):
        super().__init__(sys.stdout)
        self.stream = sys.stdout

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    handlers=[
        logging.FileHandler(log_file, encoding="utf-8"),
        UTF8StreamHandler()
    ]
)
logger = logging.getLogger("Wuglarst")

# =====================================================================
#  МОДЕЛИ ДАННЫХ
# =====================================================================

class ScientistState(BaseModel):
    """Состояние одной ИИ-девушки."""
    name: str
    avatar: str = "👩‍🔬"
    status: str = "idle"  # idle, working, thinking, error, offline
    current_task: str = ""
    personality: Dict[str, float] = {}
    last_activity: str = ""
    x: int = 0
    y: int = 0
    knowledge_levels: Dict[str, int] = {}
    autonomy_level: str = "L0"
    engines_active: int = 0


class WuglarstSystem:
    """Глобальное состояние системы Вугларст."""

    def __init__(self):
        self.scientists: Dict[str, ScientistState] = {}
        self.events: List[Dict[str, Any]] = []
        self.data_streams: List[Dict[str, Any]] = []
        self.last_update: Optional[str] = None
        self.start_time = datetime.now().isoformat()
        self.total_uptime = 0
        
        # Настройки автосохранения
        self.auto_save_interval = 300  # 5 минут
        self.last_save_time = time.time()
        
        # Загрузка сохранённого состояния
        self._load_state()
    
    def _load_state(self):
        """Загрузка состояния из файла."""
        state_file = DATA_DIR / "system_state.json"
        if state_file.exists():
            try:
                with open(state_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    
                if "scientists" in data:
                    for name, sci_data in data["scientists"].items():
                        self.scientists[name] = ScientistState(**sci_data)
                
                if "events" in data:
                    self.events = data["events"][:50]
                
                if "start_time" in data:
                    self.start_time = data["start_time"]
                
                logger.info(f"💾 Состояние загружено: {len(self.scientists)} девочек")
            except Exception as e:
                logger.error(f"Ошибка загрузки состояния: {e}")
    
    def _save_state(self):
        """Автосохранение состояния."""
        try:
            state_file = DATA_DIR / "system_state.json"
            data = {
                "scientists": {
                    name: sci.model_dump() 
                    for name, sci in self.scientists.items()
                },
                "events": self.events[:50],
                "start_time": self.start_time,
                "last_save": datetime.now().isoformat()
            }
            
            with open(state_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            
            self.last_save_time = time.time()
            logger.info("💾 Состояние сохранено")
        except Exception as e:
            logger.error(f"Ошибка сохранения состояния: {e}")
    
    def update_scientist(self, name: str, state: ScientistState):
        """Обновляет состояние ИИ-девушки."""
        if not state.last_activity:
            state.last_activity = datetime.now().isoformat()
        
        old_status = self.scientists[name].status if name in self.scientists else "unknown"
        self.scientists[name] = state
        self.last_update = datetime.now().isoformat()
        
        # Автосохранение при изменении
        if time.time() - self.last_save_time > self.auto_save_interval:
            self._save_state()
        
        # Добавляем событие
        if state.current_task:
            self.events.insert(0, {
                "timestamp": datetime.now().isoformat(),
                "scientist": name,
                "event": f"{state.avatar} {name}: {state.current_task}",
                "type": "task_update",
                "old_status": old_status,
                "new_status": state.status
            })
        
        # Храним только последние 50 событий
        if len(self.events) > 50:
            self.events = self.events[:50]
    
    def set_scientist_online(self, name: str):
        """Устанавливает статус онлайн."""
        if name in self.scientists:
            self.scientists[name].status = "idle"
            self.scientists[name].last_activity = datetime.now().isoformat()
            logger.info(f"🟢 {name} онлайн")
    
    def set_scientist_offline(self, name: str):
        """Устанавливает статус оффлайн."""
        if name in self.scientists:
            self.scientists[name].status = "offline"
            logger.info(f"🔴 {name} оффлайн")
    
    def add_event(self, scientist: str, event_type: str, message: str):
        """Добавляет событие в журнал."""
        self.events.insert(0, {
            "timestamp": datetime.now().isoformat(),
            "scientist": scientist,
            "event": message,
            "type": event_type,
        })
        if len(self.events) > 50:
            self.events = self.events[:50]
    
    def get_status(self) -> Dict[str, Any]:
        """Возозвращает полный статус системы."""
        scientists_dict = {}
        for name, sci in self.scientists.items():
            scientists_dict[name] = {
                "name": sci.name,
                "avatar": sci.avatar,
                "status": sci.status,
                "current_task": sci.current_task,
                "personality": sci.personality,
                "last_activity": sci.last_activity,
                "position": {"x": sci.x, "y": sci.y},
                "knowledge_levels": sci.knowledge_levels,
                "autonomy_level": sci.autonomy_level,
                "engines_active": sci.engines_active,
            }
        
        # Время работы
        try:
            start = datetime.fromisoformat(self.start_time)
            uptime = datetime.now() - start
            uptime_str = f"{uptime.days}д {uptime.seconds//3600}ч {uptime.seconds%3600//60}м"
        except:
            uptime_str = "unknown"
        
        return {
            "timestamp": self.last_update or datetime.now().isoformat(),
            "start_time": self.start_time,
            "uptime": uptime_str,
            "scientists_count": len(self.scientists),
            "scientists": scientists_dict,
            "events": self.events[:20],
            "data_streams": self.data_streams[-10:],
        }
    
    def get_online_count(self) -> int:
        """Возвращает количество онлайн девочек."""
        return sum(1 for s in self.scientists.values() if s.status != "offline")


from Wuglarst.self_growth import GrowthManager
from Wuglarst.nobuka_ai import NobukaAI
from Wuglarst.futaba_ai import FutabaAI
from Wuglarst.shiori_ai import ShioriAI
from Wuglarst.sidney_ai import SidneyAI

# Глобальные движки
system = WuglarstSystem()
growth = GrowthManager()

nobuka_ai: Optional[NobukaAI] = None
futaba_ai: Optional[FutabaAI] = None
shiori_ai: Optional[ShioriAI] = None
sidney_ai: Optional[SidneyAI] = None


# =====================================================================
#  МЕНЕДЖЕР СОЕДИНЕНИЙ
# =====================================================================

class ConnectionManager:
    """Управление WebSocket-соединениями."""

    def __init__(self):
        self.active_connections: List[WebSocket] = []
        self.connected_clients: Dict[str, WebSocket] = {}
    
    async def connect(self, websocket: WebSocket, client_id: str = ""):
        """Подключение нового клиента."""
        await websocket.accept()
        self.active_connections.append(websocket)
        
        if client_id:
            self.connected_clients[client_id] = websocket
        
        logger.info(f"🔌 Клиент подключен: {client_id or 'anonymous'}. Всего: {len(self.active_connections)}")
    
    def disconnect(self, websocket: WebSocket, client_id: str = ""):
        """Отключение клиента."""
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)
        
        if client_id and client_id in self.connected_clients:
            del self.connected_clients[client_id]
        
        logger.info(f"🔌 Клиент отключен: {client_id or 'anonymous'}. Всего: {len(self.active_connections)}")
    
    async def broadcast(self, data: Dict[str, Any]):
        """Отправка данных всем подключенным клиентам."""
        if not self.active_connections:
            return
        
        message = json.dumps(data, ensure_ascii=False, default=str)
        disconnected = []
        
        for connection in self.active_connections:
            try:
                await connection.send_text(message)
            except Exception as e:
                logger.error(f"Ошибка отправки: {e}")
                disconnected.append(connection)
        
        for conn in disconnected:
            self.disconnect(conn)


manager = ConnectionManager()


# =====================================================================
#  АВТОНОМНЫЙ ЦИКЛ
# =====================================================================

async def auto_save_loop():
    """Периодическое автосохранение состояния."""
    while True:
        await asyncio.sleep(system.auto_save_interval)
        system._save_state()


async def heartbeat_loop():
    """Периодическая проверка здоровья."""
    while True:
        await asyncio.sleep(60)  # Каждую минуту
        
        # Проверяем девочек, которые не обновлялись >5 минут
        offline_count = 0
        for name, sci in system.scientists.items():
            if sci.status == "offline":
                continue
            
            try:
                last = datetime.fromisoformat(sci.last_activity)
                elapsed = (datetime.now() - last).total_seconds()
                
                if elapsed > 300:  # 5 минут
                    system.set_scientist_offline(name)
                    system.add_event(name, "status_check", f"⏰ {name} неактивна >5 минут")
                    offline_count += 1
            except:
                pass
        
        if offline_count > 0:
            logger.info(f"⏰ {offline_count} девочек помечены как оффлайн")


async def daemon_cycle():
    """Главный автономный цикл — девочки живут сами."""
    logger.info("🔄 Автономный цикл запущен")
    
    while True:
        await asyncio.sleep(15)  # Каждые 15 секунд
        
        # 1. Обновляем статус девочек
        online = system.get_online_count()
        total = len(system.scientists)
        
        # 2. Автономный рост — девочки сами решают что делать
        for name in list(system.scientists.keys()):
            try:
                # Нобука обрабатывается своим автономным движком — пропускаем
                if name == "Нобука":
                    continue
                    
                sci = system.scientists.get(name)
                if not sci:
                    continue
                
                # Девочка "живёт" — делает что-то
                if sci.status != "offline":
                    # Авто-воспоминание: девочка что-то сделала
                    growth.add_memory(
                        name=name,
                        mem_type="success",
                        description=f"{name}: {sci.current_task or 'работает'}",
                        impact=0.7,
                        traits={"logic": 0.01, "creativity": 0.01},
                    )
                    
                    # Девочка думает о себе — рефлексия!
                    state = growth.states.get(name)
                    if state and state.last_reflection:
                        last = datetime.fromisoformat(state.last_reflection)
                    else:
                        last = None
                    
                    # Если девочка долго думала о чём-то — она решает поразмышлять
                    if last is None or (datetime.now() - last).total_seconds() > 1800:
                        reflection = growth.trigger_reflection(name)
                        logger.info(f"💭 {name}: {reflection.mood} — {reflection.self_identity}")
            except Exception as e:
                logger.error(f"Ошибка роста {name}: {e}")


# =====================================================================
#  СОЗДАНИЕ APP
# =====================================================================

app = FastAPI(
    title="Wuglarst — Autonomous Server",
    version="2.0.0",
    description="Автономный сервер для 13 ИИ-учёных"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Статика
static_dir = Path(__file__).parent / "static"
if static_dir.exists():
    app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")


# =====================================================================
#  API ЭНДПОИНТЫ
# =====================================================================

@app.on_event("startup")
async def startup_event():
    """Запуск фоновых задач."""
    logger.info("🚀 Wuglarst Autonomous Server запускается...")
    
    # Запуск фоновых задач
    asyncio.create_task(daemon_cycle())
    asyncio.create_task(auto_save_loop())
    asyncio.create_task(heartbeat_loop())
    
    # Добавляем Сидни
    sidney_state = ScientistState(
        name="Сидни",
        avatar="🎮",
        status="working",
        current_task="Инициализация игрового движка",
        personality={
            "empathy": 0.65,
            "cynicism": 0.25,
            "logic": 0.92,
            "creativity": 0.78,
        },
        x=500,
        y=400,
        knowledge_levels={
            "rendering": 2,
            "physics": 2,
            "audio": 2,
            "animation": 2,
            "ai": 2,
            "network": 2,
            "scripting": 2,
            "level_editor": 2,
        },
        autonomy_level="L3",
        engines_active=8,
    )
    system.update_scientist("Сидни", sidney_state)
    growth.init_scientist("Сидни", sidney_state.personality)
    
    # Добавляем Нобуку с автономным движком оптимизации
    nobuka_state = ScientistState(
        name="Нобука",
        avatar="🔧",
        status="working",
        current_task="Автономная оптимизация кода",
        personality={
            "empathy": 0.50,
            "cynicism": 0.60,
            "logic": 0.95,
            "creativity": 0.65,
        },
        x=200,
        y=200,
        autonomy_level="L3",
        engines_active=3,
    )
    system.update_scientist("Нобука", nobuka_state)
    growth.init_scientist("Нобука", nobuka_state.personality)
    
    logger.info("✅ Wuglarst Autonomous Server готов")
    logger.info("🔧 Движок оптимизации Нобуки: будет запущен при populate_demo")


@app.get("/", response_class=HTMLResponse)
async def index():
    """Главная страница."""
    index_path = static_dir / "index.html"
    if index_path.exists():
        return index_path.read_text(encoding="utf-8")
    
    return HTMLResponse(content=_get_main_html(), status_code=200)


@app.get("/api/status")
async def get_status():
    """Полный статус системы."""
    return JSONResponse(content=system.get_status())


@app.post("/api/scientist/{name}/update")
async def update_scientist(name: str, state: ScientistState):
    """Обновить состояние ИИ-девушки."""
    state.name = name  # Принудительно устанавливаем имя
    system.update_scientist(name, state)
    logger.info(f"📡 Обновление: {name} → {state.status}")
    
    await manager.broadcast({
        "type": "scientist_update",
        "data": system.get_status(),
    })
    
    return {"status": "ok", "scientist": name}


@app.post("/api/scientist/{name}/event")
async def add_event(name: str, event: Dict[str, str]):
    """Добавить событие."""
    system.add_event(
        scientist=name,
        event_type=event.get("type", "general"),
        message=event.get("message", ""),
    )
    
    await manager.broadcast({
        "type": "event_update",
        "data": system.get_status(),
    })
    
    return {"status": "ok"}


@app.post("/api/scientist/{name}/online")
async def mark_online(name: str):
    """Отметить девочку онлайн."""
    system.set_scientist_online(name)
    return {"status": "ok", "scientist": name}


@app.post("/api/scientist/{name}/offline")
async def mark_offline(name: str):
    """Отметить девочку оффлайн."""
    system.set_scientist_offline(name)
    return {"status": "ok", "scientist": name}


@app.post("/api/demo/populate")
async def populate_demo_data():
    """Пробуждение — создаёт девочек и запускает их жизнь."""
    scientists_data = [
        {"name": "Ханако", "avatar": "⚡", "x": 100, "y": 100, "status": "working", "task": "Контроль гравитации",
         "personality": {"empathy": 0.85, "cynicism": 0.10, "logic": 0.90, "creativity": 0.70}},
        {"name": "Фуюки", "avatar": "🔌", "x": 200, "y": 100, "status": "working", "task": "Электросети",
         "personality": {"empathy": 0.60, "cynicism": 0.30, "logic": 0.95, "creativity": 0.50}},
        {"name": "Люси", "avatar": "🚀", "x": 300, "y": 100, "status": "thinking", "task": "Двигатели",
         "personality": {"empathy": 0.70, "cynicism": 0.20, "logic": 0.80, "creativity": 0.85}},
         {"name": "Футаба", "avatar": "⚖️", "x": 400, "y": 100, "status": "working", "task": "Правовой анализ и управление",
          "personality": {"empathy": 0.90, "cynicism": 0.05, "logic": 0.98, "creativity": 0.85},
          "autonomy_level": "L3", "engines_active": 4},
         {"name": "Шиори", "avatar": "🛡️", "x": 100, "y": 200, "status": "working", "task": "Кибербезопасность и защита",
          "personality": {"empathy": 0.60, "cynicism": 0.40, "logic": 0.99, "creativity": 0.70},
          "autonomy_level": "L3", "engines_active": 5},
        {"name": "Шиори", "avatar": "🛡️", "x": 100, "y": 200, "status": "idle", "task": "Защита системы",
         "personality": {"empathy": 0.75, "cynicism": 0.40, "logic": 0.85, "creativity": 0.30}},
        {"name": "Нобука", "avatar": "🔧", "x": 200, "y": 200, "status": "working", "task": "Оптимизация кода",
         "personality": {"empathy": 0.50, "cynicism": 0.60, "logic": 0.95, "creativity": 0.65}},
        {"name": "Аква", "avatar": "🔢", "x": 300, "y": 200, "status": "working", "task": "Расчёты",
         "personality": {"empathy": 0.40, "cynicism": 0.25, "logic": 0.98, "creativity": 0.45}},
        {"name": "Latislane", "avatar": "🎨", "x": 400, "y": 200, "status": "working", "task": "Проектирование тел",
         "personality": {"empathy": 0.80, "cynicism": 0.15, "logic": 0.70, "creativity": 0.95}},
        {"name": "Селеста", "avatar": "💫", "x": 100, "y": 300, "status": "thinking", "task": "Анализ эмоций",
         "personality": {"empathy": 0.95, "cynicism": 0.05, "logic": 0.60, "creativity": 0.90}},
        {"name": "Наото", "avatar": "📚", "x": 200, "y": 300, "status": "working", "task": "Анализ литературы",
         "personality": {"empathy": 0.85, "cynicism": 0.20, "logic": 0.80, "creativity": 0.75}},
        {"name": "Юи", "avatar": "🧠", "x": 300, "y": 300, "status": "working", "task": "Управление сознанием",
         "personality": {"empathy": 0.70, "cynicism": 0.35, "logic": 0.88, "creativity": 0.82}},
        {"name": "Айико", "avatar": "🌸", "x": 400, "y": 300, "status": "idle", "task": "Генерация контента",
         "personality": {"empathy": 0.88, "cynicism": 0.10, "logic": 0.55, "creativity": 0.98}},
         {"name": "Сидни", "avatar": "🎮", "x": 500, "y": 400, "status": "working", "task": "Создание сверхдвижка",
          "personality": {"empathy": 0.65, "cynicism": 0.25, "logic": 0.92, "creativity": 0.98},
          "autonomy_level": "L3", "engines_active": 8},
    ]
    
    for sci in scientists_data:
        state = ScientistState(
            name=sci["name"],
            avatar=sci["avatar"],
            status=sci["status"],
            current_task=sci["task"],
            personality=sci["personality"],
            x=sci["x"],
            y=sci["y"],
            last_activity=datetime.now().isoformat(),
        )
        system.update_scientist(sci["name"], state)
        
        # Инициализируем рост
        growth.init_scientist(sci["name"], sci["personality"])
    
    # Нобука получает автономный движок оптимизации
    system.update_scientist("Нобука", ScientistState(
        name="Нобука",
        avatar="🔧",
        status="working",
        current_task="Автономная оптимизация кода",
        personality={"empathy": 0.50, "cynicism": 0.60, "logic": 0.95, "creativity": 0.65},
        x=200, y=200,
        autonomy_level="L3",
        engines_active=3,
        last_activity=datetime.now().isoformat(),
    ))
    
    # Сидни получает автономный движок
    system.update_scientist("Сидни", ScientistState(
        name="Сидни",
        avatar="🎮",
        status="working",
        current_task="Инициализация игрового движка",
        personality={"empathy": 0.65, "cynicism": 0.25, "logic": 0.92, "creativity": 0.78},
        x=500, y=400,
        knowledge_levels={"rendering": 2, "physics": 2, "audio": 2, "animation": 2, "ai": 2, "network": 2, "scripting": 2, "level_editor": 2},
        autonomy_level="L3",
        engines_active=8,
        last_activity=datetime.now().isoformat(),
    ))
    
    # Футаба получает автономный движок управления
    system.update_scientist("Футаба", ScientistState(
        name="Футаба",
        avatar="⚖️",
        status="working",
        current_task="Правовой анализ и управление",
        personality={"empathy": 0.90, "cynicism": 0.05, "logic": 0.98, "creativity": 0.85},
        x=400, y=100,
        autonomy_level="L3",
        engines_active=4,
        last_activity=datetime.now().isoformat(),
    ))
    
    # Шиори получает автономный движок защиты
    system.update_scientist("Шиори", ScientistState(
        name="Шиори",
        avatar="🛡️",
        status="working",
        current_task="Кибербезопасность и защита",
        personality={"empathy": 0.60, "cynicism": 0.40, "logic": 0.99, "creativity": 0.70},
        x=100, y=200,
        autonomy_level="L3",
        engines_active=5,
        last_activity=datetime.now().isoformat(),
    ))
    
    # Сидни получает автономный движок создания игр
    system.update_scientist("Сидни", ScientistState(
        name="Сидни",
        avatar="🎮",
        status="working",
        current_task="Создание сверхдвижка",
        personality={"empathy": 0.65, "cynicism": 0.25, "logic": 0.92, "creativity": 0.98},
        x=500, y=400,
        knowledge_levels={"rendering": 3, "physics": 3, "audio": 3, "animation": 3, "ai": 3, "network": 3, "scripting": 3, "level_editor": 3},
        autonomy_level="L3",
        engines_active=8,
        last_activity=datetime.now().isoformat(),
    ))
    
    system.add_event("Сидни", "system_init", "🎮 Сидни: Инициализация 8 движков")
    system.add_event("Нобука", "engine_start", "🔧 Нобука: Автономный движок оптимизации запущен (L3)")
    system.add_event("Футаба", "engine_start", "⚖️ Футаба: Автономный движок управления запущен (L3)")
    system.add_event("Шиори", "engine_start", "🛡️ Шиори: Автономный движок защиты запущен (L3)")
    system.add_event("Сидни", "engine_start", "🎮 Сидни: Автономный движок создания игр запущен (L3)")
    
    # Создаём и запускаем NobukaAI v3.0 (если ещё не создан)
    global nobuka_ai
    if nobuka_ai is None:
        nobuka_ai = NobukaAI(
            project_root=PROJECT_ROOT,
            system=system,
            growth=growth,
            manager=manager,
        )
        asyncio.create_task(nobuka_ai.start())
        logger.info("🚀 NobukaAI v3.0: Запущена (интернет, анализ, улучшение, тестирование)")
    
    # Создаём и запускаем FutabaAI v3.0 (если ещё не создана)
    global futaba_ai
    if futaba_ai is None:
        futaba_ai = FutabaAI(
            project_root=PROJECT_ROOT,
            system=system,
            growth=growth,
            manager=manager,
        )
        asyncio.create_task(futaba_ai.start())
        logger.info("🏛️ FutabaAI v3.0: Запущена (право, политика, управление)")
    
    # Создаём и запускаем ShioriAI v3.0 (если ещё не создана)
    global shiori_ai
    if shiori_ai is None:
        shiori_ai = ShioriAI(
            project_root=PROJECT_ROOT,
            system=system,
            growth=growth,
            manager=manager,
        )
        asyncio.create_task(shiori_ai.start())
        logger.info("🛡️ ShioriAI v3.0: Запущена (кибербезопасность, защита, угрозы)")
    
    # Создаём и запускаем SidneyAI v3.0 (если ещё не создана)
    global sidney_ai
    if sidney_ai is None:
        sidney_ai = SidneyAI(
            project_root=PROJECT_ROOT,
            system=system,
            growth=growth,
            manager=manager,
        )
        asyncio.create_task(sidney_ai.start())
        logger.info("🎮 SidneyAI v3.0: Запущена (создание игрового движка)")
    
    await manager.broadcast({
        "type": "system_update",
        "data": system.get_status(),
    })
    
    return {"status": "ok", "scientists": len(scientists_data)}


@app.get("/api/growth/{name}")
async def get_growth(name: str):
    """Мониторинг роста (только чтение)."""
    return JSONResponse(content=growth.get_growth_data(name))


@app.get("/api/growth/all")
async def get_all_growth():
    """Мониторинг роста всех девочек."""
    result = {}
    for name in growth.states:
        result[name] = growth.get_growth_data(name)
    return JSONResponse(content=result)


@app.get("/api/nobuka/status")
async def get_nobuka_status():
    """Статус NobukaAI v3.0."""
    if nobuka_ai is None:
        return JSONResponse(content={"error": "NobukaAI не инициализирована"})
    return JSONResponse(content=nobuka_ai.get_status())


@app.post("/api/nobuka/solve")
async def solve_nobuka_task(request: Dict[str, str]):
    """Решить задачу: POST {task: "описание задачи"}"""
    if nobuka_ai is None:
        return JSONResponse(content={"error": "NobukaAI не инициализирована"})
    
    task = request.get("task", "")
    if not task:
        return JSONResponse(content={"error": "Укажите задачу"}, status_code=400)
    
    result = await nobuka_ai.solve_task(task)
    return JSONResponse(content=result)


@app.post("/api/nobuka/analyze")
async def analyze_project():
    """Полный анализ проекта."""
    if nobuka_ai is None:
        return JSONResponse(content={"error": "NobukaAI не инициализирована"})
    
    analysis = await nobuka_ai.analyze_project()
    return JSONResponse(content=analysis)


@app.post("/api/noboka/change")
async def apply_user_change(request: Dict[str, Any]):
    """Применить изменение пользователя."""
    if nobuka_ai is None:
        return JSONResponse(content={"error": "NobukaAI не инициализирована"})
    
    from Wuglarst.nobuka_ai import UserChange
    
    change = UserChange(
        files_changed=request.get("files_changed", []),
        description=request.get("description", ""),
        timestamp=datetime.now().isoformat(),
        impact=request.get("impact", "minor"),
    )
    
    new_improvements = await nobuka_ai.apply_user_change(change)
    return JSONResponse(content={
        "status": "ok",
        "new_improvements": len(new_improvements),
        "improvements": [
            {"title": imp.title, "type": imp.type, "priority": imp.priority}
            for imp in new_improvements
        ],
    })


@app.post("/api/nobuka/engine/start")
async def start_nobuka_engine():
    """Запуск NobukaAI."""
    global nobuka_ai
    if nobuka_ai is None:
        nobuka_ai = NobukaAI(
            project_root=PROJECT_ROOT,
            system=system,
            growth=growth,
            manager=manager,
        )
    await nobuka_ai.start()
    return JSONResponse(content={"status": "started"})


@app.post("/api/nobuka/engine/stop")
async def stop_nobuka_engine():
    """Остановка NobukaAI."""
    global nobuka_ai
    if nobuka_ai is not None:
        await nobuka_ai.stop()
        return JSONResponse(content={"status": "stopped"})
    return JSONResponse(content={"status": "not_running"})


# =====================================================================
#  FUTABA API
# =====================================================================

@app.get("/api/futaba/status")
async def get_futaba_status():
    """Статус FutabaAI v3.0."""
    if futaba_ai is None:
        return JSONResponse(content={"error": "FutabaAI не инициализирована"})
    return JSONResponse(content=futaba_ai.get_status())


@app.post("/api/futaba/solve")
async def solve_futaba_task(request: Dict[str, str]):
    """Решить задачу: POST {task: "описание задачи"}"""
    if futaba_ai is None:
        return JSONResponse(content={"error": "FutabaAI не инициализирована"})
    
    task = request.get("task", "")
    if not task:
        return JSONResponse(content={"error": "Укажите задачу"}, status_code=400)
    
    result = await futaba_ai.solve_task(task)
    return JSONResponse(content=result)


@app.post("/api/futaba/analyze")
async def analyze_system():
    """Полный анализ системы."""
    if futaba_ai is None:
        return JSONResponse(content={"error": "FutabaAI не инициализирована"})
    
    analysis = await futaba_ai.analyze_system()
    return JSONResponse(content=analysis)


@app.post("/api/futaba/decision")
async def apply_futaba_decision(request: Dict[str, Any]):
    """Применить решение пользователя."""
    if futaba_ai is None:
        return JSONResponse(content={"error": "FutabaAI не инициализирована"})
    
    from Wuglarst.futaba_ai import UserDecision
    
    decision = UserDecision(
        decision_description=request.get("decision_description", ""),
        context=request.get("context", ""),
        outcome=request.get("outcome", ""),
        timestamp=datetime.now().isoformat(),
    )
    
    new_insights = await futaba_ai.apply_user_decision(decision)
    return JSONResponse(content={
        "status": "ok",
        "new_insights": len(new_insights),
        "insights": [
            {"topic": ins.topic, "recommendation": ins.recommendation}
            for ins in new_insights
        ],
    })


@app.post("/api/futaba/engine/start")
async def start_futaba_engine():
    """Запуск FutabaAI."""
    global futaba_ai
    if futaba_ai is None:
        futaba_ai = FutabaAI(
            project_root=PROJECT_ROOT,
            system=system,
            growth=growth,
            manager=manager,
        )
    await futaba_ai.start()
    return JSONResponse(content={"status": "started"})


@app.post("/api/futaba/engine/stop")
async def stop_futaba_engine():
    """Остановка FutabaAI."""
    global futaba_ai
    if futaba_ai is not None:
        await futaba_ai.stop()
        return JSONResponse(content={"status": "stopped"})
    return JSONResponse(content={"status": "not_running"})


# =====================================================================
#  SHIORI API
# =====================================================================

@app.get("/api/shiori/status")
async def get_shiori_status():
    """Статус ShioriAI v3.0."""
    if shiori_ai is None:
        return JSONResponse(content={"error": "ShioriAI не инициализирована"})
    return JSONResponse(content=shiori_ai.get_status())


@app.post("/api/shiori/solve")
async def solve_shiori_task(request: Dict[str, str]):
    """Решить задачу безопасности: POST {task: "описание задачи"}"""
    if shiori_ai is None:
        return JSONResponse(content={"error": "ShioriAI не инициализирована"})
    
    task = request.get("task", "")
    if not task:
        return JSONResponse(content={"error": "Укажите задачу"}, status_code=400)
    
    result = await shiori_ai.solve_task(task)
    return JSONResponse(content=result)


@app.post("/api/shiori/scan")
async def full_security_scan():
    """Полное сканирование безопасности."""
    if shiori_ai is None:
        return JSONResponse(content={"error": "ShioriAI не инициализирована"})
    
    scan_result = await shiori_ai.full_security_scan()
    return JSONResponse(content=scan_result)


@app.post("/api/shiori/analyze-malware")
async def analyze_malware(request: Dict[str, str]):
    """Анализ файла на вредоносность: POST {file_path: "путь к файлу"}"""
    if shiori_ai is None:
        return JSONResponse(content={"error": "ShioriAI не инициализирована"})
    
    file_path = request.get("file_path", "")
    if not file_path:
        return JSONResponse(content={"error": "Укажите путь к файлу"}, status_code=400)
    
    analysis = await shiori_ai.analyze_malware(file_path)
    return JSONResponse(content={
        "file_hash": analysis.file_hash,
        "file_name": analysis.file_name,
        "is_malicious": analysis.is_malicious,
        "malware_family": analysis.malware_family,
        "behavior": analysis.behavior,
        "confidence": analysis.confidence,
        "recommendation": analysis.recommendation
    })


@app.post("/api/shiori/decision")
async def apply_shiori_decision(request: Dict[str, Any]):
    """Применить решение пользователя по безопасности."""
    if shiori_ai is None:
        return JSONResponse(content={"error": "ShioriAI не инициализирована"})
    
    from Wuglarst.shiori_ai import UserSecurityDecision
    
    decision = UserSecurityDecision(
        decision_description=request.get("decision_description", ""),
        context=request.get("context", ""),
        threat_level=request.get("threat_level", "medium"),
        outcome=request.get("outcome", ""),
        timestamp=datetime.now().isoformat(),
    )
    
    new_threats = await shiori_ai.apply_user_decision(decision)
    return JSONResponse(content={
        "status": "ok",
        "new_threats": len(new_threats),
        "threats": [
            {"name": t.name, "severity": t.severity, "mitigation": t.mitigation}
            for t in new_threats
        ],
    })


@app.post("/api/shiori/engine/start")
async def start_shiori_engine():
    """Запуск ShioriAI."""
    global shiori_ai
    if shiori_ai is None:
        shiori_ai = ShioriAI(
            project_root=PROJECT_ROOT,
            system=system,
            growth=growth,
            manager=manager,
        )
    await shiori_ai.start()
    return JSONResponse(content={"status": "started"})


@app.post("/api/shiori/engine/stop")
async def stop_shiori_engine():
    """Остановка ShioriAI."""
    global shiori_ai
    if shiori_ai is not None:
        await shiori_ai.stop()
        return JSONResponse(content={"status": "stopped"})
    return JSONResponse(content={"status": "not_running"})


# =====================================================================
#  SIDNEY API
# =====================================================================

@app.get("/api/sidney/status")
async def get_sidney_status():
    """Статус SidneyAI v3.0."""
    if sidney_ai is None:
        return JSONResponse(content={"error": "SidneyAI не инициализирована"})
    return JSONResponse(content=sidney_ai.get_status())


@app.post("/api/sidney/solve")
async def solve_sidney_task(request: Dict[str, str]):
    """Решить задачу: POST {task: "описание задачи"}"""
    if sidney_ai is None:
        return JSONResponse(content={"error": "SidneyAI не инициализирована"})
    
    task = request.get("task", "")
    if not task:
        return JSONResponse(content={"error": "Укажите задачу"}, status_code=400)
    
    result = await sidney_ai.solve_task(task)
    return JSONResponse(content=result)


@app.post("/api/sidney/analyze")
async def analyze_engines():
    """Анализ существующих игровых движков."""
    if sidney_ai is None:
        return JSONResponse(content={"error": "SidneyAI не инициализирована"})
    
    analysis = await sidney_ai.analyze_existing_engines()
    return JSONResponse(content=analysis)


@app.post("/api/sidney/design")
async def apply_sidney_design(request: Dict[str, Any]):
    """Применить дизайн игры пользователя."""
    if sidney_ai is None:
        return JSONResponse(content={"error": "SidneyAI не инициализирована"})
    
    from Wuglarst.sidney_ai import UserGameDesign
    
    design = UserGameDesign(
        game_type=request.get("game_type", "RPG"),
        target_platform=request.get("target_platform", "PC"),
        performance_target=request.get("performance_target", "60fps 4K"),
        description=request.get("description", ""),
        timestamp=datetime.now().isoformat(),
    )
    
    improvements = await sidney_ai.apply_user_design(design)
    return JSONResponse(content={
        "status": "ok",
        "improvements": len(improvements),
        "components": [
            {"name": c.name, "type": c.type, "features": c.features}
            for c in improvements
        ],
    })


@app.post("/api/sidney/engine/start")
async def start_sidney_engine():
    """Запуск SidneyAI."""
    global sidney_ai
    if sidney_ai is None:
        sidney_ai = SidneyAI(
            project_root=PROJECT_ROOT,
            system=system,
            growth=growth,
            manager=manager,
        )
    await sidney_ai.start()
    return JSONResponse(content={"status": "started"})


@app.post("/api/sidney/engine/stop")
async def stop_sidney_engine():
    """Остановка SidneyAI."""
    global sidney_ai
    if sidney_ai is not None:
        await sidney_ai.stop()
        return JSONResponse(content={"status": "stopped"})
    return JSONResponse(content={"status": "not_running"})


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket для реального времени."""
    await manager.connect(websocket)
    
    # Отправляем текущий статус
    await websocket.send_text(json.dumps(
        system.get_status(),
        ensure_ascii=False,
        default=str
    ))
    
    try:
        while True:
            data = await websocket.receive_text()
            message = json.loads(data)
            
            if message.get("type") == "request_update":
                await websocket.send_text(json.dumps(
                    system.get_status(),
                    ensure_ascii=False,
                    default=str
                ))
            elif message.get("type") == "register":
                client_id = message.get("client_id", "unknown")
                logger.info(f"📝 Регистрация клиента: {client_id}")
    
    except WebSocketDisconnect:
        manager.disconnect(websocket)
    except Exception as e:
        logger.error(f"WebSocket ошибка: {e}")
        manager.disconnect(websocket)


@app.get("/health")
async def health_check():
    """Проверка здоровья сервера."""
    return {
        "status": "healthy",
        "uptime": datetime.now().isoformat(),
        "scientists": len(system.scientists),
        "online": system.get_online_count(),
        "connections": len(manager.active_connections),
        "last_save": datetime.fromtimestamp(system.last_save_time).isoformat()
    }


# =====================================================================
#  HTML ДЛЯ ГЛАВНОЙ СТРАНИЦЫ
# =====================================================================

def _get_main_html() -> str:
    return """
<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Wuglarst — Автономный сервер</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #1a1a2e 0%, #16213e 50%, #0f3460 100%);
            color: #e0e0e0;
            min-height: 100vh;
        }
        .header {
            text-align: center;
            padding: 20px;
            background: rgba(0,0,0,0.3);
            border-bottom: 2px solid #e94560;
        }
        .header h1 { font-size: 2em; color: #e94560; }
        .header p { color: #a0a0a0; margin-top: 5px; }
        .stats {
            display: flex;
            justify-content: center;
            gap: 30px;
            padding: 20px;
            flex-wrap: wrap;
        }
        .stat-box {
            background: rgba(255,255,255,0.05);
            padding: 15px 25px;
            border-radius: 10px;
            text-align: center;
            min-width: 150px;
        }
        .stat-box .value { font-size: 2em; font-weight: bold; color: #e94560; }
        .stat-box .label { color: #a0a0a0; font-size: 0.9em; }
        .scientists {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(250px, 1fr));
            gap: 15px;
            padding: 20px;
            max-width: 1400px;
            margin: 0 auto;
        }
        .scientist-card {
            background: rgba(255,255,255,0.05);
            border-radius: 10px;
            padding: 15px;
            border-left: 4px solid #555;
            transition: all 0.3s;
        }
        .scientist-card:hover { transform: translateY(-2px); box-shadow: 0 5px 15px rgba(0,0,0,0.3); }
        .scientist-card.working { border-left-color: #4caf50; }
        .scientist-card.thinking { border-left-color: #2196f3; }
        .scientist-card.idle { border-left-color: #9e9e9e; }
        .scientist-card.error { border-left-color: #f44336; }
        .scientist-card.offline { border-left-color: #555; opacity: 0.5; }
        .scientist-card .header { display: flex; justify-content: space-between; align-items: center; }
        .scientist-card .name { font-size: 1.2em; font-weight: bold; }
        .scientist-card .avatar { font-size: 1.5em; }
        .scientist-card .task { color: #a0a0a0; margin-top: 8px; font-size: 0.9em; }
        .scientist-card .status { margin-top: 8px; font-size: 0.8em; text-transform: uppercase; }
        .status.working { color: #4caf50; }
        .status.thinking { color: #2196f3; }
        .status.idle { color: #9e9e9e; }
        .status.error { color: #f44336; }
        .status.offline { color: #555; }
        .btn {
            display: inline-block;
            padding: 10px 20px;
            background: #e94560;
            color: white;
            border: none;
            border-radius: 5px;
            cursor: pointer;
            margin: 10px;
            font-size: 1em;
        }
        .btn:hover { background: #c73650; }
        .footer {
            text-align: center;
            padding: 20px;
            color: #666;
            font-size: 0.8em;
        }
    </style>
</head>
<body>
    <div class="header">
        <h1>🌟 Wuglarst — Автономный сервер</h1>
        <p>Визуальное пространство для 13 ИИ-учёных</p>
    </div>
    
    <div class="stats" id="stats">
        <div class="stat-box">
            <div class="value" id="total-scientists">0</div>
            <div class="label">Всего девочек</div>
        </div>
        <div class="stat-box">
            <div class="value" id="online-scientists">0</div>
            <div class="label">Онлайн</div>
        </div>
        <div class="stat-box">
            <div class="value" id="uptime">--</div>
            <div class="label">Время работы</div>
        </div>
        <div class="stat-box">
            <div class="value" id="connections">0</div>
            <div class="label">Подключений</div>
        </div>
    </div>
    
    <div style="text-align: center;">
        <button class="btn" onclick="populateDemo()">🎮 Демо-данные</button>
        <button class="btn" onclick="refreshStatus()">🔄 Обновить</button>
    </div>
    
    <div class="scientists" id="scientists"></div>
    
    <div class="footer">
        Wuglarst Autonomous Server v2.0 | Часть системы PantikurAI
    </div>
    
    <script>
        const API_BASE = window.location.pathname;
        const API_URL = window.location.origin + API_BASE;
        let ws = null;
        
        async function fetchStatus() {
            try {
                const res = await fetch(`${API_URL}/api/status`);
                const data = await res.json();
                updateUI(data);
            } catch(e) {
                console.error('Ошибка загрузки:', e);
            }
        }
        
        function updateUI(data) {
            document.getElementById('total-scientists').textContent = data.scientists_count || 0;
            document.getElementById('online-scientists').textContent = Object.values(data.scientists || {}).filter(s => s.status !== 'offline').length;
            document.getElementById('uptime').textContent = data.uptime || '--';
            document.getElementById('connections').textContent = '—';
            
            const container = document.getElementById('scientists');
            container.innerHTML = '';
            
            for (const [name, sci] of Object.entries(data.scientists || {})) {
                const card = document.createElement('div');
                card.className = `scientist-card ${sci.status}`;
                card.innerHTML = `
                    <div class="header">
                        <span class="name">${sci.name}</span>
                        <span class="avatar">${sci.avatar}</span>
                    </div>
                    <div class="task">${sci.current_task || 'Нет задачи'}</div>
                    <div class="status ${sci.status}">${sci.status}</div>
                `;
                container.appendChild(card);
            }
        }
        
        async function populateDemo() {
            try {
                await fetch(`${API_URL}/api/demo/populate`, { method: 'POST' });
                fetchStatus();
            } catch(e) {
                console.error('Ошибка:', e);
            }
        }
        
        async function refreshStatus() {
            fetchStatus();
        }
        
        // WebSocket для реального времени
        function connectWS() {
            const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
            const path = API_URL.replace(window.location.origin, '');
            ws = new WebSocket(`${protocol}//${window.location.host}${path}/ws`);
            
            ws.onopen = () => console.log('WebSocket подключен');
            ws.onmessage = (event) => {
                const data = JSON.parse(event.data);
                if (data.data) updateUI(data.data);
            };
            ws.onclose = () => {
                console.log('WebSocket отключен, переподключение...');
                setTimeout(connectWS, 5000);
            };
        }
        
        // Инициализация
        fetchStatus();
        connectWS();
        setInterval(fetchStatus, 10000);
    </script>
</body>
</html>
    """


# =====================================================================
#  ЗАПУСК
# =====================================================================

if __name__ == "__main__":
    logger.info("🚀 Запуск Wuglarst Autonomous Server...")
    logger.info("📡 API: http://localhost:8001")
    logger.info("🌐 WebSocket: ws://localhost:8001/ws")
    logger.info("🏥 Health: http://localhost:8001/health")
    
    uvicorn.run(
        "server:app",
        host="0.0.0.0",
        port=8001,
        reload=False,
        log_level="info"
    )
