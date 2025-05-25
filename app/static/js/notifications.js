// Configuración de Socket.IO
const socket = io();

// Clase para manejar notificaciones
class NotificationManager {
    constructor() {
        this.socket = io();
        this.notifications = [];
        this.unreadCount = 0;
        this.setupSocketListeners();
        this.setupUIElements();
    }

    setupSocketListeners() {
        this.socket.on('notification', (data) => {
            this.showNotification(data);
            this.updateUnreadCount(1);
        });
    }

    setupUIElements() {
        this.badge = document.getElementById('notification-badge');
        this.panel = document.getElementById('notification-panel');
        this.toastContainer = document.getElementById('toast-container');
    }

    showNotification(data) {
        // Mostrar toast
        const toast = document.createElement('div');
        toast.className = `toast show animate__animated animate__fadeIn ${data.type || 'bg-primary'} text-white`;
        toast.setAttribute('role', 'alert');
        toast.innerHTML = `
            <div class="toast-body">
                <button type="button" class="btn-close btn-close-white float-end" data-bs-dismiss="toast"></button>
                ${data.message}
            </div>
        `;
        this.toastContainer.appendChild(toast);

        // Agregar al panel
        const notification = document.createElement('div');
        notification.className = 'notification-item unread';
        notification.innerHTML = `
            <div class="notification-content">
                <p class="mb-1">${data.message}</p>
                <small class="text-muted">${new Date().toLocaleTimeString()}</small>
            </div>
        `;
        this.panel.appendChild(notification);

        // Auto-ocultar toast después de 5 segundos
        setTimeout(() => {
            toast.classList.remove('show');
            setTimeout(() => toast.remove(), 500);
        }, 5000);
    }

    updateUnreadCount(increment) {
        this.unreadCount += increment;
        if (this.unreadCount > 0) {
            this.badge.textContent = this.unreadCount;
            this.badge.classList.remove('d-none');
        } else {
            this.badge.classList.add('d-none');
        }
    }

    markAllAsRead() {
        const unreadItems = this.panel.querySelectorAll('.notification-item.unread');
        unreadItems.forEach(item => item.classList.remove('unread'));
        this.updateUnreadCount(-this.unreadCount);
    }

    getIconForType(type) {
        const icons = {
            success: 'fa-check-circle text-success',
            warning: 'fa-exclamation-triangle text-warning',
            error: 'fa-times-circle text-danger',
            info: 'fa-info-circle text-info'
        };
        return icons[type] || icons.info;
    }

    timeAgo(timestamp) {
        const seconds = Math.floor((new Date() - new Date(timestamp)) / 1000);
        
        const intervals = {
            año: 31536000,
            mes: 2592000,
            semana: 604800,
            día: 86400,
            hora: 3600,
            minuto: 60,
            segundo: 1
        };
        
        for (let [unit, secondsInUnit] of Object.entries(intervals)) {
            const interval = Math.floor(seconds / secondsInUnit);
            
            if (interval >= 1) {
                return `hace ${interval} ${unit}${interval > 1 ? 's' : ''}`;
            }
        }
        
        return 'justo ahora';
    }
}

// Inicializar el gestor de notificaciones
const notificationManager = new NotificationManager();

// Exportar para uso global
window.notificationManager = notificationManager; 