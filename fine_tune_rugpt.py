import json
import torch
from torch.utils.data import Dataset, DataLoader
from transformers import AutoTokenizer, AutoModelForCausalLM, Trainer, TrainingArguments

class DialogDataset(Dataset):
    def __init__(self, data_path, tokenizer):
        with open(data_path, 'r', encoding='utf-8') as f:
            self.data = json.load(f)
        self.tokenizer = tokenizer

    def __len__(self):
        return len(self.data)

    def __getitem__(self, idx):
        item = self.data[idx]
        input_text = item['input']
        output_text = item['output']
        
        # Объединяем в один текст: "Пользователь: ...\nБот: ..."
        text = f"Пользователь: {input_text}\nБот: {output_text}\n\n"
        
        encodings = self.tokenizer(text, truncation=True, max_length=512, padding='max_length')
        return {
            'input_ids': torch.tensor(encodings['input_ids']),
            'attention_mask': torch.tensor(encodings['attention_mask']),
            'labels': torch.tensor(encodings['input_ids'])
        }

# Загружаем модель и токенизатор
def fine_tune():
    model_name = "sberbank-ai/rugpt3small_based_on_gpt2"
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    model = AutoModelForCausalLM.from_pretrained(model_name)
    
    # Убедимся, что токен-разделитель установлен
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token
    
    # Настраиваем аргументы обучения
    training_args = TrainingArguments(
        output_dir="./rugpt3_finetuned",
        num_train_epochs=3,
        per_device_train_batch_size=2,
        save_steps=100,
        logging_steps=50,
        save_total_limit=2,
        prediction_loss_only=True,
        report_to=[],  # отключаем логирование в W&B и др.
        learning_rate=5e-5,
        weight_decay=0.01,
        warmup_steps=100,
        gradient_accumulation_steps=4,
        fp16=torch.cuda.is_available(),  # включаем FP16, если есть GPU
        remove_unused_columns=False,
    )

    # Создаём датасет
    dataset = DialogDataset("training_data.json", tokenizer)

    # Создаём тренер
    trainer = Trainer(
        model=model,
        args=training_args,
        train_dataset=dataset,
    )

    # Запускаем дообучение
    trainer.train()

    # Сохраняем модель
    trainer.save_model("./rugpt3_finetuned")
    tokenizer.save_pretrained("./rugpt3_finetuned")
    
    print("✅ Модель дообучена и сохранена в ./rugpt3_finetuned")

if __name__ == "__main__":
    fine_tune()