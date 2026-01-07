from flask import Blueprint, render_template, request, flash, redirect, url_for
from flask_login import login_required, current_user
from werkzeug.security import generate_password_hash
from app.extensions import db
from app.models import Project, User, AuditLog, Role
from app.decorators import require_perm
from app.services import log_activity
from datetime import datetime

admin_bp = Blueprint('admin', __name__)

# --- ניהול פרויקטים ---

@admin_bp.route('/projects')
@login_required
@require_perm('PROJECT_VIEW')
def projects_list():
    show_deleted = request.args.get('deleted') == 'true'
    query = Project.query
    if not show_deleted:
        query = query.filter_by(is_deleted=False)
    
    projects = query.all()
    users = User.query.filter_by(is_active=True).all()
    return render_template('admin/projects_list.html', projects=projects, users=users)

@admin_bp.route('/projects/save', methods=['POST'])
@login_required
@require_perm('PROJECT_EDIT')
def project_save():
    pid = request.form.get('id')
    name = request.form.get('name')
    
    if not name:
        flash('שם פרויקט חובה', 'danger')
        return redirect(url_for('admin.projects_list'))

    # שליפת הנתונים החדשים
    division = request.form.get('division')
    region = request.form.get('region')
    
    # טיפול בשדות ריקים (Empty String -> None)
    eng_id = request.form.get('engineer_id')
    eng_id = eng_id if eng_id else None
    
    pm_id = request.form.get('project_manager_id')
    pm_id = pm_id if pm_id else None

    if pid and pid != '': # Edit Mode
        project = Project.query.get_or_404(int(pid))
        project.name = name
        project.division = division
        project.region = region
        project.engineer_id = eng_id
        project.project_manager_id = pm_id
        
        flash('הפרויקט עודכן בהצלחה', 'success')
        log_activity('UPDATE', 'Project', project.id, {'name': name})
    else: # Create Mode
        project = Project(
            name=name,
            division=division,
            region=region,
            engineer_id=eng_id,
            project_manager_id=pm_id
        )
        db.session.add(project)
        # Commit קודם כדי לקבל ID ללוג
        db.session.commit()
        flash('פרויקט חדש נוצר', 'success')
        log_activity('CREATE', 'Project', project.id, {'name': name})
        
    db.session.commit()
    return redirect(url_for('admin.projects_list'))

@admin_bp.route('/projects/<int:id>/delete', methods=['POST'])
@login_required
@require_perm('PROJECT_DELETE')
def project_delete(id):
    project = Project.query.get_or_404(id)
    project.is_deleted = True
    project.deleted_at = datetime.now()
    project.deleted_by_id = current_user.id
    db.session.commit()
    log_activity('DELETE', 'Project', id)
    flash('הפרויקט נמחק (Soft Delete)', 'warning')
    return redirect(url_for('admin.projects_list'))

# --- ניהול משתמשים ---

@admin_bp.route('/users')
@login_required
def users_list():
    # רק אדמין יכול לראות משתמשים
    if current_user.role.name != 'Admin':
        flash('אין הרשאה', 'danger')
        return redirect(url_for('main.dashboard'))
        
    users = User.query.all()
    roles = Role.query.all()
    return render_template('admin/users.html', users=users, roles=roles)

@admin_bp.route('/users/save', methods=['POST'])
@login_required
def user_save():
    if current_user.role.name != 'Admin': return redirect(url_for('main.dashboard'))
    
    uid = request.form.get('id')
    email = request.form.get('email')
    full_name = request.form.get('full_name')
    role_id = request.form.get('role_id')
    password = request.form.get('password')
    
    if uid:
        # עריכה
        user = User.query.get_or_404(uid)
        user.email = email
        user.full_name = full_name
        user.role_id = role_id
        if password: # רק אם הוזנה סיסמה חדשה
            user.password = generate_password_hash(password)
        flash('משתמש עודכן', 'success')
    else:
        # יצירה
        if User.query.filter_by(email=email).first():
            flash('המייל כבר קיים', 'danger')
            return redirect(url_for('admin.users_list'))
            
        new_user = User(
            email=email,
            full_name=full_name,
            role_id=role_id,
            password=generate_password_hash(password),
            is_active=True
        )
        db.session.add(new_user)
        flash('משתמש נוצר', 'success')
        
    db.session.commit()
    return redirect(url_for('admin.users_list'))