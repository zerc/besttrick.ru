# coding: utf-8
"""
    apps.ahcives.views
    ~~~~~~~~~~~~~~~~~~

    Views for achives module

    :copyright: (c) 2013 by zero13cool
"""
from flask import render_template, request, jsonify, session, redirect, url_for, make_response, flash, g

from project import app

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
                'progress'     : e.get('progress'),
                #'time_changed' : e.get('time_changed').t,
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
