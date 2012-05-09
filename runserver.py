#!venv/bin/python
# -*- coding: utf-8 -*-
import simplejson as json

from flask import g, Flask, render_template, request, session, make_response, jsonify
from flaskext.mail import Message, email_dispatched
from mongokit import Connection

from project import app, connection, db, mail, markdown
from apps import tricks as tricks_view, users as users_view


@app.route('/')
def index():
    context, user = {'user': False}, False
    user_id = session.get('user_id', False)
    json_field = request.args.get('json', False)

    def _dumps(d):
        return d if json_field else json.dumps(d)

    if user_id is not False:
        user = db.user.find_one({'_id': user_id})
        user['id'] = user.pop('_id')
        context = {'user': _dumps(user)}

    tricks = list(db.trick.find())

    # лучшие результаты по трюкам + общее число делающих пользователей
    reduce_func = u"""
    function(obj, prev) {
        if (prev.best_user_cones < obj.cones) {
            prev.best_user_cones = obj.cones;
            prev.best_user_id = obj.user;
        }
        prev.users += 1;

        %s

    }""" % (("if (obj.user === %s) { prev.user_do_this = true; }" % user_id) if user_id is not False else '')
    best_users_qs = db.trick_user.group(['trick'], None, {'best_user_cones': 0, 'best_user_id': '', 'users': 0, 'user_do_this': False}, reduce_func)
    best_users = {}
    default = {'user_do_this': False}
    for x in best_users_qs:
        k = x.pop(u'trick')
        best_users[k] = dict(default, **x)
        best_users[k]['best_user'] = db.user.find_one({'_id': best_users[k]['best_user_id']})


    # результат пользователя
    user_stats = {}
    if user_id is not False:
        reduce_func = u"""function(obj, prev) { 
            prev.cones = obj.cones;
            prev.video_url = obj.video_url;
        }"""
        user_stats_qs = db.trick_user.group(['trick'], {'user': user_id}, {'cones': 0, 'video_url': ''}, reduce_func)

        for x in user_stats_qs:
            k = x.pop(u'trick')
            user_stats[k] = x

    tags = {}
    for x in db.tag.find():
        x[u'tricks'] = []
        tags[x.pop(u'_id')] = x

    # навешиваем
    for trick in tricks:
        trick[u'id'] = trick.pop(u'_id')
        try:
            trick.update(best_users[unicode(trick[u'id'])])
        except KeyError:
            trick.update({'best_user_cones': None, 'best_user': None})

        try:
            trick.update(user_stats[unicode(trick[u'id'])])
        except KeyError:
            trick.update({'cones': 0})

        trick['descr'] = markdown(trick['descr'])

        for t in trick['tags']:
            tags[t]['tricks'].append(trick[u'id'])

    context['tricks'] = _dumps(tricks)
    context['tags']   = _dumps(tags)

    if json_field:
        r = json.dumps(context[json_field])
    else:
        r = render_template('index.html', **context)

    response = make_response(r)
    response.headers['X-Frame-Options'] = 'SAMEORIGIN'
    return response


@app.route('/feedback/', methods=['POST'])
def feedback():
    body = u'\n'.join(['%s:%s' % (k,v) for k, v in request.form.items()])
    msg = Message(u"Feedback", recipients=app.config['ADMINS'])
    msg.body = body
    mail.send(msg)
    return 'Ok'

@app.route('/youtube_reciver/')
def youtube_reciver():
    """
    Просто принимаем ответ от ютуба и переводим его в json
    """
    return jsonify(request.args)



if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000)
