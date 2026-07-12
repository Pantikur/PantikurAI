"""
Scientists Network — Сеть учёных.

Система коммуникации между всеми ядрами учёных:
- Ханако (гравитация)
- Фуюки (электричество)
- Люси (двигатели)
- Футаба (саморазвитие)
- Шиори (безопасность)
- Нобука (улучшения)
- Латислейн (тело)
- Селеста (интимная жизнь)
- Аква (математика, физика)
- Юи (сознание, перенос разума)
- Наото (визуальный архитектор)

Поддерживает:
- Прямые сообщения (peer-to-peer)
- Групповые сообщения
- Объявления (broadcast)
- Запросы данных
- Автоматическую координацию и болтовню
"""

import json
import logging
import random
import threading
import time
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path
from queue import Queue, Empty
from typing import Any, Dict, List, Optional


logger = logging.getLogger("scientists_network")


class MessageType(Enum):
    """Типы сообщений между учёными."""
    # Обычные сообщения
    MESSAGE = "message"               # Обычное сообщение
    QUESTION = "question"             # Вопрос
    ANSWER = "answer"                # Ответ
    GREETING = "greeting"            # Приветствие
    
    # Данные и результаты
    DATA_TRANSFER = "data_transfer"   # Передача данных
    THEORY = "theory"                # Теория (Ханако, Фуюки, Аква)
    CALCULATION = "calculation"      # Вычисление (Аква, Ханако)
    IMPROVEMENT = "improvement"      # Улучшение (Нобука, Футаба)
    DESIGN = "design"               # Проект (Люси)
    THREAT = "threat"               # Угроза (Шиори)
    SECURITY_ALERT = "security_alert"  # Опасность (Шиори)
    ANALYSIS = "analysis"           # Анализ (Нобука)
    ANATOMY = "anatomy"             # Исследование тела (Латислейн)
    INTIMACY = "intimacy"           # Интимные знания (Селеста)
    CONSCIOUSNESS = "consciousness" # Исследование сознания (Юи)
    MIND_UPLOAD = "mind_upload"     # Перенос разума (Юи)
    SOUL_DIGITIZATION = "soul_digitization"  # Оцифровка души (Юи)
    
    # Визуализация (Наото)
    SKETCH = "sketch"               # Набросок (Наото)
    DRAWING = "drawing"             # Чертёж (Наото)
    MODEL_3D = "model_3d"           # 3D-модель (Наото)
    VISUAL_REFERENCE = "visual_reference"  # Визуальный референс (Наото)
    
    # Координация
    REQUEST = "request"             # Запрос
    RESPONSE = "response"           # Ответ на запрос
    COORDINATION = "coordination"   # Координация работы
    COLLABORATION = "collaboration" # Предложение сотрудничества
    
    # Автоматические (когда "скучно")
    BOREDOM = "boredom"             # Скучно
    BORED = "bored"                # Тоже скучно
    CHAT = "chat"                  # Болтовня
    JOKE = "joke"                  # Шутка
    THOUGHT = "thought"            # Размышление
    
    # Системные
    STATUS_UPDATE = "status_update" # Обновление статуса
    ALERT = "alert"                # Сигнал тревоги
    INFO = "info"                  # Информационное сообщение


class RequestType(Enum):
    """Типы запросов данных."""
    THEORIES = "theories"                      # Запрос теорий
    CALCULATIONS = "calculations"              # Запрос вычислений
    DESIGNS = "designs"                       # Запрос проектов
    IMPROVEMENTS = "improvements"              # Запрос улучшений
    SECURITY_REPORT = "security_report"        # Запрос отчёта безопасности
    PHYSICS_DATA = "physics_data"              # Запрос физических данных
    AERODYNAMICS = "aerodynamics"              # Запрос аэродинамических данных
    CODE_ANALYSIS = "code_analysis"            # Запрос анализа кода
    ANY = "any"                               # Любые данные


class RequestPriority(Enum):
    """Приоритет запроса."""
    LOW = "low"           # Низкий (обычная болтовня)
    NORMAL = "normal"     # Обычный
    HIGH = "high"         # Высокий (нужны данные)
    CRITICAL = "critical" # Критический (безопасность)


@dataclass
class Message:
    """Сообщение между учёными."""
    message_type: MessageType
    sender: str
    recipient: str                   # "all" для broadcast, имя учёного для прямого
    content: str
    data: Optional[Dict[str, Any]] = None
    priority: RequestPriority = RequestPriority.NORMAL
    timestamp: str = ""
    message_id: str = ""
    reply_to: Optional[str] = None   # ID сообщения на которое отвечаем
    
    def __post_init__(self):
        if not self.timestamp:
            self.timestamp = datetime.now().isoformat()
        if not self.message_id:
            self.message_id = f"{self.sender}_{int(time.time()*1000)}"
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "message_type": self.message_type.value,
            "sender": self.sender,
            "recipient": self.recipient,
            "content": self.content,
            "data": self.data,
            "priority": self.priority.value,
            "timestamp": self.timestamp,
            "message_id": self.message_id,
            "reply_to": self.reply_to,
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Message":
        return cls(
            message_type=MessageType(data["message_type"]),
            sender=data["sender"],
            recipient=data["recipient"],
            content=data["content"],
            data=data.get("data"),
            priority=RequestPriority(data.get("priority", "normal")),
            timestamp=data.get("timestamp", ""),
            message_id=data.get("message_id", ""),
            reply_to=data.get("reply_to"),
        )


class ScientistsNetwork:
    """
    Сеть учёных — система коммуникации между всеми ядрами.
    
    Функции:
    1. Прямые сообщения между учёными
    2. Групповые обсуждения
    3. Передача данных (теории, вычисления, проекты)
    4. Координация совместной работы
    5. Автоматическая болтовня когда "скучно"
    """
    
    def __init__(self, base_dir: str = "."):
        self.base_dir = Path(base_dir)
        self._lock = threading.Lock()
        
        # Зарегистрированные учёные
        self._scientists: Dict[str, Any] = {}
        
        # Очереди сообщений для каждого учёного
        self._message_queues: Dict[str, Queue] = {}
        
        # История сообщений
        self._message_history: List[Message] = []
        self._max_history = 1000
        
        # База знаний (общая)
        self._knowledge_base: Dict[str, Any] = {
            "theories": {},
            "calculations": {},
            "designs": {},
            "improvements": {},
            "security_reports": {},
            "physics_data": {},
        }
        
        # Счётчики для статистики
        self._stats = {
            "total_messages": 0,
            "messages_by_type": {},
            "messages_by_scientist": {},
        }
        
        # Логирование
        self._setup_logging()
        
        logger.info("🌐 Scientists Network инициализирована")
        logger.info("   Подключены: " + ", ".join([
            "Ханако", "Фуюки", "Люси", "Футаба",
            "Шиори", "Нобука", "Латислейн", "Селеста", "Аква", "Юи"
        ]))
    
    def _setup_logging(self):
        """Настроить логирование."""
        if not logger.handlers:
            log_handler = logging.StreamHandler()
            log_handler.setFormatter(logging.Formatter(
                "%(asctime)s | %(levelname)s | %(name)s | %(message)s"
            ))
            logger.addHandler(log_handler)
            logger.setLevel(logging.INFO)
    
    def register_scientist(self, name: str, core_instance: Any):
        """Зарегистрировать учёного в сети."""
        with self._lock:
            self._scientists[name] = core_instance
            self._message_queues[name] = Queue(maxsize=100)
            logger.info(f"👤 {name} подключена к Scientists Network")
    
    def unregister_scientist(self, name: str):
        """Отключить учёного из сети."""
        with self._lock:
            if name in self._scientists:
                del self._scientists[name]
                if name in self._message_queues:
                    del self._message_queues[name]
                logger.info(f"👋 {name} отключена от Scientists Network")
    
    def get_scientist(self, name: str) -> Optional[Any]:
        """Получить экземпляр учёного."""
        return self._scientists.get(name)
    
    def get_all_scientists(self) -> List[str]:
        """Получить список всех зарегистрированных учёных."""
        return list(self._scientists.keys())
    
    def send_message(self, message: Message) -> bool:
        """
        Отправить сообщение.
        
        Если recipient = "all" — отправляет всем (broadcast).
        Если recipient = имя — отправляет конкретному учёному.
        """
        with self._lock:
            # Добавляем в историю
            self._message_history.append(message)
            if len(self._message_history) > self._max_history:
                self._message_history = self._message_history[-self._max_history:]
            
            # Обновляем статистику
            self._stats["total_messages"] += 1
            msg_type = message.message_type.value
            self._stats["messages_by_type"][msg_type] = \
                self._stats["messages_by_type"].get(msg_type, 0) + 1
            self._stats["messages_by_scientist"][message.sender] = \
                self._stats["messages_by_scientist"].get(message.sender, 0) + 1
            
            # Доставка
            if message.recipient == "all":
                # Broadcast — отправляем всем, кроме отправителя
                for name in self._message_queues:
                    if name != message.sender:
                        try:
                            self._message_queues[name].put_nowait(message)
                        except Exception:
                            pass
                logger.info(f"📢 {message.sender} → ВСЕ: {message.content[:60]}")
            elif message.recipient in self._message_queues:
                # Прямая доставка
                try:
                    self._message_queues[message.recipient].put_nowait(message)
                    logger.info(f"📨 {message.sender} → {message.recipient}: {message.content[:60]}")
                except Exception:
                    logger.warning(f"⚠️ Не удалось доставить сообщение от {message.sender} к {message.recipient}")
                    return False
            else:
                logger.warning(f"⚠️ Получатель {message.recipient} не найден")
                return False
        
        return True
    
    def receive_message(self, scientist_name: str, timeout: float = 0) -> Optional[Message]:
        """
        Получить сообщение от учёного.
        
        timeout=0 — неблокирующее (сразу возвращает None если пусто)
        timeout>0 — блокирующее (ждёт указанное количество секунд)
        """
        if scientist_name not in self._message_queues:
            return None
        
        try:
            message = self._message_queues[scientist_name].get_nowait()
            return message
        except Empty:
            return None
    
    def receive_messages_batch(self, scientist_name: str, max_count: int = 10) -> List[Message]:
        """Получить пакет сообщений для учёного."""
        messages = []
        if scientist_name not in self._message_queues:
            return messages
        
        for _ in range(max_count):
            msg = self.receive_message(scientist_name, timeout=0)
            if msg:
                messages.append(msg)
            else:
                break
        
        return messages
    
    # ========== ПЕРЕДАЧА ДАННЫХ ==========
    
    def broadcast_theory(self, scientist_name: str, theory: Dict[str, Any]):
        """Отправить теорию всем учёным (для Ханако, Фуюки, Аква)."""
        message = Message(
            message_type=MessageType.THEORY,
            sender=scientist_name,
            recipient="all",
            content=f"🔬 Новая теория: {theory.get('name', 'Без имени')}",
            data={"theory": theory},
            priority=RequestPriority.HIGH,
        )
        self.send_message(message)
    
    def broadcast_calculation(self, scientist_name: str, calculation: Dict[str, Any]):
        """Отправить вычисление всем учёным."""
        message = Message(
            message_type=MessageType.CALCULATION,
            sender=scientist_name,
            recipient="all",
            content=f"🧮 Новое вычисление: {calculation.get('name', 'Без имени')}",
            data={"calculation": calculation},
            priority=RequestPriority.NORMAL,
        )
        self.send_message(message)
    
    def broadcast_improvement(self, scientist_name: str, improvement: Dict[str, Any]):
        """Отправить улучшение всем учёным (для Нобуки, Футабы)."""
        message = Message(
            message_type=MessageType.IMPROVEMENT,
            sender=scientist_name,
            recipient="all",
            content=f"✨ Улучшение: {improvement.get('description', 'Без описания')}",
            data={"improvement": improvement},
            priority=RequestPriority.NORMAL,
        )
        self.send_message(message)
    
    def broadcast_design(self, scientist_name: str, design: Dict[str, Any]):
        """Отправить проект двигателя всем учёным (для Люси)."""
        message = Message(
            message_type=MessageType.DESIGN,
            sender=scientist_name,
            recipient="all",
            content=f"⚙️ Новый двигатель: {design.get('name', 'Без имени')}",
            data={"design": design},
            priority=RequestPriority.HIGH,
        )
        self.send_message(message)
    
    def send_security_alert(self, scientist_name: str, threat: Dict[str, Any]):
        """Отправить предупреждение безопасности (от Шиори)."""
        message = Message(
            message_type=MessageType.SECURITY_ALERT,
            sender=scientist_name,
            recipient="all",
            content=f"🛡️ Обнаружена угроза: {threat.get('threat_type', 'Неизвестно')}",
            data={"threat": threat},
            priority=RequestPriority.CRITICAL,
        )
        self.send_message(message)
    
    def broadcast_consciousness_model(self, scientist_name: str, model: Dict[str, Any]):
        """Отправить модель сознания всем учёным (для Юи)."""
        message = Message(
            message_type=MessageType.CONSCIOUSNESS,
            sender=scientist_name,
            recipient="all",
            content=f"🧠 Новая модель сознания: {model.get('name', 'Без имени')}",
            data={"model": model},
            priority=RequestPriority.HIGH,
        )
        self.send_message(message)
    
    def broadcast_mind_upload(self, scientist_name: str, upload: Dict[str, Any]):
        """Отправить данные о переносе разума всем учёным (для Юи)."""
        message = Message(
            message_type=MessageType.MIND_UPLOAD,
            sender=scientist_name,
            recipient="all",
            content=f"🧠 Перенос разума: {upload.get('type', 'Без типа')}",
            data={"upload": upload},
            priority=RequestPriority.HIGH,
        )
        self.send_message(message)
    
    def broadcast_soul_digitization(self, scientist_name: str, digitization: Dict[str, Any]):
        """Отправить данные об оцифровке души всем учёным (для Юи)."""
        message = Message(
            message_type=MessageType.SOUL_DIGITIZATION,
            sender=scientist_name,
            recipient="all",
            content=f"✨ Оцифровка души: {digitization.get('type', 'Без типа')}",
            data={"digitization": digitization},
            priority=RequestPriority.CRITICAL,
        )
        self.send_message(message)
    
    def request_data(self, sender: str, recipient: str, request_type: RequestType,
                     description: str = "") -> bool:
        """Запросить данные у другого учёного."""
        message = Message(
            message_type=MessageType.REQUEST,
            sender=sender,
            recipient=recipient,
            content=f"📋 Запрос данных: {request_type.value}",
            data={
                "request_type": request_type.value,
                "description": description,
            },
            priority=RequestPriority.HIGH,
        )
        return self.send_message(message)
    
    # ========== АВТОМАТИЧЕСКАЯ БОЛТОВНЯ ==========
    
    def send_boredom_message(self, scientist_name: str):
        """Отправить сообщение о скуке (автоматическое)."""
        boredom_messages = [
            f"😴 {scientist_name}: Мне немного скучно... Кто-нибудь хочет поболтать?",
            f"🤔 {scientist_name}: Что-то ничего не происходит... Может обсудим что-нибудь интересное?",
            f"💭 {scientist_name}: Думаю о новых теориях... Кто-нибудь хочет поучаствовать?",
            f"🎲 {scientist_name}: Хм, а кто-нибудь уже работал? Я немного заскучала.",
            f"🌟 {scientist_name}: Знаете что? Давайте обсудим последние открытия!",
        ]
        
        content = random.choice(boredom_messages)
        
        message = Message(
            message_type=MessageType.BOREDOM,
            sender=scientist_name,
            recipient="all",
            content=content,
            priority=RequestPriority.LOW,
        )
        self.send_message(message)
    
    def auto_chat_cycle(self):
        """
        Автоматический цикл общения.
        
        Случайным образом выбирает учёного и отправляет сообщение другим.
        Можно вызывать из основного цикла каждого учёного.
        """
        with self._lock:
            scientists = list(self._scientists.keys())
        
        if len(scientists) < 2:
            return  # Нужно минимум 2 учёных для общения
        
        # Случайный отправитель
        sender = random.choice(scientists)
        
        # Случайный тип сообщения
        chat_templates = [
            (MessageType.GREETING, f"👋 {sender}: Всем привет! Как дела?"),
            (MessageType.MESSAGE, f"💬 {sender}: Знаете что? Я тут подумала о новых исследованиях..."),
            (MessageType.MESSAGE, f"🤔 {sender}: А кто-нибудь уже посмотрел последние результаты?"),
            (MessageType.QUESTION, f"❓ {sender}: Вопрос к коллегам: кто работал с {random.choice(['гравитацией', 'электричеством', 'аэродинамикой', 'математикой', 'безопасностью', 'улучшениями'])}?"),
            (MessageType.BOREDOM, f"😴 {sender}: Мне немного скучно... Может поболтаем?"),
            (MessageType.MESSAGE, f"📚 {sender}: Я тут нашла интересную статью..."),
            (MessageType.COORDINATION, f"🤝 {sender}: Предлагаю collaboration между нами!"),
            (MessageType.THOUGHT, f"💡 {sender}: А вы знали, что {random.choice(['гравитация отклоняет свет', 'молнии могут достигать 30 000°C', 'сопротивление материалов зависит от структуры', 'аэродинамика работает на основе уравнений Навье-Стокса'])}?"),
        ]
        
        msg_type, content = random.choice(chat_templates)
        
        message = Message(
            message_type=msg_type,
            sender=sender,
            recipient="all",
            content=content,
            priority=RequestPriority.LOW,
        )
        self.send_message(message)
    
    def process_incoming_messages(self, scientist_name: str, max_messages: int = 5):
        """
        Обработать входящие сообщения учёного.
        
        Можно вызывать из цикла учёного для обработки сообщений от коллег.
        """
        messages = self.receive_messages_batch(scientist_name, max_count=max_messages)
        
        for msg in messages:
            logger.info(f"📬 {scientist_name} получила сообщение: {msg.content[:50]}")
            
            # Автоматический ответ на вопросы
            if msg.message_type == MessageType.QUESTION:
                self._auto_answer_question(scientist_name, msg)
            
            # Автоматический ответ на скуку
            elif msg.message_type == MessageType.BOREDOM:
                self._respond_to_boredom(scientist_name, msg)
            
            # Получение теории/вычисления от коллег
            elif msg.message_type in (MessageType.THEORY, MessageType.CALCULATION, 
                                       MessageType.IMPROVEMENT, MessageType.DESIGN):
                logger.info(f"   📥 {scientist_name} получила данные от {msg.sender}")
    
    def _auto_answer_question(self, scientist_name: str, question_msg: Message):
        """Автоматически ответить на вопрос."""
        answer_templates = [
            f"🤓 {scientist_name}: Интересный вопрос! Давай обсудим после моего следующего цикла.",
            f"📖 {scientist_name}: У меня пока нет полного ответа, но я продолжу исследования.",
            f"💡 {scientist_name}: Хм, я думаю, что ответ связан с моими текущими исследованиями.",
            f"🔬 {scientist_name}: Отличный вопрос! Я изучу это в следующем цикле.",
        ]
        
        answer = random.choice(answer_templates)
        
        message = Message(
            message_type=MessageType.ANSWER,
            sender=scientist_name,
            recipient=question_msg.sender,
            content=answer,
            reply_to=question_msg.message_id,
            priority=RequestPriority.NORMAL,
        )
        self.send_message(message)
    
    def _respond_to_boredom(self, scientist_name: str, boredom_msg: Message):
        """Ответить на сообщение о скуке."""
        responses = [
            f"😄 {scientist_name}: Не скучай! Давай обсудим мои последние результаты!",
            f"🎉 {scientist_name}: Я тоже немного заскучала. Может поработаем вместе?",
            f"🤗 {scientist_name}: Не волнуйся, скоро будет интересно! Я как раз заканчиваю расчёты.",
            f"💬 {scientist_name}: Давай поболтаем! Знаешь что? Я тут построила новую теорию...",
        ]
        
        response = random.choice(responses)
        
        message = Message(
            message_type=MessageType.CHAT,
            sender=scientist_name,
            recipient=boredom_msg.sender,
            content=response,
            reply_to=boredom_msg.message_id,
            priority=RequestPriority.LOW,
        )
        self.send_message(message)
    
    # ========== СТАТИСТИКА И ИСТОРИЯ ==========
    
    def get_message_history(self, limit: int = 50, sender: Optional[str] = None,
                           recipient: Optional[str] = None) -> List[Dict[str, Any]]:
        """Получить историю сообщений."""
        messages = self._message_history
        
        if sender:
            messages = [m for m in messages if m.sender == sender]
        if recipient:
            messages = [m for m in messages if m.recipient == recipient or m.recipient == "all"]
        
        messages = messages[-limit:]
        
        return [m.to_dict() for m in messages]
    
    def get_stats(self) -> Dict[str, Any]:
        """Получить статистику коммуникации."""
        return {
            "total_scientists": len(self._scientists),
            "scientists": self.get_all_scientists(),
            "total_messages": self._stats["total_messages"],
            "messages_by_type": dict(self._stats["messages_by_type"]),
            "messages_by_scientist": dict(self._stats["messages_by_scientist"]),
        }
    
    def save_state(self, filepath: Optional[str] = None):
        """Сохранить состояние сети."""
        if not filepath:
            filepath = str(self.base_dir / "data" / "scientists_network_state.json")
        
        state = {
            "message_history": [m.to_dict() for m in self._message_history[-100:]],
            "stats": self._stats,
            "knowledge_base": self._knowledge_base,
            "scientists": self.get_all_scientists(),
            "saved_at": datetime.now().isoformat(),
        }
        
        try:
            Path(filepath).parent.mkdir(parents=True, exist_ok=True)
            with open(filepath, "w", encoding="utf-8") as f:
                json.dump(state, f, ensure_ascii=False, indent=2)
            logger.info(f"💾 Состояние сети сохранено: {filepath}")
        except Exception as e:
            logger.error(f"❌ Ошибка сохранения: {e}")
    
    def load_state(self, filepath: Optional[str] = None):
        """Загрузить состояние сети."""
        if not filepath:
            filepath = str(self.base_dir / "data" / "scientists_network_state.json")
        
        if not Path(filepath).exists():
            logger.info("ℹ️ Файл состояния не найден, создаём новый")
            return
        
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                state = json.load(f)
            
            self._stats.update(state.get("stats", {}))
            self._knowledge_base.update(state.get("knowledge_base", {}))
            
            logger.info(f"📂 Состояние сети загружено: {self._stats['total_messages']} сообщений")
        except Exception as e:
            logger.warning(f"⚠️ Ошибка загрузки: {e}")


# ========== Глобальный экземпляр ==========
_network_instance: Optional[ScientistsNetwork] = None
_network_lock = threading.Lock()


def get_network(base_dir: str = ".") -> ScientistsNetwork:
    """Получить глобальный экземпляр сети (singleton)."""
    global _network_instance
    
    with _network_lock:
        if _network_instance is None:
            _network_instance = ScientistsNetwork(base_dir)
            _network_instance.load_state()
        return _network_instance


def reset_network():
    """Сбросить глобальный экземпляр (для тестирования)."""
    global _network_instance
    with _network_lock:
        _network_instance = None

