"""
Калькулятор гравитационных параметров Ханако.
"""

from __future__ import annotations

import math
import random
import logging
from datetime import datetime
from pathlib import Path
from typing import Optional

from hanako.engine.config import HanakoConfig



class GravityCalculator:
    """
    Калькулятор гравитационных параметров.
    
    Возможности:
    - Вычисление гравитационных сил
    - Расчёт орбитальных параметров
    - Моделирование гравитационных полей
    - Расчёт параметров чёрных дыр
    - Вычисление гравитационных волн
    """

    # Константы
    G = 6.67430e-11       # Гравитационная постоянная (м³/(кг·с²))
    c = 299792458.0       # Скорость света (м/с)
    h_bar = 1.054571817e-34  # Постоянная Планка (Дж·с)
    k_B = 1.380649e-23    # Постоянная Больцмана (Дж/К)

    def __init__(self, config: HanakoConfig):
        self.config = config
        self.logger = logging.getLogger("GravityCalculator")

    def gravitational_force(self, m1: float, m2: float, r: float) -> float:
        """Вычисление гравитационной силы по закону Ньютона."""
        if r <= 0:
            raise ValueError("Расстояние должно быть больше 0")
        return self.G * m1 * m2 / (r ** 2)

    def escape_velocity(self, mass: float, radius: float) -> float:
        """Вычисление второй космической скорости."""
        if radius <= 0 or mass <= 0:
            raise ValueError("Масса и радиус должны быть больше 0")
        return math.sqrt(2 * self.G * mass / radius)

    def orbital_period(self, mass: float, radius: float) -> float:
        """Вычисление орбитального периода."""
        if radius <= 0 or mass <= 0:
            raise ValueError("Масса и радиус должны быть больше 0")
        return 2 * math.pi * math.sqrt(radius ** 3 / (self.G * mass))

    def schwarzschild_radius(self, mass: float) -> float:
        """Вычисление радиуса Шварцшильда (горизонт событий чёрной дыры)."""
        if mass <= 0:
            raise ValueError("Масса должна быть больше 0")
        return 2 * self.G * mass / (self.c ** 2)

    def hawking_temperature(self, mass: float) -> float:
        """Вычисление температуры Хокинга чёрной дыры."""
        if mass <= 0:
            raise ValueError("Масса должна быть больше 0")
        return self.h_bar * self.c ** 3 / (8 * math.pi * self.G * mass * self.k_B)

    def hawking_luminosity(self, mass: float) -> float:
        """Вычисление светимости Хокинга."""
        if mass <= 0:
            raise ValueError("Масса должна быть больше 0")
        temp = self.hawking_temperature(mass)
        return 4 * math.pi * (self.schwarzschild_radius(mass) ** 2) * 5.670374419e-8 * (temp ** 4)

    def gravitational_redshift(self, mass: float, radius: float) -> float:
        """Вычисление гравитационного красного смещения."""
        if radius <= 0 or mass <= 0:
            raise ValueError("Масса и радиус должны быть больше 0")
        return 1 / math.sqrt(1 - 2 * self.G * mass / (radius * self.c ** 2)) - 1

    def time_dilation(self, mass: float, radius: float) -> float:
        """Вычисление замедления времени в гравитационном поле."""
        if radius <= 0 or mass <= 0:
            raise ValueError("Масса и радиус должны быть больше 0")
        factor = 1 - 2 * self.G * mass / (radius * self.c ** 2)
        if factor <= 0:
            return float('inf')
        return 1 / math.sqrt(factor)

    def tidal_force(self, m1: float, r1: float, m2: float, r2: float) -> float:
        """Вычисление приливной силы."""
        if r1 <= 0 or r2 <= 0 or r2 <= r1:
            raise ValueError("Некорректные параметры")
        return 2 * self.G * m2 * (r1 / r2 ** 3)

    def gravitational_wave_amplitude(self, m1: float, m2: float, distance: float, frequency: float) -> float:
        """Приблизительная амплитуда гравитационной волны."""
        if distance <= 0 or frequency <= 0:
            raise ValueError("Расстояние и частота должны быть больше 0")
        total_mass = m1 + m2
        reduced_mass = (m1 * m2) / total_mass
        chirp_mass = reduced_mass ** (3/5) / total_mass ** (1/5)
        omega = 2 * math.pi * frequency
        return (4 * self.G ** 2 * chirp_mass * omega ** 2) / (distance * self.c ** 4)

    def energy_density_planck(self) -> float:
        """Планковская плотность энергии."""
        return self.c ** 7 / (self.h_bar * self.G ** 2)

    def planck_length(self) -> float:
        """Планковская длина."""
        return math.sqrt(self.h_bar * self.G / self.c ** 3)

    def planck_mass(self) -> float:
        """Планковская масса."""
        return math.sqrt(self.h_bar * self.c / self.G)

    def planck_time(self) -> float:
        """Планковское время."""
        return math.sqrt(self.h_bar * self.G / self.c ** 5)

    def simulate_gravity_field(self, points: int = 100) -> list[dict]:
        """Симуляция гравитационного поля (2D)."""
        results = []
        central_mass = 1e30  # Масса Солнца в кг
        center_x, center_y = 50, 50

        for _ in range(points):
            x = random.uniform(0, 100)
            y = random.uniform(0, 100)
            dx = x - center_x
            dy = y - center_y
            r = math.sqrt(dx ** 2 + dy ** 2)
            if r < 1:
                r = 1
            force = self.G * central_mass / (r ** 2)
            fx = force * dx / r
            fy = force * dy / r
            results.append({
                "x": round(x, 2),
                "y": round(y, 2),
                "force": round(force, 10),
                "fx": round(fx, 10),
                "fy": round(fy, 10),
            })
        return results

    def calculate_xp(self) -> float:
        """Расчёт опыта за вычисления."""
        return 5.0  # Базовый опыт за цикл вычислений
