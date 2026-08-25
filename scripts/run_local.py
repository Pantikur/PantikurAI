#!/usr/bin/env python3
"""
Локальный запуск Pantikur ChatBot (без Docker).

Использование:
    python run_local.py              # Запустить на порту 8000
    python run_local.py --port 9000  # Запустить на другом порту
    python run_local.py --host 127.0.0.1  # Только локально
"""

import sys
import argparse
import os


def main():
    parser = argparse.ArgumentParser(description="Локальный запуск Pantikur ChatBot")
    parser.add_argument("--port", type=int, default=8000, help="Порт (по умолчанию: 8000)")
    parser.add_argument("--host", type=str, default="0.0.0.0", help="Хост (по умолчанию: 0.0.0.0)")
    parser.add_argument("--reload", action="store_true", help="Auto-reload при изменении кода")
    parser.add_argument("--workers", type=int, default=1, help="Количество воркеров (по умолчанию: 1)")
    
    args = parser.parse_args()
    
    print("=" * 70)
    print("🚀 Pantikur ChatBot - Локальный запуск")
    print("=" * 70)
    print(f"   Хост: {args.host}")
    print(f"   Порт: {args.port}")
    print(f"   Reload: {'вкл' if args.reload else 'выкл'}")
    print(f"   Воркеры: {args.workers}")
    print("=" * 70)
    
    # Устанавливаем переменные окружения
    os.environ["HOST"] = args.host
    os.environ["PORT"] = str(args.port)
    os.environ["PYTHONUNBUFFERED"] = "1"
    os.environ["PYTHONPATH"] = "/app"
    
    # Создаём директории
    os.makedirs("logs", exist_ok=True)
    os.makedirs("data", exist_ok=True)
    
    # Запускаем uvicorn
    import uvicorn
    
    uvicorn.run(
        "main:app",
        host=args.host,
        port=args.port,
        reload=args.reload,
        workers=args.workers,
        log_level="info",
        access_log=True,
    )


if __name__ == "__main__":
    main()
