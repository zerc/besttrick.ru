# coding: utf-8
"""
    apps.users.base
    ~~~~~~~~~~~

    Низкоуровневая логика хранится сдесь

    :copyright: (c) 2012 by zero13cool
"""
from functools import wraps

from flask import g, redirect
from project import app
from apps.common import get_user_rating

from .models import User


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


def clean_fields(user_dict):
    """
    Убирает из словаря с данными пользователя некоторые "секьюрные" поля.
    Просто чтобы не палить их на клиенте.
    """
    for field in (u'identity', u'provider', u'email', u'banned', u'uid'):
        try:
            user_dict.pop(field)
        except KeyError:
            continue

    return user_dict


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
    # HACK: если нет никнейма, конструируем его
    if not user_data.get(u'nickname'):
        user_data[u'nickname'] = u' '.join([user_data['name'].get('first_name', ''), user_data['name'].get('last_name')])

    new_user = app.connection.User()
    for k, t in User.structure.items():
        if k == 'admin':
            continue

        try:
            new_user[k] = t(get_field(user_data, LOGINZA_FIELDS_MAP.get(k, k)))
        except KeyError:
            continue

    new_user['_id'] = app.db.seqs.find_and_modify({"_id": "user_seq"}, {"$inc": {"val": 1}})['val']
    new_user.save()
    return new_user


def get_user(user_id=None, full=False, user_dict=None):
    """
    Хэлпер возвращает пропатченый объект юзера.
    Если указан user_dict - то не делает выборку из монги,
    а использует эти данные.
    """
    if user_dict is None:
        user = app.db.user.find_one({'_id': user_id}) or False
        if user is False: return False
        user['id'] = int(user.pop('_id'))
    else:
        user = user_dict

    user['rating'] = get_user_rating(user['id'])

    return user if full else clean_fields(user)
