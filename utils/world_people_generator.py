# utils/world_people_generator.py
# Генератор людей, семей, организаций и стран на основе файлов знаний

import os
import re
import json
import random
import hashlib
import sys
from datetime import datetime
from typing import Dict, List, Optional, Any, Tuple
from pathlib import Path
from dataclasses import dataclass, field, asdict

# === Настройка кодировки для Windows ===
if sys.platform == "win32":
    import codecs
    sys.stdout = codecs.getwriter("utf-8")(sys.stdout.buffer, "strict")
    sys.stderr = codecs.getwriter("utf-8")(sys.stderr.buffer, "strict")


# ========================
# КОНФИГУРАЦИЯ
# ========================

DEFAULT_KNOWLEDGE_DIR = "data/knowledge"
DEFAULT_OUTPUT_DIR = "data/generated_worlds"

KNOWLEDGE_FILES = [
    "human_adolescence.md",
    "human_early_development.md",
    "human_emerging_adulthood.md",
    "human_late_adolescence.md",
    "human_middle_childhood.md",
    "human_24_years.md",
    "human_daily_life.md",
    "human_daily_routine.md",
]

# Японские имена для генерации
JAPANESE_NAMES_FILE = "japanese_names_complete.md"


# ========================
# DATA CLASSES
# ========================

@dataclass
class Person:
    """Персонаж с детальными параметрами из знаний"""
    id: str
    name: str
    age: int
    gender: str
    archetype: str
    education: str
    job: str
    finance: str
    housing: str
    relationships: str
    children: str
    region: str
    temperament: str
    sociality: str
    routine_type: str
    weekend_type: str
    parenting_style: str
    vacation_type: str
    health: str
    values: List[str] = field(default_factory=list)
    habits: List[str] = field(default_factory=list)
    goals: List[str] = field(default_factory=list)
    problems: List[str] = field(default_factory=list)
    created_at: str = ""
    
    def to_dict(self) -> Dict:
        return asdict(self)


@dataclass
class Family:
    """Семья с отношениями"""
    id: str
    name: str
    members: List[Dict] = field(default_factory=list)
    relationships: Dict[str, Dict] = field(default_factory=dict)
    traditions: List[str] = field(default_factory=list)
    problems: List[str] = field(default_factory=list)
    budget: str = "средний"
    housing: str = "квартира"
    region: str = "Москва"
    created_at: str = ""
    
    def to_dict(self) -> Dict:
        return asdict(self)


@dataclass
class Organization:
    """Организация/компания/группа"""
    id: str
    name: str
    type: str  # company, government, ngo, club, criminal
    size: str  # small, medium, large, corporation
    industry: str
    culture: str
    goals: List[str] = field(default_factory=list)
    members: List[str] = field(default_factory=list)
    resources: Dict[str, float] = field(default_factory=dict)
    reputation: float = 0.5
    created_at: str = ""
    
    def to_dict(self) -> Dict:
        return asdict(self)


@dataclass
class Country:
    """Страна/государство"""
    id: str
    name: str
    population: int
    gdp_per_capita: float
    government_type: str
    culture: str
    regions: List[str] = field(default_factory=list)
    cities: List[str] = field(default_factory=list)
    laws: List[str] = field(default_factory=list)
    traditions: List[str] = field(default_factory=list)
    international_relations: Dict[str, str] = field(default_factory=dict)
    created_at: str = ""
    
    def to_dict(self) -> Dict:
        return asdict(self)


# ========================
# KNOWLEDGE PARSER
# ========================

class KnowledgeParser:
    """Парсит markdown-файлы с знаниями"""
    
    def __init__(self, knowledge_dir: str = DEFAULT_KNOWLEDGE_DIR):
        self.knowledge_dir = Path(knowledge_dir)
        self.tables_cache: Dict[str, List[Dict]] = {}
        self.sections_cache: Dict[str, str] = {}
        
    def parse_file(self, filename: str) -> Dict[str, Any]:
        """Парсит markdown-файл и извлекает таблицы"""
        filepath = self.knowledge_dir / filename
        if not filepath.exists():
            print(f"⚠️ Файл не найден: {filepath}")
            return {}
            
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        result = {
            "tables": self._extract_tables(content),
            "sections": self._extract_sections(content),
        }
        
        return result
    
    def _extract_tables(self, content: str) -> List[Dict]:
        """Извлекает все markdown-таблицы из контента"""
        tables = []
        
        # Regex для markdown-таблиц
        table_pattern = r'(\|[^|\n]+\|(?:\n\|[-:| ]+\|)?(?:\n\|[^|\n]+\|)*)'
        matches = re.findall(table_pattern, content)
        
        for match in matches:
            table = self._parse_table(match)
            if table and len(table) > 1:
                tables.append(table)
        
        return tables
    
    def _parse_table(self, table_text: str) -> List[Dict]:
        """Парсит одну таблицу в список словарей"""
        lines = table_text.strip().split('\n')
        if len(lines) < 2:
            return []
        
        # Пропускаем разделительную строку
        headers = [h.strip() for h in lines[0].split('|') if h.strip()]
        data_lines = [l for l in lines[1:] if not re.match(r'^\|[\s\-:|]+\|$', l)]
        
        table_data = []
        for line in data_lines:
            values = [v.strip() for v in line.split('|') if v.strip()]
            if len(values) == len(headers):
                row = dict(zip(headers, values))
                table_data.append(row)
        
        return table_data
    
    def _extract_sections(self, content: str) -> Dict[str, str]:
        """Извлекает секции по заголовкам"""
        sections = {}
        
        # Regex для заголовков
        header_pattern = r'^(#{1,6})\s+(.+)$'
        current_header = None
        current_content = []
        
        for line in content.split('\n'):
            match = re.match(header_pattern, line)
            if match:
                if current_header:
                    sections[current_header] = '\n'.join(current_content)
                current_header = match.group(2).strip()
                current_content = []
            else:
                current_content.append(line)
        
        if current_header:
            sections[current_header] = '\n'.join(current_content)
        
        return sections
    
    def get_parameter_options(self, parameter: str) -> List[str]:
        """Возвращает варианты для параметра из знаний"""
        options = []
        
        # Словарь соответствий параметров и ключей в таблицах
        param_mapping = {
            "архетип": ["Архетип", "Тип", "Типаж"],
            "образование": ["Образование", "Обр", "Учеба"],
            "работа": ["Работа", "Профессия", "Должность", "Занятость"],
            "финансы": ["Финансы", "Деньги", "Доход", "Богатство"],
            "жильё": ["Жильё", "Жилье", "Дом", "Квартира"],
            "отношения": ["Отношения", "Семья", "Партнёр", "Партнер"],
            "дети": ["Дети", "Ребёнок", "Ребенок", "Чад"],
            "регион": ["Регион", "Город", "Место", "Локация"],
            "темперамент": ["Темперамент", "Характер", "Тип личности"],
            "социальность": ["Социальность", "Общение", "Экстраверсия"],
            "рутина": ["Рутина", "Распорядок", "Режим"],
            "выходные": ["Выходные", "Отдых", "Досуг"],
            "воспитание": ["Воспитание", "Дети", "Родительство"],
            "отпуск": ["Отпуск", "Каникулы", "Отдых"],
            "здоровье": ["Здоровье", "Здоров", "Физическое"],
            "ценности": ["Ценности", "Важно", "Приоритеты"],
            "привычки": ["Привычки", "Хаби", "Паттерны"],
            "цели": ["Цели", "Планы", "Амбиции"],
            "проблемы": ["Проблемы", "Сложности", "Трудности"],
            "традиции": ["Традиции", "Обычаи", "Ритуалы"],
            "законы": ["Законы", "Правила", "Нормы"],
        }
        
        keys_to_search = param_mapping.get(parameter.lower(), [parameter.capitalize(), parameter.title()])
        
        for filename in KNOWLEDGE_FILES:
            if filename not in self.tables_cache:
                parsed = self.parse_file(filename)
                self.tables_cache[filename] = parsed.get('tables', [])
            
            for table in self.tables_cache[filename]:
                for row in table:
                    # Ищем параметр в ключах
                    for key, value in row.items():
                        if any(k.lower() in key.lower() for k in keys_to_search):
                            if value and value != '—' and value.strip():
                                # Очищаем значение от кавычек и пробелов
                                clean_value = value.strip('"«»\'').strip()
                                # Разделяем по запятой если несколько значений
                                if ',' in clean_value:
                                    for v in clean_value.split(','):
                                        v = v.strip()
                                        if v and v not in options and len(v) > 2:
                                            options.append(v)
                                else:
                                    if clean_value not in options and len(clean_value) > 2:
                                        options.append(clean_value)
        
        # Возвращаем дефолтные значения если ничего не найдено
        if not options:
            defaults = {
                "архетип": ["Обычный человек", "Достигатор", "Ищущий"],
                "образование": ["Высшее", "Среднее", "Неполное высшее"],
                "работа": ["Офисный работник", "Специалист", "Менеджер"],
                "финансы": ["Средний класс", "Выше среднего", "Низкий"],
                "жильё": ["Квартира", "Дом", "Снимает"],
                "отношения": ["В отношениях", "Холост", "В браке"],
                "дети": ["Нет детей", "Один ребёнок", "Двое детей"],
                "регион": ["Москва", "Санкт-Петербург", "Регион"],
                "темперамент": ["Сангвиник", "Холерик", "Флегматик", "Меланхолик"],
                "социальность": ["Амбиверт", "Интроверт", "Экстраверт"],
                "рутина": ["Стандартная", "Хаотичная", "Размеренная"],
                "выходные": ["Активные", "Спокойные", "Домашние"],
                "воспитание": ["Авторитетный", "Либеральный", "Авторитарный"],
                "отпуск": ["Пляжный", "Активный", "Домашний"],
                "здоровье": ["Хорошее", "Среднее", "Отличное"],
                "ценности": ["Семья", "Карьера", "Развитие"],
                "привычки": ["Чтение", "Спорт", "Прогулки"],
                "цели": ["Развитие", "Путешествия", "Стабильность"],
                "проблемы": ["Усталость", "Стресс", "Время"],
                "традиции": ["Семейный ужин", "Праздники вместе"],
                "законы": ["Конституция", "Трудовой кодекс"],
            }
            return defaults.get(parameter.lower(), [f"Неизвестный {parameter}"])
        
        return options


# ========================
# GENERATORS
# ========================

class PeopleGenerator:
    """Генерирует людей, семьи, организации и страны"""
    
    def __init__(self, knowledge_dir: str = DEFAULT_KNOWLEDGE_DIR):
        self.parser = KnowledgeParser(knowledge_dir)
        self.knowledge_dir = Path(knowledge_dir)
        self.output_dir = Path(DEFAULT_OUTPUT_DIR)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Кэшированные данные
        self.knowledge_data: Dict[str, Any] = {}
        self._load_all_knowledge()
        
        # Генераторы имён
        self.first_names_male = [
            "Александр", "Дмитрий", "Максим", "Артём", "Иван", "Кирилл",
            "Андрей", "Михаил", "Сергей", "Алексей", "Никита", "Павел",
            "Владимир", "Константин", "Егор", "Илья", "Роман", "Тимофей"
        ]
        self.first_names_female = [
            "Анна", "Мария", "Елена", "Ольга", "Наталья", "Екатерина",
            "Анастасия", "Татьяна", "Юлия", "Светлана", "Ирина", "Ксения",
            "Дарья", "Полина", "Алина", "Виктория", "София", "Марина"
        ]
        self.last_names = [
            "Иванов", "Смирнов", "Кузнецов", "Попов", "Васильев", "Петров",
            "Соколов", "Михайлов", "Новиков", "Фёдоров", "Морозов", "Волков",
            "Алексеев", "Лебедев", "Семёнов", "Егоров", "Павлов", "Козлов"
        ]
    
        # Японские имена
        self.japanese_names_female = []
        self.japanese_names_male = []
        self.japanese_surnames = []
        self.japanese_locations = []
        self._load_japanese_names()
    
    def _load_japanese_names(self):
        """Загружает японские имена из файла"""
        filepath = self.knowledge_dir / JAPANESE_NAMES_FILE
        if not filepath.exists():
            print(f"⚠️ Файл японских имён не найден: {filepath}")
            return
        
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        current_section = None
        
        for line in content.split('\n'):
            line = line.strip()
            
            # Определяем секцию
            if '## 1. ЖЕНСКИЕ ИМЕНА' in line:
                current_section = 'female'
            elif '## 2. МУЖСКИЕ ИМЕНА' in line:
                current_section = 'male'
            elif '## 3. ФАМИЛИИ' in line:
                current_section = 'surname'
            elif '## 4. ГОРОДА И МЕСТА' in line:
                current_section = 'location'
            elif line.startswith('## '):
                current_section = None
            
            # Парсим строки таблиц
            if current_section and line.startswith('|') and '|' in line[1:]:
                parts = [p.strip() for p in line.split('|') if p.strip()]
                if len(parts) >= 2 and not parts[0].startswith('Имя') and not parts[0].startswith('Фамилия'):
                    name = parts[0]
                    if name and len(name) > 1 and name != '---':
                        if current_section == 'female':
                            self.japanese_names_female.append(name)
                        elif current_section == 'male':
                            self.japanese_names_male.append(name)
                        elif current_section == 'surname':
                            self.japanese_surnames.append(name)
                        elif current_section == 'location':
                            self.japanese_locations.append(name)
        
        print(f"✅ Загружено японских имён: женских={len(self.japanese_names_female)}, мужских={len(self.japanese_names_male)}, фамилий={len(self.japanese_surnames)}, локаций={len(self.japanese_locations)}")
    
    def generate_japanese_name(self, gender: Optional[str] = None) -> str:
        """Генерирует японское имя"""
        if gender is None:
            gender = random.choice(["мужской", "женский"])
        
        if gender == "мужской":
            if self.japanese_names_male:
                first_name = random.choice(self.japanese_names_male)
            else:
                first_name = "Хироси"
        else:
            if self.japanese_names_female:
                first_name = random.choice(self.japanese_names_female)
            else:
                first_name = "Сакура"
        
        if self.japanese_surnames:
            surname = random.choice(self.japanese_surnames)
        else:
            surname = "Танака"
        
        return f"{surname} {first_name}"
    
    def generate_japanese_location(self) -> str:
        """Генерирует японскую локацию"""
        if self.japanese_locations:
            return random.choice(self.japanese_locations)
        return "Токио"
    
    def _load_all_knowledge(self):
        """Загружает все файлы знаний"""
        for filename in KNOWLEDGE_FILES:
            self.knowledge_data[filename] = self.parser.parse_file(filename)
    
    def generate_person(self, age_range: Tuple[int, int] = (18, 40), 
                        gender: Optional[str] = None,
                        archetype: Optional[str] = None,
                        use_japanese_names: bool = False) -> Person:
        """Генерирует одного человека"""
        
        # Возраст
        age = random.randint(*age_range)
        
        # Пол
        if gender is None:
            gender = random.choice(["мужской", "женский"])
        
        # Имя
        if use_japanese_names:
            name = self.generate_japanese_name(gender)
        else:
            if gender == "мужской":
                first_name = random.choice(self.first_names_male)
            else:
                first_name = random.choice(self.first_names_female)
            last_name = random.choice(self.last_names)
            name = f"{first_name} {last_name}"
        
        # Архетип
        if archetype is None:
            archetypes = self.parser.get_parameter_options("архетип")
            archetype = random.choice(archetypes) if archetypes else "Обычный человек"
        
        # Параметры из знаний
        education = random.choice(self.parser.get_parameter_options("образование") or ["Высшее"])
        job = random.choice(self.parser.get_parameter_options("работа") or ["Офисный работник"])
        finance = random.choice(self.parser.get_parameter_options("финансы") or ["Средний класс"])
        housing = random.choice(self.parser.get_parameter_options("жильё") or ["Квартира"])
        relationships = random.choice(self.parser.get_parameter_options("отношения") or ["В отношениях"])
        children = random.choice(self.parser.get_parameter_options("дети") or ["Нет детей"])
        region = random.choice(self.parser.get_parameter_options("регион") or ["Москва"])
        temperament = random.choice(self.parser.get_parameter_options("темперамент") or ["Сангвиник"])
        sociality = random.choice(self.parser.get_parameter_options("социальность") or ["Амбиверт"])
        routine_type = random.choice(self.parser.get_parameter_options("рутина") or ["Стандартная"])
        weekend_type = random.choice(self.parser.get_parameter_options("выходные") or ["Активные"])
        parenting_style = random.choice(self.parser.get_parameter_options("воспитание") or ["Авторитетный"])
        vacation_type = random.choice(self.parser.get_parameter_options("отпуск") or ["Пляжный"])
        health = random.choice(self.parser.get_parameter_options("здоровье") or ["Хорошее"])
        
        # Ценности и привычки
        values = random.sample(self.parser.get_parameter_options("ценности") or ["Семья", "Карьера"], k=min(3, len(self.parser.get_parameter_options("ценности") or [])))
        habits = random.sample(self.parser.get_parameter_options("привычки") or ["Чтение", "Спорт"], k=min(3, len(self.parser.get_parameter_options("привычки") or [])))
        goals = random.sample(self.parser.get_parameter_options("цели") or ["Развитие", "Путешествия"], k=min(2, len(self.parser.get_parameter_options("цели") or [])))
        problems = random.sample(self.parser.get_parameter_options("проблемы") or ["Усталость", "Стресс"], k=min(2, len(self.parser.get_parameter_options("проблемы") or [])))
        
        # ID
        person_id = hashlib.md5(f"{name}:{age}:{datetime.now().isoformat()}".encode()).hexdigest()[:12]
        
        person = Person(
            id=person_id,
            name=name,
            age=age,
            gender=gender,
            archetype=archetype,
            education=education,
            job=job,
            finance=finance,
            housing=housing,
            relationships=relationships,
            children=children,
            region=region,
            temperament=temperament,
            sociality=sociality,
            routine_type=routine_type,
            weekend_type=weekend_type,
            parenting_style=parenting_style,
            vacation_type=vacation_type,
            health=health,
            values=values if values else ["Семья"],
            habits=habits if habits else ["Чтение"],
            goals=goals if goals else ["Развитие"],
            problems=problems if problems else ["Усталость"],
            created_at=datetime.now().isoformat()
        )
        
        return person
    
    def generate_family(self, size: int = 4, region: Optional[str] = None,
                        use_japanese_names: bool = False) -> Family:
        """Генерирует семью"""
        
        if region is None:
            if use_japanese_names:
                region = self.generate_japanese_location()
            else:
                region = random.choice(self.parser.get_parameter_options("регион") or ["Москва"])
        
        # Родители
        father = self.generate_person(age_range=(30, 50), gender="мужской", use_japanese_names=use_japanese_names)
        mother = self.generate_person(age_range=(28, 48), gender="женский", use_japanese_names=use_japanese_names)
        
        # Дети
        children = []
        for i in range(size - 2):
            child_age = random.randint(0, 25)
            child = self.generate_person(age_range=(child_age, child_age))
            children.append(child.to_dict())
        
        # Название семьи (извлекаем фамилию из имени отца)
        father_last_name = father.name.split()[-1] if father.name.split() else "Ивановых"
        family_name = f"Семья {father_last_name}ых"
        
        # Традиции
        traditions = random.sample(self.parser.get_parameter_options("традиции") or ["Совместный ужин"], k=min(3, len(self.parser.get_parameter_options("традиции") or [])))
        
        # Проблемы
        problems = random.sample(self.parser.get_parameter_options("семейные_проблемы") or ["Баланс работа-семья"], k=min(2, len(self.parser.get_parameter_options("семейные_проблемы") or [])))
        
        # ID
        family_id = hashlib.md5(f"{family_name}:{datetime.now().isoformat()}".encode()).hexdigest()[:12]
        
        family = Family(
            id=family_id,
            name=family_name,
            members=[father.to_dict(), mother.to_dict()] + children,
            relationships={
                f"{father.name}-{mother.name}": {"type": "супруги", "strength": random.uniform(0.6, 1.0)},
            },
            traditions=traditions if traditions else ["Совместный ужин"],
            problems=problems if problems else ["Баланс работа-семья"],
            budget=random.choice(["низкий", "средний", "высокий"]),
            housing=random.choice(["квартира", "дом", "общежитие"]),
            region=region,
            created_at=datetime.now().isoformat()
        )
        
        return family
    
    def generate_organization(self, type: Optional[str] = None, 
                              size: Optional[str] = None) -> Organization:
        """Генерирует организацию"""
        
        org_types = ["company", "government", "ngo", "club", "criminal"]
        org_type = type if type else random.choice(org_types)
        
        org_sizes = ["small", "medium", "large", "corporation"]
        org_size = size if size else random.choice(org_sizes)
        
        # Названия по типам
        name_templates = {
            "company": ["ООО \"{name}\"", "АО \"{name}\"", "Корпорация \"{name}\""],
            "government": ["Министерство {name}", "Департамент {name}", "Агентство \"{name}\""],
            "ngo": ["Фонд \"{name}\"", "Организация \"{name}\"", "Движение \"{name}\""],
            "club": ["Клуб \"{name}\"", "Сообщество \"{name}\"", "Группа \"{name}\""],
            "criminal": ["Группировка \"{name}\"", "Синдикат \"{name}\"", "Банда \"{name}\""],
        }
        
        name_bases = ["Техно", "Инновация", "Развитие", "Прогресс", "Вектор", "Горизонт", "Альфа", "Омега"]
        name = random.choice(name_templates.get(org_type, ["\"{name}\""])).format(
            name=random.choice(name_bases) + random.choice(["Тех", "Групп", "Строй", "Финанс"])
        )
        
        # Индустрия
        industries = ["IT", "Финансы", "Производство", "Торговля", "Образование", "Медицина", "Строительство"]
        industry = random.choice(industries)
        
        # Культура
        cultures = ["Корпоративная", "Семейная", "Агрессивная", "Инновационная", "Традиционная"]
        culture = random.choice(cultures)
        
        # Цели
        goals = random.sample(self.parser.get_parameter_options("цели_организаций") or ["Рост прибыли", "Развитие"], k=min(3, len(self.parser.get_parameter_options("цели_организаций") or [])))
        
        # Ресурсы
        resources = {
            "money": random.uniform(10000, 10000000),
            "reputation": random.uniform(0.3, 1.0),
            "influence": random.uniform(0.2, 1.0),
        }
        
        # ID
        org_id = hashlib.md5(f"{name}:{datetime.now().isoformat()}".encode()).hexdigest()[:12]
        
        organization = Organization(
            id=org_id,
            name=name,
            type=org_type,
            size=org_size,
            industry=industry,
            culture=culture,
            goals=goals if goals else ["Рост"],
            resources=resources,
            reputation=resources["reputation"],
            created_at=datetime.now().isoformat()
        )
        
        return organization
    
    def generate_country(self, population_range: Tuple[int, int] = (1000000, 100000000)) -> Country:
        """Генерирует страну"""
        
        # Названия
        name_prefixes = ["Рос", "Бел", "Укр", "Каза", "Узб", "Груз", "Арм", "Азер", "Молд", "Лит", "Латв", "Эст"]
        name_suffixes = ["ия", "ия", "стан", "ланд", "гия", "ния", "вия"]
        name = random.choice(name_prefixes) + random.choice(name_suffixes)
        
        # Население
        population = random.randint(*population_range)
        
        # ВВП на душу
        gdp_per_capita = random.uniform(5000, 50000)
        
        # Тип правительства
        gov_types = ["Демократия", "Республика", "Монархия", "Авторитарный режим", "Федерация"]
        government_type = random.choice(gov_types)
        
        # Культура
        cultures = ["Западная", "Восточная", "Смешанная", "Традиционная", "Современная"]
        culture = random.choice(cultures)
        
        # Регионы и города
        regions = [f"{name}ская область {i}" for i in range(1, random.randint(3, 10))]
        cities = [f"Город {random.choice(name_prefixes)}{i}" for i in range(1, random.randint(5, 20))]
        
        # Законы
        laws = random.sample(self.parser.get_parameter_options("законы") or ["Конституция", "Налоговый кодекс"], k=min(5, len(self.parser.get_parameter_options("законы") or [])))
        
        # Традиции
        traditions = random.sample(self.parser.get_parameter_options("традиции_стран") or ["Новый год", "День Победы"], k=min(5, len(self.parser.get_parameter_options("традиции_стран") or [])))
        
        # ID
        country_id = hashlib.md5(f"{name}:{datetime.now().isoformat()}".encode()).hexdigest()[:12]
        
        country = Country(
            id=country_id,
            name=name,
            population=population,
            gdp_per_capita=gdp_per_capita,
            government_type=government_type,
            culture=culture,
            regions=regions,
            cities=cities,
            laws=laws if laws else ["Конституция"],
            traditions=traditions if traditions else ["Праздники"],
            created_at=datetime.now().isoformat()
        )
        
        return country
    
    def generate_world_population(self, num_people: int = 100, 
                                   num_families: int = 20,
                                   num_organizations: int = 10,
                                   num_countries: int = 5,
                                   use_japanese_names: bool = False) -> Dict:
        """Генерирует полную популяцию мира"""
        
        print(f"🌍 Генерация популяции мира...")
        print(f"   Люди: {num_people}")
        print(f"   Семьи: {num_families}")
        print(f"   Организации: {num_organizations}")
        print(f"   Страны: {num_countries}")
        print(f"   Японские имена: {'✅' if use_japanese_names else '❌'}")
        
        # Генерация
        people = [self.generate_person(use_japanese_names=use_japanese_names) for _ in range(num_people)]
        families = [self.generate_family(use_japanese_names=use_japanese_names) for _ in range(num_families)]
        organizations = [self.generate_organization() for _ in range(num_organizations)]
        countries = [self.generate_country() for _ in range(num_countries)]
        
        # Связи
        world_data = {
            "generated_at": datetime.now().isoformat(),
            "people": [p.to_dict() for p in people],
            "families": [f.to_dict() for f in families],
            "organizations": [o.to_dict() for o in organizations],
            "countries": [c.to_dict() for c in countries],
            "stats": {
                "total_people": len(people),
                "total_families": len(families),
                "total_organizations": len(organizations),
                "total_countries": len(countries),
                "gender_distribution": {
                    "male": sum(1 for p in people if p.gender == "мужской"),
                    "female": sum(1 for p in people if p.gender == "женский"),
                },
                "age_distribution": {
                    "18-25": sum(1 for p in people if 18 <= p.age <= 25),
                    "26-35": sum(1 for p in people if 26 <= p.age <= 35),
                    "36-50": sum(1 for p in people if 36 <= p.age <= 50),
                    "50+": sum(1 for p in people if p.age > 50),
                },
            }
        }
        
        # Сохранение
        output_file = self.output_dir / f"world_population_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(world_data, f, ensure_ascii=False, indent=2)
        
        print(f"✅ Популяция сохранена в {output_file}")
        
        return world_data


# ========================
# ИНТЕГРАЦИЯ С WORLD ENGINE
# ========================

class WorldEngineIntegration:
    """Интеграция генератора с WorldEngine"""
    
    def __init__(self, world_engine_path: str = "Wuglarst/src/world_engine.py"):
        self.world_engine_path = Path(world_engine_path)
        self.people_generator = PeopleGenerator()
        
    def add_people_to_world(self, world_name: str, num_people: int = 10) -> bool:
        """Добавляет сгенерированных людей в существующий мир"""
        
        if not self.world_engine_path.exists():
            print(f"❌ WorldEngine не найден: {self.world_engine_path}")
            return False
        
        # Загружаем мир
        worlds_dir = Path("data/worlds")
        world_file = worlds_dir / f"{world_name}.json"
        
        if not world_file.exists():
            print(f"❌ Мир не найден: {world_name}")
            return False
        
        with open(world_file, 'r', encoding='utf-8') as f:
            world = json.load(f)
        
        # Генерируем людей
        print(f"👥 Генерация {num_people} персонажей для мира {world_name}...")
        
        for i in range(num_people):
            person = self.people_generator.generate_person()
            
            # Конвертируем в формат NPC WorldEngine
            npc = {
                "name": person.name,
                "age": person.age,
                "race": "человек",
                "role": person.job,
                "personality": person.temperament,
                "skills": person.habits,
                "secrets": person.problems,
                "goals": person.goals,
                "relations": {},
                "memories": [],
                "location": person.region,
                "alive": True,
                "created_at": person.created_at,
                "last_seen": person.created_at,
                "influence": random.uniform(0.1, 0.9),
                "mood": random.choice(["neutral", "happy", "anxious", "angry"]),
                # Дополнительные поля из знаний
                "archetype": person.archetype,
                "education": person.education,
                "finance": person.finance,
                "housing": person.housing,
                "relationships": person.relationships,
                "children": person.children,
                "temperament": person.temperament,
                "sociality": person.sociality,
                "values": person.values,
            }
            
            if "npcs" not in world:
                world["npcs"] = []
            
            world["npcs"].append(npc)
        
        # Сохраняем мир
        with open(world_file, 'w', encoding='utf-8') as f:
            json.dump(world, f, ensure_ascii=False, indent=2)
        
        print(f"✅ Добавлено {num_people} персонажей в мир {world_name}")
        return True


# ========================
# CLI
# ========================

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Генератор людей, семей, организаций и стран")
    parser.add_argument("--people", type=int, default=50, help="Количество людей")
    parser.add_argument("--families", type=int, default=10, help="Количество семей")
    parser.add_argument("--organizations", type=int, default=5, help="Количество организаций")
    parser.add_argument("--countries", type=int, default=3, help="Количество стран")
    parser.add_argument("--knowledge-dir", type=str, default=DEFAULT_KNOWLEDGE_DIR, help="Директория с знаниями")
    parser.add_argument("--add-to-world", type=str, help="Добавить в существующий мир")
    parser.add_argument("--japanese-names", action="store_true", help="Использовать японские имена")
    
    args = parser.parse_args()
    
    # Инициализация
    generator = PeopleGenerator(knowledge_dir=args.knowledge_dir)
    
    if args.add_to_world:
        # Интеграция с WorldEngine
        integration = WorldEngineIntegration()
        integration.add_people_to_world(args.add_to_world, num_people=args.people)
    else:
        # Генерация полной популяции
        world_data = generator.generate_world_population(
            num_people=args.people,
            num_families=args.families,
            num_organizations=args.organizations,
            num_countries=args.countries,
            use_japanese_names=args.japanese_names
        )
        
        # Печать статистики
        print("\n" + "="*50)
        print("📊 СТАТИСТИКА МИРА")
        print("="*50)
        print(f"Всего людей: {world_data['stats']['total_people']}")
        print(f"Всего семей: {world_data['stats']['total_families']}")
        print(f"Всего организаций: {world_data['stats']['total_organizations']}")
        print(f"Всего стран: {world_data['stats']['total_countries']}")
        print(f"\nГендерное распределение:")
        print(f"  Мужчины: {world_data['stats']['gender_distribution']['male']}")
        print(f"  Женщины: {world_data['stats']['gender_distribution']['female']}")
        print(f"\nВозрастное распределение:")
        for age_range, count in world_data['stats']['age_distribution'].items():
            print(f"  {age_range}: {count}")
        print("="*50)
