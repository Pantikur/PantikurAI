# create_theme.py

import os
import sys

def create_theme(name, title, sentiments, examples_per_sentiment=4):
    """
    Создаёт JSONL-файл с шаблоном для новой эмоциональной темы.
    
    :param name: имя файла (например, 'pride')
    :param title: заголовок (например, 'Гордыня')
    :param sentiments: список меток (например, ['pride_strength', 'pride_superiority', ...])
    :param examples_per_sentiment: сколько примеров создать (пока с плейсхолдерами)
    """
    filename = f"data/{name}_emotional_phrases.jsonl"
    os.makedirs("data", exist_ok=True)

    with open(filename, 'w', encoding='utf-8') as f:
        f.write(f"// {title}\n\n")
        
        for sentiment in sentiments:
            # Человеческое описание из метки (пример: pride_strength → "гордыня как сила")
            description = sentiment.replace(f"{name}_", "").replace("_", " ")
            f.write(f"// {title.lower()} как {description}\n")
            
            for i in range(examples_per_sentiment):
                example = {
                    "text": f"Пример фразы для '{sentiment}' — замените на реальную.",
                    "sentiment": sentiment,
                    "source": f"{name}_emotional_training"
                }
                f.write(f"{example}\n")
            
            f.write("\n")  # Пустая строка между блоками
    
    print(f"✅ Шаблон создан: {filename}")
    print(f"📌 Откройте файл и замените 'Пример фразы...' на настоящие тексты.")
    print(f"💡 Используйте контекст: {title}, {description}.")


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("❌ Использование:")
        print("   python create_theme.py <имя> <заголовок> <метка1 метка2 ...>")
        print("Пример:")
        print("   python create_theme.py pride Гордыня pride_strength pride_superiority")
        sys.exit(1)

    name = sys.argv[1].lower()
    title = sys.argv[2]
    sentiments = sys.argv[3].split()

    if not sentiments:
        print("❌ Укажите хотя бы одну метку (sentiment)")
        sys.exit(1)

    create_theme(name, title, sentiments)