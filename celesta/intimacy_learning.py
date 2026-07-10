"""
Celesta — Движок обучения интимным знаниям.

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

logger = logging.getLogger("celesta.learning")


class KnowledgeNode:
    """Узел знаний — единица изученной информации."""
    
    def __init__(self, topic: str, content: str, source: str = "", stage: str = ""):
        self.topic = topic
        self.content = content
        self.source = source
        self.confidence = 0.3
        self.related_nodes: List[str] = []
        self.timestamp = time.time()
        self.tags: List[str] = []
        self.is_verified = False
        self.stage = stage
    
    def update_confidence(self, delta: float):
        self.confidence = max(0.0, min(1.0, self.confidence + delta))
    
    def add_tag(self, tag: str):
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
            "stage": self.stage,
            "timestamp": self.timestamp
        }


class IntimacyLearningEngine:
    """
    Автономный движок обучения интимным знаниям.
    """
    
    # Темы для изучения
    INTIMACY_TOPICS = [
        # Физиология прикосновений
        "human touch physiology C-tactile fibers",
        "skin receptor density distribution",
        "tactile deprivation effects psychology",
        "oral sensory cortex representation",
        "cutaneous mechanoreceptors types",
        
        # Возбуждение
        "human sexual arousal physiology phases",
        "parasympathetic nervous system erection",
        "sympathetic nervous system orgasm",
        "nitric oxide vasodilation mechanism",
        "sexual response cycle Masters Johnson",
        
        # Гормоны
        "oxytocin bonding effects psychology",
        "prolactin refractory period mechanism",
        "dopamine reward system sexuality",
        "endorphins pain relief intimacy",
        "cortisol stress sexual function",
        
        # Репродуктивная система
        "sperm egg fertilization timeline",
        "ovulation fertility window calculation",
        "male refractory period biology",
        "female orgasm uterine contractions",
        
        # Избыточный интим
        "excessive sexual activity health effects",
        "zinc depletion semen analysis",
        "prolactin testosterone relationship",
        "dopamine tolerance addiction sexuality",
        "tissue microtrauma healing intimacy",
        
        # Прерванный процесс
        "vasocongestion pelvic syndrome",
        "retrograde ejaculation consequences",
        "chronic prostatitis etiology",
        "conditioned reflex disruption sexuality",
        "sexual frustration psychological effects",
        
        # Восстановление
        "post coital somnolence biology",
        "refractory period age correlation",
        "nutritional recovery sexuality zinc magnesium",
        "sleep growth hormone recovery",
        
        # Психология
        "intimate bonding psychology attachment",
        "sexual trauma effects recovery",
        "communication intimacy relationship",
        "emotional vs physical intimacy",
        
        # Расы (фэнтези)
        "elf physiology metabolism fantasy",
        "demon stamina physiology fantasy",
        "undead sensory function biology",
        "elemental energy exchange concept",
    ]
    
    def __init__(self, data_dir: str = "data/celesta/learning"):
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)
        
        self.knowledge_nodes: Dict[str, KnowledgeNode] = {}
        self.topic_progress: Dict[str, float] = {}
        self.search_history: List[Dict[str, Any]] = []
        
        # Реальный веб-исследователь
        use_real_web = os.getenv("CELESTA_REAL_WEB", "true").lower() in ("true", "1", "yes")
        self.web_researcher = WebResearcher() if use_real_web else None
        
        if use_real_web:
            logger.info("🌐 Интернет-поиск: ВКЛЮЧЕН (реальный)")
        else:
            logger.info("🌐 Интернет-поиск: ОТКЛЮЧЕН (демо-режим)")
        
        self._load_state()
        
        logger.info(f"🌹 IntimacyLearningEngine инициализирован: {data_dir}")
        logger.info(f"   📚 Загружено узлов знаний: {len(self.knowledge_nodes)}")
        logger.info(f"   📊 Тем для изучения: {len(self.INTIMACY_TOPICS)}")
    
    def _load_state(self):
        state_file = self.data_dir / "learning_state.json"
        if state_file.exists():
            try:
                with open(state_file, "r", encoding="utf-8") as f:
                    state = json.load(f)
                
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
                    node.stage = node_data.get("stage", "")
                    self.knowledge_nodes[node.topic] = node
                
                self.topic_progress = state.get("topic_progress", {})
                logger.info(f"✅ Состояние загружено: {len(self.knowledge_nodes)} узлов")
            except Exception as e:
                logger.warning(f"⚠️ Ошибка загрузки состояния: {e}")
        else:
            logger.info("ℹ️ Новое состояние создано")
    
    def _save_state(self):
        state = {
            "knowledge_nodes": [node.to_dict() for node in self.knowledge_nodes.values()],
            "topic_progress": self.topic_progress,
            "search_history": self.search_history[-100:],
            "saved_at": time.time()
        }
        
        state_file = self.data_dir / "learning_state.json"
        try:
            with open(state_file, "w", encoding="utf-8") as f:
                json.dump(state, f, ensure_ascii=False, indent=2)
        except Exception as e:
            logger.error(f"❌ Ошибка сохранения: {e}")
    
    def get_knowledge_gaps(self) -> List[str]:
        gaps = []
        
        for topic in self.INTIMACY_TOPICS:
            progress = self.topic_progress.get(topic, 0.0)
            
            if progress < 0.3:
                gaps.append((topic, 0.9))
            elif progress < 0.6:
                gaps.append((topic, 0.6))
            elif progress < 0.9:
                gaps.append((topic, 0.3))
        
        gaps.sort(key=lambda x: x[1], reverse=True)
        return [g[0] for g in gaps]
    
    async def search_and_learn(self, topic: str) -> Dict[str, Any]:
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
                    node.add_tag(topic.split()[0])
                    
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
        
        for node in nodes:
            if node.topic not in self.knowledge_nodes:
                self.knowledge_nodes[node.topic] = node
                result["nodes_added"] += 1
            
            existing = self.knowledge_nodes[node.topic]
            if node.confidence > existing.confidence:
                existing.update_confidence(node.confidence - existing.confidence)
                result["confidence_improved"] += node.confidence - existing.confidence
            
            existing.related_nodes = list(set(existing.related_nodes + node.related_nodes))
            existing.tags = list(set(existing.tags + node.tags))
            if node.stage:
                existing.stage = node.stage
        
        self.topic_progress[topic] = min(1.0, self.topic_progress.get(topic, 0.0) + 0.15)
        
        self.search_history.append({
            "topic": topic,
            "timestamp": time.time(),
            "nodes_added": result["nodes_added"],
            "confidence": self.topic_progress.get(topic, 0.0),
            "web_researcher": bool(self.web_researcher)
        })
        
        logger.info(f"✅ Тема '{topic}' изучена: +{result['nodes_added']} узлов")
        return result
    
    def _generate_demo_knowledge(self, topic: str) -> List[KnowledgeNode]:
        nodes = []
        topic_lower = topic.lower()
        
        # Прикосновения
        if "touch" in topic_lower or "tactile" in topic_lower or "skin" in topic_lower:
            nodes.append(KnowledgeNode(
                topic=topic,
                content="Кожа содержит ~5 миллионов тактильных рецепторов. C-волокна передают медленные приятные прикосновения (1 м/с), A-дельта волокна — быстрые давящие (20 м/с).",
                source="demo_touch_physiology",
                stage="touch"
            ))
            nodes[-1].add_tag("touch")
            nodes[-1].add_tag("physiology")
        
        # Возбуждение
        elif "arousal" in topic_lower or "erection" in topic_lower or "lubrication" in topic_lower:
            nodes.append(KnowledgeNode(
                topic=topic,
                content="Возбуждение запускается парасимпатической системой. Оксид азота (NO) вызывает вазодилатацию. Время реакции: 30 секунд. Фазы: желание → возбуждение → плато → оргазм.",
                source="demo_arousal_physiology",
                stage="arousal"
            ))
            nodes[-1].add_tag("arousal")
            nodes[-1].add_tag("physiology")
        
        # Гормоны
        elif "oxytocin" in topic_lower or "prolactin" in topic_lower or "dopamine" in topic_lower:
            nodes.append(KnowledgeNode(
                topic=topic,
                content="Окситоцин вызывает привязанность и доверие. Пролактин подавляет тестостерон, вызывая рефрактерный период. Дофамин — система вознаграждения, может вызывать зависимость.",
                source="demo_hormone_effects",
                stage="intimacy"
            ))
            nodes[-1].add_tag("hormones")
            nodes[-1].add_tag("psychology")
        
        # Избыточный интим
        elif "excessive" in topic_lower or "zinc" in topic_lower or "depletion" in topic_lower:
            nodes.append(KnowledgeNode(
                topic=topic,
                content="Чрезмерная активность истощает запасы цинка (3 мг за событие). Пролактин ↑ → тестостерон ↓ на 25%. Хроническая усталость, раздражительность, микроповреждения тканей.",
                source="demo_excessive_effects",
                stage="excessive"
            ))
            nodes[-1].add_tag("excessive")
            nodes[-1].add_tag("pathology")
        
        # Прерванный процесс
        elif "interrupted" in topic_lower or "vasocongestion" in topic_lower or "prostatitis" in topic_lower:
            nodes.append(KnowledgeNode(
                topic=topic,
                content="Прерванное возбуждение вызывает венозный застой в тазу (боль, давление 6-24ч). Ретроградная эякуляция — риск повреждения мочевого пузыря. Хроническое прерывание → простатит (3-12 мес восстановление).",
                source="demo_interrupted_effects",
                stage="interrupted"
            ))
            nodes[-1].add_tag("interrupted")
            nodes[-1].add_tag("pathology")
        
        # Восстановление
        elif "recovery" in topic_lower or "refractory" in topic_lower or "sleep" in topic_lower:
            nodes.append(KnowledgeNode(
                topic=topic,
                content="Рефрактерный период: 15 мин — 48 часов (возрастзависимый). Восстановление цинка: 2-3 дня. Сон с гормоном роста ускоряет восстановление на 40%. Гидратация: 2 л/день.",
                source="demo_recovery_biology",
                stage="recovery"
            ))
            nodes[-1].add_tag("recovery")
            nodes[-1].add_tag("physiology")
        
        # Расы
        elif "elf" in topic_lower or "demon" in topic_lower or "race" in topic_lower or "fantasy" in topic_lower:
            nodes.append(KnowledgeNode(
                topic=topic,
                content="Эльфы: замедленный метаболизм, возбуждение ×2, высокая гормональная чувствительность. Демоны: выносливость ×3, рефрактерный ÷3, экстремальная интенсивность. Нежить: репродукция нет, сенсорика сохранена.",
                source="demo_race_specific",
                stage="full_understanding"
            ))
            nodes[-1].add_tag("race_specific")
            nodes[-1].add_tag("fantasy")
        
        # Репродукция
        elif "fertilization" in topic_lower or "ovulation" in topic_lower or "sperm" in topic_lower:
            nodes.append(KnowledgeNode(
                topic=topic,
                content="Сперматозоид достигает яйцеклетки за 5-30 минут. Фертильное окно: 5 дней перед овуляцией. Выживание сперматозоидов: 24 часа. Женский оргазм может ускорять транспорт спермы сокращениями матки.",
                source="demo_reproductive_biology",
                stage="intimacy"
            ))
            nodes[-1].add_tag("reproductive")
            nodes[-1].add_tag("biology")
        
        else:
            nodes.append(KnowledgeNode(
                topic=topic,
                content=f"[Демо] Тема '{topic}' требует подключения к реальному источнику.",
                source="demo_placeholder",
                stage=""
            ))
            nodes[-1].add_tag("placeholder")
        
        return nodes
    
    async def learn_batch(self, topics: List[str], batch_size: int = 3) -> Dict[str, Any]:
        results = []
        
        for i in range(0, len(topics), batch_size):
            batch = topics[i:i + batch_size]
            batch_results = await asyncio.gather(
                *[self.search_and_learn(topic) for topic in batch]
            )
            results.extend(batch_results)
            
            if i + batch_size < len(topics):
                await asyncio.sleep(1)
        
        self._save_state()
        
        return {
            "total_topics": len(topics),
            "completed": len(results),
            "results": results
        }
    
    async def run_continuous_learning(self, interval_minutes: int = 10):
        logger.info(f"🔄 Запуск непрерывного обучения (интервал: {interval_minutes} мин)")
        
        cycle_count = 0
        
        while True:
            try:
                cycle_count += 1
                logger.info(f"📚 Цикл #{cycle_count}")
                
                gaps = self.get_knowledge_gaps()
                
                if not gaps:
                    logger.info("✅ Все темы изучены")
                    break
                
                topics_to_learn = gaps[:5]
                results = await self.learn_batch(topics_to_learn)
                
                logger.info(f"✅ Цикл #{cycle_count} завершён: {results['completed']}/{results['total_topics']}")
                
                self._save_state()
                await asyncio.sleep(interval_minutes * 60)
                
            except asyncio.CancelledError:
                logger.info("⏹️ Обучение остановлено")
                self._save_state()
                break
            except Exception as e:
                logger.error(f"❌ Ошибка: {e}")
                await asyncio.sleep(60)
    
    def get_learning_report(self) -> Dict[str, Any]:
        total_topics = len(self.INTIMACY_TOPICS)
        studied_topics = sum(1 for p in self.topic_progress.values() if p > 0.1)
        high_confidence = sum(1 for n in self.knowledge_nodes.values() if n.confidence > 0.7)
        
        return {
            "total_topics": total_topics,
            "studied_topics": studied_topics,
            "knowledge_nodes": len(self.knowledge_nodes),
            "high_confidence_nodes": high_confidence,
            "overall_progress": sum(self.topic_progress.values()) / total_topics if total_topics > 0 else 0,
            "search_history_count": len(self.search_history)
        }
