from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_required, current_user
from app import db
from app.models.project import Project
from app.forms.project_form import ProjectForm

projects = Blueprint('projects', __name__)

@projects.route('/projects')
@login_required
def list_projects():
    """Lista todos los proyectos del usuario"""
    # Obtener parámetros de filtrado
    status = request.args.get('status', 'all')
    
    # Consulta base
    query = Project.query.filter_by(user_id=current_user.id)
    
    # Aplicar filtro de estado si se especifica
    if status != 'all' and status in Project.STATES:
        query = query.filter_by(status=status)
    
    # Ordenar por última actualización
    projects = query.order_by(Project.updated_at.desc()).all()
    
    return render_template('projects/list_projects.html',
                         projects=projects,
                         current_status=status,
                         states=Project.STATES)

@projects.route('/project/new', methods=['GET', 'POST'])
@login_required
def create_project():
    """Crear un nuevo proyecto"""
    form = ProjectForm()
    if form.validate_on_submit():
        project = Project(
            title=form.title.data,
            description=form.description.data,
            user_id=current_user.id
        )
        db.session.add(project)
        db.session.commit()
        flash('Proyecto creado exitosamente.', 'success')
        return redirect(url_for('projects.view_project', project_id=project.id))
    
    return render_template('projects/project_form.html',
                         title='Nuevo Proyecto',
                         form=form)

@projects.route('/project/<int:project_id>')
@login_required
def view_project(project_id):
    """Ver detalles de un proyecto"""
    project = Project.query.get_or_404(project_id)
    if project.user_id != current_user.id:
        flash('No tienes permiso para ver este proyecto.', 'danger')
        return redirect(url_for('main.index'))
    
    return render_template('projects/project_detail.html',
                         project=project)

@projects.route('/project/<int:project_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_project(project_id):
    """Editar un proyecto existente"""
    project = Project.query.get_or_404(project_id)
    if project.user_id != current_user.id:
        flash('No tienes permiso para editar este proyecto.', 'danger')
        return redirect(url_for('main.index'))
    
    form = ProjectForm(obj=project)
    if form.validate_on_submit():
        project.title = form.title.data
        project.description = form.description.data
        db.session.commit()
        flash('Proyecto actualizado exitosamente.', 'success')
        return redirect(url_for('projects.view_project', project_id=project.id))
    
    return render_template('projects/project_form.html',
                         title='Editar Proyecto',
                         form=form)

@projects.route('/project/<int:project_id>/status', methods=['POST'])
@login_required
def change_project_status(project_id):
    """Cambiar el estado de un proyecto"""
    project = Project.query.get_or_404(project_id)
    if project.user_id != current_user.id:
        return jsonify({'success': False, 'message': 'No tienes permiso para modificar este proyecto'}), 403
    
    new_status = request.json.get('status')
    if not new_status:
        return jsonify({'success': False, 'message': 'Estado no especificado'}), 400
    
    if project.change_status(new_status):
        try:
            db.session.commit()
            return jsonify({
                'success': True,
                'message': 'Estado actualizado exitosamente',
                'status_label': project.status_label,
                'status_color': project.status_color
            })
        except Exception as e:
            db.session.rollback()
            return jsonify({'success': False, 'message': 'Error al actualizar el estado'}), 500
    else:
        return jsonify({'success': False, 'message': 'Transición de estado no válida'}), 400

@projects.route('/project/<int:project_id>/delete', methods=['POST'])
@login_required
def delete_project(project_id):
    """Eliminar un proyecto y todos sus reportes asociados"""
    project = Project.query.get_or_404(project_id)
    
    if project.user_id != current_user.id:
        flash('No tienes permiso para eliminar este proyecto.', 'danger')
        return redirect(url_for('projects.list_projects'))
    
    # Eliminar el proyecto (los reportes se eliminarán en cascada)
    db.session.delete(project)
    db.session.commit()
    
    flash('Proyecto eliminado exitosamente.', 'success')
    return redirect(url_for('projects.list_projects')) 