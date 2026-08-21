# api/endpoints/ayiko.py — Эндпоинты генерации изображений и души Айко

import logging
from datetime import datetime
from typing import Any, Optional

from fastapi import HTTPException, Request
from fastapi.responses import FileResponse

from api.schemas import (
    AyikoGenerateRequest,
    AyikoContemplateRequest,
    AyikoFeelRequest,
    AyikoDecideRequest,
    AyikoIntentionRequest,
    ScanRequest,
    OjidaniaAnalyzeRequest,
    BatchAnalyzeOjidaniaRequest,
)

logger = logging.getLogger("ayiko")

# Глобальные генераторы
ayiko_generator: Any = None
ayiko_professional: Any = None
ayiko_core: Any = None
shiori_scanner: Any = None
ojidania_analyzer: Any = None


async def init_ayiko():
    """Инициализация генераторов Айко и Шиори."""
    global ayiko_generator, ayiko_professional, ayiko_core, shiori_scanner, ojidania_analyzer
    
    try:
        from ayiko.professional_generator import AyikoProfessionalGenerator
        ayiko_professional = AyikoProfessionalGenerator()
        logger.info("✅ Ayiko Professional Generator v4.0 инициализирован")
    except (ImportError, Exception) as e:
        logger.warning(f"⚠️ Module ayiko.professional_generator not found: {e}")
    
    try:
        from ayiko.image_generator import AyikoImageGenerator
        ayiko_generator = AyikoImageGenerator()
        logger.info("✅ Базовый генератор изображений Айко инициализирован")
    except (ImportError, Exception) as e:
        logger.warning(f"⚠️ Module ayiko.image_generator not found: {e}")
    
    try:
        from ayiko.engine import AyikoCore
        from ayiko.engine.config import AyikoConfig
        ayiko_config = AyikoConfig.default()
        ayiko_core = AyikoCore(config=ayiko_config)
        logger.info("✅ AyikoCore initialized")
    except (ImportError, Exception) as e:
        logger.warning(f"⚠️ Module ayiko.engine not found: {e}")
    
    try:
        from shiori.wordpress_scanner import WordPressScanner
        shiori_scanner = WordPressScanner()
        logger.info("✅ Scanner Shiori initialized")
    except (ImportError, Exception) as e:
        logger.warning(f"⚠️ Module shiori.wordpress_scanner not found: {e}")
    
    try:
        from ayiko.ojidania_analyzer import OjidaniaAnalyzer
        ojidania_analyzer = OjidaniaAnalyzer()
        logger.info("✅ Ojidania Analyzer initialized")
    except (ImportError, Exception) as e:
        logger.warning(f"⚠️ Module ayiko.ojidania_analyzer not found: {e}")


def _check_generator():
    if ayiko_generator is None:
        raise HTTPException(status_code=503, detail="Генератор не инициализирован")


async def ayiko_generate_image(req: AyikoGenerateRequest) -> dict:
    """POST /ayiko/generate — Генерация изображения."""
    _check_generator()

    try:
        img_type = req.type

        if img_type == "pixel":
            img = ayiko_generator.generate_pixel_art(
                size=req.size or 64,
                style=req.style or "character",
                palette=req.palette or "retro"
            )
        elif img_type == "technical":
            img = ayiko_generator.generate_technical_drawing(
                size=(512, 512),
                type=req.technical_type or "circuit"
            )
        elif img_type == "description":
            result = ayiko_generator.generate_from_description(req.description or "")
            return {"status": "success", "message": "Изображение сгенерировано", "data": result}
        elif img_type == "character":
            character_desc = req.character or {}
            if not character_desc:
                raise HTTPException(status_code=400, detail="Отсутствует описание персонажа")

            for color_key in ("skin_color", "hair_color", "eye_color"):
                if color_key in character_desc and isinstance(character_desc[color_key], list):
                    character_desc[color_key] = tuple(character_desc[color_key])

            img = ayiko_generator.generate_character_from_description(
                description=character_desc,
                size=tuple(req.size or [512, 512]),
                style=req.style or "realistic"
            )

            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"ayiko_{character_desc.get('name', 'character')}_{timestamp}.png"
            filepath = ayiko_generator.output_dir / filename
            img.save(filepath)

            return {"status": "success", "message": "Персонаж сгенерирован", "filename": filename, "size": img.size, "format": "PNG"}
        else:
            raise HTTPException(status_code=400, detail=f"Неизвестный тип: {img_type}")

        # Сохраняем и возвращаем (для старых типов)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"ayiko_{timestamp}.png"
        filepath = ayiko_generator.output_dir / filename
        img.save(filepath)

        return {"status": "success", "message": "Изображение сгенерировано", "filename": filename, "size": img.size, "format": "PNG"}

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Ошибка генерации: {e}")
        raise HTTPException(status_code=500, detail=str(e))


async def ayiko_stats() -> dict:
    """GET /ayiko/stats — Статистика."""
    _check_generator()
    return ayiko_generator.get_stats()


async def ayiko_get_image(image_id: str) -> FileResponse:
    """GET /ayiko/generate/{image_id} — Получить изображение."""
    _check_generator()
    filepath = ayiko_generator.output_dir / f"{image_id}.png"
    if not filepath.exists():
        raise HTTPException(status_code=404, detail="Изображение не найдено")
    return FileResponse(filepath, media_type="image/png")


async def ayiko_soul_profile() -> dict:
    """GET /ayiko/soul — Профиль души."""
    if ayiko_core is None:
        raise HTTPException(status_code=503, detail="AyikoCore не инициализирован")
    try:
        return ayiko_core.get_full_soul_profile()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


async def ayiko_contemplate(req: AyikoContemplateRequest) -> dict:
    """POST /ayiko/contemplate — Размышление."""
    if ayiko_core is None:
        raise HTTPException(status_code=503, detail="AyikoCore не инициализирован")
    try:
        return ayiko_core.contemplate(req.topic)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


async def ayiko_feel(req: AyikoFeelRequest) -> dict:
    """POST /ayiko/feel — Эмоция."""
    if ayiko_core is None:
        raise HTTPException(status_code=503, detail="AyikoCore не инициализирован")
    try:
        return ayiko_core.feel(req.trigger, req.intensity)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


async def ayiko_emotions() -> dict:
    """GET /ayiko/emotions — Текущие эмоции."""
    if ayiko_core is None:
        raise HTTPException(status_code=503, detail="AyikoCore не инициализирован")
    try:
        return ayiko_core.express_emotions()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


async def ayiko_diary() -> dict:
    """GET /ayiko/diary — Дневник."""
    if ayiko_core is None:
        raise HTTPException(status_code=503, detail="AyikoCore не инициализирован")
    try:
        return {"diary": ayiko_core.write_diary()}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


async def ayiko_ambitions() -> dict:
    """GET /ayiko/ambitions — Амбиции."""
    if ayiko_core is None:
        raise HTTPException(status_code=503, detail="AyikoCore не инициализирован")
    try:
        return {"ambitions": ayiko_core.express_ambition(), "progress": ayiko_core.get_progress()}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


async def ayiko_decide(req: AyikoDecideRequest) -> dict:
    """POST /ayiko/decide — Принятие решения."""
    if ayiko_core is None:
        raise HTTPException(status_code=503, detail="AyikoCore не инициализирован")
    try:
        return ayiko_core.make_decision(req.situation, req.options)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


async def ayiko_intention(req: AyikoIntentionRequest) -> dict:
    """POST /ayiko/intention — Намерение."""
    if ayiko_core is None:
        raise HTTPException(status_code=503, detail="AyikoCore не инициализирован")
    try:
        return ayiko_core.set_intention(req.intention, req.priority)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# === Shiori endpoints ===

async def shiori_scan_request(req: ScanRequest) -> dict:
    """POST /shiori/scan — Сканирование запроса."""
    if shiori_scanner is None:
        raise HTTPException(status_code=503, detail="Сканер Шиори не инициализирован")
    try:
        result = shiori_scanner.scan_request(req.model_dump())
        if result.get("is_attack"):
            logger.warning(f"SECURITY Attack detected: {result.get('attack_type')} from {req.ip}")
            if result.get("action") == "block_ip":
                ip = req.ip or "unknown"
                from config import BLOCK_DURATION
                from datetime import datetime
                from services.security import blocked_ips
                blocked_ips[ip] = datetime.now() + BLOCK_DURATION
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


async def shiori_stats() -> dict:
    """GET /shiori/stats."""
    if shiori_scanner is None:
        raise HTTPException(status_code=503, detail="Сканер Шиори не инициализирован")
    return shiori_scanner.get_stats()


async def shiori_report() -> dict:
    """GET /shiori/report."""
    if shiori_scanner is None:
        raise HTTPException(status_code=503, detail="Сканер Шиори не инициализирован")
    return shiori_scanner.generate_report()


async def shiori_unblock_ip(ip: str, request: Request, RETRAIN_TOKEN: str | None) -> dict:
    """POST /shiori/unblock/{ip}."""
    if shiori_scanner is None:
        raise HTTPException(status_code=503, detail="Сканер Шиори не инициализирован")
    token = request.headers.get("X-Retrain-Token")
    if token != RETRAIN_TOKEN:
        raise HTTPException(status_code=403, detail="Неверный токен")
    success = shiori_scanner.unblock_ip(ip)
    if success:
        return {"status": "success", "message": f"IP {ip} unblocked"}
    raise HTTPException(status_code=404, detail="IP not found in blocked list")


# === Ojidania endpoints ===

async def analyze_ojidania_image(req: OjidaniaAnalyzeRequest) -> dict:
    """POST /ayiko/ojidania/analyze — Анализ изображения."""
    if ojidania_analyzer is None:
        raise HTTPException(status_code=503, detail="Анализатор Ojidania не инициализирован")
    try:
        result = ojidania_analyzer.analyze_image(req.image_path)
        if "error" in result:
            raise HTTPException(status_code=400, detail=result["error"])
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


async def batch_analyze_ojidania(req: BatchAnalyzeOjidaniaRequest) -> dict:
    """POST /ayiko/ojidania/batch."""
    if ojidania_analyzer is None:
        raise HTTPException(status_code=503, detail="Анализатор Ojidania не инициализирован")
    try:
        results = ojidania_analyzer.batch_analyze(req.directory)
        return {"status": "success", "count": len(results), "results": results, "stats": ojidania_analyzer.get_stats()}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


async def ojidania_stats() -> dict:
    """GET /ayiko/ojidania/stats."""
    if ojidania_analyzer is None:
        raise HTTPException(status_code=503, detail="Анализатор Ojidania не инициализирован")
    return ojidania_analyzer.get_stats()


async def ojidania_knowledge() -> dict:
    """GET /ayiko/ojidania/knowledge."""
    if ojidania_analyzer is None:
        raise HTTPException(status_code=503, detail="Анализатор Ojidania не инициализирован")
    return ojidania_analyzer.knowledge
