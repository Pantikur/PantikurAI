"""
SHIORI POLYGON — Боевой тренажёр Шиори.

Изолированная среда для обучения и тренировки защиты:
  - Генерация виртуальных угроз (вирусы, хакеры, взломщики)
  - Симуляция атак всех видов
  - Отработка методов защиты
  - Запись опыта и результатов
  - Система рангов и прогресса

Polygon полностью отделён от основного проекта — безопасный тренажёр!
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

class ThreatType(Enum):
    """Типы виртуальных угроз."""
    # Вредоносное ПО
    VIRUS_TROJAN = "virus_trojan"           # Вирус-троян
    VIRUS_WORM = "virus_worm"               # Червь
    VIRUS_RANSOMWARE = "virus_ransomware"   # Шифровальщик
    VIRUS_KEYLOGGER = "virus_keylogger"     # Кейлоггер
    VIRUS_ROOTKIT = "virus_rootkit"         # Руткит
    VIRUS_BACKDOOR = "virus_backdoor"       # Бэкдор
    
    # Хакерские атаки
    HACKER_DDOS = "hacker_ddos"             # DDoS-атака
    HACKER_BRUTEFORCE = "hacker_bruteforce" # Подбор паролей
    HACKER_SQLI = "hacker_sqli"             # SQL-инъекция
    HACKER_XSS = "hacker_xss"               # XSS
    HACKER_PHISHING = "hacker_phishing"     # Фишинг
    HACKER_ZERO_DAY = "hacker_zero_day"     # Zero-day
    
    # Продвинутые угрозы
    APT_GROUP = "apt_group"                 # APT-группа
    ZERO_DAY_EXPLOIT = "zero_day_exploit"   # Эксплойт zero-day
    C2_SERVER = "c2_server"                 # Command & Control
    DATA_EXFIL = "data_exfiltration"        # Утечка данных
    CREDENTIAL_THEFT = "credential_theft"   # Кража учётных данных


class AttackMethod(Enum):
    """Методы атак."""
    NETWORK_SCAN = "network_scan"           # Сканирование сети
    PORT_SCAN = "port_scan"                 # Сканирование портов
    BRUTE_FORCE = "brute_force"             # Подбор паролей
    SQL_INJECTION = "sql_injection"         # SQL-инъекция
    XSS_ATTACK = "xss_attack"               # Межсайтовый скрипт
    DOS_ATTACK = "dos_attack"               # Отказ в обслуживании
    PRIVILEGE_ESCALATION = "privilege_escalation"  # Повышение привилегий
    DATA_THEFT = "data_theft"               # Кража данных
    LATERAL_MOVEMENT = "lateral_movement"   # Боковое перемещение
    PERSISTENCE = "persistence"             # Зарождение


class DefenseAction(Enum):
    """Действия защиты."""
    BLOCK = "block"                         # Блокировка
    QUARANTINE = "quarantine"               # Карантин
    ALERT = "alert"                         # Алерт
    MONITOR = "monitor"                     # Мониторинг
    PATCH = "patch"                         # Патч
    ROLLBACK = "rollback"                   # Откат
    ISOLATE = "isolate"                     # Изоляция
    DECRYPT = "decrypt"                     # Расшифровка


class TrainingResult(Enum):
    """Результат тренировки."""
    SUCCESS = "success"                     # Успех
    PARTIAL = "partial"                     # Частичный успех
    FAILURE = "failure"                     # Провал
    LEARNED = "learned"                     # Получен опыт


# =====================================================================
#  МОДЕЛИ ДАННЫХ
# =====================================================================

@dataclass
class VirtualThreat:
    """Виртуальная угроза (симуляция)."""
    id: str
    threat_type: ThreatType
    name: str
    description: str
    severity: int                              # 1-10
    difficulty: int                            # 1-10
    attack_method: AttackMethod
    payload: str = ""                          # Код/скрипт атаки
    targets: List[str] = field(default_factory=list)
    persistence: bool = False                  # Остаётся ли после удаления
    encryption: bool = False                   # Шифрование
    stealth_level: int = 1                     # 1-5 (уровень скрытности)
    created_at: str = ""
    
    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "threat_type": self.threat_type.value,
            "name": self.name,
            "description": self.description,
            "severity": self.severity,
            "difficulty": self.difficulty,
            "attack_method": self.attack_method.value,
            "persistence": self.persistence,
            "encryption": self.encryption,
            "stealth_level": self.stealth_level,
            "created_at": self.created_at,
        }


@dataclass
class DefenseRecord:
    """Запись о действиях защиты."""
    action: DefenseAction
    timestamp: str
    target_id: str
    description: str
    success: bool = False
    response_time_ms: float = 0.0
    resources_used: float = 0.0              # 0.0-1.0


@dataclass
class TrainingSession:
    """Тренировочная сессия."""
    id: str
    timestamp: str
    threats_faced: List[VirtualThreat] = field(default_factory=list)
    defenses_used: List[DefenseRecord] = field(default_factory=list)
    result: TrainingResult = TrainingResult.FAILURE
    experience_gained: int = 0
    rating: str = "E"                        # E, D, C, B, A, S, SS, SSS
    notes: str = ""
    duration_seconds: float = 0.0
    
    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "timestamp": self.timestamp,
            "threats_count": len(self.threats_faced),
            "defenses_count": len(self.defenses_used),
            "result": self.result.value,
            "experience_gained": self.experience_gained,
            "rating": self.rating,
            "notes": self.notes,
            "duration_seconds": self.duration_seconds,
        }


@dataclass
class ShioriStats:
    """Статистика и прогресс Шиори."""
    total_sessions: int = 0
    total_threats_faced: int = 0
    total_defenses_used: int = 0
    successful_defenses: int = 0
    failed_defenses: int = 0
    total_experience: int = 0
    current_rank: str = "E"
    rank_progress: int = 0                   # 0-100 до следующего ранга
    best_rating: str = "E"
    skills: Dict[str, int] = field(default_factory=dict)  # навык -> уровень
    threat_specialization: Dict[str, int] = field(default_factory=dict)  # тип угрозы -> уровень
    last_session_timestamp: str = ""
    streak_days: int = 0
    last_training_date: str = ""
    
    RANKS = ["E", "D", "C", "B", "A", "S", "SS", "SSS"]
    RANK_THRESHOLDS = [0, 100, 500, 1500, 3000, 5000, 10000, 20000]
    
    def to_dict(self) -> dict[str, Any]:
        return {
            "total_sessions": self.total_sessions,
            "total_threats_faced": self.total_threats_faced,
            "total_defenses_used": self.total_defenses_used,
            "successful_defenses": self.successful_defenses,
            "failed_defenses": self.failed_defenses,
            "success_rate": round(self.successful_defenses / max(1, self.total_defenses_used) * 100, 1),
            "total_experience": self.total_experience,
            "current_rank": self.current_rank,
            "rank_progress": self.rank_progress,
            "best_rating": self.best_rating,
            "skills": self.skills,
            "threat_specialization": self.threat_specialization,
            "last_session_timestamp": self.last_session_timestamp,
            "streak_days": self.streak_days,
            "last_training_date": self.last_training_date,
        }


# =====================================================================
#  ГЕНЕРАТОР УГРОЗ
# =====================================================================

class ThreatGenerator:
    """Генератор виртуальных угроз для тренировки."""
    
    THREAT_TEMPLATES = {
        ThreatType.VIRUS_TROJAN: [
            {"name": "Trojan.Win32.Generic", "desc": "Общий троян для кражи данных", "severity": 6},
            {"name": "Trojan.Ransom.LockBit", "desc": "Шифровальщик с ransom note", "severity": 9},
            {"name": "Trojan.Backdoor.C2", "desc": "Троян с бэкдором и C2", "severity": 8},
        ],
        ThreatType.VIRUS_WORM: [
            {"name": "Worm.Net.WannaCry", "desc": "Червь-шифровальщик через SMB", "severity": 9},
            {"name": "Worm.Email.Boomy", "desc": "Червь распространяющийся через email", "severity": 5},
        ],
        ThreatType.HACKER_DDOS: [
            {"name": "DDoS.SYN.Flood", "desc": "SYN-флуд атака", "severity": 7},
            {"name": "DDoS.Volumetric.Botnet", "desc": "Объёмная атака через ботнет", "severity": 8},
            {"name": "DDoS.Application.L7", "desc": "L7 атака на веб-приложение", "severity": 6},
        ],
        ThreatType.HACKER_BRUTEFORCE: [
            {"name": "Hacker.BruteForce.SSH", "desc": "Подбор паролей SSH", "severity": 5},
            {"name": "Hacker.BruteForce.RDP", "desc": "Подбор паролей RDP", "severity": 6},
            {"name": "Hacker.PasswordSpray", "desc": "Распыление паролей по множеству аккаунтов", "severity": 7},
        ],
        ThreatType.HACKER_SQLI: [
            {"name": "Hacker.SQLi.Union", "desc": "SQL-инъекция через UNION", "severity": 8},
            {"name": "Hacker.SQLi.Blind", "desc": "Слепая SQL-инъекция", "severity": 7},
        ],
        ThreatType.HACKER_XSS: [
            {"name": "Hacker.XSS.Reflected", "desc": "Отражённый XSS", "severity": 5},
            {"name": "Hacker.XSS.Stored", "desc": "Хранящийся XSS", "severity": 7},
        ],
        ThreatType.HACKER_PHISHING: [
            {"name": "Hacker.Phishing.Email", "desc": "Фишинговое письмо", "severity": 6},
            {"name": "Hacker.Phishing.Spear", "desc": "Целевой фишинг", "severity": 8},
        ],
        ThreatType.APT_GROUP: [
            {"name": "APT.Stealth.C2", "desc": "Скрытый C2 сервер APT", "severity": 10},
            {"name": "APT.Lateral.Movement", "desc": "Боковое перемещение APT", "severity": 9},
        ],
        ThreatType.ZERO_DAY_EXPLOIT: [
            {"name": "ZeroDay.Exploit.BufferOverflow", "desc": "Переполнение буфера", "severity": 10},
            {"name": "ZeroDay.Exploit.RCE", "desc": "Удалённое выполнение кода", "severity": 10},
        ],
    }
    
    ATTACK_METHODS = list(AttackMethod)
    
    def __init__(self, logger: logging.Logger):
        self.logger = logger
    
    def generate_threat(self, threat_type: Optional[ThreatType] = None, 
                       difficulty: Optional[int] = None) -> VirtualThreat:
        """
        Сгенерировать виртуальную угрозу.
        
        Args:
            threat_type: тип угрозы (случайный если None)
            difficulty: сложность 1-10 (случайная если None)
        """
        # Выбираем тип угрозы
        if threat_type is None:
            threat_type = random.choice(list(ThreatType))
        
        # Выбираем сложность
        if difficulty is None:
            difficulty = random.randint(1, 10)
        
        # Выбираем шаблон
        templates = self.THREAT_TEMPLATES.get(threat_type, [])
        if templates:
            template = random.choice(templates)
        else:
            template = {
                "name": f"Threat.{threat_type.value.replace('_', '.')}",
                "desc": f"Виртуальная угроза типа {threat_type.value}",
                "severity": difficulty,
            }
        
        # Определяем метод атаки
        attack_method = random.choice(self.ATTACK_METHODS)
        
        # Создаём угрозу
        threat = VirtualThreat(
            id=f"THREAT-{datetime.now().strftime('%Y%m%d%H%M%S')}-{random.randint(1000, 9999)}",
            threat_type=threat_type,
            name=template["name"],
            description=template["desc"],
            severity=max(1, min(10, difficulty + random.randint(-1, 1))),
            difficulty=difficulty,
            attack_method=attack_method,
            targets=self._generate_targets(),
            persistence=random.random() < 0.3,
            encryption=random.random() < 0.2,
            stealth_level=random.randint(1, min(5, difficulty // 2 + 1)),
            created_at=datetime.now().isoformat(),
        )
        
        self.logger.debug(f"Сгенерирована угроза: {threat.name} (сложность {threat.difficulty})")
        return threat
    
    def generate_wave(self, count: int = 5, 
                      min_difficulty: int = 1,
                      max_difficulty: int = 5) -> List[VirtualThreat]:
        """
        Сгенерировать волну угроз (серия атак).
        
        Args:
            count: количество угроз
            min_difficulty: минимальная сложность
            max_difficulty: максимальная сложность
        """
        threats = []
        for _ in range(count):
            difficulty = random.randint(min_difficulty, max_difficulty)
            threat = self.generate_threat(difficulty=difficulty)
            threats.append(threat)
        
        self.logger.info(f"Сгенерирована волна из {len(threats)} угроз")
        return threats
    
    def _generate_targets(self) -> List[str]:
        """Сгенерировать список целей."""
        all_targets = [
            "core", "network", "api", "database", "filesystem",
            "authentication", "user_data", "config", "logs",
            "web_server", "email_server", "dns", "firewall",
        ]
        count = random.randint(1, 4)
        return random.sample(all_targets, count)


# =====================================================================
#  СИМУЛЯТОР АТАК
# =====================================================================

class AttackSimulator:
    """Симулятор атак для тренировки защиты."""
    
    def __init__(self, logger: logging.Logger):
        self.logger = logger
        self.attack_history: List[Dict[str, Any]] = []
    
    def simulate_attack(self, threat: VirtualThreat, defense_action: DefenseAction) -> Dict[str, Any]:
        """
        Симулировать атаку и определить результат.
        
        Args:
            threat: виртуальная угроза
            defense_action: действие защиты
        
        Returns:
            Результат симуляции
        """
        start_time = time.time()
        
        # Шанс успеха защиты зависит от:
        # - Действия защиты
        # - Сложности угрозы
        # - Скрытности угрозы
        
        success_chance = self._calculate_success_chance(threat, defense_action)
        success = random.random() < success_chance
        
        response_time = (time.time() - start_time) * 1000  # мс
        
        result = {
            "threat_id": threat.id,
            "threat_name": threat.name,
            "defense_action": defense_action.value,
            "success": success,
            "success_chance": round(success_chance * 100, 1),
            "response_time_ms": round(response_time, 2),
            "severity": threat.severity,
            "difficulty": threat.difficulty,
        }
        
        self.attack_history.append(result)
        self.logger.debug(
            f"Атака {threat.name} vs {defense_action.value}: "
            f"{'УСПЕХ' if success else 'ПРОВАЛ'} (шанс {success_chance:.1%})"
        )
        
        return result
    
    def _calculate_success_chance(self, threat: VirtualThreat, defense_action: DefenseAction) -> float:
        """Рассчитать шанс успеха защиты."""
        # Базовый шанс
        base_chance = 0.6
        
        # Корректировка по действию защиты
        action_modifiers = {
            DefenseAction.BLOCK: 0.1,
            DefenseAction.QUARANTINE: 0.05,
            DefenseAction.ALERT: -0.1,
            DefenseAction.MONITOR: -0.2,
            DefenseAction.PATCH: 0.15,
            DefenseAction.ROLLBACK: 0.1,
            DefenseAction.ISOLATE: 0.05,
            DefenseAction.DECRYPT: 0.0,
        }
        base_chance += action_modifiers.get(defense_action, 0)
        
        # Корректировка по сложности
        difficulty_penalty = (threat.difficulty - 5) * 0.05
        base_chance -= difficulty_penalty
        
        # Корректировка по скрытности
        stealth_penalty = (threat.stealth_level - 1) * 0.05
        base_chance -= stealth_penalty
        
        # Корректировка по шифрованию
        if threat.encryption:
            base_chance -= 0.1
        
        # Ограничиваем 0-1
        return max(0.05, min(0.95, base_chance))


# =====================================================================
#  СИСТЕМА ОПЫТА И РАНГОВ
# =====================================================================

class ExperienceSystem:
    """Система опыта, рангов и прогресса."""
    
    def __init__(self, logger: logging.Logger):
        self.logger = logger
        self.stats = ShioriStats()
    
    def calculate_experience(self, session: TrainingSession) -> int:
        """
        Рассчитать опыт за сессию.
        
        Returns:
            Количество полученного опыта
        """
        experience = 0
        
        # Базовый опыт за сессию
        experience += 10 * len(session.threats_faced)
        
        # Опыт за каждую угрозу
        for threat in session.threats_faced:
            experience += threat.severity * 5
            experience += threat.difficulty * 3
        
        # Опыт за успешные действия защиты
        for defense in session.defenses_used:
            if defense.success:
                experience += 20
            else:
                experience += 5  # Малый опыт даже за неудачу
        
        # Бонус за рейтинг
        rating_bonuses = {
            "E": 0, "D": 10, "C": 25, "B": 50,
            "A": 100, "S": 200, "SS": 400, "SSS": 800
        }
        experience += rating_bonuses.get(session.rating, 0)
        
        # Бонус за скорость реакции
        for defense in session.defenses_used:
            if defense.response_time_ms < 100:
                experience += 5
        
        # Бонус за серию
        if self.stats.streak_days > 1:
            experience *= (1 + self.stats.streak_days * 0.1)
        
        return int(experience)
    
    def update_rating(self, session: TrainingSession) -> str:
        """
        Определить рейтинг сессии.
        
        Returns:
            Рейтинг (E, D, C, B, A, S, SS, SSS)
        """
        success_rate = 0
        if session.defenses_used:
            success_rate = sum(1 for d in session.defenses_used if d.success) / len(session.defenses_used)
        
        # Рейтинг на основе успешности
        if success_rate >= 0.95 and len(session.defenses_used) >= 5:
            return "SSS"
        elif success_rate >= 0.9 and len(session.defenses_used) >= 4:
            return "SS"
        elif success_rate >= 0.8 and len(session.defenses_used) >= 3:
            return "S"
        elif success_rate >= 0.7:
            return "A"
        elif success_rate >= 0.6:
            return "B"
        elif success_rate >= 0.5:
            return "C"
        elif success_rate >= 0.3:
            return "D"
        else:
            return "E"
    
    def update_stats(self, session: TrainingSession, experience: int):
        """Обновить статистику после сессии."""
        self.stats.total_sessions += 1
        self.stats.total_threats_faced += len(session.threats_faced)
        self.stats.total_defenses_used += len(session.defenses_used)
        
        for defense in session.defenses_used:
            if defense.success:
                self.stats.successful_defenses += 1
            else:
                self.stats.failed_defenses += 1
        
        self.stats.total_experience += experience
        
        # Обновление рейтинга
        session.rating = self.update_rating(session)
        if self._rating_value(session.rating) > self._rating_value(self.stats.best_rating):
            self.stats.best_rating = session.rating
        
        # Обновление навыков
        for defense in session.defenses_used:
            skill_name = defense.action.value
            current_level = self.stats.skills.get(skill_name, 0)
            self.stats.skills[skill_name] = current_level + (1 if defense.success else 0)
        
        # Обновление специализации по угрозам
        for threat in session.threats_faced:
            spec_name = threat.threat_type.value
            current_level = self.stats.threat_specialization.get(spec_name, 0)
            self.stats.threat_specialization[spec_name] = current_level + 1
        
        # Обновление ранга
        self._update_rank()
        
        # Обновление серии
        today = datetime.now().strftime("%Y-%m-%d")
        if self.stats.last_training_date == today:
            pass  # Тот же день
        elif self.stats.last_training_date == (datetime.now().timestamp() - 86400):
            self.stats.streak_days += 1
        else:
            self.stats.streak_days = 1
        
        self.stats.last_training_date = today
        self.stats.last_session_timestamp = session.timestamp
    
    def _update_rank(self):
        """Обновить текущий ранг."""
        total_exp = self.stats.total_experience
        ranks = ShioriStats.RANKS
        thresholds = ShioriStats.RANK_THRESHOLDS
        
        current_rank_idx = 0
        for i, threshold in enumerate(thresholds):
            if total_exp >= threshold:
                current_rank_idx = i
        
        self.stats.current_rank = ranks[current_rank_idx]
        
        # Прогресс до следующего ранга
        if current_rank_idx < len(ranks) - 1:
            current_threshold = thresholds[current_rank_idx]
            next_threshold = thresholds[current_rank_idx + 1]
            progress = (total_exp - current_threshold) / (next_threshold - current_threshold) * 100
            self.stats.rank_progress = min(100, max(0, int(progress)))
        else:
            self.stats.rank_progress = 100
    
    def _rating_value(self, rating: str) -> int:
        """Получить числовое значение рейтинга."""
        values = {"E": 0, "D": 1, "C": 2, "B": 3, "A": 4, "S": 5, "SS": 6, "SSS": 7}
        return values.get(rating, 0)


# =====================================================================
#  POLYGON (ГЛАВНЫЙ КЛАСС)
# =====================================================================

class ShioriPolygon:
    """
    Боевой тренажёр Шиори — изолированная среда для тренировки защиты.
    
    Позволяет:
      - Генерировать виртуальные угрозы всех видов
      - Симулировать атаки
      - Отрабатывать методы защиты
      - Записывать опыт и результаты
      - Растить ранг и навыки
    """
    
    def __init__(self, state_dir: Optional[Path] = None):
        self.state_dir = state_dir or Path("shiori/polygon")
        self.state_dir.mkdir(parents=True, exist_ok=True)
        
        self.logger = logging.getLogger("ShioriPolygon")
        
        # Компоненты
        self.threat_generator = ThreatGenerator(self.logger)
        self.attack_simulator = AttackSimulator(self.logger)
        self.experience_system = ExperienceSystem(self.logger)
        
        # Статистика (ссылка на experience_system.stats)
        self.stats = self.experience_system
        
        # Загрузка статистики
        self.stats_path = self.state_dir / "polygon_stats.json"
        self.sessions_path = self.state_dir / "polygon_sessions.json"
        
        self._load_stats()
        self._load_sessions()
    
    def train_single(self, threat_type: Optional[ThreatType] = None,
                     difficulty: Optional[int] = None,
                     defense_action: Optional[DefenseAction] = None) -> TrainingSession:
        """
        Провести одиночную тренировку.
        
        Args:
            threat_type: тип угрозы (случайный если None)
            difficulty: сложность 1-10
            defense_action: действие защиты (выбирается автоматически если None)
        """
        self.logger.info(f"[TRAIN] Начало тренировки (сложность: {difficulty or 'случайная'})")
        
        start_time = time.time()
        
        # 1. Генерируем угрозу
        threat = self.threat_generator.generate_threat(
            threat_type=threat_type,
            difficulty=difficulty
        )
        
        # 2. Если действие защиты не выбрано — выбираем лучшее
        if defense_action is None:
            defense_action = self._choose_best_defense(threat)
        
        # 3. Симулируем атаку
        result = self.attack_simulator.simulate_attack(threat, defense_action)
        
        # 4. Создаём запись о тренировке
        session = TrainingSession(
            id=f"SESSION-{datetime.now().strftime('%Y%m%d%H%M%S')}-{random.randint(1000, 9999)}",
            timestamp=datetime.now().isoformat(),
            threats_faced=[threat],
            defenses_used=[DefenseRecord(
                action=defense_action,
                timestamp=datetime.now().isoformat(),
                target_id=threat.id,
                description=f"Защита от {threat.name} через {defense_action.value}",
                success=result["success"],
                response_time_ms=result["response_time_ms"],
            )],
            experience_gained=0,  # Будет рассчитано позже
            duration_seconds=time.time() - start_time,
        )
        
        # 5. Рассчитываем опыт и обновляем статистику
        experience = self.experience_system.calculate_experience(session)
        session.experience_gained = experience
        session.result = TrainingResult.SUCCESS if result["success"] else TrainingResult.FAILURE
        self.experience_system.update_stats(session, experience)
        
        # 6. Сохраняем
        self._save_stats()
        self._save_session(session)
        
        self.logger.info(
            f"[TRAIN] Тренировка завершена: {threat.name} | "
            f"Защита: {defense_action.value} | "
            f"{'УСПЕХ' if result['success'] else 'ПРОВАЛ'} | "
            f"Опыт: +{experience} XP"
        )
        
        return session
    
    def train_wave(self, count: int = 5,
                   min_difficulty: int = 1,
                   max_difficulty: int = 5,
                   auto_defense: bool = True) -> List[TrainingSession]:
        """
        Провести тренировку волной (серия атак).
        
        Args:
            count: количество угроз
            min_difficulty: минимальная сложность
            max_difficulty: максимальная сложность
            auto_defense: автоматически выбирать защиту
        """
        self.logger.info(f"[WAVE] Начало волны тренировок ({count} угроз, сложность {min_difficulty}-{max_difficulty})")
        
        sessions = []
        threats = self.threat_generator.generate_wave(count, min_difficulty, max_difficulty)
        
        for threat in threats:
            defense_action = None
            if auto_defense:
                defense_action = self._choose_best_defense(threat)
            
            session = self.train_single(
                threat_type=threat.threat_type,
                difficulty=threat.difficulty,
                defense_action=defense_action
            )
            sessions.append(session)
        
        self.logger.info(f"[WAVE] Волна завершена: {len(sessions)} сессий")
        return sessions
    
    def train_specialized(self, threat_type: ThreatType, count: int = 10,
                         difficulty_range: Tuple[int, int] = (5, 8)) -> List[TrainingSession]:
        """
        Специализированная тренировка по одному типу угроз.
        
        Args:
            threat_type: тип угрозы для тренировки
            count: количество повторений
            difficulty_range: диапазон сложности (min, max)
        """
        self.logger.info(f"[SPECIAL] Специализация: {threat_type.value} x{count}")
        
        sessions = []
        for _ in range(count):
            difficulty = random.randint(difficulty_range[0], difficulty_range[1])
            session = self.train_single(threat_type=threat_type, difficulty=difficulty)
            sessions.append(session)
        
        return sessions
    
    def get_status(self) -> dict[str, Any]:
        """Получить текущий статус и статистику."""
        return {
            "stats": self.stats.stats.to_dict(),
            "last_sessions": self._get_recent_sessions(5),
            "rank_info": {
                "current": self.stats.stats.current_rank,
                "progress": self.stats.stats.rank_progress,
                "next_rank": self._get_next_rank(),
            },
        }
    
    def _choose_best_defense(self, threat: VirtualThreat) -> DefenseAction:
        """
        Выбрать лучшее действие защиты для угрозы.
        
        Это симуляция — в реальности Шиори будет анализировать и выбирать сама.
        """
        # Простая логика выбора защиты
        if threat.threat_type in [ThreatType.VIRUS_TROJAN, ThreatType.VIRUS_WORM, ThreatType.VIRUS_RANSOMWARE]:
            return DefenseAction.QUARANTINE
        elif threat.threat_type in [ThreatType.HACKER_DDOS]:
            return DefenseAction.BLOCK
        elif threat.threat_type in [ThreatType.HACKER_BRUTEFORCE]:
            return DefenseAction.BLOCK
        elif threat.threat_type in [ThreatType.HACKER_SQLI, ThreatType.HACKER_XSS]:
            return DefenseAction.PATCH
        elif threat.threat_type in [ThreatType.APT_GROUP, ThreatType.ZERO_DAY_EXPLOIT]:
            return DefenseAction.ISOLATE
        else:
            return DefenseAction.ALERT
    
    def _load_stats(self):
        """Загрузить статистику из файла."""
        if self.stats_path.exists():
            try:
                with open(self.stats_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    # Восстановление статистики
                    for key, value in data.items():
                        if hasattr(self.stats.stats, key):
                            setattr(self.stats.stats, key, value)
                    self.logger.info("[LOAD] Статистика полигона загружена")
            except Exception as e:
                self.logger.warning(f"[LOAD] Ошибка загрузки статистики: {e}")
    
    def _save_stats(self):
        """Сохранить статистику в файл."""
        try:
            with open(self.stats_path, "w", encoding="utf-8") as f:
                json.dump(self.stats.stats.to_dict(), f, ensure_ascii=False, indent=2)
        except Exception as e:
            self.logger.error(f"[SAVE] Ошибка сохранения статистики: {e}")
    
    def _load_sessions(self):
        """Загрузить историю сессий."""
        if self.sessions_path.exists():
            try:
                with open(self.sessions_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    self._recent_sessions = data.get("sessions", [])
            except Exception as e:
                self.logger.warning(f"[LOAD] Ошибка загрузки сессий: {e}")
                self._recent_sessions = []
        else:
            self._recent_sessions = []
    
    def _save_session(self, session: TrainingSession):
        """Сохранить сессию в историю."""
        self._recent_sessions.append(session.to_dict())
        
        # Храним последние 100 сессий
        if len(self._recent_sessions) > 100:
            self._recent_sessions = self._recent_sessions[-100:]
        
        # Сохраняем в файл
        try:
            with open(self.sessions_path, "w", encoding="utf-8") as f:
                json.dump({"sessions": self._recent_sessions}, f, ensure_ascii=False, indent=2)
        except Exception as e:
            self.logger.error(f"[SAVE] Ошибка сохранения сессии: {e}")
    
    def _get_recent_sessions(self, count: int = 5) -> List[dict[str, Any]]:
        """Получить последние N сессий."""
        return self._recent_sessions[-count:]
    
    def _get_next_rank(self) -> str:
        """Получить название следующего ранга."""
        ranks = ShioriStats.RANKS
        current_idx = ranks.index(self.stats.stats.current_rank)
        if current_idx < len(ranks) - 1:
            return ranks[current_idx + 1]
        return "МАКСИМУМ"


# =====================================================================
#  ИНИЦИАЛИЗАЦИЯ
# =====================================================================

def create_polygon(state_dir: Optional[Path] = None) -> ShioriPolygon:
    """Создать и инициализировать полигон."""
    return ShioriPolygon(state_dir=state_dir)
