from flask import Flask
from flask_login import LoginManager
from flask_migrate import Migrate
from config import Config

# אנו מניחים ש-db ו-limiter מוגדרים ב-extensions.py
# אם אין לך limiter, אתה יכול למחוק את הייבוא שלו
from app.extensions import db, login_manager, migrate, limiter

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    # --- אתחול התוספים ---
    db.init_app(app)
    login_manager.init_app(app)
    migrate.init_app(app, db)
    
    # אם אתה משתמש ב-Limiter (הגבלת בקשות), תוריד את ההערה:
    # limiter.init_app(app)

    # --- הגדרות התחברות ---
    login_manager.login_view = 'auth.login'
    login_manager.login_message_category = 'info'

    # --- תיקון קריטי: טעינת המודלים ---
    # השורה הזו קריטית! היא גורמת ל-Flask לקרוא את models.py
    # ולרשום את הפונקציה @login_manager.user_loader
    with app.app_context():
        from app import models

    # --- רישום ה-Blueprints (החלקים של האתר) ---
    from app.main.routes import main_bp
    from app.auth.routes import auth_bp
    from app.inquiries.routes import inquiries_bp
    from app.admin.routes import admin_bp

    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(inquiries_bp, url_prefix='/inquiries')
    app.register_blueprint(admin_bp, url_prefix='/admin')

    return app
