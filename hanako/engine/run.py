"""
Точка входа Ханако — исследователь гравитации.
"""

from __future__ import annotations

import argparse
import logging
import sys
import json
from pathlib import Path
from datetime import datetime

# UTF-8 кодировка для консоли
sys.stdout.reconfigure(encoding='utf-8')

from hanako.engine.config import HanakoConfig, AutonomyMode, WebSearchMode
from hanako.engine.hanako_core import HanakoCore


def setup_logging(log_dir: Path, verbose: bool = False):
    """Настройка логирования."""
    log_dir.mkdir(parents=True, exist_ok=True)
    log_file = log_dir / f"hanako_{datetime.now().strftime('%Y%m%d')}.log"

    level = logging.DEBUG if verbose else logging.INFO
    handlers = [
        logging.StreamHandler(sys.stdout),
        logging.FileHandler(log_file, encoding='utf-8', mode='a'),
    ]

    logging.basicConfig(
        level=level,
        format="%(asctime)s [%(name)s] %(levelname)s: %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
        handlers=handlers,
    )


def main():
    """Главная функция."""
    parser = argparse.ArgumentParser(description="Ханако — Исследователь гравитации")
    parser.add_argument("--config", type=str, default="default",
                        help="Режим конфигурации: default, demo, offline, godmode")
    parser.add_argument("--cycles", type=int, default=0,
                        help="Максимум циклов (0 = бесконечно)")
    parser.add_argument("--verbose", "-v", action="store_true",
                        help="Подробный режим")
    parser.add_argument("--status", action="store_true",
                        help="Показать статус")
    parser.add_argument("--report", action="store_true",
                        help="Сгенерировать отчёт")
    parser.add_argument("--character", action="store_true",
                        help="Создать/показать характер")
    parser.add_argument("--demo", action="store_true",
                        help="Демо-режим (быстрый запуск)")
    parser.add_argument("--research", action="store_true",
                        help="Только исследование")
    parser.add_argument("--theories", action="store_true",
                        help="Показать теории")
    parser.add_argument("--calc", action="store_true",
                        help="Вычислить гравитационные параметры")
    parser.add_argument("--communication", action="store_true",
                        help="Показать статистику общения")
    parser.add_argument("--level", action="store_true",
                        help="Показать уровень")
    parser.add_argument("--auto", action="store_true",
                        help="Включить автозапуск")
    parser.add_argument("--log-dir", type=str, default="hanako/engine/logs",
                        help="Директория логов")

    args = parser.parse_args()

    # Настройка логирования
    log_dir = Path(args.log_dir)
    setup_logging(log_dir, args.verbose)
    logger = logging.getLogger("HanakoMain")

    # Загрузка конфигурации
    config = _load_config(args.config, args.demo)

    # Создание ядра
    core = HanakoCore(config)

    # Обработка команд
    if args.status:
        print(core.get_summary())
        return

    if args.theories:
        theories = core.theorist.load_theories()
        print(f"Теорий: {len(theories)}")
        for t in theories:
            print(f"  • {t.title} ({t.category.value}) — уверенность: {t.confidence:.1%}")
        return

    if args.calc:
        calc = core.calculator
        print("=== Гравитационные вычисления ===")
        print(f"  Радиус Шварцшильда (Солнце): {calc.schwarzschild_radius(1.989e30):.2f} м = {calc.schwarzschild_radius(1.989e30)/1000:.1f} км")
        print(f"  Температура Хокинга (Солнце): {calc.hawking_temperature(1.989e30):.2e} K")
        print(f"  Планковская длина: {calc.planck_length():.2e} м")
        print(f"  Планковская масса: {calc.planck_mass():.2e} кг")
        print(f"  Планковское время: {calc.planck_time():.2e} с")
        return

    if args.character:
        traits = core.character.get_traits()
        print(core.character.get_character_summary())
        return

    if args.communication:
        stats = core.communication.get_communication_stats()
        print(f"Статистика общения:")
        print(f"  Всего сообщений: {stats['total_messages']}")
        print(f"  По типам: {stats['by_type']}")
        print(f"  По отправителям: {stats['by_sender']}")
        return

    if args.auto:
        core.auto_start.enable_auto_start()
        print("✅ Автозапуск включён")
        return

    if args.report:
        report = core.reports.generate_daily_report(core)
        if report:
            print(report.content)
        return

    if args.level:
        level = core.level
        print(f"Уровень: {level.overall_level} ({level.get_level_name()})")
        print(f"  Опыт: {level.overall_xp:.0f}/{level.xp_to_next:.0f}")
        print(f"  Гравитация: {level.gravity_theory_level}")
        print(f"  Интернет: {level.web_research_level}")
        print(f"  Саморазвитие: {level.self_development_level}")
        print(f"  Общение: {level.communication_level}")
        print(f"  Вычисления: {level.calculation_level}")
        print(f"  Характер: {level.character_growth_level}")
        return

    # Основной режим — запуск цикла
    logger.info(f"Запуск Ханако: config={args.config}, demo={args.demo}, cycles={args.cycles}")

    if args.research:
        # Только исследование
        core.start()
        cycle = 0
        try:
            while cycle < args.cycles or args.cycles == 0:
                core._do_research(datetime.now())
                cycle += 1
                logger.info(f"Исследование #{cycle}")
                if args.cycles > 0 and cycle >= args.cycles:
                    break
        except KeyboardInterrupt:
            pass
        finally:
            core.stop()
    else:
        # Полный цикл
        core.run_loop(max_cycles=args.cycles)


def _load_config(config_name: str, demo: bool) -> HanakoConfig:
    """Загрузка конфигурации."""
    if demo or config_name == "demo":
        return HanakoConfig.demo()
    elif config_name == "offline":
        return HanakoConfig.offline()
    elif config_name == "godmode":
        return HanakoConfig.godmode()
    else:
        return HanakoConfig.default()


if __name__ == "__main__":
    main()
