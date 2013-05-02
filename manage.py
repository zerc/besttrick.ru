# coding: utf-8
"""
    manage
    ~~~~~~~~~~~

    Main manage file for do some cool stuff

    :copyright: (c) 2013 by zero13cool
"""
from os.path import join as path_join

import urls
from project import app, command_manager
from apps import tricks as tricks_views

from apps.achives import manage


@command_manager.command
def sitemap():
    tricks = app.db.trick.find()
    xml = [
        u"""<?xml version="1.0" encoding="UTF-8"?>""", 
        u"""<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">"""
    ]

    # добавляем трюки
    trick_tmpl = u"""<url><loc>%s/#!trick%s</loc></url>"""
    xml.extend([trick_tmpl % (app.config['HOST'], int(trick['_id'])) for trick in tricks])

    # flatpages
    #xml.append(u"""<url><loc>%s/#!about</loc></url>""" % app.config['HOST'])

    xml.append(u"""</urlset>""")

    with open(path_join(app.static_folder, 'sitemap.txt'), 'w') as f:
        f.write("\n".join(xml))


@command_manager.command
def runserver(*args, **kwargs):    
    app.run(host='0.0.0.0', port=8000)


@command_manager.command
def slow_runserver(*args, **kwargs):
    """
    For imitation slow internet connection
    """

    import time
    from flask import request

    @app.before_request
    def before_request():
        if 'static' not in request.path:
            time.sleep(3)

    runserver()
            

if __name__ == "__main__":
    command_manager.run()
