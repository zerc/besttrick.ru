# -*- coding: utf-8 -*-
import urllib
import simplejson as json
from mongokit import Document, DocumentMigration

from flask import render_template, request, jsonify, session, redirect, url_for
from project import app, connection, db
from .utils import grouped_stats

def get_field(d, field_name):
    """ Использует точечную нотацию в имени поля, для работы со вложенными словарями """
    parts = field_name.split('.')
    value = d.get(parts[0], u'')

    if not isinstance(value, dict):
        return value

    for part in parts[1:]:
        try:
            value = value[part]
        except KeyError:
            return ''
    return value


### Models            
LOGINZA_FIELDS_MAP = {
    # me            # loginza
    'icq'           : 'im.icq',
    'nick'          : 'nickname',
    'city'          : 'address.home.city',
    'phone'         : 'phone.preferred',
    'skype'         : 'im.skype',
    'full_name'     : 'name.full_name',
    'bio'           : 'biography',
}

class UserMigration(DocumentMigration):
    def migration01__add_some_fields(self):
        self.target = {'email':{'$exists':False}}
        self.update = {'$set':{
            'email'     : unicode,
            'full_name' : unicode,
            'city'      : unicode,
            'icq'       : unicode,
            'skype'     : unicode,
            'phone'     : unicode,
            'bio'       : unicode,
        }}

    def migration02__add_rolls_and_exps_feilds(self):
        self.target = {'rolls':{'$exists':False}}
        self.update = {'$set': {
            'rolls': unicode,
            'epxs': unicode,
        }}


class User(Document):
    __database__     = app.config['MONGODB_DB']
    __collection__   = u'user'
    use_dot_notation = True

    structure = {
        'admin'     : int,
        'identity'  : unicode,
        'provider'  : unicode,
        'nick'      : unicode,

        'email'     : unicode,
        'full_name' : unicode,
        'city'      : unicode,
        'icq'       : unicode,
        'skype'     : unicode,
        'phone'     : unicode,
        'uid'       : unicode,
        'team'      : unicode,
        'photo'     : unicode,
        'bio'       : unicode,
        'rolls'     : unicode,
        'epxs'      : unicode,
    }
    default_values  = {'admin': 0}
    required_fields = ['identity', 'provider', 'nick']
    migration_handler = UserMigration
connection.register([User])
db.seqs.insert({'_id': 'user_seq',  'val': 0})


### Helpers
def register(user_data):
    # HACK: если нет никнейма, конструируем его
    if not user_data.get(u'nickname'):
        user_data[u'nickname'] = u' '.join([user_data['name'].get('first_name', ''), user_data['name'].get('last_name')])

    new_user = connection.User()
    for k, t in User.structure.items():
        if k == 'admin':
            continue

        try:
            new_user[k] = t(get_field(user_data, LOGINZA_FIELDS_MAP.get(k, k)))
        except KeyError:
            continue


    new_user['_id'] = db.seqs.find_and_modify({"_id": "user_seq"}, {"$inc": {"val": 1}})['val']
    new_user.save()
    return new_user


### Views
@app.route('/login/', methods=['POST'])
def login():
    url = "http://loginza.ru/api/authinfo?%s"
    params = urllib.urlencode({'token': request.form['token'], 'id': '', 'sig': ''})
    f = urllib.urlopen(url % params)

    if f.getcode() != 200:
        raise TypeError(u'Loginza response code = %s' % f.getcode())

    user_data = json.loads(unicode(f.read(), 'utf-8'))
    user = db.user.find_one({'identity': user_data['identity']}) or register(user_data)

    session['user_id'] = user['_id']

    return redirect(url_for('index'))


@app.route('/logout/', methods=['GET'])
def logout():
    session.pop('user_id', None)
    return redirect(url_for('index'))


@app.route('/my/tricks/', methods=['GET'])
def my_tricks():
    user_id = session.get('user_id', False)
    if user_id is False:
        return redirect(url_for('index'))

    rows = grouped_stats('trick', {'user': user_id})
    return json.dumps(sorted(rows, key=lambda x: x['cones'], reverse=True))


@app.route('/user/', methods=['PUT', 'GET'])
def my():
    user_id = session.get('user_id', False)
    if user_id is False:
        return redirect(url_for('index'))

    params = json.loads(unicode(request.data, 'utf-8'))
    params.pop('id', None)
    params.pop('_id', None)

    # типа валидация перед апдейтом данных
    for p in params.keys():
        try:
            User.structure[p]
        except KeyError:
            del params[p]

    db.user.update({'_id': user_id}, {'$set': params})
    
    return '{"success":1}'


@app.route('/profile/<user_id>/')
def user_profile(user_id):
    context = {}

    try:
        user = db.user.find_one({'_id': int(user_id)})
        if not user: raise TypeError
    except TypeError:
        return 'Unknow user', 403

    context['user'] = user

    user_tricks = grouped_stats('trick', {'user': int(user_id)})
    context['tricks'] = sorted(user_tricks, key=lambda x: x['cones'], reverse=True)

    return json.dumps(context)

