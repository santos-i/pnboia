from flask import session, redirect, url_for
from functools import wraps


def login_required(f):
    @wraps(f)
    def wrap(*args, **kwds):
        if 'username' in session:
            if session["username"]:
                return f(*args, **kwds)
            else:
                return redirect(url_for('home'))
        else:
            return redirect(url_for('home'))
    return wrap