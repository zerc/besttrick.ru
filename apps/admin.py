# -*- coding: utf-8 -*-
import re
import urllib
import simplejson as json
from os.path import join as path_join
from pytils.translit import slugify
from functools import wraps

from flask import request, session, jsonify, escape, Markup
from mongokit import ObjectId

from project import app
from .tricks import Trick as TrickModel


def stuff_only(func):
    """
    Декоратор - "только для персонала"
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        user_id = session.get('user_id', False)
        if user_id is False:
            return 'Access Deny', 403

        user = app.db.user.find_one({'_id': user_id})

        if not user or user.get('admin', 0) <= 0:
            return 'Access Deny', 403

        return func(*args, **kwargs)

    return wrapper


def _download_thumbs(trick_id, videos_urls):
    """ По переданному идентификатору видео, скачивает тумбы с ютуба """
    url = 'http://img.youtube.com/vi/%s/%s.jpg'

    for video_url in videos_urls:
        video_id = video_url.split('/')[-1]

        for x in range(4):
            response = urllib.urlopen(url % (video_id, x))
            path = path_join(app.static_folder, 'images', 'trick%s-%s.jpg' % (trick_id, x))
            with open(path, 'wb') as f:
                f.write(response.read())


def _clean_video(url):
    """
    Приводит урл видео к безопасному виду
    """
    base_url = 'http://www.youtube.com/embed/%s'

    if 'embed' in url or 'youtu.be' in url:
        return base_url % url.split('/').pop()

    if '/watch?v=' in url:
        return base_url % re.findall(r'\?v=([^&]+)', url).pop()

    raise TypeError('Cant parse youtube url')

@app.route('/admin/trick/', methods=['POST', 'PUT', 'DELETE'])
@stuff_only
def add_trick():
    """
    Работа с трюком - создание/редактирование/удаление
    """
    # разбираем данные
    raw_trick_data = json.loads(unicode(request.data, 'utf-8'))
    trick_data = {}

    # Выбираем только нужные нам поля
    for f in TrickModel.structure.keys():
        try:
            trick_data[f] = raw_trick_data[f]
        except KeyError:
            if request.method == 'DELETE':
                continue
            else:
                raise
    
    # Роутим
    if request.method in ('PUT', 'DELETE'):
        try:
            trick_data['_id'] = int(raw_trick_data.pop('id'))
        except ValueError:
            return 'Invalid trick id', 400
    elif request.method == 'POST':
        trick_data['_id'] = app.db.seqs.find_and_modify({"_id": "tricks_seq"}, {"$inc": {"val": 1}})['val']
    
    if request.method == 'DELETE':
        app.db.trick.remove({'_id': trick_data['_id']})
        # TODO: удаление картинок и связанных данных
        return json.dumps({'success': '1'})
    
    if not hasattr(trick_data['videos'], '__iter__'):
        trick_data['videos'] = [trick_data['videos']]

    # Приведем ссылки на видео к одному виду (который потом можно ембедить безопасно)
    trick_data['videos'] = map(_clean_video, trick_data['videos'])

    # экскейпим возможные неприятности
    for field in ('descr', 'title'):
        trick_data[field] = Markup(trick_data[field]).unescape()
        trick_data[field] = escape(trick_data[field])

    new_trick = app.connection.Trick()
    new_trick.update(trick_data)

    # меняем тумбу, если поле содержит порядковый номер, а не урл
    thumb = trick_data.get('thumb', '')
    if not thumb or thumb.isdigit():
        new_trick['thumb'] = u'trick%s-%s.jpg' % (trick_data['_id'], trick_data['thumb'] or 3)

    new_trick['score'] = float(new_trick['score'])

    # качаем тумбы только при создании трюка
    if request.method == 'POST':
        _download_thumbs(trick_data['_id'], trick_data['videos'])

    new_trick.save()

    return json.dumps(trick_data)


### Чекины пользователей
@app.route('/admin/checkins_count/', methods=['GET'])
@stuff_only
def get_checkins_count():
    """
    Возвращает кол-во чекинов с неотмодерированным видео.
    """
    cond = {"$where": "this.video_url && this.approved === 0"}
    return '{"success": 1, "count": %s}' % app.db.trick_user.find(cond).count()


@app.route('/admin/checkin/<checkin_id>/', methods=['PUT'])
@stuff_only
def admin_checkin(checkin_id):
    """
    Модификация чекина.
    """
    data = json.loads(unicode(request.data, 'utf-8'))
    update = {"$set": {'approved': data['approved']}}
    app.db.trick_user.update({"_id": ObjectId(checkin_id)}, update)
    return request.data


@app.route('/admin/checkins/', methods=['GET'])
@stuff_only
def admin_checkins():
    """
    Список чекинов на модерацию.
    """
    checkins = app.db.trick_user.find({"$where": "this.video_url"}).sort('time_added', -1)

    def _(checkin):
        checkin['id'] = '%s' % checkin.pop('_id')
        checkin['time_added'] = '%s' % checkin['time_added']

        # подсасываем кое-какие данные
        checkin['username'] = app.db.user.find_one({'_id': checkin['user']})['nick']
        checkin['trick_title'] = app.db.trick.find_one({'_id': checkin['trick']})['title']

        return checkin

    return json.dumps(map(_, checkins))


@app.route('/admin/user/<int:user_id>/', methods=['PUT'])
@stuff_only
def manage_user(user_id):
    data = json.loads(unicode(request.data, 'utf-8'))
    app.db.user.find_and_modify({'_id': user_id}, data)
    return '{"success":1}'
