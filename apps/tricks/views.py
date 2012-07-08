# -*- coding: utf-8 -*-
import simplejson as json
from gdata import media, youtube

from flask import render_template, request, jsonify, session, redirect, url_for
from project import app, connection, db, markdown

from apps.utils import grouped_stats, allow_for_robot, is_robot
from apps.notify import send_notify, CHECKTRICK_WITH_VIDEO, NOT_PROCESSES, GOOD, BAD
from apps.users import user_only, adding_user

from .base import yt_service, checkin_user, checkin_user, get_tricks, get_best_results


@app.route('/prepare_youtube_upload/', methods=['GET'])
@adding_user
@user_only
def prepare_youtube_upload(*args, **kwargs):
    """
    Обращается к YouTube чтобы получить url загрузки видео,
    который будет использоваться в форме на сайте.
    """

    if yt_service is None:
        return 'YouTube is unavilible now', 403

    user = kwargs['user']

    try:
        trick_id = int(request.args['trick_id'])
    except (KeyError, TypeError, ValueError):
        return 'Bad trick_id', 403

    trick = db.trick.find_one({'_id': trick_id})
    if not trick:
        return 'Unknow trick with id = %s' % trick_id, 403

    # create media group as usual
    my_media_group = media.Group(
        title=media.Title(text = u'Besttick video: %s' %  trick['title']),
        description=media.Description(description_type = 'plain', text = u'Raider: %s' % user['nick']),
        keywords=media.Keywords(text=u", ".join(trick['tags'])),
        category=[media.Category(text='Sports', scheme='http://gdata.youtube.com/schemas/2007/categories.cat', label=u'Спорт')],
        player=None
    )

    # create video entry as usual
    video_entry = youtube.YouTubeVideoEntry(media=my_media_group)

    # upload meta data only
    response = yt_service.GetFormUploadToken(video_entry)

    # parse response tuple and use the variables to build a form (see next code snippet)
    post_url, token = response

    return jsonify({'post_url': post_url, 'token': token})


@app.route('/checktrick/', methods=['PUT'])
@adding_user
@user_only
def checktrick(*args, **kwargs):
    """
    Вью выполняет чекин пользователя.
    TODO: разбить функцию на более мелкие и прояснить логику.
    """
    user_id = kwargs['user']['id']

    trick_data = json.loads(unicode(request.data, 'utf-8'))
    trick_data['_id'] = trick_id = int(trick_data.pop('id'))

    try:
        trick_data['cones'] = int(trick_data['cones'])
    except TypeError:
        return 'Number of cones must be are integer', 400
    
    update_data = {
        'cones'     : int(trick_data['cones']), 
        'video_url' : unicode(trick_data['video_url']) if trick_data.get('video_url') else None,
        'approved'  : 0,
    }

    checkin_result = checkin_user(trick_id, user_id, update_data)

    if isinstance(checkin_result, tuple):
        return checkin_result

    return json.dumps(get_best_results(trick_id))


@app.route('/trick<int:trick_id>/', methods=['GET'])
@allow_for_robot
def trick_full(trick_id):
    """ Лучшие пользователи по этому трюку """
    trick_id = int(trick_id)
    rows = grouped_stats('user', {'trick': trick_id})
    rows = sorted(rows, key=lambda x: x['cones'], reverse=True)
    
    if is_robot():
        return {
            'trick_users': rows,
            'trick': db.trick.find_one({'_id': trick_id})
        }

    return json.dumps(rows)


@app.route('/api/tricks/', methods=['GET'])
@adding_user
def tricks_list(*args, **kwargs):
    """
    Возврващет список трюков в формате json.
    Используюется в качеству url для коллескции трюков
    со стороны js.
    """
    tricks = get_tricks(*args, **kwargs)
    return json.dumps(tricks)
