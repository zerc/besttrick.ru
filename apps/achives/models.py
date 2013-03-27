# coding: utf-8
from datetime import datetime

from project import app, cached_property
from apps.common import BaseModel

__all__ = ['Achive', 'SimpleEvent', 'ComplexEvent']


class Achive(BaseModel):
    __collection__ = "achive"

    structure = {
        'title'      : unicode,
        'descr'      : unicode,
        'icon'       : unicode,
        'score'      : float,
        'trick_id'   : int,                        
        'rule'       : {unicode: []},
        'parents'    : [], 
    }
    default_values  = {'score': 1.0, 'parents': []}
    required_fields = ['title', 'descr']
    indexes = [{'fields': ['trick_id']}]

    @property
    def _event_cls(self):
        rule_to_class_map = {
            'cones'   : 'SimpleEvent',
            'complex' : 'ComplexEvent'
        }
        return getattr(app.connection, rule_to_class_map[self.get('rule').keys()[0]])

    def get_events(user_id):
        params = {"user_id": user_id, "achive_id": int(self.get("_id"))}
        return app.connection.Event.fetch(params)

    def test(self, value):
        return self._event_cls.test(self.get('rule'), value)

    def get_event_or_dummy(self, user_id):
        params  = {'user_id': user_id, 'achive_id': int(self.get("_id"))}
        event = self._event_cls.fetch_one(params.copy())
        
        if not event:
            event = self._event_cls()
            event.update(params)

        try:
            event._property_cache['achive'] = self # переписать с методом __set__
        except AttributeError:
            event._property_cache = {'achive': self}

        return event
        
    def do(self, user_id, value):
        event = self.get_event_or_dummy(user_id)
        event.update({'progress': [value]})
        event.save()
        return event

    def do_parents(self, user_id):
        event = self.get_event_or_dummy(user_id)
        parents = app.connection.Achive.fetch({"_id": {"$in": self.get('parents')}})
        _ = lambda a: unicode(int(a))

        for p in parents:
            e = p.get_event_or_dummy(user_id)

            current_progress = e.get('progress', [])

            if not current_progress:
                current_progress.append({
                    _(self.get("_id")): event.get('level')
                })
            else:
                current_progress[0][_(self.get("_id"))] = event.get('level')

            e.update({'progress': current_progress})
            e.save()
app.connection.register([Achive])
app.db.seqs.insert({'_id': 'achives_seq',  'val': 0})


class BaseEvent(BaseModel):
    __collection__ = "event"

    structure = {
        'achive_id'    : int,
        'user_id'      : int,
        'time_changed' : datetime,
        'level'        : int,
        'done'         : bool,
        'progress'     : []
    }
    default_values  = {'done': False, 'level': 0, 'time_changed': datetime.now, 'progress': []}
    required_fields = ['user_id']
    indexes         = [{'fields': ['user_id', 'achive_id']}]

    @cached_property
    def achive(self):
        return app.connection.Achive.fetch_one({"_id": self.get("achive_id")})

class SimpleEvent(BaseEvent):
    def _get_level(self):
        conditions, level = self.achive.get('rule')['cones'], 0
        value = self.get('progress')[0]
        for c in conditions:
            if value < c:
                break
            level += 1
        return level

    def test(self, rule_dict, value):
        return True
        # return value > min(rule_dict['cones'])  

    def save(self, *args, **kwargs):        
        self.update({'level' : self._get_level()})
        return super(SimpleEvent, self).save(*args, **kwargs)
app.connection.register([SimpleEvent])
app.db.seqs.insert({'_id': 'events_seq',  'val': 0})


class ComplexEvent(SimpleEvent):
    def test(self, value):
        pass

    def _get_level(self):
        l = len(self.achive.get('rule')['complex'])
        val = self.get('progress')[0].values()

        return 0 if len(val) < l else min(val)
app.connection.register([ComplexEvent])


### исключительно для теста :)
def fill():
    achives = (
        {
            'title'      : u'OneWheel forward',
            'trick_id'   : 7,
            'descr'      : u'Выполните трюк на 4,20,40 конусов',
            'icon'       : u'0.jpg',            
            'rule'       : {u'cones': [4,20,40]},
            'parents'    : [2],
        },
        {
            'title'      : u'OneWheel backward',
            'trick_id'   : 13,
            'descr'      : u'Выполните трюк на 4,20,40 конусов',
            'icon'       : u'0.jpg',
            'rule'       : {u'cones': [4,20,40]},
            'parents'    : [2],
        },
        {
            'title'      : u'OneWheel dual',            
            'descr'      : u'Получите достижения OneWheel forward и OneWheel backward.',
            'icon'       : u'0.jpg',
            'score'      : 2.0,
            'rule'       : {u'complex': [0, 1]}            
        }
    )

    for a in achives:
        achive = app.connection.Achive()
        a['_id'] = app.db.seqs.find_and_modify({"_id": "achives_seq"}, {"$inc": {"val": 1}})['val']
        achive.update(a)
        achive.save()
