"""
RUN_IN_CQ_EDITOR.PY
Откройте этот файл в CQ-editor и нажмите F5.
"""

from generator import run_in_cq_editor, FlangeParams

# Вариант A: Модель с параметрами по умолчанию
run_in_cq_editor()

# Вариант B: Кастомная модель (раскомментируйте)
# params = FlangeParams(
#     flange_diameter=75.0,
#     hole_count=8,
#     chamfer_size=2.0
# )
# run_in_cq_editor(params)