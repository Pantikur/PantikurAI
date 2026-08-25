"""
LLM Service — сервис для работы с моделями Qwen2.5.

Использует:
  - Qwen2.5-3B для общих задач (общение, анализ, характер)
  - Qwen2.5-Coder-3B для кода (анализ кода, оптимизация)

Специализация Латислейн:
  - Анатомия и тело
  - Точность и инженерия
  - Безопасность и структура
  - Научный подход к телу
"""

from __future__ import annotations

import logging
import os
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional

from latislane.engine.config import LatislaneConfig

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


class LatislaneLLMService:
    """
    Сервис для работы с LLM моделями в системе Латислейн.
    
    Загружает и управляет двумя моделями:
    - General: Qwen2.5-3B (общие задачи, общение, анализ, характер)
    - Coder: Qwen2.5-Coder-3B (работа с кодом, анализ структур)
    
    Специализация: анатомия, тело, точность, инженерия.
    """
    
    def __init__(self, config: Optional[LatislaneConfig] = None):
        self.config = config or LatislaneConfig.default()
        self.logger = logging.getLogger("LatislaneLLM")
        
        self.general_model: Optional[Any] = None
        self.general_tokenizer: Optional[Any] = None
        self.coder_model: Optional[Any] = None
        self.coder_tokenizer: Optional[Any] = None
        
        self.general_loaded = False
        self.coder_loaded = False
        
        if os.environ.get("LATISLANE_LLM_ENABLED", "1") != "1":
            self.logger.info("⚠️ LLM Latislane отключена (LATISLANE_LLM_ENABLED=0)")
            return
        self._load_models()
    
    def _load_models(self):
        """Загрузить обе модели."""
        try:
            from transformers import AutoModelForCausalLM, AutoTokenizer
            import torch
            
            self.logger.info("🧬 Латислейн: Загрузка LLM моделей для анатомии и тела...")
            
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
        Универсальная генерация через General модель.
        """
        if not self.general_loaded or self.general_model is None:
            return "⚠️ LLM не загружена"
        
        messages = [
            {"role": "system", "content": system_prompt or (
                "Ты — Латислейн, эксперт по анатомии, телу и точности. "
                "Ты точная, структурированная, научная. Отвечай на русском языке."
            )},
            {"role": "user", "content": prompt}
        ]
        
        return self._generate_with_model(
            self.general_model, self.general_tokenizer, messages, max_length
        )
    
    def generate_coder(self, prompt: str, system_prompt: str = None, max_length: int = 512) -> str:
        """
        Генерация через Coder модель (для кода и анализа).
        """
        if not self.coder_loaded or self.coder_model is None:
            return "⚠️ Coder модель не загружена"
        
        messages = [
            {"role": "system", "content": system_prompt or (
                "Ты — Латислейн, эксперт по анатомии и инженерии. "
                "Ты анализируешь кодовые структуры с точностью хирурга. Отвечай на русском языке."
            )},
            {"role": "user", "content": prompt}
        ]
        
        return self._generate_with_model(
            self.coder_model, self.coder_tokenizer, messages, max_length
        )
    
    def analyze_code(self, code: str, task: str = "code_analysis") -> str:
        """
        Проанализировать код через Coder модель.
        
        Args:
            code: Исходный код для анализа
            task: Тип задачи (code_analysis, optimization, bug_detection)
        
        Returns:
            Результат анализа
        """
        system_prompts = {
            "code_analysis": (
                "Ты — Латислейн, эксперт по анатомии и точности. "
                "Проанализируй этот код как анатом изучает тело. "
                "Найди структурные проблемы, слабые места, возможности для улучшения."
            ),
            "optimization": (
                "Ты — Латислейн, эксперт по оптимизации. "
                "Проанализируй этот код и предложи точные улучшения. "
                "Фокус на производительности, читаемости и безопасности."
            ),
            "bug_detection": (
                "Ты — Латислейн, эксперт по обнаружению багов. "
                "Найди ошибки в этом коде как хирург находит дефекты в организме. "
                "Каждая ошибка — это симптом. Найди причину."
            )
        }
        
        system_prompt = system_prompts.get(task, system_prompts["code_analysis"])
        prompt = f"Задача: {task}\n\nКод:\n{code}"
        
        return self.generate_coder(prompt, system_prompt)
    
    def analyze_anatomy(self, body_system: str, focus: str = "structure") -> str:
        """
        Проанализировать анатомическую систему.
        
        Args:
            body_system: Описание анатомической системы
            focus: Фокус анализа (structure, function, pathology)
        
        Returns:
            Результат анализа
        """
        system_prompt = (
            "Ты — Латислейн, эксперт по анатомии. "
            "Ты анализируешь тело с научной точностью. "
            "Каждая структура имеет функцию, каждая функция имеет значение."
        )
        
        prompt = f"Система: {body_system}\nФокус: {focus}\n\nПроанализируй эту анатомическую систему."
        
        return self.generate_general(prompt, system_prompt)
    
    def get_status(self) -> Dict:
        """Получить статус LLM."""
        return {
            "general_loaded": self.general_loaded,
            "coder_loaded": self.coder_loaded,
            "general_model": "Qwen2.5-3B" if self.general_loaded else "Не загружена",
            "coder_model": "Qwen2.5-Coder-3B" if self.coder_loaded else "Не загружена",
            "specialization": "Анатомия, тело, точность, инженерия"
        }
