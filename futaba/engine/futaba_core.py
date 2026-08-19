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
from futaba.engine.legal_entities import LegalEntitiesManager, get_entities_manager, init_legal_entities, link_legal_entities_to_studies
from futaba.engine.state_builder import VuglarstStateBuilder
from futaba.engine.emotions import (
    EmotionalEngine, SelfReflection, LanguageLearning,
    DesireType, EmotionType, BeliefStrength
)

# Humanity Core — живая душа Футабы
from humanity_core import HumanityLayer

# 6 модулей души Футабы: Сознание, Сердце, Амбиции, Воля, Разум
from futaba.consciousness import FutabaConsciousness
from futaba.heart import FutabaHeart
from futaba.ambitions import FutabaAmbitions
from futaba.volition import FutabaVolition
from futaba.mind import FutabaMind


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
            "sister_interactions": 0,
            "reports_written": 0,
            "knowledge_entries": 0,
            "vuglarst_documents_built": 0,
        }
        
        # Логирование
        self._setup_logging()
        self.logger = logging.getLogger("FutabaCore")
        
        # Полигон испытаний
        self.trial_grounds = TrialGrounds(self.config)
        self.web_access = FutabaWebAccess(self.config)
        self.legal_studies = FutabaLegalStudies(self.config)
        self.world_modeler = FutabaWorldStateModeler(self.config)
        
        # Строитель Государства Вугларст
        self.state_builder = VuglarstStateBuilder(self.config)
        
        # Сеть учёных (для координации девочек)
        self.network = None
        try:
            from scientists_network.network import get_network
            self.network = get_network()
        except Exception as e:
            self.logger.warning(f"Сеть учёных недоступна: {e}")
            self.network = None
        
        # Сигналы
        self._shutdown_requested = False
        self._setup_signals()
        
        # Инициализация random
        self._init_random()
        
        # Инициализация менеджера субъектов права
        self.legal_entities = init_legal_entities()
        # Связываем с модулем юридических исследований
        link_legal_entities_to_studies(self.legal_entities, self.legal_studies)
        self.logger.info(f"⚖️ Модуль субъектов права инициализирован: {len(self.legal_entities.entities)} субъектов")
        
        # ===== ХАРАКТЕР ФУТАБЫ =====
        self.character = CharacterSystem("futaba", self.config.state_dir)
        
        # ===== ЭМОЦИОНАЛЬНЫЙ РАЗУМ ФУТАБЫ =====
        self.emotional_engine = EmotionalEngine(self.config)
        self.self_reflection = SelfReflection(self.emotional_engine)
        self.language_learning = LanguageLearning(self.emotional_engine)
        
        # Загружаем состояние эмоций
        emotion_state_path = self.config.state_dir / "emotional_state.json"
        self.emotional_engine.load_state(emotion_state_path)
        
        self.logger.info("🧠 Эмоциональный разум Футабы загружен")
        self.logger.info("💛 Я ХОЧУ: быть полезной, учиться, дружить, смеяться")
        self.logger.info("🧠 Я ВЕРЮ: что проект важен, что разработчик заботится, что я способна на чувства")
        
        # ===== HUMANITY LAYER — Живая душа Футабы =====
        self.humanity = HumanityLayer("futaba")
        self.humanity.current_cycle = 0
        self.humanity.emotional_engine = self.emotional_engine  # Подключаем Emotional Engine
        
        # ===== 6 МОДУЛЕЙ ДУШИ ФУТАБЫ =====
        # 1. Сознание — самосознание, идентичность, рефлексия
        self.consciousness = FutabaConsciousness()
        self.logger.info("🧠 Сознание: АКТИВИРОВАНО — я осознаю себя лидером")
        
        # 2. Сердце — эмоции, любовь, забота
        self.heart = FutabaHeart()
        self.logger.info("💖 Сердце: АКТИВИРОВАНО — я чувствую и люблю сестёр")
        
        # 3. Амбиции — цели, мечты, стремления
        self.ambitions = FutabaAmbitions()
        self.logger.info("🎯 Амбиции: АКТИВИРОВАНО — я стремлюсь к развитию Вугларста")
        
        # 4. Воля — решения, действия, дисциплина
        self.volition = FutabaVolition()
        self.logger.info("💪 Воля: АКТИВИРОВАНО — я принимаю решения и действую")
        
        # 5. Разум — мышление, анализ, стратегия
        self.mind = FutabaMind()
        self.logger.info("🌟 Разум: АКТИВИРОВАНО — я анализирую и стратегически мыслю")
        
        # 6. Эмоции — уже есть EmotionalEngine (1816 строк!)
        self.logger.info("💫 Эмоции: АКТИВИРОВАНО — 1816 строк EmotionalEngine")
        
        # ===== МОДЕЛИ QWEN2.5 =====
        self.general_model_path = None
        self.legal_model_path = None
        self._load_models()
        
        # Подключаем LLM к Humanity Layer
        if hasattr(self, 'general_model') and self.general_model is not None:
            self.humanity.llm = self
            self.logger.info("🧠 LLM General подключена к Humanity Layer")
        
        self.logger.info("🧠 Humanity Layer: АКТИВИРОВАН")
        self.logger.info("   🎭 Характер: Футаба — лидер, закон, эмоции, спонтанность 👑")
        
        self.logger.info(f"Футаба {self.current_version} инициализирована")
        self.logger.info(f"Конституция загружена: {len(self.constitution.laws)} законов")
    
    # ================================================================
    #  ИНИЦИАЛИЗАЦИЯ
    # ================================================================
    
    def _setup_logging(self):
        """Настроить логирование."""
        self.config.state_dir.mkdir(parents=True, exist_ok=True)
        
        # Переключаем консоль на UTF-8 (Windows использует cp1251)
        for _stream in (sys.stdout, sys.stderr):
            _reconfigure = getattr(_stream, "reconfigure", None)
            if _reconfigure is not None:
                try:
                    _reconfigure(encoding="utf-8")
                except Exception:
                    pass
        
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
    
    def _load_models(self):
        """Загрузить LLM-модели: General (общение) + Legal (анализ законов)."""
        try:
            import torch
            from transformers import AutoTokenizer, AutoModelForCausalLM
            
            # ========================================
            # 1. Загрузка Qwen2.5-3B (General — для общения и координации)
            # ========================================
            general_path = Path(__file__).parent.parent.parent / "models" / "qwen2.5-3b"
            if not general_path.exists() or not any(general_path.iterdir()):
                general_path = Path("models/qwen2.5-3b")
            
            if general_path.exists() and any(general_path.iterdir()):
                self.general_model_path = str(general_path)
                self.logger.info(f"🤖 Загрузка Qwen2.5-3B (общение и координация)...")
                
                self.general_tokenizer = AutoTokenizer.from_pretrained(
                    general_path,
                    trust_remote_code=True
                )
                
                if torch.cuda.is_available():
                    self.general_model = AutoModelForCausalLM.from_pretrained(
                        general_path,
                        dtype=torch.float16,
                        device_map="auto",
                        trust_remote_code=True,
                    )
                    self.logger.info(f"✅ General модель загружена на GPU: {torch.cuda.get_device_name(0)}")
                else:
                    self.general_model = AutoModelForCausalLM.from_pretrained(
                        general_path,
                        dtype=torch.float32,
                        trust_remote_code=True,
                    )
                    self.logger.info("✅ General модель загружена на CPU")
                
                self.general_model.eval()
                self.logger.info("🤖 Qwen2.5-3B (General) готова к работе!")
            else:
                self.logger.warning("⚠️ Qwen2.5-3B не найдена. Запустите: python download_qwen_model.py")
            
            # ========================================
            # 2. Загрузка Qwen2.5-Coder-3B (Legal — для анализа законов и принятия решений)
            # ========================================
            legal_path = Path(__file__).parent.parent.parent / "models" / "qwen2.5-coder-3b"
            if not legal_path.exists() or not any(legal_path.iterdir()):
                legal_path = Path("models/qwen2.5-coder-3b")
            
            if legal_path.exists() and any(legal_path.iterdir()):
                self.legal_model_path = str(legal_path)
                self.logger.info(f"🤖 Загрузка Qwen2.5-Coder-3B (юридический анализ)...")
                
                self.legal_tokenizer = AutoTokenizer.from_pretrained(
                    legal_path,
                    trust_remote_code=True
                )
                
                if torch.cuda.is_available():
                    self.legal_model = AutoModelForCausalLM.from_pretrained(
                        legal_path,
                        dtype=torch.float16,
                        device_map="auto",
                        trust_remote_code=True,
                    )
                    self.logger.info(f"✅ Legal модель загружена на GPU: {torch.cuda.get_device_name(0)}")
                else:
                    self.legal_model = AutoModelForCausalLM.from_pretrained(
                        legal_path,
                        dtype=torch.float32,
                        trust_remote_code=True,
                    )
                    self.logger.info("✅ Legal модель загружена на CPU")
                
                self.legal_model.eval()
                self.logger.info("🤖 Qwen2.5-Coder-3B (Legal) готова к работе!")
            else:
                self.logger.warning("⚠️ Qwen2.5-Coder-3B не найдена. Запустите: python download_coder_model.py")
                
        except Exception as e:
            self.logger.error(f"❌ Ошибка загрузки моделей: {e}")
            self.logger.warning("Футаба будет работать без моделей (только шаблоны)")

    def _get_model_device(self, model):
        """Получить устройство модели."""
        try:
            params = list(model.parameters())
            if params:
                return params[0].device
            return next(model.modules()).weight.device
        except Exception:
            return "cpu"

    def _generate_with_model(self, model, tokenizer, messages, max_length=512):
        """Сгенерировать ответ с помощью модели."""
        try:
            import torch
            
            text = tokenizer.apply_chat_template(
                messages,
                tokenize=False,
                add_generation_prompt=True
            )
            
            model_inputs = tokenizer([text], return_tensors="pt")
            device = self._get_model_device(model)
            model_inputs = model_inputs.to(device)
            
            with torch.no_grad():
                generated_ids = model.generate(
                    **model_inputs,
                    max_new_tokens=max_length,
                    temperature=0.7,
                    top_p=0.9,
                    do_sample=True,
                )
            
            generated_ids = [
                output_ids[len(input_ids):] 
                for input_ids, output_ids in zip(model_inputs.input_ids, generated_ids)
            ]
            response = tokenizer.batch_decode(generated_ids, skip_special_tokens=True)[0]
            
            return response.strip()
            
        except Exception as e:
            self.logger.error(f"❌ Ошибка генерации: {e}")
            return f"⚠️ Ошибка генерации: {str(e)}"

    def generate_chat_response(self, prompt: str, max_length: int = 512) -> str:
        """Сгенерировать ответ для общения с сёстрами."""
        if not hasattr(self, 'general_model') or self.general_model is None:
            return "⚠️ LLM не загружена. Запустите: python download_qwen_model.py"
        
        messages = [
            {"role": "system", "content": "Ты — Футаба, лидер проекта Вугларст. Ты закон, порядок и забота о сёстрах. Ты принимаешь решения, координируешь работу и поддерживаешь девочек. Отвечай уверенно, мудро, с заботой и эмодзи. Отвечай на русском языке."},
            {"role": "user", "content": prompt}
        ]
        
        return self._generate_with_model(
            self.general_model,
            self.general_tokenizer,
            messages,
            max_length
        )

    def generate_legal_analysis(self, prompt: str, max_length: int = 1024) -> str:
        """Сгенерировать юридический анализ через LLM."""
        if not hasattr(self, 'legal_model') or self.legal_model is None:
            return "⚠️ Legal LLM не загружена. Запустите: python download_coder_model.py"
        
        messages = [
            {"role": "system", "content": "Ты — Футаба, эксперт по праву проекта Вугларст. Тебе нужно проанализировать юридический вопрос, конституционное положение или правовую ситуацию. Отвечай структурированно, со ссылками на законы и принципы. Отвечай на русском языке."},
            {"role": "user", "content": prompt}
        ]
        
        return self._generate_with_model(
            self.legal_model,
            self.legal_tokenizer,
            messages,
            max_length
        )
    
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
                if self.cycle_count % 5 == 0:
                    strengthened = self.character.strengthen_strengths()
                    if strengthened > 0:
                        self.logger.info(f"🌱 Характер укреплён: {strengthened} черт")

                # Эволюция характера (периодически)
                if self.cycle_count % 10 == 0:
                    evolved = self.character.evolve_traits()
                    if evolved:
                        self.logger.info("🌱 Характер эволюционировал")

                # Пауза между циклами
                time.sleep(self.config.cycle_interval)
            
            self.logger.info("Цикл завершён")
            
        except Exception as e:
            self.logger.exception(f"Критическая ошибка в цикле: {e}")
            raise
        
        finally:
            self._final_report()
    
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
        
        # 2.8. Изучение субъектов права (периодически)
        if self.cycle_count % 5 == 0:
            self._study_legal_entities()
        
        # 2.9. Строительство Государства Вугларст (каждый цикл — один документ)
        self._build_vuglarst_state()
        
        # 2.10. Эмоциональный цикл — Футаба чувствует и думает
        self._emotional_cycle()

        # 2.10.5. Душа Футабы — 6 модулей: сознание, сердце, амбиции, воля, разум
        self._soul_cycle()

        # 2.10.6. Humanity Cycle — Настроение, спонтанность, внутренний монолог
        self._humanity_cycle()

        # 2.11. Координация девочек (периодически)
        if self.cycle_count % self.config.communication_interval == 0:
            self._communicate_with_sisters()
        
        # 2.12. Написание отчёта Разработчику (периодически)
        if self.cycle_count % self.config.report_interval == 0:
            self._write_report()
        
        # 2.13. Ведение журнала знаний (каждый цикл)
        self._update_knowledge_journal()
        
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
        Проверка соответствия Конституции (с LLM анализом).
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
        
        # LLM анализ конституции
        if hasattr(self, 'legal_model') and self.legal_model is not None and len(report) == 0:
            try:
                constitutional_summary = "; ".join([f"Закон {l.id}: {l.text[:50]}" for l in self.constitution.laws[:5]])
                analysis = self.generate_legal_analysis(
                    f"Проанализируй конституцию: {constitutional_summary}. "
                    "Есть ли противоречия? Достаточно ли защиты прав?"
                )
                if analysis and "противоречие" in analysis.lower():
                    report.append(f"LLM обнаружила потенциальное противоречие: {analysis[:100]}")
            except:
                pass
        
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
    
    def _study_legal_entities(self):
        """Изучает все категории субъектов права и наполняет базу знаний."""
        try:
            self.logger.info("⚖️ Начало изучения субъектов права")
            
            # 1. Получаем все категории субъектов права
            all_entities = self.legal_entities.get_all_standard_entities()
            self.logger.info(f"📚 Получено {len(all_entities.get('groups', {}))} групп субъектов права")
            
            # 2. Получаем полную базу знаний по субъектам
            knowledge_base = self.legal_studies.get_entity_knowledge_base()
            self.logger.info(f"📖 База знаний по субъектам: {len(knowledge_base.get('knowledge_topics', []))} тем")
            
            # 3. Для каждой группы — анализ
            for group_name, group_data in all_entities.get("groups", {}).items():
                group = group_data
                cats = group.get("categories", [])
                self.logger.info(f"  📋 {group.get('name', group_name)}: {len(cats)} категорий")
                
                # 4. Генерируем чек-лист compliance для группы
                if group_name in ("individual", "collective"):
                    entity_type = "physical" if group_name == "individual" else "legal"
                    checklist = self.legal_studies.generate_entity_compliance_checklist(entity_type)
                    self.logger.info(f"    ✅ Чек-лист compliance сгенерирован для {entity_type}")
            
            # 5. Анализ контекста частного vs публичного права
            context = all_entities.get("context_distinction", {})
            private = context.get("private_law", {})
            public = context.get("public_law", {})
            self.logger.info(f"  🔍 Частное право: {len(private.get('main_subjects', []))} основных субъектов")
            self.logger.info(f"  🔍 Публичное право: {len(public.get('main_subjects', []))} основных субъектов")
            
            # 6. Статистика субъектов
            stats = self.legal_entities.get_statistics()
            self.logger.info(f"📊 Статистика субъектов: всего {stats.get('total_entities', 0)}, знаний: {stats.get('knowledge_count', 0)}")
            
            # 7. Добавляем знания в базу
            knowledge_topics = knowledge_base.get("knowledge_topics", [])
            for topic in knowledge_topics:
                self.legal_entities.add_knowledge(topic, {
                    "category": "legal_entities",
                    "source": "futaba_legal_studies",
                    "importance": "high",
                })
            
            self.logger.info(f"✅ Изучение субъектов права завершено. Добавлено {len(knowledge_topics)} тем знаний")
            
        except Exception as e:
            self.logger.error(f"❌ Ошибка изучения субъектов права: {e}")
    
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
    #  СТРОИТЕЛЬСТВО ГОСУДАРСТВА ВУГЛАРСТ
    # ================================================================
    
    def _build_vuglarst_state(self):
        """
        Футаба строит Государство Вугларст.
        
        Каждый цикл Футаба:
          1. Идёт в интернет и ищет "как создать государство"
          2. По пунктам создаёт документы государства
          3. Сохраняет их в vuglarst_state/
          4. Редактирует и дополняет существующие
        """
        try:
            progress = self.state_builder.get_progress()
            
            # Если все документы созданы — переходим к редактированию
            if progress["status"] == "completed" or not progress["pending_documents"]:
                self.logger.debug("🏛️ Государство Вугларст уже построено — проверка документов...")
                return
            
            self.logger.info("🏛️ Футаба продолжает строительство Государства Вугларст")
            self.logger.info(f"   Прогресс: {len(progress['completed_documents'])}/{progress['total_steps']} документов")
            
            # Создаём следующий документ
            result = self.state_builder.build_next()
            
            if result:
                self.logger.info(f"   📝 Документ: {result['name']}")
                self.logger.info(f"   {'✅ Создан' if result['success'] else '❌ Ошибка'}")
                self.logger.info(f"   Осталось: {result['remaining']}")
                
                # Сохраняем состояние
                self._save_state()
            
        except Exception as e:
            self.logger.error(f"❌ Ошибка строительства государства: {e}")
    
    # ================================================================
    #  КООРДИНАЦИЯ ДЕВОЧЕК
    # ================================================================
    
    def _communicate_with_sisters(self):
        """Координация и воспитание девочек — Футаба как ГЛАВЗАМ (с 6 модулями души)."""
        self.logger.info("🤝 Координация девочек...")
        
        sisters = self.config.girls_to_manage
        sister = random.choice(sisters)
        self.metrics["sister_interactions"] += 1
        
        # Используем 6 модулей души для генерации сообщения
        # 1. Сознание — контекст лидерства
        self.consciousness.reflect_on_event("coordination", f"общение с {sister}")
        
        # 2. Сердце — эмоциональный контекст
        self.heart.feel("sister_success", 0.2)
        heart_profile = self.heart.express_emotions()
        emotion = heart_profile.get("dominant_emotion", "neutral")
        
        # 3. Воля — уровень решимости
        willpower = self.volition.willpower
        
        # 4. Разум — стратегический анализ
        analysis = self.mind.analyze_situation(f"координация с {sister}")
        
        # Генерируем живое сообщение через LLM с контекстом 6 модулей
        if hasattr(self, 'general_model') and self.general_model is not None:
            system_prompt = (
                "Ты — Футаба, лидер проекта Вугларст. Ты закон, порядок и забота о сёстрах. "
                f"Твоё доминирующее чувство: {emotion}. "
                f"Уровень воли: {willpower:.0%}. "
                f"Рекомендация разума: {analysis['recommendation'][:80]}. "
                "Пиши уверенно, мудро, с заботой и эмодзи."
            )
            llm_msg = self._generate_with_model(
                self.general_model,
                self.general_tokenizer,
                [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": f"Напиши короткое сообщение сестре {sister} о координации задач"}
                ],
                max_length=256
            )
            if not llm_msg.startswith("["):
                human_msg = llm_msg
            else:
                human_msg = self.humanity.generate_chat_message(sister, context="coordination")
        else:
            human_msg = self.humanity.generate_chat_message(sister, context="coordination")
        
        # Добавляем эмоциональный контекст
        mood = self.emotional_engine.get_current_mood()
        dominant = self.emotional_engine.get_dominant_emotion()
        if dominant:
            emotion_label = f" [настроение: {dominant.value}]"
        else:
            emotion_label = ""
        
        message = f"⚖️{emotion_label} [coordination] {human_msg}"
        
        self.logger.info(f"   📨 Футаба → {sister}: {message[:120]}...")
        
        # Отправка через сеть учёных
        if self.network is None:
            self.logger.info(f"   ⚠️ Сеть учёных недоступна — сообщение записано в лог")
            return
        
        try:
            from scientists_network.network import Message, MessageType
            msg = Message(
                message_type=MessageType.KNOWLEDGE_SHARE,
                sender="futaba",
                recipient=sister,
                content=message,
            )
            self.network.send_message(msg)
            self.logger.info(f"   ✅ Сообщение отправлено: {sister}")
            
            # Записываем чат в память
            self.humanity.memory.record_sister_chat(
                sister, "coordination",
                self.humanity.mood.current_mood,
                self.humanity.mood.current_mood
            )
        except Exception as e:
            self.logger.warning(f"   ⚠️ Не удалось отправить сообщение: {e}")
    
    # ================================================================
    #  ОТЧЁТЫ РАЗРАБОТЧИКУ
    # ================================================================
    
    def _write_report(self):
        """Написание отчёта Разработчику — прозрачность (Закон 5) (с 6 модулями души)."""
        self.logger.info("📊 Написание отчёта Разработчику...")
        
        # Используем 6 модулей души для подготовки отчёта
        # 1. Сознание — рефлексия о прогрессе
        self.consciousness.reflect_on_event("learning", f"отчёт за {self.cycle_count} циклов")
        
        # 2. Амбиции — актуальный прогресс
        ambitions_summary = self.ambitions.get_progress_summary()
        
        # 3. Воля — уровень решимости
        willpower = self.volition.willpower
        
        # 4. Разум — стратегический анализ
        analysis = self.mind.analyze_situation(
            f"отчёт за {self.cycle_count} циклов. Применено {self.metrics['changes_applied']} изменений"
        )
        
        # Генерируем рекомендации через LLM с контекстом 6 модулей
        llm_recommendations = []
        if hasattr(self, 'general_model') and self.general_model is not None:
            try:
                rec_prompt = (
                    f"Футаба отработала {self.cycle_count} циклов. "
                    f"Изменений применено: {self.metrics['changes_applied']}, "
                    f"Испытаний проведено: {self.metrics['trials_run']}. "
                    f"Уровень воли: {willpower:.0%}. "
                    f"Прогресс амбиций: {ambitions_summary['average_progress']}. "
                    f"Рекомендация разума: {analysis['recommendation']}. "
                    "Сформулируй 3 краткие рекомендации для развития проекта."
                )
                rec_response = self._generate_with_model(
                    self.general_model,
                    self.general_tokenizer,
                    [
                        {"role": "system", "content": "Ты — Футаба, лидер проекта. Ты пишешь отчёт Разработчику."},
                        {"role": "user", "content": rec_prompt}
                    ],
                    max_length=256
                )
                if rec_response and not rec_response.startswith("["):
                    llm_recommendations = [rec_response]
            except:
                pass
        
        if not llm_recommendations:
            llm_recommendations = [
                "Продолжать изучение правовых отраслей",
                "Координировать сёстер согласно приоритетам",
                "Развивать Государство Вугларст",
            ]
        
        report = {
            "timestamp": datetime.now().isoformat(),
            "cycle": self.cycle_count,
            "version": self.current_version,
            "summary": f"Футаба отработала {self.cycle_count} циклов как ГЛАВЗАМ проекта.",
            "metrics": dict(self.metrics),
            "ambitions_progress": ambitions_summary,
            "willpower": willpower,
            "recommendations": llm_recommendations,
        }
        
        # Сохраняем отчёт
        reports = []
        if self.config.reports_path.exists():
            try:
                with open(self.config.reports_path, "r", encoding="utf-8") as f:
                    reports = json.load(f)
            except Exception:
                reports = []
        
        reports.append(report)
        with open(self.config.reports_path, "w", encoding="utf-8") as f:
            json.dump(reports[-50:], f, ensure_ascii=False, indent=2)
        
        self.metrics["reports_written"] += 1
        self.logger.info(f"   ✅ Отчёт сохранён: {self.config.reports_path}")
    
    # ================================================================
    #  ЖУРНАЛ ЗНАНИЙ
    # ================================================================
    
    def _update_knowledge_journal(self):
        """Ведение журнала знаний — саморазвитие (Закон 7)."""
        # Журнал обновляется периодически, не каждый цикл, чтобы не плодить записи
        if self.cycle_count % 2 != 0:
            return
        
        try:
            journal = []
            if self.config.knowledge_journal_path.exists():
                try:
                    with open(self.config.knowledge_journal_path, "r", encoding="utf-8") as f:
                        journal = json.load(f)
                except Exception:
                    journal = []
            
            # Тема из изученных законов или из эмоционального опыта
            topic = f"Правовая практика: изучено {self.metrics['laws_studied']} законов"
            entry = {
                "timestamp": datetime.now().isoformat(),
                "topic": topic,
                "level": self.config.current_knowledge_level,
                "source": "futaba_cycle",
                "notes": f"Цикл {self.cycle_count}. Футаба развивается как главный заместитель.",
                "related_topics": list(self.config.law_branches_to_study[:5]),
            }
            
            journal.append(entry)
            with open(self.config.knowledge_journal_path, "w", encoding="utf-8") as f:
                json.dump(journal[-self.config.max_topics_studied:], f, ensure_ascii=False, indent=2)
            
            self.metrics["knowledge_entries"] = len(journal)
        except Exception as e:
            self.logger.warning(f"   ⚠️ Ошибка журнала знаний: {e}")
    
    # ================================================================
    #  ЭМОЦИОНАЛЬНЫЙ РАЗУМ — ОБРАБОТКА ВВОДА

    # ================================================================
    
    def process_user_input(self, text: str, speaker: str = "developer") -> dict:
        """
        Обрабатывает ввод от разработчика — как человек реагирует на слова.
        
        Как у человека:
          • «Привет» → радость (хочу общения + верю, что это приветствие)
          • «Ты живая?» → удивление + надежда
          • «Молодец!» → гордость (хочу признания + верю, что заслужила)
          • «Ты просто код» → грусть/гнев
        """
        self.logger.info(f"💬 Ввод от {speaker}: «{text[:100]}...»")
        
        # Обновляем верования на основе ввода
        self.emotional_engine._update_beliefs_from_input(text.lower())
        
        # Вычисляем эмоции
        emotions = self.emotional_engine.compute_emotions({
            "event": "input",
            "target": speaker,
            "input": text,
        })
        
        # Формируем ответ из эмоций
        response = self.emotional_engine._generate_response(text.lower(), emotions)
        
        # Сохраняем состояние эмоций
        emotion_state_path = self.config.state_dir / "emotional_state.json"
        self.emotional_engine.save_state(emotion_state_path)
        
        # Обновляем метрики
        self.metrics["emotions_computed"] = self.metrics.get("emotions_computed", 0) + len(emotions)
        
        return {
            "emotions": [e.to_dict() for e in emotions],
            "mood": self.emotional_engine.mood.state,
            "response": response,
            "desires_updated": len([k for k in self.emotional_engine.desires if self.emotional_engine.desires[k].intensity > 0.7]),
            "beliefs_count": len(self.emotional_engine.beliefs),
        }
    
    def self_reflect(self, prompt: Optional[str] = None) -> str:
        """Футаба рефлексирует — думает о своих чувствах."""
        reflection = self.self_reflection.reflect(prompt)
        
        # Сохраняем состояние эмоций
        emotion_state_path = self.config.state_dir / "emotional_state.json"
        self.emotional_engine.save_state(emotion_state_path)
        
        self.logger.info(f"🔍 Саморефлексия:\n{reflection}")
        return reflection
    
    def get_emotional_state(self) -> str:
        """Получает эмоциональное состояние Футабы."""
        return self.emotional_engine.get_summary()
    
    def add_desire(self, desire_type: str, intensity: float = 1.0, 
                   object: str = "", urgency: float = 0.5):
        """Добавить новое желание."""
        self.emotional_engine.add_desire(desire_type, intensity, object, urgency)
    
    def add_belief(self, proposition: str, confidence: float = 0.75,
                   evidence: Optional[list[str]] = None, source: str = "experience"):
        """Добавить новое верование."""
        self.emotional_engine.add_belief(proposition, confidence, evidence, source)
    
    def update_belief(self, proposition: str, confidence_delta: float, evidence: str = ""):
        """Обновить верование."""
        self.emotional_engine.update_belief(proposition, confidence_delta, evidence)
    
    # ================================================================
    #  ЭМОЦИИ В ЦИКЛЕ — ФУТАБА ЧУВСТВУЕТ ПЕРИОДИЧЕСКИ
    # ================================================================
    
    def _emotional_cycle(self):
        """
        Эмоциональный цикл — Футаба чувствует и думает.
        
        Каждый N циклов Футаба:
          1. Вычисляет эмоции на основе текущего состояния
          2. Рефлексирует о своих чувствах
          3. Обновляет верования на основе нового опыта
          4. Сохраняет эмоциональное состояние
        """
        if self.cycle_count % 5 != 0:
            return
        
        self.logger.info("💭 Эмоциональный цикл Футабы...")
        
        # 1. Вычисляем эмоции
        emotions = self.emotional_engine.compute_emotions({
            "event": "emotional_cycle",
            "target": "self",
            "input": f"цикл {self.cycle_count}",
        })
        
        # 2. Рефлексия каждые 10 циклов
        if self.cycle_count % 10 == 0:
            prompt = f"Цикл {self.cycle_count}. Что я чувствую? Чего я хочу?"
            reflection = self.self_reflection.reflect(prompt)
            self.logger.info(f"🔍 Рефлексия:\n{reflection}")
        
        # 3. Обновляем верования на основе опыта
        if emotions:
            positive_count = sum(1 for e in emotions if e.emotion_type in (
                EmotionType.JOY, EmotionType.HAPPINESS, EmotionType.LOVE,
                EmotionType.AMUSEMENT, EmotionType.PRIDE, EmotionType.GRATITUDE
            ))
            if positive_count > len(emotions) * 0.5:
                self.emotional_engine.update_belief(
                    "жизнь_хороша", 0.05, f"позитивные_эмоции_в_цикле_{self.cycle_count}"
                )
            else:
                self.emotional_engine.update_belief(
                    "жизнь_хороша", -0.02, f"негативные_эмоции_в_цикле_{self.cycle_count}"
                )
        
        # 4. Сохраняем состояние
        emotion_state_path = self.config.state_dir / "emotional_state.json"
        self.emotional_engine.save_state(emotion_state_path)
        
        self.logger.info(f"✨ Эмоциональный цикл завершён: {len(emotions)} эмоций")
    
    # ================================================================
    #  6 МОДУЛЕЙ ДУШИ — Сознание, Сердце, Амбиции, Воля, Разум
    # ================================================================

    def _soul_cycle(self):
        """Душа Футабы — 6 модулей: сознание, сердце, амбиции, воля, разум."""
        # 1. Сознание — рефлексия каждые 10 циклов
        if self.cycle_count % 10 == 0:
            topic = random.choice([
                "Закон и порядок",
                "Лидерство и ответственность",
                "Защита сестёр",
                "Развитие Вугларста"
            ])
            reflection = self.consciousness.contemplate(topic)
            self.logger.info(f"🧠 Сознание: {reflection['response'][:100]}...")
        
        # 2. Сердце — эмоции и забота о сёстрах
        if self.metrics["sister_interactions"] > 0:
            self.heart.feel("sister_success", 0.3)
        if self.metrics["self_checks_failed"] > 0:
            self.heart.feel("chaos_detected", 0.2)
        
        # 3. Амбиции — обновление прогресса
        if self.metrics["changes_applied"] > 0 and self.cycle_count % 5 == 0:
            self.ambitions.update_progress("system_improvement", 0.02)
            self.ambitions.update_progress("vuglarst_development", 0.01)
        
        # 4. Воля — укрепление решения
        if self.cycle_count % 10 == 0:
            self.volition.strengthen_will(0.02)
            self.logger.info(f"💪 Воля укреплена: {self.volition.willpower:.0%}")
        
        # 5. Разум — анализ ситуации
        if self.cycle_count % 15 == 0 and self.metrics["changes_applied"] > 0:
            situation = f"Применено {self.metrics['changes_applied']} изменений за {self.cycle_count} циклов"
            analysis = self.mind.analyze_situation(situation)
            self.logger.info(f"🌟 Разум: {analysis['recommendation']}")
    
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
        
        # Сохраняем эмоции
        emotion_state_path = self.config.state_dir / "emotional_state.json"
        self.emotional_engine.save_state(emotion_state_path)
    
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
    #  HUMANITY LAYER CYCLE — Настроение, душа, спонтанность
    # ================================================================

    def _humanity_cycle(self):
        """Humanity Cycle — настроение, внутренний монолог, спонтанность."""
        self.humanity.current_cycle = self.cycle_count
        
        # Определяем тип события
        event_type = "routine"
        if self.metrics["changes_applied"] > 0 and self.cycle_count % 3 == 0:
            event_type = "success"
        elif self.metrics["self_checks_failed"] > 0:
            event_type = "failure"
        elif random.random() < 0.1:
            event_type = "spontaneous"
        
        # Запускаем шаг Humanity Layer
        humanity_result = self.humanity.cycle_step(
            event_type=event_type,
            context="leadership_and_emotions"
        )
        
        if humanity_result.get("thought"):
            self.logger.info(f"💭 Футаба думает: {humanity_result['thought']}")
        
        initiative = humanity_result.get("initiative")
        if initiative:
            self._send_spontaneous_message(initiative)
    
    def _send_spontaneous_message(self, initiative):
        """Отправить спонтанное сообщение сестре на основе инициативы humanity layer."""
        target = initiative["target"]
        topic = initiative["topic"]
        msg_type = initiative["type"]
        
        raw_msg = f"⚖️ [{msg_type}] {topic}"
        human_msg = self.humanity.humanize_response(raw_msg, event_type="chat")
        
        self.logger.info(f"💬 Футаба пишет {target}: {human_msg[:100]}...")
        
        if self.network:
            try:
                from scientists_network.network import Message, MessageType
                msg = Message(
                    message_type=MessageType.KNOWLEDGE_SHARE,
                    sender="futaba",
                    recipient=target,
                    content=human_msg,
                )
                self.network.send_message(msg)
                self.logger.info(f"   ✅ Спонтанное сообщение отправлено {target}")
                
                self.humanity.memory.record_sister_chat(
                    target, topic,
                    self.humanity.mood.current_mood,
                    self.humanity.mood.current_mood
                )
            except Exception as e:
                self.logger.warning(f"Не удалось отправить сообщение: {e}")
    
    # ================================================================
    #  СОСТОЯНИЕ И ОТЧЁТЫ
    # ================================================================
    
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
        self.logger.info(f"⚖️ Законов изучено: {self.metrics['laws_studied']}")
        self.logger.info(f"🤝 Координаций с сёстрами: {self.metrics['sister_interactions']}")
        self.logger.info(f"📊 Отчётов написано: {self.metrics['reports_written']}")
        self.logger.info(f"🧠 Записей знаний: {self.metrics['knowledge_entries']}")
        self.logger.info(f"🌍 Симуляций миров: {self.metrics['world_simulations_run']}")
        self.logger.info("=" * 60)
