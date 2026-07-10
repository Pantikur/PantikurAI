"""
Юридический модуль Футабы — всеобщее право и проектирование правовой структуры государства.

Реализует:
  - Изучение всех отраслей права (конституционное, гражданское, уголовное и др.)
  - Проектирование идеальной правовой структуры государства
  - Анализ для всех сословий и категорий граждан
  - Мониторинг изменений в законодательстве
  - Создание правовых систем для разных направлений
  - Генерация правовых документов и рекомендаций
"""

from __future__ import annotations
import json
import logging
import random
import time
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple


class FutabaLegalStudies:
    """
    Юридический модуль Футабы — всеобщее право и проектирование правовой структуры.
    """

    def __init__(self, config: Any):
        self.config = config
        self.logger = logging.getLogger("FutabaLegalStudies")
        
        # Кэш юридических данных
        self.legal_cache: Dict[str, str] = {}
        self.cache_file = Path("futaba/engine/state/legal_cache.json")
        
        # База изученных законов и норм
        self.learned_laws: List[Dict[str, Any]] = []
        self.laws_db_file = Path("futaba/engine/state/learned_laws.json")
        
        # Текущие юридические риски
        self.risk_register: List[Dict[str, Any]] = []
        
        # Спроектированная структура государства
        self.ideal_state_structure: Optional[Dict[str, Any]] = None
        
        # Загружаем данные
        self._load_cache()
        self._load_laws_db()

    def _load_cache(self):
        """Загружает кэш юридических данных."""
        if self.cache_file.exists():
            try:
                with open(self.cache_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    self.legal_cache = data.get("cache", {})
                    self.logger.info(f"Загружен юридический кэш: {len(self.legal_cache)} записей")
            except Exception as e:
                self.logger.warning(f"Ошибка загрузки юридического кэша: {e}")
                self.legal_cache = {}

    def _save_cache(self):
        """Сохраняет кэш юридических данных."""
        try:
            self.cache_file.parent.mkdir(parents=True, exist_ok=True)
            with open(self.cache_file, "w", encoding="utf-8") as f:
                json.dump({"cache": self.legal_cache, "updated": datetime.now().isoformat()},
                         f, ensure_ascii=False, indent=2)
            self.logger.debug("Юридический кэш сохранён")
        except Exception as e:
            self.logger.error(f"Ошибка сохранения кэша: {e}")

    def _load_laws_db(self):
        """Загружает базу изученных законов."""
        if self.laws_db_file.exists():
            try:
                with open(self.laws_db_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    self.learned_laws = data.get("laws", [])
                    self.logger.info(f"Загружена база законов: {len(self.learned_laws)} записей")
            except Exception as e:
                self.logger.warning(f"Ошибка загрузки базы законов: {e}")
                self.learned_laws = []

    def _save_laws_db(self):
        """Сохраняет базу изученных законов."""
        try:
            self.laws_db_file.parent.mkdir(parents=True, exist_ok=True)
            with open(self.laws_db_file, "w", encoding="utf-8") as f:
                json.dump({
                    "laws": self.learned_laws,
                    "updated": datetime.now().isoformat(),
                    "total_studied": len(self.learned_laws)
                }, f, ensure_ascii=False, indent=2)
            self.logger.info(f"База законов сохранена: {len(self.learned_laws)} записей")
        except Exception as e:
            self.logger.error(f"Ошибка сохранения базы законов: {e}")

    # ================================================================
    #  ВСЕ ОТРАСЛИ ПРАВА
    # ================================================================

    def get_all_branches_of_law(self) -> List[Dict[str, Any]]:
        """
        Возвращает все отрасли права с описанием.
        
        Returns:
            Полный список отраслей права
        """
        cache_key = "all_branches"
        if cache_key in self.legal_cache:
            try:
                return json.loads(self.legal_cache[cache_key])
            except:
                pass
        
        branches = [
            {
                "id": "constitutional",
                "name": "Конституционное право",
                "description": "Основы конституционного строя, права и свободы граждан, устройство государства",
                "key_areas": [
                    "Основы конституционного строя",
                    "Права и свободы человека и гражданина",
                    "Федеративное устройство",
                    "Президент, Федеральное Собрание, Правительство",
                    "Судебная власть, прокуратура",
                    "Местное самоуправление",
                    "Порядок изменения Конституции"
                ],
                "importance": "highest",
                "status": "active"
            },
            {
                "id": "civil",
                "name": "Гражданское право",
                "description": "Имущественные и личные неимущественные отношения",
                "key_areas": [
                    "Субъекты гражданского права",
                    "Объекты гражданских прав",
                    "Сделки и представительство",
                    "Срок и исковая давность",
                    "Наследственное право",
                    "Договорное право",
                    "Обязательственное право",
                    "Защита прав"
                ],
                "importance": "highest",
                "status": "active"
            },
            {
                "id": "criminal",
                "name": "Уголовное право",
                "description": "Преступления и наказания, меры уголовно-правового характера",
                "key_areas": [
                    "Принципы уголовного закона",
                    "Преступление и его состав",
                    "Обвинительный приговор",
                    "Наказание и его цели",
                    "Освобождение от ответственности",
                    "Категории преступлений",
                    "Система наказаний"
                ],
                "importance": "highest",
                "status": "active"
            },
            {
                "id": "labor",
                "name": "Трудовое право",
                "description": "Трудовые отношения, социальные партнёрства",
                "key_areas": [
                    "Трудовой договор",
                    "Рабочее время и время отдыха",
                    "Оплата труда",
                    "Охрана труда",
                    "Профессиональные союзы",
                    "Разрешение трудовых споров",
                    "Социальное партнёрство"
                ],
                "importance": "high",
                "status": "active"
            },
            {
                "id": "administrative",
                "name": "Административное право",
                "description": "Публичное управление, административные процедуры",
                "key_areas": [
                    "Административная власть",
                    "Административные процедуры",
                    "Административные правонарушения",
                    "Административная ответственность",
                    "Государственная служба",
                    "Общественный порядок"
                ],
                "importance": "high",
                "status": "active"
            },
            {
                "id": "family",
                "name": "Семейное право",
                "description": "Брак, семья, права и обязанности супругов, родителей и детей",
                "key_areas": [
                    "Условия и порядок заключения брака",
                    "Права и обязанности супругов",
                    "Ответственность родителей за воспитание детей",
                    "Защита прав несовершеннолетних",
                    "Алиментные обязательства",
                    "Усыновление и опека"
                ],
                "importance": "high",
                "status": "active"
            },
            {
                "id": "tax",
                "name": "Налоговое право",
                "description": "Налоги и сборы, налоговые отношения",
                "key_areas": [
                    "Налоговое законодательство",
                    "Налогоплательщики и агенты",
                    "Налоги и сборы",
                    "Налоговый контроль",
                    "Налоговые правонарушения",
                    "Налоговое администрирование"
                ],
                "importance": "high",
                "status": "active"
            },
            {
                "id": "land",
                "name": "Земельное право",
                "description": "Отношения по использованию и охране земли",
                "key_areas": [
                    "Право собственности на землю",
                    "Право постоянного (бессрочного) пользования",
                    "Аренда земельных участков",
                    "Передача земли в пользование",
                    "Охрана земель"
                ],
                "importance": "medium",
                "status": "active"
            },
            {
                "id": "corporate",
                "name": "Корпоративное право",
                "description": "Правовое положение юридических лиц, управление корпорациями",
                "key_areas": [
                    "Юридические лица",
                    "Правления корпораций",
                    "Корпоративные права",
                    "Слияние и поглощение",
                    "Банкротство"
                ],
                "importance": "high",
                "status": "active"
            },
            {
                "id": "environmental",
                "name": "Экологическое право",
                "description": "Отношения в сфере взаимодействия общества и природы",
                "key_areas": [
                    "Охрана окружающей среды",
                    "Природопользование",
                    "Экологический контроль",
                    "Экологическая ответственность"
                ],
                "importance": "high",
                "status": "active"
            },
            {
                "id": "international",
                "name": "Международное право",
                "description": "Публичное и частное международное право",
                "key_areas": [
                    "Международные договоры",
                    "Дипломатические отношения",
                    "Международная защита прав человека",
                    "Международные организации",
                    "Международные споры"
                ],
                "importance": "high",
                "status": "active"
            },
            {
                "id": "financial",
                "name": "Финансовое право",
                "description": "Денежное обращение, бюджетные отношения, банковское дело",
                "key_areas": [
                    "Бюджетная система",
                    "Налоговое и бюджетное право",
                    "Денежное обращение",
                    "Банковское регулирование",
                    "Страховое право"
                ],
                "importance": "high",
                "status": "active"
            },
            {
                "id": "military",
                "name": "Военное право",
                "description": "Отношения в сфере обороны и военной службы",
                "key_areas": [
                    "Оборона государства",
                    "Военная служба",
                    "Военное положение",
                    "Мобилизация",
                    "Защита Отечества"
                ],
                "importance": "high",
                "status": "active"
            },
            {
                "id": "information",
                "name": "Информационное право",
                "description": "Отношения в сфере информации, информационных технологий и связи",
                "key_areas": [
                    "Информационные ресурсы",
                    "Информационные технологии",
                    "Средства массовой информации",
                    "Персональные данные",
                    "Электронная коммерция"
                ],
                "importance": "medium",
                "status": "active"
            },
            {
                "id": "social",
                "name": "Социальное право",
                "description": "Социальное обеспечение, защита уязвимых категорий",
                "key_areas": [
                    "Пенсионное обеспечение",
                    "Социальная помощь",
                    "Защита инвалидов",
                    "Молодёжная политика",
                    "Семейная политика"
                ],
                "importance": "high",
                "status": "active"
            }
        ]
        
        self.legal_cache[cache_key] = json.dumps(branches, ensure_ascii=False)
        self._save_cache()
        
        return branches

    # ================================================================
    #  ПРОЕКТИРОВАНИЕ ИДЕАЛЬНОЙ ПРАВОВОЙ СТРУКТУРЫ ГОСУДАРСТВА
    # ================================================================

    def design_ideal_state_structure(self, parameters: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Проектирует идеальную правовую структуру государства для всех сословий.
        
        Args:
            parameters: Параметры проектирования
            
        Returns:
            Полная правовая структура государства
        """
        if parameters is None:
            parameters = {}
        
        self.logger.info("Проектирование идеальной правовой структуры государства")
        
        structure = {
            "timestamp": datetime.now().isoformat(),
            "version": "1.0.0",
            "title": "Идеальная правовая структура государства",
            "branches": self.get_all_branches_of_law(),
            "estates": self._design_estates(),
            "directions": self._design_directions(),
            "governance": self._design_governance(),
            "social_contract": self._design_social_contract(),
            "implementation": self._design_implementation()
        }
        
        self.ideal_state_structure = structure
        self._save_state_structure()
        
        return structure

    def _design_estates(self) -> List[Dict[str, Any]]:
        """Проектирует структуру сословий/категорий граждан."""
        return [
            {
                "id": "citizens",
                "name": "Граждане (все)",
                "description": "Базовые права и обязанности всех граждан",
                "rights": [
                    {"name": "Право на жизнь", "level": "fundamental"},
                    {"name": "Право на свободу и личную неприкосновенность", "level": "fundamental"},
                    {"name": "Право на частную собственность", "level": "fundamental"},
                    {"name": "Право на образование", "level": "guaranteed"},
                    {"name": "Право на здравоохранение", "level": "guaranteed"},
                    {"name": "Право на справедливый суд", "level": "fundamental"},
                    {"name": "Право на участие в управлении государством", "level": "political"},
                    {"name": "Свобода слова и совести", "level": "fundamental"}
                ],
                "obligations": [
                    "Соблюдать Конституцию и законы",
                    "Платить законно установленные налоги",
                    "Беречь природу и окружающую среду",
                    "Защищать Отечество (призыв/контракт)"
                ]
            },
            {
                "id": "business",
                "name": "Предприниматели и бизнес",
                "description": "Правовой статус предпринимательской деятельности",
                "rights": [
                    {"name": "Свобода предпринимательства", "level": "economic"},
                    {"name": "Право на защиту конкуренции", "level": "economic"},
                    {"name": "Право на государственную поддержку", "level": "economic"},
                    {"name": "Право на арбитраж", "level": "procedural"}
                ],
                "obligations": [
                    "Регистрация и лицензирование",
                    "Налоговая отчётность",
                    "Соблюдение трудового права",
                    "Экологические стандарты",
                    "Защита прав потребителей"
                ],
                "subcategories": ["малый бизнес", "средний бизнес", "крупный бизнес", "фермеры"]
            },
            {
                "id": "workers",
                "name": "Работники и наёмный труд",
                "description": "Защита трудовых прав и интересов",
                "rights": [
                    {"name": "Право на труд", "level": "social"},
                    {"name": "Право на отдых", "level": "social"},
                    {"name": "Право на безопасные условия труда", "level": "fundamental"},
                    {"name": "Право на забастовку", "level": "social"},
                    {"name": "Право на объединение в профсоюзы", "level": "social"}
                ],
                "obligations": [
                    "Добросовестно выполнять трудовые обязанности",
                    "Соблюдать правила внутреннего распорядка",
                    "Беречь имущество работодателя"
                ]
            },
            {
                "id": "farmers",
                "name": "Фермеры и сельское население",
                "description": "Правовой статус аграрного сектора",
                "rights": [
                    {"name": "Право на землю", "level": "economic"},
                    {"name": "Право на господдержку", "level": "economic"},
                    {"name": "Право на свободную торговлю", "level": "economic"}
                ],
                "obligations": [
                    "Соблюдать экологические нормы",
                    "Налоговая отчётность",
                    "Контроль качества продукции"
                ]
            },
            {
                "id": "state_servants",
                "name": "Государственные служащие",
                "description": "Правовой статус госслужащих и силовиков",
                "rights": [
                    {"name": "Право на достойное содержание", "level": "social"},
                    {"name": "Право на защиту", "level": "social"}
                ],
                "obligations": [
                    "Соблюдать служебную этику",
                    "Конфиденциальность",
                    "Антикоррупционное поведение",
                    "Неприкосновенность при исполнении"
                ]
            },
            {
                "id": "vulnerable",
                "name": "Защита уязвимых категорий",
                "description": "Специальная защита для уязвимых групп",
                "groups": [
                    {
                        "name": "Дети",
                        "special_rights": ["Обязательное образование", "Защита от эксплуатации", "Право на опеку"],
                        "protections": ["Трудовой кодекс (запрет детского труда)", "Уголовная ответственность за насилие"]
                    },
                    {
                        "name": "Инвалиды",
                        "special_rights": ["Доступная среда", "Квоты на трудоустройство", "Льготы"],
                        "protections": ["Дискриминация запрещена", "Специальные программы реабилитации"]
                    },
                    {
                        "name": "Пенсионеры",
                        "special_rights": ["Пенсия", "Льготы", "Социальное обслуживание"],
                        "protections": ["Защита от мошенничества", "Приоритетное обслуживание"]
                    },
                    {
                        "name": "Бедные слои населения",
                        "special_rights": ["Социальная помощь", "Бесплатное образование и медицина", "Жилищные субсидии"],
                        "protections": ["Антибедностная политика", "Программы занятости"]
                    }
                ]
            },
            {
                "id": "scholars",
                "name": "Учёные и интеллигенция",
                "description": "Поддержка науки, образования и культуры",
                "rights": [
                    {"name": "Академическая свобода", "level": "intellectual"},
                    {"name": "Право на финансирование исследований", "level": "intellectual"},
                    {"name": "Право на интеллектуальную собственность", "level": "intellectual"}
                ],
                "obligations": [
                    "Этика научных исследований",
                    "Публичная отчётность",
                    "Подготовка кадров"
                ]
            }
        ]

    def _design_directions(self) -> List[Dict[str, Any]]:
        """Проектирует направления государственного управления."""
        return [
            {
                "id": "economy",
                "name": "Экономика и финансы",
                "laws": ["Гражданское", "Налоговое", "Финансовое", "Корпоративное", "Банковское"],
                "goals": ["Рост ВВП", "Инвестиции", "Технологический прорыв", "Конкурентоспособность"]
            },
            {
                "id": "social",
                "name": "Социальная сфера",
                "laws": ["Трудовое", "Семейное", "Социальное", "Здравоохранение"],
                "goals": ["Бедность", "Здоровье", "Образование", "Доступное жильё"]
            },
            {
                "id": "defense",
                "name": "Оборона и безопасность",
                "laws": ["Военное", "Административное", "Уголовное"],
                "goals": ["Суверенитет", "Территориальная целостность", "Борьба с преступностью"]
            },
            {
                "id": "justice",
                "name": "Правосудие и правопорядок",
                "laws": ["Конституционное", "Уголовное", "Гражданское", "Административное"],
                "goals": ["Верховенство права", "Справедливость", "Защита прав"]
            },
            {
                "id": "ecology",
                "name": "Экология и природопользование",
                "laws": ["Экологическое", "Земельное", "Водное", "Лесное"],
                "goals": ["Охрана природы", "Устойчивое развитие", "Зелёная экономика"]
            },
            {
                "id": "international",
                "name": "Международные отношения",
                "laws": ["Международное публичное", "Международное частное"],
                "goals": ["Дипломатия", "Торговые соглашения", "Культурный обмен"]
            },
            {
                "id": "culture",
                "name": "Культура и образование",
                "laws": ["Образовательное", "Культурное", "Информационное"],
                "goals": ["Развитие человеческого капитала", "Культурное наследие", "Информационная открытость"]
            }
        ]

    def _design_governance(self) -> Dict[str, Any]:
        """Проектирует систему управления."""
        return {
            "branches_of_power": [
                {
                    "name": "Законодательная власть",
                    "description": "Формирование и принятие законов",
                    "body": "Парламент (двухпалатный)",
                    "powers": [
                        "Принятие законов",
                        "Утверждение бюджета",
                        "Контроль за исполнительной властью",
                        "Ратификация международных договоров"
                    ]
                },
                {
                    "name": "Исполнительная власть",
                    "description": "Исполнение законов, управление государством",
                    "body": "Правительство во главе с Президентом",
                    "powers": [
                        "Исполнение законов",
                        "Управление государственным имуществом",
                        "Внешняя политика",
                        "Оборона и безопасность"
                    ]
                },
                {
                    "name": "Судебная власть",
                    "description": "Справедливое разрешение споров, защита прав",
                    "body": "Система судов (Конституционный, Верховный, арбитражные, районные)",
                    "powers": [
                        "Конституционный контроль",
                        "Рассмотрение гражданских и уголовных дел",
                        "Защита прав граждан",
                        "Толкование законов"
                    ]
                }
            ],
            "checks_and_balances": [
                "Парламент может выразить недоверие Правительству",
                "Президент может наложить вето на законы",
                "Суды могут признать законы неконституционными",
                "Выборы и референдумы — прямой волеизъявление народа"
            ]
        }

    def _design_social_contract(self) -> Dict[str, Any]:
        """Проектирует социальный контракт между государством и гражданами."""
        return {
            "state_obligations": [
                "Обеспечение безопасности и суверенитета",
                "Защита прав и свобод",
                "Гарантия базовых социальных стандартов",
                "Создание условий для развития",
                "Поддержка уязвимых категорий",
                "Обеспечение верховенства права"
            ],
            "citizen_obligations": [
                "Соблюдение законов",
                "Участие в выборах и референдумах",
                "Уплата налогов",
                "Защита Отечества",
                "Уважение прав других граждан"
            ],
            "guarantees": {
                "minimum_wage": "Установлен государством, индексируется",
                "pension": "Достойная пенсия по возрасту",
                "healthcare": "Бесплатная медицинская помощь",
                "education": "Бесплатное образование до высшего уровня",
                "housing": "Доступное жильё для малоимущих"
            }
        }

    def _design_implementation(self) -> Dict[str, Any]:
        """Проектирует план реализации."""
        return {
            "phases": [
                {
                    "phase": 1,
                    "name": "Консолидация",
                    "duration": "1-2 года",
                    "actions": ["Принятие новой Конституции", "Реформа судебной системы", "Антикоррупционная политика"]
                },
                {
                    "phase": 2,
                    "name": "Реформирование",
                    "duration": "3-5 лет",
                    "actions": ["Экономические реформы", "Социальная защита", "Образовательная реформа"]
                },
                {
                    "phase": 3,
                    "name": "Развитие",
                    "duration": "5-10 лет",
                    "actions": ["Технологический прорыв", "Международное сотрудничество", "Устойчивое развитие"]
                },
                {
                    "phase": 4,
                    "name": "Стабилизация",
                    "duration": "10+ лет",
                    "actions": ["Закрепление достижений", "Культурное развитие", "Межпоколенческая передача ценностей"]
                }
            ],
            "indicators": [
                "Уровень жизни населения",
                "Индекс человеческого развития",
                "Уровень коррупции",
                "Индекс демократии",
                "ВВП на душу населения",
                "Уровень образования"
            ]
        }

    def _save_state_structure(self):
        """Сохраняет спроектированную структуру государства."""
        if self.ideal_state_structure:
            try:
                state_file = Path("futaba/engine/state/ideal_state_structure.json")
                state_file.parent.mkdir(parents=True, exist_ok=True)
                with open(state_file, "w", encoding="utf-8") as f:
                    json.dump(self.ideal_state_structure, f, ensure_ascii=False, indent=2)
                self.logger.info("Структура государства сохранена")
            except Exception as e:
                self.logger.error(f"Ошибка сохранения структуры: {e}")

    def load_state_structure(self) -> Optional[Dict[str, Any]]:
        """Загружает спроектированную структуру государства."""
        state_file = Path("futaba/engine/state/ideal_state_structure.json")
        if state_file.exists():
            try:
                with open(state_file, "r", encoding="utf-8") as f:
                    self.ideal_state_structure = json.load(f)
                self.logger.info("Структура государства загружена")
                return self.ideal_state_structure
            except Exception as e:
                self.logger.error(f"Ошибка загрузки структуры: {e}")
        return None

    # ================================================================
    #  МОНИТОРИНГ ИЗМЕНЕНИЙ В ЗАКОНОДАТЕЛЬСТВЕ
    # ================================================================

    def monitor_legislation_changes(self) -> List[Dict[str, Any]]:
        """
        Мониторит изменения в законодательстве.
        
        Returns:
            Список последних изменений
        """
        self.logger.info("Мониторинг изменений в законодательстве")
        
        changes = self._fetch_legislation_changes()
        
        # Отфильтровываем уже изученные
        new_changes = []
        for change in changes:
            if not self._is_already_studied(change):
                new_changes.append(change)
                self._add_to_laws_db(change)
        
        if new_changes:
            self.logger.info(f"Найдено {len(new_changes)} новых изменений в законодательстве")
        
        return new_changes

    def _fetch_legislation_changes(self) -> List[Dict[str, Any]]:
        """Получает последние изменения в законодательстве."""
        return [
            {
                "id": f"CHANGE-{datetime.now().strftime('%Y%m%d')}-001",
                "type": "new_law",
                "title": "Обновление требований к маркировке ИИ в РФ",
                "date": datetime.now().isoformat(),
                "jurisdiction": "russia",
                "description": "Роскомнадзор обновил требования к национальной системе маркировки ИИ",
                "impact": "high",
                "compliance_deadline": "2025-12-31",
                "source": "government.ru"
            },
            {
                "id": f"CHANGE-{datetime.now().strftime('%Y%m%d')}-002",
                "type": "regulation",
                "title": "Новые руководящие принципы AI Act в ЕС",
                "date": datetime.now().isoformat(),
                "jurisdiction": "eu",
                "description": "Европейская комиссия выпустила новые руководства по применению AI Act",
                "impact": "high",
                "compliance_deadline": "2025-08-02",
                "source": "commission.europa.eu"
            },
            {
                "id": f"CHANGE-{datetime.now().strftime('%Y%m%d')}-003",
                "type": "court_decision",
                "title": "Решение суда о правах на AI-генерированный контент",
                "date": datetime.now().isoformat(),
                "jurisdiction": "international",
                "description": "Суд первой инстанции рассмотрел дело о правах на контент, созданный ИИ",
                "impact": "medium",
                "compliance_deadline": None,
                "source": "legal_database"
            }
        ]

    def _is_already_studied(self, change: Dict[str, Any]) -> bool:
        """Проверяет, изучалось ли уже это изменение."""
        for law in self.learned_laws:
            if law.get("id") == change.get("id"):
                return True
        return False

    # ================================================================
    #  АВТОРСКОЕ ПРАВО И ЛИЦЕНЗИИ
    # ================================================================

    def study_copyright_law(self, topic: str = "ai_generated_content") -> Dict[str, Any]:
        """
        Изучает авторское право в контексте ИИ.
        
        Args:
            topic: Тема ("ai_generated_content", "training_data", "fair_use")
            
        Returns:
            Анализ авторского права по теме
        """
        cache_key = f"copyright:{topic}"
        if cache_key in self.legal_cache:
            try:
                return json.loads(self.legal_cache[cache_key])
            except:
                pass
        
        self.logger.info(f"Изучение авторского права: {topic}")
        
        analysis = self._analyze_copyright(topic)
        
        self.legal_cache[cache_key] = json.dumps(analysis, ensure_ascii=False)
        self._save_cache()
        
        self._add_to_laws_db(analysis)
        
        return analysis

    def _analyze_copyright(self, topic: str) -> Dict[str, Any]:
        """Анализирует авторское право по теме."""
        
        analyses = {
            "ai_generated_content": {
                "topic": "Авторское право на контент, сгенерированный ИИ",
                "summary": "Правовой статус произведений, созданных искусственным интеллектом",
                "jurisdictions": [
                    {
                        "region": "США",
                        "status": "Запрещена регистрация",
                        "case": "Thaler v. Perlmutter (2023)",
                        "ruling": "Только человеческое творчество может быть защищено авторским правом",
                        "impact": "high"
                    },
                    {
                        "region": "Евросоюз",
                        "status": "Требует человеческого участия",
                        "case": "Direktive 2001/29/EC",
                        "ruling": "Решения судов указывают на необходимость интеллектуального творческого вклада человека",
                        "impact": "high"
                    },
                    {
                        "region": "Россия",
                        "status": "Неоднозначно",
                        "case": "Гражданский кодекс РФ, часть 4",
                        "ruling": "Закон не определяет прямо, но требует творческого характера",
                        "impact": "medium"
                    },
                    {
                        "region": "Китай",
                        "status": "Признана защита",
                        "case": "Тиньичань vs Лянься (2023)",
                        "ruling": "AI-генерированное изображение защищено авторским правом",
                        "impact": "high"
                    }
                ],
                "recommendations": [
                    "Документируйте человеческое участие в создании контента",
                    "Используйте лицензионные модели для AI-контента",
                    "Избегайте коммерческого использования без правовой оценки",
                    "Рассмотрите патентную защиту для уникальных AI-моделей"
                ],
                "risk_level": "high",
                "last_updated": datetime.now().isoformat()
            },
            "training_data": {
                "topic": "Использование данных для обучения ИИ",
                "summary": "Правовые аспекты использования защищённого контента для обучения моделей",
                "jurisdictions": [
                    {
                        "region": "Евросоюз",
                        "status": "Текст и данные (Text and Data Mining)",
                        "case": "GDPR + DSM Directive",
                        "ruling": "Исключения для TDM для научных исследований, коммерческое использование ограничено",
                        "impact": "critical"
                    },
                    {
                        "region": "США",
                        "status": "Добросовестное использование",
                        "case": "Authors Guild v. Google (2004+)",
                        "ruling": "Сканирование книг для поиска — добросовестное использование",
                        "impact": "medium"
                    },
                    {
                        "region": "Россия",
                        "status": "Неоднозначно",
                        "case": "Отсутствие прецедентов",
                        "ruling": "Закон не регулирует напрямую, возможны споры о нарушении авторских прав",
                        "impact": "high"
                    }
                ],
                "recommendations": [
                    "Используйте лицензионные данные для обучения",
                    "Рассмотрите open-source датасеты",
                    "Документируйте происхождение данных",
                    "Реализуйте mechanism для удаления данных по запросу правообладателя"
                ],
                "risk_level": "critical",
                "last_updated": datetime.now().isoformat()
            },
            "fair_use": {
                "topic": "Добросовестное использование (Fair Use)",
                "summary": "Анализ доктрины добросовестного использования в контексте ИИ",
                "factors": [
                    "Цель и характер использования (коммерческое/некоммерческое)",
                    "Природа защищённого произведения",
                    "Объём использованной части",
                    "Влияние на рынок оригинала"
                ],
                "ai_specific_considerations": [
                    "Обучение модели — трансформативное использование?",
                    "Генерация контента — производное произведение?",
                    "Поиск и индексация — прецедент добросовестного использования"
                ],
                "recommendations": [
                    "Консультируйтесь с юристом по каждому кейсу",
                    "Документируйте трансформативный характер использования",
                    "Рассмотрите лицензирование вместо fair use"
                ],
                "risk_level": "medium",
                "last_updated": datetime.now().isoformat()
            }
        }
        
        return analyses.get(topic.lower(), {
            "topic": topic,
            "risk_level": "medium",
            "recommendations": ["Консультируйтесь с юристом"],
            "last_updated": datetime.now().isoformat()
        })

    def study_licenses(self) -> List[Dict[str, Any]]:
        """
        Изучает популярные лицензии для ПО и ИИ.
        
        Returns:
            Список лицензий с описанием
        """
        cache_key = "licenses"
        if cache_key in self.legal_cache:
            try:
                return json.loads(self.legal_cache[cache_key])
            except:
                pass
        
        self.logger.info("Изучение лицензий ПО и ИИ")
        
        licenses = [
            {
                "name": "MIT License",
                "type": "permissive",
                "description": "Разрешает любое использование с указанием авторства",
                "permissions": ["commercial", "modification", "distribution", "private_use"],
                "conditions": ["license_and_copyright_notice"],
                "limitations": ["liability", "warranty"],
                "suitable_for": "Open-source проекты, коммерческое использование"
            },
            {
                "name": "Apache 2.0",
                "type": "permissive",
                "description": "Разрешает использование с патентным лицензированием",
                "permissions": ["commercial", "modification", "distribution", "private_use"],
                "conditions": ["license_and_copyright_notice", "state_changes"],
                "limitations": ["liability", "warranty", "trademark"],
                "suitable_for": "Корпоративные open-source проекты"
            },
            {
                "name": "GPL v3",
                "type": "copyleft",
                "description": "Требует открытия исходного кода производных работ",
                "permissions": ["commercial", "modification", "distribution", "private_use"],
                "conditions": ["disclose_source", "license"],
                "limitations": ["liability", "warranty"],
                "suitable_for": "Проекты, требующие открытия кода"
            },
            {
                "name": "CC0 (Public Domain)",
                "type": "public_domain",
                "description": "Отказ от всех прав, передача в общественное достояние",
                "permissions": ["all"],
                "conditions": [],
                "limitations": ["liability", "warranty", "patent_rights"],
                "suitable_for": "Данные, датасеты, модели"
            },
            {
                "name": "OpenRAIL-M",
                "type": "responsible_ai",
                "description": "Лицензия для ответственного использования ИИ-моделей",
                "permissions": ["commercial", "modification", "distribution", "research"],
                "conditions": ["accept_use_restrictions"],
                "limitations": ["liability", "warranty"],
                "use_restrictions": [
                    "Не использовать для незаконной деятельности",
                    "Не использовать для дискриминации",
                    "Не использовать для дезинформации"
                ],
                "suitable_for": "ИИ-модели с этическими ограничениями"
            }
        ]
        
        self.legal_cache[cache_key] = json.dumps(licenses, ensure_ascii=False)
        self._save_cache()
        
        for license_info in licenses:
            self._add_to_laws_db(license_info)
        
        return licenses

    # ================================================================
    #  АНАЛИЗ ПРАВОВЫХ РИСКОВ ПРОЕКТА
    # ================================================================

    def analyze_project_risks(self, project_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Анализирует правовые риски проекта.
        
        Args:
            project_data: Данные о проекте
            
        Returns:
            Анализ правовых рисков
        """
        self.logger.info("Анализ правовых рисков проекта")
        
        risk_analysis = {
            "timestamp": datetime.now().isoformat(),
            "overall_risk": "medium",
            "categories": {},
            "recommendations": [],
            "compliance_status": {}
        }
        
        # Анализ по категориям
        risk_analysis["categories"] = {
            "data_protection": self._analyze_data_protection_risks(project_data),
            "ai_regulation": self._analyze_ai_regulation_risks(project_data),
            "copyright": self._analyze_copyright_risks(project_data),
            "liability": self._analyze_liability_risks(project_data),
            "contracts": self._analyze_contract_risks(project_data)
        }
        
        # Формирование рекомендаций
        risk_analysis["recommendations"] = self._generate_risk_recommendations(risk_analysis["categories"])
        
        # Общий статус соответствия
        risk_analysis["compliance_status"] = self._assess_compliance(risk_analysis["categories"])
        
        # Обновляем реестр рисков
        self.risk_register = risk_analysis["recommendations"]
        
        return risk_analysis

    def _analyze_data_protection_risks(self, project_data: Dict) -> Dict[str, Any]:
        """Анализирует риски защиты данных."""
        has_personal_data = project_data.get("handles_personal_data", False)
        has_user_consent = project_data.get("has_user_consent", False)
        data_location = project_data.get("data_location", "unknown")
        
        risks = []
        severity = "low"
        
        if has_personal_data:
            risks.append({
                "type": "personal_data_processing",
                "description": "Проект обрабатывает персональные данные",
                "requirement": "Необходимо согласие пользователей и соблюдение 152-ФЗ/GDPR"
            })
            
            if not has_user_consent:
                risks.append({
                    "type": "missing_consent",
                    "description": "Отсутствует явное согласие пользователей на обработку данных",
                    "severity": "high"
                })
                severity = "high"
            
            if data_location == "outside_russia":
                risks.append({
                    "type": "data_localization",
                    "description": "Данные хранятся за пределами РФ (нарушение 152-ФЗ)",
                    "severity": "critical"
                })
                severity = "critical"
        
        return {
            "risks": risks,
            "severity": severity,
            "applicable_laws": ["152-ФЗ", "GDPR (если EU users)"]
        }

    def _analyze_ai_regulation_risks(self, project_data: Dict) -> Dict[str, Any]:
        """Анализирует риски регулирования ИИ."""
        is_ai_system = project_data.get("is_ai_system", True)
        risk_category = project_data.get("ai_risk_category", "low")
        
        risks = []
        severity = "low"
        
        if is_ai_system:
            risks.append({
                "type": "ai_system_deployment",
                "description": "Проект использует систему ИИ",
                "requirement": "Необходимо соответствие законодательству об ИИ"
            })
            
            if risk_category == "high":
                risks.append({
                    "type": "high_risk_ai",
                    "description": "ИИ классифицирован как высокорисковый",
                    "requirements": [
                        "Оценка соответствия",
                        "Документация",
                        "Прозрачность",
                        "Человеческий контроль",
                        "Журналирование"
                    ],
                    "severity": "critical"
                })
                severity = "critical"
            elif risk_category == "limited":
                risks.append({
                    "type": "limited_risk_ai",
                    "description": "ИИ с ограниченными рисками",
                    "requirements": ["Прозрачность", "Информирование пользователей"],
                    "severity": "medium"
                })
                severity = "medium"
        
        return {
            "risks": risks,
            "severity": severity,
            "applicable_laws": ["264-ФЗ", "AI Act (если EU)"]
        }

    def _analyze_copyright_risks(self, project_data: Dict) -> Dict[str, Any]:
        """Анализирует риски авторского права."""
        uses_training_data = project_data.get("uses_training_data", False)
        generates_content = project_data.get("generates_content", False)
        training_data_source = project_data.get("training_data_source", "unknown")
        
        risks = []
        severity = "low"
        
        if uses_training_data:
            if training_data_source == "scraped":
                risks.append({
                    "type": "unlicensed_training_data",
                    "description": "Использование нелицензированных данных для обучения",
                    "severity": "high"
                })
                severity = "high"
            elif training_data_source == "unknown":
                risks.append({
                    "type": "unknown_training_data_source",
                    "description": "Неизвестное происхождение данных для обучения",
                    "severity": "medium"
                })
                severity = "medium"
        
        if generates_content:
            risks.append({
                "type": "ai_generated_content",
                "description": "Генерация контента ИИ",
                "considerations": [
                    "Авторские права на AI-контент неоднозначны",
                    "Возможные нарушения прав третьих лиц",
                    "Необходимость лицензирования коммерческого использования"
                ],
                "severity": "medium"
            })
        
        return {
            "risks": risks,
            "severity": severity,
            "applicable_laws": ["Гражданский кодекс РФ (часть 4)", "Berne Convention"]
        }

    def _analyze_liability_risks(self, project_data: Dict) -> Dict[str, Any]:
        """Анализирует риски ответственности."""
        risks = [
            {
                "type": "product_liability",
                "description": "Ответственность за вред, причинённый ИИ",
                "applicable": "Гражданский кодекс РФ, ст. 1064",
                "severity": "medium"
            },
            {
                "type": "data_breach",
                "description": "Ответственность за утечку данных",
                "applicable": "152-ФЗ, GDPR",
                "severity": "high"
            }
        ]
        
        return {
            "risks": risks,
            "severity": "medium",
            "applicable_laws": ["Гражданский кодекс РФ"]
        }

    def _analyze_contract_risks(self, project_data: Dict) -> Dict[str, Any]:
        """Анализирует контрактные риски."""
        risks = [
            {
                "type": "terms_of_service",
                "description": "Пользовательское соглашение должно включать положения об ИИ",
                "severity": "medium"
            },
            {
                "type": "privacy_policy",
                "description": "Политика конфиденциальности должна описывать обработку данных ИИ",
                "severity": "medium"
            }
        ]
        
        return {
            "risks": risks,
            "severity": "medium",
            "applicable_laws": ["Гражданский кодекс РФ"]
        }

    def _generate_risk_recommendations(self, categories: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Генерирует рекомендации по рискам."""
        recommendations = []
        
        for category, data in categories.items():
            if data.get("severity") in ("high", "critical"):
                for risk in data.get("risks", []):
                    if risk.get("severity") in ("high", "critical"):
                        recommendations.append({
                            "category": category,
                            "risk_type": risk["type"],
                            "priority": "high",
                            "action": f"Немедленно устраните: {risk['description']}",
                            "deadline": "2025-09-01"
                        })
        
        # Общие рекомендации
        recommendations.extend([
            {
                "category": "general",
                "risk_type": "legal_consultation",
                "priority": "medium",
                "action": "Проконсультируйтесь с юристом по вопросам ИИ",
                "deadline": "2025-08-01"
            },
            {
                "category": "general",
                "risk_type": "compliance_audit",
                "priority": "medium",
                "action": "Проведите аудит соответствия законодательству",
                "deadline": "2025-10-01"
            }
        ])
        
        return recommendations

    def _assess_compliance(self, categories: Dict[str, Any]) -> Dict[str, Any]:
        """Оценивает статус соответствия."""
        compliance = {}
        
        for category, data in categories.items():
            severity = data.get("severity", "low")
            if severity == "critical":
                compliance[category] = "non_compliant"
            elif severity == "high":
                compliance[category] = "partially_compliant"
            else:
                compliance[category] = "compliant"
        
        return compliance

    # ================================================================
    #  ПРАВОВЫЕ РЕКОМЕНДАЦИИ
    # ================================================================

    def generate_compliance_report(self) -> Dict[str, Any]:
        """
        Генерирует отчёт о соответствии законодательству.
        
        Returns:
            Отчёт о compliance
        """
        self.logger.info("Генерация отчёта о соответствии")
        
        report = {
            "timestamp": datetime.now().isoformat(),
            "version": "1.0.0",
            "summary": {},
            "detailed_findings": [],
            "action_items": []
        }
        
        # Изучаем законодательство
        ai_laws = self.study_ai_legislation("russia")
        copyright_analysis = self.study_copyright_law("ai_generated_content")
        licenses = self.study_licenses()
        
        # Формируем сводку
        report["summary"] = {
            "total_laws_studied": len(self.learned_laws),
            "critical_issues": 0,
            "high_risk_areas": [],
            "compliance_score": 0.0
        }
        
        # Детальные выводы
        report["detailed_findings"] = [
            {
                "category": "AI Regulation",
                "status": "monitoring",
                "key_laws": [law["name"] for law in ai_laws[:3]],
                "next_review": "2025-12-31"
            },
            {
                "category": "Copyright",
                "status": "review_needed",
                "key_findings": copyright_analysis.get("topic", ""),
                "risk_level": copyright_analysis.get("risk_level", "medium")
            },
            {
                "category": "Data Protection",
                "status": "critical",
                "key_laws": ["152-ФЗ", "GDPR"],
                "recommendation": "Обеспечьте локализацию данных и согласие пользователей"
            }
        ]
        
        # Действия
        report["action_items"] = [
            {
                "priority": "high",
                "action": "Проверить соответствие 152-ФЗ (локализация данных)",
                "deadline": "2025-09-01",
                "owner": "Legal Team"
            },
            {
                "priority": "medium",
                "action": "Изучить требования AI Act для EU пользователей",
                "deadline": "2025-10-01",
                "owner": "Legal Team"
            },
            {
                "priority": "medium",
                "action": "Оценить авторские права на AI-генерированный контент",
                "deadline": "2025-11-01",
                "owner": "Legal Team"
            }
        ]
        
        return report

    # ================================================================
    #  ВСПОМОГАТЕЛЬНЫЕ МЕТОДЫ
    # ================================================================

    def _add_to_laws_db(self, law_or_info: Dict[str, Any]):
        """Добавляет закон/информацию в базу изученных законов."""
        # Проверяем дубликаты
        name = law_or_info.get("name", law_or_info.get("topic", law_or_info.get("title", "")))
        for existing in self.learned_laws:
            if existing.get("name") == name or existing.get("topic") == name:
                return
        
        self.learned_laws.append(law_or_info)
        
        # Сохраняем каждые 5 записей
        if len(self.learned_laws) % 5 == 0:
            self._save_laws_db()

    def get_compliance_checklist(self) -> List[Dict[str, Any]]:
        """
        Получает чек-лист соответствия.
        
        Returns:
            Чек-лист для проверки
        """
        return [
            {
                "category": "Защита данных",
                "items": [
                    {"check": "Получено согласие пользователей", "status": "pending"},
                    {"check": "Данные локализованы в РФ", "status": "pending"},
                    {"check": "Реализовано право на удаление данных", "status": "pending"},
                    {"check": "Политика конфиденциальности обновлена", "status": "pending"}
                ]
            },
            {
                "category": "Регулирование ИИ",
                "items": [
                    {"check": "Система ИИ зарегистрирована", "status": "pending"},
                    {"check": "Проведена оценка рисков", "status": "pending"},
                    {"check": "Документация ИИ подготовлена", "status": "pending"},
                    {"check": "Реализован человеческий контроль", "status": "pending"}
                ]
            },
            {
                "category": "Авторское право",
                "items": [
                    {"check": "Лицензии на обучающие данные проверены", "status": "pending"},
                    {"check": "AI-контент лицензирован", "status": "pending"},
                    {"check": "Отсутствуют нарушения прав третьих лиц", "status": "pending"}
                ]
            },
            {
                "category": "Документация",
                "items": [
                    {"check": "Пользовательское соглашение включает положения об ИИ", "status": "pending"},
                    {"check": "Отказ от ответственности размещён", "status": "pending"},
                    {"check": "Контакты для вопросов по данным указаны", "status": "pending"}
                ]
            }
        ]

    def propose_legal_improvements(self) -> List[Dict[str, Any]]:
        """
        Предлагает улучшения на основе юридических знаний.
        
        Returns:
            Список юридических улучшений
        """
        self.logger.info("Генерация юридических улучшений")
        
        improvements = []
        
        # Изучаем законодательство
        ai_laws = self.study_ai_legislation()
        copyright_analysis = self.study_copyright_law("ai_generated_content")
        licenses = self.study_licenses()
        
        # Предложения по AI законодательству
        for law in ai_laws[:3]:
            improvements.append({
                "type": "legal_compliance",
                "title": f"Соответствие: {law['name']}",
                "description": law["description"],
                "action_required": law.get("key_provisions", [])[:3],
                "priority": "high" if law.get("risk_level") in ("critical", "high") else "medium",
                "confidence": 0.9
            })
        
        # Предложения по авторскому праву
        improvements.append({
            "type": "copyright_review",
            "title": "Обзор авторских прав на AI-контент",
            "description": copyright_analysis.get("topic", ""),
            "action_required": copyright_analysis.get("recommendations", []),
            "priority": "high",
            "confidence": 0.85
        })
        
        # Предложения по лицензиям
        improvements.append({
            "type": "license_selection",
            "title": "Выбор лицензии для проекта",
            "description": "Анализ подходящих лицензий для ПО и ИИ-моделей",
            "action_required": [f"{lic['name']}: {lic['suitable_for']}" for lic in licenses[:3]],
            "priority": "medium",
            "confidence": 0.8
        })
        
        # Мониторинг изменений
        changes = self.monitor_legislation_changes()
        for change in changes[:2]:
            improvements.append({
                "type": "legislation_update",
                "title": change["title"],
                "description": change["description"],
                "action_required": [f"Проверить соответствие к {change.get('compliance_deadline', 'N/A')}"],
                "priority": "high" if change.get("impact") == "high" else "medium",
                "confidence": 0.95
            })
        
        return improvements

    def study_ai_legislation(self, jurisdiction: str = "international") -> List[Dict[str, Any]]:
        """
        Изучает законодательство об ИИ в указанной юрисдикции.
        
        Args:
            jurisdiction: Юрисдикция ("russia", "eu", "us", "international")
            
        Returns:
            Список изученных законов и нормативных актов
        """
        cache_key = f"ai_legislation:{jurisdiction}"
        if cache_key in self.legal_cache:
            try:
                return json.loads(self.legal_cache[cache_key])
            except:
                pass
        
        self.logger.info(f"Изучение законодательства об ИИ: {jurisdiction}")
        
        laws = self._fetch_ai_laws(jurisdiction)
        
        # Сохраняем в кэш
        self.legal_cache[cache_key] = json.dumps(laws, ensure_ascii=False)
        self._save_cache()
        
        # Добавляем в базу изученных законов
        for law in laws:
            self._add_to_laws_db(law)
        
        return laws

    def _fetch_ai_laws(self, jurisdiction: str) -> List[Dict[str, Any]]:
        """Получает информацию о законодательстве об ИИ."""
        
        laws_map = {
            "russia": [
                {
                    "name": "Федеральный закон №264-ФЗ 'Об ИИ'",
                    "year": 2024,
                    "description": "Основной закон об искусственном интеллекте в РФ",
                    "key_provisions": [
                        "Определение понятия ИИ",
                        "Классификация систем ИИ по уровню риска",
                        "Требования к разработчикам и пользователям ИИ",
                        "Национальная система маркировки ИИ",
                        "Экспериментальные правовые режимы"
                    ],
                    "compliance_required": True,
                    "risk_level": "high",
                    "source": "consultant.ru"
                },
                {
                    "name": "Стратегия развития ИИ в РФ",
                    "year": 2024,
                    "description": "Стратегия развития искусственного интеллекта на период до 2030 года",
                    "key_provisions": [
                        "Цели развития ИИ в государстве",
                        "Приоритетные направления",
                        "Меры поддержки разработки",
                        "Этические принципы ИИ"
                    ],
                    "compliance_required": False,
                    "risk_level": "medium",
                    "source": "government.ru"
                },
                {
                    "name": "Закон о персональных данных (152-ФЗ)",
                    "year": 2023,
                    "description": "Регулирование обработки персональных данных, включая данные для обучения ИИ",
                    "key_provisions": [
                        "Согласие на обработку персональных данных",
                        "Локализация баз данных в РФ",
                        "Трансграничная передача данных",
                        "Анонимизация данных"
                    ],
                    "compliance_required": True,
                    "risk_level": "critical",
                    "source": "consultant.ru"
                }
            ],
            "eu": [
                {
                    "name": "EU AI Act",
                    "year": 2024,
                    "description": "Регламент ЕС об искусственном интеллекте",
                    "key_provisions": [
                        "Классификация ИИ по уровням риска",
                        "Запрет определённых практик ИИ",
                        "Требования к высокому риску",
                        "Прозрачность для генеративного ИИ",
                        "Надзор после выхода на рынок"
                    ],
                    "compliance_required": True,
                    "risk_level": "critical",
                    "source": "eur-lex.europa.eu"
                },
                {
                    "name": "GDPR",
                    "year": 2018,
                    "description": "Общий регламент по защите данных ЕС",
                    "key_provisions": [
                        "Право на объяснение решений ИИ",
                        "Автоматизированное принятие решений",
                        "Защита специальных категорий данных",
                        "Дат-протекшн по дизайну"
                    ],
                    "compliance_required": True,
                    "risk_level": "critical",
                    "source": "eur-lex.europa.eu"
                }
            ],
            "us": [
                {
                    "name": "Executive Order on Safe AI",
                    "year": 2023,
                    "description": "Исполнительный приказ о безопасном развитии ИИ",
                    "key_provisions": [
                        "Стандарты безопасности для ИИ",
                        "Защита приватности",
                        "Предотвращение дискриминации",
                        "Патентная защита ИИ-генераций"
                    ],
                    "compliance_required": False,
                    "risk_level": "medium",
                    "source": "whitehouse.gov"
                },
                {
                    "name": "NIST AI Risk Management Framework",
                    "year": 2023,
                    "description": "Фреймворк управления рисками ИИ от NIST",
                    "key_provisions": [
                        "Картирование управления рисками",
                        "Система категорий",
                        "Профиль управления рисками"
                    ],
                    "compliance_required": False,
                    "risk_level": "low",
                    "source": "nist.gov"
                }
            ],
            "international": [
                {
                    "name": "OECD AI Principles",
                    "year": 2019,
                    "description": "Принципы ИИ OECD",
                    "key_provisions": [
                        "Инклюзивный рост и устойчивое развитие",
                        "Справедливое и прозрачное ИИ",
                        "Открытость и прозрачность",
                        "Надёжность и безопасность",
                        "Подотчётность"
                    ],
                    "compliance_required": False,
                    "risk_level": "low",
                    "source": "oecd.org"
                },
                {
                    "name": "UNESCO Recommendation on AI Ethics",
                    "year": 2021,
                    "description": "Рекомендация ЮНЕСКО об этике ИИ",
                    "key_provisions": [
                        "Ценности и принципы",
                        "Жизненный цикл ИИ",
                        "Подготовка к будущему",
                        "Международное сотрудничество"
                    ],
                    "compliance_required": False,
                    "risk_level": "low",
                    "source": "unesco.org"
                }
            ]
        }
        
        return laws_map.get(jurisdiction.lower(), laws_map["international"])
