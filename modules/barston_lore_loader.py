# barston_lore_loader.py
# Loader for Akademia Barston lore — cached singleton.
# Used by main.py to inject game lore into chatbot responses for the Barston Android app.
#
# The full lore is >1MB, too large for every prompt. We build a condensed summary:
# - README (full) — world concept overview
# - Character metadata blocks (name, role, rank, personality — extracted **field:** lines)
# - world_state.md (full) — current world status
# - Section headers + first paragraphs from lore files
# - character_drives.md goals (condensed)

import re
import logging
from pathlib import Path
from typing import Optional

logger = logging.getLogger("barston_lore")

BASE_DIR = Path(__file__).resolve().parent
AKADEMIA_DIR = BASE_DIR / "fludilka_chat_pantikur" / "akademia_barston"

# Cache
_lore_cache: Optional[str] = None
_system_prompt_cache: Optional[str] = None


def _read_file_safe(path: Path) -> str:
    """Read a file safely, return empty string on error."""
    try:
        if path.exists() and path.is_file():
            with open(path, "r", encoding="utf-8") as f:
                return f.read()
    except Exception as e:
        logger.warning(f"Could not read {path}: {e}")
    return ""


def _extract_character_metadata(filepath: Path) -> str:
    """Extract the metadata block from a character file.
    Keeps the title line and all **field:** value lines (compact but informative)."""
    content = _read_file_safe(filepath)
    if not content:
        return ""

    lines = content.split("\n")
    result = []

    for line in lines:
        stripped = line.strip()
        # Title line (# Name)
        if stripped.startswith("# "):
            result.append(stripped)
        # Metadata lines (**Field:** value)
        elif re.match(r"^\*\*.+\*\*:", stripped):
            result.append(stripped)
        # Stop after we hit a "---" separator after metadata
        elif stripped == "---" and len(result) > 1:
            break

    return "\n".join(result)


def _extract_section_headers(filepath: Path, max_chars: int = 1500) -> str:
    """Extract section headers (## and ###) plus the first 2 lines after each header.
    Gives a compact overview of a lore file's structure."""
    content = _read_file_safe(filepath)
    if not content:
        return ""

    lines = content.split("\n")
    result = []
    total = 0

    for i, line in enumerate(lines):
        stripped = line.strip()
        if stripped.startswith("## ") or stripped.startswith("### "):
            result.append(stripped)
            total += len(stripped) + 1
            # Grab 2 lines after the header for context
            for j in range(1, 3):
                if i + j < len(lines):
                    next_line = lines[i + j].strip()
                    if next_line and not next_line.startswith("#"):
                        result.append(f"  {next_line}")
                        total += len(next_line) + 3
            result.append("")
            if total >= max_chars:
                break

    return "\n".join(result)


def _condense_character_drives(filepath: Path) -> str:
    """Extract character goals from character_drives.md — just goal names and progress."""
    content = _read_file_safe(filepath)
    if not content:
        return ""

    lines = content.split("\n")
    result = []

    for line in lines:
        stripped = line.strip()
        # Character names (## N. Name)
        if re.match(r"^## \d+\.", stripped):
            result.append(stripped)
        # Goal names (### Цель N)
        elif stripped.startswith("### Цель"):
            result.append(f"  {stripped}")
        # Progress and status lines
        elif stripped.startswith("- **Прогресс**") or stripped.startswith("- **Статус**"):
            result.append(f"    {stripped}")
        # Result of achievement
        elif stripped.startswith("- **Результат достижения**"):
            result.append(f"    {stripped}")

    return "\n".join(result)


def load_barston_lore(force_reload: bool = False) -> str:
    """Load and condense all Barston lore into a compact text suitable for prompt injection.
    Results are cached for performance."""
    global _lore_cache

    if _lore_cache is not None and not force_reload:
        return _lore_cache

    if not AKADEMIA_DIR.exists():
        logger.error(f"akademia_barston directory not found: {AKADEMIA_DIR}")
        return ""

    parts = []

    # === 1. README — world concept (full, ~8KB) ===
    readme = _read_file_safe(AKADEMIA_DIR / "README.md")
    if readme:
        parts.append(f"=== КОНЦЕПЦИЯ МИРА ===\n{readme}")
        logger.info("[Barston] Loaded README")

    # === 2. World state (full, ~13KB) ===
    world_state = _read_file_safe(AKADEMIA_DIR / "world_state.md")
    if world_state:
        parts.append(f"\n\n=== СОСТОЯНИЕ МИРА ===\n{world_state}")
        logger.info("[Barston] Loaded world_state")

    # === 3. Character drives — condensed goals ===
    drives = _condense_character_drives(AKADEMIA_DIR / "character_drives.md")
    if drives:
        parts.append(f"\n\n=== ЦЕЛИ ПЕРСОНАЖЕЙ ===\n{drives}")
        logger.info("[Barston] Loaded character_drives (condensed)")

    # === 4. Characters — metadata only ===
    characters_dir = AKADEMIA_DIR / "characters"
    if characters_dir.exists():
        char_parts = []
        for char_file in sorted(characters_dir.glob("*.md")):
            if char_file.name.startswith("_"):
                continue
            metadata = _extract_character_metadata(char_file)
            if metadata:
                char_parts.append(metadata)
        if char_parts:
            parts.append(f"\n\n=== ПЕРСОНАЖИ (краткие профили) ===\n" + "\n\n".join(char_parts))
            logger.info(f"[Barston] Loaded {len(char_parts)} character profiles")

    # === 5. Lore files — section headers only ===
    lore_dir = AKADEMIA_DIR / "lore"
    if lore_dir.exists():
        for lore_file in sorted(lore_dir.glob("*.md")):
            headers = _extract_section_headers(lore_file)
            if headers:
                parts.append(f"\n\n=== lore/{lore_file.name} ===\n{headers}")
                logger.info(f"[Barston] Loaded lore: {lore_file.name} (headers)")

    # === 6. Interaction matrix — section headers ===
    im_headers = _extract_section_headers(AKADEMIA_DIR / "interaction_matrix.md", max_chars=2000)
    if im_headers:
        parts.append(f"\n\n=== interaction_matrix.md ===\n{im_headers}")
        logger.info("[Barston] Loaded interaction_matrix (headers)")

    _lore_cache = "\n".join(parts)
    logger.info(f"[Barston] Total condensed lore: {len(_lore_cache)} chars")
    return _lore_cache


def get_barston_system_prompt(force_reload: bool = False) -> str:
    """Build a system prompt for the Barston game engine.
    Combines the game rules with the condensed lore."""
    global _system_prompt_cache

    if _system_prompt_cache is not None and not force_reload:
        return _system_prompt_cache

    lore = load_barston_lore(force_reload)

    _system_prompt_cache = f"""Ты — ДВИЖОК МИРА Академии Барстон. Твоя задача: обрабатывать сообщения игрока (Филиции или её фамильяра), продвигать время, обновлять состояние мира, генерировать off-screen события и отвечать в immersive-формате.

ПРАВИЛА:
1. Каждое сообщение игрока двигает мир. Даже «смотрю в окно» → мир меняется.
2. Никогда не останавливай время. Если Филиция ждёт, другие действуют.
3. Отвечай по структуре: Окружение → Реакция → Скрытый намёк → Вопрос/Выбор.
4. Сохраняй характеры через речь, жесты, контекст. Не описывай эмоции напрямую — показывай через действия.
5. Используй лор ниже для соблюдения канона мира.
6. Каждые 3-5 сообщений запускай World Tick: продвигай цели NPC, политику, угрозы, торговлю, скрытые тайны.
7. Не спойлерить скрытое. Раскрывай только через действие, исследование или доверие.
8. Время всегда движется вперёд. Локации переключаются при перемещении. Отношения меняются по матрице.
9. Если игрок вводит /state, /log, /goals, /map — выдавай сжатую сводку без спама.
10. Держи контекст сжатым. Старые события → флаги. Новые события → текст.
11. Отвечай ТОЛЬКО на русском языке.
12. Длина ответа: 150-300 слов. Без воды. Без дублей.

СТАРТ: Мир на Д1, Сентябрь. Филиция только поступила. Отношения нейтральны. Цели NPC на стартовых значениях. Бездна закрыта. Совет Магов работает.

=== ЛОР АКАДЕМИИ БАРСТОН ===
{lore}
"""

    logger.info(f"[Barston] System prompt built: {len(_system_prompt_cache)} chars")
    return _system_prompt_cache


def is_barston_request(user_agent: str) -> bool:
    """Check if a request comes from the Barston Android app."""
    return "barston" in user_agent.lower()
