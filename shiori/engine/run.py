"""
Точка входа для запуска автономной иммунной системы Шиори.

Использование:
    python -m shiori.engine.run              # постоянная работа
    python -m shiori.engine.run --demo       # демо-режим (5 циклов)
    python -m shiori.engine.run --scan       # только сканирование
    python -m shiori.engine.run --status     # показать состояние
"""

from __future__ import annotations
import argparse
import json
import random
import sys
from pathlib import Path

# Принудительный UTF-8 для вывода (Windows-консоль использует cp1251)
for _stream in (sys.stdout, sys.stderr):
    _reconfigure = getattr(_stream, "reconfigure", None)
    if _reconfigure is not None:
        _reconfigure(encoding="utf-8")

from shiori.engine.config import ShioriConfig
from shiori.engine.shiori_core import ShioriCore
from shiori.engine.threat_hunter import ThreatHunter
from shiori.engine.patch_manager import PatchManager


def cmd_run(config: ShioriConfig):
    """Запустить постоянную работу Шиори."""
    core = ShioriCore(config)
    core.run()


def cmd_scan(config: ShioriConfig):
    """Запустить только сканирование угроз."""
    print("=" * 60)
    print("🔍 СКАНИРОВАНИЕ УГРОЗ ШИОРИ")
    print("=" * 60)
    
    hunter = ThreatHunter(config)
    
    # Сканирование целевых систем
    targets = ["core", "network", "api", "database", "filesystem"]
    
    for target in targets:
        print(f"\nСканирование: {target}...")
        
        # Сканирование уязвимостей
        vulnerabilities = hunter.scan_for_vulnerabilities(target)
        if vulnerabilities:
            print(f"  ⚠️  Обнаружено уязвимостей: {len(vulnerabilities)}")
            for vuln in vulnerabilities:
                print(f"    - {vuln}")
        else:
            print(f"  ✅ Уязвимостей не обнаружено")
        
        # Симуляция метрик для обнаружения аномалий
        metrics = {
            "cpu_usage": random.uniform(30, 95),
            "memory_usage": random.uniform(40, 98),
            "disk_io": random.uniform(20, 90),
            "network_traffic": random.uniform(10, 150),
        }
        
        anomalies = hunter.detect_anomalies(metrics)
        if anomalies:
            print(f"  ⚠️  Обнаружено аномалий: {len(anomalies)}")
            for anomaly in anomalies:
                print(f"    - {anomaly}")
        else:
            print(f"  ✅ Аномалий не обнаружено")
    
    print("\n" + "=" * 60)
    print("✅ Сканирование завершено")
    print("=" * 60)


def cmd_status(config: ShioriConfig):
    """Показать текущее состояние Шиори."""
    state_path = config.state_path
    
    if not state_path.exists():
        print("Шиори ещё не запускалась. Состояние отсутствует.")
        return
    
    with open(state_path, "r", encoding="utf-8") as f:
        state = json.load(f)
    
    print("=" * 60)
    print("🛡️ СОСТОЯНИЕ ШИОРИ")
    print("=" * 60)
    print(f"Версия: {state.get('version', '?')}")
    print(f"Циклов выполнено: {state.get('cycle_count', 0)}")
    print(f"Защищает: {config.parent_system}")
    print(f"Последнее обновление: {state.get('timestamp', '?')}")
    print()
    
    # Состояние безопасности
    security = state.get("security_state", {})
    print("📊 Состояние безопасности:")
    print(f"  Активных угроз: {security.get('active_threats', 0)}")
    print(f"  Устранено угроз: {security.get('resolved_threats', 0)}")
    print(f"  Целостность системы: {security.get('system_integrity', 0):.2%}")
    print(f"  Статус сети: {security.get('network_status', '?')}")
    print(f"  В карантине: {security.get('quarantine_count', 0)}")
    print()
    
    print("Метрики:")
    for key, value in state.get("metrics", {}).items():
        print(f"  {key}: {value}")
    print()
    
    # Последние угрозы
    threats = state.get("threats_history", [])
    if threats:
        print(f"Последние угрозы ({len(threats)}):")
        for threat in threats[-5:]:
            status = "🔒" if threat.get("mitigated") else "⚠️"
            print(f"  {status} {threat.get('id', '?')}: {threat.get('description', '?')}")
    print()
    
    # Последние инциденты
    incidents = state.get("incidents_history", [])
    if incidents:
        print(f"Последние инциденты ({len(incidents)}):")
        for incident in incidents[-5:]:
            status_map = {
                "open": "🔵",
                "investigating": "🟡",
                "contained": "🟠",
                "resolved": "🟢",
                "closed": "⚪"
            }
            status_icon = status_map.get(incident.get("status", "open"), "⚪")
            print(f"  {status_icon} {incident.get('id', '?')}: {incident.get('description', '?')}")


def main():
    parser = argparse.ArgumentParser(
        description="Шиори — автономная иммунная система Вугларста",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__
    )
    
    parser.add_argument(
        "--demo",
        action="store_true",
        help="Демо-режим: 5 циклов с короткими интервалами"
    )
    parser.add_argument(
        "--scan",
        action="store_true",
        help="Запустить только сканирование угроз"
    )
    parser.add_argument(
        "--status",
        action="store_true",
        help="Показать текущее состояние"
    )
    parser.add_argument(
        "--interval",
        type=float,
        default=None,
        help="Интервал между циклами в секундах"
    )
    parser.add_argument(
        "--max-cycles",
        type=int,
        default=None,
        help="Максимальное количество циклов (по умолчанию бесконечно)"
    )
    
    args = parser.parse_args()
    
    # Конфигурация
    if args.demo:
        config = ShioriConfig.demo()
    else:
        config = ShioriConfig.default()
    
    if args.interval is not None:
        config.cycle_interval = args.interval
    if args.max_cycles is not None:
        config.max_cycles = args.max_cycles
    
    # Команды
    if args.status:
        cmd_status(config)
    elif args.scan:
        cmd_scan(config)
    else:
        cmd_run(config)


if __name__ == "__main__":
    main()
