"""
Вугларст (Wuglarst) — Визуальное пространство для наблюдения за 12 ИИ-девушками.
FastAPI сервер с WebSocket для передачи данных в реальном времени.
"""

from __future__ import annotations

import asyncio
import json
import logging
from datetime import datetime
from pathlib import Path
from pydantic import BaseModel
from typing import Any, Dict, List, Optional

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s"
)
logger = logging.getLogger("Wuglarst")

# Создание FastAPI приложения
app = FastAPI(
    title="Wuglarst — Visual Space for AI Scientists",
    version="1.0.0"
)

# Подключение статических файлов
static_dir = Path(__file__).parent / "static"
static_dir.mkdir(exist_ok=True)
app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")


class ConnectionManager:
    """Управление WebSocket-соединениями."""

    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        """Подключение нового клиента."""
        await websocket.accept()
        self.active_connections.append(websocket)
        logger.info(f"🔌 Клиент подключен. Всего: {len(self.active_connections)}")

    def disconnect(self, websocket: WebSocket):
        """Отключение клиента."""
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)
        logger.info(f"🔌 Клиент отключен. Всего: {len(self.active_connections)}")

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

        # Удаляем отключенные клиенты
        for conn in disconnected:
            self.disconnect(conn)


# Глобальный менеджер соединений
manager = ConnectionManager()


# =====================================================================
#  МОДЕЛИ ДАННЫХ
# =====================================================================

class ScientistState(BaseModel):
    """Состояние одной ИИ-девушки."""

    name: str
    avatar: str = "👩‍🔬"
    status: str = "idle"  # idle, working, thinking, error
    current_task: str = ""
    personality: Dict[str, float] = {}
    last_activity: str = ""
    x: int = 0  # Позиция на карте
    y: int = 0


class WuglarstSystem:
    """Глобальное состояние системы Вугларст."""

    def __init__(self):
        self.scientists: Dict[str, ScientistState] = {}
        self.events: List[Dict[str, Any]] = []
        self.data_streams: List[Dict[str, Any]] = []
        self.last_update: Optional[str] = None

    def update_scientist(self, name: str, state: ScientistState):
        """Обновляет состояние ИИ-девушки."""
        if not state.last_activity:
            state.last_activity = datetime.now().isoformat()
        self.scientists[name] = state
        self.last_update = datetime.now().isoformat()

        # Добавляем событие
        if state.current_task:
            self.events.insert(0, {
                "timestamp": datetime.now().isoformat(),
                "scientist": name,
                "event": f"{state.avatar} {name}: {state.current_task}",
                "type": "task_update",
            })

    def add_event(self, scientist: str, event_type: str, message: str):
        """Добавляет событие в журнал."""
        self.events.insert(0, {
            "timestamp": datetime.now().isoformat(),
            "scientist": scientist,
            "event": message,
            "type": event_type,
        })
        # Храним только последние 50 событий
        if len(self.events) > 50:
            self.events = self.events[:50]

    def get_status(self) -> Dict[str, Any]:
        """Возвращает полный статус системы."""
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
            }
        
        return {
            "timestamp": self.last_update or datetime.now().isoformat(),
            "scientists": scientists_dict,
            "events": self.events[:20],
            "data_streams": self.data_streams[-10:],
        }


# Глобальная система
system = WuglarstSystem()


# =====================================================================
#  API ЭНДПОИНТЫ
# =====================================================================

@app.get("/", response_class=HTMLResponse)
async def index():
    """Главная страница."""
    index_path = static_dir / "index.html"
    if index_path.exists():
        return index_path.read_text(encoding="utf-8")
    return """
    <html>
    <head><title>Wuglarst</title></head>
    <body>
        <h1>🌟 Wuglarst — Визуальное пространство ИИ</h1>
        <p>Веб-интерфейс пока не создан. Используйте API.</p>
        <h2>Эндпоинты:</h2>
        <ul>
            <li><code>GET /api/status</code> — статус системы</li>
            <li><code>POST /api/scientist/{name}/update</code> — обновить состояние</li>
            <li><code>GET /ws</code> — WebSocket для реального времени</li>
        </ul>
    </body>
    </html>
    """


@app.get("/api/status")
async def get_status():
    """Получить полный статус системы."""
    return system.get_status()


@app.post("/api/scientist/{name}/update")
async def update_scientist(
    name: str,
    state: ScientistState
):
    """Обновить состояние ИИ-девушки."""
    system.update_scientist(name, state)
    logger.info(f"📡 Обновление: {name} → {state.status}")

    # Отправляем обновление всем WebSocket-клиентам
    await manager.broadcast({
        "type": "scientist_update",
        "data": system.get_status(),
    })

    return {"status": "ok", "scientist": name}


@app.post("/api/scientist/{name}/event")
async def add_event(
    name: str,
    event: Dict[str, str]
):
    """Добавить событие в журнал."""
    system.add_event(
        scientist=name,
        event_type=event.get("type", "general"),
        message=event.get("message", ""),
    )

    # Отправляем обновление
    await manager.broadcast({
        "type": "event_update",
        "data": system.get_status(),
    })

    return {"status": "ok"}


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket для передачи данных в реальном времени."""
    await manager.connect(websocket)

    # Отправляем текущий статус при подключении
    await websocket.send_text(json.dumps(
        system.get_status(),
        ensure_ascii=False,
        default=str
    ))

    try:
        while True:
            # Ждем сообщения от клиента (например, запрос на обновление)
            data = await websocket.receive_text()
            message = json.loads(data)

            if message.get("type") == "request_update":
                # Отправляем актуальный статус
                await websocket.send_text(json.dumps(
                    system.get_status(),
                    ensure_ascii=False,
                    default=str
                ))

    except WebSocketDisconnect:
        manager.disconnect(websocket)
    except Exception as e:
        logger.error(f"WebSocket ошибка: {e}")
        manager.disconnect(websocket)


# =====================================================================
#  ДЕМО-ДАННЫЕ (для тестирования)
# =====================================================================

@app.post("/api/demo/populate")
async def populate_demo_data():
    """Заполняет систему демо-данными для тестирования."""
    scientists_data = [
        {"name": "Ханако", "avatar": "⚡", "x": 100, "y": 100, "status": "working", "task": "Контроль гравитации"},
        {"name": "Фуюки", "avatar": "🔌", "x": 200, "y": 100, "status": "working", "task": "Электросети"},
        {"name": "Люси", "avatar": "🚀", "x": 300, "y": 100, "status": "thinking", "task": "Проектирование двигателей"},
        {"name": "Футаба", "avatar": "🎮", "x": 400, "y": 100, "status": "working", "task": "Управление системой"},
        {"name": "Шиори", "avatar": "🛡️", "x": 100, "y": 200, "status": "idle", "task": "Защита системы"},
        {"name": "Нобука", "avatar": "🔧", "x": 200, "y": 200, "status": "working", "task": "Оптимизация кода"},
        {"name": "Аква", "avatar": "🔢", "x": 300, "y": 200, "status": "working", "task": "Математические расчеты"},
        {"name": "Latislane", "avatar": "🎨", "x": 400, "y": 200, "status": "working", "task": "Проектирование тел"},
        {"name": "Селеста", "avatar": "💫", "x": 100, "y": 300, "status": "thinking", "task": "Анализ эмоций"},
        {"name": "Наото", "avatar": "📚", "x": 200, "y": 300, "status": "working", "task": "Анализ литературы"},
        {"name": "Юи", "avatar": "🧠", "x": 300, "y": 300, "status": "working", "task": "Управление сознанием"},
        {"name": "Айико", "avatar": "🌸", "x": 400, "y": 300, "status": "idle", "task": "Генерация контента"},
    ]

    for sci in scientists_data:
        state = ScientistState(
            name=sci["name"],
            avatar=sci["avatar"],
            status=sci["status"],
            current_task=sci["task"],
            personality={
                "empathy": 0.5,
                "cynicism": 0.3,
                "logic": 0.7,
                "creativity": 0.6,
            },
            x=sci["x"],
            y=sci["y"],
            last_activity=datetime.now().isoformat(),
        )
        system.update_scientist(sci["name"], state)

    # Добавляем демо-события
    system.add_event("Наото", "task_update", "📚 Наото: Нашла новую книгу для анализа")
    system.add_event("Нобука", "task_update", "🔧 Нобука: Оптимизировала модуль обработки данных")
    system.add_event("Шиори", "security_check", "🛡️ Шиори: Система защищена")

    await manager.broadcast({
        "type": "system_update",
        "data": system.get_status(),
    })

    return {"status": "ok", "scientists": len(scientists_data)}


# =====================================================================
#  ЗАПУСК
# =====================================================================

if __name__ == "__main__":
    import uvicorn

    logger.info("🚀 Запуск Wuglarst Server...")
    logger.info("📡 API: http://localhost:8001")
    logger.info("🌐 WebSocket: ws://localhost:8001/ws")

    uvicorn.run(
        "server:app",
        host="0.0.0.0",
        port=8001,
        reload=True,
    )
