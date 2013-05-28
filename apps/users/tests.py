# coding: utf-8
"""
    apps.users.tests
    ~~~~~~~~~~~

    Tests for tricks

    :copyright: (c) 2013 by zero13cool
"""
import simplejson as json
import unittest

from flask import get_flashed_messages

from apps.tests import BaseTestCase

from .base import register
from .models import User

class UsersTestCase(BaseTestCase):
    def test_register(self):
        vk_loginza_response = {
            u'photo': u'http://cs311131.vk.me/v311131211/824/oiWLaBxWwWc.jpg',
            u'name':
            {
                u'first_name': u'\u0422\u0440\u0438\u043d\u0430\u0434\u0446\u0430\u0442\u044c',
                u'last_name': u'\u041d\u0443\u043b\u0435\u0439'
            },
            u'dob': u'1906-02-13',
            u'gender': u'M',
            u'address': {u'home': {u'country': u'1'}}, 
            u'provider': u'http://vk.com/',
            u'nickname': u'', 
            u'identity': u'http://vk.com/id12584488', 
            u'uid': 12584488
        }

        new_user = register(vk_loginza_response)
        self.assertIsInstance(new_user, User, u'Register returns invalid object type')        


if __name__ == '__main__':
    unittest.main()
