from fe_app import app, db

with app.app_context():
    print("Intentando crear las tablas de la base de datos...")
    try:
        db.create_all()
        print("Tablas de la base de datos creadas exitosamente.")
    except Exception as e:
        print(f"Ocurrió un error al crear las tablas: {e}")