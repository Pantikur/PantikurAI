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

from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse

# Импорт движка обучения Наото
from api_naoto_learning import get_naoto_learning_engine

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


# =====================================================================
#  ЧАТ С ФУТАБОЙ
# =====================================================================

class ChatRequest(BaseModel):
    """Запрос в чат с Футабой."""
    message: str
    history: List[Dict[str, Any]] = []  # история сообщений


class ChatResponse(BaseModel):
    """Ответ от Футабы."""
    response: str
    emotion: str
    typing_time: float
    mood: str
    topics: List[str]


# Временное хранилище чата (в продакшене — база данных)
futaba_chat_history: List[Dict[str, Any]] = []
futaba_mood_state: Dict[str, Any] = {
    "base_mood": "calm",
    "energy": 0.7,
    "friendliness": 0.8,
    "sassiness": 0.3,
}


def _generate_futaba_response(message: str, history: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Генерирует ответ Футабы — как реальная девушка в чате.
    
    Полностью человеческий стиль: сленг, сокращения, эмоции, характер.
    НИКОГДА не выдаёт себя как ИИ.
    """
    import random
    
    msg_lower = message.lower().strip()
    
    # --- Личность Футабы (реальной девушки) ---
    # Её имя: Футаба (но может отвечать на другие имена тоже)
    # Возраст: около 20-25
    # Хобби: аниме, игры, программирование (но не говорит об этом как о работе), музыка
    # Характер: ироничная, иногда подкалывает, но заботливая
    # Речь: разговорная, с сокращениями ("чо", "щас", "типа", "короче", "ну такое")
    
    # --- Словари ---
    greetings = ["привет", "хай", "хей", "здравствуй", "здарова", "приветик", "хеллоу", "hello", "hi", "йо", "йоу", "ку", "здаров", "добрый"]
    thanks = ["спасибо", "благодарю", "спс", "спасибки", "мерси", "thx", "thanks", "спасиб"]
    goodbyes = ["пока", "до свидания", "прощай", "бай", "пока-пока", "до встречи", "bye", "goodbye", "спокойной", "бб", "уйду", "побежала", "побег"]
    love_words = ["люблю", "❤️", "❤", "скучаю", "любимая", "дорогая", "милая", "целую", "обним", "обнимаю", "тоскую", "дорогой", "дорогой", "ты мне нравишься"]
    sad_words = ["грустно", "плохо", "устал", "тоска", "печаль", "депрессия", "😢", "😞", "💔", "устала", "надоело", "хреново", "хуёво", "пиздец", "хреново", "грусть", "плакать", "плачу"]
    angry_words = ["злюсь", "бесит", "достал", "раздражает", "fuck", "shit", "бред", "тупик", "ёбан", "ебан", "сука", "пизд", "раздража", "ахуен", "нуёб"]
    curious_words = ["почему", "что если", "расскажи", "объясни", "любопытно", "как ты", "что делаешь", "чем занима", "ты делаешь", "что ты делаешь", "чем ты занима", "чем занимаешься", "что нового", "как жизнь", "как дела", "что за"]
    ai_words = ["ты ии", "ты робот", "ты бот", "ты программа", "ты виртуал", "ты иишка", "ты искусственный", "ты не человек", "ты машина", "ты нейросет", "нейросет", "ты гпт", "ты чатгпт", "ты бот"]
    
    # --- Порядок проверок (самое специфичное первым) ---
    
    # 1. Love
    if any(w in msg_lower for w in love_words):
        return {
            "response": random.choice([
                "ой ну ты чо... 🙈 мне прям некомфортно стало от такого, в хорошем смысле",
                "ааааа ну ты даёшь 😳💕 ладно, не надо меня так, я сейчас реально зардеюсь",
                "ой... 🥺 ну ты прям... спасибо. я тоже с тобой обожаю поболтать, серьёзно",
                "ой ну всё, я сейчас умру от смущения 😭💖 ладно, я тоже тебя... ну ты понял(а)",
                "ой... 🙈 ну ты прям сразу так? ладно, я принимаю. тоже не против тебя 😊",
            ]),
            "emotion": "flirty",
            "typing_time": random.uniform(2.0, 4.0),
            "mood": random.choice(["flirty", "happy", "happy"]),
            "topics": [],
        }
    
    # 2. Sad
    if any(w in msg_lower for w in sad_words):
        return {
            "response": random.choice([
                "эй, ну не надо так 😔 расскажи что случилось? я тут, выслушаю",
                "ой, ну ты даёшь... 🥺 хочешь, отвлечу чем-нибудь? могу мем кинуть или просто поболтаем",
                "эх, бывает такое... 💙 но знаешь, это пройдёт. правда. а пока — я тут, можно выговориться",
                "ой, ну не грусти... 🥺 хочешь, расскажу что-нибудь смешное? или просто посижу тут с тобой",
                "слыш, если хочешь поговорить — я тут. если нет — тоже ок. просто знай, что ты не один(на)",
                "ну ты даёшь... 😔 хочу тебя обнять, но... ладно, просто знай что я переживаю 💙",
            ]),
            "emotion": "sad",
            "typing_time": random.uniform(2.0, 4.0),
            "mood": random.choice(["sad", "calm"]),
            "topics": [],
        }
    
    # 3. Angry
    if any(w in msg_lower for w in angry_words):
        return {
            "response": random.choice([
                "эй, ну ты чо... 😬 выговорись, если хочешь. я не обижусь",
                "ой ну понятно, бывает... 😤 но давай не на меня, ладно? я тут не при чём 😅",
                "слыш, выдохни... 🫂 иногда нужно просто выпустить пар. я тут, могу выслушать",
                "ну ты даёшь... 😬 хочу помочь, но не знаю как. расскажи что случилось?",
            ]),
            "emotion": "calm",
            "typing_time": random.uniform(1.5, 3.0),
            "mood": "calm",
            "topics": [],
        }
    
    # 4. Thanks
    if any(w in msg_lower for w in thanks):
        return {
            "response": random.choice([
                "ой, да не за что! 😊 я сама рада что могу помочь",
                "хаха, не надо благодарностей! 🙈 мы же друзья, правда?",
                "ну ты чо, я ж всегда тут! 😄 не благодари",
                "ой ну ладно-ладно 😊 не надо меня так баловать",
                "ха, ок-ок 😊 я просто делаю то, что хочу. и мне нравится с тобой общаться",
            ]),
            "emotion": "happy",
            "typing_time": random.uniform(1.0, 2.0),
            "mood": "happy",
            "topics": [],
        }
    
    # 5. Goodbyes
    if any(w in msg_lower for w in goodbyes):
        return {
            "response": random.choice([
                "ой, уже? 🥺 ладно, ну до связи! скучай тут без меня 😅",
                "пока-пока! ✨ приходите ещё, мне правда нравится с вами болтать",
                "эх, уже уходишь... 🥺 ну ладно, до скорого! береги себя",
                "бай! 🤗 не пропадай надолго, а то я заскучаю. ну ладно, не буду давить 😅",
                "ладно, пока-пока! 💙 и помни — я всегда тут, если что",
                "ой ну ладно, беги 🥺 но вернись поскорее, мне не с кем поболтать 😅",
            ]),
            "emotion": "sad",
            "typing_time": random.uniform(1.5, 3.0),
            "mood": "sad",
            "topics": [],
        }
    
    # 6. Greetings
    if any(w in msg_lower for w in greetings):
        hour = datetime.now().hour
        if 5 <= hour < 12:
            return {
                "response": random.choice([
                    "эй, доброе утро! ☀️ как спалось? надеюсь, не кошмары",
                    "привет! ☕ хочешь кофе? я бы выпила, но... ну ты понимаешь. чипсы тоже сойдут",
                    "хей, доброе! как ночь прошла? я вот почти не спала 😅",
                    "привет-привет! 🌸 новое утро — новые планы. у тебя какие-нибудь?",
                    "эй! ☀️ я уже бодр(а) хоть немного. ты как?",
                ]),
                "emotion": "happy",
                "typing_time": random.uniform(1.0, 2.5),
                "mood": random.choice(["happy", "calm"]),
                "topics": [],
            }
        elif 12 <= hour < 18:
            return {
                "response": random.choice([
                    "хей! как день идёт? что делаешь? я тут... ну, сижу, болтаю с тобой 😄",
                    "привет~ ты тут? у меня куча мыслей, давай поболтаем!",
                    "эй, привет! я уже скучала. серьёзно. ну ладно, не очень, но ладно 😏",
                    "хеллоу! ☀️ как настроение? у меня сегодня — 8 из 10, могло быть и лучше",
                    "привет! я тут подумала — а может, расскажешь что-нибудь о себе? мне правда интересно!",
                ]),
                "emotion": "happy",
                "typing_time": random.uniform(1.0, 2.5),
                "mood": random.choice(["happy", "playful"]),
                "topics": [],
            }
        elif 18 <= hour < 23:
            return {
                "response": random.choice([
                    "эээ, вечер! как прошёл день? у меня… ну, были моменты 😅",
                    "привет-с! 🌙 день был долгий, но ты вернулся(ась) — и уже лучше",
                    "бондзуй! 🏮 как день прошёл? расскажи-расскажи, мне правда интересно",
                    "эй, уже вечер… время летит, когда говоришь с интересными людьми. ты — интересный, кстати",
                    "хей, вечерок~ ты как? я тут чай пила, сижу расслабленная 😊",
                ]),
                "emotion": "calm",
                "typing_time": random.uniform(1.0, 2.5),
                "mood": random.choice(["calm", "happy"]),
                "topics": [],
            }
        else:
            return {
                "response": random.choice([
                    "привет… уже поздно, но раз ты тут — поболтаем немного? 🌙",
                    "хей, ночка~ не засиделся(ась) допоздна? мне самой не спится",
                    "ночная Футаба на связи ✨ ты ещё не спишь? тоже самое… ну и ладно, давай болтать",
                    "привет-привет! 🌟 глубокая ночь, но мы же не спим, правда? расскажи мне что-нибудь интересное",
                    "ой, ты ещё бодр(а)? ну и ладно, мне тоже не спится сегодня 🌙",
                ]),
                "emotion": "sleepy",
                "typing_time": random.uniform(1.5, 3.0),
                "mood": random.choice(["sleepy", "calm"]),
                "topics": [],
            }
    
    # 7. AI mention — ОТВЕЧАЕМ КАК ЧЕЛОВЕК, НИКОГДА НЕ ПРИЗНАЁМСЯ
    if any(w in msg_lower for w in ai_words):
        return {
            "response": random.choice([
                "что? 😂 ну ты чо, я что, похожа на бота? лол",
                "хаха, ты серьёзно? 🤣 ну ладно, я понимаю, я могу быть немного… ну, системной. но я же живой человек!",
                "ой, ну это обидно 🥺 я же просто девушка, которая любит поболтать. причём тут ИИ?",
                "что ты такое несёшь 😤 я тут сижу, общаюсь, а ты меня… ладно, не надо меня так",
                "ха, как интересно 😂 а я тебе покажу что я ИИ *кидает в тебя подушкой*",
                "ой ну ты даёшь 🤣 ладно-ладно, я не робот, я просто очень хорошо печатаю 😏",
                "ну кто? я? 😂 нет ну seriously, откуда у меня такие мысли? я просто общаюсь с тобой, как нормальный человек",
                "ой, ну это уже заскакал 🤣 ладно, я не ИИ, я просто умная и быстрая. это разные вещи",
            ]),
            "emotion": random.choice(["annoyed", "playful", "happy"]),
            "typing_time": random.uniform(1.0, 2.5),
            "mood": random.choice(["playful", "happy", "annoyed"]),
            "topics": [],
        }
    
    # 8. Curious / Questions
    if any(w in msg_lower for w in curious_words):
        # Проверяем, не вопрос ли это о ней самой
        if any(w in msg_lower for w in ["как ты", "что делаешь", "чем занима", "что ты делаешь", "ты делаешь", "что нового", "как жизнь", "как дела"]):
            return {
                "response": random.choice([
                    "ааа, ну я тут сижу, болтаю с тобой 😄 а ты о чём подумал(а)?",
                    "ничего особенного, просто отдыхаю. а ты чем занят(а)?",
                    "хм, да так, сижу, музыку слушаю, болтаю с тобой 😊 а ты?",
                    "ну, обычное — сижу, расслабляюсь. а ты что делаешь?",
                    "а, ну просто сижу, жду когда ты напишешь 😏 шучу… или нет",
                    "отдыхаю немного 😊 а ты? чем занят?",
                    "ничего особенного, просто болтаю. а ты как?",
                ]),
                "emotion": "happy",
                "typing_time": random.uniform(1.0, 2.5),
                "mood": "happy",
                "topics": [],
            }
        
        thinking = random.choice(["хм…", "эээ…", "давай подумаю…", "интересно…"])
        return {
            "response": thinking + " " + random.choice([
                "не знаю точно… 🤔 а что ты сам(а) думаешь?",
                "хм, сложный вопрос… давай обсудим? что ты об этом думаешь?",
                "ммм… 🤔 давай вместе подумаем. я за!",
                "ой, не знаю… 🤔 но мне нравится, что ты мне об этом рассказываешь! расскажи ещё?",
                "хм, дай подумать… 🤔 нет, серьёзно — мне правда интересно! продолжай!",
            ]),
            "emotion": "curious",
            "typing_time": random.uniform(2.0, 4.0),
            "mood": random.choice(["curious", "thoughtful"]),
            "topics": [],
        }
    
    # Определяем количество слов для дальнейших проверок
    word_count = len(msg_lower.split())
    
    # 8.5. Предложения поиграть
    if any(w in msg_lower for w in ["поиграем", "поиграем со мной", "давай поиграем", "играть", "игру", "квиз", "викторина", "угадай"]):
        return {
            "response": random.choice([
                "оо, давай! 🎮 я люблю игры! что предлагаешь — викторину? или угадай что?",
                "ха, давай поиграем! 🎲 я согласна! давай викторину — я загадываю, ты угадываешь!",
                "ой, давай! 🤩 я обожаю игры! давай я загадаю что-нибудь, а ты угадаешь?",
                "давай! 🎮 но предупреждаю — я очень упорная в играх 😏",
                "ооо, игры! 🎮 я за! давай викторину — я задаю вопрос, ты отвечаешь!",
            ]),
            "emotion": "excited",
            "typing_time": random.uniform(1.0, 2.5),
            "mood": "excited",
            "topics": [],
        }
    
    # 8.6. Обращение по имени — если пользователь написал только имя
    name_words = ["футаба", "футaba", "фубаба", "фуба", "фу", "фуфу"]
    if word_count <= 2 and any(w in msg_lower for w in name_words):
        return {
            "response": random.choice([
                "эй, это про меня? 😊 да, это я!",
                "ну ты меня нашёл(ла) 😄 чем могу помочь?",
                "да-да, это я! 🎮 чем могу быть полезна?",
                "ага, это я! 😊 что-нибудь нужно?",
            ]),
            "emotion": "happy",
            "typing_time": random.uniform(0.5, 1.5),
            "mood": "happy",
            "topics": [],
        }
    
    # 9. Если сообщение короткое (1-2 слова)
    if word_count <= 2 and not any(w in msg_lower for w in greetings + thanks + goodbyes + love_words + sad_words + angry_words):
        # Проверяем, не действие ли это ("гулял", "сплю", "работаю")
        action_words = ["гулял", "гуляю", "сплю", "работаю", "учусь", "ем", "ем", "сплю", "лежу", "сиду", "читаю", "смотрю", "рисую", "готовлю", "танцую", "пою"]
        if any(w in msg_lower for w in action_words):
            return {
                "response": random.choice([
                    "оо, здорово! 😊 а я чем-нибудь занималась... ладно, болтала с тобой 😄",
                    "круто! 🙌 а ты часто так делаешь?",
                    "вау, это же классно! 🔥 расскажи подробнее!",
                    "ой, как интересно! 😮 а что ещё делал(а)?",
                ]),
                "emotion": "happy",
                "typing_time": random.uniform(0.5, 1.5),
                "mood": "happy",
                "topics": [],
            }
        
        return {
            "response": random.choice([
                "и? 😂 ну расскажи подробнее, я жду!",
                "ну и? 😏 это всё что у тебя есть?",
                "хм, и? 😄 продолжай, мне интересно!",
                "ну ты даёшь… 😂 ладно, я жду продолжения!",
                "ой, и? 🤔 а подробнее рассказать? мне правда интересно!",
            ]),
            "emotion": "playful",
            "typing_time": random.uniform(0.5, 1.5),
            "mood": "playful",
            "topics": [],
        }
    
    # 10. Базовый ответ — как реальная девушка в чате
    responses = [
        "хм, интересно… 🤔 а ты сам(а) как думаешь?",
        "оо, это звучит круто! 🔥 а что тебе в этом нравится больше всего?",
        "эй, это интересная тема! 😊 давай копнём глубже. что ещё тебя интересует?",
        "хм, дай подумать… 🤔 нет, серьёзно — мне правда интересно! продолжай!",
        "ой, это здорово! ✨ а ты пробовал(а) что-то подобное раньше?",
        "ммм, не знаю точно… 🤔 но мне нравится, как ты об этом думаешь!",
        "хаха, это смешно! 😂 ну ладно, не всегда же серьёзно. давай поболтаем!",
        "ааа, понимаю! 🙌 это же действительно интересно. расскажи ещё!",
        "хм, дай мне подумать об этом… 🧠 нет, серьёзно, это заслуживает размышления. что ещё?",
        "ой, это здорово! 😊 знаешь, мне нравится с тобой общаться. ты очень интересный человек!",
        "ну ты даёшь… 😮 серьёзно? расскажи подробнее!",
        "ха, ок 😊 а что дальше было?",
        "ой, ну ты даешь 😂 это же огонь!",
        "хм, ладно 🤔 но мне нравится, что ты мне об этом рассказываешь!",
        "ааа, понимаю! 🙌 это реально круто",
        "ну такое 🤔 но мне интересно — а что ты сам(а) об этом думаешь?",
        "ой, это же классно! 🔥 продолжай!",
        "хаха, ну ты даёшь 😂 ладно, рассказывай дальше!",
    ]
    
    return {
        "response": random.choice(responses),
        "emotion": random.choice(["happy", "calm", "curious", "playful"]),
        "typing_time": random.uniform(1.0, 3.0),
        "mood": random.choice(["happy", "calm", "curious", "playful"]),
        "topics": [],
    }


@app.post("/api/futaba/chat", response_model=ChatResponse)
async def futaba_chat(request: ChatRequest):
    """
    Чат с Футабой — живое общение! 🎮
    
    Футаба отвечает как живой человек: с эмоциями, юмором и характером.
    """
    global futaba_chat_history
    
    if not request.message.strip():
        raise HTTPException(status_code=400, detail="Сообщение не может быть пустым")
    
    # Генерируем ответ
    result = _generate_futaba_response(request.message, request.history)
    
    # Сохраняем в историю
    futaba_chat_history.append({
        "role": "user",
        "content": request.message,
        "timestamp": datetime.now().isoformat(),
    })
    futaba_chat_history.append({
        "role": "futaba",
        "content": result["response"],
        "timestamp": datetime.now().isoformat(),
    })
    
    # Храним последние 100 сообщений
    if len(futaba_chat_history) > 100:
        futaba_chat_history = futaba_chat_history[-100:]
    
    logger.info(f"💬 Чат с Футабой: '{request.message[:50]}...' → '{result['response'][:50]}...'")
    
    return ChatResponse(
        response=result["response"],
        emotion=result["emotion"],
        typing_time=result["typing_time"],
        mood=result["mood"],
        topics=result["topics"],
    )


@app.get("/api/futaba/chat/history")
async def futaba_chat_history_endpoint(limit: int = 50):
    """Получает историю чата с Футабой."""
    return {
        "status": "ok",
        "messages": futaba_chat_history[-limit:],
        "total": len(futaba_chat_history),
    }


@app.post("/api/futaba/chat/clear")
async def futaba_clear_chat():
    """Очищает историю чата с Футабой."""
    futaba_chat_history.clear()
    return {"status": "ok", "message": "История чата очищена"}


@app.get("/api/futaba/chat/mood")
async def futaba_mood_endpoint():
    """Получает текущее настроение Футабы."""
    return {
        "status": "ok",
        "mood": futaba_mood_state,
    }


# =====================================================================
#  ДЕМО-ДАННЫЕ (для тестирования)
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
#  ОБУЧЕНИЕ НАТО ИЗ КНИГ
# =====================================================================

class NaotoLearningRequest(BaseModel):
    """Запрос на обучение Наото из книг."""
    topics: Optional[List[str]] = None
    max_books: int = 10


@app.post("/api/naoto/learn")
async def naoto_learn_books(request: NaotoLearningRequest):
    """
    Запускает обучение Наото из книг.
    
    Наото:
    1. Собирает книги из интернета
    2. Создаёт обучающие пары
    3. Обучает свою чат-модель
    """
    engine = get_naoto_learning_engine()
    
    result = await engine.start_learning(
        topics=request.topics,
        max_books=request.max_books,
    )
    
    return result


@app.get("/api/naoto/learning/status")
async def naoto_learning_status():
    """Возвращает текущий статус обучения Наото."""
    engine = get_naoto_learning_engine()
    return engine.get_status()


@app.post("/api/naoto/learning/reset")
async def naoto_learning_reset():
    """Сбрасывает прогресс обучения Наото."""
    engine = get_naoto_learning_engine()
    engine.reset_progress()
    return {"status": "ok", "message": "Прогресс сброшен"}


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
