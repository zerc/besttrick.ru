# coding: utf-8
"""
    apps.ahcives.views
    ~~~~~~~~~~~~~~~~~~

    Views for achives module

    :copyright: (c) 2013 by zero13cool
"""
from flask import render_template, request, jsonify, session, redirect, url_for, make_response, flash, g

from project import app, checkin_signal

from apps.common import grouped_stats, allow_for_robot, is_robot, render_to
from apps.users import user_only, get_user


def get_achives_for_user(user_id, level):
    def _patch(a):
        e, created = a.get_event(user_id, level)
        if created is False:
            a.update({
                'user_id'      : user_id,
                'level'        : level,
                'done'         : e.get('done'),
                'progress'     : e.get('progress')
            });
        a['id'] = a.pop('_id');
        return a
    return map(_patch, app.connection.Achive.fetch())


@render_to()
@user_only
def my_achives(*args, **kwargs):
    """
    Список ачивок пользователя
    """
    user_id = g.user['id'] if g.user else False
    level   = int(request.args.get('level', 1))
    
    return {
        'achives': get_achives_for_user(user_id, level)
    }


@render_to()
def my_achive(achive_id):
    return {}



def add_achive_after_checkin(trick_user):
    achives = app.connection.Achive.fetch({"trick_id": trick_user['trick']})
    for a in achives:        
        if a.test(trick_user['cones']):
            level = a.get_level(trick_user['cones'])
            a.make_event(trick_user['user'], trick_user['cones'])
            a.update_parents(trick_user['user'], level)
checkin_signal.connect(add_achive_after_checkin)
