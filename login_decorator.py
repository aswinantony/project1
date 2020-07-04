from functools import wraps
from flask import redirect, render_template, request, session

def login_required(f):
    """
    Login Required Decorator

    https://flask.palletsprojects.com/en/1.1.x/patterns/viewdecorators/
    
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("user_id") is None:
            return redirect("/login")
        return f(*args, **kwargs)
    return decorated_function