"""
Тест RUGPT3 — проверяем что модель загружается и отвечает.
"""

from transformers import AutoTokenizer, AutoModelForCausalLM
import torch

MODEL_PATH = "models/rugpt3"

print("=" * 60)
print("[TEST] RUGPT3 Small Test")
print("=" * 60)

# Загружаем
print("\n[1/3] Loading...")
tokenizer = AutoTokenizer.from_pretrained(MODEL_PATH)
model = AutoModelForCausalLM.from_pretrained(MODEL_PATH)
print("[OK] Loaded!")

# Тестируем
print("\n[2/3] Testing generation...")
test_prompts = [
    "Привет, как дела?",
    "Москва — это",
    "Футаба — это",
]

for prompt in test_prompts:
    inputs = tokenizer(prompt, return_tensors="pt")
    outputs = model.generate(
        **inputs,
        max_length=len(prompt) + 30,
        temperature=0.7,
        do_sample=True,
        pad_token_id=tokenizer.eos_token_id,
    )
    response = tokenizer.decode(outputs[0], skip_special_tokens=True)
    print(f"\n  Prompt: '{prompt}'")
    print(f"  Response: '{response}'")

# Сохраняем
print("\n[3/3] Model info:")
print(f"  Path: {MODEL_PATH}")
print(f"  Parameters: {sum(p.numel() for p in model.parameters()):,}")
print(f"  Device: {'CPU' if not torch.cuda.is_available() else 'GPU'}")

print("\n" + "=" * 60)
print("[SUCCESS] RUGPT3 works!")
print("=" * 60)
