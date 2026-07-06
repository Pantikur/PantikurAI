# Скрипт для исправления chatbot.py
with open('Wuglarst/src/chatbot.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

# Заменяем строки 1756-1763 (индексы 1755-1762)
# Нужно добавить try: и удалить лишний return
lines[1755] = '    def create_world(self, genre: str, tag: str) -> str:\n'
lines[1756] = '        """Создаёт новый мир через WorldEngine (с полным описанием)"""\n'
lines[1757] = '        if not self.world_engine_enabled or self.world_engine is None:\n'
lines[1758] = '            return "❌ WorldEngine не доступен"\n'
lines[1759] = '        try:\n'
lines[1760] = '            result = self.world_engine.create_world(genre, tag)\n'
lines[1761] = '            return result\n'
lines[1762] = '        except Exception as e:\n'
lines[1763] = '            return f"❌ Ошибка создания мира: {e}"\n'

with open('Wuglarst/src/chatbot.py', 'w', encoding='utf-8') as f:
    f.writelines(lines)
print('OK - Файл исправлен')
