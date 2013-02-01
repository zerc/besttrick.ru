# coding: utf-8
"""
    apps.tricks.tests
    ~~~~~~~~~~~

    Тесты для трюков

    :copyright: (c) 2012 by zero13cool
"""
# TODO: реализовать подсасывание данных из боевой базы в тестовую
import simplejson as json
import os
import unittest
from pymongo.helpers import OperationFailure


class TricksTestCase(unittest.TestCase):
    test_database_name = 'test_besttrick'

    @property
    def app(self, *args, **kwargs):
        """ monkey path please """
        raise NotImplemented('Set up app instance')


    def setUp(self):        
        self.app.connection.copy_database(self.app.config['MONGODB_DB'], self.test_database_name)
        self.app.config['MONGODB_DB'] = self.test_database_name
        self.client = self.app.test_client()

    def tearDown(self):
        self.app.connection.drop_database(self.test_database_name)

    def test_tricks(self):
        r = self.client.get('/tricks/')
        self.assertEqual(r.status_code, 200, u'Wrong response status code: %s' % r.status_code)

        # is json?
        json.loads(r.data)
        


if __name__ == '__main__':
    unittest.main()
