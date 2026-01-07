from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import check_password_hash
from app.models import User

auth_bp = Blueprint('auth', __name__)

# --- התיקון הקריטי: הוספת methods=['GET', 'POST'] ---
@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    # אם המשתמש כבר מחובר, זרוק אותו לדף הבית
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))

    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        remember = True if request.form.get('remember') else False

        user = User.query.filter_by(email=email).first()

        # בדיקת סיסמה (Hash)
        if not user or not check_password_hash(user.password, password):
            flash('פרטי ההתחברות שגויים. נסה שוב.', 'danger')
            return redirect(url_for('auth.login'))

        # התחברות מוצלחת
        login_user(user, remember=remember)
        return redirect(url_for('main.index'))

    return render_template('auth/login.html')

@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('התנתקת בהצלחה', 'info')
    return redirect(url_for('auth.login'))
