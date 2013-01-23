# -*- coding: utf-8 -*-
import urllib
import simplejson as json
from functools import wraps
from mongokit import Document, DocumentMigration

from flask import render_template, request, jsonify, session, url_for
from project import app, connection, db
from .utils import grouped_stats, get_user_rating, get_valid_cones_per_trick, redirect


def adding_user(func):
    """
    Подсовывает в kwargs функции объект пользователя,
    если тот авторизован, иначе - это просто False.
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        user_id = session.get('user_id')

        kwargs['user'] = get_user(user_id)
        #TODO: инкапсулировать в пользователя
        kwargs['user_admin_lvl'] = kwargs['user']['admin'] if kwargs['user'] else 0

        return func(*args, **kwargs)

    return wrapper


def user_only(func):
    """
    Декоратор - "только для пользователя"
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        user_id = session.get('user_id', False)
        if user_id is False:
            return redirect('index')

        user = db.user.find_one({'_id': user_id})

        if not user or user['banned']:
            return 'Access Deny', 403

        return func(*args, **kwargs)

    return wrapper



def clean_fields(user_dict):
    """
    Убирает из словаря с данными пользователя некоторые "секьюрные" поля.
    Просто чтобы не палить их на клиенте.
    """
    for field in (u'identity', u'provider', u'email', u'banned', u'uid'):
        try:
            user_dict.pop(field)
        except KeyError:
            continue

    return user_dict


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
            'email'     : u'',
            'full_name' : u'',
            'city'      : u'',
            'icq'       : u'',
            'skype'     : u'',
            'phone'     : u'',
            'bio'       : u'',
        }}

    def migration02__add_rolls_and_exps_feilds(self):
        self.target = {'rolls':{'$exists':False}}
        self.update = {'$set': {
            'rolls' : u'',
            'epxs'  : u'',
        }}

    def allmigration01__add_banned_feild(self):
        self.target = {'banned':{'$exists':False}}
        self.update = {'$set': {'banned': False}}


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

        'banned'    : bool,
    }
    default_values  = {'admin': 0, 'banned': False}
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


def get_user(user_id=None, full=False, user_dict=None):
    """
    Хэлпер возвращает пропатченый объект юзера.
    Если указан user_dict - то не делает выборку из монги,
    а использует эти данные.
    """
    if user_dict is None:
        user = db.user.find_one({'_id': user_id}) or False
        if user is False: return False
    else:
        user = user_dict

    user['id'] = int(user.pop('_id'))
    user['rating'] = get_user_rating(user['id'])

    return user if full else clean_fields(user)


### Views
@app.route('/banned/')
def banned():
    return render_template('banned.html')


@app.route('/login/', methods=['POST'], subdomain="<domain>")
def login(domain):
    url = "http://loginza.ru/api/authinfo?%s"
    params = urllib.urlencode({'token': request.form['token'], 'id': '', 'sig': ''})
    f = urllib.urlopen(url % params)

    if f.getcode() != 200:
        raise TypeError(u'Loginza response code = %s' % f.getcode())

    user_data = json.loads(unicode(f.read(), 'utf-8'))
    user = db.user.find_one({'identity': user_data['identity']}) or register(user_data)

    if user['banned']: return redirect('banned')
    
    session['user_id'] = user['_id']
    return redirect('index', domain)



@app.route('/logout/', methods=['GET'])
@app.route('/logout/', methods=['GET'], subdomain="m")
def logout():
    session.pop('user_id', None)
    return redirect('index')


@app.route('/my/tricks/', methods=['GET'])
@user_only
def my_tricks():
    user_id = session.get('user_id', False)
    if user_id is False:
        return 

    rows = grouped_stats('trick', {'user': user_id})
    return json.dumps(sorted(rows, key=lambda x: x['cones'], reverse=True))


@app.route('/user/', methods=['PUT', 'GET'])
@user_only
def my():
    user_id = session['user_id'] 

    if request.method == 'PUT':
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

    user = db.user.find_one({'_id': user_id})
    user['rating'] = get_user_rating(user_id)
    return json.dumps(user)


@app.route('/profile/<user_id>/')
def user_profile(user_id):
    context = {}

    try:
        user = db.user.find_one({'_id': int(user_id)})
        if not user: raise TypeError
    except TypeError:
        return 'Unknow user', 403

    user['rating'] = get_user_rating(user['_id'])
    context['user'] = clean_fields(user)

    user_tricks = grouped_stats('trick', {'user': int(user_id)})
    context['tricks'] = sorted(user_tricks, key=lambda x: x['cones'], reverse=True)

    return json.dumps(context)

#TODO: cached this!
@app.route('/rating/', methods=['GET'])
def top_users():
    tricks_scores = {}
    for trick in db.trick.find():
        tricks_scores[trick['_id']] = trick['score']

    def _(user):
        return get_user(user_dict=user)

    users = map(_, db.user.find({'banned': False}))
    return json.dumps(sorted(users, key=lambda user: user['rating'], reverse=True))


@app.route('/users/', methods=['GET'])
@user_only
def list_of_users():
    is_admin = not not db.user.find_one({'_id': session['user_id']})['admin']

    def _(user):
        user['id'] = user.pop('_id')
        return user if is_admin else clean_fields(user)

    return json.dumps([_(dict(user)) for user in db.user.find().sort("_id", -1)])
