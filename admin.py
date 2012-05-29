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

# Kazachok        0.6
# Korean Spin     0.6
# Russian Spin    0.2
# Chicken Leg     0.7
# Toe Machine     0.7
# Day Night       0.8
# Footgun Toe     0.8
# OneWheel        0.4
# Confraglide     0.7
# Cobra           0.6
# Seven           0.7
# No wiper        0.8
# Foot Spin       0.3

parser = OptionParser(u"Admin scripts for besttrick app")


def tags(options):
    """ Вгоняет тэги в базу """
    data = [
        {
            '_id'   : u'sitting',
            'title' : u'сидячие',
        },
        {
            '_id'   : u'jumping',
            'title' : u'прыжковые',
        },
        {
            '_id'   : u'wheeling',
            'title' : u'вилинги',
        },
        {
            '_id'   : u'spinning',
            'title' : u'вращательные',
        },
        {
            '_id'   : u'slalom',
            'title' : u'слалом',
            'major' : True,
        },
        {
            '_id'   : u'slides',
            'title' : u'слайды',
            'major' : True,
        }
    ]

    for t in data:
        tag = connection.Tag()
        tag.update(t)
        tag.save()


# Список трюков вынести в отдельный файл, типа "дамп базы"
parser.add_option("-t", "--update_thumbs", dest="update_thumbs", help="update_thumbs ?", action="store_true")
def import_tricks(options):
    """ Import trick to mongo. Run: admin.py import_tricks """
    tricks = [
        {
            "title"         : u"Kazachok",
            "descr"         : u"""В лучших русских традициях.""",
            "videos"        : [u"http://www.youtube.com/embed/JxJvchXvQAg"],
            "direction"     : u"forward",
            "tags"          : [u'sitting', u'jumping', u'slalom'],
            "score"         : 0.6,
        },
        {
            "title"         : u"Korean Spin",
            "thumb"         : u"2",
            "descr"         : u"""Отвертка на передних колесах.""",
            "videos"        : [u"http://www.youtube.com/embed/Bby-06T_Vxo"],
            "tags"          : [u'spinning', u'slalom',],
            "score"         : 0.6,
        },
        {
            "title"         : u"Russian Spin",
            "thumb"         : u"3",
            "descr"         : u"""Русский вольт на передних колесах.""",
            "videos"        : [u"http://www.youtube.com/embed/gfkJAcz2Vgs"],
            "tags"          : [u'spinning', u'slalom',],
            "score"         : 0.2,
        },
        {
            "title"         : u"Chicken Leg",
            "thumb"         : u"2",
            "descr"         : u"""В русском слаломе трюк известен как **Бэк факир на тое с грэбом.**""",
            "videos"        : [u"http://www.youtube.com/embed/rYLMXZfTWCM"],
            "direction"     : u"backward",
            "tags"          : [u'wheeling', u'spinning', u'slalom'],
            "score"         : 0.7,
        },
        {
            "title"         : u"Toe Machine",
            "videos"        : [u"http://www.youtube.com/embed/Q5qFX8YPtaU"],
            "descr"         : u"""Трюк так же известен как Швейная машинка.""",
            "tags"          : [u'wheeling', u'slalom'],
            "score"         : 0.7,
        },
        {
            "title"         : u"Day Night",
            "descr"         : u"""Своеобразный ответ на No Wiper. Выполняется как хиле, так и на тое.""",
            "videos"        : [u"http://www.youtube.com/embed/vRb0PAeBe2g"],
            "tags"          : [u'wheeling', u'slalom'],
            "score"         : 0.8,
        },
        {
            "title"         : u"Footgun Toe",
            "thumb"         : u"2",
            "videos"        : [u"http://www.youtube.com/embed/m2JPr2geQxA"],
            "descr"         : u"""Пистолет на переднем колесе. Существуют варианты с полном приседом, и с коленом под прямым углом.""",
            "direction"     : u"forward",
            "tags"          : [u'wheeling', u'slalom', u'sitting',],
            "score"         : 0.8,
        },
        {
            "title"         : u"OneWheel",
            "thumb"         : u"2",
            "videos"        : [u"http://www.youtube.com/embed/okiGOwGfhY0"],
            "descr"         : u"""Езда на одном колесе лицом вперед. Может выполнятся как на переднем (тое), так и на заднем (хил) колесах.""",
            "direction"     : u"forward",
            "tags"          : [u'wheeling', u'slalom'],
            "score"         : 0.4,
        },
        {
            "title"         : u"Confraglide",
            "videos"        : [u"http://www.youtube.com/embed/F6897UqZBw8"],
            "descr"         : u"""В русском слаломе, трюк так же известен как Бабочка.""",
            "tags"          : [u'slalom'],
            "score"         : 0.7,
        },
        {
            "title"         : u"Cobra",
            "videos"        : [u"http://www.youtube.com/embed/P_gyByoM4qg"],
            "descr"         : u"""Кобра спиной вперед. """,
            "direction"     : u"backward",
            "tags"          : [u'slalom'],
            "score"         : 0.6,
        },
        {
            "title"         : u"Seven",
            "thumb"         : u"2",
            "videos"        : [u"http://www.youtube.com/embed/-8O-z3vO2xs"],
            "descr":
            u"""
Вращение на одном колесе с продвижением по банками.

Выполняется на тое или хиле.
            """,
            "direction"     : u"forward",
            "tags"          : [u'wheeling', u'slalom', u'spinning'],
            "score"         : 0.7,
        },
        {
            "title"         : u"No wiper",
            "videos"        : [u"http://www.youtube.com/embed/RQeEDR7j0uc"],
            "descr"         : u"""
Также называется Toe shift.

Может выполнятся как на внутреннем, так и на внешнем ребре.
            """,
            "tags"          : [u'wheeling', u'slalom'],
            "score"         : 0.8,
        },
        {
            "title"         : u"Foot spin",
            "thumb"         : u"2",
            "videos"        : [u"http://www.youtube.com/embed/Q9fTQOopwF8"],
            "descr"         : u"""Можно рассматривать как подготовоку к Day Night :)""",
            "tags"          : [u'slalom', u'spinning'],
            "score"         : 0.3,
        },
    ]

    def _download_thumbs(trick_id, videos_urls):
        """ По переданному идентификатору видео, скачивает тумбы с ютуба """
        url = 'http://img.youtube.com/vi/%s/%s.jpg'

        for video_url in videos_urls:
            video_id = video_url.split('/')[-1]

            for x in range(4):
                response = urllib.urlopen(url % (video_id, x))
                path = path_join(app.static_folder, 'images', 'trick%s-%s.jpg' % (trick_id, x))
                with open(path, 'wb') as f:
                    f.write(response.read())

    def _update(args):
        _id, trick = args
        old_id = "-".join(filter(None, (slugify(trick['title']), trick.get('direction', '')[:1])))
        trick['thumb'] = u'trick%s-%s.jpg' % (_id, trick.get('thumb', '3'))
        print db.seqs.find_and_modify({"_id": "tricks_seq"}, {"$inc": {"val": 1}}), old_id

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

    db.seqs.find_and_modify({"_id": "tricks_seq"}, {"$set": {"val": 0}})
    map(_update, enumerate(tricks))



if __name__ == "__main__":
    options, labels = parser.parse_args()
    for label in labels:
        if not hasattr(sys.modules[__name__], label):
            print '>> Function %s does not exists' % label
            continue

        getattr(sys.modules[__name__], label)(options)

