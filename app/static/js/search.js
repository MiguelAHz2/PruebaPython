document.addEventListener('DOMContentLoaded', function() {
    const searchInput = document.getElementById('searchInput');
    const searchResults = document.getElementById('searchResults');
    const searchButton = document.querySelector('.search-button');
    let searchTimeout;
    let currentRequest = null;

    function performSearch(query) {
        // Limpiar búsqueda anterior si existe
        if (currentRequest) {
            currentRequest.abort();
        }

        // Si la consulta está vacía o es muy corta, ocultar resultados
        if (!query || query.length < 2) {
            searchResults.innerHTML = '';
            searchResults.style.display = 'none';
            return;
        }

        // Mostrar indicador de carga
        searchResults.innerHTML = `
            <div class="p-3 text-center">
                <i class="fas fa-spinner fa-spin"></i>
                <p class="mb-0">Buscando...</p>
            </div>
        `;
        searchResults.style.display = 'block';

        // Crear nuevo AbortController para esta búsqueda
        const controller = new AbortController();
        currentRequest = controller;

        // Realizar la búsqueda
        fetch(`/search?q=${encodeURIComponent(query)}`, {
            signal: controller.signal,
            headers: {
                'X-Requested-With': 'XMLHttpRequest',
                'Accept': 'application/json'
            }
        })
        .then(response => {
            if (!response.ok) {
                throw new Error('Error en la respuesta del servidor');
            }
            return response.json();
        })
        .then(data => {
            // Verificar si esta es aún la búsqueda actual
            if (currentRequest !== controller) {
                return;
            }

            if (!data || (Array.isArray(data) && data.length === 0)) {
                searchResults.innerHTML = `
                    <div class="p-3 text-center">
                        <p class="mb-0">No se encontraron resultados</p>
                    </div>
                `;
            } else if (data.error) {
                searchResults.innerHTML = `
                    <div class="p-3 text-center text-danger">
                        <p class="mb-0">${data.error}</p>
                    </div>
                `;
            } else {
                const resultsHtml = data.map(item => `
                    <a href="${item.url}" class="search-result-item d-block p-2">
                        <div class="d-flex align-items-center">
                            <i class="fas fa-${item.type === 'project' ? 'project-diagram' : 'file-alt'} me-2 
                               ${item.type === 'project' ? 'text-primary' : 'text-info'}"></i>
                            <div>
                                <div class="small text-muted">${item.type === 'project' ? 'Proyecto' : 'Reporte'}</div>
                                <div>${item.title}</div>
                            </div>
                        </div>
                    </a>
                `).join('');
                searchResults.innerHTML = resultsHtml;
            }
            searchResults.style.display = 'block';
        })
        .catch(error => {
            if (error.name === 'AbortError') {
                return; // Búsqueda cancelada, ignorar error
            }
            console.error('Error en la búsqueda:', error);
            searchResults.innerHTML = `
                <div class="p-3 text-center text-danger">
                    <p class="mb-0">Error al realizar la búsqueda</p>
                </div>
            `;
            searchResults.style.display = 'block';
        })
        .finally(() => {
            if (currentRequest === controller) {
                currentRequest = null;
            }
        });
    }

    // Event listener para el input con debounce
    searchInput.addEventListener('input', function() {
        clearTimeout(searchTimeout);
        const query = this.value.trim();
        searchTimeout = setTimeout(() => performSearch(query), 300);
    });

    // Event listener para el botón de búsqueda
    searchButton.addEventListener('click', function(e) {
        e.preventDefault();
        clearTimeout(searchTimeout);
        performSearch(searchInput.value.trim());
    });

    // Event listener para la tecla Enter
    searchInput.addEventListener('keypress', function(e) {
        if (e.key === 'Enter') {
            e.preventDefault();
            clearTimeout(searchTimeout);
            performSearch(this.value.trim());
        }
    });

    // Event listener para limpiar la búsqueda cuando se borra el input
    searchInput.addEventListener('keyup', function(e) {
        if (e.key === 'Escape') {
            this.value = '';
            searchResults.style.display = 'none';
            searchResults.innerHTML = '';
        }
    });

    // Cerrar resultados al hacer clic fuera
    document.addEventListener('click', function(e) {
        if (!searchInput.contains(e.target) && 
            !searchResults.contains(e.target) && 
            !searchButton.contains(e.target)) {
            searchResults.style.display = 'none';
        }
    });

    // Asegurarse de que el contenedor de resultados esté oculto inicialmente
    searchResults.style.display = 'none';
}); 