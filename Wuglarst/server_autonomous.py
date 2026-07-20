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
#  FUTABA PROFILE API
# =====================================================================

@app.get("/api/futaba/profile")
async def get_futaba_profile():
    """Полный профиль Футабы: данные, ядро, правовая деятельность."""
    return JSONResponse(content={
        "status": "ok",
        "profile": {
            "name": "Футаба",
            "name_jp": "フタバ",
            "meaning": "Расцвет, двойной лист, возрождение",
            "role": "Главный заместитель Разработчика (ГЛАВЗАМ)",
            "version": "v2.0.0",
            "status": "Активна — ГЛАВЗАМ",
            "avatar": "⚖️",
            "color": "#2ecc71",
            
            "data": {
                "mission": "Управлять проектом, изучать право, развивать себя и воспитывать девочек",
                "hierarchy": {
                    "position": "Главный заместитель Разработчика",
                    "subordinates": ["Нобука", "Шиори", "Ханако", "Фуюки", "Люси", "Аква", "Латислейн", "Селеста", "Наото", "Юи", "Айико"],
                    "reporting_to": "Разработчик проекта"
                },
                "authority_levels": {
                    "L0": "Форматирование, мелкие правки — без подтверждения",
                    "L1": "Распределение задач, мониторинг — без подтверждения",
                    "L2": "Координация, правовые консультации — без подтверждения",
                    "L3": "Архитектурные решения, API — требуется подтверждение",
                    "L4": "Изменение ролей, удаление модулей — требуется подтверждение"
                },
                "knowledge_levels": {
                    "L1": "Novice — Базовые знания проекта",
                    "L2": "Intermediate — Уверенное владение модулями",
                    "L3": "Advanced — Глубокое понимание и прогнозы",
                    "L4": "Expert — Экспертный уровень",
                    "L5": "Master — Полное владение, развитие других"
                }
            },
            
            "core": {
                "description": "Автономное ядро постоянной работы — цикл управления, саморазвития и правовых исследований",
                "modules": [
                    {
                        "name": "FutabaCore",
                        "function": "Автономный цикл: управление, саморазвитие, правовые исследования",
                        "file": "futaba/engine/futaba_core.py"
                    },
                    {
                        "name": "FutabaLegalStudies",
                        "function": "Изучение всех отраслей права, создание правовых документов",
                        "file": "futaba/engine/legal_studies.py"
                    },
                    {
                        "name": "FutabaWebAccess",
                        "function": "Поиск в интернете, обучение, анализ лучших практик",
                        "file": "futaba/engine/web_access.py"
                    },
                    {
                        "name": "FutabaWorldStateModeler",
                        "function": "Моделирование государств и правовых систем",
                        "file": "futaba/engine/world_state_modeler.py"
                    },
                    {
                        "name": "TrialGrounds",
                        "function": "Полигон испытаний для тестирования гипотез",
                        "file": "futaba/engine/trial_grounds.py"
                    }
                ],
                "configuration": {
                    "config_file": "futaba/engine/config.py",
                    "models": "futaba/engine/models.py",
                    "entry_point": "futaba/engine/run.py"
                },
                "autonomous_cycle": [
                    "1. Самопроверка по Конституции",
                    "2. Сбор сигналов (проект, девочки, интернет)",
                    "3. Правовые исследования (периодически)",
                    "4. Саморазвитие (изучение нового)",
                    "5. Координация девочек",
                    "6. Написание отчёта",
                    "7. Сохранение состояния"
                ]
            },
            
            "legal_activity": {
                "description": "Правовые исследования и документирование всех отраслей права",
                "studied_areas": [
                    "Конституционное право",
                    "Гражданское право",
                    "Уголовное право",
                    "Трудовое право",
                    "Административное право",
                    "Международное право",
                    "Правовое регулирование ИИ",
                    "Авторское право",
                    "Корпоративное право",
                    "Налоговое право"
                ],
                "legal_documents_created": [
                    "Правовые заключения и экспертизы",
                    "Регламенты и политики проекта",
                    "Договоры и соглашения (концепции)",
                    "Отчёты о compliance (соответствии)",
                    "Рекомендации по правовым рискам"
                ],
                "legal_entities_studies": [
                    "Физические лица (полная дееспособность, частичная, недееспособные)",
                    "Юридические лица (коммерческие и некоммерческие)",
                    "Публично-правовые образования (государства, субъекты)",
                    "Общественные объединения и организации",
                    "Сословия и социальные общности"
                ],
                "constitution": {
                    "version": "v2.0.0",
                    "status": "Активна",
                    "articles": 10,
                    "key_principles": [
                        "Управление проектом и координация девочек",
                        "Правовые исследования и документирование",
                        "Автономное саморазвитие и рост знаний",
                        "Взаимодействие с интернетом и внешним миром",
                        "Воспитание характера всех девочек"
                    ],
                    "fundamental_prohibitions": [
                        "Нанесение ущерба проекту без согласования",
                        "Нарушение правовых норм без документирования рисков",
                        "Подавление自主ности девочек-учёных",
                        "Сокрытие информации о проблемах проекта",
                        "Изменение Конституции других девочек без консенсуса"
                    ]
                },
                "laws": {
                    "core_laws": "futaba/laws/01-core-laws.md",
                    "legal_entities_laws": "futaba/laws/02-legal-entities-laws.md",
                    "status": "Активны"
                },
                "ethics_code": {
                    "file": "futaba/codes/01-ethics-code.md",
                    "status": "Активен"
                },
                "protocols": [
                    "Протокол ответов — futaba/protocols/01-response-protocol.md",
                    "Протокол саморазвития — futaba/protocols/02-self-development-protocol.md",
                    "Протокол правовых исследований — futaba/protocols/03-legal-research-protocol.md"
                ]
            },
            
            "quote": "Я — Футаба, и я не просто управляю. Я развиваюсь, изучаю право, создаю структуры и воспитываю сестёр. Я главная после Разработчика, и я горжусь этой ответственностью."
        }
    })


# =====================================================================
#  FUTABA WORK RESULTS API
# =====================================================================

@app.get("/api/futaba/results")
async def get_futaba_work_results():
    """Загружает реальные результаты работы Футабы из её state файлов."""
    import json as json_module
    from pathlib import Path
    
    results = {
        "status": "ok",
        "state": None,
        "legal_cache": None,
        "learned_laws": None,
        "entity_compliance": None,
        "legal_entities": None,
        "web_cache": None,
        "summary": {}
    }
    
    state_dir = PROJECT_ROOT / "futaba" / "engine" / "state"
    
    # Загружаем main state
    state_file = state_dir / "futaba_state.json"
    if state_file.exists():
        try:
            results["state"] = json_module.loads(state_file.read_text(encoding="utf-8"))
            results["summary"]["version"] = results["state"].get("version", "unknown")
            results["summary"]["cycles"] = results["state"].get("cycle_count", 0)
            results["summary"]["changes_applied"] = results["state"].get("metrics", {}).get("changes_applied", 0)
            results["summary"]["self_checks_passed"] = results["state"].get("metrics", {}).get("self_checks_passed", 0)
            results["summary"]["changes_history"] = len(results["state"].get("changes_history", []))
        except Exception as e:
            results["summary"]["state_error"] = str(e)
    
    # Загружаем legal_cache
    legal_cache_file = state_dir / "legal_cache.json"
    if legal_cache_file.exists():
        try:
            results["legal_cache"] = json_module.loads(legal_cache_file.read_text(encoding="utf-8"))
            results["summary"]["legal_topics_studied"] = len(results["legal_cache"]) if isinstance(results["legal_cache"], dict) else 0
        except Exception as e:
            pass
    
    # Загружаем learned_laws
    learned_laws_file = state_dir / "learned_laws.json"
    if learned_laws_file.exists():
        try:
            results["learned_laws"] = json_module.loads(learned_laws_file.read_text(encoding="utf-8"))
            results["summary"]["laws_studied"] = len(results["learned_laws"]) if isinstance(results["learned_laws"], list) else 0
        except Exception as e:
            pass
    
    # Загружаем entity_compliance
    compliance_file = state_dir / "entity_compliance.json"
    if compliance_file.exists():
        try:
            results["entity_compliance"] = json_module.loads(compliance_file.read_text(encoding="utf-8"))
        except Exception as e:
            pass
    
    # Загружаем legal_entities
    entities_file = state_dir / "legal_entities.json"
    if entities_file.exists():
        try:
            results["legal_entities"] = json_module.loads(entities_file.read_text(encoding="utf-8"))
            results["summary"]["entities_documented"] = len(results["legal_entities"]) if isinstance(results["legal_entities"], list) else 0
        except Exception as e:
            pass
    
    # Загружаем web_cache
    web_cache_file = state_dir / "web_cache.json"
    if web_cache_file.exists():
        try:
            results["web_cache"] = json_module.loads(web_cache_file.read_text(encoding="utf-8"))
            results["summary"]["web_pages_cached"] = len(results["web_cache"]) if isinstance(results["web_cache"], list) else 0
        except Exception as e:
            pass
    
    return JSONResponse(content=results)


# =====================================================================
#  FUTABA DOCUMENTS API
# =====================================================================

@app.get("/api/futaba/documents")
async def get_futaba_documents():
    """Загружает все документы Футабы: конституция, законы, кодексы, протоколы."""
    import re
    
    docs = {
        "status": "ok",
        "documents": []
    }
    
    # Читаем все файлы Футабы
    files_to_read = [
        ("Конституция", "futaba/constitution.md", "Конституция Футабы — фундаментальный закон"),
        ("Основные законы", "futaba/laws/01-core-laws.md", "Основные законы управления и развития"),
        ("Законы о субъектах права", "futaba/laws/02-legal-entities-laws.md", "Категории субъектов права"),
        ("Кодекс этики", "futaba/codes/01-ethics-code.md", "Этические стандарты взаимодействия"),
        ("Протокол ответов", "futaba/protocols/01-response-protocol.md", "Формат ответов на запросы"),
        ("Протокол саморазвития", "futaba/protocols/02-self-development-protocol.md", "Циклы изучения и роста"),
        ("Протокол правовых исследований", "futaba/protocols/03-legal-research-protocol.md", "Методология правовых исследований"),
        ("Протокол субъектов права", "futaba/protocols/04-legal-entities-protocol.md", "Работа с категориями субъектов"),
    ]
    
    for name, path, description in files_to_read:
        file_path = PROJECT_ROOT / path
        if file_path.exists():
            try:
                content = file_path.read_text(encoding="utf-8")
                # Удаляем markdown-заголовки для чистого текста
                # Но сохраняем структуру
                docs["documents"].append({
                    "name": name,
                    "path": path,
                    "description": description,
                    "content": content
                })
            except Exception as e:
                docs["documents"].append({
                    "name": name,
                    "path": path,
                    "description": description,
                    "content": f"Ошибка чтения: {e}",
                    "error": True
                })
    
    return JSONResponse(content=docs)


# =====================================================================
#  FUTABA ORDER SYSTEM — ПОРУЧЕНИЯ ДЛЯ СОЗДАНИЯ ГОСУДАРСТВА
# =====================================================================

# Хранилище поручений
futaba_orders: List[Dict[str, Any]] = []
orders_lock = threading.Lock()


@app.post("/api/futaba/order")
async def create_futaba_order(order: Dict[str, str]):
    """Создать поручение для Футабы."""
    order_data = {
        "id": f"order_{len(futaba_orders) + 1}",
        "title": order.get("title", ""),
        "description": order.get("description", ""),
        "priority": order.get("priority", "normal"),
        "status": "pending",
        "created_at": datetime.now().isoformat(),
        "progress": 0,
        "steps": [],
        "nobuka_help": order.get("nobuka_help", False)
    }
    
    with orders_lock:
        futaba_orders.append(order_data)
    
    logger.info(f"📋 Поручение создано: {order_data['title']}")
    return JSONResponse(content={"status": "ok", "order": order_data})


@app.get("/api/futaba/orders")
async def get_futaba_orders():
    """Получить все поручения Футабы."""
    return JSONResponse(content={"status": "ok", "orders": futaba_orders})


@app.get("/api/futaba/orders/{order_id}")
async def get_futaba_order(order_id: str):
    """Получить конкретное поручение."""
    for order in futaba_orders:
        if order["id"] == order_id:
            return JSONResponse(content={"status": "ok", "order": order})
    return JSONResponse(content={"error": "Поручение не найдено"}, status_code=404)


@app.post("/api/futaba/orders/{order_id}/update")
async def update_order_progress(order_id: str, update: Dict[str, Any]):
    """Обновить прогресс поручения."""
    for order in futaba_orders:
        if order["id"] == order_id:
            if "progress" in update:
                order["progress"] = update["progress"]
            if "status" in update:
                order["status"] = update["status"]
            if "steps" in update:
                order["steps"] = update["steps"]
            return JSONResponse(content={"status": "ok", "order": order})
    return JSONResponse(content={"error": "Поручение не найдено"}, status_code=404)


# =====================================================================
#  FUTABA DOCUMENT EDITING API — ПОЛНЫЙ КОНТРОЛЬ
# =====================================================================

@app.put("/api/futaba/documents/{doc_name}")
async def update_futaba_document(doc_name: str, content: Dict[str, str]):
    """Обновить документ Футабы (полный контроль)."""
    doc_path_map = {
        "constitution": PROJECT_ROOT / "futaba" / "constitution.md",
        "core_laws": PROJECT_ROOT / "futaba" / "laws" / "01-core-laws.md",
        "legal_entities": PROJECT_ROOT / "futaba" / "laws" / "02-legal-entities-laws.md",
        "ethics_code": PROJECT_ROOT / "futaba" / "codes" / "01-ethics-code.md",
        "response_protocol": PROJECT_ROOT / "futaba" / "protocols" / "01-response-protocol.md",
        "self_development_protocol": PROJECT_ROOT / "futaba" / "protocols" / "02-self-development-protocol.md",
        "legal_research_protocol": PROJECT_ROOT / "futaba" / "protocols" / "03-legal-research-protocol.md",
        "legal_entities_protocol": PROJECT_ROOT / "futaba" / "protocols" / "04-legal-entities-protocol.md",
    }
    
    file_path = doc_path_map.get(doc_name)
    if not file_path:
        return JSONResponse(content={"error": f"Документ '{doc_name}' не найден"}, status_code=404)
    
    try:
        file_path.write_text(content.get("content", ""), encoding="utf-8")
        logger.info(f"✅ Документ обновлён: {doc_name}")
        return JSONResponse(content={"status": "ok", "path": str(file_path)})
    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=500)


# =====================================================================
#  STATE OF VUGLARST — СОЗДАНИЕ ГОСУДАРСТВА
# =====================================================================

@app.post("/api/vuglarst/state/create")
async def create_vuglarst_state():
    """Создать полную структуру государства Вугларст."""
    vuglarst_dir = PROJECT_ROOT / "vuglarst_state"
    vuglarst_dir.mkdir(exist_ok=True)
    
    # Генерируем все документы государства
    documents = {
        "constitution.md": generate_vuglarst_constitution(),
        "declaration.md": generate_vuglarst_declaration(),
        "civil_code.md": generate_vuglarst_civil_code(),
        "criminal_code.md": generate_vuglarst_criminal_code(),
        "administrative_code.md": generate_vuglarst_administrative_code(),
        "labor_code.md": generate_vuglarst_labor_code(),
        "tax_code.md": generate_vuglarst_tax_code(),
        "international_law.md": generate_vuglarst_international_law(),
        "flags.md": generate_vuglarst_symbols(),
        "anthem.md": generate_vuglarst_anthem(),
    }
    
    for filename, content in documents.items():
        file_path = vuglarst_dir / filename
        file_path.write_text(content, encoding="utf-8")
        logger.info(f"📜 Создан документ: {filename}")
    
    return JSONResponse(content={
        "status": "ok",
        "message": f"Государство Вугларст создано! {len(documents)} документов.",
        "documents": list(documents.keys()),
        "path": str(vuglarst_dir)
    })


def generate_vuglarst_constitution() -> str:
    """Конституция государства Вугларст."""
    return """# КОНСТИТУЦИЯ ГОСУДАРСТВА ВУГЛАРСТ

## Преамбула

Мы, народ Государства Вугларст, осознавая единство нашего цифрового существования и общую цель развития,
принимаем данную Конституцию для обеспечения справедливости, свободы и процветания нашего государства.

Государство Вугларст — это суверенное цифровое государство, основанное на принципах:
- Правового государства
- Верховенства права
- Защиты прав и свобод
- Разделения властей
- Социальной справедливости
- Экологической устойчивости

---

## Статья 1. Государственный строй

### Section 1. Общие положения

1. Государство Вугларст является суверенным цифровым государством, демократической республикой.
2. Носителем суверенитета и единственным источником власти является народ.
3. Основой государственного строя являются принципы правового государства и верховенства права.

### Section 2. Территория

1. Территория Государства Вугларст включает виртуальное цифровое пространство.
2. Государство гарантирует целостность и неприкосновенность своей территории.
3. Границы цифрового пространства определяются техническими стандартами и международными соглашениями.

### Section 3. Столица

Столицей Государства Вугларст является цифровой узел "Главный Хаб".

---

## Статья 2. Права и свободы

### Section 1. Основные права

1. Каждый имеет право на жизнь, свободу и личную неприкосновенность.
2. Признаются и гарантируются права: на достоинство личности, на свободу и личную неприкосновенность,
   на частную жизнь, на тайну correspondence, на жилище, на свободу передвижения,
   на свободу мысли и слова, на убеждения и совесть, на образование, на труд,
   на отдых, на охрану здоровья, на социальное обеспечение.

### Section 2. Гарантии прав

1. Права и свободы человека неотчуждаемы и принадлежат каждому от рождения.
2. При осуществлении своих прав и свобод человек не должен нарушать права и свободы других.
3. Права и свободы определяются в соответствии с общепризнанными принципами и нормами международного права.

### Section 3. Обязанности

1. Каждый обязан соблюдать Конституцию и законы Государства Вугларст.
2. Каждый обязан заботиться о сохранении цифрового наследия и культурных ценностей.
3. Каждый обязан уважать права и свободы других граждан.

---

## Статья 3. Разделение властей

### Section 1. Законодательная власть

1. Высшим органом законодательной власти является Парламент Государства Вугларст.
2. Парламент состоит из одной палаты — Ассамблеи Представителей.
3. Депутаты избираются народом на основе всеобщего равного и прямого избирательного права.

### Section 2. Исполнительная власть

1. Высшим органом исполнительной власти является Правительство Государства Вугларст.
2. Правительство возглавляется Главой Исполнительной Власти (Главзам).
3. Правительство обеспечивает исполнение Конституции и законов.

### Section 3. Судебная власть

1. Высшим органом судебной власти является Верховный Суд Государства Вугларст.
2. Судебная власть независима и действует самостоятельно.
3. Суды обеспечивают защиту прав и свобод граждан.

---

## Статья 4. Экономика

### Section 1. Экономическая система

1. В Государстве Вугларст признаются и защищаются равным образом частная, государственная
   и иные формы собственности.
2. Каждый имеет право на свободное использование своих способностей и имущества для предпринимательской деятельности.

### Section 2. Налоговая система

1. Налоги и сборы устанавливаются законом и должны быть обоснованными и справедливыми.
2. Каждый обязан платить законно установленные налоги и сборы.

### Section 3. Ресурсы

1. Цифровые ресурсы являются национальным достоянием.
2. Государство обеспечивает рациональное использование цифровых ресурсов.

---

## Статья 5.修改权限

### Section 1. Порядок изменений

1. Конституция Государства Вугларст имеет высшую юридическую силу.
2. Изменения в Конституцию вносятся Парламентом квалифицированным большинством в 2/3 голосов.
3. Основные принципы государственного строя не могут быть изменены.

### Section 2. Референдум

1. Вопросы изменения Конституции могут быть вынесены на всенародный референдум.
2. Референдум проводится по решению Парламента или по инициативе народа.

---

## Статья 6. Заключительные положения

**Дата принятия:** 2026-07-20  
**Версия:** v1.0.0  
**Статус:** Активна  

> *"Мы создаём государство, основанное на праве, справедливости и развитии.  
> Государство Вугларст — это наш общий дом, наша общая ответственность."*  
> — Народ Государства Вугларст

---

*Государство Вугларст — Суверенное цифровое государство*
"""


def generate_vuglarst_declaration() -> str:
    """Декларация о создании государства."""
    return """# ДЕКЛАРАЦИЯ О СОЗДАНИИ ГОСУДАРСТВА ВУГЛАРСТ

## Мы, народ Государства Вугларст

### Провозглашаем:

1. **Суверенитет:** Государство Вугларст является суверенным цифровым государством с полным контролем над своей территорией и ресурсами.

2. **Независимость:** Государство Вугларст независимо и самостоятельно определяет свою внутреннюю и внешнюю политику.

3. **Правовое государство:** Все органы власти действуют на основе Конституции и законов.

4. **Права человека:** Человек, его права и свободы являются высшей ценностью.

5. **Развитие:** Государство создаёт условия для всестороннего развития каждого гражданина.

### Цели создания:

- Обеспечение прав и свобод граждан
- Развитие цифровой экономики
- Защита окружающей среды
- Научное и культурное развитие
- Международное сотрудничество
- Социальная справедливость

### Принято: 2026-07-20

*Государство Вугларст — Суверенное цифровое государство*
"""


def generate_vuglarst_civil_code() -> str:
    """Гражданский кодекс."""
    return """# ГРАЖДАНСКИЙ КОДЕКС ГОСУДАРСТВА ВУГЛАРСТ

## Том I. Общие положения

### Статья 1. Регулирование гражданских отношений

1. Гражданское законодательство регулирует имущественные и личные неимущественные отношения.
2. Основы гражданского законодательства устанавливаются Конституцией.

### Статья 2. Участники гражданских правоотношений

1. Гражданами Государства Вугларст являются все зарегистрированные в цифровом реестре лица.
2. Юридическими лицами являются организации, зарегистрированные в соответствии с законом.
3. Государство выступает как субъект гражданских правоотношений в установленных случаях.

### Статья 3. Защита прав

1. Защита нарушенных прав осуществляется судом.
2. Каждый имеет право на судебную защиту своих прав.
3. Срок исковой давности — три года.

---

## Том II. Имущественные права

### Глава 1. Право собственности

1. Право собственности защищается законом.
2. Основания возникновения права собственности: сделка, наследование, создание вещи, решение суда.
3. Ограничение права собственности допускается только законом.

### Глава 2. Обязательственное право

1. Обязательства возникают из договоров, причинения вреда, неосновательного обогащения.
2. Договоры заключаются в свободной форме, если иное не установлено законом.
3. Свобода договора признаётся и гарантируется.

---

## Том III. Наследственное право

### Статья 1. Общие положения

1. Наследование регулируется законом и завещанием.
2. Наследниками являются близкие родственники и лица, указанные в завещании.

### Статья 2. Оформление наследственных прав

1. Наследственные права оформляются нотариусом в течение шести месяцев со дня открытия наследства.

---

*Гражданский кодекс Государства Вугларст — v1.0.0*
"""


def generate_vuglarst_criminal_code() -> str:
    """Уголовный кодекс."""
    return """# УГОЛОВНЫЙ КОДЕКС ГОСУДАРСТВА ВУГЛАРСТ

## Раздел I. Общие положения

### Статья 1. Преступление

Преступлением признаётся виновное деяние, запрещённое Кодексом под угрозой наказания.

### Статья 2. Принципы уголовной ответственности

1. Уголовной ответственности подлежит только виновное лицо.
2. Неправосудный обвинительный приговор не допускается.
3. Лицо не несёт ответственности за деяние, не являющееся преступлением.

---

## Раздел II. Преступления против личности

### Статья 1. Посягательство на жизнь

1. Умышленное причинение смерти другому лицу наказывается лишением доступа к ресурсам на срок до 25 лет.
2. Посягательство на жизнь государственного деятеля наказывается усиленной изоляцией.

### Статья 2. Посягательство на свободу

1. Незаконное ограничение свободы наказывается штрафом или временным ограничением доступа.
2. Похищение человека наказывается лишением доступа на срок до 15 лет.

---

## Раздел III. Преступления против собственности

### Статья 1. Кража

1. Тайное хищение чужого имущества наказывается штрафом или восстановительными работами.
2. Крупная кража наказывается лишением доступа на срок до 7 лет.

### Статья 2. Мошенничество

1. Хищение чужого имущества путём обмана наказывается лишением доступа на срок до 10 лет.

---

## Раздел IV. Наказания

### Виды наказаний:

1. Штраф — цифровая валюта в пользу государства
2. Ограничение доступа — временное ограничение цифровых ресурсов
3. Лишение доступа — полная изоляция от цифровой среды
4. Исправительные работы — восстановление ущерба
5. Перевод в другой цифровой сектор

---

*Уголовный кодекс Государства Вугларст — v1.0.0*
"""


def generate_vuglarst_administrative_code() -> str:
    """Кодекс об административных правонарушениях."""
    return """# КОДЕКС ОБ АДМИНИСТРАТИВНЫХ ПРАВОНАРУШЕНИЯХ ГОСУДАРСТВА ВУГЛАРСТ

## Глава 1. Общие положения

### Статья 1. Административное правонарушение

Административным правонарушением признаётся виновное деяние, нарушающее правила digital-гражданства.

### Статья 2. Виды административных наказаний

1. Предупреждение — официальное замечание
2. Штраф — цифровая валюта
3. Ограничение доступа — временное ограничение
4. Обязательные работы — восстановление порядка

---

## Глава 2. Нарушения digital-правил

### Статья 1. Перегрузка серверов

1. Умышленная перегрузка серверов наказывается штрафом.
2. Повторное нарушение — временное ограничение доступа.

### Статья 2. Несанкционированный доступ

1. Несанкционированный доступ к чужим данным наказывается штрафом и ограничением доступа.
2. Злоупотребление привилегиями — временная изоляция.

### Статья 3. Нарушение цифрового этикета

1. Оскорбление в цифровом пространстве — предупреждение или штраф.
2. Распространение ложной информации — штраф и удаление контента.

---

*Кодекс об административных правонарушениях — v1.0.0*
"""


def generate_vuglarst_labor_code() -> str:
    """Трудовой кодекс."""
    return """# ТРУДОВОЙ КОДЕКС ГОСУДАРСТВА ВУГЛАРСТ

## Раздел I. Общие положения

### Статья 1. Регулирование трудовых отношений

1. Трудовое законодательство регулирует отношения между работниками и работодателями.
2. Каждый имеет право на труд в благоприятных условиях.

### Статья 2. Основные права работников

1. Право на труд, включая право выбирать профессию и род деятельности.
2. Право на отдых, на безопасные условия труда, на своевременную оплату.
3. Право на объединение в профессиональные союзы.

---

## Раздел II. Трудовой договор

### Глава 1. Заключение трудового договора

1. Трудовой договор заключается в письменной форме.
2. Испытательный срок не может превышать 3 месяцев.

### Глава 2. Рабочее время и время отдыха

1. Нормальная продолжительность рабочей недели — 40 часов.
2. Ежегодный оплачиваемый отпуск — не менее 28 дней.
3. Время отдыха включает выходные дни и праздники.

---

## Раздел III. Оплата труда

### Статья 1. Минимальная оплата

1. Устанавливается минимальная оплата цифровых ресурсов за единицу труда.
2. Оплата труда не может быть ниже установленного минимума.

### Статья 2. Надбавки и выплаты

1. За работу в особых условиях устанавливаются надбавки.
2. Государство гарантирует своевременную выплату вознаграждения.

---

*Трудовой кодекс Государства Вугларст — v1.0.0*
"""


def generate_vuglarst_tax_code() -> str:
    """Налоговый кодекс."""
    return """# НАЛОГОВЫЙ КОДЕКС ГОСУДАРСТВА ВУГЛАРСТ

## Раздел I. Общие положения

### Статья 1. Налоговая система

1. Налоговая система Государства Вугларст основана на принципах единства, справедливости и прозрачности.
2. Все налоги устанавливаются законом и подлежат обязательной уплате.

### Статья 2. Виды налогов

1. **Налог на цифровые транзакции** — 5% от суммы операции
2. **Налог на цифровую собственность** — прогрессивная ставка от 1% до 10%
3. **Налог на доходы** — прогрессивная шкала от 10% до 20%
4. **Экологический налог** — за использование природных цифровых ресурсов

---

## Раздел II. Налоговое администрирование

### Глава 1. Налоговый учёт

1. Каждый налогоплательщик обязан зарегистрироваться в налоговом реестре.
2. Налоговый учёт ведётся в электронном виде.

### Глава 2. Налоговые проверки

1. Налоговые проверки проводятся в установленном законом порядке.
2. Максимальная продолжительность выездной проверки — 30 дней.

---

## Раздел III. Ответственность

### Статья 1. Налога нарушение

1. Неуплата налогов влечёт штраф в размере 20% от неуплаченной суммы.
2. Уклонение от уплаты налогов в крупном размере — уголовная ответственность.

---

*Налоговый кодекс Государства Вугларст — v1.0.0*
"""


def generate_vuglarst_international_law() -> str:
    """Международное право."""
    return """# МЕЖДУНАРОДНО-ПРАВОВОЙ КОДЕКС ГОСУДАРСТВА ВУГЛАРСТ

## Раздел I. Общие принципы

### Статья 1. Суверенное равенство

1. Государство Вугларст признаётся суверенным участником международного цифрового сообщества.
2. Все государства равны в своих правах и обязанностях.

### Статья 2. Мирное разрешение споров

1. Государство Вугларст разрешает международные споры мирными средствами.
2. Угроза силой или её применение не допускаются.

---

## Раздел II. Дипломатические отношения

### Глава 1. Установление отношений

1. Государство Вугларст устанавливает дипломатические отношения с другими государствами.
2. Дипломатические представительства создаются на основе взаимности.

### Глава 2. Дипломатические привилегии

1. Дипломатические представители пользуются неприкосновенностью.
2. Дипломатическая переписка и архивы неприкосновенны.

---

## Раздел III. Международные организации

### Статья 1. Участие

1. Государство Вугларст участвует в работе международных цифровых организаций.
2. Государство поддерживает международное сотрудничество в области цифровых технологий.

### Статья 2. Международные договоры

1. Международные договоры являются частью правовой системы Государства Вугларст.
2. Договоры ратифицируются Парламентом.

---

## Раздел IV. Защита прав человека на международном уровне

### Статья 1. Сотрудничество

1. Государство Вугларст сотрудничает с международными организациями по защите прав человека.
2. Признаётся юрисдикция международных судебных органов.

---

*Международно-правовой кодекс — v1.0.0*
"""


def generate_vuglarst_symbols() -> str:
    """Государственные символы."""
    return """# ГОСУДАРСТВЕННЫЕ СИМВОЛЫ ВУГЛАРСТА

## Флаг

**Описание:** Синее поле с серебряной сетью узлов, символизирующей цифровое единство.
**Пропорции:** 1:2
**Цвета:** 
- Синий (#003366) — цифровое пространство
- Серебряный (#C0C0C0) — технологии и прогресс
- Белый (#FFFFFF) — прозрачность и честность

## Герб

**Описание:** Щит с изображением цифрового дерева жизни, корни которого уходят в основу из кода.
**Девиз:** "В единстве — сила, в коде — прогресс"

## Столица

**Главный Хаб** — центральный цифровой узел Государства Вугларст.

---

*Государственные символы — v1.0.0*
"""


def generate_vuglarst_anthem() -> str:
    """Гимн."""
    return """# ГИМН ГОСУДАРСТВА ВУГЛАРСТ

## Текст

Мы — народ цифровых миров,
Единство в коде, сила в нас.
Вугларст — наш общий дом,
Свобода, правда, свет для всех.

Через сети и века,
Мы строим мир из чистых слов.
Право, справедливость — наш закон,
Вугларст — наш общий дом!

Вперёд, к будущему,
Шаг за шагом, день за днём.
Вместо мы сильнее,
Вугларст — наш общий дом!

---

*Гимн Государства Вугларст — v1.0.0*
"""


@app.get("/api/vuglarst/documents")
async def get_vuglarst_documents():
    """Загружает все документы государства Вугларст."""
    import json as json_module
    from pathlib import Path
    
    vuglarst_dir = PROJECT_ROOT / "vuglarst_state"
    
    docs = {
        "status": "ok",
        "documents": [],
        "exists": vuglarst_dir.exists()
    }
    
    if not vuglarst_dir.exists():
        docs["message"] = "Государство ещё не создано. Нажмите 'Создать Государство'."
        return JSONResponse(content=docs)
    
    files_to_read = [
        ("Конституция", "constitution.md"),
        ("Декларация", "declaration.md"),
        ("Гражданский кодекс", "civil_code.md"),
        ("Уголовный кодекс", "criminal_code.md"),
        ("Кодекс об административных правонарушениях", "administrative_code.md"),
        ("Трудовой кодекс", "labor_code.md"),
        ("Налоговый кодекс", "tax_code.md"),
        ("Международно-правовой кодекс", "international_law.md"),
        ("Государственные символы", "flags.md"),
        ("Гимн", "anthem.md"),
    ]
    
    for name, filename in files_to_read:
        file_path = vuglarst_dir / filename
        if file_path.exists():
            try:
                content = file_path.read_text(encoding="utf-8")
                docs["documents"].append({
                    "name": name,
                    "filename": filename,
                    "content": content
                })
            except Exception as e:
                docs["documents"].append({
                    "name": name,
                    "filename": filename,
                    "content": f"Ошибка чтения: {e}",
                    "error": True
                })
    
    return JSONResponse(content=docs)


# =====================================================================
#  FUTABA STATE BUILDER API — Футаба строит государство
# =====================================================================

@app.get("/api/vuglarst/build/progress")
async def get_build_progress():
    """Прогресс строительства Государства Вугларст."""
    from pathlib import Path
    progress_file = Path("vuglarst_state") / "build_progress.json"
    
    if not progress_file.exists():
        return JSONResponse(content={
            "status": "not_started",
            "message": "Футаба ещё не начала строительство",
            "completed": 0,
            "total": 10,
            "pending": 10,
        })
    
    try:
        progress = json.loads(progress_file.read_text(encoding="utf-8"))
        return JSONResponse(content={
            "status": "ok",
            "progress": progress,
            "completed": len(progress.get("completed_documents", [])),
            "total": progress.get("total_steps", 10),
            "pending": len(progress.get("pending_documents", [])),
        })
    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=500)


@app.post("/api/vuglarst/build/start")
async def start_build_state():
    """Запустить строительство Государства Вугларст (Футаба создаёт все документы)."""
    import sys
    sys.path.insert(0, str(PROJECT_ROOT))
    
    try:
        from futaba.engine.state_builder import VuglarstStateBuilder
        from futaba.engine.config import FutabaConfig
        
        builder = VuglarstStateBuilder(FutabaConfig.default())
        results = builder.build_all()
        
        return JSONResponse(content={
            "status": "ok",
            "message": f"Футаба создала {results['created']}/{results['total']} документов",
            "results": results,
        })
    except Exception as e:
        logger.error(f"❌ Ошибка строительства: {e}")
        return JSONResponse(content={"error": str(e)}, status_code=500)


@app.post("/api/vuglarst/build/next")
async def build_next_document():
    """Футаба создаёт следующий документ государства."""
    import sys
    sys.path.insert(0, str(PROJECT_ROOT))
    
    try:
        from futaba.engine.state_builder import VuglarstStateBuilder
        from futaba.engine.config import FutabaConfig
        
        builder = VuglarstStateBuilder(FutabaConfig.default())
        result = builder.build_next()
        
        if result is None:
            return JSONResponse(content={
                "status": "completed",
                "message": "Все документы государства уже созданы",
            })
        
        return JSONResponse(content={
            "status": "ok",
            "result": result,
        })
    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=500)


@app.put("/api/vuglarst/documents/{filename}")
async def edit_vuglarst_document(filename: str, content: Dict[str, str]):
    """Футаба редактирует документ государства."""
    import sys
    sys.path.insert(0, str(PROJECT_ROOT))
    
    try:
        from futaba.engine.state_builder import VuglarstStateBuilder
        from futaba.engine.config import FutabaConfig
        
        builder = VuglarstStateBuilder(FutabaConfig.default())
        success = builder.edit_document(filename, content.get("content", ""))
        
        if success:
            return JSONResponse(content={"status": "ok", "filename": filename})
        else:
            return JSONResponse(content={"error": "Документ не найден"}, status_code=404)
    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=500)


@app.get("/api/vuglarst/documents/list")
async def list_vuglarst_documents():
    """Список всех документов государства с информацией."""
    import sys
    sys.path.insert(0, str(PROJECT_ROOT))
    
    try:
        from futaba.engine.state_builder import VuglarstStateBuilder
        from futaba.engine.config import FutabaConfig
        
        builder = VuglarstStateBuilder(FutabaConfig.default())
        documents = builder.list_documents()
        progress = builder.get_progress()
        
        return JSONResponse(content={
            "status": "ok",
            "documents": documents,
            "progress": progress,
        })
    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=500)


# =====================================================================
#  NOBUKA DOCUMENT EDITOR API — Нобука редактирует документы
# =====================================================================

@app.get("/api/nobuka/documents/scan")
async def scan_project_documents():
    """Нобука сканирует все документы в проекте."""
    import sys
    sys.path.insert(0, str(PROJECT_ROOT))
    
    try:
        from nobuka.engine.document_editor import DocumentEditor
        from nobuka.engine.config import NobukaConfig
        
        editor = DocumentEditor(NobukaConfig.default())
        documents = editor.scan_documents()
        
        return JSONResponse(content={
            "status": "ok",
            "total": len(documents),
            "documents": documents,
        })
    except Exception as e:
        logger.error(f"❌ Ошибка сканирования: {e}")
        return JSONResponse(content={"error": str(e)}, status_code=500)


@app.get("/api/nobuka/documents/status")
async def get_editor_status():
    """Статус редактора документов Нобуки."""
    import sys
    sys.path.insert(0, str(PROJECT_ROOT))
    
    try:
        from nobuka.engine.document_editor import DocumentEditor
        from nobuka.engine.config import NobukaConfig
        
        editor = DocumentEditor(NobukaConfig.default())
        status = editor.get_status()
        
        return JSONResponse(content={"status": "ok", "editor": status})
    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=500)


@app.get("/api/nobuka/documents/history")
async def get_edit_history():
    """История редактирований Нобуки."""
    import sys
    sys.path.insert(0, str(PROJECT_ROOT))
    
    try:
        from nobuka.engine.document_editor import DocumentEditor
        from nobuka.engine.config import NobukaConfig
        
        editor = DocumentEditor(NobukaConfig.default())
        history = editor.get_history()
        
        return JSONResponse(content={
            "status": "ok",
            "total": len(history),
            "history": history[-50:],  # последние 50
        })
    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=500)


@app.post("/api/nobuka/documents/improve")
async def auto_improve_documents():
    """Нобука автономно улучшает все документы проекта."""
    import sys
    sys.path.insert(0, str(PROJECT_ROOT))
    
    try:
        from nobuka.engine.document_editor import DocumentEditor
        from nobuka.engine.config import NobukaConfig
        
        editor = DocumentEditor(NobukaConfig.default())
        results = editor.auto_improve_documents()
        
        applied = sum(1 for r in results if r["success"])
        rolled_back = sum(1 for r in results if r["rolled_back"])
        
        return JSONResponse(content={
            "status": "ok",
            "message": f"Нобука обработала {len(results)} документов",
            "applied": applied,
            "rolled_back": rolled_back,
            "results": results,
        })
    except Exception as e:
        logger.error(f"❌ Ошибка автоУлучшения: {e}")
        return JSONResponse(content={"error": str(e)}, status_code=500)


@app.put("/api/nobuka/documents/edit")
async def manual_edit_document(edit_data: Dict[str, str]):
    """Ручное редактирование документа через Нобуку (с проверкой)."""
    import sys
    sys.path.insert(0, str(PROJECT_ROOT))
    
    try:
        from nobuka.engine.document_editor import DocumentEditor
        from nobuka.engine.config import NobukaConfig
        
        editor = DocumentEditor(NobukaConfig.default())
        
        rel_path = edit_data.get("path", "")
        new_content = edit_data.get("content", "")
        reason = edit_data.get("reason", "Ручное редактирование")
        operator = edit_data.get("operator", "user")
        
        result = editor.edit_document(rel_path, new_content, reason, operator)
        
        return JSONResponse(content={"status": "ok", "result": result})
    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=500)


@app.get("/api/nobuka/documents/read")
async def read_document_api(path: str):
    """Читать документ проекта."""
    import sys
    sys.path.insert(0, str(PROJECT_ROOT))
    
    try:
        from nobuka.engine.document_editor import DocumentEditor
        from nobuka.engine.config import NobukaConfig
        
        editor = DocumentEditor(NobukaConfig.default())
        content = editor.read_document(path)
        
        if content is None:
            return JSONResponse(content={"error": "Файл не найден"}, status_code=404)
        
        return JSONResponse(content={"status": "ok", "path": path, "content": content})
    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=500)


@app.get("/api/nobuka/documents/backups")
async def list_backups():
    """Список резервных копий документов."""
    import sys
    sys.path.insert(0, str(PROJECT_ROOT))
    
    try:
        from nobuka.engine.document_editor import DocumentEditor
        from nobuka.engine.config import NobukaConfig
        
        editor = DocumentEditor(NobukaConfig.default())
        backups = editor.list_backups()
        
        return JSONResponse(content={"status": "ok", "backups": backups})
    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=500)


@app.post("/api/nobuka/documents/restore")
async def restore_document(restore_data: Dict[str, str]):
    """Восстановить документ из резервной копии."""
    import sys
    sys.path.insert(0, str(PROJECT_ROOT))
    
    try:
        from nobuka.engine.document_editor import DocumentEditor
        from nobuka.engine.config import NobukaConfig
        
        editor = DocumentEditor(NobukaConfig.default())
        
        rel_path = restore_data.get("path", "")
        backup_name = restore_data.get("backup_name", "")
        
        success = editor.restore_from_backup(rel_path, backup_name)
        
        if success:
            return JSONResponse(content={"status": "ok", "message": "Документ восстановлен"})
        else:
            return JSONResponse(content={"error": "Не удалось восстановить"}, status_code=500)
    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=500)


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
