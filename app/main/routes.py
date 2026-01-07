from flask import Blueprint, render_template
from flask_login import login_required, current_user
from app.extensions import db
from app.models import User, Role
from werkzeug.security import generate_password_hash

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def index():
    if current_user.is_authenticated:
        return render_template('index.html')
    return render_template('auth/login.html')

@main_bp.route('/fix-login')
def fix_login():
    try:
        # 1. יצירת תפקיד Admin אם לא קיים
        admin_role = Role.query.filter_by(name='Admin').first()
        if not admin_role:
            admin_role = Role(name='Admin', description='Administrator')
            db.session.add(admin_role)
            db.session.commit()
        
        # 2. יצירת משתמש Admin אם לא קיים
        user = User.query.filter_by(email='admin@system.com').first()
        if not user:
            user = User(
                email='admin@system.com',
                password=generate_password_hash('1234'),
                full_name='Admin User',
                role=admin_role,
                is_active=True
            )
            db.session.add(user)
            db.session.commit()
            return "✅ הצלחה! המשתמש admin@system.com נוצר (סיסמה: 1234). <a href='/auth/login'>לחץ כאן להתחברות</a>"
        
        return "⚠️ המשתמש כבר קיים במערכת."

    except Exception as e:
        return f"❌ שגיאה: {str(e)}"
