from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SelectField
from wtforms.validators import DataRequired, Length, Optional

class ReportForm(FlaskForm):
    title = StringField('Título', validators=[
        DataRequired(message='El título es requerido'),
        Length(min=3, max=100, message='El título debe tener entre 3 y 100 caracteres')
    ])
    content = TextAreaField('Contenido', validators=[
        DataRequired(message='El contenido es requerido'),
        Length(min=10, message='El contenido debe tener al menos 10 caracteres')
    ])
    type = SelectField('Tipo', validators=[DataRequired(message='El tipo es requerido')])
    project_id = SelectField('Proyecto', coerce=int, validators=[Optional()])
    
    def __init__(self, *args, **kwargs):
        super(ReportForm, self).__init__(*args, **kwargs)
        from app.models.report import Report
        from app.models.project import Project
        from flask_login import current_user
        
        # Configurar opciones de tipo
        self.type.choices = Report.get_type_choices()
        
        # Configurar opciones de proyecto
        projects = Project.query.filter_by(user_id=current_user.id).all()
        self.project_id.choices = [(0, 'Sin proyecto')] + [
            (p.id, p.title) for p in projects
        ] 