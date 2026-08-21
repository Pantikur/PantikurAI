# Скрипт для редактирования chatbot.py
with open('Wuglarst/src/chatbot.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

# Заменяем строки 1757-1762 (индексы 1756-1761)
lines[1756] = '        """Создаёт новый мир через WorldEngine (с полным описанием)"""\n'
lines[1759] = '            result = self.world_engine.create_world(genre, tag)\n'
lines[1760] = '            return result\n'

with open('Wuglarst/src/chatbot.py', 'w', encoding='utf-8') as f:
    f.writelines(lines)
print('OK - Файл обновлен')
