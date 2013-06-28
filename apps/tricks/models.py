# -*- coding: utf-8 -*-
import re
from datetime import datetime

from mongokit import DocumentMigration
from mongokit.schema_document import ValidationError
import simplejson as json

from project import app
from apps.common import BaseModel

from .base import get_best_results


__all__ = ['Trick', 'TrickUser', 'Tag']

### Validators
def positive_integer(val):
    try:
        if int(val) <= 0:
            raise ValidationError(u'%s cones must be > 0')
    except (ValueError, TypeError), e:
        raise ValidationError(u'Value must be integer')
    return True

youtube_re = re.compile(r'^(http|https):\/\/(www\.youtube\.com|youtu.be)\/[a-zA-Z0-9\?&\/=\-]+$', re.S|re.I)
def is_youtube_link(val):
    if val and not youtube_re.findall(val):
        raise ValidationError(u'%s is not youtube link!')
    return True

def cones_value_validator(val):
    if val > 300:
        raise ValidationError(u'%s value to big!')
    return True


### Models
class Trick(BaseModel):
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

    @property
    def checkins(self):
        return app.connection.TrickUser.find({'trick': self._id})

    @property
    def best_checkin(self):
        return list(app.connection.TrickUser.find({'trick': self._id}).sort('cones', -1))[0]

    @property
    def users_count(self):
        return len(set([ch['user'] for ch in self.checkins]))

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
        Patch and return (for chain) object.
        """
        if self._patched: return self
        self.update({
            'id': self._id
        })
        self.pop('_id', None)
        self._patched = True
        return self
    _patched = False
app.connection.register([Trick])
app.db.seqs.insert({'_id': 'tricks_seq',  'val': 0})


class TrickUser(BaseModel):
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
        'cones'     : [positive_integer, cones_value_validator],
        'video_url' : is_youtube_link,
    }

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
        Patch and return (for chain) object.
        """
        if self._patched: return self
        self.pop('_id', None)
        self._patched = True
        return self
    _patched = False
app.connection.register([TrickUser])


class Tag(BaseModel):
    __collection__ = "tag"
    
    structure = {
        'title': unicode,
        'major': bool,
    }
    default_values  = {'major': False}
    required_fields = ['title']
app.connection.register([Tag])
