import os

class Config:
    # אבטחה בסיסית
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-key-change-in-prod'
    
    # הגדרת מסד נתונים - תמיכה ב-Postgres של Render
    database_url = os.environ.get('DATABASE_URL')
    if database_url and database_url.startswith("postgres://"):
        database_url = database_url.replace("postgres://", "postgresql://", 1)
    
    SQLALCHEMY_DATABASE_URI = database_url or 'sqlite:///site.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # הגדרות נוספות
    WTF_CSRF_ENABLED = True
