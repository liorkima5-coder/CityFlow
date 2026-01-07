from datetime import datetime
from flask_login import UserMixin
from sqlalchemy.dialects.mysql import JSON
from app.extensions import db

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# --- RBAC Models ---
roles_permissions = db.Table('roles_permissions',
    db.Column('role_id', db.Integer, db.ForeignKey('roles.id')),
    db.Column('permission_id', db.Integer, db.ForeignKey('permissions.id'))
)

class Permission(db.Model):
    __tablename__ = 'permissions'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True)

class Role(db.Model):
    __tablename__ = 'roles'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True)
    permissions = db.relationship('Permission', secondary=roles_permissions, backref='roles')

# --- Core Models ---
class User(UserMixin, db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    full_name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    is_active = db.Column(db.Boolean, default=True)
    
    role_id = db.Column(db.Integer, db.ForeignKey('roles.id'), nullable=True)
    role = db.relationship('Role', backref='users')

    def has_perm(self, perm_name):
        if not self.role: return False
        return any(p.name == perm_name for p in self.role.permissions)

class Project(db.Model):
    __tablename__ = 'projects'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), nullable=False)
    division = db.Column(db.String(50), nullable=False)
    region = db.Column(db.String(100))
    
    # שני אחראים: מהנדס ומנהל פרויקט
    engineer_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    project_manager_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    
    # Audit & Soft Delete
    created_at = db.Column(db.DateTime, default=datetime.now)
    is_deleted = db.Column(db.Boolean, default=False)
    deleted_at = db.Column(db.DateTime, nullable=True)
    deleted_by_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)

    # Relationships (עם שמות ייחודיים כדי למנוע התנגשות)
    engineer = db.relationship('User', foreign_keys=[engineer_id], backref='engineered_projects')
    project_manager = db.relationship('User', foreign_keys=[project_manager_id], backref='managed_projects')

class Customer(db.Model):
    __tablename__ = 'customers'
    id = db.Column(db.Integer, primary_key=True)
    full_name = db.Column(db.String(100), nullable=False)
    phone = db.Column(db.String(20), nullable=False)
    email = db.Column(db.String(100))

class Inquiry(db.Model):
    __tablename__ = 'inquiries'
    id = db.Column(db.Integer, primary_key=True)
    customer_id = db.Column(db.Integer, db.ForeignKey('customers.id'))
    project_id = db.Column(db.Integer, db.ForeignKey('projects.id'))
    assigned_to_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    
    subject = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=False)
    status = db.Column(db.String(50), default='New') 
    priority = db.Column(db.String(20), default='Normal')
    
    created_at = db.Column(db.DateTime, default=datetime.now)
    updated_at = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)
    last_activity_at = db.Column(db.DateTime, default=datetime.now)
    closed_at = db.Column(db.DateTime, nullable=True)
    image_filename = db.Column(db.String(255), nullable=True)
    
    customer = db.relationship('Customer', backref='inquiries')
    project = db.relationship('Project', backref='inquiries')
    assigned_to = db.relationship('User', foreign_keys=[assigned_to_id], backref='assigned_inquiries')

class InquiryMessage(db.Model):
    __tablename__ = 'inquiry_messages'
    id = db.Column(db.Integer, primary_key=True)
    inquiry_id = db.Column(db.Integer, db.ForeignKey('inquiries.id'))
    author_user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    author_type = db.Column(db.String(20)) 
    body = db.Column(db.Text)
    is_public = db.Column(db.Boolean, default=False)
    attachment_filename = db.Column(db.String(255), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.now)

    inquiry = db.relationship('Inquiry', backref=db.backref('messages', order_by=created_at.asc()))
    author = db.relationship('User')

class AuditLog(db.Model):
    __tablename__ = 'audit_logs'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    action = db.Column(db.String(50)) 
    entity_type = db.Column(db.String(50)) 
    entity_id = db.Column(db.Integer, nullable=True)
    meta_json = db.Column(JSON, nullable=True)
    ip_address = db.Column(db.String(50))
    created_at = db.Column(db.DateTime, default=datetime.now)
    

    user = db.relationship('User')
