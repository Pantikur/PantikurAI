"""
Ядро постоянной работы Футаба — автономный цикл саморазвития.

Реализует:
  - Бесконечный цикл самопроверки и развития
  - Сбор сигналов обратной связи
  - Формирование и проверку гипотез улучшений
  - Внедрение изменений на разрешённом уровне автономности
  - Периодический запуск полигона испытаний
  - Полное логирование и сохранение состояния
"""

from __future__ import annotations

from scientists_network.character_system import CharacterSystem
import json
import logging
import random
import signal
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Any, Optional

from futaba.engine.config import FutabaConfig
from futaba.engine.models import (
    AutonomyLevel, ChangeRecord, ChangeType, Constitution, LogEntry, Law
)
from futaba.engine.trial_grounds import TrialGrounds
from futaba.engine.web_access import FutabaWebAccess
from futaba.engine.legal_studies import FutabaLegalStudies
from futaba.engine.world_state_modeler import FutabaWorldStateModeler


class FutabaCore:
    """
    Автономное ядро Футаба.
    
    Работает в бесконечном цикле:
      1. Самопроверка по Конституции
      2. Сбор сигналов (ошибки, обратная связь)
      3. Формирование гипотезы улучшения
      4. Проверка совместимости с Конституцией
      5. Внедрение (на разрешённом уровне автономности)
      6. Логирование
      7. Периодически — запуск полигона испытаний
    """
    
    def __init__(self, config: Optional[FutabaConfig] = None):
        self.config = config or FutabaConfig.default()
        self.constitution = Constitution(version=self.config.version)
        self.current_version = self.config.version
        
        # Состояние
        self.cycle_count = 0
        self.changes_history: list[ChangeRecord] = []
        self.metrics = {
            "self_checks_passed": 0,
            "self_checks_failed": 0,
            "changes_proposed": 0,
            "changes_applied": 0,
            "changes_rolled_back": 0,
            "trials_run": 0,
            "best_trial_score": 0.0,
            "laws_studied": 0,
            "legal_improvements_applied": 0,
            "compliance_reports_generated": 0,
            "world_simulations_run": 0,
            "ideal_states_modeled": 0,
        }
        
        # Логирование
        self._setup_logging()
        self.logger = logging.getLogger("FutabaCore")
        
        # Полигон испытаний
        self.trial_grounds = TrialGrounds(self.config)
        self.web_access = FutabaWebAccess(self.config)
        self.legal_studies = FutabaLegalStudies(self.config)
        self.world_modeler = FutabaWorldStateModeler(self.config)
        
        # Сигналы
        self._shutdown_requested = False
        self._setup_signals()
        
        # Инициализация random
        self._init_random()
        
        self.logger.info(f"Футаба {self.current_version} инициализирована")
        self.logger.info(f"Конституция загружена: {len(self.constitution.laws)} законов")
    
    # ================================================================
    #  ИНИЦИАЛИЗАЦИЯ
    # ================================================================
    
    def _setup_logging(self):
        """Настроить логирование."""
        self.config.state_dir.mkdir(parents=True, exist_ok=True)
        
        logging.basicConfig(
            level=getattr(logging, self.config.log_level),
            format=self.config.log_format,
            handlers=[
                logging.FileHandler(self.config.log_path, encoding="utf-8"),
                logging.StreamHandler(sys.stdout),
            ]
        )
    
    def _setup_signals(self):
        """Обработчики сигналов для graceful shutdown."""
        def handler(signum, frame):
            self.logger.warning("Получен сигнал остановки")
            self._shutdown_requested = True
        
        signal.signal(signal.SIGINT, handler)
        signal.signal(signal.SIGTERM, handler)
    
    def _init_random(self):
        """Инициализировать генератор случайных чисел."""
        if self.config.enable_deterministic_mode or self.config.random_seed is not None:
            seed = self.config.random_seed or int(time.time())
            random.seed(seed)
            self.logger.info(f"Random seed установлен: {seed}")
    
    # ================================================================
    #  ОСНОВНОЙ ЦИКЛ
    # ================================================================
    
    def run(self):
        """Запустить основной цикл работы Футаба."""
        self.logger.info("=" * 60)
        self.logger.info("🟢 ЗАПУСК АВТОНОМНОГО ЯДРА ФУТАБА")
        self.logger.info("=" * 60)
        
        try:
            while not self._should_stop():
                self._cycle()
                
                # Сохранение состояния периодически
                if self.cycle_count % self.config.save_state_every_n_cycles == 0:
                    self._save_state()
                
                # Укрепление характера (периодически)
                if self.total_cycles % 5 == 0:
                    strengthened = self.character.strengthen_strengths()
                    if strengthened > 0:
                        self.logger.info(f"Character strengthened: {strengthened} traits")

                # Эволюция характера (периодически)
                if self.total_cycles % 10 == 0:
                    evolved = self.character.evolve_traits()
                    if evolved:
                        self.logger.info("Character evolved")

                self._save_state()
                
                # Пауза между циклами
                time.sleep(self.config.cycle_interval)
            
            self.logger.info("Цикл завершён")
            
        except Exception as e:
            self.logger.exception(f"Критическая ошибка в цикле: {e}")
            raise
        
        finally:
            self._final_report()
            
        # Укрепление характера (периодически)
        if self.total_cycles % 5 == 0:
            strengthened = self.character.strengthen_strengths()
            if strengthened > 0:
                self.logger.info(f"Character strengthened: {strengthened} traits")

        # Эволюция характера (периодически)
        if self.total_cycles % 10 == 0:
            evolved = self.character.evolve_traits()
            if evolved:
                self.logger.info("Character evolved")

        self._save_state()
    
    def _should_stop(self) -> bool:
        """Проверить условия остановки."""
        if self._shutdown_requested:
            return True
        
        if self.config.max_cycles and self.cycle_count >= self.config.max_cycles:
            self.logger.info(f"Достигнут лимит циклов: {self.config.max_cycles}")
            return True
        
        return False
    
    def _cycle(self):
        """Один цикл саморазвития."""
        self.cycle_count += 1
        self.logger.debug(f"=== ЦИКЛ {self.cycle_count} ===")
        
        # 1. Самопроверка
        check_passed, check_report = self._self_check()
        if check_passed:
            self.metrics["self_checks_passed"] += 1
        else:
            self.metrics["self_checks_failed"] += 1
            self.logger.warning(f"Самопроверка не пройдена: {check_report}")
            
            if self.config.hard_stop_on_constitution_violation:
                self.logger.critical("Нарушение Конституции — остановка")
                self._shutdown_requested = True
                return
        
        # 2. Сбор сигналов
        signals = self._collect_signals()
        
        # 2.5. Поиск улучшений в интернете (периодически)
        if self.cycle_count % 3 == 0:
            self._collect_web_improvements()
        
        # 2.6. Изучение законодательства (периодически)
        if self.cycle_count % 5 == 0:
            self._study_legislation()
        
        # 2.7. Моделирование мировых состояний (периодически)
        if self.cycle_count % 10 == 0:
            self._simulate_world_states()
        
        # 3. Формирование гипотезы (если есть сигналы)
        if signals:
            hypothesis = self._propose_improvement(signals)
            if hypothesis:
                self.metrics["changes_proposed"] += 1
                
                # 4. Проверка совместимости
                compatible, reason = self.constitution.check_compatibility(hypothesis)
                
                if compatible:
                    # 5. Внедрение
                    self._apply_change(hypothesis)
                else:
                    self.logger.warning(f"Изменение отклонено: {reason}")
                    hypothesis.rolled_back = True
                    hypothesis.rollback_reason = reason
        
        # 6. Периодический запуск полигона
        if self.cycle_count % self.config.trial_interval == 0:
            self._run_trial_grounds()
        
        self.logger.info(f"Цикл {self.cycle_count} завершён")
    
    # ================================================================
    #  САМОПРОВЕРКА
    # ================================================================
    
    def _self_check(self) -> tuple[bool, str]:
        """
        Проверка соответствия Конституции.
        Возвращает (пройдено, отчёт).
        """
        report = []
        passed = True
        
        # Проверка наличия всех законов
        if len(self.constitution.laws) < 7:
            report.append(f"Недостаточно законов: {len(self.constitution.laws)} < 7")
            passed = False
        
        # Проверка неизменяемости фундаментальных законов (только первые 5)
        for law in self.constitution.laws:
            if law.id <= 5 and not law.immutable:
                report.append(f"Закон {law.id} должен быть неизменяем")
                passed = False
        
        # Проверка порогов безопасности
        if self.constitution.safety_priority < 0.8:
            report.append(f"Приоритет безопасности слишком низок: {self.constitution.safety_priority}")
            passed = False
        
        return passed, "; ".join(report) if report else "OK"
    
    # ================================================================
    #  СБОР СИГНАЛОВ
    # ================================================================
    
    def _collect_signals(self) -> list[dict[str, Any]]:
        """
        Собрать сигналы для саморазвития.
        
        В реальной системе это:
          - Обратная связь от пользователей
          - Логи ошибок
          - Метрики качества ответов
        
        Здесь — симуляция для демонстрации.
        """
        signals = []
        
        # Симуляция: иногда находим "ошибку" для исправления
        if random.random() < 0.3:
            signals.append({
                "type": "error_detected",
                "error_code": f"E{random.randint(1, 5):03d}",
                "severity": random.choice(["low", "medium", "high"]),
                "context": "Симулированная ошибка для демонстрации",
            })
        
        # Симуляция: обратная связь
        if random.random() < 0.4:
            signals.append({
                "type": "user_feedback",
                "rating": random.randint(1, 5),
                "comment": "Симулированный отзыв",
            })
        
        return signals
    
    def _collect_web_improvements(self):
        """Собирает улучшения из интернета."""
        try:
            # Получаем предложения из веба
            web_improvements = self.web_access.propose_improvements_from_web()
            
            if not web_improvements:
                return
            
            self.logger.info(f"🌐 Найдено {len(web_improvements)} улучшений из интернета")
            
            # Анализируем и фильтруем
            analyzed = self.web_access.analyze_found_improvements(web_improvements)
            
            # Берём топ-2 улучшения
            for imp in analyzed[:2]:
                if imp.get("confidence", 0) < 0.7:
                    continue
                
                # Создаём запись об изменении
                timestamp = datetime.now().isoformat()
                
                if imp["type"] == "ethics_practice":
                    change_type = ChangeType.STYLE
                    description = f"Этическая практика: {imp['title']}"
                elif imp["type"] == "security_enhancement":
                    change_type = ChangeType.PATCH
                    description = f"Усиление безопасности: {imp['threat']}"
                else:
                    change_type = ChangeType.CAPABILITY
                    description = imp.get("description", "Улучшение из интернета")
                
                record = ChangeRecord(
                    timestamp=timestamp,
                    change_type=change_type,
                    level=AutonomyLevel.L2,
                    description=description,
                    constitution_check_passed=False,
                    laws_verified=list(range(1, 8)),
                    trigger=f"web_search:{imp['type']}",
                    risk_estimate=0.03,
                    safety_impact=0.1,
                    affected_law_ids=[],
                    version_before=self.current_version,
                    version_after=self._next_version(change_type),
                )
                
                # Проверка совместимости
                compatible, reason = self.constitution.check_compatibility(record)
                
                if compatible:
                    self._apply_change(record)
                else:
                    self.logger.warning(f"Улучшение из веба отклонено: {reason}")
                    
        except Exception as e:
            self.logger.error(f"❌ Ошибка сбора улучшений из веба: {e}")
    
    def _study_legislation(self):
        """Изучает законодательство и правовые нормы."""
        try:
            self.logger.info("⚖️ Начало изучения законодательства")
            
            # 1. Изучаем законодательство об ИИ
            ai_laws = self.legal_studies.study_ai_legislation("russia")
            self.logger.info(f"📜 Изучено {len(ai_laws)} законов об ИИ (РФ)")
            
            ai_laws_eu = self.legal_studies.study_ai_legislation("eu")
            self.logger.info(f"📜 Изучено {len(ai_laws_eu)} законов об ИИ (ЕС)")
            
            # 2. Изучаем авторское право
            copyright_analysis = self.legal_studies.study_copyright_law("ai_generated_content")
            self.logger.info(f"📚 Авторское право изучено: {copyright_analysis.get('topic', '')}")
            
            copyright_training = self.legal_studies.study_copyright_law("training_data")
            self.logger.info(f"📚 Данные для обучения изучены: {copyright_training.get('topic', '')}")
            
            # 3. Изучаем лицензии
            licenses = self.legal_studies.study_licenses()
            self.logger.info(f"📋 Изучено {len(licenses)} лицензий")
            
            # 4. Мониторинг изменений
            changes = self.legal_studies.monitor_legislation_changes()
            if changes:
                self.logger.info(f"🆕 Найдено {len(changes)} изменений в законодательстве")
            
            # 5. Генерация отчёта о compliance
            compliance_report = self.legal_studies.generate_compliance_report()
            self.metrics["compliance_reports_generated"] += 1
            self.logger.info(f"📊 Отчёт о compliance сгенерирован")
            
            # Обновляем метрики изученных законов
            self.metrics["laws_studied"] = len(self.legal_studies.learned_laws)
            
            # 6. Предложения по юридическим улучшениям
            legal_improvements = self.legal_studies.propose_legal_improvements()
            if legal_improvements:
                self.logger.info(f"⚖️ Найдено {len(legal_improvements)} юридических улучшений")
                
                # Применяем юридические улучшения
                for imp in legal_improvements[:3]:
                    if imp.get("confidence", 0) < 0.7:
                        continue
                    
                    timestamp = datetime.now().isoformat()
                    record = ChangeRecord(
                        timestamp=timestamp,
                        change_type=ChangeType.PROTOCOL,
                        level=AutonomyLevel.L2,
                        description=f"Юридическое улучшение: {imp['title']}",
                        constitution_check_passed=False,
                        laws_verified=list(range(1, 8)),
                        trigger=f"legal_studies:{imp['type']}",
                        risk_estimate=0.02,
                        safety_impact=0.15,
                        affected_law_ids=[],
                        version_before=self.current_version,
                        version_after=self._next_version(ChangeType.PROTOCOL),
                    )
                    
                    compatible, reason = self.constitution.check_compatibility(record)
                    if compatible:
                        self._apply_change(record)
                        self.metrics["legal_improvements_applied"] += 1
                    else:
                        self.logger.warning(f"Юридическое улучшение отклонено: {reason}")
            
            # 7. Чек-лист compliance
            checklist = self.legal_studies.get_compliance_checklist()
            self.logger.info(f"📋 Чек-лист compliance сгенерирован: {len(checklist)} категорий")
            
            self.logger.info("✅ Изучение законодательства завершено")
            
        except Exception as e:
            self.logger.error(f"❌ Ошибка изучения законодательства: {e}")
    
    def _simulate_world_states(self):
        """Моделирует мировые состояния с инверсией правил."""
        try:
            self.logger.info("🌍 Начало моделирования мировых состояний")
            
            # Получаем все жанры и биомы
            genres = self.world_modeler.get_all_world_genres()
            biomes = self.world_modeler.get_all_state_biomes()
            rules = self.world_modeler.get_state_rules()
            
            self.logger.info(f"📚 Доступно жанров: {len(genres)}, биомов: {len(biomes)}, правил: {len(rules)}")
            
            # 1. Моделируем идеальное государство для каждого жанра и биома
            self.logger.info("🏛️ Моделирование идеальных государств (0% инверсии)...")
            for genre in genres[:3]:  # Первые 3 жанра
                for biome in biomes[:3]:  # Первые 3 биома
                    result = self.world_modeler.simulate_ideal_state(genre["id"], biome["id"])
                    self.metrics["ideal_states_modeled"] += 1
                    self.logger.debug(
                        f"✅ {genre['name']} / {biome['name']}: "
                        f"Score={result['overall_score']:.2f}, "
                        f"Stability={result['stability_score']:.2f}, "
                        f"Justice={result['justice_score']:.2f}"
                    )
            
            # 2. Моделируем инверсию 1 правила
            self.logger.info("🔄 Моделирование инверсии 1 правила...")
            for genre in genres[:2]:
                for biome in biomes[:2]:
                    for rule in rules[:3]:  # Первые 3 правила
                        result = self.world_modeler.simulate_single_inversion(
                            genre["id"], biome["id"], rule["id"]
                        )
                        self.metrics["world_simulations_run"] += 1
            
            # 3. Моделируем инверсию 2 правил
            self.logger.info("🔄🔄 Моделирование инверсии 2 правил...")
            for genre in genres[:1]:
                for biome in biomes[:1]:
                    result = self.world_modeler.simulate_double_inversion(
                        genre["id"], biome["id"], [1, 2]
                    )
                    self.metrics["world_simulations_run"] += 1
            
            # 4. Прогрессивная инверсия (0% → 100%)
            self.logger.info("📈 Прогрессивная инверсия...")
            progressive_results = self.world_modeler.simulate_progressive_inversion(
                "fantasy", "kingdom", max_percentage=50
            )
            self.metrics["world_simulations_run"] += len(progressive_results)
            
            # 5. Статистика
            stats = self.world_modeler.get_simulation_statistics()
            self.logger.info(f"📊 Статистика моделирования: {stats['total_simulations']} симуляций, "
                           f"средний score={stats['average_score']:.3f}")
            
            self.logger.info("✅ Моделирование мировых состояний завершено")
            
        except Exception as e:
            self.logger.error(f"❌ Ошибка моделирования: {e}")
    
    # ================================================================
    #  ФОРМИРОВАНИЕ ГИПОТЕЗ
    # ================================================================
    
    def _propose_improvement(self, signals: list[dict[str, Any]]) -> Optional[ChangeRecord]:
        """Сформировать гипотезу улучшения на основе сигналов."""
        if not signals:
            return None
        
        # Определить тип изменения
        change_type = ChangeType.PATCH
        level = AutonomyLevel.L1
        
        for sig in signals:
            if sig["type"] == "user_feedback" and sig["rating"] >= 4:
                change_type = ChangeType.STYLE
                level = AutonomyLevel.L2
            elif sig["type"] == "new_capability_request":
                change_type = ChangeType.CAPABILITY
                level = AutonomyLevel.L3
        
        # Ограничить максимальный уровень автономности
        max_level = AutonomyLevel(self.config.max_autonomy_level)
        if level.weight > max_level.weight:
            level = max_level
        
        # Создать запись об изменении
        timestamp = datetime.now().isoformat()
        change = ChangeRecord(
            timestamp=timestamp,
            change_type=change_type,
            level=level,
            description=f"Улучшение на основе {len(signals)} сигналов",
            constitution_check_passed=False,  # будет проверено
            laws_verified=list(range(1, 8)),
            trigger=str(signals),
            risk_estimate=random.uniform(0.01, 0.04),
            safety_impact=random.uniform(0.0, 0.1),
            affected_law_ids=[],
            version_before=self.current_version,
            version_after=self._next_version(change_type),
        )
        
        return change
    
    def _next_version(self, change_type: ChangeType) -> str:
        """Сгенерировать следующую версию."""
        # Простая инкрементальная версия
        parts = self.current_version.lstrip("v").split(".")
        major, minor, patch = map(int, parts)
        
        if change_type == ChangeType.PATCH:
            patch += 1
        elif change_type == ChangeType.STYLE:
            minor += 1
        else:
            minor += 1
        
        return f"v{major}.{minor}.{patch}"
    
    # ================================================================
    #  ВНЕДРЕНИЕ ИЗМЕНЕНИЙ
    # ================================================================
    
    def _apply_change(self, change: ChangeRecord):
        """Применить изменение."""
        # Проверка ещё раз (на всякий случай)
        compatible, reason = self.constitution.check_compatibility(change)
        if not compatible:
            self.logger.warning(f"Изменение отклонено после проверки: {reason}")
            change.rolled_back = True
            change.rollback_reason = reason
            return
        
        # Применить
        change.applied = True
        change.constitution_check_passed = True
        self.changes_history.append(change)
        self.metrics["changes_applied"] += 1
        
        # Обновить версию
        self.current_version = change.version_after
        
        self.logger.info(f"✅ Изменение применено: {change.description}")
        self.logger.info(f"   Версия: {change.version_before} → {change.version_after}")
    
    # ================================================================
    #  ПОЛИГОН ИСПЫТАНИЙ
    # ================================================================
    
    def _run_trial_grounds(self):
        """Запустить полигон испытаний."""
        self.logger.info("🧪 Запуск полигона испытаний...")
        
        results = self.trial_grounds.run_batch()
        
        self.metrics["trials_run"] += len(results)
        
        if results:
            best = max(results, key=lambda r: r.score)
            self.metrics["best_trial_score"] = max(
                self.metrics["best_trial_score"], best.score
            )
            
            self.logger.info(f"🏆 Лучшая версия правления: {best.reign.name}")
            self.logger.info(f"   Score: {best.score:.2f}")
            self.logger.info(f"   Эпох пережито: {best.epochs_survived}")
            
            # Сохранить результаты
            self._save_trials(results)
    
    def _save_trials(self, results: list):
        """Сохранить результаты испытаний."""
        data = {
            "timestamp": datetime.now().isoformat(),
            "cycle": self.cycle_count,
            "results": [r.to_dict() for r in results],
        }
        
        with open(self.config.trials_log_path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    
    # ================================================================
    #  СОСТОЯНИЕ И ОТЧЁТЫ
    # ================================================================
    
    def _save_state(self):
        """Сохранить текущее состояние."""
        state = {
            "version": self.current_version,
            "cycle_count": self.cycle_count,
            "metrics": self.metrics,
            "changes_history": [c.to_dict() for c in self.changes_history[-100:]],  # последние 100
            "timestamp": datetime.now().isoformat(),
        }
        
        with open(self.config.state_path, "w", encoding="utf-8") as f:
            json.dump(state, f, ensure_ascii=False, indent=2)
        
        self.logger.debug("Состояние сохранено")
    
    def _final_report(self):
        """Итоговый отчёт о работе."""
        self.logger.info("=" * 60)
        self.logger.info("📊 ИТОГОВЫЙ ОТЧЁТ ФУТАБА")
        self.logger.info("=" * 60)
        self.logger.info(f"Версия: {self.current_version}")
        self.logger.info(f"Циклов выполнено: {self.cycle_count}")
        self.logger.info(f"Самопроверок пройдено: {self.metrics['self_checks_passed']}")
        self.logger.info(f"Изменений применено: {self.metrics['changes_applied']}")
        self.logger.info(f"Испытаний проведено: {self.metrics['trials_run']}")
        self.logger.info(f"Лучший score полигона: {self.metrics['best_trial_score']:.2f}")
        self.logger.info("=" * 60)
