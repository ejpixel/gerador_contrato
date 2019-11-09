from functools import wraps
from flask import session, request, redirect, url_for

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("user_id") == "pixel":
            return f(*args, **kwargs)
        return redirect(url_for('access'))
    return decorated_function