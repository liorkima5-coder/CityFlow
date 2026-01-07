from flask import Flask, render_template, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_migrate import Migrate
import os

# 1. יצירת האפליקציה והגדרות
app = Flask(__name__)

# הגדרות אבטחה ודאטה בייס
app.config['SECRET_KEY'] = 'dev_secret_key_123'  # בפרודקשן לשנות למשהו חזק
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///cityflow.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# 2. אתחול התוספים
db = SQLAlchemy(app)
migrate = Migrate(app, db)
login_manager = LoginManager(app)
login_manager.login_view = 'auth.login'  # שם הפונקציה שאליה מפנים אם לא מחוברים
login_manager.login_message = 'נא להתחבר כדי לצפות בעמוד זה.'
login_manager.login_message_category = 'info'

# 3. ייבוא המודלים
# הערה: חייבים לייבא את המודלים כאן כדי ש-SQLAlchemy יכיר אותם לפני יצירת הטבלאות
# וודא שקובץ models.py קיים ושיש בו את המחלקות: User, Role, Project, Inquiry
try:
    from models import User, Role, Project, Inquiry
except ImportError:
    print("❌ Error: models.py not found or missing classes.")

# 4. הגדרת טעינת משתמש (User Loader) עבור Flask-Login
@login_manager.user_loader
def load_user(user_id):
    if user_id is not None:
        return User.query.get(int(user_id))
    return None

# 5. רישום Blueprints (הנתיבים של האתר)
# מבוסס על הקישורים שיש לך ב-HTML (main, auth, inquiries, admin)
# אם הקבצים האלו עדיין לא קיימים אצלך, שים את השורות האלו בהערה (#) זמנית
try:
    from routes.main import main_bp
    from routes.auth import auth_bp
    from routes.inquiries import inquiries_bp
    from routes.admin import admin_bp

    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(inquiries_bp)
    app.register_blueprint(admin_bp)
except ImportError as e:
    print(f"⚠️ Warning: Some routes could not be imported. Check your 'routes' folder. Error: {e}")

# ראוט בסיסי למקרה שה-Blueprint לא עובד, כדי שהאתר יעלה
@app.route('/')
def index():
    # אם יש Blueprint 'main', נפנה אליו, אחרת נציג הודעה
    try:
        return redirect(url_for('main.dashboard'))
    except:
        return "CityFlow System is Running! (Please configure routes)"

# 6. יצירת הדאטה בייס והרצת Seed (החלק שקרס לך מקודם)
with app.app_context():
    # יוצר את הקובץ cityflow.db ואת כל הטבלאות
    db.create_all()

    # בדיקה: אם אין משתמשים בכלל, נריץ את ה-Seed
    # שים לב: זה דורש שיהיה לך קובץ seed_data.py באותה תיקייה
    try:
        if not User.query.first():
            print("⚠️ Database is empty. Starting seed process...")
            try:
                from seed_data import seed_database
                seed_database()
            except ImportError:
                print("❌ Error: 'seed_data.py' file is missing.")
            except Exception as e:
                print(f"❌ Error during seeding: {e}")
    except Exception as db_err:
        print(f"⚠️ Database check failed (might be first run): {db_err}")

# 7. הרצת האפליקציה
if __name__ == '__main__':
    app.run(debug=True, port=5000)
