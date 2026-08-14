"""
Менеджер патчей Шиори — управление патчами и восстановлением.

Реализует:
  - Создание и применение патчей
  - Резервное копирование перед изменениями
  - Откат при неудачном применении
  - Управление уязвимостями
"""

from __future__ import annotations
import json
import logging
import random
from datetime import datetime
from pathlib import Path
from typing import Any, Optional

from shiori.engine.config import ShioriConfig
from shiori.engine.models import Patch


class PatchManager:
    """
    Менеджер патчей — управление патчами и восстановлением Вугларста.
    """
    
    def __init__(self, config: ShioriConfig):
        self.config = config
        self.patches_applied: list[Patch] = []
        self.backup_dir = config.state_dir / "backups"
        self.backup_dir.mkdir(parents=True, exist_ok=True)
        self.logger = logging.getLogger("ShioriPatchManager")
        self.llm = None
    
    def set_llm(self, llm):
        """Установить LLM сервис для генерации кода."""
        self.llm = llm
    
    # ================================================================
    #  СОЗДАНИЕ И ПРИМЕНЕНИЕ ПАТЧЕЙ
    # ================================================================
    
    def create_patch(self, vulnerability_id: str, description: str) -> Patch:
        """
        Создать патч для устранения уязвимости.
        
        Args:
            vulnerability_id: ID уязвимости
            description: описание патча
        
        Returns:
            Созданный патч
        """
        patch = Patch(
            id=f"PATCH-{datetime.now().strftime('%Y%m%d%H%M%S')}-{random.randint(1000, 9999)}",
            vulnerability_id=vulnerability_id,
            description=description,
        )
        
        self.logger.debug(f"Создан патч {patch.id} для уязвимости {vulnerability_id}: {description}")
        return patch
    
    def apply_patch(self, patch: Patch) -> bool:
        """
        Применить патч с проверками и резервным копированием.
        
        Args:
            patch: патч для применения
        
        Returns:
            True если успешно, False если ошибка
        """
        self.logger.info(f"🔧 Применение патча: {patch.id} (уязвимость {patch.vulnerability_id})")
        
        # Проверка перед применением
        if not self._pre_patch_checks(patch):
            self.logger.warning(f"⚠️ Отклонено предварительными проверками: {patch.id}")
            return False
        
        # Резервное копирование
        if self.config.backup_before_patch:
            self._create_backup(patch)
        
        # Симуляция применения патча
        success = self._simulate_patch_application(patch)
        
        if success:
            patch.applied = True
            patch.success = True
            patch.applied_at = datetime.now().isoformat()
            patch.applied_by = "Shiori"
            self.patches_applied.append(patch)
            self.logger.info(f"✅ Патч применён успешно: {patch.id} — {patch.description}")
            return True
        else:
            self.logger.warning(f"❌ Патч не применён: {patch.id} — {patch.description}")
            # Откат при неудаче
            if self.config.rollback_on_failure:
                self._rollback_patch(patch)
            return False
    
    def _pre_patch_checks(self, patch: Patch) -> bool:
        """
        Проверки перед применением патча.
        """
        # Проверка валидности ID
        if not patch.vulnerability_id or not patch.vulnerability_id.startswith("VULN-"):
            self.logger.warning(f"Неверный ID уязвимости у патча {patch.id}: {patch.vulnerability_id}")
            return False
        
        # Проверка доступности резервной копии
        if self.config.backup_before_patch:
            # В реальной системе проверка файлов
            pass
        
        return True
    
    def _create_backup(self, patch: Patch):
        """
        Создать резервную копию перед применением патча.
        """
        backup_data = {
            "timestamp": datetime.now().isoformat(),
            "patch_id": patch.id,
            "vulnerability_id": patch.vulnerability_id,
            "backup_type": "pre_patch",
            "system_state": "pre_patch",
        }
        
        backup_path = self.backup_dir / f"backup_{patch.id}.json"
        with open(backup_path, "w", encoding="utf-8") as f:
            json.dump(backup_data, f, ensure_ascii=False, indent=2)
        
        self.logger.debug(f"Резервная копия создана: {backup_path}")
    
    def _simulate_patch_application(self, patch: Patch) -> bool:
        """
        Применить патч с использованием LLM Coder или симуляции.
        
        В реальной системе это:
          - Применение патча к файлам
          - Проверка целостности
          - Тестирование функциональности
        """
        # Если есть LLM Coder — генерируем реальный патч
        if self.llm and self.llm.coder_loaded:
            return self._apply_llm_patch(patch)
        
        # Иначе — симуляция
        # 90% успешных патчей (симуляция)
        result = random.random() < 0.9
        self.logger.debug(f"Симуляция применения патча {patch.id}: {'успех' if result else 'отказ'}")
        return result
    
    def _apply_llm_patch(self, patch: Patch) -> bool:
        """
        Применить патч с помощью LLM Coder.
        
        Args:
            patch: патч для применения
            
        Returns:
            True если успешно, False если ошибка
        """
        try:
            # Гарантируем, что LLM не None (проверено выше)
            assert self.llm is not None, "LLM должен быть установлен"
            
            self.logger.info(f"💻 LLM Coder генерирует патч для {patch.vulnerability_id}")
            
            # Формируем запрос для кодера
            prompt = (
                f"Устранить уязвимость {patch.vulnerability_id}.\n"
                f"Описание: {patch.description}\n\n"
                f"Напиши исправленный код или патч.\n"
            )
            
            # Генерируем патч с помощью LLM
            generated_code = self.llm.generate_coder(prompt)
            
            if generated_code.startswith("# [Ошибка") or generated_code.startswith("# [LLM"):
                self.logger.warning(f"⚠️ LLM Coder не смогла сгенерировать патч: {generated_code[:50]}")
                return False
            
            # В реальной системе здесь был бы код записи патча в файлы
            # self._write_patch_to_files(patch, generated_code)
            
            patch.generated_code = generated_code[:500]  # Сохраняем начало кода
            self.logger.info(f"✅ LLM Coder сгенерировала патч для {patch.id}")
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Ошибка применения LLM патча: {e}")
            return False
    
    def _rollback_patch(self, patch: Patch):
        """
        Откатить патч при неудачном применении.
        """
        # Восстановление из резервной копии
        backup_path = self.backup_dir / f"backup_{patch.id}.json"
        if backup_path.exists():
            self.logger.debug(f"Восстановление из резервной копии: {backup_path}")
            # В реальной системе восстановление данных
            pass
        
        patch.applied = False
        patch.rollback_available = False
        self.logger.warning(f"↩️ Откат патча: {patch.id} (уязвимость {patch.vulnerability_id})")
    
    # ================================================================
    #  УПРАВЛЕНИЕ ПАТЧАМИ
    # ================================================================
    
    def get_pending_patches(self) -> list[Patch]:
        """
        Получить список ожидающих применения патчей.
        """
        # В реальной системе запрос к базе уязвимостей
        return []
    
    def apply_all_pending(self) -> list[Patch]:
        """
        Применить все ожидающие патчи.
        
        Returns:
            Список успешно применённых патчей
        """
        applied = []
        
        for patch in self.get_pending_patches():
            if self.apply_patch(patch):
                applied.append(patch)
        
        return applied
    
    def rollback_last_patch(self) -> bool:
        """
        Откатить последний применённый патч.
        
        Returns:
            True если успешно откатили
        """
        if not self.patches_applied:
            return False
        
        last_patch = self.patches_applied[-1]
        
        if last_patch.rollback_available:
            last_patch.applied = False
            self.patches_applied.pop()
            return True
        
        return False
    
    # ================================================================
    #  СТАТИСТИКА И ОТЧЁТЫ
    # ================================================================
    
    def get_patch_statistics(self) -> dict[str, Any]:
        """
        Получить статистику по патчам.
        """
        total = len(self.patches_applied)
        successful = sum(1 for p in self.patches_applied if p.applied)
        failed = total - successful
        
        return {
            "total_patches": total,
            "successful_patches": successful,
            "failed_patches": failed,
            "success_rate": successful / total if total > 0 else 0,
        }
    
    def export_patches_log(self, path: Optional[Path] = None) -> Path:
        """
        Экспортировать журнал патчей.
        """
        if path is None:
            path = self.config.state_dir / "patches_log.json"
        
        log_data = {
            "timestamp": datetime.now().isoformat(),
            "patches": [p.to_dict() for p in self.patches_applied],
            "statistics": self.get_patch_statistics(),
        }
        
        with open(path, "w", encoding="utf-8") as f:
            json.dump(log_data, f, ensure_ascii=False, indent=2)
        
        self.logger.debug(f"Журнал патчей экспортирован: {path}")
        return path
