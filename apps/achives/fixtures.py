# coding: utf-8
"""
    apps.achives.fixtures
    ~~~~~~~~~~~~~~~~~~

    Базовое наполнение ачивками

    :copyright: (c) 2013 by zero13cool
"""
from project import app


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
        'title'      : u'Dual OneWheeler',            
        'descr'      : u'Вы умело колесите как лицом так и спиной вперед!',
        'icon'       : u'0.jpg',
        'score'      : 2.0,
        'rule'       : {u'complex': [0, 1]}            
    },

    # Вращательные
    {
        'title'      : u'Seven forward',
        'trick_id'   : 10,
        'descr'      : u'',
        'icon'       : u'0.jpg',
        'rule'       : {u'cones': [4,20,40]},
        'parents'    : [6],
    },
    {
        'title'      : u'Chicken Leg forward',
        'trick_id'   : 18,
        'descr'      : u'',
        'icon'       : u'0.jpg',
        'rule'       : {u'cones': [3,4,6]},
        'parents'    : [6],
    },
    {
        'title'      : u'Chamomile Toe forward',
        'trick_id'   : 28,
        'descr'      : u'',
        'icon'       : u'0.jpg',
        'rule'       : {u'cones': [1,2,10]},
        'parents'    : [6],
    },
    {
        'title'      : u'Forward WheelSpiner',            
        'descr'      : u'Вы не плохо вращаетесь на одном колесе лицом вперед!',
        'icon'       : u'0.jpg',
        'score'      : 2.0,
        'rule'       : {u'complex': [3, 4, 5]}            
    },
)

def fill():
    for a in achives:
        achive = app.connection.Achive()
        a['_id'] = app.db.seqs.find_and_modify({"_id": "achives_seq"}, {"$inc": {"val": 1}})['val']
        achive.update(a)
        achive.save()
