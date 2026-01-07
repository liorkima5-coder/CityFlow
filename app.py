from flask import Flask, redirect, url_for
from flask_migrate import Migrate
from flask_login import LoginManager
from models import db, User # וודא ש-models.py קיים ומוגדר נכון
import os
import logging

# הגדרת לוגים כדי שנראה מה קורה ב-Render
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def create_app():
    app = Flask(__name__)

    # --- הגדרות ---
    # ב-Render המשתנה DATABASE_URL נכנס אוטומטית אם הגדרת דאטה בייס
    # אם לא, הוא משתמש ב-sqlite מקומי
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev_key_12345')
    app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:///cityflow.db')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    # --- אתחול תוספים ---
    db.init_app(app) # מחבר את ה-DB לאפליקציה
    migrate = Migrate(app, db)
    
    login_manager = LoginManager()
    login_manager.login_view = 'auth.login'
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    # --- הקסם קורה כאן: שימוש ב-app_context ---
    with app.app_context():
        # 1. רישום ה-Blueprints
        try:
            from auth.routes import auth_bp
            app.register_blueprint(auth_bp)
            
            # אם יש לך עוד Blueprints, הסר את ההערה:
            # from main.routes import main_bp
            # app.register_blueprint(main_bp)
            
        except ImportError as e:
            logger.warning(f"⚠️ Could not register routes: {e}")

        # 2. יצירת הטבלאות
        try:
            db.create_all()
        except Exception as e:
            logger.error(f"❌ Error creating tables: {e}")

        # 3. הרצת Seed (מילוי ראשוני)
        # הבדיקה נעשית בתוך הקונטקסט כדי למנוע את השגיאה שקיבלת
        try:
            if not User.query.first():
                logger.info("🌱 Database empty. Starting seed...")
                from seed_data import seed
                seed() # הפונקציה הזו חייבת להשתמש ב-db שכבר אותחל
                logger.info("✅ Seed finished successfully.")
        except ImportError:
            logger.warning("⚠️ seed_data.py not found, skipping seed.")
        except Exception as e:
            logger.error(f"❌ Error during seed: {e}")

    # --- נתיב ראשי ---
    @app.route('/')
    def index():
        return redirect(url_for('auth.login'))

    return app

# יצירת המופע של האפליקציה ש-Gunicorn מחפש
app = create_app()

if __name__ == '__main__':
    app.run(debug=True, port=5000)
