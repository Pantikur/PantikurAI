# auto_retrain.py — автоматический ретраин при изменении данных
import time
import subprocess
import os
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

DATA_DIR = "data"
MODEL_PATH = "models/qwen2.5-3b"

# Файлы, за которыми следим
WATCHED_FILES = ["conversations.json", "training_pairs.jsonl"]


class RetrainHandler(FileSystemEventHandler):
    def on_modified(self, event):
        if event.is_directory:
            return

        filename = os.path.basename(event.src_path)
        if filename in WATCHED_FILES:
            print(f"\n🔥 Изменён файл: {filename}")
            print("🔄 Запускаем ретраин...")

            try:
                result = subprocess.run(
                    ["python", "retrain.py"],
                    check=True,
                    capture_output=True,
                    text=True
                )
                print("✅ Ретраин успешно завершён")
                print(result.stdout)
            except subprocess.CalledProcessError as e:
                print("❌ Ошибка при ретраине")
                print(e.stderr)
            except Exception as e:
                print(f"⚠️ Неизвестная ошибка: {e}")


def start_watching():
    print(f"👀 Слежение за папкой: {DATA_DIR}")
    print("💡 Измените conversations.json или training_pairs.jsonl — начнётся обучение")

    event_handler = RetrainHandler()
    observer = Observer()
    observer.schedule(event_handler, path=DATA_DIR, recursive=False)
    observer.start()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
        print("\n🛑 Слежение остановлено")

    observer.join()


if __name__ == "__main__":
    start_watching()