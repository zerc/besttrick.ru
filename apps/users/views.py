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
        'user_json'     : g.user.to_json() if g.user else 'false'
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


@for_owner(['POST', 'PUT'])
@render_to()
def user(user_id):
    """
    Responser for user model.
    Request method
        `POST` or `PUT` allowed only for owner
        `GET' allow for all
    """
    user = app.connection.User.find_one({"_id": user_id})

    if request.method == 'GET':
        return {'user': user.patched.hide}

    params = json.loads(unicode(request.data, 'utf-8'))
    params.pop('id', None)
    params.pop('_id', None)

    # TODO: решить более адекватно, валидация перед апдейтом данных
    for p in params.keys():
        try:
            User.structure[p]
        except KeyError:
            del params[p]

    user.update(params)
    user.save()

    return {'user': user.patched.hide}


@user_only
def my_tricks():
    rows = grouped_stats('trick', {'user': g.user['id']})
    return json.dumps(sorted(rows, key=lambda x: x['cones'], reverse=True))


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


@render_to()
def users():
    is_admin = g.user and g.user['admin']
    # add validation
    sort, direction = request.args.get('sort', '_id,-1').split(',') 

    def _(u):
        u.patched
        return u if is_admin else u.hide

    # TODO: refactor
    if app.connection.User.structure.get(sort):
        return {
            'users': [_(u) for u in app.connection.User.find({'banned': False}).sort(sort, int(direction))]
        }

    return {
        'users': sorted(app.connection.User.find({'banned': False}), key=lambda user: _(user)[sort], reverse=int(direction) > 0)
    }


    
