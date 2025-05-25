# Sistema de Gestión de Proyectos y Reportes

## Descripción
Sistema web para la gestión de proyectos y reportes, desarrollado con Flask.

## Requisitos
- Python 3.11.7
- PostgreSQL (producción)
- Redis (producción)

## Instalación

1. Clonar el repositorio:
```bash
git clone <url-del-repositorio>
cd <nombre-del-proyecto>
```

2. Crear un entorno virtual:
```bash
python -m venv venv
```

3. Activar el entorno virtual:
- Windows:
```bash
venv\Scripts\activate
```
- Linux/Mac:
```bash
source venv/bin/activate
```

4. Instalar dependencias:
```bash
pip install -r requirements.txt
```

5. Configurar variables de entorno:
Crear un archivo `.env` en la raíz del proyecto con las siguientes variables:
```
FLASK_APP=run.py
FLASK_ENV=production
SECRET_KEY=tu-clave-secreta
DATABASE_URL=tu-url-de-base-de-datos
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USE_TLS=True
MAIL_USERNAME=tu-email
MAIL_PASSWORD=tu-contraseña
MAIL_DEFAULT_SENDER=tu-email
```

6. Inicializar la base de datos:
```bash
flask db upgrade
```

## Despliegue en Producción

### Heroku
1. Crear una aplicación en Heroku
2. Configurar las variables de entorno en Heroku
3. Agregar los add-ons necesarios:
   - Heroku Postgres
   - Heroku Redis
4. Desplegar:
```bash
git push heroku main
```

### VPS/Servidor Dedicado
1. Instalar dependencias del sistema:
```bash
sudo apt-get update
sudo apt-get install python3-pip python3-dev nginx
```

2. Configurar Gunicorn:
```bash
gunicorn -w 4 run:app
```

3. Configurar Nginx:
```nginx
server {
    listen 80;
    server_name tu-dominio.com;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

## Mantenimiento

### Respaldo de Base de Datos
```bash
pg_dump -U usuario nombre_db > backup.sql
```

### Actualización
1. Activar entorno virtual
2. Actualizar dependencias:
```bash
pip install -r requirements.txt --upgrade
```
3. Aplicar migraciones:
```bash
flask db upgrade
```

## Seguridad
- Todas las contraseñas se almacenan hasheadas
- CSRF protection habilitado
- Rate limiting configurado
- Sesiones seguras con SSL
- Validación de entrada en todos los formularios

## Soporte
Para soporte, contactar a: tu-email@dominio.com 