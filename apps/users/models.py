# coding: utf-8
"""
    apps.users.models
    ~~~~~~~~~~~

    Модели обосновались тут

    :copyright: (c) 2012 by zero13cool
"""
from mongokit import Document, DocumentMigration

from project import app
from apps.utils import grouped_stats, get_user_rating


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
app.connection.register([User])
app.db.seqs.insert({'_id': 'user_seq',  'val': 0})
