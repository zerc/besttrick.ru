# coding: utf-8
"""
    apps.tricks.base
    ~~~~~~~~~~~

    Low level functions for tricks module

    :copyright: (c) 2012 by zero13cool
"""
import simplejson as json
from urllib import unquote
from httplib import socket
from gdata.youtube import service

from flask import request, g
from werkzeug.routing import BaseConverter, ValidationError

from project import app, markdown, checkin_signal
from apps.notify import send_notify, CHECKTRICK_WITH_VIDEO
from apps.users import get_user, User
from apps.common import grouped_stats


class TrickConverter(BaseConverter):
    def to_python(self, trick_id):
        try:
            return get_trick(trick_id, False)
        except BaseException, e:            
            raise ValidationError(e)

    def to_url(self, trick):
        return trick.get('id')
app.url_map.converters['trick'] = TrickConverter

### авторизуемся на ютубе, чтобы заливать видосы
try:
    yt_service = service.YouTubeService()
    yt_service.email = app.config['G_EMAIL'] 
    yt_service.password = app.config['G_PASSWORD'] 
    yt_service.source = app.config['G_SOURCE'] 
    yt_service.developer_key = app.config['G_DEV_KEY'] 
    yt_service.client_id = app.config['G_SOURCE']
    yt_service.ProgrammaticLogin()
except socket.gaierror, e:
    # нет коннекта до YouTube
    yt_service = None


def get_checkins(user_id, only_best=True):
    """
    Returns collection of TrickUser objects selected for selected by user_id grouped by trick
    * only_best - if False return all checkins for this trick & user.
    """
    reduce_func = u"""function(obj, prev) {
        if (obj.cones > prev.cones) {
            prev.user      = NumberInt(obj.user);
            prev.trick     = NumberInt(obj.trick);
            prev.cones     = NumberInt(obj.cones);
            prev.video_url = obj.video_url;
        }
    }"""
    # Avoid cross imports >_<
    TU = app.connection.TrickUser
    if only_best:
        return (TU(x) for x in app.db.trick_user.group(['trick'], {'user': user_id}, {'cones': 0}, reduce_func))

    result, tricks_user = {}, app.db.trick_user.find({'user': user_id})
    for t in tricks_user:
        try:
            result[t['trick']].append(TU(t))
        except KeyError:
            result[t['trick']] = [TU(t)]
    return result


def get_tags(*args, **kwargs):
    """
    Хэлпер, возврашаюший пропатченный список тэгов.
    """
    tags = {}
    tricks = kwargs.get('tricks', [])

    for tag in app.db.tag.find({'major': {'$ne': True}}):
        tag[u'tricks'] = []
        tags[tag.pop(u'_id')] = tag

    # Если передан список трюков, то к каждому тэгу
    # прилепляем id его трюков, типа reverse lookup
    # TODO: в монге вероятно это как-то можно решить
    for trick in tricks:
        for tag in trick['tags']:
            try:
                tags[tag]['tricks'].append(trick[u'id'])
            except KeyError:
                continue # тэг отключен

    return tags


def get_trick(trick_id, simple=True):
    trick_id = int(trick_id)
    trick = app.db.trick.find_one({'_id': trick_id})

    rows = grouped_stats('user', {'trick': trick_id})

    for row in rows:
        row['user'] = User(row['user']).patched.hide

    trick['users'] = sorted(rows, key=lambda x: x['cones'], reverse=True)

    # патчу трюк, как-то объеденить функции get_trick и get_tricks
    trick['descr_html'] = markdown(trick['descr'])
    trick['id'] = trick.pop('_id')

    return trick


def get_tricks(*args, **kwargs):
    """
    Хэлпер, возвращающий пропатченный список трюков.
    Пропатченный - значит:
        * к каждому трюку добавляется лучший чекин 
        * результат пользователя (если тот авторизован)
        * сколько пользователей делает этот трюк
    Трюк в данном случае - это просто словарь с данными.
    Если передан аргумент simple - просто список трюков возвращает.
    """
    #TODO: нужно как-то срефакторить, функция слишком большая и непонятная
    tricks = app.connection.Trick.find().sort("_id", 1)
    user_id = g.user['id'] if g.user else False # по идее функция не должна знать про это!

    best_users, user_stats = {}, {}

    if not kwargs.get('simple'):
        # собираем лучшие чекины для каждого трюяка
        for r in get_best_results(None, user_id):
            best_users[int(r.pop(u'trick'))] = r

        # результат пользователя
        if user_id is not False:
            for x in get_checkins(user_id):
                k = x.pop(u'trick')
                user_stats[k] = x

    def _patch(trick):
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

        return trick

    return map(_patch, tricks)


def get_best_results(trick_id=None, user_id=False):
    """
    Возвращает словарь лучших результатов (структура как у trick_user) 
    по указанному трюку или список словарей по всем трюкам.
    """
    ## Кто последний зачекинился, тот и в дамках при возникновении спорной ситуации.
    ## TODO: разруливать чекины на одинаковое кол-во банок, например придавать вес
    ## тем чекинам, которые с видосом.
    reduce_func = u"""
    function(obj, prev) {
        if (prev.best_user_cones <= obj.cones) {
            prev.best_user_cones = NumberInt(obj.cones);
            prev.best_user_id = NumberInt(obj.user);
        }

        prev.users.push(NumberInt(obj.user));

        %s

    }""" % (("if (obj.user === %s) { prev.user_do_this = true; }" % user_id) if user_id is not False else '')

    defaults = {'best_user_cones': 0, 'best_user_id': '', 'users': [], 'user_do_this': False}
    _filter = {'trick': trick_id} if trick_id else None
    best_result = app.db.trick_user.group(['trick'], _filter, defaults, reduce_func)

    for result in best_result:
        result.update({
            'users'        : len(set(result['users'])),
            'best_user'    : get_user(result['best_user_id']).hide,
        })

    return result if trick_id >= 0 else best_result


def send_notice_about_video(trick, user_id, update_data):
    """
    Если в обновляемых данных есть видос, то отсылаем уведомление модератору.
    """
    if not update_data.get('video_url'): return
    
    notify_data = dict(**update_data)
    notify_data.update({
        'user'      : user_id,
        'trick'     : trick['_id'],
        'trickname' : trick['title'],
    })
    send_notify(notify_type=CHECKTRICK_WITH_VIDEO, data=notify_data)


def checkin_user(trick_id, user_id, update_data):
    """
    Низкоуровневая функция чекина пользователя.

    В случае успешного чекина возвращает словарь update_data
    (т.к. он мог быть модифицирован под нужды чекина).

    Или же возвращает кортеж (u'Текст ошибки', http_код_ошибки)
    """
    #TODO: внести валидацию непосредственно в модель (вадидаторы написать)
    #      отлавливать ошибки все дела
    try:
        trick_id = int(trick_id)
    except (ValueError, TypeError):
        return u'Incorrect trick_id = %s' % trick_id, 400

    trick = app.db.trick.find_one({'_id': trick_id})
    if not trick:
        return u'Unknow trick with id = %s' % trick_id, 400

    def _checkin(update_data):
        update_data.update({'user': user_id, 'trick': trick_id})
        trick_user = app.connection.TrickUser()
        trick_user.update(update_data)

        try:
            trick_user.validate()
        except BaseException, e:
            return str(e), 400

        trick_user.save()
        send_notice_about_video(trick, user_id, update_data)
        checkin_signal.send(trick_user)
        return update_data

    # выбираем последний лучший результат
    try:
        prev_checkin = app.db.trick_user.find({'user': user_id, 'trick': trick_id}).sort('cones', -1).next()
    except StopIteration:
        return _checkin(update_data)

    # поддерживаем только положительную динамику
    if prev_checkin['cones'] >= update_data['cones']:
        return u'Ни шагу назад!', 400

    # пользоавтель добавил видос - припишем его к старому чекину
    if prev_checkin['cones'] == update_data['cones']:
        app.db.trick_user.update({'user': user_id, 'trick': trick_id}, {'$set': update_data})
        send_notice_about_video(trick, user_id, update_data)
        return update_data

    # пользователь улучшил свой результат, нужно ли ему обновлять видео?
    if prev_checkin['cones'] < update_data['cones']:
        if prev_checkin['video_url'] and prev_checkin['video_url'] == update_data['video_url']:
            if need_new_video(prev_checkin['cones'], update_data['cones'], trick['score']):
                del update_data['video_url']
                del update_data['approved']
            else:
                # оставим старый видос и сохраним его статус
                update_data['approved'] = prev_checkin['approved']

        return _checkin(update_data)

    return u'Неизвестная ошибка чекина', 500


def update_checktrick_from_cookie(user_id):
    """
    Функция используется для сохранения чекина, который пользователь
    произвел до авторизации.
    """
    cookie_data = json.loads(unquote(request.cookies.get('trick')))
    cookie_data.setdefault('video_url', None)
    trick_id = int(cookie_data.pop('id'))

    update_data = {
        'cones'     : cookie_data['cones'],
        'approved'  : 0,
        'video_url' : cookie_data['video_url'],
    }

    return checkin_user(trick_id, user_id, update_data)


def need_new_video(old_cones, new_cones, score):
    """
    Нужно ли пользователю с обновлением своего результата
    также обновить и видео?
    """
    diff = new_cones - old_cones # разница
    diff_limit = (1 - score) * 100 # порог в процентах выше которого требуем обновления

    return (diff * 100 / old_cones) > diff_limit
