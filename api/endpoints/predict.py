# api/endpoints/predict.py — Эндпоинт /predict (основной чат)

import json
import re
import textwrap
import logging
import asyncio
from typing import List, Dict

from fastapi import Request, HTTPException
from fastapi.responses import JSONResponse

from services.model_loader import get_qwen_cache
from api.schemas import MessageItem, ChatRequest

logger = logging.getLogger("predict")


# Импорты для обнаружения режимов и параметров человека
from utils.human_params import HumanParamsDetector


def detect_rpg_mode(messages: List[MessageItem]) -> str:
    """Автоматическое определение RPG-режима по контексту."""
    context_snippet = "\n".join([
        m.message.lower() for m in messages[-2:]
    ])

    rpg_keywords = {
        "hp", "здоровье", "урон", "атака", "защита", "шанс", "пробой",
        "инвентарь", "предмет", "золото", "эксп", " xp ", "lvl", "уровень",
        "локация", "место", "пещера", "лес", "город", "дом", "таверна",
        "враг", "монстр", "гоблин", "орк", "дракон", "скелет", "призрак",
        "шаг", "идти", "бежать", "осмотреться", "взять", "схватить",
        "схватка", "борьба", "драка", "выстрел", "заклинание", "магия",
        "класс", "рыцарь", "маг", "вор", "паладин", "жрец", "некромант"
    }

    if any(kw in context_snippet for kw in rpg_keywords):
        return "rpg"
    
    # Специфичные фразы → narrative/world_gen/world
    if any(kw in context_snippet for kw in ["создай", "мир", "вселенная"]):
        return "world" if ("жанр" in context_snippet or "тег" in context_snippet) else ("world_gen" if "жанр" in context_snippet else "narrative")

    return "chat"


async def predict_endpoint(request: Request, req: ChatRequest) -> JSONResponse:
    """Основной эндпоинт: /predict, /chat, и корень /"""
    start_time = asyncio.get_event_loop().time()
    logger.info(f"📥 Запрос | UA: {request.headers.get('User-Agent', 'unknown')}")

    # === Определение запроса от приложения Академии Барстон ===
    barston_prompt = None
    try:
        from barston_lore_loader import get_barston_system_prompt, is_barston_request
        user_agent = request.headers.get("User-Agent", "")
        if is_barston_request(user_agent):
            barston_prompt = get_barston_system_prompt()
            logger.info(f"🏰 Запрос от Академии Барстон — лор инъецирован ({len(barston_prompt)} символов)")
    except Exception as e:
        logger.error(f"❌ Ошибка загрузки лора Барстон: {e}")

    logger.info(f"✅ Запрос валидирован | mode={req.mode}, count={len(req.messages)}")

    if not req.messages:
        logger.warning("⚠️ История пуста")
        raise HTTPException(status_code=422, detail="История сообщений пуста")
    if len(req.messages) > 32:
        logger.warning(f"⚠️ Слишком длинная история: {len(req.messages)}")
        raise HTTPException(status_code=422, detail="Слишком длинная история (макс. 32 сообщения)")

    # 🔁 Автоматическое определение RPG-режима
    mode = req.mode
    if mode == "chat":
        detected = detect_rpg_mode(req.messages)
        if detected in ["rpg", "world_gen", "narrative"]:
            logger.info(f"➡️ Переключено с 'chat' → '{detected}' (RPG-сигналы)")
            mode = detected
    
    # === Определение параметров человека ===
    messages_dicts = [{"message": m.message, "is_own": m.is_own} for m in req.messages]
    params = HumanParamsDetector.detect_all_params(messages_dicts)
    logger.info(f"👤 Параметры: пол={params.gender}, возраст={params.age}({params.age_years})")

    # Безопасное получение chatbot
    local_bot = get_qwen_cache()
    if local_bot is None:
        logger.warning("⚠️ Модель ещё загружается, жду до 30 сек...")
        for i in range(60):
            await asyncio.sleep(0.5)
            local_bot = get_qwen_cache()
            if local_bot is not None:
                logger.info("✅ Модель загрузилась, продолжаем...")
                break
        else:
            logger.error("❌ chatbot не загружен за 30 сек")
            raise HTTPException(status_code=503, detail="Модель ещё загружается, попробуйте через минуту")

    # === Генерация по режимам ===
    try:
        start_gen = asyncio.get_event_loop().time()
        response = ""

        if mode == "world":
            logger.info("🔧 Режим: world (создание мира)")
            if not hasattr(local_bot, 'world_engine') or not local_bot.world_engine_enabled:
                raise HTTPException(status_code=503, detail="WorldEngine не доступен")
            
            genre = "Фэнтези"
            tag = ""
            genre_match = re.search(r"Жанр[:\s]+([^.\n]+)", req.messages[-1].message, re.IGNORECASE)
            if genre_match:
                genre = genre_match.group(1).strip()
            else:
                genre = req.messages[-1].message.strip()[:50]
            
            tag_match = re.search(r"Тег[:\s]+([^.\n]+)", req.messages[-1].message, re.IGNORECASE)
            if tag_match:
                tag = tag_match.group(1).strip()
            
            result = local_bot.create_world(genre, tag)
            response = json.dumps({"response": result}, ensure_ascii=False)

        elif mode == "narrative":
            logger.info("🔧 Режим: narrative")
            context = "\n".join([
                f"{'Пользователь' if m.is_own else 'Бот'}: {m.message}"
                for m in req.messages
            ])
            prompt_text = textwrap.dedent(f"""
                Ты — писатель-сценарист. Пиши атмосферные сцены в стиле научной фантастики/драмы.
                Отвечай только на русском языке.

                Строгий формат ответа:
                **Локация — Время**
                Описание окружения и действий персонажей.
                «Диалог» — описание действия говорящего.
                *Внутренние мысли в курсиве.*

                История диалога:
                {context}

                Бот:
            """).strip()
            
            HumanParamsDetector.apply_params_to_bot(local_bot, params)
            response = local_bot.generate_response([{"message": prompt_text, "is_own": True}], mode="chat", system_prompt=barston_prompt).strip()

            if len(response) < 20:
                response = "*Фигура медленно обернулась* 'ты... вернулся... *(внутренне: сердце сжалось)*'"
                logger.warning("⚠️ Слишком короткий ответ → fallback")

        elif mode == "world_gen":
            logger.info("🔧 Режим: world_gen")
            last_msg = req.messages[-1].message
            
            genre = "Фэнтези"
            tag = ""
            genre_match = re.search(r"Жанр[:\s]+([^.;\n]+)", last_msg, re.IGNORECASE)
            if genre_match:
                genre = genre_match.group(1).strip()
            else:
                genre = last_msg.strip()[:50]
            
            tag_match = re.search(r"Тег[иае]*[:\s]+([^.;\n]+)", last_msg, re.IGNORECASE)
            if tag_match:
                tag = tag_match.group(1).strip()
            
            try:
                response = local_bot.generate_response(
                    [{"message": last_msg, "is_own": True}],
                    mode="world_gen"
                )
                parsed = json.loads(response)
                response = parsed.get("world", parsed.get("response", ""))
                logger.info(f"📚 world_gen: сгенерирован мир '{genre}' (тег: '{tag}')")
            except (ImportError, json.JSONDecodeError, Exception) as e:
                logger.warning(f"⚠️ world_gen fallback: {e}")
                response = f"В мире {genre} {tag if tag else 'что-то необычное'} происходит магия. Ты стоишь перед городом..."
            
            HumanParamsDetector.apply_params_to_bot(local_bot, params)

        elif mode == "rpg":
            logger.info("🔧 Режим: rpg")
            valid_msgs = [{"message": m.message, "is_own": m.is_own} for m in req.messages]
            HumanParamsDetector.apply_params_to_bot(local_bot, params)
            response = local_bot.generate_response(valid_msgs, mode="rpg", system_prompt=barston_prompt).strip()

        elif mode == "continue":
            logger.info("🔧 Режим: continue")
            valid_msgs = [{"message": m.message, "is_own": m.is_own} for m in req.messages]
            HumanParamsDetector.apply_params_to_bot(local_bot, params)
            response = local_bot.generate_response(valid_msgs, mode="continue", system_prompt=barston_prompt).strip()

            if not response:
                import random
                response = random.choice(["Это важно...", "Ты прав...", "Может быть...", "Интересно..."])
                logger.warning("⚠️ Пустой ответ → fallback")

        else:  # chat
            logger.info("🔧 Режим: chat")
            valid_msgs = [{"message": m.message, "is_own": m.is_own} for m in req.messages]
            HumanParamsDetector.apply_params_to_bot(local_bot, params)
            response = local_bot.generate_response(valid_msgs, mode="chat", memory_data=req.memory_data, system_prompt=barston_prompt).strip()

            if not response:
                response = "Я здесь! 🤖"
                logger.warning("⚠️ Пустой ответ → fallback")

            # === Двухпроходная генерация: обработка запроса к архиву памяти ===
            if req.memory_data is None and "[MEMORY_QUERY]" in response:
                m = re.search(r"\[MEMORY_QUERY\](.*?)\[/MEMORY_QUERY\]", response, re.DOTALL)
                if m:
                    try:
                        memory_query = json.loads(m.group(1).strip())
                        response = response.replace(f"[MEMORY_QUERY]{m.group(1)}[/MEMORY_QUERY]", "").strip()
                        logger.info(f"🔍 Модель запросила архив: {memory_query}")
                        return JSONResponse(content={"response": response, "memory_query": memory_query})
                    except Exception as _e:
                        logger.warning(f"⚠️ Не удалось распарсить memory_query: {_e}")

        total_elapsed = asyncio.get_event_loop().time() - start_time
        logger.info(f"✅ Ответ сгенерирован за {total_elapsed:.2f} сек | Mode: {mode} | len={len(response)}")
        return JSONResponse(content={"response": response})

    except Exception as e:
        logger.error(f"❌ Ошибка генерации: {e}", exc_info=True)
        import traceback
        error_details = traceback.format_exc()
        logger.error(f"📋 Детали ошибки: {error_details[:500]}")
        return JSONResponse(content={"response": f"Извини, произошла ошибка. ({type(e).__name__}: {str(e)[:100]})"})
