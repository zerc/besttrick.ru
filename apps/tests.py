# coding: utf-8
"""
    apps.tests
    ~~~~~~~~~~~

    Общие тесты

    :copyright: (c) 2012 by zero13cool
"""
import unittest


class BaseTestCase(unittest.TestCase):
    @property
    def app(self, *args, **kwargs):
        """ monkey path please """
        raise NotImplemented('Set up app instance')

    def setUp(self):
        self.client = self.app.test_client()
    

class BtTestCase(BaseTestCase):
    def test_urls(self):
        r = self.client.get('/')
        self.assertEqual(r.status_code, 200, u'Index page BROKEN!')

        self.client.get('/pown/0/', follow_redirects=True)

        pages = ('/user/', '/my/tricks/', '/users/', '/users/user0/', '/users/rating/')
        for page in pages:
            self.assertEqual(self.client.get(page).status_code, 200, u'Page: %s BROKEN!' % page)


if __name__ == '__main__':
    unittest.main()
