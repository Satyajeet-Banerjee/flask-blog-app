import hashlib
from functools import wraps
from flask import abort
from flask_login import current_user


def gravatar_url(email, size=100):
    email = email.strip().lower().encode("utf-8")
    email_hash = hashlib.md5(email).hexdigest()
    return f"https://www.gravatar.com/avatar/{email_hash}?s={size}&d=identicon"


def admin_only(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_admin:
            return abort(403)
        return f(*args, **kwargs)
    return decorated_function