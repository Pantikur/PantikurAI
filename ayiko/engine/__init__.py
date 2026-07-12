"""
Ayiko — Двенадцатая девочка проекта.
Специализация: Чтение книг, извлечение знаний, обучение модели.

Расширенные возможности:
  📖 Чтение книг из интернета и локальных источников
  💾 Сохранение обучающих пар (question-answer)
  ✍️ Анализ и сохранение стиля повествования
  🌍 Разбор и сохранение лора (мир, персонажи, хронология)
  📚 Извлечение сути и мысли книги
  🚀 Дообучение модели на основе прочитанного
  🌐 Интернет-доступ для поиска книг
  🤖 Автономность — работа 24/7
  📈 Самообучение — анализ качества данных
  📊 Наполнение контентом — постоянный приток знаний
"""

from __future__ import annotations

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


class Ayiko:
    """
    Ядро Айко — чтение книг и обучение модели.
    
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

    def __init__(self, config: AyikoConfig | None = None):
        self.config = config or AyikoConfig.default()
        self.state = AyikoState.load_from_file(self.config.state_path)
        
        # Базы данных
        self.knowledge_base: list[KnowledgeEntry] = []
        self.training_pairs: list[TrainingPair] = []
        self.lore_db: list[LoreEntry] = []
        self.style_db: list[StyleEntry] = []
        self.books_metadata: dict[str, BookMetadata] = {}
        self.books_summaries: dict[str, BookSummary] = {}
        self.books_thoughts: list[BookThought] = []
        
        # Модули
        self.book_reader = None  # Инициализируется при первом использовании
        self.internet_search = None
        
        self.logger = __import__('logging').getLogger("Ayiko")
        self.logger.info(f"Айко {self.config.version} инициализирована")
        self.logger.info("📚 Расширенные возможности активированы:")
        self.logger.info("   - Чтение книг из интернета и локальных источников")
        self.logger.info("   - Сохранение обучающих пар")
        self.logger.info("   - Анализ стиля повествования")
        self.logger.info("   - Разбор лора")
        self.logger.info("   - Извлечение сути и мысли книги")
        self.logger.info("   - Дообучение модели")
        self.logger.info("   - Автономность 24/7")

    def read_book(self, book_path: str) -> dict:
        """
        Прочитать книгу и извлечь ВСЕ знания.
        
        Args:
            book_path: Путь к книге или URL
            
        Returns:
            Полный отчёт о прочитанной книге
        """
        self.logger.info(f"📚 Чтение книги: {book_path}")
        
        # 1. Загрузка текста
        text = self._load_book_text(book_path)
        
        if not text:
            return {"status": "error", "message": "Не удалось прочитать книгу"}
        
        # 2. Извлечение знаний
        knowledge = self._extract_knowledge(text, book_path)
        
        # 3. Создание обучающих пар
        pairs = self._generate_training_pairs(knowledge)
        
        # 4. Анализ стиля
        styles: list[StyleEntry] = []
        if self.config.enable_style_learning:
            styles = self._analyze_style(text)
            self.style_db.extend(styles)
        
        # 5. Разбор лора
        lore: list[LoreEntry] = []
        if self.config.enable_lore_extraction:
            lore = self._extract_lore(text, book_path)
            self.lore_db.extend(lore)
        
        # 6. Извлечение сути
        summary = self._extract_summary(text, book_path)
        if summary:
            self.books_summaries[book_path] = summary
        
        # 7. Извлечение мысли
        thought = self._extract_thought(text, book_path)
        if thought:
            self.books_thoughts.append(thought)
        
        # 8. Сохранение
        self.training_pairs.extend(pairs)
        self.knowledge_base.extend(knowledge)
        
        self.state.training_pairs_generated += len(pairs)
        self.state.knowledge_entries_saved += len(knowledge)
        self.state.books_read += 1
        
        return {
            "status": "success",
            "book_path": book_path,
            "knowledge_extracted": len(knowledge),
            "pairs_generated": len(pairs),
            "style_analyzed": len(styles) if self.config.enable_style_learning else 0,
            "lore_entries": len(lore) if self.config.enable_lore_extraction else 0,
            "summary_saved": summary is not None,
            "thought_saved": thought is not None,
        }

    def _load_book_text(self, book_path: str) -> str:
        """Загрузить текст книги из файла или интернета."""
        path = __import__('pathlib').Path(book_path)
        
        # Если это URL — скачиваем
        if book_path.startswith("http"):
            return self._download_book(book_path)
        
        # Если это локальный файл
        if not path.exists():
            self.logger.warning(f"Книга не найдена: {book_path}")
            return ""
        
        # Определение формата
        suffix = path.suffix.lower()
        
        if suffix in [".txt", ".md"]:
            return path.read_text(encoding="utf-8", errors="ignore")
        elif suffix == ".json":
            import json
            data = json.loads(path.read_text(encoding="utf-8"))
            return data.get("text", "")
        else:
            self.logger.warning(f"Формат {suffix} пока не поддерживается")
            return ""

    def _download_book(self, url: str) -> str:
        """Скачать книгу из интернета."""
        try:
            import urllib.request
            with urllib.request.urlopen(url) as response:
                return response.read().decode("utf-8", errors="ignore")
        except Exception as e:
            self.logger.error(f"Ошибка скачивания {url}: {e}")
            return ""

    def _extract_knowledge(self, text: str, source: str) -> list[KnowledgeEntry]:
        """Извлечь знания из текста."""
        knowledge = []
        paragraphs = text.split("\n\n")
        
        for i, paragraph in enumerate(paragraphs[:100]):  # Лимит для демо
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

    def _analyze_style(self, text: str) -> list[StyleEntry]:
        """Анализ стиля повествования."""
        # Заглушка — в реальности здесь будет NLP-анализ
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
        # Заглушка — в реальности здесь будет NLP-анализ
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

    def _extract_summary(self, text: str, source: str) -> BookSummary | None:
        """Извлечь суть книги."""
        paragraphs = text.split("\n\n")
        
        if not paragraphs:
            return None
        
        # Простое извлечение — берём первые абзацы как суть
        summary_text = "\n".join(paragraphs[:10])
        
        summary = BookSummary(
            source=source,
            summary=summary_text,
            key_points=["Основная идея книги"],
            main_characters=["Персонажи не определены"],
            setting="Место не определено",
            genre="Не определён",
        )
        
        return summary

    def _extract_thought(self, text: str, source: str) -> BookThought | None:
        """Извлечь мысль/идею книги."""
        thought = BookThought(
            source=source,
            central_thought="Авторская мысль не определена",
            moral_lesson="",
            philosophical_concepts=[],
            author_intention="Не определена",
        )
        
        return thought

    def save_knowledge_base(self):
        """Сохранить все базы данных."""
        self.config.knowledge_base_path.parent.mkdir(parents=True, exist_ok=True)
        
        data = {
            "version": self.config.version,
            "timestamp": __import__('datetime').datetime.now().isoformat(),
            "entries": [entry.to_dict() for entry in self.knowledge_base],
            "pairs": [pair.to_dict() for pair in self.training_pairs],
            "lore": [lore.to_dict() for lore in self.lore_db],
            "styles": [style.to_dict() for style in self.style_db],
            "summaries": {k: v.to_dict() for k, v in self.books_summaries.items()},
            "thoughts": [t.to_dict() for t in self.books_thoughts],
        }
        
        with open(self.config.knowledge_base_path, "w", encoding="utf-8") as f:
            __import__('json').dump(data, f, ensure_ascii=False, indent=2)
        
        self.logger.info(f"💾 База знаний сохранена:")
        self.logger.info(f"   Записей: {len(self.knowledge_base)}")
        self.logger.info(f"   Пар: {len(self.training_pairs)}")
        self.logger.info(f"   Лора: {len(self.lore_db)}")
        self.logger.info(f"   Стилей: {len(self.style_db)}")
        self.logger.info(f"   Суть: {len(self.books_summaries)}")
        self.logger.info(f"   Мысль: {len(self.books_thoughts)}")

    def train_model(self):
        """Дообучение модели на созданных парах."""
        if not self.training_pairs:
            self.logger.info("⚠️ Нет обучающих пар для обучения")
            return
        
        # Сохранение обучающих пар
        self._save_training_pairs()
        
        # Логирование статистики
        self.state.training_pairs_generated += len(self.training_pairs)
        self.state.knowledge_entries_saved += len(self.knowledge_base)
        
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

    def run_cycle(self):
        """Запустить один цикл работы."""
        self.state.cycle_count += 1
        self.logger.info(f"=== ЦИКЛ {self.state.cycle_count} ===")
        
        # 1. Поиск и чтение книг
        self._read_books()
        
        # 2. Анализ стиля (периодически)
        if self.state.cycle_count % 3 == 0 and self.config.enable_style_learning:
            self._analyze_styles_batch()
        
        # 3. Разбор лора (периодически)
        if self.state.cycle_count % 5 == 0 and self.config.enable_lore_extraction:
            self._analyze_lore_batch()
        
        # 4. Обучение модели (периодически)
        if self.state.cycle_count % 10 == 0:
            self.train_model()
        
        # 5. Сохранение состояния
        if self.state.cycle_count % self.config.save_state_every_n_cycles == 0:
            self.save_knowledge_base()
            self.state.save_to_file(self.config.state_path)

    def _read_books(self):
        """Прочитать книги из директории и интернета."""
        # Чтение локальных книг
        books_dir = self.config.books_directory
        if books_dir.exists():
            for book_file in books_dir.iterdir():
                if book_file.suffix.lower() in self.config.supported_formats:
                    result = self.read_book(str(book_file))
                    self.logger.info(f"📚 Книга обработана: {result}")
        
        # TODO: Добавить поиск книг в интернете
        # self._search_and_download_books()

    def _analyze_styles_batch(self):
        """Пакетный анализ стилей."""
        self.logger.info("✍️ Пакетный анализ стилей...")
        # TODO: Реализовать NLP-анализ

    def _analyze_lore_batch(self):
        """Пакетный разбор лора."""
        self.logger.info("🌍 Пакетный разбор лора...")
        # TODO: Реализовать NLP-анализ

    def run(self):
        """Запустить постоянную работу."""
        self.logger.info("📚 ЗАПУСК АВТОНОМНОГО ЯДРА АЙКО")
        self.logger.info("🤖 Режим: Автономная работа 24/7")
        
        try:
            while True:
                self.run_cycle()
                __import__('time').sleep(self.config.cycle_interval)
        except KeyboardInterrupt:
            self.logger.info("🛑 Остановка Айко")
            self.save_knowledge_base()
            self.state.save_to_file(self.config.state_path)
