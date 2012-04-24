#!venv/bin/python
# -*- coding: utf-8 -*-
import sys
from pytils.translit import slugify
from optparse import OptionParser

from apps.users import User
from apps.tricks import Trick
from project import connection

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
    static_dir = 'static/images/'

    tricks = [
        {"title": u"Parallel", "thumb": u"4.jpg",},
        {"title": u"Monoline"},
        {"title": u"Criss-cross"},
        {"title": u"One foot forward"},
        {"title": u"One foot backward"},
    ]

    for trick in tricks:
        t = connection.Trick.find_one({'title': trick['title']})
        if t:
            connection.besttrick.trick.update({'_id': t['_id']}, {'$set': trick})
            continue

        t = connection.Trick()
        t.update(trick)
        t['_id'] = slugify(trick['title'])
        #t['thumb'] = static_dir + t['thumb']
        t.save()

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

