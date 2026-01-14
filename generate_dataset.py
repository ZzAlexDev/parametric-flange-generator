"""
GENERATE_DATASET.PY
Запуск: python generate_dataset.py --count 20
"""

import argparse
from pathlib import Path
from generator import create_random_variations, generate_dataset
from datetime import datetime

def main():
    parser = argparse.ArgumentParser(description='Генератор датасетов фланцев')
    parser.add_argument('--count', type=int, default=10, help='Количество моделей')
    parser.add_argument('--output', type=str, default=None, help='Имя папки')
    parser.add_argument('--formats', nargs='+', default=['step'], help='Форматы (step, stl)')
    
    args = parser.parse_args()
    
    # Имя папки с датой
    if args.output is None:
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        output_dir = Path(f"ai_dataset_{timestamp}")
    else:
        output_dir = Path(args.output)
    
    print(f"Создаю датасет из {args.count} моделей...")
    
    # Генерация случайных параметров
    variations = create_random_variations(args.count)
    
    # Создание датасета
    successful, metadata_path = generate_dataset(
        variations, 
        output_dir,
        args.formats
    )
    
    print(f"\n✅ Готово! Успешно создано: {successful}/{args.count} моделей")
    print(f"📁 Папка: {output_dir}")
    print(f"📄 Метаданные: {metadata_path}")

if __name__ == "__main__":
    main()