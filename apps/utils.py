# -*- coding: utf-8 -*-
from pytils.utils import takes, one_of
from pytils.numeral import choose_plural, get_plural

from project import db, app


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
        }
        prev.%(key)s = obj.%(key)s;
    }""" % {'key': key}

    rows = []
    for x in db.trick_user.group([key], _filter, {key: '', 'cones': 0, 'video_url': ''}, reduce_func):
        # HACK для потдтягивания данных по id
        x[key] = db[key].find_one({'_id': x[key]})
        rows.append(x)

    return rows

#TODO: cached this!
def get_user_rating(user_id):
    """
    Считает и возвращает рейтинг пользователя.
    NOTE: нужно будет переписать, когда будет введена история трюков пользователя.
    """
    cones_per_trick = get_valid_cones_per_trick(user_id)

    for trick in db.trick.find({'_id': {'$in': cones_per_trick.keys()}}):
        cones_per_trick[trick['_id']] *= trick['score']

    return float('%.2f' % sum(cones_per_trick.values()))


def get_valid_cones_per_trick(user_id):
    """
    Возвращает "правильное" кол-во конусов для трюка, в зависиомости
    от положения луны
    """
    grouped_data = {}

    for trick_user in db.trick_user.find({"user": user_id}):
        if trick_user.get(u'video_url') and trick_user.get(u'approved'):
            grouped_data[trick_user['trick']] = trick_user['cones'] * (1 if trick_user['cones'] > 3 else 1.2)
        else:
            grouped_data[trick_user['trick']] = min(trick_user['cones'], 3)

    return grouped_data
