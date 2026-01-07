from app import db
from models import User, Role, Project, Inquiry # וודא שהשמות תואמים למודלים שלך
from werkzeug.security import generate_password_hash
from datetime import datetime

def seed_database():
    """Function to seed the database with initial data."""
    
    print("🌱 Starting database seed...")

    # 1. יצירת תפקידים (Roles)
    admin_role = Role.query.filter_by(name='Admin').first()
    if not admin_role:
        admin_role = Role(name='Admin', description='Administrator with full access')
        db.session.add(admin_role)
        print("   + Created Role: Admin")

    user_role = Role.query.filter_by(name='Employee').first()
    if not user_role:
        user_role = Role(name='Employee', description='Standard user with limited access')
        db.session.add(user_role)
        print("   + Created Role: Employee")
    
    db.session.commit()

    # 2. יצירת משתמש אדמין (Admin User)
    admin_user = User.query.filter_by(email='admin@cityflow.local').first()
    if not admin_user:
        admin_user = User(
            full_name='מנהל מערכת',
            email='admin@cityflow.local',
            password_hash=generate_password_hash('123456', method='pbkdf2:sha256'),
            role_id=admin_role.id,
            is_active=True
        )
        db.session.add(admin_user)
        print("   + Created Admin User: admin@cityflow.local (Pass: 123456)")

    # 3. יצירת פרויקט לדוגמה (Sample Project)
    # הערה: עטוף ב-try/except למקרה שהמודל Project עדיין לא קיים או שונה
    try:
        sample_project = Project.query.filter_by(name='שיפוץ מרכז העיר').first()
        if not sample_project:
            sample_project = Project(
                name='שיפוץ מרכז העיר',
                description='פרויקט התחדשות עירונית ברחוב יפו',
                start_date=datetime.utcnow(),
                status='In Progress',
                manager_id=admin_user.id
            )
            db.session.add(sample_project)
            print("   + Created Sample Project")
    except Exception as e:
        print(f"   ! Skipped Project seed: {e}")

    # 4. יצירת פנייה לדוגמה (Sample Inquiry)
    try:
        sample_inquiry = Inquiry.query.first()
        if not sample_inquiry and admin_user:
            sample_inquiry = Inquiry(
                title='בור בכביש',
                description='יש בור גדול בכניסה לחניון העירייה',
                status='Open',
                priority='High',
                created_at=datetime.utcnow(),
                user_id=admin_user.id
            )
            db.session.add(sample_inquiry)
            print("   + Created Sample Inquiry")
    except Exception as e:
        print(f"   ! Skipped Inquiry seed: {e}")

    db.session.commit()
    print("✅ Database seeded successfully!")
