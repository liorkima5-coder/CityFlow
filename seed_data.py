from app import db
from models import User, Role, Project, Inquiry
from werkzeug.security import generate_password_hash
from datetime import datetime

def seed_database():
    print("🌱 Starting database seed...")

    # 1. יצירת תפקידים
    admin_role = Role.query.filter_by(name='Admin').first()
    if not admin_role:
        admin_role = Role(name='Admin', description='Administrator')
        db.session.add(admin_role)
    
    user_role = Role.query.filter_by(name='Employee').first()
    if not user_role:
        user_role = Role(name='Employee', description='User')
        db.session.add(user_role)
    
    db.session.commit()

    # 2. יצירת משתמש אדמין (קריטי לכניסה ראשונית)
    if not User.query.filter_by(email='admin@cityflow.local').first():
        admin_user = User(
            full_name='מנהל מערכת',
            email='admin@cityflow.local',
            password_hash=generate_password_hash('123456', method='pbkdf2:sha256'),
            role_id=admin_role.id,
            is_active=True
        )
        db.session.add(admin_user)
        print("   + Created Admin: admin@cityflow.local (Pass: 123456)")

    # 3. יצירת פנייה לדוגמה (כדי שהדשבורד לא יהיה ריק)
    if admin_role: 
        # מוודאים שיש משתמש לקשר אליו
        user = User.query.filter_by(email='admin@cityflow.local').first()
        if user and not Inquiry.query.first():
            inquiry = Inquiry(
                title='מפגע בטיחותי בגן סאקר',
                description='ספסל שבור עם מסמרים בולטים',
                status='Open',
                priority='High',
                created_at=datetime.utcnow(),
                user_id=user.id
            )
            db.session.add(inquiry)
            print("   + Created sample inquiry")

    db.session.commit()
    print("✅ Seed completed successfully!")
