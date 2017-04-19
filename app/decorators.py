# coding=utf-8
from functools import wraps
from flask_login import current_user
from flask import abort
from .models import Permissions


def permission_required(permissions):
    def decorator(func):
        @wraps(func)
        def decorator_func(*args, **kwds):
            if not current_user.can(permissions):
                abort(403)
            return func(*args, **kwds)
        return decorator_func
    return decorator


def admin_required(func):
    return permission_required(Permissions.ADMINISTER)(func)
