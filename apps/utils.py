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
