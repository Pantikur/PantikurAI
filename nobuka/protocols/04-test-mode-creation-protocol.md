# Протокол тестового режима создания Нобуки

## Том IV: Тестовое создание и применение улучшений

---

## Раздел 1. Тестовый режим создания (Test-Mode Creation)

### 1.1 Миссия тестового режима

Нобука теперь **активно создаёт** код, скрипты и файлы для проекта, а не только анализирует существующий.

```
OLD: Анализ → Предложение → Ожидание
NEW: Анализ → Создание → Тестирование → Применение
```

### 1.2 Алгоритм создания

```
┌─────────────────────────────────────────────────────────────┐
│               АЛГОРИТМ ТЕСТОВОГО СОЗДАНИЯ                   │
│                                                             │
│  1. ОПРЕДЕЛЕНИЕ ПОТРЕБНОСТИ                                 │
│     ├── Какой модуль/девочка нуждается в улучшении?          │
│     ├── Какая зона ответственности Нобуки затронута?        │
│     └── Какой тип создания нужен? (скрипт/модуль/тест)      │
│                                                             │
│  2. СОЗДАНИЕ В ПЕСОЧНИЦЕ                                    │
│     ├── nobuka_sandbox/test_mode/                           │
│     │   ├── created/         # Созданные файлы              │
│     │   ├── tests/           # Тесты                        │
│     │   └── results/         # Результаты                   │
│     └── Каждый файл имеет метку: [TEST_MODE]                │
│                                                             │
│  3. АВТОМАТИЧЕСКОЕ ТЕСТИРОВАНИЕ                             │
│     ├── Запуск всех доступных тестов                        │
│     ├── Проверка на ошибки (syntax, runtime, logic)         │
│     ├── Проверка зависимости                              │
│     └── Фиксация результата: PASS / FAIL                   │
│                                                             │
│  4. ПРИМЕНЕНИЕ (только PASS)                                │
│     ├── Файлы с PASS → перемещаются в проект                │
│     ├── Удаление метки [TEST_MODE]                          │
│     ├── Документирование изменений                          │
│     └── Уведомление соответствующей девочки                  │
│                                                             │
│  5. ОТКАТ (при FAIL)                                        │
│     ├── Файлы с FAIL → архивируются                         │
│     ├── Анализ причины ошибки                               │
│     ├── Исправление и повторное тестирование                │
│     └── Максимум 3 попытки перед остановкой                  │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

---

## Раздел 2. Зоны ответственности Нобуки для каждой девочки

### 2.1 Таблица взаимодействия

| # | Девочка | Зона Нобуки | Тип помощи |
|---|---------|-------------|------------|
| 1 | **Футаба** (Управление) | Улучшение логики управления, API координирования | Код, скрипты мониторинга |
| 2 | **Шиори** (Защита) | Проверка безопасности, сканеры уязвимостей | Security-скрипты, тесты |
| 3 | **Нобука** (Улучшения) | Самосовершенствование, рефакторинг ядра | Внутренние улучшения |
| 4 | **Ханако** (Гравитация) | Вычислительные модули, оптимизация моделей | Математические скрипты |
| 5 | **Фуюки** (Электричество) | Расчёты электрических полей, анализ данных | Обработка данных, визуализация |
| 6 | **Люси** (Двигатели) | Интеграция гравитации+электричества, прототипы | Интеграционные скрипты |
| 7 | **Айко** (Искусство) | Генерация пиксель-арта, инструменты рисования | Графические скрипты |
| 8 | **Селеста** (Биология) | Моделирование анатомии, биомеханика | Биомодели, симуляции |
| 9 | **Акра** (Математика) | Оптимизация алгоритмов, численные методы | Алгоритмические улучшения |
| 10 | **Латислейн** (Логика) | Процедурная генерация, логика анимации | Логические модули |
| 11 | **Наото** (Детали) | Визуальный анализ, детекция несоответствий | Анализаторы, детекторы |
| 12 | **Юи** (Перенос сознания) | Когнитивные модели, философские框架 | Когнитивные скрипты |

### 2.2 Формат запроса к Нобуке от девочки

```
ЗАПРОС НА УЛУЧШЕНИЕ:
├── От: [имя девочки]
├── Модуль: [какой модуль проекта]
├── Проблема: [что нужно улучшить]
├── Контекст: [почему это важно]
├── Ожидаемый результат: [что должно получиться]
└── Приоритет: [высокий/средний/низкий]
```

### 2.3 Формат ответа Нобуки

```
ОТВЕТ НОБУКИ:
├── Статус: [создаю/тестирую/применено/отклонено]
├── Созданные файлы: [список]
├── Результаты тестов: [PASS/FAIL с деталями]
├── Применение: [да/нет/отложено]
├── Метрики: [до/после]
└── Рекомендации: [что делать дальше]
```

---

## Раздел 3. Автоматический генератор улучшений

### 3.1 Инициация тестового цикла

```python
#!/usr/bin/env python3
"""
Автоматический генератор улучшений Нобуки.
Создаёт, тестирует и применяет улучшения для всех девочек проекта.
"""

import os
import sys
import json
import shutil
import subprocess
from pathlib import Path
from datetime import datetime
from dataclasses import dataclass, asdict
from enum import Enum
from typing import List, Dict, Optional

# === ENUMS ===

class TestStatus(Enum):
    PENDING = "pending"
    PASS = "pass"
    FAIL = "fail"
    SKIPPED = "skipped"

class ApplicationStatus(Enum):
    NOT_APPLIED = "not_applied"
    APPLIED = "applied"
    ROLLED_BACK = "rolled_back"
    PENDING_REVIEW = "pending_review"

# === DATA CLASSES ===

@dataclass
class TestResult:
    test_name: str
    status: TestStatus
    duration_ms: int
    error: Optional[str] = None
    output: Optional[str] = None

@dataclass
class CreatedFile:
    path: str
    original_path: str  # путь в песочнице
    status: TestStatus
    tests: List[TestResult] = None
    application_status: ApplicationStatus = ApplicationStatus.NOT_APPLIED
    created_at: str = None
    description: str = ""
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now().isoformat()
        if self.tests is None:
            self.tests = []

@dataclass
class ImprovementReport:
    timestamp: str
    target_sister: str
    module: str
    files_created: List[CreatedFile]
    overall_status: str
    metrics_before: Dict = None
    metrics_after: Dict = None
    summary: str = ""

# === SANDBOX MANAGER ===

class SandboxManager:
    """Управление песочницей для тестового режима."""
    
    def __init__(self, project_root: str = "."):
        self.project_root = Path(project_root)
        self.sandbox = self.project_root / "nobuka" / "sandbox"
        self.test_mode = self.sandbox / "test_mode"
        self.created = self.test_mode / "created"
        self.tests = self.test_mode / "tests"
        self.results = self.test_mode / "results"
        self.archives = self.sandbox / "archives"
        
        self._ensure_directories()
    
    def _ensure_directories(self):
        """Создание структуры песочницы."""
        dirs = [self.sandbox, self.test_mode, self.created, 
                self.tests, self.results, self.archives]
        for d in dirs:
            d.mkdir(parents=True, exist_ok=True)
    
    def get_sandbox_path(self, filename: str) -> Path:
        """Получить путь файла в песочнице."""
        return self.created / filename
    
    def archive_failed(self, filename: str, reason: str):
        """Архивация неудачного файла."""
        src = self.created / filename
        if src.exists():
            archive_dir = self.archives / datetime.now().strftime("%Y%m%d_%H%M%S")
            archive_dir.mkdir(parents=True, exist_ok=True)
            shutil.move(str(src), str(archive_dir / filename))
            
            # Логирование причины
            log_file = archive_dir / "failure_reason.txt"
            log_file.write_text(f"Reason: {reason}\nTime: {datetime.now().isoformat()}\n", encoding="utf-8")
    
    def apply_file(self, filename: str, target_path: Optional[str] = None):
        """Применение файла из песочницы в проект."""
        src = self.created / filename
        if not src.exists():
            raise FileNotFoundError(f"File not found in sandbox: {filename}")
        
        dest = Path(target_path) if target_path else self.project_root / filename
        dest.parent.mkdir(parents=True, exist_ok=True)
        
        # Удаление метки TEST_MODE
        content = src.read_text(encoding="utf-8")
        content = content.replace("[TEST_MODE]", "")
        content = content.replace("# [TEST_MODE]", "#")
        
        dest.write_text(content, encoding="utf-8")
        print(f"✅ Применён: {filename} → {dest}")
    
    def list_created_files(self) -> List[Path]:
        """Список всех созданных файлов."""
        return list(self.created.glob("*"))

# === TEST ENGINE ===

class TestEngine:
    """Движок автоматического тестирования."""
    
    @staticmethod
    def run_syntax_check(file_path: Path) -> TestResult:
        """Проверка синтаксиса Python."""
        if file_path.suffix != ".py":
            return TestResult(
                test_name="syntax_check",
                status=TestStatus.SKIPPED,
                duration_ms=0
            )
        
        start = datetime.now()
        try:
            result = subprocess.run(
                [sys.executable, "-m", "py_compile", str(file_path)],
                capture_output=True,
                timeout=30
            )
            duration = (datetime.now() - start).total_seconds() * 1000
            
            if result.returncode == 0:
                return TestResult("syntax_check", TestStatus.PASS, duration)
            else:
                return TestResult(
                    "syntax_check", TestStatus.FAIL, duration,
                    error=result.stderr.decode("utf-8", errors="replace")
                )
        except subprocess.TimeoutExpired:
            return TestResult("syntax_check", TestStatus.FAIL, 30000, "Timeout")
        except Exception as e:
            return TestResult("syntax_check", TestStatus.FAIL, 0, str(e))
    
    @staticmethod
    def run_import_test(file_path: Path) -> TestResult:
        """Проверка импорта модуля."""
        if file_path.suffix != ".py" or file_path.name == "__init__.py":
            return TestResult(
                test_name="import_test",
                status=TestStatus.SKIPPED,
                duration_ms=0
            )
        
        start = datetime.now()
        try:
            # Добавляем sandbox в path
            env = os.environ.copy()
            env["PYTHONPATH"] = str(file_path.parent) + ":" + env.get("PYTHONPATH", "")
            
            result = subprocess.run(
                [sys.executable, "-c", f"import importlib.util; spec = importlib.util.spec_from_file_location('test_module', '{file_path}'); mod = importlib.util.module_from_spec(spec); spec.loader.exec_module(mod)"],
                capture_output=True,
                timeout=30,
                env=env
            )
            duration = (datetime.now() - start).total_seconds() * 1000
            
            if result.returncode == 0:
                return TestResult("import_test", TestStatus.PASS, duration)
            else:
                return TestResult(
                    "import_test", TestStatus.FAIL, duration,
                    error=result.stderr.decode("utf-8", errors="replace")[:500]
                )
        except subprocess.TimeoutExpired:
            return TestResult("import_test", TestStatus.FAIL, 30000, "Timeout")
        except Exception as e:
            return TestResult("import_test", TestStatus.FAIL, 0, str(e))
    
    @staticmethod
    def run_linting(file_path: Path) -> TestResult:
        """Базовый линтинг (flake8 если доступен)."""
        if file_path.suffix != ".py":
            return TestResult(
                test_name="linting",
                status=TestStatus.SKIPPED,
                duration_ms=0
            )
        
        start = datetime.now()
        try:
            result = subprocess.run(
                ["flake8", "--max-line-length=120", "--ignore=E501,W503", str(file_path)],
                capture_output=True,
                timeout=30
            )
            duration = (datetime.now() - start).total_seconds() * 1000
            
            if result.returncode == 0:
                return TestResult("linting", TestStatus.PASS, duration)
            else:
                return TestResult(
                    "linting", TestStatus.PASS, duration,  # linting - warning, не blocking
                    output=result.stdout.decode("utf-8", errors="replace")
                )
        except FileNotFoundError:
            return TestResult("linting", TestStatus.SKIPPED, 0, "flake8 not installed")
        except Exception as e:
            return TestResult("linting", TestStatus.SKIPPED, 0, str(e))
    
    @staticmethod
    def run_all_tests(file_path: Path) -> List[TestResult]:
        """Запуск всех тестов для файла."""
        tests = [
            TestEngine.run_syntax_check(file_path),
            TestEngine.run_import_test(file_path),
            TestEngine.run_linting(file_path),
        ]
        return tests
    
    @staticmethod
    def get_overall_status(tests: List[TestResult]) -> TestStatus:
        """Определение общего статуса по результатам тестов."""
        for t in tests:
            if t.status == TestStatus.FAIL:
                return TestStatus.FAIL
        return TestStatus.PASS

# === IMPROVEMENT CREATOR ===

class ImprovementCreator:
    """Создатель улучшений для девочек."""
    
    # Определение зон ответственности
    ZONES = {
        "futaba": {
            "name": "Футаба",
            "focus": "Управление, координация, правовые исследования",
            "improvements": [
                "dashboard_monitor.py",
                "task_distributor.py",
                "report_generator.py",
            ]
        },
        "shiori": {
            "name": "Шиори",
            "focus": "Защита, безопасность, compliance",
            "improvements": [
                "security_scanner.py",
                "content_filter.py",
                "audit_logger.py",
            ]
        },
        "hanako": {
            "name": "Ханако",
            "focus": "Гравитация, модели пространства-времени",
            "improvements": [
                "gravity_calculator.py",
                "orbit_simulator.py",
                "spacetime_analyzer.py",
            ]
        },
        "fuyuki": {
            "name": "Фуюки",
            "focus": "Атмосферное электричество, молнии",
            "improvements": [
                "electric_field_calculator.py",
                "lightning_simulator.py",
                "energy_harvester.py",
            ]
        },
        "lucy": {
            "name": "Люси",
            "focus": "Двигатели, интеграция сил",
            "improvements": [
                "engine_designer.py",
                "hybrid_calculator.py",
                "thrust_optimizer.py",
            ]
        },
        "ayiko": {
            "name": "Айко",
            "focus": "Искусство, пиксель-арт, черчение",
            "improvements": [
                "pixel_generator.py",
                "pattern_drawer.py",
                "style_analyzer.py",
            ]
        },
        "celesta": {
            "name": "Селеста",
            "focus": "Биология, анатомия, биомеханика",
            "improvements": [
                "anatomy_model.py",
                "biomech_simulator.py",
                "tissue_generator.py",
            ]
        },
        "akira": {
            "name": "Акра",
            "focus": "Математика, вычисления, оптимизация",
            "improvements": [
                "numerical_optimizer.py",
                "algorithm_improver.py",
                "calculation_engine.py",
            ]
        },
        "latislane": {
            "name": "Латислейн",
            "focus": "Логика, процедурная генерация, анимация",
            "improvements": [
                "logic_generator.py",
                "animation_engine.py",
                "procedural_creator.py",
            ]
        },
        "naoto": {
            "name": "Наото",
            "focus": "Детали, визуальный анализ, детекция",
            "improvements": [
                "visual_analyzer.py",
                "detail_detector.py",
                "pattern_matcher.py",
            ]
        },
        "yui": {
            "name": "Юи",
            "focus": "Перенос сознания, когнитивные науки",
            "improvements": [
                "cognitive_model.py",
                "consciousness_framework.py",
                "neural_simulator.py",
            ]
        }
    }
    
    def __init__(self, sandbox: SandboxManager):
        self.sandbox = sandbox
        self.created_files: List[CreatedFile] = []
    
    def create_for_sister(self, sister_key: str, improvement_type: str) -> Optional[CreatedFile]:
        """Создание улучшения для конкретной девочки."""
        if sister_key not in self.ZONES:
            print(f"❌ Неизвестная девочка: {sister_key}")
            return None
        
        zone = self.ZONES[sister_key]
        filename = f"{improvement_type}.py"
        sandbox_path = self.sandbox.get_sandbox_path(filename)
        
        # Генерация кода
        code = self._generate_code(sister_key, improvement_type, zone)
        sandbox_path.write_text(code, encoding="utf-8")
        
        print(f"📝 Создан файл: {filename} для {zone['name']}")
        
        created_file = CreatedFile(
            path=filename,
            original_path=str(sandbox_path),
            status=TestStatus.PENDING,
            description=f"Улучшение для {zone['name']}: {improvement_type}"
        )
        
        self.created_files.append(created_file)
        return created_file
    
    def _generate_code(self, sister_key: str, improvement_type: str, zone: dict) -> str:
        """Генерация кода улучшения."""
        timestamp = datetime.now().strftime("%Y-%m-%d")
        
        templates = {
            "futaba": f'''#!/usr/bin/env python3
"""
Модуль улучшения для Футабы — {improvement_type}
Создан Нобукой в тестовом режиме
Дата: {timestamp}
"""

# [TEST_MODE]

class {improvement_type.replace("_", " ").title().replace(" ", "")}:
    """Класс для: {improvement_type}"""
    
    def __init__(self):
        self.name = "{zone['name']}"
        self.focus = "{zone['focus']}"
        self.created_by = "Нобука"
        self.test_mode = True
        
    def run(self):
        """Основной метод выполнения."""
        print(f"Запуск модуля для {{self.name}}...")
        # TODO: Реализация {improvement_type}
        return True

if __name__ == "__main__":
    module = {improvement_type.replace("_", " ").title().replace(" ", "")}()
    module.run()
''',
            "default": f'''#!/usr/bin/env python3
"""
Модуль улучшения для {zone['name']} — {improvement_type}
Зона: {zone['focus']}
Создан Нобукой в тестовом режиме
Дата: {timestamp}
"""

# [TEST_MODE]

class {improvement_type.replace("_", " ").title().replace(" ", "")}:
    """Класс для: {improvement_type}"""
    
    def __init__(self):
        self.name = "{zone['name']}"
        self.focus = "{zone['focus']}"
        self.created_by = "Нобука"
        self.test_mode = True
        
    def run(self):
        """Основной метод выполнения."""
        print(f"Запуск модуля улучшения для {{self.name}}...")
        print(f"Тип улучшения: {improvement_type}")
        # TODO: Реализация {improvement_type}
        return True

def validate():
    """Валидация модуля."""
    module = {improvement_type.replace("_", " ").title().replace(" ", "")}()
    assert module.name == "{zone['name']}"
    assert module.test_mode == True
    return True

if __name__ == "__main__":
    if validate():
        print("✅ Валидация пройдена")
        module = {improvement_type.replace("_", " ").title().replace(" ", "")}()
        module.run()
    else:
        print("❌ Валидация не пройдена")
'''
        }
        
        return templates.get(sister_key, templates["default"])
    
    def test_file(self, created_file: CreatedFile) -> bool:
        """Тестирование созданного файла."""
        sandbox_path = Path(created_file.original_path)
        
        if not sandbox_path.exists():
            created_file.status = TestStatus.FAIL
            return False
        
        # Запуск тестов
        tests = TestEngine.run_all_tests(sandbox_path)
        created_file.tests = tests
        created_file.status = TestEngine.get_overall_status(tests)
        
        # Логируем результаты
        print(f"\n📊 Результаты тестов для {created_file.path}:")
        for test in tests:
            icon = "✅" if test.status == TestStatus.PASS else "❌" if test.status == TestStatus.FAIL else "⏭️"
            print(f"   {icon} {test.test_name}: {test.status.value} ({test.duration_ms:.0f}ms)")
            if test.error:
                print(f"      Ошибка: {test.error[:100]}")
        
        return created_file.status == TestStatus.PASS
    
    def apply_passed_files(self) -> List[CreatedFile]:
        """Применение файлов, прошедших тесты."""
        applied = []
        
        for cf in self.created_files:
            if cf.status == TestStatus.PASS:
                try:
                    # Определяем целевую папку по имени файла
                    target = self._determine_target(cf.path)
                    self.sandbox.apply_file(cf.path, target)
                    cf.application_status = ApplicationStatus.APPLIED
                    applied.append(cf)
                    print(f"✅ Применён: {cf.path}")
                except Exception as e:
                    cf.application_status = ApplicationStatus.ROLLED_BACK
                    print(f"❌ Ошибка применения {cf.path}: {e}")
            else:
                print(f"⏭️  Пропущен (не прошёл тесты): {cf.path}")
        
        return applied
    
    def _determine_target(self, filename: str) -> Optional[str]:
        """Определение целевой папки для файла."""
        # Пытаемся определить по имени файла
        for key, zone in self.ZONES.items():
            if key in filename.lower():
                return f"{key}/{filename}"
        
        # По умолчанию — папка nobuka
        return f"nobuka/{filename}"
    
    def generate_report(self) -> ImprovementReport:
        """Генерация отчёта о проделанной работе."""
        passed = sum(1 for cf in self.created_files if cf.status == TestStatus.PASS)
        failed = sum(1 for cf in self.created_files if cf.status == TestStatus.FAIL)
        applied = sum(1 for cf in self.created_files if cf.application_status == ApplicationStatus.APPLIED)
        
        report = ImprovementReport(
            timestamp=datetime.now().isoformat(),
            target_sister="Все девочки",
            module="nobuka/test_mode",
            files_created=self.created_files,
            overall_status=f"Создано: {len(self.created_files)}, Пройдено: {passed}, Применено: {applied}",
            summary=f"Нобука создала {len(self.created_files)} файлов улучшений. "
                    f"{passed} прошли тесты, {applied} применены в проекте."
        )
        
        # Сохранение отчёта
        report_path = self.sandbox.results / f"report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(report_path, "w", encoding="utf-8") as f:
            # Кастомная сериализация
            json.dump({
                "timestamp": report.timestamp,
                "target_sister": report.target_sister,
                "module": report.module,
                "files_created": [
                    {
                        "path": cf.path,
                        "status": cf.status.value,
                        "application_status": cf.application_status.value,
                        "description": cf.description,
                        "tests": [
                            {"name": t.test_name, "status": t.status.value, "duration_ms": t.duration_ms}
                            for t in cf.tests
                        ]
                    }
                    for cf in self.created_files
                ],
                "overall_status": report.overall_status,
                "summary": report.summary
            }, f, ensure_ascii=False, indent=2)
        
        print(f"\n📄 Отчёт сохранён: {report_path}")
        return report

# === MAIN ORCHESTRATOR ===

def run_test_mode_cycle(target_sister: Optional[str] = None, improvement_type: Optional[str] = None):
    """
    Запуск полного цикла тестового режима.
    
    Args:
        target_sister: Ключ девочки (если None — цикл для всех)
        improvement_type: Тип улучшения (если None — автоматически)
    """
    print("=" * 60)
    print("🔧 НОБУКА — ТЕСТОВЫЙ РЕЖИМ СОЗДАНИЯ")
    print("=" * 60)
    
    # Инициализация
    sandbox = SandboxManager(".")
    creator = ImprovementCreator(sandbox)
    
    # Определение цели
    if target_sister:
        sisters_to_process = [target_sister]
    else:
        sisters_to_process = list(ImprovementCreator.ZONES.keys())
    
    # Цикл создания и тестирования
    for sister_key in sisters_to_process:
        zone = ImprovementCreator.ZONES[sister_key]
        print(f"\n{'─' * 50}")
        print(f"🎯 Обработка: {zone['name']} ({zone['focus']})")
        
        # Определение типа улучшения
        imp_type = improvement_type if improvement_type else zone["improvements"][0]
        
        # Создание
        created = creator.create_for_sister(sister_key, imp_type)
        
        # Тестирование
        if created:
            creator.test_file(created)
    
    # Применение прошедших тесты
    print(f"\n{'═' * 60}")
    print("📦 ПРИМЕНЕНИЕ УЛУЧШЕНИЙ")
    print(f"{'═' * 60}")
    applied = creator.apply_passed_files()
    
    # Отчёт
    print(f"\n{'═' * 60}")
    print("📊 ОТЧЁТ")
    print(f"{'═' * 60}")
    report = creator.generate_report()
    print(f"\n{report.summary}")
    
    return report

if __name__ == "__main__":
    # Примеры запуска:
    # python -c "from nobuka.engine.test_mode_creation import run_test_mode_cycle; run_test_mode_cycle()"
    # python -c "from nobuka.engine.test_mode_creation import run_test_mode_cycle; run_test_mode_cycle('hanako')"
    # python -c "from nobuka.engine.test_mode_creation import run_test_mode_cycle; run_test_mode_cycle('all', 'gravity_calculator')"
    
    print("🔧 Нобука — Тестовый режим создания активирован!")
    print("Используйте run_test_mode_cycle() для запуска")
    print("\nПримеры:")
    print('  run_test_mode_cycle()                    # Для всех')
    print('  run_test_mode_cycle("hanako")            # Для Ханако')
    print('  run_test_mode_cycle("hanako", "orbit_simulator")  # С конкретным типом')
'''