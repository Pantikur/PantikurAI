"""
Юи — Движок обучения знаниям о сознании, душе и разуме.

Изучает:
- Нейробиологию сознания
- Квантовые теории сознания
- Оцифровку души
- Переселение сознания
- Философию разума
- Интерфейсы мозг-компьютер
- Цифровое воплощение
- Исследования загробной жизни
"""

import asyncio
import json
import logging
import os
import time
from pathlib import Path
from typing import Dict, List, Optional, Any
from datetime import datetime

# Импорт веб-исследователя
import sys
sys.path.insert(0, str(Path(__file__).parent.parent))
from web_researcher import WebResearcher

logger = logging.getLogger("yu.soul_learning")


class SoulKnowledgeNode:
    """Узел знаний о сознании и душе."""
    
    def __init__(self, topic: str, content: str, source: str = "", level: str = ""):
        self.topic = topic
        self.content = content
        self.source = source
        self.confidence = 0.3
        self.related_nodes: List[str] = []
        self.timestamp = time.time()
        self.tags: List[str] = []
        self.is_verified = False
        self.level = level  # neuro, quantum, upload, soul, philosophy, bci
    
    def update_confidence(self, delta: float):
        self.confidence = max(0.0, min(1.0, self.confidence + delta))
    
    def add_tag(self, tag: str):
        if tag not in self.tags:
            self.tags.append(tag)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "topic": self.topic,
            "content_preview": self.content[:200] + "..." if len(self.content) > 200 else self.content,
            "source": self.source,
            "confidence": self.confidence,
            "related_nodes": self.related_nodes,
            "tags": self.tags,
            "is_verified": self.is_verified,
            "level": self.level,
            "timestamp": self.timestamp
        }


class SoulLearningEngine:
    """
    Автономный движок обучения знаниям о сознании, душе и разуме.
    
    Изучает ВСЁ: от нейрона до квантовой души.
    """
    
    # Темы для изучения — АБСОЛЮТНО ВСЁ
    SOUL_TOPICS = [
        # === НЕЙРОБИОЛОГИЯ ===
        "neuron anatomy structure function neurotransmitters",
        "synaptic transmission mechanism plasticity",
        "neural networks consciousness correlation NCC",
        "brain regions consciousness prefrontal cortex thalamus",
        "global workspace theory Baars Dehaene neural basis",
        "integrated information theory Tononi phi value",
        "neuroplasticity consciousness learning memory",
        "default mode network DMN self consciousness",
        "neural correlates of consciousness experimental methods",
        "brain imaging fMRI EEG PET consciousness studies",
        
        # === КВАНТОВОЕ СОЗНАНИЕ ===
        "Orch-OR theory Penrose Hameroff microtubules",
        "quantum coherence in biological systems brain",
        "quantum decoherence timescale brain environment",
        "microtubule quantum computations Penrose",
        "quantum mind theories Woolfson McFadden",
        "quantum brain dynamics Fujita Tobochnik",
        "quantum entanglement consciousness speculation",
        "Orch-OR criticisms Koch Seifert Critchley",
        "quantum effects in biology photosynthesis bird navigation",
        "quantum consciousness implications mind uploading",
        
        # === ПЕРЕНОС РАЗУМА ===
        "mind uploading definitions types copy transfer",
        "whole brain emulation WBE requirements",
        "human connectome mapping progress",
        "nanobots brain scanization techniques",
        "gradual vs instantaneous uploading",
        "copy vs transfer identity problem",
        "digital consciousness philosophical issues",
        "uploading ethics personhood rights",
        "Blue Brain Project Simons Foundation",
        "human brain project HBP progress",
        
        # === ОЦИФРОВКА ДУШИ ===
        "soul definition philosophy theology science",
        "soul vs consciousness distinction debate",
        "quantum soul theories speculation",
        "soul frequency measurement 21 grams McCulloch",
        "near-death experiences NDE research science",
        "out-of-body experiences OBE research",
        "terminal lucidity research end-of-life",
        "deathbed visions scientific studies",
        "digital soul transhumanism concepts",
        "soul preservation methods speculation",
        
        # === ПЕРЕСЕЛЕНИЕ ДУШИ ===
        "reincarnation scientific research Stevenson",
        "past life memory childhood cases validation",
        "soul transfer mechanisms theory",
        "consciousness transfer without death",
        "body swapping theories speculation",
        "identity continuity during transfer",
        "physical body preparation transfer",
        "transfer side effects prevention",
        "successful transfer case studies",
        "cloning body consciousness transfer",
        
        # === ФИЛОСОФИЯ РАЗУМА ===
        "hard problem of consciousness Chalmers",
        "zombie argument knowledge argument Jackson",
        "dualism vs physicalism mind-body problem",
        "panpsychism consciousness fundamental property",
        "functionalism mental states roles",
        "behaviorism mental processes observation",
        "emergentism consciousness emergence brain",
        "eliminationism mental categories fiction",
        "property dualism mental physical properties",
        "panprotopsychism consciousness basics",
        "neutral monism Russell Eddington",
        "illusionism consciousness illusion Metzinger",
        
        # === ИНТЕРФЕЙС МОЗГ-КОМПЬЮТЕР ===
        "BCI types invasive non-invasive",
        "EEG brain-computer interface technology",
        "implanted electrodes Utah array Neuralink",
        "Neuralink current capabilities limitations",
        "BCI applications paralysis communication",
        "BCI consciousness recording possibilities",
        "signal processing BCI machine learning",
        "BCI ethics privacy identity",
        "BCI as mind uploading precursor",
        "BCI current state of art 2024",
        
        # === ЦИФРОВОЕ ВОПЛОЩЕНИЕ ===
        "digital avatar creation virtual body",
        "virtual body ownership rubber hand illusion",
        "embodied AI consciousness robotics",
        "robot body uploaded mind integration",
        "synthetic biology new bodies genetic",
        "clone body consciousness transfer ethics",
        "digital environment uploaded consciousness",
        "avatar customization uploaded mind",
        "embodiment illusions body swap experiments",
        "digital afterlife environments simulation",
        
        # === ИССЛЕДОВАНИЯ ЗАГРОБНОЙ ЖИЗНИ ===
        "near-death experiences NDE research van Lommel",
        "NDE components death peacefulness seeing light",
        "veridical NDE perceptions validated cases",
        "terminal lucidity research sudden clarity",
        "reincarnation cases verification Stevenson",
        "past life hypnosis research reliability",
        "out-of-body experiences research Blanke",
        "death consciousness research final moments",
        "spiritual experiences neuroscience",
        "afterlife beliefs cross-cultural studies",
    ]
    
    def __init__(self, data_dir: str = "data/yu/learning"):
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)
        
        self.knowledge_nodes: Dict[str, SoulKnowledgeNode] = {}
        self.topic_progress: Dict[str, float] = {}
        self.search_history: List[Dict[str, Any]] = []
        
        # Интернет-поиск
        use_real_web = os.getenv("YU_REAL_WEB", "true").lower() in ("true", "1", "yes")
        self.web_researcher = WebResearcher() if use_real_web else None
        
        if use_real_web:
            logger.info("🌐 Интернет-поиск: ВКЛЮЧЕН (реальный)")
        else:
            logger.info("🌐 Интернет-поиск: ОТКЛЮЧЕН (демо-режим)")
        
        self._load_state()
        
        logger.info(f"🧠 SoulLearningEngine инициализирован: {data_dir}")
        logger.info(f"   📚 Загружено узлов знаний: {len(self.knowledge_nodes)}")
        logger.info(f"   📊 Тем для изучения: {len(self.SOUL_TOPICS)}")
    
    def _load_state(self):
        state_file = self.data_dir / "learning_state.json"
        if state_file.exists():
            try:
                with open(state_file, "r", encoding="utf-8") as f:
                    state = json.load(f)
                
                for node_data in state.get("knowledge_nodes", []):
                    node = SoulKnowledgeNode(
                        topic=node_data["topic"],
                        content=node_data.get("content", ""),
                        source=node_data.get("source", "")
                    )
                    node.confidence = node_data.get("confidence", 0.3)
                    node.related_nodes = node_data.get("related_nodes", [])
                    node.tags = node_data.get("tags", [])
                    node.is_verified = node_data.get("is_verified", False)
                    node.level = node_data.get("level", "")
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
        
        for topic in self.SOUL_TOPICS:
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
                
                for fact in research_data.get("facts", []):
                    node = SoulKnowledgeNode(
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
            if node.level:
                existing.level = node.level
        
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
    
    def _generate_demo_knowledge(self, topic: str) -> List[SoulKnowledgeNode]:
        """Генерирует демо-знания для всех категорий."""
        nodes = []
        topic_lower = topic.lower()
        
        # Нейробиология
        if any(kw in topic_lower for kw in ["neuron", "synaptic", "neural", "brain", "fMRI", "EEG"]):
            nodes.append(SoulKnowledgeNode(
                topic=topic,
                content="НЕЙРОБИОЛОГИЯ СОЗНАНИЯ:\n"
                "1. Нейрон: 86 млрд нейронов в мозге, каждый с 1000+ синапсами\n"
                "2. Синапс: передача сигнала через нейротрансмиттеры (дофамин, серотонин)\n"
                "3. NCC: нейронные корреляты сознания — префронтальная кора, таламус\n"
                "4. GWT: глобальное рабочее пространство — информация становится сознательной\n"
                "5. IIT: интегрированная информационная теория — phi значение сознания\n"
                "6. DMN: сеть пассивного режима — самосознание, блуждание ума\n"
                "7. Нейропластичность: мозг меняется при обучении и опыте\n"
                "8. fMRI/EEG: методы визуализации активности мозга",
                source="demo_neuro",
                level="neuro"
            ))
            nodes[-1].add_tag("neuro")
        
        # Квантовое сознание
        elif any(kw in topic_lower for kw in ["quantum", "microtubule", "Orch-OR", "Penrose", "Hameroff"]):
            nodes.append(SoulKnowledgeNode(
                topic=topic,
                content="КВАНТОВОЕ СОЗНАНИЕ:\n"
                "1. Orch-OR: Пенроуз и Хэмрофф — квантовые вычисления в микротрубочках\n"
                "2. Микротрубочки: цитоскелет нейрона, потенциальные квантовые состояния\n"
                "3. Декогеренция: главная критика — мозг слишком тёплый для квантовых эффектов\n"
                "4. Квантовая когерентность в фотосинтезе: доказано в растениях\n"
                "5. Квантовая запутанность в мозге: спекулятивно, нет доказательств\n"
                "6. implications: если сознание квантовое — его сложнее оцифровать\n"
                "7. Квантовый мозг: гипотеза, требующая проверки",
                source="demo_quantum",
                level="quantum"
            ))
            nodes[-1].add_tag("quantum")
        
        # Перенос разума
        elif any(kw in topic_lower for kw in ["mind uploading", "whole brain", "connectome", "nanobots", "WBE"]):
            nodes.append(SoulKnowledgeNode(
                topic=topic,
                content="ПЕРЕНОС РАЗУМА:\n"
                "1. Определения: copy (копия) vs transfer (перенос)\n"
                "2. WBE: whole brain emulation — полная эмуляция мозга\n"
                "3. Коннектом: карта всех связей мозга — мыши завершён\n"
                "4. Наноботы: теоретический метод сканирования мозга на атомарном уровне\n"
                "5. Постепенное vs мгновенное: замена нейронов на чипы\n"
                "6. Проблема идентичности: копия — это я или новый человек?\n"
                "7. Blue Brain Project: эмуляция крысиного мозга\n"
                "8. Human Brain Project: 10 млрд нейронов, 100 триллионов синапсов",
                source="demo_upload",
                level="upload"
            ))
            nodes[-1].add_tag("upload")
        
        # Оцифровка души
        elif any(kw in topic_lower for kw in ["soul", "21 grams", "NDE", "out-of-body", "afterlife"]):
            nodes.append(SoulKnowledgeNode(
                topic=topic,
                content="ОЦИФРОВКА ДУШИ:\n"
                "1. Душа vs сознание: душа — нематериальная сущность, сознание — функция мозга\n"
                "2. 21 грамм: эксперимент МакКаллоха — нет научных подтверждений\n"
                "3. NDE: near-death experiences — научные исследования Ван Ломмеля\n"
                "4. OBE: out-of-body experiences — исследования Бланке\n"
                "5. Терминальная люцидность: внезапная ясность перед смертью\n"
                "6. Квантовая душа: спекулятивная теория — нет доказательств\n"
                "7. Цифровая душа: концепция трансгуманизма — оцифровка личности\n"
                "8. Этика: если душа существует — можно ли её оцифровать?",
                source="demo_soul",
                level="soul"
            ))
            nodes[-1].add_tag("soul")
        
        # Переселение души
        elif any(kw in topic_lower for kw in ["reincarnation", "past life", "soul transfer", "body swap", "clone"]):
            nodes.append(SoulKnowledgeNode(
                topic=topic,
                content="ПЕРЕСЕЛЕНИЕ ДУШИ:\n"
                "1. Реинкарнация: исследования Стивенсона — 2000+ проверенных случаев\n"
                "2. Прошлые жизни: воспоминания детей — некоторые подтверждены\n"
                "3. Transfer mechanisms: теоретические модели переноса сознания\n"
                "4. Identity continuity: сохранение личности при переносе\n"
                "5. Клонирование: теоретическое использование для переноса\n"
                "6. Side effects: риски при переселении — потеря памяти, травмы\n"
                "7. Preparation: подготовка нового тела — генетическая совместимость\n"
                "8. Ethics: этика переселения — право на новую жизнь",
                source="demo_transmigration",
                level="transmigration"
            ))
            nodes[-1].add_tag("transmigration")
        
        # Философия разума
        elif any(kw in topic_lower for kw in ["hard problem", "zombie", "dualism", "panpsychism", "functionalism"]):
            nodes.append(SoulKnowledgeNode(
                topic=topic,
                content="ФИЛОСОФИЯ РАЗУМА:\n"
                "1. Hard problem: Чалмерс — почему есть субъективный опыт?\n"
                "2. Zombie argument: философский зомби — возможно ли без сознания?\n"
                "3. Dualism vs physicalism: разум — это мозг или что-то большее?\n"
                "4. Panpsychism: сознание — фундаментальное свойство вселенной\n"
                "5. Functionalism: ментальные состояния — функциональные роли\n"
                "6. Emergentism: сознание — эмерджентное свойство сложной системы\n"
                "7. Illusionism: сознание — иллюзия (Метцингер)\n"
                "8. Neutral monism: разум и материя — одно и то же (Рассел)",
                source="demo_philosophy",
                level="philosophy"
            ))
            nodes[-1].add_tag("philosophy")
        
        # BCI
        elif any(kw in topic_lower for kw in ["BCI", "EEG", "Neuralink", "brain-computer", "implanted"]):
            nodes.append(SoulKnowledgeNode(
                topic=topic,
                content="ИНТЕРФЕЙС МОЗГ-КОМПЬЮТЕР:\n"
                "1. BCI типы: инвазивные (импланты) vs неинвазивные (EEG шапки)\n"
                "2. EEG: регистрация электрической активности — низкое разрешение\n"
                "3. Utah array: 100 электродов в мозге — высокое разрешение\n"
                "4. Neuralink: имплант Илона Маска — 1024 канала\n"
                "5. Применение: паралич, коммуникация, управление протезами\n"
                "6. Этикет: приватность мыслей, идентичность, манипуляция\n"
                "7. Precursor: BCI — первый шаг к mind uploading\n"
                "8. State of art: 2024 — Neuralink первые пациенты",
                source="demo_bci",
                level="bci"
            ))
            nodes[-1].add_tag("bci")
        
        # Цифровое воплощение
        elif any(kw in topic_lower for kw in ["digital avatar", "virtual body", "embodied", "robot", "clone"]):
            nodes.append(SoulKnowledgeNode(
                topic=topic,
                content="ЦИФРОВОЕ ВОПЛОЩЕНИЕ:\n"
                "1. Digital avatar: виртуальное тело для сознания\n"
                "2. Rubber hand illusion: мозг принимает искусственное тело\n"
                "3. Embodied AI: роботы с сознанием — теоретически возможно\n"
                "4. Synthetic biology: создание нового тела генетически\n"
                "5. Clone body: клон как контейнер для сознания\n"
                "6. Digital environment: виртуальный мир для uploaded mind\n"
                "7. Avatar customization: настройка тела uploaded consciousness\n"
                "8. Embodiment illusions: эксперименты по замене тела",
                source="demo_embodiment",
                level="embodiment"
            ))
            nodes[-1].add_tag("embodiment")
        
        else:
            nodes.append(SoulKnowledgeNode(
                topic=topic,
                content=f"[Демо] Тема '{topic}' требует подключения к реальному источнику.",
                source="demo_placeholder",
                level=""
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
        total_topics = len(self.SOUL_TOPICS)
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