# services/model_loader.py — Загрузка и кэширование Qwen2.5-3B модели

import os
import json
import logging
from typing import Optional, Dict, Any, List

import torch
from transformers import AutoTokenizer, AutoModelForCausalLM

logger = logging.getLogger("model_loader")

_qwen_cache = None  # Кэш загруженной модели


class QwenBot:
    """Обёртка над Qwen2.5-3B моделью для совместимости с ChatBot API."""
    
    def __init__(self, tokenizer, model):
        self.tokenizer = tokenizer
        self.model = model
        self.context_enabled = False
        self.manipulation_enabled = False
        self.world_engine_enabled = False
        self.world_engine = None
    
    def generate_response(self, messages: List[Dict[str, str | bool]], mode: str = "chat", 
                          memory_data: str | None = None, system_prompt: str | None = None) -> str:
        """Генерация ответа через Qwen2.5-3B.
        
        Двухпроходная генерация:
        - Проход 1 (memory_data=None): модель может запросить архивные данные через [MEMORY_QUERY]
        - Проход 2 (memory_data!=None): модель получает архивные данные и генерирует финальный ответ
        """
        # Строим контекст
        context = []
        last_user_msg = ""
        
        for msg in messages:
            if not msg["message"].strip():
                continue
            role = "Пользователь" if msg["is_own"] else "Бот"
            context.append(f"{role}: {msg['message']}")
        
        for msg in reversed(messages):
            if msg["is_own"]:
                last_user_msg = msg["message"].strip()
                break
        
        if not last_user_msg:
            return json.dumps({"response": "Я здесь! 🤖"}, ensure_ascii=False)
        
        # Строим промпт
        context_str = "\n".join(context[-10:])  # Последние 10 сообщений
        
        # Системный промпт
        system_prefix = f"{system_prompt}\n\n" if system_prompt else ""
        
        if mode == "chat":
            if memory_data:
                # === ПРОХОД 2: финальный ответ ===
                prompt = (
                    f"{system_prefix}{context_str}\n\n"
                    f"=== АРХИВНЫЕ ДАННЫЕ ИЗ ПАМЯТИ ИГРЫ ===\n{memory_data}\n"
                    f"=== КОНЕЦ АРХИВНЫХ ДАННЫХ ===\n\n"
                    f"Используй эти архивные данные для финального ответа. "
                    f"Отвечай от имени персонажа, продолжая сцену с учётом лора, отношений "
                    f"и архивных данных выше. НЕ запрашивай [MEMORY_QUERY] — данные уже предоставлены.\n\nБот:"
                )
            else:
                # === ПРОХОД 1: модель может запросить архив через [MEMORY_QUERY] ===
                prompt = (
                    f"{system_prefix}{context_str}\n\n"
                    f"Ты — персонаж в ролевой игре. Отвечай от имени своего персонажа, "
                    f"продолжая сцену, с учётом лора и отношений.\n"
                    f"ВАЖНО: если тебе для ответа не хватает информации из архива памяти "
                    f"(хронология прошлых событий, где находится предмет, что было в локации, "
                    f"отношения с персонажем) — ты МОЖЕШЬ запросить её. Для этого начни ответ "
                    f"со строки [MEMORY_QUERY] и в ней укажи JSON с нужными данными, например:\n"
                    f"[MEMORY_QUERY]{{\"timeline\": 5}}[/MEMORY_QUERY]\n"
                    f"[MEMORY_QUERY]{{\"item\": \"ключ\"}}[/MEMORY_QUERY]\n"
                    f"[MEMORY_QUERY]{{\"location\": \"Комната Лилиан\"}}[/MEMORY_QUERY]\n"
                    f"[MEMORY_QUERY]{{\"relationship\": \"Виктор\"}}[/MEMORY_QUERY]\n"
                    f"[MEMORY_QUERY]{{\"items\": \"all\"}}[/MEMORY_QUERY]\n"
                    f"[MEMORY_QUERY]{{\"scene\": 10}}[/MEMORY_QUERY]\n"
                    f"[MEMORY_QUERY]{{\"full\": true}}[/MEMORY_QUERY]\n"
                    f"Ты можешь запросить только ОДИН запрос за раз. Если данных достаточно — "
                    f"просто отвечай как персонаж.\n\nБот:"
                )
        elif mode == "rpg":
            prompt = f"{system_prefix}{context_str}\nБот:"
        elif mode == "continue":
            prompt = f"{system_prefix}{context_str}\nБот:"
        else:
            prompt = f"{system_prefix}{context_str}\nБот:"
        
        # Генерация
        try:
            self.model.eval()
            inputs = self.tokenizer.encode(prompt, return_tensors="pt")
            
            if torch.cuda.is_available():
                inputs = inputs.to("cuda")
            
            with torch.no_grad():
                outputs = self.model.generate(
                    inputs.input_ids,
                    max_new_tokens=768,
                    temperature=0.8,
                    top_p=0.9,
                    do_sample=True,
                    pad_token_id=self.tokenizer.eos_token_id,
                    eos_token_id=self.tokenizer.eos_token_id
                )
            
            generated_ids = outputs[0][inputs.input_ids.shape[1]:]
            response = self.tokenizer.decode(generated_ids, skip_special_tokens=True)
            
            # Убираем имя "Бот:" из ответа
            if response.startswith("Бот:"):
                response = response[4:].strip()
            elif response.startswith("Пользователь:"):
                response = response[11:].strip()
            
            return response.strip()
        except Exception as e:
            logger.error(f"Ошибка генерации Qwen2.5: {e}")
            return "Я здесь! 🤖"


def load_qwen_model():
    """Загружает модель ТОЛЬКО из локальных папок (без интернета).
    
    Приоритет загрузки:
    1. models/qwen2.5-3b (Qwen2.5-3B — основная универсальная)
    """
    global _qwen_cache
    if _qwen_cache is not None:
        logger.info("📦 Использую кэшированную модель Qwen2.5-3B")
        return _qwen_cache
    
    from pathlib import Path
    BASE_DIR = Path(__file__).resolve().parent.parent
    
    # Список локальных моделей для проверки
    local_models = [
        ("models/qwen2.5-3b", "Qwen2.5-3B (основная)"),
    ]
    
    tokenizer = None
    model = None
    model_name = None
    
    for model_path, display_name in local_models:
        full_path = str(BASE_DIR / model_path)
        if not os.path.isdir(full_path) or not os.path.exists(os.path.join(full_path, "config.json")):
            continue
        
        logger.info(f"🤖 Загрузка модели: {display_name} ({full_path})...")
        try:
            # Проверяем, это Qwen2.5 или ruGPT3
            is_qwen = False
            config_path = os.path.join(full_path, "config.json")
            with open(config_path, "r", encoding="utf-8") as f:
                config = json.load(f)
                is_qwen = config.get("model_type", "").startswith("qwen")
            
            if is_qwen and torch.cuda.is_available():
                # Qwen2.5 с 4-bit квантизацией для экономии VRAM
                try:
                    from transformers import BitsAndBytesConfig
                    
                    quantization_config = BitsAndBytesConfig(
                        load_in_4bit=True,
                        bnb_4bit_compute_dtype=torch.float16,
                        bnb_4bit_quant_type="nf4",
                        bnb_4bit_use_double_quant=True,
                    )
                    
                    tokenizer = AutoTokenizer.from_pretrained(full_path, trust_remote_code=True, local_files_only=True)
                    model = AutoModelForCausalLM.from_pretrained(
                        full_path,
                        quantization_config=quantization_config,
                        device_map="auto",
                        trust_remote_code=True,
                        local_files_only=True,
                    )
                    logger.info(f"✅ {display_name} загружена с 4-bit квантизацией (экономия VRAM)")
                except ImportError:
                    logger.warning("⚠️ bitsandbytes не установлен, загружаю без квантизации...")
                    tokenizer = AutoTokenizer.from_pretrained(full_path, trust_remote_code=True, local_files_only=True)
                    model = AutoModelForCausalLM.from_pretrained(
                        full_path,
                        torch_dtype=torch.float16,
                        device_map="auto",
                        trust_remote_code=True,
                        local_files_only=True,
                    )
                    logger.info(f"✅ {display_name} загружена (float16, без квантизации)")
                except Exception as e:
                    logger.warning(f"⚠️ Ошибка квантизации ({e}), пробую без неё...")
                    tokenizer = AutoTokenizer.from_pretrained(full_path, trust_remote_code=True, local_files_only=True)
                    model = AutoModelForCausalLM.from_pretrained(
                        full_path,
                        torch_dtype=torch.float16,
                        device_map="auto",
                        trust_remote_code=True,
                        local_files_only=True,
                    )
                    logger.info(f"✅ {display_name} загружена (float16, без квантизации)")
            else:
                # Загрузка без квантизации (для дообученной модели или CPU)
                tokenizer = AutoTokenizer.from_pretrained(full_path, local_files_only=True)
                model = AutoModelForCausalLM.from_pretrained(
                    full_path,
                    torch_dtype=torch.float16 if torch.cuda.is_available() else torch.float32,
                    device_map="auto" if torch.cuda.is_available() else None,
                    local_files_only=True
                )
                logger.info(f"✅ {display_name} загружена")
            
            model_name = display_name
            break
            
        except Exception as e:
            logger.warning(f"⚠️ Не удалось загрузить {display_name}: {e}")
            continue
    
    if tokenizer is None:
        logger.warning("⚠️ Локальная модель не найдена, пытаюсь загрузить из HF кэша...")
        logger.warning("ℹ️ Модель загрузится позже через авто-загрузку или при первом запросе")
        return None
    
    if torch.cuda.is_available():
        logger.info(f"   ✅ Модель загружена на GPU: {torch.cuda.get_device_name(0)}")
    else:
        logger.info("   ✅ Модель загружена на CPU")
    
    # Оборачиваем в QwenBot
    bot = QwenBot(tokenizer, model)
    
    # Сохраняем в кэш
    _qwen_cache = bot
    logger.info("✅ Модель сохранена в кэш")
    
    return bot


def get_qwen_cache():
    """Получить кэш модели (для проверки)."""
    return _qwen_cache
