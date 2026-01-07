import random
from faker import Faker
from app import create_app, db
from app.models import User, Project, Customer, Inquiry, Role, Permission, InquiryMessage
from werkzeug.security import generate_password_hash

app = create_app()
fake = Faker('he_IL') # נתונים בעברית

def seed():
    with app.app_context():
        print("🗑️ מוחק נתונים ישנים...")
        db.drop_all()
        db.create_all()

        print("👮 יוצר תפקידים והרשאות...")
        # Roles Setup (כמו ב-run.py)
        perms = {
            'PROJECT_VIEW': Permission(name='PROJECT_VIEW'),
            'PROJECT_EDIT': Permission(name='PROJECT_EDIT'),
            'PROJECT_DELETE': Permission(name='PROJECT_DELETE'),
        }
        for p in perms.values(): db.session.add(p)
        db.session.commit()
        
        admin_role = Role(name='Admin', permissions=list(perms.values()))
        pm_role = Role(name='Project Manager', permissions=[perms['PROJECT_VIEW'], perms['PROJECT_EDIT']])
        eng_role = Role(name='Engineer', permissions=[perms['PROJECT_VIEW']])
        db.session.add_all([admin_role, pm_role, eng_role])
        db.session.commit()

        print("👥 יוצר משתמשים...")
        # Admin
        db.session.add(User(full_name='מנהל מערכת', email='admin@system.com', password=generate_password_hash('1234'), role=admin_role))
        
        # 5 PMs
        pms = []
        for i in range(5):
            u = User(full_name=fake.name(), email=f'pm{i}@system.com', password=generate_password_hash('1234'), role=pm_role)
            db.session.add(u)
            pms.append(u)
        
        # 10 Engineers
        engineers = []
        for i in range(10):
            u = User(full_name=fake.name(), email=f'eng{i}@system.com', password=generate_password_hash('1234'), role=eng_role)
            db.session.add(u)
            engineers.append(u)
        
        db.session.commit()

        print("🏗️ יוצר פרויקטים...")
        projects = []
        divisions = ['תשתיות', 'רכבות', 'אורבני', 'חינוך', 'פארקים']
        for i in range(20):
            p = Project(
                name=f"פרויקט {fake.street_name()}",
                division=random.choice(divisions),
                region=fake.city(),
                project_manager_id=random.choice(pms).id,
                engineer_id=random.choice(engineers).id
            )
            db.session.add(p)
            projects.append(p)
        db.session.commit()

        print("📞 יוצר לקוחות ופניות (500)...")
        customers = []
        for _ in range(100):
            c = Customer(full_name=fake.name(), phone=fake.phone_number(), email=fake.email())
            db.session.add(c)
            customers.append(c)
        db.session.commit()

        for _ in range(500):
            status = random.choice(['New', 'In Progress', 'In Progress', 'Closed'])
            priority = random.choice(['Low', 'Normal', 'Normal', 'High'])
            
            inq = Inquiry(
                customer_id=random.choice(customers).id,
                project_id=random.choice(projects).id,
                assigned_to_id=random.choice(engineers).id if status != 'New' else None,
                subject=fake.sentence(nb_words=6),
                description=fake.paragraph(),
                status=status,
                priority=priority,
                created_at=fake.date_time_this_year()
            )
            db.session.add(inq)
            
            # הוספת היסטוריית תגובות אקראית
            if status != 'New':
                for _ in range(random.randint(1, 5)):
                    msg = InquiryMessage(
                        inquiry=inq,
                        author_user_id=inq.assigned_to_id,
                        author_type='staff',
                        body=fake.sentence(),
                        is_public=random.choice([True, False]),
                        created_at=fake.date_time_between(start_date=inq.created_at)
                    )
                    db.session.add(msg)

        db.session.commit()
        print("✅ סיימנו! המערכת מוכנה עם נתונים.")

if __name__ == '__main__':
    seed()