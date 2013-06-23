# coding: utf-8
"""
    apps.users.base
    ~~~~~~~~~~~

    Низкоуровневая логика хранится сдесь

    :copyright: (c) 2012 by zero13cool
"""
from functools import wraps

from flask import g, redirect, request
from project import app
from apps.common import get_user_rating

from .models import User, LOGINZA_FIELDS_MAP


def for_owner(methods=None):
    """
    Allow defined methods only for owner
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            if not g.user: return 'Access Deny', 403

            user_id = kwargs.get('user_id')
            if user_id is None: return 'Missed user_id attribute', 403

            if g.user.get('id') != user_id:
                if methods is None or request.method in methods:
                    return 'Allow only for owner', 403

            return func(*args, **kwargs)
        return wrapper
    return decorator

      
def user_only(func):
    """
    Декоратор - "только для пользователя"
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        if not g.user or g.user.get('banned'):
            return 'Access Deny', 403

        return func(*args, **kwargs)

    return wrapper


def get_field(d, field_name):
    """ Использует точечную нотацию в имени поля, для работы со вложенными словарями """
    parts = field_name.split('.')
    value = d.get(parts[0], u'')

    if not isinstance(value, dict):
        return value

    for part in parts[1:]:
        try:
            value = value[part]
        except KeyError:
            return ''
    return value


def register(user_data):
    """
    Register user
    """
    # HACK: если нет никнейма, конструируем его
    if not user_data.get(u'nickname'):
        user_data[u'nickname'] = u' '.join([user_data['name'].get('first_name', ''), user_data['name'].get('last_name')])

    new_user = app.connection.User()
    for k, t in User.structure.items():
        if k == 'admin':
            continue

        try:
            new_user[k] = t(get_field(user_data, LOGINZA_FIELDS_MAP.get(k, k)))
        except (KeyError, ValueError):
            continue

    new_user['_id'] = app.db.seqs.find_and_modify({"_id": "user_seq"}, {"$inc": {"val": 1}})['val']
    new_user.save()
    return new_user


def get_user(user_id, **kwargs):
    user = app.connection.User.find_one({"_id": user_id})
    return user.patched  if user else None
