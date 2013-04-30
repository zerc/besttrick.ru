# coding: utf-8
"""
    apps.achives.manage
    ~~~~~~~~~~~

    Some scripts for achive module

    :copyright: (c) 2013 by zero13cool
"""
from project import app, command_manager, checkin_signal
from apps import users, tricks, achives


@command_manager.command
def achives_update():
    """
    Update achives from old user checkins
    """
    for user in app.db.User.find():
        map(checkin_signal.send, tricks.get_checkins(int(user.get('_id'))))


@command_manager.command
def achives_drop():
    """
    Drop all events and reset seqs
    """
    app.db.achive.drop()
    app.db.event.drop()
    app.db.seqs.find_and_modify({u'_id': u'achives_seq'}, {u'val': 0})


@command_manager.command
def achives_fill():
    """
    Fill achives from fixtures
    """
    from apps.achives import fixtures as f 
    for a in f.achives:
        achive = app.connection.Achive()
        a['_id'] = app.db.seqs.find_and_modify({"_id": "achives_seq"}, {"$inc": {"val": 1}})['val']
        achive.update(a)
        achive.save()

