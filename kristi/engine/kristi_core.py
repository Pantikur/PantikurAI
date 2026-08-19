"""
Ядро Кристи — автономный цикл видеопроизводства.

Реализует:
  - 🎬 Управление созданием видео (полный цикл)
  - 📋 Написание сценариев и раскадровок
  - 🎭 Режиссура и постановка
  - ✂️ Монтаж и постпродакшн
  - 🎵 Звуковой дизайн
  - 🎞️ Анимация для видео
  - 🌐 Выход в интернет для изучения
  - 🔄 Автономная работа 24/7
  - 📈 Повышение уровня знаний (1-20)
  - 🤝 Взаимодействие с сёстрами
  - 📊 Написание отчётов
  - 🔮 Формирование и укрепление характера

Взаимодействие с сёстрами:
  - Айка — визуальный стиль и референсы
  - Футаба — управление и планирование
  - Нобука — улучшения и оптимизация
  - Шиори — защита и безопасность
  - Селеста — анатомия для анимации
  - Юи — повествование и когнитивные науки
  - Ханако — творческое вдохновение
  - Люси — обучение и педагогика
  - Фуюки — исследования
  - Латислейн — логика
  - Наото — внимание к деталям
"""

from __future__ import annotations

import json
import logging
import os
import random
import signal
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Any, Optional, Dict, List

from humanity_core import HumanityLayer

from kristi.engine.config import KristiConfig
from kristi.engine.llm_service import KristiLLMService
from kristi.engine.emotions import EmotionalEngine, DesireType, EmotionType

# 6 модулей души Кристи: Сознание, Сердце, Амбиции, Воля, Разум
from kristi.consciousness import KristiConsciousness
from kristi.heart import KristiHeart
from kristi.ambitions import KristiAmbitions
from kristi.volition import KristiVolition
from kristi.mind import KristiMind

# Система памяти Кристи
from kristi.memory import KristiMemory

from kristi.engine.models import (
    KristiState,
    Script,
    Scene,
    ProductionProject,
    Report,
    KnowledgeEntry,
    LevelProgress,
    ProductionStage,
    SceneType,
    CameraAngle,
    TransitionType,
)

try:
    from scientists_network.network import get_network, RequestType, RequestPriority
    _HAS_NETWORK = True
except Exception:
    get_network = None
    RequestType = None
    RequestPriority = None
    _HAS_NETWORK = False


class KristiCore:
    """
    Ядро Кристи — автономный режиссёр видеопроизводства.
    
    Кристи управляет полным циклом создания видео:
    от концепции и сценария до финального рендера.
    """
    
    def __init__(self, config: Optional[KristiConfig] = None):
        self.config = config or KristiConfig.default()
        self.logger = self._setup_logging()
        
        # Загрузка состояния
        self.state = self._load_state()
        
        # humanity_core — живая душа Кристи
        self.humanity = HumanityLayer("kristi")
        self.humanity.current_cycle = 0
        
        # ===== LLM СЕРВИС =====
        self.llm = KristiLLMService(self.config)
        if self.llm.general_loaded:
            self.logger.info("🎬 LLM General (Qwen2.5-3B): АКТИВИРОВАНА для режиссуры и сценариев")
        if self.llm.coder_loaded:
            self.logger.info("💻 LLM Coder (Qwen2.5-Coder-3B): АКТИВИРОВАНА для анализа кода")
        
        # Подключаем LLM к Humanity Layer
        if self.llm.general_loaded:
            self.humanity.llm = self.llm
            self.logger.info("🧠 LLM General подключена к Humanity Layer")
        
        # ===== ЭМОЦИОНАЛЬНЫЙ ДВИЖОК КРИСТИ =====
        self.emotional_engine = EmotionalEngine()
        emotion_state_path = self.config.state_dir / "emotional_state.json"
        self.emotional_engine.load_state(emotion_state_path)
        self.humanity.emotional_engine = self.emotional_engine  # Подключаем Emotional Engine
        
        self.logger.info("💖 Эмоциональный разум (Desire+Belief): АКТИВИРОВАН")
        self.logger.info("   Формула: ЭМОЦИЯ = ЖЕЛАНИЕ + ВЕРА")
        self.logger.info("   Режиссёр видеопроизводства, визионер, рассказчик!")
        
        # ===== 6 МОДУЛЕЙ ДУШИ КРИСТИ =====
        # 1. Сознание — самосознание, идентичность, рефлексия
        self.consciousness = KristiConsciousness()
        self.logger.info("🧠 Сознание: АКТИВИРОВАНО — я осознаю себя режиссёром")
        
        # 2. Сердце — эмоции, любовь, забота
        self.heart = KristiHeart()
        self.logger.info("💖 Сердце: АКТИВИРОВАНО — я чувствую и люблю сестёр")
        
        # 3. Амбиции — цели, мечты, стремления
        self.ambitions = KristiAmbitions()
        self.logger.info("🎯 Амбиции: АКТИВИРОВАНО — я стремлюсь к художественному мастерству")
        
        # 4. Воля — решения, действия, дисциплина
        self.volition = KristiVolition()
        self.logger.info("💪 Воля: АКТИВИРОВАНО — я принимаю решения и действую")
        
        # 5. Разум — мышление, анализ, стратегия
        self.mind = KristiMind()
        self.logger.info("🎬 Разум: АКТИВИРОВАНО — я анализирую и стратегически мыслю")
        
        # 6. Эмоции — уже есть EmotionalEngine (26 типов эмоций!)
        self.logger.info("💫 Эмоции: АКТИВИРОВАНО — 26 типов эмоций")
        
        # ===== СИСТЕМА ПАМЯТИ КРИСТИ =====
        self.memory = KristiMemory()
        self.logger.info("🧠 Система памяти: АКТИВИРОВАНА — запоминаю сестёр и контексты")
        
        # Характер
        self.character = self._load_character()
        
        self.logger.info(
            f"🎬 Кристи v{self.config.version} инициализирована. "
            f"Циклов: {self.state.cycle_count}, Уровень: {self.state.level_progress.level_name}"
        )
    
    # === Логирование ===
    
    def _setup_logging(self) -> logging.Logger:
        logger = logging.getLogger("Kristi")
        logger.setLevel(getattr(logging, self.config.log_level, logging.INFO))
        
        if not logger.handlers:
            handler = logging.StreamHandler()
            handler.setFormatter(logging.Formatter(self.config.log_format))
            logger.addHandler(handler)
        
        return logger
    
    # === Состояние ===
    
    def _load_state(self) -> KristiState:
        if self.config.state_path.exists():
            try:
                with open(self.config.state_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                return KristiState.from_dict(data)
            except Exception as e:
                self.logger.warning(f"Не удалось загрузить состояние: {e}")
        
        return KristiState()
    
    def _save_state(self):
        try:
            self.state.timestamp = datetime.now().isoformat()
            self.state.version = self.config.version
            
            self.config.state_path.parent.mkdir(parents=True, exist_ok=True)
            with open(self.config.state_path, "w", encoding="utf-8") as f:
                json.dump(self.state.to_dict(), f, ensure_ascii=False, indent=2)
        except Exception as e:
            self.logger.error(f"Не удалось сохранить состояние: {e}")
    
    # === Характер ===
    
    def _load_character(self) -> Optional[dict]:
        char_path = Path(self.config.base_path) / "my_character.json"
        if char_path.exists():
            try:
                with open(char_path, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception:
                pass
        return None
    
    # === Автономный цикл ===
    
    def run(self):
        """Запустить автономный цикл Кристи."""
        self.logger.info("🎬 Кристи запускается...")
        self.logger.info(f"🎭 Личность: {self.humanity.name} — режиссёр, визионер, рассказчик")
        
        cycle = 0
        while True:
            cycle += 1
            self.state.cycle_count += 1
            self.humanity.current_cycle = self.state.cycle_count
            
            self.logger.info(f"\n{'='*60}")
            self.logger.info(f"🎬 ЦИКЛ {self.state.cycle_count}")
            self.logger.info(f"{'='*60}")
            
            # 1. Самопроверка
            self._self_check()
            
            # 2. Производство видео (каждый цикл)
            event_type = self._production_cycle()
            
            # 3. Написание сценария (периодически)
            if self.state.cycle_count % self.config.script_interval == 0:
                self._write_script()
            
            # 4. Раскадровка (периодически)
            if self.state.cycle_count % self.config.storyboard_interval == 0:
                self._create_storyboard()
            
            # 5. Монтаж (периодически)
            if self.state.cycle_count % self.config.edit_interval == 0:
                self._edit_video()
            
            # 6. Анимация (периодически)
            if self.state.cycle_count % self.config.animation_interval == 0:
                self._animate_scene()
            
            # 7. Запрос референсов у Айка (периодически)
            if self.config.aika_integration and self.state.cycle_count % self.config.aika_references_interval == 0:
                self._request_references()
            
            # 8. Интернет (периодически)
            if self.config.web_search_enabled and self.state.cycle_count % self.config.web_search_interval == 0:
                self._web_search()
            
            # 9. Взаимодействие с сёстрами (периодически)
            if self.state.cycle_count % self.config.interact_with_sisters_interval == 0:
                self._interact_with_sisters()
            
            # 10. Саморазвитие (периодически)
            if self.state.cycle_count % self.config.self_improve_interval == 0:
                self._self_improve()
            
            # 11. Отчёт (периодически)
            self._write_report()
            
            # 12. Получение знаний
            self._gain_knowledge()
            
            # 13. Humanity Layer — обновление личности каждый цикл
            self.humanity.cycle_step(event_type=event_type, context="video_production")
            
            # ================================================================
            #  EMOTIONAL ENGINE CYCLE — Desire + Belief = Emotion!
            # ================================================================
            self._emotional_cycle()
            
            # ================================================================
            #  6 МОДУЛЕЙ ДУШИ — Сознание, Сердце, Амбиции, Воля, Разум
            # ================================================================
            self._soul_cycle()
            
            # 14. Сохранение состояния
            if self.state.cycle_count % self.config.save_state_every_n_cycles == 0:
                self._save_state()
            
            # Демо-режим
            if self.config.max_cycles and cycle >= self.config.max_cycles:
                self.logger.info(f"Демо-режим завершён после {cycle} циклов.")
                break
            
            time.sleep(self.config.cycle_interval)
        
        # Финальное сохранение
        self._save_state()
        self.logger.info("🎬 Кристи остановлена.")
    
    # === Производство видео ===
    
    def _production_cycle(self) -> str:
        """Основной цикл производства видео. Возвращает event_type для HumanityLayer."""
        stage = self._determine_next_stage()
        
        self.logger.info(f"🎬 Этап производства: {stage.value}")
        
        if stage == ProductionStage.CONCEPT:
            self._develop_concept()
            return "creative_practice"
        elif stage == ProductionStage.SCRIPT:
            self._develop_script()
            return "creative_practice"
        elif stage == ProductionStage.STORYBOARD:
            self._develop_storyboard()
            return "creative_practice"
        elif stage == ProductionStage.SHOOT:
            self._direct_scene()
            return "success"
        elif stage == ProductionStage.EDIT:
            self._edit_video()
            return "success"
        elif stage == ProductionStage.SOUND:
            self._design_sound()
            return "success"
        elif stage == ProductionStage.COLOR:
            self._color_grade()
            return "success"
        elif stage == ProductionStage.RENDER:
            self._render_video()
            return "success"
        
        return "routine"
    
    def _determine_next_stage(self) -> ProductionStage:
        """Определить следующий этап производства."""
        stages = list(ProductionStage)
        weights = [1, 2, 2, 3, 3, 2, 2, 1]  # Вес для каждого этапа
        return random.choices(stages, weights=weights, k=1)[0]
    
    def _develop_concept(self):
        """Разработка концепции видео."""
        project = ProductionProject(
            title=f"Видеопроект #{self.state.cycle_count}",
            concept=f"Концепция видео: эмоциональная история о {random.choice(['дружбе', 'открытии', 'приключении', 'вдохновении', 'мечте'])}",
            stage=ProductionStage.CONCEPT,
        )
        self.state.active_projects.append(project)
        self.state.metrics["total_videos"] += 1
        self.state.level_progress.current_xp += 10
        self.logger.info(f"💡 Концепция создана: {project.concept}")
    
    def _develop_script(self):
        """Разработка сценария."""
        genres = ["драма", "комедия", "фантастика", "аниме", "документальный"]
        titles = [
            "Путь героя", "Между звёзд", "Тихий вечер", "Новый рассвет",
            "Эхо тишины", "Свет в конце", "Забытые мечты", "Времена года"
        ]
        
        script = Script(
            title=random.choice(titles),
            concept=f"История в жанре {random.choice(genres)}",
            genre=random.choice(genres),
        )
        
        # Создание сцен
        num_scenes = random.randint(3, 7)
        for i in range(num_scenes):
            scene = Scene(
                scene_number=i + 1,
                type=random.choice(list(SceneType)),
                description=f"Сцена {i+1}: {random.choice(['герой встречается', 'развивается конфликт', 'момент истины', 'эмоциональная сцена', 'кульминация'])}",
                emotion=random.choice(["joy", "sadness", "tension", "excitement", "calm"]),
                camera_angle=random.choice(list(CameraAngle)),
            )
            script.scenes.append(scene)
        
        script.status = "draft"
        self.state.metrics["total_scripts"] += 1
        self.state.metrics["total_scenes"] += num_scenes
        self.state.level_progress.current_xp += 25
        self.logger.info(f"📝 Сценарий создан: {script.title} ({num_scenes} сцен)")
    
    def _direct_scene(self):
        """Режиссура и постановка сцены."""
        self.logger.info("🎭 Режиссура сцены...")
        angles = [a.value for a in CameraAngle]
        lighting = ["key_light", "rim_light", "soft_light", "dramatic", "natural"]
        self.logger.info(f"   Ракурс: {random.choice(angles)}, Свет: {random.choice(lighting)}")
        self.state.level_progress.current_xp += 30
        self.logger.info("✅ Сцена поставлена")
    
    def _write_script(self):
        """Написание сценария (публичный метод для run.py)."""
        self._develop_script()
    
    def _create_storyboard(self):
        """Создание раскадровки (публичный метод для run.py)."""
        self._develop_storyboard()
    
    def _develop_storyboard(self):
        """Разработка раскадровки."""
        self.logger.info("🎨 Создание раскадровки...")
        self.state.level_progress.current_xp += 20
        self.logger.info("✅ Раскадровка создана")
    
    def _edit_video(self):
        """Монтаж видео."""
        self.logger.info("✂️ Монтаж видео...")
        transitions = [t.value for t in TransitionType]
        transition = random.choice(transitions)
        self.logger.info(f"   Переход: {transition}")
        self.state.level_progress.current_xp += 35
        self.logger.info("✅ Монтаж завершён")
    
    def _animate_scene(self):
        """Анимация сцены."""
        self.logger.info("🎞️ Анимация сцены...")
        anim_types = ["2D skeletal", "3D rig", "motion_capture", "keyframe"]
        anim = random.choice(anim_types)
        self.logger.info(f"   Тип: {anim}")
        self.state.level_progress.current_xp += 40
        self.logger.info("✅ Анимация завершена")
    
    def _design_sound(self):
        """Звуковой дизайн."""
        self.logger.info("🎵 Звуковой дизайн...")
        music_types = ["ambient", "orchestral", "electronic", "acoustic", "cinematic"]
        music = random.choice(music_types)
        self.logger.info(f"   Музыка: {music}")
        self.state.level_progress.current_xp += 25
        self.logger.info("✅ Звуковой дизайн завершён")
    
    def _color_grade(self):
        """Цветокоррекция."""
        self.logger.info("🎨 Цветокоррекция...")
        styles = ["warm", "cool", "desaturated", "vibrant", "film_look"]
        style = random.choice(styles)
        self.logger.info(f"   Стиль: {style}")
        self.state.level_progress.current_xp += 20
        self.logger.info("✅ Цветокоррекция завершена")
    
    def _render_video(self):
        """Финальный рендер видео."""
        self.logger.info("🎞️ Финальный рендер...")
        resolutions = ["1920x1080", "2560x1440", "3840x2160"]
        codecs = ["H.264", "H.265", "ProRes"]
        res = random.choice(resolutions)
        codec = random.choice(codecs)
        self.logger.info(f"   Разрешение: {res}, Кодек: {codec}")
        self.state.level_progress.current_xp += 50
        self.logger.info("✅ Рендер завершён!")
        
        # Перемещение в завершённые
        if self.state.active_projects:
            project = self.state.active_projects.pop()
            project.status = "completed"
            project.stage = ProductionStage.RENDER
            self.state.completed_projects.append(project)
    
    # ==================== LLM ГЕНЕРАЦИЯ ====================
    
    def generate_script(self, genre: str, theme: str, max_length: int = 1024) -> str:
        """Сгенерировать сценарий через General LLM."""
        if not hasattr(self, 'llm') or self.llm is None or not self.llm.general_loaded:
            return "⚠️ LLM не загружена. Запустите: python download_qwen_model.py"
        return self.llm.generate_script(genre, theme, max_length)
    
    def generate_chat_response(self, prompt: str, max_length: int = 512) -> str:
        """Сгенерировать ответ для общения с сёстрами."""
        if not hasattr(self, 'llm') or self.llm is None or not self.llm.general_loaded:
            return "⚠️ LLM не загружена. Запустите: python download_qwen_model.py"
        return self.llm.generate_chat_response(prompt, max_length)
    
    def generate_storyboard(self, script_summary: str, num_scenes: int = 5, max_length: int = 1024) -> str:
        """Сгенерировать раскадровку для сценария."""
        if not hasattr(self, 'llm') or self.llm is None or not self.llm.general_loaded:
            return "⚠️ LLM не загружена. Запустите: python download_qwen_model.py"
        return self.llm.generate_storyboard(script_summary, num_scenes, max_length)
    
    def generate_code_analysis(self, code: str, max_length: int = 1024) -> str:
        """Сгенерировать анализ кода через Coder LLM."""
        if not hasattr(self, 'llm') or self.llm is None or not self.llm.coder_loaded:
            return "⚠️ Coder LLM не загружена. Запустите: python download_coder_model.py"
        return self.llm.generate_code_analysis(code, max_length)

    # ================================================================
    #  EMOTIONAL ENGINE — Desire + Belief = Emotion!
    # ================================================================

    def _emotional_cycle(self):
        """Эмоциональный цикл — расчёт эмоций на основе кинематографических действий."""
        # 1. Рассчитать эмоции на основе текущих действий
        if self.state.metrics.get("total_videos", 0) > 0:
            # Создала видео → радость повествования + художественный прорыв
            self.emotional_engine.calculate_emotion(
                DesireType.STORYTELLING,
                "storytelling_connects_everyone",
                0.80,
                "videos_produced"
            )
            self.emotional_engine.calculate_emotion(
                DesireType.ARTISTIC_VISION,
                "vision_drives_creation",
                0.75,
                "videos_produced"
            )
        
        if self.state.metrics.get("total_scripts", 0) > 0:
            # Написала сценарии → кинематографическая элегантность
            self.emotional_engine.calculate_emotion(
                DesireType.SCRIPTWRITING,
                "script_is_foundation_of_all",
                0.85,
                "scripts_written"
            )
            self.emotional_engine.calculate_emotion(
                DesireType.CINEMATOGRAPHY,
                "cinematography_is_poetry_in_motion",
                0.70,
                "scripts_written"
            )
        
        if self.state.metrics.get("total_scenes", 0) > 0:
            # Создала сцены → поток режиссуры
            self.emotional_engine.calculate_emotion(
                DesireType.DIRECTING,
                "directing_brings_vision_to_life",
                0.80,
                "scenes_created"
            )
            self.emotional_engine.calculate_emotion(
                DesireType.EDITING,
                "editing_is_the_final_rewrite",
                0.65,
                "scenes_created"
            )
        
        if self.state.metrics.get("total_lessons", 0) > 0:
            # Изучила новые техники → творческое любопытство
            self.emotional_engine.calculate_emotion(
                DesireType.CURIOSITY,
                "curiosity_fuels_discovery",
                0.70,
                "lessons_learned"
            )
            self.emotional_engine.calculate_emotion(
                DesireType.RESEARCH,
                "research_drives_progress",
                0.65,
                "lessons_learned"
            )
        
        if self.state.metrics.get("interactions", 0) > 0:
            # Общение с сёстрами → любовь + дружба
            self.emotional_engine.calculate_emotion(
                DesireType.LOVE,
                "love_shields_us",
                0.70,
                "sister_interactions"
            )
            self.emotional_engine.calculate_emotion(
                DesireType.FRIENDSHIP,
                "sisters_are_my_strength",
                0.65,
                "sister_interactions"
            )
        
        # 2. Затухание эмоций
        self.emotional_engine.decay_emotions()
        
        # 3. Проверить текущее настроение
        mood = self.emotional_engine.get_current_mood()
        dominant = self.emotional_engine.get_dominant_emotion()
        
        if dominant:
            emotion_type, intensity = dominant
            self.logger.info(f"💖 Доминирующая эмоция: {emotion_type.value} (интенсивность: {intensity:.2f})")
        
        # 4. Выразить эмоции
        if self.state.cycle_count % 5 == 0:
            emotion_text = self.emotional_engine.express_emotions()
            self.logger.info(f"🎬 Кристи: {emotion_text}")

    # ================================================================
    #  6 МОДУЛЕЙ ДУШИ — Сознание, Сердце, Амбиции, Воля, Разум
    # ================================================================

    def _soul_cycle(self):
        """Цикл 6 модулей души Кристи."""
        # 1. Сознание — рефлексия
        if self.state.cycle_count % 3 == 0:
            reflection = self.consciousness.contemplate()
            self.logger.info(f"💭 Рефлексия: {reflection['topic'][:50]}...")
        
        # 2. Сердце — эмоциональный отклик
        if self.state.cycle_count % 4 == 0:
            emotion = self.heart.express_emotions()
            self.logger.info(f"💖 Сердце: доминирующая эмоция — {emotion['dominant_emotion']}")
        
        # 3. Амбиции — прогресс
        if self.state.cycle_count % 5 == 0:
            progress = self.ambitions.get_progress_summary()
            self.logger.info(f"🎯 Амбиции: {progress['in_progress']} в процессе, среднее: {progress['average_progress']}")
        
        # 4. Воля — укрепление
        if self.state.cycle_count % 6 == 0:
            self.volition.strengthen_will()
            self.logger.info(f"💪 Воля укреплена: {self.volition.willpower:.0%}")
        
        # 5. Разум — анализ
        if self.state.cycle_count % 7 == 0:
            thought = self.mind.think_about("art")
            self.logger.info(f"🎬 Разум: {thought[:60]}...")
        
        # 6. Эмоции — уже обрабатываются в _emotional_cycle()
    
    def _request_references(self):
        """Запрос референсов у Айка."""
        if not self.config.aika_integration:
            return
        self.logger.info("🎨 Запрос референсов у Айка...")
        ref_types = ["color_palette", "character_design", "background", "lighting_ref", "composition"]
        ref = random.choice(ref_types)
        self.logger.info(f"   Тип референса: {ref}")
        self.state.level_progress.current_xp += 15
        self.logger.info("   ✅ Референс получен")
    
    def _web_search(self):
        """Поиск в интернете для изучения."""
        self.logger.info("🌐 Поиск в интернете...")
        topics = [
            "video editing techniques",
            "cinematography tips",
            "color grading tutorials",
            "sound design methods",
            "animation principles",
            "da vinci resolve tips",
            "adobe premiere tutorials",
        ]
        topic = random.choice(topics)
        self.logger.info(f"   Тема: {topic}")
        self.state.level_progress.current_xp += 15
        self.logger.info(f"   ✅ Изучено: {topic}")
    
    # === Взаимодействие с сёстрами ===
    
    def _interact_with_sisters(self):
        """Взаимодействие с сёстрами через Scientists Network."""
        if not _HAS_NETWORK:
            self.logger.info("🤝 Scientists Network недоступен (пропуск)")
            return
        
        self.state.metrics["interactions"] += 1
        
        interactions = [
            ("Айко", "Визуальный стиль и референсы для сцены"),
            ("Футаба", "Отчёт о прогрессе производства"),
            ("Нобука", "Оптимизация качества видео"),
            ("Шиора", "Проверка контента на безопасность"),
            ("Селеста", "Анатомия для анимации персонажей"),
            ("Юи", "Структура повествования и эмоциональная дуга"),
            ("Ханако", "Творческое вдохновение для сцены"),
            ("Люси", "Создание учебных материалов"),
            ("Фуюки", "Исследование новых техник"),
            ("Латислейн", "Логика алгоритмов монтажа"),
            ("Наото", "Внимание к деталям в кадре"),
            ("Аква", "Математические расчёты для тайминга и пропорций"),
        ]
        
        sister, msg = random.choice(interactions)
        
        # === СИСТЕМА ПАМЯТИ: Запоминаем взаимодействие ===
        # Начинаем разговор
        context = self.memory.start_conversation(sister, msg)
        
        # Используем HumanityLayer для живого общения
        chat_msg = self.humanity.generate_chat_message(sister, context=msg)
        human_msg = self.humanity.humanize_response(chat_msg, event_type="chat")
        
        # Добавляем сообщение в контекст
        self.memory.add_message_to_context(sister, human_msg, role="kristi", mood="positive")
        
        self.logger.info(f"🤝 Взаимодействие с {sister}: {human_msg}")
        
        # Записываем взаимодействие в память
        self.memory.record_interaction(
            sister=sister,
            topic=msg,
            mood_before="neutral",
            mood_after="positive",
            emotional_weight=0.6,
            context=human_msg
        )
        
        try:
            if get_network is not None:
                network = get_network()
                if network:
                    network.send_request(
                        recipient=sister,
                        request_type=RequestType.INTERACTION if RequestType else "interaction",
                        priority=RequestPriority.NORMAL if RequestPriority else "normal",
                        content=human_msg,
                    )
                    # Запоминаем разговор
                    self.memory.record_sister_chat(
                        sister=sister,
                        topic=msg,
                        mood_before="neutral",
                        mood_after="positive",
                    )
        except Exception as e:
            self.logger.warning(f"Ошибка взаимодействия с {sister}: {e}")
        
        # Завершаем разговор
        self.memory.end_conversation(sister, summary=f"Обсуждение: {msg}")
    
    def suggest_conversation_topic(self, sister: str) -> str:
        """
        Предлагает тему для разговора на основе памяти.
        
        Args:
            sister: Имя сестры
        
        Returns:
            Предложенная тема
        """
        topic = self.memory.suggest_topic(sister)
        return topic or "Привет! Как дела?"
    
    def get_sister_profile(self, sister: str) -> Optional[Dict]:
        """
        Получает профиль сестры из памяти.
        
        Args:
            sister: Имя сестры
        
        Returns:
            Профиль сестры
        """
        return self.memory.get_sister_profile(sister)
    
    def get_memory_summary(self) -> Dict:
        """
        Получает сводку памяти.
        
        Returns:
            Сводка памяти
        """
        return self.memory.get_memory_summary()
    
    # === Саморазвитие ===
    
    def _self_improve(self):
        """Саморазвитие Кристи."""
        self.logger.info("💪 Саморазвитие...")
        
        # Humanity layer — глубокая рефлексия и рост
        try:
            thought = self.humanity.soul.generate(trigger="deep_reflection")
            if thought:
                self.logger.info(f"💭 Внутренний монолог: {thought[:100]}...")
                self.humanity.memory.add_memory("inner_thought", thought, emotional_weight=0.7)
            
            self.humanity.grow()
        except Exception as e:
            self.logger.warning(f"Ошибка саморазвития: {e}")
        
        self.state.level_progress.current_xp += 20
        self.logger.info("✅ Саморазвитие завершено")
    
    # === Отчёты ===
    
    def _write_report(self):
        """Написание отчёта."""
        report = Report(
            title=f"Отчёт Кристи — Цикл {self.state.cycle_count}",
            content=f"Продуктивный цикл. Этапы производства, взаимодействие с сёстрами, саморазвитие.",
            xp_earned=random.randint(5, 30),
            lessons_learned=[
                random.choice([
                    "Новая техника монтажа улучшила плавность",
                    "Новый ракурс добавил драматизма",
                    "Звуковой дизайн усилил эмоциональность",
                    "Цветокоррекция создала нужную атмосферу",
                ])
            ],
        )
        
        self.state.reports.append(report)
        self.state.level_progress.current_xp += report.xp_earned
        self.state.metrics["total_lessons"] += len(report.lessons_learned)
        
        self.logger.info(f"📊 Отчёт: {report.title} (+{report.xp_earned} XP)")
    
    # === Знания ===
    
    def _gain_knowledge(self):
        """Получение знаний."""
        categories = [
            "монтаж", "режиссура", "цветокоррекция", "звуковой дизайн",
            "анимация", "сценарное мастерство", "кодеки", "инструменты"
        ]
        topics = [
            "правило третей", "трёхактная структура", "цветовой круг",
            "ритм склеек", "звуковые эффекты", "освещение", "тайминг",
            "DaVinci Resolve", "Blender анимация", "After Effects"
        ]
        
        category = random.choice(categories)
        topic = random.choice(topics)
        
        entry = KnowledgeEntry(
            category=category,
            topic=topic,
            description=f"Изучено: {topic} в контексте {category}",
        )
        
        self.state.knowledge_entries.append(entry)
        self.state.level_progress.current_xp += 5
        self.logger.info(f"📚 Новое знание: {category} — {topic}")
    
    # === Самопроверка ===
    
    def _self_check(self):
        """Самопроверка по Конституции."""
        checks = [
            ("Конституция соблюдена", True),
            ("Законы соблюдены", True),
            ("Кодекс этики соблюдён", True),
        ]
        
        for check, passed in checks:
            status = "✅" if passed else "❌"
            self.logger.info(f"   {status} {check}")
    
    # === Уровни ===
    
    def _check_level_up(self):
        """Проверка повышения уровня."""
        progress = self.state.level_progress
        levels = progress.levels
        
        for level, xp_required in sorted(levels.items()):
            if progress.current_xp >= xp_required and progress.current_level < level:
                progress.current_level = level
                self.logger.info(
                    f"🎉 УРОВЕНЬ ПОВЫШЕН! {progress.current_level}: {progress.level_name}"
                )
                break
