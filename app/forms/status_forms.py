from flask_wtf import FlaskForm
from wtforms import SelectField, TextAreaField
from wtforms.validators import DataRequired

class ChangeProjectStatusForm(FlaskForm):
    status = SelectField('Estado', validators=[DataRequired()])
    comment = TextAreaField('Comentario (opcional)')
    
    def __init__(self, *args, **kwargs):
        super(ChangeProjectStatusForm, self).__init__(*args, **kwargs)
        from app.models.project import Project
        self.status.choices = Project.get_status_choices()

class ChangeReportStatusForm(FlaskForm):
    status = SelectField('Estado', validators=[DataRequired()])
    comment = TextAreaField('Comentario (opcional)')
    
    def __init__(self, *args, **kwargs):
        super(ChangeReportStatusForm, self).__init__(*args, **kwargs)
        from app.models.report import Report
        self.status.choices = Report.get_status_choices() 