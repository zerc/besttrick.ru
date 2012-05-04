# -*- coding: utf-8 -*-
import simplejson as json
from datetime import datetime
from pytils.utils import takes, one_of

from flask import render_template, request, jsonify, session, redirect, url_for
from mongokit import Document, DocumentMigration

from project import app, connection, db
from .utils import grouped_stats


### Models
class TrickMigration(DocumentMigration):
    def migration01__add_tags(self):
        self.target = {'tags':{'$exists':False}}
        self.update = {'$set':{'tags': [unicode]}}

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


class TrickUser(Document):
    __database__   = app.config['MONGODB_DB']
    __collection__ = "trick_user"

    structure = {
        'user'       : int,
        'trick'      : unicode,
        'cones'      : int,
        'approved'   : bool,
        'time_added' : datetime,
    }

    indexes = [{'fields':['user', 'trick']}]

    default_values  = {'cones': 0, 'approved': False, 'time_added': datetime.now}
    required_fields = ['user', 'trick']
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
@app.route('/trick/full/<trick_id>/', methods=['GET'])
def trick_full(trick_id):
    """ Лучшие пользователи по этому трюку """
    rows = grouped_stats('user', {'trick': trick_id})
    return json.dumps(sorted(rows, key=lambda x: x['cones'], reverse=True))


@app.route('/trick/', methods=['PUT'])
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

    if trick_user:
        db.trick_user.update({'user': user_id, 'trick': trick_data['_id']}, {'$set': {
            'cones': int(trick_data['cones']),
        }})
    else:
        trick_user = connection.TrickUser()
        trick_user['user'] = user_id
        trick_user['trick'] = trick_data['_id']
        trick_user['cones'] = int(trick_data['cones'])
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
