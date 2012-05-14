#!venv/bin/python
# -*- coding: utf-8 -*-
from fabric.api import *
from project import app, JS_PROJECT, final_script_name
from os.path import join as path_join


env.hosts = _app.config['FLASK_HOSTS']
 
def roll():
    execute(static)
    put(path_join(app.static_folder, final_script_name), 'www/static/js/main.js')
    
    local('git push origin master')
    run("""
        cd www/ &&
        git reset HEAD --hard &&
        rm static/js/main_min.js &&
        /etc/init.d/bt-uwsgi reload
    """)
    sudo("/etc/init.d/nginx reload")

def update_tricks():
    run("""
        cd www/ &&
        . venv/bin/activate &&
        ./admin.py import_tricks && 
        /etc/init.d/bt-uwsgi reload
    """)

def pull():
    local('git pull origin master')

def static():
    final_file = open(path_join(app.static_folder, final_script_name), 'w+')
    print >> final_file, 'window.app = function (args) {'

    for f in JS_PROJECT:
        with open(path_join(app.static_folder, f), 'r') as js_file:
            print >> final_file, js_file.read()

    print >> final_file, 'var app = new App(args); };'
    final_file.close()
