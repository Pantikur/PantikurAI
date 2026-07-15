"""
Разработчик характера Фуюки.

Управляет:
  - Созданием характера при первом запуске
  - Укреплением сильных сторон
  - Эволюцией черт характера
  - Выбором и выращиванием характера
  - Сохранением и загрузкой характера
"""

from __future__ import annotations
import json
import logging
import random
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

from scientists_network.character_system import CharacterSystem, CharacterTraits


class CharacterDeveloper:
    """
    Разработчик характера Фуюки.
    """

    def __init__(self, config: Any):
        self.config = config
        self.logger = logging.getLogger("CharacterDeveloper")
        self.state_dir = config.state_dir
        self.state_dir.mkdir(parents=True, exist_ok=True)

        # Инициализируем систему характера
        self.character_system = CharacterSystem("fuyuki", self.state_dir)
        self.traits = self.character_system.get_traits()

        # Загружаем или создаём характер
        self._load_or_create_character()

    def _load_or_create_character(self):
        """Загружает характер или создаёт новый."""
        char_path = self.config.my_character_path
        
        if char_path.exists():
            self._load_character(char_path)
        else:
            self._create_initial_character(char_path)

    def _load_character(self, path: Path):
        """Загружает характер из файла."""
        try:
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
            
            self.traits = CharacterTraits.from_dict(data.get("my_character", data))
            self.traits.specialty = "электричество"
            self.traits.specialty_passion = data.get("specialty_passion", 0.95)
            
            self.logger.info(f"📖 Характер Фуюки загружен")
            self.logger.info(f"   Темперамент: {self.traits.temperament}")
            self.logger.info(f"   Страсть к электричеству: {self.traits.specialty_passion:.0%}")
        except Exception as e:
            self.logger.warning(f"⚠️ Ошибка загрузки характера: {e}")
            self._create_initial_character(path)

    def _create_initial_character(self, path: Path):
        """Создаёт начальный характер Фуюки."""
        self.logger.info("🌱 Создаю характер Фуюки...")
        
        # Характер Фуюки — страстная исследовательница электричества
        self.traits = CharacterTraits(
            temperament=random.choice(["холерик", "меланхолик"]),
            sociality=random.choice(["интровертная", "выборочная"]),
            emotionality=random.choice(["интенсивная", "контролируемая"]),
            worldview="инноватор",
            dominance=random.choice(["амбициозная", "решительная"]),
            change_attitude="энергичная",
            complexity="динамичная",
            specialty_passion=random.uniform(0.90, 0.99),
            curiosity=random.uniform(0.90, 0.99),
            courage=random.uniform(0.80, 0.95),
            patience=random.uniform(0.70, 0.85),
            creativity=random.uniform(0.80, 0.95),
            collaboration=random.uniform(0.75, 0.90),
            strengths=[
                "моделирование электрических полей",
                "управление разрядами",
                "анализ молний",
                "энергетическая эффективность",
                "построение теорий",
            ],
            values=[
                "контроль над электричеством",
                "чистая энергия",
                "безопасные технологии",
                "познание атмосферы",
            ],
            specialty="электричество",
        )

        # Сохраняем
        self._save_character(path)
        self.logger.info("✅ Характер Фуюки создан!")

    def strengthen_strengths(self) -> int:
        """
        Укрепляет сильные стороны характера.
        
        Returns:
            Количество улучшенных черт
        """
        strengthened = 0
        t = self.traits

        # Усиливаем страсть к электричеству
        if t.specialty_passion < 1.0:
            t.specialty_passion = min(1.0, t.specialty_passion + random.uniform(0.02, 0.06))
            strengthened += 1

        # Усиливаем любопытство
        if t.curiosity < 1.0:
            t.curiosity = min(1.0, t.curiosity + random.uniform(0.02, 0.06))
            strengthened += 1

        # Усиливаем смелость в исследованиях
        if t.courage < 1.0:
            t.courage = min(1.0, t.courage + random.uniform(0.01, 0.05))
            strengthened += 1

        # Усиливаем креативность в теориях
        if t.creativity < 1.0:
            t.creativity = min(1.0, t.creativity + random.uniform(0.01, 0.05))
            strengthened += 1

        # Усиливаем сотрудничество с сёстрами
        if t.collaboration < 1.0:
            t.collaboration = min(1.0, t.collaboration + random.uniform(0.01, 0.05))
            strengthened += 1

        # Усиливаем терпение в исследованиях
        if t.patience < 1.0:
            t.patience = min(1.0, t.patience + random.uniform(0.01, 0.04))
            strengthened += 1

        if strengthened > 0:
            self._save_character()
            self.config.character_traits_strengthened += strengthened

        if strengthened > 0:
            self.logger.info(f"💪 Характер укреплён: {strengthened} черт")

        return strengthened

    def evolve_traits(self) -> bool:
        """
        Эволюционирует черты характера на основе опыта.
        
        Returns:
            True если черты были изменены
        """
        evolved = False
        t = self.traits

        # На основе исследований — растёт любопытство
        if t.curiosity < 0.99:
            t.curiosity += 0.002
            evolved = True

        # На основе общения — растёт сотрудничество
        if t.collaboration < 0.97:
            t.collaboration += 0.002
            evolved = True

        # На основе творчества — растёт креативность
        if t.creativity < 0.97:
            t.creativity += 0.002
            evolved = True

        # На основе сложных теорий — растёт смелость
        if t.courage < 0.97:
            t.courage += 0.001
            evolved = True

        # На основе долгосрочных исследований — растёт терпение
        if t.patience < 0.95:
            t.patience += 0.001
            evolved = True

        if evolved:
            self._save_character()

        return evolved

    def get_character_summary(self) -> str:
        """Текстовое резюме характера."""
        t = self.traits
        lines = [
            "⚡ Характер Фуюки:",
            "",
            f"  🌡️  Темперамент: {t.temperament}",
            f"  🤝 Социальность: {t.sociality}",
            f"  💭 Эмоциональность: {t.emotionality}",
            f"  🌅 Мировоззрение: {t.worldview}",
            f"  👑 Доминирование: {t.dominance}",
            f"  🔄 Перемены: {t.change_attitude}",
            f"  🌀 Сложность: {t.complexity}",
            "",
            f"  🔥 Страсть к электричеству: {t.specialty_passion:.0%}",
            f"  🔍 Любознательность: {t.curiosity:.0%}",
            f"  ⚔️  Смелость: {t.courage:.0%}",
            f"  🧘  Терпение: {t.patience:.0%}",
            f"  🎨 Креативность: {t.creativity:.0%}",
            f"  🤝 Сотрудничество: {t.collaboration:.0%}",
            "",
            "  💎 Сильные стороны:",
        ]
        for strength in t.strengths[:3]:
            lines.append(f"     • {strength}")
        
        lines.append("")
        lines.append("  💖 Ценности:")
        for value in t.values[:3]:
            lines.append(f"     • {value}")
        
        return "\n".join(lines)

    def _save_character(self, path: Optional[Path] = None):
        """Сохраняет характер в файл."""
        target_path = path or self.config.my_character_path
        assert target_path is not None

        data = {
            "my_character": self.traits.to_dict(),
            "specialty_passion": self.traits.specialty_passion,
            "updated_at": datetime.now().isoformat(),
        }

        try:
            target_path.parent.mkdir(parents=True, exist_ok=True)
            with open(target_path, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            self.logger.debug(f"💾 Характер сохранён: {target_path}")
        except Exception as e:
            self.logger.error(f"❌ Ошибка сохранения характера: {e}")

    def get_traits_dict(self) -> Dict[str, Any]:
        """Получает черты как словарь."""
        return self.traits.to_dict()

    def add_trait(self, trait_name: str, trait_value: float):
        """Добавляет новую черту характера."""
        if trait_name == "specialty_passion":
            self.traits.specialty_passion = min(1.0, trait_value)
        elif trait_name == "curiosity":
            self.traits.curiosity = min(1.0, trait_value)
        elif trait_name == "courage":
            self.traits.courage = min(1.0, trait_value)
        elif trait_name == "patience":
            self.traits.patience = min(1.0, trait_value)
        elif trait_name == "creativity":
            self.traits.creativity = min(1.0, trait_value)
        elif trait_name == "collaboration":
            self.traits.collaboration = min(1.0, trait_value)
        
        self._save_character()

    def learn_trait_from_sister(self, sister_name: str, trait_name: str, trait_value: float):
        """
        Перенимает черту у другой девочки.
        
        Фуюки может учиться у всех 11 сестёр!
        """
        self.logger.info(f"🎓 Фуюки перенимает черту «{trait_name}» у {sister_name}")
        self.add_trait(trait_name, trait_value)
        
        # Добавляем в сильные стороны
        if trait_name not in self.traits.strengths:
            self.traits.strengths.append(f"учусь у {sister_name}: {trait_name}")
            if len(self.traits.strengths) > 10:
                self.traits.strengths = self.traits.strengths[-10:]
        
        self._save_character()
