# coding: utf-8
from datetime import datetime

from project import app
from apps.common import BaseModel


class Achive(BaseModel):
    __collection__ = "achive"

    structure = {
        'title'      : unicode,
        'descr'      : unicode,
        'icon'       : unicode,
        'score'      : float,
        'trick_id'   : int,                        
        'rule'       : {
            'cones'        : [], # диапазоны конусов 
            'elements'     : {      # для ачивки с чек-листом
                'collection'      : unicode,
                'collection_ids'  : []
            },
        },
        'parents'    : [int],        
    }
    default_values  = {'score': 1.0, 'parents': []}
    required_fields = ['title', 'descr']
    #indexes = [{'fields': ['trick_id']}]

    ### some methods

    # testing value
    def test_cones(self, value):
        conditions = self.get('rule')['cones']
        test_result = False
        return value > min(conditions)

    def test_elements(self, value_dict):
        result = value_dict['collection'] == self.get('rule')['elements']['collection']
        if not result: return

        ids = set(value_dict['collection_ids'])
        diff = set(self.get('rule')['elements']['collection_ids']) - ids
        return diff == ids

    def test(self, rule_name, value):
        """
        Тестирует value согласно правилу rule.<field_name>
        """
        try:
            return getattr(self, 'test_%s' % rule_name)(value)
        except AttributeError:
            print u'Unknow rule: %s' % rule_name
        return False

    def get_event(self, user_id):
        event = app.connection.Event.fetch_one({"user_id": user_id, "achive_id": self.get("_id")})
        
        if not event:
            event = app.connection.Event()
            event.update({"user_id": user_id, "achive_id": self.get("_id")})

        return event

    def make_event(self, user_id, rule_name, value):
        """
        Регистрирует достижение пользователя
        """
        if not self.test(rule_name, value): return

        event = self.get_event(user_id)
        event.get('progress').update({rule_name: value})
        event.save()


    def update_parents(self, user_id):
        """
        Обновляет данные по дереву родителей
        """
        parents = app.connection.Achive.fetch({"_id": {"$in": self.get('parents')}})
        for p in parents:
            event = p.get_event(user_id)
            event.get('progress', []).append(self.get("_id"))
            event.save()
app.connection.register([Achive])
app.db.seqs.insert({'_id': 'achives_seq',  'val': 0})


class Event(BaseModel):
    __collection__ = "event"

    structure = {
        'achive_id'    : int,
        'user_id'      : int,
        'time_changed' : datetime,
        'level'        : int,
        'done'         : bool,
        'progress'     : {
            'cones'        : int,   
            'elements'     : {
                'collection'      : unicode,
                'collection_ids'  : []
            },
        },
    }
    default_values = {'done': False, 'level': 0, 'time_changed': datetime.now}
    required_fields = ['user_id']
    indexes = [{'fields': ['user_id', 'achive_id']}]
app.connection.register([Event])
app.db.seqs.insert({'_id': 'events_seq',  'val': 0})



### исключительно для теста :)
def fill():
    achives = (
        {
            'title'      : u'OneWheel forward',
            'trick_id'   : 7,
            'descr'      : u'Выполните трюк на 4,20,40 конусов',
            'icon'       : u'0.jpg',            
            'rule'   : {u'cones': [4,20,40], u'elements': {'collection': u'', 'collection_ids':[]}},
            'parents'    : [2],
        },
        {
            'title'      : u'OneWheel backward',
            'trick_id'   : 13,
            'descr'      : u'Выполните трюк на 4,20,40 конусов',
            'icon'       : u'0.jpg',
            'rule'   : {u'cones': [4,20,40],  u'elements': {'collection': u'', 'collection_ids':[]}},
            'parents'    : [2],
        },
        {
            'title'      : u'OneWheel dual',            
            'descr'      : u'Получите достижения OneWheel forward и OneWheel backward.',
            'icon'       : u'0.jpg',
            'score'      : 2.0,
            'rule'   : {
                'cones': [],
                'elements': {
                    'collection'      : u'achive',
                    'collection_ids'  : [0, 1]
                }
            }
        }
    )

    for a in achives:
        achive = app.connection.Achive()
        a['_id'] = app.db.seqs.find_and_modify({"_id": "achives_seq"}, {"$inc": {"val": 1}})['val']
        achive.update(a)
        achive.save()
