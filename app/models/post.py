from datetime import datetime
from app import db
from app.models.user import User
from app.models.tag import Tag
from app.models.comment import Comment

class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    content = db.Column(db.Text, nullable=False)
    summary = db.Column(db.String(300))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    published = db.Column(db.Boolean, default=False)
    views = db.Column(db.Integer, default=0)
    
    # Relaciones
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    author = db.relationship('User', backref=db.backref('posts', lazy=True))
    
    # Tags (relación muchos a muchos)
    tags = db.relationship('app.models.tag.Tag', secondary='post_tags',
                         backref=db.backref('posts', lazy=True))
    
    # Likes (relación muchos a muchos con usuarios)
    likes = db.relationship('User', secondary='post_likes',
                          backref=db.backref('liked_posts', lazy=True))
    
    # Comentarios
    comments = db.relationship('app.models.comment.Comment', backref='post', lazy=True)
    
    def __repr__(self):
        return f'<Post {self.title}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'content': self.content,
            'summary': self.summary,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
            'published': self.published,
            'views': self.views,
            'author': {
                'id': self.author.id,
                'username': self.author.username,
                'avatar': self.author.avatar(30)
            },
            'tags': [tag.name for tag in self.tags],
            'likes_count': len(self.likes)
        }

# Tabla intermedia para la relación muchos a muchos entre posts y tags
post_tags = db.Table('post_tags',
    db.Column('post_id', db.Integer, db.ForeignKey('post.id'), primary_key=True),
    db.Column('tag_id', db.Integer, db.ForeignKey('tag.id'), primary_key=True),
    extend_existing=True
)

# Tabla intermedia para los likes de los posts
post_likes = db.Table('post_likes',
    db.Column('post_id', db.Integer, db.ForeignKey('post.id'), primary_key=True),
    db.Column('user_id', db.Integer, db.ForeignKey('user.id'), primary_key=True),
    db.Column('created_at', db.DateTime, default=datetime.utcnow),
    extend_existing=True
)

class Comment(db.Model):
    __tablename__ = 'comment'
    __table_args__ = {'extend_existing': True}
    
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relaciones
    post_id = db.Column(db.Integer, db.ForeignKey('post.id'), nullable=False)
    post = db.relationship('Post', backref=db.backref('comments', lazy=True))
    
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    author = db.relationship('User', backref=db.backref('comments', lazy=True))
    
    # Para comentarios anidados
    parent_id = db.Column(db.Integer, db.ForeignKey('comment.id'))
    replies = db.relationship('Comment', backref=db.backref('parent', remote_side=[id]),
                            lazy=True)
    
    def __repr__(self):
        return f'<Comment {self.id}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'content': self.content,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
            'author': {
                'id': self.author.id,
                'username': self.author.username,
                'avatar': self.author.avatar(30)
            },
            'replies': [reply.to_dict() for reply in self.replies]
        } 