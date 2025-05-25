from datetime import datetime
from app import db
from sqlalchemy import Index

class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    due_date = db.Column(db.DateTime)
    status = db.Column(db.String(20), default='pending')
    priority = db.Column(db.String(20), default='medium')
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    project_id = db.Column(db.Integer, db.ForeignKey('project.id'), nullable=False)
    
    # Índices
    __table_args__ = (
        Index('idx_task_user', user_id),
        Index('idx_task_project', project_id),
        Index('idx_task_status', status),
        Index('idx_task_created', created_at),
        Index('idx_task_due_date', due_date),
    )
    
    # Estados posibles
    STATES = {
        'pending': 'Pendiente',
        'in_progress': 'En Progreso',
        'completed': 'Completado',
        'cancelled': 'Cancelado'
    }
    
    # Prioridades
    PRIORITIES = {
        'low': 'Baja',
        'medium': 'Media',
        'high': 'Alta',
        'urgent': 'Urgente'
    }
    
    # Colores para los estados
    STATE_COLORS = {
        'pending': 'warning',
        'in_progress': 'info',
        'completed': 'success',
        'cancelled': 'secondary'
    }
    
    # Colores para las prioridades
    PRIORITY_COLORS = {
        'low': 'success',
        'medium': 'info',
        'high': 'warning',
        'urgent': 'danger'
    }
    
    @property
    def status_label(self):
        """Retorna el nombre legible del estado"""
        return self.STATES.get(self.status, 'Desconocido')
    
    @property
    def priority_label(self):
        """Retorna el nombre legible de la prioridad"""
        return self.PRIORITIES.get(self.priority, 'Desconocido')
    
    @property
    def status_color(self):
        """Retorna el color Bootstrap para el estado"""
        return self.STATE_COLORS.get(self.status, 'secondary')
    
    @property
    def priority_color(self):
        """Retorna el color Bootstrap para la prioridad"""
        return self.PRIORITY_COLORS.get(self.priority, 'secondary')
    
    def can_transition_to(self, new_status):
        """Verifica si la tarea puede cambiar al estado especificado"""
        if new_status not in self.STATES:
            return False
            
        # Reglas de transición
        if self.status == 'cancelled':
            return False  # Una tarea cancelada no puede cambiar de estado
        if new_status == 'completed' and self.status == 'pending':
            return False  # Debe pasar por 'in_progress' antes de completarse
            
        return True
    
    def change_status(self, new_status):
        """Cambia el estado de la tarea si es válido"""
        if self.can_transition_to(new_status):
            self.status = new_status
            self.updated_at = datetime.utcnow()
            return True
        return False
    
    @staticmethod
    def get_status_choices():
        """Retorna las opciones de estado para formularios"""
        return [(k, v) for k, v in Task.STATES.items()]
    
    @staticmethod
    def get_priority_choices():
        """Retorna las opciones de prioridad para formularios"""
        return [(k, v) for k, v in Task.PRIORITIES.items()]
    
    def __repr__(self):
        return f'<Task {self.title}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
            'due_date': self.due_date.isoformat() if self.due_date else None,
            'status': self.status,
            'priority': self.priority,
            'user_id': self.user_id,
            'project_id': self.project_id
        } 