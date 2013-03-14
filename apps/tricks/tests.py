# coding: utf-8
"""
    apps.tricks.tests
    ~~~~~~~~~~~

    Тесты для трюков

    :copyright: (c) 2012 by zero13cool
"""
import simplejson as json
import os
import unittest


class TricksTestCase(unittest.TestCase):
    @property
    def app(self, *args, **kwargs):
        """ monkey path please """
        raise NotImplemented('Set up app instance')

    def setUp(self):
        self.client = self.app.test_client()

    def tearDown(self):
        pass

    def test_tricks(self):
        r = self.client.get('/tricks/')
        self.assertEqual(r.status_code, 200, u'Wrong response status code: %s' % r.status_code)

        # is json?
        json.loads(r.data)

    def test_check(self):
        r = self.client.put('/tricks/trick0/check/')
        self.assertEqual(r.status_code, 403, u'Not private!')

        r = self.client.get('/tricks/trick0/check/')
        self.assertEqual(r.status_code, 405, u'Not closed for another requests types!')

        # типа авторизовались :D
        self.client.get('/pown/0/', follow_redirects=True)
        
        test_data_sets = (
            {'cones': -1},
            {'cones': 0},
            {'cones': 9999},
            {'cones': u'ada'},
            {'cones': u'фыв2'},
            {'cones': 10, 'video_url': u'asdsa'},
            {'cones': 10, 'video_url': u'http://'},
            {'cones': 10, 'video_url': u'<script>alert("asda");</script>'},
        )

        for data_set in test_data_sets:
            r = self.client.put('/tricks/trick0/check/', data=json.dumps(data_set))
            self.assertEqual(r.status_code, 400, u'Validation broken with data_set=%s' % repr(data_set))

        r = self.client.put('/tricks/trick0/check/', data=json.dumps({'cones': 200}))
        self.assertEqual(r.status_code, 200, u'Checkin broken, ALARM! (status_code = %s, text = %s)' % \
            (r.status_code, unicode(r.data, r.charset)))

if __name__ == '__main__':
    unittest.main()
