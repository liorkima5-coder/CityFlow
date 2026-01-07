from flask import Blueprint, render_template, redirect, url_for, flash, request, current_app
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import check_password_hash
from models import User

# הגדרת ה-Blueprint
auth_bp = Blueprint('auth', __name__, url_prefix='/auth')

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    # לוג לאבחון
    if request.method == 'POST':
        current_app.logger.info(f"🔐 Login attempt via POST to {request.path}")

    if current_user.is_authenticated:
        # כאן צריך להיות הנתיב לדשבורד שלך (למשל 'main.dashboard')
        # כרגע נשאיר הודעה אם אין main
        try:
            return redirect(url_for('main.dashboard'))
        except:
            return "Login Successful! (Please define main.dashboard route)"

    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        
        user = User.query.filter_by(email=email).first()
        
        if user and check_password_hash(user.password_hash, password):
            login_user(user)
            next_page = request.args.get('next')
            # וודא שה-next page בטוח או ברירת מחדל
            try:
                return redirect(next_page or url_for('main.dashboard'))
            except:
                return "Login Successful! (User authenticated)"
        else:
            flash('שם משתמש או סיסמה שגויים', 'danger')
            
    return render_template('auth/login.html')

@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('התנתקת בהצלחה', 'info')
    return redirect(url_for('auth.login'))
