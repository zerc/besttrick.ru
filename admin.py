#!venv/bin/python
# -*- coding: utf-8 -*-
import sys
import urllib
from os.path import join as path_join
from pytils.translit import slugify
from optparse import OptionParser

from apps.users import User
from apps.tricks import Trick
from project import connection, db, app

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
parser.add_option("-t", "--update_thumbs", dest="update_thumbs", help="update_thumbs ?", action="store_true")
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
            "thumb": u"2",
            "videos": [u"http://www.youtube.com/embed/m2JPr2geQxA"],
            "descr": u"""Пистолет на переднем колесе. Существуют варианты с полном приседом, и с коленом под прямым углом.""",
        },
        {
            "title": u"OneWheel Heel",
            "thumb": u"2",
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
            "thumb": u"2",
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
            "thumb": u"2",
            "videos": [u"http://www.youtube.com/embed/Q9fTQOopwF8"],
            "descr": u"""Можно рассматривать как подготовоку к Day Night :)"""
        },
    ]

    def _download_thumbs(trick_id, videos_urls):
        """ По переданному идентификатору видео, скачивает тумбы с ютуба """
        url = 'http://img.youtube.com/vi/%s/%s.jpg'

        for video_url in videos_urls:
            video_id = video_url.split('/')[-1]

            for x in range(4):
                response = urllib.urlopen(url % (video_id, x))
                path = path_join(app.static_folder, 'images', '%s-%s.jpg' % (trick_id, x))
                with open(path, 'wb') as f:
                    f.write(response.read())


    def _update(trick):
        _id = slugify(trick['title'])
        trick['thumb'] = u'%s-%s.jpg' % (_id, trick.get('thumb', '3'))

        if db.trick.find_one({'_id': _id}):
            db.trick.update({'_id': _id}, {'$set': trick})
            if options.update_thumbs:
                _download_thumbs(_id, trick['videos'])
            return

        t = connection.Trick()
        t.update(trick)
        t['_id'] = _id
        t.save()

        _download_thumbs(_id, trick['videos'])

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

