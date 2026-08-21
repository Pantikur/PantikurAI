# api/endpoints/knowledge.py — Эндпоинты модели и знаний

import os
import logging
from datetime import datetime
from fastapi.responses import FileResponse

logger = logging.getLogger("knowledge")


def format_size(size_bytes):
    if size_bytes < 1024:
        return f"{size_bytes} B"
    elif size_bytes < 1024 ** 2:
        return f"{size_bytes / 1024:.2f} KB"
    elif size_bytes < 1024 ** 3:
        return f"{size_bytes / 1024 ** 2:.2f} MB"
    else:
        return f"{size_bytes / 1024 ** 3:.2f} GB"


def get_file_size(path):
    if os.path.exists(path):
        return os.path.getsize(path)
    return None


def get_dir_size(path):
    if not os.path.exists(path):
        return None
    total = 0
    for dirpath, dirnames, filenames in os.walk(path):
        for f in filenames:
            fp = os.path.join(dirpath, f)
            if os.path.isfile(fp):
                total += os.path.getsize(fp)
    return total if total > 0 else None


async def get_model_size() -> dict:
    """GET /model/size — Размер модели и данных."""
    model_size = get_dir_size("models/qwen2.5-3b")
    conv_size = get_dir_size("data")
    train_size = get_dir_size("data")
    
    return {
        "name": "Qwen2.5-3B",
        "path": "models/qwen2.5-3b",
        "exists": model_size is not None,
        "size_bytes": model_size,
        "size_human": format_size(model_size) if model_size else "Не найдена",
        "tokenizer": {
            "path": "data/tokenizer.json",
            "exists": get_file_size("data/tokenizer.json") is not None,
            "size_bytes": get_file_size("data/tokenizer.json"),
            "size_human": format_size(get_file_size("data/tokenizer.json")) if get_file_size("data/tokenizer.json") else "Не найден",
        },
        "training_data": {
            "conversations_json": {
                "path": "data/conversations.json",
                "exists": conv_size is not None,
                "size_bytes": conv_size,
                "size_human": format_size(conv_size) if conv_size else "Не найден",
            },
            "training_pairs_jsonl": {
                "path": "data/training_pairs.jsonl",
                "exists": train_size is not None,
                "size_bytes": train_size,
                "size_human": format_size(train_size) if train_size else "Не найден",
            }
        },
        "total_size_bytes": sum(s for s in [model_size, get_file_size("data/tokenizer.json"), conv_size, train_size] if s is not None),
        "total_size_human": format_size(sum(s for s in [model_size, get_file_size("data/tokenizer.json"), conv_size, train_size] if s is not None)),
        "timestamp": datetime.now().isoformat()
    }
