"""
Люси — инженер двигателей.

Реализует:
  - Изучение двигателестроения в интернете
  - Анализ теорий Ханако и Фуюки
  - Проектирование двигателей
  - Расчёты характеристик
  - Поиск способов создания гибридных двигателей
"""

from __future__ import annotations
import json
import logging
import random
import time
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

from lucy.engine.config import LucyConfig
from lucy.engine.models import (
    ResearchRecord, EngineDesign, Calculation, EngineType,
    PropulsionPrinciple, EngineConstants, ResearchPaper
)
from lucy.engine.web_access import LucyWebAccess
from lucy.engine.designer import EngineDesigner
from lucy.engine.calculator import EngineCalculator
from scientists_network.network import get_network, RequestType, RequestPriority


class LucyCore:
    """
    Ядро Люси — автономный инженер двигателей.
    
    Работает в бесконечном цикле:
      1. Изучение двигателестроения в интернете
      2. Анализ теорий Ханако и Фуюки
      3. Проектирование двигателей
      4. Расчёты характеристик
      5. Поиск оптимальных решений
      6. Логирование и сохранение
    """
    
    def __init__(self, config: Optional[LucyConfig] = None):
        self.config = config or LucyConfig.default()
        
        # Состояние
        self.cycle_count = 0
        self.research_history: List[ResearchRecord] = []
        self.designs: List[EngineDesign] = []
        self.calculations: List[Calculation] = []
        self.papers: List[ResearchPaper] = []
        
        self.metrics = {
            "designs_created": 0,
            "calculations_run": 0,
            "papers_studied": 0,
            "web_searches": 0,
            "hanako_theories_analyzed": 0,
            "fuyuki_theories_analyzed": 0,
            "hybrid_engines_designed": 0,
        }
        
        # Константы
        self.constants = EngineConstants()
        
        # Логирование
        self._setup_logging()
        self.logger = logging.getLogger("LucyCore")
        
        # Компоненты
        self.web_access = LucyWebAccess(self.config)
        self.designer = EngineDesigner(self.config)
        self.calculator = EngineCalculator(self.config)
        
        # Сеть учёных
        self.network = get_network()
        
        # Данные от сестёр
        self.hanako_theories: List[Dict[str, Any]] = []
        self.fuyuki_theories: List[Dict[str, Any]] = []
        
        # Загрузка данных
        self._load_state()
        self._load_sisters_data()
        
        self.logger.info(f"Люси {self.config.version} инициализирована")
        self.logger.info(f"Фокус исследований: {self.config.research_focus}")
        self.logger.info("🔗 Подключена к Scientists Network")
        self.logger.info(f"   Теорий Ханако: {len(self.hanako_theories)}")
        self.logger.info(f"   Теорий Фуюки: {len(self.fuyuki_theories)}")
        self.network.print_mission_reminder()
    
    def _setup_logging(self):
        """Настроить логирование."""
        self.config.log_dir.mkdir(parents=True, exist_ok=True)
        log_file = self.config.log_dir / f"lucy_{datetime.now().strftime('%Y%m%d')}.log"
        
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
        designs_file = self.config.state_dir / "designs.json"
        if designs_file.exists():
            try:
                with open(designs_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    self.designs = [EngineDesign.from_dict(d) for d in data.get("designs", [])]
                    self.logger.info(f"Загружено проектов: {len(self.designs)}")
            except (json.JSONDecodeError, Exception) as e:
                self.logger.warning(f"Не удалось загрузить проекты: {e}")
                self.designs = []
        
        calc_file = self.config.state_dir / "calculations.json"
        if calc_file.exists():
            try:
                with open(calc_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    self.calculations = [Calculation(**c) for c in data.get("calculations", [])]
                    self.logger.info(f"Загружено расчётов: {len(self.calculations)}")
            except (json.JSONDecodeError, Exception) as e:
                self.logger.warning(f"Не удалось загрузить расчёты: {e}")
                self.calculations = []
    
    def _load_sisters_data(self):
        """Загрузить данные от Ханако и Фуюки через сеть."""
        try:
            self.hanako_theories = self.network.get_hanako_theories()
            self.fuyuki_theories = self.network.get_fuyuki_theories()
            self.metrics["hanako_theories_analyzed"] = len(self.hanako_theories)
            self.metrics["fuyuki_theories_analyzed"] = len(self.fuyuki_theories)
        except Exception as e:
            self.logger.warning(f"Ошибка загрузки данных сестёр: {e}")
            # Fallback на прямое чтение
            hanako_theories_file = Path("hanako/engine/state/theories.json")
            if hanako_theories_file.exists():
                try:
                    with open(hanako_theories_file, "r", encoding="utf-8") as f:
                        data = json.load(f)
                        self.hanako_theories = data.get("theories", [])
                except Exception:
                    pass
            
            fuyuki_theories_file = Path("fuyuki/engine/state/theories.json")
            if fuyuki_theories_file.exists():
                try:
                    with open(fuyuki_theories_file, "r", encoding="utf-8") as f:
                        data = json.load(f)
                        self.fuyuki_theories = data.get("theories", [])
                except Exception:
                    pass
    
    def _save_state(self):
        """Сохранить состояние."""
        designs_file = self.config.state_dir / "designs.json"
        with open(designs_file, "w", encoding="utf-8") as f:
            json.dump({
                "designs": [d.to_dict() for d in self.designs],
                "updated": datetime.now().isoformat()
            }, f, ensure_ascii=False, indent=2)
        
        calc_file = self.config.state_dir / "calculations.json"
        with open(calc_file, "w", encoding="utf-8") as f:
            json.dump({
                "calculations": [c.to_dict() for c in self.calculations],
                "updated": datetime.now().isoformat()
            }, f, ensure_ascii=False, indent=2)
    
    def run(self):
        """Запустить автономный цикл проектирования."""
        self.logger.info("🚀 Запуск автономного цикла проектирования двигателей")
        
        try:
            while True:
                if self._should_stop():
                    self.logger.info("Завершение цикла проектирования")
                    break
                
                self._cycle()
                time.sleep(self.config.cycle_interval)
                
        except KeyboardInterrupt:
            self.logger.info("Проектирование приостановлено пользователем")
        finally:
            self._save_state()
    
    def _should_stop(self) -> bool:
        """Проверить условие остановки."""
        if self.config.max_cycles > 0 and self.cycle_count >= self.config.max_cycles:
            return True
        return False
    
    def _cycle(self):
        """Один цикл проектирования."""
        self.cycle_count += 1
        self.logger.info(f"=== ЦИКЛ ПРОЕКТИРОВАНИЯ {self.cycle_count} ===")
        
        # 1. Изучение в интернете (каждые 3 цикла)
        if self.cycle_count % self.config.web_search_interval == 0:
            self._research_from_web()
        
        # 2. Обновление теорий от сестёр (каждые 5 циклов)
        if self.cycle_count % 5 == 0:
            self._refresh_sisters_data()
        
        # 3. Проектирование двигателей
        self._design_engines()
        
        # 4. Расчёты характеристик
        self._run_calculations()
        
        # 5. Поиск гибридных решений
        self._seek_hybrid_solutions()
        
        # 6. Синхронизация с сетью (каждые 10 циклов)
        if self.cycle_count % 10 == 0:
            self._sync_with_network()
        
        # 7. Сохранение
        self._save_state()
        
        self.logger.info(f"Цикл {self.cycle_count} завершён")
    
    def _refresh_sisters_data(self):
        """Обновить данные от Ханако и Фуюки."""
        try:
            self.logger.info("🔗 Обновление данных от сестёр")
            
            new_hanako = self.network.get_hanako_theories()
            new_fuyuki = self.network.get_fuyuki_theories()
            
            if len(new_hanako) > len(self.hanako_theories):
                self.logger.info(f"   Ханако: {len(self.hanako_theories)} → {len(new_hanako)} теорий (+{len(new_hanako) - len(self.hanako_theories)})")
                self.hanako_theories = new_hanako
                self.metrics["hanako_theories_analyzed"] = len(self.hanako_theories)
            
            if len(new_fuyuki) > len(self.fuyuki_theories):
                self.logger.info(f"   Фуюки: {len(self.fuyuki_theories)} → {len(new_fuyuki)} теорий (+{len(new_fuyuki) - len(self.fuyuki_theories)})")
                self.fuyuki_theories = new_fuyuki
                self.metrics["fuyuki_theories_analyzed"] = len(self.fuyuki_theories)
            
        except Exception as e:
            self.logger.error(f"Ошибка обновления данных: {e}")
    
    def _sync_with_network(self):
        """Синхронизация с сетью учёных."""
        try:
            self.logger.info("🔗 Синхронизация с Scientists Network")
            
            # Уведомление о новых проектах
            new_designs = [d for d in self.designs[-5:] if d.feasibility_score > 0.5]
            if new_designs:
                for design in new_designs:
                    self.network.notify_discovery(
                        from_scientist="lucy",
                        discovery=f"Двигатель: {design.name} (тяга: {design.thrust:.1f} N, Isp: {design.specific_impulse:.1f} s)",
                        importance="high" if design.feasibility_score > 0.7 else "normal"
                    )
            
            # Запрос помощи у Нобуки при критических проблемах
            low_feasibility = [d for d in self.designs[-10:] if d.feasibility_score < 0.2]
            if len(low_feasibility) > 5:
                self.network.create_request(
                    from_scientist="lucy",
                    to_scientist="nobuka",
                    request_type=RequestType.CODE_REVIEW,
                    message=f"Слишком много нереализуемых проектов ({len(low_feasibility)} из 10). Нужен анализ!",
                    priority=RequestPriority.HIGH,
                    data={"low_feasibility_count": len(low_feasibility)}
                )
            
            # Запрос новых теорий у сестёр
            if len(self.hanako_theories) < 5:
                self.network.create_request(
                    from_scientist="lucy",
                    to_scientist="hanako",
                    request_type=RequestType.THEORY_REQUEST,
                    message="Нужно больше теорий гравитации для проектирования двигателей!",
                    priority=RequestPriority.NORMAL
                )
            
            if len(self.fuyuki_theories) < 5:
                self.network.create_request(
                    from_scientist="lucy",
                    to_scientist="fuyuki",
                    request_type=RequestType.THEORY_REQUEST,
                    message="Нужно больше теорий электричества для проектирования двигателей!",
                    priority=RequestPriority.NORMAL
                )
            
        except Exception as e:
            self.logger.error(f"Ошибка синхронизации: {e}")
    
    def _research_from_web(self):
        """Исследование в интернете."""
        try:
            self.logger.info("🌐 Поиск исследований о двигателях")
            
            papers = self.web_access.search_engine_papers()
            self.papers.extend(papers)
            self.metrics["papers_studied"] += len(papers)
            self.metrics["web_searches"] += 1
            
            self.logger.info(f"Найдено статей: {len(papers)}")
            
        except Exception as e:
            self.logger.error(f"Ошибка исследования: {e}")
    
    def _design_engines(self):
        """Проектирование двигателей."""
        try:
            self.logger.info("⚙️ Проектирование двигателей")
            
            design = self.designer.generate_design(
                self.papers,
                self.hanako_theories,
                self.fuyuki_theories
            )
            
            if design:
                self.designs.append(design)
                self.metrics["designs_created"] += 1
                
                if design.engine_type == EngineType.HYBRID:
                    self.metrics["hybrid_engines_designed"] += 1
                
                self.logger.info(f"Спроектирован двигатель: {design.name}")
                self.logger.info(f"Тип: {design.engine_type.value}")
                self.logger.info(f"Тяга: {design.thrust:.2f} N")
                self.logger.info(f"Удельный импульс: {design.specific_impulse:.2f} s")
                self.logger.info(f"Эффективность: {design.efficiency:.2f}")
                
                if design.gravity_theory_used:
                    self.logger.info(f"Теория Ханако: {design.gravity_theory_used}")
                if design.electricity_theory_used:
                    self.logger.info(f"Теория Фуюки: {design.electricity_theory_used}")
            
        except Exception as e:
            self.logger.error(f"Ошибка проектирования: {e}")
    
    def _run_calculations(self):
        """Выполнение расчётов."""
        try:
            self.logger.info("🧮 Выполнение расчётов двигателей")
            
            # Случайный тип расчёта
            calc_types = ["thrust", "specific_impulse", "power", "efficiency"]
            calc_type = random.choice(calc_types)
            
            if calc_type == "thrust":
                calc = self.calculator.calculate_thrust(
                    random.uniform(0.1, 100),
                    random.uniform(1000, 50000)
                )
            elif calc_type == "specific_impulse":
                calc = self.calculator.calculate_specific_impulse(
                    random.uniform(10000, 100000)
                )
            elif calc_type == "power":
                calc = self.calculator.calculate_power(
                    random.uniform(100, 10000),
                    random.uniform(1000, 5000)
                )
            else:
                calc = self.calculator.calculate_efficiency(
                    random.uniform(100, 10000),
                    random.uniform(1e6, 1e9),
                    random.uniform(1000, 5000)
                )
            
            if calc:
                self.calculations.append(calc)
                self.metrics["calculations_run"] += 1
                
                self.logger.info(f"Расчёт: {calc_type}")
                self.logger.info(f"Результат: {calc.result} {calc.units}")
            
        except Exception as e:
            self.logger.error(f"Ошибка расчёта: {e}")
    
    def _seek_hybrid_solutions(self):
        """Поиск гибридных решений."""
        try:
            hybrid_designs = [
                d for d in self.designs
                if d.engine_type == EngineType.HYBRID and d.feasibility_score > 0.3
            ]
            
            if hybrid_designs:
                self.logger.info(f"🚀 Найдено {len(hybrid_designs)} перспективных гибридных двигателей")
                
                for design in hybrid_designs[:3]:
                    self.logger.info(f"  - {design.name}: эффективность {design.efficiency:.2f}")
            
        except Exception as e:
            self.logger.error(f"Ошибка поиска: {e}")
    
    def get_status(self) -> Dict[str, Any]:
        """Получить статус проектирования."""
        return {
            "name": self.config.name,
            "version": self.config.version,
            "cycle_count": self.cycle_count,
            "metrics": self.metrics,
            "designs_count": len(self.designs),
            "calculations_count": len(self.calculations),
            "papers_count": len(self.papers),
        }
