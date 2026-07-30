# Загрузка Wuglarst на HuggingFace

## 1. Получи токен

1. Зайди на https://huggingface.co/settings/tokens
2. Создай новый токен (тип: Write)
3. Скопируй токен

## 2. Создай репозиторий

Нажми **"New repository"** и создай с именем:
- **Name:** `Wuglarst`
- **Private:** можно сделать Private
- **Initialize:** не инициализируй (пустой)

## 3. Настрой токен

```powershell
$env:HF_TOKEN = "hf_твой_токен"
```

## 4. Загрузи модель

```powershell
python upload_to_huggingface.py
```

## 5. Проверь

Модель будет доступна по адресу:
https://huggingface.co/Pantikur/Wuglarst

## 6. Готово!

Приложение будет автоматически загружать модель из HF при запуске.