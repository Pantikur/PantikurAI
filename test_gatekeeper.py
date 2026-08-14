"""
Тест SHIORI GATEKEEPER — Шлюз-проходная проекта.

Демонстрирует работу системы перехвата реальных угроз.
Реальные угрозы сначала попадают в полигон, где их "съедают" хищники!
"""

import sys
import logging
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from shiori.polygon.gatekeeper import (
    Gatekeeper,
    Zoo,
    PredatorType,
    create_gatekeeper,
)


def setup_logging():
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
        handlers=[logging.StreamHandler(sys.stdout)],
    )


def test_gatekeeper():
    print("\n" + "=" * 70)
    print("TEST 1: Perekhvakt real'nykh ugroz")
    print("=" * 70)
    
    # Создаём Gatekeeper с зоопарком
    gatekeeper = create_gatekeeper()
    
    # Симулируем реальные угрозы
    threats = [
        ("192.168.1.100", "malware_trojan", 7),
        ("suspicious_file.exe", "ransomware", 9),
        ("10.0.0.5", "ddos_attack", 6),
        ("login_page.html", "phishing", 5),
        ("exploit.py", "zero_day_exploit", 10),
        ("192.168.1.200", "sql_injection", 8),
        ("mail_server", "bruteforce", 4),
        ("backup.zip", "worm", 6),
    ]
    
    print(f"\nPerekhvakho ugroz: {len(threats)}")
    
    for source, threat_type, severity in threats:
        threat = gatekeeper.intercept_threat(
            source=source,
            threat_type=threat_type,
            severity=severity,
        )
        
        print(f"  [{threat.status.value:12}] {threat_type:25} ot {source:20} severity={severity}")
    
    return gatekeeper


def test_zoo_stats(gatekeeper):
    print("\n" + "=" * 70)
    print("TEST 2: Statistika zoo parka")
    print("=" * 70)
    
    zoo_stats = gatekeeper.zoo.get_zoo_stats()
    
    print(f"\nStatistika zoo parka:")
    print(f"  Vsego khishchnikov: {zoo_stats['total_predators']}")
    print(f"  Aktivnykh: {zoo_stats['active_predators']}")
    print(f"  Vsego 'poedyaniy': {zoo_stats['total_digestions']}")
    print(f"  Sredniy uroven': {zoo_stats['average_level']}")
    
    print(f"\nKhishchniki po tipam:")
    for ptype, count in zoo_stats['predators_by_type'].items():
        print(f"  {ptype:25} x{count}")
    
    return zoo_stats


def test_gatekeeper_status(gatekeeper):
    print("\n" + "=" * 70)
    print("TEST 3: Status Gatekeeper")
    print("=" * 70)
    
    status = gatekeeper.get_status()
    
    print(f"\nStatus Gatekeeper:")
    print(f"  Vsego perekhvacheno: {status['total_threats']}")
    print(f"  S'edeno khishchnikami: {status['eaten_threats']}")
    print(f"  Sb ezhalo: {status['escaped_threats']}")
    print(f"  Uspeshnost': {status['success_rate']}%")
    
    return status


def test_create_new_predator():
    print("\n" + "=" * 70)
    print("TEST 4: Sozdanie novogo khishchnika")
    print("=" * 70)
    
    zoo = Zoo(logging.getLogger("TestZoo"))
    predator = zoo.create_predator(
        predator_type=PredatorType.VIRUS_HUNTER,
        level=20,
        name="SuperHunter-X1",
    )
    
    print(f"\nSozdan khishchnik:")
    print(f"  Imya: {predator.name}")
    print(f"  Tip: {predator.predator_type.value}")
    print(f"  Uroven': {predator.level}")
    print(f"  Sila: {predator.strength:.1f}")
    print(f"  Skorost': {predator.speed:.1f}")
    
    return predator


if __name__ == "__main__":
    print("\n" + "=" * 70)
    print("SHIORI GATEKEEPER - SHLYUZ-PROKHODNAYA")
    print("Real'nye ugrozy -> Poligon -> Khishchniki -> Unichtozheno")
    print("=" * 70)
    
    setup_logging()
    
    # Тестируем Gatekeeper
    gatekeeper = test_gatekeeper()
    test_zoo_stats(gatekeeper)
    test_gatekeeper_status(gatekeeper)
    test_create_new_predator()
    
    # Итог
    print("\n" + "=" * 70)
    print("ITOGOVAYA STATISTIKA")
    print("=" * 70)
    
    status = gatekeeper.get_status()
    print(f"\nVsego ugroz perekhvacheno: {status['total_threats']}")
    print(f"S'edeno khishchnikami: {status['eaten_threats']}")
    print(f"Sbezhalo: {status['escaped_threats']}")
    print(f"Uspeshnost' zashchity: {status['success_rate']}%")
    print("=" * 70 + "\n")
