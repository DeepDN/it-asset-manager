import functools
from flask import flash, redirect, url_for, jsonify
from flask_login import current_user


def route_error_handler(template=None, redirect_to=None):
    def decorator(f):
        @functools.wraps(f)
        def wrapped(*args, **kwargs):
            try:
                return f(*args, **kwargs)
            except Exception as e:
                flash(f'Error: {str(e)}', 'error')
                if redirect_to:
                    return redirect(url_for(redirect_to))
                if template:
                    return render_template(template, error=str(e), user=current_user)
                return redirect(url_for('main.dashboard'))
        return wrapped
    return decorator
