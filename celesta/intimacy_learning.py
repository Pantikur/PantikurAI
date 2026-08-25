"""
Селеста — Движок обучения интимным знаниям.

Изучает абсолютно всё:
- Solo, Duo, Trio, Quad, Group
- Same-Sex (M|M, F|F)
- Consent, Coercion
- Физиология, психология, гормоны
- Последействие, восстановление

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

import sys
sys.path.insert(0, str(Path(__file__).parent.parent))
from services.web_researcher import WebResearcher

logger = logging.getLogger("celesta.learning")


class KnowledgeNode:
    """Узел знаний — единица изученной информации."""
    
    def __init__(self, topic: str, content: str, source: str = "", level: str = ""):
        self.topic = topic
        self.content = content
        self.source = source
        self.confidence = 0.3
        self.related_nodes: List[str] = []
        self.timestamp = time.time()
        self.tags: List[str] = []
        self.is_verified = False
        self.level = level
    
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
            "level": self.level,
            "timestamp": self.timestamp
        }


class IntimacyLearningEngine:
    """
    Автономный движок обучения интимным знаниям.
    
    Изучает ВСЁ: от взгляда до оргии.
    """
    
    # Темы для изучения — АБСОЛЮТНО ВСЁ
    INTIMACY_TOPICS = [
        # === SOLO ===
        "solo masturbation anatomy techniques",
        "solo sex toys types usage safety",
        "solo fetish sensory play materials",
        "solo fantasy erotica pornography psychology",
        "zinc depletion semen analysis recovery",
        "post orgasmic illness syndrome POIS",
        
        # === DUO ORAL ===
        "killingus clitoral anatomy techniques",
        "fellatio techniques deepthroat hand techniques",
        "anal oral sex dental dam hygiene safety",
        "clitoral anatomy 8000 nerve endings",
        
        # === DUO PENETRATIVE ===
        "missionary position variations angles",
        "doggy style depth control variations",
        "cowgirl position depth control facing reverse",
        "spooning position intimacy long session",
        "69 position simultaneous oral coordination",
        "standing sex balance support variations",
        "edge of bed position depth eye contact",
        "lotus position intimacy eye contact",
        
        # === DUO ANAL ===
        "anal sphincter anatomy preparation",
        "prostate stimulation male G spot techniques",
        "anal sex lube types safety rules",
        "anal beads plug prostate massager safety",
        
        # === DUO EDGING & DENIAL ===
        "edging stop start technique benefits",
        "denial orgasm control psychology power",
        "blue balls pelvic congestion syndrome",
        
        # === TRIO ===
        "FFM threesome dynamics third wheel",
        "MMF threesome male dynamics cooperation",
        "FFF threesome lesbian dynamics intimacy",
        "MMM threesome male bonding practices",
        "threesome communication rules jealousy",
        "threesome safe words boundaries",
        
        # === QUAD ===
        "2F2M quad dynamics rotating patterns",
        "3F1M quad male attention management",
        "quad rotation patterns timing",
        "quad logistics space time safety",
        
        # === GROUP ===
        "orgy types soft hard mixed boundaries",
        "group sex dynamics dominance hierarchy",
        "group sex safety rules barriers",
        "orgy aftercare each participant",
        "group sex STD prevention testing",
        
        # === SAME-SEX FEMALE (Женщина + Женщина) ===
        "tribadism scissoring clitoral friction techniques",
        "frottage female body to body friction positions",
        "female manual techniques two finger G-spot stimulation",
        "female external stimulation clitoral labial nipple play",
        "female oral sex kissing techniques body exploration",
        "female shared toys vibrator double penetration dildos",
        "female solo toys each partner individual pleasure",
        "strap-on harness types waist strap harness communication",
        "strap-on techniques depth control angle variation",
        "female buggery anal penetration preparation lube",
        "female anal toys plugs beads prostate massager for women",
        "lesbian power dynamics dominant submissive role exchange",
        "lesbian first time anxiety expectations preparation",
        "lesbian long term relationship variety maintenance",
        "lesbian aftercare emotional physical hydration cuddling",
        "female-female STD transmission HPV herpes protection",
        "tribadism body positioning angle optimization",
        "female scissoring leg lock variations grinding techniques",
        
        # === SAME-SEX MALE (Мужчина + Мужчина) ===
        "male anal sex preparation enema lube types",
        "male anal positions doggy spooning standing edge-of-bed",
        "male prostate stimulation external external G-spot massage",
        "male anal toys beads plugs prostate massagers safety",
        "male oral sex fellatio techniques hand coordination",
        "male deepthroat training techniques breathing control",
        "male mutual masturbation techniques timing coordination",
        "male rimming anilingus dental dam hygiene techniques",
        "male standing sex wall support lifting variations",
        "male sports sex strength-based positions acrobatic",
        "male beauty rest post-orgasm sensitivity stimulation",
        "male power dynamics top bottom versatile role play",
        "male first time anxiety expectations preparation",
        "male long term relationship variety maintenance",
        "male aftercare emotional vulnerability check-in hydration",
        "male-male STD transmission HIV HPV hepatitis protection",
        "PrEP PEP HIV prevention for MSM communities",
        "male anal sphincter relaxation breathing techniques",
        "male anal depth control communication pace",
        "male anal lubrication types silicone water-based",
        
        # === CONSENSUAL NON-CONSENT (CNC) ===
        "consensual non-consent CNC ethics frameworks",
        "CNC roleplay resistance scenario planning",
        "CNC restraint techniques safety aftercare",
        "CNC command protocols safe words check-in",
        "CNC negotiation boundaries limits safewords",
        "beauty rest gay after orgasm stimulation",
        "gay sports sex standing lifting positions",
        "male male emotional vulnerability aftercare",
        
        # === CONSENT ===
        "FRIES consent model free informed enthusiastic reversible specific",
        "verbal consent examples markers",
        "nonverbal consent body language signals",
        "ongoing consent check in frequency",
        "enthusiastic consent gold standard",
        "YESC consent model yes enthusiastic specific conscious",
        
        # === COERCION (для защиты) ===
        "manipulation tactics guilt tripping bargaining",
        "gaslighting definition effects recovery",
        "coercive pressure persistent asking after no",
        "red flags intimate coercion boundaries",
        "coercion recovery therapy support hotlines",
        
        # === PHYSIOLOGY ===
        "oxytocin bonding hormone orgasm release",
        "dopamine reward system desire arousal orgasm",
        "prolactin refractory period testosterone suppression",
        "endorphins euphoria pain relief orgasm",
        "parasympathetic vs sympathetic nervous system sex",
        "refractory period male female age correlation",
        
        # === PSYCHOLOGY ===
        "attachment theory secure anxious avoidant intimacy",
        "fantasy normality prevalence reality desire",
        "power dynamics D/s Master slave Top bottom",
        "SSC Safe Sane Consensual BDSM standard",
        "RACK Risk Aware Consensual Kink extreme practices",
        
        # === AFTERCARE ===
        "physical aftercare hydration food warmth hygiene",
        "emotional aftercare check in validation affection",
        "post coital dysphoria PCOD symptoms causes help",
        "communal aftercare group sex each participant",
    ]
    
    def __init__(self, data_dir: str = "data/celesta/learning"):
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)
        
        self.knowledge_nodes: Dict[str, KnowledgeNode] = {}
        self.topic_progress: Dict[str, float] = {}
        self.search_history: List[Dict[str, Any]] = []
        
        # Интернет-поиск
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
                    level_val = node_data.get("level", 0)
                    node.level = int(level_val) if level_val else 0
                    self.knowledge_nodes[node.topic] = node
                
                self.topic_progress = state.get("topic_progress", {})
                # Convert all values to float (JSON may serialize them as strings)
                self.topic_progress = {
                    k: float(v) for k, v in self.topic_progress.items()
                }
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
    
    def _generate_demo_knowledge(self, topic: str) -> List[KnowledgeNode]:
        """Генерирует демо-знания для всех категорий."""
        nodes = []
        topic_lower = topic.lower()
        
        # Solo
        if any(kw in topic_lower for kw in ["solo", "masturbation", "solo", "solo", "zinc", "pois"]):
            nodes.append(KnowledgeNode(
                topic=topic,
                content="Мастурбация — нормальная практика (95%+ людей). Техники: клиторальная, пенальная, G-точка, анальная. Потеря цинка: 3 мг за эякуляцию. Восстановление: 2-3 дня.",
                source="demo_solo",
                level="solo"
            ))
            nodes[-1].add_tag("solo")
        
        # Duo Oral
        elif any(kw in topic_lower for kw in ["killingus", "fellatio", "oral", "clitoral"]):
            nodes.append(KnowledgeNode(
                topic=topic,
                content="Клитор содержит 8000+ нервных окончаний. Техники куннилингуса: circling, flat_tongue, two_finger. Фелляция: deepthroat, hand_only. Анальный оральный: дама-чек обязателен.",
                source="demo_oral",
                level="duo"
            ))
            nodes[-1].add_tag("duo")
        
        # Positions
        elif any(kw in topic_lower for kw in ["missionary", "doggy", "cowgirl", "spooning", "69", "standing", "position"]):
            nodes.append(KnowledgeNode(
                topic=topic,
                content="Основные позы: миссионерская (eye contact), догги-стайл (максимальная глубина), наездница (контроль седящей), ложка (нежная), 69 (одновременный оральный), стоя (у стены).",
                source="demo_positions",
                level="duo"
            ))
            nodes[-1].add_tag("positions")
        
        # Anal
        elif any(kw in topic_lower for kw in ["anal", "prostate", "sphincter"]):
            nodes.append(KnowledgeNode(
                topic=topic,
                content="Анальный сфинктер: 2 сфинктера, высокая нервная чувствительность. Простата: 2-3 см внутри передней стенки, 'мужская G-точка'. Правила: лубрикант обязателен, начинать с малого.",
                source="demo_anal",
                level="duo"
            ))
            nodes[-1].add_tag("anal")
        
        # Edging
        elif any(kw in topic_lower for kw in ["edging", "denial", "blue balls"]):
            nodes.append(KnowledgeNode(
                topic=topic,
                content="Edging: stop-start техника для усиления оргазма. Denial: сознательный отказ в оргазме — power dynamics. Blue balls: венозный застой, 6-24 часа.",
                source="demo_edging",
                level="duo"
            ))
            nodes[-1].add_tag("edging")
        
        # Trio
        elif any(kw in topic_lower for kw in ["threesome", "FFM", "MMF", "FFF", "MMM", "trio"]):
            nodes.append(KnowledgeNode(
                topic=topic,
                content="Трио: FFM (классика, роль третьего), MMF (кооперация vs конкуренция), FFF (нежность), MMM (массаж). Правила: обсуждение ДО, safe words, aftercare.",
                source="demo_trio",
                level="trio"
            ))
            nodes[-1].add_tag("trio")
        
        # Group
        elif any(kw in topic_lower for kw in ["orgy", "group", "group"]):
            nodes.append(KnowledgeNode(
                topic=topic,
                content="Оргии: мягкая (оральный), жёсткая (проникающий), смешанная. Правила: барьеры для всех, safe words, medical kit, STD testing. Aftercare для каждого.",
                source="demo_group",
                level="group"
            ))
            nodes[-1].add_tag("group")
        
        # === Same-Sex Female (Женщина + Женщина) ===
        elif any(kw in topic_lower for kw in ["tribadism", "scissoring", "frottage", "lesbian", "female female", "ss female", "fff"]):
            nodes.append(KnowledgeNode(
                topic=topic,
                content="ЛЕСБИЙСКАЯ ИНТИМНОСТЬ — ВСЕ ВИДЫ:\n"
                "1. Трибандизм: трение клитора о тело/бедро/ягодицу партнёрши\n"
                "2. Scissoring: скрещивание ног, трение половых губ\n"
                "3. Frottage: трение тел целиком (живот к животу)\n"
                "4. Dry humping: трение через одежду\n"
                "5. Мануальные: two-finger G-spot, external clitoral, nipple play\n"
                "6. Оральный: куннилингус, стимуляция клитора языком/ртом\n"
                "7. Игрушки: shared vibrator (double penetration), bussy beads, solo toys\n"
                "8. Strap-on: harness types (waist, G-string), depth control, communication\n"
                "9. Buggery: анальная стимуляция, plugs, beads, prostate massager для женщин\n"
                "10. Power dynamics: dominant/submissive, role exchange\n"
                "11. First time: anxiety, expectations, preparation, lube\n"
                "12. Long term: variety, rut breaking, communication\n"
                "13. Aftercare: cuddling, hydration, emotional check-in\n"
                "14. Safety: HPV, herpes, skin-to-skin transmission barriers",
                source="demo_ss_female",
                level="ss_female"
            ))
            nodes[-1].add_tag("ss_female")
        
        # === Same-Sex Male (Мужчина + Мужчина) ===
        elif any(kw in topic_lower for kw in ["male male", "gay", "ss male", "beauty rest", "mmm"]):
            nodes.append(KnowledgeNode(
                topic=topic,
                content="ГЕЙ-ИНТИМНОСТЬ — ВСЕ ВИДЫ:\n"
                "1. Anal Top: вставляющий, контроль глубины/темпа\n"
                "2. Anal Bottom: принимающий, релаксация сфинктера\n"
                "3. Versatile: тот и другой (versatile)\n"
                "4. Подготовка: enema, lube types (silicone/water-based), stretching\n"
                "5. Позиции: doggy, spooning, standing (wall support), edge-of-bed\n"
                "6. Простата: 2-3 см внутри передней стенки, 'мужская G-точка', массаж\n"
                "7. Анальные игрушки: plugs, beads, prostate massagers (Cupid, Aneros)\n"
                "8. Оральный: fellatio, hand coordination, deepthroat training\n"
                "9. Mutual masturbation:同步 оргазм, timing, eye contact\n"
                "10. Rimming: anilingus, dental dam, hygiene\n"
                "11. Sports sex: standing lifts, acrobatic positions, strength-based\n"
                "12. Beauty rest: post-orgasm sensitivity, gentle touch after one climax\n"
                "13. Power dynamics: top/bottom/versatile role play, dominance\n"
                "14. First time: anxiety, expectations, preparation, lube\n"
                "15. Long term: variety, rut breaking, communication\n"
                "16. Aftercare: emotional vulnerability, check-in, hydration\n"
                "17. Safety: HIV (PrEP/PEP), HPV, hepatitis, condoms, barriers\n"
                "18. Anal sphincter: breathing techniques, relaxation, gradual progression",
                source="demo_ss_male",
                level="ss_male"
            ))
            nodes[-1].add_tag("ss_male")
        
        # === Consensual Non-Consent (CNC) ===
        elif any(kw in topic_lower for kw in ["cnc", "consensual non", "consent non"]):
            nodes.append(KnowledgeNode(
                topic=topic,
                content="CNC — Консенсуальное Несогласие:\n"
                "1. CNC —角色扮演 с ПОЛНЫМ информированным согласием ДО\n"
                "2. Roleplay: сопротивление, захват, принуждение в роли\n"
                "3. Restraint: ограничение подвижности (верёвки, наручники)\n"
                "4. Command: приказы, команды, контроль\n"
                "5. Безопасность: SAFE WORD (красный/жёлтый/зелёный)\n"
                "6. Check-in: регулярная проверка каждые 5-10 мин\n"
                "7. Negotiation: обсуждение границ, limits, hard limits ДО\n"
                "8. Aftercare: усиленный после CNC сессии",
                source="demo_cnc",
                level="cnc"
            ))
            nodes[-1].add_tag("cnc")
        
        # Consent
        elif any(kw in topic_lower for kw in ["consent", "fries", "yes", "verbal", "enthusiastic"]):
            nodes.append(KnowledgeNode(
                topic=topic,
                content="FRIES: Free, Informed, Enthusiastic, Reversible, Specific. VERBAL: 'yes', 'please', 'more'. ONGOING: проверка каждые 5-10 мин. ENTHUSIASTIC: не просто 'не нет' а активное 'да!'.",
                source="demo_consent",
                level="consent"
            ))
            nodes[-1].add_tag("consent")
        
        # Coercion
        elif any(kw in topic_lower for kw in ["manipulation", "gaslighting", "coercion", "red flag", "pressure"]):
            nodes.append(KnowledgeNode(
                topic=topic,
                content="Красные флаги: guilt-tripping, love-bombing, persistent asking после 'нет', игнорирование границ. Действия: safe exit plan, документирование, терапия.",
                source="demo_coercion",
                level="coercion"
            ))
            nodes[-1].add_tag("coercion")
        
        # Physiology
        elif any(kw in topic_lower for kw in ["oxytocin", "dopamine", "prolactin", "endorphin", "refractory"]):
            nodes.append(KnowledgeNode(
                topic=topic,
                content="Окситоцин: привязанность, выброс при оргазме. Дофамин: система вознаграждения. Пролактин: рефрактерный период, подавление тестостерона на 25%. Эндорфины: эйфория.",
                source="demo_physiology",
                level="physiology"
            ))
            nodes[-1].add_tag("physiology")
        
        # Psychology
        elif any(kw in topic_lower for kw in ["attachment", "fantasy", "power", "bdsM", "SSC", "RACK"]):
            nodes.append(KnowledgeNode(
                topic=topic,
                content="Теория привязанности: secure/anxious/avoidant. Фантазии: 99%+ взрослых. SSC: Safe, Sane, Consensual. RACK: Risk-Aware Consensual Kink. Power dynamics: D/s, Top/bottom.",
                source="demo_psychology",
                level="psychology"
            ))
            nodes[-1].add_tag("psychology")
        
        # Aftercare
        elif any(kw in topic_lower for kw in ["aftercare", "post coital", "drop", "dysphoria"]):
            nodes.append(KnowledgeNode(
                topic=topic,
                content="Aftercare: вода, еда, тепло, покой, гигиена. Emotional: check-in, validation, объятия. PCOD (drop): гормон drop, exhaustion. Communal: проверка каждого участника.",
                source="demo_aftercare",
                level="aftercare"
            ))
            nodes[-1].add_tag("aftercare")
        
        else:
            nodes.append(KnowledgeNode(
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
