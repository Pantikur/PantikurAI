"""
Саморазвитие Ханако — изучение проекта, документации и научных работ.
"""

from __future__ import annotations

import os
import ast
import json
import logging
import random
from pathlib import Path
from datetime import datetime
from typing import Optional

from hanako.engine.config import HanakoConfig


class SelfDevelopment:
    """
    Модуль саморазвития Ханако.
    
    Функции:
    - Изучение кода проекта
    - Чтение документации
    - Анализ научных работ
    - Генерация идей для улучшения
    - Самоанализ
    """

    def __init__(self, config: HanakoConfig):
        self.config = config
        self.logger = logging.getLogger("SelfDevelopment")

    def analyze_project_code(self) -> list[str]:
        """Анализ кода проекта для изучения гравитационных компонентов."""
        insights = []
        project_root = Path(__file__).parent.parent.parent.parent

        # Ищем файлы с гравитацией
        gravity_files = []
        for ext in ['*.py', '*.md', '*.json']:
            gravity_files.extend(project_root.rglob(f'*gravit*'))
            gravity_files.extend(project_root.rglob(f'*gravity*'))
            gravity_files.extend(project_root.rglob(f'*hanako*'))

        for fp in list(set(gravity_files))[:20]:
            try:
                if fp.suffix == '.py':
                    insight = self._analyze_python_file(fp)
                    if insight:
                        insights.append(insight)
                elif fp.suffix == '.md':
                    insight = self._analyze_markdown_file(fp)
                    if insight:
                        insights.append(insight)
                elif fp.suffix == '.json':
                    insight = self._analyze_json_file(fp)
                    if insight:
                        insights.append(insight)
            except Exception:
                pass

        return insights

    def _analyze_python_file(self, path: Path) -> Optional[str]:
        """Анализ Python файла."""
        try:
            text = path.read_text(encoding='utf-8')
            tree = ast.parse(text)

            classes = [n.name for n in ast.walk(tree) if isinstance(n, ast.ClassDef)]
            functions = [n.name for n in ast.walk(tree) if isinstance(n, ast.FunctionDef)]

            if classes or functions:
                return f"📊 {path.relative_to(Path(__file__).parent.parent.parent.parent)}: " \
                       f"{len(classes)} классов, {len(functions)} функций"
        except Exception:
            pass
        return None

    def _analyze_markdown_file(self, path: Path) -> Optional[str]:
        """Анализ Markdown файла."""
        try:
            text = path.read_text(encoding='utf-8')
            words = len(text.split())
            if words > 100:
                return f"📖 {path.name}: {words} слов — документация проекта"
        except Exception:
            pass
        return None

    def _analyze_json_file(self, path: Path) -> Optional[str]:
        """Анализ JSON файла."""
        try:
            with open(path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            if isinstance(data, dict):
                return f"📋 {path.name}: {len(data)} записей данных"
        except Exception:
            pass
        return None

    def read_project_documentation(self) -> list[str]:
        """Чтение документации проекта."""
        docs = []
        project_root = Path(__file__).parent.parent.parent.parent

        # Ищем документацию
        doc_files = ['README.md', 'AGENTS.md', 'GIRL_SCIENTISTS.md', 'SCIENTISTS_NETWORK.md']
        for doc_file in doc_files:
            doc_path = project_root / doc_file
            if doc_path.exists():
                try:
                    text = doc_path.read_text(encoding='utf-8')
                    words = len(text.split())
                    docs.append(f"📚 {doc_file}: {words} слов изучено")
                except Exception:
                    pass

        return docs

    def analyze_scientific_papers(self) -> int:
        """Анализ научных работ (локальная база)."""
        count = 0
        project_root = Path(__file__).parent.parent.parent.parent

        # Ищем файлы с научными данными
        for f in project_root.rglob('*.json'):
            try:
                with open(f, 'r', encoding='utf-8') as fp:
                    data = json.load(fp)
                if isinstance(data, list) and len(data) > 0:
                    count += len(data)
            except Exception:
                pass

        return count

    def self_analyze(self) -> dict:
        """Самоанализ Ханако."""
        return {
            "module": "self_development",
            "timestamp": datetime.now().isoformat(),
            "capabilities": [
                "Анализ кода проекта",
                "Чтение документации",
                "Анализ научных работ",
                "Генерация идей",
                "Самоанализ",
            ],
            "learning_goals": [
                "Углубить знания о гравитации",
                "Изучить последние теории",
                "Улучшить навыки общения",
                "Развить креативность",
            ],
        }
