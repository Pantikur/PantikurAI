"""
ML Optimizer — Оптимизатор процесса машинного обучения.

Наото анализирует проблемы в коде обучения и автоматически:
  - Улучшает скрипты обучения (train.py, main.py и др.)
  - Оптимизирует обработку данных (JSONL, CSV)
  - Устраняет дубликаты и устаревшие файлы
  - Улучшает pipeline обработки данных
  - Добавляет мониторинг и логирование обучения
  - Оптимизирует использование памяти и GPU

Работает на основе проблем, найденных в universal_analyzer.
"""

from __future__ import annotations
import json
import re
import shutil
from pathlib import Path
from typing import Any, Optional
from datetime import datetime

from naoto.engine.config import NaotoConfig


class MLOptimizer:
    """
    Оптимизатор процесса машинного обучения Наото.

    Автоматически находит проблемы в коде обучения и исправляет их.
    """

    # Файлы обучения, которые нужно оптимизировать
    TRAINING_FILES = [
        "train.py", "main.py", "train_logic.py", "inference.py",
        "auto_gigachat_learning.py", "learn_knowledge_from_web.py",
        "add_anatomy_knowledge.py", "generate_training_data.py",
        "create_data.py", "inspect_data.py", "retrain.py",
    ]

    # Директории с данными
    DATA_DIRECTORIES = [
        "data", "models", "Pantikur", "Wuglarst",
    ]

    def __init__(self, config: NaotoConfig):
        self.config = config
        self.project_root = config.project_root
        self.logger = __import__('logging').getLogger("MLOptimizer")
        self.optimizations_applied = []

    def analyze_and_optimize(self) -> dict[str, Any]:
        """
        Анализ проблем и применение оптимизаций.
        
        Returns:
            Отчёт о проделанной работе
        """
        self.logger.info("🧠 Запуск ML-оптимизатора...")
        
        report = {
            "timestamp": datetime.now().isoformat(),
            "optimizations": [],
            "data_quality": {},
            "training_pipeline": {},
            "recommendations": [],
        }

        # 1. Анализ проблем в скриптах обучения
        training_issues = self._analyze_training_scripts()
        report["training_pipeline"] = training_issues
        
        # 2. Оптимизация скриптов обучения
        if training_issues.get("issues"):
            fixes = self._fix_training_scripts(training_issues["issues"])
            report["optimizations"].extend(fixes)

        # 3. Анализ качества данных
        data_quality = self._analyze_data_quality()
        report["data_quality"] = data_quality

        # 4. Оптимизация данных (удаление дубликатов, очистка)
        if data_quality.get("duplicate_files"):
            duplicates_removed = self._remove_data_duplicates(data_quality["duplicate_files"])
            report["optimizations"].append({
                "type": "data_cleanup",
                "description": f"Удалено {duplicates_removed} дубликатов данных",
                "files_affected": duplicates_removed,
            })

        # 5. Оптимизация использования памяти
        memory_issues = self._analyze_memory_usage()
        report["training_pipeline"]["memory_issues"] = memory_issues

        # 6. Генерация рекомендаций
        report["recommendations"] = self._generate_recommendations(report)

        self.logger.info(f"✅ ML-оптимизация завершена: {len(report['optimizations'])} улучшений")
        
        return report

    def _analyze_training_scripts(self) -> dict:
        """Анализ проблем в скриптах обучения."""
        issues = []
        files_to_fix = []

        for dir_name in self.DATA_DIRECTORIES:
            dir_path = self.project_root / dir_name
            
            if not dir_path.exists():
                continue
            
            for script in self.TRAINING_FILES:
                file_path = dir_path / script
                if not file_path.exists():
                    continue
                
                try:
                    content = file_path.read_text(encoding="utf-8")
                    lines = content.splitlines()
                    
                    # Проверка длины файла
                    if len(lines) > 500:
                        issues.append({
                            "type": "large_file",
                            "severity": "warning",
                            "file": str(file_path),
                            "message": f"Слишком большой файл: {len(lines)} строк. Следует разбить на модули.",
                        })
                        files_to_fix.append({
                            "path": file_path,
                            "lines": len(lines),
                        })
                    
                    # Проверка trailing whitespace
                    trailing = sum(1 for line in lines if line != line.rstrip())
                    if trailing > 10:
                        issues.append({
                            "type": "trailing_whitespace",
                            "severity": "info",
                            "file": str(file_path),
                            "message": f"{trailing} строк с пробелами в конце.",
                        })
                    
                    # Проверка отсутствия логирования
                    if "logging" not in content and "logger" not in content:
                        issues.append({
                            "type": "no_logging",
                            "severity": "info",
                            "file": str(file_path),
                            "message": "Отсутствует логирование. Добавьте мониторинг обучения.",
                        })
                    
                    # Проверка отсутствия прогресс-баров
                    if "tqdm" not in content and "progress" not in content.lower():
                        issues.append({
                            "type": "no_progress_bar",
                            "severity": "info",
                            "file": str(file_path),
                            "message": "Отсутствует прогресс-бар. Добавьте мониторинг обучения.",
                        })
                    
                    # Проверка отсутствия валидации данных
                    if "validate" not in content.lower() and "check" not in content.lower():
                        issues.append({
                            "type": "no_validation",
                            "severity": "warning",
                            "file": str(file_path),
                            "message": "Отсутствует валидация данных перед обучением.",
                        })
                    
                except Exception as e:
                    self.logger.warning(f"Ошибка анализа {file_path}: {e}")

        return {
            "issues": issues,
            "files_to_fix": files_to_fix,
            "total_files_analyzed": len(files_to_fix),
        }

    def _fix_training_scripts(self, issues: list[dict]) -> list[dict]:
        """Автоматическое исправление проблем в скриптах обучения."""
        fixes = []
        
        for issue in issues:
            file_path = Path(issue["file"])
            try:
                content = file_path.read_text(encoding="utf-8")
                original = content
                
                # Исправление trailing whitespace
                if issue["type"] == "trailing_whitespace":
                    lines = content.splitlines()
                    fixed_lines = [line.rstrip() for line in lines]
                    content = "\n".join(fixed_lines)
                    fixes.append({
                        "type": "whitespace_cleanup",
                        "file": str(file_path),
                        "description": f"Очищено {issue['message'].split()[0]} строк от пробелов",
                        "changes": "trailing_whitespace",
                    })
                
                # Добавление логирования
                if issue["type"] == "no_logging":
                    # Добавляем импорт logging в начало файла
                    import_section = "import logging\n\nlogger = logging.getLogger(__name__)\n"
                    if "import logging" not in content:
                        content = import_section + content
                        fixes.append({
                            "type": "add_logging",
                            "file": str(file_path),
                            "description": "Добавлено логирование для мониторинга обучения",
                            "changes": "logging",
                        })
                
                # Добавление прогресс-бара (рекомендация)
                if issue["type"] == "no_progress_bar":
                    fixes.append({
                        "type": "recommendation",
                        "file": str(file_path),
                        "description": "Рекомендуется добавить tqdm для мониторинга обучения",
                        "changes": "recommendation",
                        "suggestion": "from tqdm import tqdm\nfor batch in tqdm(dataloader):\n    ...",
                    })
                
                # Сохранение изменений
                if content != original:
                    backup_path = file_path.with_suffix(file_path.suffix + ".bak")
                    if not backup_path.exists():
                        shutil.copy2(file_path, backup_path)
                    
                    file_path.write_text(content, encoding="utf-8")
                    self.logger.info(f"✅ Исправлено: {file_path}")
                    
            except Exception as e:
                self.logger.warning(f"Ошибка исправления {file_path}: {e}")
        
        return fixes

    def _analyze_data_quality(self) -> dict:
        """Анализ качества данных обучения."""
        report = {
            "total_files": 0,
            "jsonl_files": [],
            "duplicate_files": [],
            "empty_files": [],
            "large_files": [],
        }

        for dir_name in self.DATA_DIRECTORIES:
            dir_path = self.project_root / dir_name
            if not dir_path.exists():
                continue
            
            # Поиск JSONL-файлов
            for jsonl in dir_path.rglob("*.jsonl"):
                parts = jsonl.parts
                if any(p in ['__pycache__', '.git', 'venv'] for p in parts):
                    continue
                
                report["total_files"] += 1
                try:
                    size = jsonl.stat().st_size
                    report["jsonl_files"].append({
                        "path": str(jsonl),
                        "size_mb": size / 1024 / 1024,
                        "size": size,
                    })
                    
                    if size == 0:
                        report["empty_files"].append(str(jsonl))
                    elif size > 10 * 1024 * 1024:  # > 10MB
                        report["large_files"].append({
                            "path": str(jsonl),
                            "size_mb": size / 1024 / 1024,
                        })
                except Exception:
                    continue

        # Поиск дубликатов (по хешу первых 4KB)
        import hashlib
        
        hash_map = {}
        duplicates = []
        
        for jsonl_info in report["jsonl_files"]:
            try:
                jsonl_path = Path(jsonl_info["path"])
                with open(jsonl_path, 'rb') as f:
                    first_4kb = f.read(4096)
                    file_hash = hashlib.md5(first_4kb).hexdigest()
                
                if file_hash in hash_map:
                    duplicates.append({
                        "file1": hash_map[file_hash],
                        "file2": jsonl_info["path"],
                        "hash": file_hash,
                    })
                else:
                    hash_map[file_hash] = jsonl_info["path"]
            except Exception:
                continue
        
        report["duplicate_files"] = duplicates[:20]  # Лимит 20 пар
        
        return report

    def _remove_data_duplicates(self, duplicates: list[dict]) -> int:
        """
        Удаление дубликатов данных (с подтверждением через логирование).
        
        Args:
            duplicates: Список пар дубликатов
            
        Returns:
            Количество удалённых файлов
        """
        removed = 0
        
        for dup in duplicates[:10]:  # Ограничение для безопасности
            try:
                file2 = Path(dup["file2"])
                
                # Удаляем только если это временный/циклический файл
                if "cycle" in file2.name.lower() or "temp" in file2.name.lower():
                    file2.unlink()
                    removed += 1
                    self.logger.info(f"🗑️  Удалён дубликат: {file2}")
            except Exception as e:
                self.logger.warning(f"Ошибка удаления {dup['file2']}: {e}")
        
        return removed

    def _analyze_memory_usage(self) -> list[dict]:
        """Анализ использования памяти в скриптах обучения."""
        issues = []
        
        for dir_name in self.DATA_DIRECTORIES:
            dir_path = self.project_root / dir_name
            if not dir_path.exists():
                continue
            
            for script in dir_path.rglob("*.py"):
                parts = script.parts
                if any(p in ['__pycache__', '.git', 'venv'] for p in parts):
                    continue
                
                try:
                    content = script.read_text(encoding="utf-8")
                    
                    # Проверка загрузки больших файлов в память
                    if "json.load" in content or "json.loads" in content:
                        if "with open" not in content.split("json.load")[0][-200:]:
                            issues.append({
                                "type": "memory_risk",
                                "file": str(script),
                                "message": "Потенциальная проблема: json.load() может загрузить большой файл в память.",
                                "severity": "warning",
                            })
                    
                    # Проверка отсутствия batch-обработки
                    if "for line in" in content and "json" in content:
                        if "batch" not in content.lower():
                            issues.append({
                                "type": "no_batching",
                                "file": str(script),
                                "message": "Отсутствует batch-обработка. Для больших файлов рекомендуется использовать batch.",
                                "severity": "info",
                            })
                    
                except Exception:
                    continue
        
        return issues

    def _generate_recommendations(self, report: dict) -> list[str]:
        """Генерация рекомендаций по оптимизации обучения."""
        recommendations = []
        
        # На основе качества данных
        data_quality = report.get("data_quality", {})
        if data_quality.get("duplicate_files"):
            recommendations.append(
                f"🔄 Найдено {len(data_quality['duplicate_files'])} пар дубликатов данных. "
                "Рекомендуется удалить дубликаты и объединить данные."
            )
        
        if data_quality.get("large_files"):
            recommendations.append(
                f"📦 Найдено {len(data_quality['large_files'])} больших JSONL-файлов (>10MB). "
                "Рассмотрите использование chunked-загрузки для экономии памяти."
            )
        
        # На основе проблем в коде
        training_pipeline = report.get("training_pipeline", {})
        
        if training_pipeline.get("memory_issues"):
            recommendations.append(
                "⚡ Обнаружены проблемы с использованием памяти. "
                "Рекомендуется использовать batch-обработку и генераторы."
            )
        
        # Общие рекомендации
        recommendations.extend([
            "📈 Добавьте tqdm для визуализации прогресса обучения",
            "💾 Сохраняйте checkpoints каждые N эпох для предотвращения потери данных",
            "📊 Добавьте метрики валидации для отслеживания переобучения",
            "🧪 Проводите A/B-тестирование разных гиперпараметров",
            "🔄 Используйте Data Augmentation для увеличения обучающей выборки",
        ])
        
        return recommendations

    def generate_optimization_report(self, report: dict) -> str:
        """Генерация человекочитаемого отчёта."""
        lines = [
            "=" * 80,
            "🧠 ОТЧЁТ ML-OPTIMIZATORA (Наото)",
            "=" * 80,
            "",
            f"Время анализа: {report.get('timestamp', '?')}",
            "",
            "--- Оптимизации применены ---",
        ]
        
        optimizations = report.get("optimizations", [])
        if optimizations:
            for opt in optimizations:
                lines.append(f"  ✅ {opt['description']}")
                lines.append(f"     Файл: {opt.get('file', 'N/A')}")
                lines.append("")
        else:
            lines.append("  Нет применённых оптимизаций")
            lines.append("")
        
        # Качество данных
        lines.extend(["--- Качество данных ---", ""])
        data_quality = report.get("data_quality", {})
        
        jsonl_files = data_quality.get("jsonl_files", [])
        lines.append(f"  JSONL-файлов: {len(jsonl_files)}")
        
        if jsonl_files:
            total_size = sum(f.get("size_mb", 0) for f in jsonl_files)
            lines.append(f"  Общий размер: {total_size:.1f}MB")
            
            large = data_quality.get("large_files", [])
            if large:
                lines.append(f"  📦 Больших файлов (>10MB): {len(large)}")
        
        duplicates = data_quality.get("duplicate_files", [])
        if duplicates:
            lines.append(f"  🔄 Дубликатов найдено: {len(duplicates)} пар")
        
        empty = data_quality.get("empty_files", [])
        if empty:
            lines.append(f"  ⚠️  Пустых файлов: {len(empty)}")
        
        # Рекомендации
        lines.extend(["", "--- Рекомендации ---", ""])
        recommendations = report.get("recommendations", [])
        for i, rec in enumerate(recommendations, 1):
            lines.append(f"  {i}. {rec}")
        
        lines.extend(["", "=" * 80])
        
        return "\n".join(lines)
