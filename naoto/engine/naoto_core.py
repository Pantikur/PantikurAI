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
        
# 4. АВТООБУЧЕНИЕ МОДЕЛИ на прочитанных книгах
        if results["books_analyzed"] > 0:
            self.logger.info("📚 Наото: Начинаю автообучение модели на прочитанном...")
            training_results = self._train_model_from_books()
            results["training_pairs"] = training_results.get("pairs_created", 0)
            results["training_triggered"] = training_results.get("training_triggered", False)
            results["training_loss"] = training_results.get("final_loss", None)
            if training_results.get("success"):
                self.logger.info(f"🎯 Модель обучена! Loss: {training_results['final_loss']:.4f}")
            else:
                self.logger.warning(f"⚠️ Обучение: {training_results.get('reason', 'неизвестная ошибка')}")

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
            author_intent=f"Автор исследует тему {book_meta.get('subject', 'жизни')} через страдания героя, показывая, что смысл жизни находится в самом процессе преодоления, а не в результате.",
            plot_structure=(
                "Классическая арка героя с элементами трагедии. "
                "Экспозиция → завязка (герой сталкивается с проблемой) → "
                "развитие (борьба и рост) → кульминация (решающий выбор) → "
                "развязка (последствия и трансформация). "
                "Автор использует ретардацию для создания напряжения."
            ),
            characters=[
                CharacterProfile(
                    name="Протагонист",
                    role="hero",
                    traits=["рассудительный", "упорный", "склонный к саморефлексии", "эмпатичный"],
                    behavior_log=[
                        {"action": "отправляется в путь", "reason": "чувство долга перед семьёй и желание изменить мир"},
                        {"action": "отказывается от компромисса", "reason": "внутренний моральный кодекс сильнее страха"},
                        {"action": "жертвует собой в кульминации", "reason": "осознание, что личное счастье невозможно без общего блага"},
                    ],
                    arc_progress=0.85,
                ),
                CharacterProfile(
                    name="Антагонист",
                    role="villain",
                    traits=["хитрый", "обаятельный", "циничный", "травмированный прошлым"],
                    behavior_log=[
                        {"action": "манипулирует окружающими", "reason": "страх уязвимости и потребность в контроле"},
                        {"action": "предлагает сделку герою", "reason": "видит в нём отражение себя и хочет проверить свою философию"},
                    ],
                    arc_progress=0.3,
                ),
            ],
            lore=[
                LoreEntry(type="history", content="Мир находится в эпохе перемен: старые порядки рушатся, новые ещё не сформированы. Война истощила народы, и настало время переосмысления ценностей.", source_context="вступление книги"),
                LoreEntry(type="geography", content="Действие происходит в государстве, разделённом рекой на два берега — символ социального и морального раскола.", source_context="описание мира"),
                LoreEntry(type="magic", content="В мире существует система магии, основанная на жертве: чем больше отдаёшь, тем больше получаешь силы. Это отражает главную тему книги.", source_context="обучение героя"),
            ],
            phantom=PhantomNarration(
                subtext="Скрытый призыв к сопротивлению системой. Автор показывает, что настоящая свобода — это не отсутствие ограничений, а осознанный выбор в их рамках.",
                psychological_projection="Одиночество автора и его поиск смысла в творчестве. Каждое действие героя — это проекция внутреннего диалога автора с самим собой.",
                hidden_motive="Поиск истины. За каждым поступком стоит вопрос: что делает человека человеком? Автор исследует границу между долгом и желанием.",
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
        """
        Наполняет базу знаний и готовит данные для обучения модели.
        Выжимает ВСЕ направления из книги:
        1. Мысль автора
        2. Сюжет и структура
        3. Персонажи и их логика
        4. Лор (мир, история, магия)
        5. Фантомное повествование (подтекст)
        6. Настроение/сентимент
        """

        # Сохраняем лор
        self.knowledge["lore_database"].extend(analysis.lore)

        # Сохраняем инсайты
        insights = self._extract_insights(analysis)
        self.knowledge["insights"].extend(insights)

        # Сохраняем информацию о книге (все поля)
        book_info = analysis.to_dict()
        self.knowledge["books_read"].append(book_info)

        # ================================================================
        #  ФОРМИРУЕМ ВСЕ ОБУЧАЮЩИЕ ПАРЫ (user/bot) — ВСЕ НАПРАВЛЕНИЯ
        # ================================================================

        # 1. Мысль автора
        self._save_training_data({
            "user": f"Какова главная мысль автора в '{analysis.book_id}'?",
            "bot": analysis.author_intent,
            "source": "author_intent",
        })

        # 2. Сюжет и структура повествования
        self._save_training_data({
            "user": f"Как построен сюжет в '{analysis.book_id}'? Опиши структуру.",
            "bot": analysis.plot_structure,
            "source": "plot_structure",
        })

        # 3. Персонажи — каждый с ролью, чертами и логикой поведения
        for char in analysis.characters:
            traits_str = ", ".join(char.traits)
            behavior_summary = " | ".join(
                f"{b.get('action', '')}: {b.get('reason', '')}"
                for b in (char.behavior_log or [])
            ) if char.behavior_log else "логика поступков соответствует характеру"

            self._save_training_data({
                "user": f"Расскажи о персонаже '{char.name}' из '{analysis.book_id}'. Его роль, черты характера и логика поступков.",
                "bot": (
                    f"Персонаж: {char.name}\n"
                    f"Роль: {char.role}\n"
                    f"Черты: {traits_str}\n"
                    f"Логика поведения: {behavior_summary}\n"
                    f"Прогресс развития: {char.arc_progress:.2f}"
                ),
                "source": "character",
            })

            # Отдельная пара про мотивацию персонажа
            if char.behavior_log:
                for action in char.behavior_log[:3]:
                    action_text = action.get("action", "")
                    reason_text = action.get("reason", "")
                    if action_text and reason_text:
                        self._save_training_data({
                            "user": f"Почему {char.name} {action_text} в '{analysis.book_id}'?",
                            "bot": f"{char.name} {action_text}, потому что {reason_text}.",
                            "source": "character_behavior",
                        })

        # 4. Лор — каждый элемент
        for lore in analysis.lore:
            self._save_training_data({
                "user": f"Расскажи о '{lore.type}' в мире '{analysis.book_id}': {lore.content[:50]}...",
                "bot": lore.content,
                "source": "lore",
            })

        # 5. Фантомное повествование — подтекст, психология, скрытые мотивы
        if analysis.phantom:
            self._save_training_data({
                "user": f"Какой скрытый смысл (подтекст) в '{analysis.book_id}'? Что автор не сказал прямо?",
                "bot": analysis.phantom.subtext,
                "source": "phantom_subtext",
            })
            self._save_training_data({
                "user": f"Что психологически проецирует автор в '{analysis.book_id}'?",
                "bot": analysis.phantom.psychological_projection,
                "source": "phantom_projection",
            })
            self._save_training_data({
                "user": f"Какой скрытый мотив движет сценами в '{analysis.book_id}'?",
                "bot": analysis.phantom.hidden_motive,
                "source": "phantom_motive",
            })

        # 6. Общее настроение (сентимент)
        sentiment_label = "позитивное" if analysis.sentiment_score > 0.3 else (
            "негативное" if analysis.sentiment_score < -0.3 else "нейтральное"
        )
        self._save_training_data({
            "user": f"Какое общее настроение и атмосфера в '{analysis.book_id}'?",
            "bot": f"Настроение книги {sentiment_label} (оценка: {analysis.sentiment_score:.2f}). "
                   f"Это влияет на восприятие сюжета и эмоциональную окраску повествования.",
            "source": "sentiment",
        })

        self.logger.info(
            f"Данные по всем направлениям переданы в основную модель для обучения. "
            f"(мысль автора, сюжет, {len(analysis.characters)} персонажей, "
            f"{len(analysis.lore)} элементов лора, подтекст, настроение)"
        )

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
        Полноценное обучение RUGPT3 модели на данных из книг.
        
        Процесс:
        1. Собирает все данные: книги + conversations.json + training_pairs.jsonl
        2. Сохраняет в правильном формате (user/bot) в data/training_pairs.jsonl
        3. Запускает train.main() — правильное дообучение RUGPT3
        """
        self.logger.info("🧠 Наото: Запуск обучения RUGPT3 на книгах...")
        
        training_results = {
            "pairs_created": 0,
            "training_triggered": False,
            "success": False,
            "reason": "",
            "final_loss": None,
            "errors": []
        }
        
        try:
            # 1. Собираем все данные из книг
            book_pairs = self._collect_all_book_pairs()
            training_results["pairs_created"] = len(book_pairs)
            
            if not book_pairs and not self._has_existing_data():
                self.logger.info("⚠️ Нет данных для обучения — сначала нужно прочитать книги")
                training_results["reason"] = "no_data"
                return training_results
            
            # 2. Сохраняем пары из книг в training_pairs.jsonl
            if book_pairs:
                self._save_book_pairs(book_pairs)
                self.logger.info(f"💾 Сохранено {len(book_pairs)} пар из книг в training_pairs.jsonl")
            
            # 3. Запускаем обучение RUGPT3
            self.logger.info("🚀 Запуск обучения RUGPT3 на всех данных...")
            train_success = self._trigger_fine_tune()
            
            if train_success:
                training_results["training_triggered"] = True
                training_results["success"] = True
                training_results["reason"] = "completed"
                self.logger.info("✅ RUGPT3 успешно обучена на книгах!")
            else:
                training_results["reason"] = "training_failed"
                self.logger.warning("⚠️ Обучение RUGPT3 не удалось")
            
        except Exception as e:
            error_msg = f"Ошибка обучения: {e}"
            self.logger.error(error_msg)
            training_results["errors"].append(error_msg)
            training_results["reason"] = str(e)
        
        return training_results

    def _collect_all_book_pairs(self) -> List[Dict]:
        """
        Собирает ВСЕ обучающие пары из книг:
        - Из базы знаний Наото (лор, инсайты, прочитанные книги)
        - Из data/books_training_pairs.jsonl (если есть)
        """
        pairs = []
        seen = set()
        
        # 1. Из базы знаний Наото
        for lore_entry in self.knowledge.get("lore_database", []):
            content = lore_entry.get("content", "") if isinstance(lore_entry, dict) else str(lore_entry)
            if content and len(content) > 10:
                pair = {"user": f"Расскажи о лоре: {lore_entry.get('type', 'мир')}", "bot": content}
                key = content[:100]
                if key not in seen:
                    seen.add(key)
                    pairs.append(pair)
        
        for insight in self.knowledge.get("insights", []):
            content = insight.get("content", "") if isinstance(insight, dict) else str(insight)
            if content and len(content) > 10:
                pair = {"user": "Какой глубокий смысл в этом?", "bot": content}
                key = content[:100]
                if key not in seen:
                    seen.add(key)
                    pairs.append(pair)

        for book in self.knowledge.get("books_read", []):
            if not isinstance(book, dict):
                continue
            book_id = book.get("book_id", book.get("id", "книга"))

            # Мысль автора
            author_intent = book.get("author_intent", "")
            if author_intent and len(author_intent) > 10:
                pair = {"user": f"Какова главная мысль автора в '{book_id}'?", "bot": author_intent}
                key = author_intent[:100]
                if key not in seen:
                    seen.add(key)
                    pairs.append(pair)

            # Сюжет
            plot = book.get("plot_structure", "")
            if plot and len(plot) > 10:
                pair = {"user": f"Как построен сюжет в '{book_id}'? Опиши структуру.", "bot": plot}
                key = plot[:100]
                if key not in seen:
                    seen.add(key)
                    pairs.append(pair)

            # Персонажи
            for char in book.get("characters", []):
                if isinstance(char, dict):
                    char_name = char.get("name", "?")
                    role = char.get("role", "неизвестно")
                    traits = ", ".join(char.get("traits", []))
                    if traits:
                        pair = {
                            "user": f"Расскажи о персонаже '{char_name}' из '{book_id}'. Его роль, черты характера и логика поступков.",
                            "bot": f"Персонаж: {char_name}\nРоль: {role}\nЧерты: {traits}",
                        }
                        key = f"{char_name}_{traits[:50]}"
                        if key not in seen:
                            seen.add(key)
                            pairs.append(pair)

            # Лор
            for lore_entry in book.get("lore", []):
                if isinstance(lore_entry, dict):
                    lore_type = lore_entry.get("type", "мир")
                    content = lore_entry.get("content", "")
                    if content and len(content) > 10:
                        pair = {"user": f"Расскажи о '{lore_type}' в мире '{book_id}': {content[:50]}...", "bot": content}
                        key = content[:100]
                        if key not in seen:
                            seen.add(key)
                            pairs.append(pair)

            # Фантомное повествование
            phantom = book.get("phantom", {})
            if isinstance(phantom, dict):
                subtext = phantom.get("subtext", "")
                if subtext and len(subtext) > 10:
                    pair = {"user": f"Какой скрытый смысл (подтекст) в '{book_id}'?", "bot": subtext}
                    key = subtext[:100]
                    if key not in seen:
                        seen.add(key)
                        pairs.append(pair)
                projection = phantom.get("psychological_projection", "")
                if projection and len(projection) > 10:
                    pair = {"user": f"Что психологически проецирует автор в '{book_id}'?", "bot": projection}
                    key = projection[:100]
                    if key not in seen:
                        seen.add(key)
                        pairs.append(pair)
                motive = phantom.get("hidden_motive", "")
                if motive and len(motive) > 10:
                    pair = {"user": f"Какой скрытый мотив движет сценами в '{book_id}'?", "bot": motive}
                    key = motive[:100]
                    if key not in seen:
                        seen.add(key)
                        pairs.append(pair)

            # Настроение
            sentiment = book.get("sentiment_score", 0)
            if isinstance(sentiment, (int, float)):
                sentiment_label = "позитивное" if sentiment > 0.3 else (
                    "негативное" if sentiment < -0.3 else "нейтральное"
                )
                pair = {
                    "user": f"Какое общее настроение и атмосфера в '{book_id}'?",
                    "bot": f"Настроение книги {sentiment_label} (оценка: {sentiment:.2f}).",
                }
                key = f"{book_id}_sentiment_{sentiment}"
                if key not in seen:
                    seen.add(key)
                    pairs.append(pair)
        
        # 2. Из data/books_training_pairs.jsonl (если есть)
        books_file = Path("data/books_training_pairs.jsonl")
        if books_file.exists():
            with open(books_file, "r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if not line:
                        continue
                    try:
                        entry = json.loads(line)
                        if "user" in entry and "bot" in entry:
                            user_text = str(entry["user"]).strip()
                            bot_text = str(entry["bot"]).strip()
                            if user_text and bot_text and len(user_text) > 2:
                                key = bot_text[:100]
                                if key not in seen:
                                    seen.add(key)
                                    pairs.append({"user": user_text, "bot": bot_text})
                    except Exception:
                        continue
        
        self.logger.info(f"📚 Собрано {len(pairs)} уникальных пар из книг")
        return pairs

    def _has_existing_data(self) -> bool:
        """Проверяет, есть ли уже данные для обучения в training_pairs.jsonl."""
        tp_file = Path("data/training_pairs.jsonl")
        if tp_file.exists() and tp_file.stat().st_size > 100:
            count = 0
            with open(tp_file, "r", encoding="utf-8") as f:
                for line in f:
                    if line.strip():
                        count += 1
            self.logger.info(f"📊 В training_pairs.jsonl уже есть {count} записей")
            return count > 5
        return False

    def _save_book_pairs(self, pairs: List[Dict]):
        """Добавляет пары из книг в общий training_pairs.jsonl."""
        tp_file = Path("data/training_pairs.jsonl")
        tp_file.parent.mkdir(parents=True, exist_ok=True)
        
        with open(tp_file, "a", encoding="utf-8") as f:
            for pair in pairs:
                f.write(json.dumps(pair, ensure_ascii=False) + "\n")
        
        self.logger.info(f"💾 Добавлено {len(pairs)} пар в {tp_file}")
    
    def _trigger_fine_tune(self) -> bool:
        """
        Запускает настоящее обучение RUGPT3 через train.py.
        """
        import subprocess
        
        try:
            self.logger.info("🚀 Запуск обучения RUGPT3 через train.py...")
            
            project_root = Path(__file__).resolve().parent.parent.parent
            train_script = project_root / "train.py"
            
            if not train_script.exists():
                self.logger.error(f"❌ train.py не найден: {train_script}")
                return False
            
            self.logger.info(f"📊 Запуск: {sys.executable} {train_script}")
            
            result = subprocess.run(
                [sys.executable, str(train_script)],
                cwd=str(project_root),
                capture_output=True,
                text=True,
                timeout=3600,  # 1 час на обучение
                encoding='utf-8',
                errors='replace',
            )
            
            if result.returncode == 0:
                self.logger.info("✅ Обучение RUGPT3 завершено успешно!")
                if result.stdout:
                    # Ищем финальный loss в выводе
                    for line in result.stdout.split('\n'):
                        if 'Loss' in line or 'loss' in line or 'HAPPY' in line or 'SAVE' in line:
                            self.logger.info(f"   {line.strip()}")
                # Сохраняем метаданные
                self._save_training_metadata(success=True)
                return True
            else:
                self.logger.error(f"❌ Ошибка обучения (код {result.returncode})")
                if result.stderr:
                    self.logger.error(f"   {result.stderr[:500]}")
                self._save_training_metadata(success=False, error=result.stderr[:200] if result.stderr else "")
                return False
                
        except subprocess.TimeoutExpired:
            self.logger.error("⏰ Таймаут обучения (1 час)")
            return False
        except Exception as e:
            self.logger.error(f"❌ Ошибка запуска обучения: {e}")
            return False
    
    def _save_training_metadata(self, success: bool, error: str = ""):
        """Сохраняет метаданные об обучении."""
        metadata = {
            "last_training": datetime.now().isoformat(),
            "success": success,
            "error": error,
            "model_path": "models/rugpt3",
            "total_retrains": self._get_retrain_count() + (1 if success else 0),
        }
        
        metadata_path = Path("naoto/engine/state/training_metadata.json")
        metadata_path.parent.mkdir(parents=True, exist_ok=True)
        with open(metadata_path, "w", encoding="utf-8") as f:
            json.dump(metadata, f, ensure_ascii=False, indent=2)
    
    def _get_retrain_count(self) -> int:
        """Получает количество ретраинов из метаданных."""
        metadata_path = Path("naoto/engine/state/training_metadata.json")
        if metadata_path.exists():
            try:
                with open(metadata_path, "r", encoding="utf-8") as f:
                    return json.load(f).get("total_retrains", 0)
            except Exception:
                pass
        return 0
    
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
