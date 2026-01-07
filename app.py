from flask import Flask, redirect, url_for
from flask_migrate import Migrate
from flask_login import LoginManager
from models import db, User 
import os

app = Flask(__name__)

# --- הגדרות ---
app.config['SECRET_KEY'] = 'dev_key_12345'
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:///cityflow.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# --- חיבורים (קריטי לסדר) ---
db.init_app(app)  # 1. מחברים את ה-DB לאפליקציה
migrate = Migrate(app, db)
login_manager = LoginManager(app)
login_manager.login_view = 'auth.login'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# --- הרצה בתוך הקשר (Context) ---
with app.app_context():
    # רישום נתיבים
    try:
        from auth.routes import auth_bp
        app.register_blueprint(auth_bp)
    except ImportError as e:
        print(f"Error importing auth: {e}")

    # יצירת טבלאות + Seed
    db.create_all()
    
    # בדיקה והרצה של Seed
    try:
        if not User.query.first():
            from seed_data import seed
            seed() # עכשיו זה יעבוד כי ה-Context פעיל
    except Exception as e:
        print(f"Seed Error: {e}")

@app.route('/')
def index():
    return redirect(url_for('auth.login'))

if __name__ == '__main__':
    app.run(debug=True, port=5000)
