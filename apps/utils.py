# -*- coding: utf-8 -*-
from pytils.utils import takes, one_of
from project import db


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


def get_user_rating(user_id):
    """
    Считает и возвращает рейтинг пользователя.
    NOTE: нужно будет переписать, когда будет введена история трюков пользователя.
    """
    tricks_user = db.trick_user.find({"user": user_id})
    grouped_data = {}

    for trick_user in tricks_user:
        if trick_user.get(u'video_url') and trick_user.get(u'approved'):
            grouped_data[trick_user[u'trick']] = trick_user['cones'] * (1 if trick_user['cones'] > 3 else 1.2)
        else:
            grouped_data[trick_user[u'trick']] = min(trick_user['cones'], 3)


    for trick in db.trick.find({'_id': {'$in': grouped_data.keys()}}):
        grouped_data[trick['_id']] *= trick['score']

    return float('%.2f' % sum(grouped_data.values()))
