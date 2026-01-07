from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import check_password_hash
from models import User, db

auth_bp = Blueprint('auth', __name__, url_prefix='/auth')

# 👇👇👇 השורה הזאת חייבת להיראות בדיוק ככה! 👇👇👇
@auth_bp.route('/login', methods=['GET', 'POST']) 
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))
    
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        
        user = User.query.filter_by(email=email).first()
        
        if user and check_password_hash(user.password_hash, password):
            login_user(user)
            # הפניה לדף הבית אחרי התחברות
            return redirect(url_for('main.dashboard'))
        else:
            flash('שם משתמש או סיסמה שגויים', 'danger')
            
    return render_template('auth/login.html')

@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('התנתקת בהצלחה', 'info')
    return redirect(url_for('auth.login'))
