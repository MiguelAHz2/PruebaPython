from datetime import datetime
from app import db
from sqlalchemy import Index

class Project(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    status = db.Column(db.String(20), default='active')
    priority = db.Column(db.String(20), default='medium')
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    
    # Relaciones
    tasks = db.relationship('Task', backref='project', lazy='dynamic', cascade='all, delete-orphan')
    reports = db.relationship('Report', backref='project', lazy='dynamic', cascade='all, delete-orphan')
    
    # Índices
    __table_args__ = (
        Index('idx_project_user', user_id),
        Index('idx_project_status', status),
        Index('idx_project_created', created_at),
        Index('idx_project_title_description', 'title', 'description'),
    )
    
    # Estados posibles
    STATES = {
        'active': 'Activo',
        'in_progress': 'En Progreso',
        'on_hold': 'En Pausa',
        'completed': 'Completado',
        'archived': 'Archivado'
    }

    # Colores para los estados
    STATE_COLORS = {
        'active': 'primary',
        'in_progress': 'info',
        'on_hold': 'warning',
        'completed': 'success',
        'archived': 'secondary'
    }
    
    @property
    def status_label(self):
        """Retorna el nombre legible del estado"""
        return self.STATES.get(self.status, 'Desconocido')
    
    @property
    def status_color(self):
        """Retorna el color Bootstrap para el estado"""
        return self.STATE_COLORS.get(self.status, 'secondary')
    
    def can_transition_to(self, new_status):
        """Verifica si el proyecto puede cambiar al estado especificado"""
        if new_status not in self.STATES:
            return False
            
        # Reglas de transición
        if self.status == 'archived':
            return False  # Un proyecto archivado no puede cambiar de estado
        if new_status == 'completed' and self.status == 'active':
            return False  # Debe pasar por 'in_progress' antes de completarse
            
        return True
    
    def change_status(self, new_status):
        """Cambia el estado del proyecto si es válido"""
        if self.can_transition_to(new_status):
            self.status = new_status
            self.updated_at = datetime.utcnow()
            return True
        return False
    
    @staticmethod
    def get_status_choices():
        """Retorna las opciones de estado para formularios"""
        return [(k, v) for k, v in Project.STATES.items()]
    
    def get_completed_tasks(self):
        """Retorna el número de tareas completadas en el proyecto"""
        from app.models.user import Activity
        return Activity.query.filter_by(
            type='task',
            action='completed',
            target_id=self.id
        ).count()
    
    def __repr__(self):
        return f'<Project {self.title}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
            'status': self.status,
            'priority': self.priority,
            'user_id': self.user_id,
            'task_count': self.tasks.count(),
            'report_count': self.reports.count()
        }
    
    @property
    def completion_rate(self):
        total_tasks = self.tasks.count()
        if total_tasks == 0:
            return 0
        completed_tasks = self.tasks.filter_by(status='completed').count()
        return (completed_tasks / total_tasks) * 100 