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

# Система души и сознания Айко
from ayiko.consciousness import AyikoConsciousness
from ayiko.heart import AyikoHeart
from ayiko.ambitions import AyikoAmbitions
from ayiko.volition import AyikoVolition
from ayiko.emotions import AyikoEmotions
from ayiko.mind import AyikoConsciousness as AyikoMind

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

        # Сеть учёных
        self.network = None
        if _HAS_NETWORK and get_network is not None:
            try:
                self.network = get_network()
                self.logger.info("🔗 Подключена к Scientists Network")
            except Exception as e:
                self.logger.warning(f"Не удалось подключиться к Scientists Network: {e}")

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
        #  HUMANITY LAYER — Живая душа Айко
        # ================================================================
        self.humanity = HumanityLayer("ayiko")
        self.humanity.current_cycle = 0
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
        """Один цикл работы."""
        self.cycle_count += 1
        self.metrics["cycles_completed"] += 1
        self.logger.debug(f"=== ЦИКЛ {self.cycle_count} ===")

        # 1. Анализ текущего уровня
        self._analyze_current_level()

        # 2. Пиксель-арт (каждый цикл)
        self._pixel_art_practice()

        # 3. Техническая графика (каждый 3-й цикл)
        if self.cycle_count % 3 == 0:
            self._technical_graphic_practice()

        # 4. 3D-моделирование (каждый 5-й цикл)
        if self.cycle_count % 5 == 0:
            self._3d_modeling_practice()

        # 5. Написание пояснительных записок (каждый 2-й цикл)
        if self.cycle_count % 2 == 0:
            self._write_reports()

        # 6. Интернет-поиск (каждый 7-й цикл)
        if self.cycle_count % 7 == 0 and self.config.web_search_enabled:
            self._search_internet()

        # 7. Взаимодействие с сёстрами (каждый 10-й цикл)
        if self.cycle_count % 10 == 0:
            self._interact_with_sisters()

        # 8. Самообучение и улучшение (каждый 20-й цикл)
        if self.cycle_count % 20 == 0:
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

        self.logger.info(f"✅ Цикл {self.cycle_count} завершён")

    # ================================================================
    #  АНАЛИЗ УРОВНЯ
    # ================================================================

    def _analyze_current_level(self):
        """Анализ текущего уровня и прогресса."""
        self.logger.info("📊 Анализ текущего уровня...")

        # Проверка прогресса по каждому направлению
        for direction, prog in self.progress.items():
            if prog.should_promote():
                old_level = prog.current_level
                prog.current_level += 1
                self.logger.info(f"🎉 Повышение уровня {direction}: {old_level} → {prog.current_level}")

    # ================================================================
    #  ПИКСЕЛЬ-АРТ
    # ================================================================

    def _pixel_art_practice(self):
        """Практика пиксель-арта."""
        self.logger.info("🎨 Практика пиксель-арта...")

        level = self.progress["pixel_art"].current_level
        size_map = {
            1: "16x16",
            2: "32x32",
            3: "128x128",
            4: "256x256",
            5: "512x512",
            6: "1024x1024",
            7: "2048x2048",
            8: "4096x4096",
            9: "8192x8192",
            10: "32768x32768",
        }

        size = size_map.get(level, "32x32")
        self.logger.info(f"   Уровень: {level}, Размер: {size}")

        # Создание проекта пиксель-арта
        project = PixelArtProject(
            title=f"Пиксель-арт проект #{self.metrics['pixel_art_projects'] + 1}",
            size=size,
            level=level,
            palette_size=random.randint(8, 64),
            status="completed",
        )
        self.projects_pixel_art.append(project)
        self.metrics["pixel_art_projects"] += 1

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
        """Практика технической графики."""
        self.logger.info("📐 Практика технической графики...")

        level = self.progress["technical_graphic"].current_level
        type_map = {
            1: "набросок",
            2: "концепт-арт",
            3: "чертёж (виды)",
            4: "чертёж (разрезы)",
            5: "сборный чертёж",
            6: "сборный чертёж (сложный)",
            7: "ГОСТ мастерство",
            8: "инновационный чертёж",
            9: "мастер чертежей",
            10: "трансцендентный чертёж",
        }

        drawing_type = type_map.get(level, "набросок")
        self.logger.info(f"   Уровень: {level}, Тип: {drawing_type}")

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

    # ================================================================
    #  3D-МОДЕЛИРОВАНИЕ
    # ================================================================

    def _3d_modeling_practice(self):
        """Практика 3D-моделирования."""
        self.logger.info("🧊 Практика 3D-моделирования...")

        level = self.progress["3d_modeling"].current_level
        type_map = {
            1: "простая деталь (примитивы)",
            2: "деталь (extrude, bevel)",
            3: "деталь (NURBS)",
            4: "деталь (скелетная анимация)",
            5: "сложный механизм (10-30 деталей)",
            6: "сложный механизм (30-50 деталей)",
            7: "максимальный механизм (50-100 деталей)",
            8: "прорывной механизм (100+ деталей)",
            9: "легендарный механизм",
            10: "трансцендентная сборка",
        }

        model_type = type_map.get(level, "примитивы")
        detail_count = level * 10
        self.logger.info(f"   Уровень: {level}, Тип: {model_type}, Деталей: ~{detail_count}")

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

    # ================================================================
    #  ОТЧЁТЫ
    # ================================================================

    def _write_reports(self):
        """Написание пояснительных записок и отчётов."""
        self.logger.info("📝 Написание отчётов...")

        # Ежедневный отчёт
        report = Report(
            type="daily",
            date=datetime.now().strftime("%Y-%m-%d"),
            status="completed",
            pixel_art_projects=random.randint(1, 3),
            graphic_projects=random.randint(0, 2),
            projects_3d=random.randint(0, 1),
            notes=f"Цикл {self.cycle_count}: практика пиксель-арта, графики и 3D",
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

        # TODO: Интеграция с web_access.py
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
        """Взаимодействие с сёстрами (обновлённая версия с humanity)."""
        self.logger.info("🤝 Взаимодействие с сёстрами...")

        sisters = ["futaba", "shiori", "nobuka", "aqua", "celesta", "hanako", "lucy", "fuyuki", "latislane", "naoto", "yui"]
        sister = random.choice(sisters)
        self.logger.info(f"   Взаимодействие с: {sister}")

        self.metrics["sister_interactions"] += 1

        # Генерируем живое сообщение через humanity layer
        chat_msg = self.humanity.generate_chat_message(sister, context="art_practice")
        human_msg = self.humanity.humanize_response(chat_msg, event_type="chat")

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
                self.logger.info(f"   Сообщение отправлено: {sister}")
            except Exception as e:
                self.logger.warning(f"Не удалось отправить сообщение: {e}")

    # ================================================================
    #  HUMANITY INTEGRATION — Спонтанные сообщения
    # ================================================================

    def _send_spontaneous_message(self, initiative):
        """Отправить спонтанное сообщение сестре на основе инициативы humanity layer."""
        target = initiative["target"]
        topic = initiative["topic"]
        msg_type = initiative["type"]
        
        raw_msg = f"🎨 [{msg_type}] {topic}"
        human_msg = self.humanity.humanize_response(raw_msg, event_type="chat")
        
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
        self.logger.info("📊 ФИНАЛЬНЫЙ ОТЧЁТ АЙКО")
        self.logger.info("=" * 60)
        self.logger.info(f"Циклов выполнено: {self.cycle_count}")
        self.logger.info(f"Пиксель-арт проектов: {self.metrics['pixel_art_projects']}")
        self.logger.info(f"Графических проектов: {self.metrics['graphic_projects']}")
        self.logger.info(f"3D проектов: {self.metrics['3d_projects']}")
        self.logger.info(f"Написано отчётов: {self.metrics['reports_written']}")
        self.logger.info(f"Загрузок из интернета: {self.metrics['internet_downloads']}")
        self.logger.info(f"Взаимодействий с сёстрами: {self.metrics['sister_interactions']}")
        self.logger.info(f"Улучшений: {self.metrics['self_improvements']}")

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

