# -*- coding: utf-8 -*-
from pytils.utils import takes, one_of
from pytils.numeral import get_plural
import simplejson as json
from functools import wraps
from mongokit import Document
from project import app

from flask import render_template, request, make_response, url_for
from werkzeug.wrappers import BaseResponse


def render_to(template=None):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            subdomain = subdomain_or_none(request.host)
            status_code = 200
            ctx = f(*args, **kwargs) or {}

            if isinstance(ctx, BaseResponse):
                return ctx

            if isinstance(ctx, tuple):
                ctx, status_code = ctx

            subdomain_to_folder = {'m': 'mobile/'}

            if subdomain is None:
                return json.dumps(ctx), status_code

            template_name = template
            if template_name is None:
                template_name = subdomain_to_folder.get(subdomain, '') + f.__name__ + '.html'

            return render_template(template_name, **ctx), status_code
        return decorated_function
    return decorator


def subdomain_or_none(host):
    parts = host.split('.')
    return None if len(parts) <= 2 else parts[0]


def is_mobile():
    """
    Testing request for mobile subdomain
    """
    return request.url_root.startswith('http://m.')


@app.template_filter('plural')
def plural(s, amount):
    return get_plural(int(s), amount)


@takes(one_of('trick', 'user'))
def grouped_stats(key, _filter):
    """
    Выдают сгруппированную статистику по указанному полю.
    - key = user || trick
    - filter = dict условия фильтрации

    """
    reduce_func = u"""function(obj, prev) {
        if (prev.cones < obj.cones) {
            prev.cones = obj.cones;
            prev.video_url = obj.video_url;
            prev.approved = obj.approved;
        }
        prev.%(key)s = obj.%(key)s;
    }""" % {'key': key}

    rows = []
    defaults = {key: '', 'cones': 0, 'video_url': '', 'approved': 0}
    for x in app.db.trick_user.group([key], _filter, defaults, reduce_func):
        # HACK для потдтягивания данных по id
        x[key] = app.db[key].find_one({'_id': x[key]})
        x[key]['id'] = x[key].pop('_id')
        rows.append(x)

    return rows

#TODO: cached this!
def get_user_rating(user_id):
    """
    Считает и возвращает рейтинг пользователя.
    NOTE: нужно будет переписать, когда будет введена история трюков пользователя.
    """
    cones_per_trick = get_valid_cones_per_trick(user_id)

    for trick in app.db.trick.find({'_id': {'$in': cones_per_trick.keys()}}):
        cones_per_trick[trick['_id']] *= trick['score']

    return float('%.2f' % sum(cones_per_trick.values()))


def get_valid_cones_per_trick(user_id):
    """
    Возвращает "правильное" кол-во конусов для трюка, в зависиомости
    от положения луны
    """
    grouped_data = {}

    for trick_user in app.db.trick_user.find({"user": user_id}):
        if trick_user.get(u'video_url') and trick_user.get(u'approved') == 1:
            grouped_data[trick_user['trick']] = trick_user['cones'] * (1 if trick_user['cones'] > 3 else 1.2)
        else:
            grouped_data[trick_user['trick']] = min(trick_user['cones'], 3)

    return grouped_data


def is_robot():
    return request.args.get('robot') > 0


def allow_for_robot(func):
    """
    Вовзвращает html для отдачи поисковому роботу.
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        context = func(*args, **kwargs)

        if is_robot():
            template_name = 'crawler_%s.html' % func.__name__

            if isinstance(context, basestring):
                context = json.loads(context)

            return render_template(template_name, **context)

        return context

    return wrapper


### Models stuff
class classproperty(object):
    """
    decorator :)
    """
    def __init__(self, getter):
        self.getter= getter
    def __get__(self, instance, owner):
        return self.getter(owner)


class BaseModel(Document):
    @classproperty
    def __database__(self):
        return app.config['MONGODB_DB']

    @classproperty
    def migrate(cls):
        return cls.migration_handler(cls).migrate_all(app.db[cls.__collection__])
