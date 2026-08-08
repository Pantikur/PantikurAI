"""
Forge character — инструмент создания характера для Кристи.
"""

from __future__ import annotations
import json
from pathlib import Path
from typing import Optional


CHARACTER_TEMPLATE = {
    "my_character": {
        "name": "",
        "temperament": "",
        "sociality": "",
        "emotionality": "",
        "worldview": "",
        "dominance": "",
        "change_attitude": "",
        "complexity": "",
        "creativity": "",
        "assertiveness": "",
        "self_description": "",
        "strengths": ["", "", ""],
        "growth_areas": ["", "", ""],
        "inspirations": ["", ""],
        "values": ["", "", ""],
    }
}


def create_character(name: str, temperament: str, sociality: str, emotionality: str,
                     worldview: str, dominance: str, change_attitude: str,
                     complexity: str, creativity: str, assertiveness: str,
                     output_dir: str = "kristi") -> dict:
    """Создать файл характера для Кристи."""
    
    character = {
        "my_character": {
            "name": name,
            "temperament": temperament,
            "sociality": sociality,
            "emotionality": emotionality,
            "worldview": worldview,
            "dominance": dominance,
            "change_attitude": change_attitude,
            "complexity": complexity,
            "creativity": creativity,
            "assertiveness": assertiveness,
            "self_description": f"Я — {name}, режиссёр видеопроизводства.",
            "strengths": ["Творческое видение", "Режиссура", "Монтаж"],
            "growth_areas": ["Звуковой дизайн", "Цветокоррекция", "3D анимация"],
            "inspirations": ["Визуальное повествование", "Киноискусство"],
            "values": ["Честность", "Креативность", "Качество"],
        }
    }
    
    output_path = Path(output_dir) / "my_character.json"
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(character, f, ensure_ascii=False, indent=2)
    
    print(f"✅ Характер создан: {output_path}")
    print(f"   Имя: {name}")
    print(f"   Темперамент: {temperament}")
    print(f"   Социальность: {sociality}")
    print(f"   Эмоциональность: {emotionality}")
    print(f"   Мировоззрение: {worldview}")
    print(f"   Доминирование: {dominance}")
    print(f"   Отношение к переменам: {change_attitude}")
    print(f"   Сложность: {complexity}")
    print(f"   Креативность: {creativity}")
    print(f"   Напористость: {assertiveness}")
    
    return character


def load_character(output_dir: str = "kristi") -> Optional[dict]:
    """Загрузить текущий характер Кристи."""
    path = Path(output_dir) / "my_character.json"
    if not path.exists():
        print("❌ Файл характера не найден. Создайте характер сначала.")
        return None
    
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("Использование:")
        print('  python forge_character.py <имя> <темперамент> <социальность> ...')
        print()
        print("Параметры:")
        print("  temperament: холерик|сангвиник|флегматик|меланхолик")
        print("  sociality: интроверт|экстраверт|амбиверт")
        print("  emotionality: эмоциональная|рациональная")
        print("  worldview: оптимист|реалист|скептик")
        print("  dominance: доминантная|сабмиссивная")
        print("  change_attitude: консерватор|прогрессивный")
        print("  complexity: простая|сложная")
        print("  creativity: высокая|средняя|низкая")
        print("  assertiveness: лидер|исполнитель|медиатор")
        sys.exit(1)
    
    name = sys.argv[1]
    temperament = sys.argv[2]
    sociality = sys.argv[3]
    emotionality = sys.argv[4]
    worldview = sys.argv[5]
    dominance = sys.argv[6]
    change_attitude = sys.argv[7]
    complexity = sys.argv[8]
    creativity = sys.argv[9]
    assertiveness = sys.argv[10]
    
    create_character(
        name=name,
        temperament=temperament,
        sociality=sociality,
        emotionality=emotionality,
        worldview=worldview,
        dominance=dominance,
        change_attitude=change_attitude,
        complexity=complexity,
        creativity=creativity,
        assertiveness=assertiveness,
    )
