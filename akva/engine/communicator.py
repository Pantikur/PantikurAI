"""
Система общения Аква с другими модулями.
"""

from __future__ import annotations
import json
import logging
import random
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

from .models import Message, MessageType


class AkvaCommunicator:
    """Общение Аква с другими модулями-«девочками»."""

    TOPIC_MAP = {
        "hanako": ["гравитация", "общая теория относительности", "космология", "чёрные дыры", "волны"],
        "fuyuki": ["электричество", "магнетизм", "электродинамика", "электромагнитные волны", "плазма"],
        "lucy": ["двигатели", "реактивная тяга", "аэродинамика крыла", "турбины", "сверхзвук"],
        "futaba": ["теория игр", "оптимизация", "управление системами", "марковские процессы"],
        "shiori": ["верификация расчётов", "безопасность моделей", "численная стабильность"],
        "nobuka": ["код научных расчётов", "оптимизация алгоритмов", "качество кода"],
        "latislane": ["аэродинамические формы", "проектирование крыла", "оптимизация формы"],
        "celest": ["термодинамика", "энергетика", "энтропия", "тепловые машины"],
        "yu": ["нейросети", "машинное обучение", "сознание", "искусственный интеллект"],
        "naoto": ["визуализация данных", "чертежи", "графики", "3D моделирование"],
    }

    GREETINGS = [
        "Привет! 📐 Как дела? Я тут считала формулы...",
        "Хей! Аква на связи. Готово делиться знаниями! 😊",
        "Приветствую! Только что закончила расчёты. Есть что обсудить!",
        "Здравствуй! Я Аква — математика и физика! 🧮",
    ]

    def __init__(self, config: Any):
        self.config = config
        self.logger = logging.getLogger("AkvaCommunicator")
        self.communication_dir = config.communication_dir
        self.communication_dir.mkdir(parents=True, exist_ok=True)
        self.sent_messages: List[Dict[str, Any]] = []

    def send_message(self, sender: str, recipient: str, content: str,
                     msg_type: str = "knowledge_share",
                     priority: str = "normal",
                     attachments: Optional[Dict] = None) -> Message:
        """Отправить сообщение."""
        msg = Message(
            sender=sender,
            recipient=recipient,
            content=content,
            message_type=msg_type,
            priority=priority,
            attachments=attachments or {},
        )

        # Сохранить в историю
        history_file = self.communication_dir / f"akva_{recipient}.jsonl"
        with open(history_file, "a", encoding="utf-8") as f:
            f.write(json.dumps(msg.to_dict(), ensure_ascii=False) + "\n")

        self.sent_messages.append(msg.to_dict())
        self.logger.info(f"💬 Аква → {recipient}: [{msg_type}] {content[:80]}...")
        return msg

    def send_to_all(self, content: str, msg_type: str = "report",
                    priority: str = "normal") -> List[Message]:
        """Отправить сообщение всем модулям."""
        messages = []
        for girl in self.config.other_girls:
            msg = self.send_message("akva", girl, content, msg_type, priority)
            messages.append(msg)
        return messages

    def generate_greeting(self, recipient: str) -> str:
        """Сгенерировать приветствие."""
        greeting = random.choice(self.GREETINGS)
        return f"{greeting} ({recipient})"

    def generate_knowledge_share(self, area: str, topic: str) -> str:
        """Сгенерировать обмен знаниями."""
        templates = {
            "mathematics": [
                f"Я изучила {topic}! Это невероятно красивая тема. 📐",
                f"Только что разобралась с {topic}. Формулы просто восхитительные!",
                f"Новые открытия в {topic}: хочу поделиться!",
            ],
            "physics": [
                f"Изучила {topic} — физика прекрасна! ⚛️",
                f"Только что провела расчёты по {topic}. Результаты впечатляют!",
                f"Обнаружила интересные связи в {topic}!",
            ],
            "aerodynamics": [
                f"Аэродинамика {topic} — моя страсть! ✈️",
                f"Рассчитала параметры обтекания для {topic}. Данные отправляю!",
                f"Новые данные по {topic}: число Рейнольдса и подъёмная сила!",
            ],
            "strength_of_materials": [
                f"Изучила прочность материалов для {topic}. 🏗️",
                f"Рассчитала напряжения в конструкции: {topic}. Результаты в отчёте!",
                f"Интересные данные по усталости материалов: {topic}!",
            ],
        }

        templates_list = templates.get(area, templates["mathematics"])
        return random.choice(templates_list)

    def generate_question(self, recipient: str, area: str) -> str:
        """Сгенерировать вопрос другому модулю."""
        topics = self.TOPIC_MAP.get(recipient, [])
        if not topics:
            return "Привет! Чем занимаешься?"

        topic = random.choice(topics)
        questions = {
            "hanako": [
                f"Ханако, какие у тебя данные по гравитации? Мне для расчётов нужно!",
                f"Ханако, объясни пожалуйста связь между ОТО и кривизной пространства?",
            ],
            "lucy": [
                f"Люси, какие данные по тяге двигателя у тебя есть?",
                f"Люси, как ты считаешь, какое оптимальное соотношение тяги к массе?",
            ],
            "fuyuki": [
                f"Фуюки, какие у тебя данные по электромагнетизму?",
                f"Фуюки, как электромагнитное поле влияет на плазму?",
            ],
            "celest": [
                f"Селеста, какие у тебя данные по термодинамике?",
                f"Селеста, как рассчитать КПД тепловой машины?",
            ],
            "yu": [
                f"Юи, можешь помочь с нейросетью для предсказания формул?",
                f"Юи, как ML может помочь в научных вычислениях?",
            ],
        }

        return random.choice(questions.get(recipient, [f"Юи, расскажи о {topic}!"]))

    def get_recent_communication(self, recipient: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Получить недавнюю переписку с модулем."""
        history_file = self.communication_dir / f"akva_{recipient}.jsonl"
        if not history_file.exists():
            return []

        messages = []
        with open(history_file, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line:
                    messages.append(json.loads(line))

        return messages[-limit:]

    def analyze_communication_patterns(self) -> Dict[str, Any]:
        """Анализ паттернов общения."""
        communication_counts: Dict[str, int] = {}

        for msg in self.sent_messages:
            recipient = msg.get("recipient", "")
            communication_counts[recipient] = communication_counts.get(recipient, 0) + 1

        total = len(self.sent_messages)
        most_frequent = max(communication_counts.items(), key=lambda x: x[1])[0] if communication_counts else "none"

        return {
            "total_messages": total,
            "communication_counts": communication_counts,
            "most_frequent_contact": most_frequent,
            "unique_contacts": len(communication_counts),
        }
