import logging
import sys
from flask import Flask, jsonify
from flask_wtf.csrf import CSRFProtect
from config import Config
from app.extensions import db, login_manager, migrate, limiter, csrf

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    # --- 1. הגדרת לוגים ל-STDOUT (כדי שנראה שגיאות ב-Render) ---
    if not app.debug:
        handler = logging.StreamHandler(sys.stdout)
        handler.setLevel(logging.INFO)
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        app.logger.addHandler(handler)
        app.logger.setLevel(logging.INFO)

    # --- אתחול תוספים ---
    db.init_app(app)
    login_manager.init_app(app)
    migrate.init_app(app, db)
    csrf.init_app(app)
    
    login_manager.login_view = 'auth.login'
    login_manager.login_message_category = 'info'

    # --- ייבוא מודלים ---
    with app.app_context():
        from app import models

    # --- 2. הפעלת מנגנון Bootstrap (יצירת טבלאות ואדמין) ---
    from app.utils import setup_database
    try:
        setup_database(app)
    except Exception as e:
        app.logger.error(f"Database setup failed: {e}")

    # --- 3. Health Check Endpoint ---
    @app.route('/health')
    def health_check():
        try:
            # בדיקה שה-DB חי
            db.session.execute(db.text('SELECT 1'))
            return jsonify({"status": "ok", "database": "connected"}), 200
        except Exception as e:
            app.logger.exception("Health check failed")
            return jsonify({"status": "error", "details": str(e)}), 500

    # --- 4. Error Handler ל-500 ---
    @app.errorhandler(500)
    def internal_error(error):
        app.logger.error(f"Server Error: {error}")
        return "Internal Server Error (Check Logs)", 500

    # --- רישום Blueprints ---
    from app.main.routes import main_bp
    from app.auth.routes import auth_bp
    from app.inquiries.routes import inquiries_bp
    from app.admin.routes import admin_bp

    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(inquiries_bp, url_prefix='/inquiries')
    app.register_blueprint(admin_bp, url_prefix='/admin')

    return app
