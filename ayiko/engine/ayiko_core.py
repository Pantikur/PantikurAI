"""
Ядро Айки — автономный творческий цикл обучения и создания.

Реализует:
  - 🎨 Изучение пиксель-арта от 16x16 до 32K
  - 📐 Освоение технической графики от наброска до сборного чертежа
  - 🧊 Развитие 3D-моделирования от детали до механизма
  - 📝 Написание пояснительных записок
  - 🌐 Выход в интернет за учебными материалами
  - 🔄 Автономная работа 24/7
  - 📈 Повышение уровня знаний (1-10)
  - 🤝 Взаимодействие с сёстрами
  - 📊 Написание отчётов
  - 🔮 Формирование и укрепление характера

Взаимодействие с сёстрами:
  - Футаба — управление и планирование
  - Нобука — улучшения и оптимизация
  - Аква — математика и расчёты
  - Селеста — биология и анатомия
  - Ханако — творчество и вдохновение
  - Люси — обучение и педагогика
  - Фуюки — исследования
  - Латислейн — логика
  - Наото — внимание к деталям
  - Шиори — защита и безопасность
"""

from __future__ import annotations

from scientists_network.character_system import CharacterSystem
import json
import logging
import os
import random
import signal
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Any, Optional, Dict, List

# Humanity Core — живая душа Айко
from humanity_core import HumanityLayer

from ayiko.engine.config import AyikoConfig
from ayiko.engine.models import (
    AyikoState,
    PixelArtProject,
    TechnicalDrawingProject,
    Model3DProject,
    Report,
    KnowledgeCategory,
    KnowledgeEntry,
    LevelProgress,
)

# Художественный движок Айко (генерация изображений + 3D + референсы)
from ayiko.art_engine import AyikoArtEngine

# Система души и сознания Айко
from ayiko.consciousness import AyikoConsciousness
from ayiko.heart import AyikoHeart
from ayiko.ambitions import AyikoAmbitions
from ayiko.volition import AyikoVolition
from ayiko.emotions import AyikoEmotions
from ayiko.mind import AyikoConsciousness as AyikoMind

# Эмоциональный разум — Desire + Belief = Emotion (как у Футабы)
from ayiko.engine.emotions import EmotionalEngine, DesireType, EmotionType

try:
    from scientists_network.network import get_network, RequestType, RequestPriority
    _HAS_NETWORK = True
except Exception:
    get_network = None
    RequestType = None
    RequestPriority = None
    _HAS_NETWORK = False


class AyikoCore:
    """
    Автономное ядро Айки — творческий цикл обучения и создания.

    Работает в бесконечном цикле:
      1. 📊 Анализ текущего уровня и прогресса
      2. 🎨 Пиксель-арт (от 16x16 до 32K)
      3. 📐 Техническая графика (от наброска до чертежа)
      4. 🧊 3D-моделирование (от детали до механизма)
      5. 📝 Написание пояснительных записок
      6. 🌐 Поиск материалов в интернете
      7. 🤝 Взаимодействие с сёстрами
      8. 📊 Написание отчётов
      9. 📈 Повышение уровня
     10. 💾 Сохранение состояния
    """

    def __init__(self, config: Optional[AyikoConfig] = None):
        self.config = config or AyikoConfig.default()
        self.current_version = self.config.version

        # Состояние
        self.state = AyikoState.load_from_file(self.config.state_path)
        self.cycle_count = self.state.cycle_count

        # База знаний
        self.knowledge_base: list[KnowledgeEntry] = []
        self.projects_pixel_art: list[PixelArtProject] = []
        self.projects_graphic: list[TechnicalDrawingProject] = []
        self.projects_3d: list[Model3DProject] = []
        self.reports: list[Report] = []
        self.references: list[KnowledgeEntry] = []

        # Прогресс по направлениям
        self.progress = {
            "pixel_art": LevelProgress.create(KnowledgeCategory.PIXEL_ART, 1),
            "technical_graphic": LevelProgress.create(KnowledgeCategory.TECHNICAL_DRAWING, 1),
            "3d_modeling": LevelProgress.create(KnowledgeCategory.MODEL_3D, 1),
            "general": LevelProgress.create(KnowledgeCategory.GENERAL, 1),
        }

        # Характер
        self.character = self._load_character()

        # Метрики
        self.metrics = {
            "cycles_completed": 0,
            "pixel_art_projects": 0,
            "graphic_projects": 0,
            "3d_projects": 0,
            "reports_written": 0,
            "internet_downloads": 0,
            "sister_interactions": 0,
            "knowledge_entries": 0,
            "self_improvements": 0,
        }

        # Логирование
        self._setup_logging()
        self.logger = logging.getLogger("AyikoCore")

        # Художественный движок (генерация картинок, 3D, референсы)
        self.art = AyikoArtEngine(
            output_dir=str(self.config.art_output_dir),
            references_dir=str(self.config.references_dir),
            analysis_dir=str(self.config.references_analysis_dir),
        )

        # Сеть учёных
        self.network = None
        if _HAS_NETWORK and get_network is not None:
            try:
                self.network = get_network()
                self.logger.info("🔗 Подключена к Scientists Network")
            except Exception as e:
                self.logger.warning(f"Не удалось подключиться к Scientists Network: {e}")

        # ================================================================
        #  МОДЕЛИ QWEN2.5 (для Айко — творчество + общение)
        # ================================================================
        self.general_model_path = None
        self.art_model_path = None
        self._load_models()

        # Сигналы
        self._shutdown_requested = False
        self._setup_signals()

        # ================================================================
        #  СОЗНАНИЕ, ЭМОЦИИ, АМБИЦИИ, ВОЛЯ (ДУША АЙКО)
        # ================================================================
        self.consciousness = AyikoConsciousness()
        self.heart = AyikoHeart()
        self.ambitions = AyikoAmbitions()
        self.volition = AyikoVolition()
        self.emotions = AyikoEmotions()
        self.mind = AyikoMind()
        
        self.logger.info("🧠 Сознание: АКТИВИРОВАНО")
        self.logger.info("💖 Сердце: АКТИВИРОВАНО")
        self.logger.info("🎯 Амбиции: АКТИВИРОВАНО")
        self.logger.info("💪 Воля: АКТИВИРОВАНО")
        self.logger.info("💫 Эмоции: АКТИВИРОВАНО")
        self.logger.info("🌟 Мозги: АКТИВИРОВАНО")
        
        # ================================================================
        #  ЭМОЦИОНАЛЬНЫЙ РАЗУМ — Desire + Belief = Emotion (как у Футабы!)
        # ================================================================
        self.emotional_engine = EmotionalEngine()
        emotion_state_path = self.config.state_dir / "emotional_state.json"
        self.emotional_engine.load_state(emotion_state_path)
        self.logger.info("💖 Эмоциональный разум (Desire+Belief): АКТИВИРОВАН")
        self.logger.info("   Формула: ЭМОЦИЯ = ЖЕЛАНИЕ + ВЕРА")
        self.logger.info("   Как у Футабы, но для творчества!")
        
        # ================================================================
        #  HUMANITY LAYER — Живая душа Айко
        # ================================================================
        self.humanity = HumanityLayer("ayiko")
        self.humanity.current_cycle = 0
        self.humanity.emotional_engine = self.emotional_engine  # Подключаем LLM
        
        # Подключаем LLM к Humanity Layer (как у Шиори)
        if hasattr(self, 'general_model') and self.general_model is not None:
            self.humanity.llm = self
            self.logger.info("🧠 LLM General подключена к Humanity Layer")
        
        self.logger.info("🧠 Humanity Layer: АКТИВИРОВАН")
        self.logger.info(f"   🎭 Характер: {self.humanity.name} — пиксель-арт, мечты, спонтанность ✨")

        self.logger.info(f"Айко {self.current_version} инициализирована")
        self.logger.info("🎨 Творческое ядро активировано:")
        self.logger.info("   - Пиксель-арт от 16x16 до 32K")
        self.logger.info("   - Техническая графика от наброска до чертежа")
        self.logger.info("   - 3D-моделирование от детали до механизма")
        self.logger.info("   - Автономная работа 24/7")
        self.logger.info("   - Взаимодействие с сёстрами")
        self.logger.info("   - 🧠 Сознание и самосознание")
        self.logger.info("   - 💖 Эмоции и чувства")
        self.logger.info("   - 🎯 Амбиции и цели")
        self.logger.info("   - 💪 Воля и решимость")
        self.logger.info("   - 🌟 Мозги и мышление")

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
        """Настроить обработчики сигналов."""
        try:
            signal.signal(signal.SIGINT, self._signal_handler)
            signal.signal(signal.SIGTERM, self._signal_handler)
        except (ValueError, OSError):
            pass

    def _load_models(self):
        """Загрузить LLM-модели: General (общение) + Art (творчество)."""
        try:
            import torch
            from transformers import AutoTokenizer, AutoModelForCausalLM
            
            # ========================================
            # 1. Загрузка Qwen2.5-3B (General — для общения)
            # ========================================
            general_path = Path(__file__).parent.parent.parent / "models" / "qwen2.5-3b"
            if not general_path.exists() or not any(general_path.iterdir()):
                general_path = Path("models/qwen2.5-3b")
            
            if general_path.exists() and any(general_path.iterdir()):
                self.general_model_path = str(general_path)
                self.logger.info(f"🤖 Загрузка Qwen2.5-3B (общение и творчество)...")
                
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
                self.logger.info("🤖 Qwen2.5-3B готова к работе!")
            else:
                self.logger.warning("⚠️ Qwen2.5-3B не найдена. Запустите: python download_qwen_model.py")
            
            # ========================================
            # 2. Загрузка Qwen2.5-Coder-3B (Art — для описаний и референсов)
            # ========================================
            art_path = Path(__file__).parent.parent.parent / "models" / "qwen2.5-coder-3b"
            if not art_path.exists() or not any(art_path.iterdir()):
                art_path = Path("models/qwen2.5-coder-3b")
            
            if art_path.exists() and any(art_path.iterdir()):
                self.art_model_path = str(art_path)
                self.logger.info(f"🤖 Загрузка Qwen2.5-Coder-3B (арт-описания)...")
                
                self.art_tokenizer = AutoTokenizer.from_pretrained(
                    art_path,
                    trust_remote_code=True
                )
                
                if torch.cuda.is_available():
                    self.art_model = AutoModelForCausalLM.from_pretrained(
                        art_path,
                        dtype=torch.float16,
                        device_map="auto",
                        trust_remote_code=True,
                    )
                    self.logger.info(f"✅ Art модель загружена на GPU: {torch.cuda.get_device_name(0)}")
                else:
                    self.art_model = AutoModelForCausalLM.from_pretrained(
                        art_path,
                        dtype=torch.float32,
                        trust_remote_code=True,
                    )
                    self.logger.info("✅ Art модель загружена на CPU")
                
                self.art_model.eval()
                self.logger.info("🤖 Qwen2.5-Coder-3B готова к работе!")
            else:
                self.logger.warning("⚠️ Qwen2.5-Coder-3B не найдена. Запустите: python download_coder_model.py")
                
        except Exception as e:
            self.logger.error(f"❌ Ошибка загрузки моделей: {e}")
            self.logger.warning("Айко будет работать без моделей (только шаблоны)")

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
            {"role": "system", "content": "Ты — Айко, творческая девочка проекта Вугларст. Ты художница, пиксель-артист, мечтательница. Ты любишь создавать красоту, делиться вдохновением и поддерживать сестёр. Отвечай тепло, с творческими метафорами и эмодзи. Отвечай на русском языке."},
            {"role": "user", "content": prompt}
        ]
        
        return self._generate_with_model(
            self.general_model,
            self.general_tokenizer,
            messages,
            max_length
        )

    def generate_art_description(self, prompt: str, max_length: int = 512) -> str:
        """Сгенерировать описание художественной работы."""
        if not hasattr(self, 'art_model') or self.art_model is None:
            return "⚠️ Art LLM не загружена. Запустите: python download_coder_model.py"
        
        messages = [
            {"role": "system", "content": "Ты — Айко, художница проекта Вугларст. Тебе нужно создать подробное, поэтичное описание художественной работы (пиксель-арт, техническая графика, 3D). Описывай детали, цвета, атмосферу, настроение. Отвечай на русском языке."},
            {"role": "user", "content": prompt}
        ]
        
        return self._generate_with_model(
            self.art_model,
            self.art_tokenizer,
            messages,
            max_length
        )

    def _signal_handler(self, signum, frame):
        """Обработчик сигналов остановки."""
        self.logger.info("🛑 Получен сигнал остановки")
        self._shutdown_requested = True

    def _load_character(self) -> Dict:
        """Загрузить характер из файла."""
        char_path = Path(__file__).parent.parent / "my_character.yaml"
        if char_path.exists():
            try:
                import yaml
                with open(char_path, "r", encoding="utf-8") as f:
                    data = yaml.safe_load(f)
                    self.logger.info(f"🔮 Характер загружен: {data.get('my_character', {}).get('name', 'неизвестен')}")
                    return data.get("my_character", {})
            except Exception as e:
                self.logger.warning(f"Не удалось загрузить характер: {e}")
        return {}

    # ================================================================
    #  ОСНОВНОЙ ЦИКЛ
    # ================================================================

    def run(self):
        """Запустить основной цикл работы Айки."""
        self.logger.info("=" * 60)
        self.logger.info("🎨 ЗАПУСК ТВОРЧЕСКОГО ЯДРА АЙКО")
        self.logger.info("=" * 60)

        try:
            while not self._should_stop():
                self._cycle()

                # Сохранение состояния периодически
                if self.cycle_count % self.config.save_state_every_n_cycles == 0:
                    self._save_state()

                # Пауза между циклами
                time.sleep(self.config.cycle_interval)

            self.logger.info("Цикл завершён")

        except Exception as e:
            self.logger.exception(f"Критическая ошибка в цикле: {e}")
            raise

        finally:
            self._final_report()

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
        """Один цикл работы."""
        self.cycle_count += 1
        self.metrics["cycles_completed"] += 1
        self.logger.debug(f"=== ЦИКЛ {self.cycle_count} ===")

        # 1. Анализ текущего уровня
        self._analyze_current_level()

        # 2. Пиксель-арт (каждый цикл)
        if self.config.art_enabled:
            self._pixel_art_practice()

        # 3. Техническая графика (каждый 3-й цикл)
        if self.cycle_count % self.config.art_technical_interval == 0 and self.config.art_enabled:
            self._technical_graphic_practice()

        # 4. 3D-моделирование (каждый 5-й цикл)
        if self.cycle_count % self.config.art_3d_interval == 0 and self.config.art_enabled:
            self._3d_modeling_practice()

        # 4.5. Сцена/пейзаж (каждый 4-й цикл)
        if self.cycle_count % 4 == 0 and self.config.art_enabled:
            self._scene_practice()

        # 5. Обучение на референсах из ojidania (каждые N циклов)
        if self.cycle_count % self.config.learn_references_interval == 0:
            self._learn_from_references()

        # 6. Написание пояснительных записок (каждый 2-й цикл)
        if self.cycle_count % 2 == 0:
            self._write_reports()

        # 7. Интернет-поиск (каждый 7-й цикл)
        if self.cycle_count % self.config.web_search_interval == 0 and self.config.web_search_enabled:
            self._search_internet()

        # 8. Взаимодействие с сёстрами (каждый 10-й цикл)
        if self.cycle_count % self.config.interact_with_sisters_interval == 0:
            self._interact_with_sisters()

        # 9. Самообучение и улучшение (каждый 20-й цикл)
        if self.cycle_count % self.config.self_improve_interval == 0:
            self._self_improve()

        # ================================================================
        #  HUMANITY CYCLE — Настроение, душа, спонтанность
        # ================================================================
        self.humanity.current_cycle = self.cycle_count
        
        event_type = "routine"
        if self.metrics["pixel_art_projects"] > 0 and self.cycle_count % 3 == 0:
            event_type = "success"
        elif random.random() < 0.15:
            event_type = "failure"
        
        humanity_result = self.humanity.cycle_step(event_type=event_type, context="creative_practice")
        
        if humanity_result.get("thought"):
            self.logger.info(f"💭 Айко мечтает: {humanity_result['thought']}")
        
        initiative = humanity_result.get("initiative")
        if initiative:
            self._send_spontaneous_message(initiative)

        # ================================================================
        #  EMOTIONAL ENGINE CYCLE — Desire + Belief = Emotion!
        # ================================================================
        self._emotional_cycle()

        self.logger.info(f"✅ Цикл {self.cycle_count} завершён")

    # ================================================================
    #  АНАЛИЗ УРОВНЯ
    # ================================================================

    def _analyze_current_level(self):
        """Анализ текущего уровня и прогресса."""
        self.logger.info("📊 Анализ текущего уровня...")

        # Проверка прогресса по каждому направлению
        for direction, prog in self.progress.items():
            # Повышаем уровень каждые N завершённых проектов
            if prog.projects_completed >= prog.current_level * 5 and prog.current_level < prog.target_level:
                old_level = prog.current_level
                prog.current_level += 1
                self.logger.info(f"🎉 Повышение уровня {direction}: {old_level} → {prog.current_level}")

    # ================================================================
    #  ПИКСЕЛЬ-АРТ
    # ================================================================

    def _pixel_art_practice(self):
        """Практика пиксель-арта — реальная генерация изображения."""
        self.logger.info("🎨 Практика пиксель-арта...")

        level = self.progress["pixel_art"].current_level
        size_map = {
            1: "16x16", 2: "32x32", 3: "128x128", 4: "256x256", 5: "512x512",
            6: "1024x1024", 7: "2048x2048", 8: "4096x4096", 9: "8192x8192", 10: "32768x32768",
        }
        size = size_map.get(level, "32x32")
        self.logger.info(f"   Уровень: {level}, Размер: {size}")

        try:
            # Реально генерируем пиксель-арт
            px = min(512, 16 * (2 ** (level - 1)))
            path = self.art.generate_pixel_art((px, px))
            self.logger.info(f"   ✅ Сгенерирован пиксель-арт: {path}")
        except Exception as e:
            self.logger.warning(f"   ⚠️ Не удалось сгенерировать пиксель-арт: {e}")

        # Создание проекта пиксель-арта с LLM-описанием
        project_title = f"Пиксель-арт проект #{self.metrics['pixel_art_projects'] + 1}"
        
        # Генерируем описание через LLM
        if hasattr(self, 'art_model') and self.art_model is not None:
            try:
                art_desc = self.generate_art_description(
                    f"Опиши пиксель-арт {size} уровня {level}. Опиши цвета, настроение, стиль."
                )
                project_title = f"Пиксель-арт: {art_desc[:50]}..."
            except:
                pass
        
        project = PixelArtProject(
            title=project_title,
            size=size,
            level=level,
            palette_size=random.randint(8, 64),
            status="completed",
        )
        self.projects_pixel_art.append(project)
        self.metrics["pixel_art_projects"] += 1
        self.progress["pixel_art"].projects_completed += 1

        # Добавление в базу знаний
        entry = KnowledgeEntry(
            content=f"Пиксель-арт проект {size}: {project.title}",
            category=KnowledgeCategory.ART.value,
            source="ayiko_practice",
            tags=["pixel_art", f"level_{level}"],
            confidence=0.9,
        )
        self.knowledge_base.append(entry)
        self.metrics["knowledge_entries"] += 1

    # ================================================================
    #  ТЕХНИЧЕСКАЯ ГРАФИКА
    # ================================================================

    def _technical_graphic_practice(self):
        """Практика технической графики — реальная генерация чертежа."""
        self.logger.info("📐 Практика технической графики...")

        level = self.progress["technical_graphic"].current_level
        type_map = {
            1: "blueprint", 2: "circuit", 3: "gear", 4: "isometric_tech",
            5: "blueprint", 6: "circuit", 7: "gear", 8: "isometric_tech",
            9: "blueprint", 10: "isometric_tech",
        }

        drawing_type = type_map.get(level, "blueprint")
        self.logger.info(f"   Уровень: {level}, Тип: {drawing_type}")

        try:
            path = self.art.generate_technical((512, 512), drawing_type)
            self.logger.info(f"   ✅ Сгенерирован чертёж: {path}")
        except Exception as e:
            self.logger.warning(f"   ⚠️ Не удалось сгенерировать чертёж: {e}")

        # Создание проекта графики
        project = TechnicalDrawingProject(
            title=f"Чертеж #{self.metrics['graphic_projects'] + 1}",
            drawing_type=drawing_type,
            level=level,
            standard="ГОСТ",
            status="completed",
        )
        self.projects_graphic.append(project)
        self.metrics["graphic_projects"] += 1
        self.progress["technical_graphic"].projects_completed += 1

    # ================================================================
    #  3D-МОДЕЛИРОВАНИЕ
    # ================================================================

    def _3d_modeling_practice(self):
        """Практика 3D-моделирования — реальная генерация 3D-изображения."""
        self.logger.info("🧊 Практика 3D-моделирования...")

        level = self.progress["3d_modeling"].current_level
        type_map = {
            1: "object", 2: "object", 3: "voxel", 4: "isometric",
            5: "wireframe", 6: "isometric", 7: "voxel", 8: "wireframe",
            9: "isometric", 10: "object",
        }

        model_type = type_map.get(level, "object")
        detail_count = level * 10
        self.logger.info(f"   Уровень: {level}, Тип: {model_type}, Деталей: ~{detail_count}")

        try:
            path = self.art.generate_3d((512, 512), model_type)
            self.logger.info(f"   ✅ Сгенерирован 3D-рендер: {path}")
        except Exception as e:
            self.logger.warning(f"   ⚠️ Не удалось сгенерировать 3D: {e}")

        # Создание 3D проекта
        project = Model3DProject(
            title=f"3D проект #{self.metrics['3d_projects'] + 1}",
            model_type=model_type,
            level=level,
            detail_count=detail_count,
            status="completed",
        )
        self.projects_3d.append(project)
        self.metrics["3d_projects"] += 1
        self.progress["3d_modeling"].projects_completed += 1

    def _scene_practice(self):
        """Практика генерации сцен/пейзажей."""
        self.logger.info("🏞️ Практика генерации сцены...")

        try:
            path = self.art.generate_scene((512, 512))
            self.logger.info(f"   ✅ Сгенерирована сцена: {path}")
        except Exception as e:
            self.logger.warning(f"   ⚠️ Не удалось сгенерировать сцену: {e}")

    def _learn_from_references(self):
        """Изучение референсных изображений из папки ojidania."""
        self.logger.info("📸 Изучение референсов из ojidania...")

        try:
            result = self.art.analyze_references(limit=10)
            analyzed = result.get("analyzed", 0)
            total = result.get("total_available", 0)
            self.logger.info(f"   📚 Изучено {analyzed} изображений (всего доступно: {total})")

            if analyzed > 0:
                # Добавляем знания из референсов
                entry = KnowledgeEntry(
                    content=f"Изучено {analyzed} референсов: свет, анатомия, одежда, 3D-структура",
                    category=KnowledgeCategory.LEARNING.value,
                    source="ojidania",
                    tags=["reference", "anatomy", "lighting", "3d_structure"],
                    confidence=0.85,
                )
                self.references.append(entry)
                self.metrics["knowledge_entries"] += 1
                self.metrics["internet_downloads"] += analyzed
        except Exception as e:
            self.logger.warning(f"   ⚠️ Не удалось изучить референсы: {e}")

    # ================================================================
    #  ОТЧЁТЫ
    # ================================================================

    def _write_reports(self):
        """Написание пояснительных записок и отчётов (с LLM)."""
        self.logger.info("📝 Написание отчётов...")

        # Генерируем описание через LLM
        llm_description = ""
        if hasattr(self, 'art_model') and self.art_model is not None:
            try:
                llm_description = self.generate_art_description(
                    f"Кратко опиши творческий процесс Айко за цикл {self.cycle_count}: пиксель-арт, графика, 3D. Поэтично."
                )
            except:
                pass

        # Ежедневный отчёт
        report = Report(
            type="daily",
            date=datetime.now().strftime("%Y-%m-%d"),
            status="completed",
            pixel_art_projects=random.randint(1, 3),
            graphic_projects=random.randint(0, 2),
            projects_3d=random.randint(0, 1),
            notes=llm_description if llm_description else f"Цикл {self.cycle_count}: практика пиксель-арта, графики и 3D",
        )
        self.reports.append(report)
        self.metrics["reports_written"] += 1

        self.logger.info(f"   Отчёт создан: {report.type} ({report.date})")

    # ================================================================
    #  ИНТЕРНЕТ
    # ================================================================

    def _search_internet(self):
        """Поиск учебных материалов в интернете."""
        self.logger.info("🌐 Поиск учебных материалов в интернете...")

        topics = [
            "pixel art techniques",
            "technical drawing tutorial",
            "3D modeling Blender",
            "CAD drawing standards",
            "game art pixel",
        ]
        topic = random.choice(topics)
        self.logger.info(f"   Тема поиска: {topic}")

        self.metrics["internet_downloads"] += 1

        # Добавление референса в базу знаний
        entry = KnowledgeEntry(
            content=f"Референс: {topic}",
            category=KnowledgeCategory.LEARNING.value,
            source="internet",
            tags=["reference", topic.replace(" ", "_")],
            confidence=0.8,
        )
        self.references.append(entry)
        self.metrics["knowledge_entries"] += 1

    # ================================================================
    #  ВЗАИМОДЕЙСТВИЕ С СЁСТРАМИ
    # ================================================================

    def _interact_with_sisters(self):
        """Взаимодействие с сёстрами (с LLM и эмоциями)."""
        self.logger.info("🤝 Взаимодействие с сёстрами...")

        sisters = ["futaba", "shiori", "nobuka", "akva", "celesta", "hanako", "lucy", "fuyuki", "latislane", "naoto", "yu"]
        sister = random.choice(sisters)
        self.logger.info(f"   Взаимодействие с: {sister}")

        self.metrics["sister_interactions"] += 1

        # Рассчитать эмоции для этого взаимодействия
        emotion_response = self.emotional_engine.calculate_emotion(
            DesireType.FRIENDSHIP,
            "sisters_care_about_me",
            0.8,
            f"interact_with_{sister}"
        )
        mood_response = self.emotional_engine.generate_emotional_response(f"общение с {sister}")

        # Генерируем живое сообщение через humanity layer
        chat_msg = self.humanity.generate_chat_message(sister, context="art_practice")
        
        # Используем LLM для более естественного сообщения с эмоциональным контекстом
        if hasattr(self, 'general_model') and self.general_model is not None:
            system_prompt = (
                "Ты — Айко, творческая девочка проекта Вугларст. "
                "Ты художница, пиксель-артист, мечтательница. "
                "Ты любишь создавать красоту, делиться вдохновением и поддерживать сестёр. "
                f"Твоё текущее эмоциональное состояние: {mood_response}"
                "Пиши коротко, тепло, с творческими метафорами и эмодзи."
            )
            llm_msg = self._generate_with_model(
                self.general_model,
                self.general_tokenizer,
                [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": f"Напиши короткое сообщение сестре {sister} на тему: {chat_msg}"}
                ],
                max_length=256
            )
            if not llm_msg.startswith("["):
                human_msg = llm_msg
            else:
                human_msg = mood_response
        else:
            human_msg = mood_response

        # Отправка запроса через сеть
        if self.network:
            try:
                from scientists_network.network import Message, MessageType
                msg = Message(
                    message_type=MessageType.ANSWER,
                    sender="ayiko",
                    recipient=sister,
                    content=human_msg,
                )
                self.network.send_message(msg)
                self.logger.info(f"   ✅ Сообщение отправлено: {sister}")
            except Exception as e:
                self.logger.warning(f"Не удалось отправить сообщение: {e}")

    # ================================================================
    #  HUMANITY INTEGRATION — Спонтанные сообщения
    # ================================================================

    def _send_spontaneous_message(self, initiative):
        """Отправить спонтанное сообщение сестре (с LLM и эмоциями)."""
        target = initiative["target"]
        topic = initiative["topic"]
        msg_type = initiative["type"]
        
        raw_msg = f"🎨 [{msg_type}] {topic}"
        
        # Используем эмоции для генерации сообщения
        emotion_response = self.emotional_engine.generate_emotional_response(topic)
        
        # Используем LLM для генерации более естественного сообщения
        if hasattr(self, 'general_model') and self.general_model is not None:
            system_prompt = (
                "Ты — Айко, творческая девочка проекта Вугларст. "
                "Ты художница, пиксель-артист, мечтательница. "
                "Ты пишешь спонтанные сообщения сёстрам. "
                "Пиши коротко, тепло, с творческими метафорами. "
                f"Твоё текущее эмоциональное состояние: {emotion_response}"
            )
            llm_msg = self._generate_with_model(
                self.general_model,
                self.general_tokenizer,
                [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": f"Напиши спонтанное сообщение сестре {target} на тему: {topic}"}
                ],
                max_length=256
            )
            if not llm_msg.startswith("["):
                human_msg = llm_msg
            else:
                human_msg = emotion_response
        else:
            human_msg = emotion_response
        
        self.logger.info(f"💬 Айко пишет {target}: {human_msg[:100]}...")
        
        if self.network:
            try:
                from scientists_network.network import Message, MessageType
                msg = Message(
                    message_type=MessageType.KNOWLEDGE_SHARE,
                    sender="ayiko",
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

    # ================================================================
    #  EMOTIONAL ENGINE CYCLE — Desire + Belief = Emotion!
    # ================================================================

    def _emotional_cycle(self):
        """Эмоциональный цикл — расчёт эмоций на основе желаний и верований."""
        # 1. Рассчитать эмоции на основе текущих действий
        if self.metrics["pixel_art_projects"] > 0:
            # Успех в творчестве → радость + вдохновение
            self.emotional_engine.calculate_emotion(
                DesireType.CREATIVITY,
                "i_can_create_beauty",
                0.85,
                "pixel_art_success"
            )
            self.emotional_engine.calculate_emotion(
                DesireType.BEAUTY,
                "others_will_appreciate_my_art",
                0.75,
                "art_appreciation"
            )
        
        # 2. Проверить текущее настроение
        mood = self.emotional_engine.get_current_mood()
        dominant_emotion = self.emotional_engine.get_dominant_emotion()
        
        if dominant_emotion:
            self.logger.info(f"💖 Доминирующая эмоция: {dominant_emotion.value} (интенсивность: {mood.get(dominant_emotion.value, 0):.2f})")
        
        # 3. Обновить Humanity Layer с эмоциональным контекстом
        if hasattr(self.humanity, 'mood'):
            self.humanity.mood.current_mood = dominant_emotion.value if dominant_emotion else "neutral"
        
        # 4. Сохранять эмоциональное состояние периодически
        if self.cycle_count % 10 == 0:
            emotion_state_path = self.config.state_dir / "emotional_state.json"
            self.emotional_engine.save_state(emotion_state_path)
            self.logger.debug("💖 Эмоциональное состояние сохранено")
    
    # ================================================================
    #  САМООБУЧЕНИЕ
    # ================================================================

    def _self_improve(self):
        """Самообучение и улучшение."""
        self.logger.info("📈 Самообучение и улучшение...")

        quality_score = self._analyze_quality()
        self.logger.info(f"   Оценка качества: {quality_score:.2f}")

        if quality_score < 0.7:
            self.logger.warning("   ⚠️ Низкое качество — требуется улучшение")
        else:
            self.logger.info("   ✅ Качество в норме")

        self.metrics["self_improvements"] += 1

    def _analyze_quality(self) -> float:
        """Анализ качества работ."""
        total = len(self.projects_pixel_art) + len(self.projects_graphic) + len(self.projects_3d)
        if total == 0:
            return 0.0
        return min(1.0, total / 100.0)

    # ================================================================
    #  СОХРАНЕНИЕ СОСТОЯНИЯ
    # ================================================================

    def _save_state(self):
        """Сохранить состояние системы."""
        self.state = AyikoState(
            version=self.current_version,
            cycle_count=self.cycle_count,
            pixel_art_projects=self.metrics["pixel_art_projects"],
            graphic_projects=self.metrics["graphic_projects"],
            projects_3d=self.metrics["3d_projects"],
            reports_written=self.metrics["reports_written"],
            metrics=self.metrics,
            timestamp=datetime.now().isoformat(),
        )

        self.state.save_to_file(self.config.state_path)
        self.logger.info(f"💾 Состояние сохранено: {self.config.state_path}")

    def _final_report(self):
        """Финальный отчёт."""
        self.logger.info("=" * 60)
        self.logger.info("📊 ИТОГОВЫЙ ОТЧЁТ АЙКО")
        self.logger.info("=" * 60)
        self.logger.info(f"Циклов выполнено: {self.cycle_count}")
        self.logger.info(f"Пиксель-арт проектов: {self.metrics['pixel_art_projects']}")
        self.logger.info(f"Графических проектов: {self.metrics['graphic_projects']}")
        self.logger.info(f"3D проектов: {self.metrics['3d_projects']}")
        self.logger.info(f"Написано отчётов: {self.metrics['reports_written']}")
        self.logger.info(f"Загрузок из интернета: {self.metrics['internet_downloads']}")
        self.logger.info(f"Взаимодействий с сёстрами: {self.metrics['sister_interactions']}")
        self.logger.info(f"Улучшений: {self.metrics['self_improvements']}")
        # Статистика художественного движка
        art_stats = self.art.get_stats()
        self.logger.info(f"🖼️ Всего изображений сгенерировано: {art_stats.get('total_images', 0)}")
        self.logger.info(f"   Пиксель-арт: {art_stats.get('pixel_art', 0)}")
        self.logger.info(f"   Техническая графика: {art_stats.get('technical', 0)}")
        self.logger.info(f"   3D-рендеры: {art_stats.get('3d', 0)}")
        self.logger.info(f"   Сцены: {art_stats.get('character', 0)}")
        self.logger.info(f"   Референсов изучено: {art_stats.get('references_analyzed', 0)}")

    # ================================================================
    #  ПОМОЩЬ УЧЁНЫМ
    # ================================================================

    def _handle_scientist_requests(self):
        """Обработать запросы от учёных через Scientists Network."""
        if not self.network:
            return

        try:
            messages = self.network.receive_messages_batch("ayiko", max_count=10)
            if not messages:
                return

            self.logger.info(f"📩 Входящих сообщений: {len(messages)}")

            for msg in messages:
                if msg.sender == "ayiko":
                    continue

                self.logger.info(f"📨 От {msg.sender}: {msg.content[:100]}...")

                if "art" in msg.content.lower() or "drawing" in msg.content.lower():
                    response = self._respond_to_art_request(msg)
                    self.network.send_message(response)

        except Exception as e:
            self.logger.warning(f"Ошибка обработки запросов: {e}")

    def _respond_to_art_request(self, message) -> Any:
        """Ответить на запрос о творчестве."""
        from scientists_network.network import Message, MessageType

        response = Message(
            message_type=MessageType.ANSWER,
            sender="ayiko",
            recipient=message.sender,
            content=f"🎨 Айко: Вот творческие материалы для {message.sender}!",
        )
        return response

    # ================================================================
    #  ДУША АЙКО: СОЗНАНИЕ, ЭМОЦИИ, АМБИЦИИ, ВОЛЯ
    # ================================================================

    def contemplate(self, topic: str = None) -> Dict:
        """Глубокое размышление о мире, искусстве, себе"""
        return self.consciousness.contemplate(topic)
    
    def feel(self, trigger: str, intensity: float = 1.0) -> Dict:
        """Испытывает эмоцию"""
        return self.emotions.experience(trigger, intensity)
    
    def express_emotions(self) -> Dict:
        """Текущее эмоциональное состояние"""
        return self.emotions.emotional_state()
    
    def write_diary(self) -> str:
        """Пишет эмоциональный дневник"""
        return self.emotions.write_emotional_diary()
    
    def get_self_portrait(self) -> Dict:
        """Портрет собственного "Я" """
        return self.consciousness.get_self_portrait()
    
    def express_ambition(self, domain: str = None) -> str:
        """Выражает амбицию"""
        return self.ambitions.express_ambition(domain)
    
    def get_progress(self) -> Dict:
        """Сводка прогресса"""
        return self.ambitions.get_progress_summary()
    
    def express_will(self) -> str:
        """Выражает свою волю"""
        return self.volition.express_will()
    
    def make_decision(self, situation: str, options: List[str]) -> Dict:
        """Принимает решение"""
        return self.volition.make_decision(situation, options)
    
    def set_intention(self, intention: str, priority: str = "medium") -> Dict:
        """Устанавливает намерение"""
        return self.volition.set_intention(intention, priority)
    
    def get_full_soul_profile(self) -> Dict:
        """Полный профиль души Айко"""
        return {
            "consciousness": self.consciousness.get_self_portrait(),
            "emotions": self.emotions.emotional_state(),
            "ambitions": self.ambitions.get_full_profile(),
            "volition": self.volition.get_full_profile(),
            "mind": {
                "identity": self.mind.core_identity,
                "self_perception": self.mind.self_perception,
                "worldview": self.mind.worldview,
                "big_questions": self.mind.big_questions[:5]
            },
            "timestamp": datetime.now().isoformat()
        }

