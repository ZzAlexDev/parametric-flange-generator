print("=== ФИНАЛЬНАЯ ПРОВЕРКА ПРОЕКТА ===")

# 1. Проверка generator.py
from generator import FlangeParams, generate_flange
params = FlangeParams(hole_count=4)
model = generate_flange(params)
show_object(model, name="Final_Test")
print("✅ generator.py работает")

# 2. Проверка examples/parameters.json
from pathlib import Path
import json
if Path("examples/parameters.json").exists():
    with open("examples/parameters.json", 'r') as f:
        examples = json.load(f)
    print(f"✅ parameters.json найден ({len(examples)} примеров)")
else:
    print("⚠️  parameters.json не найден (создайте его кодом выше)")

# 3. Проверка создания датасета
try:
    from generator import create_random_variations
    test_vars = create_random_variations(2)
    print(f"✅ Генерация вариаций работает ({len(test_vars)} создано)")
except Exception as e:
    print(f"❌ Ошибка: {e}")

print("\n=== ПРОЕКТ ГОТОВ К РАБОТЕ ===")