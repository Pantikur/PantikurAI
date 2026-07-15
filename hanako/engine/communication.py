"""
Система общения Ханако с 11 девочками-учёными.
"""

from __future__ import annotations

import json
import uuid
import logging
from datetime import datetime
from pathlib import Path
from typing import Optional

from hanako.engine.config import HanakoConfig
from hanako.engine.models import ScientistMessage, CommunicationType


class CommunicationSystem:
    """
    Система общения между девочками-учёными.
    
    Функции:
    - Отправка и получение сообщений
    - Фильтрация по типу и приоритету
    - Интеграция с сетью девочек
    - Управление входящим/исходящим почтовым ящиком
    """

    def __init__(self, config: HanakoConfig):
        self.config = config
        self.logger = logging.getLogger("CommunicationSystem")
        self.messages_path = config.state_dir / "messages.json"
        self._messages: list[ScientistMessage] = self._load_messages()

    def send_message(self, message: ScientistMessage):
        """Отправить сообщение."""
        self._messages.append(message)

        # Если отправляем всем — добавляем в inbox каждой
        if message.recipient == "all":
            for scientist in self.config.all_scientists:
                if scientist != message.sender:
                    inbox_msg = ScientistMessage(
                        sender=message.sender,
                        recipient=scientist,
                        content=message.content,
                        message_type=message.message_type,
                        priority=message.priority,
                        metadata=message.metadata,
                    )
                    inbox_msg.message_id = f"{scientist}_inbox_{uuid.uuid4().hex[:8]}"
                    self._messages.append(inbox_msg)
        else:
            message.message_id = f"{message.sender}_{uuid.uuid4().hex[:8]}"

        # Ограничиваем размер
        if len(self._messages) > self.config.max_messages_inbox * 2:
            self._messages = self._messages[-self.config.max_messages_inbox:]

        self._save_messages()

    def check_inbox(self, scientist: str) -> list[ScientistMessage]:
        """Проверить входящие сообщения."""
        inbox = [
            msg for msg in self._messages
            if msg.recipient == scientist and not msg.read
        ]
        # Помечаем как прочитанные
        for msg in inbox:
            msg.read = True
        self._save_messages()
        return inbox

    def get_outbox(self, scientist: str) -> list[ScientistMessage]:
        """Получить исходящие сообщения."""
        return [
            msg for msg in self._messages
            if msg.sender == scientist
        ]

    def get_messages_by_type(self, scientist: str, msg_type: CommunicationType) -> list[ScientistMessage]:
        """Получить сообщения определённого типа."""
        return [
            msg for msg in self._messages
            if msg.sender == scientist and msg.message_type == msg_type
        ]

    def get_messages_by_sender(self, sender: str) -> list[ScientistMessage]:
        """Получить сообщения от конкретного отправителя."""
        return [
            msg for msg in self._messages
            if msg.sender == sender
        ]

    def get_recent_messages(self, limit: int = 20) -> list[ScientistMessage]:
        """Получить последние сообщения."""
        sorted_msgs = sorted(self._messages, key=lambda m: m.timestamp, reverse=True)
        return sorted_msgs[:limit]

    def get_communication_stats(self) -> dict:
        """Статистика общения."""
        stats = {
            "total_messages": len(self._messages),
            "by_type": {},
            "by_sender": {},
            "by_recipient": {},
        }

        for msg in self._messages:
            # По типу
            t = msg.message_type.value
            stats["by_type"][t] = stats["by_type"].get(t, 0) + 1

            # По отправителю
            stats["by_sender"][msg.sender] = stats["by_sender"].get(msg.sender, 0) + 1

            # По получателю
            stats["by_recipient"][msg.recipient] = stats["by_recipient"].get(msg.recipient, 0) + 1

        return stats

    def load_messages(self) -> list[ScientistMessage]:
        """Публичная загрузка сообщений."""
        return self._load_messages()

    def save_messages(self, messages: list[ScientistMessage] | None = None):
        """Публичное сохранение сообщений."""
        if messages is not None:
            self._messages = messages
        self._save_messages()

    def _load_messages(self) -> list[ScientistMessage]:
        """Загрузка сообщений."""
        if not self.messages_path.exists():
            return []
        try:
            with open(self.messages_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                messages = []
                for d in data:
                    messages.append(ScientistMessage(
                        sender=d["sender"],
                        recipient=d["recipient"],
                        content=d["content"],
                        message_type=CommunicationType(d["message_type"]),
                        priority=d.get("priority", 5),
                        metadata=d.get("metadata", {}),
                        timestamp=datetime.fromisoformat(d["timestamp"]),
                        message_id=d.get("message_id", ""),
                        read=d.get("read", False),
                    ))
                return messages
        except Exception:
            return []

    def _save_messages(self):
        """Сохранение сообщений."""
        with open(self.messages_path, 'w', encoding='utf-8') as f:
            json.dump([m.to_dict() for m in self._messages[-self.config.max_messages_inbox:]],
                      f, ensure_ascii=False, indent=2)
