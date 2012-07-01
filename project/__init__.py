#!venv/bin/python
# -*- coding: utf-8 -*-
from mongokit import Connection

from flask import Flask
from flask.ext.assets import Environment, Bundle
from flaskext.markdown import Markdown

try:
    from flaskext.mail import Mail, email_dispatched
    from flask_errormail import mail_on_500
except ImportError:
    Mail, email_dispatched, mail_on_500 = None, None, None


app = Flask(__name__)
app.root_path = '/'.join(app.root_path.split('/')[:-1])
app.config.from_object('project.settings')

if mail_on_500: mail_on_500(app, app.config['ADMINS'])

markdown = Markdown(app)

connection = Connection(app.config['MONGODB_HOST'], app.config['MONGODB_PORT'])
db = connection.besttrick

assets = Environment(app)
JS_LIBS = (
    'js/jquery.min.js',
    'js/underscore.js',
    'js/backbone.js',
    'js/ejs.js',
    'js/jquery.form.js',
    'js/bootstrap-tooltip.js',
    'js/jquery.reject.js',
    'js/jquery.cookie.js',

    'js/common.js',
    'js/tricks.js',
    'js/users.js',
    'js/app.js',
)

js = Bundle(*JS_LIBS, filters='jsmin', output='js/main.min.js')
assets.register('js_all', js)


def log_message(message, app):
    app.logger.debug(u'\n'.join([message.subject, message.body]))

if Mail:
    email_dispatched.connect(log_message)
    mail = Mail(app)
