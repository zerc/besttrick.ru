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
import tricks, common


def index(*args, **context):
    """
    Главная страница.
    Собирает context для рендера в шаблон страницы (index.html)
    
    Выполняет отложенные действия, т.е. те действия,
    которые были сохранены в куки, пока пользователь 
    был неавторизован. (Например чекин неавторизованного пользователя)
    """
    user = g.user
    template = context.pop('template', 'index.html')

    # проверим есть ли чекины от пользователя, когда он был неавторизован?
    if user and request.cookies.get('trick'):
        try:
            tricks.update_checktrick_from_cookie(user['_id'])
        except BaseException:
            """ pokemon exception handler - im bad black ass :p """
            #raise

    all_tricks = tricks.get_tricks(*args, **context)
    tags       = tricks.get_tags(*args, tricks=all_tricks)

    context.update({
        'tricks' : json.dumps(all_tricks),
        'tags'   : json.dumps(tags)
    })

    r = render_template(template, **context)
    response = make_response(r)
    response.headers['X-Frame-Options'] = 'SAMEORIGIN'
    
    return response


@common.render_to(template="mobile/index.html")
def mobile_index(*args, **kwargs):
    return {
        'tricks': tricks.get_tricks(*args, **kwargs)
    }


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
    # TODO: вероятно добавить проверку по домену
    """
    return jsonify(request.args)


def pown(user_id):
    """
    Авторизация по указанному user_id. Исключительно в отладочных целях и на локальной копии.
    """
    if not app.config.get('LOCAL'):
        return 'Only for local use', 403

    session['user_id'] = user_id

    return redirect('http://%s' % request.host)
