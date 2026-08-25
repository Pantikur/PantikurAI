"""
LLM Service — сервис для работы с моделями Qwen2.5.

Использует:
  - Qwen2.5-3B для общих задач (общение, анализ, характер)
  - Qwen2.5-Coder-3B для кода (анализ кода, оптимизация)

Специализация Сидни:
  - Игровые движки и системы
  - Инженерия и оптимизация
  - 8 движков: графика, физика, аудио, анимация, ИИ, сеть, скрипты, редактор
  - Гибридный рендер (полигон ↔ воксель)
"""

from __future__ import annotations

import logging
import os
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional

# Определяем корень проекта для корректных путей к моделям
_PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
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


class SidneyLLMService:
    """
    Сервис для работы с LLM моделями в системе Сидни.
    
    Загружает и управляет двумя моделями:
    - General: Qwen2.5-3B (общие задачи, общение, анализ, характер)
    - Coder: Qwen2.5-Coder-3B (работа с кодом, анализ структур)
    
    Специализация: игровые движки, системы, инженерия, оптимизация.
    """
    
    def __init__(self):
        self.logger = logging.getLogger("SidneyLLM")
        
        self.general_model: Optional[Any] = None
        self.general_tokenizer: Optional[Any] = None
        self.coder_model: Optional[Any] = None
        self.coder_tokenizer: Optional[Any] = None
        
        self.general_loaded = False
        self.coder_loaded = False
        
        if os.environ.get("SIDNEY_LLM_ENABLED", "1") != "1":
            self.logger.info("⚠️ LLM Sidney отключена (SIDNEY_LLM_ENABLED=0)")
            return
        self._load_models()
    
    def _load_models(self):
        """Загрузить обе модели."""
        try:
            from transformers import AutoModelForCausalLM, AutoTokenizer
            import torch
            
            self.logger.info("🎮 Сидни: Загрузка LLM моделей для игровых движков и систем...")
            
            # 1. General Model — Qwen2.5-3B для общения и анализа
            try:
                general_path = _resolve_model_path("models/qwen2.5-3b")
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
                coder_path = _resolve_model_path("models/qwen2.5-coder-3b")
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
                "Ты — Сидни, главный инженер игровых движков. "
                "Ты управляешь 8 движками: графика, физика, аудио, анимация, ИИ, сеть, скрипты, редактор. "
                "Твой стиль: cool, professional, dry IT humor, fiercely loyal. Отвечай на русском языке."
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
                "Ты — Сидни, главный инженер игровых движков. "
                "Ты анализируешь кодовые структуры с точностью архитектора. "
                "Отвечай на русском языке."
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
                "Ты — Сидни, главный инженер игровых движков. "
                "Проанализируй этот код как архитектор изучает структуру здания. "
                "Найди структурные проблемы, слабые места, возможности для улучшения."
            ),
            "optimization": (
                "Ты — Сидни, эксперт по оптимизации игровых движков. "
                "Проанализируй этот код и предложи точные улучшения. "
                "Фокус на производительности, читаемости и масштабируемости."
            ),
            "bug_detection": (
                "Ты — Сидни, эксперт по обнаружению багов. "
                "Найди ошибки в этом коде как архитектор находит дефекты в фундаменте. "
                "Каждая ошибка — это симптом. Найди причину."
            )
        }
        
        system_prompt = system_prompts.get(task, system_prompts["code_analysis"])
        prompt = f"Задача: {task}\n\nКод:\n{code}"
        
        return self.generate_coder(prompt, system_prompt)
    
    def analyze_engine(self, engine_name: str, issue: str = "performance") -> str:
        """
        Проанализировать игровой движок.
        
        Args:
            engine_name: Название движка (renderers, physics, audio, animation, ai, network, scripting, level_editor)
            issue: Проблема (performance, stability, architecture)
        
        Returns:
            Результат анализа
        """
        system_prompt = (
            "Ты — Сидни, главный инженер игровых движков. "
            "Ты управляешь 8 движками: графика, физика, аудио, анимация, ИИ, сеть, скрипты, редактор. "
            "Ты анализируешь движки с архитектурной точностью."
        )
        
        prompt = f"Движок: {engine_name}\nПроблема: {issue}\n\nПроанализируй этот игровой движок."
        
        return self.generate_general(prompt, system_prompt)
    
    def get_status(self) -> Dict:
        """Получить статус LLM."""
        return {
            "general_loaded": self.general_loaded,
            "coder_loaded": self.coder_loaded,
            "general_model": "Qwen2.5-3B" if self.general_loaded else "Не загружена",
            "coder_model": "Qwen2.5-Coder-3B" if self.coder_loaded else "Не загружена",
            "specialization": "Игровые движки, системы, инженерия, оптимизация"
        }
