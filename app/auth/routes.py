from flask import Blueprint, render_template, redirect, url_for, flash, request, current_app
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import check_password_hash, generate_password_hash
from app.extensions import db
from app.models import User, Role

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))

    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        remember = True if request.form.get('remember') else False

        user = User.query.filter_by(email=email).first()

        # בדיקה קפדנית
        if not user or not check_password_hash(user.password, password):
            flash('פרטי ההתחברות שגויים.', 'danger')
            return redirect(url_for('auth.login'))

        login_user(user, remember=remember)
        return redirect(url_for('main.index'))

    return render_template('auth/login.html')

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
        
    if request.method == 'POST':
        try:
            email = request.form.get('email')
            full_name = request.form.get('full_name')
            password = request.form.get('password')
            
            if User.query.filter_by(email=email).first():
                flash('האימייל כבר קיים במערכת.', 'warning')
                return redirect(url_for('auth.register'))
                
            # שליפת תפקיד ברירת מחדל
            default_role = Role.query.filter_by(name='Project Manager').first()
            
            # Fail-safe: אם איכשהו התפקיד לא קיים, ניצור אותו ידנית
            if not default_role:
                current_app.logger.warning("Default role not found during register, creating fallback.")
                default_role = Role(name='Project Manager', description='Fallback Role')
                db.session.add(default_role)

            new_user = User(
                email=email,
                full_name=full_name,
                password=generate_password_hash(password),
                role=default_role,
                is_active=True
            )
            
            db.session.add(new_user)
            db.session.commit()
            
            flash('החשבון נוצר בהצלחה! נא להתחבר.', 'success')
            return redirect(url_for('auth.login'))
            
        except Exception as e:
            db.session.rollback()
            current_app.logger.exception("Error during registration")
            flash('שגיאה ביצירת החשבון. נסה שנית מאוחר יותר.', 'danger')
            return redirect(url_for('auth.register'))

    return render_template('auth/register.html')

@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('התנתקת בהצלחה', 'info')
    return redirect(url_for('auth.login'))
