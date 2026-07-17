"""
Wuglarst Daemon — Демон для постоянной работы сервера.

Создаёт фоновый процесс, который:
- Перезапускает сервер при падении
- Ведёт логи
- Автозапускается при старте Windows
- Мониторит здоровье сервера
"""

import asyncio
import json
import logging
import os
import signal
import subprocess
import sys
import time
import threading
from datetime import datetime
from pathlib import Path

# =====================================================================
#  НАСТРОЙКИ
# =====================================================================

PROJECT_ROOT = Path(__file__).parent.parent
SERVER_SCRIPT = Path(__file__).parent / "server_autonomous.py"
PID_FILE = Path(__file__).parent / "server.pid"
LOG_DIR = PROJECT_ROOT / "logs"
LOG_DIR.mkdir(parents=True, exist_ok=True)
DAEMON_LOG = LOG_DIR / "daemon.log"

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
    handlers=[
        logging.FileHandler(DAEMON_LOG, encoding="utf-8"),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger("Daemon")

# =====================================================================
#  КЛАСС ДЕМОНА
# =====================================================================

class WuglarstDaemon:
    """Демон для постоянной работы Wuglarst."""
    
    def __init__(self):
        self.process = None
        self.running = False
        self.restart_count = 0
        self.max_restarts = 100  # Практически бесконечно
        self.restart_delay = 5  # Секунд между перезапусками
        self.health_check_interval = 30  # Секунд
        
        # Настройки
        self.host = os.getenv("WUGLARST_HOST", "0.0.0.0")
        self.port = int(os.getenv("WUGLARST_PORT", "8001"))
        
        logger.info("=" * 60)
        logger.info("🚀 Wuglarst Daemon инициализирован")
        logger.info(f"📍 Порт: {self.port}")
        logger.info(f"📁 Сервер: {SERVER_SCRIPT}")
        logger.info("=" * 60)
    
    def start(self):
        """Запуск демона."""
        logger.info("▶️ Запуск демона...")
        self.running = True
        
        # Запуск мониторинга в отдельном потоке
        monitor_thread = threading.Thread(target=self._monitor_loop, daemon=True)
        monitor_thread.start()
        
        # Запуск сервера
        self._start_server()
        
        logger.info("✅ Демон запущен")
    
    def stop(self):
        """Остановка демона."""
        logger.info("⏹️ Остановка демона...")
        self.running = False
        
        if self.process:
            self.process.terminate()
            try:
                self.process.wait(timeout=10)
            except:
                self.process.kill()
        
        # Удаление PID файла
        if PID_FILE.exists():
            PID_FILE.unlink()
        
        logger.info("✅ Демон остановлен")
    
    def _start_server(self):
        """Запуск серверного процесса."""
        if self.process:
            self.process.wait()
        
        self.restart_count += 1
        logger.info(f"🔄 Запуск сервера (попытка #{self.restart_count})...")
        
        # Запись PID
        pid_file_content = {
            "pid": None,
            "start_time": datetime.now().isoformat(),
            "restart_count": self.restart_count
        }
        
        try:
            # Запуск сервера
            self.process = subprocess.Popen(
                [sys.executable, str(SERVER_SCRIPT)],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                cwd=str(SERVER_SCRIPT.parent)
            )
            
            pid_file_content["pid"] = self.process.pid
            
            with open(PID_FILE, 'w', encoding='utf-8') as f:
                json.dump(pid_file_content, f, indent=2)
            
            logger.info(f"✅ Сервер запущен (PID: {self.process.pid})")
            
        except Exception as e:
            logger.error(f"❌ Ошибка запуска сервера: {e}")
    
    def _monitor_loop(self):
        """Цикл мониторинга."""
        logger.info("👁️ Мониторинг запущен")
        
        while self.running:
            try:
                # Проверка процесса
                if self.process:
                    poll = self.process.poll()
                    if poll is not None:
                        logger.warning(f"⚠️ Процесс завершён с кодом {poll}")
                        self.process = None
                        
                        if self.running and self.restart_count < self.max_restarts:
                            time.sleep(self.restart_delay)
                            self._start_server()
                
                # Проверка здоровья через API
                self._check_health()
                
                time.sleep(self.health_check_interval)
                
            except Exception as e:
                logger.error(f"Ошибка мониторинга: {e}")
                time.sleep(10)
    
    def _check_health(self):
        """Проверка здоровья сервера."""
        try:
            import urllib.request
            url = f"http://localhost:{self.port}/health"
            req = urllib.request.Request(url, method='GET')
            
            with urllib.request.urlopen(req, timeout=5) as response:
                data = json.loads(response.read().decode())
                
                if data.get("status") == "healthy":
                    scientists = data.get("scientists", 0)
                    online = data.get("online", 0)
                    logger.info(f"🏥 Здоровье: OK | Девочек: {scientists}/{online} онлайн")
                else:
                    logger.warning("⚠️ Сервер не здоров")
                    
        except Exception as e:
            logger.warning(f"⚠️ Проверка здоровья не удалась: {e}")
    
    def get_status(self) -> dict:
        """Получить статус демона."""
        return {
            "running": self.running,
            "restart_count": self.restart_count,
            "process_pid": self.process.pid if self.process else None,
            "process_alive": self.process.poll() is None if self.process else False
        }


# =====================================================================
#  УПРАВЛЕНИЕ
# =====================================================================

daemon = WuglarstDaemon()


def handle_signal(signum, frame):
    """Обработчик сигналов."""
    logger.info(f"Получен сигнал {signum}, остановка...")
    daemon.stop()
    sys.exit(0)


# =====================================================================
#  СЛУЖБА WINDOWS
# =====================================================================

def install_service():
    """Установка как служба Windows."""
    try:
        import win32serviceutil  # type: ignore
        import win32service  # type: ignore
        import win32event  # type: ignore
    except ImportError:
        logger.warning("⚠️ pywin32 не установлен")
        logger.info("💡 Установите: pip install pywin32")
        return
    
    try:
        class WuglarstService(win32serviceutil.ServiceFramework):
            _svc_name_ = "Wuglarst"
            _svc_display_name_ = "Wuglarst Autonomous Server"
            _svc_description_ = "Автономный сервер для 13 ИИ-учёных PantikurAI"
            
            def __init__(self, args):
                win32serviceutil.ServiceFramework.__init__(self, args)
                self.stop_event = win32event.CreateEvent(None, 0, 0, None)
                self.daemon = WuglarstDaemon()
            
            def SvcStop(self):
                self.daemon.stop()
                win32event.SetEvent(self.stop_event)
            
            def SvcDoRun(self):
                self.daemon.start()
                win32event.WaitForSingleObject(self.stop_event, win32event.INFINITE)
        
        win32serviceutil.HandleCommandLine(WuglarstService)
    
    except Exception as e:
        logger.error(f"Ошибка установки службы: {e}")



def install_autostart():
    """Установка автозапуска при старте Windows."""
    try:
        import winreg  # type: ignore  # Python 3.x
    except ImportError:
        try:
            import _winreg  # type: ignore  # Python 2.x (устаревший)
        except ImportError:
            logger.warning("⚠️ Модуль winreg недоступен (не Windows)")
            logger.info("💡 Установите pywin32: pip install pywin32")
            return
    
    startup_path = Path(
        os.environ["APPDATA"],
        "Microsoft",
        "Windows",
        "Start Menu",
        "Programs",
        "Startup"
    )
    
    shortcut_path = startup_path / "Wuglarst.lnk"
    
    # Создаём BAT файл
    bat_path = startup_path / "Wuglarst_start.bat"
    bat_content = f"""@echo off
cd /d "{Path(__file__).parent}"
start /B python server_autonomous.py
exit
"""
    
    with open(bat_path, 'w', encoding='utf-8') as f:
        f.write(bat_content)
    
    logger.info(f"✅ Автозапуск установлен: {bat_path}")
    logger.info("📌 Создан файл: Wuglarst_start.bat")
    logger.info("📍 Путь: " + str(startup_path))


def uninstall_autostart():
    """Удаление автозапуска."""
    try:
        import winreg  # type: ignore  # Python 3.x
    except ImportError:
        try:
            import _winreg  # type: ignore  # Python 2.x
        except ImportError:
            logger.info("ℹ️ Не Windows — автозапуск не нужен")
            return
    
    startup_path = Path(
        os.environ["APPDATA"],
        "Microsoft",
        "Windows",
        "Start Menu",
        "Programs",
        "Startup"
    )
    
    bat_path = startup_path / "Wuglarst_start.bat"
    
    if bat_path.exists():
        bat_path.unlink()
        logger.info("❌ Автозапуск удалён")
    else:
        logger.info("ℹ️ Автозапуск не найден")


# =====================================================================
#  CLI
# =====================================================================

def main():
    """Главная функция CLI."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Wuglarst Daemon Manager")
    parser.add_argument("command", choices=["start", "stop", "restart", "status", "install", "uninstall", "service"],
                       help="Команда")
    parser.add_argument("--foreground", action="store_true",
                       help="Запуск в foreground (не как демон)")
    
    args = parser.parse_args()
    
    if args.command == "start":
        daemon.start()
        
        if not args.foreground:
            # Запуск в фоне
            logger.info("🚀 Запуск в фоновом режиме...")
            
            # Перезапуск себя в фоне
            subprocess.Popen(
                [sys.executable, __file__, "start", "--foreground"],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )
            
            logger.info("✅ Запущено в фоне")
            sys.exit(0)
        else:
            # Foreground режим
            signal.signal(signal.SIGINT, handle_signal)
            signal.signal(signal.SIGTERM, handle_signal)
            
            try:
                while True:
                    time.sleep(1)
            except KeyboardInterrupt:
                daemon.stop()
    
    elif args.command == "stop":
        # Остановка через PID файл
        if PID_FILE.exists():
            with open(PID_FILE, 'r') as f:
                pid_data = json.load(f)
                pid = pid_data.get("pid")
                
                if pid:
                    try:
                        os.kill(pid, signal.SIGTERM)
                        logger.info(f"✅ Процесс {pid} остановлен")
                    except ProcessLookupError:
                        logger.error("❌ Процесс не найден")
                    except Exception as e:
                        logger.error(f"❌ Ошибка: {e}")
        else:
            logger.error("❌ PID файл не найден")
    
    elif args.command == "restart":
        daemon.stop()
        time.sleep(2)
        daemon.start()
    
    elif args.command == "status":
        status = daemon.get_status()
        print(f"\nСтатус Wuglarst Daemon:")
        print(f"  Работает: {status['running']}")
        print(f"  PID процесса: {status['process_pid']}")
        print(f"  Процесс жив: {status['process_alive']}")
        print(f"  Перезапусков: {status['restart_count']}")
        
        # Попытка получить статус сервера
        try:
            import urllib.request
            with urllib.request.urlopen("http://localhost:8001/health", timeout=5) as response:
                health = json.loads(response.read().decode())
                print(f"\nСтатус сервера:")
                print(f"  Статус: {health.get('status')}")
                print(f"  Девочек: {health.get('scientists', 0)}")
                print(f"  Онлайн: {health.get('online', 0)}")
        except:
            print(f"\n⚠️ Сервер недоступен")
    
    elif args.command == "install":
        install_autostart()
        logger.info("✅ Автозапуск установлен")
        logger.info("🔄 Перезагрузите компьютер для применения")
    
    elif args.command == "uninstall":
        uninstall_autostart()
    
    elif args.command == "service":
        install_service()


if __name__ == "__main__":
    main()
