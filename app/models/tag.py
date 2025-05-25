from app import db

# Tabla de asociación entre tags y tareas
task_tags = db.Table('task_tags',
    db.Column('tag_id', db.Integer, db.ForeignKey('tag.id'), primary_key=True),
    db.Column('task_id', db.Integer, db.ForeignKey('task.id'), primary_key=True),
    extend_existing=True
)

# Tabla de asociación entre tags y proyectos
project_tags = db.Table('project_tags',
    db.Column('tag_id', db.Integer, db.ForeignKey('tag.id'), primary_key=True),
    db.Column('project_id', db.Integer, db.ForeignKey('project.id'), primary_key=True),
    extend_existing=True
)

class Tag(db.Model):
    __tablename__ = 'tag'
    __table_args__ = {'extend_existing': True}

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)
    color = db.Column(db.String(7), nullable=False, default='#000000')  # Formato hexadecimal
    description = db.Column(db.String(200))
    
    # Relaciones many-to-many
    tasks = db.relationship('Task', secondary=task_tags, backref=db.backref('tags', lazy='dynamic'))
    projects = db.relationship('Project', secondary=project_tags, backref=db.backref('tags', lazy='dynamic'))

    def __init__(self, name, color='#000000', description=None):
        self.name = name
        self.color = color
        self.description = description

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'color': self.color,
            'description': self.description
        }

    def __repr__(self):
        return f'<Tag {self.name}>' 