from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify, current_app, session, abort
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from app.models.user import User, Activity
from app import db
from datetime import datetime
from urllib.parse import urlparse
import os
import imghdr
from app.forms.auth_forms import LoginForm, RegistrationForm, ProfileForm, SecurityForm, NotificationForm, Enable2FAForm, Verify2FAForm, BackupCodeForm
import qrcode
import io
import base64

auth = Blueprint('auth', __name__)

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in {'png', 'jpg', 'jpeg', 'gif'}

def validate_image(stream):
    header = stream.read(512)
    stream.seek(0)
    format = imghdr.what(None, header)
    if not format:
        return None
    return '.' + format if format != 'jpeg' else '.jpg'

@auth.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))

    form = RegistrationForm()
    if form.validate_on_submit():
        if User.query.filter_by(username=form.username.data).first():
            flash('El nombre de usuario ya está en uso', 'danger')
            return redirect(url_for('auth.register'))
            
        if User.query.filter_by(email=form.email.data.lower()).first():
            flash('El correo electrónico ya está registrado', 'danger')
            return redirect(url_for('auth.register'))
        
        new_user = User(
            username=form.username.data,
            email=form.email.data.lower(),
            created_at=datetime.utcnow()
        )
        new_user.set_password(form.password.data)
        
        try:
            db.session.add(new_user)
            db.session.commit()
            flash('¡Registro exitoso! Ahora puedes iniciar sesión', 'success')
            return redirect(url_for('auth.login'))
        except Exception as e:
            db.session.rollback()
            flash('Ocurrió un error durante el registro. Por favor, intenta nuevamente.', 'danger')
            return redirect(url_for('auth.register'))
    
    return render_template('auth/register.html', title='Registro', form=form)

@auth.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        
        if user is None or not user.check_password(form.password.data):
            flash('Usuario o contraseña inválidos.', 'danger')
            return redirect(url_for('auth.login'))
        
        if user.is_account_locked():
            flash('Tu cuenta está temporalmente bloqueada. Por favor intenta más tarde.', 'danger')
            return redirect(url_for('auth.login'))
        
        # Verificar 2FA si está habilitado
        if user.two_factor_enabled and not session.get('2fa_verified'):
            session['user_id'] = user.id
            session['next'] = request.args.get('next')
            return redirect(url_for('auth.verify_2fa'))
        
        login_user(user, remember=form.remember_me.data)
        user.record_login_attempt(success=True)
        
        next_page = request.args.get('next')
        if not next_page or urlparse(next_page).netloc != '':
            next_page = url_for('main.index')
        return redirect(next_page)
    
    return render_template('auth/login.html', title='Iniciar Sesión', form=form)

@auth.route('/logout', methods=['GET', 'POST'])
@login_required
def logout():
    try:
        if request.method == 'POST':
            logout_user()
            flash('Has cerrado sesión exitosamente', 'success')
            return redirect(url_for('main.index'))
        return redirect(url_for('main.index'))
    except Exception as e:
        current_app.logger.error(f'Error durante el logout: {str(e)}')
        flash('Ocurrió un error al cerrar sesión. Por favor, intenta nuevamente.', 'danger')
        return redirect(url_for('main.index'))

@auth.route('/profile')
@login_required
def profile():
    activities = current_user.get_recent_activities()
    return render_template('auth/profile.html', 
                         title='Mi Perfil',
                         user=current_user,
                         activities=activities)

@auth.route('/settings', methods=['GET', 'POST'])
@login_required
def settings():
    profile_form = ProfileForm(
        original_username=current_user.username,
        original_email=current_user.email,
        obj=current_user
    )
    security_form = SecurityForm()
    notification_form = NotificationForm(obj=current_user)
    
    if request.method == 'POST':
        if 'profile_submit' in request.form and profile_form.validate_on_submit():
            current_user.username = profile_form.username.data
            current_user.email = profile_form.email.data
            current_user.bio = profile_form.bio.data
            
            if profile_form.avatar.data:
                file = profile_form.avatar.data
                if file and allowed_file(file.filename):
                    filename = secure_filename(file.filename)
                    file.save(os.path.join(current_app.config['UPLOAD_FOLDER'], filename))
                    current_user.avatar = filename
            
            db.session.commit()
            flash('Perfil actualizado exitosamente', 'success')
            return redirect(url_for('auth.settings'))
            
        elif 'security_submit' in request.form and security_form.validate_on_submit():
            if current_user.check_password(security_form.current_password.data):
                current_user.set_password(security_form.new_password.data)
                db.session.commit()
                flash('Contraseña actualizada exitosamente', 'success')
                return redirect(url_for('auth.settings'))
            else:
                flash('Contraseña actual incorrecta', 'danger')
                
        elif 'notification_submit' in request.form and notification_form.validate_on_submit():
            current_user.email_notifications = notification_form.email_notifications.data
            current_user.project_notifications = notification_form.project_updates.data
            db.session.commit()
            flash('Preferencias de notificación actualizadas', 'success')
            return redirect(url_for('auth.settings'))
    
    return render_template('auth/settings.html',
                         title='Configuración',
                         profile_form=profile_form,
                         security_form=security_form,
                         notification_form=notification_form)

@auth.route('/update_profile', methods=['POST'])
@login_required
def update_profile():
    if 'avatar' in request.files:
        file = request.files['avatar']
        if file and file.filename:
            file_ext = validate_image(file.stream)
            if file_ext is None:
                flash('Formato de imagen no válido', 'danger')
                return redirect(url_for('auth.settings'))
            
            if file.content_length and file.content_length > 5 * 1024 * 1024:  # 5MB
                flash('El archivo es demasiado grande. Máximo 5MB', 'danger')
                return redirect(url_for('auth.settings'))
            
            filename = secure_filename(f"{current_user.id}{file_ext}")
            file.save(os.path.join('app', 'static', 'uploads', 'avatars', filename))
            current_user.avatar = filename

    current_user.username = request.form.get('username', current_user.username)
    current_user.email = request.form.get('email', current_user.email).lower()
    current_user.bio = request.form.get('bio', current_user.bio)

    try:
        db.session.commit()
        flash('Perfil actualizado exitosamente', 'success')
    except Exception as e:
        db.session.rollback()
        flash('Error al actualizar el perfil', 'danger')

    return redirect(url_for('auth.settings'))

@auth.route('/change_password', methods=['POST'])
@login_required
def change_password():
    current_password = request.form.get('current_password')
    new_password = request.form.get('new_password')
    confirm_password = request.form.get('confirm_password')

    if not current_user.check_password(current_password):
        flash('Contraseña actual incorrecta', 'danger')
        return redirect(url_for('auth.settings'))

    if new_password != confirm_password:
        flash('Las contraseñas no coinciden', 'danger')
        return redirect(url_for('auth.settings'))

    current_user.set_password(new_password)
    db.session.commit()
    flash('Contraseña actualizada exitosamente', 'success')
    return redirect(url_for('auth.settings'))

@auth.route('/update_notifications', methods=['POST'])
@login_required
def update_notifications():
    current_user.email_notifications = request.form.get('email_notifications', False) == 'on'
    current_user.project_notifications = request.form.get('project_updates', False) == 'on'
    current_user.report_notifications = request.form.get('report_updates', False) == 'on'
    
    try:
        db.session.commit()
        flash('Preferencias de notificación actualizadas', 'success')
    except Exception as e:
        db.session.rollback()
        flash('Error al actualizar las preferencias', 'danger')
    
    return redirect(url_for('auth.settings'))

@auth.route('/update_appearance', methods=['POST'])
@login_required
def update_appearance():
    current_user.theme = request.form.get('theme', 'light')
    current_user.font_size = request.form.get('font_size', 'medium')
    
    try:
        db.session.commit()
        flash('Preferencias de apariencia actualizadas', 'success')
    except Exception as e:
        db.session.rollback()
        flash('Error al actualizar las preferencias', 'danger')
    
    return redirect(url_for('auth.settings'))

@auth.route('/update_theme', methods=['POST'])
@login_required
def update_theme():
    theme = request.form.get('theme', 'light')
    if theme not in ['light', 'dark']:
        return jsonify({'success': False, 'message': 'Tema no válido'}), 400
    
    try:
        current_user.theme = theme
        db.session.commit()
        return jsonify({'success': True, 'message': 'Tema actualizado correctamente'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': 'Error al actualizar el tema'}), 500

@auth.route('/check-username', methods=['POST'])
def check_username():
    username = request.json.get('username')
    user = User.query.filter_by(username=username).first()
    return jsonify({'available': user is None})

@auth.route('/check-email', methods=['POST'])
def check_email():
    email = request.json.get('email')
    user = User.query.filter_by(email=email.lower()).first()
    return jsonify({'available': user is None})

@auth.route('/setup_2fa', methods=['GET', 'POST'])
@login_required
def setup_2fa():
    if current_user.two_factor_enabled:
        flash('La autenticación de dos factores ya está activada.', 'info')
        return redirect(url_for('main.index'))
    
    form = Enable2FAForm()
    
    if form.validate_on_submit():
        if current_user.verify_2fa(form.code.data):
            current_user.two_factor_enabled = True
            db.session.commit()
            flash('¡La autenticación de dos factores ha sido activada!', 'success')
            return redirect(url_for('auth.setup_2fa_success'))
        flash('Código inválido. Por favor intenta de nuevo.', 'danger')
    
    # Generar código QR
    qr = qrcode.QRCode(version=1, box_size=10, border=5)
    qr.add_data(current_user.get_2fa_uri())
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")
    
    # Convertir imagen a base64
    buffered = io.BytesIO()
    img.save(buffered, format="PNG")
    qr_code = base64.b64encode(buffered.getvalue()).decode()
    
    return render_template('auth/setup_2fa.html',
                         form=form,
                         qr_code=f"data:image/png;base64,{qr_code}",
                         secret_key=current_user.two_factor_secret,
                         backup_codes=current_user.backup_codes)

@auth.route('/verify_2fa', methods=['GET', 'POST'])
def verify_2fa():
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
    
    user = User.query.get(session['user_id'])
    if not user:
        session.pop('user_id', None)
        return redirect(url_for('auth.login'))
    
    form = Verify2FAForm()
    
    if form.validate_on_submit():
        if user.verify_2fa(form.code.data):
            login_user(user)
            session.pop('user_id', None)
            
            if form.remember_device.data:
                session['2fa_verified'] = True
                session.permanent = True
            
            next_page = session.pop('next', None)
            return redirect(next_page or url_for('main.index'))
        
        flash('Código inválido. Por favor intenta de nuevo.', 'danger')
    
    return render_template('auth/verify_2fa.html', form=form)

@auth.route('/backup_code', methods=['GET', 'POST'])
def backup_code():
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
    
    user = User.query.get(session['user_id'])
    if not user:
        session.pop('user_id', None)
        return redirect(url_for('auth.login'))
    
    form = BackupCodeForm()
    
    if form.validate_on_submit():
        if user.verify_backup_code(form.code.data):
            login_user(user)
            session.pop('user_id', None)
            next_page = session.pop('next', None)
            return redirect(next_page or url_for('main.index'))
        
        flash('Código de respaldo inválido.', 'danger')
    
    return render_template('auth/backup_code.html', form=form)

@auth.route('/setup_2fa_success', methods=['GET'])
@login_required
def setup_2fa_success():
    return render_template('auth/setup_2fa_success.html') 