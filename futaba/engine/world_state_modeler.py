"""
Модуль моделирования мировых состояний Футабы.

Реализует:
  - Генерацию жанров и биомов мира
  - Проектирование идеального государства для всех сословий
  - Инверсию правил (от 1 до 100%)
  - Симуляцию последствий для каждого сословия
  - Анализ устойчивости государственных систем
  - Сохранение результатов моделирования
"""

from __future__ import annotations
import json
import logging
import random
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple
from itertools import combinations


class FutabaWorldStateModeler:
    """
    Модуль моделирования мировых состояний — симуляция государств с инверсией правил.
    """

    def __init__(self, config: Any):
        self.config = config
        self.logger = logging.getLogger("FutabaWorldStateModeler")
        
        # Кэш моделирования
        self.simulation_cache: Dict[str, str] = {}
        self.cache_file = Path("futaba/engine/state/world_simulation_cache.json")
        
        # Результаты моделирования
        self.simulation_results: List[Dict[str, Any]] = []
        self.results_file = Path("futaba/engine/state/world_simulation_results.json")
        
        # Загружаем данные
        self._load_cache()
        self._load_results()

    def _load_cache(self):
        """Загружает кэш моделирования."""
        if self.cache_file.exists():
            try:
                with open(self.cache_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    self.simulation_cache = data.get("cache", {})
                    self.logger.info(f"Загружен кэш моделирования: {len(self.simulation_cache)} записей")
            except Exception as e:
                self.logger.warning(f"Ошибка загрузки кэша: {e}")
                self.simulation_cache = {}

    def _save_cache(self):
        """Сохраняет кэш моделирования."""
        try:
            self.cache_file.parent.mkdir(parents=True, exist_ok=True)
            with open(self.cache_file, "w", encoding="utf-8") as f:
                json.dump({"cache": self.simulation_cache, "updated": datetime.now().isoformat()},
                         f, ensure_ascii=False, indent=2)
            self.logger.debug("Кэш моделирования сохранён")
        except Exception as e:
            self.logger.error(f"Ошибка сохранения кэша: {e}")

    def _load_results(self):
        """Загружает результаты моделирования."""
        if self.results_file.exists():
            try:
                with open(self.results_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    self.simulation_results = data.get("results", [])
                    self.logger.info(f"Загружены результаты: {len(self.simulation_results)} симуляций")
            except Exception as e:
                self.logger.warning(f"Ошибка загрузки результатов: {e}")
                self.simulation_results = []

    def _save_results(self):
        """Сохраняет результаты моделирования."""
        try:
            self.results_file.parent.mkdir(parents=True, exist_ok=True)
            with open(self.results_file, "w", encoding="utf-8") as f:
                json.dump({
                    "results": self.simulation_results,
                    "updated": datetime.now().isoformat(),
                    "total_simulations": len(self.simulation_results)
                }, f, ensure_ascii=False, indent=2)
            self.logger.info(f"Результаты сохранены: {len(self.simulation_results)} симуляций")
        except Exception as e:
            self.logger.error(f"Ошибка сохранения результатов: {e}")

    # ================================================================
    #  ЖАНРЫ МИРА
    # ================================================================

    def get_all_world_genres(self) -> List[Dict[str, Any]]:
        """Возвращает все жанры миров."""
        cache_key = "world_genres"
        if cache_key in self.simulation_cache:
            try:
                return json.loads(self.simulation_cache[cache_key])
            except:
                pass
        
        genres = [
            {
                "id": "fantasy",
                "name": "Фэнтези",
                "description": "Магия, мифические существа, средневековый уровень технологий",
                "features": ["магия", "мечи", "драконы", "эльфы", "боги"],
                "technology_level": "medieval"
            },
            {
                "id": "scifi",
                "name": "Научная фантастика",
                "description": "Высокие технологии, космос, ИИ, футуризм",
                "features": ["космические корабли", "ИИ", "лазеры", "кибернетика", "колонии"],
                "technology_level": "advanced"
            },
            {
                "id": "cyberpunk",
                "name": "Киберпанк",
                "description": "Высокие технологии, низкий уровень жизни, корпорации",
                "features": ["киберимпланты", "мегакорпорации", "хакеры", "неоновые города"],
                "technology_level": "high_tech"
            },
            {
                "id": "steampunk",
                "name": "Стимпанк",
                "description": "Паровые технологии, викторианская эпоха, механика",
                "features": ["паровые машины", "механизмы", "дирижабли", "викторианский стиль"],
                "technology_level": "industrial"
            },
            {
                "id": "postapoc",
                "name": "Постапокалипсис",
                "description": "Мир после катастрофы, выживание, руины цивилизации",
                "features": ["радиация", "мутанты", "бандиты", "убежища", "ресурсы"],
                "technology_level": "ruined"
            },
            {
                "id": "historical",
                "name": "Исторический",
                "description": "Реальные исторические эпохи",
                "features": ["рыцари", "замки", "войны", "империи", "революции"],
                "technology_level": "historical"
            },
            {
                "id": "dystopia",
                "name": "Антиутопия",
                "description": "Тоталитарное общество, контроль, подавление",
                "features": ["слежка", "пропаганда", "полиция", "бунты", "цензура"],
                "technology_level": "modern_or_advanced"
            },
            {
                "id": "utopia",
                "name": "Утопия",
                "description": "Идеальное общество, гармония, процветание",
                "features": ["равенство", "изобилие", "мир", "наука", "искусство"],
                "technology_level": "advanced"
            },
            {
                "id": "magic_school",
                "name": "Магическая академия",
                "description": "Школы магии, обучение волшебников",
                "features": ["заклинания", "ученики", "профессора", "артефакты"],
                "technology_level": "magical"
            },
            {
                "id": "space_opera",
                "name": "Космическая опера",
                "description": "Галактические империи, космические войны",
                "features": ["звёздные флоты", "инопланетяне", "галактики", "войны"],
                "technology_level": "space_age"
            }
        ]
        
        self.simulation_cache[cache_key] = json.dumps(genres, ensure_ascii=False)
        self._save_cache()
        
        return genres

    # ================================================================
    #  БИОМЫ И ТИПЫ ГОСУДАРСТВ
    # ================================================================

    def get_all_state_biomes(self) -> List[Dict[str, Any]]:
        """Возвращает все биомы и типы государств."""
        cache_key = "state_biomes"
        if cache_key in self.simulation_cache:
            try:
                return json.loads(self.simulation_cache[cache_key])
            except:
                pass
        
        biomes = [
            {
                "id": "family",
                "name": "Семья",
                "scale": "micro",
                "population": "5-50",
                "description": "Минимальная ячейка общества",
                "governance": "родители/старейшины"
            },
            {
                "id": "clan",
                "name": "Клан/Род",
                "scale": "micro",
                "population": "50-500",
                "description": "Объединение семей по кровному родству",
                "governance": "глава клана/совет старейшин"
            },
            {
                "id": "tribe",
                "name": "Племя",
                "scale": "small",
                "population": "500-5000",
                "description": "Объединение кланов",
                "governance": "вождь/совет вождей"
            },
            {
                "id": "village",
                "name": "Поселение/Деревня",
                "scale": "small",
                "population": "100-2000",
                "description": "Сельское поселение",
                "governance": "староста/совет"
            },
            {
                "id": "town",
                "name": "Город",
                "scale": "medium",
                "population": "2000-100000",
                "description": "Крупное поселение",
                "governance": "мэр/городской совет"
            },
            {
                "id": "city_state",
                "name": "Город-государство",
                "scale": "medium",
                "population": "50000-500000",
                "description": "Независимый город с территорией",
                "governance": "правитель/сенат"
            },
            {
                "id": "principality",
                "name": "Княжество",
                "scale": "medium",
                "population": "100000-1000000",
                "description": "Владение князя",
                "governance": "князь/феодалы"
            },
            {
                "id": "kingdom",
                "name": "Королевство",
                "scale": "large",
                "population": "1000000-10000000",
                "description": "Государство во главе с королём",
                "governance": "король/парламент"
            },
            {
                "id": "empire",
                "name": "Империя",
                "scale": "huge",
                "population": "10000000+",
                "description": "Крупное государство с колониями",
                "governance": "император/сенат"
            },
            {
                "id": "republic",
                "name": "Республика",
                "scale": "large",
                "population": "1000000+",
                "description": "Государство с выборной властью",
                "governance": "президент/парламент"
            },
            {
                "id": "federation",
                "name": "Федерация/Штаты",
                "scale": "huge",
                "population": "10000000+",
                "description": "Союз государств/штатов",
                "governance": "президент/конгресс"
            },
            {
                "id": "confederation",
                "name": "Конфедерация",
                "scale": "huge",
                "population": "10000000+",
                "description": "Союз независимых государств",
                "governance": "совет представителей"
            },
            {
                "id": "theocracy",
                "name": "Теократия",
                "scale": "medium_to_large",
                "population": "500000+",
                "description": "Государство во главе с религиозными лидерами",
                "governance": "верховный жрец/совет жрецов"
            },
            {
                "id": "magocracy",
                "name": "Магократия",
                "scale": "medium_to_large",
                "population": "500000+",
                "description": "Государство во главе с магами",
                "governance": "архимаг/совет магов"
            },
            {
                "id": "corporatocracy",
                "name": "Корпоратократия",
                "scale": "large",
                "population": "1000000+",
                "description": "Государство управляемое корпорациями",
                "governance": "CEO/совет директоров"
            },
            {
                "id": "commune",
                "name": "Коммуна/Община",
                "scale": "small",
                "population": "100-1000",
                "description": "Коллективное самоуправление",
                "governance": "общее собрание"
            },
            {
                "id": "hive_mind",
                "name": "Коллективный разум",
                "scale": "any",
                "population": "variable",
                "description": "Единое сознание множества существ",
                "governance": "коллективное решение"
            }
        ]
        
        self.simulation_cache[cache_key] = json.dumps(biomes, ensure_ascii=False)
        self._save_cache()
        
        return biomes

    # ================================================================
    #  ПРАВИЛА ГОСУДАРСТВА
    # ================================================================

    def get_state_rules(self) -> List[Dict[str, Any]]:
        """Возвращает все правила государства."""
        cache_key = "state_rules"
        if cache_key in self.simulation_cache:
            try:
                return json.loads(self.simulation_cache[cache_key])
            except:
                pass
        
        rules = [
            {"id": 1, "name": "Право на жизнь", "category": "fundamental", "invertible": True},
            {"id": 2, "name": "Право на свободу", "category": "fundamental", "invertible": True},
            {"id": 3, "name": "Право на собственность", "category": "fundamental", "invertible": True},
            {"id": 4, "name": "Равенство перед законом", "category": "fundamental", "invertible": True},
            {"id": 5, "name": "Свобода слова", "category": "fundamental", "invertible": True},
            {"id": 6, "name": "Свобода совести", "category": "fundamental", "invertible": True},
            {"id": 7, "name": "Право на образование", "category": "social", "invertible": True},
            {"id": 8, "name": "Право на труд", "category": "social", "invertible": True},
            {"id": 9, "name": "Право на отдых", "category": "social", "invertible": True},
            {"id": 10, "name": "Право на здравоохранение", "category": "social", "invertible": True},
            {"id": 11, "name": "Социальная защита", "category": "social", "invertible": True},
            {"id": 12, "name": "Избирательное право", "category": "political", "invertible": True},
            {"id": 13, "name": "Право на участие в управлении", "category": "political", "invertible": True},
            {"id": 14, "name": "Свобода собраний", "category": "political", "invertible": True},
            {"id": 15, "name": "Свобода объединений", "category": "political", "invertible": True},
            {"id": 16, "name": "Неприкосновенность жилища", "category": "fundamental", "invertible": True},
            {"id": 17, "name": "Тайна переписки", "category": "fundamental", "invertible": True},
            {"id": 18, "name": "Презумпция невиновности", "category": "legal", "invertible": True},
            {"id": 19, "name": "Запрет пыток", "category": "fundamental", "invertible": True},
            {"id": 20, "name": "Запрет рабства", "category": "fundamental", "invertible": True},
            {"id": 21, "name": "Свобода предпринимательства", "category": "economic", "invertible": True},
            {"id": 22, "name": "Защита конкуренции", "category": "economic", "invertible": True},
            {"id": 23, "name": "Право на справедливые налоги", "category": "economic", "invertible": True},
            {"id": 24, "name": "Экологическая защита", "category": "environmental", "invertible": True},
            {"id": 25, "name": "Защита культурного наследия", "category": "cultural", "invertible": True}
        ]
        
        self.simulation_cache[cache_key] = json.dumps(rules, ensure_ascii=False)
        self._save_cache()
        
        return rules

    # ================================================================
    #  МОДЕЛИРОВАНИЕ МИРА
    # ================================================================

    def simulate_world(
        self,
        genre: str,
        biome: str,
        inverted_rule_ids: List[int],
        removed_rule_ids: List[int]
    ) -> Dict[str, Any]:
        """
        Моделирует мир с инверсией/удалением правил.
        
        Args:
            genre: Жанр мира
            biome: Тип государства
            inverted_rule_ids: IDs правил для инверсии
            removed_rule_ids: IDs правил для удаления
            
        Returns:
            Результаты симуляции
        """
        all_rules = self.get_state_rules()
        genres = self.get_all_world_genres()
        biomes = self.get_all_state_biomes()
        
        genre_info = next((g for g in genres if g["id"] == genre), None)
        biome_info = next((b for b in biomes if b["id"] == biome), None)
        
        if not genre_info or not biome_info:
            return {"error": "Invalid genre or biome"}
        
        # Применяем инверсию и удаление
        active_rules = []
        inverted_rules = []
        removed_rules = []
        
        for rule in all_rules:
            if rule["id"] in removed_rule_ids:
                removed_rules.append(rule)
            elif rule["id"] in inverted_rule_ids:
                inverted_rule = rule.copy()
                inverted_rule["inverted"] = True
                inverted_rule["name"] = f"НЕ ({rule['name']})"
                inverted_rules.append(inverted_rule)
            else:
                active_rules.append(rule)
        
        # Оцениваем последствия для каждого сословия
        estate_impacts = self._calculate_estate_impacts(
            active_rules, inverted_rules, removed_rules, genre_info, biome_info
        )
        
        # Общая оценка устойчивости
        stability_score = self._calculate_stability(estate_impacts)
        
        # Оценка справедливости
        justice_score = self._calculate_justice(estate_impacts)
        
        result = {
            "simulation_id": f"SIM-{datetime.now().strftime('%Y%m%d%H%M%S')}-{random.randint(1000, 9999)}",
            "timestamp": datetime.now().isoformat(),
            "genre": genre_info,
            "biome": biome_info,
            "inverted_rules": inverted_rules,
            "removed_rules": removed_rules,
            "active_rules": active_rules,
            "estate_impacts": estate_impacts,
            "stability_score": stability_score,
            "justice_score": justice_score,
            "overall_score": (stability_score + justice_score) / 2,
            "recommendation": self._generate_recommendation(stability_score, justice_score, inverted_rules, removed_rules)
        }
        
        return result

    def _calculate_estate_impacts(
        self,
        active_rules: List[Dict],
        inverted_rules: List[Dict],
        removed_rules: List[Dict],
        genre: Dict,
        biome: Dict
    ) -> Dict[str, Any]:
        """Рассчитывает влияние на каждое сословие."""
        
        estates = [
            "citizens", "business", "workers", "farmers",
            "state_servants", "vulnerable", "scholars"
        ]
        
        impacts = {}
        
        for estate in estates:
            # Базовый score
            base_score = 0.5
            
            # Влияние инвертированных правил
            inverted_penalty = len(inverted_rules) * 0.1
            if estate == "vulnerable":
                inverted_penalty *= 1.5  # Уязвимые страдают больше
            
            # Влияние удалённых правил
            removed_penalty = len(removed_rules) * 0.08
            if estate == "vulnerable":
                removed_penalty *= 1.5
            
            # Влияние жанра
            genre_modifier = 0
            if genre["id"] == "dystopia":
                genre_modifier = -0.2
            elif genre["id"] == "utopia":
                genre_modifier = 0.2
            elif genre["id"] == "postapoc":
                genre_modifier = -0.15
            elif genre["id"] == "cyberpunk":
                genre_modifier = -0.1
            
            # Влияние типа государства
            biome_modifier = 0
            if biome["scale"] == "micro":
                biome_modifier = 0.1  # Малые сообщества устойчивее
            elif biome["scale"] == "huge":
                biome_modifier = -0.05  # Крупные менее устойчивы
            
            # Финальный score
            final_score = max(0, min(1, base_score - inverted_penalty - removed_penalty + genre_modifier + biome_modifier))
            
            impacts[estate] = {
                "score": round(final_score, 2),
                "status": self._get_status(final_score),
                "risk_level": self._get_risk_level(final_score),
                "details": self._get_estate_details(estate, final_score, inverted_rules, removed_rules, genre)
            }
        
        return impacts

    def _get_status(self, score: float) -> str:
        """Определяет статус по score."""
        if score >= 0.8:
            return "prosperous"
        elif score >= 0.6:
            return "stable"
        elif score >= 0.4:
            return "unstable"
        elif score >= 0.2:
            return "critical"
        else:
            return "collapse"

    def _get_risk_level(self, score: float) -> str:
        """Определяет уровень риска."""
        if score >= 0.8:
            return "low"
        elif score >= 0.6:
            return "medium"
        elif score >= 0.4:
            return "high"
        else:
            return "critical"

    def _get_estate_details(
        self,
        estate: str,
        score: float,
        inverted: List[Dict],
        removed: List[Dict],
        genre: Dict
    ) -> str:
        """Генерирует описание для сословия."""
        if score >= 0.8:
            return f"Благоденствуют в {genre['name']} мире"
        elif score >= 0.6:
            return f"Стабильное положение с умеренными рисками"
        elif score >= 0.4:
            return f"Нестабильность из-за нарушения прав"
        elif score >= 0.2:
            return f"Критическое положение, требуются реформы"
        else:
            return f"Полный коллапс, выживание под угрозой"

    def _calculate_stability(self, estate_impacts: Dict) -> float:
        """Рассчитывает общую устойчивость."""
        scores = [impact["score"] for impact in estate_impacts.values()]
        avg = sum(scores) / len(scores)
        
        # Штраф за неравенство
        variance = sum((s - avg) ** 2 for s in scores) / len(scores)
        inequality_penalty = min(0.3, variance * 0.5)
        
        return max(0, min(1, avg - inequality_penalty))

    def _calculate_justice(self, estate_impacts: Dict) -> float:
        """Рассчитывает справедливость."""
        scores = [impact["score"] for impact in estate_impacts.values()]
        
        # Справедливость = минимальный score (уязвимые не должны страдать)
        min_score = min(scores)
        
        # Также учитываем разброс
        avg_score = sum(scores) / len(scores)
        max_score = max(scores)
        gap = max_score - min_score
        
        justice = min_score * 0.7 + (1 - gap) * 0.3
        
        return max(0, min(1, justice))

    def _generate_recommendation(
        self,
        stability: float,
        justice: float,
        inverted: List[Dict],
        removed: List[Dict]
    ) -> str:
        """Генерирует рекомендацию."""
        if stability >= 0.8 and justice >= 0.8:
            return "Идеальное государство! Сохранить текущую систему."
        elif stability >= 0.6 and justice >= 0.6:
            return "Стабильное государство с хорошей справедливостью."
        elif stability < 0.4:
            return "КРИТИЧЕСКИ: Требуется немедленная стабилизация системы."
        elif justice < 0.4:
            return "КРИТИЧЕСКИ: Высокая несправедливость, нужны социальные реформы."
        elif len(inverted) > 5:
            return "ПРЕДУПРЕЖДЕНИЕ: Слишком много инвертированных правил."
        elif len(removed) > 5:
            return "ПРЕДУПРЕЖДЕНИЕ: Слишком много удалённых правил."
        else:
            return "Рекомендуется постепенная реформа системы."

    # ================================================================
    #  ПОЛНОЕ МОДЕЛИРОВАНИЕ
    # ================================================================

    def run_full_simulation(self, genres: Optional[List[str]] = None, biomes: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        Запускает полное моделирование всех комбинаций.
        
        Args:
            genres: Список жанров (или все)
            biomes: Список биомов (или все)
            
        Returns:
            Сводные результаты
        """
        self.logger.info("Запуск полного моделирования...")
        
        all_genres = [g["id"] for g in self.get_all_world_genres()]
        all_biomes = [b["id"] for b in self.get_all_state_biomes()]
        all_rules = self.get_state_rules()
        
        selected_genres = genres or all_genres
        selected_biomes = biomes or all_biomes
        
        total_simulations = 0
        results_summary = {
            "timestamp": datetime.now().isoformat(),
            "total_simulations": 0,
            "by_inversion_level": {},
            "best_scenarios": [],
            "worst_scenarios": []
        }
        
        # Моделирование для каждого уровня инверсии (0% до 100%)
        for inversion_level in range(0, len(all_rules) + 1):
            self.logger.info(f"Уровень инверсии: {inversion_level}/{len(all_rules)}")
            
            level_results = []
            
            # Для каждого жанра и биома
            for genre in selected_genres:
                for biome in selected_biomes:
                    # Генерируем комбинации правил для инверсии
                    if inversion_level == 0:
                        # Идеальное состояние (без инверсии)
                        result = self.simulate_world(genre, biome, [], [])
                        result["inversion_percentage"] = 0
                        level_results.append(result)
                        total_simulations += 1
                    else:
                        # Инверсия N правил
                        for rule_combo in combinations(all_rules, inversion_level):
                            inverted_ids = [r["id"] for r in rule_combo]
                            result = self.simulate_world(genre, biome, inverted_ids, [])
                            result["inversion_percentage"] = round(inversion_level / len(all_rules) * 100, 1)
                            level_results.append(result)
                            total_simulations += 1
                            
                            # Ограничиваем количество симуляций
                            if total_simulations >= 1000:
                                break
                        
                        if total_simulations >= 1000:
                            break
                
                if total_simulations >= 1000:
                    break
            
            # Сохраняем результаты уровня
            if level_results:
                avg_score = sum(r["overall_score"] for r in level_results) / len(level_results)
                results_summary["by_inversion_level"][str(inversion_level)] = {
                    "simulations": len(level_results),
                    "average_score": round(avg_score, 3),
                    "best_score": max(r["overall_score"] for r in level_results),
                    "worst_score": min(r["overall_score"] for r in level_results)
                }
            
            if total_simulations >= 1000:
                break
        
        # Находим лучшие и худшие сценарии
        all_results = []
        for level_data in results_summary["by_inversion_level"].values():
            all_results.append(level_data)
        
        results_summary["total_simulations"] = total_simulations
        
        self.logger.info(f"Моделирование завершено: {total_simulations} симуляций")
        
        return results_summary

    def simulate_ideal_state(self, genre: str, biome: str) -> Dict[str, Any]:
        """
        Моделирует идеальное государство (0% инверсии).
        
        Args:
            genre: Жанр мира
            biome: Тип государства
            
        Returns:
            Результаты симуляции идеального государства
        """
        self.logger.info(f"Моделирование идеального государства: {genre} / {biome}")
        
        result = self.simulate_world(genre, biome, [], [])
        result["simulation_type"] = "ideal_state"
        
        self.simulation_results.append(result)
        self._save_results()
        
        return result

    def simulate_single_inversion(self, genre: str, biome: str, rule_id: int) -> Dict[str, Any]:
        """
        Моделирует инверсию одного правила.
        
        Args:
            genre: Жанр мира
            biome: Тип государства
            rule_id: ID правила для инверсии
            
        Returns:
            Результаты симуляции
        """
        self.logger.info(f"Моделирование инверсии правила {rule_id}: {genre} / {biome}")
        
        result = self.simulate_world(genre, biome, [rule_id], [])
        result["simulation_type"] = "single_inversion"
        
        self.simulation_results.append(result)
        self._save_results()
        
        return result

    def simulate_double_inversion(self, genre: str, biome: str, rule_ids: List[int]) -> Dict[str, Any]:
        """
        Моделирует инверсию двух правил.
        
        Args:
            genre: Жанр мира
            biome: Тип государства
            rule_ids: IDs правил для инверсии
            
        Returns:
            Результаты симуляции
        """
        self.logger.info(f"Моделирование инверсии правил {rule_ids}: {genre} / {biome}")
        
        result = self.simulate_world(genre, biome, rule_ids, [])
        result["simulation_type"] = "double_inversion"
        
        self.simulation_results.append(result)
        self._save_results()
        
        return result

    def simulate_progressive_inversion(
        self,
        genre: str,
        biome: str,
        max_percentage: float = 100
    ) -> List[Dict[str, Any]]:
        """
        Моделирует прогрессивную инверсию от 0% до max_percentage.
        
        Args:
            genre: Жанр мира
            biome: Тип государства
            max_percentage: Максимальный процент инверсии
            
        Returns:
            Список результатов для каждого уровня
        """
        self.logger.info(f"Прогрессивная инверсия: {genre} / {biome} до {max_percentage}%")
        
        all_rules = self.get_state_rules()
        results = []
        
        max_rules = int(len(all_rules) * max_percentage / 100)
        
        for i in range(0, max_rules + 1):
            # Выбираем первые i правил для инверсии
            inverted_ids = [all_rules[j]["id"] for j in range(min(i, len(all_rules)))]
            
            result = self.simulate_world(genre, biome, inverted_ids, [])
            result["inversion_level"] = i
            result["inversion_percentage"] = round(i / len(all_rules) * 100, 1)
            result["simulation_type"] = "progressive_inversion"
            
            results.append(result)
            self.simulation_results.append(result)
        
        self._save_results()
        
        return results

    def get_simulation_statistics(self) -> Dict[str, Any]:
        """Возвращает статистику всех симуляций."""
        if not self.simulation_results:
            return {"total": 0}
        
        total = len(self.simulation_results)
        avg_score = sum(r.get("overall_score", 0) for r in self.simulation_results) / total
        
        by_genre = {}
        by_biome = {}
        by_type = {}
        
        for result in self.simulation_results:
            genre = result.get("genre", {}).get("name", "Unknown")
            biome = result.get("biome", {}).get("name", "Unknown")
            sim_type = result.get("simulation_type", "unknown")
            
            by_genre[genre] = by_genre.get(genre, 0) + 1
            by_biome[biome] = by_biome.get(biome, 0) + 1
            by_type[sim_type] = by_type.get(sim_type, 0) + 1
        
        return {
            "total_simulations": total,
            "average_score": round(avg_score, 3),
            "by_genre": by_genre,
            "by_biome": by_biome,
            "by_simulation_type": by_type,
            "last_updated": datetime.now().isoformat()
        }

    def export_results(self, filename: Optional[str] = None) -> str:
        """Экспортирует результаты в файл."""
        if filename is None:
            filename = f"world_simulation_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        filepath = Path("futaba/engine/state") / filename
        
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump({
                "exported_at": datetime.now().isoformat(),
                "total_results": len(self.simulation_results),
                "results": self.simulation_results
            }, f, ensure_ascii=False, indent=2)
        
        self.logger.info(f"Результаты экспортированы: {filepath}")
        
        return str(filepath)
