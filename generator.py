"""
GENERATOR.PY - Универсальный генератор параметрических фланцев
Работает в трёх режимах:
1. В CQ-editor: отображает модель в 3D-окне (через show_object)
2. Автономно: экспортирует одиночную модель в файл
3. Генерация датасетов: создаёт множество вариаций для ИИ
"""

import cadquery as cq
import math
import json
import random
import sys
import os
from pathlib import Path
from typing import Dict, Any, List, Tuple, Optional
from dataclasses import dataclass, asdict
import logging

# === НАСТРОЙКА ЛОГГИРОВАНИЯ ===
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# === КЛАСС ДЛЯ ХРАНЕНИЯ ПАРАМЕТРОВ ===
@dataclass
class FlangeParams:
    """Структура для хранения всех параметров фланца."""
    flange_diameter: float = 50.0
    flange_thickness: float = 8.0
    hole_count: int = 6
    hole_diameter: float = 5.5
    center_hole_diameter: float = 12.0
    bolt_circle_percentage: float = 0.65
    chamfer_size: float = 1.5
    fillet_size: float = 0.0  # Новый параметр - скругление
    
    def validate(self) -> List[str]:
        """Проверяет корректность параметров, возвращает список ошибок."""
        errors = []
        if self.center_hole_diameter >= self.flange_diameter:
            errors.append(f"Центральное отверстие ({self.center_hole_diameter}) ≥ диаметра фланца ({self.flange_diameter})")
        if self.hole_diameter >= self.flange_diameter * self.bolt_circle_percentage:
            errors.append(f"Диаметр отверстий ({self.hole_diameter}) слишком велик для расположения")
        if self.hole_count < 1:
            errors.append(f"Количество отверстий должно быть ≥ 1 (задано: {self.hole_count})")
        if self.bolt_circle_percentage < 0.1 or self.bolt_circle_percentage > 0.9:
            errors.append(f"Расположение отверстий ({self.bolt_circle_percentage}) должно быть между 0.1 и 0.9")
        return errors

# === ОСНОВНАЯ ФУНКЦИЯ ГЕНЕРАЦИИ ===
def generate_flange(params: FlangeParams) -> cq.Workplane:
    """
    Генерирует 3D-модель фланца по заданным параметрам.
    
    Args:
        params: Объект FlangeParams с параметрами модели
        
    Returns:
        CadQuery Workplane object
        
    Raises:
        ValueError: Если параметры невалидны
    """
    # Валидация параметров
    if errors := params.validate():
        raise ValueError(f"Невалидные параметры:\n" + "\n".join(f"  • {e}" for e in errors))
    
    # Сокращённые имена для удобства
    d, t, hc, hd, chd, bcp, cs, fs = (
        params.flange_diameter, params.flange_thickness, params.hole_count,
        params.hole_diameter, params.center_hole_diameter, 
        params.bolt_circle_percentage, params.chamfer_size, params.fillet_size
    )
    
    try:
        # 1. ОСНОВНОЙ ЦИЛИНДР
        model = cq.Workplane("XY").circle(d / 2).extrude(t)
        logger.debug(f"Создан основной цилиндр: Ø{d}мм, толщина {t}мм")
        
        # 2. ЦЕНТРАЛЬНОЕ ОТВЕРСТИЕ
        model = model.faces(">Z").workplane(centerOption="CenterOfMass").hole(chd)
        logger.debug(f"Добавлено центральное отверстие: Ø{chd}мм")
        
        # 3. ОТВЕРСТИЯ ПО ОКРУЖНОСТИ (параметрическое размещение)
        bolt_radius = (d * bcp) / 2
        points = [
            (bolt_radius * math.cos(2 * math.pi * i / hc),
             bolt_radius * math.sin(2 * math.pi * i / hc))
            for i in range(hc)
        ]
        
        model = (model.faces(">Z").workplane(centerOption="CenterOfMass")
                .pushPoints(points).hole(hd))
        logger.debug(f"Добавлено {hc} отверстий Ø{hd}мм на радиусе {bolt_radius:.1f}мм")
        
        # 4. ФАСКА (если задана)
        if cs > 0:
            model = model.edges(">Z and (not <Z)").chamfer(cs)
            logger.debug(f"Добавлена фаска {cs}мм")
        
        # 5. СКРУГЛЕНИЕ (если задано)
        if fs > 0:
            model = model.edges("|Z").fillet(fs)
            logger.debug(f"Добавлено скругление {fs}мм")
        
        logger.info(f"✅ Модель успешно создана: Ø{d}мм, {hc} отв., фаска {cs}мм")
        return model
        
    except Exception as e:
        logger.error(f"❌ Ошибка при генерации модели: {e}")
        raise

# === ФУНКЦИИ ЭКСПОРТА ===
def export_model(model: cq.Workplane, base_name: str, 
                export_dir: Path = Path("output")) -> Dict[str, Path]:
    """
    Экспортирует модель в STEP и STL форматы.
    
    Args:
        model: Объект CadQuery
        base_name: Базовое имя файла (без расширения)
        export_dir: Папка для экспорта
        
    Returns:
        Словарь с путями к созданным файлам {'step': Path, 'stl': Path}
    """
    export_dir.mkdir(parents=True, exist_ok=True)
    exported = {}
    
    # Экспорт в STEP (для CAD)
    step_path = export_dir / f"{base_name}.step"
    cq.exporters.export(model, str(step_path))
    exported['step'] = step_path
    logger.debug(f"Экспортирован STEP: {step_path}")
    
    # Экспорт в STL (для 3D-печати/визуализации)
    stl_path = export_dir / f"{base_name}.stl"
    cq.exporters.export(model, str(stl_path), tolerance=0.01, angularTolerance=0.1)
    exported['stl'] = stl_path
    logger.debug(f"Экспортирован STL: {stl_path}")
    
    return exported

# === ГЕНЕРАЦИЯ ДАТАСЕТА ===
def generate_dataset(variations: List[FlangeParams], 
                    dataset_dir: Path = Path("ai_dataset"),
                    export_formats: List[str] = None) -> Tuple[int, Path]:
    """
    Генерирует набор вариативных моделей для обучения ИИ.
    
    Args:
        variations: Список объектов FlangeParams
        dataset_dir: Папка для сохранения датасета
        export_formats: Список форматов для экспорта (по умолчанию ['step'])
        
    Returns:
        Кортеж (количество успешных моделей, путь к metadata.json)
    """
    if export_formats is None:
        export_formats = ['step']
    
    dataset_dir.mkdir(parents=True, exist_ok=True)
    metadata = []
    successful = 0
    
    logger.info(f"Начинаю генерацию датасета из {len(variations)} вариаций...")
    
    for idx, params in enumerate(variations):
        try:
            # Генерация модели
            model = generate_flange(params)
            
            # Экспорт в указанные форматы
            base_name = f"flange_{idx:04d}"
            exported_files = {}
            
            for fmt in export_formats:
                if fmt.lower() == 'step':
                    path = dataset_dir / f"{base_name}.step"
                    cq.exporters.export(model, str(path))
                    exported_files['step'] = str(path)
                elif fmt.lower() == 'stl':
                    path = dataset_dir / f"{base_name}.stl"
                    cq.exporters.export(model, str(path), tolerance=0.01, angularTolerance=0.1)
                    exported_files['stl'] = str(path)
            
            # Сохранение метаданных
            meta_entry = {
                "id": idx,
                "filename": f"{base_name}.step",
                "parameters": asdict(params),
                "exported_files": exported_files,
                "timestamp": datetime.now().isoformat()
            }
            metadata.append(meta_entry)
            successful += 1
            
            if (idx + 1) % 10 == 0:
                logger.info(f"  Обработано: {idx + 1}/{len(variations)}")
                
        except ValueError as e:
            logger.warning(f"  Вариация {idx} пропущена: {e}")
        except Exception as e:
            logger.error(f"  Ошибка при обработке вариации {idx}: {e}")
    
    # Сохранение метаданных
    metadata_path = dataset_dir / "metadata.json"
    with open(metadata_path, 'w', encoding='utf-8') as f:
        json.dump(metadata, f, indent=2, ensure_ascii=False, default=str)
    
    logger.info(f"✅ Генерация завершена! Успешно: {successful}/{len(variations)}")
    logger.info(f"   Папка: {dataset_dir}")
    logger.info(f"   Метаданные: {metadata_path}")
    
    return successful, metadata_path

# === УТИЛИТЫ ДЛЯ СОЗДАНИЯ ВАРИАЦИЙ ===
def create_random_variations(count: int = 10) -> List[FlangeParams]:
    """Создаёт список случайных, но реалистичных параметров."""
    variations = []
    
    for _ in range(count):
        params = FlangeParams(
            flange_diameter=random.uniform(30.0, 100.0),
            flange_thickness=random.uniform(5.0, 20.0),
            hole_count=random.choice([4, 6, 8, 12]),
            hole_diameter=random.uniform(3.0, 12.0),
            center_hole_diameter=random.uniform(8.0, 25.0),
            bolt_circle_percentage=random.uniform(0.5, 0.75),
            chamfer_size=random.choice([0, 0.5, 1.0, 1.5]),
            fillet_size=random.choice([0, 0.5, 1.0])
        )
        variations.append(params)
    
    return variations

def create_systematic_variations() -> List[FlangeParams]:
    """Создаёт систематические вариации для тестирования."""
    variations = []
    
    # Пример: меняем количество отверстий при фиксированных остальных параметрах
    base_params = FlangeParams()
    
    for hole_count in [3, 4, 6, 8, 12]:
        params = FlangeParams(**asdict(base_params))
        params.hole_count = hole_count
        # Автоматически корректируем диаметр отверстий
        params.hole_diameter = min(6.0, params.flange_diameter * 0.1)
        variations.append(params)
    
    return variations

# === РЕЖИМ CQ-EDITOR ===
def run_in_cq_editor(params: Optional[FlangeParams] = None):
    """
    Режим для запуска в CQ-editor.
    Используйте эту функцию в run_in_cq_editor.py
    """
    if params is None:
        params = FlangeParams()
    
    try:
        # Генерация модели
        model = generate_flange(params)
        
        # В CQ-editor функция show_object доступна глобально
        # (Вариант 2, который у вас сработал)
        show_object(model, name=f"Flange_{params.hole_count}holes", 
                   options={"color": (64, 164, 223, 0.8)})
        
        # Дополнительно показываем отдельные элементы для отладки
        if hasattr(globals(), 'debug'):
            # Показываем расположение отверстий как точки
            bolt_radius = (params.flange_diameter * params.bolt_circle_percentage) / 2
            for i in range(params.hole_count):
                angle = 2 * math.pi * i / params.hole_count
                x = bolt_radius * math.cos(angle)
                y = bolt_radius * math.sin(angle)
                point = cq.Workplane("XY").workplane(offset=params.flange_thickness/2).center(x, y).circle(1).extrude(1)
                debug(point, name=f"Hole_pos_{i}", options={"color": (255, 50, 50, 0.5)})
        
        logger.info(f"✅ Модель отображена в CQ-editor")
        logger.info(f"   Параметры: {params}")
        
        return model
        
    except Exception as e:
        logger.error(f"❌ Ошибка в режиме CQ-editor: {e}")
        raise

# === КОМАНДНАЯ СТРОКА ===
def main():
    """Главная функция для запуска из командной строки."""
    import argparse
    from datetime import datetime
    
    parser = argparse.ArgumentParser(description='Генератор параметрических фланцев')
    parser.add_argument('--mode', choices=['single', 'dataset', 'cq'], 
                       default='single', help='Режим работы')
    parser.add_argument('--count', type=int, default=10, 
                       help='Количество моделей в датасете')
    parser.add_argument('--output', type=Path, default=Path("output"),
                       help='Папка для вывода')
    parser.add_argument('--formats', nargs='+', default=['step', 'stl'],
                       help='Форматы экспорта')
    parser.add_argument('--debug', action='store_true',
                       help='Включить отладочный вывод')
    
    args = parser.parse_args()
    
    if args.debug:
        logger.setLevel(logging.DEBUG)
    
    logger.info(f"Запуск в режиме: {args.mode}")
    
    if args.mode == 'single':
        # Режим одиночной модели
        params = FlangeParams()
        model = generate_flange(params)
        files = export_model(model, "single_flange", args.output)
        logger.info(f"Одиночная модель создана: {files}")
        
    elif args.mode == 'dataset':
        # Режим генерации датасета
        variations = create_random_variations(args.count)
        successful, meta_path = generate_dataset(
            variations, 
            args.output / f"dataset_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            args.formats
        )
        logger.info(f"Создан датасет: {successful} моделей, метаданные: {meta_path}")
        
    elif args.mode == 'cq':
        # Режим для CQ-editor (только информационное сообщение)
        logger.info("Для режима CQ-editor создайте отдельный файл run_in_cq_editor.py:")
        logger.info("""
from generator import run_in_cq_editor, FlangeParams

# Использование параметров по умолчанию
run_in_cq_editor()

# Или с кастомными параметрами
# params = FlangeParams(flange_diameter=75.0, hole_count=8)
# run_in_cq_editor(params)
""")
    
    logger.info("Готово!")

if __name__ == "__main__":
    # Импортируем datetime здесь, чтобы не мешать CQ-editor
    from datetime import datetime
    main()