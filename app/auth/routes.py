from flask import Blueprint, render_template, redirect, url_for, flash, request
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

        if not user or not check_password_hash(user.password, password):
            flash('פרטי ההתחברות שגויים. נסה שוב או צור חשבון חדש.', 'danger')
            return redirect(url_for('auth.login'))

        login_user(user, remember=remember)
        return redirect(url_for('main.index'))

    return render_template('auth/login.html')

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
        
    if request.method == 'POST':
        email = request.form.get('email')
        full_name = request.form.get('full_name')
        password = request.form.get('password')
        
        # בדיקה אם המשתמש קיים
        if User.query.filter_by(email=email).first():
            flash('כתובת האימייל הזו כבר רשומה במערכת.', 'warning')
            return redirect(url_for('auth.register'))
            
        # יצירת משתמש חדש (ברירת מחדל: מנהל פרויקט, כדי שיהיה לו מעניין)
        # אם אין תפקידים במערכת - ניצור אותם אוטומטית
        role = Role.query.filter_by(name='Project Manager').first()
        if not role:
            role = Role(name='Project Manager', description='Default User Role')
            db.session.add(role)
            
        new_user = User(
            email=email,
            full_name=full_name,
            password=generate_password_hash(password),
            role=role,
            is_active=True
        )
        
        db.session.add(new_user)
        db.session.commit()
        
        flash('החשבון נוצר בהצלחה! כעת ניתן להתחבר.', 'success')
        return redirect(url_for('auth.login'))

    return render_template('auth/register.html')

@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('התנתקת בהצלחה', 'info')
    return redirect(url_for('auth.login'))
