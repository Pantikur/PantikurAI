#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Memory Manager v2 — Akademia Barston Chat
==========================================

СИСТЕМА ДВУХ УРОВНЕЙ ПАМЯТИ С ОТСЛЕЖИВАНИЕМ ОТНОШЕНИЙ

Как это работает на примере:
  1. Игрок-фамильяр попадает к главной героине (слабой, буллинг)
  2. 20 сообщений в локации А — отношения меняются (героиня начинает доверять)
  3. Смена локации на Б — игрок играет ещё 20 сообщений
  4. В локации Б появляется персонаж из локации А
  5. Нейросеть получает: "Месяц назад в локации А игрок защитил героиню от буллинга, 
     её доверие к игроку выросло с 20 до 65. Персонаж X из локации А помнит, 
     что героиня стала увереннее."

=== СТРУКТУРА ДАННЫХ ===

LOCALE SCENE (локальная сцена) — последние N сообщений текущей сцены
RELATIONSHIPS (отношения) — уровень доверия/враждебности между каждым персонажем
                          — история изменений: кто сделал что и почему
LOCATION SCENES (сцены локаций) — что происходило в каждой локации
                                  — кто где находился, какие события
CHARACTER STATE (состояние персонажей) — текущий статус, позиция, инвентарь
ITEMS (предметы) — инвентарь и мировые предметы
WORLD KNOWLEDGE (знания мира) — что персонажи знают о мире

=== ИСПОЛЬЗОВАНИЕ ===
    python memory_manager_v2.py <команда> [аргументы]
"""

import json
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Any

# === Пути к файлам памяти ===
BASE_DIR = Path(__file__).parent
MEMORY_FILE = BASE_DIR / "world_memory.json"

# === Константы ===
MAX_CHAT_MESSAGES = 20  # максимальное количество сообщений в локальной сцене


# === Вспомогательные функции ===
def load_json(filepath: Path, default: dict[str, Any] | None = None) -> dict[str, Any]:
    """Загрузить JSON файл или вернуть значение по умолчанию."""
    if default is None:
        default = {}
    if filepath.exists():
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                content = f.read().strip()
                if content:
                    return json.loads(content)
        except (json.JSONDecodeError, IOError):
            pass
    return default


def save_json(filepath: Path, data: dict) -> None:
    """Сохранить данные в JSON файл."""
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def get_timestamp() -> str:
    """Получить текущую метку времени в ISO формате."""
    return datetime.now().isoformat()


# ============================================================
# УРОВЕНЬ 1: ЛОКАЛЬНАЯ СЦЕНА (текущий чат)
# ============================================================
class CurrentScene:
    """Текущая сцена чата — последние N сообщений."""

    @staticmethod
    def add_message(role: str, text: str, location: str = None, participants: list = None):
        """Добавить сообщение в текущую сцену."""
        data = load_json(MEMORY_FILE, get_default_memory())
        
        message = {
            "role": role,
            "text": text,
            "timestamp": get_timestamp(),
            "location": location or data.get("current_location", "unknown"),
            "participants": participants or []
        }
        data.setdefault("scene_messages", []).append(message)
        
        # Ограничиваем количество сообщений
        if len(data["scene_messages"]) > MAX_CHAT_MESSAGES:
            data["scene_messages"] = data["scene_messages"][-MAX_CHAT_MESSAGES:]
        
        save_json(MEMORY_FILE, data)
        return message

    @staticmethod
    def get_messages(limit: int = None) -> list:
        """Получить сообщения текущей сцены."""
        data = load_json(MEMORY_FILE, get_default_memory())
        messages = data.get("scene_messages", [])
        if limit:
            messages = messages[-limit:]
        return messages

    @staticmethod
    def get_context_text(max_messages: int = 10) -> str:
        """Получить текстовый контекст из текущей сцены."""
        messages = CurrentScene.get_messages(max_messages)
        if not messages:
            return "Нет сообщений в текущей сцене."
        
        lines = [f"=== ТЕКУЩАЯ СЦЕНА ({len(messages)} сообщений) ==="]
        for msg in messages:
            role = msg["role"].upper()
            text = msg["text"]
            time = msg.get("timestamp", "")
            lines.append(f"[{time}] {role}: {text}")
        lines.append("=== КОНЕЦ СЦЕНЫ ===")
        return "\n".join(lines)

    @staticmethod
    def set_location(location_name: str):
        """Установить текущую локацию."""
        data = load_json(MEMORY_FILE, get_default_memory())
        data["current_location"] = location_name
        
        # Сохраняем предыдущую сцену в историю локаций
        if location_name != data.get("last_location", ""):
            if data.get("scene_messages"):
                data.setdefault("location_scenes", {})
                data["location_scenes"][data.get("last_location", "unknown")] = {
                    "messages": data["scene_messages"],
                    "timestamp_ended": get_timestamp(),
                    "character_states": data.get("character_states", {})
                }
        
        data["last_location"] = location_name
        data["scene_messages"] = []
        
        save_json(MEMORY_FILE, data)
        print(f"[OK] Сцена перемещена: {data.get('last_location', 'unknown')} -> {location_name}")

    @staticmethod
    def get_current_location() -> str:
        """Получить текущую локацию."""
        data = load_json(MEMORY_FILE, get_default_memory())
        return data.get("current_location", "unknown")


# ============================================================
# УРОВЕНЬ 2: ОТНОШЕНИЯ (Relationships)
# ============================================================
class Relationships:
    """
    Отслеживание отношений между персонажами.
    
    Уровень: от -100 (полная ненависть) до +100 (полное доверие/любовь)
    0 — нейтральное отношение
    
    История изменений: каждое событие, изменившее отношение, записывается.
    """

    @staticmethod
    def init_relationship(char1: str, char2: str, initial_level: int = 0):
        """Инициализировать отношения между двумя персонажами."""
        data = load_json(MEMORY_FILE, get_default_memory())
        data.setdefault("relationships", {})
        
        # Создаём уникальный ключ для пары (всегда в алфавитном порядке)
        pair_key = Relationships._pair_key(char1, char2)
        
        if pair_key not in data["relationships"]:
            data["relationships"][pair_key] = {
                "characters": [char1, char2],
                "level": initial_level,        # от -100 до +100
                "label": Relationships._level_label(initial_level),
                "history": [],                  # история изменений
                "first_seen": get_timestamp(),
                "last_interaction": None
            }
        
        save_json(MEMORY_FILE, data)
        rel = data["relationships"][pair_key]
        print(f"[OK] Отношения инициализированы: {char1} <-> {char2} = {rel['level']} ({rel['label']})")

    @staticmethod
    def update_level(char1: str, char2: str, delta: int, reason: str, event_type: str = "interaction"):
        """
        Изменить уровень отношений.
        
        delta: +10 (стал ближе), -15 (стал враждебнее)
        reason: описание почему
        event_type: тип события (protect, betray, help, insult, share, fight, etc.)
        """
        data = load_json(MEMORY_FILE, get_default_memory())
        pair_key = Relationships._pair_key(char1, char2)
        
        if pair_key not in data["relationships"]:
            # Автоматически инициализируем с нейтральным уровнем
            data["relationships"][pair_key] = {
                "characters": [char1, char2],
                "level": 0,
                "label": "нейтральное",
                "history": [],
                "first_seen": get_timestamp(),
                "last_interaction": None
            }
        
        rel = data["relationships"][pair_key]
        old_level = rel["level"]
        new_level = max(-100, min(100, old_level + delta))
        
        # Записываем изменение
        change_record = {
            "timestamp": get_timestamp(),
            "old_level": old_level,
            "delta": delta,
            "new_level": new_level,
            "reason": reason,
            "event_type": event_type
        }
        rel["history"].append(change_record)
        rel["level"] = new_level
        rel["label"] = Relationships._level_label(new_level)
        rel["last_interaction"] = get_timestamp()
        
        save_json(MEMORY_FILE, data)
        
        # Показываем результат
        direction = "вверх" if delta > 0 else "вниз"
        print(f"[OK] Отношения {char1} <-> {char2}: {old_level} -> {new_level} ({rel['label']}) [{direction}] ({reason})")

    @staticmethod
    def get_level(char1: str, char2: str) -> dict:
        """Получить текущий уровень отношений."""
        data = load_json(MEMORY_FILE, get_default_memory())
        pair_key = Relationships._pair_key(char1, char2)
        
        if pair_key not in data.get("relationships", {}):
            return {"found": False}
        
        rel = data["relationships"][pair_key]
        return {
            "found": True,
            "characters": rel["characters"],
            "level": rel["level"],
            "label": rel["label"],
            "history": rel["history"]
        }

    @staticmethod
    def get_context_for_npc(npc_name: str, max_history: int = 5) -> str:
        """
        Получить контекст отношений для NPC.
        
        Используется когда NPC появляется в сцене — нейросеть получает:
        "Игрок и Мира имеют уровень доверия 65 (близкие друзья). 
         Последние изменения: [3 дня назад] Игрок защитил Мира от буллинга (+30),
         [2 дня назад] Мира поделилась заклинанием с Игроком (+10)..."
        """
        data = load_json(MEMORY_FILE, get_default_memory())
        relationships = data.get("relationships", {})
        
        # Находим все отношения, где участвует этот NPC
        relevant = []
        for pair_key, rel in relationships.items():
            if npc_name in rel["characters"]:
                # Исключаем самого NPC
                other = [c for c in rel["characters"] if c != npc_name]
                if other:
                    other_name = other[0]
                    # Берём последние N записей истории
                    recent_history = rel["history"][-max_history:] if max_history else rel["history"]
                    relevant.append({
                        "other": other_name,
                        "level": rel["level"],
                        "label": rel["label"],
                        "recent_history": recent_history
                    })
        
        if not relevant:
            return f"Нет записанных отношений с {npc_name} (отношения инициализируются заново)."
        
        lines = [f"\n=== ОТНОШЕНИЯ С {npc_name.upper()} ==="]
        for r in relevant:
            lines.append(f"\nС {r['other']}: уровень {r['level']} ({r['label']})")
            if r["recent_history"]:
                lines.append(f"  Последние события:")
                for h in r["recent_history"]:
                    delta_str = f"+{h['delta']}" if h['delta'] > 0 else str(h['delta'])
                    lines.append(f"    [{h['event_type']}] {h['reason']} ({delta_str})")
        lines.append("=== КОНЕЦ ОТНОШЕНИЙ ===")
        return "\n".join(lines)

    @staticmethod
    def _pair_key(char1: str, char2: str) -> str:
        """Создать уникальный ключ для пары персонажей."""
        return "||".join(sorted([char1.lower(), char2.lower()]))

    @staticmethod
    def _level_label(level: int) -> str:
        """Получить текстовую метку уровня."""
        if level >= 80: return "лучшие друзья"
        if level >= 60: return "близкие друзья"
        if level >= 40: return "друзья"
        if level >= 20: return "товарищи"
        if level >= 0:  return "нейтральное"
        if level >= -20: return "охладели"
        if level >= -40: return "враждебное"
        if level >= -60: return "с враждой"
        if level >= -80: return "ненависть"
        return "полная вражда"

    @staticmethod
    def list_all(data: dict = None) -> str:
        """Вывести все отношения."""
        if data is None:
            data = load_json(MEMORY_FILE, get_default_memory())
        relationships = data.get("relationships", {})
        
        if not relationships:
            return "Нет записанных отношений."
        
        lines = ["=== ВСЕ ОТНОШЕНИЯ ==="]
        for pair_key, rel in relationships.items():
            chars = " <-> ".join(rel["characters"])
            lines.append(f"  {chars}: {rel['level']} ({rel['label']})")
            if rel["history"]:
                last = rel["history"][-1]
                lines.append(f"    Последнее: [{last['event_type']}] {last['reason']}")
        lines.append("=== КОНЕЦ ===")
        return "\n".join(lines)


# ============================================================
# УРОВЕНЬ 3: ИСТОРИЯ ЛОКАЦИЙ (Location Scenes)
# ============================================================
class LocationHistory:
    """
    История того, что происходило в каждой локации.
    
    При смене локации текущая сцена сохраняется в историю.
    При возвращении или встрече персонажа из другой локации — контекст подтягивается.
    """

    @staticmethod
    def add_location(name: str, description: str, features: list = None):
        """Добавить или обновить локацию."""
        data = load_json(MEMORY_FILE, get_default_memory())
        data.setdefault("locations", {})
        
        timestamp = get_timestamp()
        
        if name not in data["locations"]:
            data["locations"][name] = {
                "description": description,
                "features": features or [],
                "first_seen": timestamp,
                "characters_present": [],
                "events": [],
                "scenes": []  # все сцены, которые были здесь
            }
        
        loc = data["locations"][name]
        if description:
            loc["description"] = description
        if features:
            loc["features"] = features
        loc["last_updated"] = timestamp
        
        save_json(MEMORY_FILE, data)
        print(f"[OK] Локация сохранена: {name}")

    @staticmethod
    def add_location_event(location: str, event_type: str, description: str, 
                           participants: list = None, tags: list = None):
        """Добавить событие в конкретную локацию."""
        data = load_json(MEMORY_FILE, get_default_memory())
        data.setdefault("locations", {})
        
        if location not in data["locations"]:
            data["locations"][location] = {
                "description": f"(локация {location})",
                "features": [],
                "first_seen": get_timestamp(),
                "characters_present": [],
                "events": [],
                "scenes": []
            }
        
        event = {
            "id": len(data["locations"][location].get("events", [])) + 1,
            "type": event_type,
            "description": description,
            "participants": participants or [],
            "tags": tags or [],
            "timestamp": get_timestamp(),
            "location": location
        }
        data["locations"][location]["events"].append(event)
        data["locations"][location]["last_updated"] = get_timestamp()
        
        save_json(MEMORY_FILE, data)
        print(f"[OK] Событие в {location}: [{event_type}] {description[:50]}...")

    @staticmethod
    def get_location_context(location_name: str) -> str:
        """
        Получить полный контекст локации.
        
        Используется когда:
        1. Игрок входит в новую локацию — знать что здесь было
        2. NPC из локации А появляется в локации Б — знать историю NPC
        3. Возврат в старую локацию — восстановить обстановку
        """
        data = load_json(MEMORY_FILE, get_default_memory())
        locations = data.get("locations", {})
        
        if location_name not in locations:
            return f"Нет записей о локации '{location_name}'."
        
        loc = locations[location_name]
        lines = [f"\n=== КОНТЕКСТ ЛОКАЦИИ: {location_name} ==="]
        
        # Описание
        lines.append(f"Описание: {loc.get('description', 'нет')}")
        if loc.get("features"):
            lines.append(f"Особенности: {', '.join(loc['features'])}")
        
        # Персоналы
        chars = loc.get("characters_present", [])
        if chars:
            lines.append(f"Персоналы были здесь: {', '.join(chars)}")
        
        # События (последние 10)
        events = loc.get("events", [])
        if events:
            lines.append(f"\nСобытия ({len(events)} всего, последние 10):")
            for event in events[-10:]:
                parts = []
                if event.get("participants"):
                    parts.append(f"участники: {', '.join(event['participants'])}")
                if event.get("type"):
                    parts.append(f"[{event['type']}]")
                parts.append(event["description"])
                lines.append(f"  * {' | '.join(parts)}")
        
        lines.append("=== КОНЕЦ КОНТЕКСТА ===")
        return "\n".join(lines)

    @staticmethod
    def get_related_context(npc_name: str) -> str:
        """
        Получить контекст всех локаций, где был этот NPC.
        
        Используется когда NPC появляется в сцене — нейросеть знает:
        "NPC Мира была в локации 'Академия > Класс магии': 
         [событие] Игрок защитил Мира от буллинга.
         NPC Мира была в локации 'Библиотека':
         [событие] Мира и Игрок нашли тайник."
        """
        data = load_json(MEMORY_FILE, get_default_memory())
        locations = data.get("locations", {})
        
        relevant_locations = []
        for loc_name, loc_data in locations.items():
            events = loc_data.get("events", [])
            loc_events_with_npc = [e for e in events if npc_name in e.get("participants", [])]
            if loc_events_with_npc:
                relevant_locations.append({
                    "name": loc_name,
                    "description": loc_data.get("description", ""),
                    "events": loc_events_with_npc
                })
        
        if not relevant_locations:
            return f"Нет записей о предыдущих встречах с {npc_name}."
        
        lines = [f"\n=== ПРЕДЫСТОРИЯ: {npc_name} ==="]
        for loc in relevant_locations:
            lines.append(f"\nЛокация: {loc['name']} ({loc['description']})")
            for event in loc["events"]:
                parts = []
                if event.get("type"):
                    parts.append(f"[{event['type']}]")
                parts.append(event["description"])
                other_participants = [p for p in event.get("participants", []) if p != npc_name]
                if other_participants:
                    parts.append(f"(с: {', '.join(other_participants)})")
                lines.append(f"  * {' | '.join(parts)}")
        lines.append("=== КОНЕЦ ПРЕДЫСТОРИИ ===")
        return "\n".join(lines)

    @staticmethod
    def record_character_in_location(location: str, character: str):
        """Зафиксировать присутствие персонажа в локации."""
        data = load_json(MEMORY_FILE, get_default_memory())
        data.setdefault("locations", {})
        
        if location not in data["locations"]:
            data["locations"][location] = {
                "description": f"(локация {location})",
                "features": [],
                "first_seen": get_timestamp(),
                "characters_present": [],
                "events": [],
                "scenes": []
            }
        
        chars = data["locations"][location].setdefault("characters_present", [])
        if character not in chars:
            chars.append(character)
        
        save_json(MEMORY_FILE, data)


# ============================================================
# УРОВЕНЬ 4: СОСТОЯНИЕ ПЕРСОНАЖЕЙ (Character States)
# ============================================================
class CharacterStates:
    """Текущее состояние каждого персонажа."""

    @staticmethod
    def update(name: str, description: str = None, status: str = None, 
               position: str = None, inventory: dict = None, knowledge: list = None):
        """Обновить состояние персонажа."""
        data = load_json(MEMORY_FILE, get_default_memory())
        data.setdefault("characters", {})
        
        timestamp = get_timestamp()
        
        if name not in data["characters"]:
            data["characters"][name] = {
                "name": name,
                "description": description or "",
                "status": "unknown",
                "position": "unknown",
                "inventory": {},
                "knowledge": [],  # что персонаж знает о мире
                "first_seen": timestamp,
                "last_seen": timestamp,
                "interactions": 0
            }
        
        char = data["characters"][name]
        if description:
            char["description"] = description
        if status:
            char["status"] = status
        if position:
            char["position"] = position
        if inventory:
            char["inventory"].update(inventory)
        if knowledge:
            for item in knowledge:
                if item not in char["knowledge"]:
                    char["knowledge"].append(item)
        
        char["last_seen"] = timestamp
        char["interactions"] = char.get("interactions", 0) + 1
        
        save_json(MEMORY_FILE, data)
        print(f"[OK] Персонаж обновлён: {name}")

    @staticmethod
    def get(name: str) -> dict:
        """Получить состояние персонажа."""
        data = load_json(MEMORY_FILE, get_default_memory())
        characters = data.get("characters", {})
        if name in characters:
            return {"found": True, **characters[name]}
        return {"found": False}

    @staticmethod
    def add_item_to_inventory(character: str, item_name: str, properties: dict = None):
        """Добавить предмет в инвентарь персонажа."""
        data = load_json(MEMORY_FILE, get_default_memory())
        data.setdefault("characters", {})
        
        if character not in data["characters"]:
            data["characters"][character] = {
                "name": character, "description": "", "status": "unknown",
                "position": "unknown", "inventory": {},
                "knowledge": [], "first_seen": get_timestamp(),
                "last_seen": get_timestamp(), "interactions": 0
            }
        
        char = data["characters"][character]
        char.setdefault("inventory", {})[item_name] = {
            "properties": properties or {},
            "acquired": get_timestamp()
        }
        
        save_json(MEMORY_FILE, data)
        print(f"[OK] Предмет '{item_name}' добавлен в инвентарь {character}")


# ============================================================
# УРОВЕНЬ 5: ПРЕДМЕТЫ (Items)
# ============================================================
class Items:
    """Управление предметами."""

    @staticmethod
    def add(name: str, properties: dict = None, location: str = None, 
            owner: str = None, description: str = None):
        """Добавить предмет в мир."""
        data = load_json(MEMORY_FILE, get_default_memory())
        data.setdefault("items", {})
        
        timestamp = get_timestamp()
        
        if name not in data["items"]:
            data["items"][name] = {
                "name": name,
                "description": description or "",
                "properties": properties or {},
                "location": location or "unknown",
                "owner": owner or "world",
                "first_seen": timestamp,
                "last_seen": timestamp,
                "status": "active"  # active, lost, used, destroyed, hidden
            }
        else:
            item = data["items"][name]
            if properties:
                item["properties"].update(properties)
            if location:
                item["location"] = location
            if owner:
                item["owner"] = owner
            item["last_seen"] = timestamp
        
        save_json(MEMORY_FILE, data)
        print(f"[OK] Предмет сохранён: {name}")

    @staticmethod
    def get(name: str) -> dict:
        """Получить информацию о предмете."""
        data = load_json(MEMORY_FILE, get_default_memory())
        items = data.get("items", {})
        if name in items:
            return {"found": True, **items[name]}
        return {"found": False}


# ============================================================
# ДОПОЛНИТЕЛЬНЫЕ СОБЫТИЯ
# ============================================================
class GlobalEvents:
    """Глобальные события (не привязанные к конкретной локации)."""

    @staticmethod
    def add(event_type: str, description: str, participants: list = None, 
            tags: list = None, location: str = None):
        """Добавить глобальное событие."""
        data = load_json(MEMORY_FILE, get_default_memory())
        data.setdefault("events", [])
        
        event = {
            "id": len(data["events"]) + 1,
            "type": event_type,
            "description": description,
            "participants": participants or [],
            "tags": tags or [],
            "location": location or "",
            "timestamp": get_timestamp()
        }
        data["events"].append(event)
        
        save_json(MEMORY_FILE, data)
        print(f"[OK] Событие добавлено: [{event_type}] {description[:50]}...")


# ============================================================
# ЭКСПОРТ КОНТЕКСТА ДЛЯ НЕЙРОСЕТИ
# ============================================================
def get_full_context_for_npc(npc_name: str = None, max_chat: int = 10) -> str:
    """
    Собрать полный контекст для нейросети.
    
    Если npc_name указан — вернуть контекст конкретно для этого NPC:
    - Отношения с NPC
    - Предысторию встреч с NPC
    - Текущую сцену
    
    Если npc_name не указан — вернуть общий контекст.
    """
    parts = []
    timestamp = get_timestamp()
    
    parts.append(f"=== ПАМЯТЬ АКАДЕМИИ БАРСТОН (обновлено: {timestamp}) ===")
    data = load_json(MEMORY_FILE, get_default_memory())
    
    # Текущая локация
    current_loc = data.get("current_location", "unknown")
    parts.append(f"\n[ЛОКАЦИЯ] Текущая: {current_loc}")
    
    if npc_name:
        # Контекст для конкретного NPC
        
        # 1. Отношения
        rel_context = Relationships.get_context_for_npc(npc_name)
        parts.append(rel_context)
        
        # 2. Предыстория встреч
        history_context = LocationHistory.get_related_context(npc_name)
        parts.append(history_context)
        
        # 3. Состояние NPC
        char_data = CharacterStates.get(npc_name)
        if char_data.get("found"):
            parts.append(f"\n=== СОСТОЯНИЕ {npc_name} ===")
            parts.append(f"Описание: {char_data.get('description', '')}")
            parts.append(f"Статус: {char_data.get('status', 'unknown')}")
            parts.append(f"Позиция: {char_data.get('position', 'unknown')}")
            inv = char_data.get("inventory", {})
            if inv:
                parts.append(f"Инвентарь: {', '.join(inv.keys())}")
            parts.append("=== КОНЕЦ СОСТОЯНИЯ ===")
    
    # 4. Все отношения (если NPC не указан)
    if not npc_name:
        parts.append(f"\n{Relationships.list_all(data)}")
    
    # 5. Все персонажи
    characters = data.get("characters", {})
    if characters:
        parts.append(f"\n=== ПЕРСОНАЖИ ({len(characters)}) ===")
        for name, char in characters.items():
            parts.append(f"  * {name}: {char.get('description', '')} | статус={char.get('status', '?')} | позиция={char.get('position', '?')}")
        parts.append("=== КОНЕЦ ===")
    
    # 6. Предметы
    items = data.get("items", {})
    if items:
        parts.append(f"\n=== ПРЕДМЕТЫ ({len(items)}) ===")
        for name, item in items.items():
            parts.append(f"  * {name}: {item.get('description', '')} | владелец={item.get('owner', '?')} | {item.get('location', '?')}")
        parts.append("=== КОНЕЦ ===")
    
    # 7. Последние глобальные события (10)
    events = data.get("events", [])
    if events:
        parts.append(f"\n=== ПОСЛЕДНИЕ СОБЫТИЯ ({len(events)}, последние 10) ===")
        for event in events[-10:]:
            parts.append(f"  * [{event['type']}] {event['description']}")
        parts.append("=== КОНЕЦ ===")
    
    # 8. Текущая сцена (чат)
    parts.append(f"\n{CurrentScene.get_context_text(max_chat)}")
    
    return "\n".join(parts)


def get_default_memory() -> dict:
    """Структура по умолчанию для памяти мира."""
    return {
        "current_location": "unknown",
        "last_location": None,
        "scene_messages": [],
        
        "relationships": {},       # отношения между персонажами
        "characters": {},          # состояние персонажей
        "items": {},               # предметы
        "locations": {},           # локации с их историей
        "events": [],              # глобальные события
        
        "meta": {
            "created": get_timestamp(),
            "last_updated": get_timestamp()
        }
    }


# ============================================================
# КОМАНДНАЯ СТРОКА
# ============================================================
def print_help():
    """Показать справку."""
    print(__doc__)


def main():
    if len(sys.argv) < 2:
        print_help()
        return
    
    command = sys.argv[1].lower()
    
    try:
        # === СЦЕНА ===
        if command == "add-chat":
            if len(sys.argv) < 4:
                print("Использование: add-chat <роль> <текст>")
                return
            role = sys.argv[2]
            text = " ".join(sys.argv[3:])
            msg = CurrentScene.add_message(role, text)
            print(f"[OK] Сообщение: [{msg['role']}] {msg['text'][:50]}...")
        
        elif command == "move":
            if len(sys.argv) < 3:
                print("Использование: move <новая_локация>")
                return
            CurrentScene.set_location(sys.argv[2])
        
        elif command == "current-location":
            loc = CurrentScene.get_current_location()
            print(f"Текущая локация: {loc}")
        
        elif command == "list-chat":
            messages = CurrentScene.get_messages()
            if not messages:
                print("Сцена пуста.")
            else:
                print(f"Сообщений в сцене: {len(messages)}")
                print("---")
                for msg in messages:
                    print(f"[{msg['role']}] {msg['text']}")
        
        # === ОТНОШЕНИЯ ===
        elif command == "init-relationship":
            if len(sys.argv) < 5:
                print("Использование: init-relationship <персонаж1> <персонаж2> [начальный_уровень]")
                return
            char1 = sys.argv[2]
            char2 = sys.argv[3]
            level = int(sys.argv[4]) if len(sys.argv) > 4 else 0
            Relationships.init_relationship(char1, char2, level)
        
        elif command == "update-relation":
            if len(sys.argv) < 6:
                print("Использование: update-relation <персонаж1> <персонаж2> <изменение> <причина> [тип_события]")
                return
            char1 = sys.argv[2]
            char2 = sys.argv[3]
            delta = int(sys.argv[4])
            reason = " ".join(sys.argv[5:])
            event_type = sys.argv[6] if len(sys.argv) > 6 else "interaction"
            Relationships.update_level(char1, char2, delta, reason, event_type)
        
        elif command == "check-relation":
            if len(sys.argv) < 4:
                print("Использование: check-relation <персонаж1> <персонаж2>")
                return
            result = Relationships.get_level(sys.argv[2], sys.argv[3])
            if result.get("found"):
                print(f"{result['characters'][0]} <-> {result['characters'][1]}: {result['level']} ({result['label']})")
                if result["history"]:
                    print("  История:")
                    for h in result["history"]:
                        d = f"+{h['delta']}" if h['delta'] > 0 else str(h['delta'])
                        print(f"    [{h['event_type']}] {h['reason']} ({d})")
            else:
                print("Отношения не инициализированы.")
        
        elif command == "list-relations":
            data = load_json(MEMORY_FILE, get_default_memory())
            print(Relationships.list_all(data))
        
        # === ПЕРСОНАЖИ ===
        elif command == "add-npc" or command == "update-npc":
            if len(sys.argv) < 4:
                print("Использование: add-npc <имя> <описание>")
                return
            name = sys.argv[2]
            desc = " ".join(sys.argv[3:])
            CharacterStates.update(name, description=desc)
            print(f"[OK] Персонаж создан: {name}")
        
        elif command == "set-status":
            if len(sys.argv) < 4:
                print("Использование: set-status <npc> <статус>")
                return
            CharacterStates.update(sys.argv[2], status=sys.argv[3])
            print(f"[OK] Статус: {sys.argv[2]} -> {sys.argv[3]}")
        
        elif command == "set-position":
            if len(sys.argv) < 4:
                print("Использование: set-position <npc> <позиция>")
                return
            CharacterStates.update(sys.argv[2], position=sys.argv[3])
            print(f"[OK] Позиция: {sys.argv[2]} -> {sys.argv[3]}")
        
        elif command == "add-item-to-inv":
            if len(sys.argv) < 4:
                print("Использование: add-item-to-inv <персонаж> <предмет> [свойства...]")
                return
            char_name = sys.argv[2]
            item_name = sys.argv[3]
            props = {}
            for part in sys.argv[4:]:
                if "=" in part:
                    k, v = part.split("=", 1)
                    props[k] = v
            CharacterStates.add_item_to_inventory(char_name, item_name, props)
        
        elif command == "get-char":
            if len(sys.argv) < 3:
                print("Использование: get-char <имя_персонажа>")
                return
            result = CharacterStates.get(sys.argv[2])
            if result.get("found"):
                print(json.dumps(result, ensure_ascii=False, indent=2))
            else:
                print("Персонаж не найден.")
        
        # === ЛОКАЦИИ ===
        elif command == "add-location":
            if len(sys.argv) < 4:
                print("Использование: add-location <имя> <описание>")
                return
            name = sys.argv[2]
            desc = " ".join(sys.argv[3:])
            LocationHistory.add_location(name, desc)
        
        elif command == "add-location-event":
            if len(sys.argv) < 5:
                print("Использование: add-location-event <локация> <тип> <описание> [участники...]")
                return
            location = sys.argv[2]
            event_type = sys.argv[3]
            desc = " ".join(sys.argv[4:])
            participants = []
            for part in sys.argv[5:]:
                if part in ("participants", "-p"):
                    # Следующий аргумент — участники через запятую
                    if len(sys.argv) > sys.argv.index(part) + 1:
                        idx = sys.argv.index(part) + 1
                        participants = [p.strip() for p in sys.argv[idx].split(",")]
            LocationHistory.add_location_event(location, event_type, desc, participants)
        
        elif command == "location-context":
            if len(sys.argv) < 3:
                print("Использование: location-context <имя_локации>")
                return
            print(LocationHistory.get_location_context(sys.argv[2]))
        
        elif command == "record-location":
            if len(sys.argv) < 3:
                print("Использование: record-location <локация> <персонаж>")
                return
            LocationHistory.record_character_in_location(sys.argv[2], sys.argv[3])
        
        # === СОБЫТИЯ ===
        elif command == "add-event":
            if len(sys.argv) < 4:
                print("Использование: add-event <тип> <описание> [участники...]")
                return
            event_type = sys.argv[2]
            desc = " ".join(sys.argv[3:])
            participants = []
            for part in sys.argv[4:]:
                if "=" in part:
                    k, v = part.split("=", 1)
                    if k == "participants":
                        participants = [p.strip() for p in v.split(",")]
            GlobalEvents.add(event_type, desc, participants)
        
        # === ПРЕДМЕТЫ ===
        elif command == "add-item":
            if len(sys.argv) < 3:
                print("Использование: add-item <имя> [свойства...]")
                return
            name = sys.argv[2]
            props = {}
            for part in sys.argv[3:]:
                if "=" in part:
                    k, v = part.split("=", 1)
                    props[k] = v
            Items.add(name, props)
        
        # === КОНТЕКСТ ДЛЯ НЕЙРОСЕТИ ===
        elif command == "get-context" or command == "context":
            npc = sys.argv[2] if len(sys.argv) > 2 else None
            print(get_full_context_for_npc(npc))
        
        elif command == "npc-context":
            if len(sys.argv) < 3:
                print("Использование: npc-context <имя_персонажа>")
                return
            print(get_full_context_for_npc(sys.argv[2]))
        
        elif command == "export-context" or command == "export":
            npc = sys.argv[2] if len(sys.argv) > 2 else None
            context = get_full_context_for_npc(npc)
            output_file = BASE_DIR / "exported_context.txt"
            with open(output_file, "w", encoding="utf-8") as f:
                f.write(context)
            print(f"Контекст экспортирован в: {output_file}")
        
        elif command == "summarize" or command == "summary":
            print(get_full_context_for_npc())
        
        # === СБРОС ===
        elif command == "clear-scene":
            data = load_json(MEMORY_FILE, get_default_memory())
            data["scene_messages"] = []
            save_json(MEMORY_FILE, data)
            print("Сцена очищена.")
        
        elif command == "reset-all":
            confirm = input("Вы уверены? Вся память будет удалена! (yes/no): ")
            if confirm.lower() == "yes":
                save_json(MEMORY_FILE, get_default_memory())
                print("Вся память сброшена.")
        
        # === СПРАВКА ===
        elif command == "help" or command == "-h" or command == "--help":
            print_help()
        
        else:
            print(f"Неизвестная команда: {command}")
            print("Используйте 'help' для справки.")
    
    except KeyboardInterrupt:
        print("\nОтменено.")
    except Exception as e:
        print(f"Ошибка: {e}")


if __name__ == "__main__":
    main()
