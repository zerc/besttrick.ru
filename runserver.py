#!venv/bin/python
# -*- coding: utf-8 -*-
import re
import simplejson as json

from flask import g, Flask, render_template, request, redirect, session, make_response, jsonify, url_for
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
@users_view.adding_user
def index(*args, **kwargs):
    """
    Главная страница.
    Собирает context для рендера в шаблон страницы (index.html)
    
    Выполняет отложенные действия, т.е. те действия,
    которые были сохранены в куки, пока пользователь 
    был неавторизован. (Например чекин неавторизованного пользователя)
    """
    _is_mobile = utils.is_mobile()
    _tmpl_name = 'mobile/index.html' if _is_mobile else 'index.html'
    
    if kwargs['user'] is not False:
        # проверим есть ли чекины от пользователя, когда он был неавторизован?
        if request.cookies.get('trick'):
            try:
                tricks_view.update_checktrick_from_cookie(kwargs['user']['id'])
            except BaseException:
                """ pokemon exception handler - im bad black ass :p """
                #raise

    context = {
        'user': kwargs['user'],

        # просто шоткат, типа :)
        'user_admin_lvl': kwargs['user']['admin'] if kwargs['user'] else 0,
    }

    if not _is_mobile:
        tricks = tricks_view.get_tricks(*args, **kwargs)
        tags   = tricks_view.get_tags(*args, tricks=tricks)

        context.update({
            'user'   : json.dumps(kwargs['user']),
            'tricks' : json.dumps(tricks),
            'tags'   : json.dumps(tags)
        })

    r = render_template(_tmpl_name, **context)

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


@app.route('/pown/<int:user_id>/', methods=['GET'])
def pown(user_id):
    """
    Авторизация по указанному user_id. Исключительно в отладочных целях и на локальной копии.
    """
    if not app.config.get('LOCAL'):
        return 'Only for local use', 403

    user = db.user.find_one({'_id': user_id})

    if not user:
        return u'User with id = %d does not exists' % user_id, 404

    session['user_id'] = user['_id']

    return redirect(url_for('index'))


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000)
