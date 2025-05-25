from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import StringField, PasswordField, BooleanField, SubmitField, TextAreaField, SelectField
from wtforms.validators import DataRequired, Email, Length, EqualTo, ValidationError
from app.models.user import User

class LoginForm(FlaskForm):
    username = StringField('Usuario', validators=[DataRequired()])
    password = PasswordField('Contraseña', validators=[DataRequired()])
    remember_me = BooleanField('Recordarme')
    submit = SubmitField('Iniciar Sesión')

class RegistrationForm(FlaskForm):
    username = StringField('Usuario', validators=[
        DataRequired(message='El usuario es requerido'),
        Length(min=3, max=64, message='El usuario debe tener entre 3 y 64 caracteres')
    ])
    email = StringField('Email', validators=[
        DataRequired(message='El email es requerido'),
        Email(message='Por favor ingresa un email válido'),
        Length(max=120, message='El email no puede exceder los 120 caracteres')
    ])
    password = PasswordField('Contraseña', validators=[
        DataRequired(message='La contraseña es requerida'),
        Length(min=6, message='La contraseña debe tener al menos 6 caracteres')
    ])
    password2 = PasswordField('Confirmar Contraseña', validators=[
        DataRequired(message='Por favor confirma tu contraseña'),
        EqualTo('password', message='Las contraseñas deben coincidir')
    ])
    submit = SubmitField('Registrarse')
    
    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user is not None:
            raise ValidationError('Este nombre de usuario ya está en uso.')
    
    def validate_email(self, email):
        user = User.query.filter_by(email=email.data.lower()).first()
        if user is not None:
            raise ValidationError('Este email ya está registrado.')

class ProfileForm(FlaskForm):
    username = StringField('Usuario', validators=[
        DataRequired(),
        Length(min=3, max=64)
    ])
    email = StringField('Email', validators=[
        DataRequired(),
        Email(),
        Length(max=120)
    ])
    bio = TextAreaField('Biografía', validators=[
        Length(max=500)
    ])
    avatar = FileField('Avatar')
    submit = SubmitField('Guardar Cambios')

    def __init__(self, original_username, original_email, *args, **kwargs):
        super(ProfileForm, self).__init__(*args, **kwargs)
        self.original_username = original_username
        self.original_email = original_email

    def validate_username(self, username):
        if username.data != self.original_username:
            user = User.query.filter_by(username=username.data).first()
            if user is not None:
                raise ValidationError('Este nombre de usuario ya está en uso.')

    def validate_email(self, email):
        if email.data.lower() != self.original_email.lower():
            user = User.query.filter_by(email=email.data.lower()).first()
            if user is not None:
                raise ValidationError('Este email ya está registrado.')

class SecurityForm(FlaskForm):
    current_password = PasswordField('Contraseña Actual', validators=[DataRequired()])
    new_password = PasswordField('Nueva Contraseña', validators=[
        DataRequired(),
        Length(min=6)
    ])
    confirm_password = PasswordField('Confirmar Nueva Contraseña', validators=[
        DataRequired(),
        EqualTo('new_password', message='Las contraseñas deben coincidir')
    ])
    submit = SubmitField('Cambiar Contraseña')

class NotificationForm(FlaskForm):
    email_notifications = BooleanField('Notificaciones por Email')
    project_updates = BooleanField('Actualizaciones de Proyectos')
    submit = SubmitField('Guardar Preferencias')

class AppearanceForm(FlaskForm):
    theme = SelectField('Tema', choices=[
        ('light', 'Claro'),
        ('dark', 'Oscuro'),
        ('auto', 'Automático (según sistema)')
    ])
    font_size = SelectField('Tamaño de fuente', choices=[
        ('small', 'Pequeño'),
        ('medium', 'Mediano'),
        ('large', 'Grande')
    ])
    submit = SubmitField('Guardar Preferencias')

class Enable2FAForm(FlaskForm):
    code = StringField('Código de Verificación', validators=[
        DataRequired(),
        Length(min=6, max=6, message='El código debe tener 6 dígitos')
    ])
    submit = SubmitField('Verificar y Activar 2FA')

class Verify2FAForm(FlaskForm):
    code = StringField('Código de Verificación', validators=[
        DataRequired(),
        Length(min=6, max=6, message='El código debe tener 6 dígitos')
    ])
    remember_device = BooleanField('Recordar este dispositivo por 30 días')
    submit = SubmitField('Verificar')

class BackupCodeForm(FlaskForm):
    code = StringField('Código de Respaldo', validators=[
        DataRequired(),
        Length(min=8, max=8, message='El código de respaldo debe tener 8 caracteres')
    ])
    submit = SubmitField('Verificar') 