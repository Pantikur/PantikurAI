# rpg_generator.py (обновлённая)
import json
import os
from pathlib import Path

DATA_DIR = Path("data")
RPG_SCENES_PATH = DATA_DIR / "rpg_scenes.jsonl"
TRAINING_PAIRS_PATH = DATA_DIR / "training_pairs.jsonl"

def load_rpg_scenes():
    scenes = []
    if RPG_SCENES_PATH.exists():
        with open(RPG_SCENES_PATH, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith("#"):
                    continue
                try:
                    scenes.append(json.loads(line))
                except Exception as e:
                    print(f"⚠️ Пропущена строка: {e}")
    return scenes

def generate_training_pairs(scenes):
    pairs = []
    for scene in scenes:
        context = scene.get("context", "").strip()
        user_input = scene.get("user_input", "").strip()
        bot_response = scene.get("bot_response", "").strip()

        if not context or not user_input or not bot_response:
            continue

        # Формируем пару: «контекст + ввод → ответ»
        user_prompt = f"{context}\n{user_input}"
        pairs.append({
            "user": user_prompt,
            "bot": bot_response
        })
    return pairs

def main():
    os.makedirs(DATA_DIR, exist_ok=True)

    scenes = load_rpg_scenes()
    if not scenes:
        print("⚠️ Нет RPG-сценариев. Создайте data/rpg_scenes.jsonl")
        return

    print(f"✅ Загружено {len(scenes)} RPG-сценариев")

    pairs = generate_training_pairs(scenes)
    print(f"✅ Генерировано {len(pairs)} обучающих пар")

    # Добавляем в training_pairs.jsonl
    if not TRAINING_PAIRS_PATH.exists():
        open(TRAINING_PAIRS_PATH, "w", encoding="utf-8").close()

    with open(TRAINING_PAIRS_PATH, "a", encoding="utf-8") as f:
        for pair in pairs:
            line = json.dumps(pair, ensure_ascii=False)
            f.write(line + "\n")

    print(f"✅ Сохранено в {TRAINING_PAIRS_PATH}")


if __name__ == "__main__":
    main()