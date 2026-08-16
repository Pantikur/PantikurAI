"""
API для вызова Qwen2.5 моделей из других частей проекта.

Использование:
    from nobuka.engine.qwen_api import qwen
    
    # Автоматический выбор модели
    response = qwen.generate("Напиши функцию сортировки")
    
    # Принудительное использование Coder
    response = qwen.generate_coder("def bubble_sort(arr): pass")
    
    # Принудительное использование General
    response = qwen.generate_general("Привет, как дела?")
    
    # Проверка статуса
    print(qwen.status())
"""

from __future__ import annotations
import logging
import sys
from pathlib import Path
from typing import Optional

# Добавляем текущую директорию и корень проекта в path
_script_dir = Path(__file__).parent.resolve()
if str(_script_dir) not in sys.path:
    sys.path.insert(0, str(_script_dir))

# Корень проекта (D:\NewCod\Pantikur)
_project_root = _script_dir.parent.parent.resolve()
if str(_project_root) not in sys.path:
    sys.path.insert(0, str(_project_root))

from nobuka_core import NobukaCore
from config import NobukaConfig


class QwenAPI:
    """
    Простой API для работы с Qwen2.5 моделями.
    
    Этот класс предоставляет глобальный экземпляр для удобного вызова
    моделей из любой части проекта.
    """

    def __init__(self, config: Optional[NobukaConfig] = None):
        self.config = config or NobukaConfig.default()
        self.logger = logging.getLogger("QwenAPI")
        
        # Логгер
        handler = logging.StreamHandler(sys.stdout)
        handler.setFormatter(logging.Formatter("%(asctime)s | %(levelname)s | %(name)s | %(message)s"))
        self.logger.addHandler(handler)
        self.logger.setLevel(logging.INFO)

        # Инициализируем ядро
        try:
            self.core = NobukaCore(self.config)
            self.logger.info("✅ QwenAPI инициализирована")
        except Exception as e:
            self.logger.error(f"❌ Ошибка инициализации QwenAPI: {e}")
            self.core = None

    def generate(self, prompt: str, max_length: int = 512) -> str:
        """
        Сгенерировать ответ с автоматическим выбором модели.
        
        Args:
            prompt: Текст запроса
            max_length: Максимальная длина ответа
            
        Returns:
            Сгенерированный ответ
        """
        if self.core is None:
            return "❌ QwenAPI не инициализирована"
        return self.core.generate_response(prompt, max_length)

    def generate_coder(self, prompt: str, max_length: int = 512) -> str:
        """
        Сгенерировать ответ с использованием Coder модели.
        
        Args:
            prompt: Текст запроса
            max_length: Максимальная длина ответа
            
        Returns:
            Сгенерированный ответ
        """
        if self.core is None:
            return "❌ QwenAPI не инициализирована"
        return self.core.generate_coder_response(prompt, max_length)

    def generate_general(self, prompt: str, max_length: int = 512) -> str:
        """
        Сгенерировать ответ с использованием General модели.
        
        Args:
            prompt: Текст запроса
            max_length: Максимальная длина ответа
            
        Returns:
            Сгенерированный ответ
        """
        if self.core is None:
            return "❌ QwenAPI не инициализирована"
        
        if not hasattr(self.core, 'general_model') or self.core.general_model is None:
            return "⚠️ General модель не загружена"
        
        messages = [
            {"role": "system", "content": "Ты — Нобука, третья младшая сестра. Ты отвечаешь на вопросы, помогаешь с диалогами, эмоциями и общими темами. Отвечай на русском языке тепло и дружелюбно."},
            {"role": "user", "content": prompt}
        ]
        
        return self.core._generate_with_model(
            self.core.general_model,
            self.core.general_tokenizer,
            messages,
            max_length
        )

    def status(self) -> dict:
        """
        Получить статус моделей.
        
        Returns:
            Словарь со статусом моделей
        """
        if self.core is None:
            return {"error": "QwenAPI не инициализирована"}

        return {
            "coder_available": hasattr(self.core, 'coder_model') and self.core.coder_model is not None,
            "general_available": hasattr(self.core, 'general_model') and self.core.general_model is not None,
            "coder_model_path": getattr(self.core, 'coder_model_path', None),
            "general_model_path": getattr(self.core, 'general_model_path', None),
        }

    def is_coder_task(self, prompt: str) -> bool:
        """
        Определить, является ли запрос задачей программирования.
        
        Args:
            prompt: Текст запроса
            
        Returns:
            True если это задача программирования
        """
        if self.core is None:
            return False
        return self.core._should_use_coder_model(prompt)


# Глобальный экземпляр API
qwen: QwenAPI = None  # type: ignore


def init_qwen_api(config: Optional[NobukaConfig] = None) -> QwenAPI:
    """
    Инициализировать глобальный экземпляр QwenAPI.
    
    Args:
        config: Опциональная конфигурация
        
    Returns:
        Экземпляр QwenAPI
    """
    global qwen
    qwen = QwenAPI(config)
    return qwen


def get_qwen_api() -> QwenAPI:
    """
    Получить глобальный экземпляр QwenAPI.
    
    Returns:
        Экземпляр QwenAPI
    """
    assert qwen is not None, "QwenAPI не инициализирована"
    return qwen  # type: ignore


# Инициализация при импорте
init_qwen_api()
