"""
Фуюки — исследователь атмосферного электричества.

Реализует:
  - Изучение атмосферного электричества в интернете
  - Построение теорий
  - Вычисления электрических параметров
  - Поиск способов обуздать атмосферное электричество
"""

from __future__ import annotations
import json
import logging
import random
import time
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

from fuyuki.engine.config import FuyukiConfig
from fuyuki.engine.models import (
    ResearchRecord, ElectricityTheory, Calculation, ElectricityTheoryCategory,
    CalculationType, ElectricityConstants, ResearchPaper, LightningStrike
)
from fuyuki.engine.web_access import FuyukiWebAccess
from fuyuki.engine.theorist import ElectricityTheorist
from fuyuki.engine.calculator import ElectricityCalculator
from scientists_network.network import get_network, RequestType, RequestPriority


class FuyukiCore:
    """
    Ядро Фуюки — автономный исследователь атмосферного электричества.
    """
    
    def __init__(self, config: Optional[FuyukiConfig] = None):
        self.config = config or FuyukiConfig.default()
        
        # Состояние
        self.cycle_count = 0
        self.research_history: List[ResearchRecord] = []
        self.theories: List[ElectricityTheory] = []
        self.calculations: List[Calculation] = []
        self.papers: List[ResearchPaper] = []
        
        self.metrics = {
            "theories_built": 0,
            "calculations_run": 0,
            "papers_studied": 0,
            "web_searches": 0,
            "lightning_secrets_found": 0,
        }
        
        # Константы
        self.constants = ElectricityConstants()
        
        # Логирование
        self._setup_logging()
        self.logger = logging.getLogger("FuyukiCore")
        
        # Компоненты
        self.web_access = FuyukiWebAccess(self.config)
        self.theorist = ElectricityTheorist(self.config)
        self.calculator = ElectricityCalculator(self.config)
        
        # Сеть учёных
        self.network = get_network()
        
        # Загрузка данных
        self._load_state()
        
        self.logger.info(f"Фуюки {self.config.version} инициализирована")
        self.logger.info(f"Фокус исследований: {self.config.research_focus}")
        self.logger.info("🔗 Подключена к Scientists Network")
        self.network.print_mission_reminder()
    
    def _setup_logging(self):
        """Настроить логирование."""
        self.config.log_dir.mkdir(parents=True, exist_ok=True)
        log_file = self.config.log_dir / f"fuyuki_{datetime.now().strftime('%Y%m%d')}.log"
        
        logging.basicConfig(
            level=getattr(logging, self.config.log_level),
            format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
            handlers=[
                logging.FileHandler(log_file, encoding="utf-8"),
                logging.StreamHandler()
            ]
        )
    
    def _load_state(self):
        """Загрузить состояние."""
        theories_file = self.config.state_dir / "theories.json"
        if theories_file.exists():
            try:
                with open(theories_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    self.theories = [ElectricityTheory.from_dict(t) for t in data.get("theories", [])]
                    self.logger.info(f"Загружено теорий: {len(self.theories)}")
            except (json.JSONDecodeError, Exception) as e:
                self.logger.warning(f"Не удалось загрузить теории: {e}")
                self.theories = []
        
        calc_file = self.config.state_dir / "calculations.json"
        if calc_file.exists():
            try:
                with open(calc_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    self.calculations = [Calculation.from_dict(c) for c in data.get("calculations", [])]
                    self.logger.info(f"Загружено вычислений: {len(self.calculations)}")
            except (json.JSONDecodeError, Exception) as e:
                self.logger.warning(f"Не удалось загрузить вычисления: {e}")
                self.calculations = []
    
    def _save_state(self):
        """Сохранить состояние."""
        theories_file = self.config.state_dir / "theories.json"
        with open(theories_file, "w", encoding="utf-8") as f:
            json.dump({
                "theories": [t.to_dict() for t in self.theories],
                "updated": datetime.now().isoformat()
            }, f, ensure_ascii=False, indent=2)
        
        calc_file = self.config.state_dir / "calculations.json"
        with open(calc_file, "w", encoding="utf-8") as f:
            json.dump({
                "calculations": [c.to_dict() for c in self.calculations],
                "updated": datetime.now().isoformat()
            }, f, ensure_ascii=False, indent=2)
    
    def run(self):
        """Запустить автономный цикл исследований."""
        self.logger.info("⚡ Запуск автономного цикла исследований атмосферного электричества")
        
        try:
            while True:
                if self._should_stop():
                    self.logger.info("Завершение цикла исследований")
                    break
                
                self._cycle()
                time.sleep(self.config.cycle_interval)
                
        except KeyboardInterrupt:
            self.logger.info("Исследования приостановлены пользователем")
        finally:
            self._save_state()
    
    def _should_stop(self) -> bool:
        """Проверить условие остановки."""
        if self.config.max_cycles > 0 and self.cycle_count >= self.config.max_cycles:
            return True
        return False
    
    def _cycle(self):
        """Один цикл исследований."""
        self.cycle_count += 1
        self.logger.info(f"=== ЦИКЛ ИССЛЕДОВАНИЙ {self.cycle_count} ===")
        
        if self.cycle_count % self.config.web_search_interval == 0:
            self._research_from_web()
        
        self._build_theories()
        self._run_calculations()
        self._seek_lightning_control()
        
        # Обмен данными с сетью (каждые 10 циклов)
        if self.cycle_count % 10 == 0:
            self._sync_with_network()
        
        self._save_state()
        
        self.logger.info(f"Цикл {self.cycle_count} завершён")
    
    def _sync_with_network(self):
        """Синхронизация с сетью учёных."""
        try:
            self.logger.info("🔗 Синхронизация с Scientists Network")
            
            # Уведомление об открытиях
            new_theories = [t for t in self.theories[-5:] if t.scientific_value > 0.8]
            if new_theories:
                for theory in new_theories:
                    self.network.notify_discovery(
                        from_scientist="fuyuki",
                        discovery=f"Теория: {theory.name} (ценность: {theory.scientific_value:.2f})",
                        importance="high" if theory.scientific_value > 0.9 else "normal"
                    )
            
            # Запрос помощи если нужно
            if len(self.theories) > 0 and len(self.theories) % 20 == 0:
                self.network.create_request(
                    from_scientist="fuyuki",
                    to_scientist="nobuka",
                    request_type=RequestType.VALIDATION,
                    message=f"Проверь последние 20 теорий электричества",
                    priority=RequestPriority.NORMAL,
                    data={"theories_count": len(self.theories)}
                )
            
        except Exception as e:
            self.logger.error(f"Ошибка синхронизации: {e}")
    
    def _research_from_web(self):
        """Исследование в интернете."""
        try:
            self.logger.info("🌐 Поиск исследований атмосферного электричества")
            
            papers = self.web_access.search_electricity_papers()
            self.papers.extend(papers)
            self.metrics["papers_studied"] += len(papers)
            self.metrics["web_searches"] += 1
            
            self.logger.info(f"Найдено статей: {len(papers)}")
            
        except Exception as e:
            self.logger.error(f"Ошибка исследования: {e}")
    
    def _build_theories(self):
        """Построение теорий."""
        try:
            self.logger.info("🔬 Построение теорий атмосферного электричества")
            
            theory = self.theorist.generate_theory(self.papers, self.theories)
            
            if theory:
                self.theories.append(theory)
                self.metrics["theories_built"] += 1
                
                self.logger.info(f"Построена теория: {theory.name}")
                self.logger.info(f"Категория: {theory.category.value}")
                self.logger.info(f"Научная ценность: {theory.scientific_value:.2f}")
            
        except Exception as e:
            self.logger.error(f"Ошибка построения теории: {e}")
    
    def _run_calculations(self):
        """Выполнение вычислений."""
        try:
            self.logger.info("🧮 Выполнение электрических вычислений")
            
            calc_types = list(CalculationType)
            calc_type = random.choice(calc_types)
            
            calculation = self.calculator.calculate(calc_type)
            
            if calculation:
                self.calculations.append(calculation)
                self.metrics["calculations_run"] += 1
                
                self.logger.info(f"Вычисление: {calc_type.value}")
                self.logger.info(f"Результат: {calculation.result} {calculation.units}")
            
        except Exception as e:
            self.logger.error(f"Ошибка вычисления: {e}")
    
    def _seek_lightning_control(self):
        """Поиск способов обуздать молнии."""
        try:
            viable_theories = [
                t for t in self.theories
                if t.scientific_value > 0.7 and t.category in [
                    ElectricityTheoryCategory.CONTROL,
                    ElectricityTheoryCategory.HARVESTING,
                    ElectricityTheoryCategory.BALL_LIGHTNING
                ]
            ]
            
            if viable_theories:
                self.logger.info(f"⚡ Найдено {len(viable_theories)} перспективных теорий для управления молниями")
                
                for theory in viable_theories[:3]:
                    self.logger.info(f"  - {theory.name}: ценность {theory.scientific_value:.2f}")
                    self.metrics["lightning_secrets_found"] += 1
            
        except Exception as e:
            self.logger.error(f"Ошибка поиска: {e}")
    
    def get_status(self) -> Dict[str, Any]:
        """Получить статус исследований."""
        return {
            "name": self.config.name,
            "version": self.config.version,
            "cycle_count": self.cycle_count,
            "metrics": self.metrics,
            "theories_count": len(self.theories),
            "calculations_count": len(self.calculations),
            "papers_count": len(self.papers),
        }
