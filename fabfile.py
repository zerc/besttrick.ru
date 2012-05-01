#!venv/bin/python
# -*- coding: utf-8 -*-
from fabric.api import *


env.hosts = _app.config['FLASK_HOSTS']
 
def roll():
    local('git push origin master')
    run("""
        cd www/ &&
        git reset HEAD --hard &&
        rm static/js/main_min.js &&
        /etc/init.d/bt-uwsgi reload
    """)
    sudo("/etc/init.d/nginx reload")
    
