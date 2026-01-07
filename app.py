import os
import io
import pandas as pd
from datetime import datetime
from functools import wraps
from urllib.parse import quote_plus
from werkzeug.utils import secure_filename
from werkzeug.security import generate_password_hash, check_password_hash

from flask import Flask, request, redirect, url_for, flash, render_template, send_from_directory, send_file, abort
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from flask_wtf.csrf import CSRFProtect
from sqlalchemy import text, inspect

# --- Config & Setup ---
app = Flask(__name__)

# Security Config
# במערכת אמיתית - יש לשים את זה ב-Environment Variables
db_pass = quote_plus(os.environ.get('DB_PASSWORD', 'Lk#180998'))
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'super_secret_key_change_me_in_prod')
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get(
    'DATABASE_URL', 
    f'mysql+pymysql://root:{db_pass}@localhost/pniot_system'
)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # Max upload 16MB

# Uploads Configuration
UPLOAD_FOLDER = os.path.join('static', 'uploads')
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'pdf', 'doc', 'docx'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

# Extensions
db = SQLAlchemy(app)
csrf = CSRFProtect(app) # הגנת CSRF לכל הטפסים
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'
login_manager.login_message = "אנא התחבר כדי לגשת לדף זה."
login_manager.login_message_category = "warning"

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# --- Models ---

class User(UserMixin, db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    full_name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(50), default='Project Manager') 
    is_active = db.Column(db.Boolean, default=True)

class Project(db.Model):
    __tablename__ = 'projects'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), nullable=False)
    division = db.Column(db.String(50), nullable=False)
    region = db.Column(db.String(100))
    engineer_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    
    # Soft Delete Support
    is_deleted = db.Column(db.Boolean, default=False)
    deleted_at = db.Column(db.DateTime, nullable=True)

    engineer = db.relationship('User', backref='projects')

class Customer(db.Model):
    __tablename__ = 'customers'
    id = db.Column(db.Integer, primary_key=True)
    full_name = db.Column(db.String(100), nullable=False)
    phone = db.Column(db.String(20), nullable=False)
    email = db.Column(db.String(100))
    address = db.Column(db.String(200))

class Inquiry(db.Model):
    __tablename__ = 'inquiries'
    id = db.Column(db.Integer, primary_key=True)
    customer_id = db.Column(db.Integer, db.ForeignKey('customers.id'))
    project_id = db.Column(db.Integer, db.ForeignKey('projects.id'))
    assigned_to_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True) # שיוך מטפל
    
    subject = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=False)
    status = db.Column(db.String(50), default='חדש')
    created_at = db.Column(db.DateTime, default=datetime.now)
    updated_at = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)
    image_filename = db.Column(db.String(255), nullable=True)
    
    customer = db.relationship('Customer', backref='inquiries')
    project = db.relationship('Project', backref='inquiries')
    assigned_to = db.relationship('User', foreign_keys=[assigned_to_id], backref='assigned_inquiries')

class InquiryComment(db.Model):
    __tablename__ = 'inquiry_comments'
    id = db.Column(db.Integer, primary_key=True)
    inquiry_id = db.Column(db.Integer, db.ForeignKey('inquiries.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True) # Null if system/public
    author_name = db.Column(db.String(100)) # Snapshot of name
    message = db.Column(db.Text, nullable=False)
    is_public = db.Column(db.Boolean, default=False) # Visible to customer?
    created_at = db.Column(db.DateTime, default=datetime.now)
    attachment_filename = db.Column(db.String(255), nullable=True)

    inquiry = db.relationship('Inquiry', backref=db.backref('comments', order_by=created_at.desc()))
    user = db.relationship('User')

# --- Helpers & Decorators ---

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or current_user.role != 'Admin':
            flash('אין לך הרשאות ניהול לביצוע פעולה זו.', 'danger')
            return redirect(url_for('dashboard'))
        return f(*args, **kwargs)
    return decorated_function

def check_db_schema():
    """Auto-migration helper for new fields"""
    with app.app_context():
        inspector = inspect(db.engine)
        
        # Check Project fields
        cols = [c['name'] for c in inspector.get_columns('projects')]
        if 'is_deleted' not in cols:
            print("Migrating: Adding is_deleted to projects")
            db.session.execute(text("ALTER TABLE projects ADD COLUMN is_deleted BOOLEAN DEFAULT 0"))
            db.session.execute(text("ALTER TABLE projects ADD COLUMN deleted_at DATETIME NULL"))
        
        # Check Inquiry fields
        cols = [c['name'] for c in inspector.get_columns('inquiries')]
        if 'assigned_to_id' not in cols:
            print("Migrating: Adding assigned_to_id to inquiries")
            db.session.execute(text("ALTER TABLE inquiries ADD COLUMN assigned_to_id INT NULL"))
            db.session.execute(text("ALTER TABLE inquiries ADD CONSTRAINT fk_inq_assign FOREIGN KEY (assigned_to_id) REFERENCES users(id)"))
        if 'updated_at' not in cols:
             db.session.execute(text("ALTER TABLE inquiries ADD COLUMN updated_at DATETIME DEFAULT NOW()"))

        db.session.commit()

# --- Routes ---

@app.route('/')
@login_required
def dashboard():
    # Admin Dashboard logic
    if current_user.role == 'Admin':
        status_counts = db.session.query(Inquiry.status, db.func.count(Inquiry.status)).group_by(Inquiry.status).all()
        chart_data = {
            'status_labels': [s[0] for s in status_counts],
            'status_counts': [s[1] for s in status_counts],
            'project_names': [], 'project_counts': [] # Simplified for brevity
        }
        
        # Active projects only
        active_projects_count = Project.query.filter_by(is_deleted=False).count()
        
        stats = {
            'users': User.query.count(),
            'projects': active_projects_count,
            'inquiries': Inquiry.query.count(),
            'open_inquiries': Inquiry.query.filter(Inquiry.status != 'טופל').count()
        }
        return render_template('dashboard_admin.html', stats=stats, chart_data=chart_data)

    elif current_user.role == 'Project Manager':
        # PM Logic
        my_projects = Project.query.filter_by(engineer_id=current_user.id, is_deleted=False).all()
        pm_data = []
        for p in my_projects:
            open_c = Inquiry.query.filter_by(project_id=p.id).filter(Inquiry.status != 'טופל').count()
            closed_c = Inquiry.query.filter_by(project_id=p.id, status='טופל').count()
            total = open_c + closed_c
            pm_data.append({
                'id': p.id, 'name': p.name, 'division': p.division,
                'open': open_c, 'closed': closed_c, 'percent': int((closed_c/total*100) if total else 0)
            })
        return render_template('dashboard_pm.html', pm_data=pm_data)

    elif current_user.role == 'Engineer':
        # Engineer sees assigned inquiries OR inquiries in their projects
        my_projects = Project.query.filter_by(engineer_id=current_user.id, is_deleted=False).all()
        p_ids = [p.id for p in my_projects]
        
        my_inquiries = Inquiry.query.filter(
            (Inquiry.assigned_to_id == current_user.id) | 
            (Inquiry.project_id.in_(p_ids))
        ).filter(Inquiry.status != 'טופל').all()
        
        return render_template('dashboard_engineer.html', projects=my_projects, inquiries=my_inquiries)

    return render_template('base.html')

# --- Auth ---
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        remember = True if request.form.get('remember') else False
        
        user = User.query.filter_by(email=email).first()
        if not user or not check_password_hash(user.password, password):
            flash('שם משתמש או סיסמה שגויים', 'danger')
            return redirect(url_for('login'))
            
        login_user(user, remember=remember)
        return redirect(url_for('dashboard'))
    return render_template('login.html')

@app.route('/register', methods=['POST'])
def register():
    # Basic registration logic
    email = request.form.get('email')
    password = request.form.get('password')
    full_name = request.form.get('full_name')
    
    if User.query.filter_by(email=email).first():
        flash('האימייל כבר קיים במערכת', 'warning')
        return redirect(url_for('login'))
        
    new_user = User(
        full_name=full_name, 
        email=email, 
        password=generate_password_hash(password),
        role='Project Manager'
    )
    db.session.add(new_user)
    db.session.commit()
    login_user(new_user)
    flash('נרשמת בהצלחה!', 'success')
    return redirect(url_for('dashboard'))

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

# --- Project CRUD ---

@app.route('/admin/projects')
@login_required
@admin_required
def manage_projects():
    # Only show non-deleted projects
    projects = Project.query.filter_by(is_deleted=False).all()
    # Users for the add/edit modal
    users = User.query.all()
    return render_template('admin_projects.html', projects=projects, users=users)

@app.route('/admin/projects/save', methods=['POST'])
@login_required
@admin_required
def save_project():
    project_id = request.form.get('project_id')
    name = request.form.get('name')
    division = request.form.get('division')
    region = request.form.get('region')
    engineer_id = request.form.get('engineer_id')

    if not name or not division:
        flash('שם פרויקט וחטיבה הם שדות חובה', 'danger')
        return redirect(url_for('manage_projects'))

    if project_id: # Edit
        project = Project.query.get_or_404(project_id)
        project.name = name
        project.division = division
        project.region = region
        project.engineer_id = engineer_id
        flash('הפרויקט עודכן בהצלחה', 'success')
    else: # New
        new_project = Project(
            name=name, division=division, region=region, engineer_id=engineer_id
        )
        db.session.add(new_project)
        flash('הפרויקט נוצר בהצלחה', 'success')

    db.session.commit()
    return redirect(url_for('manage_projects'))

@app.route('/admin/projects/delete/<int:project_id>', methods=['POST'])
@login_required
@admin_required
def delete_project(project_id):
    project = Project.query.get_or_404(project_id)
    # Soft delete
    project.is_deleted = True
    project.deleted_at = datetime.now()
    db.session.commit()
    flash(f'פרויקט "{project.name}" נמחק (Soft Delete)', 'warning')
    return redirect(url_for('manage_projects'))

@app.route('/admin/projects/<int:project_id>/edit')
@login_required
@admin_required
def edit_project_form(project_id):
    # This route is for the standalone edit page (Optional, as we use Modal usually, but good for direct links)
    project = Project.query.get_or_404(project_id)
    users = User.query.all()
    return render_template('project_form.html', project=project, users=users)

# --- Inquiry & Case Management ---

@app.route('/admin/inquiries')
@login_required
def all_inquiries():
    query = Inquiry.query
    
    # Filter by role
    if current_user.role == 'Project Manager':
        my_projs = Project.query.filter_by(engineer_id=current_user.id, is_deleted=False).with_entities(Project.id).all()
        p_ids = [p.id for p in my_projs]
        query = query.filter(Inquiry.project_id.in_(p_ids))
    elif current_user.role == 'Engineer':
        query = query.filter(Inquiry.assigned_to_id == current_user.id)
    
    # Filter by URL params (search/filter)
    status_filter = request.args.get('status')
    if status_filter:
        query = query.filter_by(status=status_filter)

    inquiries = query.order_by(Inquiry.updated_at.desc()).all()
    return render_template('admin_inquiries.html', inquiries=inquiries)

@app.route('/inquiries/<int:inq_id>')
@login_required
def inquiry_detail(inq_id):
    # Access control
    inquiry = Inquiry.query.get_or_404(inq_id)
    
    # Check permissions (Simplified)
    if current_user.role != 'Admin':
        # Logic: If PM, must own project. If Eng, must be assigned or own project.
        is_my_project = (inquiry.project.engineer_id == current_user.id)
        is_assigned = (inquiry.assigned_to_id == current_user.id)
        if not (is_my_project or is_assigned):
            flash('אין לך הרשאה לצפות בפנייה זו', 'danger')
            return redirect(url_for('dashboard'))

    users = User.query.filter_by(is_active=True).all()
    return render_template('inquiry_detail.html', inquiry=inquiry, users=users)

@app.route('/inquiries/<int:inq_id>/update', methods=['POST'])
@login_required
def inquiry_update(inq_id):
    inquiry = Inquiry.query.get_or_404(inq_id)
    
    # Update Status/Assignee
    new_status = request.form.get('status')
    assigned_to = request.form.get('assigned_to_id')
    
    if new_status: inquiry.status = new_status
    if assigned_to: inquiry.assigned_to_id = assigned_to
    
    # Add Comment
    message_text = request.form.get('message')
    if message_text:
        is_public = True if request.form.get('is_public') else False
        filename = None
        if 'attachment' in request.files:
            file = request.files['attachment']
            if file and allowed_file(file.filename):
                filename = secure_filename(f"{datetime.now().strftime('%Y%m%d%H%M')}_{file.filename}")
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        
        comment = InquiryComment(
            inquiry_id=inq_id,
            user_id=current_user.id,
            author_name=current_user.full_name,
            message=message_text,
            is_public=is_public,
            attachment_filename=filename
        )
        db.session.add(comment)
    
    inquiry.updated_at = datetime.now()
    db.session.commit()
    flash('הפנייה עודכנה בהצלחה', 'success')
    return redirect(url_for('inquiry_detail', inq_id=inq_id))

# --- Public & Misc ---

@app.route('/report', methods=['GET', 'POST'])
def report():
    # Public route - No login required (CSRF enabled)
    projects = Project.query.filter_by(is_deleted=False).all()
    
    if request.method == 'POST':
        # Handle Public Form Logic (Same as before but safer)
        full_name = request.form.get('full_name')
        phone = request.form.get('phone')
        
        cust = Customer.query.filter_by(phone=phone).first()
        if not cust:
            cust = Customer(full_name=full_name, phone=phone, email=request.form.get('email'))
            db.session.add(cust)
            db.session.commit()
            
        filename = None
        if 'image' in request.files:
            file = request.files['image']
            if file and allowed_file(file.filename):
                filename = secure_filename(f"PUB_{datetime.now().strftime('%Y%m%d')}_{file.filename}")
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        
        inq = Inquiry(
            customer_id=cust.id,
            project_id=request.form.get('project_id'),
            subject=request.form.get('subject'),
            description=request.form.get('description'),
            image_filename=filename
        )
        db.session.add(inq)
        db.session.commit()
        flash('הדיווח התקבל בהצלחה! תודה.', 'success')
        return redirect(url_for('report'))

    return render_template('public_report.html', projects=projects)

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

@app.route('/admin/export_excel')
@login_required
@admin_required
def export_excel():
    results = db.session.query(
        Inquiry.id, Inquiry.created_at, Inquiry.status, Inquiry.subject,
        Customer.full_name.label('Customer'), Project.name.label('Project')
    ).join(Customer).join(Project).all()
    
    df = pd.DataFrame([{
        'ID': r.id, 'Date': r.created_at, 'Status': r.status, 
        'Subject': r.subject, 'Customer': r.Customer, 'Project': r.Project
    } for r in results])
    
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False)
    output.seek(0)
    
    return send_file(
        output,
        mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        as_attachment=True,
        download_name=f'report_{datetime.now().strftime("%Y%m%d")}.xlsx'
    )

# --- Initialization ---
if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        check_db_schema() # Run auto-migration
        
        # Create Admin if not exists
        if not User.query.filter_by(email='admin@system.com').first():
            hashed = generate_password_hash('1234')
            db.session.add(User(full_name='מנהל', email='admin@system.com', password=hashed, role='Admin'))
            db.session.commit()
            
    app.run(debug=True)