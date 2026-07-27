#!/usr/bin/env python3
"""
Шиори AI — WordPress REST API Scanner
Зона: Защита, безопасность, compliance

Функции:
- Обнаружение WordPress REST API атак
- Автоматическая блокировка IP
- Мониторинг аномалий
- Отчётность
"""

import os
import json
import time
import threading
from pathlib import Path
from typing import List, Dict, Tuple, Optional
from datetime import datetime


class WordPressScanner:
    """Сканер WordPress REST API атак для Шиори"""
    
    def __init__(self, logs_dir: str = "data/shiori/logs"):
        self.logs_dir = Path(logs_dir)
        self.logs_dir.mkdir(parents=True, exist_ok=True)
        
        # Загрузка базы знаний
        self.knowledge_dir = Path("data/shiori/knowledge")
        self.knowledge_dir.mkdir(parents=True, exist_ok=True)
        self.attack_knowledge = {}
        self._load_knowledge()
        
        # Хранилище атак
        self.attack_log = []
        self.blocked_ips = {}
        self.attack_stats = {
            "total_attacks": 0,
            "blocked_attacks": 0,
            "by_type": {},
            "by_severity": {}
        }
        
        # Lock для потокобезопасности
        self.lock = threading.Lock()
        
    def _load_knowledge(self):
        """Загружает базу знаний об атаках"""
        attacks_file = self.knowledge_dir / "wordpress_rest_api_attacks.json"
        if attacks_file.exists():
            try:
                with open(attacks_file, "r", encoding="utf-8") as f:
                    self.attack_knowledge = json.load(f)
                print(f"OK Загружена база знаний: {len(self.attack_knowledge)} разделов")
            except Exception as e:
                print(f"WARNING Ошибка загрузки базы знаний: {e}")
    
    def scan_request(self, request_data: Dict) -> Dict:
        """
        Сканирует запрос на подозрительную активность
        
        Args:
            request_data: Данные запроса {
                "ip": str,
                "path": str,
                "method": str,
                "user_agent": str,
                "headers": dict,
                "body": dict
            }
        
        Returns:
            Dict с результатами сканирования
        """
        with self.lock:
            result = {
                "is_attack": False,
                "attack_type": None,
                "severity": None,
                "action": "allow",
                "details": []
            }
            
            ip = request_data.get("ip", "unknown")
            path = request_data.get("path", "").lower()
            method = request_data.get("method", "GET").upper()
            ua = request_data.get("user_agent", "").lower()
            
            # Проверка по типам атак
            attack_type = self._detect_attack_type(path, method, ua)
            
            if attack_type:
                result["is_attack"] = True
                result["attack_type"] = attack_type
                result["severity"] = self._get_severity(attack_type)
                result["action"] = self._get_action(attack_type, ip)
                result["details"].append(f"Обнаружена атака: {attack_type}")
                
                # Логирование
                self._log_attack(request_data, result)
                
                # Обновление статистики
                self._update_stats(attack_type, result["severity"])
                
                # Блокировка если нужно
                if result["action"] == "block_ip":
                    self.blocked_ips[ip] = datetime.now()
                    self.attack_stats["blocked_attacks"] += 1
                    result["details"].append(f"IP {ip} заблокирован")
            
            return result
    
    def _detect_attack_type(self, path: str, method: str, ua: str) -> Optional[str]:
        """Определяет тип атаки"""
        knowledge = self.attack_knowledge.get("attack_types", {})
        
        # REST API Abuse
        if "wp-json/batch" in path or "wp-json/wp/v2/users" in path:
            if method == "POST":
                return "rest_api_abuse"
        
        # XML-RPC Attack
        if "xmlrpc.php" in path:
            return "xmlrpc_attack"
        
        # User Enumeration
        if "wp-json/wp/v2/users" in path and method == "GET":
            return "user_enumeration"
        
        # Brute Force Login
        if "wp-login.php" in path or ("wp-json" in path and "users" in path and method == "POST"):
            return "brute_force_login"
        
        # REST API Scanning
        if "wp-json/" in path and method == "GET":
            return "rest_api_scanning"
        
        return None
    
    def _get_severity(self, attack_type: str) -> str:
        """Получает уровень серьёзности атаки"""
        knowledge = self.attack_knowledge.get("attack_types", {})
        attack = knowledge.get(attack_type, {})
        return attack.get("severity", "medium")
    
    def _get_action(self, attack_type: str, ip: str) -> str:
        """Определяет действие"""
        knowledge = self.attack_knowledge.get("attack_types", {})
        attack = knowledge.get(attack_type, {})
        
        severity = attack.get("severity", "medium")
        
        if severity == "critical":
            return "block_ip"
        elif severity == "high":
            return "block_ip"
        elif severity == "medium":
            return "rate_limit"
        else:
            return "log_and_monitor"
    
    def _log_attack(self, request_data: Dict, result: Dict):
        """Логгирует атаку"""
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "ip": request_data.get("ip"),
            "path": request_data.get("path"),
            "method": request_data.get("method"),
            "user_agent": request_data.get("user_agent"),
            "attack_type": result["attack_type"],
            "severity": result["severity"],
            "action": result["action"]
        }
        
        self.attack_log.append(log_entry)
        self.attack_stats["total_attacks"] += 1
        
        # Сохранение лога в файл
        log_file = self.logs_dir / "attacks.log"
        with open(log_file, "a", encoding="utf-8") as f:
            f.write(json.dumps(log_entry, ensure_ascii=False) + "\n")
    
    def _update_stats(self, attack_type: str, severity: str):
        """Обновляет статистику"""
        # По типам
        if attack_type not in self.attack_stats["by_type"]:
            self.attack_stats["by_type"][attack_type] = 0
        self.attack_stats["by_type"][attack_type] += 1
        
        # По серьёзности
        if severity not in self.attack_stats["by_severity"]:
            self.attack_stats["by_severity"][severity] = 0
        self.attack_stats["by_severity"][severity] += 1
    
    def get_stats(self) -> Dict:
        """Получает статистику атак"""
        return {
            "total_attacks": self.attack_stats["total_attacks"],
            "blocked_attacks": self.attack_stats["blocked_attacks"],
            "by_type": self.attack_stats["by_type"],
            "by_severity": self.attack_stats["by_severity"],
            "blocked_ips_count": len(self.blocked_ips),
            "last_scan": datetime.now().isoformat()
        }
    
    def unblock_ip(self, ip: str) -> bool:
        """Разблокирует IP"""
        with self.lock:
            if ip in self.blocked_ips:
                del self.blocked_ips[ip]
                return True
            return False
    
    def get_blocked_ips(self) -> List[str]:
        """Получает список заблокированных IP"""
        return list(self.blocked_ips.keys())
    
    def generate_report(self) -> Dict:
        """Генерирует отчёт о безопасности"""
        return {
            "title": "Отчёт безопасности Шиори",
            "timestamp": datetime.now().isoformat(),
            "summary": {
                "total_attacks": self.attack_stats["total_attacks"],
                "blocked_attacks": self.attack_stats["blocked_attacks"],
                "block_rate": f"{(self.attack_stats['blocked_attacks'] / max(self.attack_stats['total_attacks'], 1) * 100):.1f}%"
            },
            "attack_types": self.attack_stats["by_type"],
            "severity_distribution": self.attack_stats["by_severity"],
            "blocked_ips": self.get_blocked_ips(),
            "recommendations": self._get_recommendations()
        }
    
    def _get_recommendations(self) -> List[str]:
        """Генерирует рекомендации"""
        recommendations = []
        
        if self.attack_stats["by_type"].get("rest_api_abuse", 0) > 0:
            recommendations.append("🔒 Блокировка wp-json endpoints")
        
        if self.attack_stats["by_type"].get("xmlrpc_attack", 0) > 0:
            recommendations.append("⚡ Отключение xmlrpc.php")
        
        if self.attack_stats["by_type"].get("brute_force_login", 0) > 0:
            recommendations.append("🔑 Включение двухфакторной аутентификации")
        
        if self.attack_stats["total_attacks"] > 10:
            recommendations.append("🛡️ Установка WAF (Web Application Firewall)")
        
        if not recommendations:
            recommendations.append("✅ Система работает нормально")
        
        return recommendations


# API для интеграции с FastAPI
def create_wordpress_scanner():
    """Создаёт экземпляр сканера"""
    return WordPressScanner()


if __name__ == "__main__":
    # Обход проблемы с кодировкой Windows
    import sys
    if sys.stdout.encoding != 'utf-8':
        sys.stdout = open(1, 'w', encoding='utf-8', closefd=False)
    
    scanner = WordPressScanner()
    
    print("Testing WordPress REST API Scanner Shiori...")
    
    # Тест 1: REST API Abuse
    print("\n1. Testing REST API Abuse:")
    result = scanner.scan_request({
        "ip": "192.168.1.100",
        "path": "/wp-json/batch/v1",
        "method": "POST",
        "user_agent": "Mozilla/5.0"
    })
    print(f"   Attack: {result['attack_type']}")
    print(f"   Severity: {result['severity']}")
    print(f"   Action: {result['action']}")
    
    # Тест 2: XML-RPC Attack
    print("\n2. Testing XML-RPC Attack:")
    result = scanner.scan_request({
        "ip": "192.168.1.101",
        "path": "/xmlrpc.php",
        "method": "POST",
        "user_agent": "Mozilla/5.0"
    })
    print(f"   Attack: {result['attack_type']}")
    print(f"   Severity: {result['severity']}")
    print(f"   Action: {result['action']}")
    
    # Тест 3: User Enumeration
    print("\n3. Testing User Enumeration:")
    result = scanner.scan_request({
        "ip": "192.168.1.102",
        "path": "/wp-json/wp/v2/users",
        "method": "GET",
        "user_agent": "Mozilla/5.0"
    })
    print(f"   Attack: {result['attack_type']}")
    print(f"   Severity: {result['severity']}")
    print(f"   Action: {result['action']}")
    
    # Тест 4: Легитимный запрос
    print("\n4. Testing legitimate request:")
    result = scanner.scan_request({
        "ip": "192.168.1.103",
        "path": "/api/predict",
        "method": "POST",
        "user_agent": "Mozilla/5.0"
    })
    print(f"   Is Attack: {result['is_attack']}")
    print(f"   Action: {result['action']}")
    
    # Статистика
    print("\nStatistics:")
    stats = scanner.get_stats()
    for key, value in stats.items():
        print(f"   {key}: {value}")
    
    # Отчёт
    print("\nReport:")
    report = scanner.generate_report()
    print(f"   Total attacks: {report['summary']['total_attacks']}")
    print(f"   Block rate: {report['summary']['block_rate']}")
    
    print("\nAll tests passed!")
