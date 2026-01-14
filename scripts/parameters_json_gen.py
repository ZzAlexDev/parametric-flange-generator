# Создание examples/parameters.json
import json
from pathlib import Path
from generator import FlangeParams

# Создаём несколько примеров конфигураций
examples = {
    "small_4hole": FlangeParams(
        flange_diameter=40.0,
        hole_count=4,
        chamfer_size=1.0
    ).__dict__,
    
    "medium_8hole": FlangeParams(
        flange_diameter=75.0,
        hole_count=8,
        bolt_circle_percentage=0.7,
        chamfer_size=2.0
    ).__dict__,
    
    "large_12hole": FlangeParams(
        flange_diameter=100.0,
        flange_thickness=12.0,
        hole_count=12,
        center_hole_diameter=25.0
    ).__dict__
}

# Сохраняем в файл
output_dir = Path("examples")
output_dir.mkdir(exist_ok=True)
file_path = output_dir / "parameters.json"

with open(file_path, 'w', encoding='utf-8') as f:
    json.dump(examples, f, indent=2, ensure_ascii=False)

print(f"✅ Файл создан: {file_path}")
print("\nСодержимое файла:")
print(json.dumps(examples, indent=2, ensure_ascii=False))