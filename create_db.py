from app import create_app, db
from app.models.user import User
from app.models.project import Project
from app.models.report import Report

app = create_app()

with app.app_context():
    # Crear todas las tablas
    db.drop_all()  # Eliminar tablas existentes
    db.create_all()  # Crear nuevas tablas
    
    print("Base de datos creada exitosamente") 