#!venv/bin/python
# coding: utf-8
"""
    Common views for website
"""
import re
import simplejson as json

from flask import g, Flask, render_template, request, session, make_response, jsonify, url_for, redirect

# window hack
try:
    from flaskext.mail import Message, email_dispatched
    from project import mail
except ImportError:
    Message, email_dispatched = None, None

from project import app, markdown
import tricks as tricks_view
import users as users_view
import utils, admin


def index(*args, **context):
    """
    Главная страница.
    Собирает context для рендера в шаблон страницы (index.html)
    
    Выполняет отложенные действия, т.е. те действия,
    которые были сохранены в куки, пока пользователь 
    был неавторизован. (Например чекин неавторизованного пользователя)
    """
    # проверим есть ли чекины от пользователя, когда он был неавторизован?
    user = g.user

    if user and request.cookies.get('trick'):
        try:
            tricks_view.update_checktrick_from_cookie(user['_id'])
        except BaseException:
            """ pokemon exception handler - im bad black ass :p """
            #raise

    tricks = tricks_view.get_tricks(*args, **context)
    tags   = tricks_view.get_tags(*args, tricks=tricks)

    context.update({
        #'user'   : json.dumps(context['user']),
        'tricks' : json.dumps(tricks),
        'tags'   : json.dumps(tags)
    })

    r = render_template('index.html', **context)
    response = make_response(r)
    response.headers['X-Frame-Options'] = 'SAMEORIGIN'
    
    return response


@utils.render_to(template="mobile/index.html")
def mobile_index():
    return {}


def feedback():
    body = u'\n'.join(['%s:%s' % (k,v) for k, v in request.form.items()])
    if Message:
        msg = Message(u"Feedback", recipients=app.config['ADMINS'])
        msg.body = body
        mail.send(msg)
    else:
        print body
    return 'Ok'


def youtube_reciver():
    """
    Просто принимаем ответ от ютуба и переводим его в json
    """
    return jsonify(request.args)


def pown(user_id, domain=None):
    """
    Авторизация по указанному user_id. Исключительно в отладочных целях и на локальной копии.
    """
    if not app.config.get('LOCAL'):
        return 'Only for local use', 403

    user = users_view.get_user(user_id)
    session['user_id'] = user['id']

    return redirect('http://%s' % request.host)
