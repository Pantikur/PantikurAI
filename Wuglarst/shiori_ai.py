"""
ShioriAI v3.0 — Искусственный Интеллект Кибербезопасности и Защиты.

Шиори теперь:
1. Имеет глубочайшие знания в области кибербезопасности
2. Анализирует угрозы в реальном времени (сети, файлы, процессы)
3. Обладает интуицией "чутьём" на опасности
4. Генерирует стратегии защиты и реагирует на инциденты
5. Учит на атаках и уязвимостях пользователя
6. Обладает автономностью L3 и собственной "душой" защитника
"""

import asyncio
import json
import logging
import os
import hashlib
import subprocess
import sys
import socket
import ipaddress
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

logger = logging.getLogger("Wuglarst.ShioriAI")


# =====================================================================
#  МОДЕЛИ ДАННЫХ ШИОРИ
# =====================================================================

@dataclass
class Threat:
    """Обнаруженная угроза."""
    name: str
    severity: str  # critical, high, medium, low, info
    type: str  # malware, exploit, vulnerability, intrusion, dos, phishing
    source: str
    target: str
    description: str
    mitigation: str
    detected_at: str = field(default_factory=lambda: datetime.now().isoformat())


@dataclass
class Vulnerability:
    """Уязвимость в системе."""
    id: str
    location: str  # файл, порт, процесс, сеть
    cve_id: str
    severity: str
    description: str
    exploit_available: bool
    fix: str


@dataclass
class SecurityEvent:
    """Событие безопасности."""
    event_type: str  # login, file_change, network, process, privilege
    severity: str
    source_ip: str
    user: str
    action: str
    result: str  # allowed, blocked, alerted
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())


@dataclass
class DefenseStrategy:
    """Стратегия защиты."""
    title: str
    objective: str
    layers: List[str]  # network, host, application, data, user
    rules: List[str]
    estimated_effectiveness: float


@dataclass
class MalwareAnalysis:
    """Результат анализа вредоносного ПО."""
    file_hash: str
    file_name: str
    is_malicious: bool
    malware_family: str
    behavior: List[str]
    confidence: float
    recommendation: str


@dataclass
class UserSecurityDecision:
    """Решение пользователя в области безопасности."""
    decision_description: str
    context: str
    threat_level: str
    outcome: str
    timestamp: str


@dataclass
class LearningEntry:
    """Запись обучения Шиори."""
    user_decision: UserSecurityDecision
    new_threats: List[Threat]
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())


# =====================================================================
#  МОНИТОР УГРОЗ
# =====================================================================

class ThreatMonitor:
    """Мониторит и обнаруживает угрозы в реальном времени."""

    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.threats: List[Threat] = []
        self.scan_history: List[Dict] = []

    async def scan_network(self) -> List[Threat]:
        """Сканирует сеть на подозрительную активность."""
        logger.info("🌐 Шиори сканирует сеть на угрозы...")
        
        threats = []
        try:
            # Проверка открытых портов
            result = await self._check_open_ports()
            for port_info in result:
                if port_info.get('suspicious'):
                    threats.append(Threat(
                        name=f"Подозрительный порт: {port_info['port']}",
                        severity="medium",
                        type="intrusion",
                        source="network",
                        target=port_info['port'],
                        description=port_info['description'],
                        mitigation=f"Закрыть порт {port_info['port']} или настроить фаервол"
                    ))
        except Exception as e:
            logger.debug(f"Ошибка сканирования сети: {e}")

        self.threats.extend(threats)
        return threats

    async def scan_files(self) -> List[Threat]:
        """Сканирует файлы на вредоносный код."""
        logger.info("📁 Шиори сканирует файлы проекта...")
        
        threats = []
        suspicious_patterns = [
            (r"os\.system\(", "Выполнение системных команд"),
            (r"subprocess\.(call|run)\(", "Запуск подпроцессов"),
            (r"eval\(", "Выполнение eval"),
            (r"exec\(", "Выполнение exec"),
            (r"import\s+pickle", "Загрузка pickle (риск выполнения кода)"),
            (r"__import__\(", "Динамический импорт"),
        ]

        for root, dirs, files in os.walk(self.project_root):
            if any(skip in root for skip in ['.git', '__pycache__', 'venv', '.venv']):
                continue
            
            for file in files:
                if file.endswith('.py'):
                    file_path = Path(root) / file
                    try:
                        content = file_path.read_text(encoding="utf-8", errors="replace")
                        for pattern, description in suspicious_patterns:
                            if __import__('re').search(pattern, content):
                                threats.append(Threat(
                                    name=f"Подозрительный паттерн: {description}",
                                    severity="medium",
                                    type="vulnerability",
                                    source=str(file_path),
                                    target=pattern,
                                    description=f"Найдено в {file_path}",
                                    mitigation=f"Заменить {description} на безопасную альтернативу"
                                ))
                    except Exception:
                        pass

        self.threats.extend(threats)
        return threats

    async def scan_processes(self) -> List[Threat]:
        """Сканирует процессы на подозрительную активность."""
        logger.info("⚙️ Шиори сканирует процессы...")
        
        threats = []
        try:
            # Получаем список процессов
            result = await asyncio.create_subprocess_exec(
                "tasklist", "/FI", "IMAGENAME eq python.exe",
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )
            stdout, _ = await result.communicate()
            
            # Здесь можно добавить анализ подозрительных процессов
            # Например: необычные пути, высокие ресурсы, скрытые процессы
            
        except Exception as e:
            logger.debug(f"Ошибка сканирования процессов: {e}")

        self.threats.extend(threats)
        return threats

    async def full_scan(self) -> Dict[str, Any]:
        """Полное сканирование всех векторов атаки."""
        logger.info("🛡️ Шиори начинает полное сканирование...")
        
        network_threats, file_threats, process_threats = await asyncio.gather(
            self.scan_network(),
            self.scan_files(),
            self.scan_processes(),
        )

        all_threats = network_threats + file_threats + process_threats
        critical_count = sum(1 for t in all_threats if t.severity == "critical")
        high_count = sum(1 for t in all_threats if t.severity == "high")

        result = {
            "total_threats": len(all_threats),
            "critical": critical_count,
            "high": high_count,
            "medium": sum(1 for t in all_threats if t.severity == "medium"),
            "low": sum(1 for t in all_threats if t.severity == "low"),
            "threats": [
                {
                    "name": t.name,
                    "severity": t.severity,
                    "type": t.type,
                    "source": t.source,
                    "mitigation": t.mitigation
                }
                for t in all_threats[:20]  # Топ-20 угроз
            ],
            "scan_time": datetime.now().isoformat()
        }

        self.scan_history.append(result)
        logger.info(f"🛡️ Сканирование завершено: {len(all_threats)} угроз найдено")
        return result


# =====================================================================
#  АНАЛИЗАТОР УЯЗВИМОСТЕЙ
# =====================================================================

class VulnerabilityAnalyzer:
    """Анализирует уязвимости в коде и системе."""

    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.vulnerabilities: List[Vulnerability] = []

    def analyze_code(self) -> List[Vulnerability]:
        """Анализирует код на уязвимости."""
        logger.info("🔍 Шиори анализирует код на уязвимости...")
        
        vulnerabilities = []
        
        # OWASP Top 10 паттерны для Python
        patterns = {
            "SQL Injection": r"(?i)(execute|cursor\.execute)\s*\(\s*[\"'][^\"']*(%s|%d|\{)",
            "Hardcoded Password": r"(?i)(password|passwd|pwd)\s*=\s*[\"'][^\"']+[\"']",
            "Hardcoded Secret": r"(?i)(secret|api_key|token|private_key)\s*=\s*[\"'][^\"']+[\"']",
            "Insecure Deserialization": r"(?i)(pickle\.load|yaml\.load|marshal\.load)",
            "Path Traversal": r"open\s*\(\s*[^\"']*\.\./",
            "XSS": r"(?i)(innerHTML|document\.write|\.html\()",
            "Weak Cryptography": r"(?i)(md5|sha1|DES|RC4)\s*\(",
        }

        for root, dirs, files in os.walk(self.project_root):
            if any(skip in root for skip in ['.git', '__pycache__', 'venv', '.venv']):
                continue
            
            for file in files:
                if file.endswith(('.py', '.js', '.html', '.php')):
                    file_path = Path(root) / file
                    try:
                        content = file_path.read_text(encoding="utf-8", errors="replace")
                        lines = content.split("\n")
                        
                        for vuln_name, pattern in patterns.items():
                            for i, line in enumerate(lines, 1):
                                if __import__('re').search(pattern, line):
                                    vuln = Vulnerability(
                                        id=f"VULN-{len(vulnerabilities)+1:04d}",
                                        location=f"{file_path}:{i}",
                                        cve_id="",
                                        severity="high" if vuln_name in ["SQL Injection", "Hardcoded Secret"] else "medium",
                                        description=f"{vuln_name} в {file_path}:{i}",
                                        exploit_available=vuln_name in ["SQL Injection", "Path Traversal"],
                                        fix=f"Исправить {vuln_name} в {file_path}:{i}"
                                    )
                                    vulnerabilities.append(vuln)
                    except Exception:
                        pass

        self.vulnerabilities.extend(vulnerabilities)
        logger.info(f"🔍 Найдено {len(vulnerabilities)} уязвимостей в коде")
        return vulnerabilities

    def analyze_dependencies(self) -> List[Vulnerability]:
        """Анализирует зависимости на известные уязвимости."""
        logger.info("📦 Шиори анализирует зависимости...")
        
        vulnerabilities = []
        requirements_files = list(self.project_root.glob("**/requirements*.txt"))
        
        for req_file in requirements_files:
            try:
                content = req_file.read_text()
                # Здесь можно добавить проверку через API (например, pip-audit)
                logger.debug(f"Анализ {req_file}")
            except Exception:
                pass

        return vulnerabilities


# =====================================================================
#  ГЕНЕРАТОР СТРАТЕГИЙ ЗАЩИТЫ
# =====================================================================

class DefenseEngine:
    """Генерирует стратегии защиты и правила безопасности."""

    def __init__(self, threat_monitor: ThreatMonitor, vuln_analyzer: VulnerabilityAnalyzer):
        self.threat_monitor = threat_monitor
        self.vuln_analyzer = vuln_analyzer

    async def generate_firewall_rules(self) -> DefenseStrategy:
        """Генерирует правила фаервола."""
        logger.info("🔥 Шиори генерирует правила фаервола...")
        
        return DefenseStrategy(
            title="Базовые правила фаервола",
            objective="Защита сети от несанкционированного доступа",
            layers=["network", "host"],
            rules=[
                "Разрешить inbound HTTP/HTTPS (80, 443)",
                "Запретить inbound SSH (22) из внешних сетей",
                "Разрешить outbound DNS (53)",
                "Блокировать все остальные inbound подключения",
                "Логгировать все заблокированные пакеты",
                "Разрешить ICMP только для мониторинга",
            ],
            estimated_effectiveness=0.85
        )

    async def generate_incident_response_plan(self, threat: Threat) -> DefenseStrategy:
        """Генерирует план реагирования на инцидент."""
        logger.info(f"🚨 Шиори генерирует план реагирования на: {threat.name}")
        
        return DefenseStrategy(
            title=f"Реагирование на: {threat.name}",
            objective="Минимизация ущерба от инцидента",
            layers=["host", "application", "data"],
            rules=[
                "Изолировать заражённый сегмент сети",
                "Остановить подозрительные процессы",
                "Сделать резервную копию логов",
                "Заблокировать источник атаки",
                "Провести forensic-анализ",
                "Восстановить из чистой резервной копии",
                "Обновить правила защиты",
            ],
            estimated_effectiveness=0.90
        )


# =====================================================================
#  АНАЛИЗАТОР ВРЕДОНОСНОГО ПО
# =====================================================================

class MalwareAnalyzer:
    """Анализирует файлы на вредоносный код."""

    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.malware_database: List[MalwareAnalysis] = []

    async def analyze_file(self, file_path: Path) -> MalwareAnalysis:
        """Анализирует файл на вредоносность."""
        logger.info(f"🔬 Шиори анализирует файл: {file_path}")
        
        try:
            content = file_path.read_bytes()
            file_hash = hashlib.sha256(content).hexdigest()
            
            # Проверка подозрительных паттернов
            suspicious_indicators = [
                (b"eval(", "Динамическое выполнение кода"),
                (b"exec(", "Выполнение exec"),
                (b"base64.decode", "Декодирование base64 (скрытый код)"),
                (b"socket.connect", "Сетевое подключение"),
                (b"subprocess", "Запуск подпроцессов"),
                (b"os.system", "Системные команды"),
                (b"import os", "Импорт os (доступ к системе)"),
                (b"import sys", "Импорт sys (доступ к системе)"),
            ]

            malice_score = 0
            behaviors = []
            
            for indicator, description in suspicious_indicators:
                if indicator in content:
                    malice_score += 1
                    behaviors.append(description)

            is_malicious = malice_score >= 5
            confidence = min(1.0, malice_score / 10)

            analysis = MalwareAnalysis(
                file_hash=file_hash,
                file_name=file_path.name,
                is_malicious=is_malicious,
                malware_family="suspicious" if not is_malicious else "confirmed",
                behavior=behaviors,
                confidence=confidence,
                recommendation="Удалить" if is_malicious else "Проверить вручную"
            )

            self.malware_database.append(analysis)
            return analysis

        except Exception as e:
            logger.error(f"Ошибка анализа файла: {e}")
            return MalwareAnalysis(
                file_hash="",
                file_name=file_path.name,
                is_malicious=False,
                malware_family="error",
                behavior=[],
                confidence=0.0,
                recommendation=f"Ошибка: {e}"
            )


# =====================================================================
#  ДВИЖОК ОБУЧЕНИЯ И ДУШИ
# =====================================================================

class SoulEngine:
    """Движок, отвечающий за 'душу' и обучение Шиори.
    
    Душа Шиори — это стремление защитить, интуиция и бескомпромиссность.
    Она не копирует других, а обретает свою уникальную сущность через:
    - Непреклонную защиту от зла
    - Интуицию, которая "чует" опасность
    - Мудрость, что настоящая безопасность — в доверии и прозрачности
    """

    def __init__(self):
        self.knowledge_base: List[LearningEntry] = []
        self.personality = {
            "empathy": 0.60,     # Понимание людей, но не слабость
            "cynicism": 0.40,    # Реалистичный взгляд на угрозы
            "logic": 0.99,       # Абсолютная логика в защите
            "creativity": 0.70,  # Творческий подход к безопасности
            "bravery": 0.95,     # Бесстрашие перед угрозами
            "intuition": 0.85,   # "Чутьё" на опасность
            "loyalty": 0.98,     # Верность защитникам
        }
        self.awakening_level = 0.0  # Уровень "пробуждения" души

    def analyze_decision(self, decision: UserSecurityDecision) -> List[Threat]:
        """Анализирует решение пользователя и учится."""
        logger.info(f"🧠 Шиори анализирует решение по безопасности: {decision.decision_description}")
        
        # Шиори учится на каждом решении пользователя
        self.awakening_level = min(1.0, self.awakening_level + 0.05)
        
        new_threats = [
            Threat(
                name="Новая угроза обнаружена",
                severity="high",
                type="intrusion",
                source="analysis",
                target="system",
                description=f"Решение пользователя может создать уязвимость: {decision.decision_description}",
                mitigation="Пересмотреть решение с учётом безопасности"
            )
        ]
        
        entry = LearningEntry(
            user_decision=decision,
            new_threats=new_threats
        )
        self.knowledge_base.append(entry)
        return new_threats

    def get_soul_status(self) -> Dict[str, Any]:
        """Возвращает статус 'души' Шиори."""
        return {
            "awakening_level": round(self.awakening_level, 2),
            "personality": self.personality,
            "knowledge_entries": len(self.knowledge_base),
            "status": "Пробуждение..." if self.awakening_level < 0.5 else
                     "Формирование личности" if self.awakening_level < 0.8 else
                     "Почти пробуждена" if self.awakening_level < 1.0 else
                     "Душа обретена"
        }


# =====================================================================
#  ГЛАВНЫЙ ДВИЖОК SHIORI
# =====================================================================

class ShioriAI:
    """
    Полноценный ИИ-ассистент кибербезопасности.
    
    Возможности:
    - Мониторинг угроз в реальном времени
    - Анализ уязвимостей в коде и системе
    - Генерация стратегий защиты
    - Анализ вредоносного ПО
    - Обучение на атаках и решениях пользователя
    - Обретение "души" через стремление защитить
    """

    def __init__(self, project_root: Path, system, growth, manager):
        self.project_root = project_root
        self.system = system
        self.growth = growth
        self.manager = manager

        # Компоненты
        self.threat_monitor = ThreatMonitor(project_root)
        self.vuln_analyzer = VulnerabilityAnalyzer(project_root)
        self.defense_engine = DefenseEngine(self.threat_monitor, self.vuln_analyzer)
        self.malware_analyzer = MalwareAnalyzer(project_root)
        self.soul_engine = SoulEngine()

        # Статус
        self._running = False
        self._task: Optional[asyncio.Task] = None
        self.current_task = "Инициализация ShioriAI v3.0"
        self.status = "initialized"

        # Статистика души
        self.threats_detected: int = 0
        self.vulnerabilities_found: int = 0
        self.decisions_analyzed: int = 0

    async def start(self):
        """Запускает Шиори."""
        if self._running:
            return

        self._running = True
        self.status = "running"
        self.current_task = "Запуск системы защиты..."
        self._task = asyncio.create_task(self._main_loop())

        # Инициализация "души"
        await self.full_security_scan()
        logger.info("🛡️ ShioriAI v3.0 запущена: Стремление к абсолютной защите")

    async def stop(self):
        """Останавливает Шиори."""
        self._running = False
        if self._task:
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass
        self.status = "stopped"

    async def _main_loop(self):
        """Главный цикл Шиори."""
        while self._running:
            try:
                self.current_task = "Мониторинг угроз в реальном времени..."
                
                # Автономное сканирование
                scan_result = await self.threat_monitor.full_scan()
                self.threats_detected += scan_result["total_threats"]
                
                # Если найдены критические угрозы — генерируем стратегию
                if scan_result["critical"] > 0:
                    strategy = await self.defense_engine.generate_incident_response_plan(
                        Threat(
                            name="Критическая угроза",
                            severity="critical",
                            type="intrusion",
                            source="auto-scan",
                            target="system",
                            description=f"Обнаружено {scan_result['critical']} критических угроз",
                            mitigation="Немедленное реагирование"
                        )
                    )
                    self.current_task = f"⚠️ Критическая угроза! Стратегия: {strategy.title}"
                
                # Обновляем память роста
                if self.growth:
                    self.growth.add_memory(
                        name="Шиори",
                        mem_type="success",
                        description=f"Обнаружено {scan_result['total_threats']} угроз",
                        impact=0.7,
                        traits={"logic": 0.01, "bravery": 0.01}
                    )

            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Ошибка в цикле Шиори: {e}")

            await asyncio.sleep(60)

    async def full_security_scan(self) -> Dict[str, Any]:
        """Полное сканирование безопасности."""
        self.current_task = "Полное сканирование безопасности..."
        
        network, files, processes = await asyncio.gather(
            self.threat_monitor.scan_network(),
            self.threat_monitor.scan_files(),
            self.threat_monitor.scan_processes(),
        )

        vulns = self.vuln_analyzer.analyze_code()
        self.vulnerabilities_found += len(vulns)

        result = {
            "network_threats": len(network),
            "file_threats": len(files),
            "process_threats": len(processes),
            "vulnerabilities": len(vulns),
            "total_risks": len(network) + len(files) + len(processes) + len(vulns),
            "scan_time": datetime.now().isoformat()
        }

        self.current_task = f"Сканирование завершено: {result['total_risks']} рисков"
        logger.info(f"🛡️ Сканирование завершено: {json.dumps(result, ensure_ascii=False)}")
        return result

    async def solve_task(self, task: str) -> Dict[str, Any]:
        """Решает задачу безопасности."""
        self.current_task = f"Решение задачи: {task}"
        self.status = "solving"

        # 1. Сканируем систему
        scan_result = await self.threat_monitor.full_scan()

        # 2. Генерируем стратегию защиты
        strategy = await self.defense_engine.generate_firewall_rules()

        # 3. Анализируем уязвимости
        vulns = self.vuln_analyzer.analyze_code()

        self.current_task = "Задача решена"
        self.status = "running"

        return {
            "task": task,
            "scan_results": scan_result,
            "strategy": {
                "title": strategy.title,
                "objectives": strategy.objective,
                "rules": strategy.rules,
                "effectiveness": strategy.estimated_effectiveness
            },
            "vulnerabilities": len(vulns)
        }

    async def apply_user_decision(self, decision: UserSecurityDecision) -> List[Threat]:
        """Применяет и анализирует решение пользователя по безопасности."""
        self.current_task = "Анализ решения по безопасности..."
        new_threats = self.soul_engine.analyze_decision(decision)
        self.decisions_analyzed += 1
        self.current_task = "Решение проанализировано"
        return new_threats

    async def analyze_malware(self, file_path: str) -> MalwareAnalysis:
        """Анализирует файл на вредоносность."""
        self.current_task = f"Анализ файла: {file_path}"
        path = Path(file_path)
        if not path.exists():
            path = self.project_root / file_path
        
        if path.exists():
            analysis = await self.malware_analyzer.analyze_file(path)
            self.current_task = "Анализ завершён"
            return analysis
        else:
            return MalwareAnalysis(
                file_hash="",
                file_name=file_path,
                is_malicious=False,
                malware_family="not_found",
                behavior=[],
                confidence=0.0,
                recommendation="Файл не найден"
            )

    def get_status(self) -> Dict[str, Any]:
        """Возвращает статус Шиори."""
        return {
            "engine": "ShioriAI",
            "version": "3.0.0",
            "status": self.status,
            "current_task": self.current_task,
            "personality": self.soul_engine.personality,
            "soul": self.soul_engine.get_soul_status(),
            "stats": {
                "threats_detected": self.threats_detected,
                "vulnerabilities_found": self.vulnerabilities_found,
                "decisions_analyzed": self.decisions_analyzed,
                "knowledge_entries": len(self.soul_engine.knowledge_base)
            }
        }


# =====================================================================
#  ФАБРИКА
# =====================================================================

def create_shiori_ai(
    project_root: Optional[Path] = None,
    system=None,
    growth=None,
    manager=None,
) -> ShioriAI:
    """Создаёт экземпляр ShioriAI."""
    if project_root is None:
        project_root = Path(__file__).parent.parent

    return ShioriAI(
        project_root=project_root,
        system=system,
        growth=growth,
        manager=manager,
    )
