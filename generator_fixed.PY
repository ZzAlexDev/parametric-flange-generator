"""
GENERATOR_FIXED.PY - Минимальная рабочая версия
"""

from dataclasses import dataclass, asdict
import cadquery as cq
import math
import json
from pathlib import Path

# === КЛАСС ПАРАМЕТРОВ ===
@dataclass
class FlangeParams:
    flange_diameter: float = 50.0
    flange_thickness: float = 8.0
    hole_count: int = 6
    hole_diameter: float = 5.5
    center_hole_diameter: float = 12.0
    bolt_circle_percentage: float = 0.65
    chamfer_size: float = 1.5

# === ФУНКЦИЯ ГЕНЕРАЦИИ ===
def generate_flange(params: FlangeParams) -> cq.Workplane:
    """Создаёт фланец по параметрам."""
    d = params.flange_diameter
    t = params.flange_thickness
    hc = params.hole_count
    hd = params.hole_diameter
    chd = params.center_hole_diameter
    bcp = params.bolt_circle_percentage
    cs = params.chamfer_size
    
    # 1. Основной цилиндр
    model = cq.Workplane("XY").circle(d/2).extrude(t)
    
    # 2. Центральное отверстие
    model = model.faces(">Z").workplane(centerOption="CenterOfMass").hole(chd)
    
    # 3. Отверстия по окружности
    bolt_radius = (d * bcp) / 2
    points = [
        (bolt_radius * math.cos(2 * math.pi * i / hc),
         bolt_radius * math.sin(2 * math.pi * i / hc))
        for i in range(hc)
    ]
    model = model.faces(">Z").workplane(centerOption="CenterOfMass").pushPoints(points).hole(hd)
    
    # 4. Фаска
    if cs > 0:
        model = model.edges(">Z and (not <Z)").chamfer(cs)
    
    return model

# === ТЕСТ ===
if __name__ == "__main__":
    print("Тест generator_fixed.py...")
    params = FlangeParams()
    model = generate_flange(params)
    print(f"✅ Модель создана! Диаметр: {params.flange_diameter}мм, отверстий: {params.hole_count}")