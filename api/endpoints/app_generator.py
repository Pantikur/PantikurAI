# api/endpoints/app_generator.py — Эндпоинты генерации Android-приложений

import logging
from fastapi import HTTPException, Depends

from api.dependencies import get_base_dir
from api.schemas import AppGenerateRequest

logger = logging.getLogger("app_generator")


async def app_generate(request: AppGenerateRequest, base_dir: str = Depends(get_base_dir)) -> dict:
    """POST /app/generate"""
    try:
        from utils.kotlin_assistant import KotlinAssistant
        assistant = KotlinAssistant(project_root=str(base_dir))
        result = assistant.generate_app(
            app_name=request.app_name,
            app_type=request.app_type,
            package_name=request.package_name,
            features=request.features
        )
        logger.info(f"✅ Приложение '{request.app_name}' ({request.app_type}) сгенерировано")
        return {"status": "ok", **result}
    except Exception as e:
        logger.error(f"❌ Ошибка генерации приложения: {e}")
        raise HTTPException(status_code=500, detail=str(e))


async def app_templates() -> dict:
    """GET /app/templates"""
    return {
        "status": "ok",
        "templates": [
            {"type": "todo", "name": "Todo List", "description": "Список задач с отметками"},
            {"type": "notes", "name": "Notes", "description": "Заметки с Rich Text"},
            {"type": "gallery", "name": "Gallery", "description": "Галерея изображений"},
            {"type": "weather", "name": "Weather", "description": "Прогноз погоды"},
            {"type": "chat", "name": "Chat", "description": "Мессенджер"},
            {"type": "custom", "name": "Custom", "description": "Пользовательский шаблон"}
        ]
    }
