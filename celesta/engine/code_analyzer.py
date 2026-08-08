"""
Анализатор кода Селесты — статический анализ проекта.

Реализует:
  - Сканирование файлов проекта
  - Анализ сложности (циклломатическая)
  - Поиск дубликатов
  - Проверку документации
  - Проверку метрик (строки, функции, классы)
  - Генерацию отчёта
"""

from __future__ import annotations
import ast
import re
import sys
from collections import Counter
from pathlib import Path
from typing import Any

from celesta.engine.config import CelestaConfig
from celesta.engine.models import CodeMetric, FileAnalysis, Issue


class CodeAnalyzer:
    """
    Статический анализатор кода.
    """

    def __init__(self, config: CelestaConfig):
        self.config = config
        self.max_lines = config.max_file_lines
        self.max_function_lines = config.max_function_lines
        self.max_complexity = config.max_complexity

    def analyze_file(self, file_path: Path | str) -> FileAnalysis:
        """
        Проанализировать один Python-файл.
        """
        file_path = Path(file_path)

        analysis = FileAnalysis(path=str(file_path))

        if not file_path.exists():
            analysis.issues.append(f"Файл не существует: {file_path}")
            return analysis

        try:
            source = file_path.read_text(encoding="utf-8")
            lines = source.splitlines()
            analysis.lines = len(lines)
        except Exception as e:
            analysis.issues.append(f"Ошибка чтения: {e}")
            return analysis

        if analysis.lines > self.max_lines:
            analysis.issues.append(
                f"Слишком много строк: {analysis.lines} > {self.max_lines}"
            )

        # Парсинг AST
        try:
            tree = ast.parse(source)
        except SyntaxError as e:
            analysis.issues.append(f"Ошибка синтаксиса: {e}")
            return analysis

        # Анализ функций
        functions = [n for n in ast.walk(tree) if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))]
        analysis.functions = len(functions)

        # Анализ классов
        classes = [n for n in ast.walk(tree) if isinstance(n, ast.ClassDef)]
        analysis.classes = len(classes)

        # Цикломатическая сложность
        complexity = self._calculate_complexity(tree)
        analysis.complexity = complexity

        if complexity > self.max_complexity:
            analysis.issues.append(
                f"Высокая сложность: {complexity} > {self.max_complexity}"
            )

        # Проверка длинных функций
        for func in functions:
            end_line = getattr(func, 'end_lineno', None)
            if end_line is not None:
                func_lines = end_line - func.lineno + 1
            else:
                func_lines = 0
            if func_lines > self.max_function_lines:
                analysis.issues.append(
                    f"Длинная функция '{func.name}': {func_lines} > {self.max_function_lines} строк"
                )

        # Проверка документации
        analysis.has_docstrings = self._check_docstrings(tree)

        # Проверка метрик
        analysis.metrics = [
            CodeMetric("lines", float(analysis.lines), float(self.max_lines), "строк"),
            CodeMetric("complexity", float(complexity), float(self.max_complexity), ""),
            CodeMetric("functions", float(analysis.functions), 0, "шт"),
        ]

        return analysis

    def _calculate_complexity(self, tree: ast.AST) -> int:
        """
        Вычислить цикломатическую сложность функции/модуля.
        """
        complexity = 1  # Базовая сложность

        for node in ast.walk(tree):
            if isinstance(node, (ast.If, ast.While, ast.For, ast.AsyncFor)):
                complexity += 1
            elif isinstance(node, ast.ExceptHandler):
                complexity += 1
            elif isinstance(node, ast.BoolOp):
                complexity += len(node.values) - 1
            elif isinstance(node, ast.Assert):
                complexity += 1
            elif isinstance(node, (ast.ListComp, ast.SetComp, ast.DictComp, ast.GeneratorExp)):
                complexity += len(node.generators)
            elif isinstance(node, ast.With):
                complexity += 1
            elif isinstance(node, ast.IfExp):
                complexity += 1

        return complexity

    def _check_docstrings(self, tree: ast.AST) -> bool:
        """
        Проверить наличие docstrings в модуле, функциях и классах.
        """
        # Модуль
        if not ast.get_docstring(tree):  # type: ignore[arg-type]
            return False

        # Функции и классы
        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
                if not ast.get_docstring(node):  # type: ignore[arg-type]
                    return False

        return True

    def analyze_directory(self, dir_path: Path | str) -> list[FileAnalysis]:
        """
        Проанализировать все Python-файлы в директории.
        """
        dir_path = Path(dir_path)
        results = []

        for py_file in dir_path.rglob("*.py"):
            # Пропустить __pycache__ и venv
            parts = py_file.parts
            if "__pycache__" in parts or "venv" in parts or ".git" in parts:
                continue
            results.append(self.analyze_file(py_file))

        return results

    def _scan_files(self, dir_path: Path) -> list[Path]:
        """Сканировать файлы в директории."""
        files = []
        for pattern in ["*.py"]:
            files.extend(dir_path.rglob(pattern))

        # Фильтрация
        excluded = set()
        for pat in self.config.exclude_patterns:
            excluded.add(pat)

        result = []
        for f in files:
            # Проверить, не в excluded
            for exc in excluded:
                if exc in str(f):
                    break
            else:
                result.append(f)

        return result[:50]  # Лимит для демо

    def generate_issues_report(self, analyses: list[FileAnalysis]) -> dict[str, Any]:
        """
        Сгенерировать отчёт по проблемам.
        """
        all_issues: list[dict] = []
        files_with_issues = 0
        total_issues = 0

        for analysis in analyses:
            if analysis.issues:
                files_with_issues += 1
                total_issues += len(analysis.issues)
                all_issues.append({
                    "file": analysis.path,
                    "issues": analysis.issues,
                    "metrics": {
                        "lines": analysis.lines,
                        "functions": analysis.functions,
                        "complexity": analysis.complexity,
                    }
                })

        return {
            "total_files": len(analyses),
            "files_with_issues": files_with_issues,
            "total_issues": total_issues,
            "issues": all_issues,
        }
