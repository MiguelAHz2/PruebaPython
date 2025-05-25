import os
from dotenv import load_dotenv
from app import create_app, db
from flask_migrate import upgrade
from app.models.user import User
from app.models.project import Project
from app.models.task import Task
from app.models.report import Report
from app.models.comment import Comment
from app.models.tag import Tag

# Cargar variables de entorno
basedir = os.path.abspath(os.path.dirname(__file__))
load_dotenv(os.path.join(basedir, '.env'))

# Crear la aplicación
app = create_app()

# Inicializar la base de datos
with app.app_context():
    try:
        # Ejecutar las migraciones
        upgrade()
        print("Migraciones aplicadas correctamente")
        
        # Verificar si las tablas existen
        inspector = db.inspect(db.engine)
        if not inspector.has_table("user"):
            # Si no existen las tablas, crearlas
            db.create_all()
            print("Tablas creadas correctamente")
        
    except Exception as e:
        print(f"Error durante la inicialización de la base de datos: {e}")
        # No levantar la excepción, permitir que la aplicación continúe

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port) 