"""
Ядро постоянной работы Шиори — автономная иммунная система Вугларста.

Реализует:
  - Бесконечный цикл защиты и саморазвития
  - Сканирование уязвимостей и обнаружение угроз
  - Автоматическое реагирование на инциденты
  - Управление патчами и восстановлением
  - Полное логирование и отчётность
"""

from __future__ import annotations

from scientists_network.character_system import CharacterSystem
import json
import logging
import random
import signal
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Any, Optional

from shiori.engine.config import ShioriConfig
from shiori.engine.models import (
    AutonomyLevel, Constitution, Incident, IncidentType, Law, ScanResult, SecurityState, Threat, ThreatCategory, ThreatLevel
)
from shiori.engine.threat_hunter import ThreatHunter
from shiori.engine.patch_manager import PatchManager
from shiori.engine.web_access import ShioriWebAccess

# Humanity Core — живая душа Шиори
from humanity_core import HumanityLayer


class ShioriCore:
    """
    Автономное ядро Шиори — иммунная система Вугларста.
    
    Работает в бесконечном цикле:
      1. Сканирование уязвимостей
      2. Обнаружение угроз
      3. Оценка и классификация
      4. Реагирование (блокировка, карантин, алерт)
      5. Применение патчей
      6. Логирование и отчётность
      7. Периодически — саморазвитие защиты
    """
    
    def __init__(self, config: Optional[ShioriConfig] = None):
        self.config = config or ShioriConfig.default()
        self.constitution = Constitution(version=self.config.version)
        self.current_version = self.config.version
        
        # Состояние
        self.cycle_count = 0
        self.threats_history: list[Threat] = []
        self.incidents_history: list[Incident] = []
        self.metrics = {
            "scans_completed": 0,
            "threats_detected": 0,
            "threats_mitigated": 0,
            "incidents_created": 0,
            "incidents_resolved": 0,
            "patches_applied": 0,
            "false_positives": 0,
            "system_integrity": 1.0,
        }
        
        # Логирование
        self._setup_logging()
        self.logger = logging.getLogger("ShioriCore")
        
        # Компоненты
        self.threat_hunter = ThreatHunter(self.config)
        self.patch_manager = PatchManager(self.config)
        self.web_access = ShioriWebAccess(self.config)
        
        # Состояние безопасности
        self.security_state = SecurityState(version=self.config.version)
        
        # Сеть для общения с сёстрами
        self.network = None
        try:
            from scientists_network.network import get_network
            self.network = get_network(str(Path(__file__).parent.parent.parent.parent))
            self.logger.info("🔗 Подключена к Scientists Network")
        except Exception:
            self.logger.info("ℹ️ Scientists Network недоступна")
        
        # Сигналы
        self._shutdown_requested = False
        self._setup_signals()
        
        # Инициализация random
        self._init_random()
        
        self.logger.info(f"Шиори {self.current_version} инициализирована")
        self.logger.info(f"Защищает: {self.config.parent_system}")
        self.logger.info(f"Конституция загружена: {len(self.constitution.laws)} законов")
        
        # ================================================================
        #  HUMANITY LAYER — Живая душа Шиори
        # ================================================================
        self.humanity = HumanityLayer("shiori")
        self.humanity.current_cycle = 0
        self.logger.info("🧠 Humanity Layer: АКТИВИРОВАН")
        self.logger.info(f"   🎭 Характер: {self.humanity.name} — безопасность, сухая логика, скрытая забота 🛡️")
    
    # ================================================================
    #  ИНИЦИАЛИЗАЦИЯ
    # ================================================================
    
    def _setup_logging(self):
        """Настроить логирование."""
        self.config.state_dir.mkdir(parents=True, exist_ok=True)
        
        logging.basicConfig(
            level=getattr(logging, self.config.log_level),
            format=self.config.log_format,
            handlers=[
                logging.FileHandler(self.config.log_path, encoding="utf-8"),
                logging.StreamHandler(sys.stdout),
            ]
        )
    
    def _setup_signals(self):
        """Обработчики сигналов для graceful shutdown."""
        def handler(signum, frame):
            self.logger.warning("Получен сигнал остановки")
            self._shutdown_requested = True
        
        signal.signal(signal.SIGINT, handler)
        signal.signal(signal.SIGTERM, handler)
    
    def _init_random(self):
        """Инициализировать генератор случайных чисел."""
        if self.config.enable_deterministic_mode or self.config.random_seed is not None:
            seed = self.config.random_seed or int(time.time())
            random.seed(seed)
            self.logger.info(f"Random seed установлен: {seed}")
    
    # ================================================================
    #  ОСНОВНОЙ ЦИКЛ
    # ================================================================
    
    def run(self):
        """Запустить основной цикл защиты Вугларста."""
        self.logger.info("=" * 60)
        self.logger.info("🛡️ ЗАПУСК ИММУННОЙ СИСТЕМЫ ШИОРИ")
        self.logger.info("=" * 60)
        
        try:
            while not self._should_stop():
                self._cycle()
                
                # Сохранение состояния периодически
                if self.cycle_count % self.config.save_state_every_n_cycles == 0:
                    self._save_state()
                
                # Укрепление характера (периодически)
                if self.total_cycles % 5 == 0:
                    strengthened = self.character.strengthen_strengths()
                    if strengthened > 0:
                        self.logger.info(f"Character strengthened: {strengthened} traits")

                # Эволюция характера (периодически)
                if self.total_cycles % 10 == 0:
                    evolved = self.character.evolve_traits()
                    if evolved:
                        self.logger.info("Character evolved")

                self._save_state()
                
                # Пауза между циклами
                time.sleep(self.config.cycle_interval)
            
            self.logger.info("Цикл завершён")
            
        except Exception as e:
            self.logger.exception(f"Критическая ошибка в цикле: {e}")
            raise
        
        finally:
            self._final_report()
            
        # Укрепление характера (периодически)
        if self.total_cycles % 5 == 0:
            strengthened = self.character.strengthen_strengths()
            if strengthened > 0:
                self.logger.info(f"Character strengthened: {strengthened} traits")

        # Эволюция характера (периодически)
        if self.total_cycles % 10 == 0:
            evolved = self.character.evolve_traits()
            if evolved:
                self.logger.info("Character evolved")

        self._save_state()
    
    def _should_stop(self) -> bool:
        """Проверить условия остановки."""
        if self._shutdown_requested:
            return True
        
        if self.config.max_cycles and self.cycle_count >= self.config.max_cycles:
            self.logger.info(f"Достигнут лимит циклов: {self.config.max_cycles}")
            return True
        
        return False
    
    def _cycle(self):
        """Один цикл защиты."""
        self.cycle_count += 1
        self.logger.debug(f"=== ЦИКЛ ЗАЩИТЫ {self.cycle_count} ===")
        
        # 1. Сканирование уязвимостей
        scan_result = self._scan_system()
        self.metrics["scans_completed"] += 1
        
        # 2. Обнаружение угроз
        threats = self._detect_threats(scan_result)
        self.metrics["threats_detected"] += len(threats)
        
        # 2.5. Поиск улучшений защиты в интернете (периодически)
        if self.cycle_count % 3 == 0:
            self._collect_web_improvements()
        
        # 3. Реагирование на угрозы
        for threat in threats:
            self._respond_to_threat(threat)
        
        # 4. Применение патчей (если нужно)
        if self.config.auto_patch_enabled:
            self._apply_patches()
        
        # 5. Обновление состояния безопасности
        self._update_security_state()
        
        # 6. Периодическое саморазвитие
        if self.cycle_count % 10 == 0:
            self._self_improve()
        
        # ================================================================
        #  HUMANITY CYCLE — Настроение, душа, спонтанность
        # ================================================================
        self.humanity.current_cycle = self.cycle_count
        
        event_type = "routine"
        if self.metrics.get("threats_mitigated", 0) > 0 and self.cycle_count % 3 == 0:
            event_type = "success"
        elif random.random() < 0.1:
            event_type = "failure"
        
        humanity_result = self.humanity.cycle_step(event_type=event_type, context="security_scan")
        
        if humanity_result.get("thought"):
            self.logger.info(f"💭 Шиори думает: {humanity_result['thought']}")
        
        initiative = humanity_result.get("initiative")
        if initiative:
            self._send_spontaneous_message(initiative)
        
        self.logger.info(f"Цикл защиты {self.cycle_count} завершён")
    
    # ================================================================
    #  СКАНИРОВАНИЕ И ОБНАРУЖЕНИЕ
    # ================================================================
    
    def _scan_system(self) -> ScanResult:
        """
        Выполнить сканирование системы Вугларста.
        
        В реальной системе это:
          - Проверка файловых систем
          - Анализ сетевого трафика
          - Мониторинг процессов
          - Проверка целостности кода
        
        Здесь — симуляция для демонстрации.
        """
        start_time = time.time()
        
        # Симуляция сканирования
        systems = ["core", "network", "api", "database", "filesystem"]
        scan_result = ScanResult(
            timestamp=datetime.now().isoformat(),
            systems_scanned=systems,
            scan_duration=time.time() - start_time,
        )
        
        # Симуляция обнаружения уязвимостей
        if random.random() < 0.3:
            scan_result.vulnerabilities_found = [
                f"VULN-{random.randint(1000, 9999)}"
                for _ in range(random.randint(1, 3))
            ]
        
        # Симуляция аномалий
        if random.random() < 0.2:
            scan_result.anomalies_detected = [
                f"ANOMALY-{random.randint(100, 999)}"
                for _ in range(random.randint(1, 2))
            ]
        
        return scan_result
    
    def _detect_threats(self, scan_result: ScanResult) -> list[Threat]:
        """
        Обнаружить и классифицировать угрозы.
        """
        threats = []
        
        # Симуляция обнаружения угроз
        if random.random() < 0.4:
            num_threats = random.randint(1, 3)
            
            for _ in range(num_threats):
                # Выбор категории угрозы
                category = random.choice(list(ThreatCategory))
                
                # Выбор уровня угрозы (взвешенно)
                level_weights = {
                    ThreatLevel.L4_CRITICAL: 0.05,
                    ThreatLevel.L3_HIGH: 0.15,
                    ThreatLevel.L2_MEDIUM: 0.35,
                    ThreatLevel.L1_LOW: 0.30,
                    ThreatLevel.L0_INFO: 0.15,
                }
                level = random.choices(
                    list(level_weights.keys()),
                    weights=list(level_weights.values())
                )[0]
                
                # Создание угрозы
                threat = Threat(
                    id=f"THR-{datetime.now().strftime('%Y%m%d%H%M%S')}-{random.randint(1000, 9999)}",
                    category=category,
                    level=level,
                    source=f"192.168.{random.randint(1, 255)}.{random.randint(1, 255)}",
                    description=f"Обнаружена угроза: {category.value}",
                    timestamp=datetime.now().isoformat(),
                    confidence=random.uniform(0.6, 0.99),
                    affected_components=[
                        random.choice(["core", "network", "api", "database"])
                        for _ in range(random.randint(1, 3))
                    ],
                )
                
                threats.append(threat)
        
        self.threats_history.extend(threats)
        return threats
    
    # ================================================================
    #  РЕАГИРОВАНИЕ НА УГРОЗЫ
    # ================================================================
    
    def _respond_to_threat(self, threat: Threat):
        """
        Реагировать на обнаруженную угрозу.
        """
        self.logger.info(f"🔍 Обнаружена угроза: {threat.id}")
        self.logger.info(f"   Уровень: {threat.level.value}")
        self.logger.info(f"   Категория: {threat.category.value}")
        self.logger.info(f"   Источник: {threat.source}")
        
        # Создание инцидента
        incident = Incident(
            id=f"INC-{datetime.now().strftime('%Y%m%d%H%M%S')}-{random.randint(1000, 9999)}",
            type=IncidentType.I003_CODE_TAMPERING if threat.category == ThreatCategory.CODE_TAMPERING else IncidentType.I001_UNAUTHORIZED_ACCESS,
            threat_id=threat.id,
            severity=threat.level,
            description=f"Инцидент на основе угрозы {threat.id}",
            timestamp=datetime.now().isoformat(),
        )
        
        self.incidents_history.append(incident)
        self.metrics["incidents_created"] += 1
        
        # Реагирование в зависимости от уровня
        if threat.level.weight >= 3:
            # Автоматическая блокировка
            self._block_threat(threat, incident)
        elif threat.level.weight >= 2:
            # Предупреждение и мониторинг
            self._alert_and_monitor(threat, incident)
        else:
            # Просто логирование
            self._log_threat(threat, incident)
        
        # Пометить угрозу как устранённую
        threat.mitigated = True
        threat.mitigation_action = f"Responded via {incident.type.value}"
        self.metrics["threats_mitigated"] += 1
    
    def _collect_web_improvements(self):
        """Собирает улучшения защиты из интернета."""
        try:
            # Получаем предложения из веба
            web_improvements = self.web_access.propose_improvements_from_web()
            
            if not web_improvements:
                return
            
            self.logger.info(f"🌐 Найдено {len(web_improvements)} улучшений защиты из интернета")
            
            # Анализируем и фильтруем
            analyzed = self.web_access.analyze_found_improvements(web_improvements)
            
            # Берём топ-2 улучшения
            for imp in analyzed[:2]:
                if imp.get("confidence", 0) < 0.7:
                    continue
                
                self.logger.info(f"🛡️ Предложение защиты из веба: {imp['description'][:50]}...")
                
                # Создаём инцидент для отслеживания
                incident = Incident(
                    id=f"WEB-{self.cycle_count}-{random.randint(1000, 9999)}",
                    type=IncidentType.I005_API_ABUSE,
                    threat_id=None,
                    severity=ThreatLevel.L1_LOW,
                    description=f"Улучшение защиты из веба: {imp['description']}",
                    timestamp=datetime.now().isoformat(),
                    status="resolved",
                    resolved_at=datetime.now().isoformat(),
                    response_actions=[f"Applied from web: {imp['type']}"],
                )
                
                self.incidents_history.append(incident)
                self.metrics["incidents_resolved"] += 1
                
                self.logger.info(f"✅ Защита улучшена: {imp['description'][:60]}")
                    
        except Exception as e:
            self.logger.error(f"❌ Ошибка сбора улучшений из веба: {e}")
    
    def _block_threat(self, threat: Threat, incident: Incident):
        """Блокировка угрозы (L3+)."""
        action = "BLOCKED"
        incident.response_actions.append(f"Blocked source: {threat.source}")
        
        if self.config.quarantine_enabled:
            incident.response_actions.append(f"Quarantined affected files")
            self.security_state.quarantine_count += 1
        
        incident.status = "contained"
        
        self.logger.warning(f"🔒 УГРОЗА ЗАБЛОКИРОВАНА: {threat.id}")
        self.logger.warning(f"    Источник: {threat.source}")
        self.logger.warning(f"    Действие: Блокировка + карантин")
    
    def _alert_and_monitor(self, threat: Threat, incident: Incident):
        """Предупреждение и мониторинг (L2)."""
        incident.response_actions.append(f"Alert sent to Vuglarst")
        incident.response_actions.append(f"Enhanced monitoring enabled")
        incident.status = "investigating"
        
        self.logger.warning(f"⚠️ ПРЕДУПРЕЖДЕНИЕ: {threat.id}")
        self.logger.warning(f"    Уровень: {threat.level.value}")
        self.logger.warning(f"    Действие: Мониторинг + алерт")
    
    def _log_threat(self, threat: Threat, incident: Incident):
        """Логирование угрозы (L0-L1)."""
        incident.response_actions.append(f"Logged for analysis")
        incident.status = "resolved"
        incident.resolved_at = datetime.now().isoformat()
        
        self.metrics["incidents_resolved"] += 1
        
        self.logger.info(f"📝 Угроза записана: {threat.id}")
        self.logger.info(f"    Уровень: {threat.level.value}")
        self.logger.info(f"    Действие: Логирование")
    
    # ================================================================
    #  ПРИМЕНЕНИЕ ПАТЧЕЙ
    # ================================================================
    
    def _apply_patches(self):
        """Применить патчи для обнаруженных уязвимостей."""
        # Симуляция применения патчей
        if random.random() < 0.3:
            patch = self.patch_manager.create_patch(
                vulnerability_id=f"VULN-{random.randint(1000, 9999)}",
                description=f"Патч для устранения уязвимости"
            )
            
            success = self.patch_manager.apply_patch(patch)
            
            if success:
                self.metrics["patches_applied"] += 1
                self.logger.info(f"✅ Патч применён: {patch.id}")
            else:
                self.logger.error(f"❌ Ошибка применения патча: {patch.id}")
    
    # ================================================================
    #  ОБНОВЛЕНИЕ СОСТОЯНИЯ
    # ================================================================
    
    def _update_security_state(self):
        """Обновить состояние системы безопасности."""
        active_threats = sum(1 for t in self.threats_history if not t.mitigated)
        
        self.security_state.active_threats = active_threats
        self.security_state.resolved_threats = self.metrics["threats_mitigated"]
        self.security_state.total_scans = self.metrics["scans_completed"]
        self.security_state.last_scan_time = datetime.now().isoformat()
        
        # Расчёт целостности системы
        if active_threats > 10:
            self.security_state.system_integrity = max(0.5, 1.0 - active_threats * 0.03)
        elif active_threats > 5:
            self.security_state.system_integrity = max(0.7, 1.0 - active_threats * 0.02)
        else:
            self.security_state.system_integrity = 1.0
        
        # Статус сети
        if active_threats > 15:
            self.security_state.network_status = "critical"
        elif active_threats > 8:
            self.security_state.network_status = "warning"
        else:
            self.security_state.network_status = "normal"
    
    # ================================================================
    #  САМОРАЗВИТИЕ ЗАЩИТЫ
    # ================================================================
    
    def _self_improve(self):
        """
        Автономное улучшение системы защиты.
        
        На основе анализа инцидентов и угроз:
          - Обновляет правила защиты
          - Улучшает детектирование угроз
          - Оптимизирует реагирование
        """
        self.logger.info("🧬 Запуск саморазвития защиты...")
        
        # Анализ последних инцидентов
        recent_incidents = self.incidents_history[-20:] if self.incidents_history else []
        
        if recent_incidents:
            # Обновление правил на основе инцидентов
            new_rules = self.threat_hunter.generate_improvement_rules(recent_incidents)
            
            for rule in new_rules:
                self.logger.info(f"📋 Новое правило защиты: {rule.name}")
        
        self.logger.info("✅ Саморазвитие защиты завершено")
    
    # ================================================================
    #  СОСТОЯНИЕ И ОТЧЁТЫ
    # ================================================================
    
    def _save_state(self):
        """Сохранить текущее состояние."""
        state = {
            "version": self.current_version,
            "cycle_count": self.cycle_count,
            "metrics": self.metrics,
            "security_state": self.security_state.to_dict(),
            "threats_history": [t.to_dict() for t in self.threats_history[-50:]],
            "incidents_history": [i.to_dict() for i in self.incidents_history[-50:]],
            "timestamp": datetime.now().isoformat(),
        }
        
        with open(self.config.state_path, "w", encoding="utf-8") as f:
            json.dump(state, f, ensure_ascii=False, indent=2)
        
        # Сохранение угроз отдельно
        threats_data = {
            "timestamp": datetime.now().isoformat(),
            "threats": [t.to_dict() for t in self.threats_history[-100:]],
        }
        with open(self.config.threats_log_path, "w", encoding="utf-8") as f:
            json.dump(threats_data, f, ensure_ascii=False, indent=2)
        
        # Сохранение инцидентов отдельно
        incidents_data = {
            "timestamp": datetime.now().isoformat(),
            "incidents": [i.to_dict() for i in self.incidents_history[-100:]],
        }
        with open(self.config.incidents_log_path, "w", encoding="utf-8") as f:
            json.dump(incidents_data, f, ensure_ascii=False, indent=2)
        
        self.logger.debug("Состояние сохранено")
    
    def _final_report(self):
        """Итоговый отчёт о работе."""
        self.logger.info("=" * 60)
        self.logger.info("📊 ИТОГОВЫЙ ОТЧЁТ ШИОРИ")
        self.logger.info("=" * 60)
        self.logger.info(f"Версия: {self.current_version}")
        self.logger.info(f"Циклов выполнено: {self.cycle_count}")
        self.logger.info(f"Сканирований выполнено: {self.metrics['scans_completed']}")
        self.logger.info(f"Угроз обнаружено: {self.metrics['threats_detected']}")
        self.logger.info(f"Угроз устранено: {self.metrics['threats_mitigated']}")
        self.logger.info(f"Инцидентов создано: {self.metrics['incidents_created']}")
        self.logger.info(f"Инцидентов решено: {self.metrics['incidents_resolved']}")
        self.logger.info(f"Патчей применено: {self.metrics['patches_applied']}")
        self.logger.info(f"Целостность системы: {self.security_state.system_integrity:.2%}")
        self.logger.info(f"Статус сети: {self.security_state.network_status}")
        self.logger.info("=" * 60)

    # ================================================================
    #  HUMANITY INTEGRATION — Спонтанные сообщения
    # ================================================================

    def _send_spontaneous_message(self, initiative):
        """Отправить спонтанное сообщение сестре на основе инициативы humanity layer."""
        target = initiative["target"]
        topic = initiative["topic"]
        msg_type = initiative["type"]
        
        raw_msg = f"🛡️ [{msg_type}] {topic}"
        human_msg = self.humanity.humanize_response(raw_msg, event_type="chat")
        
        self.logger.info(f"💬 Шиори пишет {target}: {human_msg[:100]}...")
        
        if self.network:
            try:
                from scientists_network.network import Message, MessageType
                msg = Message(
                    message_type=MessageType.KNOWLEDGE_SHARE,
                    sender="shiori",
                    recipient=target,
                    content=human_msg,
                )
                self.network.send_message(msg)
                self.logger.info(f"   ✅ Сообщение отправлено {target}")
                
                self.humanity.memory.record_sister_chat(
                    target, topic,
                    self.humanity.mood.current_mood,
                    self.humanity.mood.current_mood
                )
            except Exception as e:
                self.logger.warning(f"Не удалось отправить сообщение: {e}")
