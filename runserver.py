#!venv/bin/python
# -*- coding: utf-8 -*-
import re
import simplejson as json

from flask import g, Flask, render_template, request, redirect, session, make_response, jsonify
try:
    from flaskext.mail import Message, email_dispatched
    from project import mail
except ImportError:
    # window hack
    Message, email_dispatched = None, None
from mongokit import Connection

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
        user['rating'] = utils.get_user_rating(user['id'])
        context = {'user': _dumps(user), 'user_admin_lvl': user['admin']}

    tricks = list(db.trick.find().sort("_id", 1))

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

        trick['descr'] = markdown(trick['descr'])

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
    elif crawler is not False:
        try:
            r = get_content_for_crawler(crawler, context)
        except AttributeError, e:
            return redirect('/?_escaped_fragment_=%s' % e, code=301)
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


def get_content_for_crawler(crawler_path, context):
    """
    Рендерит контент запрошенной пауком страницы
    """
    if crawler_path == '':
        return render_template('crawler.html', **context)

    # вероятно переход по старому урлу - нужно редиректнуть
    if not re.findall(r'trick\d+', crawler_path):
        OLD_IDS_MAP = {
            # old url       # new
            'trick/kazachok-f'    : 'trick0',
            'trick/korean-spin'   : 'trick1',
            'trick/russian-spin'  : 'trick2',
            'trick/chicken-leg-b' : 'trick3',
            'trick/toe-machine'   : 'trick4',
            'trick/day-night'     : 'trick5',
            'trick/footgun-toe-f' : 'trick6',
            'trick/onewheel-f'    : 'trick7',
            'trick/confraglide'   : 'trick8',
            'trick/cobra-b'       : 'trick9',
            'trick/seven-f'       : 'trick10',
            'trick/no-wiper'      : 'trick11',
            'trick/foot-spin'     : 'trick12',
        }

        if OLD_IDS_MAP.get(crawler_path):
            raise AttributeError(OLD_IDS_MAP.get(crawler_path))

    c = app.url_map.bind('')

    if not crawler_path.startswith('/'):
        crawler_path = '/' + crawler_path

    if not crawler_path.endswith('/'):
        crawler_path += '/'

    view_function_name, view_params = c.match(crawler_path)
    view_function = app.view_functions[view_function_name]
    result = view_function(**view_params)

    if isinstance(result, basestring):
        # TODO: перехват ошибки распаковки
        result = json.loads(result)

    result.update({
        'view_name'   : view_function_name,
        'global_data' : context
    })

    return render_template('crawler.html', **result)


@app.route('/youtube_reciver/')
def youtube_reciver():
    """
    Просто принимаем ответ от ютуба и переводим его в json
    """
    return jsonify(request.args)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000)
