from flask import Blueprint, render_template, request, flash, redirect, url_for
from app.extensions import db
from app.models import Project, Customer, Inquiry
from werkzeug.utils import secure_filename
import os
from datetime import datetime

public_bp = Blueprint('public', __name__)

@public_bp.route('/report', methods=['GET', 'POST'])
def report():
    if request.method == 'POST':
        full_name = request.form.get('full_name')
        phone = request.form.get('phone')
        project_id = request.form.get('project_id')
        
        # יצירת/איתור לקוח
        cust = Customer.query.filter_by(phone=phone).first()
        if not cust:
            cust = Customer(full_name=full_name, phone=phone, email=request.form.get('email'))
            db.session.add(cust)
            db.session.commit()
            
        # יצירת פנייה
        inq = Inquiry(
            customer_id=cust.id,
            project_id=project_id,
            subject=request.form.get('subject'),
            description=request.form.get('description')
        )
        db.session.add(inq)
        db.session.commit()
        
        flash('הדיווח התקבל בהצלחה!', 'success')
        return redirect(url_for('public.report'))

    projects = Project.query.filter_by(is_deleted=False).all()
    return render_template('public/report.html', projects=projects)