from app import create_app, db
from app.models import Role, Permission, User
from werkzeug.security import generate_password_hash

app = create_app()

def init_rbac():
    """סקריפט אתחול הרשאות ומשתמשים"""
    with app.app_context():
        db.create_all()
        
        # 1. יצירת תפקידים והרשאות (אם לא קיימים)
        if not Role.query.first():
            print("Creating Roles & Permissions...")
            # Permissions
            perms = {
                'PROJECT_VIEW': Permission(name='PROJECT_VIEW'),
                'PROJECT_EDIT': Permission(name='PROJECT_EDIT'),
                'PROJECT_DELETE': Permission(name='PROJECT_DELETE'),
            }
            for p in perms.values(): db.session.add(p)
            db.session.commit()
            
            # Roles
            admin_role = Role(name='Admin')
            admin_role.permissions = list(perms.values())
            
            pm_role = Role(name='Project Manager')
            pm_role.permissions = [perms['PROJECT_VIEW'], perms['PROJECT_EDIT']]
            
            eng_role = Role(name='Engineer')
            eng_role.permissions = [perms['PROJECT_VIEW']]
            
            db.session.add_all([admin_role, pm_role, eng_role])
            db.session.commit()
            print("Roles created.")

        # 2. יצירת משתמש אדמין (החלק שהיה חסר)
        if not User.query.filter_by(email='admin@system.com').first():
            print("Creating Admin User...")
            admin_role = Role.query.filter_by(name='Admin').first()
            admin_user = User(
                full_name='מנהל מערכת',
                email='admin@system.com',
                password=generate_password_hash('1234'),
                role=admin_role, # שיוך לתפקיד אדמין
                is_active=True
            )
            db.session.add(admin_user)
            db.session.commit()
            print("✅ Admin user created: admin@system.com / 1234")

if __name__ == '__main__':
    init_rbac()
    app.run(debug=True)