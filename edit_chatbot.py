# Скрипт для редактирования chatbot.py
with open('Wuglarst/src/chatbot.py', 'r', encoding='utf-8') as f:
    content = f.read()

old_text = '''    def create_world(self, genre: str, tag: str) -> str:
        """Создаёт новый мир через WorldEngine"""
        if not self.world_engine_enabled or self.world_engine is None:
            return "❌ WorldEngine не доступен"
        try:
            world_name = self.world_engine.create_world(genre, tag)
            return f"✅ Мир '{world_name}' создан!"
        except Exception as e:
            return f"❌ Ошибка создания мира: {e}"'''

new_text = '''    def create_world(self, genre: str, tag: str) -> str:
        """Создаёт новый мир через WorldEngine (с полным описанием)"""
        if not self.world_engine_enabled or self.world_engine is None:
            return "❌ WorldEngine не доступен"
        try:
            result = self.world_engine.create_world(genre, tag)
            return result
        except Exception as e:
            return f"❌ Ошибка создания мира: {e}"'''

if old_text in content:
    content = content.replace(old_text, new_text)
    with open('Wuglarst/src/chatbot.py', 'w', encoding='utf-8') as f:
        f.write(content)
    print('OK - Файл обновлен')
else:
    print('NOT FOUND - Старый текст не найден')
    # Попробуем найти похожий текст
    import re
    pattern = r'def create_world\(self, genre: str, tag: str\) -> str:'
    matches = list(re.finditer(pattern, content))
    print(f'Найдено {len(matches)} совпадений')
    for m in matches:
        print(f'  Позиция {m.start()}: {content[m.start():m.start()+100]}')

