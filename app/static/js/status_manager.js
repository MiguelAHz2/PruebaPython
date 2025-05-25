class StatusManager {
    constructor() {
        this.setupEventListeners();
    }

    setupEventListeners() {
        // Escuchar cambios en los selectores de estado
        document.querySelectorAll('.status-select').forEach(select => {
            select.addEventListener('change', (event) => {
                const itemType = event.target.dataset.type;
                const itemId = event.target.dataset.id;
                const newStatus = event.target.value;
                
                this.updateStatus(itemType, itemId, newStatus, event.target);
            });
        });
    }

    async updateStatus(type, id, status, selectElement) {
        const url = `/${type}/${id}/status`;
        const badge = selectElement.closest('.card').querySelector('.status-badge');
        const allBadges = document.querySelectorAll(`[data-${type}-id="${id}"] .status-badge`);
        
        try {
            const response = await fetch(url, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Accept': 'application/json',
                    'X-Requested-With': 'XMLHttpRequest',
                    'X-CSRFToken': document.querySelector('meta[name="csrf-token"]').content
                },
                body: JSON.stringify({ status: status })
            });

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            const data = await response.json();
            
            if (data.success) {
                // Actualizar todos los badges relacionados con este item
                allBadges.forEach(badge => {
                    badge.textContent = data.status_label;
                    badge.className = `badge bg-${data.status_color} status-badge`;
                });
                
                // Actualizar el badge principal si existe
                if (badge) {
                    badge.textContent = data.status_label;
                    badge.className = `badge bg-${data.status_color} status-badge`;
                }
                
                // Actualizar el valor actual del select
                selectElement.dataset.currentStatus = status;
                
                // Mostrar mensaje de éxito
                this.showAlert('success', data.message);
            } else {
                // Revertir el select al valor anterior
                selectElement.value = selectElement.dataset.currentStatus;
                this.showAlert('danger', data.message);
            }
        } catch (error) {
            console.error('Error:', error);
            // Revertir el select al valor anterior
            selectElement.value = selectElement.dataset.currentStatus;
            this.showAlert('danger', 'Error al actualizar el estado');
        }
    }

    showAlert(type, message) {
        const alertDiv = document.createElement('div');
        alertDiv.className = `alert alert-${type} alert-dismissible fade show`;
        alertDiv.innerHTML = `
            <div class="d-flex align-items-center">
                <i class="fas fa-info-circle me-2"></i>
                ${message}
            </div>
            <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
        `;
        
        const container = document.querySelector('.container');
        container.insertBefore(alertDiv, container.firstChild);
        
        // Auto-cerrar después de 3 segundos
        setTimeout(() => {
            alertDiv.remove();
        }, 3000);
    }
}

// Inicializar cuando el DOM esté listo
document.addEventListener('DOMContentLoaded', () => {
    new StatusManager();
}); 