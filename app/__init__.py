from flask import Flask
from flask_login import LoginManager
from flask_migrate import Migrate
from flask_wtf.csrf import CSRFProtect # וודא שזה קיים
from config import Config
from app.extensions import db, login_manager, migrate, limiter, csrf

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    # --- אתחול תוספים ---
    db.init_app(app)
    login_manager.init_app(app)
    migrate.init_app(app, db)
    csrf.init_app(app)  # חשוב מאוד לטפסים!
    # limiter.init_app(app) # אופציונלי

    login_manager.login_view = 'auth.login'
    login_manager.login_message_category = 'info'

    # --- יצירת טבלאות אוטומטית (התיקון) ---
    with app.app_context():
        # מייבאים את המודלים כדי שה-DB יכיר אותם
        from app import models
        # יוצרים את הטבלאות פיזית אם הן לא קיימות
        db.create_all()

    # --- רישום ה-Blueprints ---
    from app.main.routes import main_bp
    from app.auth.routes import auth_bp
    from app.inquiries.routes import inquiries_bp
    from app.admin.routes import admin_bp

    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(inquiries_bp, url_prefix='/inquiries')
    app.register_blueprint(admin_bp, url_prefix='/admin')

    return app
