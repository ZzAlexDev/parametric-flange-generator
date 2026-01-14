# Тестовая ячейка - выполните этот код в CQ-editor
print("=== ТЕСТ GENERATOR.PY ===")

# Пробуем импортировать основные компоненты
try:
    from generator import FlangeParams, generate_flange
    print("✅ Импорт FlangeParams и generate_flange успешен")
    
    # Пробуем создать параметры
    params = FlangeParams()
    print(f"✅ Создан объект параметров: {params}")
    
    # Пробуем сгенерировать модель
    model = generate_flange(params)
    print("✅ Модель успешно сгенерирована")
    
    # Пробуем вызвать show_object
    try:
        show_object(model, name="Test_Flange")
        print("✅ Модель отображена в CQ-editor")
    except NameError:
        print("⚠️  show_object не доступен (но это нормально для теста)")
        
except Exception as e:
    print(f"❌ Ошибка при тесте: {e}")
    import traceback
    traceback.print_exc()