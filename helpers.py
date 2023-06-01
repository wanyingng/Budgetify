from flask import render_template, redirect, session
from functools import wraps
import re


def login_required(f):
    """
    Decorate routes to require login.
    https://flask.palletsprojects.com/en/1.1.x/patterns/viewdecorators/
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("user_id") is None:
            return redirect("/login")
        return f(*args, **kwargs)
    return decorated_function


def error(message, code=400):
    """Render message as an error to user."""
    return render_template("error.html", code=code, message=message), code


def usd(value):
    """Format value as USD."""
    return f"${value:,.2f}"


def validate(password):
    """Validate password to ensure a password is at least 8 characters long and contains at least 1
    digit number, a uppercase and a lowercase letter, and a special character."""
    if len(password) < 8:
        return "Password must be at least 8 letters long", 400
    elif re.search('[0-9]',password) is None:
        return "Password must have a number", 400
    elif re.search('[A-Z]',password) is None:
        return "Password must have a uppercase letter", 400
    elif re.search('[a-z]',password) is None:
        return "Password must have a lowercase letter", 400
    elif re.search('[^a-zA-Z0-9]',password) is None:
        return "Password must have a special character", 400
    else:
        return "Password is OK", 200
