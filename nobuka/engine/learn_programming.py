#!/usr/bin/env python3
"""
Модуль обучения Нобуки в программировании.

Извлекает знания из реальных источников:
- Python Documentation (docs.python.org)
- Real Python (realpython.com)
- Refactoring.Guru (refactoring.guru)
- StackOverflow (stackoverflow.com)
- PEP (Python Enhancement Proposals)

Сохраняет знания в базу знаний Нобуки.
"""

from __future__ import annotations

import json
import logging
import re
import time
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional
from urllib.parse import quote

import requests
from bs4 import BeautifulSoup

from nobuka.engine.programming_knowledge_base import (
    ProgrammingKnowledgeBase,
    CodePattern,
    AntiPattern,
    BestPractice,
)


logger = logging.getLogger("NobukaLearning")


class ProgrammingLearner:
    """
    Обучает Нобуку программированию из реальных источников.
    """
    
    # Источники знаний
    SOURCES = {
        'python_docs': {
            'base_url': 'https://docs.python.org/3',
            'topics': [
                '/tutorial/controlflow.html',
                '/library/functions.html',
                '/reference/expressions.html',
                '/library/collections.abc.html',
                '/library/functools.html',
                '/library/contextlib.html',
                '/reference/datamodel.html',
                '/reference/import.html',
            ],
            'description': 'Официальная документация Python'
        },
        'pep': {
            'base_url': 'https://peps.python.org',
            'topics': [
                '/pep-0008/',
                '/pep-0484/',
                '/pep-0557/',
                '/pep-0421/',
                '/pep-0572/',
            ],
            'description': 'Python Enhancement Proposals'
        },
        'refactoring_guru': {
            'base_url': 'https://refactoring.guru',
            'topics': [
                '/design-patterns',
                '/refactoring',
                '/antipatterns',
            ],
            'description': 'Паттерны проектирования и рефакторинг'
        }
    }
    
    def __init__(self, knowledge_base: Optional[ProgrammingKnowledgeBase] = None):
        self.kb = knowledge_base or ProgrammingKnowledgeBase()
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
                          'AppleWebKit/537.36 (KHTML, like Gecko) '
                          'Chrome/120.0.0.0 Safari/537.36'
        })
        self._learned_items = []
    
    def learn_from_source(self, source_name: str = 'all', topic: str = None) -> List[dict]:
        """
        Обучение из указанного источника.
        
        Args:
            source_name: Имя источника или 'all'
            topic: Тема для обучения (опционально)
            
        Returns:
            Список извлечённых знаний
        """
        if source_name == 'all':
            all_knowledge = []
            for name in self.SOURCES:
                knowledge = self._learn_from_single_source(name, topic)
                all_knowledge.extend(knowledge)
            return all_knowledge
        
        return self._learn_from_single_source(source_name, topic)
    
    def _learn_from_single_source(self, source_name: str, topic: str = None) -> List[dict]:
        """Обучение из одного источника."""
        if source_name not in self.SOURCES:
            logger.warning(f"Неизвестный источник: {source_name}")
            return []
        
        source = self.SOURCES[source_name]
        logger.info(f"📚 Обучение из {source['description']}...")
        
        knowledge = []
        
        if source_name == 'python_docs':
            knowledge = self._learn_python_docs(source, topic)
        elif source_name == 'pep':
            knowledge = self._learn_pep(source, topic)
        elif source_name == 'refactoring_guru':
            knowledge = self._learn_refactoring_guru(source, topic)
        
        logger.info(f"✅ Извлечено {len(knowledge)} записей из {source_name}")
        self._learned_items.extend(knowledge)
        
        return knowledge
    
    def _learn_python_docs(self, source: dict, topic: str = None) -> List[dict]:
        """Извлечение знаний из документации Python."""
        knowledge = []
        
        # Выбираем страницы для чтения
        urls = source['topics']
        if topic:
            # Фильтрация по теме
            filtered = [
                url for url in urls
                if topic.lower() in url.lower()
            ]
            if filtered:
                urls = filtered
        
        for rel_url in urls[:5]:  # Читаем не более 5 страниц
            url = source['base_url'] + rel_url
            page_data = self._fetch_and_parse(url)
            
            if page_data:
                knowledge.append({
                    'source': 'python_docs',
                    'url': url,
                    'title': page_data.get('title', ''),
                    'content_summary': page_data.get('content_summary', '')[:500],
                    'code_examples': page_data.get('code_examples', []),
                    'learned_at': datetime.now().isoformat()
                })
                
                # Сохраняем как лучшие практики
                if page_data.get('code_examples'):
                    for example in page_data['code_examples'][:2]:
                        practice = BestPractice(
                            title=f"Python Docs: {example.get('title', 'Пример')}",
                            description=example.get('description', ''),
                            category='python-builtin',
                            code_example=example.get('code', ''),
                            source=url
                        )
                        self.kb.add_best_practice(practice)
                
                time.sleep(1)  # Вежливость к серверу
        
        return knowledge
    
    def _learn_pep(self, source: dict, topic: str = None) -> List[dict]:
        """Извлечение знаний из PEP."""
        knowledge = []
        
        for rel_url in source['topics'][:3]:
            url = source['base_url'] + rel_url
            page_data = self._fetch_and_parse(url)
            
            if page_data:
                # Извлекаем ключевые правила из PEP
                key_rules = self._extract_key_rules(page_data.get('content', ''))
                
                knowledge.append({
                    'source': 'pep',
                    'url': url,
                    'title': page_data.get('title', ''),
                    'key_rules': key_rules,
                    'learned_at': datetime.now().isoformat()
                })
                
                # Сохраняем как best practices
                for rule in key_rules[:3]:
                    practice = BestPractice(
                        title=f"PEP: {rule['title']}",
                        description=rule['description'],
                        category='python-style',
                        source=url
                    )
                    self.kb.add_best_practice(practice)
                
                time.sleep(1)
        
        return knowledge
    
    def _learn_refactoring_guru(self, source: dict, topic: str = None) -> List[dict]:
        """Извлечение знаний из Refactoring.Guru."""
        knowledge = []
        
        for rel_url in source['topics'][:2]:
            url = source['base_url'] + rel_url
            page_data = self._fetch_and_parse(url)
            
            if page_data:
                patterns = self._extract_patterns_from_html(page_data.get('content', ''))
                
                for pattern in patterns[:3]:
                    code_pattern = CodePattern(
                        name=pattern['name'],
                        category='refactoring',
                        description=pattern.get('description', ''),
                        when_to_use=pattern.get('when', ''),
                        tags=pattern.get('tags', []),
                        confidence=0.85
                    )
                    self.kb.add_pattern(code_pattern)
                
                knowledge.append({
                    'source': 'refactoring_guru',
                    'url': url,
                    'patterns_found': len(patterns),
                    'learned_at': datetime.now().isoformat()
                })
                
                time.sleep(1)
        
        return knowledge
    
    def _fetch_and_parse(self, url: str) -> Optional[dict]:
        """Загрузка и парсинг веб-страницы."""
        try:
            response = self.session.get(url, timeout=15)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Извлекаем заголовок
            title = ''
            h1 = soup.find('h1')
            if h1:
                title = h1.get_text(strip=True)
            else:
                title = soup.title.get_text(strip=True) if soup.title else url
            
            # Извлекаем основной контент
            content = ''
            main = soup.find('main') or soup.find('article') or soup.find('div', class_='body')
            if main:
                content = main.get_text(separator='\n', strip=True)
            
            # Извлекаем примеры кода
            code_examples = self._extract_code_examples(soup)
            
            # Создаём краткое содержание
            content_summary = content[:1000] if content else ''
            
            return {
                'title': title,
                'content': content[:5000],
                'content_summary': content_summary,
                'code_examples': code_examples
            }
            
        except requests.RequestException as e:
            logger.warning(f"⚠️ Ошибка загрузки {url}: {e}")
            return None
        except Exception as e:
            logger.warning(f"⚠️ Ошибка парсинга {url}: {e}")
            return None
    
    def _extract_code_examples(self, soup: BeautifulSoup) -> List[dict]:
        """Извлечение примеров кода из HTML."""
        examples = []
        
        # Ищем блоки кода
        code_blocks = soup.find_all(['pre', 'div'])
        
        for block in code_blocks[:5]:  # Максимум 5 примеров
            code = block.get_text(strip=True)
            
            # Фильтруем: код должен быть достаточно длинным и содержать Python-подобный синтаксис
            if len(code) > 50 and (
                'def ' in code or 'class ' in code or 'import ' in code or
                'if ' in code or 'for ' in code or 'with ' in code
            ):
                # Очищаем от HTML-тегов
                code = re.sub(r'<[^>]+>', '', str(block))
                code = code.strip()
                
                if len(code) > 30:
                    examples.append({
                        'title': f'Пример кода {len(examples) + 1}',
                        'description': f'Пример использования Python',
                        'code': code[:1000]  # Ограничиваем длину
                    })
        
        return examples
    
    def _extract_key_rules(self, content: str) -> List[dict]:
        """Извлечение ключевых правил из текста PEP."""
        rules = []
        
        # Ищем нумерованные списки и заголовки
        lines = content.split('\n')
        current_rule = None
        
        for line in lines:
            line = line.strip()
            
            # Проверяем на заголовок правила
            match = re.match(r'^(\d+)\.\s+(.+?)$', line)
            if match:
                if current_rule:
                    rules.append(current_rule)
                current_rule = {
                    'title': match.group(2),
                    'number': int(match.group(1))
                }
            elif current_rule and line and not line.startswith('#'):
                if 'description' not in current_rule:
                    current_rule['description'] = line[:200]
        
        if current_rule:
            rules.append(current_rule)
        
        return rules[:10]
    
    def _extract_patterns_from_html(self, content: str) -> List[dict]:
        """Извлечение паттернов из контента."""
        patterns = []
        
        # Ищем названия паттернов
        pattern_names = [
            'Strategy', 'Observer', 'Factory', 'Singleton',
            'Decorator', 'Adapter', 'Facade', 'Proxy',
            'Builder', 'Prototype', 'Command', 'State',
            'Template Method', 'Chain of Responsibility',
        ]
        
        for name in pattern_names:
            if name.lower() in content.lower():
                patterns.append({
                    'name': name,
                    'description': f'Паттерн {name} обнаружен в материале',
                    'tags': [name.lower(), 'design', 'pattern'],
                    'when': 'Используйте, когда нужен {name}'.format(name=name)
                })
        
        return patterns
    
    def learn_from_custom_topic(self, topic: str, sources: List[str] = None) -> List[dict]:
        """
        Обучение по конкретной теме.
        
        Args:
            topic: Тема (например, "asyncio", "decorators", "generators")
            sources: Список источников для поиска
        """
        if sources is None:
            sources = ['python_docs']
        
        knowledge = []
        
        for source_name in sources:
            if source_name == 'python_docs':
                # Поиск по документации Python
                for url in self.SOURCES['python_docs']['topics']:
                    if topic.lower() in url.lower():
                        page_data = self._fetch_and_parse(
                            self.SOURCES['python_docs']['base_url'] + url
                        )
                        if page_data:
                            knowledge.append({
                                'source': f'python_docs:{url}',
                                'title': page_data.get('title', ''),
                                'topics': [topic]
                            })
                            
                            # Сохраняем как паттерн
                            pattern = CodePattern(
                                name=f"{topic.title()} — {page_data.get('title', '')}",
                                category='python-builtin',
                                description=page_data.get('content_summary', '')[:300],
                                when_to_use=f"При работе с {topic}",
                                code_before=str(page_data.get('code_examples', []))[:500],
                                tags=[topic]
                            )
                            self.kb.add_pattern(pattern)
        
        return knowledge
    
    def save_learning_log(self, path: str = None):
        """Сохранить журнал обучения."""
        if path is None:
            path = "nobuka/engine/state/learning_log.json"
        
        Path(path).parent.mkdir(parents=True, exist_ok=True)
        
        data = {
            'learned_items': self._learned_items,
            'total_learned': len(self._learned_items),
            'last_session': datetime.now().isoformat(),
            'kb_stats': self.kb.stats()
        }
        
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        
        logger.info(f"📝 Журнал обучения сохранён: {path}")


# ================================================================
#  CLI
# ================================================================

def main():
    """Главная функция для CLI."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Обучение Нобуки программированию')
    parser.add_argument(
        '--source', '-s',
        choices=['all', 'python_docs', 'pep', 'refactoring_guru'],
        default='all',
        help='Источник обучения'
    )
    parser.add_argument(
        '--topic', '-t',
        default=None,
        help='Тема для обучения'
    )
    parser.add_argument(
        '--custom', '-c',
        default=None,
        help='Обучение по произвольной теме'
    )
    parser.add_argument(
        '--stats',
        action='store_true',
        help='Показать статистику базы знаний'
    )
    
    args = parser.parse_args()
    
    logging.basicConfig(level=logging.INFO)
    
    learner = ProgrammingLearner()
    
    if args.stats:
        print("\n📊 Статистика базы знаний:")
        stats = learner.kb.stats()
        for key, value in stats.items():
            print(f"  {key}: {value}")
        return
    
    if args.custom:
        print(f"\n📚 Обучение по теме: {args.custom}")
        knowledge = learner.learn_from_custom_topic(args.custom)
        print(f"✅ Извлечено {len(knowledge)} записей")
    else:
        print(f"\n📚 Обучение из источника: {args.source}")
        knowledge = learner.learn_from_source(args.source, args.topic)
        print(f"✅ Извлечено {len(knowledge)} записей")
    
    learner.save_learning_log()
    
    print(f"\n📊 Статистика базы знаний:")
    stats = learner.kb.stats()
    for key, value in stats.items():
        print(f"  {key}: {value}")


if __name__ == "__main__":
    main()
