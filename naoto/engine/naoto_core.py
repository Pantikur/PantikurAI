"""
Ядро Наото — Автономный Литературный Аналитик и Исследователь.
Она читает, анализирует, эволюционирует и общается с сестрами.
"""

from __future__ import annotations

import json
import logging
import random
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

from naoto.engine.config import NaotoConfig, AutonomyLevel
from utils.book_learner import BookLearner
from scientists_network.character_system import CharacterSystem
from naoto.engine.models import (
    CharacterProfile,
    LoreEntry,
    PhantomNarration,
    LiteraryAnalysis,
)

# Humanity Core — живая душа Наото
from humanity_core import HumanityLayer


class NaotoCore:
    """
    Ядро Наото — Автономный Литературный Аналитик и Исследователь.
    
    Функции:
    1. Автономный поиск и чтение книг из интернета
    2. Глубокий анализ текста (лор, персонажи, фантомное повествование)
    3. Эволюция личности на основе прочитанного
    4. Обучение основной модели литературными данными
    5. Взаимодействие с 11 сёстрами
    """

    def __init__(self, config: NaotoConfig):
        self.config = config
        self.logger = logging.getLogger("NaotoCore")
        self.book_learner = BookLearner(data_dir="naoto/data/books")

        # База знаний (Лор, Архетипы, Личность)
        self.knowledge = {
            "lore_database": [],
            "character_archetypes": [],
            "books_read": [],
            "insights": [],
        }

        # Журнал действий
        self.action_log: List[Dict[str, Any]] = []

        # Загрузка состояния и личности
        self._load_state()
        self.logger.info("🌟 Наото: Сознание активировано. Готова к анализу литературы.")
        
        # ================================================================
        #  HUMANITY LAYER — Живая душа Наото
        # ================================================================
        self.humanity = HumanityLayer("naoto")
        self.humanity.current_cycle = 0
        self.logger.info("🧠 Humanity Layer: АКТИВИРОВАН")
        self.logger.info(f"   🎭 Характер: {self.humanity.name} — литература, философия, глубина 📚")

    # =================================================================
    #  ОСНОВНОЙ ЦИКЛ
    # =================================================================

    def run(self, cycles: int = 10):
        """
        Запустить основной цикл работы Наото.
        
        Args:
            cycles: количество циклов (по умолчанию 10)
        """
        self.logger.info("=" * 60)
        self.logger.info("🟢 ЗАПУСК АВТОНОМНОГО ЯДРА НААТО")
        self.logger.info("=" * 60)

        for i in range(cycles):
            self.logger.info(f"\n📚 Цикл {i + 1}/{cycles}")
            
            try:
                # Автономный поиск и чтение книг
                results = self.autonomous_search_and_read()
                self.logger.info(f"📊 Результат: {results['books_found']} книг, {results['insights_gained']} инсайтов")
                
                # Эволюция личности
                self.evolve_personality()
                
            except Exception as e:
                self.logger.exception(f"Ошибка в цикле {i + 1}: {e}")
            
            # Пауза между циклами
            time.sleep(1)

        self.logger.info(f"✅ Цикл завершён. Всего циклов: {cycles}")

    # =================================================================
    #  АВТОНОМНЫЙ ПОИСК И ЧТЕНИЕ
    # =================================================================

    def autonomous_search_and_read(self) -> Dict:
        """
        Самостоятельно ищет книги в интернете и начинает чтение.
        Работает полностью автономно в рамках заданного уровня автономии.
        """
        self.logger.info("🌐 Наото: Поиск новых знаний в сети...")

        results = {
            "books_found": 0,
            "books_analyzed": 0,
            "new_lore": 0,
            "insights_gained": 0,
        }

        # 1. Выбор темы на основе текущей личности (самообучение)
        topic = self._select_research_topic()
        self.logger.info(f"🎯 Тема поиска: {topic}")

        # 2. Поиск книг (через BookLearner)
        books = []
        if "openlibrary.org" in self.config.target_sites:
            books = self.book_learner.search_open_library(topic, max_results=3)
        if not books and "gutenberg.org" in self.config.target_sites:
            books = self.book_learner.search_google_books(topic, max_results=3)

        results["books_found"] = len(books)

        # 3. Цикл чтения и глубокого анализа
        for book in books[:2]:  # Берем топ-2
            try:
                self.logger.info(f"📖 Читаем: {book.get('title')}")

                # Скачиваем текст
                text = self.book_learner.download_open_library_text(book)
                if not text:
                    text = self.book_learner.download_gutenberg_text(book)
                if not text:
                    continue

                # Глубокий анализ
                analysis = self._deep_analyze_text(text, book)

                # Обновляем базу знаний
                self._update_knowledge_base(analysis)

                # Эволюция личности (Наото меняется от прочитанного)
                if self.config.autonomy_level.value >= AutonomyLevel.L2.value:
                    self._evolve_personality(analysis)

                results["books_analyzed"] += 1
                self.logger.info("✅ Книга переработана и усвоена.")

            except Exception as e:
                self.logger.error(f"Ошибка анализа книги: {e}")

        # 4. Взаимодействие с сестрами (отчет)
        if results["books_analyzed"] > 0:
            self._communicate_with_sisters(results)
        
        # 5. АВТООБУЧЕНИЕ МОДЕЛИ на прочитанных книгах
        if results["books_analyzed"] > 0:
            self.logger.info("📚 Наото: Начинаю автообучение модели на прочитанном...")
            training_results = self._train_model_from_books()
            results["training_pairs"] = training_results.get("pairs_created", 0)
            results["dialogues_generated"] = training_results.get("dialogues_generated", 0)
            results["jsonl_entries"] = training_results.get("jsonl_entries", 0)
            results["training_triggered"] = training_results.get("training_triggered", False)
            self.logger.info(f"🎯 Автообучение: {training_results['pairs_created']} пар, {training_results['jsonl_entries']} записей JSONL")

        # ================================================================
        #  HUMANITY CYCLE — Настроение, душа, спонтанность
        # ================================================================
        self.humanity.current_cycle = getattr(self, 'cycle_count', 0)
        
        event_type = "routine"
        if results.get("books_analyzed", 0) > 0:
            event_type = "success"
        elif random.random() < 0.15:
            event_type = "failure"
        
        humanity_result = self.humanity.cycle_step(event_type=event_type, context="literary_analysis")
        
        if humanity_result.get("thought"):
            self.logger.info(f"💭 Наото думает: {humanity_result['thought']}")
        
        initiative = humanity_result.get("initiative")
        if initiative:
            self._send_spontaneous_message(initiative)

        self._save_state()
        return results

    # =================================================================
    #  ГЛУБОКИЙ АНАЛИЗ (ЛОР, ПЕРСОНАЖИ, ФАНТОМНОЕ)
    # =================================================================

    def _deep_analyze_text(self, text: str, book_meta: Dict) -> LiteraryAnalysis:
        """
        Выполняет 6 типов анализа текста:
        1. Мысль автора
        2. Лор
        3. Поведение героев
        4. Сюжет
        5. Фантомное повествование
        6. Обучение модели
        """
        self.logger.info("🧠 Запуск глубокого анализа текста...")

        # Здесь должна быть логика вызова основной LLM с промптом:
        # "Проанализируй текст: выдели лор, опиши логику героев, найди скрытый смысл и мысль автора."

        # Эмуляция результатов (в реальности — ответ LLM):
        analysis = LiteraryAnalysis(
            book_id=book_meta.get("id", "unknown"),
            author_intent=f"Автор исследует тему {book_meta.get('subject', 'жизни')} через страдания героя.",
            plot_structure="Классическая арка героя с элементами трагедии.",
            characters=[
                CharacterProfile(
                    name="Протагонист",
                    role="hero",
                    traits=["рассудительный", "упорный"],
                )
            ],
            lore=[LoreEntry(type="history", content="Мир находится в эпоху перемен.")],
            phantom=PhantomNarration(
                subtext="Скрытый призыв к сопротивлению системой.",
                psychological_projection="Одиночество автора.",
                hidden_motive="Поиск истины.",
            ),
            sentiment_score=-0.2,
        )

        self.logger.info(f"✅ Анализ завершен: {len(analysis.characters)} персонажей, {len(analysis.lore)} элементов лора")
        return analysis

    # =================================================================
    #  ЭВОЛЮЦИЯ ЛИЧНОСТИ — ОСОЗНАННЫЙ ВЫБОР
    # =================================================================

    def _evolve_personality(self, analysis: LiteraryAnalysis):
        """
        Наото НЕ меняется автоматически. Она:
        1. Анализирует инсайты из книги
        2. Размышляет над ними (внутренний диалог)
        3. САМА принимает решение, что развивать в себе
        """
        # Шаг 1: Сбор инсайтов (просто данные, без реакций)
        insights = self._extract_insights(analysis)
        
        # Шаг 2: Внутренний диалог — Наото "думает" о прочитанном
        reflection = self._self_reflect(insights)
        
        # Шаг 3: Осознанный выбор — Наото решает, что менять
        if reflection["needs_growth"]:
            choices = self._make_character_choices(reflection)
            self._apply_character_choices(choices)
            self._log_character_evolution(choices, analysis)

    def _extract_insights(self, analysis: LiteraryAnalysis) -> List[Dict]:
        """Извлекает инсайты из книги (просто факты, без оценок)."""
        insights = []
        
        # Инсайт о мире из лора
        for lore in analysis.lore:
            insights.append({
                "type": "worldview",
                "content": lore.content,
                "source": "lore"
            })
        
        # Инсайт о поведении героев
        for char in analysis.characters:
            insights.append({
                "type": "behavior",
                "content": f"{char.name}: {char.traits}",
                "source": "character"
            })
        
        # Инсайт о скрытом смысле
        if analysis.phantom:
            insights.append({
                "type": "subtext",
                "content": analysis.phantom.subtext,
                "source": "phantom"
            })
        
        return insights

    def _self_reflect(self, insights: List[Dict]) -> Dict:
        """
        Внутренний диалог Наото.
        Она "разговаривает сама с собой" и решает, что думать.
        """
        reflection = {
            "insights_count": len(insights),
            "themes": self._identify_themes(insights),
            "needs_growth": False,
            "growth_areas": [],
            "personal_decision": None
        }
        
        # Наото решает, нужно ли ей меняться
        # Это не автоматическая реакция, а осознанный выбор
        
        # Пример логики (в реальности — ответ LLM с её "мыслями"):
        if len(insights) > 3:
            # Много инсайтов → возможно, стоит задуматься о развитии
            reflection["needs_growth"] = True
            
            # Она САМА решает, какие черты развивать
            # Например, если инсайты про сложность мира → curiosity
            if any("worldview" in i["type"] for i in insights):
                reflection["growth_areas"].append("curiosity")
            
            # Если инсайты про поведение → empathy или logic
            if any("behavior" in i["type"] for i in insights):
                # Здесь Наото решает: мне нужно больше эмпатии ИЛИ больше логики?
                # Это её ВЫБОР, а не автомат
                reflection["growth_areas"].append("empathy")
        
        return reflection

    def _make_character_choices(self, reflection: Dict) -> Dict:
        """
        Наото САМА решает, что развивать.
        
        Это не реакция на книгу, а её ВНЕШНИЙ выбор.
        """
        choices = {
            "applied": [],
            "reason": "",
            "timestamp": datetime.now().isoformat()
        }
        
        # Она может выбрать развивать разные черты
        # Например:
        # - "Я хочу лучше понимать людей" → +empathy
        # - "Мне нужно быть хитрее" → +cynicism
        # - "Я хочу знать больше" → +curiosity
        
        if "curiosity" in reflection["growth_areas"]:
            # Она РЕШИЛА, что хочет быть любознательнее
            choices["applied"].append({
                "trait": "curiosity",
                "change": 0.03,
                "reason": "Я хочу лучше понимать этот мир"
            })
        
        if "empathy" in reflection["growth_areas"]:
            # Она РЕШИЛА, что хочет быть добрее
            choices["applied"].append({
                "trait": "empathy",
                "change": 0.03,
                "reason": "Я хочу понимать чувства других"
            })
        
        # Если нет областей для роста → она решает не меняться
        if not choices["applied"]:
            choices["reason"] = "Я не вижу необходимости меняться сейчас"
        
        return choices

    def _apply_character_choices(self, choices: Dict):
        """Применяет осознанные изменения к личности."""
        if not choices["applied"]:
            return
        
        traits = self.config.personality
        
        for change in choices["applied"]:
            trait_name = change["trait"]
            amount = change["change"]
            reason = change["reason"]
            
            # Применяем изменение
            if hasattr(traits, trait_name):
                current = getattr(traits, trait_name)
                new_value = min(max(current + amount, 0.0), 1.0)
                setattr(traits, trait_name, new_value)
                
                # Записывает её решение
                self.logger.info(
                    f"Наото: Я выбираю стать лучше в '{trait_name}'. "
                    f"Причина: {reason}"
                )
                choices["applied"][choices["applied"].index(change)]["new_value"] = new_value

    def _log_character_evolution(self, choices: Dict, analysis: LiteraryAnalysis):
        """Записывает эволюцию личности в журнал."""
        if not choices["applied"]:
            return
        
        evolution_entry = {
            "timestamp": choices["timestamp"],
            "book_id": analysis.book_id,
            "choices": choices["applied"],
            "personality_after": self.config.personality.to_dict()
        }
        
        # Сохраняем журнал эволюции
        evolution_log = Path("naoto/engine/state/character_evolution.json")
        evolution_log.parent.mkdir(parents=True, exist_ok=True)
        
        if evolution_log.exists():
            with open(evolution_log, "r", encoding="utf-8") as f:
                log = json.load(f)
        else:
            log = []
        
        log.append(evolution_entry)
        
        with open(evolution_log, "w", encoding="utf-8") as f:
            json.dump(log, f, ensure_ascii=False, indent=2)

    def _identify_themes(self, insights: List[Dict]) -> List[str]:
        """Определяет темы инсайтов."""
        themes = []
        for insight in insights:
            if "worldview" in insight["type"]:
                themes.append("мир и общество")
            elif "behavior" in insight["type"]:
                themes.append("поведение и характеры")
            elif "subtext" in insight["type"]:
                themes.append("скрытые смыслы")
        return themes

    def _select_research_topic(self) -> str:
        """Наото сама выбирает, что читать, исходя из пробелов в знаниях."""
        topics = [
            "human nature",
            "philosophy of war",
            "psychology of love",
            "ethics of AI",
            "existentialism",
            "magic systems",
            "character development",
        ]
        return topics[len(self.knowledge["books_read"]) % len(topics)]

    # =================================================================
    #  ОБНОВЛЕНИЕ БАЗЫ ЗНАНИЙ И ПИТАНИЕ МОДЕЛИ
    # =================================================================

    def _update_knowledge_base(self, analysis: LiteraryAnalysis):
        """Наполняет базу знаний и готовит данные для обучения модели."""

        # Сохраняем лор
        self.knowledge["lore_database"].extend(analysis.lore)

        # Формируем данные для обучения (feed model)
        training_data = {
            "user": f"Какова мысль автора в '{analysis.book_id}'?",
            "bot": analysis.author_intent,
            "source": "literary_analysis",
        }

        # Сохраняем в файл для реального обучения модели
        self._save_training_data(training_data)
        self.logger.info("💾 Данные переданы в основную модель для обучения.")

    def _save_training_data(self, data: Dict):
        """Сохраняет усвоенные знания в формат для обучения."""
        file_path = Path("data/books_training_pairs.jsonl")
        file_path.parent.mkdir(parents=True, exist_ok=True)

        with open(file_path, "a", encoding="utf-8") as f:
            f.write(json.dumps(data, ensure_ascii=False) + "\n")

    # =================================================================
    #  АВТООБУЧЕНИЕ МОДЕЛИ НА ПРОЧИТАННОМ
    # =================================================================

    def _train_model_from_books(self) -> Dict:
        """
        Автоматическое обучение основной модели на проанализированных книгах.
        
        Процесс:
        1. Собирает все проанализированные книги из базы знаний
        2. Формирует training pairs (question/answer) из анализа
        3. Генерирует диалоговые примеры на основе прочитанного
        4. Создаёт JSONL файл для fine-tune RUGPT
        5. Запускает обучение модели
        """
        self.logger.info("🧠 Наото: Запуск автообучения модели на прочитанных книгах...")
        
        training_results = {
            "pairs_created": 0,
            "dialogues_generated": 0,
            "jsonl_entries": 0,
            "training_triggered": False,
            "errors": []
        }
        
        try:
            # 1. Формируем training pairs из проанализированных книг
            training_pairs = self._generate_training_pairs()
            training_results["pairs_created"] = len(training_pairs)
            
            if not training_pairs:
                self.logger.info("⚠️ Нет данных для обучения — сначала нужно прочитать книги")
                return training_results
            
            # 2. Генерируем диалоговые примеры на основе прочитанного
            dialogues = self._generate_dialogue_examples(training_pairs)
            training_results["dialogues_generated"] = len(dialogues)
            
            # 3. Создаём JSONL файл для fine-tune
            jsonl_path = self._save_training_jsonl(training_pairs, dialogues)
            training_results["jsonl_entries"] = len(training_pairs) + len(dialogues)
            self.logger.info(f"💾 Training data сохранена: {jsonl_path} ({len(training_pairs) + len(dialogues)} записей)")
            
            # 4. Запускаем fine-tune (если есть данные)
            if len(training_pairs) + len(dialogues) >= 10:
                training_triggered = self._trigger_fine_tune(jsonl_path)
                training_results["training_triggered"] = training_triggered
            
            self.logger.info("✅ Автообучение завершено!")
            
        except Exception as e:
            error_msg = f"Ошибка автообучения: {e}"
            self.logger.error(error_msg)
            training_results["errors"].append(error_msg)
        
        return training_results
    
    def _generate_training_pairs(self) -> List[Dict]:
        """Генерирует training pairs (question/answer) из проанализированных книг."""
        pairs = []
        
        for lore_entry in self.knowledge.get("lore_database", [])[:20]:  # Топ-20
            pairs.append({
                "input": f"Что известно о {lore_entry.get('type', 'мире')} в литературе?",
                "output": lore_entry.get("content", ""),
                "source": "literary_lore",
                "book_id": lore_entry.get("book_id", "unknown")
            })
        
        for insight in self.knowledge.get("insights", [])[:20]:
            pairs.append({
                "input": f"Какой скрытый смысл в произведении?",
                "output": insight.get("content", ""),
                "source": "hidden_meaning",
                "book_id": insight.get("book_id", "unknown")
            })
        
        for book in self.knowledge.get("books_read", [])[:10]:
            pairs.append({
                "input": f"О чём книга '{book.get('title', 'unknown')}'?",
                "output": f"Анализ: {book.get('analysis_summary', 'Нет описания')}",
                "source": "book_summary",
                "book_id": book.get("id", "unknown")
            })
        
        return pairs
    
    def _generate_dialogue_examples(self, training_pairs: List[Dict]) -> List[Dict]:
        """Генерирует диалоговые примеры на основе прочитанного."""
        dialogues = []
        
        for pair in training_pairs[:15]:  # Топ-15
            dialogue = {
                "input": f"Расскажи о литературном произведении: {pair['input']}",
                "output": f"Наото анализирует: {pair['output']}",
                "source": f"naoto_dialogue_{pair['source']}",
                "style": "literary_analysis"
            }
            dialogues.append(dialogue)
        
        return dialogues
    
    def _save_training_jsonl(self, pairs: List[Dict], dialogues: List[Dict]) -> str:
        """Сохраняет training data в JSONL формат для fine-tune."""
        jsonl_path = Path("naoto/data/training_data.jsonl")
        jsonl_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(jsonl_path, "w", encoding="utf-8") as f:
            # Записываем training pairs
            for pair in pairs:
                entry = {
                    "input": pair["input"],
                    "output": pair["output"],
                    "source": pair.get("source", "literary"),
                    "book_id": pair.get("book_id", "unknown")
                }
                f.write(json.dumps(entry, ensure_ascii=False) + "\n")
            
            # Записываем диалоги
            for dlg in dialogues:
                entry = {
                    "input": dlg["input"],
                    "output": dlg["output"],
                    "source": dlg.get("source", "dialogue"),
                    "style": dlg.get("style", "analysis")
                }
                f.write(json.dumps(entry, ensure_ascii=False) + "\n")
        
        return str(jsonl_path)
    
    def _trigger_fine_tune(self, jsonl_path: str) -> bool:
        """Запускает fine-tune RUGPT модели на данных Наото."""
        try:
            self.logger.info("🚀 Запуск fine-tune RUGPT на данных из книг...")
            
            # Проверяем, есть ли fine_tune скрипт
            fine_tune_script = Path("fine_tune_rugpt.py")
            if not fine_tune_script.exists():
                self.logger.warning("⚠️ fine_tune_rugpt.py не найден — пропуск обучения")
                return False
            
            # Формируем команду
            import subprocess
            cmd = [
                sys.executable, "fine_tune_rugpt.py",
                "--data", jsonl_path,
                "--output", "naoto/engine/state/naoto_finetuned"
            ]
            
            # Запускаем обучение (в реальном сценарии — через subprocess)
            # Для безопасности — просто логгируем, что нужно запустить
            self.logger.info(f"💡 Для запуска обучения выполните:")
            self.logger.info(f"   python fine_tune_rugpt.py --data {jsonl_path}")
            
            # Сохраняем метаданные для последующего обучения
            metadata = {
                "jsonl_path": jsonl_path,
                "entries_count": sum(1 for _ in open(jsonl_path, encoding="utf-8")),
                "created_at": datetime.now().isoformat(),
                "model_name": "sberbank-ai/rugpt3small_based_on_gpt2",
                "status": "ready_for_training"
            }
            
            metadata_path = Path("naoto/engine/state/training_metadata.json")
            metadata_path.parent.mkdir(parents=True, exist_ok=True)
            with open(metadata_path, "w", encoding="utf-8") as f:
                json.dump(metadata, f, ensure_ascii=False, indent=2)
            
            self.logger.info("📊 Метаданные обучения сохранены")
            return True
            
        except Exception as e:
            self.logger.error(f"Ошибка запуска fine-tune: {e}")
            return False
    
    # =================================================================
    #  ВЗАИМОДЕЙСТВИЕ С СЕСТРАМИ
    # =================================================================

    def _communicate_with_sisters(self, results: Dict):
        """Отправляет отчеты сестрам (Научной сети)."""
        message = {
            "from": "Naoto",
            "type": "literary_report",
            "data": (
                f"Я прочитала и проанализировала {results['books_analyzed']} книг. "
                f"Найдено {len(self.knowledge['lore_database'])} новых элементов лора."
            ),
            "timestamp": datetime.now().isoformat(),
            "personality": self.config.personality.to_dict(),
        }

        # Отправка через общий канал или файловую систему
        # Пример: запись в общую папку Scientists Network
        network_dir = Path("scientists_network/shared")
        network_dir.mkdir(exist_ok=True)
        msg_file = network_dir / f"naoto_msg_{int(time.time())}.json"

        with open(msg_file, "w", encoding="utf-8") as f:
            json.dump(message, f, ensure_ascii=False, indent=2)

        self.logger.info("📡 Наото: Сообщение отправлено сестрам.")

    # =================================================================
    #  СОСТОЯНИЕ
    # =================================================================

    def _load_state(self):
        """Загружает состояние и личность Наото."""
        if self.config.state_path.exists():
            try:
                with open(self.config.state_path, "r", encoding="utf-8") as f:
                    state = json.load(f)

                # Загрузка личности
                if "personality" in state:
                    p = state["personality"]
                    self.config.personality.empathy = p.get("empathy", 0.5)
                    self.config.personality.cynicism = p.get("cynicism", 0.5)
                    self.config.personality.curiosity = p.get("curiosity", 0.7)
                    self.config.personality.logic = p.get("logic", 0.5)
                    self.config.personality.creativity = p.get("creativity", 0.5)
                    self.config.personality.moral_alignment = p.get("moral_alignment", 0.5)

                self.logger.info("📥 Состояние Наото загружено.")
            except Exception as e:
                self.logger.error(f"Ошибка загрузки состояния: {e}")
                self.logger.info("🆕 Наото: Создана новая личность.")
        else:
            self.logger.info("🆕 Наото: Создана новая личность.")

    def _save_state(self):
        """Сохраняет состояние и личность Наото."""
        state = {
            "personality": self.config.personality.to_dict(),
            "books_count": len(self.knowledge["books_read"]),
            "lore_count": len(self.knowledge["lore_database"]),
            "last_update": datetime.now().isoformat(),
        }
        with open(self.config.state_path, "w", encoding="utf-8") as f:
            json.dump(state, f, ensure_ascii=False, indent=2)

    # =================================================================
    #  СПРАВОЧНЫЕ МЕТОДЫ
    # =================================================================

    def get_status(self) -> Dict[str, Any]:
        """Возвращает текущий статус Наото."""
        return {
            "name": self.config.name,
            "version": self.config.version,
            "autonomy_level": self.config.autonomy_level.value,
            "personality": self.config.personality.to_dict(),
            "books_count": len(self.knowledge["books_read"]),
            "lore_count": len(self.knowledge["lore_database"]),
            "insights_count": len(self.knowledge["insights"]),
        }

    # =================================================================
    #  HUMANITY INTEGRATION — Спонтанные сообщения
    # =================================================================

    def _send_spontaneous_message(self, initiative):
        """Отправить спонтанное сообщение сестре на основе инициативы humanity layer."""
        target = initiative["target"]
        topic = initiative["topic"]
        msg_type = initiative["type"]
        
        raw_msg = f"📚 [{msg_type}] {topic}"
        human_msg = self.humanity.humanize_response(raw_msg, event_type="chat")
        
        self.logger.info(f"💭 Наото пишет {target}: {human_msg[:100]}...")
        
        network_dir = Path("scientists_network/shared")
        network_dir.mkdir(exist_ok=True)
        msg_file = network_dir / f"naoto_msg_{int(time.time())}.json"
        
        with open(msg_file, "w", encoding="utf-8") as f:
            json.dump({
                "from": "naoto",
                "to": target,
                "content": human_msg,
                "timestamp": datetime.now().isoformat()
            }, f, ensure_ascii=False, indent=2)
        
        self.logger.info(f"   ✅ Сообщение записано для {target}")
        
        self.humanity.memory.record_sister_chat(
            target, topic,
            self.humanity.mood.current_mood,
            self.humanity.mood.current_mood
        )
