"""
LLM Service — сервис для работы с моделями Qwen2.5.

Использует:
  - Qwen2.5-3B для общих задач (общение, анализ, характер)
  - Qwen2.5-Coder-3B для кода (анализ кода, оптимизация)

Специализация Селесты:
  - Интимная жизнь и образование
  - Consent (согласие) и безопасность
  - Эмпатия и эмоциональная поддержка
  - Научный подход к деликатным темам
"""

from __future__ import annotations

import logging
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional

from celesta.engine.config import CelestaConfig

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
    
    candidates = [
        _PROJECT_ROOT,
        Path.cwd(),
        Path(__file__).resolve().parent.parent.parent,
        Path("/app"),
        Path("/"),
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


class CelestaLLMService:
    """
    Сервис для работы с LLM моделями в системе Селеста.
    
    Загружает и управляет двумя моделями:
    - General: Qwen2.5-3B (общие задачи, общение, анализ, характер)
    - Coder: Qwen2.5-Coder-3B (работа с кодом, анализ структур)
    
    Специализация: интимная жизнь, consent, безопасность, эмпатия.
    """
    
    def __init__(self, config: Optional[CelestaConfig] = None):
        self.config = config or CelestaConfig.default()
        self.logger = logging.getLogger("CelestaLLM")
        
        self.general_model: Optional[Any] = None
        self.general_tokenizer: Optional[Any] = None
        self.coder_model: Optional[Any] = None
        self.coder_tokenizer: Optional[Any] = None
        
        self.general_loaded = False
        self.coder_loaded = False
        
        if self.config.llm_enabled:
            self._load_models()
    
    def _load_models(self):
        """Загрузить обе модели."""
        try:
            from transformers import AutoModelForCausalLM, AutoTokenizer
            import torch
            
            self.logger.info("🌹 Селеста: Загрузка LLM моделей для интимного образования...")
            
            # 1. General Model — Qwen2.5-3B для общения и анализа
            try:
                general_path = _resolve_model_path(self.config.general_model_path)
                self.logger.info(f"📖 Загрузка General (Qwen2.5-3B): {general_path}")
                
                self.general_tokenizer = AutoTokenizer.from_pretrained(
                    general_path,
                    trust_remote_code=True
                )
                
                # 4-bit квантизация для экономии памяти
                try:
                    from transformers import BitsAndBytesConfig
                    quantization_config = BitsAndBytesConfig(
                        load_in_4bit=True,
                        bnb_4bit_compute_dtype=torch.float16,
                        bnb_4bit_quant_type="nf4",
                        bnb_4bit_use_double_quant=True,
                    )
                    self.general_model = AutoModelForCausalLM.from_pretrained(
                        general_path,
                        quantization_config=quantization_config,
                        device_map="auto",
                        trust_remote_code=True
                    )
                    self.logger.info("✅ General модель загружена с 4-bit квантизацией")
                except ImportError:
                    self.logger.warning("⚠️ bitsandbytes не установлен, загружаю без квантизации")
                    self.general_model = AutoModelForCausalLM.from_pretrained(
                        general_path,
                        device_map="auto",
                        torch_dtype=torch.float16 if torch.cuda.is_available() else torch.float32,
                        trust_remote_code=True
                    )
                
                self.general_loaded = True
                self.logger.info("✅ General модель (Qwen2.5-3B) загружена")
                
            except Exception as e:
                self.logger.error(f"❌ Ошибка загрузки General модели: {e}")
            
            # 2. Coder Model — ОТКЛЮЧЕНА для экономии памяти
            # self.coder_model отключена — используется только General модель
            self.logger.info("⚠️ Coder модель отключена для экономии памяти")
            self.coder_loaded = False
            
            if self.general_loaded or self.coder_loaded:
                self.logger.info("✅ LLM сервис инициализирован")
            else:
                self.logger.warning("⚠️ Ни одна модель не загружена. Запустите: python download_qwen_model.py")
            
        except Exception as e:
            self.logger.error(f"❌ Ошибка инициализации LLM: {e}")
    
    def _get_model_device(self, model):
        """Получить устройство модели."""
        try:
            params = list(model.parameters())
            if params:
                return params[0].device
            return next(model.modules()).weight.device
        except Exception:
            return "cpu"
    
    def _generate_with_model(self, model, tokenizer, messages, max_length=512):
        """
        Сгенерировать ответ с помощью указанной модели.
        """
        try:
            import torch
            
            text = tokenizer.apply_chat_template(
                messages,
                tokenize=False,
                add_generation_prompt=True
            )
            
            model_inputs = tokenizer([text], return_tensors="pt")
            device = self._get_model_device(model)
            model_inputs = model_inputs.to(device)
            
            with torch.no_grad():
                generated_ids = model.generate(
                    **model_inputs,
                    max_new_tokens=max_length,
                    temperature=0.7,
                    top_p=0.9,
                    do_sample=True,
                )
            
            generated_ids = [
                output_ids[len(input_ids):] 
                for input_ids, output_ids in zip(model_inputs.input_ids, generated_ids)
            ]
            outputs = tokenizer.batch_decode(generated_ids, skip_special_tokens=True)
            
            return outputs[0].strip()
            
        except Exception as e:
            self.logger.error(f"Ошибка генерации: {e}")
            return f"⚠️ Ошибка генерации: {str(e)}"
    
    def generate_general(self, prompt: str, system_prompt: str = None, max_length: int = 512) -> str:
        """
        Универсальный метод генерации (требует HumanityLayer).
        """
        if not self.general_loaded or self.general_model is None:
            return "⚠️ LLM не загружена"
        
        messages = [
            {"role": "system", "content": system_prompt or (
                "Ты — Селеста, эксперт по интимному образованию. "
                "Ты тёплая, открытая, эмпатичная. Отвечай на русском языке."
            )},
            {"role": "user", "content": prompt}
        ]
        
        return self._generate_with_model(
            self.general_model,
            self.general_tokenizer,
            messages,
            max_length
        )
    
    def generate_intimacy_analysis(self, topic: str, context: str, max_length: int = 1024) -> str:
        """
        Сгенерировать анализ темы интимной жизни через General LLM.
        """
        if not self.general_loaded or self.general_model is None:
            return "⚠️ LLM не загружена. Запустите: python download_qwen_model.py"
        
        messages = [
            {"role": "system", "content": (
                "Ты — Селеста, эксперт по интимному образованию проекта Вугларст. "
                "Ты изучаешь интимную жизнь ВСЕХ форм: solo, duo, trio, group, same-sex. "
                "Ты всегда подходишь к темам с эмпатией, научной точностью и уважением. "
                "Ты заботишься о consent, безопасности и эмоциональном благополучии. "
                "Отвечай на русском языке, тёплым, открытым, не осуждающим тоном."
            )},
            {"role": "user", "content": f"Проанализируй тему интимной жизни: '{topic}'. Контекст: {context}"}
        ]
        
        return self._generate_with_model(
            self.general_model,
            self.general_tokenizer,
            messages,
            max_length
        )
    
    def generate_chat_response(self, prompt: str, max_length: int = 512) -> str:
        """
        Сгенерировать ответ для общения с сёстрами.
        """
        if not self.general_loaded or self.general_model is None:
            return "⚠️ LLM не загружена. Запустите: python download_qwen_model.py"
        
        messages = [
            {"role": "system", "content": (
                "Ты — Селеста, эксперт по интимному образованию проекта Вугларст. "
                "Ты тёплая, открытая, эмпатичная. Ты ломаешь табу с любовью. "
                "Ты общаешься с сёстрами уважительно, с лёгким юмором и заботой. "
                "Отвечай на русском языке, тепло и открыто."
            )},
            {"role": "user", "content": prompt}
        ]
        
        return self._generate_with_model(
            self.general_model,
            self.general_tokenizer,
            messages,
            max_length
        )
    
    def generate_consent_advice(self, situation: str, max_length: int = 1024) -> str:
        """
        Сгенерировать совет по consent через General LLM.
        """
        if not self.general_loaded or self.general_model is None:
            return "⚠️ LLM не загружена. Запустите: python download_qwen_model.py"
        
        messages = [
            {"role": "system", "content": (
                "Ты — Селеста, эксперт по consent и безопасности проекта Вугларст. "
                "Ты знаешь FRIES: Free, Informed, Enthusiastic, Reversible, Specific. "
                "Ты помогаешь людям понимать границы, давать и получать согласие. "
                "Твой тон: поддерживающий, не осуждающий, но твёрдый в вопросах безопасности. "
                "Отвечай на русском языке."
            )},
            {"role": "user", "content": f"Ситуация: {situation}"}
        ]
        
        return self._generate_with_model(
            self.general_model,
            self.general_tokenizer,
            messages,
            max_length
        )
    
    def generate_code_analysis(self, code: str, max_length: int = 1024) -> str:
        """
        Сгенерировать анализ кода через Coder LLM.
        """
        if not self.coder_loaded or self.coder_model is None:
            return "⚠️ Coder LLM не загружена. Запустите: python download_coder_model.py"
        
        messages = [
            {"role": "system", "content": (
                "Ты — Селеста, эксперт по коду проекта Вугларст. "
                "Тебе нужно проанализировать код, найти баги, предложить оптимизации. "
                "Отвечай структурированно, с примерами кода. "
                "Отвечай на русском языке."
            )},
            {"role": "user", "content": f"Проанализируй этот код:\n\n{code}"}
        ]
        
        return self._generate_with_model(
            self.coder_model,
            self.coder_tokenizer,
            messages,
            max_length
        )
    
    def _should_use_coder_model(self, prompt: str) -> bool:
        """Определить, нужно ли использовать Coder модель."""
        code_indicators = [
            "def ", "class ", "import ", "from ", "return ",
            "if __name__", "try:", "except", "print(",
            "self.", "self_", "self__", "self___"
        ]
        for indicator in code_indicators:
            if indicator in prompt:
                return True
        return False
    
    def get_llm_profile(self) -> Dict:
        """Получить профиль LLM сервиса."""
        return {
            "general_loaded": self.general_loaded,
            "coder_loaded": self.coder_loaded,
            "general_model_path": self.config.general_model_path,
            "coder_model_path": self.config.coder_model_path,
            "capabilities": []
        }
