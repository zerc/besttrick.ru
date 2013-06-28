# coding: utf-8
"""
    urls
    ~~~~~~~~~~~

    All project urls rules must be here

    :copyright: (c) 2013 by zero13cool
"""
from project import app
from apps import tricks, users, common, admin, bt, achives
from flask import render_template

# hook just remove this when army end
try:
    import upload
except ImportError:
    pass


url = app.add_url_rule


url('/',                        'index',            bt.index)
url('/dev/',                    'dev_index',        bt.index,           defaults={'template': 'dev_index.html'})
url('/',                        'mobile_index',     bt.mobile_index,    subdomain='m')
url('/pown/<int:user_id>/',     'pown',             bt.pown,            methods=['GET'])
url('/pown/<int:user_id>/',     'pown',             bt.pown,            subdomain='m', methods=['GET'])
url('/feedback/',               'feedback',         bt.feedback,        methods=['POST'])
url('/youtube_reciver/',        'youtube_reciver',  bt.youtube_reciver, methods=['POST'])



### Trick urls
url('/tricks/',                              'tricks',                   tricks.tricks_list)
url('/tricks/trick<trick:trick>/',           'tricks_trick',             tricks.get_trick_, methods=['GET'])
url('/tricks/trick<trick:trick>/',           'mobile_tricks_trick',      tricks.trick_page, methods=['GET'], subdomain='m')
url('/tricks/trick<int:trick_id>/check/',    'tricks_check',             tricks.check, methods=['PUT', 'POST'])
url('/check/',                               'mobile_checkin_page',      tricks.checkin_page, methods=['GET', 'POST'], subdomain='m')
url('/prepare_youtube_upload/',              'prepare_youtube_upload',   tricks.prepare_youtube_upload, methods=['GET'])

url('/checkins/', 							 'checkins',                 tricks.checkins, methods=['GET'])

### User urls
url('/login/',                  'login',            users.login,        methods=['POST'])
url('/login/',                  'login',            users.login,        methods=['POST'], subdomain="m")
url('/logout/',                 'logout',           users.logout)
url('/logout/',                 'logout',           users.logout,       subdomain="m")
url('/banned/',                 'banned',           lambda: render_template('banned.html'))

url('/my/tricks/',              'my_tricks',        users.my_tricks)

url('/users/',                          'users',            users.users)
url('/users/user<int:user_id>/',        'user',             users.user, methods=['PUT', 'GET', 'POST'])
url('/users/rating/',                   'rating',           users.top_users)
url('/users/rating/',                   'mobile_rating',    users.top_users,  subdomain="m")

## depricated
# url('/user/',                   'my',               users.user, methods=['PUT', 'GET'])
# url('/user/',                   'mobile_my',        users.user, methods=['POST', 'GET'], subdomain="m")
# url('/users/user<int:user_id>/',        'profile',          users.user_profile, subdomain="m")

### Achives urls
url('/my/achives/',                       'my_achives',      achives.my_achives)
url('/users/tituls/',   				  'get_tituls',      achives.get_tituls)
url('/users/user<int:user_id>/achives/',  'profile_achives', achives.profile_achives)
