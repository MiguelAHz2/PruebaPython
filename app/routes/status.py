from flask import Blueprint, flash, redirect, render_template, url_for, request
from flask_login import login_required, current_user
from app import db
from app.models.project import Project
from app.models.report import Report
from app.forms.status_forms import ChangeProjectStatusForm, ChangeReportStatusForm

status = Blueprint('status', __name__)

@status.route('/project/<int:project_id>/status', methods=['GET', 'POST'])
@login_required
def change_project_status(project_id):
    project = Project.query.get_or_404(project_id)
    
    # Verificar permisos
    if project.user_id != current_user.id:
        flash('No tienes permiso para modificar este proyecto.', 'danger')
        return redirect(url_for('main.index'))
    
    form = ChangeProjectStatusForm()
    
    if form.validate_on_submit():
        new_status = form.status.data
        if project.change_status(new_status):
            db.session.commit()
            flash(f'Estado del proyecto actualizado a {project.status_label}', 'success')
            # Aquí podrías registrar el comentario en un sistema de logs si lo deseas
        else:
            flash('No se puede cambiar al estado seleccionado.', 'warning')
        return redirect(url_for('projects.view_project', project_id=project.id))
    
    form.status.data = project.status
    return render_template('status/change_status.html', 
                         form=form, 
                         item=project, 
                         type='proyecto')

@status.route('/report/<int:report_id>/status', methods=['GET', 'POST'])
@login_required
def change_report_status(report_id):
    report = Report.query.get_or_404(report_id)
    
    # Verificar permisos
    if report.user_id != current_user.id:
        flash('No tienes permiso para modificar este reporte.', 'danger')
        return redirect(url_for('main.index'))
    
    form = ChangeReportStatusForm()
    
    if form.validate_on_submit():
        new_status = form.status.data
        if report.change_status(new_status):
            db.session.commit()
            flash(f'Estado del reporte actualizado a {report.status_label}', 'success')
            # Aquí podrías registrar el comentario en un sistema de logs si lo deseas
        else:
            flash('No se puede cambiar al estado seleccionado.', 'warning')
        return redirect(url_for('reports.view_report', report_id=report.id))
    
    form.status.data = report.status
    return render_template('status/change_status.html', 
                         form=form, 
                         item=report, 
                         type='reporte') 