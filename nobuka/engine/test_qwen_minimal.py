"""
Минимальный тест для проверки загрузки и работы Qwen2.5 моделей.

Не зависит от NobukaCore и других модулей.

Использование:
    python test_qwen_minimal.py              # тест обоих моделей
    python test_qwen_minimal.py --coder      # только Coder модель
    python test_qwen_minimal.py --general    # только General модель
"""

from __future__ import annotations
import argparse
import sys
import time
from pathlib import Path

# Принудительный UTF-8 для Windows-консоли
for _stream in (sys.stdout, sys.stderr):
    _reconfigure = getattr(_stream, "reconfigure", None)
    if _reconfigure is not None:
        try:
            _reconfigure(encoding="utf-8")
        except Exception:
            pass

# Добавляем корень проекта в path
_project_root = Path(__file__).parent.parent.resolve()
if str(_project_root) not in sys.path:
    sys.path.insert(0, str(_project_root))

try:
    import torch
    from transformers import AutoTokenizer, AutoModelForCausalLM
except ImportError as e:
    print(f"❌ Ошибка импорта: {e}")
    print("Установите зависимости: pip install torch transformers")
    sys.exit(1)


def get_model_device(model):
    """Получить устройство модели (работает с device_map='auto')."""
    try:
        params = list(model.parameters())
        if params:
            return params[0].device
        return next(model.modules()).weight.device
    except Exception:
        return "cpu"


def load_model(model_path: str, name: str):
    """Загрузить модель и токенизатор."""
    path = Path(model_path)
    if not path.exists() or not any(path.iterdir()):
        print(f"❌ Модель {name} не найдена по пути: {model_path}")
        return None, None

    print(f"\n📦 Загрузка {name}...")
    start = time.time()

    try:
        # Загружаем токенизатор
        tokenizer = AutoTokenizer.from_pretrained(
            path,
            trust_remote_code=True
        )
        print(f"   ✅ Токенизатор загружен ({time.time() - start:.1f}с)")

        # Определяем dtype и device
        if torch.cuda.is_available():
            dtype = torch.float16
            device = "auto"
            print(f"   🎮 GPU доступен: {torch.cuda.get_device_name(0)}")
        else:
            dtype = torch.float32
            device = None
            print("   💻 CPU режим")

        # Загружаем модель
        model = AutoModelForCausalLM.from_pretrained(
            path,
            torch_dtype=dtype,
            device_map=device if device == "auto" else None,
            trust_remote_code=True,
        )
        model.eval()
        print(f"   ✅ Модель {name} загружена ({time.time() - start:.1f}с)")
        
        return model, tokenizer
        
    except Exception as e:
        print(f"❌ Ошибка загрузки {name}: {e}")
        return None, None


def test_model(model, tokenizer, name: str, prompts: list[str]):
    """Протестировать модель на запросах."""
    if model is None or tokenizer is None:
        print(f"⚠️  Модель {name} не загружена, пропускаем тест")
        return

    device = get_model_device(model)
    print(f"\n💡 Устройство: {device}")
    print(f"📊 Параметров: {sum(p.numel() for p in model.parameters()) / 1e6:.1f}M")

    for i, prompt in enumerate(prompts, 1):
        print(f"\n{'=' * 60}")
        print(f"Запрос {i}: {prompt}")
        print('=' * 60)

        start = time.time()
        try:
            # Применяем шаблон чата
            messages = [
                {"role": "system", "content": f"Ты — {name}. Отвечай на русском языке."},
                {"role": "user", "content": prompt}
            ]
            
            text = tokenizer.apply_chat_template(
                messages,
                tokenize=False,
                add_generation_prompt=True
            )

            # Токенизируем
            model_inputs = tokenizer([text], return_tensors="pt").to(device)

            # Генерируем
            with torch.no_grad():
                generated_ids = model.generate(
                    **model_inputs,
                    max_new_tokens=512,
                    temperature=0.7,
                    top_p=0.9,
                    do_sample=True,
                )

            # Декодируем
            generated_ids = [
                output_ids[len(input_ids):]
                for input_ids, output_ids in zip(model_inputs.input_ids, generated_ids)
            ]
            response = tokenizer.batch_decode(generated_ids, skip_special_tokens=True)[0]

            elapsed = time.time() - start
            print(f"\n⏱️  Время генерации: {elapsed:.1f}с")
            print(f"\nОтвет:\n{response}")

        except Exception as e:
            print(f"\n❌ Ошибка генерации: {e}")


def main():
    parser = argparse.ArgumentParser(description="Минимальный тест Qwen2.5 моделей")
    parser.add_argument("--coder", action="store_true", help="Тестировать только Coder модель")
    parser.add_argument("--general", action="store_true", help="Тестировать только General модель")
    args = parser.parse_args()

    print("=" * 70)
    print("🧪 МИНИМАЛЬНЫЙ ТЕСТ QWEN2.5 МОДЕЛЕЙ")
    print("=" * 70)
    print(f"\nPyTorch версия: {torch.__version__}")
    print(f"CUDA доступно: {torch.cuda.is_available()}")
    if torch.cuda.is_available():
        print(f"CUDA версия: {torch.version.cuda}")
        print(f"GPU: {torch.cuda.get_device_name(0)}")

    # Пути к моделям (в корне проекта)
    coder_path = _project_root.parent / "models" / "qwen2.5-coder-3b"
    general_path = _project_root.parent / "models" / "qwen2.5-3b"

    # Тестируем Coder модель
    coder_model = None
    coder_tokenizer = None
    if not args.general:
        coder_model, coder_tokenizer = load_model(str(coder_path), "Qwen2.5-Coder-3B")

    # Тестируем General модель
    general_model = None
    general_tokenizer = None
    if not args.coder:
        general_model, general_tokenizer = load_model(str(general_path), "Qwen2.5-3B")

    # Тесты
    coder_prompts = [
        "Напиши функцию на Python для сортировки списка чисел",
        "Как исправить ошибку TypeError в Python?",
    ]

    general_prompts = [
        "Привет! Расскажи о себе",
        "Какие у тебя хобби?",
    ]

    if not args.general:
        test_model(coder_model, coder_tokenizer, "Qwen2.5-Coder-3B", coder_prompts)

    if not args.coder:
        test_model(general_model, general_tokenizer, "Qwen2.5-3B", general_prompts)

    print("\n" + "=" * 70)
    print("✅ ТЕСТ ЗАВЕРШЁН")
    print("=" * 70)


if __name__ == "__main__":
    main()
