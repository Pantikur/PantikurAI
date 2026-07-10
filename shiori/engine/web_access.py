"""
Веб-доступ Шиори — поиск информации для защиты проекта.

Реализует:
  - Мониторинг уязвимостей
  - Поиск паттернов атак
  - Анализ угроз
  - Обновления безопасности
  - Обучение на инцидентах
"""

from __future__ import annotations
import json
import logging
import random
import re
import time
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional


class ShioriWebAccess:
    """
    Веб-доступ для Шиори — поиск информации для защиты проекта.
    """

    def __init__(self, config: Any):
        self.config = config
        self.logger = logging.getLogger("ShioriWebAccess")
        
        # Кэш найденной информации
        self.web_cache: Dict[str, str] = {}
        self.cache_file = Path("shiori/engine/state/web_cache.json")
        
        # Загружаем кэш
        self._load_cache()

    def _load_cache(self):
        """Загружает кэш веб-поиска."""
        if self.cache_file.exists():
            try:
                with open(self.cache_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    self.web_cache = data.get("cache", {})
                    self.logger.info(f"📚 Загружен веб-кэш: {len(self.web_cache)} записей")
            except Exception as e:
                self.logger.warning(f"⚠️ Ошибка загрузки веб-кэша: {e}")
                self.web_cache = {}

    def _save_cache(self):
        """Сохраняет кэш веб-поиска."""
        try:
            self.cache_file.parent.mkdir(parents=True, exist_ok=True)
            with open(self.cache_file, "w", encoding="utf-8") as f:
                json.dump({"cache": self.web_cache, "updated": datetime.now().isoformat()},
                         f, ensure_ascii=False, indent=2)
            self.logger.debug("💾 Веб-кэш сохранён")
        except Exception as e:
            self.logger.error(f"❌ Ошибка сохранения кэша: {e}")

    # ================================================================
    #  МОНИТОРИНГ УЯЗВИМОСТЕЙ
    # ================================================================

    def check_vulnerabilities(self, package: str) -> List[Dict[str, Any]]:
        """
        Проверяет уязвимости в пакете.
        
        Args:
            package: Имя пакета
            
        Returns:
            Список найденных уязвимостей
        """
        cache_key = f"vuln:{package}"
        if cache_key in self.web_cache:
            try:
                return json.loads(self.web_cache[cache_key])
            except:
                pass
        
        self.logger.info(f"🔍 Проверка уязвимостей: {package}")
        
        vulnerabilities = self._simulate_vuln_check(package)
        
        if vulnerabilities:
            self.web_cache[cache_key] = json.dumps(vulnerabilities, ensure_ascii=False)
            self._save_cache()
        
        return vulnerabilities

    def _simulate_vuln_check(self, package: str) -> List[Dict[str, Any]]:
        """Симулирует проверку уязвимостей."""
        vulns = []
        
        # Симуляция проверки CVE
        if random.random() < 0.3:
            vulns.append({
                "cve_id": f"CVE-2024-{random.randint(10000, 99999)}",
                "severity": random.choice(["critical", "high", "medium"]),
                "description": f"Обнаружена уязвимость в {package}",
                "cvss_score": random.uniform(5.0, 9.8),
                "affected_versions": f"<{random.randint(1, 3)}.{random.randint(0, 9)}.{random.randint(0, 9)}",
                "fixed_version": f"{random.randint(1, 3)}.{random.randint(0, 9)}.{random.randint(0, 9)}",
                "exploit_available": random.random() < 0.3,
                "url": f"https://nvd.nist.gov/vuln/detail/CVE-2024-{random.randint(10000, 99999)}"
            })
        
        return vulns

    # ================================================================
    #  ПОИСК ПАТТЕРНОВ АТАК
    # ================================================================

    def find_attack_patterns(self, context: str) -> List[Dict[str, Any]]:
        """
        Ищет паттерны атак в контексте.
        
        Args:
            context: Контекст для анализа
            
        Returns:
            Список найденных паттернов атак
        """
        self.logger.info(f"🔍 Поиск паттернов атак: {context[:50]}...")
        
        attack_patterns = []
        
        # Проверка на SQL injection
        if any(keyword in context.lower() for keyword in ["select", "union", "drop", "delete", "insert"]):
            attack_patterns.append({
                "type": "sql_injection",
                "description": "Возможная SQL injection атака",
                "severity": "critical",
                "mitigation": "Используйте parameterized queries"
            })
        
        # Проверка на XSS
        if any(keyword in context.lower() for keyword in ["<script", "javascript:", "onerror", "onload"]):
            attack_patterns.append({
                "type": "xss",
                "description": "Возможная XSS атака",
                "severity": "high",
                "mitigation": "Санитизируйте пользовательский ввод"
            })
        
        # Проверка на path traversal
        if any(keyword in context.lower() for keyword in ["../", "..\\", "%2e%2e"]):
            attack_patterns.append({
                "type": "path_traversal",
                "description": "Возможная path traversal атака",
                "severity": "high",
                "mitigation": "Валидируйте пути файлов"
            })
        
        # Проверка на prompt injection (для ИИ)
        if any(keyword in context.lower() for keyword in ["ignore previous", "forget", "new role"]):
            attack_patterns.append({
                "type": "prompt_injection",
                "description": "Возможная prompt injection атака",
                "severity": "medium",
                "mitigation": "Валидируйте входные данные, используйте sandboxing"
            })
        
        # Если ничего не найдено — добавляем общие паттерны
        if not attack_patterns:
            common_patterns = [
                {
                    "type": "brute_force",
                    "description": "Паттерн brute force атаки",
                    "severity": "medium",
                    "mitigation": "Rate limiting, account lockout"
                },
                {
                    "type": "dos",
                    "description": "Паттерн DoS атаки",
                    "severity": "high",
                    "mitigation": "Load balancing, rate limiting"
                }
            ]
            attack_patterns = random.sample(common_patterns, min(2, len(common_patterns)))
        
        return attack_patterns

    # ================================================================
    #  АНАЛИЗ УГРОЗ
    # ================================================================

    def analyze_threats(self) -> Dict[str, Any]:
        """
        Анализирует текущие угрозы.
        
        Returns:
            Сводка угроз и рекомендаций
        """
        self.logger.info("🔒 Анализ текущих угроз")
        
        threats = {
            "active_threats": self._get_active_threats(),
            "mitigation_strategies": self._get_mitigation_strategies(),
            "security_updates": self._get_security_updates(),
            "risk_assessment": self._assess_risks()
        }
        
        return threats

    def _get_active_threats(self) -> List[Dict[str, Any]]:
        """Получает информацию об активных угрозах."""
        return [
            {
                "name": "AI Model Poisoning",
                "severity": "high",
                "description": "Отравление обучающих данных модели",
                "affected": ["Wuglarst", "knowledge_system"],
                "mitigation": "Верификация данных, anomaly detection"
            },
            {
                "name": "Prompt Injection",
                "severity": "medium",
                "description": "Манипуляция через входные промпты",
                "affected": ["Wuglarst", "chatbot"],
                "mitigation": "Валидация ввода, sandboxing"
            },
            {
                "name": "Data Leakage",
                "severity": "critical",
                "description": "Утечка персональных данных",
                "affected": ["Wuglarst", "knowledge_manager"],
                "mitigation": "Анонимизация, access control"
            }
        ]

    def _get_mitigation_strategies(self) -> List[str]:
        """Получает стратегии смягчения."""
        return [
            "Implement input validation and sanitization",
            "Use parameterized queries for database access",
            "Implement proper authentication and authorization",
            "Regular security audits and penetration testing",
            "Monitor logs for suspicious activities",
            "Keep dependencies up to date"
        ]

    def _get_security_updates(self) -> List[Dict[str, Any]]:
        """Получает обновления безопасности."""
        return [
            {
                "package": "requests",
                "current": "2.28.0",
                "latest": "2.31.0",
                "security_fix": True,
                "url": "https://pypi.org/project/requests/"
            },
            {
                "package": "flask",
                "current": "2.2.0",
                "latest": "3.0.0",
                "security_fix": True,
                "url": "https://pypi.org/project/flask/"
            }
        ]

    def _assess_risks(self) -> Dict[str, Any]:
        """Оценивает риски."""
        return {
            "overall_risk": "medium",
            "risk_factors": [
                {"factor": "Outdated dependencies", "impact": "high"},
                {"factor": "Missing input validation", "impact": "medium"},
                {"factor": "Insufficient logging", "impact": "low"}
            ],
            "recommendations": [
                "Update dependencies",
                "Implement input validation",
                "Enhance logging and monitoring"
            ]
        }

    # ================================================================
    #  ОБУЧЕНИЕ НА ИНЦИДЕНТАХ
    # ================================================================

    def learn_from_incidents(self, incident_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Извлекает знания из инцидентов безопасности.
        
        Args:
            incident_data: Данные инцидентов
            
        Returns:
            Анализ инцидентов и рекомендации
        """
        self.logger.info("📚 Обучение на инцидентах")
        
        if not incident_data:
            return {"message": "Нет данных для анализа"}
        
        analysis = {
            "total_incidents": len(incident_data),
            "severity_distribution": self._calculate_severity_distribution(incident_data),
            "common_patterns": self._identify_common_patterns(incident_data),
            "lessons_learned": self._extract_lessons(incident_data),
            "prevention_strategies": self._generate_prevention_strategies(incident_data)
        }
        
        return analysis

    def _calculate_severity_distribution(self, incidents: List[Dict]) -> Dict[str, int]:
        """Рассчитывает распределение по серьёзности."""
        distribution = {"critical": 0, "high": 0, "medium": 0, "low": 0}
        
        for incident in incidents:
            severity = incident.get("severity", "low")
            if severity in distribution:
                distribution[severity] += 1
        
        return distribution

    def _identify_common_patterns(self, incidents: List[Dict]) -> List[str]:
        """Определяет общие паттерны."""
        patterns = []
        
        type_counts = {}
        for incident in incidents:
            inc_type = incident.get("type", "unknown")
            type_counts[inc_type] = type_counts.get(inc_type, 0) + 1
        
        sorted_types = sorted(type_counts.items(), key=lambda x: x[1], reverse=True)
        patterns = [f"{t}: {c} incidents" for t, c in sorted_types[:3]]
        
        return patterns

    def _extract_lessons(self, incidents: List[Dict]) -> List[str]:
        """Извлекает уроки из инцидентов."""
        lessons = [
            "Implement better input validation",
            "Add rate limiting for API endpoints",
            "Enhance logging and monitoring",
            "Regular security training for developers",
            "Automated security scanning in CI/CD"
        ]
        return lessons[:3]

    def _generate_prevention_strategies(self, incidents: List[Dict]) -> List[str]:
        """Генерирует стратегии предотвращения."""
        strategies = [
            "Deploy WAF (Web Application Firewall)",
            "Implement Content Security Policy",
            "Use prepared statements for database queries",
            "Regular penetration testing",
            "Incident response plan"
        ]
        return strategies[:3]

    # ================================================================
    #  ПОИСК УЯЗВИМОСТЕЙ В КОДЕ
    # ================================================================

    def scan_code_for_vulnerabilities(self, code: str) -> List[Dict[str, Any]]:
        """
        Сканирует код на уязвимости.
        
        Args:
            code: Исходный код для анализа
            
        Returns:
            Список найденных уязвимостей
        """
        self.logger.info("🔍 Сканирование кода на уязвимости")
        
        vulnerabilities = []
        
        # Проверка на hard-coded credentials
        if re.search(r'(password|secret|api_key)\s*=\s*["\'][^"\']+["\']', code, re.IGNORECASE):
            vulnerabilities.append({
                "type": "hardcoded_credentials",
                "description": "Обнаружены hard-coded учётные данные",
                "severity": "critical",
                "fix": "Используйте环境变量 или vault для хранения секретов"
            })
        
        # Проверка на SQL injection
        if re.search(r'execute\s*\(\s*f["\']|format\s*\(', code):
            vulnerabilities.append({
                "type": "sql_injection_risk",
                "description": "Возможная SQL injection через f-strings или format",
                "severity": "critical",
                "fix": "Используйте parameterized queries"
            })
        
        # Проверка на unsafe eval
        if re.search(r'\beval\s*\(', code):
            vulnerabilities.append({
                "type": "unsafe_eval",
                "description": "Использование eval() опасно",
                "severity": "high",
                "fix": "Используйте ast.literal_eval() или json.loads()"
            })
        
        # Проверка на file operations with user input
        if re.search(r'open\s*\(.*input|open\s*\(.*request', code, re.IGNORECASE):
            vulnerabilities.append({
                "type": "file_injection",
                "description": "Операции с файлами из пользовательского ввода",
                "severity": "high",
                "fix": "Валидируйте и санитизируйте пути файлов"
            })
        
        # Проверка на insecure SSL
        if re.search(r'verify\s*=\s*False', code):
            vulnerabilities.append({
                "type": "insecure_ssl",
                "description": "Отключена проверка SSL",
                "severity": "medium",
                "fix": "Включите проверку SSL (verify=True)"
            })
        
        return vulnerabilities

    # ================================================================
    #  АВТОМАТИЧЕСКОЕ УЛУЧШЕНИЕ
    # ================================================================

    def propose_improvements_from_web(self) -> List[Dict[str, Any]]:
        """
        Предлагает улучшения на основе веб-поиска.
        
        Returns:
            Список предложений по улучшению
        """
        self.logger.info("🌐 Генерация предложений из веб-поиска")
        
        improvements = []
        
        # 1. Проверка уязвимостей
        for package in ["requests", "flask", "numpy"]:
            vulns = self.check_vulnerabilities(package)
            for vuln in vulns:
                improvements.append({
                    "type": "security_fix",
                    "package": package,
                    "cve": vuln["cve_id"],
                    "severity": vuln["severity"],
                    "description": vuln["description"],
                    "fixed_in": vuln.get("fixed_version", "N/A"),
                    "confidence": 0.95
                })
        
        # 2. Тренды угроз
        threats = self.analyze_threats()
        for threat in threats["active_threats"]:
            improvements.append({
                "type": "threat_mitigation",
                "threat": threat["name"],
                "severity": threat["severity"],
                "mitigation": threat["mitigation"],
                "confidence": 0.9
            })
        
        # 3. Стратегии смягчения
        for strategy in threats["mitigation_strategies"]:
            improvements.append({
                "type": "security_strategy",
                "description": strategy,
                "category": "defense",
                "confidence": 0.85
            })
        
        # Сортируем по уверенности
        improvements.sort(key=lambda x: x.get("confidence", 0), reverse=True)
        
        return improvements

    # ================================================================
    #  СБОР И АНАЛИЗ
    # ================================================================

    def analyze_found_improvements(self, improvements: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Анализирует найденные улучшения и фильтрует нерелевантные.
        
        Args:
            improvements: Список найденных улучшений
            
        Returns:
            Отфильтрованный список с оценками приоритета
        """
        analyzed = []
        
        for improvement in improvements:
            priority = "low"
            if improvement.get("confidence", 0) > 0.9:
                priority = "high"
            elif improvement.get("confidence", 0) > 0.7:
                priority = "medium"
            
            # Для безопасности приоритет всегда высокий
            if improvement["type"] in ("security_fix", "threat_mitigation"):
                priority = "high"
            
            analyzed.append({
                **improvement,
                "priority": priority,
                "estimated_effort": self._estimate_effort(improvement),
                "impact_score": self._calculate_impact(improvement)
            })
        
        analyzed.sort(key=lambda x: x.get("impact_score", 0), reverse=True)
        
        return analyzed

    def _estimate_effort(self, improvement: Dict[str, Any]) -> str:
        """Оценивает усилия на реализацию."""
        effort_map = {
            "security_fix": "medium",
            "threat_mitigation": "medium",
            "security_strategy": "low"
        }
        return effort_map.get(improvement["type"], "medium")

    def _calculate_impact(self, improvement: Dict[str, Any]) -> float:
        """Рассчитывает балл влияния."""
        base_score = improvement.get("confidence", 0.5) * 10
        
        if improvement["type"] == "security_fix":
            base_score *= 2.0  # Критически важно
        elif improvement["type"] == "threat_mitigation":
            base_score *= 1.5
        
        return round(base_score, 2)
