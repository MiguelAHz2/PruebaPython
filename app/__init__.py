from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_migrate import Migrate
from flask_mail import Mail
from flask_moment import Moment
from flask_caching import Cache
from flask_wtf.csrf import CSRFProtect
from config import Config
import os

# Inicialización de extensiones
db = SQLAlchemy()
login_manager = LoginManager()
login_manager.login_view = 'auth.login'
login_manager.login_message = 'Por favor inicia sesión para acceder a esta página.'
login_manager.login_message_category = 'info'

migrate = Migrate()
mail = Mail()
moment = Moment()
cache = Cache()
csrf = CSRFProtect()

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Asegurarse de que la clave secreta esté establecida
    if not app.config['SECRET_KEY']:
        app.config['SECRET_KEY'] = 'una-clave-secreta-muy-dificil-de-adivinar'

    # Inicializar extensiones
    db.init_app(app)
    login_manager.init_app(app)
    migrate.init_app(app, db)
    mail.init_app(app)
    moment.init_app(app)
    cache.init_app(app)
    csrf.init_app(app)

    # Configurar CSRF
    app.config['WTF_CSRF_ENABLED'] = True
    app.config['WTF_CSRF_SECRET_KEY'] = app.config['SECRET_KEY']
    app.config['WTF_CSRF_TIME_LIMIT'] = 3600

    # Registrar filtros personalizados
    from app.utils.filters import nl2br
    app.jinja_env.filters['nl2br'] = nl2br

    # Importar blueprints
    from app.routes.main import main
    from app.routes.auth import auth
    from app.routes.projects import projects
    from app.routes.reports import reports
    from app.routes.status import status

    # Registrar blueprints
    app.register_blueprint(main)
    app.register_blueprint(auth)
    app.register_blueprint(projects)
    app.register_blueprint(reports)
    app.register_blueprint(status)

    # Configurar manejo de errores personalizado
    from app.errors import handlers

    # Asegurarse de que la carpeta de subidas exista
    if not os.path.exists(app.config['UPLOAD_FOLDER']):
        os.makedirs(app.config['UPLOAD_FOLDER'])

    if not app.debug and not app.testing:
        if not os.path.exists('logs'):
            os.mkdir('logs')

    return app

from app.models import User  # noqa 