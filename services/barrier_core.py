"""
SHIORI BARRIER CORE — Автономное ядро барьера.

Полностью отделённый от проекта процесс, который:
  - Работает как отдельный сервис (не импортируется в проект)
  - Содержит виртуальных вирусов/хакеров в изолированной среде
  - Вирусы эволюционируют, мутируют, становятся сильнее
  - НИКОГДА не лезут в проект и в интернет
  - Работают только в барьере (sandbox)

Архитектура:
  [Проект] — ОТДЕЛЁН — [БАРЬЕР] — [Интернет]
                    ^
                    |
              Вирусы ТОЛЬКО здесь

Запуск:
  python barrier_core.py
  
Или как сервис:
  python barrier_core.py --service
"""

from __future__ import annotations

import json
import logging
import os
import random
import signal
import sys
import time
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional


# =====================================================================
#  ПРОВЕРКА ИЗОЛЯЦИИ
# =====================================================================

class BarrierIsolationError(Exception):
    """Ошибка нарушения изоляции барьера."""
    pass


def _check_isolation():
    """
    Проверить, что барьер работает в изоляции.
    
    Если этот файл импортирован из проекта — ЗАПРЕЩАЕМ запуск.
    """
    # Проверяем стек вызовов
    import traceback
    stack = traceback.extract_stack()
    
    for frame in stack:
        # Если импортируем из проекта — ошибка
        # Но разрешаем запуск самого barrier_core.py
        if 'Pantikur' in frame.filename and 'polygon' not in frame.filename and 'barrier_core' not in frame.filename:
            raise BarrierIsolationError(
                f"БАРЬЕР ЗАПРЕЩЁН К ИМПОРТУ ИЗ ПРОЕКТА! "
                f"Попытка импорта из: {frame.filename}"
            )


# Запускаем проверку при импорте
_check_isolation()


# =====================================================================
#  ПЕРЕЧИСЛЕНИЯ
# =====================================================================

class VirusSpecies(Enum):
    """Виды вирусов в барьере."""
    # Семейство троянов
    TROJAN_GENERIC = "trojan_generic"
    TROJAN_RANSOMWARE = "trojan_ransomware"
    TROJAN_BACKDOOR = "trojan_backdoor"
    TROJAN_KEYLOGGER = "trojan_keylogger"
    
    # Семейство червей
    WORM_NETWORK = "worm_network"
    WORM_EMAIL = "worm_email"
    WORM_USB = "worm_usb"
    
    # Семейство эксплойтов
    EXPLOIT_BUFFER_OVERFLOW = "exploit_buffer_overflow"
    EXPLOIT_SQLI = "exploit_sqli"
    EXPLOIT_XSS = "exploit_xss"
    EXPLOIT_ZERO_DAY = "exploit_zero_day"
    
    # Семейство APT
    APT_SURVEILLANCE = "apt_surveillance"
    APT_DATA_THEFT = "apt_data_theft"
    APT_C2 = "apt_c2"
    
    # Семейство ботнетов
    BOTNET_DDOS = "botnet_ddos"
    BOTNET_CRYPTOMINER = "botnet_cryptominer"


class MutationType(Enum):
    """Типы мутаций."""
    # Усиление
    INCREASE_STRENGTH = "increase_strength"       # Увеличение силы
    INCREASE_STEALTH = "increase_stealth"         # Увеличение скрытности
    INCREASE_SPEED = "increase_speed"             # Увеличение скорости
    INCREASE_INTELLIGENCE = "increase_intelligence"  # Увеличение интеллекта
    
    # Изменение формы
    CHANGE_FAMILY = "change_family"               # Смена семейства
    ADD_CAPABILITY = "add_capability"             # Добавление способности
    SPLIT = "split"                               # Разделение (размножение)
    
    # Особые
    DEVELOP_ANTIVIRUS = "develop_antivirus"       # Развитие устойчивости к антивирусам
    DEVELOP_POLYMORPHIC = "develop_polymorphic"   # Полиморфизм (изменение кода)
    DEVELOP_METAMORPHIC = "develop_metamorphic"   # Метаморфизм (полная перестройка)


class BarrierEvent(Enum):
    """События в барьере."""
    VIRUS_BORN = "virus_born"                # Рождение вируса
    VIRUS_MUTATED = "virus_mutated"          # Мутация вируса
    VIRUS_DIED = "virus_died"                # Смерть вируса
    VIRUS_EVOLVED = "virus_evolved"          # Эволюция вируса
    VIRUS_SPLIT = "virus_split"              # Разделение вируса
    BARRIER_UPGRADE = "barrier_upgrade"      # Улучшение барьера
    CYCLE_COMPLETE = "cycle_complete"        # Завершение цикла


# =====================================================================
#  МОДЕЛИ ДАННЫХ
# =====================================================================

@dataclass
class Virus:
    """
    Виртуальный вирус в барьере.
    
    Живёт ТОЛЬКО в барьере. Не может покинуть его.
    """
    id: str
    species: VirusSpecies
    name: str
    strength: float = 1.0                      # 1.0-100.0 (сила)
    stealth: float = 1.0                       # 1.0-100.0 (скрытность)
    speed: float = 1.0                         # 1.0-100.0 (скорость распространения)
    intelligence: float = 1.0                  # 1.0-100.0 (интеллект)
    generation: int = 1                        # Поколение (растёт с мутациями)
    age_seconds: float = 0.0                   # Возраст в секундах
    capabilities: List[str] = field(default_factory=list)  # Способности
    is_polymorphic: bool = False               # Полиморфный?
    is_metamorphic: bool = False               # Метаморфный?
    antivirus_resistant: bool = False          # Устойчив к антивирусам?
    born_at: str = ""
    died_at: Optional[str] = None
    status: str = "active"                     # active, dormant, dead
    
    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "species": self.species.value,
            "name": self.name,
            "strength": round(self.strength, 1),
            "stealth": round(self.stealth, 1),
            "speed": round(self.speed, 1),
            "intelligence": round(self.intelligence, 1),
            "generation": self.generation,
            "age_seconds": round(self.age_seconds, 1),
            "capabilities": self.capabilities,
            "is_polymorphic": self.is_polymorphic,
            "is_metamorphic": self.is_metamorphic,
            "antivirus_resistant": self.antivirus_resistant,
            "born_at": self.born_at,
            "status": self.status,
        }


@dataclass
class MutationRecord:
    """Запись о мутации."""
    virus_id: str
    virus_name: str
    mutation_type: MutationType
    old_values: Dict[str, float]
    new_values: Dict[str, float]
    timestamp: str
    success: bool
    
    def to_dict(self) -> dict[str, Any]:
        return {
            "virus_id": self.virus_id,
            "virus_name": self.virus_name,
            "mutation_type": self.mutation_type.value,
            "old_values": self.old_values,
            "new_values": self.new_values,
            "timestamp": self.timestamp,
            "success": self.success,
        }


@dataclass
class BarrierStats:
    """Статистика барьера."""
    total_cycles: int = 0
    total_viruses_born: int = 0
    total_viruses_dead: int = 0
    total_mutations: int = 0
    total_evolution_events: int = 0
    current_virus_count: int = 0
    max_virus_count: int = 0
    average_virus_strength: float = 0.0
    highest_generation: int = 0
    barrier_level: int = 1
    last_cycle_timestamp: str = ""
    
    def to_dict(self) -> dict[str, Any]:
        return {
            "total_cycles": self.total_cycles,
            "total_viruses_born": self.total_viruses_born,
            "total_viruses_dead": self.total_viruses_dead,
            "total_mutations": self.total_mutations,
            "total_evolution_events": self.total_evolution_events,
            "current_virus_count": self.current_virus_count,
            "max_virus_count": self.max_virus_count,
            "average_virus_strength": round(self.average_virus_strength, 1),
            "highest_generation": self.highest_generation,
            "barrier_level": self.barrier_level,
            "last_cycle_timestamp": self.last_cycle_timestamp,
        }


# =====================================================================
#  ГЕНЕРАТОР ВИРУСОВ
# =====================================================================

class VirusGenerator:
    """Генератор виртуальных вирусов для барьера."""
    
    VIRUS_TEMPLATES = {
        VirusSpecies.TROJAN_GENERIC: {
            "base_strength": 5, "base_stealth": 3, "base_speed": 4,
            "base_intelligence": 2,
            "capabilities": ["stealth_install", "data_collection"],
        },
        VirusSpecies.TROJAN_RANSOMWARE: {
            "base_strength": 8, "base_stealth": 4, "base_speed": 3,
            "base_intelligence": 5,
            "capabilities": ["file_encryption", "ransom_note", "payment_demand"],
        },
        VirusSpecies.TROJAN_BACKDOOR: {
            "base_strength": 6, "base_stealth": 7, "base_speed": 2,
            "base_intelligence": 6,
            "capabilities": ["remote_access", "command_execution", "persistence"],
        },
        VirusSpecies.WORM_NETWORK: {
            "base_strength": 5, "base_stealth": 4, "base_speed": 9,
            "base_intelligence": 3,
            "capabilities": ["network_propagation", "port_scanning"],
        },
        VirusSpecies.WORM_EMAIL: {
            "base_strength": 4, "base_stealth": 5, "base_speed": 8,
            "base_intelligence": 4,
            "capabilities": ["email_spreading", "contact_harvesting"],
        },
        VirusSpecies.EXPLOIT_ZERO_DAY: {
            "base_strength": 10, "base_stealth": 8, "base_speed": 5,
            "base_intelligence": 8,
            "capabilities": ["zero_day_exploit", "privilege_escalation"],
        },
        VirusSpecies.APT_C2: {
            "base_strength": 9, "base_stealth": 10, "base_speed": 3,
            "base_intelligence": 9,
            "capabilities": ["command_control", "lateral_movement", "data_exfiltration"],
        },
        VirusSpecies.BOTNET_DDOS: {
            "base_strength": 7, "base_stealth": 2, "base_speed": 10,
            "base_intelligence": 4,
            "capabilities": ["ddos_attack", "bot_recruitment"],
        },
    }
    
    def __init__(self, logger: logging.Logger):
        self.logger = logger
    
    def create_virus(self, species: Optional[VirusSpecies] = None) -> Virus:
        """
        Создать новый вирус.
        
        Args:
            species: вид вируса (случайный если None)
        """
        if species is None:
            species = random.choice(list(VirusSpecies))
        
        template = self.VIRUS_TEMPLATES.get(species, {
            "base_strength": 3, "base_stealth": 3, "base_speed": 3,
            "base_intelligence": 3, "capabilities": [],
        })
        
        # Создаём вирус
        virus = Virus(
            id=f"VIRUS-{datetime.now().strftime('%Y%m%d%H%M%S')}-{random.randint(1000, 9999)}",
            species=species,
            name=self._generate_virus_name(species),
            strength=template["base_strength"] + random.uniform(-1, 2),
            stealth=template["base_stealth"] + random.uniform(-1, 2),
            speed=template["base_speed"] + random.uniform(-1, 2),
            intelligence=template["base_intelligence"] + random.uniform(-1, 2),
            capabilities=list(template["capabilities"]),
            born_at=datetime.now().isoformat(),
        )
        
        # Ограничиваем значения
        virus.strength = max(1.0, min(100.0, virus.strength))
        virus.stealth = max(1.0, min(100.0, virus.stealth))
        virus.speed = max(1.0, min(100.0, virus.speed))
        virus.intelligence = max(1.0, min(100.0, virus.intelligence))
        
        self.logger.info(
            f"[VIRUS] Born virus: {virus.name} ({species.value}), "
            f"generation {virus.generation}, strength {virus.strength:.1f}"
        )
        
        return virus
    
    def _generate_virus_name(self, species: VirusSpecies) -> str:
        """Сгенерировать имя вируса."""
        prefixes = ["X", "Z", "Q", "V", "M", "D", "K", "R", "T", "W"]
        suffixes = ["trojan", "worm", "exploit", "backdoor", "keylog", "ransom", "stealth", "shadow", "phantom", "void"]
        
        prefix = random.choice(prefixes)
        suffix = random.choice(suffixes)
        number = random.randint(100, 999)
        
        return f"{prefix}{suffix}-{number}"


# =====================================================================
#  СИСТЕМА ЭВОЛЮЦИИ
# =====================================================================

class EvolutionSystem:
    """
    Система эволюции вирусов.
    
    Вирусы:
      - Муттируют с определённой вероятностью
      - Растут и становятся сильнее
      - Развивают новые способности
      - Могут мутировать в новые виды
      - Умирают от старости или конкуренции
    """
    
    def __init__(self, logger: logging.Logger):
        self.logger = logger
        self.mutation_records: List[MutationRecord] = []
    
    def evolve_virus(self, virus: Virus) -> List[MutationRecord]:
        """
        Эволюционировать вирус (одна итерация).
        
        Вирус может:
          - Увеличить силу/скрытность/скорость/интеллект
          - Развить новые способности
          - Мутировать в новый вид
          - Разделиться (размножиться)
          - Умереть (от старости или слабости)
        
        Returns:
            Список записей о мутациях
        """
        mutations = []
        virus.age_seconds += 1  # Увеличиваем возраст
        
        # Шанс мутации (растёт с поколением)
        mutation_chance = 0.1 + (virus.generation * 0.05)
        
        if random.random() < mutation_chance:
            mutation = self._mutate_virus(virus)
            if mutation:
                mutations.append(mutation)
        
        # Шанс эволюции (развитие особых способностей)
        if random.random() < 0.05:
            evolution = self._evolve_capabilities(virus)
            if evolution:
                mutations.append(evolution)
        
        # Шанс деления (размножения)
        if virus.strength > 50 and random.random() < 0.02:
            mutations.append(self._split_virus(virus))
        
        # Шанс смерти (от старости или слабости)
        if self._should_die(virus):
            mutations.append(self._kill_virus(virus))
        
        return mutations
    
    def _mutate_virus(self, virus: Virus) -> Optional[MutationRecord]:
        """Выполнить мутацию вируса."""
        # Выбираем тип мутации
        mutation_type = random.choice(list(MutationType))
        
        # Запоминаем старые значения
        old_values = {
            "strength": virus.strength,
            "stealth": virus.stealth,
            "speed": virus.speed,
            "intelligence": virus.intelligence,
        }
        
        success = False
        
        if mutation_type == MutationType.INCREASE_STRENGTH:
            virus.strength = min(100.0, virus.strength + random.uniform(1, 5))
            success = True
        elif mutation_type == MutationType.INCREASE_STEALTH:
            virus.stealth = min(100.0, virus.stealth + random.uniform(1, 5))
            success = True
        elif mutation_type == MutationType.INCREASE_SPEED:
            virus.speed = min(100.0, virus.speed + random.uniform(1, 5))
            success = True
        elif mutation_type == MutationType.INCREASE_INTELLIGENCE:
            virus.intelligence = min(100.0, virus.intelligence + random.uniform(1, 5))
            success = True
        elif mutation_type == MutationType.DEVELOP_POLYMORPHIC:
            if not virus.is_polymorphic:
                virus.is_polymorphic = True
                virus.capabilities.append("polymorphic_code")
                success = True
        elif mutation_type == MutationType.DEVELOP_METAMORPHIC:
            if not virus.is_metamorphic:
                virus.is_metamorphic = True
                virus.capabilities.append("metamorphic_code")
                success = True
        elif mutation_type == MutationType.DEVELOP_ANTIVIRUS:
            if not virus.antivirus_resistant:
                virus.antivirus_resistant = True
                virus.capabilities.append("antivirus_evasion")
                success = True
        
        if success:
            # Увеличиваем поколение
            virus.generation += 1
            
            new_values = {
                "strength": virus.strength,
                "stealth": virus.stealth,
                "speed": virus.speed,
                "intelligence": virus.intelligence,
            }
            
            record = MutationRecord(
                virus_id=virus.id,
                virus_name=virus.name,
                mutation_type=mutation_type,
                old_values=old_values,
                new_values=new_values,
                timestamp=datetime.now().isoformat(),
                success=True,
            )
            
            self.mutation_records.append(record)
            
            self.logger.info(
                f"[MUTATION] {virus.name} -> {mutation_type.value} "
                f"(gen {virus.generation})"
            )
            
            return record
        
        return None
    
    def _evolve_capabilities(self, virus: Virus) -> Optional[MutationRecord]:
        """Развить новые способности."""
        # Список возможных новых способностей
        new_capabilities = [
            "self_replication", "file_destruction", "registry_modification",
            "network_eavesdropping", "credential_harvesting", "privilege_escalation",
            "lateral_movement", "persistence_mechanism", "data_encryption",
            "anti_debugging", "virtual_machine_evasion", "sandbox_evasion",
        ]
        
        # Проверяем, есть ли уже
        available = [c for c in new_capabilities if c not in virus.capabilities]
        
        if not available:
            return None
        
        # Выбираем новую способность
        new_cap = random.choice(available)
        virus.capabilities.append(new_cap)
        
        record = MutationRecord(
            virus_id=virus.id,
            virus_name=virus.name,
            mutation_type=MutationType.ADD_CAPABILITY,
            old_values={},
            new_values={"new_capability": new_cap},
            timestamp=datetime.now().isoformat(),
            success=True,
        )
        
        self.mutation_records.append(record)
        
        self.logger.info(
            f"[EVOLVE] {virus.name} got capability: {new_cap}"
        )
        
        return record
    
    def _split_virus(self, virus: Virus) -> MutationRecord:
        """Деление вируса (размножение)."""
        virus.strength *= 0.7  # Сила уменьшается при делении
        
        record = MutationRecord(
            virus_id=virus.id,
            virus_name=virus.name,
            mutation_type=MutationType.SPLIT,
            old_values={"strength": virus.strength * 1.4},
            new_values={"strength": virus.strength},
            timestamp=datetime.now().isoformat(),
            success=True,
        )
        
        self.mutation_records.append(record)
        
        self.logger.info(
            f"[SPLIT] {virus.name} divided (strength reduced)"
        )
        
        return record
    
    def _kill_virus(self, virus: Virus) -> MutationRecord:
        """Убить вирус (от старости или слабости)."""
        virus.status = "dead"
        virus.died_at = datetime.now().isoformat()
        
        record = MutationRecord(
            virus_id=virus.id,
            virus_name=virus.name,
            mutation_type=MutationType.INCREASE_STRENGTH,  # Специальный тип для смерти
            old_values={"status": "active"},
            new_values={"status": "dead"},
            timestamp=datetime.now().isoformat(),
            success=False,
        )
        
        self.mutation_records.append(record)
        
        self.logger.info(
            f"[DEAD] Virus died: {virus.name} (age: {virus.age_seconds:.0f}s)"
        )
        
        return record
    
    def _should_die(self, virus: Virus) -> bool:
        """
        Определить, должен ли вирус умереть.
        
        Причины смерти:
          - Старость (> 3600 секунд)
          - Слабость (strength < 1)
          - Конкуренция (случайно)
        """
        # Старость
        if virus.age_seconds > 3600:
            return random.random() < 0.3
        
        # Слабость
        if virus.strength < 1:
            return True
        
        # Конкуренция (случайная смерть)
        if random.random() < 0.001:  # 0.1% шанс
            return True
        
        return False


# =====================================================================
#  БАРЬЕР (ГЛАВНЫЙ КЛАСС)
# =====================================================================

class BarrierCore:
    """
    Автономное ядро барьера.
    
    Полностью отделён от проекта. Работает как отдельный процесс.
    
    Особенности:
      - Вирусы живут ТОЛЬКО в барьере
      - Вирусы эволюционируют и мутируют
      - НИКОГДА не покидают барьер
      - НИКОГДА не контактируют с проектом
      - НИКОГДА не выходят в интернет
    """
    
    def __init__(self, state_dir: Optional[Path] = None):
        # Проверяем изоляцию при каждом создании
        _check_isolation()
        
        self.state_dir = state_dir or Path("barrier_data")
        self.state_dir.mkdir(parents=True, exist_ok=True)
        
        self.logger = logging.getLogger("BarrierCore")
        
        # Компоненты
        self.virus_generator = VirusGenerator(self.logger)
        self.evolution_system = EvolutionSystem(self.logger)
        
        # Вирусы в барьере
        self.viruses: Dict[str, Virus] = {}
        
        # Статистика
        self.stats = BarrierStats()
        
        # Флаги
        self._running = False
        self._shutdown_requested = False
        
        # Загрузка состояния
        self._load_state()
    
    def start(self, cycle_interval: float = 1.0, max_cycles: Optional[int] = None):
        """
        Запустить барьер.
        
        Args:
            cycle_interval: интервал между циклами (секунды)
            max_cycles: максимум циклов (None = бесконечно)
        """
        self._running = True
        self.logger.info("=" * 70)
        self.logger.info("[BARRIER] BARRIER STARTED")
        self.logger.info("=" * 70)
        self.logger.info("[WARN] VIRUSES ARE ONLY IN BARRIER")
        self.logger.info("[WARN] NO ACCESS TO PROJECT OR INTERNET")
        self.logger.info("=" * 70)
        
        cycle = 0
        
        while self._running and not self._shutdown_requested:
            cycle += 1
            self.stats.total_cycles += 1
            
            self.logger.info(f"\n[ЦИКЛ {cycle}]")
            
            # 1. Создаём новые вирусы
            self._spawn_viruses()
            
            # 2. Эволюционируем существующих
            self._evolve_viruses()
            
            # 3. Обновляем статистику
            self._update_stats()
            
            # 4. Сохраняем состояние
            self._save_state()
            
            self.stats.last_cycle_timestamp = datetime.now().isoformat()
            
            self.logger.info(
                f"Вирусов: {len(self.viruses)} | "
                "Средняя сила: {avg_strength:.1f}".format(
                    avg_strength=self._average_strength()
                )
            )
            
            # Пауза
            time.sleep(cycle_interval)
            
            if max_cycles and cycle >= max_cycles:
                self.logger.info(f"Достигнут лимит циклов: {max_cycles}")
                break
        
        self.logger.info("[BARRIER] BARRIER STOPPED")
    
    def stop(self):
        """Остановить барьер."""
        self._shutdown_requested = True
    
    def add_virus(self, virus: Virus) -> str:
        """
        Добавить вирус в барьер.
        
        Args:
            virus: вирус для добавления
            
        Returns:
            ID вируса
        """
        _check_isolation()
        
        self.viruses[virus.id] = virus
        self.stats.total_viruses_born += 1
        
        self.logger.info(f"Добавлен вирус: {virus.name} (ID: {virus.id})")
        
        return virus.id
    
    def get_virus(self, virus_id: str) -> Optional[Virus]:
        """Получить вирус по ID."""
        return self.viruses.get(virus_id)
    
    def get_all_viruses(self) -> List[Virus]:
        """Получить всех живых вирусов."""
        return [v for v in self.viruses.values() if v.status == "active"]
    
    def get_stats(self) -> dict[str, Any]:
        """Получить статистику барьера."""
        return {
            "stats": self.stats.to_dict(),
            "virus_count": len(self.viruses),
            "active_virus_count": len(self.get_all_viruses()),
            "recent_mutations": [
                m.to_dict() for m in self.evolution_system.mutation_records[-10:]
            ],
        }
    
    def _spawn_viruses(self):
        """Создать новые вирусы."""
        # Шанс появления нового вируса
        if random.random() < 0.3:
            num_new = random.randint(1, 3)
            
            for _ in range(num_new):
                virus = self.virus_generator.create_virus()
                self.viruses[virus.id] = virus
                self.stats.total_viruses_born += 1
    
    def _evolve_viruses(self):
        """Эволюционировать всех вирусов."""
        viruses_to_remove = []
        
        for virus_id, virus in self.viruses.items():
            if virus.status != "active":
                viruses_to_remove.append(virus_id)
                continue
            
            # Эволюция
            mutations = self.evolution_system.evolve_virus(virus)
            
            if virus.status == "dead":
                viruses_to_remove.append(virus_id)
                self.stats.total_viruses_dead += 1
        
        # Удаляём мёртвых
        for virus_id in viruses_to_remove:
            del self.viruses[virus_id]
    
    def _update_stats(self):
        """Обновить статистику."""
        active_viruses = self.get_all_viruses()
        
        self.stats.current_virus_count = len(active_viruses)
        self.stats.max_virus_count = max(
            self.stats.max_virus_count,
            len(active_viruses)
        )
        
        if active_viruses:
            self.stats.average_virus_strength = (
                sum(v.strength for v in active_viruses) / len(active_viruses)
            )
            self.stats.highest_generation = max(
                self.stats.highest_generation,
                max(v.generation for v in active_viruses)
            )
    
    def _average_strength(self) -> float:
        """Средняя сила вирусов."""
        active = self.get_all_viruses()
        if not active:
            return 0.0
        return sum(v.strength for v in active) / len(active)
    
    def _save_state(self):
        """Сохранить состояние барьера."""
        try:
            state = {
                "viruses": {k: v.to_dict() for k, v in self.viruses.items()},
                "stats": self.stats.to_dict(),
                "mutations": [
                    m.to_dict() for m in self.evolution_system.mutation_records[-100:]
                ],
                "saved_at": datetime.now().isoformat(),
            }
            
            state_path = self.state_dir / "barrier_state.json"
            with open(state_path, "w", encoding="utf-8") as f:
                json.dump(state, f, ensure_ascii=False, indent=2)
        
        except Exception as e:
            self.logger.error(f"❌ Ошибка сохранения состояния: {e}")
    
    def _load_state(self):
        """Загрузить состояние барьера."""
        try:
            state_path = self.state_dir / "barrier_state.json"
            
            if not state_path.exists():
                self.logger.info("[BARRIER] New barrier state")
                return
            
            with open(state_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            
            # Загружаем вирусов
            for virus_id, virus_data in data.get("viruses", {}).items():
                virus = Virus(
                    id=virus_data["id"],
                    species=VirusSpecies(virus_data["species"]),
                    name=virus_data["name"],
                    strength=virus_data["strength"],
                    stealth=virus_data["stealth"],
                    speed=virus_data["speed"],
                    intelligence=virus_data["intelligence"],
                    generation=virus_data["generation"],
                    age_seconds=virus_data.get("age_seconds", 0),
                    capabilities=virus_data.get("capabilities", []),
                    is_polymorphic=virus_data.get("is_polymorphic", False),
                    is_metamorphic=virus_data.get("is_metamorphic", False),
                    antivirus_resistant=virus_data.get("antivirus_resistant", False),
                    born_at=virus_data.get("born_at", ""),
                    status=virus_data.get("status", "active"),
                )
                
                self.viruses[virus.id] = virus
            
            # Загружаем статистику
            stats_data = data.get("stats", {})
            for key, value in stats_data.items():
                if hasattr(self.stats, key):
                    setattr(self.stats, key, value)
            
            self.logger.info(
                f"[BARRIER] State loaded: {len(self.viruses)} viruses"
            )
        
        except Exception as e:
            self.logger.error(f"❌ Ошибка загрузки состояния: {e}")


# =====================================================================
#  ЗАПУСК
# =====================================================================

def main():
    """Точка входа для автономного запуска барьера."""
    # Настраиваем логирование
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
        handlers=[
            logging.StreamHandler(sys.stdout),
        ],
    )
    
    # Проверяем аргументы
    if "--help" in sys.argv:
        print("ИСПОЛЬЗОВАНИЕ:")
        print("  python barrier_core.py              # Запустить барьер")
        print("  python barrier_core.py --cycles N   # N циклов")
        print("  python barrier_core.py --interval S # Интервал S секунд")
        print("  python barrier_core.py --status     # Показать статус")
        return
    
    if "--status" in sys.argv:
        # Показываем статус
        state_path = Path("barrier_data/barrier_state.json")
        if state_path.exists():
            with open(state_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            
            stats = data.get("stats", {})
            print("\nСТАТУС БАРЬЕРА:")
            print(f"  Вирусов: {stats.get('current_virus_count', 0)}")
            print(f"  Циклов: {stats.get('total_cycles', 0)}")
            print(f"  Средняя сила: {stats.get('average_virus_strength', 0):.1f}")
            print(f" 最高 поколение: {stats.get('highest_generation', 0)}")
        else:
            print("Барьер ещё не запущен.")
        return
    
    # Парсим аргументы
    max_cycles = None
    interval = 1.0
    
    if "--cycles" in sys.argv:
        idx = sys.argv.index("--cycles")
        if idx + 1 < len(sys.argv):
            max_cycles = int(sys.argv[idx + 1])
    
    if "--interval" in sys.argv:
        idx = sys.argv.index("--interval")
        if idx + 1 < len(sys.argv):
            interval = float(sys.argv[idx + 1])
    
    # Создаём и запускаем барьер
    barrier = BarrierCore()
    
    # Обработчики сигналов
    def signal_handler(signum, frame):
        barrier.stop()
    
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    # Запускаем
    barrier.start(cycle_interval=interval, max_cycles=max_cycles)


if __name__ == "__main__":
    main()
