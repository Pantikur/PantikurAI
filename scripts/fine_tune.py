#!/usr/bin/env python3
"""
Дообучение Qwen2.5-3B на данных Вугларста.

Использует LoRA (Low-Rank Adaptation) для эффективного дообучения:
  • Дообучается только 1-2% параметров
  • Работает на CPU (медленно, но работает)
  • Экономит RAM (~8 ГБ вместо ~24 ГБ)
  • Результат: models/qwen2.5-3b/

Использование:
    python scripts/fine_tune.py              # начать обучение
    python scripts/fine_tune.py --epochs 5   # 5 эпох
    python scripts/fine_tune.py --lora-r 16  # изменить rank
    python scripts/fine_tune.py --resume     # продолжить с чекпоинта
"""

import os
import sys
import json
import time
import io
from pathlib import Path
from dataclasses import dataclass, field
from typing import List, Dict, Optional

# Fix Windows console
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

# Import PyTorch
import torch
from torch.utils.data import Dataset, DataLoader

# Import transformers
from transformers import (
    AutoTokenizer,
    AutoModelForCausalLM,
    Trainer,
    TrainingArguments,
    DataCollatorForLanguageModeling,
)

from peft import LoraConfig, get_peft_model, TaskType, PeftModel

print("=" * 60)
print("[FINE-TUNE] Дообучение Qwen2.5-3B — Вугларст Edition")
print("=" * 60)


# === CONFIG ===
@dataclass
class TrainConfig:
    """Конфигурация обучения."""
    base_model: str = "models/qwen2.5-3b"  # Базовая модель
    output_dir: str = "models/qwen2.5-3b-finetuned"  # Куда сохранять
    dataset_path: str = "data/training_dataset.jsonl"  # Датасет
    epochs: int = 3  # Эпохи обучения
    batch_size: int = 2  # Размер батча
    learning_rate: float = 2e-4  # Скорость обучения
    lora_r: int = 8  # LoRA rank (8-16)
    lora_alpha: int = 16  # LoRA alpha
    lora_dropout: float = 0.1  # Dropout для LoRA
    max_length: int = 256  # Максимальная длина текста
    warmup_ratio: float = 0.1  # Прогрев
    save_steps: int = 500  # Сохранять каждые N шагов
    logging_steps: int = 50  # Логировать каждые N шагов
    weight_decay: float = 0.01  # Weight decay
    fp16: bool = False  # FP16 для GPU


# === DATASET ===
class VuglarstDataset(Dataset):
    """Датасет для дообучения на данных Вугларста."""
    
    def __init__(self, data_path: str, tokenizer, max_length: int = 256):
        self.max_length = max_length
        self.tokenizer = tokenizer
        self.encodings = []
        
        print(f"\n[LOAD] Загрузка датасета из {data_path}...")
        
        with open(data_path, "r", encoding="utf-8") as f:
            lines = f.readlines()
        
        print(f"  [INFO] Загружено {len(lines)} строк")
        
        # Кодируем все примеры
        for i, line in enumerate(lines):
            if i % 1000 == 0:
                print(f"  [PROGRESS] Кодирование: {i}/{len(lines)}")
            
            try:
                item = json.loads(line.strip())
                prompt = item.get("prompt", "")
                completion = item.get("completion", "")
                
                # Объединяем prompt + completion
                text = f"{prompt} {completion}"
                
                # Кодируем
                enc = tokenizer(
                    text,
                    truncation=True,
                    max_length=max_length,
                    padding="max_length",
                )
                
                self.encodings.append(enc)
                
            except (json.JSONDecodeError, Exception) as e:
                continue
        
        print(f"  [OK] Закодировано {len(self.encodings)} примеров")
    
    def __len__(self):
        return len(self.encodings)
    
    def __getitem__(self, idx):
        item = self.encodings[idx]
        return {
            "input_ids": torch.tensor(item["input_ids"]),
            "attention_mask": torch.tensor(item["attention_mask"]),
            "labels": torch.tensor(item["input_ids"]),  # labels = input_ids для MLM
        }


def load_model_and_tokenizer(config: TrainConfig):
    """Загружает базовую модель и токенизатор."""
    print(f"\n[LOAD] Загрузка модели из {config.base_model}...")
    
    tokenizer = AutoTokenizer.from_pretrained(config.base_model)
    # Добавляем padding token если нет
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token
    
    model = AutoModelForCausalLM.from_pretrained(config.base_model)
    
    print(f"  [OK] Модель загружена: {sum(p.numel() for p in model.parameters()):,} параметров")
    
    return model, tokenizer


def setup_lora(model, config: TrainConfig):
    """Настраивает LoRA на модель."""
    print("\n[LoRA] Настройка Low-Rank Adaptation...")
    
    lora_config = LoraConfig(
        task_type=TaskType.CAUSAL_LM,
        r=config.lora_r,
        lora_alpha=config.lora_alpha,
        lora_dropout=config.lora_dropout,
        target_modules=["c_attn", "c_proj", "c_fc"],  # Target layers для GPT-2
    )
    
    model = get_peft_model(model, lora_config)
    model.print_trainable_parameters()
    
    print(f"  [OK] LoRA настроена: rank={config.lora_r}, alpha={config.lora_alpha}")
    
    return model


def train(config: TrainConfig):
    """Запускает обучение."""
    
    # 1. Загружаем модель
    model, tokenizer = load_model_and_tokenizer(config)
    
    # 2. Настраиваем LoRA
    model = setup_lora(model, config)
    
    # 3. Загружаем датасет
    dataset = VuglarstDataset(
        data_path=config.dataset_path,
        tokenizer=tokenizer,
        max_length=config.max_length,
    )
    
    if len(dataset) == 0:
        print("[ERROR] Датасет пуст! Проверьте data/training_dataset.jsonl")
        sys.exit(1)
    
    # Разделяем на train/val (90/10)
    train_size = int(len(dataset) * 0.9)
    val_size = len(dataset) - train_size
    train_dataset, val_dataset = torch.utils.data.random_split(
        dataset, [train_size, val_size]
    )
    
    print(f"\n[DATA] Train: {len(train_dataset)}, Val: {len(val_dataset)}")
    
    # 4. Data collator
    data_collator = DataCollatorForLanguageModeling(
        tokenizer=tokenizer,
        mlm=False,  # Не MLM, а causal LM
    )
    
    # 5. Training args
    output_path = Path(config.output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    
    training_args = TrainingArguments(
        output_dir=str(output_path),
        num_train_epochs=config.epochs,
        per_device_train_batch_size=config.batch_size,
        per_device_eval_batch_size=config.batch_size,
        learning_rate=config.learning_rate,
        warmup_ratio=config.warmup_ratio,
        weight_decay=config.weight_decay,
        logging_steps=config.logging_steps,
        save_steps=config.save_steps,
        eval_strategy="steps",  # Устаревший name, но работает в transformers 5.x
        eval_steps=config.save_steps,
        save_strategy="steps",
        save_total_limit=3,
        load_best_model_at_end=True,
        fp16=config.fp16,
        report_to="none",
        dataloader_num_workers=0,
    )
    
    # 6. Trainer
    trainer = Trainer(
        model=model,
        args=training_args,
        train_dataset=train_dataset,
        eval_dataset=val_dataset,
        data_collator=data_collator,
    )
    
    # 7. Определяем устройство
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    model.to(device)
    print(f"\n[DEVICE] Используем: {device}")
    
    # 8. Начинаем обучение!
    print(f"\n{'='*60}")
    print("[TRAIN] Начало обучения!")
    print(f"  Эпохи: {config.epochs}")
    print(f"  Batch size: {config.batch_size}")
    print(f"  Learning rate: {config.learning_rate}")
    print(f"  Max length: {config.max_length}")
    print(f"  Device: {device}")
    print(f"{'='*60}")
    
    start_time = time.time()
    
    try:
        trainer.train()
    except Exception as e:
        print(f"\n[ERROR] Ошибка обучения: {e}")
        print("\n[TIP] Если ошибка out of memory:")
        print("  1. Уменьши batch_size до 1")
        print("  2. Уменьши max_length до 128")
        print("  3. Увеличь lora_r для более эффективного обучения")
        raise
    
    elapsed = time.time() - start_time
    hours = int(elapsed // 3600)
    mins = int((elapsed % 3600) // 60)
    secs = int(elapsed % 60)
    
    print(f"\n{'='*60}")
    print(f"[OK] Обучение завершено за {hours}ч {mins}м {secs}с")
    print(f"{'='*60}")
    
    # 8. Сохраняем модель
    print(f"\n[SAVE] Сохранение модели в {config.output_dir}...")
    
    # Сохраняем LoRA weights
    if hasattr(model, 'save_pretrained'):
        model.save_pretrained(output_path / "lora_weights")
        tokenizer.save_pretrained(output_path / "lora_weights")
    
    # Если есть peft, можно слить веса
    merged_model = model.merge_and_unload()
    merged_model.save_pretrained(output_path / "merged")
    tokenizer.save_pretrained(output_path / "merged")
    print(f"  [OK] Мerged модель сохранена в merged/")
    
    print(f"  [OK] LoRA веса сохранены в lora_weights/")
    
    # Сохраняем конфиг обучения
    config_path = output_path / "train_config.json"
    with open(config_path, "w", encoding="utf-8") as f:
        json.dump({
            "base_model": config.base_model,
            "epochs": config.epochs,
            "batch_size": config.batch_size,
            "learning_rate": config.learning_rate,
            "lora_r": config.lora_r,
            "lora_alpha": config.lora_alpha,
            "max_length": config.max_length,
            "dataset_path": config.dataset_path,
        }, f, ensure_ascii=False, indent=2)
    
    print(f"  [OK] Конфиг сохранён в {config_path}")
    
    print(f"\n{'='*60}")
    print("[SUCCESS] Дообучение завершено!")
    print(f"{'='*60}")
    print(f"\nМодель сохранена в: {output_path}")
    print(f"Использование:")
    print(f"  from peft import PeftModel")
    print(f"  base = AutoModelForCausalLM.from_pretrained('{config.base_model}')")
    print(f"  model = PeftModel.from_pretrained(base, '{output_path}/lora_weights')")


def main():
    """Главная функция."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Дообучение Qwen2.5-3B на данных Вугларста")
    parser.add_argument("--epochs", type=int, default=3, help="Количество эпох (default: 3)")
    parser.add_argument("--batch-size", type=int, default=2, help="Размер батча (default: 2)")
    parser.add_argument("--lora-r", type=int, default=8, help="LoRA rank (default: 8)")
    parser.add_argument("--max-length", type=int, default=256, help="Максимальная длина (default: 256)")
    parser.add_argument("--resume", action="store_true", help="Продолжить обучение")
    parser.add_argument("--dataset", type=str, default=None, help="Путь к датасету")
    
    args = parser.parse_args()
    
    config = TrainConfig(
        epochs=args.epochs,
        batch_size=args.batch_size,
        lora_r=args.lora_r,
        max_length=args.max_length,
        dataset_path=args.dataset or TrainConfig.dataset_path,
    )
    
    train(config)


if __name__ == "__main__":
    main()
