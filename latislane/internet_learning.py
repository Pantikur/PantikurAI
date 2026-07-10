"""
Latislane — Движок автономного обучения из интернета.

Использует реальные источники:
- Wikipedia API
- PubMed API (медицина)
- arXiv API (наука)
- Web scraping
"""

import asyncio
import json
import logging
import os
import re
import time
from pathlib import Path
from typing import Dict, List, Optional, Any, Set
from datetime import datetime, timedelta

# Импорт веб-исследователя
import sys
sys.path.insert(0, str(Path(__file__).parent.parent))
from web_researcher import WebResearcher

logger = logging.getLogger("latislane.learning")


class KnowledgeNode:
    """
    Узел знаний — единица изученной информации.
    
    Каждый узел содержит:
    - Тема (anatomy, robotics, genetics и т.д.)
    - Содержание
    - Источник
    - Уверенность (0.0 — 1.0)
    - Связи с другими узлами
    """
    
    def __init__(self, topic: str, content: str, source: str = ""):
        self.topic = topic
        self.content = content
        self.source = source
        self.confidence = 0.3  # Начальная уверенность
        self.related_nodes: List[str] = []
        self.timestamp = time.time()
        self.tags: List[str] = []
        self.is_verified = False
    
    def update_confidence(self, delta: float):
        """Обновить уверенность."""
        self.confidence = max(0.0, min(1.0, self.confidence + delta))
    
    def add_tag(self, tag: str):
        """Добавить тег."""
        if tag not in self.tags:
            self.tags.append(tag)
    
    def to_dict(self) -> Dict:
        return {
            "topic": self.topic,
            "content_preview": self.content[:200] + "..." if len(self.content) > 200 else self.content,
            "source": self.source,
            "confidence": self.confidence,
            "related_nodes": self.related_nodes,
            "tags": self.tags,
            "is_verified": self.is_verified,
            "timestamp": self.timestamp
        }


class InternetLearningEngine:
    """
    Автономный движок обучения из интернета.
    
    Работает по циклу:
    1. Определение пробелов в знаниях
    2. Поиск информации по пробелам
    3. Извлечение знаний
    4. Обновление модели
    5. Оценка прогресса
    """
    
    # Темы для изучения тела человека
    ANATOMY_TOPICS = [
        # Анатомия
        "human skeletal system anatomy",
        "human muscular system anatomy",
        "human nervous system neuroanatomy",
        "human cardiovascular system",
        "human respiratory system",
        "human digestive system",
        "human endocrine system",
        "human immune system",
        "human reproductive system male",
        "human reproductive system female",
        "human sensory system",
        "human integumentary system skin",
        
        # Клеточная биология
        "cell biology human cells",
        "human cell types classification",
        "stem cells human",
        "human tissue types",
        
        # Генетика
        "human genome genetics",
        "human DNA structure",
        "gene expression regulation",
        "epigenetics human",
        
        # Физиология
        "human physiology homeostasis",
        "human metabolism biochemistry",
        "human neurophysiology",
        "human immunology",
        
        # Бионика и протезирование
        "biomechanics human movement",
        "prosthetics design principles",
        "bionic limb technology",
        "neural prosthetics brain computer interface",
        "robotic exoskeleton human",
        
        # Биоинженерия
        "tissue engineering human organs",
        "3d bioprinting organs",
        "organoid human development",
        "gene editing CRISPR human",
        "synthetic biology human cells",
        
        # Нейронаука
        "human brain neuroplasticity",
        "synaptic transmission neuroscience",
        "cognitive neuroscience human",
        "neural circuits learning memory",
        
        # Эволюция
        "human evolution anatomy changes",
        "comparative anatomy primates",
    ]
    
    def __init__(self, data_dir: str = "data/latislane"):
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)
        
        # Хранилище знаний
        self.knowledge_nodes: Dict[str, KnowledgeNode] = {}
        self.topic_progress: Dict[str, float] = {}
        self.search_history: List[Dict[str, Any]] = []
        self.unresolved_gaps: List[str] = []
        
        # Реальный веб-исследователь
        use_real_web = os.getenv("LATISLANE_REAL_WEB", "true").lower() in ("true", "1", "yes")
        self.web_researcher = WebResearcher() if use_real_web else None
        
        if use_real_web:
            logger.info("🌐 Интернет-поиск: ВКЛЮЧЕН (реальный)")
        else:
            logger.info("🌐 Интернет-поиск: ОТКЛЮЧЕН (демо-режим)")
        
        # Загрузка состояния
        self._load_state()
        
        logger.info(f"🧠 InternetLearningEngine инициализирован: {data_dir}")
        logger.info(f"   📚 Загружено узлов знаний: {len(self.knowledge_nodes)}")
        logger.info(f"   📊 Тем для изучения: {len(self.ANATOMY_TOPICS)}")
    
    def _load_state(self):
        """Загрузить состояние из файла."""
        state_file = self.data_dir / "learning_state.json"
        if state_file.exists():
            try:
                with open(state_file, "r", encoding="utf-8") as f:
                    state = json.load(f)
                
                # Восстановление узлов знаний
                for node_data in state.get("knowledge_nodes", []):
                    node = KnowledgeNode(
                        topic=node_data["topic"],
                        content=node_data.get("content", ""),
                        source=node_data.get("source", "")
                    )
                    node.confidence = node_data.get("confidence", 0.3)
                    node.related_nodes = node_data.get("related_nodes", [])
                    node.tags = node_data.get("tags", [])
                    node.is_verified = node_data.get("is_verified", False)
                    self.knowledge_nodes[node.topic] = node
                
                # Восстановление прогресса
                self.topic_progress = state.get("topic_progress", {})
                
                logger.info(f"✅ Состояние загружено: {len(self.knowledge_nodes)} узлов")
            except Exception as e:
                logger.warning(f"⚠️ Ошибка загрузки состояния: {e}")
        else:
            logger.info("ℹ️ Новое состояние создано")
    
    def _save_state(self):
        """Сохранить состояние в файл."""
        state = {
            "knowledge_nodes": [node.to_dict() for node in self.knowledge_nodes.values()],
            "topic_progress": self.topic_progress,
            "search_history": self.search_history[-100:],  # последние 100 записей
            "saved_at": time.time()
        }
        
        state_file = self.data_dir / "learning_state.json"
        try:
            with open(state_file, "w", encoding="utf-8") as f:
                json.dump(state, f, ensure_ascii=False, indent=2)
            logger.debug(f"💾 Состояние сохранено: {len(self.knowledge_nodes)} узлов")
        except Exception as e:
            logger.error(f"❌ Ошибка сохранения состояния: {e}")
    
    def get_knowledge_gaps(self) -> List[str]:
        """
        Определить пробелы в знаниях.
        
        Анализирует прогресс по темам и возвращает
        темы, требующие изучения.
        """
        gaps = []
        
        for topic in self.ANATOMY_TOPICS:
            progress = self.topic_progress.get(topic, 0.0)
            
            if progress < 0.3:
                # Низкий прогресс — высокий приоритет
                gaps.append((topic, 0.9))
            elif progress < 0.6:
                # Средний прогресс
                gaps.append((topic, 0.6))
            elif progress < 0.9:
                # Высокий прогресс, но есть что улучшить
                gaps.append((topic, 0.3))
        
        # Сортировка по приоритету
        gaps.sort(key=lambda x: x[1], reverse=True)
        
        return [g[0] for g in gaps]
    
    async def search_and_learn(self, topic: str, max_results: int = 5) -> Dict[str, Any]:
        """
        Поиск и изучение по конкретной теме.
        
        Использует реальный веб-поиск через WebResearcher.
        """
        logger.info(f"🔍 Изучение темы: {topic}")
        
        result = {
            "topic": topic,
            "nodes_added": 0,
            "confidence_improved": 0.0,
            "sources": []
        }
        
        nodes = []
        
        # Реальный поиск в интернете
        if self.web_researcher:
            try:
                research_data = await self.web_researcher.learn_from_search(topic)
                
                # Создаём узлы знаний из реальных данных
                for fact in research_data.get("facts", []):
                    node = KnowledgeNode(
                        topic=topic,
                        content=fact["text"],
                        source=fact["source"]
                    )
                    node.confidence = fact["confidence"]
                    node.add_tag(topic.split()[0])  # Первый слово как тег
                    
                    nodes.append(node)
                
                result["sources"] = research_data.get("sources_used", [])
                result["facts_count"] = research_data.get("facts_count", 0)
                
                logger.info(f"📊 Найдено {research_data.get('facts_count', 0)} фактов из {len(result['sources'])} источников")
                
            except Exception as e:
                logger.warning(f"⚠️ Реальный поиск неудачен, используем демо: {e}")
                nodes = self._generate_demo_knowledge(topic)
        else:
            # Демо-режим
            nodes = self._generate_demo_knowledge(topic)
        
        # Сохранение узлов
        for node in nodes:
            if node.topic not in self.knowledge_nodes:
                self.knowledge_nodes[node.topic] = node
                result["nodes_added"] += 1
            
            # Обновление существующего узла
            existing = self.knowledge_nodes[node.topic]
            if node.confidence > existing.confidence:
                existing.update_confidence(node.confidence - existing.confidence)
                result["confidence_improved"] += node.confidence - existing.confidence
            
            existing.related_nodes = list(set(existing.related_nodes + node.related_nodes))
            existing.tags = list(set(existing.tags + node.tags))
        
        # Обновление прогресса
        self.topic_progress[topic] = min(1.0, self.topic_progress.get(topic, 0.0) + 0.15)
        
        # Логирование
        self.search_history.append({
            "topic": topic,
            "timestamp": time.time(),
            "nodes_added": result["nodes_added"],
            "confidence": self.topic_progress.get(topic, 0.0),
            "web_researcher": bool(self.web_researcher)
        })
        
        logger.info(f"✅ Тема '{topic}' изучена: +{result['nodes_added']} узлов, прогресс: {self.topic_progress.get(topic, 0.0):.2f}")
        
        return result
    
    def _generate_demo_knowledge(self, topic: str) -> List[KnowledgeNode]:
        """
        Генерация демо-знаний (заглушка для веб-поиска).
        
        В реальном режиме здесь будет вызов API поиска.
        """
        nodes = []
        
        # Категоризация темы
        topic_lower = topic.lower()
        
        if "skeletal" in topic_lower or "bone" in topic_lower:
            node1 = KnowledgeNode(topic=topic, content="Скелет взрослого человека состоит из 206 костей. Кости состоят из минерализованной матрицы (гидроксиапатит кальция) и коллагена. Костный мозг производит кровяные клетки.", source="demo_anatomy_database")
            node1.confidence = 0.7
            node1.add_tag("anatomy")
            node1.add_tag("skeletal")
            node1.add_tag("bones")
            nodes.append(node1)
            
            node2 = KnowledgeNode(topic=f"{topic}_biomechanics", content="Кости адаптируются к нагрузкам по закону Вольфа. Плотность кости зависит от механических стимулов. В микрогравитации происходит резорбция костей.", source="demo_biomechanics")
            node2.confidence = 0.6
            node2.add_tag("biomechanics")
            node2.add_tag("adaptation")
            nodes.append(node2)
            
        elif "muscular" in topic_lower or "muscle" in topic_lower:
            n1 = KnowledgeNode(topic=topic, content="Скелетные мышцы составляют 40-50% массы тела. Существуют три типа мышечных волокон: Type I (медленные), Type IIa (быстрые окислительные), Type IIx (быстрые гликолитические). Гипертрофия происходит через синтез актина и миозина.", source="demo_muscle_biology")
            n1.confidence = 0.75
            n1.add_tag("anatomy")
            n1.add_tag("muscular")
            n1.add_tag("hypertrophy")
            nodes.append(n1)
            
            n2 = KnowledgeNode(topic=f"{topic}_neural_control", content="Мышечное сокращение контролируется моторными нейронами спинного мозга. Один нейрон иннервирует от нескольких до сотен мышечных волокон (моторная единица).", source="demo_neurophysiology")
            n2.confidence = 0.65
            n2.add_tag("neurophysiology")
            n2.add_tag("motor_control")
            nodes.append(n2)
            
        elif "nervous" in topic_lower or "neuro" in topic_lower:
            n1 = KnowledgeNode(topic=topic, content="ЦНС состоит из ~86 миллиардов нейронов. Синаптическая передача происходит за 0.5-5 мс. Нейропластичность позволяет формировать новые связи всю жизнь. Миелинизация увеличивает скорость проводимости до 120 м/с.", source="demo_neuroscience")
            n1.confidence = 0.8
            n1.add_tag("neuroscience")
            n1.add_tag("neurons")
            n1.add_tag("synapses")
            nodes.append(n1)
            
            n2 = KnowledgeNode(topic=f"{topic}_interfaces", content="Нейроинтерфейсы (BCI) позволяют преобразовывать нейронную активность в команды. Имплантируемые электроды (Neuralink) используют микроиглы для записи от сотен нейронов.", source="demo_bci_research")
            n2.confidence = 0.6
            n2.add_tag("brain-computer interface")
            n2.add_tag("bionic")
            nodes.append(n2)
            
        elif "cardiovascular" in topic_lower or "heart" in topic_lower:
            n1 = KnowledgeNode(topic=topic, content="Сердце бьётся ~100 000 раз в день, перекачивая ~7 500 литров крови. Миокард состоит из кардиомиоцитов с автогенерацией потенциала действия. Коронарные артерии питают сердечную мышцу.", source="demo_cardiology")
            n1.confidence = 0.7
            n1.add_tag("cardiology")
            n1.add_tag("circulation")
            nodes.append(n1)
            
        elif "3d bioprinting" in topic_lower or "bioprinting" in topic_lower:
            n1 = KnowledgeNode(topic=topic, content="3D биопечать использует 'биочернила' с живыми клетками для создания тканевых структур. Современные методы позволяют печатать сосудистые сети, хрящи, кожу и простые органы.", source="demo_tissue_engineering")
            n1.confidence = 0.65
            n1.add_tag("tissue engineering")
            n1.add_tag("bioprinting")
            n1.add_tag("regenerative medicine")
            nodes.append(n1)
            
        elif "prosthetics" in topic_lower or "prosthetic" in topic_lower:
            n1 = KnowledgeNode(topic=topic, content="Современные протезы используют миоэлектрические сигналы для контроля. Тактильная обратная связь достигается через имплантированные сенсоры. Титановые остеоинтеграционные импланты обеспечивают прочную связь с костью.", source="demo_prosthetics")
            n1.confidence = 0.7
            n1.add_tag("prosthetics")
            n1.add_tag("bionic")
            n1.add_tag("mechatronics")
            nodes.append(n1)
            
        else:
            n1 = KnowledgeNode(topic=topic, content=f"[Демо] Изучение темы '{topic}' требует подключения к реальному источнику данных (PubMed, Google Scholar, GitHub).", source="demo_placeholder")
            n1.confidence = 0.3
            n1.add_tag("placeholder")
            nodes.append(n1)
        
        return nodes
    
    async def _real_web_search(self, topic: str) -> List[KnowledgeNode]:
        """
        Реальный поиск в интернете.
        
        Здесь будет интеграция с:
        - PubMed API (медицинские статьи)
        - Google Scholar
        - arXiv (научные预印本)
        - GitHub (открытые проекты)
        """
        nodes = []
        
        # TODO: Реализация реального поиска
        # Пример с PubMed API:
        # import requests
        # url = f"https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi?db=pmc&term={topic}&retmax=5"
        # response = requests.get(url)
        # ...
        
        logger.warning(f"⚠️ Реальный веб-поиск не реализован. Используется демо-режим.")
        return self._generate_demo_knowledge(topic)
    
    async def learn_batch(self, topics: List[str], batch_size: int = 3) -> Dict[str, Any]:
        """
        Пакетное обучение по нескольким темам.
        
        :param topics: Список тем для изучения
        :param batch_size: Размер пакета (для ограничения нагрузки)
        """
        results = []
        
        for i in range(0, len(topics), batch_size):
            batch = topics[i:i + batch_size]
            batch_results = await asyncio.gather(
                *[self.search_and_learn(topic) for topic in batch]
            )
            results.extend(batch_results)
            
            # Пауза между пакетами
            if i + batch_size < len(topics):
                await asyncio.sleep(1)
        
        self._save_state()
        
        return {
            "total_topics": len(topics),
            "completed": len(results),
            "results": results
        }
    
    async def run_continuous_learning(self, interval_minutes: int = 10):
        """
        Непрерывное автономное обучение.
        
        Запускает цикл:
        1. Определение пробелов
        2. Изучение тем
        3. Сохранение состояния
        4. Ожидание
        """
        logger.info(f"🔄 Запуск непрерывного обучения (интервал: {interval_minutes} мин)")
        
        cycle_count = 0
        
        while True:
            try:
                cycle_count += 1
                logger.info(f"📚 Цикл обучения #{cycle_count}")
                
                # Определение пробелов
                gaps = self.get_knowledge_gaps()
                
                if not gaps:
                    logger.info("✅ Все темы изучены на 100%")
                    break
                
                # Изучение топ-5 тем
                topics_to_learn = gaps[:5]
                logger.info(f"🎯 Темы для изучения: {topics_to_learn}")
                
                results = await self.learn_batch(topics_to_learn)
                
                logger.info(f"✅ Цикл #{cycle_count} завершён: {results['completed']}/{results['total_topics']} тем")
                
                # Сохранение промежуточного состояния
                self._save_state()
                
                # Ожидание
                await asyncio.sleep(interval_minutes * 60)
                
            except asyncio.CancelledError:
                logger.info("⏹️ Непрерывное обучение остановлено")
                self._save_state()
                break
            except Exception as e:
                logger.error(f"❌ Ошибка в цикле обучения: {e}")
                await asyncio.sleep(60)
    
    def get_learning_report(self) -> Dict[str, Any]:
        """Получить отчёт о прогрессе обучения."""
        total_topics = len(self.ANATOMY_TOPICS)
        studied_topics = sum(1 for p in self.topic_progress.values() if p > 0.1)
        high_confidence = sum(1 for n in self.knowledge_nodes.values() if n.confidence > 0.7)
        
        return {
            "total_topics": total_topics,
            "studied_topics": studied_topics,
            "knowledge_nodes": len(self.knowledge_nodes),
            "high_confidence_nodes": high_confidence,
            "overall_progress": sum(self.topic_progress.values()) / total_topics if total_topics > 0 else 0,
            "search_history_count": len(self.search_history),
            "topic_details": {
                topic: progress
                for topic, progress in sorted(
                    self.topic_progress.items(),
                    key=lambda x: x[1],
                    reverse=True
                )[:10]
            }
        }
    
    def export_knowledge(self, output_file: Optional[str] = None) -> str:
        """Экспорт всех знаний в JSON."""
        if output_file is None:
            output_file = str(self.data_dir / "knowledge_export.json")
        
        export_data = {
            "exported_at": time.time(),
            "total_nodes": len(self.knowledge_nodes),
            "topics_covered": len(self.topic_progress),
            "knowledge_nodes": {
                topic: node.to_dict()
                for topic, node in self.knowledge_nodes.items()
            },
            "topic_progress": self.topic_progress,
            "learning_report": self.get_learning_report()
        }
        
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(export_data, f, ensure_ascii=False, indent=2)
        
        logger.info(f"📤 Знания экспортированы: {output_file}")
        return output_file
