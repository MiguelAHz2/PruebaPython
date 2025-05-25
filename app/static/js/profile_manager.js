class ProfileManager {
    constructor() {
        this.setupEventListeners();
    }

    setupEventListeners() {
        // Validación en tiempo real del nombre de usuario
        const usernameInput = document.querySelector('input[name="username"]');
        if (usernameInput) {
            usernameInput.addEventListener('change', this.checkUsername.bind(this));
        }

        // Validación en tiempo real del email
        const emailInput = document.querySelector('input[name="email"]');
        if (emailInput) {
            emailInput.addEventListener('change', this.checkEmail.bind(this));
        }

        // Vista previa de la imagen de avatar
        const avatarInput = document.querySelector('input[name="avatar"]');
        if (avatarInput) {
            avatarInput.addEventListener('change', this.previewAvatar.bind(this));
        }

        // Aplicar tema en tiempo real
        const themeSelect = document.querySelector('select[name="theme"]');
        if (themeSelect) {
            themeSelect.addEventListener('change', this.applyTheme.bind(this));
        }

        // Aplicar tamaño de fuente en tiempo real
        const fontSizeSelect = document.querySelector('select[name="font_size"]');
        if (fontSizeSelect) {
            fontSizeSelect.addEventListener('change', this.applyFontSize.bind(this));
        }
    }

    async checkUsername(event) {
        const username = event.target.value;
        const response = await fetch('/check-username', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Accept': 'application/json'
            },
            body: JSON.stringify({ username })
        });
        
        const data = await response.json();
        const feedback = event.target.nextElementSibling;
        
        if (!data.available) {
            event.target.classList.add('is-invalid');
            if (!feedback) {
                const div = document.createElement('div');
                div.className = 'invalid-feedback';
                div.textContent = 'Este nombre de usuario ya está en uso';
                event.target.parentNode.appendChild(div);
            }
        } else {
            event.target.classList.remove('is-invalid');
            if (feedback) {
                feedback.remove();
            }
        }
    }

    async checkEmail(event) {
        const email = event.target.value;
        const response = await fetch('/check-email', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Accept': 'application/json'
            },
            body: JSON.stringify({ email })
        });
        
        const data = await response.json();
        const feedback = event.target.nextElementSibling;
        
        if (!data.available) {
            event.target.classList.add('is-invalid');
            if (!feedback) {
                const div = document.createElement('div');
                div.className = 'invalid-feedback';
                div.textContent = 'Este email ya está registrado';
                event.target.parentNode.appendChild(div);
            }
        } else {
            event.target.classList.remove('is-invalid');
            if (feedback) {
                feedback.remove();
            }
        }
    }

    previewAvatar(event) {
        const file = event.target.files[0];
        if (file) {
            if (file.size > 5 * 1024 * 1024) {  // 5MB
                alert('El archivo es demasiado grande. Máximo 5MB.');
                event.target.value = '';
                return;
            }

            const reader = new FileReader();
            reader.onload = (e) => {
                const preview = document.querySelector('img.rounded-circle');
                if (preview) {
                    preview.src = e.target.result;
                }
            };
            reader.readAsDataURL(file);
        }
    }

    applyTheme(event) {
        const theme = event.target.value;
        document.body.dataset.bsTheme = theme;
        localStorage.setItem('theme', theme);
    }

    applyFontSize(event) {
        const fontSize = event.target.value;
        const sizes = {
            'small': '14px',
            'medium': '16px',
            'large': '18px'
        };
        document.body.style.fontSize = sizes[fontSize];
        localStorage.setItem('fontSize', fontSize);
    }
}

// Inicializar el manejador cuando el DOM esté listo
document.addEventListener('DOMContentLoaded', () => {
    window.profileManager = new ProfileManager();
    
    // Aplicar preferencias guardadas
    const savedTheme = localStorage.getItem('theme');
    if (savedTheme) {
        document.body.dataset.bsTheme = savedTheme;
    }
    
    const savedFontSize = localStorage.getItem('fontSize');
    if (savedFontSize) {
        const sizes = {
            'small': '14px',
            'medium': '16px',
            'large': '18px'
        };
        document.body.style.fontSize = sizes[savedFontSize];
    }
}); 