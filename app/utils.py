import logging
from werkzeug.security import generate_password_hash
from app.extensions import db
from app.models import User, Role
import os

def setup_database(app):
    """
    פונקציה שמבצעת אתחול למסד הנתונים:
    1. יצירת טבלאות
    2. יצירת תפקידים (Roles)
    3. יצירת משתמש אדמין מתוך משתני סביבה
    """
    with app.app_context():
        # 1. יצירת טבלאות
        db.create_all()
        
        # 2. יצירת תפקידים (Roles) - חובה כדי למנוע קריסות בהרשמה
        roles_to_create = ['Admin', 'Project Manager', 'Engineer']
        for role_name in roles_to_create:
            if not Role.query.filter_by(name=role_name).first():
                new_role = Role(name=role_name, description=f'{role_name} Role')
                db.session.add(new_role)
        
        db.session.commit()
        
        # 3. יצירת/עדכון אדמין (Idempotent)
        admin_email = os.environ.get('ADMIN_EMAIL')
        admin_password = os.environ.get('ADMIN_PASSWORD')
        
        if admin_email and admin_password:
            admin_role = Role.query.filter_by(name='Admin').first()
            admin_user = User.query.filter_by(email=admin_email).first()
            
            hashed_pw = generate_password_hash(admin_password)
            
            if not admin_user:
                # יצירת אדמין חדש
                admin_user = User(
                    email=admin_email,
                    password=hashed_pw,
                    full_name='System Admin',
                    role=admin_role,
                    is_active=True
                )
                db.session.add(admin_user)
                app.logger.info(f"Admin user {admin_email} created.")
            else:
                # וידוא שהאדמין הקיים מקבל הרשאות וסיסמה מעודכנת
                admin_user.role = admin_role
                admin_user.password = hashed_pw
                admin_user.is_active = True
                app.logger.info(f"Admin user {admin_email} updated.")
            
            db.session.commit()
        else:
            app.logger.warning("No ADMIN_EMAIL/PASSWORD configured. Admin bootstrap skipped.")
