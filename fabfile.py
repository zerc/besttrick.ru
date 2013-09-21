#!venv/bin/python
# coding: utf-8
import unittest as _ut
from functools import wraps as _wraps
from fabric.api import *

from os.path import join as _path_join

from urls import app as _app

from apps.tricks.tests import TricksTestCase as _TricksTestCase
from apps.tests import BtTestCase as _BtTestCase
from apps.achives.tests import AchivesTestCase as _AchivesTestCase
from apps.users.tests import UsersTestCase as _UsersTestCase

env.hosts = _app.config['FLASK_HOSTS']


TESTS_SET = {
    'bt'     : _BtTestCase,
    'tricks' : _TricksTestCase,
    'achives': _AchivesTestCase,
    'users'  : _UsersTestCase,
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
    _app.connection.copy_database(_app.config['MONGODB_DB'], test_database_name)
    _app.config['MONGODB_DB'] = test_database_name

    # run tests
    def _(t):
        t.app = _app
        suite = _ut.TestLoader().loadTestsFromTestCase(t)
        return _ut.TextTestRunner(verbosity=1).run(suite)

    result = _(TESTS_SET[test_name]) if test_name else map(_, TESTS_SET.values())
    # clean up :)
    _app.connection.drop_database(test_database_name)

    return result


def _testing(func):
    """
    Декоратор для прогона тестов
    """
    @_wraps(func)
    def wrapper(*args, **kwargs):
        result = run_tests()
        for r in result:
            if not r.wasSuccessful():
                return None

        return func(*args, **kwargs)

    return wrapper

roll = _testing(roll)
push = _testing(push)
