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
        'rule'       : {unicode: []},
        'parents'    : [], 
    }
    default_values  = {'score': 1.0, 'parents': []}
    required_fields = ['title', 'descr']
    indexes = [{'fields': ['trick_id']}]

    ### private methods
    def __get(self, method_prefix, value):
        rule_name, condition = self.get('rule').items()[0]
        try:
            return getattr(self, '%s_%s' % (status_event, rule_name))(value)
        except AttributeError:
            print u'Unknow rule: %s' % rule_name
        return False

    
    ### Определения статуса ачивки - выполнена, не выполнена
    def status_event(self, value):
        return self.__get('_status_event', value)

    def _status_event_cones(self, value):
        index = self.get_level(value) - 1
        condition = self.get('rule')['cones']
        return value >= condition[index]        

    def _status_event_complex(self, value):
        condition = self.get('rule')['complex']
        return len(condition) == len(value)

    ### Тестирование передаваемых данных - выполняют ли они ачивку или нет
    def test(self, value):
        return self.__get('_test', value)

    def _test_cones(self, value):
        return not not self._level_for_cones(value)

    def _test_complex(self, value):
        original   = set(self.get('rule')['complex'])
        value      = set(value)
        return not value - original
        
    ### Определение уровня ачивки по передаваемым данным
    def get_level(self, value):
        return self.__get('_level_for', value)  

    def _level_for_cones(self, value):
        conditions, level = self.get('rule')['cones'], 1        
        for c in conditions:
            if value <= c or level == len(conditions):
                break
            level += 1
        return level

    def _level_for_complex(self, value):
        # берем по лвл дочерней ачивки
        pass

    def get_event(self, user_id, level):
        event = app.connection.Event.fetch_one({"user_id": user_id, "achive_id": self.get("_id"), "level": level})
        created = False
        if not event:
            event = app.connection.Event()
            event.update({"user_id": user_id, "achive_id": self.get("_id"), "level": level})
            created = True
        return event, created

    def make_event(self, user_id, value):
        """
        Регистрирует достижение пользователя
        """
        if not self.test(value): return False

        level = self.get_level(value)
        event, _ = self.get_event(user_id, level)
        event.update({'progress': [value], 'done': self.status_event(value)})
        event.save()

    def update_parents(self, user_id, level):
        """
        Обновляет данные по дереву родителей
        """
        parents = app.connection.Achive.fetch({"_id": {"$in": self.get('parents')}})
        for p in parents:
            event, _ = p.get_event(user_id, level)
            event.update({'level': level})
            current_progress = event.get('progress', [])
            current_progress.append(self.get("_id"))
            current_progress = list(set(current_progress)) # убираем возможные дубли
            event.update({'progress': current_progress, 'done': p.status_event(current_progress)})
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
        'progress'     : []
    }
    default_values  = {'done': False, 'level': 0, 'time_changed': datetime.now}
    required_fields = ['user_id']
    indexes         = [{'fields': ['user_id', 'achive_id']}]
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

# achive = app.connection.Achive.fetch({"_id": 1})[0]
# test_value, user_id = 10, 0
