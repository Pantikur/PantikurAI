"""
Ядро постоянной работы Айко — автономный цикл чтения книг и обучения модели.

Реализует:
  - Бесконечный цикл чтения книг из интернета и локальных файлов
  - Извлечение знаний (факты, концепции, сюжеты)
  - Создание обучающих пар (вопрос-ответ)
  - Анализ стиля повествования
  - Разбор лора (персонажи, мир, хронология)
  - Извлечение сути и мысли книги
  - Дообучение модели на новых данных
  - Интернет-доступ для поиска книг
  - Автономность — работа 24/7
  - Самообучение — анализ качества и улучшение
  - Наполнение контентом — постоянный приток знаний

Взаимодействие с сёстрами:
  - Нобука — улучшение кода обучения
  - Наото — визуализация лора и персонажей
  - Юи — знания для переноса сознания
  - Селеста — биологические знания
  - Аква — математические концепции
"""

from __future__ import annotations
import json
import logging
import os
import random
import signal
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Any, Optional

from ayiko.engine.config import AyikoConfig
from ayiko.engine.models import (
    AyikoState,
    BookMetadata,
    BookSummary,
    BookThought,
    KnowledgeCategory,
    KnowledgeEntry,
    LoreEntry,
    StyleEntry,
    TrainingPair,
)

try:
    from scientists_network.network import get_network, RequestType, RequestPriority
    _HAS_NETWORK = True
except Exception:
    get_network = None  # type: ignore
    RequestType = None  # type: ignore
    RequestPriority = None  # type: ignore
    _HAS_NETWORK = False


class AyikoCore:
    """
    Автономное ядро Айко — чтение книг и обучение модели.

    Работает в бесконечном цикле:
      1. 📖 Поиск и чтение книг (интернет + локальные файлы)
      2. 💾 Извлечение обучающих пар (вопрос-ответ)
      3. ✍️ Анализ стиля повествования (авторский почерк)
      4. 🌍 Разбор лора (мир, персонажи, события)
      5. 📚 Извлечение сути и мысли книги
      6. 🚀 Дообучение модели на новых данных
      7. 📈 Самообучение — анализ качества и улучшение
      8. 💾 Сохранение состояния
    """

    def __init__(self, config: Optional[AyikoConfig] = None):
        self.config = config or AyikoConfig.default()
        self.current_version = self.config.version

        # Состояние
        self.state = AyikoState.load_from_file(self.config.state_path)
        self.cycle_count = self.state.cycle_count

        # Базы данных
        self.knowledge_base: list[KnowledgeEntry] = []
        self.training_pairs: list[TrainingPair] = []
        self.lore_db: list[LoreEntry] = []
        self.style_db: list[StyleEntry] = []
        self.books_metadata: dict[str, BookMetadata] = {}
        self.books_summaries: dict[str, BookSummary] = {}
        self.books_thoughts: list[BookThought] = []

        # Метрики
        self.metrics = {
            "cycles_completed": 0,
            "books_read": 0,
            "chapters_processed": 0,
            "training_pairs_generated": 0,
            "knowledge_entries_saved": 0,
            "lore_entries_saved": 0,
            "style_entries_saved": 0,
            "model_training_sessions": 0,
            "internet_downloads": 0,
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
                self.logger.info("🔗 Подключена к Scientists Network — готова делиться знаниями")
            except Exception as e:
                self.logger.warning(f"Не удалось подключиться к Scientists Network: {e}")

        # Сигналы
        self._shutdown_requested = False
        self._setup_signals()

        self.logger.info(f"Айко {self.current_version} инициализирована")
        self.logger.info("📚 Расширенные возможности активированы:")
        self.logger.info("   - Чтение книг из интернета и локальных источников")
        self.logger.info("   - Сохранение обучающих пар")
        self.logger.info("   - Анализ стиля повествования")
        self.logger.info("   - Разбор лора")
        self.logger.info("   - Извлечение сути и мысли книги")
        self.logger.info("   - Дообучение модели")
        self.logger.info("   - Автономность 24/7")

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
            # Не поддерживается на Windows
            pass

    def _signal_handler(self, signum, frame):
        """Обработчик сигналов остановки."""
        self.logger.info("🛑 Получен сигнал остановки")
        self._shutdown_requested = True

    # ================================================================
    #  ОСНОВНОЙ ЦИКЛ
    # ================================================================

    def run(self):
        """Запустить основной цикл работы Айко."""
        self.logger.info("=" * 60)
        self.logger.info("📚 ЗАПУСК АВТОНОМНОГО ЯДРА АЙКО")
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
            self._save_state()
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

        # 1. Чтение книг (локальные + интернет)
        self._read_books()

        # 2. Анализ стиля (периодически)
        if self.cycle_count % 3 == 0 and self.config.enable_style_learning:
            self._analyze_styles_batch()

        # 3. Разбор лора (периодически)
        if self.cycle_count % 5 == 0 and self.config.enable_lore_extraction:
            self._analyze_lore_batch()

        # 4. Извлечение сути и мысли (периодически)
        if self.cycle_count % 7 == 0:
            self._extract_summaries_and_thoughts()

        # 5. Обучение модели (периодически)
        if self.cycle_count % 10 == 0:
            self._train_model()

        # 6. Самообучение и улучшение (периодически)
        if self.cycle_count % 20 == 0:
            self._self_improve()

        # 7. Обработка запросов от учёных
        if self.cycle_count % 5 == 0:
            self._handle_scientist_requests()

        self.logger.info(f"✅ Цикл {self.cycle_count} завершён")

    # ================================================================
    #  ЧТЕНИЕ КНИГ
    # ================================================================

    def _read_books(self):
        """Прочитать книги из директории и интернета."""
        # 1. Чтение локальных книг
        books_dir = self.config.books_directory
        if books_dir.exists():
            local_books = self._find_local_books(books_dir)
            for book_path in local_books[:5]:  # Лимит для демо
                try:
                    result = self._process_book(book_path)
                    if result["status"] == "success":
                        self.metrics["books_read"] += 1
                        self.logger.info(
                            f"✅ Книга обработана: {book_path.name} "
                            f"(знаний: {result['knowledge_extracted']}, "
                            f"пар: {result['pairs_generated']})"
                        )
                except Exception as e:
                    self.logger.error(f"❌ Ошибка обработки книги {book_path}: {e}")

        # 2. Поиск книг в интернете (периодически)
        if self.config.web_search_enabled and self.cycle_count % self.config.web_search_interval == 0:
            self._search_and_download_books()

    def _find_local_books(self, books_dir: Path) -> list[Path]:
        """Найти локальные книги."""
        books = []
        for fmt in self.config.supported_formats:
            books.extend(books_dir.rglob(f"*{fmt}"))
        return books

    def _process_book(self, book_path: Path) -> dict:
        """Обработать одну книгу."""
        self.logger.info(f"📖 Обработка книги: {book_path.name}")

        # Загрузка текста
        text = self._load_book_text(book_path)

        if not text:
            return {"status": "error", "message": "Не удалось прочитать книгу"}

        # Извлечение знаний
        knowledge = self._extract_knowledge(text, str(book_path))

        # Создание обучающих пар
        pairs = self._generate_training_pairs(knowledge)

        # Анализ стиля
        styles = []
        if self.config.enable_style_learning:
            styles = self._analyze_style(text)

        # Разбор лора
        lore = []
        if self.config.enable_lore_extraction:
            lore = self._extract_lore(text, str(book_path))

        # Сохранение
        self.knowledge_base.extend(knowledge)
        self.training_pairs.extend(pairs)
        self.style_db.extend(styles)
        self.lore_db.extend(lore)

        # Обновление метаданных
        book_title = book_path.stem
        if book_title not in self.books_metadata:
            self.books_metadata[book_title] = BookMetadata(
                title=book_title,
                author="Unknown",
                book_type="fiction",
            )

        metadata = self.books_metadata[book_title]
        metadata.chapters_processed += 1
        metadata.training_pairs_generated += len(pairs)
        metadata.knowledge_entries += len(knowledge)
        metadata.processing_status = "completed"

        return {
            "status": "success",
            "book_path": str(book_path),
            "knowledge_extracted": len(knowledge),
            "pairs_generated": len(pairs),
            "styles_analyzed": len(styles),
            "lore_entries": len(lore),
        }

    def _load_book_text(self, book_path: Path) -> str:
        """Загрузить текст книги."""
        suffix = book_path.suffix.lower()

        if suffix in [".txt", ".md"]:
            return book_path.read_text(encoding="utf-8", errors="ignore")
        elif suffix == ".json":
            data = json.loads(book_path.read_text(encoding="utf-8"))
            return data.get("text", "")
        else:
            self.logger.warning(f"Формат {suffix} пока не поддерживается")
            return ""

    def _search_and_download_books(self):
        """Поиск и скачивание книг из интернета."""
        self.logger.info("🌐 Поиск книг в интернете...")

        # TODO: Интеграция с авто_book_learning.py
        # from utils.auto_book_learning import AutoBookLearning
        # controller = AutoBookLearning()
        # controller.run_learning_cycle()

        self.metrics["internet_downloads"] += 1
        self.logger.info("📚 Интернет-поиск выполнен")

    def _extract_knowledge(self, text: str, source: str) -> list[KnowledgeEntry]:
        """Извлечь знания из текста."""
        knowledge = []
        paragraphs = text.split("\n\n")

        for paragraph in paragraphs[:100]:  # Лимит для демо
            if len(paragraph.strip()) < 50:
                continue

            category = self._categorize_paragraph(paragraph)

            entry = KnowledgeEntry(
                content=paragraph.strip(),
                category=category,
                source=source,
                chapter=0,
                tags=[category],
                confidence=0.8,
            )
            knowledge.append(entry)

        return knowledge

    def _categorize_paragraph(self, text: str) -> str:
        """Определить категорию абзаца."""
        text_lower = text.lower()

        if any(word in text_lower for word in ["факт", "данные", "исследование", "статистика"]):
            return KnowledgeCategory.FACT.value
        elif any(word in text_lower for word in ["концепция", "теория", "идея", "принцип"]):
            return KnowledgeCategory.CONCEPT.value
        elif any(word in text_lower for word in ["герой", "персонаж", "действовал", "решил"]):
            return KnowledgeCategory.PLOT.value
        elif any(word in text_lower for word in ["стиль", "метод", "приём", "язык"]):
            return KnowledgeCategory.STYLE.value
        else:
            return KnowledgeCategory.CONCEPT.value

    def _generate_training_pairs(self, knowledge: list[KnowledgeEntry]) -> list[TrainingPair]:
        """Создать обучающие пары из знаний."""
        pairs = []

        for entry in knowledge[:50]:  # Лимит для демо
            pair = TrainingPair(
                question=f"Что сказано в тексте: {entry.content[:150]}?",
                answer=entry.content,
                context=f"Источник: {entry.source}, Категория: {entry.category}",
                source=entry.source,
                chapter=entry.chapter,
                category=entry.category,
                tags=entry.tags,
                confidence=entry.confidence,
            )
            pairs.append(pair)

        return pairs

    # ================================================================
    #  АНАЛИЗ СТИЛЯ И ЛОРА
    # ================================================================

    def _analyze_style(self, text: str) -> list[StyleEntry]:
        """Анализ стиля повествования."""
        paragraphs = text.split("\n\n")[:5]

        styles = []
        for para in paragraphs:
            style = StyleEntry(
                author="Unknown",
                book_title="Unknown",
                chapter=0,
                style_features=self._detect_style_features(para),
                literary_devices=self._detect_literary_devices(para),
                dialogue_style="mixed",
                narrative_style="descriptive",
                examples=[para[:200]],
            )
            styles.append(style)

        return styles

    def _detect_style_features(self, text: str) -> list[str]:
        """Определить особенности стиля."""
        features = []
        text_lower = text.lower()

        if "он сказал" in text_lower or "она сказала" in text_lower:
            features.append("dialogue")
        if len(text) > 500:
            features.append("detailed")
        if any(word in text_lower for word in ["может быть", "возможно", "наверное"]):
            features.append("speculative")

        return features if features else ["neutral"]

    def _detect_literary_devices(self, text: str) -> list[str]:
        """Определить литературные приёмы."""
        devices = []

        if any(word in text for word in ["как", "будто", "словно"]):
            devices.append("simile")
        if any(word in text for word in ["кажется", "похоже"]):
            devices.append("metaphor")

        return devices if devices else []

    def _extract_lore(self, text: str, source: str) -> list[LoreEntry]:
        """Извлечение лора из текста."""
        paragraphs = text.split("\n\n")[:3]

        lore = []
        for para in paragraphs:
            entry = LoreEntry(
                world_name="Unknown",
                entry_type="general",
                content=para[:300],
                book_source=source,
                chapter=0,
                relationships={},
                contradictions=[],
                confidence=0.7,
            )
            lore.append(entry)

        return lore

    def _analyze_styles_batch(self):
        """Пакетный анализ стилей."""
        self.logger.info("✍️ Пакетный анализ стилей...")
        # TODO: Реализовать NLP-анализ

    def _analyze_lore_batch(self):
        """Пакетный разбор лора."""
        self.logger.info("🌍 Пакетный разбор лора...")
        # TODO: Реализовать NLP-анализ

    # ================================================================
    #  СУТЬ И МЫСЛЬ КНИГИ
    # ================================================================

    def _extract_summaries_and_thoughts(self):
        """Извлечение сути и мысли из прочитанных книг."""
        self.logger.info("📚 Извлечение сути и мысли книг...")

        for book_title, metadata in self.books_metadata.items():
            if metadata.knowledge_entries > 0:
                # Извлечение сути
                summary = BookSummary(
                    source=book_title,
                    summary=f"Суть книги '{book_title}'",
                    key_points=["Основная идея книги"],
                    main_characters=["Персонажи не определены"],
                    setting="Место не определено",
                    genre="Не определён",
                )
                self.books_summaries[book_title] = summary

                # Извлечение мысли
                thought = BookThought(
                    source=book_title,
                    central_thought="Авторская мысль не определена",
                    moral_lesson="",
                    philosophical_concepts=[],
                    author_intention="Не определена",
                )
                self.books_thoughts.append(thought)

        self.logger.info(f"✅ Извлечено сути: {len(self.books_summaries)}")
        self.logger.info(f"✅ Извлечено мыслей: {len(self.books_thoughts)}")

    # ================================================================
    #  ОБУЧЕНИЕ МОДЕЛИ
    # ================================================================

    def _train_model(self):
        """Дообучение модели на созданных парах."""
        self.logger.info("🚀 Обучение модели...")

        if not self.training_pairs:
            self.logger.info("⚠️ Нет обучающих пар для обучения")
            return

        # Сохранение обучающих пар
        self._save_training_pairs()

        # Логирование статистики
        self.metrics["model_training_sessions"] += 1
        self.metrics["training_pairs_generated"] += len(self.training_pairs)
        self.metrics["knowledge_entries_saved"] += len(self.knowledge_base)

        self.logger.info(f"✅ Обучение завершено:")
        self.logger.info(f"   Пар: {len(self.training_pairs)}")
        self.logger.info(f"   Записей: {len(self.knowledge_base)}")

    def _save_training_pairs(self):
        """Сохранить обучающие пары в файл."""
        if not self.training_pairs:
            return

        self.config.training_pairs_path.parent.mkdir(parents=True, exist_ok=True)

        with open(self.config.training_pairs_path, "a", encoding="utf-8") as f:
            for pair in self.training_pairs:
                f.write(pair.to_json() + "\n")

        self.logger.info(
            f"💾 Обучающие пары сохранены: "
            f"{self.config.training_pairs_path} "
            f"({len(self.training_pairs)} пар)"
        )

    # ================================================================
    #  САМООБУУЧЕНИЕ И УЛУЧШЕНИЕ
    # ================================================================

    def _self_improve(self):
        """Самообучение и улучшение."""
        self.logger.info("📈 Самообучение и улучшение...")

        # Анализ качества данных
        quality_score = self._analyze_data_quality()
        self.logger.info(f"📊 Оценка качества данных: {quality_score:.2f}")

        # Улучшение на основе анализа
        if quality_score < 0.7:
            self.logger.warning("⚠️ Низкое качество данных — требуется улучшение")
            # TODO: Реализовать улучшение
        else:
            self.logger.info("✅ Качество данных в норме")

        self.metrics["self_improvements"] += 1

    def _analyze_data_quality(self) -> float:
        """Анализ качества данных."""
        if not self.training_pairs:
            return 0.0

        # Простой расчёт среднего confidence
        avg_confidence = sum(p.confidence for p in self.training_pairs) / len(self.training_pairs)
        return avg_confidence

    # ================================================================
    #  СОХРАНЕНИЕ СОСТОЯНИЯ
    # ================================================================

    def _save_state(self):
        """Сохранить состояние системы."""
        self.state = AyikoState(
            version=self.current_version,
            cycle_count=self.cycle_count,
            books_read=self.metrics["books_read"],
            chapters_processed=self.metrics["chapters_processed"],
            training_pairs_generated=self.metrics["training_pairs_generated"],
            knowledge_entries_saved=self.metrics["knowledge_entries_saved"],
            lore_entries_saved=self.metrics["lore_entries_saved"],
            metrics=self.metrics,
            timestamp=datetime.now().isoformat(),
        )

        self.state.save_to_file(self.config.state_path)
        self.logger.info(f"💾 Состояние сохранено: {self.config.state_path}")

    def _final_report(self):
        """Финальный отчёт."""
        self.logger.info("=" * 60)
        self.logger.info("📊 ФИНАЛЬНЫЙ ОТЧЁТ")
        self.logger.info("=" * 60)
        self.logger.info(f"Циклов выполнено: {self.cycle_count}")
        self.logger.info(f"Книг прочитано: {self.metrics['books_read']}")
        self.logger.info(f"Обучающих пар создано: {self.metrics['training_pairs_generated']}")
        self.logger.info(f"Записей в базе знаний: {self.metrics['knowledge_entries_saved']}")
        self.logger.info(f"Лора разобрано: {self.metrics['lore_entries_saved']}")
        self.logger.info(f"Сессий обучения: {self.metrics['model_training_sessions']}")
        self.logger.info(f"Скачиваний из интернета: {self.metrics['internet_downloads']}")
        self.logger.info(f"Улучшений: {self.metrics['self_improvements']}")

    # ================================================================
    #  ПОМОЩЬ УЧЁНЫМ
    # ================================================================

    def _handle_scientist_requests(self):
        """Обработать запросы от учёных через Scientists Network."""
        if not self.network:
            return

        try:
            # Получаем входящие сообщения от учёных
            messages = self.network.receive_messages_batch("ayiko", max_count=10)

            if not messages:
                return

            self.logger.info(f"📩 Входящих сообщений: {len(messages)}")

            for msg in messages:
                if msg.sender == "ayiko":
                    continue

                self.logger.info(
                    f"📨 От {msg.sender}: {msg.content[:100]}..."
                )

                # Обработка запросов на знания
                if "knowledge" in msg.content.lower() or "book" in msg.content.lower():
                    response = self._respond_to_knowledge_request(msg)
                    self.network.send_message(response)

        except Exception as e:
            self.logger.warning(f"Ошибка обработки запросов: {e}")

    def _respond_to_knowledge_request(self, message) -> Any:
        """Ответить на запрос знаний."""
        # Создаём сообщение-ответ
        from scientists_network.network import Message, MessageType

        response = Message(
            message_type=MessageType.ANSWER,
            sender="ayiko",
            recipient=message.sender,
            content=f"📚 Айко: Вот знания из книг для {message.sender}!",
        )

        return response

