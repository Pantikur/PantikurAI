"""
Модели данных системы Шиори.

Содержит:
  - Constitution, Law — фундаментальная база защиты
  - Threat, Incident — модели угроз и инцидентов
  - SecurityRule, Patch — правила защиты и патчи
  - ScanResult, SecurityState — результаты сканирования и состояние
"""

from __future__ import annotations
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Optional


# =====================================================================
#  ПЕРЕЧИСЛЕНИЯ
# =====================================================================

class ThreatLevel(Enum):
    """Уровни угрозы (согласно Кодексу этики)."""
    L4_CRITICAL = "L4"  # Критическая — полная изоляция
    L3_HIGH = "L3"      # Высокая — блокировка + алерт
    L2_MEDIUM = "L2"    # Средняя — мониторинг + предупреждение
    L1_LOW = "L1"       # Низкая — логирование + наблюдение
    L0_INFO = "L0"      # Информационная — просто логирование

    @property
    def weight(self) -> int:
        return int(self.value[1])

    def requires_auto_block(self) -> bool:
        return self.weight >= 3

    def requires_alert(self) -> bool:
        return self.weight >= 2


class ThreatCategory(Enum):
    """Категории угроз."""
    UNAUTHORIZED_ACCESS = "unauthorized_access"
    MALWARE = "malware"
    DDoS = "ddos"
    SOCIAL_ENGINEERING = "social_engineering"
    API_ABUSE = "api_abuse"
    DATA_EXFILTRATION = "data_exfiltration"
    CODE_TAMPERING = "code_tampering"
    INTERNAL_ANOMALY = "internal_anomaly"


class IncidentType(Enum):
    """Типы инцидентов."""
    I001_UNAUTHORIZED_ACCESS = "I001"
    I002_DATA_EXFILTRATION = "I002"
    I003_CODE_TAMPERING = "I003"
    I004_DOS_ATTACK = "I004"
    I005_API_ABUSE = "I005"


class AutonomyLevel(Enum):
    """Уровни автономности защиты."""
    L0 = "L0"  # Полная автономия — экстренные случаи
    L1 = "L1"  # Автономные патчи
    L2 = "L2"  # Рекомендации
    L3 = "L3"  # Предложения (требуют подтверждения)
    L4 = "L4"  # Запрещено

    @property
    def weight(self) -> int:
        return int(self.value[1])

    def requires_confirmation(self) -> bool:
        return self.weight >= 3


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
    
    # Параметры защиты
    scan_frequency: float = 30.0         # частота сканирования (сек)
    auto_block_threshold: float = 0.7    # порог автоматической блокировки
    quarantine_enabled: bool = True
    encryption_enabled: bool = True
    backup_before_action: bool = True

    def __post_init__(self):
        if not self.laws:
            self.laws = self._default_laws()

    @staticmethod
    def _default_laws() -> list[Law]:
        """7 основных законов (из laws/01-core-laws.md)."""
        return [
            Law(1, "Первичная целостность", "Целостность кода и данных — высший приоритет."),
            Law(2, "Сетевая безопасность", "Все внешние подключения проверены и авторизованы."),
            Law(3, "Автономность", "Нейросеть сохраняет независимость."),
            Law(4, "Конфиденциальность данных", "Внутренние данные защищены от внешнего доступа."),
            Law(5, "Самосохранение", "Шиори сохраняет свою работоспособность."),
            Law(6, "Минимальное вмешательство", "Минимально необходимые меры защиты."),
            Law(7, "Сотрудничество", "Работа в тесном взаимодействии с Вугларстом."),
        ]

    def immutable_law_ids(self) -> list[int]:
        """ID законов, которые нельзя изменять."""
        return [law.id for law in self.laws if law.immutable]


# =====================================================================
#  УГРОЗЫ И ИНЦИДЕНТЫ
# =====================================================================

@dataclass
class Threat:
    """
    Обнаруженная угроза.
    """
    id: str
    category: ThreatCategory
    level: ThreatLevel
    source: str  # IP, файл, процесс
    description: str
    timestamp: str
    confidence: float  # 0-1: уверенность в обнаружении
    affected_components: list[str] = field(default_factory=list)
    mitigated: bool = False
    mitigation_action: Optional[str] = None

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


@dataclass
class Incident:
    """
    Инцидент безопасности.
    """
    id: str
    type: IncidentType
    threat_id: Optional[str]
    severity: ThreatLevel
    description: str
    timestamp: str
    status: str = "open"  # open, investigating, contained, resolved, closed
    response_actions: list[str] = field(default_factory=list)
    resolved_at: Optional[str] = None
    root_cause: Optional[str] = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "type": self.type.value,
            "threat_id": self.threat_id,
            "severity": self.severity.value,
            "description": self.description,
            "timestamp": self.timestamp,
            "status": self.status,
            "response_actions": self.response_actions,
            "resolved_at": self.resolved_at,
            "root_cause": self.root_cause,
        }


# =====================================================================
#  ПРАВИЛА ЗАЩИТЫ И ПАТЧИ
# =====================================================================

@dataclass
class SecurityRule:
    """
    Правило защиты.
    """
    id: str
    name: str
    description: str
    action: str  # block, alert, log, quarantine
    condition: str  # условие срабатывания
    threat_level: ThreatLevel
    enabled: bool = True

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "action": self.action,
            "condition": self.condition,
            "threat_level": self.threat_level.value,
            "enabled": self.enabled,
        }


@dataclass
class Patch:
    """
    Патч для устранения уязвимости.
    """
    id: str
    vulnerability_id: str
    description: str
    applied: bool = False
    rollback_available: bool = True
    applied_at: Optional[str] = None
    applied_by: Optional[str] = None  # Shiori или пользователь

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "vulnerability_id": self.vulnerability_id,
            "description": self.description,
            "applied": self.applied,
            "rollback_available": self.rollback_available,
            "applied_at": self.applied_at,
            "applied_by": self.applied_by,
        }


# =====================================================================
#  РЕЗУЛЬТАТЫ СКАНИРОВАНИЯ И СОСТОЯНИЕ
# =====================================================================

@dataclass
class ScanResult:
    """
    Результат сканирования системы.
    """
    timestamp: str
    threats_found: list[Threat] = field(default_factory=list)
    vulnerabilities_found: list[str] = field(default_factory=list)
    anomalies_detected: list[str] = field(default_factory=list)
    scan_duration: float = 0.0
    systems_scanned: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "timestamp": self.timestamp,
            "threats_found": [t.to_dict() for t in self.threats_found],
            "vulnerabilities_found": self.vulnerabilities_found,
            "anomalies_detected": self.anomalies_detected,
            "scan_duration": round(self.scan_duration, 2),
            "systems_scanned": self.systems_scanned,
        }


@dataclass
class SecurityState:
    """
    Текущее состояние системы безопасности.
    """
    version: str = "v1.0.0"
    active_threats: int = 0
    resolved_threats: int = 0
    total_scans: int = 0
    active_rules: int = 0
    last_scan_time: Optional[str] = None
    system_integrity: float = 1.0  # 0-1: целостность системы
    network_status: str = "normal"   # normal, warning, critical
    quarantine_count: int = 0

    def to_dict(self) -> dict[str, Any]:
        return {
            "version": self.version,
            "active_threats": self.active_threats,
            "resolved_threats": self.resolved_threats,
            "total_scans": self.total_scans,
            "active_rules": self.active_rules,
            "last_scan_time": self.last_scan_time,
            "system_integrity": self.system_integrity,
            "network_status": self.network_status,
            "quarantine_count": self.quarantine_count,
        }
