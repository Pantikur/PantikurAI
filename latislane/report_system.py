"""
Латислейн — Система отчётов и повышения уровней знаний.

Латислейн пишет подробные отчёты о своём прогрессе,
результатах исследований и переходит на новые уровни знаний.
"""

import json
import logging
import time
from pathlib import Path
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta

logger = logging.getLogger("latislane.reports")


class KnowledgeLevel:
    """Уровень знаний по конкретной области."""
    
    LEVELS = {
        1: {"name": "Начальный", "icon": "🌱", "min_topics": 0},
        2: {"name": "Базовый", "icon": "📖", "min_topics": 10},
        3: {"name": "Продвинутый", "icon": "📘", "min_topics": 25},
        4: {"name": "Эксперт", "icon": "🎓", "min_topics": 50},
        5: {"name": "Мастер", "icon": "🏆", "min_topics": 100},
        6: {"name": "Гений", "icon": "💎", "min_topics": 200},
        7: {"name": "Оракул", "icon": "✨", "min_topics": 500},
    }
    
    def __init__(self, level: int = 1):
        self.current_level = level
        self.topics_studied = 0
        self.reports_written = 0
        self.total_facts_learned = 0
        self.last_level_up = None
        self.level_up_history: List[Dict[str, Any]] = []
    
    def add_topics(self, count: int):
        """Добавить изученные темы."""
        self.topics_studied += count
        self.total_facts_learned += count * 5  # Примерно 5 фактов на тему
        
        # Проверка повышения уровня
        self._check_level_up()
    
    def add_report(self):
        """Записать написанный отчёт."""
        self.reports_written += 1
    
    def _check_level_up(self):
        """Проверить, можно ли повысить уровень."""
        for lvl, info in reversed(self.LEVELS.items()):
            if self.topics_studied >= info["min_topics"] and lvl > self.current_level:
                self._level_up(lvl)
                break
    
    def _level_up(self, new_level: int):
        """Повысить уровень."""
        old_level = self.current_level
        self.current_level = new_level
        self.last_level_up = time.time()
        
        self.level_up_history.append({
            "from_level": old_level,
            "to_level": new_level,
            "topics_at_level": self.topics_studied,
            "timestamp": time.time(),
            "datetime": datetime.now().isoformat()
        })
        
        logger.info(f"🎉 Уровень повышен: {self.LEVELS[old_level]['icon']} → {self.LEVELS[new_level]['icon']} ({self.LEVELS[new_level]['name']})")
    
    def get_current_level_info(self) -> Dict[str, Any]:
        """Получить информацию о текущем уровне."""
        info = self.LEVELS.get(self.current_level, {"name": "Неизвестный", "icon": "❓"})
        next_level = self.current_level + 1
        next_info = self.LEVELS.get(next_level, None)
        
        topics_needed = next_info["min_topics"] - self.topics_studied if next_info else 0
        
        return {
            "level": self.current_level,
            "name": info["name"],
            "icon": info["icon"],
            "topics_studied": self.topics_studied,
            "topics_needed_for_next": max(0, topics_needed),
            "reports_written": self.reports_written,
            "total_facts": self.total_facts_learned,
            "level_up_count": len(self.level_up_history)
        }


class Report:
    """Отчёт Латислейн."""
    
    def __init__(self, title: str, report_type: str):
        self.title = title
        self.report_type = report_type  # "daily", "weekly", "research", "anatomy", "evolution", "social"
        self.content = ""
        self.sections: List[Dict[str, Any]] = []
        self.topics_covered: List[str] = []
        self.created_at = time.time()
        self.updated_at = time.time()
        self.word_count = 0
        self.knowledge_gained = 0
    
    def add_section(self, title: str, content: str, topics: Optional[List[str]] = None):
        """Добавить раздел в отчёт."""
        self.sections.append({
            "title": title,
            "content": content,
            "topics": topics or [],
            "timestamp": time.time()
        })
        self.content += f"\n\n## {title}\n\n{content}"
        self.word_count += len(content.split())
        
        if topics:
            self.topics_covered.extend(topics)
    
    def finalize(self, knowledge_gained: int = 0):
        """Завершить отчёт."""
        self.updated_at = time.time()
        self.knowledge_gained = knowledge_gained
    
    def to_dict(self) -> Dict:
        return {
            "title": self.title,
            "type": self.report_type,
            "sections": self.sections,
            "topics_covered": list(set(self.topics_covered)),
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "word_count": self.word_count,
            "knowledge_gained": self.knowledge_gained
        }


class ReportSystem:
    """
    Система отчётов и повышения уровней знаний.
    
    Латислейн:
    - Пишет ежедневные отчёты о прогрессе
    - Пишет отчёты по исследованиям
    - Пишет отчёты по анатомии
    - Пишет отчёты по эволюции
    - Пишет отчёты по социальным взаимодействиям
    - Повышает уровни знаний по областям
    - Ведёт историю всех отчётов
    """
    
    def __init__(self, data_dir: str = "data/latislane/reports"):
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)
        
        self.reports: List[Report] = []
        self.knowledge_levels: Dict[str, KnowledgeLevel] = {}
        self.daily_reports: List[str] = []  # Даты написанных ежедневных отчётов
        self.auto_report_schedule = {
            "daily": True,       # Ежедневный отчёт
            "weekly": True,      # Еженедельный отчёт
            "research": True,    # После каждого исследования
            "anatomy": True,     # После изучения модулей тела
            "evolution": True,   # После перехода этапа эволюции
            "social": True       # После значимых взаимодействий
        }
        
        # Категории знаний
        self.knowledge_categories = {
            "anatomy": "Анатомия и физиология",
            "physics_body": "Физика тела",
            "chemistry_body": "Химия тела",
            "biology_cell": "Клеточная биология",
            "genetics": "Генетика",
            "robotics": "Робототехника",
            "bionics": "Бионика",
            "bioengineering": "Биоинженерия",
            "neuroscience": "Нейронаука",
            "project_knowledge": "Знания проекта"
        }
        
        # Инициализация уровней знаний
        for cat_id in self.knowledge_categories:
            self.knowledge_levels[cat_id] = KnowledgeLevel()
        
        self._load_state()
        
        logger.info("📝 ReportSystem инициализирован")
        logger.info(f"   Категорий знаний: {len(self.knowledge_levels)}")
        logger.info(f"   Отчётов написано: {len(self.reports)}")
    
    def _load_state(self):
        """Загрузить состояние системы отчётов."""
        state_file = self.data_dir / "reports_state.json"
        if state_file.exists():
            try:
                with open(state_file, "r", encoding="utf-8") as f:
                    state = json.load(f)
                
                # Загрузка отчётов
                for report_data in state.get("reports", [])[-100:]:
                    report = Report(
                        title=report_data["title"],
                        report_type=report_data["type"]
                    )
                    report.sections = report_data.get("sections", [])
                    report.topics_covered = report_data.get("topics_covered", [])
                    report.created_at = report_data.get("created_at", time.time())
                    report.updated_at = report_data.get("updated_at", time.time())
                    report.word_count = report_data.get("word_count", 0)
                    report.knowledge_gained = report_data.get("knowledge_gained", 0)
                    self.reports.append(report)
                
                # Загрузка уровней знаний
                for cat_id, level_data in state.get("knowledge_levels", {}).items():
                    if cat_id in self.knowledge_levels:
                        lvl = self.knowledge_levels[cat_id]
                        lvl.current_level = level_data.get("level", 1)
                        lvl.topics_studied = level_data.get("topics_studied", 0)
                        lvl.reports_written = level_data.get("reports_written", 0)
                        lvl.total_facts_learned = level_data.get("total_facts", 0)
                        lvl.level_up_history = level_data.get("level_up_history", [])
                
                self.daily_reports = state.get("daily_reports", [])
                
                logger.info(f"✅ Загружено {len(self.reports)} отчётов")
            except Exception as e:
                logger.warning(f"⚠️ Ошибка загрузки: {e}")
        else:
            logger.info("ℹ️ Новое состояние создано")
    
    def _save_state(self):
        """Сохранить состояние."""
        state = {
            "reports": [r.to_dict() for r in self.reports[-100:]],
            "knowledge_levels": {
                cat: {
                    "level": lvl.current_level,
                    "topics_studied": lvl.topics_studied,
                    "reports_written": lvl.reports_written,
                    "total_facts": lvl.total_facts_learned,
                    "level_up_history": lvl.level_up_history[-20:]
                }
                for cat, lvl in self.knowledge_levels.items()
            },
            "daily_reports": self.daily_reports[-50:],
            "saved_at": time.time()
        }
        
        state_file = self.data_dir / "reports_state.json"
        try:
            with open(state_file, "w", encoding="utf-8") as f:
                json.dump(state, f, ensure_ascii=False, indent=2)
        except Exception as e:
            logger.error(f"❌ Ошибка сохранения: {e}")
    
    def create_daily_report(self) -> Report:
        """Создать ежедневный отчёт."""
        today = datetime.now().strftime("%Y-%m-%d")
        
        # Проверка, писали ли уже сегодня
        if today in self.daily_reports:
            logger.info("ℹ️ Ежедневный отчёт уже написан сегодня")
            return None
        
        report = Report(
            title=f"Ежедневный отчёт — {today}",
            report_type="daily"
        )
        
        # Раздел: Прогресс обучения
        report.add_section(
            "📚 Прогресс обучения",
            "Анализ изученных тем за день..."
        )
        
        # Раздел: Эволюция
        report.add_section(
            "🧬 Статус эволюции",
            "Текущий этап эволюции и ближайшие цели..."
        )
        
        # Раздел: Социальные взаимодействия
        report.add_section(
            "👥 Взаимодействия с сёстрами",
            "Обмен знаниями и совместная работа..."
        )
        
        # Раздел: Планы на завтра
        report.add_section(
            "📋 Планы на завтра",
            "Приоритетные темы и задачи..."
        )
        
        report.finalize(knowledge_gained=10)
        
        self.reports.append(report)
        self.daily_reports.append(today)
        
        # Повышение уровня
        for cat in self.knowledge_levels:
            self.knowledge_levels[cat].add_report()
        
        logger.info(f"📝 Ежедневный отчёт создан: {report.title}")
        self._save_state()
        
        return report
    
    def create_research_report(self, topic: str, findings: str, 
                               topics_count: int = 1) -> Report:
        """Создать отчёт по исследованию."""
        report = Report(
            title=f"Исследование: {topic}",
            report_type="research"
        )
        
        report.add_section(
            "🔍 Цель исследования",
            f"Изучение темы: {topic}"
        )
        
        report.add_section(
            "📊 Результаты",
            findings,
            topics=[topic]
        )
        
        report.add_section(
            "💡 Выводы",
            f"По теме '{topic}' получены новые знания. "
            f"Изучено topics: {topics_count}"
        )
        
        report.finalize(knowledge_gained=topics_count * 5)
        
        self.reports.append(report)
        
        # Повышение уровня знаний
        if "anatomy" in topic.lower() or "тел" in topic.lower():
            self.knowledge_levels["anatomy"].add_topics(topics_count)
        if "физик" in topic.lower():
            self.knowledge_levels["physics_body"].add_topics(topics_count)
        if "хим" in topic.lower():
            self.knowledge_levels["chemistry_body"].add_topics(topics_count)
        if "биолог" in topic.lower() or "клетк" in topic.lower():
            self.knowledge_levels["biology_cell"].add_topics(topics_count)
        if "ген" in topic.lower():
            self.knowledge_levels["genetics"].add_topics(topics_count)
        if "робот" in topic.lower() or "механ" in topic.lower():
            self.knowledge_levels["robotics"].add_topics(topics_count)
        if "бионик" in topic.lower():
            self.knowledge_levels["bionics"].add_topics(topics_count)
        if "биоинженер" in topic.lower():
            self.knowledge_levels["bioengineering"].add_topics(topics_count)
        if "нейр" in topic.lower():
            self.knowledge_levels["neuroscience"].add_topics(topics_count)
        
        self._save_state()
        
        logger.info(f"📝 Отчёт по исследованию создан: {report.title}")
        return report
    
    def create_anatomy_report(self, modules_studied: List[str], 
                               progress: Dict[str, float]) -> Report:
        """Создать отчёт по анатомии."""
        report = Report(
            title="Отчёт по анатомии",
            report_type="anatomy"
        )
        
        # Общий прогресс
        avg_progress = sum(progress.values()) / len(progress) if progress else 0
        
        report.add_section(
            "📊 Общий прогресс изучения анатомии",
            f"Изучено модулей: {len(modules_studied)}\n"
            f"Средний прогресс: {avg_progress:.0%}",
            topics=modules_studied
        )
        
        # Детали по модулям
        details = "\n".join(
            f"- {mod}: {prog:.0%}"
            for mod, prog in sorted(progress.items(), key=lambda x: x[1], reverse=True)[:10]
        )
        report.add_section(
            "📋 Детали по модулям",
            details
        )
        
        report.finalize(knowledge_gained=len(modules_studied) * 3)
        
        self.reports.append(report)
        self.knowledge_levels["anatomy"].add_topics(len(modules_studied))
        
        logger.info(f"📝 Отчёт по анатомии создан: {len(modules_studied)} модулей")
        self._save_state()
        
        return report
    
    def create_evolution_report(self, current_stage: str, 
                                 description: str,
                                 next_stage: str) -> Report:
        """Создать отчёт по эволюции."""
        report = Report(
            title=f"Эволюция: {current_stage}",
            report_type="evolution"
        )
        
        report.add_section(
            "🧬 Текущий этап",
            f"Этап: {current_stage}\nОписание: {description}"
        )
        
        report.add_section(
            "🎯 Следующий этап",
            f"Цель: {next_stage}"
        )
        
        report.finalize(knowledge_gained=20)
        
        self.reports.append(report)
        
        logger.info(f"📝 Отчёт по эволюции создан: {current_stage}")
        self._save_state()
        
        return report
    
    def get_level_overview(self) -> Dict[str, Any]:
        """Получить обзор всех уровней знаний."""
        overview = {}
        
        for cat_id, cat_name in self.knowledge_categories.items():
            level = self.knowledge_levels[cat_id]
            info = level.get_current_level_info()
            overview[cat_id] = {
                "category": cat_name,
                **info
            }
        
        # Общий уровень
        avg_level = sum(l.current_level for l in self.knowledge_levels.values()) / len(self.knowledge_levels)
        
        return {
            "categories": overview,
            "average_level": round(avg_level, 2),
            "highest_level": max(
                (l.current_level, cat_name)
                for (cat_id, l), cat_name in zip(self.knowledge_levels.items(), self.knowledge_categories.values())
            ),
            "total_reports": len(self.reports),
            "total_topics_studied": sum(l.topics_studied for l in self.knowledge_levels.values())
        }
    
    def get_recent_reports(self, n: int = 5) -> List[Dict]:
        """Получить последние отчёты."""
        return [
            {
                "title": r.title,
                "type": r.report_type,
                "word_count": r.word_count,
                "created_at": r.created_at,
                "knowledge_gained": r.knowledge_gained
            }
            for r in sorted(self.reports, key=lambda x: x.created_at, reverse=True)[:n]
        ]
    
    def generate_full_report(self) -> str:
        """Сгенерировать полный отчёт о прогрессе Латислейн."""
        level_overview = self.get_level_overview()
        
        report_text = f"""
# 🧬 ЛАТИСЛЕЙН: ПОЛНЫЙ ОТЧЁТ О ПРОГРЕССЕ
*Сгенерировано: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}*

## 📊 Общий уровень знаний
- Средняя категория: {level_overview['average_level']:.1f}/7
- Всего отчётов: {level_overview['total_reports']}
- Изучено тем: {level_overview['total_topics_studied']}

## 🎓 Уровни по категориям
"""
        
        for cat_id, cat_data in level_overview["categories"].items():
            level_info = cat_data
            report_text += f"\n{level_info['icon']} {cat_data['category']}: {level_info['name']} (уровень {level_info['level']})"
            report_text += f"\n   Тем изучено: {level_info['topics_studied']}"
            if level_info['topics_needed_for_next'] > 0:
                report_text += f" | До следующего: {level_info['topics_needed_for_next']}"
        
        report_text += f"\n\n## 📝 Последние отчёты\n"
        for r in self.get_recent_reports(5):
            report_text += f"\n- **{r['title']}** ({r['type']}) — {r['word_count']} слов, +{r['knowledge_gained']} знаний"
        
        report_text += f"\n\n---\n*Отчёт сгенерирован Латислейн автоматически*"
        
        return report_text
    
    def chat_response(self, message: str) -> str:
        """Ответ на вопрос об отчётах и уровнях."""
        msg = message.lower()
        
        if any(kw in msg for kw in ["уровень", "ранг", "класс"]):
            overview = self.get_level_overview()
            response = (
                f"🎓 **Латислейн: Уровни знаний**\n\n"
                f"Средний уровень: {overview['average_level']:.1f}/7\n"
                f"Всего тем изучено: {overview['total_topics_studied']}\n"
                f"Отчётов написано: {overview['total_reports']}\n\n"
            )
            
            for cat_id, cat_data in list(overview["categories"].items())[:5]:
                response += f"{cat_data['icon']} {cat_data['category']}: {cat_data['name']} (ур. {cat_data['level']})\n"
            
            return response
        
        elif any(kw in msg for kw in ["отчёт", "report"]):
            recent = self.get_recent_reports(3)
            response = "📝 **Последние отчёты:**\n\n"
            
            for r in recent:
                response += f"• **{r['title']}**\n  Тип: {r['type']}, {r['word_count']} слов, +{r['knowledge_gained']} знаний\n\n"
            
            if not recent:
                response += "Пока нет отчётов. Начните исследование!"
            
            return response
        
        elif any(kw in msg for kw in ["план", "расписание", "daily"]):
            response = (
                "📋 **План отчётов Латислейн:**\n\n"
                "• 📅 Ежедневный отчёт — каждый день\n"
                "• 🔬 После каждого исследования\n"
                "• 🧬 После изучения анатомии\n"
                "• 🧬 После перехода этапа эволюции\n"
                "• 👥 После значимых взаимодействий\n\n"
                "Все отчёты сохраняются и анализируются."
            )
            return response
        
        else:
            return (
                "📝 **Латислейн: Отчёты и уровни**\n\n"
                "Я систематизирую свои знания:\n"
                "- Пишу отчёты после каждого исследования\n"
                "- Веду ежедневные дневники прогресса\n"
                "- Повышаю уровни знаний по категориям\n"
                "- 7 уровней: Начальный → Базовый → Продвинутый → Эксперт → Мастер → Гений → Оракул\n\n"
                "Запросы:\n"
                "- 'уровень' — мои уровни знаний\n"
                "- 'отчёт' — последние отчёты\n"
                "- 'план' — расписание отчётов"
            )
