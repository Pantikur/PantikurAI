"""
Разработчик характера Люси — создание, укрепление и эволюция характера.

Реализует:
  - Создание характера при первом запуске
  - Укрепление сильных сторон
  - Эволюция черт на основе опыта
  - Перенимание черт у сестёр
  - Сохранение и загрузка характера
"""

from __future__ import annotations
import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Optional

from lucy.engine.config import LucyConfig
from lucy.engine.models import CharacterTraits


class CharacterDeveloper:
    """
    Разработчик характера для Люси.
    """

    def __init__(self, config: LucyConfig):
        self.config = config
        self.logger = logging.getLogger("CharacterDeveloper")
        
        # Загружаем характер
        self.character_file = config.character_file
        self._load_character()

    def _load_character(self):
        """Загружает характер."""
        if self.character_file.exists():
            try:
                with open(self.character_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    self.logger.info(f"📋 Характер загружен: {self.character_file}")
            except Exception as e:
                self.logger.warning(f"⚠️ Ошибка загрузки характера: {e}")

    def _save_character(self, character: CharacterTraits):
        """Сохраняет характер."""
        try:
            self.character_file.parent.mkdir(parents=True, exist_ok=True)
            with open(self.character_file, "w", encoding="utf-8") as f:
                json.dump({
                    "my_character": character.to_dict(),
                    "updated_at": datetime.now().isoformat()
                }, f, ensure_ascii=False, indent=2)
            self.logger.debug("💾 Характер сохранён")
        except Exception as e:
            self.logger.error(f"❌ Ошибка сохранения характера: {e}")

    def strengthen_traits(self, character: CharacterTraits, count: int = 1) -> int:
        """
        Укрепляет случайные черты характера.
        
        Args:
            character: Текущий характер
            count: Количество черт для укрепления
            
        Returns:
            Количество укрепленных черт
        """
        traits_to_strengthen = [
            "specialty_passion", "curiosity", "courage",
            "patience", "creativity", "collaboration"
        ]
        
        strengthened = 0
        for _ in range(count):
            trait = traits_to_strengthen[hash(datetime.now().isoformat()) % len(traits_to_strengthen)]
            current = getattr(character, trait)
            new_value = min(1.0, current + 0.01)
            setattr(character, trait, new_value)
            strengthened += 1
        
        self.logger.info(f"💪 Укреплено {strengthened} черт характера")
        return strengthened

    def evolve_traits(self, character: CharacterTraits) -> bool:
        """
        Эволюционирует черты характера на основе опыта.
        
        Args:
            character: Текущий характер
            
        Returns:
            True если эволюция произошла
        """
        # Эволюция на основе страсти к двигателям
        if character.specialty_passion > 0.9:
            character.creativity = min(1.0, character.creativity + 0.02)
            character.curiosity = min(1.0, character.curiosity + 0.02)
            self.logger.info("✨ Характер эволюционировал: креативность и любознательность выросли")
            return True
        
        return False

    def save_character(self, character: CharacterTraits):
        """Сохраняет характер."""
        self._save_character(character)
