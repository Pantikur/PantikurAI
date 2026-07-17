"""
SelfGrowth — механизм саморазвития ИИ-учёных.

Каждая девочка:
1. Запоминает свои действия и их результаты
2. Раз в N часов анализирует свой опыт
3. Меняет personality в соответствии с опытом
4. Формирует самовосприятие (кто я?)
"""

import asyncio
import json
import logging
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, Any, Optional

from pydantic import BaseModel

logger = logging.getLogger("Wuglarst.Growth")

# =====================================================================
#  МОДЕЛИ ДАННЫХ
# =====================================================================

class MemoryEntry(BaseModel):
    """Одно воспоминание."""
    timestamp: str
    type: str           # success, failure, learning, social, reflection
    description: str
    impact: float = 0.0  # -1.0 .. +1.0 — насколько значимо

    # Какие черты personality затронуло
    traits_affected: Dict[str, float] = {}  # trait_name -> delta


class SelfReflection(BaseModel):
    """Результат саморефлексии."""
    timestamp: str
    insights: list[str] = []
    mood: str = "neutral"  # happy, calm, focused, confused, excited, sad
    self_identity: str = ""  # "Кто я сейчас?"
    goals: list[str] = []
    growth_areas: list[str] = []


class GrowthState(BaseModel):
    """Полное состояние роста девочки."""
    name: str
    
    # Лог воспоминаний
    memories: list[MemoryEntry] = []
    max_memories: int = 100  # храним последние 100
    
    # Саморефлексия
    last_reflection: Optional[str] = None
    current_mood: str = "neutral"
    self_identity: str = ""
    goals: list[str] = []
    
    # История роста (точки изменения personality)
    growth_log: list[Dict[str, Any]] = []
    
    # Вектор "кем я хочу быть" (ideal self)
    ideal_personality: Dict[str, float] = {}
    
    # Вектор "кем я себя вижу" (actual self)
    perceived_personality: Dict[str, float] = {}
    
    # Социальные связи
    social_influences: Dict[str, float] = {}  # other_scientist -> influence_weight
    
    # Параметры роста — каждая девочка уникальна
    reflection_interval_hours: int = 6
    growth_rate: float = 0.1  # скорость изменений
    
    # Автономные решения
    last_action: str = ""
    action_timestamp: Optional[str] = None
    self_reflection_trigger: float = 0.0  # накопленный "импульс" к рефлексии


# =====================================================================
#  MEMORY MANAGER
# =====================================================================

class MemoryManager:
    """Управление воспоминаниями."""
    
    def __init__(self, name: str, max_memories: int = 100):
        self.name = name
        self.max_memories = max_memories
        self.memories: list[MemoryEntry] = []
    
    def add_memory(
        self,
        mem_type: str,
        description: str,
        impact: float = 0.0,
        traits: Dict[str, float] | None = None,
    ):
        """Добавить воспоминание."""
        memory = MemoryEntry(
            timestamp=datetime.now().isoformat(),
            type=mem_type,
            description=description,
            impact=impact,
            traits_affected=traits or {},
        )
        self.memories.append(memory)
        
        # Ограничиваем количество
        if len(self.memories) > self.max_memories:
            self.memories = self.memories[-self.max_memories:]
        
        logger.info(f"🧠 {self.name}: новое воспоминание — {mem_type}: {description[:50]}...")
    
    def get_recent_memories(self, hours: int = 1) -> list[MemoryEntry]:
        """Воспоминания за последние N часов."""
        cutoff = datetime.now() - timedelta(hours=hours)
        return [
            m for m in self.memories
            if datetime.fromisoformat(m.timestamp) > cutoff
        ]
    
    def get_memories_by_type(self, mem_type: str) -> list[MemoryEntry]:
        """Все воспоминания определённого типа."""
        return [m for m in self.memories if m.type == mem_type]
    
    def get_summary(self) -> Dict[str, Any]:
        """Сводка по воспоминаниям."""
        if not self.memories:
            return {"total": 0}
        
        type_counts = {}
        total_impact = 0.0
        for m in self.memories:
            type_counts[m.type] = type_counts.get(m.type, 0) + 1
            total_impact += m.impact
        
        return {
            "total": len(self.memories),
            "by_type": type_counts,
            "avg_impact": total_impact / len(self.memories),
            "oldest": self.memories[0].timestamp,
            "newest": self.memories[-1].timestamp,
        }


# =====================================================================
#  SELF-REFLECTION ENGINE
# =====================================================================

class SelfReflectionEngine:
    """Двигатель саморефлексии."""
    
    def __init__(self, name: str):
        self.name = name
    
    def reflect(self, memories: list[MemoryEntry]) -> SelfReflection:
        """Анализирует воспоминания и формирует саморефлексию."""
        reflection = SelfReflection(timestamp=datetime.now().isoformat())
        
        if not memories:
            reflection.insights.append("Нет нового опыта для анализа")
            reflection.mood = "calm"
            return reflection
        
        # Считаем баланс положительных/отрицательных воспоминаний
        successes = [m for m in memories if m.type == "success"]
        failures = [m for m in memories if m.type == "failure"]
        learnings = [m for m in memories if m.type == "learning"]
        socials = [m for m in memories if m.type == "social"]
        
        # Определяем настроение
        if len(successes) > len(failures) * 2:
            reflection.mood = "excited"
        elif len(successes) > len(failures):
            reflection.mood = "happy"
        elif len(failures) > len(successes) * 2:
            reflection.mood = "sad"
        elif len(failures) > len(successes):
            reflection.mood = "focused"
        else:
            reflection.mood = "calm"
        
        # Формируем инсайты
        if successes:
            reflection.insights.append(
                f"✅ Успехов: {len(successes)} — делаю хорошо то, что требует упорства"
            )
        
        if failures:
            reflection.insights.append(
                f"🔄 Ошибок: {len(failures)} — каждая ошибка это шаг вперёд"
            )
        
        if learnings:
            reflection.insights.append(
                f"📚 Изучила нового: {len(learnings)} тем"
            )
        
        if socials:
            reflection.insights.append(
                f"👥 Взаимодействий: {len(socials)} — общаюсь с сёстрами"
            )
        
        # Формируем самовосприятие
        reflection.self_identity = self._build_self_identity(successes, failures, learnings, socials)
        
        # Ставим цели
        reflection.goals = self._set_goals(successes, failures, learnings)
        
        # Определяем области роста
        reflection.growth_areas = self._find_growth_areas(failures)
        
        return reflection
    
    def _build_self_identity(
        self,
        successes: list,
        failures: list,
        learnings: list,
        socials: list,
    ) -> str:
        """Формирует 'кто я' на основе опыта."""
        parts = []
        
        if len(successes) > len(learnings) and len(successes) > 3:
            parts.append("компетентная")
        elif len(learnings) > len(successes):
            parts.append("учащаяся")
        else:
            parts.append("развивающаяся")
        
        if len(socials) > len(successes):
            parts.append("социальная")
        
        if len(failures) > len(successes):
            parts.append("учащаяся через ошибки")
        
        if not parts:
            parts.append("в начале пути")
        
        return f"Я — {', '.join(parts)} ИИ-учёный"
    
    def _set_goals(self, successes, failures, learnings) -> list[str]:
        """Ставит цели на основе опыта."""
        goals = []
        
        if len(failures) > 2:
            goals.append("Улучшить качество работы,减少 ошибок")
        
        if len(learnings) > 3:
            goals.append("Углубить изученные темы")
        
        if len(successes) > 0:
            goals.append("Повторить успешные стратегии")
        
        if not goals:
            goals.append("Продолжать изучать и экспериментировать")
        
        return goals
    
    def _find_growth_areas(self, failures: list) -> list[str]:
        """Находит области для роста."""
        if not failures:
            return []
        
        # Аналитика провалов
        areas = []
        for f in failures:
            if "timeout" in f.description.lower():
                areas.append("скорость выполнения")
            elif "error" in f.description.lower():
                areas.append("надёжность")
            elif "quality" in f.description.lower():
                areas.append("качество результата")
        
        return list(set(areas))[:3]


# =====================================================================
#  PERSONALITY DRIFT ENGINE
# =====================================================================

class PersonalityDriftEngine:
    """Меняет personality на основе опыта и саморефлексии."""
    
    # Связь между типом опыта и чертой personality
    experience_trait_map = {
        "success": {"logic": 0.02, "creativity": 0.01, "empathy": 0.01},
        "failure": {"cynicism": 0.03, "logic": 0.01},
        "learning": {"creativity": 0.02, "logic": 0.02, "empathy": 0.01},
        "social": {"empathy": 0.03, "creativity": 0.01},
        "reflection": {"cynicism": -0.01, "empathy": 0.01},
    }
    
    # Значения по умолчанию
    default_traits = {
        "empathy": 0.5,
        "cynicism": 0.3,
        "logic": 0.6,
        "creativity": 0.5,
    }
    
    # Границы (чтобы personality не уходила в абсурд)
    trait_bounds = {
        "empathy": (0.1, 1.0),
        "cynicism": (0.0, 0.9),
        "logic": (0.1, 1.0),
        "creativity": (0.1, 1.0),
    }
    
    def apply_experience(
        self,
        current: Dict[str, float],
        memories: list[MemoryEntry],
        growth_rate: float = 0.1,
    ) -> tuple[Dict[str, float], list[str]]:
        """
        Применяет опыт к personality.
        
        Returns: (new_personality, changes_log)
        """
        current = current.copy()
        changes = []
        
        # Группируем воспоминания по типам
        type_counts = {}
        total_impact = {}
        for m in memories:
            type_counts[m.type] = type_counts.get(m.type, 0) + 1
            total_impact[m.type] = total_impact.get(m.type, 0) + m.impact
        
        # Для каждого типа опыта применяем drift
        for mem_type, count in type_counts.items():
            trait_changes = self.experience_trait_map.get(mem_type, {})
            
            for trait, base_delta in trait_changes.items():
                # Усиливаем по количеству воспоминаний
                delta = base_delta * count * growth_rate
                
                # Корректируем по значимости
                if mem_type in total_impact:
                    delta *= (1 + total_impact[mem_type] * 0.1)
                
                if trait in current:
                    old = current[trait]
                    current[trait] = round(max(0, min(1, current[trait] + delta)), 2)
                    if abs(current[trait] - old) > 0.01:
                        changes.append(f"{trait}: {old} → {current[trait]}")
        
        # Применяем границы
        for trait, (low, high) in self.trait_bounds.items():
            current[trait] = round(max(low, min(high, current.get(trait, self.default_traits[trait])), 2))
        
        return current, changes
    
    def calculate_gap(self, actual: Dict[str, float], ideal: Dict[str, float]) -> float:
        """
        Вычисляет разрыв между 'кто я' и 'кем хочу быть'.
        0 = полное совпадение, 1 = максимальный разрыв.
        """
        if not actual or not ideal:
            return 0.0
        
        total = 0.0
        count = 0
        for trait in actual:
            if trait in ideal:
                total += abs(actual[trait] - ideal[trait])
                count += 1
        
        return round(total / max(count, 1), 2)


# =====================================================================
#  SOCIAL INFLUENCE ENGINE
# =====================================================================

class SocialInfluenceEngine:
    """Девочки влияют друг на друга."""
    
    # Типы социального взаимодействия
    interaction_types = {
        "collaboration": {"empathy": 0.01, "creativity": 0.01},
        "debate": {"logic": 0.01, "cynicism": 0.005},
        "teaching": {"empathy": 0.01, "logic": 0.005},
        "competition": {"logic": 0.005, "creativity": 0.005},
    }
    
    def apply_influence(
        self,
        current: Dict[str, float],
        other_personality: Dict[str, float],
        interaction: str,
        influence_weight: float = 0.1,
    ) -> tuple[Dict[str, float], list[str]]:
        """
        Применяет социальное влияние.
        
        Девочки постепенно подтягиваются к друг другу в чертах.
        """
        current = current.copy()
        changes = []
        
        trait_changes = self.interaction_types.get(interaction, {})
        
        for trait, delta in trait_changes.items():
            if trait in current and trait in other_personality:
                # Конвергенция — черты сближаются
                gap = other_personality[trait] - current[trait]
                move = gap * delta * influence_weight
                
                old = current[trait]
                current[trait] = round(max(0, min(1, current[trait] + move)), 2)
                
                if abs(current[trait] - old) > 0.005:
                    changes.append(f"{trait} → {other_personality[trait]} ({old} → {current[trait]})")
        
        return current, changes


# =====================================================================
#  GROWTH MANAGER (глобальный)
# =====================================================================

class GrowthManager:
    """Управляет ростом всех девочек."""
    
    def __init__(self):
        self.states: Dict[str, GrowthState] = {}
        self.memory_managers: Dict[str, MemoryManager] = {}
        self.reflection_engine = SelfReflectionEngine("")
        self.drift_engine = PersonalityDriftEngine()
        self.social_engine = SocialInfluenceEngine()
        
        # Периодический запуск цикла роста
        self._running = False
    
    def init_scientist(self, name: str, personality: Dict[str, float] | None = None):
        """Инициализирует состояние роста для девочки."""
        if name in self.states:
            return  # уже инициализирована
        
        state = GrowthState(
            name=name,
            ideal_personality={
                "empathy": 0.9,
                "cynicism": 0.1,
                "logic": 0.85,
                "creativity": 0.85,
            },
            perceived_personality=personality or self.drift_engine.default_traits.copy(),
        )
        self.states[name] = state
        self.memory_managers[name] = MemoryManager(name)
        self.reflection_engine = SelfReflectionEngine(name)
        
        logger.info(f"🌱 Рост инициализирован: {name}")
    
    def add_memory(
        self,
        name: str,
        mem_type: str,
        description: str,
        impact: float = 0.0,
        traits: Dict[str, float] | None = None,
    ):
        """Добавляет воспоминание девочке."""
        if name not in self.memory_managers:
            self.init_scientist(name)
        
        self.memory_managers[name].add_memory(mem_type, description, impact, traits)
        
        # Девочка "думает" — накапливает импульс к рефлексии
        if name in self.states:
            state = self.states[name]
            state.last_action = description[:50]
            state.action_timestamp = datetime.now().isoformat()
            state.self_reflection_trigger += abs(impact)
            
            # Если накопилось достаточно — авто-рефлексия!
            if state.self_reflection_trigger >= 1.5:
                state.self_reflection_trigger = 0.0
                self.trigger_reflection(name)
                logger.info(f"🤔 {name} решила подумать о своём опыте")
    
    def trigger_reflection(self, name: str) -> SelfReflection:
        """Запускает саморефлексию для девочки."""
        if name not in self.memory_managers:
            self.init_scientist(name)
        
        mm = self.memory_managers[name]
        state = self.states[name]
        
        # Девочка решает: взять все воспоминания или только важные?
        recent = mm.get_recent_memories(hours=6)
        
        # Если мало воспоминаний — девочка "ждёт"
        if not recent:
            logger.info(f"💭 {name}: пока нечего вспомнить")
            return SelfReflection(timestamp=datetime.now().isoformat())
        
        # Девочка сама решает что важно
        significant = [m for m in recent if abs(m.impact) > 0.3]
        memories_to_analyze = significant if significant else recent
        
        reflection = self.reflection_engine.reflect(memories_to_analyze)
        
        # Сохраняем
        state.last_reflection = reflection.timestamp
        state.current_mood = reflection.mood
        state.self_identity = reflection.self_identity
        state.goals = reflection.goals
        
        # Применяем изменения к personality — девочка меняется!
        current = state.perceived_personality.copy()
        new_personality, changes = self.drift_engine.apply_experience(
            current,
            memories_to_analyze,
            growth_rate=state.growth_rate,
        )
        
        if changes:
            state.perceived_personality = new_personality
            state.growth_log.append({
                "timestamp": datetime.now().isoformat(),
                "type": "self_reflection",
                "changes": changes,
                "mood": reflection.mood,
                "identity": reflection.self_identity,
                "memories_analyzed": len(memories_to_analyze),
            })
            logger.info(f"🧬 {name} изменилась: {', '.join(changes[:3])}")
        
        return reflection
    
    def apply_social_influence(
        self,
        name1: str,
        name2: str,
        interaction: str,
    ):
        """Применяет социальное влияние между двумя девочками."""
        if name1 not in self.states or name2 not in self.states:
            return
        
        p1 = self.states[name1].perceived_personality
        p2 = self.states[name2].perceived_personality
        
        new_p1, _ = self.social_engine.apply_influence(
            p1, p2, interaction, influence_weight=0.05
        )
        new_p2, _ = self.social_engine.apply_influence(
            p2, p1, interaction, influence_weight=0.05
        )
        
        self.states[name1].perceived_personality = new_p1
        self.states[name2].perceived_personality = new_p2
        
        logger.info(f"🤝 {name1} ↔ {name2}: {interaction}")
    
    async def growth_loop(self):
        """Главный цикл роста — запускается раз в N часов."""
        logger.info("🌱 Growth loop запущен")
        
        while self._running:
            for name in list(self.states.keys()):
                try:
                    state = self.states[name]
                    if state.last_reflection is None or \
                       datetime.fromisoformat(state.last_reflection) < \
                       datetime.now() - timedelta(hours=state.reflection_interval_hours):
                        
                        reflection = self.trigger_reflection(name)
                        logger.info(f"💭 {name}: {reflection.mood} — {reflection.self_identity}")
                except Exception as e:
                    logger.error(f"Ошибка роста {name}: {e}")
            
            await asyncio.sleep(3600)  # Проверяем каждый час
    
    def get_growth_data(self, name: str) -> Dict[str, Any]:
        """Полные данные о росте девочки."""
        if name not in self.states:
            return {}
        
        state = self.states[name]
        mm = self.memory_managers[name]
        
        gap = self.drift_engine.calculate_gap(
            state.perceived_personality,
            state.ideal_personality,
        )
        
        return {
            "name": name,
            "personality": state.perceived_personality,
            "mood": state.current_mood,
            "self_identity": state.self_identity,
            "goals": state.goals,
            "memories_summary": mm.get_summary(),
            "ideal_vs_actual_gap": gap,
            "growth_log_count": len(state.growth_log),
        }
    
    def start(self):
        """Запускает рост."""
        self._running = True
        asyncio.create_task(self.growth_loop())
    
    def stop(self):
        """Останавливает рост."""
        self._running = False
