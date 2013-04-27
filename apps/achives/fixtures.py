# coding: utf-8
"""
    apps.achives.fixtures
    ~~~~~~~~~~~~~~~~~~

    Базовое наполнение ачивками

    :copyright: (c) 2013 by zero13cool
"""
from project import app


achives = (
    {#0 просто вилинги
        'trick_id'   : 7,
        'descr'      : u'Выполните трюк на 4,20,40 конусов',
        'icon'       : u'0.jpg',            
        'rule'       : {u'cones': [4,20,40]},
        'parents'    : [2],
    },
    {#1        
        'trick_id'   : 13,
        'descr'      : u'Выполните трюк на 4,20,40 конусов',
        'icon'       : u'0.jpg',
        'rule'       : {u'cones': [4,20,40]},
        'parents'    : [2],
    },
    {#2
        'title'      : u'Dual OneWheeler',            
        'descr'      : u'Вы умело колесите как лицом так и спиной вперед!',
        'icon'       : u'0.jpg',
        'score'      : 2.0,
        'rule'       : {u'complex': [0, 1]},
        'parents'    : [21],
    },

    # Вращательные вилинги лицом
    {#3
        'trick_id'   : 10,
        'descr'      : u'',
        'icon'       : u'0.jpg',
        'rule'       : {u'cones': [4,20,40]},
        'parents'    : [7],
    },
    {#4
        'trick_id'   : 18,
        'descr'      : u'',
        'icon'       : u'0.jpg',
        'rule'       : {u'cones': [3,4,6]},
        'parents'    : [7],
    },
    {#5
        'trick_id'   : 28,
        'descr'      : u'',
        'icon'       : u'0.jpg',
        'rule'       : {u'cones': [1,2,10]},
        'parents'    : [7],
    },
    {#61
        'trick_id'   : 29,
        'descr'      : u'',
        'icon'       : u'0.jpg',
        'rule'       : {u'cones': [3,6,10]},
        'parents'    : [7],
    },
    {#7
        'title'      : u'Forward WheelSpiner',            
        'descr'      : u'Вы не плохо вращаетесь на одном колесе лицом вперед!',
        'icon'       : u'0.jpg',
        'score'      : 2.0,
        'rule'       : {u'complex': [3, 4, 5, 6]},
        'parents'    : [21],
    },
    # Прыжковые вилинги
    {#8
        'trick_id'   : 20,
        'icon'       : u'0.jpg',            
        'rule'       : {u'cones': [4,10,20]},
        'parents'    : [10],
    },
    {#9
        'trick_id'   : 22,
        'icon'       : u'0.jpg',
        'rule'       : {u'cones': [4,10,20]},
        'parents'    : [10],
    },
    {#10
        'title'      : u'OneWheel Jumper',            
        'descr'      : u'Отлично прыгаете на одном колесике!',
        'icon'       : u'0.jpg',
        'score'      : 2.0,
        'rule'       : {u'complex': [8, 9]},
        'parents'    : [21],
    },
    # Сидячие вилинги
    {#11
        'trick_id'   : 6,
        'icon'       : u'0.jpg',            
        'rule'       : {u'cones': [4,10,20]},
        'parents'    : [13],
    },
    {#12
        'trick_id'   : 26,
        'icon'       : u'0.jpg',
        'rule'       : {u'cones': [3,10,20]},
        'parents'    : [13],
    },
    {#13
        'title'      : u'OneWheel forward seater',            
        'descr'      : u'Овладейте сидячими трюками на одном колесе!',
        'icon'       : u'0.jpg',
        'score'      : 2.0,
        'rule'       : {u'complex': [11, 12]},
        'parents'    : [21],
    },
        # Вращательные вилинги спиной
    {#14
        'trick_id'   : 17,
        'descr'      : u'',
        'icon'       : u'0.jpg',
        'rule'       : {u'cones': [4,20,40]},
        'parents'    : [16],
    },
    {#15
        'trick_id'   : 3,
        'descr'      : u'',
        'icon'       : u'0.jpg',
        'rule'       : {u'cones': [3,4,6]},
        'parents'    : [16],
    },
    {#16
        'title'      : u'Backward WheelSpiner',
        'descr'      : u'Вы не плохо вращаетесь на одном колесе спиной вперед!',
        'icon'       : u'0.jpg',
        'score'      : 2.0,
        'rule'       : {u'complex': [14, 15]},
        'parents'    : [21],
    },
    # Вилинговые шифты
    {#17        
        'trick_id'   : 5,
        'icon'       : u'0.jpg',
        'rule'       : {u'cones': [4,20,40]},
        'parents'    : [20],
    },
    {#18        
        'trick_id'   : 11,
        'icon'       : u'0.jpg',
        'rule'       : {u'cones': [4,20,40]},
        'parents'    : [20],
    },
    {#19        
        'trick_id'   : 16,
        'descr'      : u'',
        'icon'       : u'0.jpg',
        'rule'       : {u'cones': [4,20,40]},
        'parents'    : [20],
    },
    {#20
        'title'      : u'OneWheel Shift Master',
        'descr'      : u'Ваши шифты великолепны!',
        'icon'       : u'0.jpg',
        'score'      : 2.0,
        'rule'       : {u'complex': [17, 18, 19]},
        'parents'    : [21],
    },
    {#21
        'title'      : u'OneWheel King',
        'descr'      : u'От ваших вилингов девушки в воздух чепчики бросают!',
        'icon'       : u'0.jpg',
        'score'      : 2.0,
        'rule'       : {u'complex': [20, 16, 13, 10, 7, 2]},
    },
)

def fill():
    for a in achives:
        achive = app.connection.Achive()
        a['_id'] = app.db.seqs.find_and_modify({"_id": "achives_seq"}, {"$inc": {"val": 1}})['val']
        achive.update(a)
        achive.save()
