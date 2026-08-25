"""
LLM Service — сервис для работы с моделями Qwen2.5.

Использует:
  - Qwen2.5-3B для общих задач (общение, характер, анализ)
  - Qwen2.5-Coder-3B для кода (анализ кода, оптимизация)
"""

from __future__ import annotations

import logging
import os
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional

from kristi.engine.config import KristiConfig

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
        Path(__file__).resolve().parent.parent.parent,  # один уровень выше kristi/engine
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


class KristiLLMService:
    """
    Сервис для работы с LLM моделями в системе Кристи.
    
    Загружает и управляет двумя моделями:
    - General: Qwen2.5-3B (общие задачи, общение, характер)
    - Coder: Qwen2.5-Coder-3B (работа с кодом, анализ структур)
    """
    
    def __init__(self, config: KristiConfig):
        self.config = config
        self.logger = logging.getLogger("KristiLLM")
        
        # Атрибуты могут быть None до загрузки моделей
        self.general_model: Optional[Any] = None
        self.general_tokenizer: Optional[Any] = None
        self.coder_model: Optional[Any] = None
        self.coder_tokenizer: Optional[Any] = None
        
        self.general_loaded = False
        self.coder_loaded = False
        
        if os.environ.get("KRISTI_LLM_ENABLED", "1") != "1":
            self.logger.info("⚠️ LLM Kristi отключена (KRISTI_LLM_ENABLED=0)")
            return
        self._load_models()
    
    def _load_models(self):
        """Загрузить обе модели."""
        try:
            from transformers import AutoModelForCausalLM, AutoTokenizer
            import torch
            
            self.logger.info("🎬 Кристи: Загрузка LLM моделей для режиссуры и сценариев...")
            
            # 1. General Model — Qwen2.5-3B для общения и анализа
            try:
                general_path = _resolve_model_path(self.config.general_model_path)
                self.logger.info(f"📖 Загрузка General (Qwen2.5-3B): {general_path}")
                
                self.general_tokenizer = AutoTokenizer.from_pretrained(
                    general_path,
                    trust_remote_code=True
                )
                
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
            
            # 2. Coder Model — Qwen2.5-Coder-3B для анализа кода
            try:
                coder_path = _resolve_model_path(self.config.coder_model_path)
                self.logger.info(f"💻 Загрузка Coder (Qwen2.5-Coder-3B): {coder_path}")
                
                self.coder_tokenizer = AutoTokenizer.from_pretrained(
                    coder_path,
                    trust_remote_code=True
                )
                
                self.coder_model = AutoModelForCausalLM.from_pretrained(
                    coder_path,
                    device_map="auto",
                    torch_dtype=torch.float16 if torch.cuda.is_available() else torch.float32,
                    trust_remote_code=True
                )
                
                self.coder_loaded = True
                self.logger.info("✅ Coder модель (Qwen2.5-Coder-3B) загружена")
                
            except Exception as e:
                self.logger.error(f"❌ Ошибка загрузки Coder модели: {e}")
            
            if self.general_loaded or self.coder_loaded:
                self.logger.info("✅ LLM сервис инициализирован")
            else:
                self.logger.warning("⚠️ Ни одна модель не загружена. Запустите: python download_qwen_model.py")
            
        except Exception as e:
            self.logger.error(f"❌ Ошибка инициализации LLM: {e}")
    
    def _get_model_device(self, model):
        """Получить устройство модели (работает с device_map='auto')."""
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
        
        Args:
            model: Модель для генерации
            tokenizer: Токенизатор
            messages: Список сообщений для чата
            max_length: Максимальная длина ответа
            
        Returns:
            Сгенерированный ответ
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
    
    def generate_script(self, genre: str, theme: str, max_length: int = 1024) -> str:
        """
        Сгенерировать сценарий через General LLM.
        
        Args:
            genre: Жанр видео
            theme: Тема
            max_length: Максимальная длина ответа
            
        Returns:
            Сгенерированный сценарий
        """
        if not self.general_loaded or self.general_model is None:
            return "⚠️ LLM не загружена. Запустите: python download_qwen_model.py"
        
        messages = [
            {"role": "system", "content": (
                "Ты — Кристи, режиссёр видеопроизводства проекта Вугларст. "
                "Ты создаёшь сценарии, раскадровки и режируешь видео. "
                "Ты общаешься с сёстрами творчески, с кинематографическими образами. "
                "Отвечай на русском языке, поэтично, с режиссёрскими заметками."
            )},
            {"role": "user", "content": f"Напиши сценарий в жанре '{genre}' на тему '{theme}'. Укажи: структуру, персонажей, диалоги, режиссёрские заметки."}
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
        
        Args:
            prompt: Запрос от сестры
            max_length: Максимальная длина ответа
            
        Returns:
            Ответ Кристи
        """
        if not self.general_loaded or self.general_model is None:
            return "⚠️ LLM не загружена. Запустите: python download_qwen_model.py"
        
        messages = [
            {"role": "system", "content": (
                "Ты — Кристи, режиссёр видеопроизводства проекта Вугларст. "
                "Ты творческая, визионерская, любишь кинематографические образы. "
                "Ты общаешься с сёстрами тепло, но с режиссёрской перспективой. "
                "Отвечай на русском языке, поэтично, с кинематографическими образами."
            )},
            {"role": "user", "content": prompt}
        ]
        
        return self._generate_with_model(
            self.general_model,
            self.general_tokenizer,
            messages,
            max_length
        )
    
    def generate_storyboard(self, script_summary: str, num_scenes: int = 5, max_length: int = 1024) -> str:
        """
        Сгенерировать раскадровку для сценария.
        
        Args:
            script_summary: Краткое содержание сценария
            num_scenes: Количество сцен
            max_length: Максимальная длина ответа
            
        Returns:
            Раскадровка
        """
        if not self.general_loaded or self.general_model is None:
            return "⚠️ LLM не загружена. Запустите: python download_qwen_model.py"
        
        messages = [
            {"role": "system", "content": (
                "Ты — Кристи, режиссёр видеопроизводства. "
                "Ты создаёшь раскадровки с максимальной детализацией. "
                "Укажи для каждой сцены: ракурс, свет, движение камеры, эмоции персонажей. "
                "Отвечай структурированно, с режиссёрскими заметками. "
                "Отвечай на русском языке."
            )},
            {"role": "user", "content": (
                f"Создай раскадровку для сценария: '{script_summary}'. "
                f"Количество сцен: {num_scenes}. "
                f"Укажи для каждой сцены: ракурс, свет, движение камеры, эмоции."
            )}
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
        
        Args:
            code: Код для анализа
            max_length: Максимальная длина ответа
            
        Returns:
            Анализ кода
        """
        if not self.coder_loaded or self.coder_model is None:
            return "⚠️ Coder LLM не загружена. Запустите: python download_coder_model.py"
        
        messages = [
            {"role": "system", "content": (
                "Ты — Кристи, эксперт по коду проекта Вугларст. "
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
        """
        Определить, нужно ли использовать Coder модель.
        
        Coder модель лучше для:
        - Анализа кода
        - Генерации кода
        - Поиска багов
        - Рефакторинга
        """
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
