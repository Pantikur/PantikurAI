"""
ФУТАБА — Модуль субъектов права v3.0
=====================================

Полная система работы со всеми категориями субъектов права:
- Индивидуальные (физические лица)
- Коллективные (юридические лица)
- Публично-правовые образования
- Социальные общности
- Органы публичной власти
- Общественные объединения

Модуль создаёт, анализирует и наполняет юридические знания
для всех категорий субъектов — не только для ИИ, но и в общем
для юридического и физического лица.
"""

from __future__ import annotations

import json
import os
import re
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

# Принудительный UTF-8 для Windows
if sys.platform == "win32":
    for _stream in (sys.stdout, sys.stderr):
        _reconfigure = getattr(_stream, "reconfigure", None)
        if _reconfigure is not None:
            try:
                _reconfigure(encoding="utf-8")
            except Exception:
                pass
    os.environ["PYTHONIOENCODING"] = "utf-8"


class LegalEntity:
    """Базовый класс субъекта права."""

    def __init__(self, name: str, entity_type: str, jurisdiction: str = "russia"):
        self.id = f"{entity_type}_{name}_{datetime.now().strftime('%Y%m%d%H%M%S')}"
        self.name = name
        self.entity_type = entity_type  # physical, legal, public, social, authority, unregistered
        self.jurisdiction = jurisdiction
        self.capacity: Dict[str, Any] = {}  # правоспособность
        self.created_at = datetime.now().isoformat()
        self.updated_at = datetime.now().isoformat()
        self.knowledge_base = {}  # база знаний по этому субъекту
        self.risk_profile = {}  # профиль рисков
        self.compliance_status = {}  # статус compliance

    def to_dict(self) -> Dict:
        return {
            "id": self.id,
            "name": self.name,
            "entity_type": self.entity_type,
            "jurisdiction": self.jurisdiction,
            "capacity": self.capacity,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "knowledge_base": self.knowledge_base,
            "risk_profile": self.risk_profile,
            "compliance_status": self.compliance_status,
        }

    @classmethod
    def from_dict(cls, data: Dict) -> "LegalEntity":
        entity = cls(
            name=data["name"],
            entity_type=data["entity_type"],
            jurisdiction=data.get("jurisdiction", "russia"),
        )
        entity.capacity = data.get("capacity", {})
        entity.knowledge_base = data.get("knowledge_base", {})
        entity.risk_profile = data.get("risk_profile", {})
        entity.compliance_status = data.get("compliance_status", {})
        return entity


class PhysicalPerson(LegalEntity):
    """
    Физическое лицо — индивидуальный субъект права.
    
    Подкатегории:
    - Гражданин РФ
    - Иностранный гражданин
    - Лицо без гражданства (апатрид)
    - Лицо с двойным гражданством (бипатрид)
    """

    def __init__(self, name: str, citizenship: str = "russian",
                 age_group: str = "adult", jurisdiction: str = "russia"):
        super().__init__(name, "physical", jurisdiction)
        self.citizenship = citizenship
        self.age_group = age_group
        self._setup_physical_person()

    def _setup_physical_person(self):
        """Настройка правоспособности физического лица."""
        self.capacity = {
            "general_capacity": True,
            "active_capacity": True,
            "capacity_for_rights": True,
        }

        if self.citizenship == "russian":
            self.capacity.update({
                "citizenship": "Гражданин Российской Федерации",
                "political_rights": {"vote": True, "be_elected": True, "state_service": True},
                "military_service": {"conscription": True, "contract": True},
                "position": "Полноправный гражданин РФ",
                "restrictions": [],
            })
            self.knowledge_base["гражданство"] = {
                "определение": "Постоянно проживающее лицо, имеющее правовую связь с РФ",
                "права": ["Избирать и быть избранными", "Занимать государственные должности",
                          "Служить в ВС по призыву и контракту", "Свобода передвижения"],
                "обязанности": ["Соблюдать Конституцию", "Платить налоги", "Защищать РФ"],
                "источники": ["Конституция РФ, главы 1, 2", "ФКЗ О гражданстве РФ"],
            }

        elif self.citizenship == "foreign":
            self.capacity.update({
                "citizenship": "Иностранный гражданин",
                "political_rights": {"vote": False, "be_elected": False, "state_service": False},
                "military_service": {"conscription": False, "contract": True},
                "position": "Иностранец на территории РФ",
                "restrictions": [
                    "Не может избирать и быть избранными в федеральные органы власти",
                    "Не может занимать определенные государственные должности",
                    "Не может служить в ВС по призыву",
                ],
            })
            self.knowledge_base["иностранцы"] = {
                "определение": "Лицо, являющееся гражданином иностранного государства",
                "права": ["Жить в РФ (с разрешением)", "Трудиться (с патентом/разрешением)",
                          "Владеть имуществом", "Обращаться в суд"],
                "ограничения": ["Нет политических прав в федеральных органах",
                                "Нет государственных должностей", "Нет призыва в ВС"],
                "основания": ["Гр. РФ ст. 62", "ФЗ-115 О правовом положении"],
            }

        elif self.citizenship == "stateless":
            self.capacity.update({
                "citizenship": "Лицо без гражданства (апатрид)",
                "political_rights": {"vote": False, "be_elected": False, "state_service": False},
                "military_service": {"conscription": False, "contract": True},
                "position": "Апатрид на территории РФ",
                "restrictions": [
                    "Нет политических прав",
                    "Требуется разрешение на проживание",
                ],
            })
            self.knowledge_base["апатриды"] = {
                "определение": "Лицо, не признаваемое гражданином никаким государством",
                "права": ["Жить в РФ (с видом на жительство)", "Трудиться", "Владеть имуществом"],
                "ограничения": ["Нет политических прав", "Статус требует подтверждения"],
                "источники": ["Конвенция о статусе апатридов 1954", "Гр. РФ"],
            }

        elif self.citizenship == "dual":
            self.capacity.update({
                "citizenship": "Лицо с двойным гражданством (бипатрид)",
                "political_rights": {"vote": True, "be_elected": True, "state_service": True},
                "military_service": {"conscription": True, "contract": True},
                "position": "Гражданин РФ и другого государства",
                "restrictions": [
                    "В вопросах РФ считается гражданином РФ",
                    "Договоры о двойном гражданстве ограничивают список",
                ],
            })
            self.knowledge_base["двойное_гражданство"] = {
                "определение": "Лицо, имеющее гражданство двух и более государств",
                "правило": "На территории РФ бипатрид считается гражданином РФ",
                "ограничения": ["Договоры о двойном гражданстве с конкретными странами"],
                "источники": ["Конституция РФ", "Договоры о двойном гражданстве"],
            }

        # Возрастная группа
        self.knowledge_base["возрастные_группы"] = {
            "child_0_14": {
                "возраст": "0-14 лет",
                "дееспособность": "Частичная (через родителей/опекунов)",
                "права": ["На имя (депозитный счёт)", "На охрану здоровья", "На образование",
                          "На защиту интересов", "На собственность"],
            },
            "teen_14_18": {
                "возраст": "14-18 лет",
                "дееспособность": "Частичная (с 14 лет по ст. 26 ГК РФ)",
                "права": ["Распоряжаться карманными деньгами", "Делать вклады",
                          "Согласие на обработку ПД", "Авторские права",
                          "С 16 лет — работать (с согласия родителей)", "Эмансипация с 16 лет"],
            },
            "adult_18_plus": {
                "возраст": "18+ лет",
                "дееспособность": "Полная",
                "права": ["Полная гражданская дееспособность", "Избирать и быть избранными",
                          "Заключать любые сделки", "Создавать юрлица"],
            },
        }

    def get_restriction_list(self) -> List[str]:
        restrictions = self.capacity.get("restrictions", [])
        return restrictions if isinstance(restrictions, list) else []

    def get_full_profile(self) -> Dict:
        return {
            **self.to_dict(),
            "full_profile": {
                "citizenship_type": self.citizenship,
                "age_group": self.age_group,
                "restrictions": self.get_restriction_list(),
                "legal_domains": self._get_legal_domains(),
            }
        }

    def _get_legal_domains(self) -> List[str]:
        """Определяет применимые отрасли права."""
        domains = ["Гражданское право", "Семейное право", "Трудовое право", "Административное право",
                    "Налоговое право", "Уголовное право", "Конституционное право"]
        if self.citizenship != "russian":
            domains.append("Миграционное право")
        return domains


class LegalEntity_Corporation(LegalEntity):
    """
    Юридическое лицо — коллективный субъект права.
    
    Типы:
    - Коммерческие (ООО, АО, ПАО, ИП)
    - Некоммерческие (АНО, Фонды, Ассоциации, Учреждения)
    """

    def __init__(self, name: str, org_type: str = "ooo",
                 form: str = "commercial", jurisdiction: str = "russia"):
        super().__init__(name, "legal", jurisdiction)
        self.org_type = org_type
        self.form = form
        self._setup_corporation()

    def _setup_corporation(self):
        """Настройка правоспособности юридического лица."""
        self.capacity = {
            "separate_property": True,
            "independent_liability": True,
            "party_in_court": True,
            "buy_sell_rights": True,
            "hire_fire_rights": True,
        }

        if self.form == "commercial":
            org_types = {
                "ooo": {
                    "name": "Общество с ограниченной ответственностью",
                    "description": "Коммерческая организация с уставным капиталом, разделённым на доли",
                    "features": [
                        "Участники не отвечают по обязательствам",
                        "Отвечают в пределах вклада",
                        "Мин. уставный капитал: 10 000 руб.",
                        "Мин. участников: 1, макс.: 50",
                    ],
                    "legal_base": "ГК РФ ст. 87-91, ФЗ-14 'Об ООО'",
                },
                "ao": {
                    "name": "Акционерное общество",
                    "description": "Коммерческая организация с уставным капиталом, разделённым на акции",
                    "features": [
                        "Акции — ценная бумага",
                        "Акционеры не отвечают по обязательствам",
                        "Мин. уставный капитал: 100 МРОТ",
                        "Мин. акционеров: 1 (ПАО: 5+)",
                    ],
                    "legal_base": "ГК РФ ст. 96-104, ФЗ-208 'Об АО'",
                },
                "ip": {
                    "name": "Индивидуальный предприниматель",
                    "description": "Физическое лицо, зарегистрированное для предпринимательской деятельности",
                    "features": [
                        "Не является юридическим лицом",
                        "Отвечает всем имуществом",
                        "Может иметь наёмных работников",
                        "Упрощённая регистрация и отчётность",
                    ],
                    "legal_base": "ГК РФ ст. 23, ФЗ-129 'О гос. регистрации'",
                },
            }
            self.capacity.update(org_types.get(self.org_type, org_types["ooo"]))
            self.knowledge_base["коммерческие_организации"] = {
                "определение": "Коллективные субъекты, основная цель — извлечение прибыли",
                "критерии": ["Уставный капитал", "Разделённое имущество", "Собственная ответственность",
                             "Способность приобретать права и нести обязанности"],
                "налоговые_режимы": ["ОСНО", "УСН (доход 6%)", "УСН (доход-расходы 15%)",
                                     "ЕНВД", "Патентная система", "АУСН"],
                "отчётность": ["Бухгалтерский баланс", "Налоговые декларации", "Статистическая отчётность",
                              "Отчёты во внебюджетные фонды"],
            }

        elif self.form == "noncommercial":
            nco_types = {
                "ano": {
                    "name": "Автономная некоммерческая организация",
                    "description": "Некоммерческая организация, созданная для оказания услуг",
                    "features": ["Учредители могут быть юрлицами и физлицами",
                                 "Не распределяет прибыль", "Цель — оказание услуг"],
                },
                "fund": {
                    "name": "Благотворительный фонд",
                    "description": "Некоммерческая организация, имеющая имущество для благотворительных целей",
                    "features": ["Имущество определяется уставными целями",
                                 "Не распределяет прибыль", "Может быть международным"],
                },
                "association": {
                    "name": "Ассоциация/Союз",
                    "description": "Объединение юридических лиц для представления интересов",
                    "features": ["Членство добровольное", "Учредители — юрлица",
                                 "Управление через съезд/общее собрание"],
                },
                "institution": {
                    "name": "Учреждение",
                    "description": "Организация, созданная собственником для оказания услуг",
                    "features": ["Собственник — государство/муниципалитет",
                                 "Финансируется из бюджета", "Ответственность собственника"],
                },
            }
            self.capacity.update(nco_types.get(self.org_type, nco_types["ano"]))
            self.knowledge_base["некоммерческие_организации"] = {
                "определение": "Коллективные субъекты, основная цель — социальные, благотворительные, культурные цели",
                "критерии": ["Не распределяют прибыль между участниками",
                             "Имущество закреплено за организацией", "Самостоятельная ответственность"],
                "особенности": ["Регулирование ФЗ-7 'О некоммерческих организациях'",
                                "Возможна ликвидация без перехода имущества",
                                "Обязательная отчётность о целевом использовании средств"],
            }


class PublicEntity(LegalEntity):
    """
    Публично-правовое образование — крупный субъект права.
    
    Уровни:
    - Государство (РФ в целом)
    - Субъекты РФ (республики, края, области и т.д.)
    - Муниципальные образования
    """

    def __init__(self, name: str, public_level: str, jurisdiction: str = "russia"):
        super().__init__(name, "public", jurisdiction)
        self.public_level = public_level
        self._setup_public_entity()

    def _setup_public_entity(self):
        """Настройка правоспособности публично-правового образования."""
        levels = {
            "state": {
                "name": "Государство (Российская Федерация)",
                "description": "Самый крупный субъект права, носитель государственной власти",
                "status": {
                    "international_relations": True,
                    "state_debts": True,
                    "federal_property": True,
                    "sovereignty": True,
                    "legislation": True,
                    "currency": True,
                    "defense": True,
                    "foreign_policy": True,
                    "federal_budget": True,
                },
                "legal_base": "Конституция РФ, главы 1, 3, 4, 5",
                "powers": [
                    "Принимать федеральные законы",
                    "Устанавливать федеральный бюджет",
                    "Вести международные отношения",
                    "Обеспечивать оборону и безопасность",
                    "Управлять федеральной собственностью",
                    "Устанавливать гражданство РФ",
                    "Решать вопросы войны и мира",
                ],
            },
            "federal_subject": {
                "name": "Субъект Российской Федерации",
                "description": "Республика, край, область, город федерального значения, АО, автономная область",
                "types": [
                    "Республика (государственное образование)",
                    "Край",
                    "Область",
                    "Город федерального значения (Москва, Санкт-Петербург, Севастополь)",
                    "Автономная область",
                    "Автономный округ",
                ],
                "powers": [
                    "Принимать конституцию/устав",
                    "Устанавливать региональный бюджет",
                    "Управлять региональной собственностью",
                    "Региональное законодательство (в пределах компетенции)",
                    "Представительство в Совете Федерации",
                ],
                "legal_base": "Конституция РФ ст. 5, 71-73",
            },
            "municipal": {
                "name": "Муниципальное образование",
                "description": "Городское/сельское поселение, муниципальный район, городской округ",
                "types": [
                    "Городское поселение",
                    "Сельское поселение",
                    "Муниципальный район",
                    "Городской округ",
                ],
                "powers": [
                    "Принимать устав муниципалитета",
                    "Устанавливать местный бюджет",
                    "Управлять муниципальной собственностью",
                    "Организовывать жизнеобеспечение",
                    "Контроль за использованием земель",
                    "Организация транспорта, ЖКХ, образования, здравоохранения",
                ],
                "legal_base": "Конституция РФ ст. 12, ФЗ-131 'О местном самоуправлении'",
            },
        }

        level_data = levels.get(self.public_level, levels["state"])
        self.capacity.update(level_data.get("status", {}))
        self.knowledge_base["публично_правовые"] = {
            "определение": "Крупнейшие субъекты права, выступающие как носители государственной или муниципальной власти",
            "уровень": level_data.get("name", self.public_level),
            "описание": level_data.get("description", ""),
            "полномочия": level_data.get("powers", []),
            "правовая_база": level_data.get("legal_base", ""),
            "особенности": [
                "Выступают не просто как организации, а как носители власти",
                "Обладают властными полномочиями (издание нормативных актов)",
                "Несут ответственность по долгам соответствующего уровня",
                "Являются собственниками соответствующего имущества",
                "Действуют от имени государства/муниципалитета",
            ],
        }


class SocialCommunity(LegalEntity):
    """
    Социальная общность — коллективный субъект права.
    
    Категории:
    - Народы, нации
    - Население определённых территорий
    """

    def __init__(self, name: str, community_type: str, jurisdiction: str = "russia"):
        super().__init__(name, "social", jurisdiction)
        self.community_type = community_type
        self._setup_social_community()

    def _setup_social_community(self):
        """Настройка правоспособности социальной общности."""
        self.knowledge_base["социальные_общности"] = {
            "определение": "Народы, нации, население определённых территорий — субъекты, чей правовой статус проявляется в конституционном праве",
            "категории": {
                "народ": {
                    "определение": "Совокупность людей, объединённых общей историей, культурой, языком",
                    "права": ["Право на самоопределение", "Право на сохранение языка и культуры",
                              "Право на родной язык", "Право на образование на родном языке"],
                    "источники": ["Конституция РФ преамбула", "Декларация прав коренных народов ООН"],
                },
                "нация": {
                    "определение": "Исторически сложившаяся общность людей с общим языком, культурой, территорией",
                    "права": ["Культурная автономия", "Языковые права", "Национально-культурная автономия"],
                    "источники": ["ФЗ-36 'О национально-культурной автономии'"],
                },
                "население_территории": {
                    "определение": "Жители определённой территории, обладающие правом местного самоуправления",
                    "права": ["Право на местное самоуправление", "Право на участие в опросах/референдумах",
                              "Право на обращение в органы власти", "Право на доступ к информации"],
                    "источники": ["Конституция РФ ст. 12-13", "ФЗ-131 'О МС'"],
                },
            },
            "ключевые_права": [
                "Самоопределение наций",
                "Местное самоуправление",
                "Референдум",
                "Право на петиции и обращения",
                "Культурная автономия",
            ],
            "ограничения": [
                "Не являются юридическими лицами",
                "Не могут владеть имуществом в своём имени",
                "Правовой статус определяется конституционным правом",
                "Представляются через избранные органы",
            ],
        }

        self.capacity = {
            "constitutional_rights": True,
            "property_rights": False,
            "party_in_court": False,
            "self_governance": True,
            "representation": "Через избранные органы и представителей",
        }


class PublicAuthority(LegalEntity):
    """
    Орган публичной власти — субъект с властными полномочиями.
    
    Категории:
    - Министерства
    - Ведомства
    - Суды
    - Прокуратура
    - Полиция
    - Налоговые инспекции
    """

    def __init__(self, name: str, authority_type: str, jurisdiction: str = "russia"):
        super().__init__(name, "authority", jurisdiction)
        self.authority_type = authority_type
        self._setup_authority()

    def _setup_authority(self):
        """Настройка правоспособности органа публичной власти."""
        authorities = {
            "ministry": {
                "name": "Министерство",
                "description": "Федеральный орган исполнительной власти, осуществляющий выработку и реализацию политики",
                "powers": [
                    "Выработка государственной политики",
                    "Нормативное регулирование",
                    "Контроль и надзор в своей сфере",
                    "Управление федеральным имуществом",
                    "Международное сотрудничество в своей сфере",
                ],
                "legal_base": "Постановление Правительства, Положение о министерстве",
            },
            "service": {
                "name": "Федеральная служба",
                "description": "Орган исполнительной власти с контрольно-надзорными функциями",
                "powers": [
                    "Контроль и надзор",
                    "Выдача лицензий и разрешений",
                    "Применение мер ответственности",
                    "Регистрация объектов",
                ],
                "legal_base": "Постановление Правительства, Положение о службе",
            },
            "agency": {
                "name": "Федеральное агентство",
                "description": "Орган исполнительной власти с управленческими и сервисными функциями",
                "powers": [
                    "Управление федеральным имуществом",
                    "Оказание государственных услуг",
                    "Лицензирование",
                    "Аккредитация",
                ],
                "legal_base": "Постановление Правительства, Положение об агентстве",
            },
            "court": {
                "name": "Суд",
                "description": "Орган судебной власти, осуществляющий правосудие",
                "powers": [
                    "Рассмотрение гражданских дел",
                    "Рассмотрение уголовных дел",
                    "Рассмотрение административных дел",
                    "Конституционный контроль (для КС РФ)",
                    "Толкование права",
                    "Обеспечение законности",
                ],
                "legal_base": "Конституция РФ гл. 7, ФЗ-1 «О судебных органах»",
                "types": ["Конституционный суд", "Суд общей юрисдикции", "Арбитражный суд",
                          "Мировой судья", "Военный суд"],
            },
            "prosecutor": {
                "name": "Прокуратура",
                "description": "Централизованная иерархическая система надзора за исполнением законов",
                "powers": [
                    "Надзор за исполнением законов",
                    "Координация борьбы с преступностью",
                    "Участие в рассмотрении дел судами",
                    "Протестирование нормативных актов",
                    "Возбуждение дел об административных правонарушениях",
                    "Надзор за местами содержания задержанных",
                ],
                "legal_base": "ФЗ-2201-1 «О прокуратуре РФ»",
            },
            "police": {
                "name": "Полиция",
                "description": "Основной орган по охране общественного порядка и борьбе с преступностью",
                "powers": [
                    "Охрана общественного порядка",
                    "Предотвращение и пресечение преступлений",
                    "Розыск преступников",
                    "Административное задержание",
                    "Применение мер принуждения",
                    "Досмотр, задержание, проверка документов",
                ],
                "legal_base": "ФЗ-3 «О полиции»",
            },
            "tax": {
                "name": "Налоговая инспекция (ФНС)",
                "description": "Орган налогового контроля",
                "powers": [
                    "Регистрация налогоплательщиков",
                    "Налоговый контроль (проверки)",
                    "Взыскание налогов и сборов",
                    "Назначение налоговых вычетов",
                    "Ведение ЕГРЮЛ/ЕГРИП",
                    "Администрирование страховых взносов",
                ],
                "legal_base": "Налоговый кодекс РФ, ФЗ-101 «О ФНС»",
            },
        }

        auth_data = authorities.get(self.authority_type, authorities["ministry"])
        self.capacity.update({
            "public_authority": True,
            "state_powers": auth_data.get("powers", []),
            "legal_base": auth_data.get("legal_base", ""),
            "acts_as": "От имени государства/муниципалитета",
            "purpose": "Выполнение функций государства/муниципалитета",
        })
        self.knowledge_base["орган_власти"] = {
            "определение": "Органы публичной власти обладают властными полномочиями и действуют от имени государства для выполнения его функций",
            "тип": auth_data.get("name", self.authority_type),
            "описание": auth_data.get("description", ""),
            "полномочия": auth_data.get("powers", []),
            "правовая_база": auth_data.get("legal_base", ""),
            "особенности": [
                "Обладают властными полномочиями (приказ, решение, предписание)",
                "Действуют от имени государства или муниципалитета",
                "Их акты обязательны для исполнения",
                "Решения могут быть обжалованы в суде",
                "Должностные лица несут дисциплинарную, административную, уголовную ответственность",
            ],
        }


class UnregisteredAssociation(LegalEntity):
    """
    Общественное объединение без статуса юридического лица.
    
    Категории:
    - Незарегистрированные профсоюзы
    - Инициативные группы граждан
    - Религиозные группы
    """

    def __init__(self, name: str, association_type: str, jurisdiction: str = "russia"):
        super().__init__(name, "unregistered", jurisdiction)
        self.association_type = association_type
        self._setup_unregistered()

    def _setup_unregistered(self):
        """Настройка правоспособности общественного объединения."""
        self.knowledge_base["общественные_объединения"] = {
            "определение": "Объединения, которые ещё не прошли регистрацию как юридические лица, но уже имеют определённые права",
            "категории": {
                "trade_union": {
                    "name": "Незарегистрированный профсоюз",
                    "description": "Объединение работников для защиты трудовых прав",
                    "права": [
                        "Представлять интересы участников в суде",
                        "Обращаться в органы власти",
                        "Проводить собрания и митинги",
                        "Вести коллективные переговоры (после регистрации)",
                    ],
                    "ограничения": [
                        "Не может владеть имуществом",
                        "Не может заключать договоры от своего имени",
                        "Не может быть ответчиком в суде",
                    ],
                    "источники": ["ФЗ-10 «О профессиональных союзах»", "ТК РФ ст. 30"],
                },
                "initiative_group": {
                    "name": "Инициативная группа граждан",
                    "description": "Группа граждан, объединённых общей целью",
                    "права": [
                        "Обращаться с петициями в органы власти",
                        "Проводить собрания",
                        "Представлять интересы группы в суде (через представителя)",
                        "Участвовать в выборах (для инициативных групп по сбору подписей)",
                    ],
                    "ограничения": [
                        "Не может от своего имени приобретать права",
                        "Не может быть стороной в договоре",
                        "Ответственность несут отдельные участники",
                    ],
                    "источники": ["ГК РФ ст. 21", "ФЗ-67 'О выборах'", "ГК РФ ст. 123.1"],
                },
                "religious_group": {
                    "name": "Религиозная группа",
                    "description": "Группа лиц, объединённых для совместного исповедания религии",
                    "права": [
                        "Совместное исповедание религии",
                        "Проведение богослужений",
                        "Обращаться в органы власти",
                        "Создать религиозную организацию (после регистрации)",
                    ],
                    "ограничения": [
                        "Не имеет статуса юридического лица",
                        "Не может владеть имуществом от своего имени",
                        "Требуется 10 граждан для создания организации",
                    ],
                    "источники": ["ФЗ-125 'О свободе совести'", "ГК РФ ст. 123.22"],
                },
            },
            "общие_правила": {
                "права": [
                    "Представлять интересы участников в суде",
                    "Обращаться в органы власти",
                    "Проводить собрания и мероприятия",
                    "Получать членские взносы",
                ],
                "ограничения": [
                    "Нет полной правоспособности коммерческой компании",
                    "Не может владеть имуществом от своего имени",
                    "Не может заключать договоры от своего имени",
                    "Ответственность несут отдельные участники",
                ],
            },
        }

        self.capacity = {
            "partial_capacity": True,
            "court_representation": True,
            "authority_contact": True,
            "property_rights": False,
            "contract_rights": False,
            "liability": "Индивидуальная (участники)",
        }


class LegalEntitiesManager:
    """
    Менеджер субъектов права.
    
    Управляет всеми категориями субъектов:
    - Физические лица (граждане, иностранцы, апатриды, бипатриды)
    - Юридические лица (коммерческие, некоммерческие)
    - Публично-правовые образования (государство, субъекты, муниципалитеты)
    - Социальные общности (народы, нации, население территорий)
    - Органы публичной власти (министерства, суды, прокуратура и т.д.)
    - Общественные объединения без статуса юрлица
    """

    def __init__(self, state_dir: str = "futaba/engine/state"):
        self.state_dir = Path(state_dir)
        self.state_dir.mkdir(parents=True, exist_ok=True)

        self.entities_file = self.state_dir / "legal_entities.json"
        self.knowledge_base_file = self.state_dir / "legal_entity_knowledge.json"
        self.compliance_file = self.state_dir / "entity_compliance.json"

        self.entities: Dict[str, LegalEntity] = {}
        self.knowledge: Dict[str, Any] = {}
        self.compliance_records: Dict[str, Any] = {}
        self.legal_studies = None  # будет установлен извне

        self._load_state()

    def _load_state(self):
        """Загрузка состояния из файлов."""
        if self.entities_file.exists():
            try:
                with open(self.entities_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    for item in data.get("entities", []):
                        etype = item.get("entity_type", "")
                        if etype == "physical":
                            self.entities[item["id"]] = PhysicalPerson(
                                item["name"],
                                item.get("citizenship", "russian"),
                                item.get("age_group", "adult"),
                                item.get("jurisdiction", "russia"),
                            )
                        elif etype == "legal":
                            self.entities[item["id"]] = LegalEntity_Corporation(
                                item["name"],
                                item.get("org_type", "ooo"),
                                item.get("form", "commercial"),
                                item.get("jurisdiction", "russia"),
                            )
                        elif etype == "public":
                            self.entities[item["id"]] = PublicEntity(
                                item["name"],
                                item.get("public_level", "state"),
                                item.get("jurisdiction", "russia"),
                            )
                        elif etype == "social":
                            self.entities[item["id"]] = SocialCommunity(
                                item["name"],
                                item.get("community_type", "people"),
                                item.get("jurisdiction", "russia"),
                            )
                        elif etype == "authority":
                            self.entities[item["id"]] = PublicAuthority(
                                item["name"],
                                item.get("authority_type", "ministry"),
                                item.get("jurisdiction", "russia"),
                            )
                        elif etype == "unregistered":
                            self.entities[item["id"]] = UnregisteredAssociation(
                                item["name"],
                                item.get("association_type", "initiative"),
                                item.get("jurisdiction", "russia"),
                            )
                self.knowledge = data.get("knowledge", {})
                self.compliance_records = data.get("compliance", {})
            except Exception as e:
                print(f"⚠️ Ошибка загрузки состояния: {e}")

    def _save_state(self):
        """Сохранение состояния в файлы."""
        entities_data = []
        for entity in self.entities.values():
            entities_data.append(entity.to_dict())

        data = {
            "entities": entities_data,
            "knowledge": self.knowledge,
            "compliance": self.compliance_records,
            "updated": datetime.now().isoformat(),
        }

        with open(self.entities_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

        with open(self.knowledge_base_file, 'w', encoding='utf-8') as f:
            json.dump(self.knowledge, f, ensure_ascii=False, indent=2)

        with open(self.compliance_file, 'w', encoding='utf-8') as f:
            json.dump(self.compliance_records, f, ensure_ascii=False, indent=2)

    # ===================== СОЗДАНИЕ СУБЪЕКТОВ =====================

    def create_physical_person(self, name: str, citizenship: str = "russian",
                               age_group: str = "adult") -> PhysicalPerson:
        """Создаёт субъект — физическое лицо."""
        entity = PhysicalPerson(name, citizenship, age_group)
        self.entities[entity.id] = entity
        self._save_state()
        print(f"✅ Создано физическое лицо: {name} ({citizenship})")
        return entity

    def create_legal_entity(self, name: str, org_type: str = "ooo",
                            form: str = "commercial") -> LegalEntity_Corporation:
        """Создаёт субъект — юридическое лицо."""
        entity = LegalEntity_Corporation(name, org_type, form)
        self.entities[entity.id] = entity
        self._save_state()
        print(f"✅ Создано юридическое лицо: {name} ({org_type})")
        return entity

    def create_public_entity(self, name: str, public_level: str = "state") -> PublicEntity:
        """Создаёт субъект — публично-правовое образование."""
        entity = PublicEntity(name, public_level)
        self.entities[entity.id] = entity
        self._save_state()
        print(f"✅ Создано публично-правовое образование: {name}")
        return entity

    def create_social_community(self, name: str,
                                 community_type: str = "people") -> SocialCommunity:
        """Создаёт субъект — социальную общность."""
        entity = SocialCommunity(name, community_type)
        self.entities[entity.id] = entity
        self._save_state()
        print(f"✅ Создана социальная общность: {name}")
        return entity

    def create_public_authority(self, name: str,
                                 authority_type: str = "ministry") -> PublicAuthority:
        """Создаёт субъект — орган публичной власти."""
        entity = PublicAuthority(name, authority_type)
        self.entities[entity.id] = entity
        self._save_state()
        print(f"✅ Создан орган публичной власти: {name}")
        return entity

    def create_unregistered_association(self, name: str,
                                         association_type: str = "initiative") -> UnregisteredAssociation:
        """Создаёт субъект — общественное объединение без статуса юрлица."""
        entity = UnregisteredAssociation(name, association_type)
        self.entities[entity.id] = entity
        self._save_state()
        print(f"✅ Создано общественное объединение: {name}")
        return entity

    # ===================== АНАЛИЗ СУБЪЕКТОВ =====================

    def analyze_entity(self, entity_id: str) -> Optional[Dict]:
        """Полный анализ субъекта права."""
        entity = self.entities.get(entity_id)
        if not entity:
            return None

        analysis = {
            "entity": entity.to_dict(),
            "type_classification": self._classify_entity(entity),
            "legal_domains": self._get_applicable_domains(entity),
            "rights_obligations": self._get_rights_obligations(entity),
            "risk_assessment": self._assess_risks(entity),
            "compliance_check": self._check_compliance(entity),
        }
        return analysis

    def _classify_entity(self, entity: LegalEntity) -> Dict:
        """Классификация субъекта по всем критериям."""
        classification = {
            "main_type": "индивидуальный" if entity.entity_type == "physical" else "коллективный",
            "sub_type": entity.entity_type,
            "group": "",
        }

        if entity.entity_type == "physical":
            classification["group"] = "Индивидуальные субъекты"
            if hasattr(entity, 'citizenship'):
                classification["citizenship_type"] = entity.citizenship
        elif entity.entity_type == "legal":
            classification["group"] = "Коллективные субъекты (юридические лица)"
            if hasattr(entity, 'form'):
                classification["form"] = entity.form
        elif entity.entity_type == "public":
            classification["group"] = "Публично-правовые образования"
        elif entity.entity_type == "social":
            classification["group"] = "Социальные общности"
        elif entity.entity_type == "authority":
            classification["group"] = "Органы публичной власти"
        elif entity.entity_type == "unregistered":
            classification["group"] = "Общественные объединения без статуса юрлица"

        return classification

    def _get_applicable_domains(self, entity: LegalEntity) -> List[str]:
        """Определяет применимые отрасли права."""
        domains = []

        if entity.entity_type == "physical":
            domains = [
                "Конституционное право", "Гражданское право", "Семейное право",
                "Трудовое право", "Административное право", "Налоговое право",
                "Уголовное право",
            ]
            if hasattr(entity, 'citizenship') and entity.citizenship != "russian":
                domains.append("Миграционное право")
        elif entity.entity_type == "legal":
            domains = [
                "Корпоративное право", "Налоговое право", "Трудовое право",
                "Гражданское право", "Административное право", "Земельное право",
                "Таможенное право",
            ]
        elif entity.entity_type == "public":
            domains = [
                "Конституционное право", "Финансовое право", "Бюджетное право",
                "Административное право", "Земельное право",
            ]
        elif entity.entity_type == "social":
            domains = [
                "Конституционное право", "Международное право",
                "Этническое право",
            ]
        elif entity.entity_type == "authority":
            domains = [
                "Конституционное право", "Административное право",
                "Административно-процессуальное право", "Финансовое право",
            ]
        elif entity.entity_type == "unregistered":
            domains = [
                "Конституционное право", "Гражданское право",
                "Общественное право",
            ]

        return domains

    def _get_rights_obligations(self, entity: LegalEntity) -> Dict:
        """Получает права и обязанности субъекта."""
        result = {"rights": [], "obligations": []}

        if entity.entity_type == "physical":
            result["rights"] = [
                "Право на жизнь и свободу",
                "Право на собственность",
                "Право на труд",
                "Право на образование",
                "Право на охрану здоровья",
                "Право на судебную защиту",
            ]
            if hasattr(entity, 'citizenship') and entity.citizenship == "russian":
                result["rights"].extend([
                    "Право избирать и быть избранными",
                    "Право занимать государственные должности",
                    "Право на бесплатную юридическую помощь",
                ])
            result["obligations"] = [
                "Соблюдать Конституцию и законы",
                "Уважать права и свободы других лиц",
                "Платить законно установленные налоги",
                "Беречь природу и окружающую среду",
            ]

        elif entity.entity_type == "legal":
            result["rights"] = [
                "Право на наименование",
                "Право на имущество",
                "Право заключать сделки",
                "Право нанимать работников",
                "Право обращаться в суд",
            ]
            result["obligations"] = [
                "Соблюдать законодательство",
                "Платить налоги",
                "Предоставлять отчётность",
                "Соблюдать трудовое законодательство",
                "Охранять окружающую среду",
            ]

        elif entity.entity_type == "public":
            result["rights"] = [
                "Право на законодательную инициативу",
                "Право издавать нормативные акты",
                "Право на собственность",
                "Право на бюджет",
            ]
            result["obligations"] = [
                "Обеспечивать права граждан",
                "Соблюдать Конституцию",
                "Обеспечивать обороноспособность",
                "Обеспечивать жизнеобеспечение",
            ]

        return result

    def _assess_risks(self, entity: LegalEntity) -> Dict:
        """Оценка правовых рисков."""
        risk_levels = {"low": 0.2, "medium": 0.5, "high": 0.8, "critical": 1.0}

        risks = {
            "legal_risk": "medium",
            "compliance_risk": "medium",
            "financial_risk": "medium",
            "reputational_risk": "low",
            "risk_score": 0.5,
            "recommendations": [],
        }

        if entity.entity_type == "physical":
            risks["legal_risk"] = "low"
            risks["recommendations"] = [
                "Изучить свои права и обязанности",
                "Хранить документы (паспорт, ИНН, СНИЛС)",
                "Знать сроки исковой давности (3 года)",
            ]

        elif entity.entity_type == "legal":
            risks["legal_risk"] = "medium"
            risks["compliance_risk"] = "high"
            risks["recommendations"] = [
                "Вести бухгалтерский учёт",
                "Соблюдать налоговое законодательство",
                "Регулярно проходить аудит",
                "Вести реестр правоустанавливающих документов",
            ]

        elif entity.entity_type == "authority":
            risks["legal_risk"] = "high"
            risks["compliance_risk"] = "critical"
            risks["recommendations"] = [
                "Соблюдать procedure (процедуру принятия решений)",
                "Обеспечить прозрачность решений",
                "Регулярный контроль законности актов",
                "Обеспечить возможность обжалования",
            ]

        return risks

    def _check_compliance(self, entity: LegalEntity) -> Dict:
        """Проверка compliance."""
        return {
            "status": "pending",
            "checklist": self._get_compliance_checklist(entity),
            "last_check": None,
        }

    def _get_compliance_checklist(self, entity: LegalEntity) -> List[str]:
        """Чек-лист compliance для типа субъекта."""
        if entity.entity_type == "physical":
            return [
                "Регистрация по месту жительства",
                "Наличие паспорта",
                "ИНН и СНИЛС",
                "Налоговая декларация (если требуется)",
                "Соблюдение трудового законодательства (если работает)",
            ]
        elif entity.entity_type == "legal":
            return [
                "Государственная регистрация",
                "ИНН и ОГРН",
                "Бухгалтерский учёт",
                "Налоговая отчётность",
                "Отчётность во внебюджетные фонды",
                "Соблюдение трудового законодательства",
                "Лицензии (если требуется)",
                "Соблюдение авторских прав",
                "Защита персональных данных (152-ФЗ)",
            ]
        elif entity.entity_type == "public":
            return [
                "Соблюдение Конституции",
                "Соответствие федеральным законам",
                "Бюджетная дисциплина",
                "Прозрачность и открытость",
                "Обеспечение прав граждан",
            ]

        return ["Проверка в индивидуальном порядке"]

    # ===================== БАЗА ЗНАНИЙ =====================

    def add_knowledge(self, topic: str, content: Dict):
        """Добавляет знание в базу."""
        self.knowledge[topic] = {
            **content,
            "added_at": datetime.now().isoformat(),
            "source": "futaba_legal_studies",
        }
        self._save_state()
        print(f"📚 Добавлено знание: {topic}")

    def get_knowledge(self, topic: str) -> Optional[Dict]:
        """Получает знание по теме."""
        return self.knowledge.get(topic)

    def get_all_knowledge(self) -> Dict:
        """Получает все знания."""
        return self.knowledge

    def get_knowledge_summary(self) -> Dict:
        """Сводка по знаниям."""
        return {
            "total_topics": len(self.knowledge),
            "topics": list(self.knowledge.keys()),
            "last_updated": datetime.now().isoformat(),
        }

    # ===================== СТАТИСТИКА =====================

    def get_statistics(self) -> Dict:
        """Полная статистика по субъектам права."""
        stats = {
            "total_entities": len(self.entities),
            "by_type": {},
            "by_jurisdiction": {},
            "knowledge_count": len(self.knowledge),
        }

        for entity in self.entities.values():
            etype = entity.entity_type
            jurisdiction = entity.jurisdiction

            stats["by_type"][etype] = stats["by_type"].get(etype, 0) + 1
            stats["by_jurisdiction"][jurisdiction] = stats["by_jurisdiction"].get(jurisdiction, 0) + 1

        return stats

    def get_entity_list(self) -> List[Dict]:
        """Список всех субъектов."""
        return [
            {
                "id": e.id,
                "name": e.name,
                "entity_type": e.entity_type,
                "jurisdiction": e.jurisdiction,
            }
            for e in self.entities.values()
        ]

    # ===================== ЗАГРУЗКА ВСЕХ СУБЪЕКТОВ =====================

    def get_all_standard_entities(self) -> Dict:
        """Получает все стандартные субъекты права из legal_studies."""
        if self.legal_studies:
            return self.legal_studies.get_all_legal_entities()
        # Fallback — если legal_studies не установлен
        return {"groups": {}, "context_distinction": {}}

    def load_all_standard_entities(self):
        """Загружает стандартные субъекты права для полного анализа."""

        # === ФИЗИЧЕСКИЕ ЛИЦА ===
        self.create_physical_person("Гражданин РФ", "russian", "adult")
        self.create_physical_person("Иностранный гражданин", "foreign", "adult")
        self.create_physical_person("Апатрид", "stateless", "adult")
        self.create_physical_person("Бипатрид", "dual", "adult")
        self.create_physical_person("Ребёнок 10 лет", "russian", "child")
        self.create_physical_person("Подросток 16 лет", "russian", "teen")

        # === ЮРИДИЧЕСКИЕ ЛИЦА ===
        self.create_legal_entity("ООО 'Пример'", "ooo", "commercial")
        self.create_legal_entity("АО 'Пример'", "ao", "commercial")
        self.create_legal_entity("ИП Иванов", "ip", "commercial")
        self.create_legal_entity("АНО 'Центр'", "ano", "noncommercial")
        self.create_legal_entity("Благотворительный фонд", "fund", "noncommercial")
        self.create_legal_entity("Ассоциация 'Союз'", "association", "noncommercial")
        self.create_legal_entity("Государственное учреждение", "institution", "noncommercial")

        # === ПУБЛИЧНО-ПРАВОВЫЕ ОБРАЗОВАНИЯ ===
        self.create_public_entity("Российская Федерация", "state")
        self.create_public_entity("Республика Татарстан", "federal_subject")
        self.create_public_entity("Московская область", "federal_subject")
        self.create_public_entity("Городской округ Москва", "municipal")
        self.create_public_entity("Сельское поселение Берёзовка", "municipal")

        # === СОЦИАЛЬНЫЕ ОБЩНОСТИ ===
        self.create_social_community("Русский народ", "people")
        self.create_social_community("Российская нация", "nation")
        self.create_social_community("Население Москвы", "territorial_population")

        # === ОРГАНЫ ПУБЛИЧНОЙ ВЛАСТИ ===
        self.create_public_authority("Министерство цифрового развития", "ministry")
        self.create_public_authority("Федеральная налоговая служба", "service")
        self.create_public_authority("Федеральное агентство по культуре", "agency")
        self.create_public_authority("Конституционный суд РФ", "court")
        self.create_public_authority("Генеральная прокуратура РФ", "prosecutor")
        self.create_public_authority("МВД России", "police")
        self.create_public_authority("ФНС России", "tax")

        # === ОБЩЕСТВЕННЫЕ ОБЪЕДИНЕНИЯ БЕЗ СТАТУСА ЮРЛИЦА ===
        self.create_unregistered_association("Профсоюз работников IT", "trade_union")
        self.create_unregistered_association("Инициативная группа жителей", "initiative_group")
        self.create_unregistered_association("Религиозная группа верующих", "religious_group")

        print(f"\n✅ Загружено {len(self.entities)} стандартных субъектов права")
        print(f"📊 Статистика: {self.get_statistics()}")

        return self.get_statistics()


# ===================== ИНИЦИАЛИЗАЦИЯ =====================

# Глобальный экземпляр для импорта
_entities_manager: Optional[LegalEntitiesManager] = None


def get_entities_manager() -> LegalEntitiesManager:
    """Получить глобальный менеджер субъектов права."""
    global _entities_manager
    if _entities_manager is None:
        _entities_manager = LegalEntitiesManager()
    return _entities_manager


def init_legal_entities():
    """Инициализировать и загрузить все стандартные субъекты."""
    manager = get_entities_manager()
    manager.load_all_standard_entities()
    return manager


def link_legal_entities_to_studies(entities_manager: LegalEntitiesManager, legal_studies):
    """Связывает менеджер субъектов с модулем юридических исследований."""
    entities_manager.legal_studies = legal_studies


if __name__ == "__main__":
    # Принудительный UTF-8 для вывода (Windows-консоль использует cp1251)
    import sys as _sys
    for _stream in (_sys.stdout, _sys.stderr):
        _reconfigure = getattr(_stream, "reconfigure", None)
        if _reconfigure is not None:
            _reconfigure(encoding="utf-8")
    
    print("=" * 60)
    print("⚖️ СУБЪЕКТЫ ПРАВА ФУТАБЫ — Инициализация")
    print("=" * 60)

    manager = init_legal_entities()

    print("\n📊 Статистика:")
    stats = manager.get_statistics()
    for key, value in stats.items():
        print(f"  {key}: {value}")

    print("\n📋 Список субъектов:")
    for entity in manager.get_entity_list():
        print(f"  [{entity['entity_type']}] {entity['name']}")

    print("\n📚 База знаний:")
    knowledge = manager.get_knowledge_summary()
    print(f"  Тем: {knowledge['total_topics']}")

    print("\n✅ Инициализация завершена!")
