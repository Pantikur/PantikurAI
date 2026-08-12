"""
Тест дообученной модели Вугларста.
"""

import sys
import io
from transformers import AutoTokenizer, AutoModelForCausalLM
from peft import PeftModel
import torch

# Fix Windows console
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

BASE_MODEL = "models/qwen2.5-3b"
LORA_MODEL = "models/rugpt3_vuglarst/lora_weights"
MERGED_MODEL = "models/rugpt3_vuglarst/merged"

print("=" * 60)
print("[TEST] Тест дообученной модели Вугларста")
print("=" * 60)

# Загружаем
print("\n[1/3] Загрузка базовой модели...")
tokenizer = AutoTokenizer.from_pretrained(BASE_MODEL)
base_model = AutoModelForCausalLM.from_pretrained(BASE_MODEL)

print("[2/3] Применение LoRA весов...")
model = PeftModel.from_pretrained(base_model, LORA_MODEL)
model = model.merge_and_unload()  # Слияние весов
print("[OK] Модель загружена!")

# Тестируем
print("\n[3/3] Тестирование...")
test_prompts = [
    "Привет, как дела?",
    "Футаба — это",
    "Вугларст — это",
    "Правила поведения:",
    "Как стать лучше?",
]

for prompt in test_prompts:
    inputs = tokenizer(prompt, return_tensors="pt")
    outputs = model.generate(
        **inputs,
        max_length=len(prompt) + 50,
        temperature=0.8,
        do_sample=True,
        pad_token_id=tokenizer.eos_token_id,
    )
    response = tokenizer.decode(outputs[0], skip_special_tokens=True)
    print(f"\n  Prompt: '{prompt}'")
    print(f"  Response: '{response}'")

print("\n" + "=" * 60)
print("[SUCCESS] Модель работает!")
print("=" * 60)
