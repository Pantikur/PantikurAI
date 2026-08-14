"""
SHIORI GATEKEEPER — Шлюз-проходная проекта.

Перехватывает реальные угрозы ДО попадания в проект.
Перенаправляет их в полигон, где виртуальные защитники их "съедают".

Архитектура:
  Внешняя угроза → Gatekeeper → Полигон → Хищники → Уничтожено/Пропущено → Проект
"""

from __future__ import annotations

import json
import logging
import random
import time
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple


# =====================================================================
#  ПЕРЕЧИСЛЕНИЯ
# =====================================================================

class ThreatStatus(Enum):
    """Статус угрозы в системе."""
    EXTERNAL = "external"               # Внешняя угроза
    CAPTURED = "captured"               # Захвачена Gatekeeper
    IN_ZOO = "in_zoo"                   # В зоопарке полигона
    BEING_EATEN = "being_eaten"         # Съедается хищником
    DIGESTED = "digested"               # Переварена
    ESCAPED = "escaped"                 # Сбежала (не съедена)
    QUARANTINED = "quarantined"         # В карантине
    ANALYZED = "analyzed"               # Проанализирована


class PredatorType(Enum):
    """Типы хищников-защитников."""
    VIRUS_HUNTER = "virus_hunter"       # Охотник на вирусы
    WORM_EATER = "worm_eater"           # Пожиратель червей
    TROJAN_DEVOURER = "trojan_devourer" # Пожиратель троянов
    HACKER_SNAPPER = "hacker_snapper"   # Ловка хакеров
    APT_CATCHER = "apt_catcher"         # Ловка APT
    ZERO_DAY_KILLER = "zero_day_killer" # Убийца zero-day
    GENERAL_GUARD = "general_guard"     # Общий страж


class GatekeeperAction(Enum):
    """Действия Gatekeeper."""
    CAPTURE = "capture"                 # Захватить
    FORWARD_TO_ZOO = "forward_to_zoo"  # Отправить в зоопарк
    QUARANTINE = "quarantine"           # Карантин
    ANALYZE = "analyze"                 # Анализ
    RELEASE = "release"                 # Пропустить (безопасно)
    DESTROY = "destroy"                 # Уничтожить


# =====================================================================
#  МОДЕЛИ ДАННЫХ
# =====================================================================

@dataclass
class RealThreat:
    """
    Реальная угроза, перехваченная Gatekeeper.
    
    Это может быть:
      - Подозрительный файл
      - Сетевая акака
      - Попробавление несанкционированного доступа
      - Вирусный код
      - anything else
    """
    id: str
    source: str                              # IP, файл, процесс
    threat_type: str                         # Тип угрозы
    severity: int                            # 1-10
    raw_data: str = ""                       # Сырые данные угрозы
    detected_at: str = ""
    status: ThreatStatus = ThreatStatus.EXTERNAL
    captured_by: str = ""
    eaten_by: Optional[str] = None           # ID хищника, который съел
    analysis_result: Optional[Dict] = None   # Результат анализа
    risk_score: float = 0.0                  # 0.0-1.0 (вероятность реальной угрозы)
    
    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "source": self.source,
            "threat_type": self.threat_type,
            "severity": self.severity,
            "detected_at": self.detected_at,
            "status": self.status.value,
            "captured_by": self.captured_by,
            "eaten_by": self.eaten_by,
            "risk_score": self.risk_score,
        }


@dataclass
class Predator:
    """
    Хищник-защитник в зоопарке полигона.
    
    Создаётся Шиори и "ест" реальные угрозы.
    """
    id: str
    name: str
    predator_type: PredatorType
    level: int                               # 1-100
    hunger: float = 100.0                    # 0.0-100.0 (голод)
    strength: float = 50.0                   # 0.0-100.0 (сила)
    speed: float = 50.0                      # 0.0-100.0 (скорость)
    digestions: int = 0                      # Сколько угроз съедено
    last_meal_time: str = ""
    status: str = "active"                   # active, hungry, sleeping, evolved
    
    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "name": self.name,
            "predator_type": self.predator_type.value,
            "level": self.level,
            "hunger": self.hunger,
            "strength": self.strength,
            "speed": self.speed,
            "digestions": self.digestions,
            "status": self.status,
        }


@dataclass
class DigestionRecord:
    """Запись о "поедании" угрозы."""
    id: str
    predator_id: str
    predator_name: str
    threat_id: str
    threat_type: str
    threat_severity: int
    digestion_time: str
    experience_gained: int
    quality: str                             # poor, normal, excellent, perfect
    
    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "predator_id": self.predator_id,
            "predator_name": self.predator_name,
            "threat_id": self.threat_id,
            "threat_type": self.threat_type,
            "threat_severity": self.threat_severity,
            "digestion_time": self.digestion_time,
            "experience_gained": self.experience_gained,
            "quality": self.quality,
        }


# =====================================================================
#  ZOO — ЗООПАРК ХИЩНИКОВ
# =====================================================================

class Zoo:
    """
    Зоопарк полигона — дом для хищников-защитников.
    
    Хищники:
      - Создаются Шиори
      - Охотятся на реальные угрозы
      - Растут и эволюционируют
      - Получают опыт за "поедание" угроз
    """
    
    PREDATOR_NAMES = {
        PredatorType.VIRUS_HUNTER: [
            "VirusHunter-A1", "VirusHunter-B2", "VirusHunter-C3",
            "VirusHunter-D4", "VirusHunter-E5",
        ],
        PredatorType.WORM_EATER: [
            "WormEater-X1", "WormEater-Y2", "WormEater-Z3",
        ],
        PredatorType.TROJAN_DEVOURER: [
            "TrojanDevourer-T1", "TrojanDevourer-T2", "TrojanDevourer-T3",
        ],
        PredatorType.HACKER_SNAPPER: [
            "HackerSnapper-H1", "HackerSnapper-H2",
        ],
        PredatorType.APT_CATCHER: [
            "APTCatcher-A1", "APTCatcher-A2",
        ],
        PredatorType.ZERO_DAY_KILLER: [
            "ZeroDayKiller-Z1",
        ],
        PredatorType.GENERAL_GUARD: [
            "GeneralGuard-G1", "GeneralGuard-G2", "GeneralGuard-G3",
            "GeneralGuard-G4", "GeneralGuard-G5",
        ],
    }
    
    def __init__(self, logger: logging.Logger):
        self.logger = logger
        self.predators: Dict[str, Predator] = {}
        self.digestion_records: List[DigestionRecord] = []
        self._load_zoo()
    
    def create_predator(
        self,
        predator_type: PredatorType,
        level: int = 1,
        name: Optional[str] = None,
    ) -> Predator:
        """
        Создать нового хищника.
        
        Args:
            predator_type: тип хищника
            level: начальный уровень (1-100)
            name: имя (автоматическое если None)
        """
        # Выбираем имя
        if name is None:
            names = self.PREDATOR_NAMES.get(predator_type, ["Guardian"])
            name = random.choice(names)
        
        # Создаём хищника
        predator = Predator(
            id=f"PRED-{datetime.now().strftime('%Y%m%d%H%M%S')}-{random.randint(1000, 9999)}",
            name=name,
            predator_type=predator_type,
            level=level,
            hunger=random.uniform(50, 100),
            strength=min(100, level * 0.8 + random.uniform(0, 20)),
            speed=min(100, level * 0.7 + random.uniform(0, 30)),
        )
        
        self.predators[predator.id] = predator
        self.logger.info(f"🦁 Создан хищник: {predator.name} ({predator_type.value}, уровень {level})")
        
        # Сохраняем зоопарк
        self._save_zoo()
        
        return predator
    
    def create_default_zoo(self) -> List[Predator]:
        """
        Создать стандартный зоопарк (если пуст).
        
        Returns:
            Список созданных хищников
        """
        if self.predators:
            self.logger.info("🦁 Зоопарк уже содержит хищников")
            return list(self.predators.values())
        
        self.logger.info("🦁 Создание стандартного зоопарка...")
        
        predators = []
        
        # 5 общих стражей
        for i in range(5):
            p = self.create_predator(
                PredatorType.GENERAL_GUARD,
                level=random.randint(5, 15),
            )
            predators.append(p)
        
        # 3 охотника на вирусы
        for i in range(3):
            p = self.create_predator(
                PredatorType.VIRUS_HUNTER,
                level=random.randint(5, 10),
            )
            predators.append(p)
        
        # 2 ловца хакеров
        for i in range(2):
            p = self.create_predator(
                PredatorType.HACKER_SNAPPER,
                level=random.randint(8, 12),
            )
            predators.append(p)
        
        # 1 убийца zero-day
        p = self.create_predator(
            PredatorType.ZERO_DAY_KILLER,
            level=10,
        )
        predators.append(p)
        
        self.logger.info(f"🦁 Зоопарк создан: {len(predators)} хищников")
        return predators
    
    def feed_predator(self, predator_id: str, threat: RealThreat) -> Optional[DigestionRecord]:
        """
        Кормить хищника (сделать "поедание" угрозы).
        
        Args:
            predator_id: ID хищника
            threat: реальная угроза
            
        Returns:
            Запись о "поедании" или None если не удалось
        """
        if predator_id not in self.predators:
            self.logger.warning(f"⚠️ Хищник {predator_id} не найден")
            return None
        
        predator = self.predators[predator_id]
        
        # Проверяем, может ли хищник съесть эту угрозу
        can_eat = self._can_predator_eat_threat(predator, threat)
        
        if not can_eat:
            self.logger.debug(
                f"⚠️ {predator.name} не может съесть {threat.threat_type} "
                f"(слишком сильная/не тот тип)"
            )
            return None
        
        # Рассчитываем успех "поедания"
        success_chance = self._calculate_eat_chance(predator, threat)
        success = random.random() < success_chance
        
        if not success:
            self.logger.warning(
                f"❌ {predator.name} не смог съесть {threat.threat_type} "
                f"(шанс {success_chance:.1%})"
            )
            return None
        
        # "Поедание" успешно!
        digestion_time = datetime.now().isoformat()
        experience = self._calculate_experience(predator, threat)
        quality = self._digestion_quality(predator, threat)
        
        # Обновляем хищника
        predator.digestions += 1
        predator.hunger = max(0, predator.hunger - 30)
        predator.last_meal_time = digestion_time
        
        # Опыт и эволюция
        predator.level += 1
        predator.strength = min(100, predator.strength + 0.5)
        predator.speed = min(100, predator.speed + 0.3)
        
        # Создаём запись
        record = DigestionRecord(
            id=f"DIGEST-{datetime.now().strftime('%Y%m%d%H%M%S')}-{random.randint(1000, 9999)}",
            predator_id=predator.id,
            predator_name=predator.name,
            threat_id=threat.id,
            threat_type=threat.threat_type,
            threat_severity=threat.severity,
            digestion_time=digestion_time,
            experience_gained=experience,
            quality=quality,
        )
        
        self.digestion_records.append(record)
        self._save_zoo()
        
        self.logger.info(
            f"🍽️ {predator.name} съел {threat.threat_type}! "
            f"+{experience} XP, качество: {quality}"
        )
        
        return record
    
    def get_active_predators(self, predator_type: Optional[PredatorType] = None) -> List[Predator]:
        """Получить активных хищников."""
        predators = [p for p in self.predators.values() if p.status == "active"]
        
        if predator_type:
            predators = [p for p in predators if p.predator_type == predator_type]
        
        return predators
    
    def get_hungry_predators(self, max_hunger: float = 80.0) -> List[Predator]:
        """Получить голодных хищников."""
        return [
            p for p in self.predators.values()
            if p.status == "active" and p.hunger > max_hunger
        ]
    
    def get_zoo_stats(self) -> dict[str, Any]:
        """Получить статистику зоопарка."""
        total_predators = len(self.predators)
        active_predators = sum(1 for p in self.predators.values() if p.status == "active")
        total_digestions = sum(p.digestions for p in self.predators.values())
        avg_level = sum(p.level for p in self.predators.values()) / max(1, total_predators)
        
        return {
            "total_predators": total_predators,
            "active_predators": active_predators,
            "total_digestions": total_digestions,
            "average_level": round(avg_level, 1),
            "predators_by_type": self._count_by_type(),
            "recent_digestions": [r.to_dict() for r in self.digestion_records[-5:]],
        }
    
    def _can_predator_eat_threat(self, predator: Predator, threat: RealThreat) -> bool:
        """
        Проверить, может ли хищник съесть угрозу.
        
        Хищник может съесть угрозу если:
          - Угроза соответствует типу хищника
          - Уровень хищника достаточно высок
          - Сила хищника >= сложности угрозы
        """
        # Проверка типа
        type_match = self._is_type_match(predator, threat)
        
        # Проверка силы
        threat_difficulty = threat.severity * 8  # 1-10 -> 8-80
        strength_check = predator.strength >= threat_difficulty * 0.5
        
        return type_match and strength_check
    
    def _is_type_match(self, predator: Predator, threat: RealThreat) -> bool:
        """Проверить, соответствует ли тип угрозы типу хищника."""
        threat_lower = threat.threat_type.lower()
        
        type_maps = {
            PredatorType.VIRUS_HUNTER: ["virus", "trojan", "malware", "ransomware"],
            PredatorType.WORM_EATER: ["worm"],
            PredatorType.TROJAN_DEVOURER: ["trojan", "backdoor", "rootkit"],
            PredatorType.HACKER_SNAPPER: ["hacker", "ddos", "bruteforce", "sqli", "xss", "phishing"],
            PredatorType.APT_CATCHER: ["apt", "advanced", "persistent"],
            PredatorType.ZERO_DAY_KILLER: ["zero-day", "exploit", "rce"],
            PredatorType.GENERAL_GUARD: [],  # Ест всё
        }
        
        allowed_types = type_maps.get(predator.predator_type, [])
        
        if not allowed_types:
            return True  # General Guard ест всё
        
        return any(t in threat_lower for t in allowed_types)
    
    def _calculate_eat_chance(self, predator: Predator, threat: RealThreat) -> float:
        """Рассчитать шанс успешного 'поедания'."""
        # Базовый шанс
        base_chance = 0.7
        
        # Корректировка по типу
        if self._is_type_match(predator, threat):
            base_chance += 0.2
        
        # Корректировка по силе
        threat_difficulty = threat.severity * 8
        strength_ratio = predator.strength / max(1, threat_difficulty)
        base_chance += (strength_ratio - 0.5) * 0.3
        
        # Корректировка по скорости
        base_chance += (predator.speed - 50) * 0.002
        
        # Корректировка по голоду
        base_chance += (100 - predator.hunger) * 0.001
        
        # Ограничиваем 0-1
        return max(0.1, min(0.95, base_chance))
    
    def _calculate_experience(self, predator: Predator, threat: RealThreat) -> int:
        """Рассчитать опыт за 'поедание'."""
        base_exp = 10
        
        # За сложность угрозы
        base_exp += threat.severity * 5
        
        # За уровень хищника
        base_exp += predator.level
        
        # Бонус за тип
        if self._is_type_match(predator, threat):
            base_exp *= 1.5
        
        return int(base_exp)
    
    def _digestion_quality(self, predator: Predator, threat: RealThreat) -> str:
        """Определить качество 'поедания'."""
        success_chance = self._calculate_eat_chance(predator, threat)
        
        if success_chance >= 0.85:
            return "perfect"
        elif success_chance >= 0.7:
            return "excellent"
        elif success_chance >= 0.5:
            return "normal"
        else:
            return "poor"
    
    def _count_by_type(self) -> Dict[str, int]:
        """Посчитать хищников по типам."""
        counts = {}
        for p in self.predators.values():
            type_name = p.predator_type.value
            counts[type_name] = counts.get(type_name, 0) + 1
        return counts
    
    def _save_zoo(self):
        """Сохранить зоопарк в файл."""
        try:
            zoo_data = {
                "predators": {k: v.to_dict() for k, v in self.predators.items()},
                "digestion_records": [r.to_dict() for r in self.digestion_records[-100:]],
                "saved_at": datetime.now().isoformat(),
            }
            
            zoo_path = Path("shiori/polygon/zoo_data.json")
            zoo_path.parent.mkdir(parents=True, exist_ok=True)
            
            with open(zoo_path, "w", encoding="utf-8") as f:
                json.dump(zoo_data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            self.logger.error(f"❌ Ошибка сохранения зоопарка: {e}")
    
    def _load_zoo(self):
        """Загрузить зоопарк из файла."""
        try:
            zoo_path = Path("shiori/polygon/zoo_data.json")
            
            if not zoo_path.exists():
                self.logger.info("🦁 Нет сохранённого зоопарка, создаём новый")
                self.create_default_zoo()
                return
            
            with open(zoo_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            
            # Загружаем хищников
            for pred_id, pred_data in data.get("predators", {}).items():
                from enum import Enum
                
                # Восстанавливаем хищника
                predator = Predator(
                    id=pred_data["id"],
                    name=pred_data["name"],
                    predator_type=self._enum_from_value(PredatorType, pred_data["predator_type"]),
                    level=pred_data["level"],
                    hunger=pred_data.get("hunger", 100.0),
                    strength=pred_data.get("strength", 50.0),
                    speed=pred_data.get("speed", 50.0),
                    digestions=pred_data.get("digestions", 0),
                    last_meal_time=pred_data.get("last_meal_time", ""),
                    status=pred_data.get("status", "active"),
                )
                
                self.predators[predator.id] = predator
            
            # Загружаем записи о "поедании"
            for dig_data in data.get("digestion_records", []):
                record = DigestionRecord(
                    id=dig_data["id"],
                    predator_id=dig_data["predator_id"],
                    predator_name=dig_data["predator_name"],
                    threat_id=dig_data["threat_id"],
                    threat_type=dig_data["threat_type"],
                    threat_severity=dig_data["threat_severity"],
                    digestion_time=dig_data["digestion_time"],
                    experience_gained=dig_data["experience_gained"],
                    quality=dig_data["quality"],
                )
                self.digestion_records.append(record)
            
            self.logger.info(
                f"🦁 Зоопарк загружен: {len(self.predators)} хищников, "
                f"{len(self.digestion_records)} записей"
            )
        
        except Exception as e:
            self.logger.error(f"❌ Ошибка загрузки зоопарка: {e}")
            self.create_default_zoo()
    
    def _enum_from_value(self, enum_class, value: str):
        """Преобразовать строку в enum."""
        for member in enum_class:
            if member.value == value:
                return member
        return None


# =====================================================================
#  GATEKEEPER — ШЛЮЗ
# =====================================================================

class Gatekeeper:
    """
    Шлюз-проходная проекта.
    
    Перехватывает реальные угрозы ДО попадания в проект.
    Перенаправляет их в полигон, где хищники их "съедают".
    
    Архитектура:
      Внешняя угроза → Gatekeeper → Полигон (Зoop) → Хищники → Уничтожено/Пропущено
    """
    
    def __init__(self, zoo: Zoo, logger: Optional[logging.Logger] = None):
        self.zoo = zoo
        self.logger = logger or logging.getLogger("Gatekeeper")
        
        # Статистика
        self.total_threats = 0
        self.captured_threats = 0
        self.eaten_threats = 0
        self.escaped_threats = 0
        self.analyzed_threats = 0
        
        # История угроз
        self.threat_history: List[RealThreat] = []
    
    def intercept_threat(
        self,
        source: str,
        threat_type: str,
        severity: int,
        raw_data: str = "",
    ) -> RealThreat:
        """
        Перехватить реальную угрозу.
        
        Это основная точка входа — сюда попадают все подозрительные события.
        
        Args:
            source: источник угрозы (IP, файл, процесс)
            threat_type: тип угрозы
            severity: серьёзность (1-10)
            raw_data: сырые данные
            
        Returns:
            Перехваченная угроза
        """
        self.total_threats += 1
        
        # Создаём угрозу
        threat = RealThreat(
            id=f"REAL-{datetime.now().strftime('%Y%m%d%H%M%S')}-{random.randint(1000, 9999)}",
            source=source,
            threat_type=threat_type,
            severity=severity,
            raw_data=raw_data,
            detected_at=datetime.now().isoformat(),
            status=ThreatStatus.CAPTURED,
            captured_by="Gatekeeper",
            risk_score=self._assess_risk(threat_type, severity),
        )
        
        self.threat_history.append(threat)
        
        self.logger.info(
            f"🚨 Перехвачена угроза: {threat_type} от {source} "
            f"(с серьёзность: {severity}/10)"
        )
        
        # Отправляем в зоопарк
        self._forward_to_zoo(threat)
        
        return threat
    
    def _forward_to_zoo(self, threat: RealThreat):
        """
        Отправить угрозу в зоопарк полигона.
        
        Хищники "охотятся" на угрозу.
        """
        threat.status = ThreatStatus.IN_ZOO
        
        # Находим подходящих хищников
        suitable_predators = self._find_suitable_predators(threat)
        
        if not suitable_predators:
            self.logger.warning(
                f"⚠️ Нет подходящих хищников для {threat.threat_type} "
                f"(отправлено в карантин)"
            )
            threat.status = ThreatStatus.QUARANTINED
            self.escaped_threats += 1
            return
        
        # Сортируем по силе (лучшие первыми)
        suitable_predators.sort(key=lambda p: p.strength, reverse=True)
        
        # Каждый хищник пытается "съесть" угрозу
        for predator in suitable_predators:
            if predator.hunger < 20:
                continue  # Слишком голодный/сытый
            
            self.logger.info(
                f"🦁 {predator.name} охотится на {threat.threat_type}..."
            )
            
            # Пытаемся "скормить" хищнику
            record = self.zoo.feed_predator(predator.id, threat)
            
            if record:
                # Успешно съедено!
                threat.status = ThreatStatus.DIGESTED
                threat.eaten_by = predator.id
                self.eaten_threats += 1
                
                self.logger.info(
                    f"✅ {predator.name} съел {threat.threat_type}! "
                    f"+{record.experience_gained} XP"
                )
                return
        
        # Ни один хищник не смог съесть
        self.logger.warning(
            f"⚠️ Ни один хищник не смог съесть {threat.threat_type} "
            f"(отправлено на анализ)"
        )
        threat.status = ThreatStatus.ANALYZED
        self.escaped_threats += 1
    
    def _find_suitable_predators(self, threat: RealThreat) -> List[Predator]:
        """Найти подходящих хищников для угрозы."""
        suitable = []
        
        for predator in self.zoo.predators.values():
            if predator.status != "active":
                continue
            
            if self.zoo._can_predator_eat_threat(predator, threat):
                suitable.append(predator)
        
        return suitable
    
    def _assess_risk(self, threat_type: str, severity: int) -> float:
        """
        Оценить риск угрозы.
        
        Returns:
            Вероятность реальной угрозы (0.0-1.0)
        """
        # Базовый риск по серьёзности
        base_risk = severity / 10.0
        
        # Корректировка по типу
        high_risk_types = [
            "malware", "ransomware", "exploit", "apt", "zero-day",
            "backdoor", "rootkit",
        ]
        
        if any(t in threat_type.lower() for t in high_risk_types):
            base_risk = min(1.0, base_risk + 0.2)
        
        return round(base_risk, 2)
    
    def get_status(self) -> dict[str, Any]:
        """Получить статус Gatekeeper."""
        return {
            "total_threats": self.total_threats,
            "captured_threats": self.captured_threats,
            "eaten_threats": self.eaten_threats,
            "escaped_threats": self.escaped_threats,
            "analyzed_threats": self.analyzed_threats,
            "success_rate": round(
                self.eaten_threats / max(1, self.total_threats) * 100, 1
            ),
            "zoo_stats": self.zoo.get_zoo_stats(),
            "recent_threats": [
                t.to_dict() for t in self.threat_history[-5:]
            ],
        }


# =====================================================================
#  ИНИЦИАЛИЗАЦИЯ
# =====================================================================

def create_gatekeeper(zoo: Optional[Zoo] = None) -> Gatekeeper:
    """Создать Gatekeeper с зоопарком."""
    logger = logging.getLogger("Gatekeeper")
    zoo = zoo or Zoo(logger)
    zoo.create_default_zoo()
    
    return Gatekeeper(zoo=zoo, logger=logger)
