from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from app.extensions import db
# שים לב: אנחנו רק מייבאים מפה, לא מגדירים מחדש class
from app.models import Inquiry, ChatMessage, Project, User
from datetime import datetime

inquiries_bp = Blueprint('inquiries', __name__)

@inquiries_bp.route('/')
@login_required
def list_inquiries():
    if current_user.role.name == 'Admin':
        inquiries = Inquiry.query.all()
    elif current_user.role.name == 'Project Manager':
        inquiries = Inquiry.query.join(Project).filter(Project.manager_id == current_user.id).all()
    else:
        inquiries = Inquiry.query.filter_by(user_id=current_user.id).all()
    return render_template('inquiries/list.html', inquiries=inquiries)

@inquiries_bp.route('/new', methods=['GET', 'POST'])
@login_required
def new_inquiry():
    if request.method == 'POST':
        title = request.form.get('title')
        description = request.form.get('description')
        project_id = request.form.get('project_id')
        priority = request.form.get('priority')
        
        new_inquiry = Inquiry(
            title=title,
            description=description,
            project_id=project_id,
            priority=priority,
            user_id=current_user.id
        )
        db.session.add(new_inquiry)
        db.session.commit()
        flash('הפנייה נפתחה בהצלחה', 'success')
        return redirect(url_for('inquiries.list_inquiries'))
        
    projects = Project.query.all()
    return render_template('inquiries/new.html', projects=projects)

@inquiries_bp.route('/<int:id>', methods=['GET', 'POST'])
@login_required
def view_inquiry(id):
    inquiry = Inquiry.query.get_or_404(id)
    
    if request.method == 'POST':
        content = request.form.get('content')
        if content:
            msg = ChatMessage(
                content=content,
                inquiry_id=inquiry.id,
                user_id=current_user.id,
                created_at=datetime.utcnow()
            )
            db.session.add(msg)
            db.session.commit()
            flash('ההודעה נוספה', 'success')
            return redirect(url_for('inquiries.view_inquiry', id=id))

    return render_template('inquiries/view.html', inquiry=inquiry)
