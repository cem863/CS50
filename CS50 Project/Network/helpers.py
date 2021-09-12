# I have used the apology and login_required functions from finance in my project
import os

from flask import redirect, render_template, request, session
from functools import wraps

# The function below communicates an error to the user. This helps the user see what error they're facing (e.g. missing password, invalid username, etc)
def apology(message, code=400):
    # Display an error message to the user
    def escape(s):
        for old, new in [("-", "--"), (" ", "-"), ("_", "__"), ("?", "~q"),
                         ("%", "~p"), ("#", "~h"), ("/", "~s"), ("\"", "''")]:
            s = s.replace(old, new)
        return s
    return render_template("apology.html", top=code, bottom=escape(message)), code


# Again, I have used this function from finance. This will help require the user to be logged in before being able to access a list of friends, add friends, etc.
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("user_id") is None:
            return redirect("/login")
        return f(*args, **kwargs)
    return decorated_function
