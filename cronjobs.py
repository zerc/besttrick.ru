#!venv/bin/python
# -*- coding: utf-8 -*-
from os.path import join as path_join
from project import app, db
from apps import tricks as tricks_views
from flaskext.script import Manager

manager = Manager(app)

@manager.command
def sitemap():
    tricks = db.trick.find()
    xml = [
        u"""<?xml version="1.0" encoding="UTF-8"?>""", 
        u"""<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">"""
    ]

    # добавляем трюки
    trick_tmpl = u"""<url><loc>%s/#!trick/%s</loc></url>"""
    xml.extend([trick_tmpl % (app.config['HOST'], trick['_id']) for trick in tricks])

    # flatpages
    #xml.append(u"""<url><loc>%s/#!about</loc></url>""" % app.config['HOST'])

    xml.append(u"""</urlset>""")

    with open(path_join(app.static_folder, 'sitemap.txt'), 'w') as f:
        f.write("\n".join(xml))

if __name__ == "__main__":
    manager.run()
