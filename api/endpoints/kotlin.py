# api/endpoints/kotlin.py — Эндпоинты Kotlin Assistant

import logging
from fastapi import HTTPException, Depends

from api.dependencies import get_base_dir

logger = logging.getLogger("kotlin")


from api.schemas import (
    KotlinGenerateRequest,
    KotlinEditRequest,
    KotlinAnalyzeRequest,
    KotlinRefactorRequest,
    KotlinAutocompleteRequest,
    KotlinContextRequest,
)


# === Глобальный инстанс ===
_kotlin_assistant_instance = None
_kotlin_lock = __import__("threading").Lock()


def _get_assistant(project_root: str):
    global _kotlin_assistant_instance
    if _kotlin_assistant_instance is None:
        from utils.kotlin_assistant import KotlinAssistant
        _kotlin_assistant_instance = KotlinAssistant(project_root=project_root)
    return _kotlin_assistant_instance


async def kotlin_generate(request: KotlinGenerateRequest, base_dir: str = Depends(get_base_dir)) -> dict:
    """POST /kotlin/generate"""
    try:
        assistant = _get_assistant(str(base_dir))
        result = assistant.generate_code(
            description=request.description,
            template_type=request.template_type,
            package_name=request.package_name,
            class_name=request.class_name,
            additional_context=request.additional_context
        )
        logger.info(f"✅ Kotlin генерация: {request.class_name} ({request.template_type or 'custom'})")
        return {"status": "ok", **result}
    except Exception as e:
        logger.error(f"❌ Ошибка генерации Kotlin: {e}")
        raise HTTPException(status_code=500, detail=str(e))


async def kotlin_edit(request: KotlinEditRequest, base_dir: str = Depends(get_base_dir)) -> dict:
    """POST /kotlin/edit"""
    try:
        assistant = _get_assistant(str(base_dir))
        result = assistant.edit_code(
            existing_code=request.existing_code,
            instructions=request.instructions,
            file_path=request.file_path
        )
        logger.info(f"✅ Kotlin редактирование: {len(request.existing_code)} символов")
        return {"status": "ok", **result}
    except Exception as e:
        logger.error(f"❌ Ошибка редактирования Kotlin: {e}")
        raise HTTPException(status_code=500, detail=str(e))


async def kotlin_analyze(request: KotlinAnalyzeRequest, base_dir: str = Depends(get_base_dir)) -> dict:
    """POST /kotlin/analyze"""
    try:
        assistant = _get_assistant(str(base_dir))
        result = assistant.analyze_code(code=request.code, file_path=request.file_path)
        logger.info(f"✅ Kotlin анализ: {result['metrics'].get('lines', 0)} строк, {len(result['errors'])} ошибок")
        return {"status": "ok", **result}
    except Exception as e:
        logger.error(f"❌ Ошибка анализа Kotlin: {e}")
        raise HTTPException(status_code=500, detail=str(e))


async def kotlin_refactor(request: KotlinRefactorRequest, base_dir: str = Depends(get_base_dir)) -> dict:
    """POST /kotlin/refactor"""
    try:
        assistant = _get_assistant(str(base_dir))
        result = assistant.refactor_code(
            code=request.code,
            refactor_type=request.refactor_type,
            file_path=request.file_path
        )
        logger.info(f"✅ Kotlin рефакторинг: {request.refactor_type}")
        return {"status": "ok", **result}
    except Exception as e:
        logger.error(f"❌ Ошибка рефакторинга Kotlin: {e}")
        raise HTTPException(status_code=500, detail=str(e))


async def kotlin_autocomplete(request: KotlinAutocompleteRequest, base_dir: str = Depends(get_base_dir)) -> dict:
    """POST /kotlin/autocomplete"""
    try:
        assistant = _get_assistant(str(base_dir))
        result = assistant.autocomplete(
            code_prefix=request.code_prefix,
            context=request.context
        )
        logger.info(f"✅ Kotlin автодополнение: {len(result['suggestions'])} вариантов")
        return {"status": "ok", **result}
    except Exception as e:
        logger.error(f"❌ Ошибка автодополнения Kotlin: {e}")
        raise HTTPException(status_code=500, detail=str(e))


async def kotlin_context_save(request: KotlinContextRequest, base_dir: str = Depends(get_base_dir)) -> dict:
    """POST /kotlin/context/save"""
    try:
        assistant = _get_assistant(str(base_dir))
        assistant.store_context(file_path=request.file_path, code=request.code)
        logger.info(f"✅ Kotlin контекст сохранён: {request.file_path}")
        return {"status": "ok", "detail": f"Контекст сохранён: {request.file_path}"}
    except Exception as e:
        logger.error(f"❌ Ошибка сохранения контекста: {e}")
        raise HTTPException(status_code=500, detail=str(e))


async def kotlin_context_get(file_path: str, base_dir: str = Depends(get_base_dir)) -> dict:
    """GET /kotlin/context/get/{file_path}"""
    try:
        assistant = _get_assistant(str(base_dir))
        code = assistant.get_context(file_path)
        if code:
            return {"status": "ok", "file_path": file_path, "code": code}
        return {"status": "not_found", "detail": f"Контекст не найден: {file_path}"}
    except Exception as e:
        logger.error(f"❌ Ошибка получения контекста: {e}")
        raise HTTPException(status_code=500, detail=str(e))


async def kotlin_context_clear(base_dir: str = Depends(get_base_dir)) -> dict:
    """POST /kotlin/context/clear"""
    try:
        assistant = _get_assistant(str(base_dir))
        assistant.clear_context()
        logger.info("✅ Kotlin контекст очищен")
        return {"status": "ok", "detail": "Контекст очищен"}
    except Exception as e:
        logger.error(f"❌ Ошибка очистки контекста: {e}")
        raise HTTPException(status_code=500, detail=str(e))


async def kotlin_templates(base_dir: str = Depends(get_base_dir)) -> dict:
    """GET /kotlin/templates"""
    try:
        from utils.kotlin_assistant import KotlinAssistant
        assistant = KotlinAssistant(project_root=str(base_dir))
        templates = list(assistant.templates.keys())
        return {
            "status": "ok",
            "templates": templates,
            "description": {
                "activity": "Android Activity", "fragment": "Android Fragment",
                "viewmodel": "Android ViewModel", "repository": "Repository pattern",
                "dataclass": "Data class", "retrofit_api": "Retrofit API interface",
                "room_dao": "Room DAO interface", "singleton": "Singleton object",
                "coroutine_worker": "CoroutineWorker", "compose_ui": "Jetpack Compose UI",
                "compose_viewmodel": "Compose ViewModel", "dependency_injection": "Koin DI module",
                "navigation_graph": "Navigation Compose"
            }
        }
    except Exception as e:
        logger.error(f"❌ Ошибка получения шаблонов: {e}")
        raise HTTPException(status_code=500, detail=str(e))


async def kotlin_explain(request: KotlinAnalyzeRequest, base_dir: str = Depends(get_base_dir)) -> dict:
    """POST /kotlin/explain"""
    try:
        assistant = _get_assistant(str(base_dir))
        result = assistant.explain_code(code=request.code, file_path=request.file_path)
        logger.info(f"✅ Kotlin объяснение: {result.get('lines', 0)} строк")
        return {"status": "ok", **result}
    except Exception as e:
        logger.error(f"❌ Ошибка объяснения Kotlin: {e}")
        raise HTTPException(status_code=500, detail=str(e))
