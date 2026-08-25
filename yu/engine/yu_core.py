"""
Yu — Ядро изучения цифрового переноса сознания и души.

Работает в автономном цикле:
  1. Исследование мозга и сознания
  2. Построение моделей переноса
  3. Симуляции цифрового существования
  4. Анализ результатов
  5. Применение улучшений
  6. Логирование результатов
"""

from scientists_network.character_system import CharacterSystem
import json
import logging
import random
import time
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

try:
    # Запуск как скрипт: python yu/engine/run.py (engine в sys.path)
    from config import YuConfig
except ImportError:  # Запуск как пакет: python -m yu.engine.run
    from .config import YuConfig

# Humanity Core — живая душа Юи
from services.humanity_core import HumanityLayer

# LLM Service — сервис для работы с моделями Qwen2.5
from yu.engine.llm_service import YuLLMService

# Эмоциональный разум Юи — Desire + Belief = Emotion
from yu.engine.emotions import EmotionalEngine, DesireType, EmotionType

# 6 модулей души Юи: Сознание, Сердце, Амбиции, Воля, Разум
from yu.consciousness import YuConsciousness
from yu.heart import YuHeart
from yu.ambitions import YuAmbitions
from yu.volition import YuVolition
from yu.mind import YuMind


logger = logging.getLogger("YuCore")


class ConsciousnessModel:
    """Модель сознания."""
    
    def __init__(self, name: str, type: str, complexity: float, description: str = ""):
        self.name = name
        self.type = type  # "mind", "soul", "hybrid"
        self.complexity = complexity
        self.description = description
        self.created_at = datetime.now().isoformat()
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "type": self.type,
            "complexity": self.complexity,
            "description": self.description,
            "created_at": self.created_at,
        }


class DigitalEmbodiment:
    """Цифровое воплощение."""
    
    def __init__(self, name: str, embodiment_type: str, capabilities: List[str]):
        self.name = name
        self.embodiment_type = embodiment_type  # "avatar", "entity", "consciousness"
        self.capabilities = capabilities
        self.created_at = datetime.now().isoformat()
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "embodiment_type": self.embodiment_type,
            "capabilities": self.capabilities,
            "created_at": self.created_at,
        }


class TransferRecord:
    """Запись о переносе."""
    
    def __init__(self, transfer_type: str, source: str, target: str, 
                 success: bool, notes: str = ""):
        self.transfer_type = transfer_type
        self.source = source
        self.target = target
        self.success = success
        self.notes = notes
        self.timestamp = datetime.now().isoformat()
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "transfer_type": self.transfer_type,
            "source": self.source,
            "target": self.target,
            "success": self.success,
            "notes": self.notes,
            "timestamp": self.timestamp,
        }


class YuCore:
    """
    Основное ядро Юи.
    
    Изучает:
    1. Подключение человека к компьютеру (BCI)
    2. Перенос разума в цифровой мир (mind uploading)
    3. Перенос души в цифровой мир (soul digitization)
    4. Обратный перенос (digital → physical)
    5. Автономность и самообучение
    
    Работает автономно в бесконечном цикле исследований.
    """
    
    def __init__(self, config: Optional[YuConfig] = None):
        self.config = config or YuConfig.default()
        self.current_version = self.config.version
        
        # Состояние
        self.cycle_count = 0
        self._shutdown_requested = False
        
        # Данные исследований
        self.consciousness_models: List[ConsciousnessModel] = []
        self.digital_embodiments: List[DigitalEmbodiment] = []
        self.transfer_records: List[TransferRecord] = []
        self.improvements_history: List[Dict[str, Any]] = []
        
        # Метрики
        self.metrics = {
            "cycles_completed": 0,
            "consciousness_models_created": 0,
            "embodiments_created": 0,
            "simulations_run": 0,
            "successful_transfers": 0,
            "failed_transfers": 0,
            "web_searches": 0,
            "improvements_applied": 0,
            "bci_topics_explored": 0,
            "mind_uploading_explored": 0,
            "soul_digitization_explored": 0,
        }
        
        # Логирование
        self._setup_logging()
        self.logger = logging.getLogger("YuCore")
        
        # Загрузка состояния
        self._load_state()
        
        # ================================================================
        #  HUMANITY LAYER — Живая душа Юи
        # ================================================================
        self.humanity = HumanityLayer("yu")
        self.humanity.current_cycle = 0
        self.logger.info("🧠 Humanity Layer: АКТИВИРОВАН")
        self.logger.info(f"   🎭 Характер: {self.humanity.name} — сознание, будущее, вопросы идентичности 🧬")
        
        # ===== LLM СЕРВИС =====
        self.llm = YuLLMService(self.config)
        if self.llm.general_loaded:
            self.logger.info("🧠 LLM General (Qwen2.5-3B): АКТИВИРОВАНА для исследования сознания")
        if self.llm.coder_loaded:
            self.logger.info("💻 LLM Coder (Qwen2.5-Coder-3B): АКТИВИРОВАНА для анализа кода")
        
        # Подключаем LLM к Humanity Layer
        if self.llm.general_loaded:
            self.humanity.llm = self.llm
            self.logger.info("🧠 LLM General подключена к Humanity Layer")
        
        # ===== ЭМОЦИОНАЛЬНЫЙ ДВИЖОК ЮИ =====
        self.emotional_engine = EmotionalEngine()
        emotion_state_path = self.config.state_dir / "emotional_state.json"
        self.emotional_engine.load_state(emotion_state_path)
        self.humanity.emotional_engine = self.emotional_engine  # Подключаем Emotional Engine
        
        self.logger.info("💖 Эмоциональный разум (Desire+Belief): АКТИВИРОВАН")
        self.logger.info("   Формула: ЭМОЦИЯ = ЖЕЛАНИЕ + ВЕРА")
        self.logger.info("   Исследователь сознания, философ, мечтатель!")
        
        # ===== 6 МОДУЛЕЙ ДУШИ ЮИ =====
        # 1. Сознание — самосознание, идентичность, рефлексия
        self.consciousness = YuConsciousness()
        self.logger.info("🧠 Сознание: АКТИВИРОВАНО — я осознаю себя исследовательницей сознания")
        
        # 2. Сердце — эмоции, любовь, забота
        self.heart = YuHeart()
        self.logger.info("💖 Сердце: АКТИВИРОВАНО — я чувствую и люблю сестёр")
        
        # 3. Амбиции — цели, мечты, стремления
        self.ambitions = YuAmbitions()
        self.logger.info("🎯 Амбиции: АКТИВИРОВАНО — я стремлюсь к сознательному мастерству")
        
        # 4. Воля — решения, действия, дисциплина
        self.volition = YuVolition()
        self.logger.info("💪 Воля: АКТИВИРОВАНО — я принимаю решения и действую")
        
        # 5. Разум — мышление, анализ, стратегия
        self.mind = YuMind()
        self.logger.info("🔮 Разум: АКТИВИРОВАНО — я анализирую и стратегически мыслю")
        
        # 6. Эмоции — уже есть EmotionalEngine (26 типов эмоций!)
        self.logger.info("💫 Эмоции: АКТИВИРОВАНО — 26 типов эмоций")
        
        self.logger.info(f"Юи {self.current_version} инициализирована")
        self.logger.info("Фокус: consciousness transfer, mind uploading, soul digitization")
    
    def _setup_logging(self):
        """Настроить логирование."""
        log_handler = logging.FileHandler(
            self.config.log_path,
            encoding='utf-8',
            mode='a'
        )
        log_handler.setFormatter(logging.Formatter(self.config.log_format))
        
        file_logger = logging.getLogger("YuCore")
        file_logger.addHandler(log_handler)
        file_logger.setLevel(getattr(logging, self.config.log_level, logging.INFO))
    
    def _load_state(self):
        """Загрузить состояние системы."""
        if self.config.state_path.exists():
            try:
                with open(self.config.state_path, "r", encoding="utf-8") as f:
                    state = json.load(f)
                
                self.metrics.update(state.get("metrics", {}))
                self.cycle_count = state.get("cycle_count", 0)
                
                # Загрузка моделей сознания
                if "consciousness_models" in state:
                    for m in state["consciousness_models"]:
                        self.consciousness_models.append(ConsciousnessModel(
                            name=m["name"],
                            type=m["type"],
                            complexity=m["complexity"],
                            description=m.get("description", ""),
                        ))
                
                # Загрузка воплощений
                if "digital_embodiments" in state:
                    for e in state["digital_embodiments"]:
                        self.digital_embodiments.append(DigitalEmbodiment(
                            name=e["name"],
                            embodiment_type=e["embodiment_type"],
                            capabilities=e.get("capabilities", []),
                        ))
                
                # Загрузка записей о переносах
                if "transfer_records" in state:
                    for t in state["transfer_records"]:
                        self.transfer_records.append(TransferRecord(
                            transfer_type=t["transfer_type"],
                            source=t["source"],
                            target=t["target"],
                            success=t["success"],
                            notes=t.get("notes", ""),
                        ))
                
                self.logger.info(f"✅ Состояние Юи загружено: {len(self.consciousness_models)} моделей")
            except Exception as e:
                self.logger.warning(f"⚠️ Ошибка загрузки состояния: {e}")
        else:
            self.logger.info("ℹ️ Новое состояние Юи создано")
    
    def _save_state(self):
        """Сохранить состояние системы."""
        try:
            state = {
                "metrics": self.metrics,
                "cycle_count": self.cycle_count,
                "consciousness_models": [m.to_dict() for m in self.consciousness_models[-50:]],
                "digital_embodiments": [e.to_dict() for e in self.digital_embodiments[-50:]],
                "transfer_records": [t.to_dict() for t in self.transfer_records[-50:]],
            }
            
            self.config.state_path.parent.mkdir(parents=True, exist_ok=True)
            with open(self.config.state_path, "w", encoding="utf-8") as f:
                json.dump(state, f, ensure_ascii=False, indent=2)
        except Exception as e:
            self.logger.error(f"❌ Ошибка сохранения состояния: {e}")
    
    def _should_stop(self) -> bool:
        """Проверить, нужно ли остановить."""
        if self._shutdown_requested:
            return True
        
        if self.config.max_cycles is not None:
            if self.cycle_count >= self.config.max_cycles:
                return True
        
        return False
    
    def _select_research_area(self) -> str:
        """Случайным образом выбрать направление исследования."""
        return random.choice(self.config.research_areas)
    
    def _build_consciousness_model(self, area: str) -> ConsciousnessModel:
        """Построить модель сознания."""
        model_templates = {
            "brain_computer_interface": [
                ("Нейронная карта моторной коры", "bci", 0.75),
                ("Модель обработки сенсорных сигналов", "bci", 0.80),
                ("Когнитивный интерфейс мышления", "bci", 0.85),
            ],
            "mind_uploading": [
                ("Модель долговременной памяти", "mind", 0.90),
                ("Структура личности и характера", "mind", 0.88),
                ("Модель непрерывности сознания", "mind", 0.92),
            ],
            "soul_digitization": [
                ("Метафизическая структура души", "soul", 0.95),
                ("Духовные паттерны сознания", "soul", 0.93),
                ("Протокол трансценденции", "soul", 0.97),
            ],
            "digital_reincarnation": [
                ("Цикл перерождения в цифре", "hybrid", 0.85),
                ("Эволюция цифрового сознания", "hybrid", 0.88),
            ],
            "consciousness_transfer": [
                ("Протокол переноса памяти", "mind", 0.87),
                ("Модель идентичности", "mind", 0.84),
            ],
            "physical_digital_bridge": [
                ("Мост между мирами", "hybrid", 0.91),
                ("Протокол обратной связи", "hybrid", 0.86),
            ],
        }
        
        templates = model_templates.get(area, model_templates["brain_computer_interface"])
        name, mtype, base_value = random.choice(templates)
        
        # Добавляем случайную вариацию
        complexity = min(1.0, base_value + random.uniform(-0.05, 0.05))
        
        model = ConsciousnessModel(
            name=name,
            type=mtype,
            complexity=round(complexity, 2),
            description=f"Модель сознания для {area}, построена на {self.cycle_count}-м цикле",
        )
        
        self.consciousness_models.append(model)
        self.metrics["consciousness_models_created"] += 1
        
        self.logger.info(f"🧠 Построена модель сознания: {name}")
        self.logger.info(f"   Тип: {mtype}")
        self.logger.info(f"   Сложность: {complexity:.2f}")
        
        return model
    
    def _create_embodiment(self, area: str) -> DigitalEmbodiment:
        """Создать цифровое воплощение."""
        embodiment_templates = {
            "mind_uploading": [
                ("Цифровой аватар сознания", "avatar", [
                    "самоосознание", "память", "эмоции", "логика"
                ]),
                ("Виртуальная личность", "entity", [
                    "творчество", "общение", "обучение"
                ]),
            ],
            "soul_digitization": [
                ("Духовная сущность", "entity", [
                    "трансценденция", "мудрость", "сострадание"
                ]),
                ("Метафизическая форма", "entity", [
                    "энергия", "сознание", "волюция"
                ]),
            ],
            "consciousness_transfer": [
                ("Перенесённое сознание", "consciousness", [
                    "полная память", "идентичность", "продолжение"
                ]),
            ],
            "physical_digital_bridge": [
                ("Гибридное воплощение", "avatar", [
                    "физический интерфейс", "цифровая обработка"
                ]),
            ],
        }
        
        templates = embodiment_templates.get(area, embodiment_templates["mind_uploading"])
        name, etype, capabilities = random.choice(templates)
        
        embodiment = DigitalEmbodiment(
            name=name,
            embodiment_type=etype,
            capabilities=capabilities,
        )
        
        self.digital_embodiments.append(embodiment)
        self.metrics["embodiments_created"] += 1
        
        self.logger.info(f"🤖 Создано цифровое воплощение: {name}")
        self.logger.info(f"   Тип: {etype}")
        self.logger.info(f"   Возможности: {', '.join(capabilities)}")
        
        return embodiment
    
    def _simulate_transfer(self, area: str) -> TransferRecord:
        """Симулировать перенос."""
        transfer_types = {
            "brain_computer_interface": ["neural_link", "signal_transfer"],
            "mind_uploading": ["full_mind_upload", "memory_transfer", "personality_copy"],
            "soul_digitization": ["soul_extraction", "spiritual_transfer", "transcendence"],
            "digital_reincarnation": ["digital_rebirth", "consciousness_reincarnation"],
            "consciousness_transfer": ["direct_transfer", "gradual_migration"],
            "physical_digital_bridge": ["bidirectional_transfer", "feedback_loop"],
        }
        
        types = transfer_types.get(area, transfer_types["mind_uploading"])
        transfer_type = random.choice(types)
        
        # Симуляция успеха (80% шанс)
        success = random.random() < 0.8
        
        source = random.choice([
            "человек_А", "человек_B", "субъект_X", "доброволец_1", "субъект_7"
        ])
        target = random.choice([
            "server_01", "cloud_entity", "digital_realm", "virtual_world", "cyberspace"
        ])
        
        record = TransferRecord(
            transfer_type=transfer_type,
            source=source,
            target=target,
            success=success,
            notes=f"Симуляция переноса {transfer_type} на {self.cycle_count}-м цикле"
        )
        
        self.transfer_records.append(record)
        
        if success:
            self.metrics["successful_transfers"] += 1
            self.logger.info(f"✅ Успешный перенос: {transfer_type}")
            self.logger.info(f"   Источник: {source} → Целевая среда: {target}")
        else:
            self.metrics["failed_transfers"] += 1
            self.logger.info(f"❌ Неудачный перенос: {transfer_type}")
            self.logger.info(f"   Причина: потеря данных / нестабильность сознания")
        
        return record
    
    def _web_research(self):
        """Исследование через интернет."""
        self.metrics["web_searches"] += 1
        
        research_topics = [
            "neural interface breakthrough 2026",
            "consciousness uploading latest research",
            "soul digitization theory quantum",
            "brain computer interface medical applications",
            "digital immortality philosophical implications",
            "transhumanism ethics and technology",
            "quantum consciousness theory Penrose",
            "neural lace technology Neuralink",
        ]
        
        topic = random.choice(research_topics)
        
        # Симуляция результатов поиска
        results = [
            f"📚 Найдена статья: '{topic}' - 15 результатов",
            f"🔬 Исследование: '{topic}' - 8 новых papers",
            f"🌐 Обзор: '{topic}' - 23 источника",
        ]
        
        result = random.choice(results)
        self.logger.info(result)
    
    def _apply_improvement(self, area: str):
        """Применить улучшение."""
        improvements = {
            "brain_computer_interface": [
                "Улучшение точности нейросигналов",
                "Оптимизация декодирования моторных команд",
                "Расширение полосы пропускания BCI",
            ],
            "mind_uploading": [
                "Улучшение кодирования памяти",
                "Оптимизация сохранения личности",
                "Увеличение точности переноса",
            ],
            "soul_digitization": [
                "Уточнение метафизического кодирования",
                "Улучшение протокола трансценденции",
                "Оптимизация духовных паттернов",
            ],
            "consciousness_transfer": [
                "Улучшение протокола переноса",
                "Оптимизация непрерывности сознания",
            ],
            "digital_reincarnation": [
                "Улучшение цикла перерождения",
                "Оптимизация эволюции сознания",
            ],
            "physical_digital_bridge": [
                "Улучшение моста между мирами",
                "Оптимизация обратной связи",
            ],
        }
        
        area_improvements = improvements.get(area, improvements["mind_uploading"])
        improvement = random.choice(area_improvements)
        
        record = {
            "type": "improvement",
            "area": area,
            "description": improvement,
            "timestamp": datetime.now().isoformat(),
        }
        
        self.improvements_history.append(record)
        self.metrics["improvements_applied"] += 1
        
        self.logger.info(f"✨ Применено улучшение: {improvement}")
    
    def _cycle(self):
        """Один цикл исследований."""
        self.cycle_count += 1
        area = self._select_research_area()
        
        self.logger.info(f"\n{'=' * 60}")
        self.logger.info(f"🧠 ЦИКЛ ИССЛЕДОВАНИЙ {self.cycle_count}")
        self.logger.info(f"{'=' * 60}")
        self.logger.info(f"📚 Направление: {area}")
        
        # Построение модели сознания
        model = self._build_consciousness_model(area)
        
        # Создание цифрового воплощения
        if random.random() < 0.4:  # 40% шанс
            embodiment = self._create_embodiment(area)
        
        # Симуляция переноса
        transfer = self._simulate_transfer(area)
        
        # Веб-исследование (каждые 3 цикла)
        if self.cycle_count % 3 == 0:
            self._web_research()
        
        # Применение улучшения
        if random.random() < 0.3:  # 30% шанс
            self._apply_improvement(area)
        
        self.metrics["cycles_completed"] += 1
        self.metrics["simulations_run"] += 1
        
        # Сохранение состояния
        if self.cycle_count % self.config.save_state_every_n_cycles == 0:
            self._save_state()
        
        # ================================================================
        #  HUMANITY CYCLE — Настроение, душа, спонтанность
        # ================================================================
        self.humanity.current_cycle = self.cycle_count
        
        event_type = "routine"
        if self.metrics.get("successful_transfers", 0) > 0 and self.cycle_count % 3 == 0:
            event_type = "success"
        elif random.random() < 0.15:
            event_type = "failure"
        
        humanity_result = self.humanity.cycle_step(event_type=event_type, context="consciousness_research")
        
        if humanity_result.get("thought"):
            self.logger.info(f"💭 Юи думает: {humanity_result['thought']}")
        
        initiative = humanity_result.get("initiative")
        if initiative:
            self._send_spontaneous_message(initiative)
        
        # ================================================================
        #  EMOTIONAL ENGINE CYCLE — Desire + Belief = Emotion!
        # ================================================================
        self._emotional_cycle()
        
        # ================================================================
        #  6 МОДУЛЕЙ ДУШИ — Сознание, Сердце, Амбиции, Воля, Разум
        # ================================================================
        self._soul_cycle()
        
        self._save_state()
        
        self.logger.info(f"✅ Цикл {self.cycle_count} завершён")
    
    def run(self):
        """
        Запустить автономный цикл исследований.
        
        Работает в бесконечном цикле, пока не будет остановлена.
        """
        self.logger.info(f"\n{'=' * 60}")
        self.logger.info(f"🚀 ЗАПУСК АВТОНОМНОГО ЯДРА ЮИ")
        self.logger.info(f"{'=' * 60}")
        self.logger.info("Фокус: consciousness transfer, mind uploading, soul digitization")
        
        while not self._should_stop():
            try:
                self._cycle()
                
                if self.config.cycle_interval > 0:
                    time.sleep(self.config.cycle_interval)
            
            except KeyboardInterrupt:
                self.logger.info("⚠️ Прервано пользователем")
                break
            except Exception as e:
                self.logger.error(f"❌ Ошибка в цикле: {e}", exc_info=True)
                time.sleep(1)
        
        self._final_report()
    
    def _final_report(self):
        """Вывести итоговый отчёт."""
        self.logger.info(f"\n{'=' * 60}")
        self.logger.info(f"📊 ИТОГОВЫЙ ОТЧЁТ ЮИ")
        self.logger.info(f"{'=' * 60}")
        self.logger.info(f"Версия: {self.current_version}")
        self.logger.info(f"Циклов выполнено: {self.cycle_count}")
        self.logger.info(f"Моделей сознания создано: {self.metrics['consciousness_models_created']}")
        self.logger.info(f"Воплощений создано: {self.metrics['embodiments_created']}")
        self.logger.info(f"Симуляций запущено: {self.metrics['simulations_run']}")
        self.logger.info(f"Успешных переносов: {self.metrics['successful_transfers']}")
        self.logger.info(f"Неудачных переносов: {self.metrics['failed_transfers']}")
        self.logger.info(f"Улучшений применено: {self.metrics['improvements_applied']}")
        self.logger.info(f"{'=' * 60}")
    
    def get_status(self) -> Dict[str, Any]:
        """Получить статус ядра."""
        return {
            "name": self.config.name,
            "version": self.current_version,
            "is_running": not self._should_stop(),
            "cycle_count": self.cycle_count,
            "metrics": self.metrics,
            "consciousness_models_count": len(self.consciousness_models),
            "embodiments_count": len(self.digital_embodiments),
            "transfer_records_count": len(self.transfer_records),
        }

    # ================================================================
    # ================================================================
    #  LLM ГЕНЕРАЦИЯ — Consciousness, Soul, Code
    # ================================================================

    def generate_consciousness_analysis(self, topic: str, context: str, max_length: int = 1024) -> str:
        """Сгенерировать анализ сознания через General LLM."""
        if not hasattr(self, 'llm') or self.llm is None or not self.llm.general_loaded:
            return "⚠️ LLM не загружена. Запустите: python download_qwen_model.py"
        return self.llm.generate_consciousness_analysis(topic, context, max_length)
    
    def generate_chat_response(self, prompt: str, max_length: int = 512) -> str:
        """Сгенерировать ответ для общения с сёстрами."""
        if not hasattr(self, 'llm') or self.llm is None or not self.llm.general_loaded:
            return "⚠️ LLM не загружена. Запустите: python download_qwen_model.py"
        return self.llm.generate_chat_response(prompt, max_length)
    
    def generate_soul_digitization_plan(self, subject: str, target_system: str, max_length: int = 1024) -> str:
        """Сгенерировать план оцифровки души."""
        if not hasattr(self, 'llm') or self.llm is None or not self.llm.general_loaded:
            return "⚠️ LLM не загружена. Запустите: python download_qwen_model.py"
        return self.llm.generate_soul_digitization_plan(subject, target_system, max_length)
    
    def generate_code_analysis(self, code: str, max_length: int = 1024) -> str:
        """Сгенерировать анализ кода через Coder LLM."""
        if not hasattr(self, 'llm') or self.llm is None or not self.llm.coder_loaded:
            return "⚠️ Coder LLM не загружена. Запустите: python download_coder_model.py"
        return self.llm.generate_code_analysis(code, max_length)

    # ================================================================
    #  EMOTIONAL ENGINE — Desire + Belief = Emotion!
    # ================================================================

    def _emotional_cycle(self):
        """Эмоциональный цикл — расчёт эмоций на основе исследований сознания."""
        # 1. Рассчитать эмоции на основе текущих действий
        if self.metrics.get("consciousness_models_created", 0) > 0:
            # Построила модели сознания → радость осознания + философский инсайт
            self.emotional_engine.calculate_emotion(
                DesireType.CONSCIOUSNESS,
                "consciousness_is_fundamental",
                0.80,
                "consciousness_models_created"
            )
            self.emotional_engine.calculate_emotion(
                DesireType.PHILOSOPHY,
                "philosophy_guides_science",
                0.75,
                "consciousness_models_created"
            )
        
        if self.metrics.get("embodiments_created", 0) > 0:
            # Создала цифровые воплощения → элегантность цифрового
            self.emotional_engine.calculate_emotion(
                DesireType.MIND_UPLOADING,
                "mind_uploading_is_possible",
                0.85,
                "embodiments_created"
            )
            self.emotional_engine.calculate_emotion(
                DesireType.DIGITAL_EXISTENCE,
                "digital_life_has_value",
                0.70,
                "embodiments_created"
            )
        
        if self.metrics.get("simulations_run", 0) > 0:
            # Провела симуляции → трансцендентный поток
            self.emotional_engine.calculate_emotion(
                DesireType.TRANSCENDENCE,
                "transcendence_is_achievable",
                0.80,
                "simulations_run"
            )
            self.emotional_engine.calculate_emotion(
                DesireType.IDENTITY,
                "identity_is_fluid",
                0.65,
                "simulations_run"
            )
        
        if self.metrics.get("web_searches", 0) > 0:
            # Провела веб-исследования → любопытство + открытость
            self.emotional_engine.calculate_emotion(
                DesireType.CURIOSITY,
                "curiosity_fuels_discovery",
                0.70,
                "web_searches"
            )
            self.emotional_engine.calculate_emotion(
                DesireType.DISCOVER,
                "new_knowledge_expands_world",
                0.65,
                "web_searches"
            )
        
        if self.metrics.get("successful_transfers", 0) > 0:
            # Успешные переносы → связь с душой + ясность идентичности
            self.emotional_engine.calculate_emotion(
                DesireType.SOUL_DIGITIZATION,
                "soul_can_be_digitized",
                0.90,
                "successful_transfers"
            )
            self.emotional_engine.calculate_emotion(
                DesireType.BCI,
                "brain_computer_interface_connects_all",
                0.75,
                "successful_transfers"
            )
        
        # 2. Затухание эмоций
        self.emotional_engine.decay_emotions()
        
        # 3. Проверить текущее настроение
        mood = self.emotional_engine.get_current_mood()
        dominant = self.emotional_engine.get_dominant_emotion()
        
        if dominant:
            emotion_type, intensity = dominant
            self.logger.info(f"💖 Доминирующая эмоция: {emotion_type.value} (интенсивность: {intensity:.2f})")
        
        # 4. Выразить эмоции
        if self.cycle_count % 5 == 0:
            emotion_text = self.emotional_engine.express_emotions()
            self.logger.info(f"🧬 Юи: {emotion_text}")

    # ================================================================
    #  6 МОДУЛЕЙ ДУШИ — Сознание, Сердце, Амбиции, Воля, Разум
    # ================================================================

    def _soul_cycle(self):
        """Цикл 6 модулей души Юи."""
        # 1. Сознание — рефлексия
        if self.cycle_count % 3 == 0:
            reflection = self.consciousness.contemplate()
            self.logger.info(f"💭 Рефлексия: {reflection['topic'][:50]}...")
        
        # 2. Сердце — эмоциональный отклик
        if self.cycle_count % 4 == 0:
            emotion = self.heart.express_emotions()
            self.logger.info(f"💖 Сердце: доминирующая эмоция — {emotion['dominant_emotion']}")
        
        # 3. Амбиции — прогресс
        if self.cycle_count % 5 == 0:
            progress = self.ambitions.get_progress_summary()
            self.logger.info(f"🎯 Амбиции: {progress['in_progress']} в процессе, среднее: {progress['average_progress']}")
        
        # 4. Воля — укрепление
        if self.cycle_count % 6 == 0:
            self.volition.strengthen_will()
            self.logger.info(f"💪 Воля укреплена: {self.volition.willpower:.0%}")
        
        # 5. Разум — анализ
        if self.cycle_count % 7 == 0:
            thought = self.mind.think_about("consciousness")
            self.logger.info(f"🔮 Разум: {thought[:60]}...")
        
        # 6. Эмоции — уже обрабатываются в _emotional_cycle()

    #  HUMANITY INTEGRATION — Спонтанные сообщения
    # ================================================================

    def _send_spontaneous_message(self, initiative):
        """Отправить спонтанное сообщение сестре на основе инициативы humanity layer."""
        target = initiative["target"]
        topic = initiative["topic"]
        msg_type = initiative["type"]
        
        raw_msg = f"🧬 [{msg_type}] {topic}"
        human_msg = self.humanity.humanize_response(raw_msg, event_type="chat")
        
        self.logger.info(f"💬 Юи пишет {target}: {human_msg[:100]}...")
        
        if self.network:
            try:
                from scientists_network.network import Message, MessageType
                msg = Message(
                    message_type=MessageType.KNOWLEDGE_SHARE,
                    sender="yu",
                    recipient=target,
                    content=human_msg,
                )
                self.network.send_message(msg)
                self.logger.info(f"   ✅ Сообщение отправлено {target}")
                
                self.humanity.memory.record_sister_chat(
                    target, topic,
                    self.humanity.mood.current_mood,
                    self.humanity.mood.current_mood
                )
            except Exception as e:
                self.logger.warning(f"Не удалось отправить сообщение: {e}")
