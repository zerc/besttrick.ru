#!venv/bin/python
# -*- coding: utf-8 -*-
from project import app, markdown
from apps import tricks, users, utils, admin, bt
from flask import render_template

url = app.add_url_rule


url('/',                        'index',            bt.index)
url('/',                        'mobile_index',     bt.mobile_index,    subdomain='m')
url('/pown/<int:user_id>/',     'pown',             bt.pown,            methods=['GET'])
url('/pown/<int:user_id>/',     'pown',             bt.pown,            subdomain='m', methods=['GET'])
url('/feedback/',               'feedback',         bt.feedback,        methods=['POST'])
url('/youtube_reciver/',        'youtube_reciver',  bt.youtube_reciver, methods=['POST'])



### Trick urls
url('/tricks/',                             'tricks',                   tricks.tricks_list)
url('/tricks/',                             'mobile_tricks',            tricks.tricks_list, subdomain='m')
url('/tricks/trick<trick:trick>/',         'tricks_trick',              tricks.trick_page, methods=['GET'])
url('/tricks/trick<trick:trick>/',         'mobile_tricks_trick',       tricks.trick_page, methods=['GET'], subdomain='m')
url('/tricks/trick<trick:trick>/check/',   'tricks_check',              tricks.check, methods=['PUT'])
url('/check/',                              'mobile_checkin_page',      tricks.checkin_page, methods=['GET', 'POST'], subdomain='m')
url('/prepare_youtube_upload/',             'prepare_youtube_upload',   tricks.prepare_youtube_upload, methods=['GET'])


### User urls
url('/login/',                  'login',            users.login,        methods=['POST'])
url('/login/',                  'login',            users.login,        methods=['POST'], subdomain="m")
url('/logout/',                 'logout',           users.logout)
url('/logout/',                 'logout',           users.logout,       subdomain="m")
url('/banned/',                 'banned',           lambda: render_template('banned.html'))

url('/my/',                   'my',               users.my, methods=['PUT', 'GET'])
url('/my/',                   'mobile_my',        users.my, methods=['POST', 'GET'], subdomain="m")
url('/my/tricks/',            'my_tricks',        users.my_tricks)

url('/users/',                          'users',            users.list_of_users)
url('/users/user<int:user_id>/',        'profile',          users.user_profile)
url('/users/user<int:user_id>/',        'profile',          users.user_profile, subdomain="m")
url('/users/rating/',                   'rating',           users.top_users)
url('/users/rating/',                   'mobile_rating',    users.top_users,  subdomain="m")



if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000)
