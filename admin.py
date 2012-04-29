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


# Список трюков вынести в отдельный файл, типа "дамп базы"
def import_tricks(options):
    """ Import trick to mongo. Run: admin.py import_tricks """
    tricks = [
        {
            "title": u"Toe Machine",
            "videos": [u"http://www.youtube.com/embed/Q5qFX8YPtaU"],
            "descr": u"""Трюк так же известен как Швейная машинка.""",
        },
        {
            "title": u"Day Night",
            "videos": [u"http://www.youtube.com/embed/vRb0PAeBe2g"],
            "descr": u"""Своеобразный ответ на No Wiper. Выполняется как хиле, так и на тое.""",
        },
        {
            # TODO: добавить видео с неполным приседом
            "title": u"Footgun Toe",
            "videos": [u"http://www.youtube.com/embed/m2JPr2geQxA"],
            "descr": u"""Пистолет на переднем колесе. Существуют варианты с полном приседом, и с коленом под прямым углом.""",
        },
        {
            "title": u"OneWheel Heel",
            "videos": [u"http://www.youtube.com/embed/okiGOwGfhY0"],
            "descr": u"""Езда на заднем колесе (heel) лицом вперед.""",
        },
        {
            "title": u"Confraglide",
            "videos": [u"http://www.youtube.com/embed/F6897UqZBw8"],
            "descr": u"""В русском слаломе, трюк так же известен как Бабочка.""",
        },
        {
            "title": u"Cobra Back",
            "videos": [u"http://www.youtube.com/embed/P_gyByoM4qg"],
            "descr": u"""Кобра спиной вперед. """,
        },
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

