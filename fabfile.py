#!venv/bin/python
# -*- coding: utf-8 -*-
import unittest as ut
from functools import wraps
from fabric.api import *

from os.path import join as path_join

from urls import app

from apps.tricks.tests import TricksTestCase
from apps.tests import BtTestCase
from apps.achives.tests import AchivesTestCase


env.hosts = _app.config['FLASK_HOSTS']

TESTS_SET = {
    'bt'     : BtTestCase,
    'tricks' : TricksTestCase,
    'achives': AchivesTestCase,
}

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


def run_tests(test_name=None):
    """
    Запускает тесты для каждого модуля
    """
    # set up test database
    test_database_name = 'test_besttrick'
    app.connection.copy_database(app.config['MONGODB_DB'], test_database_name)
    app.config['MONGODB_DB'] = test_database_name

    # run tests
    def _(t):
        t.app  = app
        suite  = ut.TestLoader().loadTestsFromTestCase(t)
        return ut.TextTestRunner(verbosity=1).run(suite)
        
    result = _(TESTS_SET[test_name]) if test_name else map(_, TESTS_SET.values())

    # clean up :)    
    app.connection.drop_database(test_database_name)

    return result


def testing(func):
    """
    Декоратор для прогона тестов
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        result = run_tests()
        return func(*args, **kwargs) if result.wasSuccessful() else None

    return wrapper

roll = testing(roll)
push = testing(push)
