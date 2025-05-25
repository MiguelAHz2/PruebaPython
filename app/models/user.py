from datetime import datetime, timedelta
from app import db, login_manager
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from hashlib import md5
import secrets
import pyotp

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False, index=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(128))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_seen = db.Column(db.DateTime, default=datetime.utcnow)
    is_active = db.Column(db.Boolean, default=True)
    avatar = db.Column(db.String(200))
    
    # Nuevos campos para preferencias
    email_notifications = db.Column(db.Boolean, default=True)
    push_notifications = db.Column(db.Boolean, default=True)
    profile_visibility = db.Column(db.String(20), default='public')  # 'public' o 'private'
    bio = db.Column(db.Text)
    avatar_hash = db.Column(db.String(32))
    
    # Preferencias de usuario
    theme = db.Column(db.String(20), default='light')
    font_size = db.Column(db.String(10), default='medium')
    project_notifications = db.Column(db.Boolean, default=True)
    report_notifications = db.Column(db.Boolean, default=True)
    
    # Campos para 2FA
    two_factor_enabled = db.Column(db.Boolean, default=False)
    two_factor_secret = db.Column(db.String(32))
    backup_codes = db.Column(db.JSON)
    
    # Campos de estado de cuenta
    account_status = db.Column(db.String(20), default='active')  # active, suspended, locked
    failed_login_attempts = db.Column(db.Integer, default=0)
    last_failed_login = db.Column(db.DateTime)
    last_login = db.Column(db.DateTime)
    
    # Campos de auditoría
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_password_change = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relaciones
    projects = db.relationship('Project', backref='author', lazy='dynamic')
    reports = db.relationship('Report', backref='author', lazy='dynamic')
    activities = db.relationship('Activity', backref='user', lazy='dynamic')

    def __init__(self, **kwargs):
        super(User, self).__init__(**kwargs)
        if self.email is not None and self.avatar_hash is None:
            self.avatar_hash = self.gravatar_hash()
        if self.backup_codes is None:
            self.backup_codes = self.generate_backup_codes()

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def update_last_seen(self):
        self.last_seen = datetime.utcnow()
        db.session.commit()

    def gravatar_hash(self):
        return md5(self.email.lower().encode('utf-8')).hexdigest()

    def get_avatar(self, size=32):
        if self.avatar:
            return f'/static/uploads/avatars/{self.avatar}'
        # Gravatar fallback
        if not self.avatar_hash:
            self.avatar_hash = self.gravatar_hash()
            db.session.add(self)
            db.session.commit()
        return f'https://www.gravatar.com/avatar/{self.avatar_hash}?d=identicon&s={size}'

    def get_completed_tasks(self):
        from app.models.project import Project
        completed = 0
        for project in self.projects:
            completed += project.get_completed_tasks()
        return completed

    def get_recent_activities(self, limit=5):
        return self.activities.order_by(Activity.created_at.desc()).limit(limit).all()

    def generate_backup_codes(self):
        """Genera códigos de respaldo para 2FA"""
        return [secrets.token_hex(4).upper() for _ in range(8)]

    def verify_backup_code(self, code):
        """Verifica y consume un código de respaldo"""
        if not self.backup_codes:
            return False
        if code.upper() in self.backup_codes:
            self.backup_codes.remove(code.upper())
            db.session.commit()
            return True
        return False

    def get_2fa_uri(self):
        """Genera el URI para el código QR de 2FA"""
        if not self.two_factor_secret:
            self.two_factor_secret = pyotp.random_base32()
        return pyotp.totp.TOTP(self.two_factor_secret).provisioning_uri(
            name=self.email,
            issuer_name="ProjectManager"
        )

    def verify_2fa(self, code):
        """Verifica un código 2FA"""
        if not self.two_factor_secret:
            return False
        totp = pyotp.TOTP(self.two_factor_secret)
        return totp.verify(code)

    def record_login_attempt(self, success):
        """Registra un intento de inicio de sesión"""
        if success:
            self.failed_login_attempts = 0
            self.last_login = datetime.utcnow()
        else:
            self.failed_login_attempts += 1
            self.last_failed_login = datetime.utcnow()
            if self.failed_login_attempts >= 5:  # Bloquear después de 5 intentos fallidos
                self.account_status = 'locked'
        db.session.commit()

    def is_account_locked(self):
        """Verifica si la cuenta está bloqueada"""
        if self.account_status == 'locked':
            # Desbloquear después de 30 minutos
            if self.last_failed_login and \
               datetime.utcnow() - self.last_failed_login > timedelta(minutes=30):
                self.account_status = 'active'
                self.failed_login_attempts = 0
                db.session.commit()
                return False
            return True
        return False

    def __repr__(self):
        return f'<User {self.username}>'

@login_manager.user_loader
def load_user(id):
    return User.query.get(int(id))

class Activity(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    type = db.Column(db.String(20))  # project, report, task
    action = db.Column(db.String(20))  # created, updated, deleted, completed
    target_id = db.Column(db.Integer)
    title = db.Column(db.String(128))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    @property
    def type_color(self):
        colors = {
            'project': 'primary',
            'report': 'success',
            'task': 'info'
        }
        return colors.get(self.type, 'secondary')

    @property
    def icon(self):
        icons = {
            'project': 'project-diagram',
            'report': 'file-alt',
            'task': 'tasks'
        }
        return icons.get(self.type, 'circle') 