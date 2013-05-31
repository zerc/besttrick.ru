# coding: utf-8
"""
    apps.users.views
    ~~~~~~~~~~~

    Представления правят балом в этом файле

    :copyright: (c) 2012 by zero13cool
"""
import urllib
import simplejson as json

from flask import render_template, request, session, url_for, g, redirect
from project import app
from apps.common import grouped_stats, get_user_rating, render_to
from .base import *
from .models import User


@app.before_request
def before_request():
    if 'static' not in request.path:
        g.user = get_user(session.get('user_id'))


@app.context_processor
def add_user():
    return {
        'user'          : g.user,
        'user_json'     : json.dumps(g.user)
    }


def login():
    url = "http://loginza.ru/api/authinfo?%s"
    params = urllib.urlencode({'token': request.form['token'], 'id': '', 'sig': ''})
    f = urllib.urlopen(url % params)

    if f.getcode() != 200:
        raise TypeError(u'Loginza response code = %s' % f.getcode())

    user_data = json.loads(unicode(f.read(), 'utf-8'))
    
    # hack так как vkontakte стал vk
    # user_data['identity'] = user_data['identity'].replace('vk.com', 'vkontakte.ru')
    user = app.db.user.find_one({'identity': user_data['identity']}) or register(user_data)

    if user['banned']: return redirect(url_for('banned'))
    
    session['user_id'] = user['_id']

    return redirect('http://%s' % request.host)
    # return redirect(url_for('index'))


def logout():
    session.pop('user_id', None)
    return redirect(request.referrer or url_for('index'))


@user_only
def my_tricks():
    rows = grouped_stats('trick', {'user': g.user['id']})
    return json.dumps(sorted(rows, key=lambda x: x['cones'], reverse=True))


@render_to()
def user():
    if request.method == 'PUT':
        params = json.loads(unicode(request.data, 'utf-8'))
        params.pop('id', None)
        params.pop('_id', None)

        # типа валидация перед апдейтом данных
        for p in params.keys():
            try:
                User.structure[p]
            except KeyError:
                del params[p]
        app.db.user.update({'_id': g.user['id']}, {'$set': params})
        return {'success': 1}

    try:
        user_id = int(request.args.get('user_id'))
    except (ValueError, TypeError):
        user_id = g.user['id']

    return {'user': get_user(user_id).hide}
    

@render_to()
@user_only
def my():
    user = g.user

    if request.method == 'PUT':
        params = json.loads(unicode(request.data, 'utf-8'))
        params.pop('id', None)
        params.pop('_id', None)

        # типа валидация перед апдейтом данных
        for p in params.keys():
            try:
                User.structure[p]
            except KeyError:
                del params[p]

        app.db.user.update({'_id': user['id']}, {'$set': params})
        
        return {'success': 1}
    return {'user': get_user(user.get('id'))}


@render_to()
def user_profile(user_id):
    context = {
        'user': get_user(user_id).hide
    }    
    user_tricks = grouped_stats('trick', {'user': int(user_id)})
    # TODO: remove this dirty hook!
    map(lambda a: a.update(a.pop('trick')), user_tricks)
    context['tricks'] = sorted(user_tricks, key=lambda x: x['cones'], reverse=True)

    return context


@render_to()
def top_users():
    users = (u.patched.hide for u in app.connection.User.find({'banned': False}))
    return {'users': sorted(users, key=lambda user: user['rating'], reverse=True)}

@render_to()
@user_only
def list_of_users():
    is_admin = g.user['admin']    

    def _(user):
        user = app.connection.User(user).patched
        return user if is_admin else user.hide

    return {
        'users': [dict(_(user)) for user in app.db.user.find().sort("_id", -1)]
    }

    
