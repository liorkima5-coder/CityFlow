from flask import Flask, redirect, url_for
from flask_migrate import Migrate
from flask_login import LoginManager
from models import db, User
import os

# --- 1. יצירת המשתנה app באופן גלובלי (זה מה ש-Gunicorn מחפש) ---
app = Flask(__name__)

# --- 2. הגדרות ---
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev_key_12345')
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:///cityflow.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# --- 3. חיבור הדאטה-בייס ---
db.init_app(app)
migrate = Migrate(app, db)
login_manager = LoginManager(app)
login_manager.login_view = 'auth.login'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# --- 4. הגדרת ה-Context (בשביל Seed ו-Blueprints) ---
with app.app_context():
    # רישום נתיבים
    try:
        from auth.routes import auth_bp
        app.register_blueprint(auth_bp)
    except ImportError as e:
        print(f"⚠️ Error importing auth blueprint: {e}")

    # יצירת טבלאות
    try:
        db.create_all()
    except Exception as e:
        print(f"❌ DB Create Error: {e}")
    
    # הרצת Seed (בדיקה אם הטבלה ריקה)
    try:
        if not User.query.first():
            print("🌱 Database empty. Running seed...")
            from seed_data import seed
            seed()
            print("✅ Seed finished.")
    except Exception as e:
        print(f"⚠️ Seed skipped or failed: {e}")

# --- 5. נתיב ראשי ---
@app.route('/')
def index():
    return redirect(url_for('auth.login'))

# --- 6. הרצה לוקאלית (לא משפיע על Render) ---
if __name__ == '__main__':
    app.run(debug=True, port=5000)
