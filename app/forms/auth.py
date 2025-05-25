from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import DataRequired, Email, Length, EqualTo, ValidationError
from app.models import User

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