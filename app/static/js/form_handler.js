document.addEventListener('DOMContentLoaded', function() {
    // Obtener el token CSRF del meta tag
    const csrfToken = document.querySelector('meta[name="csrf-token"]').getAttribute('content');

    // Configurar el token CSRF para todas las peticiones AJAX
    function setupAjaxCSRF() {
        $.ajaxSetup({
            beforeSend: function(xhr, settings) {
                if (!/^(GET|HEAD|OPTIONS|TRACE)$/i.test(settings.type) && !this.crossDomain) {
                    xhr.setRequestHeader("X-CSRFToken", csrfToken);
                }
            }
        });
    }

    // Manejar todos los formularios
    function setupFormHandlers() {
        document.querySelectorAll('form').forEach(form => {
            // Asegurarse de que el formulario tenga el token CSRF
            if (!form.querySelector('input[name="csrf_token"]')) {
                const csrfInput = document.createElement('input');
                csrfInput.type = 'hidden';
                csrfInput.name = 'csrf_token';
                csrfInput.value = csrfToken;
                form.appendChild(csrfInput);
            }

            // Prevenir doble envío
            form.addEventListener('submit', function(e) {
                if (form.classList.contains('submitting')) {
                    e.preventDefault();
                    return;
                }

                form.classList.add('submitting');
                
                // Deshabilitar el botón de envío
                const submitButton = form.querySelector('button[type="submit"], input[type="submit"]');
                if (submitButton) {
                    submitButton.disabled = true;
                    
                    // Guardar el texto original
                    const originalText = submitButton.innerHTML;
                    submitButton.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Enviando...';

                    // Restaurar el botón después de un tiempo
                    setTimeout(() => {
                        form.classList.remove('submitting');
                        submitButton.disabled = false;
                        submitButton.innerHTML = originalText;
                    }, 5000);
                }
            });
        });
    }

    // Manejar errores de formulario
    function setupFormErrors() {
        document.querySelectorAll('.invalid-feedback').forEach(feedback => {
            const input = feedback.previousElementSibling;
            if (input) {
                input.classList.add('is-invalid');
            }
        });
    }

    // Inicializar
    setupAjaxCSRF();
    setupFormHandlers();
    setupFormErrors();

    // Reconfigurar cuando se cargue contenido dinámicamente
    document.addEventListener('htmx:afterSwap', function() {
        setupFormHandlers();
        setupFormErrors();
    });
}); 