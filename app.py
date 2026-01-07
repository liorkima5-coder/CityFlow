from flask import Flask, redirect, url_for
from flask_migrate import Migrate
from flask_login import LoginManager
from models import db, User # וודא ש-models.py קיים בתיקייה הראשית
import os

def create_app():
    app = Flask(__name__)

    # הגדרות
    app.config['SECRET_KEY'] = 'dev_key_12345'
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///cityflow.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    # אתחול תוספים
    db.init_app(app)
    migrate = Migrate(app, db)
    
    login_manager = LoginManager()
    login_manager.login_view = 'auth.login'
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    # --- רישום ה-Blueprints (החלק ששונה) ---
    with app.app_context():
        try:
            # ייבוא מהמבנה: auth/routes.py
            from auth.routes import auth_bp
            app.register_blueprint(auth_bp)
            
            # הנחתי שגם השאר באותו מבנה (למשל main/routes.py), אם לא - תעדכן אותי
            # כרגע שמתי בהערה כדי שלא יקרוס לך אם הם לא קיימים
            
            # from main.routes import main_bp
            # app.register_blueprint(main_bp)
            
            # from inquiries.routes import inquiries_bp
            # app.register_blueprint(inquiries_bp)

        except ImportError as e:
            print(f"⚠️ Warning: Could not register routes: {e}")

        # יצירת טבלאות + Seed
        db.create_all()
        
        # הרצת Seed אם אין משתמשים
        if not User.query.first():
            print("⚠️ Database empty. Running seed...")
            try:
                import seed_data
                seed_data.seed_database()
            except ImportError:
                print("❌ seed_data.py not found")
            except Exception as e:
                print(f"❌ Seed error: {e}")

    @app.route('/')
    def index():
        # אם ה-main blueprint עדיין לא קיים, נפנה זמנית ל-login
        return redirect(url_for('auth.login'))

    return app

app = create_app()

if __name__ == '__main__':
    app.run(debug=True, port=5000)
