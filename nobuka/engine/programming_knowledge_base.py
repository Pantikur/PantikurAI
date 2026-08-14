#!/usr/bin/env python3
"""
База знаний Нобуки по программированию.

Содержит:
- Паттерны проектирования (Python)
- Антипаттерны и как их исправить
- Best practices для Python
- Паттерны рефакторинга
- Шаблоны кода для типичных задач
- Стратегии тестирования
- Паттерны оптимизации производительности
- Архитектурные паттерны
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field, asdict
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional


@dataclass
class CodePattern:
    """Шаблон кода с примером и описанием."""
    name: str
    category: str
    description: str
    when_to_use: str
    code_before: str = ''
    code_after: str = ''
    tags: List[str] = field(default_factory=list)
    complexity: str = 'low'
    confidence: float = 0.9

    def to_dict(self) -> dict:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict) -> 'CodePattern':
        return cls(**data)


@dataclass
class AntiPattern:
    """Антипаттерн с описанием проблемы и решения."""
    name: str
    description: str
    symptoms: List[str]
    impact: str
    fix: str
    code_example: str = ''
    severity: str = 'medium'
    related_patterns: List[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict) -> 'AntiPattern':
        return cls(**data)


@dataclass
class BestPractice:
    """Лучшая практика."""
    title: str
    description: str
    category: str
    code_example: str = ''
    source: str = ''
    python_version: str = '3.8+'

    def to_dict(self) -> dict:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict) -> 'BestPractice':
        return cls(**data)


def get_design_patterns() -> List[CodePattern]:
    """Паттерны проектирования для Python."""
    return [
        CodePattern(
            name='Strategy Pattern',
            category='design',
            description='Позволяет определять семейство алгоритмов, инкапсулировать каждый из них и делать их взаимозаменяемыми.',
            when_to_use='Когда у вас есть несколько вариантов одного действия, и выбор зависит от контекста',
            code_before="def process(data, strategy):\n    if strategy == 'sort':\n        return sorted(data)\n    elif strategy == 'reverse':\n        return list(reversed(data))",
            code_after="from abc import ABC, abstractmethod\n\nclass ProcessingStrategy(ABC):\n    @abstractmethod\n    def execute(self, data):\n        pass\n\nclass SortStrategy(ProcessingStrategy):\n    def execute(self, data):\n        return sorted(data)\n\ndef process(data, strategy):\n    return strategy.execute(data)",
            tags=['strategy', 'design', 'oop'],
            complexity='medium'
        ),
        CodePattern(
            name='Observer Pattern',
            category='design',
            description='Механизм подписки, позволяющий одному объекту уведомлять список объектов о событиях.',
            when_to_use='Когда изменение состояния одного объекта должно автоматически уведомлять другие',
            code_before="class Order:\n    def __init__(self):\n        self._status = 'pending'\n    @status.setter\n    def status(self, value):\n        self._status = value\n        email_service.send(self.user, f'Order: {value}')\n        inventory.update(self.items)",
            code_after="class Observable:\n    def __init__(self):\n        self._observers = []\n    def subscribe(self, observer):\n        self._observers.append(observer)\n    def notify(self, event):\n        for observer in self._observers:\n            observer(event)\n\nclass Order(Observable):\n    @status.setter\n    def status(self, value):\n        old = self._status\n        self._status = value\n        self.notify({'old': old, 'new': value})",
            tags=['observer', 'event', 'publish-subscribe'],
            complexity='medium'
        ),
        CodePattern(
            name='Factory Method',
            category='design',
            description='Определяет интерфейс для создания объектов, но позволяет подклассам изменять тип создаваемых объектов.',
            when_to_use='Когда вы не знаете заранее, какие именно объекты нужно создавать',
            code_before="def create_bot(name):\n    if name == 'nobuka':\n        return NobukaBot(config)\n    elif name == 'shiori':\n        return ShioriBot(config)",
            code_after="class BotRegistry:\n    _factories = {}\n    @classmethod\n    def register(cls, name, bot_class):\n        cls._factories[name] = bot_class\n    @classmethod\n    def create(cls, name, config):\n        return cls._factories[name](config)\n\nBotRegistry.register('nobuka', NobukaBot)\nbot = BotRegistry.create('nobuka', {'mode': 'improve'})",
            tags=['factory', 'creation', 'registry'],
            complexity='medium'
        ),
        CodePattern(
            name='Dependency Injection',
            category='design',
            description='Внедрение зависимости - объект получает зависимости извне, а не создаёт их сам.',
            when_to_use='Для тестируемости, гибкости и разделения ответственности',
            code_before="class ChatBot:\n    def __init__(self):\n        self.model = QwenModel()\n        self.db = MySQLDatabase()\n        self.cache = RedisCache()",
            code_after="from typing import Protocol\n\nclass ModelProtocol(Protocol):\n    def generate(self, prompt: str) -> str: ...\n\nclass ChatBot:\n    def __init__(self, model: ModelProtocol, db, cache=None):\n        self.model = model\n        self.db = db\n        self.cache = cache",
            tags=['di', 'injection', 'testing', 'protocol'],
            complexity='medium'
        ),
        CodePattern(
            name='Builder Pattern with dataclasses',
            category='design',
            description='Конфигурация с фабричными методами для разных ролей.',
            when_to_use='Когда объект нужно создать из многих частей, и конфигурация сложная',
            code_before="class BotConfig:\n    def __init__(self, model, temperature, max_tokens, top_p, top_k,\n                 stop_sequences, presence_penalty, frequency_penalty):\n        # 10 параметров!",
            code_after="from dataclasses import dataclass, field\nfrom typing import List, Optional\n\n@dataclass\nclass BotConfig:\n    model: str = 'qwen2.5-3b'\n    temperature: float = 0.7\n    max_tokens: int = 1024\n    stop_sequences: List[str] = field(default_factory=list)\n    \n    @classmethod\n    def for_improvement(cls):\n        return cls(temperature=0.3, max_tokens=2048,\n                   system_prompt='Ты - Нобука, эксперт по коду.')",
            tags=['builder', 'factory', 'dataclass'],
            complexity='low'
        ),
    ]


def get_refactoring_patterns() -> List[CodePattern]:
    """Паттерны рефакторинга."""
    return [
        CodePattern(
            name='Extract Function',
            category='refactoring',
            description='Выделение фрагмента кода в отдельную функцию с понятным именем.',
            when_to_use='Когда функция делает слишком много',
            code_before="def handle_request(request):\n    token = request.headers.get('Authorization')\n    if not token:\n        return {'error': 'No token'}\n    user = db.query('SELECT * FROM users WHERE token=?', token)\n    if not user:\n        return {'error': 'Invalid token'}\n    # ... ещё 30 строк",
            code_after="def authenticate(request):\n    token = request.get('headers', {}).get('Authorization')\n    if not token:\n        return {'error': 'No token'}\n    return db.query('SELECT * FROM users WHERE token=?', token)\n\ndef handle_request(request):\n    user = authenticate(request)\n    if not user or 'error' in user:\n        return {'error': 'Invalid token'}\n    # ... остальная логика",
            tags=['extract', 'function', 'readability'],
            complexity='low'
        ),
        CodePattern(
            name='Guard Clauses',
            category='refactoring',
            description='Замена глубокой вложенности на ранние возвраты (early return).',
            when_to_use='Когда код имеет 4+ уровней вложенности',
            code_before="def process_user(user):\n    if user:\n        if user.is_active:\n            if user.has_permission:\n                if user.role == 'admin':\n                    grant_access(user)\n                else:\n                    deny_access(user)",
            code_after="def process_user(user):\n    if not user:\n        return deny_access(user)\n    if not user.is_active:\n        return deny_access(user)\n    if not user.has_permission:\n        return deny_access(user)\n    if user.role != 'admin':\n        return deny_access(user)\n    grant_access(user)",
            tags=['guard-clauses', 'early-return', 'readability'],
            complexity='low'
        ),
        CodePattern(
            name='Replace Conditional with Polymorphism',
            category='refactoring',
            description='Замена if/elif на полиморфизм - каждый случай становится своим подклассом.',
            when_to_use='Когда есть if/elif для разных типов',
            code_before="def get_discount(price, user_type):\n    if user_type == 'premium':\n        return price * 0.7\n    elif user_type == 'regular':\n        return price * 0.9",
            code_after="class DiscountStrategy(ABC):\n    @abstractmethod\n    def apply(self, price):\n        pass\n\nclass PremiumDiscount(DiscountStrategy):\n    def apply(self, price):\n        return price * 0.7\n\ndef get_discount(price, strategy):\n    return strategy.apply(price)",
            tags=['polymorphism', 'conditional', 'oop'],
            complexity='medium'
        ),
    ]


def get_anti_patterns() -> List[AntiPattern]:
    """Антипаттерны и как их исправить."""
    return [
        AntiPattern(
            name='God Class',
            description='Класс, который знает слишком много, делает слишком много.',
            symptoms=[
                'Файл класса > 500 строк',
                '50+ методов в одном классе',
                'Класс используется почти везде',
                'Сложно тестировать'
            ],
            impact='Сложность поддержки, дублирование кода, хрупкость',
            fix='Разделите класс на несколько по ответственности (SRP).',
            code_example="# До: class ProjectManager с 40+ методов\n# После: UserManagement, PaymentProcessing, ReportGeneration",
            severity='critical',
            related_patterns=['Strategy Pattern', 'SRP']
        ),
        AntiPattern(
            name='Feature Envy',
            description='Метод интересуется данными другого класса больше своего.',
            symptoms=[
                'Метод вызывает get_x(), get_y() у другого объекта',
                'Логика использует данные другого класса'
            ],
            impact='Связанность, дублирование логики',
            fix='Переместите метод в класс, данные которого он использует.',
            code_example="# До: Address.get_shipping_cost() интересуется Order\n# После: Order.calculate_shipping(address)",
            severity='medium',
            related_patterns=['Move Method']
        ),
        AntiPattern(
            name='Arrow Code / Deep Nesting',
            description='Слишком глубокая вложенность кода (более 3-4 уровней).',
            symptoms=[
                'Код сдвинут вправо на 4+ уровня',
                'Много вложенных if/else',
                'Трудно читать поток выполнения'
            ],
            impact='Сложность понимания, трудно добавлять условия',
            fix='Guard clauses (ранний return), выделение функций.',
            code_example="# До: 5 уровней вложенности\n# После: guard clauses - читается сверху вниз",
            severity='high',
            related_patterns=['Guard Clauses', 'Early Return']
        ),
        AntiPattern(
            name='Data Class',
            description='Класс только хранит данные с getter/setter.',
            symptoms=[
                'Все поля публичные или через getter/setter',
                'Нет бизнес-логики в классе'
            ],
            impact='Нарушение инкапсуляции, нет валидации',
            fix='Используйте dataclasses с @property для валидации.',
            code_example="# До: class User с get_name(), get_email()\n# После: @dataclass с @property email",
            severity='medium',
            related_patterns=['Encapsulation', 'DataClass']
        ),
    ]


def get_best_practices() -> List[BestPractice]:
    """Лучшие практики Python."""
    return [
        BestPractice(
            title='Используйте type hints везде',
            description='Аннотации типов делают код самодокументируемым.',
            category='code-quality',
            code_example='def calculate_total(items: list) -> float:\n    return sum(i["price"] * i["quantity"] for i in items)',
            source='PEP 484'
        ),
        BestPractice(
            title='Используйте context managers для ресурсов',
            description='Контекстные менеджеры гарантируют освобождение ресурсов.',
            category='resource-management',
            code_example='with open("data.json", "r") as f:\n    data = json.load(f)',
            source='PEP 343'
        ),
        BestPractice(
            title='Используйте logging вместо print',
            description='Logging позволяет контролировать уровень детализации.',
            category='debugging',
            code_example='import logging\nlogger = logging.getLogger(__name__)\nlogger.info("Process completed")',
            source='Python Docs'
        ),
        BestPractice(
            title='Избегайте мутабельных аргументов по умолчанию',
            description='Значения по умолчанию вычисляются один раз при определении функции.',
            category='bugs-prevention',
            code_example='def append_item(item, my_list=None):\n    if my_list is None:\n        my_list = []\n    my_list.append(item)\n    return my_list',
            source='Python Docs'
        ),
        BestPractice(
            title='Используйте dataclasses для контейнеров данных',
            description='dataclasses автоматически генерируют __init__, __repr__, __eq__.',
            category='code-quality',
            code_example='@dataclass\nclass Bot:\n    name: str\n    config: dict\n    skills: list = field(default_factory=list)',
            source='PEP 557'
        ),
        BestPractice(
            title='Используйте Enum для констант',
            description='Enum делает код читаемым и предотвращает ошибки.',
            category='code-quality',
            code_example='from enum import Enum, auto\n\nclass BotRole(Enum):\n    IMPROVER = auto()\n    PROTECTOR = auto()',
            source='PEP 435'
        ),
        BestPractice(
            title='Принцип единственной ответственности (SRP)',
            description='Класс должен иметь только одну причину для изменения.',
            category='architecture',
            code_example='class CodeAnalyzer:      # только анализ\nclass TestRunner:        # только тесты\nclass ReportGenerator:   # только отчёты',
            source='Clean Architecture'
        ),
        BestPractice(
            title='Используйте pathlib вместо os.path',
            description='pathlib - объектно-ориентированный путь к файлам.',
            category='code-quality',
            code_example='from pathlib import Path\nconfig = Path("config") / "settings.json"\nif config.exists():\n    content = config.read_text()',
            source='PEP 428'
        ),
        BestPractice(
            title='Используйте f-strings для форматирования',
            description='f-strings быстрее и читабельнее format() и %.',
            category='code-quality',
            code_example='message = f"Bot {name}: level {level}"',
            source='PEP 498'
        ),
        BestPractice(
            title='Используйте comprehensions',
            description='List/dict comprehensions короче и быстрее циклов.',
            category='performance',
            code_example='squares = [x ** 2 for x in range(10) if x % 2 == 0]',
            source='Python Docs'
        ),
    ]


def get_testing_patterns() -> List[CodePattern]:
    """Паттерны тестирования."""
    return [
        CodePattern(
            name='Arrange-Act-Assert',
            category='testing',
            description='Структура теста: подготовка, действие, проверка.',
            when_to_use='Для каждого unit-теста',
            code_after="def test_calculate():\n    # Arrange\n    items = [{'price': 100, 'quantity': 2}]\n    # Act\n    total = calculate_total(items)\n    # Assert\n    assert total == 200",
            tags=['tdd', 'unit-test', 'pattern'],
            complexity='low'
        ),
        CodePattern(
            name='Mock External Dependencies',
            category='testing',
            description='Изоляция теста от внешних зависимостей через моки.',
            when_to_use='Когда тест не должен вызывать реальные API',
            code_after="from unittest.mock import Mock, patch\n\n@patch('my_module.requests.get')\ndef test_api_call(mock_get):\n    mock_get.return_value.json.return_value = {'key': 'value'}\n    result = fetch_data('http://api.example.com')\n    assert result == {'key': 'value'}",
            tags=['mock', 'unittest', 'isolation'],
            complexity='medium'
        ),
        CodePattern(
            name='Parametrized Tests',
            category='testing',
            description='Запуск одного теста с разными входными данными.',
            when_to_use='Когда нужно проверить функцию с множеством входов',
            code_after="import pytest\n\n@pytest.mark.parametrize('a, b, op, expected', [\n    (10, 5, '+', 15),\n    (10, 5, '-', 5),\n    (10, 5, '*', 50),\n])\ndef test_calculate(a, b, op, expected):\n    assert calculate(a, b, op) == expected",
            tags=['parametrize', 'pytest', 'data-driven'],
            complexity='low'
        ),
    ]


def get_performance_patterns() -> List[CodePattern]:
    """Паттерны оптимизации производительности."""
    return [
        CodePattern(
            name='Memoization with lru_cache',
            category='performance',
            description='Кэширование результатов дорогих вызовов функций.',
            when_to_use='Когда функция вызывается с одними и теми же аргументами',
            code_after="from functools import lru_cache\n\n@lru_cache(maxsize=128)\ndef fibonacci(n):\n    if n <= 1:\n        return n\n    return fibonacci(n-1) + fibonacci(n-2)",
            tags=['lru-cache', 'memoization', 'caching'],
            complexity='low'
        ),
        CodePattern(
            name='Generator for Large Data',
            category='performance',
            description='Генераторы экономят память.',
            when_to_use='Когда данные слишком велики для памяти',
            code_after="def read_large_file(path):\n    with open(path) as f:\n        for line in f:\n            yield line.strip()\n\n# Использование\nfor line in read_large_file('huge.txt'):\n    process(line)",
            tags=['generator', 'memory', 'yield'],
            complexity='low'
        ),
        CodePattern(
            name='Profiling Before Optimization',
            category='performance',
            description='Измеряйте производительность перед оптимизацией.',
            when_to_use='Перед любой оптимизацией',
            code_after="import cProfile\n\nprofiler = cProfile.Profile()\nprofiler.enable()\nmy_slow_function()\nprofiler.disable()\nprofiler.print_stats(20)",
            tags=['profiling', 'cprofile', 'benchmarking'],
            complexity='low'
        ),
    ]


class ProgrammingKnowledgeBase:
    """Управление базой знаний по программированию."""

    def __init__(self, storage_path='nobuka/engine/programming_knowledge.json'):
        self.storage_path = Path(storage_path)
        self.storage_path.parent.mkdir(parents=True, exist_ok=True)
        self.patterns = []
        self.antipatterns = []
        self.best_practices = []
        self._load()

    def _load(self):
        """Загрузить базу знаний из файла."""
        if self.storage_path.exists():
            try:
                with open(self.storage_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.patterns = [CodePattern.from_dict(p) for p in data.get('patterns', [])]
                    self.antipatterns = [AntiPattern.from_dict(p) for p in data.get('antipatterns', [])]
                    self.best_practices = [BestPractice.from_dict(p) for p in data.get('best_practices', [])]
                print(f"Loaded: {len(self.patterns)} patterns, {len(self.antipatterns)} antipatterns, {len(self.best_practices)} practices")
            except Exception as e:
                print(f"Error loading: {e}")
                self._save_initial()
        else:
            self._save_initial()

    def _save_initial(self):
        """Сохранить исходную базу знаний."""
        self.patterns = (
            get_design_patterns() +
            get_refactoring_patterns() +
            get_testing_patterns() +
            get_performance_patterns()
        )
        self.antipatterns = get_anti_patterns()
        self.best_practices = get_best_practices()
        self._save_to_file()
        print(f"Created knowledge base: {len(self.patterns)} patterns, {len(self.antipatterns)} antipatterns, {len(self.best_practices)} practices")

    def _save_to_file(self):
        """Сохранить базу знаний в файл."""
        data = {
            'patterns': [p.to_dict() for p in self.patterns],
            'antipatterns': [p.to_dict() for p in self.antipatterns],
            'best_practices': [p.to_dict() for p in self.best_practices],
            'updated': datetime.now().isoformat()
        }
        with open(self.storage_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    def add_pattern(self, pattern):
        """Добавить новый паттерн."""
        self.patterns.append(pattern)
        self._save_to_file()
        print(f"Added pattern: {pattern.name}")

    def add_antipattern(self, antipattern):
        """Добавить новый антипаттерн."""
        self.antipatterns.append(antipattern)
        self._save_to_file()
        print(f"Added antipattern: {antipattern.name}")

    def add_best_practice(self, practice):
        """Добавить новую лучшую практику."""
        self.best_practices.append(practice)
        self._save_to_file()
        print(f"Added practice: {practice.title}")

    def search_patterns(self, query, category=None):
        """Поиск паттернов по запросу."""
        query_lower = query.lower()
        results = []
        for pattern in self.patterns:
            if category and pattern.category != category:
                continue
            text = f"{pattern.name} {pattern.description} {' '.join(pattern.tags)}".lower()
            if query_lower in text:
                results.append(pattern)
        return results

    def search_antipatterns(self, symptoms):
        """Поиск антипаттернов по симптомам."""
        symptoms_lower = symptoms.lower()
        results = []
        for ap in self.antipatterns:
            text = f"{ap.name} {ap.description} {' '.join(ap.symptoms)}".lower()
            if symptoms_lower in text:
                results.append(ap)
        return results

    def get_recommendations(self, code_sample):
        """Дать рекомендации на основе кода."""
        recommendations = []
        code_lower = code_sample.lower()
        for ap in self.antipatterns:
            if len(ap.symptoms) > 0:
                for symptom in ap.symptoms[:2]:
                    if symptom.lower() in code_lower or len(code_sample) > 500:
                        recommendations.append(f"Possible antipattern '{ap.name}': {ap.fix}")
                        break
        return recommendations

    def stats(self):
        """Статистика базы знаний."""
        categories = {}
        for p in self.patterns:
            categories[p.category] = categories.get(p.category, 0) + 1
        return {
            'total_patterns': len(self.patterns),
            'total_antipatterns': len(self.antipatterns),
            'total_best_practices': len(self.best_practices),
            'by_category': categories,
            'last_updated': datetime.now().isoformat()
        }


if __name__ == '__main__':
    kb = ProgrammingKnowledgeBase()
    print('\nStats:')
    stats = kb.stats()
    for key, value in stats.items():
        print(f'  {key}: {value}')
    print('\nSearch for "strategy":')
    results = kb.search_patterns('strategy')
    for r in results:
        print(f'  - {r.name} ({r.category})')
