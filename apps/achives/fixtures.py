# coding: utf-8
"""
    apps.achives.fixtures
    ~~~~~~~~~~~~~~~~~~

    Базовое наполнение ачивками

    :copyright: (c) 2013 by zero13cool
"""
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
    {#6
        'trick_id'   : 29,
        'descr'      : u'',
        'icon'       : u'0.jpg',
        'rule'       : {u'cones': [3,6,10]},
        'parents'    : [7],
    },
    {#7
        'title'      : u'Forward OneWheel Spiner',            
        'descr'      : u'Вы не плохо вращаетесь на одном колесе лицом вперед!',
        'icon'       : u'0.jpg',
        'score'      : 2.0,
        'rule'       : {u'complex': [3, 4, 5, 6]},
        'parents'    : [21, 31],
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
        'title'      : u'Wheel Jumper',            
        'descr'      : u'Отлично прыгаете на колесиках!',
        'icon'       : u'0.jpg',
        'score'      : 2.0,
        'rule'       : {u'complex': [8, 9]},
        'parents'    : [21, 35],
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
        'title'      : u'Master Sit-OneWheel Forward',
        'descr'      : u'Овладейте сидячими вилингами лицом вперед!',
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
        'title'      : u'Backward OneWheel Spiner',
        'descr'      : u'Вы не плохо вращаетесь на одном колесе спиной вперед!',
        'icon'       : u'0.jpg',
        'score'      : 2.0,
        'rule'       : {u'complex': [14, 15]},
        'parents'    : [21, 31],
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
        'score'      : 3.0,
        'rule'       : {u'complex': [20, 16, 13, 10, 7, 2, 24]},
    },
    # Сидячие вилинги спиной вперед
    {#22
        'trick_id'   : 27,
        'icon'       : u'0.jpg',
        'rule'       : {u'cones': [3,10,20]},
        'parents'    : [24],
    },
    {#23
        'trick_id'   : 30,
        'icon'       : u'0.jpg',
        'rule'       : {u'cones': [3,10,20]},
        'parents'    : [24],
    },
    {#24
        'title'      : u'Master Sit-OneWheel Backward',
        'descr'      : u'Мастерски освойте сидячие вилинги спиной вперед!',
        'icon'       : u'0.jpg',
        'score'      : 2.0,
        'rule'       : {u'complex': [22, 23]},
        'parents'    : [21],
    },
    # Вращательные трюки лицом вперед
    {#25
        'trick_id'   : 1,
        'icon'       : u'0.jpg',
        'rule'       : {u'cones': [6,20,40]},
        'parents'    : [29],
    },
    {#26
        'trick_id'   : 2,
        'icon'       : u'0.jpg',
        'rule'       : {u'cones': [6,20,40]},
        'parents'    : [29],
    },
    {#27
        'trick_id'   : 14,
        'icon'       : u'0.jpg',
        'rule'       : {u'cones': [6,20,40]},
        'parents'    : [29],
    },
    {#28
        'trick_id'   : 21,
        'icon'       : u'0.jpg',
        'rule'       : {u'cones': [6,20,40]},
        'parents'    : [29],
    },
    {#29
        'title'      : u'Spin Pretendent',
        'descr'      : u'Освойте вращения лицом вперед на двух колесиках',
        'icon'       : u'0.jpg',
        'score'      : 2.0,
        'rule'       : {u'complex': [25, 26, 27, 28, 30]},
        'parents'    : [31],
    },
    {#30
        'trick_id'   : 15,
        'icon'       : u'0.jpg',
        'rule'       : {u'cones': [6,20,40]},
        'parents'    : [29],
    },
    {#31
        'title'      : u'Spin King',
        'descr'      : u'От вашего мастерства идет кругом голова!',
        'icon'       : u'0.jpg',
        'score'      : 3.0,
        'rule'       : {u'complex': [29, 16, 7]},
        'parents'    : [],
    },
    {#32
        'trick_id'   : 0,
        'icon'       : u'0.jpg',
        'rule'       : {u'cones': [3,10,20]},
        'parents'    : [34],
    },
    {#33
        'trick_id'   : 23,
        'icon'       : u'0.jpg',
        'rule'       : {u'cones': [3,10,20]},
        'parents'    : [34],
    },
    {#34
        'title'      : u'Kazak',
        'descr'      : u'Вы настоящий казак!',
        'icon'       : u'0.jpg',
        'score'      : 2.0,
        'rule'       : {u'complex': [32, 33]},
        'parents'    : [35],
    },
    {#35
        'title'      : u'Jump King',
        'descr'      : u'Вы допрыгнули до звезд!',
        'icon'       : u'0.jpg',
        'score'      : 3.0,
        'rule'       : {u'complex': [34, 10]},
        'parents'    : [],
    },
    {#36
        'trick_id'   : 9,
        'icon'       : u'0.jpg',
        'rule'       : {u'cones': [3,10,20]},
        'parents'    : [38],
    },
    {#37
        'trick_id'   : 24,
        'icon'       : u'0.jpg',
        'rule'       : {u'cones': [3,10,20]},
        'parents'    : [38],
    },
    {#38
        'title'      : u'Pro Cobroid',
        'descr'      : u'Гибкость ваших ног заставляет задуматься - человек ли вы?!',
        'icon'       : u'0.jpg',
        'score'      : 2.0,
        'rule'       : {u'complex': [36, 37]},
        'parents'    : [],
    },
)
