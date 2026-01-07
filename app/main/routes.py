from app import db
from app.models import User, Role
from werkzeug.security import generate_password_hash
from flask import Blueprint, render_template
from flask_login import login_required, current_user
from sqlalchemy import func
from app.models import Inquiry, Project

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
@login_required
def dashboard():
    # 1. שליפת הפרויקטים הרלוונטיים למשתמש
    if current_user.role.name == 'Admin':
        my_projects = Project.query.filter_by(is_deleted=False).all()
        base_query = Inquiry.query # אדמין רואה הכל
    elif current_user.role.name == 'Project Manager':
        my_projects = Project.query.filter_by(project_manager_id=current_user.id, is_deleted=False).all()
        # PM רואה פניות של הפרויקטים שלו
        p_ids = [p.id for p in my_projects]
        base_query = Inquiry.query.filter(Inquiry.project_id.in_(p_ids))
    else: # Engineer
        # מהנדס רואה פרויקטים שהוא אחראי עליהם או פניות ששויכו אליו ישירות
        my_projects = Project.query.filter_by(engineer_id=current_user.id, is_deleted=False).all()
        p_ids = [p.id for p in my_projects]
        base_query = Inquiry.query.filter(
            (Inquiry.project_id.in_(p_ids)) | (Inquiry.assigned_to_id == current_user.id)
        )

    # 2. חישוב סטטיסטיקות (KPIs)
    stats = {
        'total': base_query.count(),
        'new': base_query.filter_by(status='New').count(),
        'progress': base_query.filter_by(status='In Progress').count(),
        'closed': base_query.filter_by(status='Closed').count()
    }
    
    # 3. פניות אחרונות
    recent_inquiries = base_query.order_by(Inquiry.created_at.desc()).limit(5).all()

    @main_bp.route('/fix-login')
def fix_login():
    try:
        # 1. יצירת תפקיד Admin אם לא קיים
        admin_role = Role.query.filter_by(name='Admin').first()
        if not admin_role:
            admin_role = Role(name='Admin', description='Administrator')
            db.session.add(admin_role)
            db.session.commit()
            print("Role Created")

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
            return "✅ הצלחה! המשתמש admin@system.com נוצר. <a href='/auth/login'>לחץ כאן להתחברות</a>"
        
        return "⚠️ המשתמש כבר קיים במערכת. נסה לאפס סיסמה או בדוק את הלוגים."

    except Exception as e:
        return f"❌ שגיאה: {str(e)}"


    return render_template('dashboard.html', stats=stats, recent_inquiries=recent_inquiries, projects=my_projects)

