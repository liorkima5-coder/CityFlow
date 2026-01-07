from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from config import Config  # <--- ייבוא הקובץ החדש

# אתחול התוספים
db = SQLAlchemy()
login_manager = LoginManager()

def create_app(config_class=Config): # <--- שימוש ב-Config כברירת מחדל
    app = Flask(__name__)
    
    # טעינת ההגדרות מהקובץ שיצרנו
    app.config.from_object(config_class)

    db.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'
    login_manager.login_message_category = 'info'

    # רישום ה-Blueprints (החלקים של האתר)
    from app.main.routes import main_bp
    from app.auth.routes import auth_bp
    from app.inquiries.routes import inquiries_bp
    from app.admin.routes import admin_bp

    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(inquiries_bp, url_prefix='/inquiries')
    app.register_blueprint(admin_bp, url_prefix='/admin')

    return app