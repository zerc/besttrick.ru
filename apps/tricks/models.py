# -*- coding: utf-8 -*-
import re
from datetime import datetime

from mongokit import DocumentMigration
from mongokit.schema_document import ValidationError

from project import app
from apps.common import BaseModel


__all__ = ['Trick', 'TrickUser', 'Tag']

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

def cones_value_validator(val):
    if val > 300:
        raise ValidationError(u'Cones value to big!')
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
