from flask import request
from datetime import datetime
from flask_login import current_user
from app.extensions import db
from app.models import AuditLog, Inquiry
import json

def log_activity(action, entity_type, entity_id=None, meta=None):
    """רישום לוג פעילות מרוכז"""
    try:
        uid = current_user.id if current_user.is_authenticated else None
        log = AuditLog(
            user_id=uid,
            action=action,
            entity_type=entity_type,
            entity_id=entity_id,
            meta_json=meta, # SQLAlchemy handles dict to JSON
            ip_address=request.remote_addr
        )
        db.session.add(log)
        # Commit should be handled by the caller or request teardown, 
        # but for safety we add to session here.
    except Exception as e:
        print(f"Audit Log Error: {e}")

def check_sla_status(inquiry):
    """Logic to determine if inquiry breached SLA"""
    # Simple logic: High priority > 24 hours, Normal > 48 hours
    hours_since_update = (datetime.now() - inquiry.last_activity_at).total_seconds() / 3600
    if inquiry.priority == 'High' and hours_since_update > 24:
        return 'danger' # Breached
    if inquiry.priority == 'Normal' and hours_since_update > 48:
        return 'warning' # At risk
    return 'success'