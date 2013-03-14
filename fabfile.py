#!venv/bin/python
# -*- coding: utf-8 -*-
import unittest as ut
from functools import wraps
from fabric.api import *

from os.path import join as path_join

from runserver import app
from apps.tricks import tests as tricks_tests, models as trick_models


env.hosts = _app.config['FLASK_HOSTS']
 

def roll():
    local('git push origin master')
    run("""
        cd www/ &&
        git reset HEAD --hard &&
        rm static/js/main.min.js &&
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


def push():
    local('git push origin master')
    with cd('www/'):
        run("""git reset HEAD --hard""")


def pulldb():
    """
    Клонирует базу и статику с сервера на локальную машину.
    Перед этим все дропает.
    """
    with cd('www/'):
        run("""
            mongodump -d besttrick && 
            zip -r dump.zip dump && 
            zip -r images.zip static/images/
        """)


        get('dump.zip', 'dump.zip')
        get('images.zip', 'images.zip')

    local("""
        unzip -o dump.zip && 
        unzip -o images.zip && 
        mongorestore --drop dump && 
        rm dump.zip images.zip
    """)


def run_tests():
    """
    Запускает тесты для каждого модуля
    """
    tricks_tests.TricksTestCase.app = app

    # set up test database
    test_database_name = 'test_besttrick'
    app.connection.copy_database(app.config['MONGODB_DB'], test_database_name)
    app.config['MONGODB_DB'] = test_database_name

    # path models :D
    for model_name in trick_models.__all__:
        getattr(trick_models, model_name).__database__ = app.config['MONGODB_DB']

    # run tests
    suite  = ut.TestLoader().loadTestsFromTestCase(tricks_tests.TricksTestCase)
    result = ut.TextTestRunner(verbosity=1).run(suite)

    # clean up :)    
    app.connection.drop_database(test_database_name)

    return result


def testing(func):
    """
    Сперва прогоним тесты
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        result = run_tests()
        return func(*args, **kwargs) if result.wasSuccessful() else None

    return wrapper

roll = testing(roll)
push = testing(push)




