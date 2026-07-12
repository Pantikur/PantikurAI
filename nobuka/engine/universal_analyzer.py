"""
Универсальный анализатор кода Нобуки — работа со ВСЕМИ типами файлов.

Реализует:
  - Анализ Python (.py)
  - Анализ JSON (.json, .jsonl)
  - Анализ Markdown (.md)
  - Анализ YAML (.yaml, .yml)
  - Анализ XML (.xml)
  - Анализ HTML (.html)
  - Анализ JavaScript/TypeScript (.js, .ts, .jsx, .tsx)
  - Анализ конфигурационных файлов (.env, .properties, .ini)
  - Анализ текстовых файлов (.txt, .log)
  - Поиск дубликатов файлов
  - Проверка размера файлов
  - Анализ структуры проекта
"""

from __future__ import annotations
import json
import re
import os
from pathlib import Path
from typing import Any, Optional
from collections import Counter

from nobuka.engine.config import NobukaConfig


class UniversalAnalyzer:
    """
    Универсальный анализатор для всех типов файлов проекта.
    """

    # Поддерживаемые расширения
    SUPPORTED_EXTENSIONS = {
        # Python
        '.py', '.pyi', '.pyw',
        # JSON
        '.json', '.jsonl', '.geojson', '.topojson',
        # Markdown
        '.md', '.markdown', '.mkd',
        # YAML
        '.yaml', '.yml',
        # XML
        '.xml', '.xsl', '.xsd', '.xslt',
        # HTML
        '.html', '.htm', '.xhtml',
        # JavaScript/TypeScript
        '.js', '.jsx', '.mjs', '.cjs',
        '.ts', '.tsx', '.mts', '.cts',
        # CSS
        '.css', '.scss', '.sass', '.less',
        # Конфиги
        '.env', '.properties', '.ini', '.cfg', '.conf',
        # Текстовые
        '.txt', '.log', '.rst', '.adoc',
        # Скрипты
        '.sh', '.bash', '.zsh',
        '.bat', '.cmd', '.ps1',
        '.rb', '.pl', '.php',
        # Другие
        '.sql', '.csv', '.toml', '.gitignore',
    }

    # Текстовые файлы для анализа
    TEXT_EXTENSIONS = {
        '.py', '.md', '.yaml', '.yml', '.json', '.xml',
        '.html', '.js', '.ts', '.css', '.txt', '.log',
        '.env', '.properties', '.ini', '.cfg', '.conf',
        '.sh', '.bash', '.bat', '.ps1', '.rb', '.pl',
        '.sql', '.csv', '.toml', '.rst',
    }

    # Файлы для исключения (бинарные, кэш, зависимости)
    EXCLUDE_EXTENSIONS = {
        '.pyc', '.pyo', '.pyd',  # Python bytecode
        '.jar', '.class', '.dll', '.so', '.dylib',  # Бинарные
        '.bin', '.dat', '.db', '.sqlite',  # Бинарные данные
        '.pkl', '.pickle', '.serial',  # Python pickle
        '.png', '.jpg', '.jpeg', '.gif', '.bmp', '.ico', '.svg',  # Изображения
        '.mp3', '.mp4', '.avi', '.mov', '.wav',  # Медиа
        '.zip', '.tar', '.gz', '.rar', '.7z',  # Архивы
        '.exe', '.msi', '.dmg', '.apk',  # Исполняемые
        '.o', '.a', '.lib',  # Объектные файлы
        '.class',  # Java bytecode
    }

    def __init__(self, config: NobukaConfig):
        self.config = config
        self.project_root = config.project_root

    def analyze_all_files(self, directory: Optional[str] = None) -> dict[str, Any]:
        """
        Проанализировать все файлы в директории.
        
        Returns:
            Полный отчёт по проекту
        """
        directory = directory or str(self.project_root)
        dir_path = Path(directory)

        if not dir_path.exists():
            return {"error": f"Директория не найдена: {directory}"}

        self.logger = __import__('logging').getLogger("UniversalAnalyzer")
        
        files = self._scan_all_files(dir_path)
        
        report = {
            "total_files": len(files),
            "by_extension": {},
            "by_size": {},
            "issues": [],
            "text_files_analyzed": 0,
            "python_files": [],
            "json_files": [],
            "markdown_files": [],
            "config_files": [],
            "duplicate_files": [],
            "large_files": [],
            "empty_files": [],
            "old_files": [],
        }

        # Группировка по расширениям
        ext_counter = Counter()
        size_categories = Counter()
        
        for file_info in files:
            ext = file_info['extension']
            ext_counter[ext] += 1
            
            size = file_info['size']
            if size < 1024:
                size_categories["< 1KB"] += 1
            elif size < 10240:
                size_categories["1-10KB"] += 1
            elif size < 102400:
                size_categories["10-100KB"] += 1
            elif size < 1048576:
                size_categories["100KB-1MB"] += 1
            else:
                size_categories["> 1MB"] += 1

        report["by_extension"] = dict(ext_counter.most_common(30))
        report["by_size"] = dict(size_categories)

        # Анализ текстовых файлов
        for file_info in files:
            if file_info['extension'] in self.TEXT_EXTENSIONS:
                report["text_files_analyzed"] += 1
                analysis = self._analyze_text_file(file_info)
                if analysis:
                    if file_info['extension'] == '.py':
                        report["python_files"].append(analysis)
                    elif file_info['extension'] == '.json':
                        report["json_files"].append(analysis)
                    elif file_info['extension'] == '.md':
                        report["markdown_files"].append(analysis)
                    elif file_info['extension'] in ['.env', '.properties', '.ini', '.yaml', '.yml']:
                        report["config_files"].append(analysis)
                    
                    if analysis.get('issues'):
                        report["issues"].append(analysis)

        # Поиск проблемных файлов
        for file_info in files:
            if file_info['size'] == 0:
                report["empty_files"].append(file_info)
            elif file_info['size'] > 1048576:  # > 1MB
                report["large_files"].append(file_info)
            
            # Проверка на устаревшие файлы (.bak, .backup, .old)
            if file_info['extension'] in ['.bak', '.backup', '.old', '.tmp']:
                report["old_files"].append(file_info)

        # Поиск дубликатов (по содержимому)
        report["duplicate_files"] = self._find_duplicates(files)

        self.logger.info(f"📊 Проанализировано {report['total_files']} файлов")
        self.logger.info(f"📄 Текстовых файлов: {report['text_files_analyzed']}")
        self.logger.info(f"⚠️  Найдено проблем: {len(report['issues'])}")

        return report

    def _scan_all_files(self, directory: Path) -> list[dict]:
        """
        Сканировать все файлы в директории.
        """
        files = []
        
        for path in directory.rglob('*'):
            if not path.is_file():
                continue
            
            # Пропуск системных директорий
            parts = path.parts
            if any(part in ['__pycache__', '.git', 'node_modules', 'venv', '.venv'] for part in parts):
                continue
            if any(part in ['android-studio-plugin'] for part in parts):
                continue
            
            # Пропуск бинарных файлов
            ext = path.suffix.lower()
            if ext in self.EXCLUDE_EXTENSIONS:
                continue
            
            try:
                size = path.stat().st_size
                files.append({
                    'path': str(path),
                    'name': path.name,
                    'extension': ext or '(no extension)',
                    'size': size,
                    'modified': path.stat().st_mtime,
                })
            except (OSError, PermissionError):
                continue

        return files

    def _analyze_text_file(self, file_info: dict) -> Optional[dict]:
        """
        Проанализировать текстовый файл.
        """
        try:
            path = Path(file_info['path'])
            content = path.read_text(encoding='utf-8', errors='ignore')
        except Exception:
            return None

        analysis = {
            'path': file_info['path'],
            'extension': file_info['extension'],
            'size': file_info['size'],
            'lines': len(content.splitlines()),
            'issues': [],
        }

        ext = file_info['extension']

        # Анализ Python
        if ext == '.py':
            analysis.update(self._analyze_python(content, file_info))

        # Анализ JSON
        elif ext == '.json':
            analysis.update(self._analyze_json(content, file_info))

        # Анализ Markdown
        elif ext == '.md':
            analysis.update(self._analyze_markdown(content, file_info))

        # Анализ YAML
        elif ext in ['.yaml', '.yml']:
            analysis.update(self._analyze_yaml(content, file_info))

        # Анализ HTML
        elif ext in ['.html', '.htm']:
            analysis.update(self._analyze_html(content, file_info))

        # Анализ JavaScript/TypeScript
        elif ext in ['.js', '.jsx', '.ts', '.tsx']:
            analysis.update(self._analyze_javascript(content, file_info))

        # Анализ конфигурационных файлов
        elif ext in ['.env', '.properties', '.ini', '.cfg', '.conf']:
            analysis.update(self._analyze_config(content, file_info))

        # Анализ текстовых/логов
        elif ext in ['.txt', '.log']:
            analysis.update(self._analyze_text(content, file_info))

        return analysis

    def _analyze_python(self, content: str, file_info: dict) -> dict:
        """Анализ Python-файлов."""
        issues = []
        lines = content.splitlines()
        
        # Проверка длины файла
        if len(lines) > 500:
            issues.append({
                'type': 'large_file',
                'severity': 'warning',
                'message': f'Файл слишком большой: {len(lines)} строк'
            })
        
        # Проверка длинных строк
        long_lines = sum(1 for line in lines if len(line) > 120)
        if long_lines > 5:
            issues.append({
                'type': 'long_lines',
                'severity': 'info',
                'message': f'{long_lines} строк длиннее 120 символов'
            })
        
        # Проверка tabs
        if '\t' in content:
            issues.append({
                'type': 'tabs',
                'severity': 'warning',
                'message': 'Используются табуляции вместо пробелов'
            })
        
        # Проверка trailing whitespace
        trailing = sum(1 for line in lines if line != line.rstrip())
        if trailing > 10:
            issues.append({
                'type': 'trailing_whitespace',
                'severity': 'info',
                'message': f'{trailing} строк с пробелами в конце'
            })
        
        return {'issues': issues}

    def _analyze_json(self, content: str, file_info: dict) -> dict:
        """Анализ JSON-файлов."""
        issues = []
        
        try:
            data = json.loads(content)
            
            # Проверка глубины вложенности
            def get_depth(obj, current=0):
                if isinstance(obj, dict):
                    return max((get_depth(v, current + 1) for v in obj.values()), default=current)
                elif isinstance(obj, list):
                    return max((get_depth(item, current + 1) for item in obj), default=current)
                return current
            
            depth = get_depth(data)
            if depth > 10:
                issues.append({
                    'type': 'deep_nesting',
                    'severity': 'warning',
                    'message': f'Глубокая вложенность: {depth} уровней'
                })
            
            # Проверка размера
            if file_info['size'] > 5 * 1024 * 1024:  # > 5MB
                issues.append({
                    'type': 'large_file',
                    'severity': 'warning',
                    'message': f'JSON-файл слишком большой: {file_info["size"] / 1024 / 1024:.1f}MB'
                })
        except json.JSONDecodeError as e:
            issues.append({
                'type': 'invalid_json',
                'severity': 'error',
                'message': f'Ошибка JSON: {str(e)}'
            })
        
        return {'issues': issues}

    def _analyze_markdown(self, content: str, file_info: dict) -> dict:
        """Анализ Markdown-файлов."""
        issues = []
        lines = content.splitlines()
        
        # Проверка заголовков
        headers = [line for line in lines if line.startswith('#')]
        if not headers:
            issues.append({
                'type': 'no_headers',
                'severity': 'info',
                'message': 'Файл без заголовков'
            })
        
        # Проверка сломанных ссылок (простая проверка)
        broken_links = re.findall(r'\[([^\]]+)\]\(([^)]+)\)', content)
        for text, url in broken_links:
            if url.startswith('./') or url.startswith('../'):
                # Можно проверить существование файла
                pass
        
        # Проверка изображений без alt-текста
        images = re.findall(r'!\[([^\]]*)\]\([^)]+\)', content)
        missing_alt = sum(1 for alt in images if not alt.strip())
        if missing_alt > 0:
            issues.append({
                'type': 'missing_alt',
                'severity': 'info',
                'message': f'{missing_alt} изображений без alt-текста'
            })
        
        return {'issues': issues}

    def _analyze_yaml(self, content: str, file_info: dict) -> dict:
        """Анализ YAML-файлов."""
        issues = []
        
        # Проверка tabs (YAML не поддерживает табы)
        if '\t' in content:
            issues.append({
                'type': 'tabs',
                'severity': 'error',
                'message': 'YAML не поддерживает табуляции'
            })
        
        # Проверка длины строк
        lines = content.splitlines()
        long_lines = sum(1 for line in lines if len(line) > 120)
        if long_lines > 0:
            issues.append({
                'type': 'long_lines',
                'severity': 'warning',
                'message': f'{long_lines} строк длиннее 120 символов'
            })
        
        return {'issues': issues}

    def _analyze_html(self, content: str, file_info: dict) -> dict:
        """Анализ HTML-файлов."""
        issues = []
        
        # Проверка закрытых тегов (простая)
        open_tags = re.findall(r'<([a-zA-Z][a-zA-Z0-9]*)[^>]*?(?<!/)>', content)
        close_tags = re.findall(r'</([a-zA-Z][a-zA-Z0-9]*)>', content)
        
        if len(open_tags) != len(close_tags):
            issues.append({
                'type': 'unclosed_tags',
                'severity': 'warning',
                'message': 'Возможно, есть незакрытые теги'
            })
        
        return {'issues': issues}

    def _analyze_javascript(self, content: str, file_info: dict) -> dict:
        """Анализ JavaScript/TypeScript-файлов."""
        issues = []
        lines = content.splitlines()
        
        # Проверка console.log
        console_logs = sum(1 for line in lines if 'console.log' in line)
        if console_logs > 0:
            issues.append({
                'type': 'console_logs',
                'severity': 'info',
                'message': f'Найдено {console_logs} console.log (следует удалить перед продакшеном)'
            })
        
        # Проверка длинных строк
        long_lines = sum(1 for line in lines if len(line) > 120)
        if long_lines > 5:
            issues.append({
                'type': 'long_lines',
                'severity': 'warning',
                'message': f'{long_lines} строк длиннее 120 символов'
            })
        
        return {'issues': issues}

    def _analyze_config(self, content: str, file_info: dict) -> dict:
        """Анализ конфигурационных файлов."""
        issues = []
        lines = content.splitlines()
        
        # Проверка пустых строк в начале
        empty_start = sum(1 for line in lines if not line.strip())
        if empty_start > 3:
            issues.append({
                'type': 'too_many_empty_lines',
                'severity': 'info',
                'message': f'{empty_start} пустых строк в начале файла'
            })
        
        # Проверка дубликатов ключей
        keys = [line.split('=')[0].strip() for line in lines if '=' in line and not line.startswith('#')]
        duplicates = [k for k in set(keys) if keys.count(k) > 1]
        if duplicates:
            issues.append({
                'type': 'duplicate_keys',
                'severity': 'warning',
                'message': f'Дубликаты ключей: {", ".join(duplicates[:5])}'
            })
        
        return {'issues': issues}

    def _analyze_text(self, content: str, file_info: dict) -> dict:
        """Анализ текстовых файлов."""
        issues = []
        lines = content.splitlines()
        
        if len(lines) > 10000:
            issues.append({
                'type': 'large_file',
                'severity': 'warning',
                'message': f'Текстовый файл слишком большой: {len(lines)} строк'
            })
        
        return {'issues': issues}

    def _find_duplicates(self, files: list[dict]) -> list[dict]:
        """
        Найти дубликаты файлов по содержимому (хеш).
        """
        import hashlib
        
        hash_map = {}
        duplicates = []
        
        for file_info in files:
            if file_info['size'] == 0:
                continue
            
            try:
                path = Path(file_info['path'])
                with open(path, 'rb') as f:
                    content = f.read(8192)  # Первые 8KB
                    file_hash = hashlib.md5(content).hexdigest()
                
                if file_hash in hash_map:
                    duplicates.append({
                        'files': [hash_map[file_hash], file_info['path']],
                        'hash': file_hash,
                        'size': file_info['size'],
                    })
                else:
                    hash_map[file_hash] = file_info['path']
            except (OSError, PermissionError):
                continue
        
        return duplicates[:50]  # Лимит для отчёта

    def generate_project_report(self, report: dict) -> str:
        """
        Сгенерировать человекочитаемый отчёт.
        """
        lines = [
            "=" * 80,
            "📊 ОТЧЁТ АНАЛИЗА ПРОЕКТА",
            "=" * 80,
            "",
            f"Всего файлов: {report['total_files']}",
            f"Текстовых файлов: {report['text_files_analyzed']}",
            "",
            "--- По расширениям (ТОП-10) ---",
        ]
        
        exts = report.get('by_extension', {})
        for ext, count in list(exts.items())[:10]:
            lines.append(f"  {ext or '(no ext)':15} {count:6}")
        
        lines.extend([
            "",
            "--- По размеру ---",
        ])
        
        sizes = report.get('by_size', {})
        for size_cat, count in sizes.items():
            lines.append(f"  {size_cat:15} {count:6}")
        
        if report.get('empty_files'):
            lines.extend([
                "",
                "--- Пустые файлы ---",
            ])
            for f in report['empty_files'][:10]:
                lines.append(f"  ⚠️  {f['path']}")
        
        if report.get('large_files'):
            lines.extend([
                "",
                "--- Большие файлы (>1MB) ---",
            ])
            for f in report['large_files'][:10]:
                lines.append(f"  📦 {f['path']} ({f['size'] / 1024 / 1024:.1f}MB)")
        
        if report.get('old_files'):
            lines.extend([
                "",
                "--- Устаревшие файлы (.bak, .backup) ---",
            ])
            for f in report['old_files'][:10]:
                lines.append(f"  🗑️  {f['path']}")
        
        if report.get('duplicate_files'):
            lines.extend([
                "",
                "--- Дубликаты файлов ---",
            ])
            for dup in report['duplicate_files'][:10]:
                lines.append(f"  🔄 {dup['files'][0]}")
                lines.append(f"      {dup['files'][1]}")
        
        if report.get('issues'):
            lines.extend([
                "",
                "--- Проблемы (ТОП-20) ---",
            ])
            for issue in report['issues'][:20]:
                path = issue.get('path', 'unknown')
                for issue_detail in issue.get('issues', []):
                    lines.append(f"  [{issue_detail['severity']}] {path}: {issue_detail['message']}")
        
        lines.append("")
        lines.append("=" * 80)
        
        return "\n".join(lines)
