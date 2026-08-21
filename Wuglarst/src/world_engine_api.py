# Wuglarst/src/world_engine_api.py — Методы ChatBot для работы с WorldEngine
#
# Вынесено из chatbot.py (секция "WorldEngine Methods").

import asyncio
from typing import Dict, List, Optional


class WorldEngineApiMixin:
    """Методы делегирования WorldEngine. Миксин для класса ChatBot.

    Все методы полагаются на атрибуты self.world_engine и self.world_engine_enabled,
    которые инициализируются в ChatBot.__init__.
    """

    def create_world(self, genre: str, tag: str) -> str:
        """Создаёт новый мир через WorldEngine (с полным описанием)"""
        if not self.world_engine_enabled or self.world_engine is None:
            return "❌ WorldEngine не доступен"
        try:
            result = self.world_engine.create_world(genre, tag)
            return result
        except Exception as e:
            return f"❌ Ошибка создания мира: {e}"

    def create_world_from_books(self, genre: Optional[str] = None, tag: Optional[str] = None, book_titles: Optional[List[str]] = None) -> Dict:
        """Создаёт новый мир на основе прочитанных книг"""
        if not self.world_engine_enabled or self.world_engine is None:
            raise RuntimeError("WorldEngine не доступен")
        try:
            world_data = self.world_engine.create_world_from_books(genre, tag, book_titles)
            world_name = world_data["name"]

            # Сохраняем мир
            self.world_engine.save_world(world_name, world_data)

            # Обновляем индекс
            self.world_engine.world_db.index["worlds"][world_name] = {
                "genre": world_data.get("genre", genre or "unknown"),
                "tag": world_data.get("tags", ["unknown"])[0] if world_data.get("tags") else (tag or "unknown"),
                "created_at": world_data.get("created_at", ""),
                "last_updated": world_data.get("last_updated", ""),
                "state": world_data.get("state", "draft"),
                "npc_count": len(world_data.get("npcs", [])),
                "event_count": len(world_data.get("events", [])),
                "fact_count": len(world_data.get("facts", [])),
            }
            self.world_engine.world_db._save_index()

            print(f"📚 Создан мир из книг: {world_name}")
            return world_data
        except Exception as e:
            raise RuntimeError(f"Ошибка создания мира из книг: {e}")

    def get_world_info(self, world_name: str) -> str:
        """Возвращает информацию о мире"""
        if not self.world_engine_enabled or self.world_engine is None:
            return "❌ WorldEngine не доступен"
        try:
            world = self.world_engine.get_world(world_name)
            if not world:
                return f"❌ Мир '{world_name}' не найден"

            info = f"🌍 **{world['name']}**\n"
            info += f"📚 Жанр: {world['genre']}\n"
            info += f"🏷️ Тег: {world['tags']}\n"
            info += f"⚡ Состояние: {world['state']}\n"
            info += f"📅 Эпоха: {world['era']}\n"
            info += f"👥 NPC: {len(world.get('npcs', []))}\n"
            info += f"⚔️ Фракции: {len(world.get('factions', []))}\n"
            info += f"📜 События: {len(world.get('events', []))}\n"
            info += f"📝 Факты: {len(world.get('facts', []))}\n"
            info += f"🔥 Конфликт: {world.get('conflict_level', 0):.0%}\n"
            info += f"✨ Магия: {world.get('magic_level', 0):.0%}\n"
            info += f"🔧 Технологии: {world.get('technology_level', 0):.0%}\n"

            if world.get('description'):
                info += f"\n📖 {world['description'][:200]}...\n"

            return info
        except Exception as e:
            return f"❌ Ошибка: {e}"

    def get_all_worlds(self) -> str:
        """Возвращает список всех миров"""
        if not self.world_engine_enabled or self.world_engine is None:
            return "❌ WorldEngine не доступен"
        try:
            worlds = self.world_engine.get_all_worlds()
            if not worlds:
                return "📭 Нет созданных миров"

            result = "🌍 **Все миры:**\n\n"
            for name in worlds:
                summary = self.world_engine.get_world_summary(name)
                if summary:
                    result += f"• **{name}** ({summary.get('genre', '?')}) — {summary.get('npc_count', 0)} NPC, {summary.get('event_count', 0)} событий\n"

            return result
        except Exception as e:
            return f"❌ Ошибка: {e}"

    def generate_event(self, world_name: str) -> str:
        """Генерирует событие в мире"""
        if not self.world_engine_enabled or self.world_engine is None:
            return "❌ WorldEngine не доступен"
        try:
            event = self.world_engine.generate_event(world_name)
            if not event:
                return f"❌ Мир '{world_name}' не найден"

            result = f"📜 **Событие в {world_name}:** {event.title}\n"
            result += f"📝 {event.description}\n"
            result += f"⚡ Тип: {event.type}, Серьёзность: {event.severity}\n"
            result += f"📍 Место: {event.location}\n"
            result += f"🔗 Последствия: {', '.join(event.consequences)}\n"

            return result
        except Exception as e:
            return f"❌ Ошибка: {e}"

    def check_consistency(self, world_name: str) -> str:
        """Проверяет консистентность лора"""
        if not self.world_engine_enabled or self.world_engine is None:
            return "❌ WorldEngine не доступен"
        try:
            consistency = self.world_engine.check_consistency(world_name)

            result = f"🔍 **Проверка {world_name}:**\n"
            result += f"📊 Фактов: {consistency['total_facts']}\n"
            result += f"👥 NPC: {consistency['total_npcs']}\n"
            result += f"⚔️ Фракции: {consistency['total_factions']}\n"
            result += f"⚠️ Проблем: {consistency['issues_count']}\n"

            if consistency['issues']:
                result += "\n**Проблемы:**\n"
                for issue in consistency['issues'][:5]:
                    result += f"• {issue.get('type', '?')}: {issue.get('fact1', '')[:50]}...\n"

            result += f"\n{'✅ Консистентен' if consistency['is_consistent'] else '❌ Есть проблемы'}\n"
            return result
        except Exception as e:
            return f"❌ Ошибка: {e}"

    def get_world_events(self, world_name: str, limit: int = 10) -> str:
        """Возвращает последние события мира"""
        if not self.world_engine_enabled or self.world_engine is None:
            return "❌ WorldEngine не доступен"
        try:
            events = self.world_engine.get_world_events(world_name, limit)
            if not events:
                return f"📭 В '{world_name}' пока нет событий"

            result = f"📜 **Последние события {world_name}:**\n\n"
            for event in events[-limit:]:
                result += f"• **{event['title']}** ({event['date'][:10]})\n"
                result += f"  {event['description'][:100]}...\n\n"

            return result
        except Exception as e:
            return f"❌ Ошибка: {e}"

    def get_npc_info(self, world_name: str, npc_name: str) -> str:
        """Возвращает информацию о NPC"""
        if not self.world_engine_enabled or self.world_engine is None:
            return "❌ WorldEngine не доступен"
        try:
            npc = self.world_engine.get_npc_summary(world_name, npc_name)
            if not npc:
                return f"❌ NPC '{npc_name}' не найден в '{world_name}'"

            result = f"👤 **{npc['name']}**\n"
            result += f"🎭 Роль: {npc['role']}\n"
            result += f"🎂 Возраст: {npc['age']}\n"
            result += f"🧬 Раса: {npc['race']}\n"
            result += f"🎨 Характер: {npc['personality']}\n"
            result += f"📍 Место: {npc['location']}\n"
            result += f"💚 Настроение: {npc['mood']}\n"
            result += f"⭐ Влияние: {npc['influence']:.0%}\n"
            result += f"🤝 Отношения: {npc['relations_count']}\n"
            result += f"📝 Воспоминания: {npc['memories_count']}\n"
            result += f"{'💀 Мёртв' if not npc.get('alive', True) else '✅ Жив'}\n"

            return result
        except Exception as e:
            return f"❌ Ошибка: {e}"

    async def start_background_cycle(self) -> str:
        """Запускает фоновый цикл развития миров"""
        if not self.world_engine_enabled or self.world_engine is None:
            return "❌ WorldEngine не доступен"
        try:
            if self.world_engine.background_engine.running:
                return "⏳ Фоновый цикл уже запущен"

            # Запускаем в отдельном потоке
            loop = asyncio.get_event_loop()
            await loop.run_in_executor(None, self._start_bg_cycle_sync)

            return "🔄 Фоновый цикл запущен! Миры будут развиваться автоматически."
        except Exception as e:
            return f"❌ Ошибка: {e}"

    def _start_bg_cycle_sync(self):
        """Синхронная обёртка для запуска фонового цикла"""
        if self.world_engine is None:
            return
        worlds = self.world_engine.get_all_worlds()
        asyncio.run(self.world_engine.start_background_cycle(worlds))

    def stop_background_cycle(self) -> str:
        """Останавливает фоновый цикл"""
        if not self.world_engine_enabled or self.world_engine is None:
            return "❌ WorldEngine не доступен"
        try:
            self.world_engine.stop_background_cycle()
            return "🛑 Фоновый цикл остановлен"
        except Exception as e:
            return f"❌ Ошибка: {e}"

    def get_world_status(self) -> str:
        """Возвращает статус всех систем WorldEngine"""
        if not self.world_engine_enabled or self.world_engine is None:
            return "❌ WorldEngine не доступен"
        try:
            status = self.world_engine.get_status()

            result = "🌍 **Статус WorldEngine:**\n"
            result += f"📊 Всего миров: {status['total_worlds']}\n"
            result += f"🔄 Фоновый цикл: {'✅ Запущен' if status['background_running'] else '❌ Остановлен'}\n"
            result += f"⏱ Циклов: {status['cycle_count']}\n\n"

            if status['worlds']:
                result += "**Миры:**\n"
                for world in status['worlds'][:5]:
                    result += f"• {world['name']} ({world.get('genre', '?')}) — {world.get('npc_count', 0)} NPC, {world.get('event_count', 0)} событий\n"

            return result
        except Exception as e:
            return f"❌ Ошибка: {e}"