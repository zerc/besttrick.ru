# -*- coding: utf-8 -*-
import re
import simplejson as json
from datetime import datetime
from pytils.utils import takes, one_of
from httplib import socket
from urllib import unquote

from flask import render_template, request, jsonify, session, redirect, url_for
from mongokit import Document, DocumentMigration
from mongokit.schema_document import ValidationError

from project import app, connection, db
from .utils import grouped_stats, allow_for_robot, is_robot
from .notify import send_notify, CHECKTRICK_WITH_VIDEO, NOT_PROCESSES, GOOD, BAD
from .users import user_only

from gdata.youtube import service
from gdata import media, youtube


# авторизуемся на ютубе, чтобы заливать видосы
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


### Utils
def get_best_results(trick_id=None, user_id=False):
    """
    Возвращает словарь лучших результатов (структура как у trick_user) 
    по указанному трюку или список словарей по всем трюкам.
    """
    reduce_func = u"""
    function(obj, prev) {
        if (prev.best_user_cones < obj.cones) {
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
            'best_user'    : db.user.find_one({'_id': result['best_user_id']}),
        })

    return result if trick_id >= 0 else best_result


def checkin_user(update_data):
    trick_user = connection.TrickUser()
    trick_user.update(update_data)
    trick_user.save()

    return get_best_results(update_data['trick'], update_data['user'])


def update_checktrick_from_cookie(user_id):
    """
    Функция используется для сохранения чекина, который пользователь
    произвел до авторизации.

    TODO: как-то объеденить с глобальной опцией чекина, а то получается копипаст кусков
    """
    cookie_data = json.loads(unquote(request.cookies.get('trick')))
    cookie_data['user'] = user_id
    cookie_data['trick'] = cookie_data.pop('id')

    trick_user = connection.TrickUser()

    for k in cookie_data.keys():
        if k not in trick_user.structure: del cookie_data[k]

    if db.trick_user.find_one(cookie_data):
        return

    # выбираем последний лучший результат
    try:
        prev_checkin = db.trick_user.find({
                'user': cookie_data['user'], 'trick': cookie_data['trick']
            }).sort('cones', -1).next()
    except StopIteration:
        prev_checkin = None

    # поддерживаем только положительную динамику
    if prev_checkin and prev_checkin['cones'] > cookie_data['cones']: return 

    trick_user.update(cookie_data)
    trick_user.save()


### Validators
def positive_integer(val):
    if val <= 0:
        raise ValidationError(u'%s cones must be > 0')
    return True

youtube_re = re.compile(r'^(http|https):\/\/(www\.youtube\.com|youtu.be)\/[a-zA-Z0-9\?&\/=\-]+$', re.S|re.I)
def is_youtube_link(val):
    if val and not youtube_re.findall(val):
        raise ValidationError(u'%s is not youtube link!')
    return True

### Models
class Trick(Document):
    __database__   = app.config['MONGODB_DB']
    __collection__ = "trick"

    structure = {
        'title'      : unicode,
        'direction'  : unicode,
        'thumb'      : unicode,
        'videos'     : [unicode],
        'descr'      : unicode,
        'score'      : float,
        'wssa_score' : float,
        'tags'       : [unicode],
    }
    default_values  = {'thumb': u'3', 'score': 1.0, 'wssa_score': 0.0}
    required_fields = ['title']
    indexes = [{'fields': ['tags']}]
connection.register([Trick])
db.seqs.insert({'_id': 'tricks_seq',  'val': 0})


class TrickUser(Document):
    __database__   = app.config['MONGODB_DB']
    __collection__ = "trick_user"

    structure = {
        'user'       : int,
        'trick'      : int,
        'cones'      : int,
        'approved'   : int,
        'video_url'  : unicode,
        'time_added' : datetime,
    }

    indexes = [{'fields':['user', 'trick', 'cones']}]
    default_values  = {'cones': 0, 'approved': 0, 'time_added': datetime.now}
    required_fields = ['user', 'trick']

    validators = {
        'cones'     : positive_integer,
        'video_url' : is_youtube_link,
    }
connection.register([TrickUser])


class Tag(Document):
    __database__   = app.config['MONGODB_DB']
    __collection__ = "tag"

    structure = {
        'title': unicode,
        'major': bool,
    }
    default_values  = {'major': False}
    required_fields = ['title']
connection.register([Tag])


def need_new_video(old_cones, new_cones, score):
    """
    Нужно ли пользователю с обновлением своего результата
    также обновить и видео?
    """
    diff = new_cones - old_cones # разница
    diff_limit = (1 - score) * 100 # порог в процентах выше которого требуем обновления

    return (diff * 100 / old_cones) > diff_limit


### Views
@app.route('/prepare_youtube_upload/', methods=['GET'])
def prepare_youtube_upload():
    # TODO: вынести проверку на авторизованность в декоратор
    user_id = session.get('user_id', False)
    if user_id is False:
        return 'Access Deny', 403

    if yt_service is None:
        return 'YouTube is unavilible now', 403

    user = db.user.find_one({'_id': user_id})

    try:
        trick_id = request.args['trick_id']
    except (KeyError, TypeError):
        return 'Bad trick_id', 403

    trick = db.trick.find_one({'_id': int(trick_id)})
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


@app.route('/trick<trick_id>/', methods=['GET'])
@allow_for_robot
def trick_full(trick_id):
    """ Лучшие пользователи по этому трюку """
    rows = grouped_stats('user', {'trick': int(trick_id)})
    rows = sorted(rows, key=lambda x: x['cones'], reverse=True)
    
    if is_robot():
        return {
            'trick_users': rows,
            'trick': db.trick.find_one({'_id': int(trick_id)})
        }

    return json.dumps(rows)


@app.route('/checktrick/', methods=['PUT'])
@user_only
def checktrick():
    user_id = int(session.get('user_id', False))

    trick_data = json.loads(unicode(request.data, 'utf-8'))
    trick_data['_id'] = trick_id = trick_data.pop('id')

    try:
        trick_data['cones'] = int(trick_data['cones'])
    except TypeError:
        return 'Number of cones must be are integer', 400
    
    trick = db.trick.find_one({'_id': trick_id})

    if not trick:
        return u'Unknow trick with id = %s' % trick_id, 400
    
    update_data = {
        'cones'     : int(trick_data['cones']), 
        'video_url' : unicode(trick_data['video_url']) if trick_data.get('video_url') else None,
        'approved'  : 0,
    }
    
    def send_notice_about_video():
        if update_data.get('video_url'):
            notify_data = dict(**trick_data)
            notify_data.update({
                'user'      : user_id,
                'trick'     : notify_data.pop('_id'),
                'trickname' : notify_data.pop('title')
            })
            send_notify(notify_type=CHECKTRICK_WITH_VIDEO, data=notify_data)

    # выбираем последний лучший результат
    try:
        prev_checkin = db.trick_user.find({'user': user_id, 'trick': trick_id}).sort('cones', -1).next()
    except StopIteration:
        prev_checkin = None

    # поддерживаем только положительную динамику
    if prev_checkin and prev_checkin['cones'] > update_data['cones']:
        return u'Ни шагу назад!', 400

    # скорее всего пользоавтель добавил видос - припишем его к старому чекину
    if prev_checkin and prev_checkin['cones'] == update_data['cones']:
        db.trick_user.update({'user': user_id, 'trick': trick_id}, {'$set': update_data})
        send_notice_about_video()
        return json.dumps(trick_data)

    # пользователь улучшил свой результат, нужно ли ему обновлять видео?
    if prev_checkin and prev_checkin['video_url'] == update_data['video_url']:
        if need_new_video(prev_checkin['cones'], update_data['cones'], trick['score']):
            del update_data['video_url']
            del update_data['approved']
        else:
            # оставим старый видос и сохраним его статус
            update_data['approved'] = prev_checkin['approved']

    update_data.update({'user': user_id, 'trick': trick_id})
    trick_data.update(checkin_user(update_data))
    send_notice_about_video()

    return json.dumps(trick_data)


@app.route('/tricks/', methods=['GET'])
def tricks_list():
    def _path(trick):
        trick['id'] = trick.pop('_id')
        return trick

    tricks = map(_path, db.trick.find())
    return json.dumps(tricks)
