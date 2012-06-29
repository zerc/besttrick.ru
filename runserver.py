#!venv/bin/python
# -*- coding: utf-8 -*-
import re
import simplejson as json

from flask import g, Flask, render_template, request, redirect, session, make_response, jsonify
from mongokit import Connection

# window hack
try:
    from flaskext.mail import Message, email_dispatched
    from project import mail
except ImportError:
    Message, email_dispatched = None, None

from project import app, connection, db, markdown
from apps import tricks as tricks_view, users as users_view, utils, admin


@app.route('/')
def index():
    context, user = {'user': False, 'user_admin_lvl': 0}, False
    user_id = session.get('user_id', False)

    # TODO: завернуть в декоратор
    json_field = request.args.get('json', False)
    crawler = request.args.get('_escaped_fragment_', False)

    def _dumps(d):
        return d if json_field else json.dumps(d)

    if user_id is not False:
        user = db.user.find_one({'_id': user_id})
        user['id'] = user.pop('_id')

        # проверим есть ли чекины от пользователя, когда он был неавторизован?
        if request.cookies.get('trick'):
            try:
                tricks_view.update_checktrick_from_cookie(user_id)
            except BaseException:
                """ pokemon exception handler - im bad black ass :p """
                #raise

        user['rating'] = utils.get_user_rating(user['id'])
        context = {'user': _dumps(user), 'user_admin_lvl': user['admin']}

    tricks = list(db.trick.find().sort("_id", 1))

    # лучшие результаты по каждому трюку
    best_users = {}
    for r in tricks_view.get_best_results(None, user_id):
        best_users[int(r.pop(u'trick'))] = r

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
    # так как сейчас у нас только слалом - отключил мажорные тэги вообще
    # чтобы не смущать народ
    for x in db.tag.find({'major': {'$ne': True}}):
        x[u'tricks'] = []
        tags[x.pop(u'_id')] = x

    # навешиваем
    for trick in tricks:
        trick[u'id'] = trick.pop(u'_id')
        try:
            trick.update(best_users[trick[u'id']])
        except KeyError:
            trick.update({'best_user_cones': None, 'best_user': None})

        try:
            trick.update(user_stats[trick[u'id']])
        except KeyError:
            trick.update({'cones': 0})

        trick['descr_html'] = markdown(trick['descr'])

        for t in trick['tags']:
            try:
                tags[t]['tricks'].append(trick[u'id'])
            except KeyError:
                # тэг отключен
                continue

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
    if Message:
        msg = Message(u"Feedback", recipients=app.config['ADMINS'])
        msg.body = body
        mail.send(msg)
    else:
        print body
    return 'Ok'


@app.route('/youtube_reciver/')
def youtube_reciver():
    """
    Просто принимаем ответ от ютуба и переводим его в json
    """
    return jsonify(request.args)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000)
