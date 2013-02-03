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
from apps.utils import grouped_stats, get_user_rating, render_to
from .base import *
from .models import User

@app.before_request
def before_request():
    if 'static' not in request.path:
        g.user = get_user(session.get('user_id', None), True)


@app.context_processor
def add_user():
    return {
        'user'          : g.user,
        'user_json'     : json.dumps(g.user)
    }



def banned():
    return render_template('banned.html')


def login():
    url = "http://loginza.ru/api/authinfo?%s"
    params = urllib.urlencode({'token': request.form['token'], 'id': '', 'sig': ''})
    f = urllib.urlopen(url % params)

    if f.getcode() != 200:
        raise TypeError(u'Loginza response code = %s' % f.getcode())

    user_data = json.loads(unicode(f.read(), 'utf-8'))
    user = app.db.user.find_one({'identity': user_data['identity']}) or register(user_data)

    if user['banned']: return redirect(url_for('banned'))
    
    session['user_id'] = user['_id']

    return redirect(url_for('index'))


def logout():
    session.pop('user_id', None)
    return redirect(url_for('index'))


@user_only
def my_tricks():
    rows = grouped_stats('trick', {'user': g.user['id']})
    return json.dumps(sorted(rows, key=lambda x: x['cones'], reverse=True))


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
    return {}


@render_to()
def user_profile(user_id):
    context = {}

    user = get_user(user_id)
    user['rating'] = get_user_rating(user_id)
    context['user'] = clean_fields(user)

    user_tricks = grouped_stats('trick', {'user': int(user_id)})
    context['tricks'] = sorted(user_tricks, key=lambda x: x['cones'], reverse=True)

    return json.dumps(context)


#TODO: cached this!
@render_to()
def top_users():
    tricks_scores = {}
    for trick in app.db.trick.find():
        tricks_scores[trick['_id']] = trick['score']

    def _(user):
        return get_user(user_dict=user)

    users = map(_, app.db.user.find({'banned': False}))
    return {'users': sorted(users, key=lambda user: user['rating'], reverse=True)}


@user_only
def list_of_users():
    is_admin = app.db.user.find_one({'_id': session['user_id']})['admin']

    def _(user):
        user['id'] = user.pop('_id')
        return user if is_admin else clean_fields(user)

    return json.dumps([_(dict(user)) for user in app.db.user.find().sort("_id", -1)])
