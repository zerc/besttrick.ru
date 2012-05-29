# -*- coding: utf-8 -*-
import re
import urllib
import simplejson as json
from os.path import join as path_join
from pytils.translit import slugify

from project import app, db, connection
from .tricks import Trick as TrickModel
from flask import request, session


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
        return base_url % re.findall(r'watch\?v=([a-zA-Z0-9\?\/=\-]+)&', url).pop()

    raise TypeError('Cant parse youtube url')


@app.route('/admin/trick/', methods=['POST', 'PUT', 'DELETE'])
def add_trick():
    """
    Работа с трюком - создание/редактирование/удаление
    """
    ## TODO: разделить на отдельные функции

    # проверям пользователя
    user_id = session.get('user_id', False)
    if user_id is False:
        return 'Access Deny', 403

    user = db.user.find_one({'_id': user_id})

    if not user or user.get('admin', 0) <= 0:
        return 'Access Deny', 403

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
        trick_data['_id'] = db.seqs.find_and_modify({"_id": "tricks_seq"}, {"$inc": {"val": 1}})['val']
    
    if request.method == 'DELETE':
        db.trick.remove({'_id': trick_data['_id']})
        # TODO: удаление картинок и связанных данных
        return json.dumps({'success': '1'})
    
    if not hasattr(trick_data['videos'], '__iter__'):
        trick_data['videos'] = [trick_data['videos']]

    # Приведем ссылки на видео к одному виду (который потом можно ембедить безопасно)
    trick_data['videos'] = map(_clean_video, trick_data['videos'])

    new_trick = connection.Trick()
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
