from app import create_app, db
from app.models import User
from werkzeug.security import generate_password_hash

app = create_app()

with app.app_context():
    # שליפת משתמש האדמין
    user = User.query.filter_by(email='admin@system.com').first()
    
    if user:
        # יצירת סיסמה חדשה ותקינה
        user.password = generate_password_hash('1234')
        db.session.commit()
        print("✅ הסיסמה אופסה בהצלחה ל: 1234")
    else:
        print("❌ משתמש אדמין לא נמצא במסד הנתונים")