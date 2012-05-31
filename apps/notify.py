# -*- coding: utf-8 -*-
from datetime import datetime

from mongokit import Document, DocumentMigration, ObjectId
from project import db, app, connection, mail
from flaskext.mail import Message


# Типы нотификации
CHECKTRICK_WITH_VIDEO = 0


# Статусы нотификации
NOT_PROCESSES = 0
GOOD          = 1
BAD           = 2


### Models
class Notice(Document):
    __database__   = app.config['MONGODB_DB']
    __collection__ = "notice"

    structure = {
        'notice_type' : int,
        'data'        : dict,
        'status'      : int,
        'time_added'  : datetime,
    }
    default_values  = {'status': NOT_PROCESSES, 'time_added': datetime.now}
    required_fields = ['notice_type', 'data']
connection.register([Notice])


def send_notify(notify_type, data):
    """
    Отсылает администации уведомления о каких-либо событиях.
    Как в админку так и на почту.
    """

    # пока поддреживаем только один тип нотификаций (о новых видосах)
    if notify_type != 0:
        raise NotImplemented(u'%s notify does not support yet')

    notice = connection.Notice()
    notice.update({'notice_type': notify_type, 'data': data})
    notice.save()

    msg = Message(u'Новое видео', recipients=app.config['ADMINS'])
    msg.html = u"""
    <p>Пользователь %(username)s добавил новое видео по трюку %(trickname)s:</p>
    <a href="%(video_url)s" target="_blank">%(video_url)s</a>
    <p>Отмодерировать это дело можно в админке: <a href="%(admin_url)s" target="_blank">%(admin_url)s</a></a>
    """ % {
        'username'  : db.user.find_one({"_id": notice["data"]["user"]})['nick'],
        'trickname' : db.trick.find_one({"_id": notice['data']['trick']})['title'],
        'video_url' : data['video_url'],
        'admin_url' : app.config['HOST'] + '/#admin/videos/'
    }
    msg.body = ""

    mail.send(msg)
