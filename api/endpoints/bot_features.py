# api/endpoints/bot_features.py — Эндпоинты способностей бота (интуиция, соц, когнитив и т.д.)

from services.model_loader import get_qwen_cache


def _get_bot():
    local_bot = get_qwen_cache()
    if local_bot is None:
        return {"status": "not available", "detail": "Бот не загружен"}
    return local_bot


async def intuition_status() -> dict:
    """GET /intuition — Сводка настроения."""
    bot = _get_bot()
    if isinstance(bot, dict):
        return bot
    if not hasattr(bot, 'intuition'):
        return {"status": "not available", "detail": "Бот не загружен или интуиция отключена"}
    mood_summary = bot.intuition.get_mood_summary()
    return {"status": "ok", "intuition": mood_summary, "enabled": bot.intuition_enabled}


async def social_status() -> dict:
    """GET /social — Сводка социальных способностей."""
    bot = _get_bot()
    if isinstance(bot, dict):
        return bot
    if not hasattr(bot, 'social_engine'):
        return {"status": "not available", "detail": "Бот не загружен или соц. способности отключены"}
    summary = bot.social_engine.get_social_summary()
    return {"status": "ok", "social": summary, "enabled": bot.social_enabled}


async def cognitive_status() -> dict:
    """GET /cognitive — Сводка когнитивных способностей."""
    bot = _get_bot()
    if isinstance(bot, dict):
        return bot
    if not hasattr(bot, 'cognitive_engine'):
        return {"status": "not available", "detail": "Бот не загружен или когнитивные способности отключены"}
    summary = bot.cognitive_engine.get_cognitive_summary()
    return {"status": "ok", "cognitive": summary, "enabled": bot.cognitive_enabled}


async def eq_status() -> dict:
    """GET /eq — Сводка эмоционального интеллекта."""
    bot = _get_bot()
    if isinstance(bot, dict):
        return bot
    if not hasattr(bot, 'eq_engine'):
        return {"status": "not available", "detail": "Бот не загружен или EQ отключён"}
    summary = bot.eq_engine.get_eq_summary()
    return {"status": "ok", "eq": summary, "enabled": bot.eq_enabled}


async def physiology_status() -> dict:
    """GET /physiology — Сводка физиологических способностей."""
    bot = _get_bot()
    if isinstance(bot, dict):
        return bot
    if not hasattr(bot, 'phys_engine'):
        return {"status": "not available", "detail": "Бот не загружен или физиологические способности отключены"}
    summary = bot.phys_engine.get_physiology_summary()
    return {"status": "ok", "physiology": summary, "enabled": bot.phys_enabled}


async def special_status() -> dict:
    """GET /special — Сводка специальных когнитивных способностей."""
    bot = _get_bot()
    if isinstance(bot, dict):
        return bot
    if not hasattr(bot, 'special_cognitive_engine'):
        return {"status": "not available", "detail": "Бот не загружен или специальные способности отключены"}
    summary = bot.special_cognitive_engine.get_special_cognitive_summary()
    return {"status": "ok", "special": summary, "enabled": bot.special_cognitive_enabled}


async def professions_status() -> dict:
    """GET /professions — Сводка по профессиям."""
    bot = _get_bot()
    if isinstance(bot, dict):
        return bot
    if not hasattr(bot, 'profession_engine'):
        return {"status": "not available", "detail": "Бот не загружен или анализ профессий отключён"}
    summary = bot.profession_engine.get_profession_summary()
    return {"status": "ok", "professions": summary, "enabled": bot.professions_enabled}


async def imagination_status() -> dict:
    """GET /imagination — Сводка активного воображения."""
    bot = _get_bot()
    if isinstance(bot, dict):
        return bot
    if not hasattr(bot, 'imagination_engine'):
        return {"status": "not available", "detail": "Бот не загружен или воображение отключено"}
    summary = bot.imagination_engine.get_imagination_summary()
    return {"status": "ok", "imagination": summary, "enabled": bot.imagination_enabled}
