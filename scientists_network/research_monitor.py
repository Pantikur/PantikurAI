"""
Research Monitor — мониторинг исследований учёных.

Позволяет:
  - Запускать и останавливать ядра (Ханако, Фуюки, Люси, Футаба, Шиори, Нобука, Латислейн, Селеста, Аква)
  - Смотреть процесс исследований в реальном времени
  - Просматривать результаты (теории, вычисления, статьи, улучшения)
  - Получать статистику и метрики каждого ядра
  - Отслеживать коммуникацию между учёными
"""

from __future__ import annotations
import json
import logging
import random
import threading
import time
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional
from queue import Queue, Empty


logger = logging.getLogger("research_monitor")


class ResearchEvent:
    """Событие исследования."""
    
    def __init__(self, event_type: str, scientist: str, message: str, data: Optional[Dict[str, Any]] = None):
        self.event_type = event_type
        self.scientist = scientist
        self.message = message
        self.data = data or {}
        self.timestamp = datetime.now().isoformat()
        self.timestamp_epoch = time.time()
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "event_type": self.event_type,
            "scientist": self.scientist,
            "message": self.message,
            "data": self.data,
            "timestamp": self.timestamp,
        }


class ScientistCoreProxy:
    """
    Прокси-объект для отслеживания состояния ядра учёного.
    Работает как обёртка над настоящим ядром.
    """
    
    def __init__(self, name: str, core_class, config):
        self.name = name
        self.core_class = core_class
        self.config = config
        self.core = None
        self.is_running = False
        self.start_time = None
        self.last_activity = None
        
        # События в реальном времени
        self._event_queue: Queue[ResearchEvent] = Queue(maxsize=500)
        self._all_events: List[ResearchEvent] = []
        self._lock = threading.Lock()
        
        # Метрики — базовый набор
        self.metrics = {
            "cycles_completed": 0,
            "theories_built": 0,
            "calculations_run": 0,
            "papers_studied": 0,
            "web_searches": 0,
            "secrets_found": 0,
        }
        
        # Логи
        self._log_buffer: List[str] = []
        self._max_log_lines = 200
        
        # Специфичные данные для разных типов ядер
        self._theories: List[Any] = []
        self._calculations: List[Any] = []
        self._papers: List[Any] = []
        self._history: List[Any] = []
    
    def start(self):
        """Запустить ядро."""
        if self.is_running:
            logger.warning(f"Ядро {self.name} уже запущено")
            return
        
        logger.info(f"🚀 Запуск ядра: {self.name}")
        self.core = self.core_class(self.config)
        self.is_running = True
        self.start_time = datetime.now()
        self.last_activity = datetime.now()
        
        # Перехват логов
        self._setup_log_capture()
        
        # Запуск в отдельном потоке
        self._thread = threading.Thread(target=self._run_core, daemon=True)
        self._thread.start()
        
        self._emit_event("STARTED", f"Ядро {self.name} запущено")
    
    def stop(self):
        """Остановить ядро."""
        if not self.is_running:
            return
        
        logger.info(f"🛑 Остановка ядра: {self.name}")
        self.is_running = False
        self._emit_event("STOPPED", f"Ядро {self.name} остановлено")
    
    def _run_core(self):
        """Запуск ядра в потоке с перехватом событий."""
        try:
            if self.core and hasattr(self.core, 'config'):
                self.core.config.max_cycles = 0  # Бесконечный цикл
            
            # Перехват методов ядра
            if self.core and hasattr(self.core, '_cycle'):
                original_cycle = self.core._cycle
                def wrapped_cycle():
                    # Обработка входящих сообщений перед циклом
                    try:
                        monitor = get_research_monitor()
                        monitor.network.process_incoming_messages(self.name, max_messages=3)
                    except Exception:
                        pass
                    
                    # Автоматическая болтовня (10% шанс)
                    if random.random() < 0.10:
                        try:
                            monitor = get_research_monitor()
                            monitor.network.auto_chat_cycle()
                        except Exception:
                            pass
                    
                    original_cycle()
                    self.metrics["cycles_completed"] += 1
                    self._update_metrics_from_core()
                    self.last_activity = datetime.now()
                self.core._cycle = wrapped_cycle
            
            # Запуск
            if self.core and hasattr(self.core, 'run'):
                self.core.run()
            
            self._emit_event("COMPLETED", f"Ядро {self.name} завершило работу")
            
        except KeyboardInterrupt:
            self._emit_event("INTERRUPTED", f"Ядро {self.name} прервано")
        except Exception as e:
            self._emit_event("ERROR", f"Ошибка ядра {self.name}: {e}")
            logger.error(f"❌ Ошибка ядра {self.name}: {e}", exc_info=True)
        finally:
            self.is_running = False
            self._emit_event("STOPPED", f"Ядро {self.name} остановлено")
    
    def _update_metrics_from_core(self):
        """Обновить метрики из реального ядра."""
        try:
            if not self.core:
                return
            status = self.core.get_status()
            metrics = status.get("metrics", {})
            self.metrics["theories_built"] = metrics.get("theories_built", 0)
            self.metrics["calculations_run"] = metrics.get("calculations_run", 0)
            self.metrics["papers_studied"] = metrics.get("papers_studied", 0)
            self.metrics["web_searches"] = metrics.get("web_searches", 0)
            
            # Специфичные метрики для разных ядер
            if "lightning_secrets_found" in metrics:
                self.metrics["secrets_found"] = metrics["lightning_secrets_found"]
            elif "gravity_secrets_found" in metrics:
                self.metrics["secrets_found"] = metrics["gravity_secrets_found"]
            elif "consciousness_models_created" in metrics:
                self.metrics["consciousness_models"] = metrics["consciousness_models_created"]
                self.metrics["embodiments_created"] = metrics.get("embodiments_created", 0)
                self.metrics["successful_transfers"] = metrics.get("successful_transfers", 0)
                self.metrics["failed_transfers"] = metrics.get("failed_transfers", 0)
        except Exception:
            pass
    
    def _setup_log_capture(self):
        """Настроить перехват логов."""
        # Создаём специальный handler для перехвата
        class EventCaptureHandler(logging.Handler):
            def __init__(self, proxy: ScientistCoreProxy):
                super().__init__()
                self.proxy = proxy
            
            def emit(self, record):
                msg = self.format(record)
                self.proxy._add_log_entry(msg)
                
                # Определяем тип события по сообщению
                level = record.levelname
                text = record.getMessage().lower()
                
                if "ЦИКЛ ИССЛЕДОВАНИЙ" in record.getMessage():
                    self.proxy._emit_event("CYCLE", f"Начало цикла")
                elif "теория" in text and ("построена" in text or "построен" in text):
                    self.proxy._emit_event("THEORY", f"Построена новая теория")
                elif "вычисление" in text or "вычислен" in text:
                    self.proxy._emit_event("CALCULATION", f"Выполнено вычисление")
                elif "статей" in text or "papers" in text:
                    self.proxy._emit_event("PAPERS", f"Найдены новые статьи")
                elif "молнии" in text or "lightning" in text:
                    self.proxy._emit_event("DISCOVERY", f"Обнаружены секреты молний")
                elif "гравит" in text:
                    self.proxy._emit_event("DISCOVERY", f"Обнаружены секреты гравитации")
        
        handler = EventCaptureHandler(self)
        handler.setFormatter(logging.Formatter("%(levelname)s: %(message)s"))
        
        # Добавляем ко всем логгерам, связанным с ядром
        logger_names = [
            f"{self.name}Core", 
            f"{self.name}Core.", 
            f"{self.name.lower()}core",
            f"{self.name.lower()}Core",
        ]
        for name in logger_names:
            log = logging.getLogger(name)
            log.addHandler(handler)
            log.setLevel(logging.INFO)
    
    def _add_log_entry(self, message: str):
        """Добавить запись в буфер логов."""
        with self._lock:
            self._log_buffer.append(message)
            if len(self._log_buffer) > self._max_log_lines:
                self._log_buffer = self._log_buffer[-self._max_log_lines:]
    
    def _emit_event(self, event_type: str, message: str, data: Optional[Dict[str, Any]] = None):
        """Добавить событие в очередь."""
        event = ResearchEvent(event_type, self.name, message, data)
        try:
            self._event_queue.put_nowait(event)
        except Exception:
            pass  # Очередь переполнена, игнорируем
        
        with self._lock:
            self._all_events.append(event)
            # Храним последние 1000 событий
            if len(self._all_events) > 1000:
                self._all_events = self._all_events[-1000:]
    
    def get_events(self, limit: int = 50, event_type: Optional[str] = None) -> List[Dict[str, Any]]:
        """Получить события из очереди."""
        events = []
        while not self._event_queue.empty():
            try:
                event = self._event_queue.get_nowait()
                if event_type is None or event.event_type == event_type:
                    events.append(event.to_dict())
            except Empty:
                break
        
        return events
    
    def get_all_events(self, limit: int = 100, event_type: Optional[str] = None) -> List[Dict[str, Any]]:
        """Получить все сохранённые события."""
        with self._lock:
            events = self._all_events[-limit:]
        
        if event_type:
            events = [e for e in events if e.event_type == event_type]
        
        return [e.to_dict() for e in events]
    
    def get_logs(self, limit: int = 100) -> List[str]:
        """Получить последние записи логов."""
        with self._lock:
            return self._log_buffer[-limit:]
    
    def get_status(self) -> Dict[str, Any]:
        """Получить статус ядра."""
        status = {
            "name": self.name,
            "is_running": self.is_running,
            "start_time": self.start_time.isoformat() if self.start_time else None,
            "last_activity": self.last_activity.isoformat() if self.last_activity else None,
            "uptime_seconds": (datetime.now() - self.start_time).total_seconds() if self.start_time else 0,
            "metrics": self.metrics.copy(),
            "events_count": len(self._all_events),
            "logs_count": len(self._log_buffer),
        }
        
        # Добавляем детали из ядра
        if self.core and hasattr(self.core, 'get_status'):
            try:
                core_status = self.core.get_status()
                status.update(core_status)
            except Exception:
                pass
        
        return status
    
    def get_theories(self, limit: int = 20) -> List[Dict[str, Any]]:
        """Получить последние теории."""
        if not self.core or not hasattr(self.core, 'theories'):
            return []
        
        theories = self.core.theories[-limit:]
        result = []
        for t in theories:
            try:
                if hasattr(t, 'to_dict'):
                    result.append(t.to_dict())
                else:
                    result.append(vars(t))
            except Exception:
                pass
        
        return result
    
    def get_consciousness_models(self, limit: int = 20) -> List[Dict[str, Any]]:
        """Получить последние модели сознания (Юи)."""
        if not self.core or not hasattr(self.core, 'consciousness_models'):
            return []
        
        models = self.core.consciousness_models[-limit:]
        result = []
        for m in models:
            try:
                if hasattr(m, 'to_dict'):
                    result.append(m.to_dict())
                else:
                    result.append(vars(m))
            except Exception:
                pass
        
        return result
    
    def get_embodiments(self, limit: int = 20) -> List[Dict[str, Any]]:
        """Получить последние цифровые воплощения (Юи)."""
        if not self.core or not hasattr(self.core, 'digital_embodiments'):
            return []
        
        embodiments = self.core.digital_embodiments[-limit:]
        result = []
        for e in embodiments:
            try:
                if hasattr(e, 'to_dict'):
                    result.append(e.to_dict())
                else:
                    result.append(vars(e))
            except Exception:
                pass
        
        return result
    
    def get_transfer_records(self, limit: int = 20) -> List[Dict[str, Any]]:
        """Получить последние записи о переносах (Юи)."""
        if not self.core or not hasattr(self.core, 'transfer_records'):
            return []
        
        records = self.core.transfer_records[-limit:]
        return [r.to_dict() for r in records]
    
    def get_calculations(self, limit: int = 20) -> List[Dict[str, Any]]:
        """Получить последние вычисления."""
        if not self.core or not hasattr(self.core, 'calculations'):
            return []
        
        calculations = self.core.calculations[-limit:]
        result = []
        for c in calculations:
            try:
                if hasattr(c, 'to_dict'):
                    result.append(c.to_dict())
                else:
                    result.append(vars(c))
            except Exception:
                result.append({"error": "Не удалось получить данные вычисления"})
        
        return result
    
    def get_papers(self, limit: int = 20) -> List[Dict[str, Any]]:
        """Получить последние статьи."""
        if not self.core or not hasattr(self.core, 'papers'):
            return []
        
        papers = self.core.papers[-limit:]
        result = []
        for p in papers:
            try:
                if hasattr(p, 'to_dict'):
                    result.append(p.to_dict())
                else:
                    result.append(vars(p))
            except Exception:
                result.append({"error": "Не удалось получить данные статьи"})
        
        return result
    
    def get_research_history(self, limit: int = 50) -> List[Dict[str, Any]]:
        """Получить историю исследований."""
        if not self.core or not hasattr(self.core, 'research_history'):
            return []
        
        history = self.core.research_history[-limit:]
        result = []
        for h in history:
            try:
                if hasattr(h, 'to_dict'):
                    result.append(h.to_dict())
                else:
                    result.append(vars(h))
            except Exception:
                result.append({"error": "Не удалось получить данные истории"})
        
        return result
    
    def get_improvements(self, limit: int = 20) -> List[Dict[str, Any]]:
        """Получить последние улучшения (для Nobuka)."""
        if not self.core or not hasattr(self.core, 'improvements_history'):
            return []
        
        improvements = self.core.improvements_history[-limit:]
        result = []
        for imp in improvements:
            try:
                if hasattr(imp, 'to_dict'):
                    result.append(imp.to_dict())
                else:
                    result.append(vars(imp))
            except Exception:
                result.append({"error": "Не удалось получить данные улучшения"})
        
        return result
    
    def get_threats(self, limit: int = 20) -> List[Dict[str, Any]]:
        """Получить последние угрозы (для Shiori)."""
        if not self.core or not hasattr(self.core, 'threats_history'):
            return []
        
        threats = self.core.threats_history[-limit:]
        result = []
        for t in threats:
            try:
                if hasattr(t, 'to_dict'):
                    result.append(t.to_dict())
                else:
                    result.append(vars(t))
            except Exception:
                result.append({"error": "Не удалось получить данные угрозы"})
        
        return result
    
    def get_incidents(self, limit: int = 20) -> List[Dict[str, Any]]:
        """Получить последние инциденты (для Shiori)."""
        if not self.core or not hasattr(self.core, 'incidents_history'):
            return []
        
        incidents = self.core.incidents_history[-limit:]
        result = []
        for inc in incidents:
            try:
                if hasattr(inc, 'to_dict'):
                    result.append(inc.to_dict())
                else:
                    result.append(vars(inc))
            except Exception:
                result.append({"error": "Не удалось получить данные инцидента"})
        
        return result
    
    def get_changes(self, limit: int = 20) -> List[Dict[str, Any]]:
        """Получить последние изменения (для Futaba)."""
        if not self.core or not hasattr(self.core, 'changes_history'):
            return []
        
        changes = self.core.changes_history[-limit:]
        result = []
        for c in changes:
            try:
                if hasattr(c, 'to_dict'):
                    result.append(c.to_dict())
                else:
                    result.append(vars(c))
            except Exception:
                result.append({"error": "Не удалось получить данные изменения"})
        
        return result
    
    def get_intimacy_data(self) -> Dict[str, Any]:
        """Получить данные интимных исследований (для Celesta)."""
        if not self.core or not hasattr(self.core, 'get_intimacy_report'):
            return {}
        
        try:
            report = self.core.get_intimacy_report()
            return report
        except Exception:
            return {}


class ResearchMonitor:
    """
    Менеджер мониторинга исследований учёных.
    
    Управляет:
    - Ханако (гравитация)
    - Фуюки (электричество)
    - Люси (двигатели)
    - Футаба (автономное саморазвитие)
    - Шиори (иммунная система / безопасность)
    - Нобука (улучшения проекта)
    - Латислейн (изучение тела и проектирование)
    - Селеста (изучение интимной жизни и физиологии)
    - Аква (математика, физика, аэродинамика, сопротивление материалов)
    
    Все учёные подключены к Scientists Network и могут:
    - Обмениваться сообщениями
    - Передавать данные (теории, вычисления, проекты)
    - Координировать совместную работу
    - Болтать когда "скучно"
    """
    
    def __init__(self):
        self.logger = logging.getLogger("ResearchMonitor")
        
        # Прокси ядра
        self.cores: Dict[str, ScientistCoreProxy] = {}
        
        # Состояние
        self._initialized = False
        self._lock = threading.Lock()
        
        # Инициализация сети учёных
        from scientists_network.network import get_network
        self.network = get_network(str(Path(".")))
        self.logger.info("🌐 Scientists Network подключена")
        
        self.logger.info("🔬 ResearchMonitor инициализирован")
    
    def initialize(self):
        """Инициализировать все ядра."""
        if self._initialized:
            return
        
        self.logger.info("🔬 Инициализация всех ядер...")
        
        try:
            from hanako.engine.config import HanakoConfig
            from hanako.engine.hanako_core import HanakoCore
            hanako_config = HanakoConfig.demo()
            hanako_config.web_search_interval = 1  # Чаще для демо
            self.cores["hanako"] = ScientistCoreProxy("Hanako", HanakoCore, hanako_config)
            self.logger.info("✅ Ядро Ханако (гравитация) готово")
        except Exception as e:
            self.logger.warning(f"⚠️ Ядро Ханако не загружено: {e}")
        
        try:
            from fuyuki.engine.config import FuyukiConfig
            from fuyuki.engine.fuyuki_core import FuyukiCore
            fuyuki_config = FuyukiConfig.demo()
            fuyuki_config.web_search_interval = 1  # Чаще для демо
            self.cores["fuyuki"] = ScientistCoreProxy("Fuyuki", FuyukiCore, fuyuki_config)
            self.logger.info("✅ Ядро Фуюки (электричество) готово")
        except Exception as e:
            self.logger.warning(f"⚠️ Ядро Фуюки не загружено: {e}")
        
        try:
            from lucy.engine.config import LucyConfig
            from lucy.engine.lucy_core import LucyCore
            lucy_config = LucyConfig.demo()
            lucy_config.web_search_interval = 1  # Чаще для демо
            self.cores["lucy"] = ScientistCoreProxy("Lucy", LucyCore, lucy_config)
            self.logger.info("✅ Ядро Люси (двигатели) готово")
        except Exception as e:
            self.logger.warning(f"⚠️ Ядро Люси не загружено: {e}")
        
        try:
            from futaba.engine.config import FutabaConfig
            from futaba.engine.futaba_core import FutabaCore
            futaba_config = FutabaConfig.demo()
            self.cores["futaba"] = ScientistCoreProxy("Futaba", FutabaCore, futaba_config)
            self.logger.info("✅ Ядро Футаба (саморазвитие) готово")
        except Exception as e:
            self.logger.warning(f"⚠️ Ядро Футаба не загружено: {e}")
        
        try:
            from shiori.engine.config import ShioriConfig
            from shiori.engine.shiori_core import ShioriCore
            shiori_config = ShioriConfig.demo()
            self.cores["shiori"] = ScientistCoreProxy("Shiori", ShioriCore, shiori_config)
            self.logger.info("✅ Ядро Шиори (безопасность) готово")
        except Exception as e:
            self.logger.warning(f"⚠️ Ядро Шиори не загружено: {e}")
        
        try:
            from nobuka.engine.config import NobukaConfig
            from nobuka.engine.nobuka_core import NobukaCore
            nobuka_config = NobukaConfig.demo()
            self.cores["nobuka"] = ScientistCoreProxy("Nobuka", NobukaCore, nobuka_config)
            self.logger.info("✅ Ядро Нобука (улучшения) готово")
        except Exception as e:
            self.logger.warning(f"⚠️ Ядро Нобука не загружено: {e}")
        
        try:
            from latislane import LatislaneCore
            latislane_config = "."  # Latislane использует project_root как строку
            self.cores["latislane"] = ScientistCoreProxy("Latislane", LatislaneCore, latislane_config)
            self.logger.info("✅ Ядро Латислейн (тело) готово")
        except Exception as e:
            self.logger.warning(f"⚠️ Ядро Латислейн не загружено: {e}")
        
        try:
            from celesta import CelestaCore
            celesta_config = str(Path("."))  # Celesta использует project_root как строку
            self.cores["celest"] = ScientistCoreProxy("Celesta", CelestaCore, celesta_config)
            self.logger.info("✅ Ядро Селеста (интимная жизнь) готово")
        except Exception as e:
            self.logger.warning(f"⚠️ Ядро Селеста не загружено: {e}")
        
        try:
            from akva.engine.config import AkvaConfig
            from akva.engine.akva_core import AkvaCore
            akva_config = AkvaConfig.demo()
            akva_config.web_search_interval = 10  # Интернет для Аквы
            self.cores["akva"] = ScientistCoreProxy("Akva", AkvaCore, akva_config)
            self.logger.info("✅ Ядро Аква (математика, физика) — с интернетом")
        except Exception as e:
            self.logger.warning(f"⚠️ Ядро Аква не загружено: {e}")
        
        try:
            from yu.engine.config import YuConfig
            from yu.engine.yu_core import YuCore
            yu_config = YuConfig.demo()
            self.cores["yu"] = ScientistCoreProxy("Yu", YuCore, yu_config)
            self.logger.info("✅ Ядро Юи (сознание, перенос) — с интернетом")
        except Exception as e:
            self.logger.warning(f"⚠️ Ядро Юи не загружено: {e}")
        
        try:
            from naoto.engine.config import NaotoConfig
            from naoto.engine import Naoto
            naoto_config = NaotoConfig()
            naoto_core = Naoto(naoto_config)
            self.cores["naoto"] = ScientistCoreProxy("Naoto", Naoto, naoto_config)
            self.logger.info("✅ Ядро Наото (визуальный архитектор) — с интернетом")
        except Exception as e:
            self.logger.warning(f"⚠️ Ядро Наото не загружено: {e}")
        
        try:
            from ayiko.engine import Ayiko
            from ayiko.engine.config import AyikoConfig
            ayiko_config = AyikoConfig()
            ayiko_core = Ayiko(ayiko_config)
            self.cores["ayiko"] = ScientistCoreProxy("Ayiko", Ayiko, ayiko_config)
            self.logger.info("✅ Ядро Айко (чтение книг, обучение модели) — с интернетом")
        except Exception as e:
            self.logger.warning(f"⚠️ Ядро Айко не загружено: {e}")
        
        self._initialized = True
        self.logger.info(f"📊 Инициализировано ядер: {len(self.cores)}")
    
    def get_core(self, scientist_name: str) -> Optional[ScientistCoreProxy]:
        """Получить прокси ядра по имени."""
        return self.cores.get(scientist_name.lower())
    
    def start_research(self, scientist_name: str) -> Dict[str, Any]:
        """Запустить исследования указанного ядра."""
        core = self.get_core(scientist_name)
        if not core:
            return {"status": "error", "detail": f"Ядро '{scientist_name}' не найдено"}
        
        if core.is_running:
            return {"status": "error", "detail": f"Ядро '{scientist_name}' уже запущено"}
        
        core.start()
        
        # Регистрируем в сети учёных
        try:
            self.network.register_scientist(scientist_name, core.core)
            self.logger.info(f"🌐 {scientist_name} подключена к Scientists Network")
        except Exception as e:
            self.logger.warning(f"⚠️ Не удалось подключить {scientist_name} к сети: {e}")
        
        self.logger.info(f"🚀 Запуск ядра: {scientist_name}")
        
        return {
            "status": "ok",
            "message": f"Исследования ядра {scientist_name} запущены",
            "scientist": scientist_name,
        }
    
    def stop_research(self, scientist_name: str) -> Dict[str, Any]:
        """Остановить исследования ядра."""
        core = self.get_core(scientist_name)
        if not core:
            return {"status": "error", "detail": f"Ядро '{scientist_name}' не найдено"}
        
        if not core.is_running:
            return {"status": "error", "detail": f"Ядро '{scientist_name}' не запущено"}
        
        core.stop()
        return {
            "status": "ok",
            "message": f"Исследования ядра {scientist_name} остановлены",
            "scientist": scientist_name,
        }
    
    def get_all_status(self) -> Dict[str, Any]:
        """Получить статус всех ядер."""
        result = {
            "total_cores": len(self.cores),
            "running_count": sum(1 for c in self.cores.values() if c.is_running),
            "cores": {}
        }
        
        for name, core in self.cores.items():
            result["cores"][name] = core.get_status()
        
        return result
    
    def get_research_summary(self, scientist_name: str) -> Optional[Dict[str, Any]]:
        """Получить полную сводку по исследованиям ядра."""
        core = self.get_core(scientist_name)
        if not core:
            return None
        
        # Специфичные данные для разных ядер
        theories = []
        calculations = []
        papers = []
        history = []
        improvements = []
        threats = []
        incidents = []
        changes = []
        intimacy_data = {}
        consciousness_models = []
        embodiments = []
        transfers = []
        
        if scientist_name.lower() == 'lucy':
            theories = core.get_theories(limit=10)
            calculations = core.get_calculations(limit=10)
            papers = core.get_papers(limit=10)
            history = core.get_research_history(limit=20)
        elif scientist_name.lower() == 'nobuka':
            improvements = core.get_improvements(limit=10)
            papers = core.get_papers(limit=10)
            history = core.get_research_history(limit=20)
        elif scientist_name.lower() == 'shiori':
            threats = core.get_threats(limit=10)
            incidents = core.get_incidents(limit=10)
            history = core.get_research_history(limit=20)
        elif scientist_name.lower() == 'futaba':
            changes = core.get_changes(limit=10)
            history = core.get_research_history(limit=20)
        elif scientist_name.lower() == 'celest':
            intimacy_data = core.get_intimacy_data()
            history = core.get_research_history(limit=20)
        elif scientist_name.lower() == 'yu':
            consciousness_models = core.get_consciousness_models(limit=10)
            embodiments = core.get_embodiments(limit=10)
            transfers = core.get_transfer_records(limit=10)
            history = core.get_research_history(limit=20)
        else:
            # Ханако, Фуюки
            theories = core.get_theories(limit=10)
            calculations = core.get_calculations(limit=10)
            papers = core.get_papers(limit=10)
            history = core.get_research_history(limit=20)
        
        return {
            "status": core.get_status(),
            "events": core.get_all_events(limit=50),
            "logs": core.get_logs(limit=50),
            "theories": theories,
            "calculations": calculations,
            "papers": papers,
            "research_history": history,
            "improvements": improvements,
            "threats": threats,
            "incidents": incidents,
            "changes": changes,
            "intimacy_data": intimacy_data if scientist_name.lower() == 'celest' else None,
            "consciousness_models": consciousness_models if scientist_name.lower() == 'yu' else None,
            "embodiments": embodiments if scientist_name.lower() == 'yu' else None,
            "transfer_records": transfers if scientist_name.lower() == 'yu' else None,
        }


# ========== Глобальный экземпляр ==========
RESEARCH_MONITOR: Optional[ResearchMonitor] = None


def get_research_monitor() -> ResearchMonitor:
    """Получить глобальный экземпляр ResearchMonitor."""
    global RESEARCH_MONITOR
    if RESEARCH_MONITOR is None:
        RESEARCH_MONITOR = ResearchMonitor()
    return RESEARCH_MONITOR
