from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SubmitField, SelectField
from wtforms.validators import DataRequired, Length

class ProjectForm(FlaskForm):
    title = StringField('Título', validators=[
        DataRequired(message='El título es requerido'),
        Length(min=3, max=100, message='El título debe tener entre 3 y 100 caracteres')
    ])
    description = TextAreaField('Descripción')
    submit = SubmitField('Crear Proyecto')

class ReportForm(FlaskForm):
    title = StringField('Título', validators=[
        DataRequired(message='El título es requerido'),
        Length(min=3, max=100, message='El título debe tener entre 3 y 100 caracteres')
    ])
    content = TextAreaField('Contenido', validators=[
        DataRequired(message='El contenido es requerido')
    ])
    type = SelectField('Tipo de Reporte', choices=[
        ('general', 'General'),
        ('bug', 'Bug'),
        ('feature', 'Nueva Funcionalidad'),
        ('improvement', 'Mejora')
    ])
    project_id = SelectField('Proyecto (Opcional)', coerce=int, choices=[], validate_choice=False)
    submit = SubmitField('Crear Reporte') 