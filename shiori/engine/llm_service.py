"""
LLM Service — сервис для работы с моделями Qwen2.5.

Использует:
  - Qwen2.5-3B для общих задач (общение, характер, анализ)
  - Qwen2.5-Coder-3B для кода (патчи, анализ уязвимостей)
"""

from __future__ import annotations

import logging
import os
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional

from shiori.engine.config import ShioriConfig

# Определяем корень проекта для корректных путей к моделям
_PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent.parent
if str(_PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT))


def _resolve_model_path(relative_path: str) -> str:
    """
    Преобразует относительный путь к модели в абсолютный.
    Если модель не найдена локально — возвращает HF ID.
    """
    local = Path(relative_path)
    
    # Список всех возможных корней проекта
    candidates = [
        _PROJECT_ROOT,
        Path.cwd(),  # текущая рабочая директория
        Path(__file__).resolve().parent.parent.parent,  # один уровень выше shiori/engine
        Path("/app"),  # стандартный путь в Docker
        Path("/"),     # корень файловой системы
    ]
    
    for root in candidates:
        abs_path = root / relative_path
        if abs_path.exists():
            resolved = str(abs_path)
            if resolved != relative_path:
                return resolved
    
    # Fallback — HuggingFace
    if "qwen2.5-coder" in relative_path:
        return "Qwen/Qwen2.5-Coder-3B-Instruct"
    return "Qwen/Qwen2.5-3B-Instruct"


class ShioriLLMService:
    """
    Сервис для работы с LLM моделями в системе Шиори.
    
    Загружает и управляет двумя моделями:
    - General: Qwen2.5-3B (общие задачи)
    - Coder: Qwen2.5-Coder-3B (работа с кодом)
    """
    
    def __init__(self, config: ShioriConfig):
        self.config = config
        self.logger = logging.getLogger("ShioriLLM")
        
        # Атрибуты могут быть None до загрузки моделей
        self.general_model: Optional[Any] = None
        self.general_tokenizer: Optional[Any] = None
        self.coder_model: Optional[Any] = None
        self.coder_tokenizer: Optional[Any] = None
        
        self.general_loaded = False
        self.coder_loaded = False
        
        if os.environ.get("SHIORI_LLM_ENABLED", "1") != "1":
            self.logger.info("⚠️ LLM Shiori отключена (SHIORI_LLM_ENABLED=0)")
            return
        self._load_models()
    
    def _load_models(self):
        """Загрузить обе модели."""
        try:
            import torch
            from transformers import AutoModelForCausalLM, AutoTokenizer
            
            self.logger.info("🔄 Загрузка LLM моделей...")
            
            # Загрузка General модели (Qwen2.5-3B)
            self.logger.info(f"📥 Загрузка General модели: {self.config.general_model_path}")
            
            model_id = _resolve_model_path(self.config.general_model_path)
            self.logger.info(f"📂 Используем модель: {model_id}")
            
            try:
                self.general_tokenizer = AutoTokenizer.from_pretrained(
                    model_id,
                    trust_remote_code=True,
                    local_files_only=Path(model_id).exists(),
                )
                
                # Пытаемся использовать 4-bit квантизацию для экономии памяти
                if torch.cuda.is_available():
                    try:
                        from transformers import BitsAndBytesConfig
                        quantization_config = BitsAndBytesConfig(
                            load_in_4bit=True,
                            bnb_4bit_compute_dtype=torch.float16,
                            bnb_4bit_quant_type="nf4",
                            bnb_4bit_use_double_quant=True,
                        )
                        self.general_model = AutoModelForCausalLM.from_pretrained(
                            model_id,
                            quantization_config=quantization_config,
                            device_map="auto",
                            trust_remote_code=True,
                            local_files_only=Path(model_id).exists(),
                        )
                        self.logger.info("✅ General модель загружена с 4-bit квантизацией")
                    except ImportError:
                        self.logger.warning("⚠️ bitsandbytes не установлен, загружаю без квантизации...")
                        self.general_model = AutoModelForCausalLM.from_pretrained(
                            model_id,
                            torch_dtype=torch.float16,
                            device_map="auto",
                            trust_remote_code=True,
                            local_files_only=Path(model_id).exists(),
                        )
                        self.logger.info("✅ General модель загружена (float16)")
                    except Exception as e:
                        self.logger.warning(f"⚠️ Ошибка квантизации ({e}), пробую без неё...")
                        self.general_model = AutoModelForCausalLM.from_pretrained(
                            model_id,
                            torch_dtype=torch.float16,
                            device_map="auto",
                            trust_remote_code=True,
                            local_files_only=Path(model_id).exists(),
                        )
                        self.logger.info("✅ General модель загружена (float16, fallback)")
                else:
                    self.general_model = AutoModelForCausalLM.from_pretrained(
                        model_id,
                        torch_dtype=torch.float32,
                        device_map=None,
                        trust_remote_code=True,
                        local_files_only=Path(model_id).exists(),
                    )
                    self.logger.info("✅ General модель загружена (CPU, float32)")
                
                self.general_loaded = True
            except Exception as e:
                self.logger.error(f"❌ Ошибка загрузки General модели: {e}")
            
            # Загрузка Coder модели (Qwen2.5-Coder-3B)
            self.logger.info(f"📥 Загрузка Coder модели: {self.config.coder_model_path}")
            
            coder_id = _resolve_model_path(self.config.coder_model_path)
            self.logger.info(f"📂 Используем Coder модель: {coder_id}")
            
            try:
                self.coder_tokenizer = AutoTokenizer.from_pretrained(
                    coder_id,
                    trust_remote_code=True,
                    local_files_only=Path(coder_id).exists(),
                )
                
                # Пытаемся использовать 4-bit квантизацию для экономии памяти
                if torch.cuda.is_available():
                    try:
                        from transformers import BitsAndBytesConfig
                        quantization_config = BitsAndBytesConfig(
                            load_in_4bit=True,
                            bnb_4bit_compute_dtype=torch.float16,
                            bnb_4bit_quant_type="nf4",
                            bnb_4bit_use_double_quant=True,
                        )
                        self.coder_model = AutoModelForCausalLM.from_pretrained(
                            coder_id,
                            quantization_config=quantization_config,
                            device_map="auto",
                            trust_remote_code=True,
                            local_files_only=Path(coder_id).exists(),
                        )
                        self.logger.info("✅ Coder модель загружена с 4-bit квантизацией")
                    except ImportError:
                        self.logger.warning("⚠️ bitsandbytes не установлен, загружаю без квантизации...")
                        self.coder_model = AutoModelForCausalLM.from_pretrained(
                            coder_id,
                            torch_dtype=torch.float16,
                            device_map="auto",
                            trust_remote_code=True,
                            local_files_only=Path(coder_id).exists(),
                        )
                        self.logger.info("✅ Coder модель загружена (float16)")
                    except Exception as e:
                        self.logger.warning(f"⚠️ Ошибка квантизации ({e}), пробую без неё...")
                        self.coder_model = AutoModelForCausalLM.from_pretrained(
                            coder_id,
                            torch_dtype=torch.float16,
                            device_map="auto",
                            trust_remote_code=True,
                            local_files_only=Path(coder_id).exists(),
                        )
                        self.logger.info("✅ Coder модель загружена (float16, fallback)")
                else:
                    self.coder_model = AutoModelForCausalLM.from_pretrained(
                        coder_id,
                        torch_dtype=torch.float32,
                        device_map=None,
                        trust_remote_code=True,
                        local_files_only=Path(coder_id).exists(),
                    )
                    self.logger.info("✅ Coder модель загружена (CPU, float32)")
                
                self.coder_loaded = True
            except Exception as e:
                self.logger.error(f"❌ Ошибка загрузки Coder модели: {e}")
                
        except ImportError:
            self.logger.error("❌ transformers или torch не установлены")
        except Exception as e:
            self.logger.error(f"❌ Ошибка инициализации LLM: {e}")
    
    def generate_general(self, prompt: str, system_prompt: str = None) -> str:
        """
        Генерация ответа для общих задач.
        
        Args:
            prompt: пользовательский запрос
            system_prompt: системный контекст
            
        Returns:
            Сгенерированный текст
        """
        if not self.general_loaded:
            return "[LLM не доступна] Используйте fallback ответ"
        
        # Гарантируем, что tokenizer и model не None (проверено выше)
        assert self.general_tokenizer is not None, "Tokenizer должен быть загружен"
        assert self.general_model is not None, "Model должен быть загружен"
        
        try:
            messages = []
            if system_prompt:
                messages.append({"role": "system", "content": system_prompt})
            messages.append({"role": "user", "content": prompt})
            
            # Форматирование в формат Qwen
            text = self.general_tokenizer.apply_chat_template(
                messages, tokenize=False, add_generation_prompt=True
            )
            
            inputs = self.general_tokenizer(text, return_tensors="pt")
            
            # Переносим на правильное устройство
            if hasattr(self.general_model, 'device'):
                inputs = {k: v.to(self.general_model.device) for k, v in inputs.items()}
            elif hasattr(self.general_model, 'parameters'):
                # Для квантованных моделей
                first_param = next(self.general_model.parameters())
                inputs = {k: v.to(first_param.device) for k, v in inputs.items()}
            
            # Генерация
            output = self.general_model.generate(
                **inputs,
                max_new_tokens=self.config.model_max_tokens,
                temperature=self.config.model_temperature,
                do_sample=True,
                pad_token_id=self.general_tokenizer.eos_token_id
            )
            
            # Извлечение ответа
            generated_text = self.general_tokenizer.decode(
                output[0][inputs["input_ids"].shape[1]:],
                skip_special_tokens=True
            )
            
            return generated_text.strip()
            
        except Exception as e:
            self.logger.error(f"❌ Ошибка генерации General: {e}")
            return f"[Ошибка LLM General: {str(e)}]"
    
    def generate_coder(self, prompt: str, code_context: str = None) -> str:
        """
        Генерация ответа для кода.
        
        Args:
            prompt: запрос по коду
            code_context: контекст кода (опционально)
            
        Returns:
            Сгенерированный код или ответ
        """
        if not self.coder_loaded:
            return "# [LLM Coder не доступна] Fallback код"
        
        # Гарантируем, что tokenizer и model не None (проверено выше)
        assert self.coder_tokenizer is not None, "Tokenizer должен быть загружен"
        assert self.coder_model is not None, "Model должен быть загружен"
        
        try:
            # Формирование промпта для кодера
            full_prompt = f"Ты — помощник по программированию. Напиши код или ответь на вопрос.\n\n"
            if code_context:
                full_prompt += f"Контекст:\n{code_context}\n\n"
            full_prompt += f"Задание:\n{prompt}"
            
            inputs = self.coder_tokenizer(full_prompt, return_tensors="pt")
            
            # Переносим на правильное устройство
            if hasattr(self.coder_model, 'device'):
                inputs = {k: v.to(self.coder_model.device) for k, v in inputs.items()}
            elif hasattr(self.coder_model, 'parameters'):
                # Для квантованных моделей
                first_param = next(self.coder_model.parameters())
                inputs = {k: v.to(first_param.device) for k, v in inputs.items()}
            
            # Генерация
            output = self.coder_model.generate(
                **inputs,
                max_new_tokens=self.config.model_max_tokens,
                temperature=self.config.model_temperature,
                do_sample=True,
                pad_token_id=self.coder_tokenizer.eos_token_id
            )
            
            # Извлечение ответа
            generated_text = self.coder_tokenizer.decode(
                output[0][inputs["input_ids"].shape[1]:],
                skip_special_tokens=True
            )
            
            return generated_text.strip()
            
        except Exception as e:
            self.logger.error(f"❌ Ошибка генерации Coder: {e}")
            return f"# [Ошибка LLM Coder: {str(e)}]"
    
    def is_available(self, model_type: str = "general") -> bool:
        """Проверить доступность модели."""
        if model_type == "coder":
            return self.coder_loaded
        return self.general_loaded
    
    def get_status(self) -> Dict[str, Any]:
        """Получить статус моделей."""
        return {
            "general_loaded": self.general_loaded,
            "coder_loaded": self.coder_loaded,
            "general_model": self.config.general_model_path,
            "coder_model": self.config.coder_model_path,
            "device": self.config.model_device,
        }
