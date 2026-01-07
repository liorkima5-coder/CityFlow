from flask import Blueprint, render_template, request, flash, redirect, url_for
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
from app.extensions import db
from app.models import Inquiry, InquiryMessage, Project, User
from app.services import log_activity, check_sla_status
from datetime import datetime
import os

inquiries_bp = Blueprint('inquiries', __name__)

@inquiries_bp.route('/')
@login_required
def list_inquiries():
    # Advanced Filtering
    query = Inquiry.query
    status = request.args.get('status')
    if status: query = query.filter_by(status=status)
    
    # Priority Filter
    priority = request.args.get('priority')
    if priority: query = query.filter_by(priority=priority)

    # RBAC Filtering (Simplified)
    if current_user.role.name == 'Engineer':
        query = query.filter(Inquiry.assigned_to_id == current_user.id)
        
    inquiries = query.order_by(Inquiry.updated_at.desc()).all()
    
    # Enrich with SLA
    for i in inquiries:
        i.sla_status = check_sla_status(i)
        
    return render_template('inquiries/list.html', inquiries=inquiries)

@inquiries_bp.route('/<int:id>')
@login_required
def detail(id):
    inquiry = Inquiry.query.get_or_404(id)
    users = User.query.filter_by(is_active=True).all()
    return render_template('inquiries/detail.html', inquiry=inquiry, users=users)

@inquiries_bp.route('/<int:id>/message', methods=['POST'])
@login_required
def add_message(id):
    inquiry = Inquiry.query.get_or_404(id)
    body = request.form.get('body')
    is_public = request.form.get('is_public') == 'on'
    
    # File Upload
    filename = None
    if 'attachment' in request.files:
        file = request.files['attachment']
        if file.filename:
            filename = secure_filename(f"{datetime.now().timestamp()}_{file.filename}")
            file.save(os.path.join('app/static/uploads', filename))

    msg = InquiryMessage(
        inquiry_id=id,
        author_user_id=current_user.id,
        author_type='staff',
        body=body,
        is_public=is_public,
        attachment_filename=filename
    )
    
    # Update Inquiry Metadata
    inquiry.last_activity_at = datetime.now()
    if request.form.get('status'):
        inquiry.status = request.form.get('status')
    
    db.session.add(msg)
    db.session.commit()
    
    log_activity('REPLY', 'Inquiry', id, {'public': is_public})
    flash('תגובה נוספה', 'success')
    return redirect(url_for('inquiries.detail', id=id))

@inquiries_bp.route('/<int:id>/update_meta', methods=['POST'])
@login_required
def update_meta(id):
    inquiry = Inquiry.query.get_or_404(id)
    inquiry.status = request.form.get('status')
    inquiry.priority = request.form.get('priority')
    inquiry.assigned_to_id = request.form.get('assigned_to_id') or None
    
    if inquiry.status == 'Closed' and not inquiry.closed_at:
        inquiry.closed_at = datetime.now()
        
    db.session.commit()
    log_activity('UPDATE_META', 'Inquiry', id)
    flash('פרטי פנייה עודכנו', 'success')
    return redirect(url_for('inquiries.detail', id=id))

from app.models import Customer, Project # וודא שיש את הייבוא הזה למעלה

@inquiries_bp.route('/new', methods=['GET', 'POST'])
@login_required
def new_inquiry():
    if request.method == 'POST':
        full_name = request.form.get('full_name')
        phone = request.form.get('phone')
        
        # איתור או יצירת לקוח
        cust = Customer.query.filter_by(phone=phone).first()
        if not cust:
            cust = Customer(full_name=full_name, phone=phone, email=request.form.get('email'))
            db.session.add(cust)
            db.session.commit()
            
        # העלאת קובץ
        filename = None
        if 'image' in request.files:
            file = request.files['image']
            if file.filename:
                filename = secure_filename(f"{datetime.now().timestamp()}_{file.filename}")
                file.save(os.path.join('app/static/uploads', filename))

        inq = Inquiry(
            customer_id=cust.id,
            project_id=request.form.get('project_id'),
            subject=request.form.get('subject'),
            description=request.form.get('description'),
            image_filename=filename,
            status='New',
            priority=request.form.get('priority') or 'Normal'
        )
        db.session.add(inq)
        db.session.commit()
        
        log_activity('CREATE', 'Inquiry', inq.id)
        flash('הפנייה נוצרה בהצלחה', 'success')
        return redirect(url_for('inquiries.list_inquiries'))

    projects = Project.query.filter_by(is_deleted=False).all()
    return render_template('inquiries/new.html', projects=projects)