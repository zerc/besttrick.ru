# -*- coding: utf-8 -*-
import re
import simplejson as json
from datetime import datetime
from pytils.utils import takes, one_of

from flask import render_template, request, jsonify, session, redirect, url_for
from mongokit import Document, DocumentMigration
from mongokit.schema_document import ValidationError

from project import app, connection, db
from .utils import grouped_stats

from gdata.youtube import service
from gdata import media, youtube


# авторизуемся на ютубе, чтобы заливать видосы
yt_service = service.YouTubeService()
yt_service.email = app.config['G_EMAIL'] 
yt_service.password = app.config['G_PASSWORD'] 
yt_service.source = app.config['G_SOURCE'] 
yt_service.developer_key = app.config['G_DEV_KEY'] 
yt_service.client_id = app.config['G_SOURCE']
yt_service.ProgrammaticLogin()


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


class TrickUserMigration(DocumentMigration):
    def migration01__add_video_url(self):
        self.target = {'video_url':{'$exists':False}}
        self.update = {'$set':{'video_url': unicode}}

class TrickUser(Document):
    __database__   = app.config['MONGODB_DB']
    __collection__ = "trick_user"

    structure = {
        'user'       : int,
        'trick'      : unicode,
        'cones'      : int,
        'approved'   : bool,
        'video_url'  : unicode,
        'time_added' : datetime,
    }

    indexes = [{'fields':['user', 'trick']}]
    default_values  = {'cones': 0, 'approved': False, 'time_added': datetime.now}
    required_fields = ['user', 'trick']
    migration_handler = TrickUserMigration

    validators = {
        'cones': positive_integer,
        'video_url': is_youtube_link,
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


### Views
@app.route('/prepare_youtube_upload/', methods=['GET'])
def prepare_youtube_upload():
    # TODO: вынести проверку на авторизованность в декоратор
    user_id = session.get('user_id', False)
    if user_id is False:
        return 'Access Deny', 403

    user = db.user.find_one({'_id': user_id})

    try:
        trick_id = request.args['trick_id']
    except (KeyError, TypeError):
        return 'Bad trick_id', 403

    trick = db.trick.find_one({'_id': unicode(trick_id)})
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


@app.route('/trick/full/<trick_id>/', methods=['GET'])
def trick_full(trick_id):
    """ Лучшие пользователи по этому трюку """
    rows = grouped_stats('user', {'trick': trick_id})
    return json.dumps(sorted(rows, key=lambda x: x['cones'], reverse=True))


@app.route('/checktrick/', methods=['PUT'])
def trick():
    user_id = session.get('user_id', False)

    if user_id is False:
        return 'Access Deny', 403

    trick_data = json.loads(unicode(request.data, 'utf-8'))
    trick_data['_id'] = trick_data.pop('id')

    try:
        trick_data['cones'] = int(trick_data['cones'])
    except TypeError:
        return 'Number of cones must be are integer', 400


    trick_user = db.trick_user.find_one({'user': user_id, 'trick': trick_data['_id']})
    update_data = {
        'cones': int(trick_data['cones']),
    }
    
    if trick_data.get('video_url'):
        update_data['video_url'] = unicode(trick_data['video_url'])

    if trick_user:
        db.trick_user.update({'user': user_id, 'trick': trick_data['_id']}, {'$set': update_data})
    else:
        trick_user = connection.TrickUser()
        trick_user['user'] = user_id
        trick_user['trick'] = trick_data['_id']
        trick_user.update(update_data)
        trick_user.save()

    # TODO: срефакторить это в универсальную функциюю, так как
    # нечто подобное используется на главной
    # Проверим не изменился ли король этого трюка
    # лучшие результаты по трюкам + общее число делающих пользователей
    reduce_func = u"""
    function(obj, prev) {
        if (prev.best_user_cones < obj.cones) {
            prev.best_user_cones = obj.cones;
            prev.best_user_id = obj.user;
        }
        prev.users += 1;
    }"""
    best_result = db.trick_user.group(['trick'], {'trick': trick_data['_id']}, {'best_user_cones': 0, 'best_user_id': '', 'users': 0, 'can_mark': not not user_id}, reduce_func)[0]
    trick_data.update(best_result)
    trick_data['best_user'] = db.user.find_one({'_id': best_result['best_user_id']})
    trick_data['user_do_this'] = True

    return json.dumps(trick_data)


@app.route('/tricks/', methods=['GET'])
def tricks_list():
    def _path(trick):
        trick['id'] = trick.pop('_id')
        return trick

    tricks = map(_path, db.trick.find())
    return json.dumps(tricks)
