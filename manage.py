from app import create_app, db
from app.models import User, Post, Tag, Comment
from datetime import datetime, timedelta
import random

app = create_app()

def init_db():
    with app.app_context():
        # Eliminar todas las tablas existentes
        db.drop_all()
        # Crear todas las tablas nuevamente
        db.create_all()
        
        print("Creando datos de ejemplo...")
        
        # Crear algunos usuarios
        users = []
        for i in range(5):
            user = User(
                username=f'usuario{i}',
                email=f'usuario{i}@ejemplo.com'
            )
            user.set_password(f'password{i}')
            users.append(user)
            db.session.add(user)
        
        # Crear algunos tags
        tags = []
        tag_names = ['Python', 'Flask', 'Web', 'API', 'Frontend', 'Backend', 'Database']
        for name in tag_names:
            tag = Tag(
                name=name,
                slug=name.lower()
            )
            tags.append(tag)
            db.session.add(tag)
        
        # Crear algunos posts
        for i in range(20):
            post = Post(
                title=f'Post de ejemplo #{i}',
                content=f'Este es el contenido del post #{i}. Lorem ipsum dolor sit amet...',
                summary=f'Resumen del post #{i}',
                author=random.choice(users),
                published=True,
                created_at=datetime.utcnow() - timedelta(days=random.randint(0, 30)),
                views=random.randint(0, 1000)
            )
            # Agregar tags aleatorios
            post.tags = random.sample(tags, random.randint(1, 3))
            # Agregar likes aleatorios
            post.likes = random.sample(users, random.randint(0, len(users)))
            db.session.add(post)
            
            # Agregar algunos comentarios
            for _ in range(random.randint(0, 5)):
                comment = Comment(
                    content=f'Este es un comentario en el post #{i}',
                    author=random.choice(users),
                    post=post,
                    created_at=post.created_at + timedelta(hours=random.randint(1, 24))
                )
                db.session.add(comment)
                
                # Agregar algunas respuestas a los comentarios
                for _ in range(random.randint(0, 3)):
                    reply = Comment(
                        content=f'Esta es una respuesta al comentario',
                        author=random.choice(users),
                        post=post,
                        parent=comment,
                        created_at=comment.created_at + timedelta(hours=random.randint(1, 12))
                    )
                    db.session.add(reply)
        
        db.session.commit()
        print("Base de datos reinicializada correctamente con datos de ejemplo.")

if __name__ == '__main__':
    init_db() 