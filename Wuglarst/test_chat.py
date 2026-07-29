#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Тест чата с Футабой"""
import requests
import json

BASE = "http://localhost:8001/api/futaba/chat"

tests = [
    ("привет, как дела?", "приветствие"),
    ("мне сегодня очень грустно", "грусть"),
    ("ты правда ИИ?", "упоминание ИИ"),
    ("расскажи что-нибудь интересное", "любопытство"),
    ("скучно, не знаю о чём говорить", "скучно"),
    ("пока, до свидания", "прощание"),
    ("спасибо, ты классная", "благодарность + комплимент"),
]

out = []
out.append("=" * 60)
out.append("CHAT TEST WITH FUTABA")
out.append("=" * 60)

for msg, label in tests:
    try:
        r = requests.post(BASE, json={"message": msg}, timeout=5)
        data = r.json()
        
        out.append(f"\n[{label}]")
        out.append(f"  USER: {msg}")
        out.append(f"  FUTABA: {data['response']}")
        out.append(f"  Emotion: {data['emotion']} | Mood: {data['mood']}")
        out.append(f"  Typing: {data['typing_time']:.1f}s")
    except Exception as e:
        out.append(f"\n[{label}] ERROR: {e}")

out.append("\n" + "=" * 60)
out.append("TEST COMPLETE!")
out.append("=" * 60)

result = "\n".join(out)
# Only write to file, don't print (console can't handle emojis)
with open("chat_test_result.txt", "w", encoding="utf-8") as f:
    f.write(result)
print("Results saved to chat_test_result.txt")
