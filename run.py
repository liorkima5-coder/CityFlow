from app import create_app, db
from app.models import User

app = create_app()

# --- חלק אוטומטי לשרת (Render) ---
# בכל פעם שהאפליקציה עולה, אנחנו בודקים את מצב ה-DB
with app.app_context():
    try:
        # 1. יצירת טבלאות אם הן לא קיימות
        db.create_all()
        
        # 2. בדיקה: האם המערכת ריקה? (אם אין משתמשים)
        if not User.query.first():
            print("⚠️ Database is empty. Starting seed process...")
            
            # ייבוא והרצה של פונקציית המילוי מקובץ ה-seed
            # שים לב: אנחנו מניחים שב-seed_data.py יש פונקציה בשם seed()
            from seed_data import seed
            seed()
            
            print("✅ Seed data created successfully!")
        else:
            print("✅ Database is ready and contains data.")
            
    except Exception as e:
        print(f"❌ Error during startup sequence: {e}")

# --- הרצה במחשב המקומי ---
if __name__ == '__main__':
    app.run(debug=True)
