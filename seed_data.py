from models import db, User, Role, Inquiry
from werkzeug.security import generate_password_hash
from datetime import datetime

def seed():
    print("🌱 Starting Seed Process...")
    
    # יצירת תפקידים
    if not Role.query.first():
        admin_role = Role(name='Admin', description='Administrator')
        user_role = Role(name='Employee', description='User')
        db.session.add_all([admin_role, user_role])
        db.session.commit()
        print("   + Roles created")

    # יצירת אדמין
    if not User.query.filter_by(email='admin@cityflow.local').first():
        admin_role = Role.query.filter_by(name='Admin').first()
        admin_user = User(
            full_name='מנהל מערכת',
            email='admin@cityflow.local',
            password_hash=generate_password_hash('123456', method='pbkdf2:sha256'),
            role_id=admin_role.id,
            is_active=True
        )
        db.session.add(admin_user)
        db.session.commit()
        print("   + Admin created: admin@cityflow.local / 123456")

    print("✅ Seed Finished.")
