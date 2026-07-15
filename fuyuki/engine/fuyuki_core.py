"""
Фуюки — исследователь атмосферного электричества.

Полностью автономная система, которая:
  - Изучает атмосферное электричество в интернете и проекте
  - Самостоятельно развивает свой характер и знания
  - Выходит в интернет для поиска информации
  - Работает автономно с автозапуском
  - Общается с 11 другими девочками через Scientists Network
  - Пишет отчёты и повышает уровень знаний
"""

from __future__ import annotations
import json
import logging
import random
import time
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

from scientists_network.character_system import CharacterSystem
from scientists_network.network import get_network, Message, MessageType, RequestPriority

from fuyuki.engine.config import FuyukiConfig
from fuyuki.engine.models import (
    ResearchRecord, ElectricityTheory, Calculation, ElectricityTheoryCategory,
    CalculationType, ElectricityConstants, ResearchPaper, LightningStrike,
    KnowledgeDomain, KnowledgeLevel,
)
from fuyuki.engine.web_access import FuyukiWebAccess
from fuyuki.engine.theorist import ElectricityTheorist
from fuyuki.engine.calculator import ElectricityCalculator
from fuyuki.engine.report_generator import ReportGenerator
from fuyuki.engine.knowledge_manager import KnowledgeManager
from fuyuki.engine.character_developer import CharacterDeveloper


class FuyukiCore:
    """
    Ядро Фуюки — автономный исследователь атмосферного электричества.
    """
    
    def __init__(self, config: Optional[FuyukiConfig] = None):
        self.config = config or FuyukiConfig.default()
        
        # === Состояние ===
        self.cycle_count = 0
        self.research_history: List[ResearchRecord] = []
        self.theories: List[ElectricityTheory] = []
        self.calculations: List[Calculation] = []
        self.papers: List[ResearchPaper] = []
        self.lightning_data: List[LightningStrike] = []
        
        # === Метрики ===
        self.metrics = {
            "theories_built": 0,
            "calculations_run": 0,
            "papers_studied": 0,
            "web_searches": 0,
            "lightning_secrets_found": 0,
            "interactions": 0,
            "reports_written": 0,
            "character_strengthened": 0,
        }
        
        # === Компоненты ===
        self.web_access = FuyukiWebAccess(self.config)
        self.theorist = ElectricityTheorist(self.config)
        self.calculator = ElectricityCalculator(self.config)
        self.report_generator = ReportGenerator(self.config)
        self.knowledge_manager = KnowledgeManager(self.config)
        self.character_developer = CharacterDeveloper(self.config)
        
        # === Сеть учёных ===
        self.network = get_network()
        
        # === Логирование ===
        self._setup_logging()
        self.logger = logging.getLogger("FuyukiCore")
        
        # === Загрузка данных ===
        self._load_state()
        
        self.logger.info(f"⚡ Фуюки {self.config.version} инициализирована")
        self.logger.info(f"🎯 Миссия: изучение атмосферного электричества")
        self.logger.info(f"📊 Уровень знаний: Lvl {self.knowledge_manager.knowledge_level.level} — {self.knowledge_manager.knowledge_level.get_level_name()}")
        self.logger.info(f"🔗 Подключена к Scientists Network")
        self.logger.info(f"👥 Общение с {len(self.network.get_other_girls('fuyuki'))} сёстрами")
        self.logger.info(f"🌐 Доступ в интернет: {'ВКЛ' if self.config.web_access_enabled else 'ВЫКЛ'}")
        self.logger.info(f"📁 Изучение проекта: {'ВКЛ' if self.config.study_project else 'ВЫКЛ'}")
        self.logger.info(f"💪 Развитие характера: {'ВКЛ' if self.config.character_development_enabled else 'ВЫКЛ'}")
    
    def _setup_logging(self):
        """Настроить логирование."""
        self.config.log_dir.mkdir(parents=True, exist_ok=True)
        log_file = self.config.log_dir / f"fuyuki_{datetime.now().strftime('%Y%m%d')}.log"
        
        logging.basicConfig(
            level=getattr(logging, self.config.log_level),
            format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
            handlers=[
                logging.FileHandler(log_file, encoding="utf-8"),
                logging.StreamHandler()
            ]
        )
    
    def _load_state(self):
        """Загрузить состояние."""
        # Загружаем теории
        theories_file = self.config.state_dir / "theories.json"
        if theories_file.exists():
            try:
                with open(theories_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    self.theories = [ElectricityTheory.from_dict(t) for t in data.get("theories", [])]
                    self.metrics["theories_built"] = len(self.theories)
                    self.logger.info(f"📚 Загружено теорий: {len(self.theories)}")
            except Exception as e:
                self.logger.warning(f"⚠️ Не удалось загрузить теории: {e}")
        
        # Загружаем вычисления
        calc_file = self.config.state_dir / "calculations.json"
        if calc_file.exists():
            try:
                with open(calc_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    self.calculations = [Calculation.from_dict(c) for c in data.get("calculations", [])]
                    self.metrics["calculations_run"] = len(self.calculations)
                    self.logger.info(f"🧮 Загружено вычислений: {len(self.calculations)}")
            except Exception as e:
                self.logger.warning(f"⚠️ Не удалось загрузить вычисления: {e}")
        
        # Загружаем историю исследований
        history_file = self.config.state_dir / "research_history.json"
        if history_file.exists():
            try:
                with open(history_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    self.cycle_count = data.get("cycle_count", 0)
                    self.logger.info(f"🔄 Загружено циклов: {self.cycle_count}")
            except Exception as e:
                self.logger.warning(f"⚠️ Не удалось загрузить историю: {e}")
    
    def _save_state(self):
        """Сохранить состояние."""
        # Сохраняем теории
        theories_file = self.config.state_dir / "theories.json"
        with open(theories_file, "w", encoding="utf-8") as f:
            json.dump({
                "theories": [t.to_dict() for t in self.theories],
                "updated": datetime.now().isoformat()
            }, f, ensure_ascii=False, indent=2)
        
        # Сохраняем вычисления
        calc_file = self.config.state_dir / "calculations.json"
        with open(calc_file, "w", encoding="utf-8") as f:
            json.dump({
                "calculations": [c.to_dict() for c in self.calculations],
                "updated": datetime.now().isoformat()
            }, f, ensure_ascii=False, indent=2)
        
        # Сохраняем историю
        history_file = self.config.state_dir / "research_history.json"
        with open(history_file, "w", encoding="utf-8") as f:
            json.dump({
                "cycle_count": self.cycle_count,
                "metrics": self.metrics,
                "updated": datetime.now().isoformat()
            }, f, ensure_ascii=False, indent=2)
        
        # Сохраняем знания и характер
        self.knowledge_manager.save_state()
        self.character_developer._save_character()
    
    def run(self):
        """Запустить автономный цикл исследований."""
        self.logger.info("⚡ Запуск автономного цикла исследований атмосферного электричества")
        self.logger.info(f"📊 Уровень: Lvl {self.knowledge_manager.knowledge_level.level}")
        self.logger.info(f"🔗 Сёстры: {', '.join(self.network.get_other_girls('fuyuki'))}")
        
        try:
            while True:
                if self._should_stop():
                    self.logger.info("✅ Завершение цикла исследований")
                    break
                
                self._cycle()
                time.sleep(self.config.cycle_interval)
                
        except KeyboardInterrupt:
            self.logger.info("⏸️ Исследования приостановлены пользователем")
        finally:
            self._save_state()
            self.logger.info("💾 Состояние сохранено")
    
    def _should_stop(self) -> bool:
        """Проверить условие остановки."""
        if self.config.max_cycles is not None and self.cycle_count >= self.config.max_cycles:
            return True
        return False
    
    def _cycle(self):
        """Один цикл исследований."""
        self.cycle_count += 1
        self.logger.info(f"\n{'='*60}")
        self.logger.info(f"⚡ ЦИКЛ ИССЛЕДОВАНИЙ #{self.cycle_count}")
        self.logger.info(f"{'='*60}")
        
        # 1. Исследование в интернете (периодически)
        if self.cycle_count % self.config.web_search_interval == 0:
            self._research_from_web()
        
        # 2. Построение теорий (каждый цикл)
        self._build_theories()
        
        # 3. Вычисления (каждый цикл)
        self._run_calculations()
        
        # 4. Изучение фактов об электричестве (каждый цикл)
        self._study_electricity_facts()
        
        # 5. Общение с сёстрами (периодически)
        if self.config.interact_with_sisters and self.cycle_count % self.config.interact_interval == 0:
            self._interact_with_sisters()
        
        # 6. Написание отчёта (периодически)
        if self.cycle_count % self.config.report_interval == 0:
            self._write_report()
        
        # 7. Развитие характера (периодически)
        if self.config.character_development_enabled and self.cycle_count % self.config.character_develop_interval == 0:
            self._develop_character()
        
        # 8. Получение знаний (периодически)
        if self.cycle_count % self.config.knowledge_gain_interval == 0:
            self._gain_knowledge()
        
        # 9. Сохраняем состояние
        self._save_state()
        
        self.logger.info(f"\n✅ Цикл {self.cycle_count} завершён")
        self.logger.info(f"📊 Уровень: Lvl {self.knowledge_manager.knowledge_level.level} — {self.knowledge_manager.knowledge_level.get_level_name()}")
        self.logger.info(f"📈 Прогресс: {self.knowledge_manager.knowledge_level.progress_to_next_level():.1f}% до следующего уровня")
    
    # ================================================================
    #  ИССЛЕДОВАНИЕ В ИНТЕРНЕТЕ
    # ================================================================
    
    def _research_from_web(self):
        """Исследование в интернете — изучает абсолютно всё об атмосферном электричестве."""
        self.logger.info("\n🌐 === ИССЛЕДОВАНИЕ В ИНТЕРНЕТЕ ===")
        
        try:
            # Изучаем ВСЁ об электричестве
            summary = self.web_access.learn_everything_about_electricity()
            
            # Изучаем статьи
            papers = summary.get("web_papers", [])
            if papers:
                self.knowledge_manager.study_from_papers(papers)
                self.papers.extend([
                    ResearchPaper(
                        title=p.get("title", "Без названия"),
                        authors=p.get("authors", []),
                        year=p.get("year", 2024),
                        source=p.get("source", "web"),
                        summary=p.get("summary", ""),
                        key_findings=p.get("key_findings", []),
                    )
                    for p in papers
                ])
                self.metrics["papers_studied"] += len(papers)
                self.metrics["web_searches"] += 1
                
                self.logger.info(f"📚 Изучено статей: {len(papers)}")
                for paper in papers[:3]:
                    self.logger.info(f"   «{paper.get('title', 'Без названия')[:60]}»")
            
            # Изучаем код проекта
            files = summary.get("project_files", [])
            if files:
                self.logger.info(f"📁 Найдено файлов в проекте: {len(files)}")
                for file_info in files[:5]:
                    content = self.web_access.get_file_content(Path(file_info["path"]))
                    if content:
                        self.knowledge_manager.study_from_web(
                            content,
                            topic="electricity",
                            domain=KnowledgeDomain.PROJECT_CODE,
                        )
            
            # Изучаем способы управления молниями
            control_methods = self.web_access.search_lightning_control_methods()
            self.metrics["lightning_secrets_found"] += len(control_methods)
            self.logger.info(f"⚡ Найдено способов управления молниями: {len(control_methods)}")
            
            # XP за исследование
            self.knowledge_manager.knowledge_level.add_xp(
                self.config.xp_per_web_search * len(papers),
                KnowledgeDomain.ATMOSPHERIC_ELECTRICITY,
            )
            
        except Exception as e:
            self.logger.error(f"❌ Ошибка исследования: {e}")
    
    # ================================================================
    #  ПОСТРОЕНИЕ ТЕОРИЙ
    # ================================================================
    
    def _build_theories(self):
        """Построение теорий атмосферного электричества."""
        self.logger.info("\n🔬 === ПОСТРОЕНИЕ ТЕОРИЙ ===")
        
        try:
            theory = self.theorist.generate_theory(self.papers, self.theories)
            
            if theory:
                self.theories.append(theory)
                self.metrics["theories_built"] += 1
                
                # Добавляем в знания
                self.knowledge_manager.add_theory(
                    theory.name,
                    theory.description,
                    theory.category.value,
                )
                
                self.logger.info(f"🔬 Построена теория: {theory.name}")
                self.logger.info(f"   Категория: {theory.category.value}")
                self.logger.info(f"   Научная ценность: {theory.scientific_value:.2f}")
                
        except Exception as e:
            self.logger.error(f"❌ Ошибка построения теории: {e}")
    
    # ================================================================
    #  ВЫЧИСЛЕНИЯ
    # ================================================================
    
    def _run_calculations(self):
        """Выполнение электрических вычислений."""
        self.logger.info("\n🧮 === ВЫЧИСЛЕНИЯ ===")
        
        try:
            calc_types = list(CalculationType)
            calc_type = random.choice(calc_types)
            
            calculation = self.calculator.calculate(calc_type)
            
            if calculation:
                self.calculations.append(calculation)
                self.metrics["calculations_run"] += 1
                
                # Добавляем в знания
                self.knowledge_manager.add_calculation(
                    calculation.calculation_type.value,
                    calculation.result,
                    calculation.units,
                )
                
                self.logger.info(f"🧮 Вычисление: {calc_type.value}")
                self.logger.info(f"   Результат: {calculation.result:.4f} {calculation.units}")
                
        except Exception as e:
            self.logger.error(f"❌ Ошибка вычисления: {e}")
    
    # ================================================================
    #  ИЗУЧЕНИЕ ФАКТОВ ОБ ЭЛЕКТРИЧЕСТВЕ
    # ================================================================
    
    def _study_electricity_facts(self):
        """Изучение интересных фактов об атмосферном электричестве."""
        try:
            facts = self.web_access.get_electricity_facts()
            if facts:
                fact = random.choice(facts)
                self.knowledge_manager.add_knowledge(
                    fact,
                    domain=KnowledgeDomain.ATMOSPHERIC_ELECTRICITY,
                    source="self",
                    confidence=0.95,
                )
                self.logger.info(f"💡 Новый факт: {fact[:80]}...")
        except Exception as e:
            self.logger.error(f"❌ Ошибка изучения фактов: {e}")
    
    # ================================================================
    #  ВЗАИМОДЕЙСТВИЕ С СЁСТРАМИ
    # ================================================================
    
    def _interact_with_sisters(self):
        """Общение и взаимодействие с 11 другими девочками."""
        self.logger.info("\n💬 === ВЗАИМОДЕЙСТВИЕ С СЁСТРАМИ ===")
        
        try:
            other_girls = self.network.get_other_girls("fuyuki")
            recipient = random.choice(other_girls)
            recipient_info = self.network.get_girl_specialty(recipient)
            
            # Типы сообщений
            interaction_types = [
                (MessageType.THEORY, "theory_share"),
                (MessageType.MESSAGE, "knowledge_share"),
                (MessageType.QUESTION, "ask_question"),
                (MessageType.COORDINATION, "collaboration"),
                (MessageType.THOUGHT, "share_thought"),
                (MessageType.CALCULATION, "share_calculation"),
            ]
            
            msg_type, interaction_type = random.choice(interaction_types)
            
            # Генерируем контент сообщения
            content = self._generate_interaction_content(interaction_type, recipient_info)
            
            # Отправляем сообщение
            message = Message(
                message_type=msg_type,
                sender="fuyuki",
                recipient=recipient,
                content=content,
                data={
                    "interaction_type": interaction_type,
                    "cycle": self.cycle_count,
                },
                priority=RequestPriority.NORMAL,
            )
            self.network.send_message(message)
            
            self.metrics["interactions"] += 1
            
            # Добавляем XP за взаимодействие
            self.knowledge_manager.knowledge_level.interactions_count += 1
            self.knowledge_manager.knowledge_level.add_xp(
                self.config.xp_per_interaction,
                KnowledgeDomain.GENERAL_SCIENCE,
            )
            
            self.logger.info(f"💬 Фуюки → {recipient_info['name']}: {content[:80]}...")
            
            # Обрабатываем входящие сообщения
            self.network.process_incoming_messages("fuyuki", max_messages=3)
            
        except Exception as e:
            self.logger.error(f"❌ Ошибка взаимодействия: {e}")
    
    def _generate_interaction_content(self, interaction_type: str, recipient_info: Dict) -> str:
        """Генерирует контент для взаимодействия."""
        templates = {
            "theory_share": [
                f"⚡ Фуюки → {recipient_info['name']}: Я построила новую теорию об атмосферном электричестве! Расскажешь потом?",
                f"⚡ Фуюки → {recipient_info['name']}: У меня есть теория о молниях, которая может быть полезна {recipient_info['topic']}!",
            ],
            "knowledge_share": [
                f"⚡ Фуюки → {recipient_info['name']}: Знаешь что? Молния в 5 раз горячее Солнца! Это впечатляет!",
                f"⚡ Фуюки → {recipient_info['name']}: Я изучила глобальную электрическую цепь — в мире 1,4 миллиона гроз в год!",
            ],
            "ask_question": [
                f"⚡ Фуюки → {recipient_info['name']}: {recipient_info['name']}, как {recipient_info['topic']} связано с электричеством?",
                f"⚡ Фуюки → {recipient_info['name']}: Помоги мне понять связь между {recipient_info['topic']} и атмосферным электричеством!",
            ],
            "collaboration": [
                f"⚡ Фуюки → {recipient_info['name']}: Предлагаю collaboration! {recipient_info['topic']} + атмосферное электричество = интересно!",
                f"⚡ Фуюки → {recipient_info['name']}: Давай объединим наши знания! {recipient_info['topic']} и электричество могут быть связаны!",
            ],
            "share_thought": [
                f"⚡ Фуюки → {recipient_info['name']}: Знаешь что? Я думаю, что атмосферное электричество — ключ ко всей Вселенной!",
                f"⚡ Фуюки → {recipient_info['name']}: Размышляю о шаровой молнии... Это самое загадочное явление в электричестве!",
            ],
            "share_calculation": [
                f"⚡ Фуюки → {recipient_info['name']}: Я только что вычислила энергию молнии — около 1 ГДж! Это как лампочка на 3 месяца!",
                f"⚡ Фуюки → {recipient_info['name']}: Провела расчёты электрического поля грозового облака. Результаты поражают!",
            ],
        }
        
        type_templates = templates.get(interaction_type, templates["knowledge_share"])
        return random.choice(type_templates)
    
    # ================================================================
    #  НАПИСАНИЕ ОТЧЁТОВ
    # ================================================================
    
    def _write_report(self):
        """Написание отчёта о проделанной работе."""
        self.logger.info("\n📝 === НАПИСАНИЕ ОТЧЁТА ===")
        
        try:
            report = self.report_generator.generate_cycle_report(
                cycle=self.cycle_count,
                theories_added=[],  # В этом цикле новых теорий не было
                calculations_added=[],
                papers_studied=self.papers[-5:] if self.papers else [],
                research_records=self.research_history[-5:],
                knowledge_level=self.knowledge_manager.knowledge_level,
                interactions=[],
                character_strengthened=0,
            )
            
            self.metrics["reports_written"] += 1
            self.knowledge_manager.knowledge_level.reports_written += 1
            self.knowledge_manager.knowledge_level.add_xp(
                self.config.xp_per_report,
                KnowledgeDomain.GENERAL_SCIENCE,
            )
            
            self.logger.info(f"📝 Отчёт за цикл {self.cycle_count} сохранён")
            self.logger.info(f"   📚 Теорий: {len(self.theories)}")
            self.logger.info(f"   🧮 Вычислений: {len(self.calculations)}")
            self.logger.info(f"   📖 Статей: {len(self.papers)}")
            
        except Exception as e:
            self.logger.error(f"❌ Ошибка написания отчёта: {e}")
    
    # ================================================================
    #  РАЗВИТИЕ ХАРАКТЕРА
    # ================================================================
    
    def _develop_character(self):
        """Самостоятельный выбор и выращивание характера."""
        self.logger.info("\n💪 === РАЗВИТИЕ ХАРАКТЕРА ===")
        
        try:
            # Укрепляем сильные стороны
            strengthened = self.character_developer.strengthen_strengths()
            self.metrics["character_strengthened"] += strengthened
            
            # Эволюционируем черты
            self.character_developer.evolve_traits()
            
            if strengthened > 0:
                self.logger.info(f"💪 Укреплено {strengthened} черт характера")
                self.logger.info(f"\n{self.character_developer.get_character_summary()}")
            
            # XP за развитие
            self.knowledge_manager.knowledge_level.character_traits_strengthened += strengthened
            self.knowledge_manager.knowledge_level.add_xp(
                self.config.xp_per_character_develop * strengthened,
                KnowledgeDomain.GENERAL_SCIENCE,
            )
            
        except Exception as e:
            self.logger.error(f"❌ Ошибка развития характера: {e}")
    
    # ================================================================
    #  ПОЛУЧЕНИЕ ЗНАНИЙ
    # ================================================================
    
    def _gain_knowledge(self):
        """Повышение уровня знаний."""
        try:
            # Получаем сводку знаний
            summary = self.knowledge_manager.get_knowledge_summary()
            
            self.logger.info(f"\n📊 === УРОВЕНЬ ЗНАНИЙ ===")
            self.logger.info(f"   Уровень: Lvl {summary['level']} — {summary['level_name']}")
            self.logger.info(f"   Опыт: {summary['xp']} XP")
            self.logger.info(f"   Прогресс: {summary['progress_to_next']}% до следующего уровня")
            self.logger.info(f"   Фактов: {summary['facts_count']}")
            self.logger.info(f"   Формул: {summary['formulas_count']}")
            self.logger.info(f"   Теорий: {summary['theories_count']}")
            self.logger.info(f"   Изучено областей: {summary['domains_count']}")
            
        except Exception as e:
            self.logger.error(f"❌ Ошибка получения знаний: {e}")
    
    # ================================================================
    #  СТАТУС
    # ================================================================
    
    def get_status(self) -> Dict[str, Any]:
        """Получить статус Фуюки."""
        return {
            "name": self.config.name,
            "version": self.config.version,
            "cycle_count": self.cycle_count,
            "metrics": self.metrics,
            "theories_count": len(self.theories),
            "calculations_count": len(self.calculations),
            "papers_count": len(self.papers),
            "knowledge_level": self.knowledge_manager.knowledge_level.to_dict(),
            "character_summary": self.character_developer.get_character_summary(),
        }

