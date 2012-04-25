#!venv/bin/python
# -*- coding: utf-8 -*-
import sys
from pytils.translit import slugify
from optparse import OptionParser

from apps.users import User
from apps.tricks import Trick
from project import connection, db

parser = OptionParser(u"Admin scripts for besttrick app")

def clean_do(options):
    """ Cleaning do'ers list in tricks """
    tricks = connection.Trick.find()

    for trick in tricks:
        trick['a_users'] = []
        trick.save()

    print '>> Cleaing complete'


parser.add_option("-u", "--user_id", dest="pk", help="user_id", type="int")
def toggle_admin(options):
    """ Bless/Unbless admin power to user """
    user = connection.User.find_one(options.__dict__)
    user['admin'] = abs(user.get('admin', 0)-1)
    user.save()
    print user


def import_tricks(options):
    """ Import trick to mongo. Run: admin.py import_tricks """
    tricks = [
        {
            "title": u"Seven", 
            "videos": [u"http://www.youtube.com/embed/-8O-z3vO2xs"],
            "descr": 
            u"""
Вращение на одном колесе с продвижением по банками.

Выполняется на тое или хиле.
            """,
        },
        {
            "title": u"No wiper",
            "videos": [u"http://www.youtube.com/embed/RQeEDR7j0uc"],
            "descr": u"""
Также называется Toe shift.

Может выполнятся как на внутреннем, так и на внешнем ребре.
            """,
        },
        {
            "title": u"Foot spin",
            "videos": [u"http://www.youtube.com/embed/Q9fTQOopwF8"],
            "descr": u"""Можно рассматривать как подготовоку к Day Night :)"""
        },
    ]

    def _update(trick):
        _id = slugify(trick['title'])
        
        t = connection.Trick.find_one({'_id': _id})
        if t: return db.trick.update({'_id': _id}, {'$set': trick})

        t = connection.Trick()
        t.update(trick)
        t['_id'] = _id
        t['thumb'] = u'%s.jpg' % _id
        t.save()

    map(_update, tricks)



def clean_db(options):
    tricks = connection.Trick.find()

    for t in tricks:
        t.delete()


if __name__ == "__main__":
    options, labels = parser.parse_args()
    for label in labels:
        if not hasattr(sys.modules[__name__], label):
            print '>> Function %s does not exists' % label
            continue
        
        getattr(sys.modules[__name__], label)(options)

