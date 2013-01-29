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


class TricksTestCase(unittest.TestCase):
    @property
    def app(self, *args, **kwargs):
        """ monkey path please """
        raise NotImplemented('Set up app instance')


    def setUp(self):
        self.app = self.app.test_client()

    def tearDown(self):
        pass

    def test_tricks(self):
        r = self.app.get('/tricks/')
        self.assertEqual(r.status_code, 200, u'Wrong response status code: %s' % r.status_code)

        # is json?
        json.loads(r.data)
        


if __name__ == '__main__':
    unittest.main()
