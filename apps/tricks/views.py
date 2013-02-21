# -*- coding: utf-8 -*-
import simplejson as json
from gdata import media, youtube

from flask import render_template, request, jsonify, session, redirect, url_for, make_response, flash, g
from flask.views import View
from project import app, markdown

from apps.utils import grouped_stats, allow_for_robot, is_robot, render_to
from apps.users import user_only, get_user

from .base import yt_service, checkin_user, checkin_user, get_tricks, get_trick, get_best_results


@user_only
def prepare_youtube_upload(*args, **kwargs):
    """
    Обращается к YouTube чтобы получить url загрузки видео,
    который будет использоваться в форме на сайте.
    """
    if yt_service is None:
        return 'YouTube is unavilible now', 403

    try:
        trick_id = int(request.args['trick_id'])
    except (KeyError, TypeError, ValueError):
        return 'Bad trick_id', 403

    trick = app.db.trick.find_one({'_id': trick_id})
    if not trick:
        return 'Unknow trick with id = %s' % trick_id, 403

    # create media group as usual
    my_media_group = media.Group(
        title=media.Title(text = u'Besttrick video: %s' %  trick['title']),
        description=media.Description(description_type = 'plain', text = u'Raider: %s' % g.user['nick']),
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


@user_only
def check(trick_id, *args, **kwargs):
    """
    Вью выполняет чекин пользователя.
    TODO: разбить функцию на более мелкие и прояснить логику.
    """
    trick_data = json.loads(unicode(request.data, 'utf-8'))

    try:
        trick_data['cones'] = int(trick_data['cones'])
    except TypeError:
        return 'Number of cones must be are integer', 400
    
    update_data = {
        'cones'     : int(trick_data['cones']), 
        'video_url' : unicode(trick_data['video_url']) if trick_data.get('video_url') else None,
        'approved'  : 0,
    }

    checkin_result = checkin_user(trick_id, g.user['id'], update_data)

    if isinstance(checkin_result, tuple):
        return checkin_result

    return json.dumps(get_best_results(trick_id))


@render_to()
@user_only
def checkin_page(*args, **context):
    """
    Мобильная страничка чекина.
    """
    if request.method == 'GET':
        context.update({
            'tricks': get_tricks(simple=True),
        })

        return context

    #TODO объеденить в функцией checktrick
    form_data = request.form.to_dict()
    trick_id  = form_data.pop('trick_id')
    ref       = form_data.pop('ref')

    checkin_result = checkin_user(trick_id, g.user['id'], form_data)

    if isinstance(checkin_result, tuple):
        flash(checkin_result[0], 'error')
    else:
        flash(u'Вы успешно зачекинились', 'success')

    return redirect(ref or url_for('mobile_checkin_page'))

  
@render_to()
@allow_for_robot
def trick_page(trick):
    """ Страничка трюка :) """
    return {'trick': trick}
    


@render_to()
def tricks_list(*args, **kwargs):
    """
    Возврващет список трюков в формате json.
    Используюется в качеству url для коллекции трюков со стороны js.
    """
    return {'tricks_list': get_tricks(*args, **kwargs)}
