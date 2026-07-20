"""
Нобука — Редактор документов проекта.

Нобука автономно:
  1. Сканирует все текстовые/markdown документы в проекте
  2. Анализирует их и предлагает улучшения
  3. Тестирует изменения (проверка в эксплуатации)
  4. Применяет с резервной копией
  5. Откатывает при проблемах
  6. Отчитывается о каждом изменении

Работает по всему проекту: Футаба, Вугларст, документация, протоколы.
"""

from __future__ import annotations

import json
import logging
import shutil
import time
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple


class DocumentEditor:
    """
    Редактор документов — Нобука улучшает тексты по всему проекту.
    
    Безопасность:
      - Каждое изменение тестируется перед применением
      - Создаётся резервная копия перед редактированием
      - При провале тестов — автоматический откат
      - Полное логирование всех действий
    """

    # Директории для сканирования документов
    SCAN_DIRS = [
        "vuglarst_state",
        "futaba",
        "Wuglarst/static",
        "docs",
    ]

    # Расширения документов, которые Нобука редактирует
    EDITABLE_EXTENSIONS = {".md", ".txt", ".json", ".yaml", ".yml", ".html", ".css", ".js"}

    # Исключения — файлы которые трогать нельзя
    EXCLUDE_PATTERNS = {
        "__pycache__", ".git", "node_modules", "state", ".bak",
        "build", "dist", ".venv", "venv",
    }

    def __init__(self, config: Any):
        self.config = config
        self.logger = logging.getLogger("DocumentEditor")
        self.project_root = Path(".")
        
        # Директория для резервных копий
        self.backup_dir = Path("nobuka/engine/state/document_backups")
        self.backup_dir.mkdir(parents=True, exist_ok=True)
        
        # Файл истории редактирований
        self.history_file = Path("nobuka/engine/state/edit_history.json")
        
        # Загружаем историю
        self.edit_history: List[Dict] = self._load_history()
        
        # Счётчики
        self.metrics = {
            "documents_scanned": 0,
            "edits_proposed": 0,
            "edits_tested": 0,
            "edits_applied": 0,
            "edits_rolled_back": 0,
        }

    # ================================================================
    #  ИСТОРИЯ
    # ================================================================

    def _load_history(self) -> List[Dict]:
        """Загружает историю редактирований."""
        if self.history_file.exists():
            try:
                return json.loads(self.history_file.read_text(encoding="utf-8"))
            except Exception:
                pass
        return []

    def _save_history(self):
        """Сохраняет историю редактирований."""
        # Храним последние 200 записей
        recent = self.edit_history[-200:]
        self.history_file.write_text(
            json.dumps(recent, ensure_ascii=False, indent=2),
            encoding="utf-8"
        )

    def get_history(self) -> List[Dict]:
        """Возвращает историю редактирований."""
        return self.edit_history

    def get_metrics(self) -> Dict[str, int]:
        """Возвращает метрики редактора."""
        return self.metrics

    # ================================================================
    #  СКАНИРОВАНИЕ ДОКУМЕНТОВ
    # ================================================================

    def scan_documents(self) -> List[Dict[str, Any]]:
        """
        Сканирует все документы в проекте.
        
        Returns:
            Список найденных документов с метаданными.
        """
        documents = []
        
        for scan_dir_name in self.SCAN_DIRS:
            scan_dir = self.project_root / scan_dir_name
            if not scan_dir.exists():
                continue
            
            for file_path in scan_dir.rglob("*"):
                if not file_path.is_file():
                    continue
                
                # Проверяем расширение
                if file_path.suffix not in self.EDITABLE_EXTENSIONS:
                    continue
                
                # Проверяем исключения
                rel_path = str(file_path.relative_to(self.project_root))
                if any(exc in rel_path for exc in self.EXCLUDE_PATTERNS):
                    continue
                if ".bak" in rel_path:
                    continue
                
                try:
                    content = file_path.read_text(encoding="utf-8")
                    documents.append({
                        "path": rel_path,
                        "filename": file_path.name,
                        "extension": file_path.suffix,
                        "size": len(content),
                        "lines": content.count("\n") + 1,
                        "last_modified": datetime.fromtimestamp(
                            file_path.stat().st_mtime
                        ).isoformat(),
                    })
                except Exception:
                    continue
        
        self.metrics["documents_scanned"] = len(documents)
        self.logger.info(f"📄 Нобука нашла {len(documents)} документов в проекте")
        
        return documents

    # ================================================================
    #  ЧТЕНИЕ И ЗАПИСЬ
    # ================================================================

    def read_document(self, rel_path: str) -> Optional[str]:
        """Читает документ проекта."""
        file_path = self.project_root / rel_path
        if not file_path.exists():
            return None
        try:
            return file_path.read_text(encoding="utf-8")
        except Exception as e:
            self.logger.error(f"❌ Ошибка чтения {rel_path}: {e}")
            return None

    def _create_backup(self, rel_path: str) -> Optional[Path]:
        """Создаёт резервную копию файла перед редактированием."""
        file_path = self.project_root / rel_path
        if not file_path.exists():
            return None
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        safe_name = rel_path.replace("/", "_").replace("\\", "_")
        backup_name = f"{safe_name}.{timestamp}.bak"
        backup_path = self.backup_dir / backup_name
        
        try:
            shutil.copy2(file_path, backup_path)
            self.logger.debug(f"💾 Резервная копия: {backup_path.name}")
            return backup_path
        except Exception as e:
            self.logger.error(f"❌ Ошибка создания резервной копии: {e}")
            return None

    def _rollback(self, rel_path: str, backup_path: Path) -> bool:
        """Откатывает изменения из резервной копии."""
        file_path = self.project_root / rel_path
        try:
            shutil.copy2(backup_path, file_path)
            self.logger.info(f"↩️ Откат выполнен: {rel_path}")
            return True
        except Exception as e:
            self.logger.error(f"❌ Ошибка отката {rel_path}: {e}")
            return False

    # ================================================================
    #  ТЕСТИРОВАНИЕ ИЗМЕНЕНИЙ (ПРОВЕРКА В ЭКСПЛУАТАЦИИ)
    # ================================================================

    def _test_edit(self, rel_path: str, new_content: str) -> Tuple[bool, str]:
        """
        Тестирует изменение перед применением.
        
        Проверки:
          1. Файл не пустой (если был не пустой)
          2. Синтаксис JSON/YAML валиден (если применимо)
          3. HTML/CSS/JS базовая валидность
          4. Кодировка корректна
          5. Размер не изменился критически (>90% удаления — подозрительно)
        
        Returns:
            (пройдено, отчёт)
        """
        file_path = self.project_root / rel_path
        old_content = ""
        if file_path.exists():
            old_content = file_path.read_text(encoding="utf-8")
        
        # 1. Проверка пустоты
        if not new_content.strip():
            return False, "Новый контент пуст"
        
        # 2. Проверка критического уменьшения
        if old_content and len(new_content) < len(old_content) * 0.1:
            return False, f"Контент уменьшен на >90% ({len(old_content)} → {len(new_content)} символов)"
        
        # 3. Проверка кодировки
        try:
            new_content.encode("utf-8")
        except Exception:
            return False, "Ошибка кодировки UTF-8"
        
        # 4. Проверка JSON
        if rel_path.endswith(".json"):
            try:
                json.loads(new_content)
            except json.JSONDecodeError as e:
                return False, f"Невалидный JSON: {e}"
        
        # 5. Проверка YAML (базовая)
        if rel_path.endswith((".yaml", ".yml")):
            try:
                import yaml
                yaml.safe_load(new_content)
            except ImportError:
                pass  # PyYAML может быть не установлен
            except Exception as e:
                return False, f"Невалидный YAML: {e}"
        
        # 6. Проверка HTML (базовая — наличие закрывающих тегов)
        if rel_path.endswith(".html"):
            open_tags = new_content.count("<div")
            close_tags = new_content.count("</div>")
            if abs(open_tags - close_tags) > 2:
                return False, f"Несбалансированные теги div: {open_tags} открывающих, {close_tags} закрывающих"
        
        # 7. Проверка JS (базовая — скобки)
        if rel_path.endswith(".js"):
            open_braces = new_content.count("{")
            close_braces = new_content.count("}")
            if abs(open_braces - close_braces) > 2:
                return False, f"Несбалансированные фигурные скобки: {open_braces} открывающих, {close_braces} закрывающих"
        
        # 8. Проверка markdown (базовая — наличие заголовков)
        if rel_path.endswith(".md"):
            if not new_content.strip().startswith("#"):
                # Не обязательно начинать с заголовка, но предупредим
                pass
        
        return True, "Все проверки пройдены"

    # ================================================================
    #  РЕДАКТИРОВАНИЕ
    # ================================================================

    def edit_document(
        self,
        rel_path: str,
        new_content: str,
        reason: str = "",
        operator: str = "nobuka"
    ) -> Dict[str, Any]:
        """
        Нобука редактирует документ с проверкой в эксплуатации.
        
        Полный цикл:
          1. Создание резервной копии
          2. Тестирование нового контента
          3. Применение (если тесты прошли)
          4. Пост-проверка (чтение и валидация)
          5. Откат при проблемах
        
        Returns:
            Отчёт о результате редактирования.
        """
        file_path = self.project_root / rel_path
        timestamp = datetime.now().isoformat()
        
        result = {
            "path": rel_path,
            "operator": operator,
            "reason": reason,
            "timestamp": timestamp,
            "success": False,
            "rolled_back": False,
            "old_size": 0,
            "new_size": len(new_content),
            "tests_passed": False,
            "test_report": "",
            "backup_path": "",
            "error": "",
        }
        
        # Проверяем существование файла
        if not file_path.exists():
            result["error"] = f"Файл не найден: {rel_path}"
            self.logger.error(f"❌ {result['error']}")
            return result
        
        old_content = file_path.read_text(encoding="utf-8")
        result["old_size"] = len(old_content)
        
        # Если контент не изменился
        if old_content == new_content:
            result["error"] = "Контент не изменился"
            self.logger.info(f"ℹ️ Контент не изменился: {rel_path}")
            return result
        
        self.metrics["edits_proposed"] += 1
        
        # 1. Создаём резервную копию
        backup_path = self._create_backup(rel_path)
        if not backup_path:
            result["error"] = "Не удалось создать резервную копию"
            return result
        result["backup_path"] = str(backup_path)
        
        # 2. Тестируем
        self.metrics["edits_tested"] += 1
        tests_passed, test_report = self._test_edit(rel_path, new_content)
        result["tests_passed"] = tests_passed
        result["test_report"] = test_report
        
        if not tests_passed:
            self.logger.warning(f"⚠️ Тесты не прошли: {test_report}")
            result["rolled_back"] = True
            self.metrics["edits_rolled_back"] += 1
            self.edit_history.append(result)
            self._save_history()
            return result
        
        self.logger.info(f"✅ Тесты прошли: {test_report}")
        
        # 3. Применяем
        try:
            file_path.write_text(new_content, encoding="utf-8")
            self.logger.info(f"✏️ Документ отредактирован: {rel_path}")
        except Exception as e:
            self.logger.error(f"❌ Ошибка записи: {e}")
            result["error"] = str(e)
            result["rolled_back"] = True
            self._rollback(rel_path, backup_path)
            self.metrics["edits_rolled_back"] += 1
            self.edit_history.append(result)
            self._save_history()
            return result
        
        # 4. Пост-проверка — читаем и проверяем
        try:
            verify_content = file_path.read_text(encoding="utf-8")
            if verify_content != new_content:
                self.logger.error("❌ Пост-проверка: контент не совпадает!")
                result["error"] = "Пост-проверка не пройдена"
                result["rolled_back"] = True
                self._rollback(rel_path, backup_path)
                self.metrics["edits_rolled_back"] += 1
                self.edit_history.append(result)
                self._save_history()
                return result
        except Exception as e:
            self.logger.error(f"❌ Ошибка пост-проверки: {e}")
            result["error"] = str(e)
            result["rolled_back"] = True
            self._rollback(rel_path, backup_path)
            self.metrics["edits_rolled_back"] += 1
            self.edit_history.append(result)
            self._save_history()
            return result
        
        # 5. Успех!
        result["success"] = True
        self.metrics["edits_applied"] += 1
        self.edit_history.append(result)
        self._save_history()
        
        self.logger.info(f"✅ Редактирование завершено: {rel_path}")
        self.logger.info(f"   Размер: {result['old_size']} → {result['new_size']} символов")
        self.logger.info(f"   Причина: {reason}")
        
        return result

    # ================================================================
    #  АВТОНОМНОЕ УЛУЧШЕНИЕ ДОКУМЕНТОВ
    # ================================================================

    def auto_improve_documents(self) -> List[Dict[str, Any]]:
        """
        Нобука автономно улучшает документы по всему проекту.
        
        Для каждого документа:
          1. Анализирует контент
          2. Предлагает улучшения
          3. Тестирует
          4. Применяет с откатом при проблемах
        """
        self.logger.info("📝 Нобука начинает автоУлучшение документов")
        
        documents = self.scan_documents()
        results = []
        
        for doc in documents:
            rel_path = doc["path"]
            content = self.read_document(rel_path)
            
            if content is None:
                continue
            
            # Анализируем и предлагаем улучшения
            improved_content, reason = self._analyze_and_improve(content, rel_path)
            
            if improved_content is None or improved_content == content:
                continue
            
            # Редактируем с проверкой
            result = self.edit_document(
                rel_path=rel_path,
                new_content=improved_content,
                reason=reason,
                operator="nobuka_auto"
            )
            
            results.append(result)
        
        self.logger.info(f"📝 АвтоУлучшение завершено: {len(results)} документов обработано")
        self.logger.info(f"   Применено: {sum(1 for r in results if r['success'])}")
        self.logger.info(f"   Отклонено: {sum(1 for r in results if not r['success'])}")
        
        return results

    def _analyze_and_improve(self, content: str, rel_path: str) -> Tuple[Optional[str], str]:
        """
        Анализирует документ и предлагает улучшения.
        
        Улучшения:
          - Удаление trailing whitespace
          - Добавление финального newline
          - Нормализация line endings
          - Удаление дубликатов пустых строк
          - Для markdown: проверка структуры заголовков
        """
        improved = content
        reasons = []
        
        # 1. Удаление trailing whitespace
        lines = improved.split("\n")
        new_lines = [line.rstrip() for line in lines]
        if new_lines != lines:
            improved = "\n".join(new_lines)
            reasons.append("удаление trailing whitespace")
        
        # 2. Нормализация множественных пустых строк (не более 2 подряд)
        while "\n\n\n" in improved:
            improved = improved.replace("\n\n\n", "\n\n")
            if "нормализация пустых строк" not in reasons:
                reasons.append("нормализация пустых строк")
        
        # 3. Добавление финального newline
        if improved and not improved.endswith("\n"):
            improved += "\n"
            reasons.append("добавление финального newline")
        
        # 4. Для markdown — проверка пробелов вокруг заголовков
        if rel_path.endswith(".md"):
            # Добавляем пустую строку перед заголовком (если нет)
            lines = improved.split("\n")
            fixed_lines = []
            for i, line in enumerate(lines):
                if line.startswith("#") and i > 0 and fixed_lines and fixed_lines[-1].strip() != "":
                    fixed_lines.append("")
                fixed_lines.append(line)
            new_improved = "\n".join(fixed_lines)
            if new_improved != improved:
                improved = new_improved
                reasons.append("форматирование заголовков markdown")
        
        if not reasons:
            return None, ""
        
        return improved, "; ".join(reasons)

    # ================================================================
    #  УПРАВЛЕНИЕ ЧЕРЕЗ API
    # ================================================================

    def get_status(self) -> Dict[str, Any]:
        """Возвращает полный статус редактора для API."""
        return {
            "metrics": self.metrics,
            "history_count": len(self.edit_history),
            "recent_edits": self.edit_history[-10:],
            "backup_dir": str(self.backup_dir),
            "scan_dirs": self.SCAN_DIRS,
            "editable_extensions": list(self.EDITABLE_EXTENSIONS),
        }

    def restore_from_backup(self, rel_path: str, backup_name: str) -> bool:
        """Восстанавливает документ из резервной копии."""
        backup_path = self.backup_dir / backup_name
        file_path = self.project_root / rel_path
        
        if not backup_path.exists():
            self.logger.error(f"Резервная копия не найдена: {backup_name}")
            return False
        
        try:
            shutil.copy2(backup_path, file_path)
            self.logger.info(f"✅ Документ восстановлен: {rel_path}")
            
            self.edit_history.append({
                "path": rel_path,
                "operator": "manual_restore",
                "reason": f"Восстановление из {backup_name}",
                "timestamp": datetime.now().isoformat(),
                "success": True,
                "rolled_back": False,
            })
            self._save_history()
            return True
        except Exception as e:
            self.logger.error(f"❌ Ошибка восстановления: {e}")
            return False

    def list_backups(self) -> List[Dict[str, Any]]:
        """Возвращает список резервных копий."""
        backups = []
        for f in sorted(self.backup_dir.glob("*.bak"), reverse=True):
            stat = f.stat()
            backups.append({
                "filename": f.name,
                "size": stat.st_size,
                "created": datetime.fromtimestamp(stat.st_mtime).isoformat(),
            })
        return backups
