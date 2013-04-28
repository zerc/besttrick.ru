# coding: utf-8
"""
    apps.achives.tests
    ~~~~~~~~~~~~~~~~~~

    Tests for achive module

    :copyright: (c) 2013 by zero13cool
"""
import unittest

from apps.tests import BaseTestCase
from .models import *



class AchivesTestCase(BaseTestCase):
    def setUp(self):
        self.client = self.app.test_client()

        # clean first
        self.app.connection.SimpleEvent.collection.drop()

        self.Achive = self.app.connection.Achive

    def test_update_parent(self):
        valid_checkin_data = {'cones': 21, 'video_url': None, 'trick': 7, 'user': 1, 'approved': 0}

        def do_simple():
            achive = self.Achive.fetch_one({"trick_id": valid_checkin_data['trick']})
            event = achive.do(valid_checkin_data['user'], valid_checkin_data['cones'])
            achive.do_parents(valid_checkin_data['user'])

        do_simple()
        valid_checkin_data['trick'] = 13
        do_simple()
        
        event = self.Achive.fetch_one({"_id": 21}).get_event_or_dummy(valid_checkin_data['user'])
        self.assertEqual(event.get('progress')[0], {u'2':2}, u'Recursive update parents dont work')

    def test_base_logic(self):
        valid_checkin_data = {'cones': 21, 'video_url': None, 'trick': 7, 'user': 1, 'approved': 0}
  
        def do_simple():
            achive = self.Achive.fetch_one({"trick_id": valid_checkin_data['trick']})
            self.assertEqual(achive._event_cls, self.app.connection.SimpleEvent, u'SimpleEvent expected!')
    
            event = achive.do(valid_checkin_data['user'], valid_checkin_data['cones'])
            achive.do_parents(valid_checkin_data['user'])
            return event

        do_simple()

        e = self.Achive.fetch_one({"_id": 2}).get_event_or_dummy(valid_checkin_data['user'])
        self.assertEqual(e.get('level'), 0, 'Level detection for complex event is broken!')

        val, expected = e.get('progress')[0], {u'0': 2}
        self.assertEqual(val, expected, u'Invalid progress value=%s!' % repr(val))    
        
        valid_checkin_data.update({'cones': 45, 'trick': 13})
        do_simple(), e.reload()
        self.assertEqual(e.get('level'), 2, 'Level detection for complex event is broken!')
        val, expected = e.get('progress')[0], {u'0': 2, u'1': 3}
        self.assertEqual(val, expected, u'Invalid progress for level %s value=%s!' % (2, repr(val)))

        valid_checkin_data.update({'cones': 45, 'trick': 7})
        do_simple(), e.reload()        
        self.assertEqual(e.get('level'), 3, 'Level detection for complex event is broken!')
        val, expected = e.get('progress')[0], {u'0': 3, u'1': 3}
        self.assertEqual(val, expected, u'Invalid progress for level %s value=%s!' % (3, repr(val)))
