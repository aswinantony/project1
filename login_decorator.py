from functools import wraps
from flask import redirect, render_template, request, session

def login_required(f):
    """
    Login Required Decorator - This will make sure the user is logged in before continuing if used correctly in the required route.

    https://flask.palletsprojects.com/en/1.1.x/patterns/viewdecorators/
    
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("user_id") is None:
            return redirect("/login")
        return f(*args, **kwargs)
    return decorated_function
