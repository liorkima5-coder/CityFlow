from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from app.extensions import db
from app.models import User, Role

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))
        
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        user = User.query.filter_by(email=email).first()
        
        if user and check_password_hash(user.password, password):
            login_user(user)
            return redirect(url_for('main.dashboard'))
        
        flash('שם משתמש או סיסמה שגויים', 'danger')
        
    return render_template('auth/login.html')

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))

    if request.method == 'POST':
        email = request.form.get('email')
        full_name = request.form.get('full_name')
        password = request.form.get('password')
        
        if User.query.filter_by(email=email).first():
            flash('האימייל הזה כבר קיים במערכת', 'warning')
            return redirect(url_for('auth.register'))
        
        # אבטחה: כל נרשם חדש הוא אוטומטית Engineer (מזהה 3)
        # האדמין יוכל לשנות זאת מאוחר יותר במסך ניהול משתמשים
        default_role_id = 3 
            
        new_user = User(
            full_name=full_name,
            email=email,
            password=generate_password_hash(password),
            role_id=default_role_id,
            is_active=True
        )
        db.session.add(new_user)
        db.session.commit()
        
        login_user(new_user)
        flash(f'נרשמת בהצלחה! חשבונך נוצר כמהנדס. ברוך הבא {full_name}.', 'success')
        return redirect(url_for('main.dashboard'))

    return render_template('auth/register.html')

@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('התנתקת בהצלחה', 'info')
    return redirect(url_for('auth.login'))