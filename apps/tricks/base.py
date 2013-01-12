# -*- coding: utf-8 -*-
"""
Тут должны находиться всякие низкоуровневые штуки,
относящиеся к трюкам.
"""
import simplejson as json
from urllib import unquote
from httplib import socket
from gdata.youtube import service

from flask import request

from project import app, connection, db, markdown
from apps.notify import send_notify, CHECKTRICK_WITH_VIDEO
from apps.users import get_user

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


def get_tags(*args, **kwargs):
    """
    Хэлпер, возврашаюший пропатченный список тэгов.
    """
    tags = {}
    tricks = kwargs.get('tricks', [])

    for tag in db.tag.find({'major': {'$ne': True}}):
        tag[u'tricks'] = []
        tags[tag.pop(u'_id')] = tag

    # Если передан список трюков, то к каждому тэги
    # прилепляем id его трюков, типа reverse lookup
    # TODO: в монге вероятно это как-то можно решить
    for trick in tricks:
        for tag in trick['tags']:
            try:
                tags[tag]['tricks'].append(trick[u'id'])
            except KeyError:
                continue # тэг отключен

    return tags


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
    #TODO: вероятно разделить эту функцию на 3 либо использовать ООП
    tricks = db.trick.find().sort("_id", 1)
    user_id = kwargs['user']['id'] if kwargs.get('user') else False


    best_users = {}
    user_stats = {}
    if not kwargs.get('simple'):
        # собираем лучшие чекины для каждого трюяка
        for r in get_best_results(None, user_id):
            best_users[int(r.pop(u'trick'))] = r

        # результат пользователя
        if user_id is not False:
            reduce_func = u"""function(obj, prev) { 
                prev.cones = obj.cones;
                prev.video_url = obj.video_url;
            }"""
            user_stats_qs = db.trick_user.group(['trick'], {'user': user_id}, {'cones': 0, 'video_url': ''}, reduce_func)

            for x in user_stats_qs:
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
            prev.best_user_cones = obj.cones;
            prev.best_user_id = obj.user;
        }

        prev.users.push(obj.user);

        %s

    }""" % (("if (obj.user === %s) { prev.user_do_this = true; }" % user_id) if user_id is not False else '')

    defaults = {'best_user_cones': 0, 'best_user_id': '', 'users': [], 'user_do_this': False}
    _filter = {'trick': trick_id} if trick_id else None
    best_result = db.trick_user.group(['trick'], _filter, defaults, reduce_func)

    for result in best_result:
        result.update({
            'users'        : len(set(result['users'])),
            'best_user'    : get_user(result['best_user_id']),
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
    #TODO: валидацию данных реализовать лучше
    try:
        trick_id = int(trick_id)
    except ValueError:
        return u'Incorrect trick_id = %s' % trick_id, 400

    try:
        update_data['cones'] = int(update_data['cones'])
    except ValueError:
        return 'Number of cones must be are integer', 400

    trick = db.trick.find_one({'_id': trick_id})
    if not trick:
        return u'Unknow trick with id = %s' % trick_id, 400

    def _checkin(update_data):
        update_data.update({'user': user_id, 'trick': trick_id})
        trick_user = connection.TrickUser()
        trick_user.update(update_data)
        trick_user.save()
        send_notice_about_video(trick, user_id, update_data)
        return update_data

    # выбираем последний лучший результат
    try:
        prev_checkin = db.trick_user.find({'user': user_id, 'trick': trick_id}).sort('cones', -1).next()
    except StopIteration:
        return _checkin(update_data)

    # поддерживаем только положительную динамику
    if prev_checkin['cones'] > update_data['cones']:
        return u'Ни шагу назад!', 400

    # пользоавтель добавил видос - припишем его к старому чекину
    if prev_checkin['cones'] == update_data['cones']:
        db.trick_user.update({'user': user_id, 'trick': trick_id}, {'$set': update_data})
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
