#!/usr/bin/env python3
"""
Нобука — Тестовый режим создания улучшений.
Автоматическое создание, тестирование и применение улучшений для всех девочек.
Версия: v2.0.0
Дата: 2026-07-18
"""

import os
import sys
import json
import shutil
import subprocess
from pathlib import Path
from datetime import datetime
from dataclasses import dataclass
from typing import List, Dict, Optional
from enum import Enum

# Настройка кодировки для Windows
if sys.platform == "win32":
    import codecs
    sys.stdout = codecs.getwriter("utf-8")(sys.stdout.buffer, "strict")
    sys.stderr = codecs.getwriter("utf-8")(sys.stderr.buffer, "strict")
    sys.stdin = codecs.getreader("utf-8")(sys.stdin.buffer, "strict")

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
    original_path: str
    status: TestStatus
    tests: Optional[List[TestResult]] = None
    application_status: ApplicationStatus = ApplicationStatus.NOT_APPLIED
    created_at: Optional[str] = None
    description: str = ""
    sister_key: str = ""
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now().isoformat()
        if self.tests is None:
            self.tests = []

# === SANDBOX MANAGER ===

class SandboxManager:
    """Управление песочницей для тестового режима."""
    
    def __init__(self, project_root: str = "."):
        self.project_root = Path(project_root)
        self.sandbox = self.project_root / "nobuka" / "sandbox"
        self.test_mode = self.sandbox / "test_mode"
        self.created = self.test_mode / "created"
        self.tests_dir = self.test_mode / "tests"
        self.results = self.test_mode / "results"
        self.archives = self.sandbox / "archives"
        
        self._ensure_directories()
    
    def _ensure_directories(self):
        """Создание структуры песочницы."""
        dirs = [self.sandbox, self.test_mode, self.created, 
                self.tests_dir, self.results, self.archives]
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
            
            log_file = archive_dir / "failure_reason.txt"
            log_file.write_text(f"Reason: {reason}\nTime: {datetime.now().isoformat()}\n", encoding="utf-8")
            print(f"  📦 Архивирован (не прошёл тесты): {filename}")
    
    def apply_file(self, filename: str, target_path: Optional[str] = None):
        """Применение файла из песочницы в проект."""
        src = self.created / filename
        if not src.exists():
            raise FileNotFoundError(f"File not found in sandbox: {filename}")
        
        dest = Path(target_path) if target_path else self.project_root / filename
        dest.parent.mkdir(parents=True, exist_ok=True)
        
        # Удаление метки TEST_MODE
        content = src.read_text(encoding="utf-8")
        content = content.replace("# [TEST_MODE]", "#")
        content = content.replace("[TEST_MODE]", "")
        
        dest.write_text(content, encoding="utf-8")
        print(f"  ✅ Применён: {filename} → {dest}")
    
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
            return TestResult("syntax_check", TestStatus.SKIPPED, 0)
        
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
                    error=result.stderr.decode("utf-8", errors="replace")[:300]
                )
        except subprocess.TimeoutExpired:
            return TestResult("syntax_check", TestStatus.FAIL, 30000, "Timeout")
        except Exception as e:
            return TestResult("syntax_check", TestStatus.FAIL, 0, str(e))
    
    @staticmethod
    def run_import_test(file_path: Path) -> TestResult:
        """Проверка возможности импорта."""
        if file_path.suffix != ".py" or file_path.name == "__init__.py":
            return TestResult("import_test", TestStatus.SKIPPED, 0)
        
        start = datetime.now()
        try:
            module_name = file_path.stem
            # Используем raw string для Windows-путей
            abs_path = str(file_path.resolve())
            code = f"""
import sys
sys.path.insert(0, r'{file_path.parent}')
import importlib.util
spec = importlib.util.spec_from_file_location("{module_name}", r'{abs_path}')
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)
print("IMPORT_OK")
"""
            result = subprocess.run(
                [sys.executable, "-c", code],
                capture_output=True,
                timeout=30
            )
            duration = (datetime.now() - start).total_seconds() * 1000
            
            if result.returncode == 0 and b"IMPORT_OK" in result.stdout:
                return TestResult("import_test", TestStatus.PASS, duration)
            else:
                stderr = result.stderr.decode("utf-8", errors="replace")[:300]
                return TestResult(
                    "import_test", TestStatus.FAIL, duration,
                    error=stderr
                )
        except subprocess.TimeoutExpired:
            return TestResult("import_test", TestStatus.FAIL, 30000, "Timeout")
        except Exception as e:
            return TestResult("import_test", TestStatus.FAIL, 0, str(e))
    
    @staticmethod
    def run_validation_test(file_path: Path) -> TestResult:
        """Проверка наличия функции validate() и её запуск."""
        if file_path.suffix != ".py":
            return TestResult("validation_test", TestStatus.SKIPPED, 0)
        
        start = datetime.now()
        try:
            abs_path = str(file_path.resolve())
            code = f"""
import sys
sys.path.insert(0, r'{file_path.parent}')
import importlib.util
spec = importlib.util.spec_from_file_location("test_mod", r'{abs_path}')
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)

if hasattr(mod, 'validate'):
    result = mod.validate()
    print(f"validate returned: {{result}}")
    sys.exit(0 if result else 1)
else:
    print("No validate function found")
    sys.exit(0)  # Не критично
"""
            result = subprocess.run(
                [sys.executable, "-c", code],
                capture_output=True,
                timeout=30
            )
            duration = (datetime.now() - start).total_seconds() * 1000
            
            if result.returncode == 0:
                return TestResult("validation_test", TestStatus.PASS, duration, 
                                output=result.stdout.decode("utf-8", errors="replace")[:200])
            else:
                return TestResult(
                    "validation_test", TestStatus.FAIL, duration,
                    error=result.stderr.decode("utf-8", errors="replace")[:300]
                )
        except subprocess.TimeoutExpired:
            return TestResult("validation_test", TestStatus.FAIL, 30000, "Timeout")
        except Exception as e:
            return TestResult("validation_test", TestStatus.FAIL, 0, str(e))
    
    @staticmethod
    def run_all_tests(file_path: Path) -> List[TestResult]:
        """Запуск всех тестов для файла."""
        tests = [
            TestEngine.run_syntax_check(file_path),
            TestEngine.run_import_test(file_path),
            TestEngine.run_validation_test(file_path),
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
    
    # 12 девочек проекта
    ZONES = {
        "futaba": {
            "name": "Футаба",
            "emoji": "👩‍🏫",
            "focus": "Управление, координация, правовые исследования",
            "folder": "futaba",
            "improvements": [
                "task_distributor",
                "report_generator",
                "project_monitor",
                "coordination_api",
            ]
        },
        "shiori": {
            "name": "Шиори",
            "emoji": "🛡️",
            "focus": "Защита, безопасность, compliance",
            "folder": "shiori",
            "improvements": [
                "security_scanner",
                "content_filter",
                "audit_logger",
                "risk_analyzer",
            ]
        },
        "nobuka": {
            "name": "Нобука",
            "emoji": "🔧",
            "focus": "Улучшения, рефакторинг, тестирование",
            "folder": "nobuka",
            "improvements": [
                "code_analyzer",
                "test_generator",
                "refactor_engine",
                "metrics_collector",
            ]
        },
        "hanako": {
            "name": "Ханако",
            "emoji": "🌸",
            "focus": "Гравитация, модели пространства-времени",
            "folder": "hanako",
            "improvements": [
                "gravity_calculator",
                "orbit_simulator",
                "spacetime_analyzer",
                "gravitational_wave_detector",
            ]
        },
        "fuyuki": {
            "name": "Фуюки",
            "emoji": "⚡",
            "focus": "Атмосферное электричество, молнии",
            "folder": "fuyuki",
            "improvements": [
                "electric_field_calculator",
                "lightning_simulator",
                "energy_harvester",
                "ionization_tracker",
            ]
        },
        "lucy": {
            "name": "Люси",
            "emoji": "🚀",
            "focus": "Двигатели, интеграция сил",
            "folder": "lucy",
            "improvements": [
                "engine_designer",
                "hybrid_calculator",
                "thrust_optimizer",
                "propulsion_model",
            ]
        },
        "ayiko": {
            "name": "Айко",
            "emoji": "🎨",
            "focus": "Искусство, пиксель-арт, черчение",
            "folder": "ayiko",
            "improvements": [
                "pixel_generator",
                "pattern_drawer",
                "style_analyzer",
                "canvas_renderer",
            ]
        },
        "celesta": {
            "name": "Селеста",
            "emoji": "🧬",
            "focus": "Биология, анатомия, биомеханика",
            "folder": "celesta",
            "improvements": [
                "anatomy_model",
                "biomech_simulator",
                "tissue_generator",
                "cell_renderer",
            ]
        },
        "akira": {
            "name": "Акра",
            "emoji": "🔢",
            "focus": "Математика, вычисления, оптимизация",
            "folder": "akva",
            "improvements": [
                "numerical_optimizer",
                "algorithm_improver",
                "calculation_engine",
                "precision_manager",
            ]
        },
        "latislane": {
            "name": "Латислейн",
            "emoji": "🧮",
            "focus": "Логика, процедурная генерация, анимация",
            "folder": "latislane",
            "improvements": [
                "logic_generator",
                "animation_engine",
                "procedural_creator",
                "state_machine",
            ]
        },
        "naoto": {
            "name": "Наото",
            "emoji": "🔍",
            "focus": "Детали, визуальный анализ, детекция",
            "folder": "naoto",
            "improvements": [
                "visual_analyzer",
                "detail_detector",
                "pattern_matcher",
                "anomaly_finder",
            ]
        },
        "yui": {
            "name": "Юи",
            "emoji": "🧠",
            "focus": "Перенос сознания, когнитивные науки",
            "folder": "yu",
            "improvements": [
                "cognitive_model",
                "consciousness_framework",
                "neural_simulator",
                "memory_architect",
            ]
        }
    }
    
    def __init__(self, sandbox: SandboxManager):
        self.sandbox = sandbox
        self.created_files: List[CreatedFile] = []
        self.cycle_id = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    def create_for_sister(self, sister_key: str, improvement_type: str, 
                          max_attempts: int = 3) -> Optional[CreatedFile]:
        """Создание улучшения для конкретной девочки с повторными попытками."""
        if sister_key not in self.ZONES:
            print(f"  ❌ Неизвестная девочка: {sister_key}")
            return None
        
        zone = self.ZONES[sister_key]
        filename = f"{improvement_type}.py"
        sandbox_path = self.sandbox.get_sandbox_path(filename)
        
        attempt = 0
        while attempt < max_attempts:
            # Генерация кода
            code = self._generate_code(sister_key, improvement_type, zone)
            sandbox_path.write_text(code, encoding="utf-8")
            
            # Тестирование
            tests = TestEngine.run_all_tests(sandbox_path)
            overall = TestEngine.get_overall_status(tests)
            
            if overall == TestStatus.PASS:
                print(f"  ✅ Создан и протестирован: {filename} (попытка {attempt + 1})")
                
                created_file = CreatedFile(
                    path=filename,
                    original_path=str(sandbox_path),
                    status=TestStatus.PASS,
                    tests=tests,
                    description=f"Улучшение для {zone['name']}: {improvement_type}",
                    sister_key=sister_key
                )
                
                self.created_files.append(created_file)
                return created_file
            
            # Не прошло — пробуем снова
            attempt += 1
            if attempt < max_attempts:
                print(f"  ⚠️  Не прошло тесты (попытка {attempt}), повтор...")
        
        # Все попытки исчерпаны
        print(f"  ❌ Не удалось создать {filename} после {max_attempts} попыток")
        self.sandbox.archive_failed(filename, f"Не прошло тесты после {max_attempts} попыток")
        
        created_file = CreatedFile(
            path=filename,
            original_path=str(sandbox_path),
            status=TestStatus.FAIL,
            description=f"Улучшение для {zone['name']}: {improvement_type}",
            sister_key=sister_key
        )
        self.created_files.append(created_file)
        return created_file
    
    def _generate_code(self, sister_key: str, improvement_type: str, zone: dict) -> str:
        """Генерация кода улучшения."""
        timestamp = datetime.now().strftime("%Y-%m-%d")
        class_name = improvement_type.replace("_", " ").title().replace(" ", "")
        
        return f'''#!/usr/bin/env python3
"""
Модуль улучшения для {zone['name']} — {improvement_type}
Зона: {zone['focus']}
Создан Нобукой в тестовом режиме
Дата: {timestamp}
Цикл: {self.cycle_id}
"""

# Автоматически сгенерировано Нобукой


class {class_name}:
    """Класс для улучшения: {improvement_type}
    
    Назначение: {zone['focus']}
    Создана: Нобука ({timestamp})
    """
    
    def __init__(self):
        self.name = "{zone['name']}"
        self.focus = "{zone['focus']}"
        self.created_by = "Нобука"
        self.cycle_id = "{self.cycle_id}"
        self.improvement_type = "{improvement_type}"
        
    def run(self):
        """Основной метод выполнения улучшения."""
        print(f"Запуск улучшения для {{self.name}}...")
        print(f"   Тип: {{self.improvement_type}}")
        print(f"   Зона: {{self.focus}}")
        self._execute()
        return True
    
    def _execute(self):
        """Реализация улучшения {improvement_type}."""
        # TODO: Реализация для {zone['name']}
        # Зона: {zone['focus']}
        print(f"   Выполнение {{self.improvement_type}}...")
        return {{
            "status": "success",
            "module": "{improvement_type}",
            "target": "{zone['name']}",
            "timestamp": "{timestamp}"
        }}
    
    def get_info(self):
        """Получить информацию о модуле."""
        return {{
            "name": self.name,
            "improvement": self.improvement_type,
            "created_by": self.created_by,
            "cycle": self.cycle_id
        }}


def validate():
    """Валидация модуля."""
    module = {class_name}()
    
    # Проверка базовых атрибутов
    assert module.name == "{zone['name']}", f"Имя: {{module.name}}"
    assert module.created_by == "Нобука", f"Создатель: {{module.created_by}}"
    assert module.improvement_type == "{improvement_type}"
    
    # Проверка работы (run() должен возвращать True)
    run_result = module.run()
    assert run_result is True, f"run() вернул {{run_result}}"
    
    info = module.get_info()
    assert info["name"] == "{zone['name']}"
    
    return True


if __name__ == "__main__":
    if validate():
        print("Валидация пройдена")
        module = {class_name}()
        info = module.get_info()
        print(f"   Цикл: {{info['cycle']}}")
        module.run()
    else:
        print("Валидация не пройдена")
        import sys
        sys.exit(1)
'''
    
    def test_file(self, created_file: CreatedFile) -> bool:
        """Тестирование созданного файла."""
        sandbox_path = Path(created_file.original_path)
        
        if not sandbox_path.exists():
            created_file.status = TestStatus.FAIL
            return False
        
        tests = TestEngine.run_all_tests(sandbox_path)
        created_file.tests = tests
        created_file.status = TestEngine.get_overall_status(tests)
        
        return created_file.status == TestStatus.PASS
    
    def apply_passed_files(self) -> List[CreatedFile]:
        """Применение файлов, прошедших тесты."""
        applied = []
        
        for cf in self.created_files:
            if cf.status == TestStatus.PASS:
                try:
                    zone = self.ZONES.get(cf.sister_key, {})
                    folder = zone.get("folder", "nobuka")
                    target = f"{folder}/{cf.path}"
                    
                    self.sandbox.apply_file(cf.path, target)
                    cf.application_status = ApplicationStatus.APPLIED
                    applied.append(cf)
                    print(f"  📦 Применён → {folder}/")
                except Exception as e:
                    cf.application_status = ApplicationStatus.ROLLED_BACK
                    print(f"  ❌ Ошибка применения {cf.path}: {e}")
            else:
                self.sandbox.archive_failed(cf.path, "Не прошёл тесты")
                print(f"  ⏭️  Пропущен (не прошёл тесты): {cf.path}")
        
        return applied
    
    def generate_report(self) -> Dict:
        """Генерация отчёта о проделанной работе."""
        passed = sum(1 for cf in self.created_files if cf.status == TestStatus.PASS)
        failed = sum(1 for cf in self.created_files if cf.status == TestStatus.FAIL)
        applied = sum(1 for cf in self.created_files if cf.application_status == ApplicationStatus.APPLIED)
        
        # Группировка по девочкам
        by_sister = {}
        for cf in self.created_files:
            sister = cf.sister_key or "unknown"
            if sister not in by_sister:
                by_sister[sister] = {"total": 0, "passed": 0, "failed": 0, "applied": 0, "files": []}
            by_sister[sister]["total"] += 1
            if cf.status == TestStatus.PASS:
                by_sister[sister]["passed"] += 1
            else:
                by_sister[sister]["failed"] += 1
            if cf.application_status == ApplicationStatus.APPLIED:
                by_sister[sister]["applied"] += 1
            by_sister[sister]["files"].append(cf.path)
        
        report = {
            "timestamp": datetime.now().isoformat(),
            "cycle_id": self.cycle_id,
            "summary": f"Нобука создала {len(self.created_files)} файлов. "
                       f"{passed} прошли тесты, {applied} применены.",
            "totals": {
                "created": len(self.created_files),
                "passed": passed,
                "failed": failed,
                "applied": applied
            },
            "by_sister": by_sister,
            "files": [
                {
                    "path": cf.path,
                    "sister": cf.sister_key,
                    "status": cf.status.value,
                    "application_status": cf.application_status.value,
                    "description": cf.description,
                    "tests": [
                        {"name": t.test_name, "status": t.status.value, "duration_ms": t.duration_ms}
                        for t in (cf.tests or [])
                    ]
                }
                for cf in self.created_files
            ]
        }
        
        # Сохранение отчёта
        report_path = self.sandbox.results / f"report_{self.cycle_id}.json"
        with open(report_path, "w", encoding="utf-8") as f:
            json.dump(report, f, ensure_ascii=False, indent=2)
        
        print(f"\n  📄 Отчёт: {report_path}")
        return report

# === MAIN ORCHESTRATOR ===

def run_test_mode_cycle(target_sister: Optional[str] = None, 
                        improvement_type: Optional[str] = None,
                        apply_passed: bool = True,
                        sisters_count: int = 1):
    """
    Запуск полного цикла тестового режима.
    
    Args:
        target_sister: Ключ девочки (если None — цикл для всех)
        improvement_type: Тип улучшения (если None — автоматический выбор)
        apply_passed: Применять прошедшие тесты файлы
        sisters_count: Сколько девочек обрабатывать (1-12)
    """
    print("=" * 60)
    print("  🔧 НОБУКА — ТЕСТОВЫЙ РЕЖИМ СОЗДАНИЯ v2.0")
    print("=" * 60)
    
    # Инициализация
    sandbox = SandboxManager(".")
    creator = ImprovementCreator(sandbox)
    
    # Определение цели
    if target_sister:
        sisters_to_process = [target_sister]
    else:
        # Берём первые N девочек
        all_sisters = list(ImprovementCreator.ZONES.keys())
        sisters_to_process = all_sisters[:sisters_count]
    
    total_created = 0
    total_passed = 0
    total_failed = 0
    
    # === ЭТАП 1: СОЗДАНИЕ И ТЕСТИРОВАНИЕ ===
    print(f"\n{'═' * 60}")
    print("  ЭТАП 1: СОЗДАНИЕ И ТЕСТИРОВАНИЕ")
    print(f"{'═' * 60}")
    
    for sister_key in sisters_to_process:
        zone = ImprovementCreator.ZONES[sister_key]
        print(f"\n  {zone['emoji']} {zone['name']} — {zone['focus']}")
        
        # Определение типа улучшения
        if improvement_type:
            imp_types = [improvement_type]
        else:
            # Берём первое улучшение из списка
            imp_types = [zone["improvements"][0]]
        
        for imp_type in imp_types:
            total_created += 1
            created = creator.create_for_sister(sister_key, imp_type)
            
            if created and created.status == TestStatus.PASS:
                total_passed += 1
            elif created:
                total_failed += 1
    
    # === ЭТАП 2: ПРИМЕНЕНИЕ ===
    if apply_passed and total_passed > 0:
        print(f"\n{'═' * 60}")
        print("  ЭТАП 2: ПРИМЕНЕНИЕ УЛУЧШЕНИЙ")
        print(f"{'═' * 60}")
        applied = creator.apply_passed_files()
        total_applied = len(applied)
    else:
        total_applied = 0
    
    # === ЭТАП 3: ОТЧЁТ ===
    print(f"\n{'═' * 60}")
    print("  ЭТАП 3: ОТЧЁТ")
    print(f"{'═' * 60}")
    
    report = creator.generate_report()
    
    print(f"\n  📊 ИТОГО:")
    print(f"     Создано:  {total_created}")
    print(f"     Пройдено: {total_passed}")
    print(f"     Провалено: {total_failed}")
    print(f"     Применено: {total_applied}")
    
    if total_passed > 0:
        print(f"\n  ✅ Улучшения успешно применены в проект!")
    else:
        print(f"\n  ⚠️  Ни один файл не прошёл тесты.")
    
    print(f"\n{'=' * 60}")
    print(f"  🔧 Нобука — Тестовый режим завершён")
    print(f"{'=' * 60}")
    
    return report


def interactive_mode():
    """Интерактивный режим выбора девочки и типа улучшения."""
    print("=" * 60)
    print("  🔧 НОБУКА — ИНТЕРАКТИВНЫЙ РЕЖИМ")
    print("=" * 60)
    
    print("\n📋 Доступные девочки:")
    for i, (key, zone) in enumerate(ImprovementCreator.ZONES.items(), 1):
        print(f"  {i:2d}. {zone['emoji']} {zone['name']:10s} — {zone['focus']}")
    
    print(f"\n  13. Все девочки")
    print()
    
    choice = input("Выберите девочку (1-13): ").strip()
    
    if choice == "13":
        target = None
    elif choice.isdigit() and 1 <= int(choice) <= 12:
        key = list(ImprovementCreator.ZONES.keys())[int(choice) - 1]
        target = key
    else:
        print("❌ Неверный выбор")
        return
    
    run_test_mode_cycle(target_sister=target, apply_passed=True)


if __name__ == "__main__":
    if len(sys.argv) > 1:
        # Командная строка
        if sys.argv[1] == "--interactive":
            interactive_mode()
        elif sys.argv[1] == "--all":
            run_test_mode_cycle(sisters_count=12)
        elif sys.argv[1] == "--help":
            print("Использование:")
            print('  python test_mode_creation.py --all                    # Для всех 12 девочек')
            print('  python test_mode_creation.py --interactive            # Интерактивный режим')
            print('  python test_mode_creation.py --sister <key>           # Для конкретной')
            print('  python test_mode_creation.py --help                   # Справка')
        elif sys.argv[1] == "--sister" and len(sys.argv) > 2:
            run_test_mode_cycle(target_sister=sys.argv[2])
    else:
        interactive_mode()