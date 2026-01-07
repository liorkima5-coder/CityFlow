from functools import wraps
# הוסף את request לרשימה
from flask import abort, flash, redirect, url_for, request
from flask_login import current_user

def require_perm(permission_name):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.is_authenticated:
                return redirect(url_for('auth.login'))
            
            # Admin always has access
            if current_user.role and current_user.role.name == 'Admin':
                return f(*args, **kwargs)
                
            if not current_user.has_perm(permission_name):
                flash('אין לך הרשאה לבצע פעולה זו', 'danger')
                return redirect(request.referrer or url_for('main.dashboard'))
                
            return f(*args, **kwargs)
        return decorated_function
    return decorator