#!venv/bin/python
# -*- coding: utf-8 -*-
from project import app, connection, db, markdown
from apps import tricks, users, utils, admin, bt
from flask import render_template

url = app.add_url_rule


url('/',                        'index',            bt.index)
url('/',                        'mobile_index',     lambda: render_template('mobile/index.html'),         subdomain='m')
url('/pown/<int:user_id>/',     'pown',             bt.pown,            methods=['GET'])
url('/pown/<int:user_id>/',     'pown',             bt.pown,            subdomain='m', methods=['GET'])
url('/feedback/',               'feedback',         bt.feedback,        methods=['POST'])
url('/youtube_reciver/',        'youtube_reciver',  bt.youtube_reciver, methods=['POST'])

url('/login/',                  'login',            users.login,        methods=['POST'])
url('/login/',                  'login',            users.login,        methods=['POST'], subdomain="m")

url('/logout/',                  'logout',          users.logout,        methods=['GET'])
url('/logout/',                  'logout',          users.logout,        methods=['GET'], subdomain="m")


### Trick urls
url('/tricks/',                             'tricks',                   tricks.tricks_list)
url('/tricks/',                             'mobile_tricks',            tricks.tricks_list, subdomain='m')
url('/tricks/trick<int:trick_id>/',         'tricks_trick',             tricks.trick_page, methods=['GET'])
url('/tricks/trick<int:trick_id>/',         'mobile_tricks_trick',      tricks.trick_page, methods=['GET'], subdomain='m')
url('/tricks/trick<int:trick_id>/check/',   'tricks_check',             tricks.check, methods=['PUT'])
url('/check/',                              'mobile_checkin_page',      tricks.checkin_page, methods=['GET', 'POST'], subdomain='m')
url('/prepare_youtube_upload/',             'prepare_youtube_upload',   tricks.prepare_youtube_upload, methods=['GET'])


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000)
