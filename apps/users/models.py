# coding: utf-8
"""
    apps.users.models
    ~~~~~~~~~~~

    Модели обосновались тут

    :copyright: (c) 2012 by zero13cool
"""
from mongokit import DocumentMigration
import simplejson as json

from project import app
from apps.common import grouped_stats, get_user_rating, BaseModel


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
    def allmigration01__add_banned(self):
        self.target = {'banned':{'$exists':False}}
        self.update = {'$set': {'banned': False}}

    def allmigration02__add_titul_feild(self):
        self.target = {'selected_titul':{'$exists':False}}
        self.update = {'$set': {'selected_titul': 0}}


class User(BaseModel):
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

        'banned'         : bool,
        'selected_titul' : int,
    }
    default_values  = {'admin': 0, 'banned': False, 'selected_titul': 0}
    required_fields = ['identity', 'provider', 'nick']
    migration_handler = UserMigration

    secure_fields = (u'identity', u'provider', u'email', u'banned', u'uid')

    @property
    def _id(self):
        """
        Dirty trick
        """
        _id = self.get('id', self.get('_id'))
        return None if _id is None else int(_id)

    @property
    def patched(self):
        """
        Patch and return (for chain) User object.
        """
        if self._patched: return self
        self.update({
            'titul': self.titul,
            'rating': self.rating,
            'id': self._id
        })
        self.pop('_id', None)
        self._patched = True
        return self
    _patched = False

    @property
    def hide(self):
        """
        Filter by secure fields
        """
        return self._hide()

    def _hide(self, data_dict=None):
        _ = data_dict or self
        return {k:v for k,v in _.items() if k not in self.secure_fields}

    @property
    def rating(self):
        return get_user_rating(self._id)

    @property
    def titul(self):
        """
        Selected titul
        """
        if self['selected_titul'] == 0: return
        achive = app.connection.Achive.find_one({"_id": self['selected_titul']})
        if not achive: return
        return achive.get_titul(self._id)

    def to_json(self, exclude_secure_fields=True):
        """
        Convert User model to json, exclude secure fields if needed
        """
        json_string = super(BaseModel, self).to_json()
        if not exclude_secure_fields: return json_string

        j = self._hide(json.loads(json_string))
        return unicode(json.dumps(j))

app.connection.register([User])
app.db.seqs.insert({'_id': 'user_seq',  'val': 0})
