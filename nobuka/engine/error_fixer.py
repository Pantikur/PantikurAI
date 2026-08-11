"""
Нобука — поиск, анализ и исправление реальных ошибок в коде.

ErrorFixer реализует полный цикл:

  1. ЧИТАТЬ   — код проекта (все .py из scan_directories) и логи приложения
  2. НАХОДИТЬ — реальные дефекты через AST-анализ:
       • неопределённые имена (кандидаты в NameError)
       • неиспользуемые импорты
       • сравнения `== None` / `!= None` (должно быть `is` / `is not`)
       • изменяемые аргументы по умолчанию (list/dict/set)
       • голый `except:` и проглоченные исключения
       • переопределения встроенных имён
       • синтаксические ошибки
  3. АНАЛИЗИРОВАТЬ — по каждому дефекту: категория, серьёзность, причина,
     конкретная стратегия исправления; связка с ошибками из логов
     (traceback → файл:строка → проверка конкретного места)
  4. ИСПРАВЛЯТЬ   — безопасные детерминированные правки:
       • удаление неиспользуемого импорта
       • `== None` → `is None`, `!= None` → `is not None`
       • изменяемый дефолт → `None` + guard-строка
       • `except:` → `except Exception:`
     Каждая правка: резервная копия → применение → проверка compile() →
     повторный анализ → откат при проблемах.
"""

from __future__ import annotations

import ast
import builtins
import logging
import re
import shutil
from datetime import datetime
from pathlib import Path
from typing import Any, Optional

from nobuka.engine.config import NobukaConfig
from nobuka.engine.models import Issue


class ErrorFixer:
    """
    Поиск и исправление реальных ошибок в коде.
    """

    # Голые имена встроенных функций (для проверки shadowing)
    BUILTIN_NAMES = set(dir(builtins))

    def __init__(self, config: NobukaConfig):
        self.config = config
        self.logger = logging.getLogger("NobukaErrorFixer")
        self.backup_dir = config.error_fix_backup_dir
        self.backup_dir.mkdir(parents=True, exist_ok=True)

        # Кэш: путь файла -> (mtime, size, найденные проблемы)
        self._cache: dict[str, tuple[int, int, list[dict]]] = {}

    # ================================================================
    #  1. НАХОЖДЕНИЕ ПРОБЛЕМ (AST-анализ)
    # ================================================================

    def find_issues_in_file(self, file_path: Path | str,
                            skip_cache: bool = False) -> list[dict]:
        """
        Найти реальные проблемы в одном Python-файле.

        Returns:
            Список dict-представлений Issue (совместимо с models.Issue.to_dict).
        """
        file_path = Path(file_path)
        if not file_path.exists():
            return []

        try:
            stat = file_path.stat()
            source = file_path.read_text(encoding="utf-8", errors="ignore")
        except OSError:
            return []

        # Кэш по (mtime, size) — не переанализируем неизменённые файлы
        if not skip_cache:
            cache_key = str(file_path)
            cached = self._cache.get(cache_key)
            if cached and cached[0] == stat.st_mtime and cached[1] == stat.st_size:
                return [dict(i) for i in cached[2]]

        issues = self._analyze_source(source, str(file_path))

        # Сохраняем в кэш
        self._cache[str(file_path)] = (stat.st_mtime, stat.st_size,
                                       [dict(i) for i in issues])

        return issues

    def find_project_issues(self, limit: Optional[int] = None,
                            only_fixable: bool = False) -> list[dict]:
        """
        Найти проблемы во всех директориях сканирования.

        Args:
            limit: максимум файлов для анализа (None = config.error_scan_limit)
            only_fixable: только исправимые проблемы
        """
        limit = limit or self.config.error_scan_limit
        all_issues: list[dict] = []
        scanned = 0

        for dir_name in self.config.scan_directories:
            if scanned >= limit:
                break
            dir_path = Path(dir_name)
            if not dir_path.exists():
                continue

            for py_file in dir_path.rglob("*.py"):
                if scanned >= limit:
                    break

                # Пропускаем служебные директории
                parts = py_file.parts
                if any(p in parts for p in ("__pycache__", ".git",
                                            "node_modules", "venv",
                                            ".venv", "state")):
                    continue
                if py_file.name == "__init__.py":
                    continue

                issues = self.find_issues_in_file(py_file)
                scanned += 1

                for issue in issues:
                    if only_fixable and not issue.get("fixable"):
                        continue
                    all_issues.append(issue)

        return all_issues

    def _analyze_source(self, source: str, file_path: str) -> list[dict]:
        """Анализ одного исходника."""
        issues: list[Issue] = []

        try:
            tree = ast.parse(source)
        except SyntaxError as e:
            issues.append(Issue(
                file=file_path,
                line=e.lineno or 1,
                severity="error",
                category="syntax_error",
                description=f"Ошибка синтаксиса: {e.msg}",
                suggestion="Исправить синтаксис вручную — автозамена небезопасна",
            ))
            return [i.__dict__ for i in issues]

        # Неиспользуемые импорты
        issues.extend(self._check_unused_imports(tree, source, file_path))

        # Сравнения с None через == / !=
        issues.extend(self._check_eq_none(tree, source, file_path))

        # Изменяемые аргументы по умолчанию
        issues.extend(self._check_mutable_defaults(tree, source, file_path))

        # Голый except:
        issues.extend(self._check_bare_except(tree, source, file_path))

        # Проглоченные исключения
        issues.extend(self._check_swallowed_exceptions(tree, source, file_path))

        # Неопределённые имена
        issues.extend(self._check_undefined_names(tree, source, file_path))

        # Переопределения встроенных имён
        issues.extend(self._check_shadowed_builtins(tree, source, file_path))

        return [i.__dict__ for i in issues]

    # ----------------------------------------------------------------
    #  Отдельные проверки
    # ----------------------------------------------------------------

    def _check_unused_imports(self, tree: ast.AST, source: str,
                              file_path: str) -> list[Issue]:
        """Неиспользуемые импорты. Удаление безопасно."""
        issues: list[Issue] = []
        used_names = self._collect_used_names(tree)

        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                # Текст без этого импорта — ищем имя в остальном коде
                text_without = self._without_node(source, node)
                for alias in node.names:
                    name = alias.asname or alias.name.split(".")[0]
                    if name in used_names:
                        continue
                    if re.search(rf"\b{re.escape(name)}\b", text_without):
                        continue  # имя используется в другом месте
                    issues.append(self._make_issue(
                        file_path, node, "warning", "unused_import",
                        f"Неиспользуемый импорт: {alias.name}",
                        "Удалить импорт",
                        fixable=True,
                        fix={"kind": "remove_import", "name": name},
                    ))
            elif isinstance(node, ast.ImportFrom):
                if node.module == "__future__":
                    continue
                text_without = self._without_node(source, node)
                for alias in node.names:
                    if alias.name == "*":
                        continue
                    name = alias.asname or alias.name
                    if name in used_names:
                        continue
                    if re.search(rf"\b{re.escape(name)}\b", text_without):
                        continue
                    issues.append(self._make_issue(
                        file_path, node, "warning", "unused_import",
                        f"Неиспользуемый импорт: {alias.name}",
                        "Удалить импорт",
                        fixable=True,
                        fix={"kind": "remove_import", "name": name},
                    ))

        return issues

    def _check_eq_none(self, tree: ast.AST, source: str,
                       file_path: str) -> list[Issue]:
        """Сравнения `x == None` / `x != None`."""
        issues: list[Issue] = []
        for node in ast.walk(tree):
            if not isinstance(node, ast.Compare):
                continue
            for op, comparator in zip(node.ops, node.comparators):
                if isinstance(op, (ast.Eq, ast.NotEq)) and \
                        isinstance(comparator, ast.Constant) and \
                        comparator.value is None:
                    replacement = "is" if isinstance(op, ast.Eq) else "is not"
                    issues.append(self._make_issue(
                        file_path, node, "warning", "eq_none",
                        f"Сравнение с None через {'==' if isinstance(op, ast.Eq) else '!='} "
                        f"(строка {node.lineno})",
                        f"Заменить на '{replacement} None'",
                        fixable=True,
                        fix={"kind": "eq_none", "lineno": node.lineno},
                    ))
                    break
        return issues

    def _check_mutable_defaults(self, tree: ast.AST, source: str,
                                file_path: str) -> list[Issue]:
        """Изменяемые аргументы по умолчанию."""
        issues: list[Issue] = []
        for node in ast.walk(tree):
            if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                continue
            for arg, default in zip(node.args.args, node.args.defaults):
                if isinstance(default, (ast.List, ast.Dict, ast.Set)):
                    issues.append(self._make_issue(
                        file_path, node, "warning", "mutable_default",
                        f"Изменяемый аргумент по умолчанию: {arg.arg} "
                        f"(функция {node.name}, строка {node.lineno})",
                        f"Заменить на 'None' и добавить guard: "
                        f"'if {arg.arg} is None: {arg.arg} = ...'",
                        fixable=True,
                        fix={"kind": "mutable_default",
                             "arg": arg.arg,
                             "func_lineno": node.lineno},
                    ))

        return issues

    def _check_bare_except(self, tree: ast.AST, source: str,
                           file_path: str) -> list[Issue]:
        """Голый `except:`."""
        issues: list[Issue] = []
        for node in ast.walk(tree):
            if isinstance(node, ast.ExceptHandler) and node.type is None:
                has_body = bool(node.body)
                issues.append(self._make_issue(
                    file_path, node, "warning", "bare_except",
                    f"Голый except: без типа исключения (строка {node.lineno})",
                    "Указать тип исключения, например except Exception:",
                    fixable=has_body,
                    fix={"kind": "bare_except", "lineno": node.lineno},
                ))
        return issues

    def _check_swallowed_exceptions(self, tree: ast.AST, source: str,
                                    file_path: str) -> list[Issue]:
        """`except ...: pass` — исключение проглочено."""
        issues: list[Issue] = []
        for node in ast.walk(tree):
            if not isinstance(node, ast.ExceptHandler):
                continue
            # Тело состоит только из pass
            body_only_pass = all(
                isinstance(stmt, ast.Pass) for stmt in node.body
            )
            if body_only_pass:
                issues.append(self._make_issue(
                    file_path, node, "warning", "swallowed_exception",
                    f"Исключение проглочено (except: pass), строка {node.lineno}",
                    "Залогировать исключение или сузить тип",
                    fixable=False,
                ))
        return issues

    def _check_undefined_names(self, tree: ast.AST, source: str,
                               file_path: str) -> list[Issue]:
        """Имена, которые используются, но нигде не определены."""
        issues: list[Issue] = []
        defined = self._collect_defined_names(tree)
        builtin_names = set(dir(builtins))
        undefined: dict[str, int] = {}

        for node in ast.walk(tree):
            if isinstance(node, ast.Name) and isinstance(node.ctx, ast.Load):
                name = node.id
                if name in defined or name in builtin_names:
                    continue
                # Магические имена Python (__file__, __name__, __doc__ и т.д.)
                # определяются интерпретатором автоматически
                if name.startswith("__") and name.endswith("__"):
                    continue
                undefined.setdefault(name, node.lineno)

        for name, lineno in undefined.items():
            issue = Issue(
                file=file_path,
                line=lineno,
                severity="error",
                category="undefined_name",
                description=f"Неопределённое имя: '{name}' (риск NameError)",
                suggestion=f"Определить '{name}' или исправить опечатку",
            )
            issue.__dict__["fixable"] = False
            issues.append(issue)

        return issues

    def _check_shadowed_builtins(self, tree: ast.AST, source: str,
                                 file_path: str) -> list[Issue]:
        """Переопределение встроенных имён (def list(...), len = ...)."""
        issues: list[Issue] = []
        for node in ast.walk(tree):
            name = None
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef,
                                 ast.ClassDef)):
                name = node.name
            elif isinstance(node, ast.Name) and isinstance(node.ctx, ast.Store):
                name = node.id
            if name and name in self.BUILTIN_NAMES:
                issue = Issue(
                    file=file_path,
                    line=node.lineno,
                    severity="info",
                    category="shadowed_builtin",
                    description=f"Переопределение встроенного имени: '{name}'",
                    suggestion=f"Переименовать, чтобы не затенять встроенный '{name}'",
                )
                issue.__dict__["fixable"] = False
                issues.append(issue)

        return issues

    # ----------------------------------------------------------------
    #  Вспомогательные методы анализа
    # ----------------------------------------------------------------

    @staticmethod
    def _collect_used_names(tree: ast.AST) -> set[str]:
        """Все имена, загружаемые/присваиваемые в коде."""
        names = set()
        for node in ast.walk(tree):
            if isinstance(node, ast.Name):
                names.add(node.id)
            elif isinstance(node, ast.Attribute):
                pass  # корень цепочки уже пойман Name
        return names

    @staticmethod
    def _collect_defined_names(tree: ast.AST) -> set[str]:
        """Имена, определённые в модуле: функции, классы, присваивания, импорты."""
        defined = set()
        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef,
                                 ast.ClassDef)):
                defined.add(node.name)
                # Параметры функций (включая вложенные)
                if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    args = list(node.args.args) + list(node.args.kwonlyargs)
                    if node.args.vararg:
                        args.append(node.args.vararg)
                    if node.args.kwarg:
                        args.append(node.args.kwarg)
                    for arg in args:
                        if arg is not None:
                            defined.add(arg.arg)
            elif isinstance(node, ast.Name) and isinstance(node.ctx, ast.Store):
                defined.add(node.id)
            elif isinstance(node, ast.Import):
                for alias in node.names:
                    defined.add(alias.asname or alias.name.split(".")[0])
            elif isinstance(node, ast.ImportFrom):
                for alias in node.names:
                    if alias.name != "*":
                        defined.add(alias.asname or alias.name)
            elif isinstance(node, ast.ExceptHandler) and node.name:
                defined.add(node.name)
            elif isinstance(node, ast.NamedExpr):
                if isinstance(node.target, ast.Name) and \
                        isinstance(node.target.ctx, ast.Store):
                    defined.add(node.target.id)
            elif isinstance(node, (ast.For, ast.AsyncFor, ast.With, ast.AsyncWith)):
                for target in ast.walk(node.target if hasattr(node, 'target') else node):
                    if isinstance(target, ast.Name) and isinstance(target.ctx, ast.Store):
                        defined.add(target.id)
        return defined

    def _make_issue(self, file_path: str, node: ast.AST, severity: str,
                    category: str, description: str, suggestion: str,
                    fixable: bool = False,
                    fix: Optional[dict] = None) -> Issue:
        """Собрать Issue с позицией и стратегией исправления."""
        issue = Issue(
            file=file_path,
            line=getattr(node, "lineno", 1),
            severity=severity,
            category=category,
            description=description,
            suggestion=suggestion,
        )
        # Дополнительные поля (dict-совместимо)
        if fixable:
            issue.__dict__["fixable"] = True
            issue.__dict__["fix"] = fix
        else:
            issue.__dict__["fixable"] = False
        return issue

    # ================================================================
    #  3. СВЯЗКА С ЛОГАМИ (traceback → файл:строка → проверка места)
    # ================================================================

    def find_issue_from_log(self, log_message: str) -> Optional[dict]:
        """
        Найти проблему по сообщению из лога приложения.

        Ищет в traceback `File "...py", line N` и анализирует конкретное место.
        """
        matches = re.findall(r'File\s+"([^"]+\.py)",\s*line\s+(\d+)',
                             log_message)
        if not matches:
            return None

        # Пробуем от наиболее вероятного (первый в traceback — обычно источник)
        for rel_file, line_str in matches:
            path = Path(rel_file)
            if not path.exists():
                # Возможно относительный путь от корня проекта
                path = Path(".") / rel_file
                if not path.exists():
                    continue
            try:
                line_no = int(line_str)
            except ValueError:
                continue

            try:
                source = path.read_text(encoding="utf-8", errors="ignore")
            except OSError:
                continue

            issues = self._analyze_source(source, str(path))
            # Выбираем проблемы на этой строке или ближайшие
            near = [i for i in issues if abs(i["line"] - line_no) <= 2]
            if near:
                issue = min(near, key=lambda i: abs(i["line"] - line_no))
                issue["source"] = "app_log"
                return issue

        return None

    # ================================================================
    #  4. ИСПРАВЛЕНИЕ ОШИБОК
    # ================================================================

    def fix_issue(self, issue: dict) -> dict:
        """
        Применить исправление для проблемы.

        Полный цикл:
          1. Резервная копия
          2. Правка исходника
          3. Проверка compile()
          4. Повторный анализ (убедиться, что проблема исчезла)
          5. Откат при любой неудаче

        Returns:
            {"fixed": bool, "description": str, "lines_changed": int,
             "error": str, "backup": str}
        """
        result = {
            "fixed": False,
            "description": "",
            "lines_changed": 0,
            "error": "",
            "backup": "",
        }

        file_path = Path(issue.get("file", ""))
        if not file_path.exists():
            result["error"] = f"Файл не найден: {file_path}"
            return result

        try:
            source = file_path.read_text(encoding="utf-8", errors="ignore")
        except OSError as e:
            result["error"] = f"Ошибка чтения: {e}"
            return result

        fix = issue.get("fix")
        fixable = issue.get("fixable", False)
        if not fixable or not isinstance(fix, dict):
            result["error"] = "Проблема не имеет безопасной автозамены"
            return result

        kind = fix.get("kind")
        handler = getattr(self, f"_apply_fix_{kind}", None)
        if handler is None:
            result["error"] = f"Неизвестный тип исправления: {kind}"
            return result

        # 1. Резервная копия
        backup = self._create_backup(file_path)
        if backup is None:
            result["error"] = "Не удалось создать резервную копию"
            return result
        result["backup"] = str(backup)

        # 2. Правка
        try:
            new_source, description = handler(source, fix)
        except Exception as e:
            result["error"] = f"Ошибка применения правки: {e}"
            self._rollback(file_path, backup)
            return result

        if new_source == source:
            result["error"] = "Правка ничего не изменила"
            return result

        # 3. Проверка компиляции
        try:
            compile(new_source, str(file_path), "exec")
        except SyntaxError as e:
            result["error"] = f"Правка сломала синтаксис: {e}"
            self._rollback(file_path, backup)
            return result

        # 4. Запись
        try:
            file_path.write_text(new_source, encoding="utf-8")
        except OSError as e:
            result["error"] = f"Ошибка записи: {e}"
            self._rollback(file_path, backup)
            return result

        # 5. Повторный анализ — проблема должна исчезнуть
        new_issues = self.find_issues_in_file(file_path, skip_cache=True)
        still_present = self._issue_still_present(issue, new_issues)
        if still_present:
            result["error"] = "Проблема не устранена после правки"
            self._rollback(file_path, backup)
            return result

        # Успех
        old_len = len(source.splitlines())
        new_len = len(new_source.splitlines())
        result.update({
            "fixed": True,
            "description": description,
            "lines_changed": abs(new_len - old_len),
        })

        # Инвалидируем кэш
        self._cache.pop(str(file_path), None)

        self.logger.info(f"✅ Исправлено: {issue.get('category')} — "
                         f"{file_path}:{issue.get('line')} — {description}")
        return result

    def _issue_still_present(self, original: dict, new_issues: list[dict]) -> bool:
        """Есть ли среди новых проблем та же самая (по категории и описанию)."""
        orig_desc = original.get("description", "")
        orig_cat = original.get("category", "")
        orig_file = original.get("file", "")
        for ni in new_issues:
            if ni.get("category") != orig_cat:
                continue
            if ni.get("file") != orig_file:
                continue
            # Сравниваем по описанию — оно уникально для каждой проблемы
            # (для eq_none/unused_import содержит имя/строку).
            if ni.get("description", "") == orig_desc:
                return True
        return False

    def fix_file_issues(self, file_path: Path | str,
                        max_fixes: int = 20) -> list[dict]:
        """
        Исправить все исправимые проблемы в одном файле.

        После каждой правки файл пересканируется — поэтому номера строк
        не «устаревают» и многократные проблемы одного типа правятся корректно.

        Returns:
            Список результатов fix_issue для каждой применённой правки.
        """
        file_path = Path(file_path)
        results: list[dict] = []
        fixed_count = 0

        while fixed_count < max_fixes:
            issues = self.find_issues_in_file(file_path, skip_cache=True)
            fixable = [i for i in issues if i.get("fixable")]
            if not fixable:
                break

            # Берём первую исправимую проблему
            result = self.fix_issue(fixable[0])
            results.append(result)
            if result.get("fixed"):
                fixed_count += 1
            else:
                # Правка не удалась — не зацикливаемся, выходим
                break

        return results

    # ----------------------------------------------------------------
    #  Конкретные правки
    # ----------------------------------------------------------------

    def _apply_fix_remove_import(self, source: str, fix: dict) -> tuple[str, str]:
        """Удалить неиспользуемый импорт."""
        tree = ast.parse(source)
        target_name = fix.get("name", "")
        edits = []
        n_removed = 0

        for node in ast.walk(tree):
            if isinstance(node, (ast.Import, ast.ImportFrom)):
                names = node.names if isinstance(node, ast.Import) else [
                    a for a in node.names if a.name != "*"]
                matching = [a for a in names
                            if (a.asname or a.name.split(".")[0]) == target_name]
                if not matching:
                    continue
                if len(names) == len(matching):
                    # Убираем весь импорт-стейтмент вместе со строкой
                    # (включая возможный хвостовой комментарий)
                    start = self._char_offset(source, node.lineno, 0)
                    # end_lineno/end_col_offset всегда заданы в Python 3.8+,
                    # но стабы типов помечают их Optional — подстрахуемся
                    end_lineno = node.end_lineno or node.lineno
                    end_col = node.end_col_offset or 0
                    lines = source.splitlines()
                    if end_lineno - 1 < len(lines):
                        end = start + len(lines[end_lineno - 1])
                        if end < len(source):
                            end += 1  # забираем перевод строки
                    else:
                        end = self._char_offset(source, end_lineno, end_col)
                        if end_col > 0:
                            end += 1
                    edits.append((start, min(end, len(source)), ""))
                    n_removed += 1
                # Частичное удаление алиасов — пропускаем для простоты/безопасности

        if not edits:
            return source, ""
        new_source = self._apply_edits(source, edits)
        return new_source, f"Удалён неиспользуемый импорт '{target_name}' ({n_removed} стейтмент)"

    def _apply_fix_eq_none(self, source: str, fix: dict) -> tuple[str, str]:
        """`== None` → `is None`, `!= None` → `is not None` (во всём файле)."""
        tree = ast.parse(source)
        edits = []
        n_fixed = 0
        for node in ast.walk(tree):
            if not isinstance(node, ast.Compare):
                continue
            for op, comparator in zip(node.ops, node.comparators):
                if isinstance(op, (ast.Eq, ast.NotEq)) and \
                        isinstance(comparator, ast.Constant) and \
                        comparator.value is None:
                    span_start = self._node_end_offset(source, node.left)
                    span_end = self._char_offset(source, comparator.lineno,
                                                 comparator.col_offset)
                    if span_end <= span_start:
                        continue
                    span = source[span_start:span_end]
                    new_span = span.replace("==", "is").replace("!=", "is not")
                    if new_span != span:
                        edits.append((span_start, span_end, new_span))
                        n_fixed += 1
                    break

        if not edits:
            return source, ""
        new_source = self._apply_edits(source, edits)
        return new_source, f"Заменено {n_fixed} сравнений с None на 'is'/'is not'"

    def _apply_fix_mutable_default(self, source: str, fix: dict) -> tuple[str, str]:
        """Изменяемый дефолт → None + guard-строка (по аргументу в файле)."""
        tree = ast.parse(source)
        arg_name = fix.get("arg", "")
        edits = []
        n_fixed = 0

        for node in ast.walk(tree):
            if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                continue
            for arg, default in zip(node.args.args, node.args.defaults):
                if arg.arg != arg_name:
                    continue
                if not isinstance(default, (ast.List, ast.Dict, ast.Set)):
                    continue
                def_start = self._char_offset(source, default.lineno, default.col_offset)
                def_end = self._node_end_offset(source, default)
                default_repr = source[def_start:def_end]
                edits.append((def_start, def_end, "None"))
                if node.body:
                    body_line = node.body[0].lineno
                    line_start = self._char_offset(source, body_line, 0)
                    indent = source[line_start:line_start + node.body[0].col_offset]
                    guard = (f"{indent}if {arg_name} is None:\n"
                             f"{indent}    {arg_name} = {default_repr}\n")
                    edits.append((line_start, line_start, guard))
                n_fixed += 1
                break

        if not edits:
            return source, ""
        new_source = self._apply_edits(source, edits)
        return new_source, f"{n_fixed} изменяемых дефолтов '{arg_name}' заменены на None + guard"

    def _apply_fix_bare_except(self, source: str, fix: dict) -> tuple[str, str]:
        """`except:` → `except Exception:` (во всём файле)."""
        tree = ast.parse(source)
        edits = []
        n_fixed = 0
        for node in ast.walk(tree):
            if not isinstance(node, ast.ExceptHandler) or node.type is not None:
                continue
            start = self._char_offset(source, node.lineno, 0)
            end = self._char_offset(source, node.lineno, node.col_offset + 7)
            snippet = source[start:end]
            if snippet.rstrip().endswith(":"):
                new_line = snippet.replace("except:", "except Exception:")
                if new_line != snippet:
                    edits.append((start, end, new_line))
                    n_fixed += 1
                else:
                    # Например "except :" — попробуем с пробелом
                    new_line = re.sub(r"except\s*:", "except Exception:", snippet)
                    if new_line != snippet:
                        edits.append((start, end, new_line))
                        n_fixed += 1

        if not edits:
            return source, ""
        new_source = self._apply_edits(source, edits)
        return new_source, f"Заменено {n_fixed} 'except:' на 'except Exception:'"

    # ----------------------------------------------------------------
    #  Работа со смещениями и правками
    # ----------------------------------------------------------------

    @staticmethod
    def _line_starts(source: str) -> list[int]:
        starts = [0]
        for m in re.finditer("\n", source):
            starts.append(m.end())
        return starts

    def _char_offset(self, source: str, lineno: int, col_offset: int) -> int:
        starts = self._line_starts(source)
        if lineno - 1 >= len(starts):
            return len(source)
        return min(starts[lineno - 1] + col_offset, len(source))

    def _node_end_offset(self, source: str, node: ast.AST) -> int:
        end_lineno = node.end_lineno or node.lineno
        end_col = node.end_col_offset or 0
        return self._char_offset(source, end_lineno, end_col)

    def _remove_node(self, source: str, node: ast.AST) -> str:
        """Удалить узел (строку или диапазон строк) из исходника."""
        end_lineno = node.end_lineno or node.lineno
        end_col = node.end_col_offset or 0
        start = self._char_offset(source, node.lineno, 0)
        end = self._char_offset(source, end_lineno, end_col)
        # Если забираем всю строку — удаляем и перевод строки
        if end_col > 0:
            end += 1  # переводим на следующий символ (после удаляемого)
        return source[:start] + source[end:]

    def _without_node(self, source: str, node: ast.AST) -> str:
        """Исходник без текста указанного узла (для поиска имён вне импорта)."""
        end_lineno = node.end_lineno or node.lineno
        start = self._char_offset(source, node.lineno, 0)
        end = self._char_offset(source, end_lineno, 0)
        # Добавляем длину последней строки, чтобы убрать весь блок строк
        lines = source.splitlines()
        if end_lineno - 1 < len(lines):
            end += len(lines[end_lineno - 1]) + 1
        if end > len(source):
            end = len(source)
        return source[:start] + source[end:]

    @staticmethod
    def _apply_edits(source: str, edits: list[tuple[int, int, str]]) -> str:
        """Применить правки (start, end, new_text), сортируя по убыванию."""
        for start, end, new_text in sorted(edits, key=lambda e: e[0], reverse=True):
            source = source[:start] + new_text + source[end:]
        return source

    # ----------------------------------------------------------------
    #  Резервные копии и откат
    # ----------------------------------------------------------------

    def _create_backup(self, file_path: Path) -> Optional[Path]:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_path = self.backup_dir / f"{file_path.name}.{timestamp}.bak"
        try:
            shutil.copy2(file_path, backup_path)
            return backup_path
        except OSError as e:
            self.logger.error(f"Ошибка создания резервной копии {file_path}: {e}")
            return None

    def _rollback(self, file_path: Path, backup_path: Path) -> bool:
        try:
            shutil.copy2(backup_path, file_path)
            self.logger.info(f"↩️ Откат: {file_path}")
            return True
        except OSError as e:
            self.logger.error(f"Ошибка отката {file_path}: {e}")
            return False

    # ================================================================
    #  СТАТИСТИКА
    # ================================================================

    def get_statistics(self) -> dict:
        """Статистика поиска ошибок."""
        return {
            "cache_size": len(self._cache),
            "backup_dir": str(self.backup_dir),
            "backups_count": len(list(self.backup_dir.glob("*.bak"))),
        }
