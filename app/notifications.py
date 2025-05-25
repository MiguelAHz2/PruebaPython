from flask_socketio import SocketIO
from flask_login import current_user
from datetime import datetime
import uuid

socketio = SocketIO()

class NotificationService:
    def __init__(self):
        self.notifications = {}  # user_id: [notifications]

    def create_notification(self, user_id, title, message, notification_type='info'):
        """Crear una nueva notificación"""
        notification = {
            'id': str(uuid.uuid4()),
            'title': title,
            'message': message,
            'type': notification_type,
            'timestamp': datetime.utcnow().isoformat(),
            'read': False
        }
        
        if user_id not in self.notifications:
            self.notifications[user_id] = []
        
        self.notifications[user_id].insert(0, notification)
        
        # Mantener solo las últimas 50 notificaciones
        if len(self.notifications[user_id]) > 50:
            self.notifications[user_id] = self.notifications[user_id][:50]
        
        # Emitir la notificación al usuario
        socketio.emit('notification', notification, room=str(user_id))
        
        return notification

    def get_user_notifications(self, user_id, unread_only=False):
        """Obtener notificaciones de un usuario"""
        if user_id not in self.notifications:
            return []
        
        notifications = self.notifications[user_id]
        if unread_only:
            notifications = [n for n in notifications if not n['read']]
        
        return notifications

    def mark_as_read(self, user_id, notification_id):
        """Marcar una notificación como leída"""
        if user_id not in self.notifications:
            return False
        
        for notification in self.notifications[user_id]:
            if notification['id'] == notification_id:
                notification['read'] = True
                return True
        
        return False

    def mark_all_as_read(self, user_id):
        """Marcar todas las notificaciones de un usuario como leídas"""
        if user_id not in self.notifications:
            return
        
        for notification in self.notifications[user_id]:
            notification['read'] = True

    def delete_notification(self, user_id, notification_id):
        """Eliminar una notificación"""
        if user_id not in self.notifications:
            return False
        
        self.notifications[user_id] = [
            n for n in self.notifications[user_id] 
            if n['id'] != notification_id
        ]
        return True

    def clear_notifications(self, user_id):
        """Eliminar todas las notificaciones de un usuario"""
        if user_id in self.notifications:
            self.notifications[user_id] = []

# Instancia global del servicio de notificaciones
notification_service = NotificationService()

# Eventos de Socket.IO
@socketio.on('connect')
def handle_connect():
    if current_user.is_authenticated:
        socketio.emit('notifications', {
            'notifications': notification_service.get_user_notifications(current_user.id)
        })

@socketio.on('mark_as_read')
def handle_mark_as_read(data):
    if current_user.is_authenticated:
        notification_service.mark_as_read(current_user.id, data['id'])

@socketio.on('mark_all_as_read')
def handle_mark_all_as_read():
    if current_user.is_authenticated:
        notification_service.mark_all_as_read(current_user.id)

# Funciones de ayuda para crear notificaciones comunes
def notify_login(user):
    """Notificar inicio de sesión"""
    return notification_service.create_notification(
        user.id,
        '¡Bienvenido de nuevo!',
        f'Has iniciado sesión exitosamente el {datetime.now().strftime("%d/%m/%Y a las %H:%M")}',
        'success'
    )

def notify_registration(user):
    """Notificar registro exitoso"""
    return notification_service.create_notification(
        user.id,
        '¡Registro exitoso!',
        'Tu cuenta ha sido creada correctamente. ¡Bienvenido!',
        'success'
    )

def notify_password_change(user):
    """Notificar cambio de contraseña"""
    return notification_service.create_notification(
        user.id,
        'Contraseña actualizada',
        'Tu contraseña ha sido actualizada exitosamente.',
        'info'
    )

def notify_profile_update(user):
    """Notificar actualización de perfil"""
    return notification_service.create_notification(
        user.id,
        'Perfil actualizado',
        'Los cambios en tu perfil han sido guardados correctamente.',
        'success'
    )

def notify_security_alert(user, message):
    """Notificar alerta de seguridad"""
    return notification_service.create_notification(
        user.id,
        'Alerta de seguridad',
        message,
        'warning'
    ) 