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


def get_achives_for_user(user_id):
    def _patch(a):
        e = a.get_event_or_dummy(user_id)
        a['id'] = a.pop('_id');
        a.update({'user_id': user_id, 'time_changed': e.get('time_changed').ctime()})
        a.update(dict((k, e.get(k)) for k in ('level', 'done', 'progress')))
        return a
    return map(_patch, app.connection.Achive.fetch().sort('score', -1))


@render_to()
@user_only
def my_achives(*args, **kwargs):
    user_id = g.user['id'] if g.user else False
    return {'achives': get_achives_for_user(user_id)}


@render_to()
def profile_achives(user_id, *args, **kwargs):
    return {'achives': get_achives_for_user(user_id)}


def add_achive_after_checkin(trick_user):    
    achives = app.connection.Achive.fetch({"trick_id": trick_user['trick']})
    trick_user['user'] = int(trick_user['user'])
    for a in achives:        
        a.do(trick_user['user'], trick_user['cones'])
        a.do_parents(trick_user['user'])
checkin_signal.connect(add_achive_after_checkin)


@render_to()
def get_tituls(*args, **kwargs):
    try:
        user_id = int(request.args.get('user_id'))
    except (ValueError, TypeError):
        return u'Invalid user_id', 410

    achives = app.connection.Achive.fetch({"score": {"$gt": 2}})
    return {'tituls': [a.get_titul(user_id) for a in achives]}
