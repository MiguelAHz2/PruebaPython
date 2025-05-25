from flask import Blueprint, render_template, redirect, url_for, jsonify, request
from flask_login import current_user, login_required
from app.models.project import Project
from app.models.report import Report
from app.models import User
from app import cache
from sqlalchemy import or_

main = Blueprint('main', __name__)

@main.route('/')
@main.route('/index')
def index():
    """Página principal que muestra información general o el dashboard si está autenticado"""
    if current_user.is_authenticated:
        # Obtener proyectos y reportes recientes
        projects = Project.query.filter_by(user_id=current_user.id)\
            .order_by(Project.created_at.desc())\
            .limit(5)\
            .all()
        
        reports = Report.query.filter_by(user_id=current_user.id)\
            .order_by(Report.created_at.desc())\
            .limit(5)\
            .all()
        
        return render_template('main/index_auth.html',
                            title='Inicio',
                            projects=projects,
                            reports=reports)
    return render_template('main/index.html', title='Inicio')

@main.route('/dashboard')
@login_required
def dashboard():
    """Dashboard que muestra proyectos y reportes del usuario"""
    # Obtener los últimos 5 proyectos y reportes
    projects = Project.query.filter_by(user_id=current_user.id)\
        .order_by(Project.created_at.desc())\
        .limit(5)\
        .all()
    
    reports = Report.query.filter_by(user_id=current_user.id)\
        .order_by(Report.created_at.desc())\
        .limit(5)\
        .all()
    
    # Crear lista de actividades recientes
    activities = []
    
    # Añadir proyectos a la lista de actividades
    for project in projects:
        activities.append({
            'type': 'project',
            'id': project.id,
            'title': project.title,
            'created_at': project.created_at,
            'status': project.status,
            'status_label': project.status_label,
            'status_color': project.status_color
        })
    
    # Añadir reportes a la lista de actividades
    for report in reports:
        activities.append({
            'type': 'report',
            'id': report.id,
            'title': report.title,
            'created_at': report.created_at,
            'status': report.status,
            'status_label': report.status_label,
            'status_color': report.status_color
        })
    
    # Ordenar actividades por fecha de creación
    activities.sort(key=lambda x: x['created_at'], reverse=True)
    
    return render_template('main/dashboard.html',
                         title='Dashboard',
                         projects=projects,
                         reports=reports,
                         activities=activities[:5])

@main.route('/search')
@login_required
@cache.memoize(timeout=60)  # Reducimos el tiempo de caché a 1 minuto
def search():
    query = request.args.get('q', '').strip()
    if not query or len(query) < 2:
        return jsonify([])
    
    try:
        # Buscar en proyectos del usuario actual
        projects = Project.query.filter(
            Project.user_id == current_user.id,
            or_(
                Project.title.ilike(f'%{query}%'),
                Project.description.ilike(f'%{query}%')
            )
        ).limit(10).all()
        
        # Buscar en reportes del usuario actual
        reports = Report.query.filter(
            Report.user_id == current_user.id,
            or_(
                Report.title.ilike(f'%{query}%'),
                Report.content.ilike(f'%{query}%')
            )
        ).all()
        
        results = []
        
        # Agregar proyectos a los resultados
        for project in projects:
            results.append({
                'type': 'project',
                'id': project.id,
                'title': project.title,
                'url': url_for('projects.view_project', project_id=project.id)
            })
        
        # Agregar reportes a los resultados
        for report in reports:
            try:
                project_title = report.project.title if report.project else "Sin proyecto"
                results.append({
                    'type': 'report',
                    'id': report.id,
                    'title': f'{report.title} (Proyecto: {project_title})',
                    'url': url_for('reports.view_report', report_id=report.id)
                })
            except Exception as report_error:
                print(f'Error al procesar reporte {report.id}: {str(report_error)}')
                continue
        
        # Ordenar resultados por relevancia y tipo
        results.sort(key=lambda x: (
            not x['title'].lower().startswith(query.lower()),  # Primero los que empiezan con la búsqueda
            x['type'] != 'project',  # Proyectos primero
            not query.lower() in x['title'].lower(),          # Luego los que contienen la búsqueda
            x['title'].lower()                                # Finalmente por orden alfabético
        ))
        
        response = jsonify(results[:20])  # Limitamos el total de resultados a 20
        response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, post-check=0, pre-check=0'
        response.headers['Pragma'] = 'no-cache'
        response.headers['Expires'] = '0'
        return response
        
    except Exception as e:
        print(f'Error en la búsqueda: {str(e)}')
        return jsonify({'error': 'Error al realizar la búsqueda'}), 500 