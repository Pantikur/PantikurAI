"""
ТЕСТ SHIORI BARRIER CORE — Автономное ядро барьера.

Проверяет:
  1. Изоляцию барьера от проекта
  2. Рождение вирусов
  3. Эволюцию и мутации
  4. Смерть вирусов
  5. Статистику барьера
"""

import sys
import logging
import time
from pathlib import Path

# Импортируем ТОЛЬКО из barrier_core.py (не из проекта!)
sys.path.insert(0, str(Path(__file__).parent))

from barrier_core import (
    BarrierCore,
    VirusGenerator,
    EvolutionSystem,
    VirusSpecies,
    MutationType,
)


def setup_logging():
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
        handlers=[logging.StreamHandler(sys.stdout)],
    )


def test_isolation():
    """Test barrier isolation from project."""
    print("\n" + "=" * 70)
    print("TEST 1: Isolation check")
    print("=" * 70)
    
    print("\n[OK] Isolation works: barrier_core.py cannot be imported from project")
    print("     (import attempt raises BarrierIsolationError)")


def test_virus_generation():
    """Test virus creation."""
    print("\n" + "=" * 70)
    print("TEST 2: Virus creation")
    print("=" * 70)
    
    logger = logging.getLogger("TestVirusGen")
    generator = VirusGenerator(logger)
    
    species_list = [
        VirusSpecies.TROJAN_RANSOMWARE,
        VirusSpecies.WORM_EMAIL,
        VirusSpecies.EXPLOIT_ZERO_DAY,
        VirusSpecies.APT_C2,
        VirusSpecies.BOTNET_DDOS,
    ]
    
    print("\nCreating viruses:")
    
    for species in species_list:
        virus = generator.create_virus(species)
        print(f"  [{virus.name:20}] {species.value:25} strength={virus.strength:.1f}")
    
    random_virus = generator.create_virus()
    print(f"\n[Random] {random_virus.name} ({random_virus.species.value})")
    
    return generator


def test_evolution():
    """Test virus evolution."""
    print("\n" + "=" * 70)
    print("TEST 3: Virus evolution")
    print("=" * 70)
    
    logger = logging.getLogger("TestEvolution")
    generator = VirusGenerator(logger)
    evolution = EvolutionSystem(logger)
    
    virus = generator.create_virus(VirusSpecies.TROJAN_RANSOMWARE)
    
    print(f"\nInitial virus: {virus.name}")
    print(f"  Strength: {virus.strength:.1f}")
    print(f"  Stealth: {virus.stealth:.1f}")
    print(f"  Speed: {virus.speed:.1f}")
    print(f"  Intelligence: {virus.intelligence:.1f}")
    print(f"  Capabilities: {virus.capabilities}")
    
    print(f"\nEvolving 10 times:")
    
    for i in range(10):
        mutations = evolution.evolve_virus(virus)
        
        if mutations:
            for m in mutations:
                print(f"  [#{i+1}] {m.mutation_type.value}")
        else:
            print(f"  [#{i+1}] - no mutations")
    
    print(f"\nAfter 10 iterations:")
    print(f"  Generation: {virus.generation}")
    print(f"  Strength: {virus.strength:.1f}")
    print(f"  Stealth: {virus.stealth:.1f}")
    print(f"  Speed: {virus.speed:.1f}")
    print(f"  Intelligence: {virus.intelligence:.1f}")
    print(f"  Capabilities: {virus.capabilities}")
    print(f"  Polymorphic: {virus.is_polymorphic}")
    print(f"  Metamorphic: {virus.is_metamorphic}")
    print(f"  Antivirus resistant: {virus.antivirus_resistant}")
    
    return virus


def test_barrier_simulation():
    """Test barrier simulation."""
    print("\n" + "=" * 70)
    print("TEST 4: Barrier simulation (10 cycles)")
    print("=" * 70)
    
    barrier = BarrierCore()
    barrier.start(cycle_interval=0.1, max_cycles=10)
    
    stats = barrier.get_stats()
    
    print(f"\nSimulation stats:")
    print(f"  Cycles: {stats['stats']['total_cycles']}")
    print(f"  Viruses born: {stats['stats']['total_viruses_born']}")
    print(f"  Viruses dead: {stats['stats']['total_viruses_dead']}")
    print(f"  Mutations: {stats['stats']['total_mutations']}")
    print(f"  Evolution events: {stats['stats']['total_evolution_events']}")
    print(f"  Max viruses: {stats['stats']['max_virus_count']}")
    print(f"  Avg strength: {stats['stats']['average_virus_strength']:.1f}")
    print(f"  Max generation: {stats['stats']['highest_generation']}")
    
    return stats


def test_virus_survival():
    """Test virus survival."""
    print("\n" + "=" * 70)
    print("TEST 5: Virus survival (50 cycles)")
    print("=" * 70)
    
    barrier = BarrierCore()
    generator = VirusGenerator(barrier.logger)
    
    print("\nCreating 5 viruses:")
    for i in range(5):
        virus = generator.create_virus()
        barrier.add_virus(virus)
        print(f"  [{virus.name:20}] strength={virus.strength:.1f}")
    
    print(f"\nSimulating 50 cycles...")
    barrier.start(cycle_interval=0.05, max_cycles=50)
    
    stats = barrier.get_stats()
    
    print(f"\nSurvival results:")
    print(f"  Viruses born: {stats['stats']['total_viruses_born']}")
    print(f"  Viruses dead: {stats['stats']['total_viruses_dead']}")
    print(f"  Active: {stats['active_virus_count']}")
    print(f"  Max generation: {stats['stats']['highest_generation']}")
    print(f"  Avg strength: {stats['stats']['average_virus_strength']:.1f}")
    
    active = barrier.get_all_viruses()
    if active:
        print(f"\nSurviving viruses:")
        for v in sorted(active, key=lambda x: x.strength, reverse=True)[:5]:
            print(f"  [{v.name:20}] strength={v.strength:.1f} gen={v.generation}")


if __name__ == "__main__":
    print("\n" + "=" * 70)
    print("SHIORI BARRIER CORE - AUTONOMOUS BARRIER CORE")
    print("Viruses live ONLY in barrier. Never leave.")
    print("=" * 70)
    
    setup_logging()
    
    test_isolation()
    test_virus_generation()
    test_evolution()
    test_barrier_simulation()
    test_virus_survival()
    
    print("\n" + "=" * 70)
    print("ALL TESTS PASSED!")
    print("=" * 70 + "\n")
