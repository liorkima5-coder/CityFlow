import os

# קובע את הנתיב הראשי של הפרויקט כדי שנדע איפה לשמור את קובץ ה-DB
basedir = os.path.abspath(os.path.dirname(__file__))

class Config:
    # מפתח אבטחה: לוקח מהסביבה או משתמש בברירת מחדל חזקה
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'cityflow-secret-key-2024'
    
    # הגדרת מסד הנתונים (SQLite)
    # זה יוצר קובץ בשם cityflow.db בתיקייה הראשית
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'sqlite:///' + os.path.join(basedir, 'cityflow.db')
    
    # ביטול מעקב אחרי שינויים (חוסך זיכרון)
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # הגדרות נוספות (אופציונלי - להעלאת קבצים אם תצטרך בעתיד)
    UPLOAD_FOLDER = os.path.join(basedir, 'app', 'static', 'uploads')
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # מקסימום 16MB לקובץ