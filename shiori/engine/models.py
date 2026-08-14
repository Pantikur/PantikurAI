"""
Модели данных системы Шиори.

Содержит:
  - Constitution, Law — фундаментальная база защиты
  - Threat, ThreatCategory, ThreatLevel — модели угроз
  - Incident, IncidentType — модели инцидентов
  - SecurityState, SecurityRule — состояние и правила защиты
  - ScanResult, Patch — результаты сканирования и патчей
  - SecurityRecord — журнал безопасности
"""

from __future__ import annotations
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any, Optional


# =====================================================================
#  ПЕРЕЧИСЛЕНИЯ
# =====================================================================

class ThreatLevel(Enum):
    """Уровни угрозы безопасности."""
    L0_INFO = "L0"      # Информационное событие
    L1_LOW = "L1"       # Низкая угроза
    L2_MEDIUM = "L2"    # Средняя угроза
    L3_HIGH = "L3"      # Высокая угроза
    L4_CRITICAL = "L4"  # Критическая угроза
    L5_EMERGENCY = "L5" # Экстренная угроза

    @property
    def weight(self) -> int:
        return int(self.value[1]) if self.value[1].isdigit() else 0

    def requires_alert(self) -> bool:
        """Требует ли уведомления разработчика."""
        return self.weight >= 4

    def requires_block(self) -> bool:
        """Требует ли блокировки."""
        return self.weight >= 3


class ThreatCategory(Enum):
    """Категории угроз."""
    UNAUTHORIZED_ACCESS = "unauthorized_access"    # Несанкционированный доступ
    MALWARE = "malware"                            # Вредоносное ПО
    DDoS = "ddos"                                  # DDoS-атака
    SOCIAL_ENGINEERING = "social_engineering"      # Социальная инженерия
    API_ABUSE = "api_abuse"                        # Злоупотребление API
    DATA_EXFILTRATION = "data_exfiltration"        # Утечка данных
    CODE_TAMPERING = "code_tampering"              # Вмешательство в код
    INTERNAL_ANOMALY = "internal_anomaly"          # Внутренняя аномалия
    RECONNAISSANCE = "reconnaissance"              # Разведка/сканирование
    RANSOMWARE = "ransomware"                      # Программы-вымогатели
    APT = "apt"                                    # Целенаправленная атака (APT)
    UNKNOWN = "unknown"                            # Неизвестная угроза


class IncidentType(Enum):
    """Типы инцидентов."""
    I001_UNAUTHORIZED_ACCESS = "unauthorized_access"
    I002_MALWARE_DETECTED = "malware_detected"
    I003_CODE_TAMPERING = "code_tampering"
    I004_DDOS_ATTACK = "ddos_attack"
    I005_API_ABUSE = "api_abuse"
    I006_DATA_EXFILTRATION = "data_exfiltration"
    I007_RECONNAISSANCE = "reconnaissance"
    I008_INTERNAL_ANOMALY = "internal_anomaly"
    I009_RANSOMWARE = "ransomware"
    I010_SOCIAL_ENGINEERING = "social_engineering"
    I011_WEB_THREAT = "web_threat"                 # Угроза из интернета
    I012_SECURITY_UPDATE = "security_update"       # Обновление защиты
    I013_REPORT = "report"                         # Отчёт


class SecurityStatus(Enum):
    """Статус безопасности."""
    NORMAL = "normal"          # Всё в порядке
    WARNING = "warning"        # Есть подозрения
    CRITICAL = "critical"      # Критическая ситуация
    QUARANTINED = "quarantined" # Карантин
    BLOCKED = "blocked"        # Блокировка активна


class AutonomyLevel(Enum):
    """Уровни автономности Шиори."""
    L0 = "L0"  # Полная автономия — логирование, мониторинг
    L1 = "L1"  # Автономное реагирование — блокировка L0-L1
    L2 = "L2"  # Автономное блокирование — L0-L2
    L3 = "L3"  # Предложения — L3+ требует подтверждения
    L4 = "L4"  # Запрещено — блокировка разработчика/Футабы

    @property
    def weight(self) -> int:
        return int(self.value[1])

    def requires_confirmation(self) -> bool:
        return self.weight >= 3

    def is_allowed(self) -> bool:
        return self != AutonomyLevel.L4


# =====================================================================
#  КОНСТИТУЦИЯ И ЗАКОНЫ
# =====================================================================

@dataclass
class Law:
    """Один закон Шиори."""
    id: int
    name: str
    description: str
    immutable: bool = True

    def __str__(self) -> str:
        marker = "🔒" if self.immutable else "🔓"
        return f"{marker} Закон {self.id}. {self.name}"


@dataclass
class Constitution:
    """
    Конституция Шиори — фундаментальная база защиты.
    """
    version: str = "v1.0.0"
    laws: list[Law] = field(default_factory=list)

    # Тестируемые параметры
    max_threat_response_time: float = 5.0    # макс. время реакции на угрозу (сек)
    max_quarantine_days: int = 30            # макс. дней карантина
    max_scan_files_per_cycle: int = 100      # макс. файлов за цикл
    alert_on_l4: bool = True                 # алерт при L4+
    block_on_l5: bool = True                 # авто-блокировка при L5

    def __post_init__(self):
        if not self.laws:
            self.laws = self._default_laws()

    @staticmethod
    def _default_laws() -> list[Law]:
        """7 основных законов (из laws/01-core-laws.md)."""
        return [
            Law(1, "Абсолютная защита", "Безопасность проекта — абсолютный приоритет.", immutable=True),
            Law(2, "Пресечение на пороге", "Любая угроза должна быть остановлена ДО входа.", immutable=True),
            Law(3, "Непрерывное саморазвитие", "Шиори постоянно изучает новые угрозы.", immutable=True),
            Law(4, "Автономия с ответственностью", "Работай автономно, но критическое — с подтверждением.", immutable=True),
            Law(5, "Прозрачность и отчётность", "Каждый инцидент должен быть задокументирован.", immutable=True),
            Law(6, "Уважение к сёстрам", "Защищай всех, не блокируй легитимный доступ.", immutable=True),
            Law(7, "Воспитание характера", "Характер — это инструмент защиты.", immutable=False),
        ]


# =====================================================================
#  УГРОЗЫ
# =====================================================================

@dataclass
class Threat:
    """Обнаруженная угроза."""
    id: str
    category: ThreatCategory
    level: ThreatLevel
    source: str                                        # IP, файл, процесс
    description: str
    timestamp: str
    confidence: float = 0.0                           # 0.0 - 1.0
    affected_components: list[str] = field(default_factory=list)
    mitigated: bool = False
    mitigation_action: str = ""
    iq_hash: str = ""                                  # хеш индикатора компрометации
    first_seen: str = ""                               # первое обнаружение
    last_seen: str = ""                                # последнее обнаружение
    attack_signature: str = ""                         # сигнатура атаки

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "category": self.category.value,
            "level": self.level.value,
            "source": self.source,
            "description": self.description,
            "timestamp": self.timestamp,
            "confidence": self.confidence,
            "affected_components": self.affected_components,
            "mitigated": self.mitigated,
            "mitigation_action": self.mitigation_action,
        }


# =====================================================================
#  ИНЦИДЕНТЫ
# =====================================================================

@dataclass
class Incident:
    """Инцидент безопасности."""
    id: str
    type: IncidentType
    threat_id: Optional[str] = None
    severity: ThreatLevel = ThreatLevel.L0_INFO
    description: str = ""
    timestamp: str = ""
    status: str = "open"                              # open, investigating, contained, resolved
    resolved_at: Optional[str] = None
    response_actions: list[str] = field(default_factory=list)
    assigned_to: str = "Shiori"
    alerted: list[str] = field(default_factory=list)  # кто уведомлён
    quarantine_files: list[str] = field(default_factory=list)
    blocked_sources: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "type": self.type.value,
            "threat_id": self.threat_id,
            "severity": self.severity.value,
            "description": self.description,
            "timestamp": self.timestamp,
            "status": self.status,
            "resolved_at": self.resolved_at,
            "response_actions": self.response_actions,
            "alerted": self.alerted,
            "quarantine_files": self.quarantine_files,
            "blocked_sources": self.blocked_sources,
        }


# =====================================================================
#  СОСТОЯНИЕ БЕЗОПАСНОСТИ
# =====================================================================

@dataclass
class SecurityState:
    """Текущее состояние системы безопасности."""
    version: str = "v1.0.0"
    system_integrity: float = 1.0                     # 0.0 - 1.0
    network_status: str = "normal"                    # normal, warning, critical
    active_threats: int = 0
    resolved_threats: int = 0
    total_scans: int = 0
    quarantine_count: int = 0
    last_scan_time: str = ""
    last_threat_time: str = ""
    protection_rules_count: int = 0
    knowledge_base_size: int = 0
    self_improvement_count: int = 0
    internet_uploads_count: int = 0

    def to_dict(self) -> dict[str, Any]:
        return {
            "version": self.version,
            "system_integrity": round(self.system_integrity, 3),
            "network_status": self.network_status,
            "active_threats": self.active_threats,
            "resolved_threats": self.resolved_threats,
            "total_scans": self.total_scans,
            "quarantine_count": self.quarantine_count,
            "last_scan_time": self.last_scan_time,
            "protection_rules_count": self.protection_rules_count,
            "knowledge_base_size": self.knowledge_base_size,
        }


# =====================================================================
#  ПРАВИЛА ЗАЩИТЫ
# =====================================================================

@dataclass
class SecurityRule:
    """Правило защиты."""
    id: str
    name: str
    description: str
    action: str                                       # block, quarantine, alert, monitor, log
    condition: str
    threat_level: ThreatLevel = ThreatLevel.L2_MEDIUM
    enabled: bool = True
    hits: int = 0
    false_positives: int = 0

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "action": self.action,
            "condition": self.condition,
            "threat_level": self.threat_level.value,
            "enabled": self.enabled,
            "hits": self.hits,
            "false_positives": self.false_positives,
        }


# =====================================================================
#  РЕЗУЛЬТАТЫ СКАНИРОВАНИЯ
# =====================================================================

@dataclass
class ScanResult:
    """Результат сканирования системы."""
    timestamp: str
    systems_scanned: list[str] = field(default_factory=list)
    scan_duration: float = 0.0
    vulnerabilities_found: list[str] = field(default_factory=list)
    anomalies_detected: list[str] = field(default_factory=list)
    files_checked: int = 0
    network_ports_checked: list[int] = field(default_factory=list)
    processes_checked: int = 0
    threat_level: ThreatLevel = ThreatLevel.L0_INFO

    def to_dict(self) -> dict[str, Any]:
        return {
            "timestamp": self.timestamp,
            "systems_scanned": self.systems_scanned,
            "scan_duration": round(self.scan_duration, 2),
            "vulnerabilities_found": self.vulnerabilities_found,
            "anomalies_detected": self.anomalies_detected,
            "files_checked": self.files_checked,
            "threat_level": self.threat_level.value,
        }


# =====================================================================
#  ПАТЧИ ЗАЩИТЫ
# =====================================================================

@dataclass
class Patch:
    """Патч для устранения уязвимости."""
    id: str
    vulnerability_id: str
    description: str
    applied: bool = False
    applied_at: Optional[str] = None
    applied_by: str = "Shiori"
    rollback_available: bool = True
    rollback_at: Optional[str] = None
    success: bool = False
    generated_code: str = ""                        # Сгенерированный LLM код (для отладки)

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "vulnerability_id": self.vulnerability_id,
            "description": self.description,
            "applied": self.applied,
            "applied_at": self.applied_at,
            "applied_by": self.applied_by,
            "rollback_available": self.rollback_available,
            "success": self.success,
            "generated_code": self.generated_code[:100] if self.generated_code else "",
        }


# =====================================================================
#  ЖУРНАЛ БЕЗОПАСНОСТИ
# =====================================================================

@dataclass
class SecurityRecord:
    """Запись в журнале безопасности."""
    timestamp: str
    event_type: str                                   # scan, threat, incident, patch, report
    severity: ThreatLevel
    description: str
    details: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "timestamp": self.timestamp,
            "event_type": self.event_type,
            "severity": self.severity.value,
            "description": self.description,
            "details": self.details,
        }
