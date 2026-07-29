#!/usr/bin/env python
# -*- coding: utf-8 -*-
import requests

BASE = "http://localhost:8001/api/futaba/chat"

tests = [
    ("ты ИИ? ты бот?", "тест: отрицание ИИ"),
    ("привет, как дела?", "тест: приветствие"),
    ("я тебя люблю ❤️", "тест: любовь"),
    ("мне сегодня хреново", "тест: грусть"),
    ("пока, до свидания", "тест: прощание"),
    ("спасибо", "тест: благодарность"),
    ("что ты делаешь?", "тест: что делаешь"),
    ("ой ну ты даёшь", "тест: реакция"),
    ("х", "тест: короткое сообщение"),
    ("ты серьёзно? 😂", "тест: ирония"),
]

out = []
out.append("=== ЧАТ С ФУТАБОЙ — ТЕСТИРОВАНИЕ ===\n")

for msg, label in tests:
    try:
        r = requests.post(BASE, json={"message": msg}, timeout=5)
        data = r.json()
        out.append(f"[{label}]")
        out.append(f"  👤 {msg}")
        out.append(f"  🎮 {data['response']}")
        out.append(f"  mood: {data['mood']}")
        out.append("")
    except Exception as e:
        out.append(f"[{label}] ОШИБКА: {e}\n")

with open("human_test_result.txt", "w", encoding="utf-8") as f:
    f.write("\n".join(out))
print("done")
