from app import create_app, db
from app.models import User, Role

app = create_app()

with app.app_context():
    # 1. מציאת המשתמש לפי האימייל
    email_to_fix = 'admin@system.com'
    user = User.query.filter_by(email=email_to_fix).first()
    
    # 2. וידוא שתפקיד האדמין קיים (מזהה 1)
    admin_role = Role.query.filter_by(name='Admin').first()
    
    if user and admin_role:
        print(f"🔄 נמצא המשתמש: {user.full_name} עם תפקיד נוכחי: {user.role.name if user.role else 'ללא'}")
        
        # שינוי התפקיד לאדמין
        user.role_id = admin_role.id
        db.session.commit()
        
        print(f"✅ בוצע! המשתמש {email_to_fix} שודרג בחזרה ל-Admin.")
    else:
        print(f"❌ שגיאה: המשתמש {email_to_fix} או תפקיד Admin לא נמצאו.")