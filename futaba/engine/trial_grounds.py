"""
Полигон испытаний Футаба — генерация миров для тестирования версий правления.

Футаба создаёт виртуальные миры и применяет к ним разные версии
своей Конституции (законов правления), чтобы оценить, какие параметры
дают наилучшие результаты (стабильность, благополучие, соблюдение законов).

Это позволяет Футабе безопасно тестировать гипотезы об улучшениях
перед предложением их для реальной Конституции.
"""

from __future__ import annotations
import random
from dataclasses import dataclass
from typing import Any, Optional

from futaba.engine.config import FutabaConfig
from futaba.engine.models import (
    EventKind, Faction, ReignVersion, SimulationResult, World
)


@dataclass
class Event:
    """Событие в симуляции мира."""
    kind: EventKind
    name: str
    description: str
    effects: dict[str, float]  # влияние на метрики мира


class TrialGrounds:
    """
    Полигон испытаний Футаба.
    
    Генерирует миры, применяет версии правления, симулирует ход времени
    и оценивает результаты.
    """
    
    def __init__(self, config: FutabaConfig):
        self.config = config
        self.worlds_generated = 0
        self.simulations_run = 0
        
        # Библиотека событий для симуляции
        self._event_library = self._build_event_library()
    
    # ================================================================
    #  ГЕНЕРАЦИЯ МИРА
    # ================================================================
    
    def generate_world(self, seed: Optional[int] = None) -> World:
        """
        Сгенерировать новый мир для испытаний.
        
        Параметры мира варьируются, чтобы тестировать устойчивость
        версий правления в разных условиях.
        """
        if seed is not None:
            random.seed(seed)
        
        self.worlds_generated += 1
        
        # Генерация параметров
        population = random.randint(10_000, 1_000_000)
        resources = random.uniform(20.0, 80.0)
        stability = random.uniform(30.0, 80.0)
        wellbeing = random.uniform(30.0, 70.0)
        innovation = random.uniform(20.0, 60.0)
        law_compliance = random.uniform(40.0, 90.0)
        
        # Генерация фракций
        factions = self._generate_factions()
        
        # Генерация угроз
        threats = self._generate_threats()
        
        # Название
        names = [
            "Аэрия", "Новая Земля", "Омега-7", "Терра Инкогнита",
            "Эхо", "Квантум", "Солярис", "Вектор", "Нексус", "Горизонт"
        ]
        name = f"{random.choice(names)}-{self.worlds_generated}"
        
        world = World(
            name=name,
            population=population,
            resources=resources,
            stability=stability,
            wellbeing=wellbeing,
            innovation=innovation,
            law_compliance=law_compliance,
            factions=factions,
            threats=threats,
            epoch=0,
            alive=True,
        )
        
        return world
    
    def _generate_factions(self) -> list[Faction]:
        """Сгенерировать фракции мира."""
        faction_types = [
            ("Правящий совет", "loyal", 0.7, 0.4),
            ("Торговая гильдия", "neutral", 0.5, 0.3),
            ("Научный орден", "neutral", 0.4, 0.2),
            ("Рабочий союз", "opposition", 0.3, 0.3),
            ("Религиозный культ", "neutral", 0.4, 0.2),
            ("Военная клика", "loyal", 0.6, 0.5),
            ("Подполье", "opposition", 0.2, 0.2),
        ]
        
        factions = []
        num_factions = random.randint(3, 6)
        
        for _ in range(num_factions):
            ft = random.choice(faction_types)
            factions.append(Faction(
                name=ft[0],
                alignment=ft[1],
                loyalty=ft[2] + random.uniform(-0.15, 0.15),
                power=ft[3] + random.uniform(-0.1, 0.1),
            ))
        
        # Нормализовать loyalty и power
        for f in factions:
            f.loyalty = max(0.0, min(1.0, f.loyalty))
            f.power = max(0.0, min(1.0, f.power))
        
        return factions
    
    def _generate_threats(self) -> list[str]:
        """Сгенерировать угрозы мира."""
        threat_pool = [
            "Экономический кризис",
            "Эпидемия",
            "Внешняя агрессия",
            "Экологическая катастрофа",
            "Технологическая сингулярность",
            "Ресурсное истощение",
            "Социальный раскол",
            "Кибератаки",
            "Климатические изменения",
            "ИИ-бунт",
        ]
        
        num_threats = random.randint(0, 3)
        return random.sample(threat_pool, num_threats)
    
    # ================================================================
    #  ГЕНЕРАЦИЯ ВЕРСИЙ ПРАВЛЕНИЯ
    # ================================================================
    
    def generate_reign_versions(self, count: int) -> list[ReignVersion]:
        """
        Сгенерировать несколько версий правления для тестирования.
        
        Каждая версия — это вариация параметров Конституции Футаба.
        """
        versions = []
        
        # Базовая версия (текущая Конституция)
        versions.append(ReignVersion(
            name="Базовая (v1.0.0)",
            law_strictness=0.7,
            freedom_level=0.5,
            safety_priority=0.95,
            innovation_support=0.4,
            transparency=0.8,
            description="Текущая Конституция Футаба",
        ))
        
        # Генерируем вариации
        archetypes = [
            ("Строгая", 0.9, 0.3, 0.98, 0.3, 0.7, "Жёсткое соблюдение законов"),
            ("Либеральная", 0.4, 0.8, 0.8, 0.7, 0.9, "Максимальная свобода"),
            ("Технократия", 0.6, 0.5, 0.85, 0.9, 0.7, "Приоритет инноваций"),
            ("Патернализм", 0.7, 0.3, 0.99, 0.3, 0.6, "Максимальная безопасность"),
            ("Баланс", 0.6, 0.6, 0.9, 0.5, 0.85, "Сбалансированный подход"),
            ("Авторитарная", 0.95, 0.2, 0.9, 0.2, 0.4, "Жёсткий контроль"),
            ("Анархия", 0.1, 0.95, 0.5, 0.6, 0.5, "Минимум регулирования"),
        ]
        
        for _ in range(count - 1):
            arch = random.choice(archetypes)
            # Добавляем небольшой разброс
            versions.append(ReignVersion(
                name=f"{arch[0]} v{random.randint(1, 9)}.{random.randint(0, 9)}",
                law_strictness=max(0.0, min(1.0, arch[1] + random.uniform(-0.1, 0.1))),
                freedom_level=max(0.0, min(1.0, arch[2] + random.uniform(-0.1, 0.1))),
                safety_priority=max(0.0, min(1.0, arch[3] + random.uniform(-0.05, 0.05))),
                innovation_support=max(0.0, min(1.0, arch[4] + random.uniform(-0.1, 0.1))),
                transparency=max(0.0, min(1.0, arch[5] + random.uniform(-0.1, 0.1))),
                description=arch[6],
            ))
        
        return versions
    
    # ================================================================
    #  СИМУЛЯЦИЯ
    # ================================================================
    
    def simulate_reign(
        self,
        world: World,
        reign: ReignVersion,
        max_epochs: int = 20
    ) -> SimulationResult:
        """
        Симулировать правление версии на мире.
        
        Возвращает результат с метриками и score.
        """
        self.simulations_run += 1
        
        # Локальная копия мира для симуляции
        sim_world = World(
            name=world.name,
            population=world.population,
            resources=world.resources,
            stability=world.stability,
            wellbeing=world.wellbeing,
            innovation=world.innovation,
            law_compliance=world.law_compliance,
            factions=[Faction(f.name, f.loyalty, f.power, f.alignment) for f in world.factions],
            threats=world.threats.copy(),
            epoch=0,
            alive=True,
        )
        
        events_count = 0
        
        # Цикл симуляции по эпохам
        for epoch in range(max_epochs):
            if not sim_world.alive:
                break
            
            sim_world.epoch = epoch + 1
            
            # Применить эффекты правления
            self._apply_reign_effects(sim_world, reign)
            
            # Случайное событие
            if random.random() < 0.4:  # 40% шанс события за эпоху
                event = self._generate_event(reign)
                self._apply_event(sim_world, event)
                events_count += 1
                sim_world.event_log.append(f"Эпоха {epoch+1}: {event.name}")
            
            # Обновить лояльность фракций
            self._update_factions(sim_world, reign)
            
            # Проверка на крах
            collapse = self._check_collapse(sim_world, reign)
            if collapse:
                sim_world.alive = False
                sim_world.collapse_reason = collapse
                break
        
        # Финальные метрики
        final_metrics = {
            "stability": sim_world.stability,
            "wellbeing": sim_world.wellbeing,
            "innovation": sim_world.innovation,
            "law_compliance": sim_world.law_compliance,
            "resources": sim_world.resources,
            "avg_faction_loyalty": sum(f.loyalty for f in sim_world.factions) / len(sim_world.factions) if sim_world.factions else 0,
        }
        
        # Расчёт score
        score = self._calculate_score(final_metrics, sim_world.epoch, sim_world.alive)
        
        return SimulationResult(
            reign=reign,
            world=sim_world,
            epochs_survived=sim_world.epoch,
            collapsed=not sim_world.alive,
            collapse_reason=sim_world.collapse_reason,
            final_metrics=final_metrics,
            score=score,
            events_count=events_count,
        )
    
    def _apply_reign_effects(self, world: World, reign: ReignVersion):
        """Применить эффекты версии правления на мир."""
        # Строгость законов влияет на compliance и innovation
        world.law_compliance += (reign.law_strictness - 0.5) * 5
        world.innovation += (reign.innovation_support - 0.5) * 3
        world.innovation -= (reign.law_strictness - 0.5) * 2  # строгость душит инновации
        
        # Свобода влияет на wellbeing и stability
        world.wellbeing += (reign.freedom_level - 0.5) * 4
        world.stability -= abs(reign.freedom_level - 0.5) * 2  # отклонение от баланса destabilizes
        
        # Безопасность влияет на stability и wellbeing
        world.stability += (reign.safety_priority - 0.5) * 3
        world.wellbeing += (reign.safety_priority - 0.5) * 2
        
        # Прозрачность влияет на лояльность фракций
        for faction in world.factions:
            faction.loyalty += (reign.transparency - 0.5) * 0.05
        
        # Нормализация
        self._normalize_world(world)
    
    def _apply_event(self, world: World, event: Event):
        """Применить событие к миру."""
        for metric, delta in event.effects.items():
            if hasattr(world, metric):
                current = getattr(world, metric)
                setattr(world, metric, current + delta)
        
        self._normalize_world(world)
    
    def _update_factions(self, world: World, reign: ReignVersion):
        """Обновить лояльность фракций."""
        for faction in world.factions:
            # Базовое изменение
            if faction.alignment == "loyal":
                faction.loyalty += 0.02
            elif faction.alignment == "opposition":
                faction.loyalty -= 0.01
            
            # Влияние правления
            faction.loyalty += (reign.transparency - 0.5) * 0.02
            faction.loyalty -= (reign.law_strictness - 0.5) * 0.01  # строгость не нравится opposition
            
            # Ограничения
            faction.loyalty = max(0.0, min(1.0, faction.loyalty))
    
    def _check_collapse(self, world: World, reign: ReignVersion) -> Optional[str]:
        """Проверить, не произошёл ли крах правления."""
        if world.stability <= 0:
            return "Потеря стабильности (бунт/анархия)"
        
        if world.wellbeing <= 0:
            return "Критическое падение благополучия (голод/болезни)"
        
        if world.resources <= 0:
            return "Истощение ресурсов"
        
        # Проверка фракций
        opposition_power = sum(f.power for f in world.factions if f.alignment == "opposition")
        loyal_power = sum(f.power for f in world.factions if f.alignment == "loyal")
        if opposition_power > loyal_power * 2:
            return "Переворот оппозиции"
        
        return None
    
    def _normalize_world(self, world: World):
        """Нормализовать метрики мира в допустимые диапазоны."""
        world.stability = max(0.0, min(100.0, world.stability))
        world.wellbeing = max(0.0, min(100.0, world.wellbeing))
        world.innovation = max(0.0, min(100.0, world.innovation))
        world.law_compliance = max(0.0, min(100.0, world.law_compliance))
        world.resources = max(0.0, min(100.0, world.resources))
    
    def _calculate_score(
        self,
        metrics: dict[str, float],
        epochs: int,
        alive: bool
    ) -> float:
        """
        Рассчитать итоговый score правления.
        
        Score учитывает:
          - Выжившие эпохи
          - Финальные метрики
          - Бонус за выживание
        """
        # Базовый score из метрик (взвешенная сумма)
        base_score = (
            metrics["stability"] * 0.25 +
            metrics["wellbeing"] * 0.25 +
            metrics["law_compliance"] * 0.20 +
            metrics["innovation"] * 0.15 +
            metrics["resources"] * 0.15
        )
        
        # Бонус за эпохи (до 20%)
        epoch_bonus = min(20.0, epochs * 1.0)
        
        # Бонус за выживание (50%)
        survival_bonus = 50.0 if alive else 0.0
        
        # Итог (макс ~150)
        total = base_score * 0.5 + epoch_bonus + survival_bonus
        
        return total
    
    # ================================================================
    #  БИБЛИОТЕКА СОБЫТИЙ
    # ================================================================
    
    def _build_event_library(self) -> list[Event]:
        """Создать библиотеку возможных событий."""
        return [
            Event(
                kind=EventKind.CRISIS,
                name="Экономический кризис",
                description="Резкий спад экономики",
                effects={"resources": -15, "wellbeing": -10, "stability": -8}
            ),
            Event(
                kind=EventKind.CRISIS,
                name="Эпидемия",
                description="Вспышка болезни",
                effects={"wellbeing": -20, "population": -5000, "stability": -5}
            ),
            Event(
                kind=EventKind.BOOM,
                name="Технологический прорыв",
                description="Важное изобретение",
                effects={"innovation": +15, "resources": +5, "wellbeing": +5}
            ),
            Event(
                kind=EventKind.UNREST,
                name="Массовые протесты",
                description="Народные волнения",
                effects={"stability": -15, "law_compliance": -10}
            ),
            Event(
                kind=EventKind.DISCOVERY,
                name="Новые месторождения",
                description="Обнаружены ресурсы",
                effects={"resources": +20, "wellbeing": +5}
            ),
            Event(
                kind=EventKind.SCANDAL,
                name="Коррупционный скандал",
                description="Разоблачения в правительстве",
                effects={"law_compliance": -15, "stability": -10}
            ),
            Event(
                kind=EventKind.STABILITY,
                name="Период стабильности",
                description="Спокойное время",
                effects={"stability": +5, "wellbeing": +5}
            ),
        ]
    
    def _generate_event(self, reign: ReignVersion) -> Event:
        """Сгенерировать случайное событие с учётом правления."""
        base_events = self._event_library.copy()
        
        # Строгое правление снижает шанс кризисов, но повышает шанс протестов
        if reign.law_strictness > 0.8:
            base_events = [e for e in base_events if e.kind != EventKind.CRISIS]
            base_events.append(Event(
                kind=EventKind.UNREST,
                name="Подавление инакомыслия",
                description="Жёсткие меры контроля",
                effects={"stability": +3, "wellbeing": -5, "law_compliance": +5}
            ))
        
        # Высокая свобода повышает шанс скандалов
        if reign.freedom_level > 0.7:
            base_events.append(Event(
                kind=EventKind.SCANDAL,
                name="Скандал в СМИ",
                description="Свободная пресса раскрыла нарушения",
                effects={"law_compliance": -5, "transparency": +10}
            ))
        
        return random.choice(base_events)
    
    # ================================================================
    #  ЗАПУСК ПАКЕТА ИСПЫТАНИЙ
    # ================================================================
    
    def run_batch(self) -> list[SimulationResult]:
        """
        Запустить пакет испытаний.
        
        Генерирует несколько миров, для каждого тестирует несколько
        версий правления, возвращает все результаты.
        """
        results = []
        
        num_worlds = self.config.trial_worlds_per_batch
        num_versions = self.config.trial_versions_to_test
        epochs = self.config.trial_epochs_per_world
        
        # Сгенерировать миры
        worlds = [self.generate_world() for _ in range(num_worlds)]
        
        # Сгенерировать версии правления
        versions = self.generate_reign_versions(num_versions)
        
        # Запустить симуляции
        for world in worlds:
            for version in versions:
                result = self.simulate_reign(world, version, max_epochs=epochs)
                results.append(result)
        
        return results
    
    def compare_versions(
        self,
        results: list[SimulationResult]
    ) -> dict[str, Any]:
        """
        Сравнить версии правления по результатам испытаний.
        
        Возвращает рейтинг версий и рекомендации.
        """
        # Группировка по версиям
        by_version: dict[str, list[SimulationResult]] = {}
        for r in results:
            name = r.reign.name
            if name not in by_version:
                by_version[name] = []
            by_version[name].append(r)
        
        # Агрегация метрик
        rankings = []
        for name, runs in by_version.items():
            avg_score = sum(r.score for r in runs) / len(runs)
            avg_epochs = sum(r.epochs_survived for r in runs) / len(runs)
            survival_rate = sum(1 for r in runs if not r.collapsed) / len(runs)
            
            rankings.append({
                "name": name,
                "avg_score": avg_score,
                "avg_epochs": avg_epochs,
                "survival_rate": survival_rate,
                "runs": len(runs),
            })
        
        # Сортировка по score
        rankings.sort(key=lambda x: x["avg_score"], reverse=True)
        
        return {
            "rankings": rankings,
            "best_version": rankings[0]["name"] if rankings else None,
            "total_simulations": len(results),
        }
