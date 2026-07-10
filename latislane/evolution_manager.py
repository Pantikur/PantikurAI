"""
Latislane — Система эволюционной прогрессии.

Управляет последовательным изучением:
Механическое → Бионическое → Органическое → Синтез
"""

import json
import logging
import time
from pathlib import Path
from typing import Dict, List, Optional, Any
from datetime import datetime

from .body_modules import LatislaneEvolutionStage

logger = logging.getLogger("latislane.evolution")


class EvolutionManager:
    """
    Менеджер эволюции — управляет прогрессией от механического к органическому.
    
    Работает по принципу:
    - Нельзя перейти к следующему этапу, пока не завершён предыдущий
    - Каждый этап требует изучения определённых тем
    - Прогресс сохраняется между сессиями
    """
    
    # Требования для каждого этапа
    STAGE_REQUIREMENTS = {
        LatislaneEvolutionStage.MECHANICAL_RESEARCH: {
            "min_topics": 5,
            "topics": [
                "prosthetics design principles",
                "robotic exoskeleton human",
                "biomechanics human movement",
                "titanium alloy materials",
                "servo motor systems"
            ],
            "description": "Изучение механических технологий и робототехники"
        },
        LatislaneEvolutionStage.MECHANICAL_DESIGN: {
            "min_topics": 3,
            "topics": [],
            "description": "Проектирование первого механического тела"
        },
        LatislaneEvolutionStage.MECHANICAL_COMPLETE: {
            "min_topics": 0,
            "topics": [],
            "description": "Завершение механического этапа"
        },
        LatislaneEvolutionStage.BIONIC_RESEARCH: {
            "min_topics": 8,
            "topics": [
                "neural prosthetics brain computer interface",
                "bioartificial organs tissue engineering",
                "electroactive polymers artificial muscle",
                "osseointegration titanium implants",
                "neural signal processing"
            ],
            "description": "Изучение бионических технологий"
        },
        LatislaneEvolutionStage.BIONIC_DESIGN: {
            "min_topics": 3,
            "topics": [],
            "description": "Проектирование бионического тела"
        },
        LatislaneEvolutionStage.BIONIC_COMPLETE: {
            "min_topics": 0,
            "topics": [],
            "description": "Завершение бионического этапа"
        },
        LatislaneEvolutionStage.ORGANIC_RESEARCH: {
            "min_topics": 10,
            "topics": [
                "3d bioprinting organs",
                "gene editing CRISPR human",
                "stem cells human differentiation",
                "tissue engineering human organs",
                "organoid development"
            ],
            "description": "Изучение биоинженерии и генетики"
        },
        LatislaneEvolutionStage.ORGANIC_DESIGN: {
            "min_topics": 3,
            "topics": [],
            "description": "Проектирование органического тела"
        },
        LatislaneEvolutionStage.ORGANIC_COMPLETE: {
            "min_topics": 0,
            "topics": [],
            "description": "Завершение органического этапа"
        },
        LatislaneEvolutionStage.SYNTHESIS: {
            "min_topics": 5,
            "topics": [
                "human-machine integration",
                "biohybrid systems",
                "synthetic biology"
            ],
            "description": "Синтез всех технологий"
        },
        LatislaneEvolutionStage.FINAL: {
            "min_topics": 0,
            "topics": [],
            "description": "Финальная версия — полный цикл завершён"
        }
    }
    
    def __init__(self, data_dir: str = "data/latislane/evolution"):
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)
        
        # Текущий этап
        self.current_stage = LatislaneEvolutionStage.MECHANICAL_RESEARCH
        
        # Прогресс по этапам
        self.stage_progress: Dict[LatislaneEvolutionStage, float] = {}
        self.stage_completed: Dict[LatislaneEvolutionStage, bool] = {}
        
        # История переходов
        self.transition_history: List[Dict[str, Any]] = []
        
        # Загрузка состояния
        self._load_state()
        
        logger.info(f"🧬 EvolutionManager инициализирован")
        logger.info(f"   Текущий этап: {self.current_stage.value}")
    
    def _load_state(self):
        """Загрузить состояние эволюции."""
        state_file = self.data_dir / "evolution_state.json"
        if state_file.exists():
            try:
                with open(state_file, "r", encoding="utf-8") as f:
                    state = json.load(f)
                
                # Восстановление текущего этапа
                stage_value = state.get("current_stage")
                if stage_value:
                    try:
                        self.current_stage = LatislaneEvolutionStage(stage_value)
                    except ValueError:
                        logger.warning(f"⚠️ Неизвестный этап: {stage_value}, используется начальный")
                        self.current_stage = LatislaneEvolutionStage.MECHANICAL_RESEARCH
                
                # Восстановление прогресса
                for stage_str, progress in state.get("stage_progress", {}).items():
                    try:
                        stage = LatislaneEvolutionStage(stage_str)
                        self.stage_progress[stage] = progress
                    except ValueError:
                        pass
                
                # Восстановление завершённых этапов
                for stage_str in state.get("stage_completed", []):
                    try:
                        stage = LatislaneEvolutionStage(stage_str)
                        self.stage_completed[stage] = True
                    except ValueError:
                        pass
                
                # Восстановление истории
                self.transition_history = state.get("transition_history", [])[-50:]
                
                logger.info(f"✅ Состояние эволюции загружено: {self.current_stage.value}")
            except Exception as e:
                logger.warning(f"⚠️ Ошибка загрузки состояния: {e}")
                self._reset_state()
        else:
            logger.info("ℹ️ Новое состояние эволюции создано")
    
    def _reset_state(self):
        """Сбросить состояние (для отладки)."""
        self.current_stage = LatislaneEvolutionStage.MECHANICAL_RESEARCH
        self.stage_progress = {}
        self.stage_completed = {}
        self.transition_history = []
        self._save_state()
    
    def _save_state(self):
        """Сохранить состояние эволюции."""
        state = {
            "current_stage": self.current_stage.value,
            "stage_progress": {
                stage.value: progress
                for stage, progress in self.stage_progress.items()
            },
            "stage_completed": [
                stage.value
                for stage, completed in self.stage_completed.items()
                if completed
            ],
            "transition_history": self.transition_history[-50:],
            "saved_at": time.time()
        }
        
        state_file = self.data_dir / "evolution_state.json"
        try:
            with open(state_file, "w", encoding="utf-8") as f:
                json.dump(state, f, ensure_ascii=False, indent=2)
        except Exception as e:
            logger.error(f"❌ Ошибка сохранения: {e}")
    
    def get_current_stage_info(self) -> Dict[str, Any]:
        """Получить информацию о текущем этапе."""
        reqs = self.STAGE_REQUIREMENTS.get(self.current_stage, {})
        
        return {
            "stage": self.current_stage.value,
            "description": reqs.get("description", ""),
            "stage_number": list(LatislaneEvolutionStage).index(self.current_stage) + 1,
            "total_stages": len(LatislaneEvolutionStage),
            "progress": self.stage_progress.get(self.current_stage, 0.0),
            "completed": self.stage_completed.get(self.current_stage, False),
            "requirements": {
                "min_topics": reqs.get("min_topics", 0),
                "required_topics": reqs.get("topics", [])
            },
            "next_stage": next_stage.value if (next_stage := self._get_next_stage()) else None
        }
    
    def _get_next_stage(self) -> Optional[LatislaneEvolutionStage]:
        """Получить следующий этап."""
        stages = list(LatislaneEvolutionStage)
        current_idx = stages.index(self.current_stage)
        if current_idx < len(stages) - 1:
            return stages[current_idx + 1]
        return None
    
    def can_advance(self, learned_topics_count: int = 0) -> bool:
        """
        Проверить, можно ли перейти к следующему этапу.
        
        :param learned_topics_count: Количество изученных тем
        :return: True если можно продвинуться
        """
        reqs = self.STAGE_REQUIREMENTS.get(self.current_stage, {})
        min_topics = reqs.get("min_topics", 0)
        
        # Проверка минимального количества тем
        if learned_topics_count < min_topics:
            logger.debug(f"⏳ Нужно {min_topics} тем, изучено: {learned_topics_count}")
            return False
        
        # Проверка: этап уже завершён
        if self.stage_completed.get(self.current_stage, False):
            return False
        
        return True
    
    def advance(self, reason: str = "manual"):
        """
        Перейти к следующему этапу.
        
        :param reason: Причина перехода
        """
        old_stage = self.current_stage
        next_stage = self._get_next_stage()
        
        if next_stage is None:
            logger.info("✅ Все этапы пройдены!")
            return
        
        # Помечаем текущий этап как завершённый
        self.stage_completed[self.current_stage] = True
        self.stage_progress[self.current_stage] = 1.0
        
        # Переходим к следующему
        self.current_stage = next_stage
        self.stage_progress[next_stage] = 0.0
        
        # Записываем в историю
        self.transition_history.append({
            "from": old_stage.value,
            "to": next_stage.value,
            "timestamp": time.time(),
            "datetime": datetime.now().isoformat(),
            "reason": reason
        })
        
        logger.info(f"🎉 ЭВОЛЮЦИЯ: {old_stage.value} → {next_stage.value}")
        logger.info(f"   Этап {list(LatislaneEvolutionStage).index(next_stage) + 1}/{len(LatislaneEvolutionStage)}")
        
        self._save_state()
    
    def update_progress(self, progress_delta: float):
        """
        Обновить прогресс текущего этапа.
        
        :param progress_delta: Прибавка прогресса (0.0 — 1.0)
        """
        current_progress = self.stage_progress.get(self.current_stage, 0.0)
        new_progress = min(1.0, current_progress + progress_delta)
        self.stage_progress[self.current_stage] = new_progress
        
        # Если прогресс достиг 100% — автоматически продвигаемся
        if new_progress >= 1.0 and not self.stage_completed.get(self.current_stage, False):
            logger.info(f"✅ Этап {self.current_stage.value} завершён (100%)")
            self.advance(reason="auto_progress")
    
    def get_evolution_report(self) -> Dict[str, Any]:
        """Получить полный отчёт о эволюции."""
        stages = list(LatislaneEvolutionStage)
        current_idx = stages.index(self.current_stage)
        
        # Прогресс по каждому этапу
        stage_details = []
        for i, stage in enumerate(stages):
            stage_details.append({
                "stage": stage.value,
                "progress": self.stage_progress.get(stage, 0.0),
                "completed": self.stage_completed.get(stage, False),
                "is_current": stage == self.current_stage,
                "is_past": i < current_idx,
                "is_future": i > current_idx
            })
        
        return {
            "current_stage": self.current_stage.value,
            "stage_number": current_idx + 1,
            "total_stages": len(stages),
            "overall_progress": (current_idx + self.stage_progress.get(self.current_stage, 0.0)) / len(stages),
            "stage_details": stage_details,
            "transition_count": len(self.transition_history),
            "last_transition": self.transition_history[-1] if self.transition_history else None
        }
    
    def chat_response(self, user_message: str) -> str:
        """Ответ на вопрос о прогрессе эволюции."""
        msg_lower = user_message.lower()
        
        if any(kw in msg_lower for kw in ["эволюция", "прогресс", "этап", "стадия"]):
            report = self.get_evolution_report()
            current = report["stage_number"]
            total = report["total_stages"]
            progress = report["overall_progress"] * 100
            
            return (
                f"🧬 **Латислейн: Эволюция**\n\n"
                f"Этап {current}/{total}: {self.current_stage.value}\n"
                f"Общий прогресс: {progress:.1f}%\n\n"
                f"Текущая задача: {self.STAGE_REQUIREMENTS.get(self.current_stage, {}).get('description', '')}\n\n"
                f"{'─' * 40}\n\n"
                f"Этапы:\n"
            ) + "\n".join(
                f"{'✅' if s['completed'] else '🔵' if s['is_current'] else '⚪'} {s['stage']}"
                for s in report["stage_details"]
            )
        
        elif any(kw in msg_lower for kw in ["следующий", "перейти", "продвинуть"]):
            can = self.can_advance()
            if can:
                return "✅ Можно перейти к следующему этапу! Используй /latislane/evolve"
            else:
                reqs = self.STAGE_REQUIREMENTS.get(self.current_stage, {})
                return f"⏳ Нужно изучить больше тем. Требуется: {reqs.get('min_topics', 0)} тем"
        
        else:
            return (
                "🧬 **Латислейн: Эволюция тел**\n\n"
                "Система проходит 11 этапов эволюции:\n\n"
                "1-3. Механическое тело (робототехника)\n"
                "4-6. Бионическое тело (гибрид)\n"
                "7-9. Органическое тело (биоинженерия)\n"
                "10-11. Синтез и финал\n\n"
                "Запросы:\n"
                "- 'эволюция' — текущий этап\n"
                "- 'следующий' — проверка перехода"
            )
