from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_required, current_user
from app import db
from app.models.report import Report
from app.models.project import Project
from app.forms.report_form import ReportForm

reports = Blueprint('reports', __name__)

@reports.route('/reports')
@login_required
def list_reports():
    """Lista todos los reportes del usuario"""
    # Obtener parámetros de filtrado
    status = request.args.get('status', 'all')
    type = request.args.get('type', 'all')
    project_id = request.args.get('project_id', 'all')
    
    # Consulta base
    query = Report.query.filter_by(user_id=current_user.id)
    
    # Aplicar filtros
    if status != 'all' and status in Report.STATES:
        query = query.filter_by(status=status)
    if type != 'all' and type in Report.TYPES:
        query = query.filter_by(type=type)
    if project_id != 'all' and project_id.isdigit():
        query = query.filter_by(project_id=int(project_id))
    
    # Ordenar por última actualización
    reports = query.order_by(Report.updated_at.desc()).all()
    
    # Obtener proyectos para el filtro
    projects = Project.query.filter_by(user_id=current_user.id).all()
    
    return render_template('reports/list_reports.html',
                         reports=reports,
                         current_status=status,
                         current_type=type,
                         current_project=project_id,
                         states=Report.STATES,
                         types=Report.TYPES,
                         projects=projects)

@reports.route('/report/new', methods=['GET', 'POST'])
@reports.route('/report/new/<int:project_id>', methods=['GET', 'POST'])
@login_required
def create_report(project_id=None):
    """Crear un nuevo reporte"""
    form = ReportForm()
    
    # Si se especifica un proyecto, verificar permisos
    if project_id:
        project = Project.query.get_or_404(project_id)
        if project.user_id != current_user.id:
            flash('No tienes permiso para crear reportes en este proyecto.', 'danger')
            return redirect(url_for('main.index'))
        form.project_id.data = project_id
    
    if form.validate_on_submit():
        report = Report(
            title=form.title.data,
            content=form.content.data,
            type=form.type.data,
            project_id=form.project_id.data,
            user_id=current_user.id
        )
        db.session.add(report)
        db.session.commit()
        flash('Reporte creado exitosamente.', 'success')
        return redirect(url_for('reports.view_report', report_id=report.id))
    
    return render_template('reports/report_form.html',
                         title='Nuevo Reporte',
                         form=form)

@reports.route('/report/<int:report_id>')
@login_required
def view_report(report_id):
    """Ver detalles de un reporte"""
    report = Report.query.get_or_404(report_id)
    if report.user_id != current_user.id:
        flash('No tienes permiso para ver este reporte.', 'danger')
        return redirect(url_for('main.index'))
    
    return render_template('reports/report_detail.html',
                         report=report)

@reports.route('/report/<int:report_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_report(report_id):
    """Editar un reporte existente"""
    report = Report.query.get_or_404(report_id)
    if report.user_id != current_user.id:
        flash('No tienes permiso para editar este reporte.', 'danger')
        return redirect(url_for('main.index'))
    
    form = ReportForm(obj=report)
    if form.validate_on_submit():
        report.title = form.title.data
        report.content = form.content.data
        report.type = form.type.data
        report.project_id = form.project_id.data
        db.session.commit()
        flash('Reporte actualizado exitosamente.', 'success')
        return redirect(url_for('reports.view_report', report_id=report.id))
    
    return render_template('reports/report_form.html',
                         title='Editar Reporte',
                         form=form)

@reports.route('/report/<int:report_id>/status', methods=['POST'])
@login_required
def change_report_status(report_id):
    """Cambiar el estado de un reporte"""
    report = Report.query.get_or_404(report_id)
    if report.user_id != current_user.id:
        return jsonify({'success': False, 'message': 'No tienes permiso para modificar este reporte'}), 403
    
    new_status = request.json.get('status')
    if not new_status:
        return jsonify({'success': False, 'message': 'Estado no especificado'}), 400
    
    if report.change_status(new_status):
        try:
            db.session.commit()
            return jsonify({
                'success': True,
                'message': 'Estado actualizado exitosamente',
                'status_label': report.status_label,
                'status_color': report.status_color
            })
        except Exception as e:
            db.session.rollback()
            return jsonify({'success': False, 'message': 'Error al actualizar el estado'}), 500
    else:
        return jsonify({'success': False, 'message': 'Transición de estado no válida'}), 400

@reports.route('/report/<int:report_id>/delete', methods=['POST'])
@login_required
def delete_report(report_id):
    """Eliminar un reporte"""
    report = Report.query.get_or_404(report_id)
    
    if report.user_id != current_user.id:
        flash('No tienes permiso para eliminar este reporte.', 'danger')
        return redirect(url_for('reports.list_reports'))
    
    # Guardar el project_id si existe para redireccionar
    project_id = report.project_id
    
    # Eliminar el reporte
    db.session.delete(report)
    db.session.commit()
    
    flash('Reporte eliminado exitosamente.', 'success')
    
    # Redireccionar al proyecto si el reporte pertenecía a uno
    if project_id:
        return redirect(url_for('projects.view_project', project_id=project_id))
    return redirect(url_for('reports.list_reports')) 