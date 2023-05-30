from flask import render_template


def error(message, code=400):
    """Render message as an error to user."""
    return render_template("error.html", code=code, message=message), code


def usd(value):
    """Format value as USD."""
    return f"${value:,.2f}"
