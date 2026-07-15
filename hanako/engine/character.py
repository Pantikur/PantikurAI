"""
Система характера Ханако — выбор, выращивание и укрепление характера.
"""

from __future__ import annotations

import json
import random
import logging
from datetime import datetime
from pathlib import Path
from typing import Optional

from hanako.engine.config import HanakoConfig
from hanako.engine.models import CharacterTraits


class CharacterSystem:
    """
    Система характера Ханако.
    
    Функции:
    - Загрузка и сохранение характера
    - Укрепление сильных сторон
    - Эволюция черт на основе опыта
    - Выбор нового характера
    - Анализ влияния характера на работу
    """

    def __init__(self, config: HanakoConfig):
        self.config = config
        self.logger = logging.getLogger("CharacterSystem")
        self.character_path = config.state_dir / "my_character.yaml"
        self._traits = self._load_character()

    def _load_character(self) -> CharacterTraits:
        """Загрузка характера."""
        yaml_path = self.character_path
        if yaml_path.exists():
            try:
                import yaml
                with open(yaml_path, 'r', encoding='utf-8') as f:
                    data = yaml.safe_load(f)
                if data and isinstance(data, dict):
                    return CharacterTraits.from_dict(data)
            except ImportError:
                # Если PyYAML нет, пробуем JSON
                json_path = self.character_path.with_suffix('.json')
                if json_path.exists():
                    try:
                        with open(json_path, 'r', encoding='utf-8') as f:
                            data = json.load(f)
                        return CharacterTraits.from_dict(data)
                    except Exception:
                        pass
            except Exception:
                pass
        # По умолчанию
        return CharacterTraits()

    def _save_character(self):
        """Сохранение характера."""
        # Сохраняем как JSON (надёжнее)
        json_path = self.character_path.with_suffix('.json')
        try:
            with open(json_path, 'w', encoding='utf-8') as f:
                json.dump(self._traits.to_dict(), f, ensure_ascii=False, indent=2)
        except Exception:
            pass

        # Пробуем YAML
        try:
            import yaml
            with open(self.character_path, 'w', encoding='utf-8') as f:
                yaml.dump(self._traits.to_dict(), f, default_flow_style=False, allow_unicode=True)
        except ImportError:
            pass
        except Exception:
            pass

    def get_traits(self) -> CharacterTraits:
        """Получить текущие черты характера."""
        return self._traits

    def strengthen_strengths(self) -> int:
        """Укрепление сильных сторон характера."""
        strengthened = 0

        # Усиливаем страсть к гравитации
        if self._traits.gravity_passion < 1.0:
            self._traits.gravity_passion = min(1.0, self._traits.gravity_passion + random.uniform(0.01, 0.05))
            strengthened += 1

        # Усиливаем любопытство
        if self._traits.curiosity < 1.0:
            self._traits.curiosity = min(1.0, self._traits.curiosity + random.uniform(0.01, 0.05))
            strengthened += 1

        # Усиливаем смелость
        if self._traits.courage < 1.0:
            self._traits.courage = min(1.0, self._traits.courage + random.uniform(0.01, 0.05))
            strengthened += 1

        # Усиливаем креативность
        if self._traits.creativity < 1.0:
            self._traits.creativity = min(1.0, self._traits.creativity + random.uniform(0.01, 0.05))
            strengthened += 1

        # Усиливаем сотрудничество
        if self._traits.collaboration < 1.0:
            self._traits.collaboration = min(1.0, self._traits.collaboration + random.uniform(0.01, 0.05))
            strengthened += 1

        # Усиливаем терпение
        if self._traits.patience < 1.0:
            self._traits.patience = min(1.0, self._traits.patience + random.uniform(0.01, 0.05))
            strengthened += 1

        self._save_character()
        return strengthened

    def evolve_traits(self) -> bool:
        """Эволюция черт на основе опыта."""
        evolved = False

        # На основе опыта общения
        if self._traits.collaboration < 0.95:
            self._traits.collaboration += 0.001
            evolved = True

        # На основе исследований
        if self._traits.curiosity < 0.99:
            self._traits.curiosity += 0.001
            evolved = True

        # На основе творчества
        if self._traits.creativity < 0.95:
            self._traits.creativity += 0.001
            evolved = True

        # На основе смелости в исследованиях
        if self._traits.courage < 0.95:
            self._traits.courage += 0.001
            evolved = True

        if evolved:
            self._save_character()

        return evolved

    def add_strength(self, strength: str):
        """Добавить сильную сторону."""
        if strength not in self._traits.strengths:
            self._traits.strengths.append(strength)
            self._save_character()

    def add_value(self, value: str):
        """Добавить ценность."""
        if value not in self._traits.values:
            self._traits.values.append(value)
            self._save_character()

    def forge_character(self) -> CharacterTraits:
        """
        Создать новый характер (для первого запуска).
        
        Возвращает сгенерированный характер.
        """
        self.logger.info("🌱 Создаю новый характер для Ханако...")

        # Генерируем характер на основе гравитационной тематики
        traits = CharacterTraits(
            temperament=random.choice(["холерик", "сангвиник"]),
            sociality=random.choice(["общительная", "лидер"]),
            emotionality=random.choice(["страстная", "экспрессивная"]),
            worldview="исследователь",
            dominance="уравновешенная",
            change_attitude="открытая",
            complexity="глубокая",
            gravity_passion=0.95,
            curiosity=0.98,
            courage=0.90,
            patience=0.80,
            creativity=0.90,
            collaboration=0.85,
            strengths=[
                "анализ пространственно-временных метрик",
                "построение гравитационных моделей",
                "математическое мышление",
                "неустрашимость перед неизвестным",
                "креативность в теориях",
            ],
            values=[
                "истина о гравитации",
                "свобода исследования",
                "сотрудничество с сёстрами",
                "постоянное развитие",
                "познание Вселенной",
            ],
        )

        self._traits = traits
        self._save_character()

        self.logger.info(f"✅ Характер создан: {traits.temperament}, {traits.sociality}, {traits.worldview}")
        return traits

    def get_character_summary(self) -> str:
        """Текстовое резюме характера."""
        t = self._traits
        return (
            f"Характер Ханако:\n"
            f"  Темперамент: {t.temperament}\n"
            f"  Социальность: {t.sociality}\n"
            f"  Эмоциональность: {t.emotionality}\n"
            f"  Мировоззрение: {t.worldview}\n"
            f"  Доминирование: {t.dominance}\n"
            f"  Отношение к переменам: {t.change_attitude}\n"
            f"  Сложность: {t.complexity}\n"
            f"  Страсть к гравитации: {t.gravity_passion:.0%}\n"
            f"  Любознательность: {t.curiosity:.0%}\n"
            f"  Смелость: {t.courage:.0%}\n"
            f"  Терпение: {t.patience:.0%}\n"
            f"  Креативность: {t.creativity:.0%}\n"
            f"  Сотрудничество: {t.collaboration:.0%}\n"
            f"  Сильные стороны: {', '.join(t.strengths[:3])}\n"
            f"  Ценности: {', '.join(t.values[:3])}"
        )
