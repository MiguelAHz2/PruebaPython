from datetime import datetime
from app import db
from sqlalchemy import Index

class Report(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    content = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    type = db.Column(db.String(20), default='general')
    status = db.Column(db.String(20), default='draft')
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    project_id = db.Column(db.Integer, db.ForeignKey('project.id'), nullable=False)
    
    # Índices
    __table_args__ = (
        Index('idx_report_user', user_id),
        Index('idx_report_project', project_id),
        Index('idx_report_status', status),
        Index('idx_report_created', created_at),
        Index('idx_report_title_content', 'title', 'content'),
    )
    
    # Tipos de reporte
    TYPES = {
        'general': 'General',
        'bug': 'Error',
        'feature': 'Nueva Funcionalidad',
        'improvement': 'Mejora',
        'documentation': 'Documentación'
    }
    
    # Estados posibles
    STATES = {
        'draft': 'Borrador',
        'in_review': 'En Revisión',
        'approved': 'Aprobado',
        'rejected': 'Rechazado',
        'in_progress': 'En Progreso',
        'completed': 'Completado',
        'archived': 'Archivado'
    }
    
    # Colores para los tipos
    TYPE_COLORS = {
        'general': 'secondary',
        'bug': 'danger',
        'feature': 'success',
        'improvement': 'info',
        'documentation': 'primary'
    }
    
    # Colores para los estados
    STATE_COLORS = {
        'draft': 'secondary',
        'in_review': 'info',
        'approved': 'success',
        'rejected': 'danger',
        'in_progress': 'primary',
        'completed': 'success',
        'archived': 'dark'
    }
    
    @property
    def type_label(self):
        """Retorna el nombre legible del tipo"""
        return self.TYPES.get(self.type, 'Desconocido')
    
    @property
    def status_label(self):
        """Retorna el nombre legible del estado"""
        return self.STATES.get(self.status, 'Desconocido')
    
    @property
    def type_color(self):
        """Retorna el color Bootstrap para el tipo"""
        return self.TYPE_COLORS.get(self.type, 'secondary')
    
    @property
    def status_color(self):
        """Retorna el color Bootstrap para el estado"""
        return self.STATE_COLORS.get(self.status, 'secondary')
    
    def can_transition_to(self, new_status):
        """Verifica si el reporte puede cambiar al estado especificado"""
        if new_status not in self.STATES:
            return False
            
        # Reglas de transición
        if self.status == 'archived':
            return False  # Un reporte archivado no puede cambiar de estado
        if new_status == 'completed' and self.status not in ['approved', 'in_progress']:
            return False  # Debe estar aprobado o en progreso para completarse
        if new_status == 'in_progress' and self.status != 'approved':
            return False  # Debe estar aprobado para iniciar progreso
            
        return True
    
    def change_status(self, new_status):
        """Cambia el estado del reporte si es válido"""
        if self.can_transition_to(new_status):
            self.status = new_status
            self.updated_at = datetime.utcnow()
            return True
        return False
    
    @staticmethod
    def get_type_choices():
        """Retorna las opciones de tipo para formularios"""
        return [(k, v) for k, v in Report.TYPES.items()]
    
    @staticmethod
    def get_status_choices():
        """Retorna las opciones de estado para formularios"""
        return [(k, v) for k, v in Report.STATES.items()]
    
    def __repr__(self):
        return f'<Report {self.title}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'content': self.content,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
            'status': self.status,
            'user_id': self.user_id,
            'project_id': self.project_id
        }
    
    @property
    def summary(self):
        """Retorna un resumen del contenido del reporte"""
        if not self.content:
            return ''
        words = self.content.split()
        if len(words) <= 30:
            return self.content
        return ' '.join(words[:30]) + '...' 