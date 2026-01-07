from flask import Flask, redirect, url_for, request
from flask_migrate import Migrate
from flask_login import LoginManager
from models import db, User
import logging # הוספנו לוגים
import os

def create_app():
    app = Flask(__name__)

    # --- הגדרות ---
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev_key_12345')
    app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:///cityflow.db')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    # --- לוגים לאבחון (Debugger) ---
    # זה ידפיס ללוג ב-Render כל בקשה שנכנסת
    logging.basicConfig(level=logging.INFO)
    
    @app.before_request
    def log_request_info():
        # נרשום רק בקשות POST או בקשות ל-login כדי לא להציף את הלוג
        if request.method == 'POST' or 'login' in request.path:
            app.logger.info(f"🔍 REQUEST: {request.method} {request.path}")
            if request.method == 'POST':
                # מדפיס את השדות שנשלחו (ללא ערכים רגישים)
                app.logger.info(f"📦 FORM DATA KEYS: {list(request.form.keys())}")

    # --- אתחול תוספים ---
    db.init_app(app)
    migrate = Migrate(app, db)
    
    login_manager = LoginManager()
    login_manager.login_view = 'auth.login'
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    # --- רישום Blueprints ---
    with app.app_context():
        try:
            from auth.routes import auth_bp
            # url_prefix='/auth' מבטיח שהנתיב יהיה /auth/login
            app.register_blueprint(auth_bp) 
            
            # כאן תוסיף את שאר ה-Blueprints שלך (main, inquiries וכו')
            # from main.routes import main_bp
            # app.register_blueprint(main_bp)

        except ImportError as e:
            app.logger.error(f"⚠️ Error importing routes: {e}")

        db.create_all()
        
        # Seed (אופציונלי, רק אם צריך)
        if not User.query.first():
            try:
                from seed_data import seed
                seed()
            except Exception as e:
                app.logger.error(f"❌ Seed error: {e}")

    # --- נתיב ראשי ---
    @app.route('/')
    def index():
        # מפנה תמיד ללוגין של ה-Blueprint
        return redirect(url_for('auth.login'))

    return app

app = create_app()

if __name__ == '__main__':
    app.run(debug=True, port=5000)
