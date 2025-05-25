from datetime import datetime
from app import db

class Comment(db.Model):
    __tablename__ = 'comment'

    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relaciones
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    task_id = db.Column(db.Integer, db.ForeignKey('task.id'), nullable=True)
    project_id = db.Column(db.Integer, db.ForeignKey('project.id'), nullable=True)
    report_id = db.Column(db.Integer, db.ForeignKey('report.id'), nullable=True)
    
    # Relaciones inversas
    user = db.relationship('User', backref=db.backref('comments', lazy='dynamic'))
    task = db.relationship('Task', backref=db.backref('comments', lazy='dynamic'))
    project = db.relationship('Project', backref=db.backref('comments', lazy='dynamic'))
    report = db.relationship('Report', backref=db.backref('comments', lazy='dynamic'))

    def __init__(self, content, user_id, task_id=None, project_id=None, report_id=None):
        self.content = content
        self.user_id = user_id
        self.task_id = task_id
        self.project_id = project_id
        self.report_id = report_id

    def to_dict(self):
        return {
            'id': self.id,
            'content': self.content,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
            'user_id': self.user_id,
            'task_id': self.task_id,
            'project_id': self.project_id,
            'report_id': self.report_id
        }

    def __repr__(self):
        return f'<Comment {self.id}>' 